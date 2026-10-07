"""Validated projection from a density matrix into a spatial probability field."""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

from .grid import Grid2D, RealArray

ComplexArray = NDArray[np.complex128]


def validate_density_matrix(rho: ComplexArray, dimension: int, atol: float = 1e-9) -> ComplexArray:
    value = np.asarray(rho, dtype=np.complex128)
    if value.shape != (dimension, dimension):
        raise ValueError(f"rho must have shape {(dimension, dimension)}")
    if not np.all(np.isfinite(value)):
        raise ValueError("rho contains non-finite values")
    if not np.allclose(value, value.conj().T, atol=atol):
        raise ValueError("rho must be Hermitian")
    if not np.isclose(np.trace(value).real, 1.0, atol=atol) or abs(np.trace(value).imag) > atol:
        raise ValueError("rho must have unit trace")
    if np.linalg.eigvalsh(value).min() < -atol:
        raise ValueError("rho must be positive semidefinite")
    return value


def localized_gaussian_basis(
    grid: Grid2D,
    dimension: int = 16,
    width: float | None = None,
    orthonormalize: bool = True,
) -> ComplexArray:
    """Create localized sites using symmetric Loewdin orthonormalization."""
    side = int(np.ceil(np.sqrt(dimension)))
    xmin, xmax, ymin, ymax = grid.extent
    margin_x, margin_y = 0.15 * (xmax - xmin), 0.15 * (ymax - ymin)
    centers_x = np.linspace(xmin + margin_x, xmax - margin_x, side)
    centers_y = np.linspace(ymin + margin_y, ymax - margin_y, side)
    if width is None:
        width = 0.32 * min((xmax - xmin) / side, (ymax - ymin) / side)
    if width <= 0.0:
        raise ValueError("width must be positive")
    xx, yy = grid.mesh()
    basis = []
    for cy in centers_y:
        for cx in centers_x:
            gaussian = np.exp(-0.5 * ((xx - cx) ** 2 + (yy - cy) ** 2) / width**2)
            norm = np.sqrt(np.sum(gaussian**2) * grid.cell_area)
            basis.append(gaussian / norm)
            if len(basis) == dimension:
                result = np.asarray(basis, dtype=np.complex128)
                if not orthonormalize:
                    return result
                flat = result.reshape(dimension, -1)
                gram = (flat @ flat.conj().T) * grid.cell_area
                values, vectors = np.linalg.eigh(gram)
                if np.min(values) <= 1e-12:
                    raise ValueError("localized Gaussian Gram matrix is singular")
                inverse_sqrt = (vectors / np.sqrt(values)) @ vectors.conj().T
                return (inverse_sqrt @ flat).reshape(result.shape)
    raise RuntimeError("failed to construct requested basis")


class QuantumSpatialProjector:
    def __init__(self, basis: ComplexArray, grid: Grid2D):
        value = np.asarray(basis, dtype=np.complex128)
        if value.ndim != 3 or value.shape[1:] != grid.shape:
            raise ValueError(f"basis must have shape (dimension, {grid.shape[0]}, {grid.shape[1]})")
        if not np.all(np.isfinite(value)):
            raise ValueError("basis contains non-finite values")
        norms = np.sum(np.abs(value) ** 2, axis=(1, 2)) * grid.cell_area
        if np.any(norms <= 1e-15):
            raise ValueError("basis functions must have nonzero norm")
        self.basis = value.copy()
        self.grid = grid

    @property
    def dimension(self) -> int:
        return self.basis.shape[0]

    def density(self, rho: ComplexArray) -> RealArray:
        state = validate_density_matrix(rho, self.dimension)
        mu = np.einsum("ab,ayx,byx->yx", state, self.basis, self.basis.conj(), optimize=True).real
        if float(mu.min()) < -1e-9:
            raise ValueError("projected density is significantly negative")
        mu = np.maximum(mu, 0.0)
        normalization = float(mu.sum() * self.grid.cell_area)
        if normalization <= 0.0:
            raise ValueError("projected density has zero normalization")
        return mu / normalization
