"""Event-clocked harmonic memory development for downstream QMW adapters.

This is deliberately a control observer, not quantum evolution, measurement,
or an audio feedback implementation.  A meaningful musical event advances the
integer clock; audio samples and quantum-frame arrivals do not.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
import threading

import numpy as np

from .engine import _density


Array = np.ndarray
_EULER_GAMMA = 0.5772156649015329
_ZETA_2 = math.pi**2 / 6.0
_EPS = 1.0e-12


def _readonly(values: object) -> Array:
    result = np.array(values, dtype=float, copy=True)
    result.setflags(write=False)
    return result


@dataclass(frozen=True)
class HarmonicMemorySeries:
    """Exact harmonic-number values and bounded downstream descriptors.

    ``event_index`` is one-based and advances only when an explicit memory
    event occurs.  ``euler_sum`` and ``recursion_index`` are exposed for the
    later cross-memory stage, but this first prototype does not apply them to
    an audio feedback matrix.
    """

    event_index: int
    injection: float
    harmonic: float
    harmonic2: float
    euler_sum: float
    residual: float
    event_write: float
    persistence: float
    topology_index: float
    recursion_index: float
    instability: float
    euler_exponent: float = 1.25
    provenance: str = "derived_read_only_harmonic_memory_development_v1"

    def __post_init__(self) -> None:
        if int(self.event_index) != self.event_index or self.event_index < 1:
            raise ValueError("event_index must be a positive integer.")
        for name in (
            "injection", "harmonic", "harmonic2", "euler_sum", "residual",
            "event_write", "persistence", "topology_index", "recursion_index",
            "instability", "euler_exponent",
        ):
            value = float(getattr(self, name))
            if not math.isfinite(value):
                raise ValueError(f"{name} must be finite.")
        if self.injection <= 0.0 or self.harmonic <= 0.0 or self.harmonic2 <= 0.0:
            raise ValueError("harmonic values must be positive.")
        if self.euler_exponent <= 0.0:
            raise ValueError("euler_exponent must be positive.")
        for name in ("event_write", "persistence", "topology_index", "recursion_index", "instability"):
            if not 0.0 <= float(getattr(self, name)) <= 1.0:
                raise ValueError(f"{name} must lie in [0, 1].")
        object.__setattr__(self, "event_index", int(self.event_index))


def harmonic_memory_series(event_index: int, *, euler_exponent: float = 1.25) -> HarmonicMemorySeries:
    """Return exact finite harmonic/Euler values for one meaningful event."""

    if int(event_index) != event_index or event_index < 1:
        raise ValueError("event_index must be a positive integer.")
    exponent = float(euler_exponent)
    if not math.isfinite(exponent) or exponent <= 0.0:
        raise ValueError("euler_exponent must be finite and positive.")
    indices = np.arange(1, int(event_index) + 1, dtype=float)
    reciprocal = 1.0 / indices
    harmonic_terms = np.cumsum(reciprocal)
    harmonic = float(harmonic_terms[-1])
    harmonic2 = float(np.sum(reciprocal * reciprocal))
    euler_sum = float(np.sum(harmonic_terms / (indices**exponent)))
    residual = harmonic - math.log(float(event_index)) - _EULER_GAMMA
    # These bounded curves are musical control descriptors, separate from the
    # exact series above.  They never write back to rho or its evolution.
    persistence = 0.84 * math.tanh(harmonic / 4.0)
    topology_index = min(harmonic2 / _ZETA_2, 1.0)
    recursion_index = math.tanh(euler_sum / 5.0)
    initial_residual = 1.0 - _EULER_GAMMA
    instability = min(max(abs(residual) / initial_residual, 0.0), 1.0)
    return HarmonicMemorySeries(
        event_index=int(event_index), injection=1.0 / float(event_index),
        harmonic=harmonic, harmonic2=harmonic2, euler_sum=euler_sum,
        residual=residual, event_write=1.0 / float(event_index),
        persistence=persistence, topology_index=topology_index,
        recursion_index=recursion_index, instability=instability,
        euler_exponent=exponent,
    )


class HarmonicMemoryClock:
    """Thread-safe event clock; callers must explicitly advance it."""

    def __init__(self, event_index: int = 0, *, euler_exponent: float = 1.25) -> None:
        if int(event_index) != event_index or event_index < 0:
            raise ValueError("event_index must be a nonnegative integer.")
        if not math.isfinite(float(euler_exponent)) or euler_exponent <= 0.0:
            raise ValueError("euler_exponent must be finite and positive.")
        self._event_index = int(event_index)
        self._euler_exponent = float(euler_exponent)
        self._lock = threading.RLock()

    @property
    def event_index(self) -> int:
        with self._lock:
            return self._event_index

    def advance(self, events: int = 1) -> HarmonicMemorySeries:
        if int(events) != events or events < 1:
            raise ValueError("events must be a positive integer.")
        with self._lock:
            self._event_index += int(events)
            return harmonic_memory_series(self._event_index, euler_exponent=self._euler_exponent)

    def snapshot(self) -> HarmonicMemorySeries | None:
        with self._lock:
            if self._event_index == 0:
                return None
            return harmonic_memory_series(self._event_index, euler_exponent=self._euler_exponent)


@dataclass(frozen=True)
class HarmonicMemoryDevelopmentFrame:
    """Four-node, read-only prototype descriptors for later audio rendering.

    Nodes correspond to the four one-qubit marginal populations of a canonical
    16-dimensional four-qubit density matrix.  The frame does not instantiate
    delays, update feedback, or mutate its density input.
    """

    revision: int
    source_revision: int
    time: float
    series: HarmonicMemorySeries
    node_population: Array
    event_injection: Array
    self_persistence: Array
    delay_seconds: Array
    topology_index: float
    instability: float
    provenance: str = "derived_read_only_four_node_harmonic_memory_v1"

    def __post_init__(self) -> None:
        if int(self.revision) != self.revision or self.revision < 0:
            raise ValueError("revision must be a nonnegative integer.")
        if int(self.source_revision) != self.source_revision or self.source_revision < 0:
            raise ValueError("source_revision must be a nonnegative integer.")
        if not math.isfinite(float(self.time)):
            raise ValueError("time must be finite.")
        if not isinstance(self.series, HarmonicMemorySeries):
            raise TypeError("series must be a HarmonicMemorySeries.")
        vectors = {
            "node_population": _readonly(self.node_population),
            "event_injection": _readonly(self.event_injection),
            "self_persistence": _readonly(self.self_persistence),
            "delay_seconds": _readonly(self.delay_seconds),
        }
        if any(value.shape != (4,) or not np.all(np.isfinite(value)) for value in vectors.values()):
            raise ValueError("four-node harmonic-memory vectors must be finite length-four arrays.")
        for name in ("node_population", "event_injection", "self_persistence"):
            if np.any(vectors[name] < 0.0) or np.any(vectors[name] > 1.0):
                raise ValueError(f"{name} must lie in [0, 1].")
        if np.any(vectors["delay_seconds"] <= 0.0):
            raise ValueError("delay_seconds must be positive.")
        if not 0.0 <= float(self.topology_index) <= 1.0 or not 0.0 <= float(self.instability) <= 1.0:
            raise ValueError("topology_index and instability must lie in [0, 1].")
        object.__setattr__(self, "revision", int(self.revision))
        object.__setattr__(self, "source_revision", int(self.source_revision))
        object.__setattr__(self, "time", float(self.time))
        for name, values in vectors.items():
            object.__setattr__(self, name, values)
        object.__setattr__(self, "topology_index", float(self.topology_index))
        object.__setattr__(self, "instability", float(self.instability))


def observe_harmonic_memory_development(
    rho: object,
    *,
    revision: int,
    time: float,
    event_index: int,
    base_delay_seconds: float = 0.137,
    euler_exponent: float = 1.25,
) -> HarmonicMemoryDevelopmentFrame:
    """Observe four qubit marginals through one event-clocked memory series."""

    if int(revision) != revision or revision < 0:
        raise ValueError("revision must be a nonnegative integer.")
    if not math.isfinite(float(time)):
        raise ValueError("time must be finite.")
    base = float(base_delay_seconds)
    if not math.isfinite(base) or not 0.020 <= base <= 2.500:
        raise ValueError("base_delay_seconds must lie in [0.020, 2.500].")
    density = _density(rho)
    if density.shape != (16, 16):
        raise ValueError("four-node prototype requires a canonical 16x16 four-qubit density matrix.")
    series = harmonic_memory_series(event_index, euler_exponent=euler_exponent)
    diagonal = np.real(np.diag(density))
    node_population = np.array([
        diagonal[((np.arange(16) >> (3 - qubit)) & 1) == 1].sum()
        for qubit in range(4)
    ], dtype=float)
    event_injection = np.sqrt(np.clip(node_population, 0.0, 1.0)) * series.event_write
    self_persistence = series.persistence * (0.25 + (0.75 * node_population))
    ratios = np.array([1.0, 5.0 / 4.0, 4.0 / 3.0, 3.0 / 2.0], dtype=float)
    # A signed fixed four-node spread makes epsilon's convergence audible as
    # temporal settling without presenting random jitter as quantum dynamics.
    residual_shape = np.array([-1.0, -1.0 / 3.0, 1.0 / 3.0, 1.0], dtype=float)
    delay_seconds = base * ratios * (1.0 + (0.04 * series.instability * residual_shape))
    return HarmonicMemoryDevelopmentFrame(
        revision=int(event_index), source_revision=int(revision), time=float(time), series=series,
        node_population=node_population, event_injection=event_injection,
        self_persistence=self_persistence, delay_seconds=delay_seconds,
        topology_index=series.topology_index, instability=series.instability,
    )


class HarmonicMemoryEventObserver:
    """Advance a harmonic clock only for admitted performance events.

    The observer deliberately receives an event *count*, rather than density
    frames or audio buffers.  This prevents accidental advancement at frame or
    sample rate and keeps the event source explicit at the coordinator seam.
    """

    def __init__(self, *, euler_exponent: float = 1.25) -> None:
        self._clock = HarmonicMemoryClock(euler_exponent=euler_exponent)
        self._euler_exponent = float(euler_exponent)

    @property
    def event_index(self) -> int:
        return self._clock.event_index

    def observe_admitted_events(
        self,
        rho: object,
        *,
        source_revision: int,
        time: float,
        event_count: int,
        base_delay_seconds: float = 0.137,
    ) -> tuple[HarmonicMemoryDevelopmentFrame, ...]:
        if int(event_count) != event_count or event_count < 0:
            raise ValueError("event_count must be a nonnegative integer.")
        frames: list[HarmonicMemoryDevelopmentFrame] = []
        for _ in range(int(event_count)):
            series = self._clock.advance()
            frames.append(observe_harmonic_memory_development(
                rho, revision=source_revision, time=time,
                event_index=series.event_index,
                base_delay_seconds=base_delay_seconds,
                euler_exponent=self._euler_exponent,
            ))
        return tuple(frames)


__all__ = [
    "HarmonicMemoryClock", "HarmonicMemoryDevelopmentFrame", "HarmonicMemoryEventObserver", "HarmonicMemorySeries",
    "harmonic_memory_series", "observe_harmonic_memory_development",
]
