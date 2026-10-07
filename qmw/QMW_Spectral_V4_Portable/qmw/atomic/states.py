"""State preparation for the hydrogenic Pauli manifold."""

from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np

from .model import AtomicManifoldModel


@dataclass(frozen=True)
class AtomicState:
    amplitudes: np.ndarray

    def validated(self, model: AtomicManifoldModel) -> "AtomicState":
        value = np.asarray(self.amplitudes, dtype=np.complex128)
        if value.shape != (model.dimension,) or not np.isfinite(value).all():
            raise ValueError("atomic amplitudes must be one finite state vector")
        norm = float(np.linalg.norm(value))
        if not np.isclose(norm, 1.0, atol=1e-12):
            raise ValueError("atomic state must be normalized")
        result = value.copy()
        result.setflags(write=False)
        return AtomicState(result)

    @property
    def density_matrix(self) -> np.ndarray:
        value = np.asarray(self.amplitudes, dtype=np.complex128)
        return np.outer(value, value.conj())


def pauli_spinor(theta: float = 0.0, phi: float = 0.0) -> np.ndarray:
    """Return a normalized spinor with the requested Bloch-sphere direction."""

    theta, phi = float(theta), float(phi)
    if not np.isfinite([theta, phi]).all() or not 0.0 <= theta <= math.pi:
        raise ValueError("spin angles require theta in [0, pi] and finite phi")
    return np.asarray(
        [math.cos(0.5 * theta), np.exp(1j * phi) * math.sin(0.5 * theta)],
        dtype=np.complex128,
    )


def basis_state(
    model: AtomicManifoldModel, *, m_l: int = 0, spin: str = "up"
) -> AtomicState:
    if int(m_l) != m_l or not -model.spec.ell <= m_l <= model.spec.ell:
        raise ValueError("m_l lies outside the selected ell manifold")
    spin = str(spin).lower()
    if spin not in {"up", "down"}:
        raise ValueError("spin must be 'up' or 'down'")
    index = 2 * (int(m_l) + model.spec.ell) + (spin == "down")
    amplitudes = np.zeros(model.dimension, dtype=np.complex128)
    amplitudes[index] = 1.0
    return AtomicState(amplitudes).validated(model)


def product_state(
    model: AtomicManifoldModel,
    orbital_amplitudes: np.ndarray,
    spinor: np.ndarray,
) -> AtomicState:
    orbital = np.asarray(orbital_amplitudes, dtype=np.complex128)
    spin = np.asarray(spinor, dtype=np.complex128)
    if orbital.shape != (model.orbital_dimension,) or not np.isfinite(orbital).all():
        raise ValueError("one finite amplitude per m_l value is required")
    if spin.shape != (2,) or not np.isfinite(spin).all():
        raise ValueError("spinor must contain two finite amplitudes")
    orbital_norm = float(np.linalg.norm(orbital))
    spin_norm = float(np.linalg.norm(spin))
    if orbital_norm <= 0.0 or spin_norm <= 0.0:
        raise ValueError("orbital and spin amplitudes must be nonzero")
    amplitudes = np.kron(orbital / orbital_norm, spin / spin_norm)
    return AtomicState(amplitudes).validated(model)


__all__ = ["AtomicState", "basis_state", "pauli_spinor", "product_state"]
