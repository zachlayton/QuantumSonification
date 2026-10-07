"""Verified geometry-mode observations for two-dimensional GPE fields.

This module is a read-only modal layer.  It supplies a geometry-aligned
eigenbasis, projects an already evolved GPE mean field into it, and preserves
complex amplitude, power, phase, and phase velocity.  It does not alter the
GPE evolution, determine an acoustic tuning, or create sound events.

``separable_periodic_eigenbasis`` is deliberately narrow: it diagonalizes the
same periodic spectral *linear* Hamiltonian used by the dimensionless GPE for
potentials of the form ``V(x, y) = Vx(x) + Vy(y)``.  The double-well terrain
used by Phase Collision I is in that class.  General two-dimensional geometry
still requires a supplied, independently verified eigensolver/eigenbasis.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Any

import numpy as np

from .geometry_engine import GeometryEigenbasis2D, GeometryPotential2D


Array = np.ndarray


def _uniform_axis(name: str, values: Any) -> tuple[Array, float]:
    axis = np.asarray(values, dtype=float)
    if axis.ndim != 1 or axis.size < 4 or not np.all(np.isfinite(axis)):
        raise ValueError(f"{name} must be a finite one-dimensional periodic-grid axis with at least four points.")
    differences = np.diff(axis)
    if np.any(differences <= 0.0) or not np.allclose(differences, differences[0], rtol=1.0e-9, atol=1.0e-12):
        raise ValueError(f"{name} must be strictly increasing with uniform spacing.")
    return np.array(axis, copy=True), float(differences[0])


def _finite_positive(name: str, value: float) -> float:
    value = float(value)
    if not math.isfinite(value) or value <= 0.0:
        raise ValueError(f"{name} must be finite and greater than zero.")
    return value


@dataclass(frozen=True)
class GeometryModeFrame:
    """Complex coefficients of one field observed in a geometry eigenbasis."""

    time: float
    coefficients: Array
    power: Array
    phase: Array
    phase_velocity: Array
    eigenvalues: Array | None
    field_probability: float
    modal_probability: float
    unprojected_probability: float
    reconstruction_error: float
    basis_kind: str = "verified_geometry_eigenbasis"
    provenance: str = "read_only_geometry_mode_decomposition_of_gpe_mean_field"


class GeometryModeBasis2D:
    """Orthonormal geometry modes with volume-correct complex projections."""

    def __init__(self, eigenbasis: GeometryEigenbasis2D, *, orthonormal_tolerance: float = 1.0e-8) -> None:
        tolerance = _finite_positive("orthonormal_tolerance", orthonormal_tolerance)
        self.x, self.dx = _uniform_axis("eigenbasis.x", eigenbasis.x)
        self.y, self.dy = _uniform_axis("eigenbasis.y", eigenbasis.y)
        modes = np.asarray(eigenbasis.modes, dtype=np.complex128)
        if modes.ndim != 3 or modes.shape[0] < 1 or modes.shape[1:] != (self.x.size, self.y.size) or not np.all(np.isfinite(modes)):
            raise ValueError("geometry eigenbasis modes must be finite with shape (mode_count, len(x), len(y)).")
        self.modes = np.array(modes, copy=True)
        self.eigenvalues = None if eigenbasis.eigenvalues is None else np.array(eigenbasis.eigenvalues, dtype=float, copy=True)
        if self.eigenvalues is not None and self.eigenvalues.shape != (self.modes.shape[0],):
            raise ValueError("geometry eigenbasis eigenvalues must have one value per mode.")
        self.cell_area = self.dx * self.dy
        gram = self.cell_area * np.einsum("aij,bij->ab", np.conj(self.modes), self.modes)
        if not np.allclose(gram, np.eye(self.modes.shape[0]), rtol=tolerance, atol=tolerance):
            raise ValueError("geometry eigenmodes must be orthonormal on their declared periodic grid.")

    @property
    def shape(self) -> tuple[int, int]:
        return (self.x.size, self.y.size)

    def project(self, psi: Any, *, time: float, previous: GeometryModeFrame | None = None) -> GeometryModeFrame:
        """Project ``psi`` as ``a_n = integral conj(phi_n) psi``."""

        logical_time = float(time)
        if not math.isfinite(logical_time):
            raise ValueError("time must be finite.")
        field = np.asarray(psi, dtype=np.complex128)
        if field.shape != self.shape or not np.all(np.isfinite(field)):
            raise ValueError("psi must be finite and match the geometry eigenbasis grid.")
        coefficients = self.cell_area * np.einsum("aij,ij->a", np.conj(self.modes), field)
        power = np.abs(coefficients) ** 2
        phase = np.angle(coefficients)
        phase_velocity = np.zeros_like(phase, dtype=float)
        if previous is not None:
            if previous.coefficients.shape != coefficients.shape or logical_time <= previous.time:
                raise ValueError("previous geometry-mode frame must match this basis and have an earlier time.")
            phase_velocity = np.angle(np.exp(1j * (phase - previous.phase))) / (logical_time - previous.time)
        reconstruction = self.reconstruct(coefficients)
        field_probability = self.cell_area * float(np.sum(np.abs(field) ** 2))
        modal_probability = float(np.sum(power))
        return GeometryModeFrame(
            time=logical_time, coefficients=np.array(coefficients, copy=True), power=np.array(power, copy=True),
            phase=np.array(phase, copy=True), phase_velocity=np.array(phase_velocity, copy=True),
            eigenvalues=None if self.eigenvalues is None else np.array(self.eigenvalues, copy=True),
            field_probability=field_probability, modal_probability=modal_probability,
            unprojected_probability=field_probability - modal_probability,
            reconstruction_error=float(np.max(np.abs(reconstruction - field))),
        )

    def reconstruct(self, coefficients: Any) -> Array:
        """Reconstruct the projection of a field into the available mode span."""

        values = np.asarray(coefficients, dtype=np.complex128)
        if values.shape != (self.modes.shape[0],) or not np.all(np.isfinite(values)):
            raise ValueError("coefficients must be finite with one value per geometry mode.")
        return np.einsum("a,aij->ij", values, self.modes)


def _periodic_linear_hamiltonian(axis: Array, potential: Array, *, hbar: float, mass: float) -> Array:
    """Dense one-dimensional representation of the periodic spectral Hamiltonian."""

    spacing = float(axis[1] - axis[0])
    count = axis.size
    wavenumbers = 2.0 * np.pi * np.fft.fftfreq(count, d=spacing)
    kinetic_symbol = 0.5 * hbar**2 * wavenumbers**2 / mass
    identity = np.eye(count, dtype=np.complex128)
    kinetic = np.fft.ifft(kinetic_symbol[:, None] * np.fft.fft(identity, axis=0), axis=0)
    return np.real_if_close(kinetic, tol=1000).real + np.diag(potential)


def separable_periodic_eigenbasis(
    potential: GeometryPotential2D,
    *,
    mode_count: int = 16,
    hbar: float = 1.0,
    mass: float = 1.0,
    separability_tolerance: float = 1.0e-10,
) -> GeometryEigenbasis2D:
    """Solve the periodic linear eigenbasis for a separable geometry potential.

    The result is a true discrete eigenbasis of ``-hbar^2/2m laplacian + V``
    on the provided periodic grid.  Its modes are normalized with the grid
    area integral, so modal Parseval and reconstruction tests have their
    physical measure rather than raw array normalization.
    """

    if int(mode_count) != mode_count or mode_count < 1:
        raise ValueError("mode_count must be a positive integer.")
    hbar = _finite_positive("hbar", hbar)
    mass = _finite_positive("mass", mass)
    tolerance = _finite_positive("separability_tolerance", separability_tolerance)
    x, dx = _uniform_axis("potential.x", potential.x)
    y, dy = _uniform_axis("potential.y", potential.y)
    values = np.asarray(potential.potential, dtype=float)
    if values.shape != (x.size, y.size) or not np.all(np.isfinite(values)):
        raise ValueError("potential values must be finite and match its coordinate axes.")
    vx = values[:, 0]
    vy = values[0, :] - values[0, 0]
    residual = values - vx[:, None] - vy[None, :]
    if not np.allclose(residual, 0.0, rtol=tolerance, atol=tolerance):
        raise ValueError("a separable periodic eigenbasis requires V(x, y) = Vx(x) + Vy(y).")
    ex, ux = np.linalg.eigh(_periodic_linear_hamiltonian(x, vx, hbar=hbar, mass=mass))
    ey, uy = np.linalg.eigh(_periodic_linear_hamiltonian(y, vy, hbar=hbar, mass=mass))
    pairs = sorted(((float(ex[i] + ey[j]), i, j) for i in range(x.size) for j in range(y.size)), key=lambda item: item[0])
    active = min(int(mode_count), len(pairs))
    modes = np.empty((active, x.size, y.size), dtype=np.complex128)
    eigenvalues = np.empty(active, dtype=float)
    for index, (eigenvalue, ix, iy) in enumerate(pairs[:active]):
        modes[index] = np.outer(ux[:, ix] / math.sqrt(dx), uy[:, iy] / math.sqrt(dy))
        eigenvalues[index] = eigenvalue
    return GeometryEigenbasis2D(x=x, y=y, modes=modes, eigenvalues=eigenvalues, provenance="verified_separable_periodic_geometry_eigenbasis")


__all__ = ["GeometryModeBasis2D", "GeometryModeFrame", "separable_periodic_eigenbasis"]
