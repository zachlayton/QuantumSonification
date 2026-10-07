"""Positive conformal metric derived from the effective potential."""

from __future__ import annotations

import numpy as np

from .config import MetricConfig
from .grid import Grid2D, RealArray


def periodic_gradient(field: RealArray, grid: Grid2D) -> RealArray:
    values = np.asarray(field, dtype=np.float64)
    grad_x = (np.roll(values, -1, axis=1) - np.roll(values, 1, axis=1)) / (2.0 * grid.dx)
    grad_y = (np.roll(values, -1, axis=0) - np.roll(values, 1, axis=0)) / (2.0 * grid.dy)
    return np.stack((grad_x, grad_y))


def periodic_laplacian(field: RealArray, grid: Grid2D) -> RealArray:
    values = np.asarray(field, dtype=np.float64)
    return (
        (np.roll(values, -1, axis=1) - 2.0 * values + np.roll(values, 1, axis=1)) / grid.dx**2
        + (np.roll(values, -1, axis=0) - 2.0 * values + np.roll(values, 1, axis=0)) / grid.dy**2
    )


class QuantumMetricField:
    """Construct ``g_ij = exp(2 sigma) delta_ij`` with bounded sigma."""

    def __init__(self, grid: Grid2D, config: MetricConfig = MetricConfig()):
        self.grid = grid
        self.config = config

    def construct(self, potential: RealArray) -> dict[str, RealArray]:
        value = np.asarray(potential, dtype=np.float64)
        if value.shape != self.grid.shape or not np.all(np.isfinite(value)):
            raise ValueError("potential must be a finite grid-shaped array")
        # Preserve the absolute coupling scale: alpha and kappa remain audible
        # and visible controls rather than being erased by normalization.
        sigma = np.clip(
            self.config.spatial_strength * value,
            -self.config.sigma_limit,
            self.config.sigma_limit,
        )
        lapse_exponent = np.clip(
            self.config.lapse_strength * value,
            -self.config.lapse_exponent_limit,
            self.config.lapse_exponent_limit,
        )
        lapse = np.exp(lapse_exponent)
        sqrt_g = np.exp(2.0 * sigma)
        determinant = sqrt_g**2
        inverse_factor = 1.0 / sqrt_g
        metric = np.zeros((2, 2, *self.grid.shape), dtype=np.float64)
        inverse_metric = np.zeros_like(metric)
        metric[0, 0] = metric[1, 1] = sqrt_g
        inverse_metric[0, 0] = inverse_metric[1, 1] = inverse_factor
        grad_potential = periodic_gradient(value, self.grid)
        grad_sigma = periodic_gradient(sigma, self.grid)
        hessian = np.empty((2, 2, *self.grid.shape), dtype=np.float64)
        hessian[0, 0] = (
            np.roll(value, -1, axis=1) - 2.0 * value + np.roll(value, 1, axis=1)
        ) / self.grid.dx**2
        hessian[1, 1] = (
            np.roll(value, -1, axis=0) - 2.0 * value + np.roll(value, 1, axis=0)
        ) / self.grid.dy**2
        mixed = 0.5 * (
            periodic_gradient(grad_potential[0], self.grid)[1]
            + periodic_gradient(grad_potential[1], self.grid)[0]
        )
        hessian[0, 1] = hessian[1, 0] = mixed
        christoffel = np.zeros((2, 2, 2, *self.grid.shape), dtype=np.float64)
        for i in range(2):
            for j in range(2):
                for k in range(2):
                    christoffel[i, j, k] = (
                        (1.0 if i == j else 0.0) * grad_sigma[k]
                        + (1.0 if i == k else 0.0) * grad_sigma[j]
                        - (1.0 if j == k else 0.0) * grad_sigma[i]
                    )
        potential_laplacian = periodic_laplacian(value, self.grid)
        return {
            "sigma": sigma,
            "lapse": lapse,
            "metric": metric,
            "inverse_metric": inverse_metric,
            "determinant": determinant,
            "sqrt_g": sqrt_g,
            "inverse_metric_factor": inverse_factor,
            "grad_potential": grad_potential,
            "grad_sigma": grad_sigma,
            "potential_laplacian": potential_laplacian,
            "hessian": hessian,
            "christoffel": christoffel,
            # R = -2 exp(-2 sigma) Delta sigma for a 2-D conformal metric.
            "curvature": -2.0 * np.exp(-2.0 * sigma) * periodic_laplacian(sigma, self.grid),
        }
