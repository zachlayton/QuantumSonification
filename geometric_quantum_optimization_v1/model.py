"""Constrained QAOA and Fubini--Study diagnostics on ``J(4, 2)``."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
import math
from typing import Iterable

import numpy as np

Array = np.ndarray


@dataclass(frozen=True)
class HexanyVertex:
    index: int
    factor_indices: tuple[int, int]
    factors: tuple[int, int]
    bitmask: int
    product: int
    label: str
    complement_index: int
    ratio: float
    cents: float


@dataclass(frozen=True)
class HexanyProblem:
    factors: tuple[int, int, int, int]
    vertices: tuple[HexanyVertex, ...]
    johnson_edges: tuple[tuple[int, int], ...]
    decision_edges: tuple[tuple[int, int, float], ...]
    cut_values: Array
    energies: Array
    optimum_cut: float
    optimum_vertices: tuple[int, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "factors": list(self.factors),
            "vertices": [
                {
                    "index": vertex.index,
                    "factor_indices": list(vertex.factor_indices),
                    "factors": list(vertex.factors),
                    "bitmask": vertex.bitmask,
                    "bitstring": format(vertex.bitmask, "04b"),
                    "product": vertex.product,
                    "label": vertex.label,
                    "complement_index": vertex.complement_index,
                    "ratio": vertex.ratio,
                    "cents": vertex.cents,
                    "cut_value": float(self.cut_values[vertex.index]),
                    "energy": float(self.energies[vertex.index]),
                }
                for vertex in self.vertices
            ],
            "johnson_edges": [list(edge) for edge in self.johnson_edges],
            "decision_edges": [list(edge) for edge in self.decision_edges],
            "optimum_cut": self.optimum_cut,
            "optimum_vertices": list(self.optimum_vertices),
        }


def _fold_octave(value: float) -> float:
    while value < 1.0:
        value *= 2.0
    while value >= 2.0:
        value *= 0.5
    return value


def build_hexany_problem(
    decision_edges: Iterable[tuple[int, int, float]] | None = None,
) -> HexanyProblem:
    factors = (1, 3, 5, 7)
    subsets = tuple(combinations(range(4), 2))
    subset_to_index = {subset: index for index, subset in enumerate(subsets)}
    universe = frozenset(range(4))
    products = tuple(factors[a] * factors[b] for a, b in subsets)
    anchor = products[0]
    vertices: list[HexanyVertex] = []
    for index, (subset, product) in enumerate(zip(subsets, products)):
        complement = tuple(sorted(universe.difference(subset)))
        selected = (factors[subset[0]], factors[subset[1]])
        ratio = _fold_octave(product / anchor)
        vertices.append(
            HexanyVertex(
                index=index,
                factor_indices=subset,
                factors=selected,
                bitmask=sum(1 << value for value in subset),
                product=product,
                label=f"{selected[0]}·{selected[1]}",
                complement_index=subset_to_index[complement],
                ratio=ratio,
                cents=1200.0 * math.log2(ratio),
            )
        )
    johnson_edges = tuple(
        (left, right)
        for left, right in combinations(range(6), 2)
        if len(set(subsets[left]).symmetric_difference(subsets[right])) == 2
    )
    weighted_edges = tuple(
        decision_edges
        if decision_edges is not None
        else (
            (0, 1, 1.00),
            (0, 2, 1.60),
            (0, 3, 0.70),
            (1, 2, 0.90),
            (1, 3, 1.40),
            (2, 3, 0.50),
        )
    )
    for left, right, weight in weighted_edges:
        if not (0 <= int(left) < 4 and 0 <= int(right) < 4 and left != right):
            raise ValueError("decision edges must join distinct nodes in 0..3")
        if not math.isfinite(float(weight)) or float(weight) < 0.0:
            raise ValueError("decision edge weights must be finite and nonnegative")
    cuts = np.empty(6, dtype=np.float64)
    for index, subset in enumerate(subsets):
        side = set(subset)
        cuts[index] = sum(
            float(weight)
            for left, right, weight in weighted_edges
            if (left in side) != (right in side)
        )
    maximum = float(np.max(cuts))
    minimum = float(np.min(cuts))
    span = maximum - minimum
    energies = (maximum - cuts) / span if span > 1e-15 else np.zeros_like(cuts)
    optimum = tuple(int(index) for index in np.flatnonzero(np.isclose(cuts, maximum)))
    return HexanyProblem(
        factors=factors,
        vertices=tuple(vertices),
        johnson_edges=johnson_edges,
        decision_edges=weighted_edges,
        cut_values=cuts,
        energies=energies,
        optimum_cut=maximum,
        optimum_vertices=optimum,
    )


@dataclass(frozen=True)
class StateMetrics:
    objective: float
    expected_cut: float
    approximation_ratio: float
    optimum_probability: float
    entropy_bits: float
    participation: float
    phase_order: float
    geodesic_step: float
    shell_leakage: float


class HexanyOptimizationModel:
    def __init__(self, problem: HexanyProblem | None = None, *, layers: int = 2) -> None:
        if int(layers) < 1:
            raise ValueError("layers must be positive")
        self.problem = problem or build_hexany_problem()
        self.layers = int(layers)
        self.parameter_count = 2 * self.layers
        adjacency = np.zeros((6, 6), dtype=np.float64)
        for left, right in self.problem.johnson_edges:
            adjacency[left, right] = adjacency[right, left] = 1.0
        self.mixer = adjacency / 4.0
        self._mixer_values, self._mixer_vectors = np.linalg.eigh(self.mixer)
        self.initial_state = np.full(6, 1.0 / math.sqrt(6.0), dtype=np.complex128)

    def _mix(self, state: Array, beta: float) -> Array:
        modal = self._mixer_vectors.T.conj() @ state
        modal *= np.exp(-1j * float(beta) * self._mixer_values)
        return self._mixer_vectors @ modal

    def state(self, theta: Array) -> Array:
        parameters = np.asarray(theta, dtype=np.float64)
        if parameters.shape != (self.parameter_count,):
            raise ValueError(f"theta must have shape ({self.parameter_count},)")
        if not np.all(np.isfinite(parameters)):
            raise ValueError("theta must be finite")
        state = self.initial_state.copy()
        for layer in range(self.layers):
            gamma, beta = parameters[2 * layer : 2 * layer + 2]
            state *= np.exp(-1j * gamma * self.problem.energies)
            state = self._mix(state, beta)
        return state / np.linalg.norm(state)

    def objective_from_state(self, state: Array) -> float:
        return float(np.abs(np.asarray(state)) ** 2 @ self.problem.energies)

    def objective(self, theta: Array) -> float:
        return self.objective_from_state(self.state(theta))

    def metrics_from_state(
        self, state: Array, *, previous_state: Array | None = None
    ) -> StateMetrics:
        state = np.asarray(state, dtype=np.complex128)
        probabilities = np.abs(state) ** 2
        expected_cut = float(probabilities @ self.problem.cut_values)
        entropy = float(-np.sum(probabilities * np.log2(np.maximum(probabilities, 1e-300))))
        phase_order = float(abs(np.sum(probabilities * np.exp(1j * np.angle(state)))))
        return StateMetrics(
            objective=float(probabilities @ self.problem.energies),
            expected_cut=expected_cut,
            approximation_ratio=expected_cut / self.problem.optimum_cut,
            optimum_probability=float(np.sum(probabilities[list(self.problem.optimum_vertices)])),
            entropy_bits=entropy,
            participation=float(1.0 / np.sum(probabilities**2)),
            phase_order=phase_order,
            geodesic_step=(
                0.0 if previous_state is None else fubini_study_distance(previous_state, state)
            ),
            shell_leakage=0.0,
        )

    def derivatives(self, theta: Array, epsilon: float = 1e-5) -> tuple[Array, Array]:
        parameters = np.asarray(theta, dtype=np.float64)
        state = self.state(parameters)
        derivatives = np.empty((self.parameter_count, 6), dtype=np.complex128)
        for index in range(self.parameter_count):
            shift = np.zeros_like(parameters)
            shift[index] = epsilon
            derivatives[index] = (
                self.state(parameters + shift) - self.state(parameters - shift)
            ) / (2.0 * epsilon)
        return state, derivatives

    def objective_gradient_and_metric(
        self, theta: Array, *, epsilon: float = 1e-5
    ) -> tuple[Array, Array]:
        state, derivatives = self.derivatives(theta, epsilon)
        gradient = 2.0 * np.real(derivatives.conj() @ (self.problem.energies * state))
        overlaps = derivatives.conj() @ state
        gram = derivatives.conj() @ derivatives.T
        metric = np.real(gram - np.outer(overlaps, overlaps.conj()))
        return np.asarray(gradient), 0.5 * (metric + metric.T)

    def edge_currents_from_state(self, state: Array) -> tuple[tuple[int, int, float], ...]:
        state = np.asarray(state, dtype=np.complex128)
        return tuple(
            (
                left,
                right,
                float(2.0 * np.imag(np.conj(state[left]) * self.mixer[left, right] * state[right])),
            )
            for left, right in self.problem.johnson_edges
        )


def fubini_study_distance(left: Array, right: Array) -> float:
    a = np.asarray(left, dtype=np.complex128)
    b = np.asarray(right, dtype=np.complex128)
    overlap = abs(np.vdot(a, b)) / max(float(np.linalg.norm(a) * np.linalg.norm(b)), 1e-300)
    return float(np.arccos(np.clip(overlap, 0.0, 1.0)))
