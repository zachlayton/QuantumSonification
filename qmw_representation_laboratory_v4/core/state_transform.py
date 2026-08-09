"""General state-transform contract and density-matrix validation."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Mapping
from typing import Any

import numpy as np


DEFAULT_TOLERANCE = 1e-10
TransformContext = Mapping[str, Any] | None


def square_matrix(value: Any, *, name: str) -> np.ndarray:
    matrix = np.asarray(value, dtype=complex)
    if matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1]:
        raise ValueError(f"{name} must be a square matrix")
    if matrix.shape[0] == 0:
        raise ValueError(f"{name} must not be empty")
    if not np.all(np.isfinite(matrix)):
        raise ValueError(f"{name} contains a non-finite value")
    return matrix


def validate_density_matrix(
    rho: Any,
    *,
    tolerance: float = DEFAULT_TOLERANCE,
) -> np.ndarray:
    matrix = square_matrix(rho, name="rho")
    if not np.allclose(matrix, matrix.conj().T, atol=tolerance, rtol=0.0):
        raise ValueError("rho must be Hermitian")
    trace = complex(np.trace(matrix))
    if abs(trace.imag) > tolerance or not np.isclose(
        trace.real, 1.0, atol=tolerance, rtol=0.0
    ):
        raise ValueError("rho must have trace 1")
    if float(np.min(np.linalg.eigvalsh(matrix))) < -tolerance:
        raise ValueError("rho must be positive semidefinite")
    return matrix


class StateTransform(ABC):
    name: str
    description: str
    kind = "state_transform"

    @abstractmethod
    def apply(
        self,
        rho: Any,
        context: TransformContext = None,
    ) -> np.ndarray:
        """Return one transformed density representation."""

    def metadata(
        self,
        dimension: int,
        context: TransformContext = None,
    ) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "kind": self.kind,
            "dimension": int(dimension),
            "unitary": False,
        }
