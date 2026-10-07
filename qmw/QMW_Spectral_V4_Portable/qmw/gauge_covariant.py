"""Gauge-covariant periodic finite-difference primitives for the GPE layer.

The stored link phase is dimensionless:
``alpha_a(x) = (q / hbar) integral_x^(x+dx_a) A_a dl``.
For a positive-axis link, ``U_a = exp(-i alpha_a)`` and
``D_a^+ psi = (U_a psi(x + dx_a) - psi(x)) / dx_a``.  These definitions are
invariant under ``psi -> exp(i chi) psi`` and
``alpha_a -> alpha_a + chi(x + dx_a) - chi(x)``.
"""

from __future__ import annotations

import math
from typing import Any, Sequence

import numpy as np


Array = np.ndarray


def gauge_link_phases(values: Sequence[Any], shape: tuple[int, ...]) -> tuple[Array, ...]:
    if len(values) != len(shape):
        raise ValueError("gauge connection needs one positive-axis link phase field per grid axis.")
    links: list[Array] = []
    for axis, raw in enumerate(values):
        phase = np.asarray(raw, dtype=float)
        if phase.shape != shape or not np.all(np.isfinite(phase)):
            raise ValueError(f"gauge link phase for axis {axis} must be finite with shape {shape}.")
        links.append(np.array(np.angle(np.exp(1j * phase)), copy=True))
    return tuple(links)


def gauge_transform_links(links: Sequence[Any], local_phase: Any, shape: tuple[int, ...]) -> tuple[Array, ...]:
    validated = gauge_link_phases(links, shape)
    chi = np.asarray(local_phase, dtype=float)
    if chi.shape != shape or not np.all(np.isfinite(chi)):
        raise ValueError("local_phase must be finite and match the GPE grid.")
    return tuple(
        np.angle(np.exp(1j * (link + np.roll(chi, -1, axis=axis) - chi)))
        for axis, link in enumerate(validated)
    )


def covariant_forward_difference(psi: Any, links: Sequence[Any], spacing: Sequence[float]) -> tuple[Array, ...]:
    field = np.asarray(psi, dtype=np.complex128)
    shape = field.shape
    if field.ndim not in (1, 2) or not np.all(np.isfinite(field)):
        raise ValueError("psi must be a finite one- or two-dimensional field.")
    validated = gauge_link_phases(links, shape)
    if len(spacing) != field.ndim or any(not math.isfinite(float(step)) or step <= 0.0 for step in spacing):
        raise ValueError("spacing must contain one finite positive value per grid axis.")
    return tuple(
        (np.exp(-1j * link) * np.roll(field, -1, axis=axis) - field) / float(spacing[axis])
        for axis, link in enumerate(validated)
    )


def covariant_laplacian(psi: Any, links: Sequence[Any], spacing: Sequence[float]) -> Array:
    field = np.asarray(psi, dtype=np.complex128)
    derivatives = covariant_forward_difference(field, links, spacing)
    validated = gauge_link_phases(links, field.shape)
    result = np.zeros_like(field)
    for axis, (link, step, forward) in enumerate(zip(validated, spacing, derivatives)):
        backward_transport = np.exp(1j * np.roll(link, 1, axis=axis)) * np.roll(forward, 1, axis=axis)
        result += (forward - backward_transport) / float(step)
    return result


def covariant_probability_current(psi: Any, links: Sequence[Any], spacing: Sequence[float], *, hbar: float = 1.0, mass: float = 1.0) -> tuple[Array, ...]:
    if not math.isfinite(float(hbar)) or hbar <= 0.0 or not math.isfinite(float(mass)) or mass <= 0.0:
        raise ValueError("hbar and mass must be finite and positive.")
    field = np.asarray(psi, dtype=np.complex128)
    derivatives = covariant_forward_difference(field, links, spacing)
    return tuple((float(hbar) / float(mass)) * np.imag(np.conj(field) * derivative) for derivative in derivatives)


def covariant_gradient_energy_density(psi: Any, links: Sequence[Any], spacing: Sequence[float], *, hbar: float = 1.0, mass: float = 1.0) -> Array:
    if not math.isfinite(float(hbar)) or hbar <= 0.0 or not math.isfinite(float(mass)) or mass <= 0.0:
        raise ValueError("hbar and mass must be finite and positive.")
    return (float(hbar) ** 2 / (2.0 * float(mass))) * sum(
        np.abs(derivative) ** 2 for derivative in covariant_forward_difference(psi, links, spacing)
    )


def covariant_kinetic_step(psi: Any, links: Sequence[Any], spacing: Sequence[float], duration: float, *, hbar: float = 1.0, mass: float = 1.0) -> Array:
    """Apply a norm-preserving periodic kinetic step.

    For two dimensions this uses the symmetric axis product ``x/2, y, x/2``.
    Each one-axis factor is an exact matrix exponential of a Hermitian
    covariant finite-difference kinetic operator.
    """
    if not math.isfinite(float(duration)):
        raise ValueError("duration must be finite.")
    field = np.asarray(psi, dtype=np.complex128)
    if duration == 0.0:
        return np.array(field, copy=True)
    validated = gauge_link_phases(links, field.shape)
    if field.ndim == 1:
        operations = ((0, float(duration)),)
    elif field.ndim == 2:
        operations = ((0, 0.5 * float(duration)), (1, float(duration)), (0, 0.5 * float(duration)))
    else:
        raise ValueError("psi must be one- or two-dimensional.")
    result = np.array(field, copy=True)
    for axis, axis_duration in operations:
        if axis_duration != 0.0:
            result = _axis_kinetic_step(result, validated[axis], axis, float(spacing[axis]), axis_duration, hbar=float(hbar), mass=float(mass))
    return result


def _axis_kinetic_step(field: Array, link: Array, axis: int, spacing: float, duration: float, *, hbar: float, mass: float) -> Array:
    moved = np.moveaxis(field, axis, 0)
    moved_link = np.moveaxis(link, axis, 0)
    size = moved.shape[0]
    result = np.empty_like(moved)
    for index in np.ndindex(moved.shape[1:]):
        vector = moved[(slice(None),) + index]
        phase = moved_link[(slice(None),) + index]
        laplacian = np.zeros((size, size), dtype=np.complex128)
        for site in range(size):
            forward, backward = (site + 1) % size, (site - 1) % size
            laplacian[site, site] = -2.0 / (spacing * spacing)
            laplacian[site, forward] += np.exp(-1j * phase[site]) / (spacing * spacing)
            laplacian[site, backward] += np.exp(1j * phase[backward]) / (spacing * spacing)
        kinetic = -(hbar * hbar / (2.0 * mass)) * laplacian
        eigenvalues, eigenvectors = np.linalg.eigh(kinetic)
        result[(slice(None),) + index] = eigenvectors @ (
            np.exp(-1j * eigenvalues * duration / hbar) * (eigenvectors.conj().T @ vector)
        )
    return np.moveaxis(result, 0, axis)


__all__ = [
    "covariant_forward_difference", "covariant_gradient_energy_density", "covariant_kinetic_step",
    "covariant_laplacian", "covariant_probability_current", "gauge_link_phases", "gauge_transform_links",
]
