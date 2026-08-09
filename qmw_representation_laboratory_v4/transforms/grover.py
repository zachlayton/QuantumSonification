"""Grover oracle/diffusion iterations as a reversible transform."""

from __future__ import annotations

from typing import Any, Iterable

import numpy as np

from ..core import TransformContext, UnitaryOperator


class GroverAmplifiedBasis(UnitaryOperator):
    name = "grover_amplified"
    description = "Grover oracle and diffusion iterations over marked states."
    kind = "amplification"

    def __init__(
        self,
        marked_states: Iterable[int],
        *,
        iterations: int = 1,
    ) -> None:
        marked = tuple(sorted({int(value) for value in marked_states}))
        if not marked or marked[0] < 0:
            raise ValueError("at least one non-negative marked state is required")
        if int(iterations) != iterations or iterations < 0:
            raise ValueError("Grover iterations must be a non-negative integer")
        self.marked_states = marked
        self.iterations = int(iterations)

    def unitary(self, dimension: int, context: TransformContext = None) -> np.ndarray:
        if dimension <= self.marked_states[-1]:
            raise ValueError("marked state lies outside the Hilbert dimension")
        oracle = np.eye(dimension, dtype=complex)
        for state in self.marked_states:
            oracle[state, state] = -1.0
        uniform = np.ones(dimension, dtype=complex) / np.sqrt(dimension)
        diffusion = 2.0 * np.outer(uniform, uniform.conj()) - np.eye(dimension)
        return np.linalg.matrix_power(diffusion @ oracle, self.iterations)

    def metadata(
        self, dimension: int, context: TransformContext = None
    ) -> dict[str, Any]:
        metadata = super().metadata(dimension, context)
        metadata.update(
            marked_states=list(self.marked_states),
            iterations=self.iterations,
        )
        return metadata
