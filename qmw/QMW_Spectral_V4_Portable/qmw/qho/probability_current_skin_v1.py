"""Read-only QHO probability-current to finite-width skin bridge.

This module makes the state -> flow -> event seam explicit for one-dimensional
complex wavefunction frames. ``WavefunctionFrame.probability_current`` is the
authoritative physical current; a ``SkinField1D`` supplies an oriented,
finite-width boundary; and the flux threshold is an optional downstream event
adapter. No function here evolves, measures, collapses, or writes back to a
wavefunction.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Any

import numpy as np

from qmw.qmw_skin import SkinEncounter1D, SkinField1D, evaluate_skin_encounter
from qmw.qmw_probability_flow import flow_from_observed_current_1d


EPS = 1.0e-12


def _finite_vector(name: str, values: Any) -> np.ndarray:
    result = np.asarray(values, dtype=float)
    if result.ndim != 1 or result.size < 3 or not np.all(np.isfinite(result)):
        raise ValueError(f"{name} must be a finite one-dimensional field of length >= 3.")
    return np.array(result, copy=True)


@dataclass(frozen=True)
class ProbabilityCurrentFlow1D:
    """A 1D probability-flow observation derived from a native wavefunction frame."""

    time: float
    coordinates: np.ndarray
    density: np.ndarray
    phase: np.ndarray
    current: np.ndarray
    source: str = "wavefunction"

    def __post_init__(self) -> None:
        coordinates = _finite_vector("coordinates", self.coordinates)
        if not np.all(np.diff(coordinates) > 0.0):
            raise ValueError("coordinates must be strictly increasing.")
        density = _finite_vector("density", self.density)
        phase = _finite_vector("phase", self.phase)
        current = _finite_vector("current", self.current)
        if any(field.shape != coordinates.shape for field in (density, phase, current)):
            raise ValueError("density, phase, and current must match coordinates.")
        if np.any(density < 0.0):
            raise ValueError("density must be nonnegative.")
        if not math.isfinite(float(self.time)):
            raise ValueError("time must be finite.")
        object.__setattr__(self, "coordinates", coordinates)
        object.__setattr__(self, "density", density)
        object.__setattr__(self, "phase", phase)
        object.__setattr__(self, "current", current)


def observe_probability_current_1d(frame: Any) -> ProbabilityCurrentFlow1D:
    """Expose a native one-dimensional frame as the skin's read-only contract.

    The input must provide the existing ``WavefunctionFrame`` fields
    ``dimension``, ``coordinates``, ``probability``, ``phase``,
    ``probability_current``, and ``time``. It deliberately does not estimate
    current from density, because a uniform density can still carry current
    through a phase gradient.
    """

    if int(frame.dimension) != 1:
        raise ValueError("Probability-current skin observation requires a one-dimensional frame.")
    if len(frame.coordinates) != 1 or len(frame.probability_current) != 1:
        raise ValueError("One-dimensional frame must provide exactly one coordinate and current axis.")
    shared = flow_from_observed_current_1d(
        frame.probability,
        frame.phase,
        frame.probability_current[0],
        frame.coordinates[0],
        time=float(frame.time),
    )
    return ProbabilityCurrentFlow1D(
        time=shared.time,
        coordinates=shared.coordinates,
        density=shared.density,
        phase=shared.phase,
        current=shared.current,
        source=str(getattr(frame, "source", "wavefunction")),
    )


def observe_skin_boundary(
    frame: Any,
    skin: SkinField1D,
    *,
    sensitivity: float = 1.0,
) -> SkinEncounter1D:
    """Observe signed probability passage through ``skin`` without state mutation."""

    return evaluate_skin_encounter(
        observe_probability_current_1d(frame), skin, sensitivity=sensitivity
    )


@dataclass(frozen=True)
class FluxThresholdState:
    """Carry-over state for a downstream accumulated-flux event adapter."""

    accumulated_flux: float = 0.0
    emitted_events: int = 0

    def __post_init__(self) -> None:
        if not math.isfinite(float(self.accumulated_flux)) or self.accumulated_flux < 0.0:
            raise ValueError("accumulated_flux must be finite and nonnegative.")
        if int(self.emitted_events) < 0:
            raise ValueError("emitted_events must be nonnegative.")


@dataclass(frozen=True)
class FluxThresholdEvent:
    """One sonic/control event caused by enough signed-boundary passage."""

    time: float
    sequence: int
    direction: int
    threshold: float
    directional_flux: float


@dataclass(frozen=True)
class FluxThresholdStep:
    """Result of advancing accumulated passage by one observation interval."""

    state: FluxThresholdState
    passage: float
    events: tuple[FluxThresholdEvent, ...]


def advance_flux_threshold(
    state: FluxThresholdState,
    encounter: SkinEncounter1D,
    *,
    dt: float,
    threshold: float,
) -> FluxThresholdStep:
    """Accumulate boundary passage and retain threshold remainder after events.

    ``abs(encounter.directional_flux) * dt`` is the signed-boundary flux
    magnitude integrated over the observation interval. A threshold crossing
    creates an adapter event; it is not a quantum measurement. Retaining the
    remainder prevents arbitrary phase resetting and permits multiple events
    during a high-flux interval.
    """

    dt = float(dt)
    threshold = float(threshold)
    if not math.isfinite(dt) or dt < 0.0:
        raise ValueError("dt must be finite and nonnegative.")
    if not math.isfinite(threshold) or threshold <= 0.0:
        raise ValueError("threshold must be finite and greater than zero.")
    directional_flux = float(encounter.directional_flux)
    if not math.isfinite(directional_flux):
        raise ValueError("encounter directional_flux must be finite.")

    passage = abs(directional_flux) * dt
    accumulated = float(state.accumulated_flux) + passage
    event_count = int(math.floor((accumulated + EPS) / threshold))
    remainder = accumulated - (event_count * threshold)
    if remainder < EPS:
        remainder = 0.0
    direction = 1 if directional_flux > EPS else (-1 if directional_flux < -EPS else 0)
    events = tuple(
        FluxThresholdEvent(
            time=float(encounter.time),
            sequence=int(state.emitted_events) + index + 1,
            direction=direction,
            threshold=threshold,
            directional_flux=directional_flux,
        )
        for index in range(event_count)
    )
    return FluxThresholdStep(
        state=FluxThresholdState(
            accumulated_flux=remainder,
            emitted_events=int(state.emitted_events) + event_count,
        ),
        passage=passage,
        events=events,
    )


__all__ = [
    "FluxThresholdEvent",
    "FluxThresholdState",
    "FluxThresholdStep",
    "ProbabilityCurrentFlow1D",
    "advance_flux_threshold",
    "observe_probability_current_1d",
    "observe_skin_boundary",
]
