"""State-distance clock for atomic evolution."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .model import AtomicManifoldModel
from .states import AtomicState


@dataclass(frozen=True)
class AtomicClockReading:
    distance: float
    accumulated_distance: float
    pulses: int
    pulse_index: int


class AtomicStateClock:
    """Emit pulses from Fubini-Study distance between successive pure states."""

    def __init__(self, distance_per_pulse: float = 0.1, clock_scale: float = 1.0):
        if not np.isfinite(distance_per_pulse) or distance_per_pulse <= 0.0:
            raise ValueError("distance_per_pulse must be finite and positive")
        if not np.isfinite(clock_scale) or clock_scale <= 0.0:
            raise ValueError("clock_scale must be finite and positive")
        self.distance_per_pulse = float(distance_per_pulse)
        self.clock_scale = float(clock_scale)
        self._previous: np.ndarray | None = None
        self._remainder = 0.0
        self._pulse_index = 0

    def rebase(self, state: AtomicState, model: AtomicManifoldModel) -> None:
        """Change the comparison baseline without generating a false event."""

        self._previous = state.validated(model).amplitudes.copy()

    def update(
        self, state: AtomicState, model: AtomicManifoldModel
    ) -> AtomicClockReading:
        current = state.validated(model).amplitudes
        if self._previous is None:
            self._previous = current.copy()
            return AtomicClockReading(0.0, self._remainder, 0, self._pulse_index)
        fidelity_amplitude = float(np.clip(abs(np.vdot(self._previous, current)), 0.0, 1.0))
        distance = float(np.arccos(fidelity_amplitude)) * self.clock_scale
        accumulated = self._remainder + distance
        pulses = int(np.floor((accumulated + 1e-15) / self.distance_per_pulse))
        self._remainder = accumulated - pulses * self.distance_per_pulse
        self._pulse_index += pulses
        self._previous = current.copy()
        return AtomicClockReading(distance, self._remainder, pulses, self._pulse_index)


__all__ = ["AtomicClockReading", "AtomicStateClock"]
