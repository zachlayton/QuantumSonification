"""Resonance scoring and soft oracle generation from ``QuantumMemory``.

Phase 3 turns stored density-matrix snapshots into a dynamic phase oracle:

    current rho -> resonance scores -> selected memories -> spectral oracle

The selected mixed memories are combined without collapsing them to pure
states. Their weighted mixture is spectrally normalized to a positive
generator R with eigenvalues in [0, 1], and the oracle is
``exp(-i*pi*strength*R)``.
"""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass, field
from typing import Any, Mapping, Sequence

import numpy as np

from feedback.quantum_memory import QuantumMemory, QuantumSnapshot


@dataclass(frozen=True)
class ResonanceWeights:
    fidelity: float = 0.30
    trace: float = 0.20
    bures: float = 0.10
    entropy: float = 0.075
    coherence: float = 0.075
    pauli: float = 0.20
    hamiltonian: float = 0.025
    trajectory: float = 0.025

    def __post_init__(self) -> None:
        values = asdict(self)
        if any(not math.isfinite(value) or value < 0.0 for value in values.values()):
            raise ValueError("resonance weights must be finite and non-negative")
        if sum(values.values()) <= 0.0:
            raise ValueError("at least one resonance weight must be positive")


@dataclass(frozen=True)
class MemoryOracleConfig:
    weights: ResonanceWeights = field(default_factory=ResonanceWeights)
    top_k: int = 4
    minimum_resonance: float = 0.20
    recency_decay: float = 0.08
    oracle_strength: float = 1.0
    confidence_modulates_strength: bool = True
    trajectory_keys: tuple[str, ...] = (
        "trajectory_speed",
        "trajectory_acceleration",
        "trajectory_direction_change",
    )

    def __post_init__(self) -> None:
        if isinstance(self.top_k, bool) or not isinstance(self.top_k, int) or self.top_k < 1:
            raise ValueError("top_k must be a positive integer")
        if not 0.0 <= self.minimum_resonance <= 1.0:
            raise ValueError("minimum_resonance must be in [0, 1]")
        if not math.isfinite(self.recency_decay) or self.recency_decay < 0.0:
            raise ValueError("recency_decay must be finite and non-negative")
        if not math.isfinite(self.oracle_strength) or not 0.0 <= self.oracle_strength <= 1.0:
            raise ValueError("oracle_strength must be finite and in [0, 1]")


@dataclass(frozen=True)
class ResonanceMetrics:
    fidelity: float
    trace_distance: float
    trace_similarity: float
    bures_distance: float
    bures_similarity: float
    entropy_similarity: float
    coherence_similarity: float
    pauli_similarity: float
    hamiltonian_similarity: float | None
    trajectory_similarity: float | None

    def as_dict(self) -> dict[str, float | None]:
        return asdict(self)


@dataclass(frozen=True)
class MemoryMatch:
    snapshot_index: int
    age: int
    snapshot: QuantumSnapshot
    metrics: ResonanceMetrics
    resonance: float
    recency_weight: float
    selection_weight: float


@dataclass(frozen=True)
class QuantumMemoryOracleResult:
    oracle: np.ndarray
    resonance_generator: np.ndarray
    memory_mixture: np.ndarray
    matches: tuple[MemoryMatch, ...]
    selected_matches: tuple[MemoryMatch, ...]
    effective_strength: float
    aggregate_resonance: float

    @property
    def has_resonance(self) -> bool:
        return bool(self.selected_matches)

    @property
    def phase_angles(self) -> np.ndarray:
        values = np.linalg.eigvalsh(self.resonance_generator).real
        return -math.pi * self.effective_strength * values

    def apply(self, rho: np.ndarray) -> np.ndarray:
        state = density_matrix(rho)
        if state.shape != self.oracle.shape:
            raise ValueError("rho dimension does not match memory oracle")
        return self.oracle @ state @ self.oracle.conj().T


