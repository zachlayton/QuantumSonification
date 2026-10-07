"""Explicit discrete geometry-quench amplitude transfer."""

from __future__ import annotations

import numpy as np

from .frames import CurvedModeFrame
from .grid import Grid2D, RealArray


class GeometryQuenchEngine:
    def __init__(self, grid: Grid2D):
        self.grid = grid

    def overlap(
        self,
        old_modes: CurvedModeFrame,
        new_modes: CurvedModeFrame,
        metric_weight: RealArray,
    ) -> RealArray:
        weight = np.asarray(metric_weight, dtype=np.float64)
        if weight.shape != self.grid.shape or np.min(weight) <= 0.0:
            raise ValueError("metric_weight must be positive and grid-shaped")
        old = old_modes.modes.reshape(old_modes.modes.shape[0], -1)
        new = new_modes.modes.reshape(new_modes.modes.shape[0], -1)
        return (new * (weight.ravel() * self.grid.cell_area)) @ old.T

    def transfer_energy(
        self,
        old_amplitudes: RealArray,
        old_modes: CurvedModeFrame,
        new_modes: CurvedModeFrame,
        metric_weight: RealArray,
    ) -> RealArray:
        amplitudes = np.asarray(old_amplitudes, dtype=np.float64)
        if amplitudes.shape != (old_modes.modes.shape[0],):
            raise ValueError("old_amplitudes do not match old mode count")
        return self.overlap(old_modes, new_modes, metric_weight) @ amplitudes
