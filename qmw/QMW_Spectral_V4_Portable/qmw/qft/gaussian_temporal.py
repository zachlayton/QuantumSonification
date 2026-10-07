"""Intrinsic pulse clocks for site-reduced Gaussian field states.

The quantum distance at each lattice site is the Bures angle of its exact
single-mode Gaussian marginal.  The global diagnostic is deliberately an
aggregate of those local angles; it is not advertised as the full multimode
Gaussian Bures distance when the sites are correlated.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import math

import numpy as np

from .schema import ScalarFieldFrame


def single_mode_gaussian_fidelity(
    mean_a: np.ndarray,
    covariance_a: np.ndarray,
    mean_b: np.ndarray,
    covariance_b: np.ndarray,
    *,
    hbar: float = 1.0,
) -> float:
    """Squared Uhlmann fidelity of two one-mode Gaussian states.

    Means are ordered ``(q, p)`` and covariances are symmetrized, with
    ``[q, p] = i hbar`` and vacuum covariance ``hbar I / 2``.
    """

    hbar = float(hbar)
    if not np.isfinite(hbar) or hbar <= 0.0:
        raise ValueError("hbar must be finite and positive")
    first_mean = np.asarray(mean_a, dtype=float)
    second_mean = np.asarray(mean_b, dtype=float)
    first_covariance = np.asarray(covariance_a, dtype=float)
    second_covariance = np.asarray(covariance_b, dtype=float)
    if first_mean.shape != (2,) or second_mean.shape != (2,):
        raise ValueError("single-mode means must have shape (2,)")
    if first_covariance.shape != (2, 2) or second_covariance.shape != (2, 2):
        raise ValueError("single-mode covariances must have shape (2, 2)")
    if not all(
        np.isfinite(value).all()
        for value in (
            first_mean,
            second_mean,
            first_covariance,
            second_covariance,
        )
    ):
        raise ValueError("Gaussian moments must be finite")
    first_covariance = 0.5 * (first_covariance + first_covariance.T)
    second_covariance = 0.5 * (second_covariance + second_covariance.T)
    minimum_determinant = 0.25 * hbar * hbar
    determinants = (
        float(np.linalg.det(first_covariance)),
        float(np.linalg.det(second_covariance)),
    )
    tolerance = 1e-10 * max(1.0, hbar * hbar)
    if min(determinants) < minimum_determinant - tolerance:
        raise ValueError("covariance violates the one-mode uncertainty relation")

    covariance_sum = first_covariance + second_covariance
    delta = max(float(np.linalg.det(covariance_sum)) / (hbar * hbar), 0.0)
    lambda_term = 4.0 * max(
        determinants[0] / (hbar * hbar) - 0.25, 0.0
    ) * max(determinants[1] / (hbar * hbar) - 0.25, 0.0)
    denominator = math.sqrt(max(delta + lambda_term, 0.0)) - math.sqrt(
        lambda_term
    )
    if denominator <= 0.0:
        raise ValueError("Gaussian fidelity denominator is non-positive")
    displacement = first_mean - second_mean
    exponent = -0.5 * float(
        displacement @ np.linalg.solve(covariance_sum, displacement)
    )
    fidelity = float(np.clip(math.exp(exponent) / denominator, 0.0, 1.0))
    # Suppress roundoff-only motion of exactly stationary Gaussian states.
    return 1.0 if fidelity > 1.0 - 1e-13 else fidelity


def single_mode_bures_angle(
    mean_a: np.ndarray,
    covariance_a: np.ndarray,
    mean_b: np.ndarray,
    covariance_b: np.ndarray,
    *,
    hbar: float = 1.0,
) -> float:
    fidelity = single_mode_gaussian_fidelity(
        mean_a,
        covariance_a,
        mean_b,
        covariance_b,
        hbar=hbar,
    )
    return float(math.acos(math.sqrt(np.clip(fidelity, 0.0, 1.0))))


@dataclass(frozen=True)
class GaussianClockReading:
    source_revision: int
    record_index: int
    intrinsic_time: float
    delta_bures: float
    scaled_increment: float
    remainder: float
    next_record_distance: float
    pulses: int

    def to_dict(self) -> dict[str, int | float]:
        return asdict(self)


@dataclass(frozen=True)
class GaussianSiteClockReading(GaussianClockReading):
    site: int
    mean_phi: float
    mean_pi: float
    local_energy: float
    variance_phi: float
    variance_pi: float
    covariance_phi_pi: float


@dataclass(frozen=True)
class GaussianGeodesicReading:
    source_revision: int
    site: int
    record_index: int
    intrinsic_length: float
    weighted_time: float
    delta_bures: float
    chord_bures: float
    triangle_defect: float
    normalized_bending: float
    weighted_increment: float
    remainder: float
    pulses: int


@dataclass(frozen=True)
class GaussianFieldTemporalFrame:
    source_revision: int
    global_clock: GaussianClockReading
    site_clocks: tuple[GaussianSiteClockReading, ...]
    geodesic_site_clocks: tuple[GaussianGeodesicReading, ...] = ()
    aggregate_kind: str = "root_sum_square_local_bures"

    @property
    def pulses(self) -> int:
        return sum(reading.pulses for reading in self.site_clocks)


class _DistanceRecordClock:
    def __init__(
        self,
        distance_per_pulse: float,
        *,
        mode: str,
        seed: int,
        clock_scale: float,
        max_pulses_per_update: int,
    ) -> None:
        self.distance_per_pulse = self._validate_distance(distance_per_pulse)
        self.mode = self._validate_mode(mode)
        self.clock_scale = self._validate_scale(clock_scale)
        self.max_pulses_per_update = max(1, int(max_pulses_per_update))
        self.rng = np.random.default_rng(seed)
        self.intrinsic_time = 0.0
        self.remainder = 0.0
        self.record_index = 0
        self.next_record_distance = self._draw_distance()

    @staticmethod
    def _validate_distance(value: float) -> float:
        value = float(value)
        if not np.isfinite(value) or value <= 0.0:
            raise ValueError("distance_per_pulse must be finite and positive")
        return value

    @staticmethod
    def _validate_scale(value: float) -> float:
        value = float(value)
        if not np.isfinite(value) or value <= 0.0:
            raise ValueError("clock_scale must be finite and positive")
        return value

    @staticmethod
    def _validate_mode(value: str) -> str:
        value = str(value).strip().lower()
        if value not in {"fixed", "poisson"}:
            raise ValueError("clock mode must be 'fixed' or 'poisson'")
        return value

    def _draw_distance(self) -> float:
        if self.mode == "fixed":
            return self.distance_per_pulse
        return max(float(self.rng.exponential(self.distance_per_pulse)), 1e-12)

    def update(self, delta: float, source_revision: int) -> GaussianClockReading:
        delta = float(delta)
        if not np.isfinite(delta) or delta < 0.0:
            raise ValueError("distance increment must be finite and nonnegative")
        scaled = self.clock_scale * delta
        self.intrinsic_time += delta
        self.remainder += scaled
        pulses = 0
        while (
            self.remainder + 1e-15 >= self.next_record_distance
            and pulses < self.max_pulses_per_update
        ):
            self.remainder -= self.next_record_distance
            pulses += 1
            self.next_record_distance = self._draw_distance()
        self.record_index += pulses
        return GaussianClockReading(
            source_revision=int(source_revision),
            record_index=self.record_index,
            intrinsic_time=self.intrinsic_time,
            delta_bures=delta,
            scaled_increment=scaled,
            remainder=self.remainder,
            next_record_distance=self.next_record_distance,
            pulses=pulses,
        )


class _GaussianGeodesicClock:
    """Fixed-threshold clock weighted by local Gaussian path bending.

    The three-frame triangle defect is cubic in a smooth path's sampling
    interval.  ``normalized_bending`` divides out the cube of the combined
    segment length, yielding a path-local curvature-density estimate rather
    than a sampling-rate-dependent increment.
    """

    def __init__(
        self,
        distance_per_pulse: float,
        *,
        hbar: float,
        bending_depth: float,
        clock_scale: float,
        max_pulses_per_update: int,
    ) -> None:
        self.distance_per_pulse = _DistanceRecordClock._validate_distance(
            distance_per_pulse
        )
        self.hbar = float(hbar)
        self.bending_depth = self._validate_bending_depth(bending_depth)
        self.clock_scale = _DistanceRecordClock._validate_scale(clock_scale)
        self.max_pulses_per_update = max(1, int(max_pulses_per_update))
        self._older: tuple[np.ndarray, np.ndarray] | None = None
        self._previous: tuple[np.ndarray, np.ndarray] | None = None
        self._previous_segment = 0.0
        self.intrinsic_length = 0.0
        self.weighted_time = 0.0
        self.remainder = 0.0
        self.record_index = 0

    @staticmethod
    def _validate_bending_depth(value: float) -> float:
        value = float(value)
        if not np.isfinite(value) or not 0.0 <= value <= 100.0:
            raise ValueError("geodesic bending depth must lie in [0, 100]")
        return value

    def _distance(
        self,
        first: tuple[np.ndarray, np.ndarray],
        second: tuple[np.ndarray, np.ndarray],
    ) -> float:
        return single_mode_bures_angle(*first, *second, hbar=self.hbar)

    @staticmethod
    def _copy_state(
        state: tuple[np.ndarray, np.ndarray],
    ) -> tuple[np.ndarray, np.ndarray]:
        return state[0].copy(), state[1].copy()

    def rebase(self, state: tuple[np.ndarray, np.ndarray]) -> None:
        self._older = None
        self._previous = self._copy_state(state)
        self._previous_segment = 0.0

    def update(
        self,
        state: tuple[np.ndarray, np.ndarray],
        source_revision: int,
        site: int,
    ) -> GaussianGeodesicReading:
        segment = chord = defect = normalized = 0.0
        if self._previous is not None:
            segment = self._distance(self._previous, state)
            if self._older is not None:
                chord = self._distance(self._older, state)
                two_segment_length = self._previous_segment + segment
                defect = max(two_segment_length - chord, 0.0)
                if two_segment_length > 1e-15:
                    normalized = defect / (two_segment_length**3)
        weighted_increment = self.clock_scale * segment * (
            1.0 + self.bending_depth * normalized
        )
        self.intrinsic_length += segment
        self.weighted_time += weighted_increment
        self.remainder += weighted_increment
        pulses = min(
            int(np.floor((self.remainder + 1e-15) / self.distance_per_pulse)),
            self.max_pulses_per_update,
        )
        self.remainder -= pulses * self.distance_per_pulse
        self.record_index += pulses
        self._older = self._previous
        self._previous = self._copy_state(state)
        self._previous_segment = segment
        return GaussianGeodesicReading(
            source_revision=int(source_revision),
            site=int(site),
            record_index=self.record_index,
            intrinsic_length=self.intrinsic_length,
            weighted_time=self.weighted_time,
            delta_bures=segment,
            chord_bures=chord,
            triangle_defect=defect,
            normalized_bending=normalized,
            weighted_increment=weighted_increment,
            remainder=self.remainder,
            pulses=pulses,
        )


class GaussianFieldTemporalEngine:
    """One site-reduced Gaussian clock per lattice site plus a global summary."""

    def __init__(
        self,
        sites: int,
        *,
        hbar: float = 1.0,
        distance_per_pulse: float = 0.025,
        mode: str = "poisson",
        seed: int = 23,
        clock_scale: float = 1.0,
        geodesic_bending_depth: float = 0.6,
        max_pulses_per_update: int = 8,
    ) -> None:
        if int(sites) != sites or sites < 1:
            raise ValueError("sites must be a positive integer")
        self.sites = int(sites)
        self.hbar = float(hbar)
        self.distance_per_pulse = float(distance_per_pulse)
        self.mode = str(mode).lower()
        self.seed = int(seed)
        self.clock_scale = float(clock_scale)
        self.geodesic_bending_depth = float(geodesic_bending_depth)
        self.max_pulses_per_update = int(max_pulses_per_update)
        self._previous: tuple[tuple[np.ndarray, np.ndarray], ...] | None = None
        self._global_clock: _DistanceRecordClock
        self._site_clocks: tuple[_DistanceRecordClock, ...]
        self._geodesic_site_clocks: tuple[_GaussianGeodesicClock, ...]
        self._make_clocks()

    def _new_clock(self, seed: int) -> _DistanceRecordClock:
        return _DistanceRecordClock(
            self.distance_per_pulse,
            mode=self.mode,
            seed=seed,
            clock_scale=self.clock_scale,
            max_pulses_per_update=self.max_pulses_per_update,
        )

    def _make_clocks(self) -> None:
        self._global_clock = self._new_clock(self.seed)
        self._site_clocks = tuple(
            self._new_clock(self.seed + 1 + site) for site in range(self.sites)
        )
        self._geodesic_site_clocks = tuple(
            _GaussianGeodesicClock(
                self.distance_per_pulse,
                hbar=self.hbar,
                bending_depth=self.geodesic_bending_depth,
                clock_scale=self.clock_scale,
                max_pulses_per_update=self.max_pulses_per_update,
            )
            for _ in range(self.sites)
        )

    def reset(self) -> None:
        self._previous = None
        self._make_clocks()

    def rebase(self, frame: ScalarFieldFrame) -> None:
        """Accept an external state intervention without emitting records.

        Record indices, intrinsic time, and pending distance are preserved.
        Only the comparison origin changes to the newly prepared field frame.
        """

        current = self._site_marginals(frame)
        self._previous = tuple(
            (mean.copy(), covariance.copy()) for mean, covariance in current
        )
        for clock, state in zip(self._geodesic_site_clocks, current):
            clock.rebase(state)

    def set_distance_per_pulse(self, value: float) -> float:
        new_distance = _DistanceRecordClock._validate_distance(value)
        old_distance = self.distance_per_pulse
        self.distance_per_pulse = new_distance
        ratio = new_distance / old_distance
        for clock in (self._global_clock, *self._site_clocks):
            clock.distance_per_pulse = new_distance
            # Preserve fractional progress through the pending interval.
            clock.remainder *= ratio
            clock.next_record_distance *= ratio
        for clock in self._geodesic_site_clocks:
            clock.distance_per_pulse = new_distance
            clock.remainder *= ratio
        return self.distance_per_pulse

    def set_mode(self, value: str) -> str:
        self.mode = _DistanceRecordClock._validate_mode(value)
        for clock in (self._global_clock, *self._site_clocks):
            clock.mode = self.mode
            clock.next_record_distance = clock._draw_distance()
        return self.mode

    def set_clock_scale(self, value: float) -> float:
        self.clock_scale = _DistanceRecordClock._validate_scale(value)
        for clock in (self._global_clock, *self._site_clocks):
            clock.clock_scale = self.clock_scale
        for clock in self._geodesic_site_clocks:
            clock.clock_scale = self.clock_scale
        return self.clock_scale

    def set_geodesic_bending_depth(self, value: float) -> float:
        self.geodesic_bending_depth = _GaussianGeodesicClock._validate_bending_depth(
            value
        )
        for clock in self._geodesic_site_clocks:
            clock.bending_depth = self.geodesic_bending_depth
        return self.geodesic_bending_depth

    def _site_marginals(
        self, frame: ScalarFieldFrame
    ) -> tuple[tuple[np.ndarray, np.ndarray], ...]:
        if frame.sites != self.sites:
            raise ValueError("field frame site count changed")
        result = []
        for site in range(self.sites):
            mean = np.asarray(
                [frame.mean_phi[site], frame.mean_pi[site]], dtype=float
            )
            covariance = np.asarray(
                [
                    [
                        frame.covariance_phi[site, site],
                        frame.covariance_phi_pi[site, site],
                    ],
                    [
                        frame.covariance_phi_pi[site, site],
                        frame.covariance_pi[site, site],
                    ],
                ],
                dtype=float,
            )
            result.append((mean, covariance))
        return tuple(result)

    def update(
        self, frame: ScalarFieldFrame, source_revision: int = 0
    ) -> GaussianFieldTemporalFrame:
        current = self._site_marginals(frame)
        deltas = np.zeros(self.sites, dtype=float)
        if self._previous is not None:
            for site, ((old_mean, old_covariance), (mean, covariance)) in enumerate(
                zip(self._previous, current)
            ):
                deltas[site] = single_mode_bures_angle(
                    old_mean,
                    old_covariance,
                    mean,
                    covariance,
                    hbar=self.hbar,
                )
        aggregate = float(np.linalg.norm(deltas))
        global_reading = self._global_clock.update(aggregate, source_revision)
        site_readings = []
        geodesic_readings = []
        for site, delta in enumerate(deltas):
            reading = self._site_clocks[site].update(float(delta), source_revision)
            site_readings.append(
                GaussianSiteClockReading(
                    **reading.to_dict(),
                    site=site,
                    mean_phi=float(frame.mean_phi[site]),
                    mean_pi=float(frame.mean_pi[site]),
                    local_energy=float(frame.local_energy_density[site]),
                    variance_phi=float(frame.covariance_phi[site, site]),
                    variance_pi=float(frame.covariance_pi[site, site]),
                    covariance_phi_pi=float(
                        frame.covariance_phi_pi[site, site]
                    ),
                )
            )
            geodesic_readings.append(
                self._geodesic_site_clocks[site].update(
                    current[site], source_revision, site
                )
            )
        self._previous = tuple(
            (mean.copy(), covariance.copy()) for mean, covariance in current
        )
        return GaussianFieldTemporalFrame(
            source_revision=int(source_revision),
            global_clock=global_reading,
            site_clocks=tuple(site_readings),
            geodesic_site_clocks=tuple(geodesic_readings),
        )


__all__ = [
    "GaussianClockReading",
    "GaussianFieldTemporalEngine",
    "GaussianFieldTemporalFrame",
    "GaussianGeodesicReading",
    "GaussianSiteClockReading",
    "single_mode_bures_angle",
    "single_mode_gaussian_fidelity",
]
