"""Generalized conformal Laplace eigenproblem on the shared grid."""

from __future__ import annotations

import numpy as np
from scipy.sparse import csr_matrix, diags, eye, kron
from scipy.sparse.linalg import eigsh

from .frames import CurvedModeFrame
from .grid import Grid2D, RealArray
from typing import Any, cast


def _periodic_negative_laplacian_1d(count: int, spacing: float) -> csr_matrix:
    matrix = diags(
        (
            -np.ones(count - 1),
            2.0 * np.ones(count),
            -np.ones(count - 1),
        ),
        offsets=(-1, 0, 1),  # type: ignore[arg-type]
        shape=(count, count),
    ).tolil()
    matrix[0, count - 1] = -1.0
    matrix[count - 1, 0] = -1.0
    return (matrix.tocsr() / spacing**2)


def periodic_stiffness_matrix(grid: Grid2D) -> csr_matrix:
    lx = _periodic_negative_laplacian_1d(grid.x.size, grid.dx)
    ly = _periodic_negative_laplacian_1d(grid.y.size, grid.dy)
    laplacian = kron(eye(grid.y.size), lx) + kron(ly, eye(grid.x.size))
    # Make the scalar scaling explicit on the sparse matrix side so the
    # type checker sees a sparse matrix result before calling tocsr().
    result = (laplacian * grid.cell_area).tocsr()
    return csr_matrix(result)  # force the checked return type


class CurvedModeSolver:
    """Solve ``K phi = lambda M_g phi`` and return M-normalized modes."""

    def __init__(
        self,
        grid: Grid2D,
        stiffness_matrix: csr_matrix | None = None,
        frequency_floor_hz: float = 30.0,
        frequency_scale_hz: float = 80.0,
        damping_ratio: float = 0.015,
    ):
        self.grid = grid
        self.K = periodic_stiffness_matrix(grid) if stiffness_matrix is None else stiffness_matrix.tocsr()
        self.frequency_floor_hz = float(frequency_floor_hz)
        self.frequency_scale_hz = float(frequency_scale_hz)
        self.damping_ratio = float(damping_ratio)
        point_count = grid.x.size * grid.y.size
        if self.K.shape != (point_count, point_count):
            raise ValueError("stiffness matrix size does not match grid")

    def solve(self, sqrt_g: RealArray, mode_count: int, time: float = 0.0) -> CurvedModeFrame:
        weight = np.asarray(sqrt_g, dtype=np.float64)
        if weight.shape != self.grid.shape or not np.all(np.isfinite(weight)) or np.min(weight) <= 0.0:
            raise ValueError("sqrt_g must be finite, positive, and grid-shaped")
        if mode_count <= 0 or mode_count >= weight.size - 1:
            raise ValueError("invalid mode_count")
        mass = diags(weight.ravel() * self.grid.cell_area, format="csr")
        # Ask for one extra eigenpair and remove the constant periodic zero mode.
        # A deterministic nonconstant start vector makes controlled scene
        # comparisons reproducible while still allowing ARPACK to resolve the
        # periodic zero mode and low eigenspaces.
        start = np.linspace(1.0, 2.0, weight.size, dtype=np.float64)
        start /= np.linalg.norm(start)
        values, vectors = eigsh(
            self.K, k=mode_count + 1, M=mass, which="SM", v0=start
        )
        order = np.argsort(values)
        values, vectors = values[order], vectors[:, order]
        keep = values > max(1e-10, 1e-9 * float(np.max(values)))
        values, vectors = values[keep], vectors[:, keep]
        if values.size < mode_count:
            raise RuntimeError("eigensolver did not return enough nonzero modes")
        values, vectors = values[:mode_count], vectors[:, :mode_count]
        values = np.maximum(values, 0.0)
        frequencies = self.frequency_floor_hz + self.frequency_scale_hz * np.sqrt(values)
        modes = vectors.T.reshape(mode_count, *self.grid.shape)
        return CurvedModeFrame(
            time=float(time),
            eigenvalues=values,
            frequencies=frequencies,
            modes=modes,
            damping=np.full(mode_count, self.damping_ratio),
            gains=np.ones(mode_count),
            basis_derivative_overlap=np.zeros((mode_count, mode_count)),
            metric_rate_overlap=np.zeros((mode_count, mode_count)),
            intermodal_connection=np.zeros((mode_count, mode_count)),
        )