def density_matrix(value: np.ndarray, *, atol: float = 1e-10) -> np.ndarray:
    """Return a validated, normalized density matrix."""
    state = np.asarray(value, dtype=np.complex128)
    if state.ndim == 1:
        norm = float(np.linalg.norm(state))
        if norm <= atol:
            raise ValueError("statevector has zero norm")
        state = np.outer(state / norm, (state / norm).conj())
    if state.ndim != 2 or state.shape[0] != state.shape[1]:
        raise ValueError("density state must be square")
    dimension = state.shape[0]
    if dimension < 2 or dimension & (dimension - 1):
        raise ValueError("density dimension must be a power of two")
    if not np.all(np.isfinite(state)):
        raise ValueError("density state must contain finite values")
    if not np.allclose(state, state.conj().T, atol=atol, rtol=0.0):
        raise ValueError("density state must be Hermitian")
    state = 0.5 * (state + state.conj().T)
    trace = float(np.trace(state).real)
    if trace <= atol:
        raise ValueError("density state must have positive trace")
    state = state / trace
    minimum = float(np.min(np.linalg.eigvalsh(state)).real)
    if minimum < -atol:
        raise ValueError("density state must be positive semidefinite")
    return state


def density_fidelity(left: np.ndarray, right: np.ndarray) -> float:
    """Uhlmann fidelity including the conventional outer square."""
    rho = density_matrix(left)
    sigma = density_matrix(right)
    _matching_shapes(rho, sigma)
    values, vectors = np.linalg.eigh(rho)
    root = (vectors * np.sqrt(np.clip(values, 0.0, None))) @ vectors.conj().T
    middle = root @ sigma @ root
    middle = 0.5 * (middle + middle.conj().T)
    root_fidelity = float(
        np.sum(np.sqrt(np.clip(np.linalg.eigvalsh(middle).real, 0.0, None)))
    )
    return float(np.clip(root_fidelity * root_fidelity, 0.0, 1.0))


def trace_distance(left: np.ndarray, right: np.ndarray) -> float:
    rho = density_matrix(left)
    sigma = density_matrix(right)
    _matching_shapes(rho, sigma)
    singular_values = np.linalg.svd(rho - sigma, compute_uv=False)
    return float(np.clip(0.5 * np.sum(singular_values), 0.0, 1.0))


def von_neumann_entropy(rho: np.ndarray) -> float:
    values = np.clip(np.linalg.eigvalsh(density_matrix(rho)).real, 0.0, 1.0)
    nonzero = values[values > 1e-15]
    return float(-np.sum(nonzero * np.log2(nonzero)))


def l1_coherence(rho: np.ndarray) -> float:
    state = density_matrix(rho)
    return float(np.sum(np.abs(state - np.diag(np.diag(state)))))


def pauli_coefficient_similarity(left: np.ndarray, right: np.ndarray) -> float:
    """Cosine similarity of complete Pauli coefficient vectors via Parseval."""
    rho = density_matrix(left)
    sigma = density_matrix(right)
    _matching_shapes(rho, sigma)
    numerator = float(np.trace(rho @ sigma).real)
    denominator = math.sqrt(
        max(float(np.trace(rho @ rho).real), 0.0)
        * max(float(np.trace(sigma @ sigma).real), 0.0)
    )
    if denominator <= 1e-15:
        return 0.0
    return float(np.clip(numerator / denominator, 0.0, 1.0))


def _matching_shapes(left: np.ndarray, right: np.ndarray) -> None:
    if left.shape != right.shape:
        raise ValueError("density matrices must have matching dimensions")


def _numeric_vector(value: Any) -> np.ndarray | None:
    if value is None:
        return None
    if hasattr(value, "as_pauli_terms"):
        value = value.as_pauli_terms()
    elif all(hasattr(value, axis) for axis in ("x", "y", "z")):
        value = [value.x, value.y, value.z]
    if isinstance(value, Mapping):
        numeric = [float(value[key]) for key in sorted(value) if np.isscalar(value[key])]
        return np.asarray(numeric, dtype=np.float64) if numeric else None
    array = np.asarray(value)
    if array.size == 0:
        return None
    if np.iscomplexobj(array):
        array = np.concatenate((array.real.reshape(-1), array.imag.reshape(-1)))
    return np.asarray(array, dtype=np.float64).reshape(-1)


