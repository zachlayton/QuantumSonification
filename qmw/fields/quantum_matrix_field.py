"""Primary complex-matrix field representation for QMW."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

import numpy as np


@dataclass(frozen=True)
class QuantumMatrixField:
    """One matrix slice and its non-destructive derived views.

    ``complex_matrix`` is primary. ``buffer`` is a reversible row-major complex
    representation; magnitude, phase, and normalized magnitude are derived.
    """

    complex_matrix: np.ndarray
    eta: float | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        matrix = np.asarray(self.complex_matrix, dtype=np.complex128)
        if matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1]:
            raise ValueError(f"complex_matrix must be square, got {matrix.shape}")
        if not np.all(np.isfinite(matrix)):
            raise ValueError("complex_matrix contains non-finite values")
        object.__setattr__(self, "complex_matrix", matrix.copy())
        object.__setattr__(self, "metadata", dict(self.metadata))

    @property
    def dimension(self) -> int:
        return self.complex_matrix.shape[0]

    @property
    def magnitude(self) -> np.ndarray:
        return np.abs(self.complex_matrix)

    @property
    def phase(self) -> np.ndarray:
        return np.angle(self.complex_matrix)

    @property
    def normalized_magnitude(self) -> np.ndarray:
        magnitude = self.magnitude
        maximum = float(np.max(magnitude))
        if maximum <= 1e-15:
            return np.zeros_like(magnitude, dtype=float)
        return magnitude / maximum

    @property
    def buffer(self) -> np.ndarray:
        return self.flatten(self.complex_matrix)

    @staticmethod
    def flatten(matrix: np.ndarray) -> np.ndarray:
        value = np.asarray(matrix)
        if value.ndim != 2 or value.shape[0] != value.shape[1]:
            raise ValueError(f"matrix must be square, got {value.shape}")
        return value.reshape(value.size, order="C").copy()

    @staticmethod
    def unflatten(buffer: np.ndarray, dimension: int = 16) -> np.ndarray:
        value = np.asarray(buffer)
        expected = int(dimension) ** 2
        if value.ndim != 1 or value.size != expected:
            raise ValueError(
                f"buffer must be one-dimensional with {expected} values, got {value.shape}"
            )
        return value.reshape((dimension, dimension), order="C").copy()

