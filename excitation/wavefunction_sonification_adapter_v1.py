"""Project continuous wavefunction frames into short spatial grain events.

Every grain is a fresh micro-event.  There is no sustained chord or oscillator
state in this adapter.  The default renderer contract specifies a 5 ms decay.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
import math
import time
from typing import Any, Iterable, Protocol

import numpy as np

from excitation.wavefunction_sources_v1 import WavefunctionFrame
from excitation.grw_wavefunction_source_v1 import GRWWavefunctionEvent


class OSCClient(Protocol):
    def send_message(self, address: str, value: Any) -> None: ...


@dataclass(frozen=True)
class WavefunctionGrainConfig:
    grains_per_frame: int = 16
    decay_ms: float = 5.0
    amplitude_gain: float = 0.32
    adaptive_rate: bool = False
    min_grains_per_frame: int = 0
    max_grains_per_frame: int = 12
    density_change_sensitivity: float = 32.0
    current_weight: float = 0.25
    rate_smoothing: float = 0.35

    def __post_init__(self) -> None:
        if self.grains_per_frame < 0 or self.grains_per_frame > 128:
            raise ValueError("grains_per_frame must lie in [0, 128]")
        if self.decay_ms <= 0.0:
            raise ValueError("decay_ms must be positive")
        if self.amplitude_gain < 0.0:
            raise ValueError("amplitude_gain must be non-negative")
        if self.min_grains_per_frame < 0:
            raise ValueError("min_grains_per_frame must be non-negative")
        if self.max_grains_per_frame > 128 or self.max_grains_per_frame < self.min_grains_per_frame:
            raise ValueError("adaptive grain range must satisfy 0 <= min <= max <= 128")
        if self.density_change_sensitivity <= 0.0:
            raise ValueError("density_change_sensitivity must be positive")
        if not 0.0 <= self.current_weight <= 1.0:
            raise ValueError("current_weight must lie in [0, 1]")
        if not 0.0 < self.rate_smoothing <= 1.0:
            raise ValueError("rate_smoothing must lie in (0, 1]")


@dataclass(frozen=True)
class WavefunctionGrain:
    frame_id: int
    grain_id: int
    x: float
    y: float
    z: float
    amplitude: float
    phase: float
    current_x: float
    current_y: float
    current_z: float
    energy: float
    decay_ms: float

    def packet(self) -> list[float | int]:
        return [
            self.frame_id,
            self.grain_id,
            self.x,
            self.y,
            self.z,
            self.amplitude,
            self.phase,
            self.current_x,
            self.current_y,
            self.current_z,
            self.energy,
            self.decay_ms,
        ]


@dataclass(frozen=True)
class WavefunctionCloudFrame:
    frame_id: int
    time: float
    norm: float
    center: tuple[float, float, float]
    spread: tuple[float, float, float]
    grains: tuple[WavefunctionGrain, ...]
    activity: float = 0.0
    density_change: float = 0.0
    current_activity: float = 0.0

    def packet(self) -> list[float | int]:
        return [
            self.frame_id,
            self.time,
            len(self.grains),
            self.norm,
            *self.center,
            *self.spread,
            self.activity,
            self.density_change,
            self.current_activity,
        ]


def _pad3(values: Iterable[float], fill: float = 0.0) -> tuple[float, float, float]:
    result = list(values)[:3]
    result.extend([fill] * (3 - len(result)))
    return tuple(float(value) for value in result)  # type: ignore[return-value]


def _coordinate_moments(
    frame: WavefunctionFrame,
) -> tuple[tuple[float, float, float], tuple[float, float, float]]:
    probability = np.asarray(frame.probability, dtype=np.float64)
    measure = float(frame.norm) / max(float(np.sum(probability)), 1e-15)
    meshes = np.meshgrid(*frame.coordinates, indexing="ij", sparse=True)
    centers = []
    spreads = []
    for axis in meshes:
        center = float(np.sum(probability * axis) * measure / max(frame.norm, 1e-15))
        variance = float(
            np.sum(probability * (axis - center) ** 2)
            * measure
            / max(frame.norm, 1e-15)
        )
        centers.append(center)
        spreads.append(math.sqrt(max(0.0, variance)))
    return _pad3(centers), _pad3(spreads)


def _normalized_position(index: tuple[int, ...], shape: tuple[int, ...]) -> tuple[float, float, float]:
    values = [
        2.0 * cell / max(size - 1, 1) - 1.0
        for cell, size in zip(index, shape)
    ]
    return _pad3(values)


def grains_from_wavefunction_frame(
    frame: WavefunctionFrame,
    frame_id: int,
    config: WavefunctionGrainConfig = WavefunctionGrainConfig(),
) -> WavefunctionCloudFrame:
    """Systematically sample probability mass into deterministic grain events."""

    probability = np.asarray(frame.probability, dtype=np.float64)
    flat_probability = np.maximum(probability.reshape(-1), 0.0)
    total = float(np.sum(flat_probability))
    if total <= 1e-15:
        raise ValueError("wavefunction frame has no probability mass")
    weights = flat_probability / total
    cdf = np.cumsum(weights)

    # A golden-ratio phase advances the stratified samples without random
    # flicker; adjacent frames explore the complete cloud deterministically.
    count = config.grains_per_frame
    if count == 0:
        flat_indices = np.empty(0, dtype=np.int64)
    else:
        offset = ((frame_id * 0.6180339887498949) % 1.0) / count
        quantiles = (np.arange(count, dtype=np.float64) + 0.5) / count + offset
        quantiles %= 1.0
        flat_indices = np.searchsorted(cdf, quantiles, side="left")
        flat_indices = np.minimum(flat_indices, flat_probability.size - 1)

    peak_probability = max(float(np.max(flat_probability)), 1e-15)
    currents = tuple(np.asarray(value, dtype=np.float64) for value in frame.probability_current)
    current_magnitude = np.sqrt(sum(value * value for value in currents))
    peak_current = max(float(np.max(current_magnitude)), 1e-15)
    energy_density = np.asarray(frame.energy_density, dtype=np.float64)
    peak_energy = max(float(np.max(np.abs(energy_density))), 1e-15)

    grains = []
    for grain_id, flat_index in enumerate(flat_indices):
        grid_index = np.unravel_index(int(flat_index), probability.shape)
        x, y, z = _normalized_position(grid_index, probability.shape)
        local_probability = float(probability[grid_index])
        amplitude = float(
            np.clip(
                config.amplitude_gain * math.sqrt(local_probability / peak_probability),
                0.0,
                1.0,
            )
        )
        local_current = _pad3(
            (float(component[grid_index]) / peak_current for component in currents)
        )
        grains.append(
            WavefunctionGrain(
                frame_id=int(frame_id),
                grain_id=int(grain_id),
                x=x,
                y=y,
                z=z,
                amplitude=amplitude,
                phase=float(np.angle(frame.psi[grid_index]) / math.pi),
                current_x=float(np.clip(local_current[0], -1.0, 1.0)),
                current_y=float(np.clip(local_current[1], -1.0, 1.0)),
                current_z=float(np.clip(local_current[2], -1.0, 1.0)),
                energy=float(np.clip(abs(energy_density[grid_index]) / peak_energy, 0.0, 1.0)),
                decay_ms=float(config.decay_ms),
            )
        )

    center, spread = _coordinate_moments(frame)
    return WavefunctionCloudFrame(
        frame_id=int(frame_id),
        time=float(frame.time),
        norm=float(frame.norm),
        center=center,
        spread=spread,
        grains=tuple(grains),
    )


class WavefunctionSonificationAdapter:
    PREFIX = "/qmw/wavefunction/cloud"

    def __init__(
        self,
        clients: Iterable[OSCClient] = (),
        config: WavefunctionGrainConfig = WavefunctionGrainConfig(),
    ) -> None:
        self.clients = tuple(client for client in clients if client is not None)
        self.config = config
        self.frame_id = 0
        self._previous_probability: np.ndarray | None = None
        self._smoothed_activity: float | None = None

    def _adaptive_activity(self, frame: WavefunctionFrame) -> tuple[float, float, float]:
        probability = np.maximum(np.asarray(frame.probability, dtype=np.float64).reshape(-1), 0.0)
        probability /= max(float(np.sum(probability)), 1e-15)
        if self._previous_probability is None or self._previous_probability.shape != probability.shape:
            density_change = 0.0
        else:
            # Total-variation distance: the fraction of probability mass that
            # has redistributed since the preceding rendered frame.
            density_change = 0.5 * float(np.sum(np.abs(probability - self._previous_probability)))
        self._previous_probability = probability.copy()

        temporal_activity = 1.0 - math.exp(
            -self.config.density_change_sensitivity * max(0.0, density_change)
        )
        current_activity = float(np.clip(frame.descriptor.current, 0.0, 1.0))
        raw_activity = (
            (1.0 - self.config.current_weight) * temporal_activity
            + self.config.current_weight * current_activity
        )
        if self._smoothed_activity is None:
            self._smoothed_activity = raw_activity
        else:
            smoothing = self.config.rate_smoothing
            self._smoothed_activity += smoothing * (raw_activity - self._smoothed_activity)
        return float(np.clip(self._smoothed_activity, 0.0, 1.0)), density_change, current_activity

    def _send(self, suffix: str, value: Any) -> None:
        for client in self.clients:
            client.send_message(f"{self.PREFIX}/{suffix}", value)

    @staticmethod
    def grain_onset_fractions(frame_id: int, grain_count: int) -> tuple[float, ...]:
        """Deterministic Poisson-like onsets within one physics frame.

        The extra final gap prevents the last grain from being forced onto the
        frame boundary.  This removes the audible 30 Hz packetization without
        introducing nondeterministic random timing.
        """

        if grain_count <= 0:
            return ()
        gaps = []
        for index in range(grain_count + 1):
            phase = (frame_id + 1) * 0.7548776662466927 + (index + 1) * 0.5698402909980532
            uniform = (math.sin(phase * 12.9898) * 43758.5453) % 1.0
            gaps.append(-math.log(max(1e-9, 1.0 - uniform)))
        total = max(sum(gaps), 1e-12)
        cumulative = 0.0
        onsets = []
        for gap in gaps[:-1]:
            cumulative += gap
            onsets.append(cumulative / total)
        return tuple(onsets)

    def publish_frame(self, frame: WavefunctionFrame) -> WavefunctionCloudFrame:
        if self.config.adaptive_rate:
            activity, density_change, current_activity = self._adaptive_activity(frame)
            span = self.config.max_grains_per_frame - self.config.min_grains_per_frame
            grain_count = int(round(self.config.min_grains_per_frame + span * activity))
            frame_config = replace(self.config, grains_per_frame=grain_count)
        else:
            activity = density_change = 0.0
            current_activity = float(np.clip(frame.descriptor.current, 0.0, 1.0))
            frame_config = self.config
        cloud = grains_from_wavefunction_frame(frame, self.frame_id, frame_config)
        cloud = replace(
            cloud,
            activity=activity,
            density_change=density_change,
            current_activity=current_activity,
        )
        self._send("frame", cloud.packet())
        for grain in cloud.grains:
            self._send("grain", grain.packet())
        self._send("end", [cloud.frame_id, len(cloud.grains)])
        self.frame_id += 1
        return cloud

    def publish_frame_timed(
        self,
        frame: WavefunctionFrame,
        frame_duration: float,
    ) -> WavefunctionCloudFrame:
        """Publish grains at irregular onsets spread across a physics frame."""

        if frame_duration <= 0.0:
            raise ValueError("frame_duration must be positive")
        # Build through the same adaptive path without emitting a burst.
        if self.config.adaptive_rate:
            activity, density_change, current_activity = self._adaptive_activity(frame)
            span = self.config.max_grains_per_frame - self.config.min_grains_per_frame
            grain_count = int(round(self.config.min_grains_per_frame + span * activity))
            frame_config = replace(self.config, grains_per_frame=grain_count)
        else:
            activity = density_change = 0.0
            current_activity = float(np.clip(frame.descriptor.current, 0.0, 1.0))
            frame_config = self.config
        cloud = replace(
            grains_from_wavefunction_frame(frame, self.frame_id, frame_config),
            activity=activity,
            density_change=density_change,
            current_activity=current_activity,
        )

        self._send("frame", cloud.packet())
        started = time.monotonic()
        onsets = self.grain_onset_fractions(cloud.frame_id, len(cloud.grains))
        for onset, grain in zip(onsets, cloud.grains):
            target = started + onset * frame_duration
            time.sleep(max(0.0, target - time.monotonic()))
            self._send("grain", grain.packet())
        self._send("end", [cloud.frame_id, len(cloud.grains)])
        self.frame_id += 1
        return cloud

    def publish_grw_event(
        self,
        event: GRWWavefunctionEvent,
        *,
        min_grains: int = 1,
        max_grains: int = 48,
    ) -> WavefunctionCloudFrame:
        """Render one actual localization from its delta field at jump time."""

        if min_grains < 0 or max_grains < min_grains or max_grains > 128:
            raise ValueError("GRW grain range must satisfy 0 <= min <= max <= 128")
        salience = float(np.clip(event.total_variation, 0.0, 1.0))
        grain_count = int(round(min_grains + (max_grains - min_grains) * math.sqrt(salience)))
        delta_currents = tuple(
            np.asarray(after, dtype=np.float64) - np.asarray(before, dtype=np.float64)
            for before, after in zip(
                event.frame_before.probability_current,
                event.frame_after.probability_current,
            )
        )
        change_frame = replace(
            event.frame_after,
            probability=np.abs(event.delta_probability),
            probability_current=delta_currents,
            metadata={
                **event.frame_after.metadata,
                "sonification_field": "abs_delta_probability",
            },
        )
        event_config = replace(
            self.config,
            adaptive_rate=False,
            grains_per_frame=grain_count,
            amplitude_gain=self.config.amplitude_gain * math.sqrt(salience),
        )
        cloud = replace(
            grains_from_wavefunction_frame(change_frame, event.event_id, event_config),
            activity=salience,
            density_change=salience,
            current_activity=float(np.clip(event.frame_after.descriptor.current, 0.0, 1.0)),
        )
        self._send("frame", cloud.packet())
        for grain in cloud.grains:
            self._send("grain", grain.packet())
        self._send("end", [cloud.frame_id, len(cloud.grains)])
        self.frame_id = max(self.frame_id, event.event_id + 1)
        return cloud


__all__ = [
    "WavefunctionCloudFrame",
    "WavefunctionGrain",
    "WavefunctionGrainConfig",
    "WavefunctionSonificationAdapter",
    "grains_from_wavefunction_frame",
]
