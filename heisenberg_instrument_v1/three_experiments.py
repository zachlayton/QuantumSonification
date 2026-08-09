"""Heisenberg's three intermediate-observation experiments.

The three cases follow the distinction in *The Physical Principles of the
Quantum Theory*, chapter IV, section 2:

1. no intermediate observation;
2. an intermediate observation whose result is discarded;
3. an intermediate observation whose result is retained.

The implementation is density-matrix native so the unread and recorded cases
can be compared without changing representations.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable, Sequence

import numpy as np


_TOLERANCE = 1.0e-10


class ExperimentMode(str, Enum):
    COHERENT = "coherent"
    UNREAD = "unread"
    RECORDED = "recorded"


@dataclass(frozen=True)
class ExperimentResult:
    mode: ExperimentMode
    rho_after_first: np.ndarray
    rho_after_measurement: np.ndarray
    final_rho: np.ndarray
    outcome_probabilities: tuple[float, ...]
    outcome: int | None
    measurement_disturbance: float
    coherence_before: float
    coherence_after: float


@dataclass(frozen=True)
class ThreeExperimentResults:
    coherent: ExperimentResult
    unread: ExperimentResult
    recorded: ExperimentResult


def _as_square_matrix(value: np.ndarray, name: str) -> np.ndarray:
    matrix = np.asarray(value, dtype=np.complex128)
    if matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1]:
        raise ValueError(f"{name} must be a square matrix")
    if not np.all(np.isfinite(matrix)):
        raise ValueError(f"{name} contains non-finite values")
    return matrix


def _validated_density_matrix(rho: np.ndarray) -> np.ndarray:
    matrix = _as_square_matrix(rho, "rho")
    if not np.allclose(matrix, matrix.conj().T, atol=_TOLERANCE):
        raise ValueError("rho must be Hermitian")
    trace = np.trace(matrix)
    if not np.isclose(trace.imag, 0.0, atol=_TOLERANCE):
        raise ValueError("rho must have a real trace")
    if not np.isclose(trace.real, 1.0, atol=_TOLERANCE):
        raise ValueError(f"rho must have trace one; received {trace}")
    minimum = float(np.min(np.linalg.eigvalsh(matrix)).real)
    if minimum < -_TOLERANCE:
        raise ValueError(f"rho must be positive semidefinite; min={minimum}")
    return matrix.copy()


def _validated_unitary(value: np.ndarray, dimension: int, name: str) -> np.ndarray:
    matrix = _as_square_matrix(value, name)
    if matrix.shape != (dimension, dimension):
        raise ValueError(
            f"{name} must have shape {(dimension, dimension)}; got {matrix.shape}"
        )
    identity = np.eye(dimension, dtype=np.complex128)
    if not np.allclose(matrix.conj().T @ matrix, identity, atol=_TOLERANCE):
        raise ValueError(f"{name} must be unitary")
    return matrix


def _validated_projectors(
    projectors: Iterable[np.ndarray], dimension: int
) -> tuple[np.ndarray, ...]:
    result = tuple(
        _as_square_matrix(projector, f"projector[{index}]")
        for index, projector in enumerate(projectors)
    )
    if not result:
        raise ValueError("at least one measurement projector is required")

    identity = np.eye(dimension, dtype=np.complex128)
    completeness = np.zeros_like(identity)
    for index, projector in enumerate(result):
        if projector.shape != identity.shape:
            raise ValueError(
                f"projector[{index}] must have shape {identity.shape}; "
                f"got {projector.shape}"
            )
        if not np.allclose(projector, projector.conj().T, atol=_TOLERANCE):
            raise ValueError(f"projector[{index}] must be Hermitian")
        if not np.allclose(projector @ projector, projector, atol=_TOLERANCE):
            raise ValueError(f"projector[{index}] must be idempotent")
        completeness += projector

    if not np.allclose(completeness, identity, atol=_TOLERANCE):
        raise ValueError("measurement projectors must resolve the identity")
    for left in range(len(result)):
        for right in range(left + 1, len(result)):
            if not np.allclose(
                result[left] @ result[right], 0.0, atol=_TOLERANCE
            ):
                raise ValueError("measurement projectors must be orthogonal")
    return result


def computational_projectors(dimension: int) -> tuple[np.ndarray, ...]:
    """Return rank-one projectors for the computational basis."""
    if dimension < 1:
        raise ValueError("dimension must be positive")
    projectors = []
    for index in range(int(dimension)):
        projector = np.zeros((dimension, dimension), dtype=np.complex128)
        projector[index, index] = 1.0
        projectors.append(projector)
    return tuple(projectors)


def _unitary_evolve(rho: np.ndarray, unitary: np.ndarray) -> np.ndarray:
    return unitary @ rho @ unitary.conj().T


def _l1_coherence(rho: np.ndarray) -> float:
    off_diagonal = rho - np.diag(np.diag(rho))
    return float(np.sum(np.abs(off_diagonal)))


def _trace_distance(left: np.ndarray, right: np.ndarray) -> float:
    singular_values = np.linalg.svd(left - right, compute_uv=False)
    return 0.5 * float(np.sum(singular_values))


def _measurement_probabilities(
    rho: np.ndarray, projectors: Sequence[np.ndarray]
) -> np.ndarray:
    probabilities = np.asarray(
        [np.trace(projector @ rho).real for projector in projectors],
        dtype=np.float64,
    )
    probabilities[np.abs(probabilities) < _TOLERANCE] = 0.0
    probabilities = np.clip(probabilities, 0.0, None)
    total = float(np.sum(probabilities))
    if total <= _TOLERANCE:
        raise ValueError("measurement probabilities have zero total weight")
    return probabilities / total


def _nonselective_measurement(
    rho: np.ndarray, projectors: Sequence[np.ndarray]
) -> np.ndarray:
    measured = np.zeros_like(rho)
    for projector in projectors:
        measured += projector @ rho @ projector
    return measured


def _selective_measurement(
    rho: np.ndarray,
    projectors: Sequence[np.ndarray],
    probabilities: np.ndarray,
    outcome: int,
) -> np.ndarray:
    if not (0 <= outcome < len(projectors)):
        raise ValueError(f"measurement outcome {outcome} is out of range")
    probability = float(probabilities[outcome])
    if probability <= _TOLERANCE:
        raise ValueError(f"measurement outcome {outcome} has zero probability")
    projector = projectors[outcome]
    return (projector @ rho @ projector) / probability


def run_experiment(
    rho: np.ndarray,
    first: np.ndarray,
    second: np.ndarray,
    projectors: Sequence[np.ndarray],
    mode: ExperimentMode | str,
    *,
    rng: np.random.Generator | None = None,
    outcome: int | None = None,
) -> ExperimentResult:
    """Run one of the three protocols around an intermediate measurement."""
    selected_mode = ExperimentMode(mode)
    initial = _validated_density_matrix(rho)
    dimension = initial.shape[0]
    first_u = _validated_unitary(first, dimension, "first")
    second_u = _validated_unitary(second, dimension, "second")
    measurement = _validated_projectors(projectors, dimension)

    after_first = _unitary_evolve(initial, first_u)
    probabilities = _measurement_probabilities(after_first, measurement)
    selected_outcome: int | None = None

    if selected_mode is ExperimentMode.COHERENT:
        after_measurement = after_first.copy()
    elif selected_mode is ExperimentMode.UNREAD:
        after_measurement = _nonselective_measurement(after_first, measurement)
    else:
        if outcome is None:
            generator = rng if rng is not None else np.random.default_rng()
            selected_outcome = int(
                generator.choice(len(measurement), p=probabilities)
            )
        else:
            selected_outcome = int(outcome)
        after_measurement = _selective_measurement(
            after_first,
            measurement,
            probabilities,
            selected_outcome,
        )

    final = _unitary_evolve(after_measurement, second_u)
    return ExperimentResult(
        mode=selected_mode,
        rho_after_first=after_first,
        rho_after_measurement=after_measurement,
        final_rho=final,
        outcome_probabilities=tuple(float(value) for value in probabilities),
        outcome=selected_outcome,
        measurement_disturbance=_trace_distance(after_first, after_measurement),
        coherence_before=_l1_coherence(after_first),
        coherence_after=_l1_coherence(after_measurement),
    )


def run_three_experiments(
    rho: np.ndarray,
    first: np.ndarray,
    second: np.ndarray,
    projectors: Sequence[np.ndarray],
    *,
    rng: np.random.Generator | None = None,
    recorded_outcome: int | None = None,
) -> ThreeExperimentResults:
    """Evaluate the coherent, unread, and recorded cases from one preparation."""
    return ThreeExperimentResults(
        coherent=run_experiment(
            rho, first, second, projectors, ExperimentMode.COHERENT
        ),
        unread=run_experiment(
            rho, first, second, projectors, ExperimentMode.UNREAD
        ),
        recorded=run_experiment(
            rho,
            first,
            second,
            projectors,
            ExperimentMode.RECORDED,
            rng=rng,
            outcome=recorded_outcome,
        ),
    )
