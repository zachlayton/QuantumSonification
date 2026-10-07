"""Directional excitation of curved modes by a moving force."""

from __future__ import annotations

import numpy as np

from .frames import CurvedModeFrame
from .grid import Grid2D, RealArray


class TrajectoryModeCoupler:
    def __init__(self, grid: Grid2D):
        self.grid = grid

    def mode_gradients(self, modes: CurvedModeFrame) -> RealArray:
        values = modes.modes
        grad_x = (np.roll(values, -1, axis=2) - np.roll(values, 1, axis=2)) / (2.0 * self.grid.dx)
        grad_y = (np.roll(values, -1, axis=1) - np.roll(values, 1, axis=1)) / (2.0 * self.grid.dy)
        return np.stack((grad_x, grad_y), axis=1)

    def excitation(
        self, position: RealArray, force: RealArray, modes: CurvedModeFrame
    ) -> RealArray:
        sampled = np.asarray(self.grid.sample(self.mode_gradients(modes), position))
        applied_force = np.asarray(force, dtype=np.float64)
        if applied_force.shape != (2,):
            raise ValueError("force must have shape (2,)")
        return sampled @ applied_force
