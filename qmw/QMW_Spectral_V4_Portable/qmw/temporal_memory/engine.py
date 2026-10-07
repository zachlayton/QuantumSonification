"""Read-only polymetric temporal-memory observation over a density matrix.

This is a sound-control adapter, not a delay differential equation for the
quantum system.  Its input is a sealed density snapshot and, optionally, the
authoritative computational-basis current supplied by :class:`QuantumFrame`.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:  # Avoid a runtime dependency cycle for a lightweight adapter.
    from qmw.quantum.dynamics import QuantumFrame


Array = np.ndarray
_EPS = 1.0e-12


def _readonly(values: object, *, dtype: object = float) -> Array:
    result = np.array(values, dtype=dtype, copy=True)
    result.setflags(write=False)
    return result


def _finite_scalar(name: str, value: float, *, lower: float | None = None) -> float:
    result = float(value)
    if not math.isfinite(result) or (lower is not None and result < lower):
        qualifier = "finite" if lower is None else f"finite and >= {lower}"
        raise ValueError(f"{name} must be {qualifier}.")
    return result


def _density(values: object) -> Array:
    rho = np.asarray(values, dtype=np.complex128)
    if rho.ndim != 2 or rho.shape[0] != rho.shape[1] or rho.shape[0] < 2:
        raise ValueError("rho must be a square density matrix with dimension >= 2.")
    if not np.all(np.isfinite(rho)):
        raise ValueError("rho must be finite.")
    if not np.allclose(rho, rho.conj().T, atol=1.0e-9, rtol=0.0):
        raise ValueError("rho must be Hermitian.")
    diagonal = np.real(np.diag(rho))
    if np.any(diagonal < -1.0e-9) or not np.isclose(float(diagonal.sum()), 1.0, atol=1.0e-8, rtol=0.0):
        raise ValueError("rho must have a nonnegative unit-trace diagonal.")
    return np.array(rho, copy=True)


def _inflow_matrix(values: object | None, dimension: int) -> Array:
    if values is None:
        return np.zeros((dimension, dimension), dtype=float)
    current = np.asarray(values, dtype=float)
    if current.shape != (dimension, dimension) or not np.all(np.isfinite(current)):
        raise ValueError("basis_current_inflow must be a finite matrix matching rho.")
    if not np.allclose(current, -current.T, atol=1.0e-9, rtol=0.0):
        raise ValueError("basis_current_inflow must be antisymmetric.")
    return np.array(current, copy=True)


def harmonic_weights(count: int, exponent: float) -> Array:
    """Return normalized generalized-harmonic weights ``k**(-exponent)``."""

    if int(count) != count or count < 1:
        raise ValueError("count must be a positive integer.")
    shape = _finite_scalar("exponent", exponent, lower=0.0)
    if shape == 0.0:
        raise ValueError("exponent must be positive to retain harmonic ordering.")
    raw = np.arange(1, int(count) + 1, dtype=float) ** (-shape)
    return _readonly(raw / raw.sum())


@dataclass(frozen=True)
class TemporalMemoryConfig:
    """Bounded, declared rendering policy for polymetric delay controls.

    ``metric_ratios`` multiply ``base_delay_seconds``.  They are deliberately
    incommensurate-looking rational ratios, not clock rates or quantum times.
    ``cross_feedback_cap`` is a maximum *row* sum, which keeps the downstream
    matrix-feedback network bounded before its own DSP safety limiter.
    """

    harmonic_exponent: float = 1.25
    base_delay_seconds: float = 0.137
    metric_ratios: tuple[float, ...] = (
        1.0, 3.0 / 2.0, 4.0 / 3.0, 5.0 / 4.0,
        7.0 / 5.0, 9.0 / 7.0, 11.0 / 8.0, 13.0 / 9.0,
        16.0 / 11.0, 17.0 / 13.0, 19.0 / 14.0, 23.0 / 17.0,
        25.0 / 18.0, 29.0 / 21.0, 31.0 / 23.0, 37.0 / 27.0,
    )
    phase_delay_depth: float = 0.23
    population_excitation_mix: float = 0.72
    flow_excitation_mix: float = 0.28
    coherence_persistence_mix: float = 0.62
    cross_feedback_cap: float = 0.42
    feedback_diffusion: float = 0.0

    def __post_init__(self) -> None:
        exponent = _finite_scalar("harmonic_exponent", self.harmonic_exponent, lower=0.0)
        base = _finite_scalar("base_delay_seconds", self.base_delay_seconds, lower=_EPS)
        ratios = tuple(float(value) for value in self.metric_ratios)
        if not ratios or not all(math.isfinite(value) and value > 0.0 for value in ratios):
            raise ValueError("metric_ratios must be a nonempty sequence of finite positive values.")
        for name, value in (
            ("phase_delay_depth", self.phase_delay_depth),
            ("population_excitation_mix", self.population_excitation_mix),
            ("flow_excitation_mix", self.flow_excitation_mix),
            ("coherence_persistence_mix", self.coherence_persistence_mix),
            ("cross_feedback_cap", self.cross_feedback_cap),
            ("feedback_diffusion", self.feedback_diffusion),
        ):
            checked = _finite_scalar(name, value, lower=0.0)
            if checked > 1.0:
                raise ValueError(f"{name} must lie in [0, 1].")
        if not math.isclose(self.population_excitation_mix + self.flow_excitation_mix, 1.0, abs_tol=1.0e-12):
            raise ValueError("population_excitation_mix and flow_excitation_mix must sum to 1.")
        if self.cross_feedback_cap > 0.42:
            raise ValueError("cross_feedback_cap must not exceed the receiver safety cap of 0.42.")
        object.__setattr__(self, "harmonic_exponent", exponent)
        object.__setattr__(self, "base_delay_seconds", base)
        object.__setattr__(self, "metric_ratios", ratios)


@dataclass(frozen=True)
class TemporalMemoryFrame:
    """Immutable, bounded sound descriptors derived from one density snapshot.

    ``basis_current_inflow`` uses QMW's ``destination <- source`` convention.
    The relative-coherence phase used for fractional delay is representation
    dependent: it is expressly a musical encoder, not a gauge-invariant or
    physical-space observable.
    """

    revision: int
    time: float
    source_dimension: int
    line_count: int
    harmonic_weights: Array
    delay_seconds: Array
    excitation: Array
    persistence: Array
    cross_feedback: Array
    relative_phase_cycles: Array
    current_activity: Array
    provenance: str = "derived_read_only_density_temporal_memory_v1"

    def __post_init__(self) -> None:
        if int(self.revision) != self.revision or self.revision < 0:
            raise ValueError("revision must be a nonnegative integer.")
        if not math.isfinite(float(self.time)):
            raise ValueError("time must be finite.")
        source_dimension = int(self.source_dimension)
        size = int(self.line_count)
        if source_dimension < 2:
            raise ValueError("source_dimension must be >= 2.")
        if size < 2:
            raise ValueError("line_count must be >= 2.")
        vectors = {
            "harmonic_weights": _readonly(self.harmonic_weights),
            "delay_seconds": _readonly(self.delay_seconds),
            "excitation": _readonly(self.excitation),
            "persistence": _readonly(self.persistence),
            "relative_phase_cycles": _readonly(self.relative_phase_cycles),
            "current_activity": _readonly(self.current_activity),
        }
        if any(value.shape != (size,) or not np.all(np.isfinite(value)) for value in vectors.values()):
            raise ValueError("temporal-memory vectors must be finite and match line_count.")
        if not np.isclose(float(vectors["harmonic_weights"].sum()), 1.0, atol=1.0e-10):
            raise ValueError("harmonic_weights must sum to one.")
        if np.any(vectors["harmonic_weights"] <= 0.0) or np.any(vectors["delay_seconds"] <= 0.0):
            raise ValueError("harmonic weights and delays must be positive.")
        if any(np.any(vectors[name] < 0.0) or np.any(vectors[name] > 1.0) for name in ("excitation", "persistence")):
            raise ValueError("excitation and persistence must lie in [0, 1].")
        if np.any(np.abs(vectors["relative_phase_cycles"]) > 0.5 + 1.0e-10):
            raise ValueError("relative_phase_cycles must lie in [-0.5, 0.5].")
        cross = _readonly(self.cross_feedback)
        if cross.shape != (size, size) or not np.all(np.isfinite(cross)) or np.any(cross < 0.0) or np.any(np.diag(cross) > 1.0e-12):
            raise ValueError("cross_feedback must be a finite nonnegative square matrix with zero diagonal.")
        object.__setattr__(self, "revision", int(self.revision))
        object.__setattr__(self, "time", float(self.time))
        object.__setattr__(self, "source_dimension", source_dimension)
        object.__setattr__(self, "line_count", size)
        for name, value in vectors.items():
            object.__setattr__(self, name, value)
        object.__setattr__(self, "cross_feedback", cross)


def _resample(values: Array, count: int) -> Array:
    if values.size == count:
        return np.array(values, dtype=float, copy=True)
    source = np.linspace(0.0, 1.0, values.size)
    target = np.linspace(0.0, 1.0, count)
    return np.interp(target, source, values)


def observe_temporal_memory(
    rho: object,
    *,
    revision: int,
    time: float,
    basis_current_inflow: object | None = None,
    config: TemporalMemoryConfig | None = None,
) -> TemporalMemoryFrame:
    """Map rho populations, coherences, and current into bounded delay controls.

    The line count follows ``rho`` when its dimension is at most the configured
    polymeter bank size.  Larger density matrices are deterministically
    resampled to that fixed bank; no state components are discarded silently.
    """

    if int(revision) != revision or revision < 0:
        raise ValueError("revision must be a nonnegative integer.")
    if not math.isfinite(float(time)):
        raise ValueError("time must be finite.")
    cfg = config or TemporalMemoryConfig()
    density = _density(rho)
    source_dimension = density.shape[0]
    current = _inflow_matrix(basis_current_inflow, source_dimension)
    line_count = min(source_dimension, len(cfg.metric_ratios))

    population = np.clip(np.real(np.diag(density)), 0.0, None)
    population = population / max(float(population.max()), _EPS)
    coherence = np.abs(density).astype(float)
    np.fill_diagonal(coherence, 0.0)
    coherence_strength = coherence.sum(axis=1) / max(source_dimension - 1, 1)
    coherence_strength /= max(float(coherence_strength.max()), _EPS)
    # Use incident magnitude rather than signed node balance.  A closed
    # current circulation can have zero divergence at every node while still
    # being an active, musically useful transport observation.
    current_activity = np.abs(current).sum(axis=1)
    current_activity /= max(float(current_activity.max()), _EPS)

    excitation_full = (
        cfg.population_excitation_mix * population
        + cfg.flow_excitation_mix * current_activity
    )
    persistence_full = np.clip(
        (1.0 - cfg.coherence_persistence_mix) * population
        + cfg.coherence_persistence_mix * coherence_strength,
        0.0,
        1.0,
    )
    adjacent = np.array([density[index, (index + 1) % source_dimension] for index in range(source_dimension)])
    relative_phase = np.angle(adjacent) / (2.0 * np.pi)

    raw_cross = coherence / max(float(coherence.max()), _EPS)
    directed_flow = np.abs(current) / max(float(np.abs(current).max()), _EPS)
    raw_cross = 0.72 * raw_cross + 0.28 * directed_flow
    np.fill_diagonal(raw_cross, 0.0)
    row_total = raw_cross.sum(axis=1, keepdims=True)
    cross_full = np.divide(raw_cross, np.maximum(row_total, 1.0), out=np.zeros_like(raw_cross), where=row_total > _EPS)
    cross_full *= cfg.cross_feedback_cap
    if cfg.feedback_diffusion > 0.0:
        # A wholly downstream morph between the observed directed matrix and
        # an equal off-diagonal field.  It changes the sound network only;
        # neither rho nor its current are modified or fed back upstream.
        uniform_cross = np.ones((source_dimension, source_dimension), dtype=float)
        np.fill_diagonal(uniform_cross, 0.0)
        uniform_cross /= max(source_dimension - 1, 1)
        uniform_cross *= cfg.cross_feedback_cap
        cross_full = (
            ((1.0 - cfg.feedback_diffusion) * cross_full)
            + (cfg.feedback_diffusion * uniform_cross)
        )

    if line_count != source_dimension:
        excitation = _resample(excitation_full, line_count)
        persistence = _resample(persistence_full, line_count)
        phase = _resample(relative_phase, line_count)
        activity = _resample(current_activity, line_count)
        # Deterministic interval resampling retains the control field while
        # preserving the downstream row-sum bound.
        positions = np.linspace(0, source_dimension - 1, line_count).round().astype(int)
        cross = cross_full[np.ix_(positions, positions)]
        np.fill_diagonal(cross, 0.0)
        total = cross.sum(axis=1, keepdims=True)
        cross = np.divide(cross, np.maximum(total, 1.0), out=np.zeros_like(cross), where=total > _EPS) * cfg.cross_feedback_cap
    else:
        excitation, persistence, phase, activity, cross = excitation_full, persistence_full, relative_phase, current_activity, cross_full

    weights = harmonic_weights(line_count, cfg.harmonic_exponent)
    base = cfg.base_delay_seconds * np.asarray(cfg.metric_ratios[:line_count], dtype=float)
    delays = base * (1.0 + cfg.phase_delay_depth * phase)
    return TemporalMemoryFrame(
        revision=int(revision), time=float(time), source_dimension=source_dimension,
        line_count=line_count,
        harmonic_weights=weights, delay_seconds=delays,
        excitation=np.clip(excitation, 0.0, 1.0),
        persistence=np.clip(persistence, 0.0, 1.0),
        cross_feedback=cross, relative_phase_cycles=np.clip(phase, -0.5, 0.5),
        current_activity=np.clip(activity, 0.0, 1.0),
    )


def observe_quantum_frame_temporal_memory(
    frame: "QuantumFrame",
    *,
    config: TemporalMemoryConfig | None = None,
) -> TemporalMemoryFrame:
    """Observe a sealed :class:`qmw.quantum.dynamics.QuantumFrame` read-only."""

    from qmw.quantum.dynamics import QuantumFrame

    if not isinstance(frame, QuantumFrame):
        raise TypeError("frame must be a QuantumFrame.")
    return observe_temporal_memory(
        frame.rho, revision=frame.frame_index, time=frame.time,
        basis_current_inflow=frame.basis_current_inflow, config=config,
    )


__all__ = [
    "TemporalMemoryConfig", "TemporalMemoryFrame", "harmonic_weights",
    "observe_quantum_frame_temporal_memory", "observe_temporal_memory",
]
