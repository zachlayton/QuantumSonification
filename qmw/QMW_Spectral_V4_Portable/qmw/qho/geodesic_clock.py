"""Bures-geodesic timing observer for authoritative density trajectories.

This observer does not evolve quantum state.  It measures the path supplied by
the coupled-QHO backend and turns a declared Bures-geometric quantity into
records for downstream timing adapters.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import math

import numpy as np

from quantum_temporal_mechanics_v1.core import density_matrix


def bures_angle(rho: np.ndarray, sigma: np.ndarray) -> float:
    """Return the Bures angle with stable near-identity evaluation.

    ``acos(sqrt(F))`` is mathematically correct but loses the small difference
    from one when successive states are close.  The equivalent Uhlmann
    Procrustes distance computes the small chord directly:

        D_B = min_U ||sqrt(rho) - sqrt(sigma) U||_F
        angle = 2 asin(D_B / 2)
    """

    def root(value: np.ndarray) -> np.ndarray:
        value = density_matrix(value)
        eigenvalues, eigenvectors = np.linalg.eigh(value)
        return (eigenvectors * np.sqrt(np.clip(eigenvalues, 0.0, None))) @ (
            eigenvectors.conj().T
        )

    first = root(rho)
    second = root(sigma)
    left, _, right_h = np.linalg.svd(first.conj().T @ second)
    alignment = right_h.conj().T @ left.conj().T
    chord = float(np.linalg.norm(first - second @ alignment, ord="fro"))
    return float(2.0 * math.asin(np.clip(0.5 * chord, 0.0, 1.0)))


@dataclass(frozen=True)
class GeodesicClockReading:
    source_revision: int
    record_index: int
    intrinsic_length: float
    weighted_time: float
    delta_bures: float
    chord_bures: float
    triangle_defect: float
    normalized_bending: float
    bending_increment: float
    weighted_increment: float
    remainder: float
    next_record_distance: float
    pulses: int

    def to_dict(self) -> dict[str, float | int]:
        return asdict(self)


class BuresGeodesicClock:
    """Clock a density trajectory by Bures arc length and geodesic bending.

    Given three successive states ``rho0, rho1, rho2``, the nonnegative
    triangle defect

        d(rho0, rho1) + d(rho1, rho2) - d(rho0, rho2)

    measures how far the sampled path departs from the shortest connection
    between its endpoints.  It is zero for samples lying on one shortest
    geodesic (up to numerical error).  The raw defect is cubic in the sampling
    interval for a smooth path.  The pulse-budget contribution therefore uses
    ``defect / two_segment_length**2``; it scales like an ordinary segment and
    gives a stable accumulated bending rate as the sampling interval changes.
    ``normalized_bending`` reports ``defect / two_segment_length**3``, a local
    curvature-squared-like density independent of uniform reparameterization.
    These are path observables and sonification mappings, not modifications of
    the quantum evolution or claims about the manifold's curvature tensor.
    """

    def __init__(
        self,
        *,
        distance_per_pulse: float = 0.025,
        bending_depth: float = 1.0,
        clock_scale: float = 1.0,
        mode: str = "fixed",
        seed: int = 23,
        max_pulses_per_update: int = 8,
    ) -> None:
        self.distance_per_pulse = self._validate_distance(distance_per_pulse)
        self.bending_depth = self._validate_bending_depth(bending_depth)
        self.clock_scale = self._validate_clock_scale(clock_scale)
        self.mode = self._validate_mode(mode)
        self.rng = np.random.default_rng(int(seed))
        self.max_pulses_per_update = max(1, int(max_pulses_per_update))
        self.previous_previous: np.ndarray | None = None
        self.previous: np.ndarray | None = None
        self.previous_segment = 0.0
        self.intrinsic_length = 0.0
        self.weighted_time = 0.0
        self.remainder = 0.0
        self.record_index = 0
        self.next_record_distance = self._draw_record_distance()

    @staticmethod
    def _validate_distance(value: float) -> float:
        value = float(value)
        if not np.isfinite(value) or value <= 0.0:
            raise ValueError("geodesic distance_per_pulse must be positive")
        return value

    @staticmethod
    def _validate_bending_depth(value: float) -> float:
        value = float(value)
        if not np.isfinite(value) or not 0.0 <= value <= 100.0:
            raise ValueError("geodesic bending_depth must lie in [0, 100]")
        return value

    @staticmethod
    def _validate_clock_scale(value: float) -> float:
        value = float(value)
        if not np.isfinite(value) or not 0.01 <= value <= 4.0:
            raise ValueError("geodesic clock_scale must lie in [0.01, 4]")
        return value

    @staticmethod
    def _validate_mode(value: str) -> str:
        value = str(value).strip().lower()
        if value not in {"fixed", "poisson"}:
            raise ValueError("geodesic mode must be 'fixed' or 'poisson'")
        return value

    def _draw_record_distance(self) -> float:
        if self.mode == "fixed":
            return self.distance_per_pulse
        return max(float(self.rng.exponential(self.distance_per_pulse)), 1e-12)

    def set_distance_per_pulse(self, value: float) -> float:
        old_distance = self.distance_per_pulse
        self.distance_per_pulse = self._validate_distance(value)
        ratio = self.distance_per_pulse / old_distance
        self.remainder *= ratio
        self.next_record_distance *= ratio
        return self.distance_per_pulse

    def set_bending_depth(self, value: float) -> float:
        self.bending_depth = self._validate_bending_depth(value)
        return self.bending_depth

    def set_clock_scale(self, value: float) -> float:
        self.clock_scale = self._validate_clock_scale(value)
        return self.clock_scale

    def set_mode(self, value: str) -> str:
        self.mode = self._validate_mode(value)
        self.next_record_distance = self._draw_record_distance()
        return self.mode

    def update(
        self, rho: np.ndarray, source_revision: int = 0
    ) -> GeodesicClockReading:
        current = density_matrix(rho)
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
            defect = max(0.0, two_segment_length - chord)
            if two_segment_length > 1e-12:
                bending_increment = defect / (two_segment_length**2)
                normalized_bending = defect / (two_segment_length**3)

        weighted_increment = self.clock_scale * (
            delta + self.bending_depth * bending_increment
        )
        self.intrinsic_length += delta
        self.weighted_time += weighted_increment
        self.remainder += weighted_increment
        pulses = 0
        while (
            self.remainder + 1e-15 >= self.next_record_distance
            and pulses < self.max_pulses_per_update
        ):
            self.remainder -= self.next_record_distance
            pulses += 1
            self.next_record_distance = self._draw_record_distance()
        self.record_index += pulses
        self.previous_previous = (
            None if self.previous is None else self.previous.copy()
        )
        self.previous = current.copy()
        self.previous_segment = delta
        return GeodesicClockReading(
            source_revision=int(source_revision),
            record_index=self.record_index,
            intrinsic_length=self.intrinsic_length,
            weighted_time=self.weighted_time,
            delta_bures=delta,
            chord_bures=chord,
            triangle_defect=defect,
            normalized_bending=normalized_bending,
            bending_increment=bending_increment,
            weighted_increment=weighted_increment,
            remainder=self.remainder,
            next_record_distance=self.next_record_distance,
            pulses=pulses,
        )


__all__ = [
    "BuresGeodesicClock",
    "GeodesicClockReading",
    "bures_angle",
]
