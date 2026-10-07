"""Discrete periodic evolution as a unitary representation transform."""

from __future__ import annotations

from typing import Any

import numpy as np

from ..core import (
    TransformContext,
    UnitaryOperator,
    square_matrix,
    validate_unitary,
)


class FloquetOperator(UnitaryOperator):
    name = "floquet"
    description = "Repeated application of one unitary Floquet period."
    kind = "dynamics"

    def __init__(
        self,
        period_unitary: Any,
        *,
        steps: int = 1,
        period: float | None = None,
    ) -> None:
        matrix = square_matrix(period_unitary, name="Floquet period unitary")
        validate_unitary(matrix, matrix.shape[0])
        if int(steps) != steps or steps < 0:
            raise ValueError("Floquet steps must be a non-negative integer")
        self._period_unitary = np.array(matrix, copy=True)
        self.steps = int(steps)
        self.period = None if period is None else float(period)

    @classmethod
    def from_hamiltonian(
        cls,
        hamiltonian: Any,
        *,
        period: float = 1.0,
        steps: int = 1,
    ) -> "FloquetOperator":
        matrix = square_matrix(hamiltonian, name="hamiltonian")
        if not np.allclose(matrix, matrix.conj().T, atol=1e-10, rtol=0.0):
            raise ValueError("hamiltonian must be Hermitian")
        values, vectors = np.linalg.eigh(matrix)
        evolution = (
            vectors
            @ np.diag(np.exp(-1j * values * float(period)))
            @ vectors.conj().T
        )
        return cls(evolution, steps=steps, period=period)

    def unitary(self, dimension: int, context: TransformContext = None) -> np.ndarray:
        if self._period_unitary.shape != (dimension, dimension):
            raise ValueError("Floquet and density dimensions do not match")
        return np.linalg.matrix_power(self._period_unitary, self.steps)

    def metadata(
        self, dimension: int, context: TransformContext = None
    ) -> dict[str, Any]:
        metadata = super().metadata(dimension, context)
        metadata.update(steps=self.steps, period=self.period)
        return metadata
