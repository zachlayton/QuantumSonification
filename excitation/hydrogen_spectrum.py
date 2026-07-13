from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from excitation.base import QuantumSource
from excitation.descriptor import QuantumDescriptor


@dataclass(frozen=True)
class HydrogenSpectrumState:
    """Snapshot of one idealized hydrogen transition."""

    index: int
    n_hi: int
    n_lo: int
    delta_e: float
    normalized_energy: float
    phase: float
    probability: float
    topology: float
    curvature: float


class HydrogenSpectrumSource(QuantumSource):
    """Discrete hydrogen transition source based on the Rydberg energy law."""

    TRANSITIONS = (
        (3, 2),
        (4, 2),
        (5, 2),
        (6, 2),
        (7, 2),
        (8, 2),
        (4, 3),
        (5, 3),
        (6, 3),
        (7, 3),
        (2, 1),
        (3, 1),
    )

    RYDBERG_EV = 13.605693122994

    def __init__(self) -> None:
        self.index = 0
        self._state = self._transition_state(self.index)
        self._descriptor = self._descriptor_from_state(self._state)

    def _transition_state(self, index: int) -> HydrogenSpectrumState:
        n_hi, n_lo = self.TRANSITIONS[index % len(self.TRANSITIONS)]

        delta_e = self.RYDBERG_EV * ((1.0 / n_lo**2) - (1.0 / n_hi**2))
        normalized_energy = np.clip(delta_e / self.RYDBERG_EV, 0.0, 1.0)

        transition_ratio = n_hi / n_lo
        phase = transition_ratio % 1.0
        probability = np.clip(normalized_energy * (1.0 / n_lo), 0.0, 1.0)

        topology = np.clip(abs(n_hi - n_lo) / 7.0, 0.0, 1.0)
        curvature = topology

        return HydrogenSpectrumState(
            index=int(index),
            n_hi=int(n_hi),
            n_lo=int(n_lo),
            delta_e=float(delta_e),
            normalized_energy=float(normalized_energy),
            phase=float(phase),
            probability=float(probability),
            topology=float(topology),
            curvature=float(curvature),
        )

    def _descriptor_from_state(
        self,
        state: HydrogenSpectrumState,
    ) -> QuantumDescriptor:
        return QuantumDescriptor(
            energy=state.normalized_energy,
            phase=state.phase,
            probability=state.probability,
            coherence=1.0,
            entanglement=0.0,
            spin=0.5,
            topology=state.topology,
            curvature=state.curvature,
        )

    def step(self, dt: float) -> None:
        """Advance to the next transition in the sequence."""
        if dt < 0:
            raise ValueError("dt must be non-negative.")

        self._state = self._transition_state(self.index)
        self._descriptor = self._descriptor_from_state(self._state)
        self.index += 1

    @property
    def descriptor(self) -> QuantumDescriptor:
        """Return the latest compact descriptor without advancing."""
        return self._descriptor

    @property
    def state(self) -> HydrogenSpectrumState:
        """Return the latest transition state without advancing."""
        return self._state