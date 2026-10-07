"""Directed computational-basis probability current from authoritative rho and H."""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Mapping

import numpy as np


Array = np.ndarray


def hermitian_matrix(name: str, values: object, *, tolerance: float = 1.0e-9) -> Array:
    result = np.asarray(values, dtype=np.complex128)
    if tolerance <= 0.0 or not math.isfinite(tolerance):
        raise ValueError("tolerance must be finite and positive.")
    if result.ndim != 2 or result.shape[0] != result.shape[1] or not np.all(np.isfinite(result)):
        raise ValueError(f"{name} must be a finite square matrix.")
    if not np.allclose(result, result.conj().T, rtol=0.0, atol=tolerance):
        raise ValueError(f"{name} must be Hermitian.")
    return np.array(result, copy=True)


def _pair(rho: object, hamiltonian: object, tolerance: float) -> tuple[Array, Array]:
    density = hermitian_matrix("rho", rho, tolerance=tolerance)
    generator = hermitian_matrix("hamiltonian", hamiltonian, tolerance=tolerance)
    if density.shape != generator.shape:
        raise ValueError("rho and hamiltonian must share a shape.")
    return density, generator


def current_matrix(rho: object, hamiltonian: object, *, hbar: float = 1.0, tolerance: float = 1.0e-9) -> Array:
    """Return source-to-destination current J[i,j]."""

    if not math.isfinite(hbar) or hbar <= 0.0:
        raise ValueError("hbar must be finite and positive.")
    density, generator = _pair(rho, hamiltonian, tolerance)
    inflow_indexed = (2.0 / hbar) * np.imag(generator * density.T)
    source_indexed = 0.5 * (inflow_indexed.T - inflow_indexed)
    np.fill_diagonal(source_indexed, 0.0)
    return np.asarray(source_indexed, dtype=float)


def von_neumann_population_rate(rho: object, hamiltonian: object, *, hbar: float = 1.0, tolerance: float = 1.0e-9) -> Array:
    if not math.isfinite(hbar) or hbar <= 0.0:
        raise ValueError("hbar must be finite and positive.")
    density, generator = _pair(rho, hamiltonian, tolerance)
    derivative = (-1j / hbar) * (generator @ density - density @ generator)
    return np.asarray(np.real(np.diag(derivative)), dtype=float)


def node_inflow(current: object) -> Array:
    matrix = np.asarray(current, dtype=float)
    if matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1] or not np.all(np.isfinite(matrix)):
        raise ValueError("current must be a finite square matrix.")
    return np.sum(matrix, axis=0)


def continuity_residual(rho: object, hamiltonian: object, *, hbar: float = 1.0, tolerance: float = 1.0e-9) -> Array:
    return von_neumann_population_rate(rho, hamiltonian, hbar=hbar, tolerance=tolerance) - node_inflow(
        current_matrix(rho, hamiltonian, hbar=hbar, tolerance=tolerance)
    )


def pauli_resolved_current(rho: object, operator: object, coefficient: float, *, hbar: float = 1.0, tolerance: float = 1.0e-9) -> Array:
    if not math.isfinite(float(coefficient)):
        raise ValueError("coefficient must be finite.")
    return current_matrix(rho, float(coefficient) * hermitian_matrix("operator", operator, tolerance=tolerance), hbar=hbar, tolerance=tolerance)


@dataclass(frozen=True)
class CurrentEdge:
    source: int
    destination: int
    magnitude: float
    dominant_pauli: str | None = None
    dominant_contribution: float = 0.0


def sparse_current_edges(current: object, *, threshold: float = 1.0e-9, pauli_contributions: Mapping[str, object] | None = None) -> tuple[CurrentEdge, ...]:
    matrix = np.asarray(current, dtype=float)
    if threshold <= 0.0 or matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1]:
        raise ValueError("threshold must be positive and current must be square.")
    if not np.all(np.isfinite(matrix)) or not np.allclose(matrix, -matrix.T, rtol=0.0, atol=threshold * 0.1):
        raise ValueError("current must be finite and antisymmetric.")
    contributions = {str(label): np.asarray(values, dtype=float) for label, values in (pauli_contributions or {}).items()}
    if any(values.shape != matrix.shape or not np.all(np.isfinite(values)) for values in contributions.values()):
        raise ValueError("Pauli contributions must match current.")
    edges: list[CurrentEdge] = []
    for left in range(matrix.shape[0]):
        for right in range(left + 1, matrix.shape[0]):
            value = float(matrix[left, right])
            if abs(value) < threshold:
                continue
            source, destination = (left, right) if value > 0.0 else (right, left)
            directed = {label: float(values[source, destination]) for label, values in contributions.items()}
            dominant = max(directed, key=lambda label: abs(directed[label]), default=None)
            edges.append(CurrentEdge(source, destination, abs(value), dominant, 0.0 if dominant is None else directed[dominant]))
    return tuple(edges)


__all__ = [
    "CurrentEdge", "continuity_residual", "current_matrix", "hermitian_matrix",
    "node_inflow", "pauli_resolved_current", "sparse_current_edges",
    "von_neumann_population_rate",
]
