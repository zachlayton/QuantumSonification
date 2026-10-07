"""Read-only Bures timing observer for the authoritative density trajectory.

The observer measures consecutive committed density matrices. It never writes
to ``rho`` and its records are downstream timing events, not quantum state
updates.
"""

from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np


Array = np.ndarray


def _density_root(value: Array) -> Array:
    matrix = np.asarray(value, dtype=np.complex128)
    matrix = 0.5 * (matrix + matrix.conj().T)
    eigenvalues, eigenvectors = np.linalg.eigh(matrix)
    eigenvalues = np.clip(eigenvalues.real, 0.0, None)
    total = float(np.sum(eigenvalues))
    if total <= 1.0e-15:
        raise ValueError("density matrix must have positive trace")
    eigenvalues /= total
    return (eigenvectors * np.sqrt(eigenvalues)) @ eigenvectors.conj().T


def bures_angle(rho: Array, sigma: Array) -> float:
    """Return the Bures angle using a stable Uhlmann-Procrustes chord."""
    first = _density_root(rho)
    second = _density_root(sigma)
    left, _, right_h = np.linalg.svd(first.conj().T @ second)
    alignment = right_h.conj().T @ left.conj().T
    chord = float(np.linalg.norm(first - second @ alignment, ord="fro"))
    return float(2.0 * math.asin(np.clip(0.5 * chord, 0.0, 1.0)))


@dataclass(frozen=True)
class BuresTemporalFrame:
    delta_bures: float
    intrinsic_length: float
    temporal_remainder: float
    temporal_pulses: int
    temporal_record_index: int
    weighted_time: float
    geodesic_remainder: float
    geodesic_pulses: int
    geodesic_record_index: int
    chord_bures: float
    triangle_defect: float
    normalized_bending: float
    bending_increment: float
    clock_scale: float
    distance_per_pulse: float
    geodesic_bending_depth: float
    schema: str = "qmw.quantum_resonant_membrane.bures_time.v2"


class BuresTemporalObserver:
    """Generate ordinary and path-bending records from Bures motion."""

    def __init__(
        self,
        *,
        distance_per_pulse: float = 0.025,
        clock_scale: float = 1.0,
        geodesic_bending_depth: float = 0.6,
        max_pulses_per_frame: int = 8,
    ) -> None:
        self.distance_per_pulse = self._distance(distance_per_pulse)
        self.clock_scale = self._scale(clock_scale)
        self.geodesic_bending_depth = self._bending(geodesic_bending_depth)
        self.max_pulses_per_frame = max(1, int(max_pulses_per_frame))
        self.reset()

    @staticmethod
    def _distance(value: float) -> float:
        value = float(value)
        if not np.isfinite(value) or not 0.001 <= value <= 0.2:
            raise ValueError("Bures distance_per_pulse must lie in [0.001, 0.2]")
        return value

    @staticmethod
    def _scale(value: float) -> float:
        value = float(value)
        if not np.isfinite(value) or not 0.01 <= value <= 4.0:
            raise ValueError("master clock_scale must lie in [0.01, 4]")
        return value

    @staticmethod
    def _bending(value: float) -> float:
        value = float(value)
        if not np.isfinite(value) or not 0.0 <= value <= 100.0:
            raise ValueError("geodesic_bending_depth must lie in [0, 100]")
        return value

    def reset(self) -> None:
        self.previous_previous: Array | None = None
        self.previous: Array | None = None
        self.previous_segment = 0.0
        self.intrinsic_length = 0.0
        self.temporal_remainder = 0.0
        self.temporal_record_index = 0
        self.weighted_time = 0.0
        self.geodesic_remainder = 0.0
        self.geodesic_record_index = 0

    def set_distance_per_pulse(self, value: float) -> float:
        old = self.distance_per_pulse
        self.distance_per_pulse = self._distance(value)
        ratio = self.distance_per_pulse / old
        self.temporal_remainder *= ratio
        self.geodesic_remainder *= ratio
        return self.distance_per_pulse

    def set_clock_scale(self, value: float) -> float:
        self.clock_scale = self._scale(value)
        return self.clock_scale

    def set_geodesic_bending_depth(self, value: float) -> float:
        self.geodesic_bending_depth = self._bending(value)
        return self.geodesic_bending_depth

    def _consume(self, remainder: float) -> tuple[float, int]:
        pulses = min(
            int((remainder + 1.0e-15) / self.distance_per_pulse),
            self.max_pulses_per_frame,
        )
        return max(0.0, remainder - pulses * self.distance_per_pulse), pulses

    def observe(self, rho: Array) -> BuresTemporalFrame:
        current = np.asarray(rho, dtype=np.complex128)
        delta = 0.0
        chord = 0.0
        defect = 0.0
        normalized_bending = 0.0
        bending_increment = 0.0
        if self.previous is not None:
            delta = bures_angle(self.previous, current)
        if self.previous_previous is not None and self.previous is not None:
            chord = bures_angle(self.previous_previous, current)
            two_segment_length = self.previous_segment + delta
            defect = float(np.clip(two_segment_length - chord, 0.0, two_segment_length))
            numerical_floor = 64.0 * np.finfo(float).eps * max(
                1.0, two_segment_length
            )
            if defect <= numerical_floor:
                defect = 0.0
            # For a smooth curve the triangle defect is cubic in sample
            # spacing. Dividing by the combined segment length cubed yields a
            # path-local curvature-density estimate that converges when the
            # same physical trajectory is sampled faster. The weighted clock
            # still advances by a length: delta * curvature_density.
            if two_segment_length > 1.0e-8:
                normalized_bending = defect / (two_segment_length**3)
                bending_increment = delta * normalized_bending

        temporal_increment = self.clock_scale * delta
        geodesic_increment = self.clock_scale * (
            delta + self.geodesic_bending_depth * bending_increment
        )
        self.intrinsic_length += delta
        self.temporal_remainder, temporal_pulses = self._consume(
            self.temporal_remainder + temporal_increment
        )
        self.temporal_record_index += temporal_pulses
        self.weighted_time += geodesic_increment
        self.geodesic_remainder, geodesic_pulses = self._consume(
            self.geodesic_remainder + geodesic_increment
        )
        self.geodesic_record_index += geodesic_pulses
        self.previous_previous = None if self.previous is None else self.previous.copy()
        self.previous = current.copy()
        self.previous_segment = delta
        return BuresTemporalFrame(
            delta_bures=delta,
            intrinsic_length=self.intrinsic_length,
            temporal_remainder=self.temporal_remainder,
            temporal_pulses=temporal_pulses,
            temporal_record_index=self.temporal_record_index,
            weighted_time=self.weighted_time,
            geodesic_remainder=self.geodesic_remainder,
            geodesic_pulses=geodesic_pulses,
            geodesic_record_index=self.geodesic_record_index,
            chord_bures=chord,
            triangle_defect=defect,
            normalized_bending=normalized_bending,
            bending_increment=bending_increment,
            clock_scale=self.clock_scale,
            distance_per_pulse=self.distance_per_pulse,
            geodesic_bending_depth=self.geodesic_bending_depth,
        )


__all__ = ["BuresTemporalFrame", "BuresTemporalObserver", "bures_angle"]
