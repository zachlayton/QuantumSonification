"""Plane-wave solution of V(x)=V0 sin^2(pi x/a), in recoil units."""

from __future__ import annotations

from dataclasses import dataclass
import numpy as np


@dataclass(frozen=True)
class BlochState:
    q: float
    band: int
    energy: float
    coefficients: np.ndarray


class BlochLattice1D:
    def __init__(self, depth_recoil: float = 4.0, basis_order: int = 5) -> None:
        if depth_recoil < 0 or basis_order < 1:
            raise ValueError("depth must be non-negative and basis order positive")
        self.depth_recoil = float(depth_recoil)
        self.basis_order = int(basis_order)
        self.orders = np.arange(-basis_order, basis_order + 1, dtype=float)

    def hamiltonian(self, q: float) -> np.ndarray:
        matrix = np.diag(4.0 * (self.orders + float(q)) ** 2 + self.depth_recoil / 2.0)
        coupling = -self.depth_recoil / 4.0
        indices = np.arange(self.orders.size - 1)
        matrix[indices, indices + 1] = coupling
        matrix[indices + 1, indices] = coupling
        return matrix

    def eigensystem(self, q: float) -> tuple[np.ndarray, np.ndarray]:
        energies, vectors = np.linalg.eigh(self.hamiltonian(q))
        return energies, vectors.T.astype(np.complex128)

    def state(self, q: float, band: int = 0) -> BlochState:
        energies, vectors = self.eigensystem(q)
        if not 0 <= band < energies.size:
            raise ValueError("band outside truncated basis")
        vector = vectors[band].copy()
        pivot = int(np.argmax(np.abs(vector)))
        vector *= np.exp(-1j * np.angle(vector[pivot]))
        return BlochState(float(q), int(band), float(energies[band]), vector)

    def continuous_path(self, q_values: np.ndarray, band: int = 0) -> tuple[np.ndarray, np.ndarray]:
        q_values = np.asarray(q_values, dtype=float)
        energies = np.empty(q_values.size)
        coefficients = np.empty((q_values.size, self.orders.size), dtype=np.complex128)
        previous = None
        for index, q in enumerate(q_values):
            state = self.state(float(q), band)
            vector = state.coefficients.copy()
            if previous is not None:
                overlap = np.vdot(previous, vector)
                if abs(overlap) > 1e-14:
                    vector *= np.exp(-1j * np.angle(overlap))
            energies[index] = state.energy
            coefficients[index] = vector
            previous = vector
        return energies, coefficients
