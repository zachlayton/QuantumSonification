"""Explicit density-matrix control mappings for a two-dimensional GPE field.

This module is deliberately an adapter, not an identity between an arbitrary
density matrix and a Gross--Pitaevskii order parameter.  It maps populations
to initial packet coefficients, coherence phase to packet-relative phase, and
normalized coherence magnitude to finite corridor-barrier control in an
external potential.  It never mutates or evolves ``rho``.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Any, Sequence

import numpy as np


Array = np.ndarray
EPS = 1.0e-12


def _axis(name: str, values: Any) -> tuple[Array, float]:
    axis = np.asarray(values, dtype=float)
    if axis.ndim != 1 or axis.size < 4 or not np.all(np.isfinite(axis)) or np.any(np.diff(axis) <= 0.0):
        raise ValueError(f"{name} must be a finite, strictly increasing coordinate array with length >= 4.")
    spacing = float(axis[1] - axis[0])
    if not np.allclose(np.diff(axis), spacing, rtol=1.0e-9, atol=1.0e-12):
        raise ValueError("density-to-GPE control requires uniform periodic coordinate axes.")
    return np.array(axis, copy=True), spacing


def _rho(values: Any, tolerance: float = 1.0e-9) -> Array:
    matrix = np.asarray(values, dtype=np.complex128)
    if matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1] or matrix.shape[0] < 1 or not np.all(np.isfinite(matrix)):
        raise ValueError("rho must be a finite, nonempty square density matrix.")
    if not np.allclose(matrix, matrix.conj().T, atol=tolerance, rtol=tolerance):
        raise ValueError("rho must be Hermitian within tolerance.")
    trace = complex(np.trace(matrix))
    if abs(trace.imag) > tolerance or abs(trace.real - 1.0) > tolerance:
        raise ValueError("rho must have unit trace within tolerance.")
    if float(np.min(np.linalg.eigvalsh(matrix))) < -tolerance:
        raise ValueError("rho must be positive semidefinite within tolerance.")
    return np.array(matrix, copy=True)


@dataclass(frozen=True)
class DensityMatrixGPEControl2D:
    """Declared initial-field and corridor-potential controls derived from ``rho``."""

    initial_psi: Array
    packet_modes: Array
    populations: Array
    relative_phases: Array
    coherence_magnitude: Array
    normalized_coherence: Array
    corridor_potential: Array
    purity: float
    provenance: str = "experimental_density_matrix_to_gpe_control_mapping"

    def combined_potential(self, geometry_potential: Any = 0.0) -> Array:
        """Add this experimental corridor control to a supplied geometry potential."""

        geometry = np.asarray(geometry_potential, dtype=float)
        if geometry.ndim == 0:
            geometry = np.full(self.corridor_potential.shape, float(geometry), dtype=float)
        if geometry.shape != self.corridor_potential.shape or not np.all(np.isfinite(geometry)):
            raise ValueError("geometry_potential must be finite and match the control grid.")
        return np.array(geometry + self.corridor_potential, copy=True)


def density_matrix_to_gpe_control_2d(
    rho: Any,
    x: Any,
    y: Any,
    *,
    packet_centers: Sequence[Sequence[float]] | Array | None = None,
    packet_width: float | None = None,
    pair_barrier_masks: Any | None = None,
    base_barrier: float = 0.0,
    coherence_barrier_scale: float = 0.0,
) -> DensityMatrixGPEControl2D:
    """Build an explicit density-matrix control packet and finite barriers.

    With the standard convention ``rho[i,j] = c_i conj(c_j)``, packet ``i``
    has relative phase ``arg(rho[i,0])``.  A pair's normalized coherence is
    ``abs(rho[i,j]) / sqrt(rho[i,i] rho[j,j])`` where defined.  On a supplied
    pair corridor mask, high coherence lowers its barrier and hence increases
    the *experimental* spatial coupling through that corridor.
    """

    matrix = _rho(rho)
    x_axis, dx = _axis("x", x)
    y_axis, dy = _axis("y", y)
    if not math.isfinite(float(base_barrier)) or not math.isfinite(float(coherence_barrier_scale)):
        raise ValueError("barrier parameters must be finite.")
    count = matrix.shape[0]
    X, Y = np.meshgrid(x_axis, y_axis, indexing="ij")
    if packet_centers is None:
        center_x, center_y = float(np.mean(x_axis)), float(np.mean(y_axis))
        radius = 0.25 * min(float(x_axis[-1] - x_axis[0]), float(y_axis[-1] - y_axis[0]))
        angles = 2.0 * np.pi * np.arange(count) / count
        centers = np.column_stack((center_x + radius * np.cos(angles), center_y + radius * np.sin(angles)))
    else:
        centers = np.asarray(packet_centers, dtype=float)
        if centers.shape != (count, 2) or not np.all(np.isfinite(centers)):
            raise ValueError("packet_centers must have shape (density_matrix_dimension, 2).")
    default_width = min(float(x_axis[-1] - x_axis[0]), float(y_axis[-1] - y_axis[0])) / max(4.0 * count, 4.0)
    width = default_width if packet_width is None else float(packet_width)
    if not math.isfinite(width) or width <= 0.0:
        raise ValueError("packet_width must be finite and greater than zero.")
    modes = np.exp(-0.5 * (((X[None, ...] - centers[:, 0, None, None]) / width) ** 2 + ((Y[None, ...] - centers[:, 1, None, None]) / width) ** 2)).astype(np.complex128)
    area = dx * dy
    for index in range(count):
        modes[index] /= math.sqrt(float(np.sum(np.abs(modes[index]) ** 2) * area))
    populations = np.maximum(np.real(np.diag(matrix)), 0.0)
    phases = np.zeros(count, dtype=float)
    if count > 1:
        phases[1:] = np.angle(matrix[1:, 0])
    psi = np.sum(np.sqrt(populations)[:, None, None] * np.exp(1j * phases)[:, None, None] * modes, axis=0)
    norm = float(np.sum(np.abs(psi) ** 2) * area)
    if norm <= EPS:
        raise ValueError("density-matrix control produced a zero GPE initial field.")
    psi /= math.sqrt(norm)
    magnitude = np.abs(matrix)
    denominator = np.sqrt(populations[:, None] * populations[None, :])
    normalized = np.divide(magnitude, denominator, out=np.zeros_like(magnitude), where=denominator > EPS)
    normalized = np.clip(normalized, 0.0, 1.0)
    np.fill_diagonal(normalized, 1.0)
    corridor = np.zeros(X.shape, dtype=float)
    if pair_barrier_masks is not None:
        masks = np.asarray(pair_barrier_masks, dtype=float)
        expected = (count, count, *X.shape)
        if masks.shape != expected or not np.all(np.isfinite(masks)) or np.any(masks < 0.0) or np.any(masks > 1.0):
            raise ValueError("pair_barrier_masks must be finite in [0, 1] with shape (n, n, len(x), len(y)).")
        if not np.allclose(masks, np.swapaxes(masks, 0, 1), atol=1.0e-12):
            raise ValueError("pair_barrier_masks must be symmetric in its two basis indices.")
        for first in range(count):
            for second in range(first + 1, count):
                barrier = float(base_barrier) + float(coherence_barrier_scale) * (1.0 - normalized[first, second])
                corridor += barrier * masks[first, second]
    return DensityMatrixGPEControl2D(
        initial_psi=np.array(psi, copy=True), packet_modes=np.array(modes, copy=True),
        populations=np.array(populations, copy=True), relative_phases=phases,
        coherence_magnitude=np.array(magnitude, copy=True), normalized_coherence=normalized,
        corridor_potential=corridor, purity=float(np.real(np.trace(matrix @ matrix))),
    )


__all__ = ["DensityMatrixGPEControl2D", "density_matrix_to_gpe_control_2d"]
