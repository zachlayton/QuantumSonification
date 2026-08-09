"""Graph Laplacians as density matrices, with explicit limitations.

This module implements the ordinary real, undirected, non-negative weighted
graph construction studied by Braunstein, Ghosh, and Severini:

    rho_G = L_G / Tr(L_G)

It deliberately keeps this graph-derived state distinct from an arbitrary
quantum density matrix.  ``project_density_to_graph_state`` quantifies how
closely a general density matrix can be represented as a convex mixture of
ordinary edge-difference projectors.

The tensor utilities require an explicit ``TensorLabeling``.  Entanglement is
therefore always evaluated relative to a declared subsystem factorization;
it is never treated as an intrinsic property of an unlabeled graph.

Dependencies
------------
numpy
scipy
"""

from __future__ import annotations

from dataclasses import dataclass, field
from itertools import combinations, product
from math import prod
from typing import Any, Iterable, Sequence

import numpy as np
from scipy.optimize import minimize


Array = np.ndarray


def _as_square_matrix(matrix: Array, name: str) -> Array:
    result = np.asarray(matrix)
    if result.ndim != 2 or result.shape[0] != result.shape[1]:
        raise ValueError(f"{name} must be a square matrix")
    return result


def _validate_ordinary_adjacency(
    adjacency: Array,
    name: str = "adjacency",
    *,
    atol: float = 1e-12,
) -> Array:
    """Return a finite real symmetric non-negative adjacency matrix."""

    matrix = _as_square_matrix(np.asarray(adjacency), name)
    if not np.all(np.isfinite(matrix)):
        raise ValueError(f"{name} must contain only finite values")
    if np.max(np.abs(np.imag(matrix))) > atol:
        raise ValueError("ordinary BGS adjacency weights must be real")
    matrix = np.real(matrix).astype(np.float64, copy=True)
    if np.max(np.abs(matrix - matrix.T)) > atol:
        raise ValueError(f"{name} must be symmetric")
    if float(np.min(matrix)) < -atol:
        raise ValueError("ordinary BGS edge weights must be non-negative")
    matrix[np.abs(matrix) < atol] = 0.0
    np.fill_diagonal(matrix, 0.0)
    return matrix


def validate_density_matrix(
    rho: Array,
    *,
    atol: float = 1e-10,
    repair: bool = False,
) -> Array:
    """Validate a density matrix, optionally repairing roundoff-scale errors.

    ``repair=False`` is intentionally strict so upstream state-generation
    errors are not silently hidden.  ``repair=True`` Hermitianizes, clips
    negative eigenvalues, and renormalizes the state.
    """

    state = _as_square_matrix(np.asarray(rho, dtype=np.complex128), "rho")
    if repair:
        state = 0.5 * (state + state.conj().T)
        values, vectors = np.linalg.eigh(state)
        values = np.clip(values.real, 0.0, None)
        total = float(np.sum(values))
        if total <= atol:
            raise ValueError("rho cannot be repaired because its positive trace is zero")
        state = (vectors * (values / total)[None, :]) @ vectors.conj().T
        return state

    hermitian_error = float(np.max(np.abs(state - state.conj().T)))
    if hermitian_error > atol:
        raise ValueError(
            f"rho must be Hermitian; maximum error is {hermitian_error:.3e}"
        )
    trace = np.trace(state)
    if abs(trace.imag) > atol or abs(trace.real - 1.0) > atol:
        raise ValueError(f"rho must have trace one; trace is {trace}")
    minimum = float(np.min(np.linalg.eigvalsh(state)).real)
    if minimum < -atol:
        raise ValueError(
            f"rho must be positive semidefinite; minimum eigenvalue is {minimum:.3e}"
        )
    return state