def vector_similarity(left: Any, right: Any) -> float | None:
    a = _numeric_vector(left)
    b = _numeric_vector(right)
    if a is None or b is None:
        return None
    if a.shape != b.shape:
        return None
    norm_a = float(np.linalg.norm(a))
    norm_b = float(np.linalg.norm(b))
    if norm_a <= 1e-15 and norm_b <= 1e-15:
        return 1.0
    if norm_a <= 1e-15 or norm_b <= 1e-15:
        return 0.0
    cosine = float(np.dot(a, b) / (norm_a * norm_b))
    return float(np.clip(0.5 * (cosine + 1.0), 0.0, 1.0))


def trajectory_similarity(
    current: Mapping[str, Any] | None,
    remembered: Mapping[str, Any] | None,
    keys: Sequence[str],
) -> float | None:
    if not current or not remembered:
        return None
    similarities: list[float] = []
    for key in keys:
        if key not in current or key not in remembered:
            continue
        left = float(current[key])
        right = float(remembered[key])
        scale = abs(left) + abs(right)
        similarities.append(1.0 if scale <= 1e-15 else max(0.0, 1.0 - abs(left - right) / scale))
    return float(np.mean(similarities)) if similarities else None


def resonance_metrics(
    current_rho: np.ndarray,
    remembered_rho: np.ndarray,
    *,
    current_hamiltonian: Any = None,
    remembered_hamiltonian: Any = None,
    current_trajectory: Mapping[str, Any] | None = None,
    remembered_trajectory: Mapping[str, Any] | None = None,
    trajectory_keys: Sequence[str] = (),
) -> ResonanceMetrics:
    current = density_matrix(current_rho)
    remembered = density_matrix(remembered_rho)
    _matching_shapes(current, remembered)
    fidelity = density_fidelity(current, remembered)
    distance = trace_distance(current, remembered)
    bures_distance = math.sqrt(max(0.0, 2.0 - 2.0 * math.sqrt(fidelity)))
    dimension = current.shape[0]
    entropy_scale = math.log2(dimension)
    coherence_scale = dimension - 1.0
    return ResonanceMetrics(
        fidelity=fidelity,
        trace_distance=distance,
        trace_similarity=1.0 - distance,
        bures_distance=bures_distance,
        bures_similarity=float(
            np.clip(1.0 - bures_distance / math.sqrt(2.0), 0.0, 1.0)
        ),
        entropy_similarity=float(
            np.clip(
                1.0
                - abs(von_neumann_entropy(current) - von_neumann_entropy(remembered))
                / entropy_scale,
                0.0,
                1.0,
            )
        ),
        coherence_similarity=float(
            np.clip(
                1.0 - abs(l1_coherence(current) - l1_coherence(remembered)) / coherence_scale,
                0.0,
                1.0,
            )
        ),
        pauli_similarity=pauli_coefficient_similarity(current, remembered),
        hamiltonian_similarity=vector_similarity(current_hamiltonian, remembered_hamiltonian),
        trajectory_similarity=trajectory_similarity(
            current_trajectory,
            remembered_trajectory,
            trajectory_keys,
        ),
    )


def weighted_resonance(metrics: ResonanceMetrics, weights: ResonanceWeights) -> float:
    candidates = (
        (metrics.fidelity, weights.fidelity),
        (metrics.trace_similarity, weights.trace),
        (metrics.bures_similarity, weights.bures),
        (metrics.entropy_similarity, weights.entropy),
        (metrics.coherence_similarity, weights.coherence),
        (metrics.pauli_similarity, weights.pauli),
        (metrics.hamiltonian_similarity, weights.hamiltonian),
        (metrics.trajectory_similarity, weights.trajectory),
    )
    available = [(float(value), weight) for value, weight in candidates if value is not None and weight > 0.0]
    denominator = sum(weight for _, weight in available)
    if denominator <= 0.0:
        raise ValueError("no weighted resonance metrics are available")
    return float(np.clip(sum(value * weight for value, weight in available) / denominator, 0.0, 1.0))


