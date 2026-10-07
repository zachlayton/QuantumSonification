"""Read-only basis analysis for Gross--Pitaevskii mean fields.

The GPE engine evolves one spatial order parameter.  A basis is an observer of
that same field, never an alternate evolution or acoustic oscillator bank.
This first implementation supplies the periodic Fourier basis used directly by
the split-step solver.  Geometry-aligned eigenbases continue to be supplied by
``qmw.gpe.modal_engine`` through the same complex-projection convention.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Any, Sequence

import numpy as np


Array = np.ndarray


def _spacing(values: float | Sequence[float], dimensions: int) -> tuple[float, ...]:
    result = (float(values),) * dimensions if np.isscalar(values) else tuple(float(value) for value in values)
    if len(result) != dimensions or any(not math.isfinite(value) or value <= 0.0 for value in result):
        raise ValueError("spacing must contain one finite positive value per field dimension.")
    return result


@dataclass(frozen=True)
class FourierModeFrame:
    """Complex periodic Fourier coefficients of one observed GPE mean field."""

    time: float
    coefficients: Array
    power: Array
    phase: Array
    phase_velocity: Array
    wavenumbers: tuple[Array, ...]
    field_probability: float
    modal_probability: float
    parseval_error: float
    reconstruction_error: float
    basis_kind: str = "periodic_fourier_basis"
    provenance: str = "read_only_fourier_decomposition_of_gpe_mean_field"


class FourierBasis:
    """Unitary-with-respect-to-grid-volume periodic Fourier basis.

    ``coefficients`` are normalized so that ``sum(abs(a_k)**2)`` equals the
    real-space probability integral.  This keeps Parseval's identity explicit
    and makes the complex amplitudes portable to a later modal observer.
    """

    def __init__(self, grid_shape: Sequence[int], *, spacing: float | Sequence[float] = 1.0) -> None:
        self.grid_shape = tuple(int(size) for size in grid_shape)
        if len(self.grid_shape) not in (1, 2) or any(size < 4 for size in self.grid_shape):
            raise ValueError("grid_shape must be one- or two-dimensional with every axis >= 4.")
        self.spacing = _spacing(spacing, len(self.grid_shape))
        self.cell_volume = float(np.prod(self.spacing))
        self._sample_count = int(np.prod(self.grid_shape))
        self._scale = math.sqrt(self.cell_volume / self._sample_count)
        axes = [2.0 * np.pi * np.fft.fftfreq(size, d=step) for size, step in zip(self.grid_shape, self.spacing)]
        self.wavenumbers = tuple(np.array(axis, copy=True) for axis in np.meshgrid(*axes, indexing="ij"))

    def project(self, psi: Any, *, time: float, previous: FourierModeFrame | None = None) -> FourierModeFrame:
        """Project a field and retain complex phase rather than amplitude only."""

        logical_time = float(time)
        if not math.isfinite(logical_time):
            raise ValueError("time must be finite.")
        field = np.asarray(psi, dtype=np.complex128)
        if field.shape != self.grid_shape or not np.all(np.isfinite(field)):
            raise ValueError("psi must be finite and match the Fourier basis grid.")
        coefficients = self._scale * np.fft.fftn(field)
        power = np.abs(coefficients) ** 2
        phase = np.angle(coefficients)
        phase_velocity = np.zeros(self.grid_shape, dtype=float)
        if previous is not None:
            if previous.coefficients.shape != self.grid_shape or logical_time <= previous.time:
                raise ValueError("previous Fourier frame must match the grid and have an earlier time.")
            phase_velocity = np.angle(np.exp(1j * (phase - previous.phase))) / (logical_time - previous.time)
        reconstruction = np.fft.ifftn(coefficients / self._scale)
        field_probability = self.cell_volume * float(np.sum(np.abs(field) ** 2))
        modal_probability = float(np.sum(power))
        return FourierModeFrame(
            time=logical_time,
            coefficients=np.array(coefficients, copy=True), power=np.array(power, copy=True),
            phase=np.array(phase, copy=True), phase_velocity=np.array(phase_velocity, copy=True),
            wavenumbers=tuple(np.array(axis, copy=True) for axis in self.wavenumbers),
            field_probability=field_probability, modal_probability=modal_probability,
            parseval_error=abs(field_probability - modal_probability),
            reconstruction_error=float(np.max(np.abs(reconstruction - field))),
        )

    def reconstruct(self, coefficients: Any) -> Array:
        """Reconstruct the spatial field from this basis's normalized coefficients."""

        values = np.asarray(coefficients, dtype=np.complex128)
        if values.shape != self.grid_shape or not np.all(np.isfinite(values)):
            raise ValueError("coefficients must be finite and match the Fourier basis grid.")
        return np.array(np.fft.ifftn(values / self._scale), copy=True)


def project_fourier_modes(
    psi: Any,
    *,
    spacing: float | Sequence[float] = 1.0,
    time: float = 0.0,
    previous: FourierModeFrame | None = None,
) -> FourierModeFrame:
    """Convenience projection for a finite one- or two-dimensional GPE field."""

    field = np.asarray(psi, dtype=np.complex128)
    if field.ndim not in (1, 2) or any(size < 4 for size in field.shape):
        raise ValueError("psi must be a one- or two-dimensional field with every axis >= 4.")
    return FourierBasis(field.shape, spacing=spacing).project(field, time=time, previous=previous)


__all__ = ["FourierBasis", "FourierModeFrame", "project_fourier_modes"]
