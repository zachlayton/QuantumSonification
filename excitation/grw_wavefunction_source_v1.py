"""Exact-jump GRW wrapper for numerically propagated wavefunctions.

The wrapper owns one Poisson clock and applies Gaussian localization directly
to the wrapped source's complex field.  It does not invent renderer events:
between jumps the wrapped source follows its ordinary Schrödinger evolution.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
import math
from typing import Any

import numpy as np

from excitation.wavefunction_sources_v1 import (
    WavefunctionDescriptor,
    WavefunctionFrame,
    WavefunctionSource,
)


@dataclass(frozen=True)
class GRWWavefunctionConfig:
    enabled: bool = True
    rate_hz: float = 1.0
    localization_width: float = 0.75
    constituent_scale: float = 1.0
    seed: int = 23

    def __post_init__(self) -> None:
        if self.rate_hz < 0.0:
            raise ValueError("rate_hz must be non-negative")
        if self.localization_width <= 0.0:
            raise ValueError("localization_width must be positive")
        if self.constituent_scale < 0.0:
            raise ValueError("constituent_scale must be non-negative")

    @property
    def total_rate_hz(self) -> float:
        return self.rate_hz * self.constituent_scale


@dataclass(frozen=True)
class GRWWavefunctionEvent:
    event_id: int
    logical_time: float
    waiting_time: float
    center: tuple[float, ...]
    localization_width: float
    total_variation: float
    probability_peak_before: float
    probability_peak_after: float
    frame_before: WavefunctionFrame
    frame_after: WavefunctionFrame
    delta_probability: np.ndarray


class GRWWavefunctionSource:
    """Wrap a mutable split-step source with exact-time GRW localizations.

    The wrapped source must expose its current complex array as ``psi``.  This
    includes PotentialWavefunctionSource and its free-packet/harmonic variants.
    Analytic sources that reconstruct psi from a closed formula on every frame
    cannot retain a collapse and are rejected explicitly.
    """

    def __init__(
        self,
        source: WavefunctionSource,
        config: GRWWavefunctionConfig = GRWWavefunctionConfig(),
    ) -> None:
        if not hasattr(source, "psi"):
            raise TypeError(
                "GRWWavefunctionSource requires a mutable numerical source with a psi field"
            )
        self.source = source
        self.config = config
        self.rng = np.random.default_rng(config.seed)
        self.logical_time = float(getattr(source, "time", 0.0))
        self.event_count = 0
        self.last_event_time = self.logical_time
        self.events: tuple[GRWWavefunctionEvent, ...] = ()
        self.last_event: GRWWavefunctionEvent | None = None
        self.next_event_time = math.inf
        self._schedule_from_now()

    @property
    def next_event_seconds(self) -> float:
        if not np.isfinite(self.next_event_time):
            return math.inf
        return max(0.0, self.next_event_time - self.logical_time)

    def _schedule_from_now(self) -> None:
        rate = self.config.total_rate_hz
        if not self.config.enabled or rate <= 0.0:
            self.next_event_time = math.inf
            return
        self.next_event_time = self.logical_time + float(self.rng.exponential(1.0 / rate))

    def sample_waiting_time(self, size: int | None = None) -> np.ndarray | float:
        rate = self.config.total_rate_hz
        if rate <= 0.0:
            return math.inf if size is None else np.full(size, math.inf)
        return self.rng.exponential(1.0 / rate, size=size)

    def reset(self) -> None:
        self.source.reset()
        self.rng = np.random.default_rng(self.config.seed)
        self.logical_time = float(getattr(self.source, "time", 0.0))
        self.event_count = 0
        self.last_event_time = self.logical_time
        self.events = ()
        self.last_event = None
        self._schedule_from_now()

    @staticmethod
    def _cell_measure(frame: WavefunctionFrame) -> float:
        spacings = []
        for coordinate in frame.coordinates:
            values = np.asarray(coordinate, dtype=np.float64)
            spacings.append(float(np.mean(np.diff(values))))
        return float(abs(np.prod(spacings)))

    def _sample_center(self, frame: WavefunctionFrame) -> tuple[float, ...]:
        probability = np.maximum(np.asarray(frame.probability, dtype=np.float64), 0.0)
        weights = probability.reshape(-1)
        weights /= max(float(np.sum(weights)), 1e-15)
        flat_index = int(self.rng.choice(weights.size, p=weights))
        grid_index = np.unravel_index(flat_index, probability.shape)
        # For L_x(q) ~ exp[-|q-x|^2/(4 r_C^2)], the center distribution is
        # the convolution of |psi(q)|^2 with N(0, r_C^2).  Sampling q from
        # |psi|^2 and adding this Gaussian displacement samples that mixture.
        return tuple(
            float(np.asarray(axis)[grid_index[dimension]])
            + float(self.rng.normal(0.0, self.config.localization_width))
            for dimension, axis in enumerate(frame.coordinates)
        )

    def _apply_jump(self, frame_before: WavefunctionFrame) -> GRWWavefunctionEvent:
        center = self._sample_center(frame_before)
        meshes = np.meshgrid(*frame_before.coordinates, indexing="ij", sparse=True)
        distance_squared: Any = 0.0
        for axis, location in zip(meshes, center):
            distance_squared = distance_squared + (axis - location) ** 2
        localization = np.exp(
            -distance_squared / (4.0 * self.config.localization_width**2)
        )
        collapsed = np.asarray(frame_before.psi, dtype=np.complex128) * localization
        measure = self._cell_measure(frame_before)
        norm = math.sqrt(max(float(np.sum(np.abs(collapsed) ** 2) * measure), 1e-30))
        collapsed /= norm
        setattr(self.source, "psi", collapsed)
        raw_after = self.source.frame(0.0)

        before_mass = np.asarray(frame_before.probability, dtype=np.float64) * measure
        after_mass = np.asarray(raw_after.probability, dtype=np.float64) * measure
        delta_probability = np.asarray(raw_after.probability - frame_before.probability)
        total_variation = 0.5 * float(np.sum(np.abs(after_mass - before_mass)))
        self.event_count += 1
        waiting_time = self.logical_time - self.last_event_time

        metadata = dict(raw_after.metadata)
        metadata.update(
            grw_event_id=self.event_count,
            grw_jump_time=self.logical_time,
            grw_center=center,
            grw_localization_width=self.config.localization_width,
            grw_total_variation=total_variation,
        )
        frame_after = replace(
            raw_after,
            source=f"grw:{raw_after.source}",
            metadata=metadata,
        )
        event = GRWWavefunctionEvent(
            event_id=self.event_count,
            logical_time=self.logical_time,
            waiting_time=waiting_time,
            center=center,
            localization_width=self.config.localization_width,
            total_variation=total_variation,
            probability_peak_before=float(np.max(frame_before.probability)),
            probability_peak_after=float(np.max(frame_after.probability)),
            frame_before=frame_before,
            frame_after=frame_after,
            delta_probability=delta_probability,
        )
        self.last_event_time = self.logical_time
        self.last_event = event
        return event

    def frame(self, dt: float = 0.0) -> WavefunctionFrame:
        if dt < 0.0:
            raise ValueError("dt must be non-negative")
        end_time = self.logical_time + dt
        step_events = []

        while self.config.enabled and self.next_event_time <= end_time:
            segment = max(0.0, self.next_event_time - self.logical_time)
            frame_before = self.source.frame(segment)
            self.logical_time = self.next_event_time
            step_events.append(self._apply_jump(frame_before))
            self._schedule_from_now()

        remainder = max(0.0, end_time - self.logical_time)
        result = self.source.frame(remainder)
        self.logical_time = end_time
        self.events = tuple(step_events)

        metadata = dict(result.metadata)
        metadata.update(
            grw_enabled=self.config.enabled,
            grw_rate_hz=self.config.total_rate_hz,
            grw_localization_width=self.config.localization_width,
            grw_jump_count=len(step_events),
            grw_next_event_time=self.next_event_time,
        )
        if step_events:
            metadata.update(
                grw_event_id=step_events[-1].event_id,
                grw_jump_time=step_events[-1].logical_time,
                grw_center=step_events[-1].center,
                grw_total_variation=step_events[-1].total_variation,
            )
        return replace(result, source=f"grw:{result.source}", metadata=metadata)

    def descriptor(self, dt: float) -> WavefunctionDescriptor:
        return self.frame(dt).descriptor


__all__ = [
    "GRWWavefunctionConfig",
    "GRWWavefunctionEvent",
    "GRWWavefunctionSource",
]
