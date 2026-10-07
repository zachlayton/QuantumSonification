"""Read-only Bures timing observations for sealed density-matrix frames.

The clock measures successive authoritative snapshots.  It never changes the
Hamiltonian, density operator, or integration step; its pulse count is only a
downstream observation that an adapter may choose to render.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from threading import RLock

import numpy as np

from .dynamics import QuantumFrame, _density_matrix, _readonly


def bures_angle(rho: object, sigma: object) -> float:
    """Return the Bures angle between two physical density operators.

    The Uhlmann-Procrustes form is stable for adjacent, nearly equal snapshots,
    where evaluating ``acos(sqrt(F))`` directly loses precision.
    """

    def root(value: object) -> np.ndarray:
        density = _density_matrix(value)
        eigenvalues, eigenvectors = np.linalg.eigh(density)
        return (eigenvectors * np.sqrt(np.clip(eigenvalues, 0.0, None))) @ eigenvectors.conj().T

    first, second = root(rho), root(sigma)
    left, _, right_h = np.linalg.svd(first.conj().T @ second)
    alignment = right_h.conj().T @ left.conj().T
    chord = float(np.linalg.norm(first - second @ alignment, ord="fro"))
    return float(2.0 * math.asin(np.clip(0.5 * chord, 0.0, 1.0)))


@dataclass(frozen=True)
class BuresClockReading:
    """One immutable timing observation derived from one sealed frame."""

    revision: int
    delta: float
    intrinsic_length: float
    remainder: float
    pulses: int
    distance_per_pulse: float
    clock_scale: float


class BuresFrameClock:
    """Accumulate full-state Bures angle into bounded read-only pulse records."""

    def __init__(
        self,
        *,
        distance_per_pulse: float = 0.025,
        clock_scale: float = 1.0,
        max_pulses_per_frame: int = 8,
    ) -> None:
        self._lock = RLock()
        self.distance_per_pulse = self._distance(distance_per_pulse)
        self.clock_scale = self._scale(clock_scale)
        if int(max_pulses_per_frame) != max_pulses_per_frame or max_pulses_per_frame < 1:
            raise ValueError("max_pulses_per_frame must be a positive integer.")
        self.max_pulses_per_frame = int(max_pulses_per_frame)
        self._previous: np.ndarray | None = None
        self._intrinsic_length = 0.0
        self._remainder = 0.0

    @staticmethod
    def _distance(value: float) -> float:
        result = float(value)
        if not math.isfinite(result) or not 0.0001 <= result <= 2.0:
            raise ValueError("Bures distance per pulse must lie in [0.0001, 2].")
        return result

    @staticmethod
    def _scale(value: float) -> float:
        result = float(value)
        if not math.isfinite(result) or not 0.01 <= result <= 8.0:
            raise ValueError("Bures clock scale must lie in [0.01, 8].")
        return result

    def configure(
        self, *, distance_per_pulse: float | None = None, clock_scale: float | None = None,
    ) -> None:
        """Change observer parameters without resetting state or path history."""

        with self._lock:
            if distance_per_pulse is not None:
                self.distance_per_pulse = self._distance(distance_per_pulse)
            if clock_scale is not None:
                self.clock_scale = self._scale(clock_scale)

    def observe(self, frame: QuantumFrame) -> BuresClockReading:
        """Measure one sealed snapshot and return its bounded pulse budget."""

        if not isinstance(frame, QuantumFrame):
            raise ValueError("Bures clock requires a sealed QuantumFrame.")
        with self._lock:
            state = _readonly(frame.rho)
            delta = 0.0 if self._previous is None else bures_angle(self._previous, state)
            self._previous = state
            self._intrinsic_length += delta
            available = self._remainder + (delta * self.clock_scale)
            requested = int(math.floor((available + 1.0e-14) / self.distance_per_pulse))
            pulses = min(requested, self.max_pulses_per_frame)
            self._remainder = max(0.0, available - (pulses * self.distance_per_pulse))
            return BuresClockReading(
                revision=int(frame.frame_index), delta=delta,
                intrinsic_length=self._intrinsic_length, remainder=self._remainder,
                pulses=pulses, distance_per_pulse=self.distance_per_pulse,
                clock_scale=self.clock_scale,
            )


__all__ = ["BuresClockReading", "BuresFrameClock", "bures_angle"]
