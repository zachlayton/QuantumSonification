"""Mixed-state probability current and its effective circulation field."""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

from .grid import Grid2D, RealArray
from .metric_field import periodic_gradient
from .quantum_projector import validate_density_matrix

ComplexArray = NDArray[np.complex128]


class ProbabilityCurrentProjector:
    def __init__(self, basis: ComplexArray, grid: Grid2D, hbar_over_mass: float = 1.0):
        value = np.asarray(basis, dtype=np.complex128)
        if value.ndim != 3 or value.shape[1:] != grid.shape:
            raise ValueError("basis shape does not match grid")
        if hbar_over_mass <= 0.0:
            raise ValueError("hbar_over_mass must be positive")
        self.basis = value.copy()
        self.grid = grid
        self.hbar_over_mass = float(hbar_over_mass)
        grad_x = (np.roll(value, -1, axis=2) - np.roll(value, 1, axis=2)) / (2.0 * grid.dx)
        grad_y = (np.roll(value, -1, axis=1) - np.roll(value, 1, axis=1)) / (2.0 * grid.dy)
        self.basis_gradient = np.stack((grad_x, grad_y), axis=0)

    def current(
        self, rho: ComplexArray, density: RealArray, density_floor: float = 1e-9
    ) -> tuple[RealArray, RealArray, RealArray]:
        state = validate_density_matrix(rho, self.basis.shape[0])
        mu = np.asarray(density, dtype=np.float64)
        if mu.shape != self.grid.shape or np.min(mu) < 0.0:
            raise ValueError("density must be a nonnegative grid field")
        current = self.hbar_over_mass * np.imag(
            np.einsum(
                "ab,iayx,byx->iyx",
                state,
                self.basis_gradient,
                self.basis.conj(),
                optimize=True,
            )
        )
        # Suppress ill-conditioned velocities where there is effectively no mass.
        floor = max(float(density_floor), 1e-12 * float(mu.max()))
        velocity = current / np.maximum(mu[None, :, :], floor)
        velocity[:, mu < floor] = 0.0
        grad_ux = periodic_gradient(velocity[0], self.grid)
        grad_uy = periodic_gradient(velocity[1], self.grid)
        vorticity = grad_uy[0] - grad_ux[1]
        return current, velocity, vorticity
