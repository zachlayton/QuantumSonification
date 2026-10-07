"""Hydrogenic fixed-manifold Pauli model for AtomicOrbitalFrame V4."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

import numpy as np


def pauli_matrices() -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return ``sigma_x, sigma_y, sigma_z`` in the up/down basis."""

    sigma_x = np.asarray([[0, 1], [1, 0]], dtype=np.complex128)
    sigma_y = np.asarray([[0, -1j], [1j, 0]], dtype=np.complex128)
    sigma_z = np.asarray([[1, 0], [0, -1]], dtype=np.complex128)
    return sigma_x, sigma_y, sigma_z


def angular_momentum_operators(
    ell: int, *, hbar: float = 1.0
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return ``Lx, Ly, Lz`` ordered by ``m_l=-ell,...,+ell``."""

    if int(ell) != ell or ell < 0:
        raise ValueError("ell must be a nonnegative integer")
    hbar = float(hbar)
    if not np.isfinite(hbar) or hbar <= 0.0:
        raise ValueError("hbar must be finite and positive")
    ell = int(ell)
    magnetic = np.arange(-ell, ell + 1, dtype=float)
    dimension = magnetic.size
    raising = np.zeros((dimension, dimension), dtype=np.complex128)
    for column, m_value in enumerate(magnetic[:-1]):
        raising[column + 1, column] = hbar * np.sqrt(
            ell * (ell + 1) - m_value * (m_value + 1)
        )
    lowering = raising.conj().T
    lx = 0.5 * (raising + lowering)
    ly = (raising - lowering) / (2j)
    lz = np.diag(hbar * magnetic).astype(np.complex128)
    return lx, ly, lz


@dataclass(frozen=True)
class AtomicManifoldSpec:
    """One hydrogenic ``(n, ell)`` manifold in atomic-energy units.

    ``spin_orbit_strength`` is an effective energy multiplying
    ``L dot S / hbar^2`` within the selected manifold. The spatial Coulomb
    energy is ``-Z^2/(2 n^2)`` Hartree.
    """

    n: int = 2
    ell: int = 1
    nuclear_charge: float = 1.0
    magnetic_field: tuple[float, float, float] = (0.0, 0.0, 0.0)
    spin_orbit_strength: float = 0.0
    hbar: float = 1.0
    bohr_magneton: float = 0.5
    electron_g_factor: float = 2.00231930436256
    bohr_radius: float = 1.0

    def __post_init__(self) -> None:
        if int(self.n) != self.n or self.n < 1:
            raise ValueError("n must be a positive integer")
        if int(self.ell) != self.ell or not 0 <= self.ell < self.n:
            raise ValueError("ell must be an integer in [0, n-1]")
        positive = (
            self.nuclear_charge,
            self.hbar,
            self.bohr_magneton,
            self.electron_g_factor,
            self.bohr_radius,
        )
        if not np.isfinite(positive).all() or min(positive) <= 0.0:
            raise ValueError("atomic scales must be finite and positive")
        field = np.asarray(self.magnetic_field, dtype=float)
        if field.shape != (3,) or not np.isfinite(field).all():
            raise ValueError("magnetic_field must contain three finite values")
        if not np.isfinite(self.spin_orbit_strength):
            raise ValueError("spin_orbit_strength must be finite")


@dataclass(frozen=True)
class AtomicManifoldModel:
    spec: AtomicManifoldSpec
    basis_labels: tuple[tuple[int, str], ...]
    hamiltonian: np.ndarray
    operators: Mapping[str, np.ndarray]

    @classmethod
    def from_spec(
        cls, spec: AtomicManifoldSpec | None = None
    ) -> "AtomicManifoldModel":
        spec = spec or AtomicManifoldSpec()
        orbital_dimension = 2 * spec.ell + 1
        identity_orbital = np.eye(orbital_dimension, dtype=np.complex128)
        identity_spin = np.eye(2, dtype=np.complex128)
        lx, ly, lz = angular_momentum_operators(spec.ell, hbar=spec.hbar)
        sigma_x, sigma_y, sigma_z = pauli_matrices()
        spin = tuple(0.5 * spec.hbar * value for value in (sigma_x, sigma_y, sigma_z))
        orbital = (lx, ly, lz)
        full_l = tuple(np.kron(value, identity_spin) for value in orbital)
        full_s = tuple(np.kron(identity_orbital, value) for value in spin)
        full_j = tuple(l_value + s_value for l_value, s_value in zip(full_l, full_s))
        l_dot_s = sum(
            (l_value @ s_value for l_value, s_value in zip(full_l, full_s)),
            np.zeros_like(full_l[0]),
        )
        dimension = 2 * orbital_dimension
        coulomb_energy = -0.5 * spec.nuclear_charge**2 / spec.n**2
        hamiltonian = coulomb_energy * np.eye(dimension, dtype=np.complex128)
        field = np.asarray(spec.magnetic_field, dtype=float)
        for axis in range(3):
            hamiltonian += spec.bohr_magneton * field[axis] * (
                full_l[axis] / spec.hbar
                + spec.electron_g_factor * full_s[axis] / spec.hbar
            )
        hamiltonian += (
            spec.spin_orbit_strength * l_dot_s / (spec.hbar * spec.hbar)
        )
        labels = tuple(
            (m_value, spin_label)
            for m_value in range(-spec.ell, spec.ell + 1)
            for spin_label in ("up", "down")
        )
        operators = {
            "Lx": full_l[0],
            "Ly": full_l[1],
            "Lz": full_l[2],
            "Sx": full_s[0],
            "Sy": full_s[1],
            "Sz": full_s[2],
            "Jx": full_j[0],
            "Jy": full_j[1],
            "Jz": full_j[2],
            "LdotS": l_dot_s,
        }
        return cls(spec, labels, hamiltonian, operators)

    @property
    def orbital_dimension(self) -> int:
        return 2 * self.spec.ell + 1

    @property
    def dimension(self) -> int:
        return 2 * self.orbital_dimension

    @property
    def coulomb_energy(self) -> float:
        return -0.5 * self.spec.nuclear_charge**2 / self.spec.n**2


__all__ = [
    "AtomicManifoldModel",
    "AtomicManifoldSpec",
    "angular_momentum_operators",
    "pauli_matrices",
]
