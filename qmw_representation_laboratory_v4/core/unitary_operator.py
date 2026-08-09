"""Validated unitary specialization of StateTransform."""

from __future__ import annotations

from abc import abstractmethod
from typing import Any

import numpy as np

from .state_transform import (
    DEFAULT_TOLERANCE,
    StateTransform,
    TransformContext,
    square_matrix,
    validate_density_matrix,
)


def validate_unitary(
    value: Any,
    dimension: int,
    *,
    tolerance: float = DEFAULT_TOLERANCE,
) -> np.ndarray:
    matrix = square_matrix(value, name="unitary")
    if matrix.shape != (dimension, dimension):
        raise ValueError(
            f"unitary has shape {matrix.shape}; expected {(dimension, dimension)}"
        )
    identity = np.eye(dimension, dtype=complex)
    if not np.allclose(
        matrix @ matrix.conj().T,
        identity,
        atol=tolerance,
        rtol=0.0,
    ):
        raise ValueError("unitary must satisfy U U† = I")
    return matrix


class UnitaryOperator(StateTransform):
    kind = "basis"

    @abstractmethod
    def unitary(
        self,
        dimension: int,
        context: TransformContext = None,
    ) -> np.ndarray:
        """Return U for the requested Hilbert dimension."""

    def checked_unitary(
        self,
        dimension: int,
        context: TransformContext = None,
    ) -> np.ndarray:
        return validate_unitary(self.unitary(dimension, context), dimension)

    def apply(
        self,
        rho: Any,
        context: TransformContext = None,
    ) -> np.ndarray:
        density = validate_density_matrix(rho)
        unitary = self.checked_unitary(density.shape[0], context)
        transformed = unitary @ density @ unitary.conj().T
        return (transformed + transformed.conj().T) / 2.0

    def transform(
        self,
        rho: Any,
        context: TransformContext = None,
    ) -> np.ndarray:
        return self.apply(rho, context)

    def transform_observable(
        self,
        observable: Any,
        context: TransformContext = None,
    ) -> np.ndarray:
        matrix = square_matrix(observable, name="observable")
        unitary = self.checked_unitary(matrix.shape[0], context)
        return unitary @ matrix @ unitary.conj().T

    def pullback_observable(
        self,
        observable: Any,
        context: TransformContext = None,
    ) -> np.ndarray:
        matrix = square_matrix(observable, name="observable")
        unitary = self.checked_unitary(matrix.shape[0], context)
        return unitary.conj().T @ matrix @ unitary

    def metadata(
        self,
        dimension: int,
        context: TransformContext = None,
    ) -> dict[str, Any]:
        self.checked_unitary(dimension, context)
        return {
            "name": self.name,
            "description": self.description,
            "kind": self.kind,
            "dimension": int(dimension),
            "unitary": True,
            "convention": "rho_prime = U rho U_dagger",
        }
