"""Patch template for integrating qmw_circuit_bridge into Quantum Population v5.

Copy the indicated methods into your existing engine. This is intentionally a
non-destructive adapter: it does not prescribe your current Hamiltonian,
Lindblad model, OSC paths, or Max mappings.
"""
from __future__ import annotations

import numpy as np

from qmw_circuit_bridge import QMWCircuitBridge

from dataclasses import dataclass
import numpy as np

from qmw_circuit_bridge import PilotFrame, QMWCircuitBridge
from qmw_circuit_bridge import QMWCircuitBridge


@dataclass
class GuidanceVector:
    node: int
    target_node: int
    momentum: float
    phase_force: float
    diffusion: float


    def pilot_to_population_guidance(pilot: PilotFrame, purity_value: float, coherence_value: float) -> GuidanceVector:
        """Convert state-graph dynamics into musically stable population guidance.

        This is deliberately low-noise. The pilot current supplies direction;
        entropy supplies controlled spread; purity/coherence determine focus.
        """
        focus = float(np.clip(0.55 * purity_value + 0.45 * min(1.0, coherence_value / 4.0), 0.0, 1.0))
        return GuidanceVector(
            node=pilot.node,
            target_node=pilot.next_node,
            momentum=float(np.clip(abs(pilot.current) + pilot.velocity, 0.0, 1.0)),
            phase_force=float(np.clip(pilot.phase_gradient, -1.0, 1.0)),
            diffusion=float(np.clip((pilot.branch_entropy / 4.0) * (1.0 - focus), 0.0, 1.0)),
        )


class CircuitEnabledPopulationMixin:
    """Mixin skeleton: adapt member field names to your Quantum Population v5."""

    def initialise_circuit_layer(self) -> None:
        self.qmw_bridge = QMWCircuitBridge(
            n_qubits=4,
            n_steps=16,
            osc_out_port=9001,      # Max receives here
            osc_control_port=9002,  # Circuit GUI sends edits here
            circuit_interval_seconds=0.20,
        )
        self.qmw_bridge.start_control_server()

    def circuit_step(self, dt: float) -> GuidanceVector:
        # 1. Discrete top-layer intervention.
        self.rho, column, labels = self.qmw_bridge.apply_due_circuit_column(self.rho, dt)

        # 2. Your existing continuous density evolution goes here.
        self.rho = self.apply_lindblad_step(self.rho, dt)

        # 3. Derive guidance and broadcast all quantum / pilot OSC data.
        pilot = self.qmw_bridge.update_and_send(
            self.rho, self.hamiltonian, dt, column, labels
        )
        rho_purity = float(np.trace(self.rho @ self.rho).real)
        rho_coherence = float(np.sum(np.abs(self.rho - np.diag(np.diag(self.rho)))))
        return pilot_to_population_guidance(pilot, rho_purity, rho_coherence)

    def guide_member(self, member, guidance: GuidanceVector, noise_amount: float = 0.03) -> None:
        """Replace broad perturbation with directed state-dependent movement.

        Assumes your members have position/velocity numpy vectors. Adapt the
        field names and parameter dimensions to your actual v5 data structure.
        """
        dim = len(member.position)
        node_bits = np.array([(guidance.node >> shift) & 1 for shift in range(3, -1, -1)], dtype=float)
        target_bits = np.array([(guidance.target_node >> shift) & 1 for shift in range(3, -1, -1)], dtype=float)
        # Fold four configuration bits into any parameter-vector dimension.
        desired = np.resize(2.0 * target_bits - 1.0, dim)
        current = np.resize(2.0 * node_bits - 1.0, dim)
        direction = desired - current
        norm = np.linalg.norm(direction)
        if norm > 1e-12:
            direction /= norm

        controlled_noise = self.rng.normal(0.0, noise_amount * (0.25 + guidance.diffusion), size=dim)
        member.velocity = (
            0.70 * member.velocity
            + 0.24 * guidance.momentum * direction
            + 0.10 * guidance.phase_force * np.roll(direction, 1)
            + controlled_noise
        )
        member.position = member.position + member.velocity
