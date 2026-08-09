"""Pairwise quantum-correlation clock for live density matrices."""

from __future__ import annotations

from itertools import combinations
import math
import time
from typing import Any

import numpy as np

from .core import (
    CorrelationSnapshot,
    EdgeClock,
    TemporalV2Config,
    Tick,
    _normalize_density,
)


def _qubit_count(dimension: int) -> int:
    count = int(round(math.log2(dimension)))
    if 2**count != dimension:
        raise ValueError("density dimension must be a power of two")
    return count


def reduced_density(rho: np.ndarray, keep_qubits: tuple[int, ...]) -> np.ndarray:
    """Partial trace using Qiskit's least-significant-bit qubit ordering."""
    rho = _normalize_density(rho)
    n_qubits = _qubit_count(rho.shape[0])
    if not keep_qubits:
        raise ValueError("keep_qubits cannot be empty")
    if any(q < 0 or q >= n_qubits for q in keep_qubits):
        raise ValueError("invalid qubit index")
    keep_axes = [n_qubits - 1 - q for q in keep_qubits]
    trace_axes = [axis for axis in range(n_qubits) if axis not in keep_axes]
    tensor = rho.reshape([2] * (2 * n_qubits))
    permutation = (
        keep_axes
        + trace_axes
        + [axis + n_qubits for axis in keep_axes]
        + [axis + n_qubits for axis in trace_axes]
    )
    arranged = np.transpose(tensor, permutation)
    keep_dimension = 2 ** len(keep_axes)
    trace_dimension = 2 ** len(trace_axes)
    arranged = arranged.reshape(
        keep_dimension, trace_dimension, keep_dimension, trace_dimension
    )
    return np.trace(arranged, axis1=1, axis2=3)


def von_neumann_entropy(rho: np.ndarray) -> float:
    eigenvalues = np.clip(np.linalg.eigvalsh(_normalize_density(rho)).real, 0.0, 1.0)
    nonzero = eigenvalues[eigenvalues > 1e-15]
    return float(-np.sum(nonzero * np.log2(nonzero)))


def pairwise_mutual_information(rho: np.ndarray, left: int, right: int) -> float:
    pair = reduced_density(rho, (left, right))
    left_state = reduced_density(rho, (left,))
    right_state = reduced_density(rho, (right,))
    value = (
        von_neumann_entropy(left_state)
        + von_neumann_entropy(right_state)
        - von_neumann_entropy(pair)
    )
    # Two qubits have at most two bits of quantum mutual information.
    return float(np.clip(value / 2.0, 0.0, 1.0))


class DensityCorrelationClockSystem:
    """Advance only when pairwise quantum mutual information changes."""

    def __init__(
        self,
        config: TemporalV2Config,
        publisher: Any = None,
    ) -> None:
        self.config = config
        self.publisher = publisher
        self.edges: dict[str, EdgeClock] = {}
        self.observation = 0
        self.relational_time = 0
        self.started = time.monotonic()

    def update(
        self,
        rho: np.ndarray,
        source_revision: int = 0,
    ) -> CorrelationSnapshot:
        current = _normalize_density(rho)
        n_qubits = _qubit_count(current.shape[0])
        if n_qubits < 2:
            raise ValueError("correlation clock requires at least two qubits")
        pairs = list(combinations(range(n_qubits), 2))
        for left, right in pairs:
            name = f"q{left}:q{right}"
            self.edges.setdefault(
                name,
                EdgeClock(
                    name,
                    self.config.change_quantum,
                    self.config.change_deadband,
                ),
            )
        relations: dict[str, dict[str, float | int | str]] = {}
        ticks: list[Tick] = []
        for edge_index, (left, right) in enumerate(pairs):
            name = f"q{left}:q{right}"
            edge = self.edges[name]
            correlation = pairwise_mutual_information(current, left, right)
            differentiation, emissions = edge.sample(
                correlation,
                self.config.max_ticks_per_edge_observation,
            )
            inspection = edge.inspect()
            inspection["differentiation"] = differentiation
            relations[name] = inspection
            for kind, strength in emissions:
                self.relational_time += 1
                ticks.append(
                    self._make_tick(
                        edge,
                        edge_index,
                        kind,
                        correlation,
                        differentiation,
                        strength,
                    )
                )
        purity = float(np.trace(current @ current).real)
        off_diagonal = current - np.diag(np.diag(current))
        coherence = float(
            np.sum(np.abs(off_diagonal)) / max(1, current.shape[0] - 1)
        )
        strongest = off_diagonal.flat[int(np.argmax(np.abs(off_diagonal)))]
        phase = float(np.angle(strongest) % math.tau) if abs(strongest) > 1e-15 else 0.0
        nodes = {}
        for qubit in range(n_qubits):
            local = reduced_density(current, (qubit,))
            nodes[f"q{qubit}"] = {
                "phase": float(np.angle(local[0, 1]) % math.tau) if abs(local[0, 1]) > 1e-15 else 0.0,
                "energy": float(local[1, 1].real),
                "memory": float(np.trace(local @ local).real),
                "drive": von_neumann_entropy(local),
            }
        snapshot = CorrelationSnapshot(
            observation=int(source_revision),
            wall_elapsed=time.monotonic() - self.started,
            relational_time=self.relational_time,
            source="canonical-density-engine",
            clock_phase=phase,
            clock_confidence=float(np.clip(coherence, 0.0, 1.0)),
            conditional_purity=purity,
            nodes=nodes,
            relations=relations,
            ticks=ticks,
        )
        if self.publisher is not None:
            self.publisher.publish(snapshot)
        self.observation += 1
        return snapshot

    def set_change_quantum(self, value: float) -> float:
        value = float(value)
        if not np.isfinite(value) or value <= 0.0:
            raise ValueError("change quantum must be finite and positive")
        self.config.change_quantum = value
        for edge in self.edges.values():
            edge.change_quantum = value
        return value

    def _make_tick(
        self,
        edge: EdgeClock,
        edge_index: int,
        kind: str,
        correlation: float,
        differentiation: float,
        strength: float,
    ) -> Tick:
        scale = (0, 2, 5, 7, 9, 12)
        midi = 42 + 5 * edge_index + scale[edge.edge_time % len(scale)]
        if kind == "differentiate":
            midi += 6
        velocity = int(np.clip(45 + 72 * strength, 1, 127))
        duration = float(
            np.clip(
                (160.0 + 1200.0 * correlation)
                * (1.2 if kind == "correlate" else 0.45),
                35.0,
                1600.0,
            )
        )
        return Tick(
            tick_id=f"t{self.relational_time:09d}",
            edge=edge.edge,
            kind=kind,
            edge_time=edge.edge_time,
            relational_time=self.relational_time,
            observation=self.observation,
            correlation=correlation,
            differentiation=differentiation,
            strength=strength,
            midi=int(np.clip(midi, 24, 96)),
            velocity=velocity,
            duration_ms=duration,
        )
