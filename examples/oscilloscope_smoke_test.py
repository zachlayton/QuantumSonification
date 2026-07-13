from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sys

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from hamiltonian.hamiltonian_state import HamiltonianState
from qmw.core import QuantumStateFrame
from quantum_oscilloscope.scope_engine import (
    QuantumOscilloscope,
    QuantumOscilloscopeConfig,
)


class RecordingOscClient:
    def __init__(self) -> None:
        self.messages: list[tuple[str, object]] = []

    def send_message(self, address: str, value: object) -> None:
        self.messages.append((address, value))


@dataclass
class PilotStub:
    node: int = 3
    velocity: float = 0.25
    phase_gradient: float = -0.1
    branch_entropy: float = 0.4


def build_frame() -> QuantumStateFrame:
    rho = np.eye(4, dtype=np.complex128) / 4.0
    observables = {
        "bloch_x": 0.1,
        "bloch_y": -0.2,
        "bloch_z": 0.3,
        "purity": 0.25,
        "entropy": 1.5,
        "coherence": 0.75,
        "entanglement": 0.2,
        "single_qubit_entropy": {0: 0.1, 1: 0.2, 2: 0.3, 3: 0.4},
        "mean_single_entropy": 0.25,
        "entropy_spread": 0.3,
        "entropy_centroid": 1.7,
        "entropy_centroid_norm": 0.57,
        "entropy_motion": 0.08,
        "entropy_motion_mean": 0.02,
        "entropy_motion_vector": [0.01, 0.02, 0.03, 0.04],
        "entropy_dominant_qubit": 3,
        "bipartition_entropy": {
            "01_vs_23": 0.9,
            "02_vs_13": 0.8,
            "03_vs_12": 0.7,
        },
        "trajectory_speed": 0.6,
        "trajectory_acceleration": 0.07,
        "trajectory_direction_change": 0.03,
        "density_delta_rho_max": 0.004,
        "density_delta_rho_mean": 0.001,
    }
    metadata = {
        "memory": {
            "size": 5,
            "purity": 0.8,
            "coherence": 1.2,
        },
        "bohm": {
            "x": 0.12,
            "velocity": -0.03,
            "speed": 0.03,
            "phase": 0.6,
            "density": 0.4,
            "node_proximity": 0.2,
            "curvature": 0.09,
            "field_velocity": 0.01,
        },
        "visual": {
            "bloch_x": 0.1,
            "bloch_y": -0.2,
            "bloch_z": 0.3,
            "perturbed_bloch_x": 0.11,
            "perturbed_bloch_y": -0.18,
            "perturbed_bloch_z": 0.35,
            "field_strength": 0.6,
            "field_acceleration": 0.07,
        },
        "circuit_state": {
            "populations": [0.25, 0.25, 0.25, 0.25],
            "qasm": "OPENQASM 2.0;",
            "basis_labels": ["00", "01", "10", "11"],
            "phase_reference": 0,
            "basis_phases": [0.0, 0.1, 0.2, 0.3],
            "phase_quality": [1.0, 0.8, 0.7, 0.6],
            "entropy_spread": 0.3,
            "entropy_centroid": 1.7,
            "entropy_centroid_norm": 0.57,
            "entropy_motion": 0.08,
            "entropy_motion_mean": 0.02,
            "entropy_motion_vector": [0.01, 0.02, 0.03, 0.04],
            "entropy_dominant_qubit": 3,
            "coherence": 0.75,
            "purity": 0.25,
            "entropy": 1.5,
            "column": 2,
            "pilot": PilotStub(),
            "gate_applied": 1,
            "gate_delta_rho": 0.005,
            "last_gate_column": 2,
            "last_gate_delta_rho": 0.005,
            "gate_energy": 0.4,
            "gate_event_count": 7,
        },
    }
    arrays = {
        "wavepacket_probability": np.array([0.2, 0.3, 0.5]),
        "wavefunction": np.array([1.0 + 0.0j, 0.0 + 1.0j, 0.5 + 0.5j]),
    }
    return QuantumStateFrame(
        t=0.0,
        dt=0.01,
        rho=rho,
        hamiltonian=HamiltonianState(x=0.2, y=-0.1, z=0.7),
        source_name="SmokeSource",
        observables=observables,
        arrays=arrays,
        metadata=metadata,
    )


def main() -> None:
    scope = QuantumOscilloscope(
        QuantumOscilloscopeConfig(send_pauli_aliases=True)
    )
    scope.osc = RecordingOscClient()
    scope.visual_osc = RecordingOscClient()

    scope.observe(build_frame())

    main_addresses = {address for address, _ in scope.osc.messages}
    visual_addresses = {address for address, _ in scope.visual_osc.messages}

    required_main = {
        "/qmw/hamiltonian/x",
        "/qmw/hamiltonian/pauli_x",
        "/qmw/bloch/x",
        "/qmw/purity",
        "/qmw/circuit/populations",
        "/qmw/circuit/gate_applied",
        "/qmw/memory/size",
        "/qmw/trajectory/speed",
        "/qmw/bohm/x",
        "/qmw/entanglement/partition_01_vs_23",
        "/qmw/density/delta_rho/max",
    }
    required_visual = {
        "/qmw/density/real/0",
        "/qmw/density/imag/0",
        "/qmw/source/wavepacket/probability",
        "/qmw/source/wavepacket/available",
        "/qmw/source/wavepacket/real",
        "/qmw/source/wavepacket/imag",
        "/qmw/source/wavepacket/spectrum",
        "/qmw/source/wavepacket/spectrum_phase",
        "/qmw/source/wavepacket/phase",
        "/qmw/bloch/perturbed_x",
        "/qmw/visual/field_strength",
    }

    missing_main = sorted(required_main - main_addresses)
    missing_visual = sorted(required_visual - visual_addresses)
    if missing_main or missing_visual:
        raise AssertionError(
            f"Missing main={missing_main}; missing visual={missing_visual}"
        )

    print(
        "Oscilloscope smoke test passed:",
        f"{len(scope.osc.messages)} main messages,",
        f"{len(scope.visual_osc.messages)} visual messages",
    )


if __name__ == "__main__":
    main()
