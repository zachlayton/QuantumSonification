"""Continuous sampling across the discrete matrix indices m and n."""

from __future__ import annotations

from enum import Enum

import numpy as np


class BoundaryMode(str, Enum):
    CLAMP = "clamp"
    RAISE = "raise"
    WRAP = "wrap"


class ManifoldSampler:
    """Bilinear complex sampler for a square matrix slice."""

    def __init__(self, boundary: BoundaryMode | str = BoundaryMode.CLAMP) -> None:
        self.boundary = BoundaryMode(boundary)

    @staticmethod
    def _matrix(matrix: np.ndarray) -> np.ndarray:
        value = np.asarray(matrix)
        if value.ndim != 2 or value.shape[0] != value.shape[1]:
            raise ValueError(f"matrix must be square, got {value.shape}")
        return value

    def _coordinate(self, value: float, dimension: int, name: str) -> float:
        coordinate = float(value)
        if not np.isfinite(coordinate):
            raise ValueError(f"{name} must be finite")
        if self.boundary is BoundaryMode.RAISE:
            if coordinate < 0.0 or coordinate > dimension - 1:
                raise IndexError(f"{name}={coordinate} is outside [0, {dimension - 1}]")
            return coordinate
        if self.boundary is BoundaryMode.WRAP:
            return coordinate % dimension
        return float(np.clip(coordinate, 0.0, dimension - 1.0))

    def _indices(self, coordinate: float, dimension: int) -> tuple[int, int, float]:
        lower = int(np.floor(coordinate))
        fraction = coordinate - lower
        if self.boundary is BoundaryMode.WRAP:
            return lower % dimension, (lower + 1) % dimension, fraction
        upper = min(lower + 1, dimension - 1)
        return lower, upper, fraction

    def sample(self, matrix: np.ndarray, m: float, n: float) -> complex:
        value = self._matrix(matrix)
        dimension = value.shape[0]
        mc = self._coordinate(m, dimension, "m")
        nc = self._coordinate(n, dimension, "n")
        m0, m1, tm = self._indices(mc, dimension)
        n0, n1, tn = self._indices(nc, dimension)
        top = (1.0 - tn) * value[m0, n0] + tn * value[m0, n1]
        bottom = (1.0 - tn) * value[m1, n0] + tn * value[m1, n1]
        return complex((1.0 - tm) * top + tm * bottom)

    def spatial_gradient(
        self, matrix: np.ndarray, m: float, n: float
    ) -> tuple[complex, complex]:
        """Return analytic derivatives of the local bilinear interpolant."""
        value = self._matrix(matrix)
        dimension = value.shape[0]
        mc = self._coordinate(m, dimension, "m")
        nc = self._coordinate(n, dimension, "n")
        m0, m1, tm = self._indices(mc, dimension)
        n0, n1, tn = self._indices(nc, dimension)

        if m0 == m1:
            derivative_m = 0.0j
        else:
            derivative_m = (
                (1.0 - tn) * (value[m1, n0] - value[m0, n0])
                + tn * (value[m1, n1] - value[m0, n1])
            )
        if n0 == n1:
            derivative_n = 0.0j
        else:
            derivative_n = (
                (1.0 - tm) * (value[m0, n1] - value[m0, n0])
                + tm * (value[m1, n1] - value[m1, n0])
            )
        return complex(derivative_m), complex(derivative_n)

