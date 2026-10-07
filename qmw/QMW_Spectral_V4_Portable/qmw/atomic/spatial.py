"""Hydrogenic spatial reconstruction for a fixed ``(n, ell)`` manifold."""

from __future__ import annotations

import math

import numpy as np
from scipy.special import eval_genlaguerre, sph_harm_y

from .model import AtomicManifoldModel, AtomicManifoldSpec
from .states import AtomicState


def hydrogen_radial(spec: AtomicManifoldSpec, radius: np.ndarray | float) -> np.ndarray:
    """Normalized hydrogenic radial function ``R_nl(r)``."""

    radius = np.asarray(radius, dtype=float)
    if np.any(radius < 0.0) or not np.isfinite(radius).all():
        raise ValueError("radius must be finite and nonnegative")
    n, ell = spec.n, spec.ell
    rho = 2.0 * spec.nuclear_charge * radius / (n * spec.bohr_radius)
    log_norm = 0.5 * (
        3.0 * math.log(2.0 * spec.nuclear_charge / (n * spec.bohr_radius))
        + math.lgamma(n - ell)
        - math.log(2.0 * n)
        - math.lgamma(n + ell + 1)
    )
    return (
        math.exp(log_norm)
        * np.exp(-0.5 * rho)
        * np.power(rho, ell)
        * eval_genlaguerre(n - ell - 1, 2 * ell + 1, rho)
    )


def spinor_wavefunction(
    state: AtomicState,
    model: AtomicManifoldModel,
    radius: np.ndarray | float,
    theta: np.ndarray | float,
    phi: np.ndarray | float,
) -> np.ndarray:
    """Return the two-component position-space Pauli spinor."""

    vector = state.validated(model).amplitudes.reshape(model.orbital_dimension, 2)
    radius, theta, phi = np.broadcast_arrays(radius, theta, phi)
    if np.any(theta < 0.0) or np.any(theta > math.pi):
        raise ValueError("theta must lie in [0, pi]")
    radial = hydrogen_radial(model.spec, radius)
    result = np.zeros(radius.shape + (2,), dtype=np.complex128)
    for index, m_value in enumerate(range(-model.spec.ell, model.spec.ell + 1)):
        harmonic = sph_harm_y(model.spec.ell, m_value, theta, phi)
        result += (radial * harmonic)[..., None] * vector[index]
    return result


def probability_density(spinor: np.ndarray) -> np.ndarray:
    value = np.asarray(spinor, dtype=np.complex128)
    if value.shape[-1:] != (2,):
        raise ValueError("the final spinor axis must have length two")
    return np.sum(np.abs(value) ** 2, axis=-1).real


def spin_density(spinor: np.ndarray) -> np.ndarray:
    """Return local Pauli-vector density, not a normalized spin direction."""

    value = np.asarray(spinor, dtype=np.complex128)
    if value.shape[-1:] != (2,):
        raise ValueError("the final spinor axis must have length two")
    up, down = value[..., 0], value[..., 1]
    overlap = np.conj(up) * down
    return np.stack(
        (2.0 * overlap.real, 2.0 * overlap.imag, np.abs(up) ** 2 - np.abs(down) ** 2),
        axis=-1,
    )


__all__ = ["hydrogen_radial", "probability_density", "spin_density", "spinor_wavefunction"]
