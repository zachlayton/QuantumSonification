"""Explicit, downstream granular-control projection for an XY trajectory."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .xy import Array, QuantumTrajectory, _readonly


def _scale(values: Array, lower: float, upper: float, *, fallback: float | None = None) -> Array:
    source = np.asarray(values, dtype=float)
    minimum = float(np.min(source))
    maximum = float(np.max(source))
    if maximum - minimum <= 1.0e-12:
        value = (lower + upper) * 0.5 if fallback is None else float(fallback)
        return np.full(source.shape, value, dtype=float)
    return lower + (source - minimum) * (upper - lower) / (maximum - minimum)


@dataclass(frozen=True)
class GrainMapping:
    """Bounded, declared mappings from transport observables to grain controls.

    These ranges and choices are compositional.  They do not make grain
    parameters physical observables.
    """

    duration_ms: tuple[float, float] = (22.0, 180.0)
    rate: tuple[float, float] = (0.67, 1.5)
    amplitude: tuple[float, float] = (0.04, 0.55)
    density_hz: tuple[float, float] = (2.0, 36.0)

    def __post_init__(self) -> None:
        for name in ("duration_ms", "rate", "amplitude", "density_hz"):
            lower, upper = (float(value) for value in getattr(self, name))
            if not np.isfinite(lower) or not np.isfinite(upper) or lower < 0.0 or upper <= lower:
                raise ValueError(f"{name} must be a finite, increasing nonnegative range.")
            object.__setattr__(self, name, (lower, upper))


@dataclass(frozen=True)
class GrainControlTrajectory:
    """One declared musical projection of :class:`QuantumTrajectory`."""

    time: Array
    position: Array
    duration_ms: Array
    rate: Array
    amplitude: Array
    pan: Array
    density_hz: Array
    mapping: GrainMapping

    def __post_init__(self) -> None:
        arrays = {
            "time": self.time,
            "position": self.position,
            "duration_ms": self.duration_ms,
            "rate": self.rate,
            "amplitude": self.amplitude,
            "pan": self.pan,
            "density_hz": self.density_hz,
        }
        length = np.asarray(self.time).size
        if length < 2:
            raise ValueError("a control trajectory needs at least two samples.")
        for name, values in arrays.items():
            array = np.asarray(values, dtype=float)
            if array.shape != (length,) or not np.all(np.isfinite(array)):
                raise ValueError(f"{name} must be a finite one-dimensional trajectory.")
            object.__setattr__(self, name, _readonly(array, dtype=float))

    @property
    def samples(self) -> int:
        return int(self.time.size)

    def validate(self) -> dict[str, bool]:
        return {
            "position_bounded": bool(np.all((0.0 <= self.position) & (self.position <= 1.0))),
            "duration_positive": bool(np.all(self.duration_ms > 0.0)),
            "rate_positive": bool(np.all(self.rate > 0.0)),
            "amplitude_bounded": bool(np.all((0.0 <= self.amplitude) & (self.amplitude <= 1.0))),
            "pan_bounded": bool(np.all((-1.0 <= self.pan) & (self.pan <= 1.0))),
            "density_positive": bool(np.all(self.density_hz > 0.0)),
        }


def project_grains(
    trajectory: QuantumTrajectory,
    *,
    mapping: GrainMapping | None = None,
) -> GrainControlTrajectory:
    """Map dynamic transport quantities into a bounded granular control frame.

    - excitation-population center -> source-buffer position
    - site-population entropy -> grain duration
    - signed net chain current -> playback rate
    - maximum site population -> amplitude
    - center of edge-current activity -> stereo pan
    - total edge-current activity -> grain density
    """
    if not isinstance(trajectory, QuantumTrajectory):
        raise TypeError("trajectory must be a QuantumTrajectory.")
    selected = mapping if mapping is not None else GrainMapping()
    if not isinstance(selected, GrainMapping):
        raise TypeError("mapping must be a GrainMapping or None.")
    center = trajectory.population_center / float(trajectory.model.qubits - 1)
    entropy = trajectory.population_entropy
    edge_current = trajectory.edge_current_left_to_right
    signed_transport = edge_current.sum(axis=1)
    activity = np.abs(edge_current)
    activity_total = activity.sum(axis=1)
    edge_midpoints = np.arange(trajectory.model.qubits - 1, dtype=float) + 0.5
    activity_center = np.divide(
        activity @ edge_midpoints,
        activity_total,
        out=trajectory.population_center.copy(),
        where=activity_total > 1.0e-12,
    )
    return GrainControlTrajectory(
        time=trajectory.time,
        position=np.clip(center, 0.0, 1.0),
        duration_ms=_scale(entropy, *selected.duration_ms),
        rate=_scale(signed_transport, *selected.rate),
        amplitude=_scale(trajectory.site_populations.max(axis=1), *selected.amplitude),
        pan=np.clip((activity_center / float(trajectory.model.qubits - 1)) * 2.0 - 1.0, -1.0, 1.0),
        density_hz=_scale(activity_total, *selected.density_hz, fallback=selected.density_hz[0]),
        mapping=selected,
    )