def score_quantum_memory(
    memory: QuantumMemory,
    current_rho: np.ndarray,
    *,
    current_hamiltonian: Any = None,
    current_metrics: Mapping[str, Any] | None = None,
    config: MemoryOracleConfig | None = None,
) -> tuple[MemoryMatch, ...]:
    settings = config or MemoryOracleConfig()
    current = density_matrix(current_rho)
    matches: list[MemoryMatch] = []
    snapshot_count = len(memory.snapshots)
    for index, snapshot in enumerate(memory.snapshots):
        remembered = density_matrix(snapshot.rho)
        _matching_shapes(current, remembered)
        age = snapshot_count - 1 - index
        metrics = resonance_metrics(
            current,
            remembered,
            current_hamiltonian=current_hamiltonian,
            remembered_hamiltonian=snapshot.hamiltonian,
            current_trajectory=current_metrics,
            remembered_trajectory=snapshot.metrics,
            trajectory_keys=settings.trajectory_keys,
        )
        resonance = weighted_resonance(metrics, settings.weights)
        recency = math.exp(-settings.recency_decay * age)
        matches.append(
            MemoryMatch(
                snapshot_index=index,
                age=age,
                snapshot=snapshot,
                metrics=metrics,
                resonance=resonance,
                recency_weight=recency,
                selection_weight=resonance * recency,
            )
        )
    return tuple(sorted(matches, key=lambda match: (match.selection_weight, match.snapshot_index), reverse=True))


def build_quantum_memory_oracle(
    memory: QuantumMemory,
    current_rho: np.ndarray,
    *,
    current_hamiltonian: Any = None,
    current_metrics: Mapping[str, Any] | None = None,
    config: MemoryOracleConfig | None = None,
) -> QuantumMemoryOracleResult:
    """Score memory, select resonances, and return a soft spectral oracle."""
    settings = config or MemoryOracleConfig()
    current = density_matrix(current_rho)
    matches = score_quantum_memory(
        memory,
        current,
        current_hamiltonian=current_hamiltonian,
        current_metrics=current_metrics,
        config=settings,
    )
    selected = tuple(
        match for match in matches if match.resonance >= settings.minimum_resonance
    )[: settings.top_k]
    dimension = current.shape[0]
    if not selected:
        identity = np.eye(dimension, dtype=np.complex128)
        zero = np.zeros_like(identity)
        return QuantumMemoryOracleResult(
            oracle=identity,
            resonance_generator=zero,
            memory_mixture=identity / dimension,
            matches=matches,
            selected_matches=(),
            effective_strength=0.0,
            aggregate_resonance=0.0,
        )

    total_weight = sum(match.selection_weight for match in selected)
    if total_weight <= 1e-15:
        raise ValueError("selected memory weights are zero")
    mixture = sum(
        match.selection_weight * density_matrix(match.snapshot.rho) for match in selected
    ) / total_weight
    mixture = density_matrix(mixture)
    eigenvalues, eigenvectors = np.linalg.eigh(mixture)
    maximum = float(np.max(eigenvalues).real)
    if maximum <= 1e-15:
        raise ValueError("memory mixture has no spectral support")
    normalized_values = np.clip(eigenvalues / maximum, 0.0, 1.0)
    generator = (eigenvectors * normalized_values) @ eigenvectors.conj().T
    aggregate = sum(
        match.selection_weight * match.resonance for match in selected
    ) / total_weight
    effective_strength = settings.oracle_strength * (
        aggregate if settings.confidence_modulates_strength else 1.0
    )
    phases = np.exp(-1j * math.pi * effective_strength * normalized_values)
    oracle = (eigenvectors * phases) @ eigenvectors.conj().T
    return QuantumMemoryOracleResult(
        oracle=oracle,
        resonance_generator=generator,
        memory_mixture=mixture,
        matches=matches,
        selected_matches=selected,
        effective_strength=float(effective_strength),
        aggregate_resonance=float(aggregate),
    )