@dataclass(frozen=True)
class TensorLabeling:
    """Map graph vertices to a declared product-basis factorization.

    The default ordering is lexicographic with the final subsystem varying
    fastest, matching NumPy's reshape convention and conventional qubit
    bitstring ordering.
    """

    dimensions: tuple[int, ...]
    vertex_labels: tuple[tuple[int, ...], ...] | None = None
    _index: dict[tuple[int, ...], int] = field(init=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        dimensions = tuple(int(value) for value in self.dimensions)
        if not dimensions or any(value < 1 for value in dimensions):
            raise ValueError("all subsystem dimensions must be positive")
        object.__setattr__(self, "dimensions", dimensions)

        labels = self.vertex_labels
        if labels is None:
            labels = tuple(product(*(range(value) for value in dimensions)))
        else:
            labels = tuple(tuple(int(value) for value in label) for label in labels)

        expected = prod(dimensions)
        if len(labels) != expected:
            raise ValueError(
                f"label count {len(labels)} does not match product dimension {expected}"
            )
        if len(set(labels)) != len(labels):
            raise ValueError("vertex labels must be unique")
        for label in labels:
            if len(label) != len(dimensions):
                raise ValueError("each vertex label must contain one index per subsystem")
            if any(index < 0 or index >= dimensions[axis] for axis, index in enumerate(label)):
                raise ValueError(f"vertex label {label} is outside dimensions {dimensions}")

        object.__setattr__(self, "vertex_labels", labels)
        object.__setattr__(self, "_index", {label: i for i, label in enumerate(labels)})

    @property
    def dimension(self) -> int:
        return prod(self.dimensions)

    def label(self, vertex: int) -> tuple[int, ...]:
        assert self.vertex_labels is not None
        return self.vertex_labels[int(vertex)]

    def vertex(self, label: Sequence[int]) -> int:
        key = tuple(int(value) for value in label)
        try:
            return self._index[key]
        except KeyError as exc:
            raise ValueError(f"unknown tensor label {key}") from exc

    def canonical_permutation(self) -> Array:
        """Return ``p`` such that ``rho[p,p]`` is in canonical tensor order."""

        canonical = tuple(product(*(range(value) for value in self.dimensions)))
        return np.asarray([self.vertex(label) for label in canonical], dtype=np.int64)


def laplacian_from_adjacency(adjacency: Array, *, atol: float = 1e-12) -> Array:
    """Return the combinatorial Laplacian of a weighted undirected graph.

    Diagonal adjacency entries (loops) are ignored, as in the BGS
    combinatorial-Laplacian construction.
    """

    matrix = _validate_ordinary_adjacency(adjacency, atol=atol)
    degree = np.sum(matrix, axis=1)
    return np.diag(degree) - matrix


def graph_density_matrix(laplacian: Array, *, atol: float = 1e-10) -> Array:
    """Normalize a non-zero graph Laplacian to a density matrix."""

    operator = _as_square_matrix(
        np.asarray(laplacian, dtype=np.complex128), "laplacian"
    )
    hermitian_error = float(np.max(np.abs(operator - operator.conj().T)))
    if hermitian_error > atol:
        raise ValueError("laplacian must be Hermitian")
    minimum = float(np.min(np.linalg.eigvalsh(operator)).real)
    if minimum < -atol:
        raise ValueError(
            f"laplacian must be positive semidefinite; minimum is {minimum:.3e}"
        )
    trace = np.trace(operator)
    if abs(trace.imag) > atol or trace.real <= atol:
        raise ValueError("laplacian must have a positive real trace")
    state = operator / trace.real
    return validate_density_matrix(state, atol=max(atol, 1e-9))


def adjacency_from_edges(
    dimension: int,
    edges: Iterable[tuple[int, int]],
    weights: Sequence[float] | None = None,
) -> Array:
    """Construct a symmetric adjacency matrix, accumulating repeated edges."""

    dimension = int(dimension)
    if dimension < 2:
        raise ValueError("dimension must be at least two")
    edge_list = [(int(i), int(j)) for i, j in edges]
    if weights is None:
        weight_values = np.ones(len(edge_list), dtype=np.float64)
    else:
        weight_values = np.asarray(weights, dtype=np.float64).reshape(-1)
        if len(weight_values) != len(edge_list):
            raise ValueError("weights must contain one value per edge")
    if np.any(weight_values < 0.0):
        raise ValueError("edge weights must be non-negative")

    adjacency = np.zeros((dimension, dimension), dtype=np.float64)
    for (i, j), weight in zip(edge_list, weight_values):
        if not (0 <= i < dimension and 0 <= j < dimension):
            raise ValueError(f"edge {(i, j)} is outside dimension {dimension}")
        if i == j:
            continue
        adjacency[i, j] += float(weight)
        adjacency[j, i] += float(weight)
    return adjacency


def weighted_edges_from_adjacency(
    adjacency: Array,
    *,
    atol: float = 1e-12,
) -> tuple[list[tuple[int, int]], Array]:
    matrix = _as_square_matrix(np.asarray(adjacency), "adjacency")
    edges: list[tuple[int, int]] = []
    weights: list[float] = []
    for i, j in combinations(range(matrix.shape[0]), 2):
        value = float(np.real(matrix[i, j]))
        if value > atol:
            edges.append((i, j))
            weights.append(value)
    return edges, np.asarray(weights, dtype=np.float64)


def edge_state(i: int, j: int, dimension: int) -> Array:
    """Return ``(|i> - |j>) / sqrt(2)``."""

    i, j, dimension = int(i), int(j), int(dimension)
    if i == j:
        raise ValueError("an edge state requires two distinct vertices")
    if not (0 <= i < dimension and 0 <= j < dimension):
        raise ValueError("edge vertex is outside the Hilbert-space dimension")
    state = np.zeros(dimension, dtype=np.complex128)
    state[i] = 1.0 / np.sqrt(2.0)
    state[j] = -1.0 / np.sqrt(2.0)
    return state


def edge_projector(i: int, j: int, dimension: int) -> Array:
    state = edge_state(i, j, dimension)
    return np.outer(state, state.conj())


def signless_edge_projector(i: int, j: int, dimension: int) -> Array:
    i, j, dimension = int(i), int(j), int(dimension)
    if i == j:
        raise ValueError("an edge state requires two distinct vertices")
    state = np.zeros(dimension, dtype=np.complex128)
    state[i] = 1.0 / np.sqrt(2.0)
    state[j] = 1.0 / np.sqrt(2.0)
    return np.outer(state, state.conj())


def _normalized_mixture_weights(count: int, weights: Sequence[float] | None) -> Array:
    if count < 1:
        raise ValueError("at least one edge is required")
    if weights is None:
        result = np.ones(count, dtype=np.float64)
    else:
        result = np.asarray(weights, dtype=np.float64).reshape(-1)
        if len(result) != count:
            raise ValueError("weights must contain one value per edge")
        if np.any(result < 0.0):
            raise ValueError("mixture weights must be non-negative")
    total = float(np.sum(result))
    if total <= 0.0:
        raise ValueError("mixture weights must have a positive sum")
    return result / total


def edge_mixture(
    edges: Iterable[tuple[int, int]],
    dimension: int,
    weights: Sequence[float] | None = None,
) -> Array:
    edge_list = list(edges)
    coefficients = _normalized_mixture_weights(len(edge_list), weights)
    state = np.zeros((dimension, dimension), dtype=np.complex128)
    for coefficient, (i, j) in zip(coefficients, edge_list):
        state += coefficient * edge_projector(i, j, dimension)
    return validate_density_matrix(state, atol=1e-9)


def signless_edge_mixture(
    edges: Iterable[tuple[int, int]],
    dimension: int,
    weights: Sequence[float] | None = None,
) -> Array:
    edge_list = list(edges)
    coefficients = _normalized_mixture_weights(len(edge_list), weights)
    state = np.zeros((dimension, dimension), dtype=np.complex128)
    for coefficient, (i, j) in zip(coefficients, edge_list):
        state += coefficient * signless_edge_projector(i, j, dimension)
    return validate_density_matrix(state, atol=1e-9)


def von_neumann_entropy(rho: Array, *, atol: float = 1e-15) -> float:
    state = validate_density_matrix(rho, atol=1e-9)
    values = np.linalg.eigvalsh(state).real
    values = values[values > atol]
    return float(-np.sum(values * np.log2(values)))


def partial_transpose(
    rho: Array,
    dimensions: Sequence[int],
    subsystems: int | Iterable[int],
) -> Array:
    """Partially transpose a density matrix in canonical tensor order."""

    dims = tuple(int(value) for value in dimensions)
    if any(value < 1 for value in dims):
        raise ValueError("subsystem dimensions must be positive")
    state = validate_density_matrix(rho, atol=1e-9)
    if state.shape[0] != prod(dims):
        raise ValueError("density-matrix dimension does not match subsystem dimensions")
    selected = {int(subsystems)} if isinstance(subsystems, int) else {int(s) for s in subsystems}
    if any(axis < 0 or axis >= len(dims) for axis in selected):
        raise ValueError("partial-transpose subsystem index is out of range")

    tensor = state.reshape(dims + dims)
    axes = list(range(2 * len(dims)))
    for axis in selected:
        axes[axis], axes[len(dims) + axis] = axes[len(dims) + axis], axes[axis]
    return tensor.transpose(axes).reshape(state.shape)


def negativity(
    rho: Array,
    dimensions: Sequence[int],
    subsystems: int | Iterable[int],
) -> float:
    transformed = partial_transpose(rho, dimensions, subsystems)
    eigenvalues = np.linalg.eigvalsh(0.5 * (transformed + transformed.conj().T)).real
    return float(np.sum(np.abs(eigenvalues[eigenvalues < 0.0])))


def logarithmic_negativity(
    rho: Array,
    dimensions: Sequence[int],
    subsystems: int | Iterable[int],
) -> float:
    return float(np.log2(1.0 + 2.0 * negativity(rho, dimensions, subsystems)))


def relabel_density_matrix(rho: Array, permutation: Sequence[int]) -> Array:
    """Reorder vertices using ``permutation[new_index] = old_index``."""

    state = validate_density_matrix(rho, atol=1e-9)
    order = np.asarray(permutation, dtype=np.int64).reshape(-1)
    if sorted(order.tolist()) != list(range(state.shape[0])):
        raise ValueError("permutation must contain every vertex exactly once")
    return state[np.ix_(order, order)]


def direct_product_adjacency(adjacency_a: Array, adjacency_b: Array) -> Array:
    """Adjacency-Kronecker/direct graph product used in the BGS paper.

    The explicit name avoids conflating it with Cartesian and strong graph
    products, whose Laplacians and physical interpretations differ.
    """

    a = _validate_ordinary_adjacency(adjacency_a, "adjacency_a")
    b = _validate_ordinary_adjacency(adjacency_b, "adjacency_b")
    return np.kron(a, b)


def direct_product_density_formula(adjacency_a: Array, adjacency_b: Array) -> Array:
    """Return the separable density-state formula for a direct graph product."""

    a = _validate_ordinary_adjacency(adjacency_a, "adjacency_a")
    b = _validate_ordinary_adjacency(adjacency_b, "adjacency_b")
    edges_a, weights_a = weighted_edges_from_adjacency(a)
    edges_b, weights_b = weighted_edges_from_adjacency(b)
    rho_a = edge_mixture(edges_a, a.shape[0], weights_a)
    rho_b = edge_mixture(edges_b, b.shape[0], weights_b)
    plus_a = signless_edge_mixture(edges_a, a.shape[0], weights_a)
    plus_b = signless_edge_mixture(edges_b, b.shape[0], weights_b)
    return 0.5 * (np.kron(rho_a, plus_b) + np.kron(plus_a, rho_b))


@dataclass(frozen=True)
class GraphProjectionReport:
    rho_projected: Array
    edge_weights: Array
    edges: tuple[tuple[int, int], ...]
    frobenius_error: float
    trace_distance: float
    imaginary_residual: float
    rank_deficit: int
    success: bool
    iterations: int
    message: str


def project_density_to_graph_state(
    rho: Array,
    *,
    candidate_edges: Iterable[tuple[int, int]] | None = None,
    max_iterations: int = 2000,
    tolerance: float = 1e-11,
) -> GraphProjectionReport:
    """Find the nearest convex mixture of ordinary BGS edge projectors.

    The default candidate set is the complete graph.  A non-zero residual is
    expected for generic complex or full-rank density matrices and is part of
    the result, not an error condition.
    """

    state = validate_density_matrix(rho, atol=1e-8)
    dimension = state.shape[0]
    edges = tuple(
        combinations(range(dimension), 2)
        if candidate_edges is None
        else ((int(i), int(j)) for i, j in candidate_edges)
    )
    if not edges:
        raise ValueError("candidate_edges must contain at least one edge")
    if len(set(edges)) != len(edges):
        raise ValueError("candidate_edges must not contain duplicates")
    projectors = np.stack(
        [edge_projector(i, j, dimension) for i, j in edges], axis=0
    )

    def mixture(coefficients: Array) -> Array:
        return np.einsum("e,eij->ij", coefficients, projectors, optimize=True)

    def objective(coefficients: Array) -> float:
        residual = mixture(coefficients) - state
        return float(np.real(np.vdot(residual, residual)))

    def gradient(coefficients: Array) -> Array:
        residual = mixture(coefficients) - state
        return 2.0 * np.real(
            np.einsum("eij,ij->e", projectors.conj(), residual, optimize=True)
        )

    initial = np.full(len(edges), 1.0 / len(edges), dtype=np.float64)
    result = minimize(
        objective,
        initial,
        jac=gradient,
        method="SLSQP",
        bounds=[(0.0, 1.0)] * len(edges),
        constraints=[
            {
                "type": "eq",
                "fun": lambda values: float(np.sum(values) - 1.0),
                "jac": lambda values: np.ones_like(values),
            }
        ],
        options={"maxiter": int(max_iterations), "ftol": float(tolerance)},
    )

    coefficients = np.clip(np.asarray(result.x, dtype=np.float64), 0.0, None)
    coefficients /= max(float(np.sum(coefficients)), 1e-15)
    projected = validate_density_matrix(mixture(coefficients), atol=1e-8, repair=True)
    difference = projected - state
    hermitian_difference = 0.5 * (difference + difference.conj().T)
    trace_distance = 0.5 * float(
        np.sum(np.abs(np.linalg.eigvalsh(hermitian_difference).real))
    )
    rank = int(np.linalg.matrix_rank(projected, tol=1e-9))
    return GraphProjectionReport(
        rho_projected=projected,
        edge_weights=coefficients,
        edges=edges,
        frobenius_error=float(np.linalg.norm(difference, ord="fro")),
        trace_distance=trace_distance,
        imaginary_residual=float(np.linalg.norm(np.imag(state), ord="fro")),
        rank_deficit=dimension - rank,
        success=bool(result.success),
        iterations=int(getattr(result, "nit", 0)),
        message=str(result.message),
    )


@dataclass(frozen=True)
class GraphDensityState:
    adjacency: Array
    laplacian: Array
    rho_graph: Array
    entropy_bits: float
    purity: float
    rank: int
    nullity: int
    component_count: int
    edges: tuple[tuple[int, int], ...]
    edge_weights: Array
    labeling: TensorLabeling | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_adjacency(
        cls,
        adjacency: Array,
        *,
        labeling: TensorLabeling | None = None,
        atol: float = 1e-10,
        metadata: dict[str, Any] | None = None,
    ) -> "GraphDensityState":
        matrix = _as_square_matrix(np.asarray(adjacency), "adjacency")
        if labeling is not None and labeling.dimension != matrix.shape[0]:
            raise ValueError("tensor labeling dimension does not match the graph")
        laplacian = laplacian_from_adjacency(matrix, atol=atol)
        clean_adjacency = -np.real(laplacian)
        np.fill_diagonal(clean_adjacency, 0.0)
        state = graph_density_matrix(laplacian, atol=atol)
        eigenvalues = np.linalg.eigvalsh(laplacian).real
        zero_tolerance = max(atol, atol * float(np.max(np.abs(eigenvalues))))
        nullity = int(np.sum(np.abs(eigenvalues) <= zero_tolerance))
        edges, weights = weighted_edges_from_adjacency(clean_adjacency, atol=atol)
        mixture = edge_mixture(edges, matrix.shape[0], weights)
        residual = float(np.linalg.norm(state - mixture, ord="fro"))
        return cls(
            adjacency=clean_adjacency,
            laplacian=laplacian,
            rho_graph=state,
            entropy_bits=von_neumann_entropy(state),
            purity=float(np.real(np.trace(state @ state))),
            rank=int(np.linalg.matrix_rank(state, tol=1e-9)),
            nullity=nullity,
            component_count=nullity,
            edges=tuple(edges),
            edge_weights=weights,
            labeling=labeling,
            metadata={
                **({} if metadata is None else metadata),
                "edge_mixture_residual": residual,
                "construction": "ordinary_weighted_bgs_laplacian",
            },
        )

    def negativity(self, subsystems: int | Iterable[int]) -> float:
        if self.labeling is None:
            raise ValueError("negativity requires an explicit tensor labeling")
        canonical = relabel_density_matrix(
            self.rho_graph, self.labeling.canonical_permutation()
        )
        return negativity(canonical, self.labeling.dimensions, subsystems)


__all__ = [
    "GraphDensityState",
    "GraphProjectionReport",
    "TensorLabeling",
    "adjacency_from_edges",
    "direct_product_adjacency",
    "direct_product_density_formula",
    "edge_mixture",
    "edge_projector",
    "edge_state",
    "graph_density_matrix",
    "laplacian_from_adjacency",
    "logarithmic_negativity",
    "negativity",
    "partial_transpose",
    "project_density_to_graph_state",
    "relabel_density_matrix",
    "signless_edge_mixture",
    "validate_density_matrix",
    "von_neumann_entropy",
    "weighted_edges_from_adjacency",
]
