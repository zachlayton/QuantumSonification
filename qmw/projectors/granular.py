from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

from qmw.core.physics_frame import PhysicsFrame
from qmw.core.state_frame import QuantumStateFrame


@dataclass(frozen=True)
class GranularControl:
    index: int
    time: float
    position: float
    duration_ms: float
    rate: float
    amplitude: float
    pan: float
    density_hz: float


@dataclass(frozen=True)
class GranularControlFrame:
    time: np.ndarray
    position: np.ndarray
    duration_ms: np.ndarray
    rate: np.ndarray
    amplitude: np.ndarray
    pan: np.ndarray
    density_hz: np.ndarray
    metadata: dict[str, Any]


class QuantumGranularProjector:
    """Project QMW transport observables into bounded granular controls.

    The mapping is explicit and musical, not a physical identity:

      excitation center     -> buffer position
      site entropy          -> grain duration
      net current direction -> playback rate
      strongest site weight -> amplitude
      current center        -> pan
      current activity      -> grain density

    The projector uses only bounded or saturating transforms, so live mode does
    not require future samples for min/max normalization.
    """

    def __init__(
        self,
        *,
        duration_min_ms: float = 18.0,
        duration_max_ms: float = 180.0,
        rate_min: float = 0.5,
        rate_max: float = 2.0,
        amplitude_min: float = 0.08,
        amplitude_max: float = 0.9,
        density_min_hz: float = 2.0,
        density_max_hz: float = 70.0,
        current_scale: float = 1.0,
    ) -> None:
        if current_scale <= 0.0:
            raise ValueError("current_scale must be positive")
        self.duration_min_ms = float(duration_min_ms)
        self.duration_max_ms = float(duration_max_ms)
        self.rate_min = float(rate_min)
        self.rate_max = float(rate_max)
        self.amplitude_min = float(amplitude_min)
        self.amplitude_max = float(amplitude_max)
        self.density_min_hz = float(density_min_hz)
        self.density_max_hz = float(density_max_hz)
        self.current_scale = float(current_scale)

    @staticmethod
    def _normalized_site_distribution(populations: np.ndarray) -> np.ndarray:
        p = np.clip(np.asarray(populations, dtype=float), 0.0, None)
        total = float(np.sum(p))
        if total <= 1e-15:
            return np.full_like(p, 1.0 / max(1, p.size))
        return p / total

    @staticmethod
    def _site_entropy(populations: np.ndarray) -> float:
        p = QuantumGranularProjector._normalized_site_distribution(populations)
        nonzero = p[p > 1e-15]
        if p.size <= 1:
            return 0.0
        return float(-np.sum(nonzero * np.log(nonzero)) / np.log(p.size))

    @staticmethod
    def _population_center(populations: np.ndarray) -> float:
        p = QuantumGranularProjector._normalized_site_distribution(populations)
        if p.size <= 1:
            return 0.5
        positions = np.linspace(0.0, 1.0, p.size)
        return float(np.dot(positions, p))

    @staticmethod
    def _current_descriptors(currents: np.ndarray) -> tuple[float, float, float]:
        j = np.asarray(currents, dtype=float)
        if j.size == 0:
            return 0.0, 0.5, 0.0
        magnitude = np.abs(j)
        activity = float(np.sum(magnitude))
        if activity <= 1e-15:
            return 0.0, 0.5, 0.0
        direction = float(np.clip(np.sum(j) / activity, -1.0, 1.0))
        edge_positions = (np.arange(j.size, dtype=float) + 0.5) / j.size
        center = float(np.dot(edge_positions, magnitude) / activity)
        return direction, center, activity

    def _map(
        self,
        populations: np.ndarray,
        currents: np.ndarray,
        *,
        index: int,
        time: float,
    ) -> GranularControl:
        center = self._population_center(populations)
        entropy = self._site_entropy(populations)
        direction, current_center, current_activity = self._current_descriptors(currents)

        duration = self.duration_min_ms + entropy * (
            self.duration_max_ms - self.duration_min_ms
        )

        # Exponential rate mapping makes zero current exactly 1x when using
        # the default symmetric 0.5..2.0 range.
        if self.rate_min <= 0.0 or self.rate_max <= 0.0:
            raise ValueError("grain rates must be positive")
        log_min = np.log(self.rate_min)
        log_max = np.log(self.rate_max)
        rate = float(np.exp(log_min + 0.5 * (direction + 1.0) * (log_max - log_min)))

        strongest = float(np.clip(np.max(populations), 0.0, 1.0))
        amplitude = self.amplitude_min + strongest * (
            self.amplitude_max - self.amplitude_min
        )
        pan = float(np.clip(2.0 * current_center - 1.0, -1.0, 1.0))

        density_norm = float(np.tanh(current_activity / self.current_scale))
        density = self.density_min_hz + density_norm * (
            self.density_max_hz - self.density_min_hz
        )

        return GranularControl(
            index=int(index),
            time=float(time),
            position=float(np.clip(center, 0.0, 1.0)),
            duration_ms=float(duration),
            rate=rate,
            amplitude=float(amplitude),
            pan=pan,
            density_hz=float(density),
        )

    def project_state(self, frame: QuantumStateFrame) -> GranularControl:
        try:
            populations = frame.arrays["site_populations"]
            currents = frame.arrays["edge_currents"]
        except KeyError as exc:
            raise KeyError(
                "live granular projection requires site_populations and edge_currents"
            ) from exc

        index = int(frame.metadata.get("state_revision", 0))
        return self._map(
            np.asarray(populations, dtype=float),
            np.asarray(currents, dtype=float),
            index=index,
            time=float(frame.t),
        )

    def project(self, frame: PhysicsFrame) -> GranularControlFrame:
        try:
            populations = np.asarray(
                frame.observables["site_populations"], dtype=float
            )
            currents = np.asarray(
                frame.observables["edge_currents"], dtype=float
            )
        except KeyError as exc:
            raise KeyError(
                "PhysicsFrame granular projection requires site_populations "
                "and edge_currents"
            ) from exc

        if populations.shape[0] != frame.samples or currents.shape[0] != frame.samples:
            raise ValueError("granular source arrays must match PhysicsFrame sample count")

        controls = [
            self._map(
                populations[i],
                currents[i],
                index=i,
                time=float(frame.t[i]),
            )
            for i in range(frame.samples)
        ]

        return GranularControlFrame(
            time=frame.t.copy(),
            position=np.asarray([c.position for c in controls], dtype=float),
            duration_ms=np.asarray([c.duration_ms for c in controls], dtype=float),
            rate=np.asarray([c.rate for c in controls], dtype=float),
            amplitude=np.asarray([c.amplitude for c in controls], dtype=float),
            pan=np.asarray([c.pan for c in controls], dtype=float),
            density_hz=np.asarray([c.density_hz for c in controls], dtype=float),
            metadata={
                "projector": type(self).__name__,
                "sources": {
                    "position": "site_populations:center",
                    "duration_ms": "site_populations:entropy",
                    "rate": "edge_currents:net_direction",
                    "amplitude": "site_populations:max",
                    "pan": "edge_currents:center",
                    "density_hz": "edge_currents:activity",
                },
                "note": "Granular controls are musical projections, not quantum observables.",
            },
        )
