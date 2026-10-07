"""Canonical oscillator states in the truncated Fock basis."""

from __future__ import annotations

import math

import numpy as np
from scipy.linalg import expm

from .model import OscillatorModel, OscillatorSpec


def density_matrix(state: np.ndarray, *, atol: float = 1e-10) -> np.ndarray:
    """Return a validated density matrix from a ket or density operator."""

    value = np.asarray(state, dtype=np.complex128)
    if value.ndim == 1:
        norm = float(np.linalg.norm(value))
        if not np.isfinite(norm) or norm <= atol:
            raise ValueError("statevector must have nonzero finite norm")
        ket = value / norm
        return np.outer(ket, ket.conj())
    if value.ndim != 2 or value.shape[0] != value.shape[1]:
        raise ValueError("state must be a square density matrix or a statevector")
    if not np.all(np.isfinite(value)):
        raise ValueError("density matrix contains non-finite values")
    hermitian = 0.5 * (value + value.conj().T)
    if not np.allclose(value, hermitian, atol=atol, rtol=0.0):
        raise ValueError("density matrix must be Hermitian")
    trace = np.trace(hermitian)
    if abs(trace.imag) > atol or trace.real <= atol:
        raise ValueError("density matrix must have positive real trace")
    normalized = hermitian / trace.real
    if float(np.min(np.linalg.eigvalsh(normalized))) < -atol:
        raise ValueError("density matrix must be positive semidefinite")
    return normalized


def vacuum_state(dimension: int = 16) -> np.ndarray:
    return fock_state(0, dimension)


def fock_state(level: int, dimension: int = 16) -> np.ndarray:
    if dimension < 2:
        raise ValueError("dimension must be at least 2")
    if not 0 <= level < dimension:
        raise ValueError("level must lie inside the truncated basis")
    ket = np.zeros(dimension, dtype=np.complex128)
    ket[level] = 1.0
    return ket


def coherent_state(alpha: complex, dimension: int = 16) -> np.ndarray:
    """Normalized projection of an infinite coherent state into the cutoff."""

    if dimension < 2:
        raise ValueError("dimension must be at least 2")
    coefficients = np.empty(dimension, dtype=np.complex128)
    coefficients[0] = 1.0
    for level in range(1, dimension):
        coefficients[level] = coefficients[level - 1] * alpha / math.sqrt(level)
    norm = np.linalg.norm(coefficients)
    if not np.isfinite(norm) or norm == 0.0:
        raise ValueError("alpha produces a numerically invalid truncated state")
    return coefficients / norm


def thermal_state(mean_n: float, dimension: int = 16) -> np.ndarray:
    """Normalized finite-cutoff Gibbs state parameterized by infinite-basis mean n."""

    if dimension < 2:
        raise ValueError("dimension must be at least 2")
    if not np.isfinite(mean_n) or mean_n < 0.0:
        raise ValueError("mean_n must be finite and nonnegative")
    if mean_n == 0.0:
        return density_matrix(vacuum_state(dimension))
    ratio = mean_n / (mean_n + 1.0)
    weights = ratio ** np.arange(dimension, dtype=float)
    weights /= np.sum(weights)
    return np.diag(weights.astype(np.complex128))


def squeezed_vacuum(
    zeta: complex,
    dimension: int = 16,
) -> np.ndarray:
    """Finite-dimensional unitary squeeze operator applied to vacuum.

    The convention is S(zeta)=exp((zeta* a^2-zeta a†^2)/2).
    """

    model = OscillatorModel.from_spec(OscillatorSpec(dimension=dimension))
    a = model.operators.annihilation
    adag = model.operators.creation
    generator = 0.5 * (np.conj(zeta) * (a @ a) - zeta * (adag @ adag))
    return expm(generator) @ vacuum_state(dimension)


__all__ = [
    "coherent_state",
    "density_matrix",
    "fock_state",
    "squeezed_vacuum",
    "thermal_state",
    "vacuum_state",
]
