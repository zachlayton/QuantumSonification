"""Assignment, sign correction, and degenerate-subspace mode alignment."""

from __future__ import annotations

import numpy as np
from scipy.optimize import linear_sum_assignment

from .frames import CurvedModeFrame
from .grid import Grid2D, RealArray


class ModeTracker:
    def __init__(self, grid: Grid2D, degeneracy_tolerance: float = 1e-3):
        self.grid = grid
        self.degeneracy_tolerance = float(degeneracy_tolerance)

    def overlap_matrix(
        self, previous: CurvedModeFrame, current: CurvedModeFrame, metric_weight: RealArray
    ) -> RealArray:
        if previous.modes.shape != current.modes.shape:
            raise ValueError("mode frame shapes must match")
        weight = np.asarray(metric_weight, dtype=np.float64)
        if weight.shape != self.grid.shape or np.min(weight) <= 0.0:
            raise ValueError("metric_weight must be positive and grid-shaped")
        old = previous.modes.reshape(previous.modes.shape[0], -1)
        new = current.modes.reshape(current.modes.shape[0], -1)
        return (old * (weight.ravel() * self.grid.cell_area)) @ new.T

    def match(
        self,
        previous: CurvedModeFrame | None,
        current: CurvedModeFrame,
        metric_weight: RealArray,
        previous_metric_weight: RealArray | None = None,
    ) -> CurvedModeFrame:
        if previous is None:
            return current
        signed_overlap = self.overlap_matrix(previous, current, metric_weight)
        old_indices, new_indices = linear_sum_assignment(-np.abs(signed_overlap))
        permutation = np.empty(current.modes.shape[0], dtype=int)
        permutation[old_indices] = new_indices
        values = current.eigenvalues[permutation].copy()
        frequencies = current.frequencies[permutation].copy()
        modes = current.modes[permutation].copy()
        damping = current.damping[permutation].copy()
        gains = current.gains[permutation].copy()
        diagonal = signed_overlap[np.arange(permutation.size), permutation]
        modes[diagonal < 0.0] *= -1.0

        # Orthogonal Procrustes alignment for contiguous old near-degenerate clusters.
        start = 0
        old_values = previous.eigenvalues
        while start < old_values.size:
            stop = start + 1
            while stop < old_values.size:
                scale = max(abs(old_values[stop - 1]), abs(old_values[stop]), 1.0)
                if abs(old_values[stop] - old_values[stop - 1]) > self.degeneracy_tolerance * scale:
                    break
                stop += 1
            if stop - start > 1:
                old_group = previous.modes[start:stop].reshape(stop - start, -1)
                new_group = modes[start:stop].reshape(stop - start, -1)
                weighted_overlap = (old_group * (np.asarray(metric_weight).ravel() * self.grid.cell_area)) @ new_group.T
                u, _, vt = np.linalg.svd(weighted_overlap)
                rotation = vt.T @ u.T
                modes[start:stop] = (rotation.T @ new_group).reshape(stop - start, *self.grid.shape)
            start = stop

        dt = current.time - previous.time
        if dt > 0.0:
            new = modes.reshape(modes.shape[0], -1)
            derivative = (modes - previous.modes).reshape(modes.shape[0], -1) / dt
            current_weight = np.asarray(metric_weight, dtype=np.float64)
            old_weight = (
                current_weight
                if previous_metric_weight is None
                else np.asarray(previous_metric_weight, dtype=np.float64)
            )
            if old_weight.shape != self.grid.shape or np.min(old_weight) <= 0.0:
                raise ValueError("previous_metric_weight must be positive and grid-shaped")
            basis_overlap = (
                new * (current_weight.ravel() * self.grid.cell_area)
            ) @ derivative.T
            weight_rate = (current_weight - old_weight).ravel() / dt
            metric_rate_overlap = (
                new * (weight_rate * self.grid.cell_area)
            ) @ new.T
            metric_rate_overlap = 0.5 * (
                metric_rate_overlap + metric_rate_overlap.T
            )
            # The rotation/gauge part of the moving basis is the skew part.
            # Keep the raw overlap and metric-rate term alongside it.
            connection = 0.5 * (basis_overlap - basis_overlap.T)
        else:
            basis_overlap = np.zeros((modes.shape[0], modes.shape[0]))
            metric_rate_overlap = np.zeros_like(basis_overlap)
            connection = np.zeros_like(basis_overlap)
        return CurvedModeFrame(
            time=current.time,
            eigenvalues=values,
            frequencies=frequencies,
            modes=modes,
            damping=damping,
            gains=gains,
            basis_derivative_overlap=basis_overlap,
            metric_rate_overlap=metric_rate_overlap,
            intermodal_connection=connection,
        )
