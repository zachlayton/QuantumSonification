"""Screened Poisson potential on the shared periodic grid."""

from __future__ import annotations

import numpy as np

from .config import PotentialConfig
from .grid import Grid2D, RealArray


class ScreenedPoissonSolver:
    """Solve ``(-laplacian + ell^-2) Phi = -kappa density`` by FFT."""

    def __init__(self, grid: Grid2D, config: PotentialConfig = PotentialConfig()):
        self.grid = grid
        self.config = config
        kx = 2.0 * np.pi * np.fft.fftfreq(grid.x.size, d=grid.dx)
        ky = 2.0 * np.pi * np.fft.fftfreq(grid.y.size, d=grid.dy)
        self.k_squared = ky[:, None] ** 2 + kx[None, :] ** 2

    def solve(self, density: RealArray) -> RealArray:
        source = np.asarray(density, dtype=np.float64)
        if source.shape != self.grid.shape:
            raise ValueError(f"density must have shape {self.grid.shape}")
        if not np.all(np.isfinite(source)) or np.min(source) < 0.0:
            raise ValueError("density must be finite and nonnegative")
        if self.config.remove_mean:
            source = source - source.mean()
        denominator = self.k_squared + 1.0 / self.config.screening_length**2
        potential_k = -self.config.coupling * np.fft.fft2(source) / denominator
        potential = np.fft.ifft2(potential_k).real
        if self.config.remove_mean:
            potential -= potential.mean()
        return potential

    def residual(self, density: RealArray, potential: RealArray) -> RealArray:
        """Return the spectral equation residual for numerical audits."""
        source = np.asarray(density, dtype=np.float64)
        if self.config.remove_mean:
            source = source - source.mean()
        phi_k = np.fft.fft2(np.asarray(potential, dtype=np.float64))
        lhs = np.fft.ifft2(
            (self.k_squared + 1.0 / self.config.screening_length**2) * phi_k
        ).real
        return lhs + self.config.coupling * source
