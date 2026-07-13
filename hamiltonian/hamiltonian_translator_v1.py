

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from excitation.descriptor import QuantumDescriptor
from hamiltonian.hamiltonian_state import HamiltonianState


@dataclass(frozen=True)
class HamiltonianTranslationWeights:
    """Weights for mapping a QuantumDescriptor into Hamiltonian axes.

    The translator keeps the density engine source-agnostic:

        QuantumSource -> QuantumDescriptor -> HamiltonianTranslator -> HamiltonianState

    The three Pauli-field axes are treated as musical/physical control axes:
        X: energy / coherence / curvature drive
        Y: phase / spin drive
        Z: probability / topology / entanglement drive
    """

    energy_to_x: float = 1.00
    coherence_to_x: float = 0.35
    curvature_to_x: float = 0.25

    phase_to_y: float = 1.00
    spin_to_y: float = 0.45

    probability_to_z: float = 1.00
    topology_to_z: float = 0.50
    entanglement_to_z: float = 0.75

    current_memory: float = 0.92
    descriptor_amount: float = 0.18


class HamiltonianTranslator:
    """Translate compact quantum-source descriptors into Hamiltonian states.

    This class does not know whether a descriptor came from hydrogen spectra,
    hydrogen orbitals, a Schrödinger packet, or a future Zeeman / IBM source.
    It only consumes the canonical descriptor fields.
    """

    def __init__(
        self,
        weights: HamiltonianTranslationWeights | None = None,
    ) -> None:
        self.weights = weights or HamiltonianTranslationWeights()

    def translate(
        self,
        current: HamiltonianState,
        descriptor: QuantumDescriptor,
    ) -> HamiltonianState:
        """Return a new normalized HamiltonianState.

        The mapping is intentionally conservative: the current Hamiltonian keeps
        most of its momentum, while the descriptor bends it toward a new vector.
        This prevents abrupt discontinuities when a quantum source changes.
        """
        w = self.weights

        phase_centered = self._center(descriptor.phase)
        spin_centered = self._center(descriptor.spin)
        coherence_centered = self._center(descriptor.coherence)
        entanglement_centered = self._center(descriptor.entanglement)
        topology_centered = self._center(descriptor.topology)
        curvature_centered = self._center(descriptor.curvature)

        descriptor_x = (
            w.energy_to_x * descriptor.energy
            + w.coherence_to_x * coherence_centered
            + w.curvature_to_x * curvature_centered
        )
        descriptor_y = (
            w.phase_to_y * phase_centered
            + w.spin_to_y * spin_centered
        )
        descriptor_z = (
            w.probability_to_z * descriptor.probability
            + w.topology_to_z * topology_centered
            + w.entanglement_to_z * entanglement_centered
        )

        x = (w.current_memory * current.x) + (w.descriptor_amount * descriptor_x)
        y = (w.current_memory * current.y) + (w.descriptor_amount * descriptor_y)
        z = (w.current_memory * current.z) + (w.descriptor_amount * descriptor_z)

        return HamiltonianState(x=float(x), y=float(y), z=float(z)).normalize()

    def direct(self, descriptor: QuantumDescriptor) -> HamiltonianState:
        """Create a HamiltonianState from a descriptor without current-state memory."""
        zero = HamiltonianState(x=0.0, y=0.0, z=0.0)
        original_weights = self.weights
        try:
            self.weights = HamiltonianTranslationWeights(
                energy_to_x=original_weights.energy_to_x,
                coherence_to_x=original_weights.coherence_to_x,
                curvature_to_x=original_weights.curvature_to_x,
                phase_to_y=original_weights.phase_to_y,
                spin_to_y=original_weights.spin_to_y,
                probability_to_z=original_weights.probability_to_z,
                topology_to_z=original_weights.topology_to_z,
                entanglement_to_z=original_weights.entanglement_to_z,
                current_memory=0.0,
                descriptor_amount=1.0,
            )
            return self.translate(zero, descriptor)
        finally:
            self.weights = original_weights

    @staticmethod
    def _center(value: float) -> float:
        """Map normalized 0..1 values into approximately -1..+1."""
        return (2.0 * float(np.clip(value, 0.0, 1.0))) - 1.0