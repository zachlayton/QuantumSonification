"""Initial basis operators for the QMW Pauli Basis Laboratory v2."""

from __future__ import annotations

from typing import Any

import numpy as np

from .basis_operator import BasisOperator, square_matrix


def _require_power_of_two(dimension: int, basis_name: str) -> int:
    if dimension <= 0 or dimension & (dimension - 1):
        raise ValueError(
            f"{basis_name} requires a power-of-two Hilbert dimension"
        )
    return dimension.bit_length() - 1


class IdentityBasis(BasisOperator):
    name = "identity"
    description = "Computational basis; the canonical density representation."

    def unitary(self, dimension: int) -> np.ndarray:
        if dimension <= 0:
            raise ValueError("dimension must be positive")
        return np.eye(dimension, dtype=complex)


class HadamardBasis(BasisOperator):
    name = "hadamard"
    description = "Tensor-product Hadamard basis over all logical qubits."

    def unitary(self, dimension: int) -> np.ndarray:
        qubits = _require_power_of_two(dimension, self.name)
        single = np.array([[1, 1], [1, -1]], dtype=complex) / np.sqrt(2.0)
        result = np.array([[1.0]], dtype=complex)
        for _qubit in range(qubits):
            result = np.kron(result, single)
        return result


class QFTBasis(BasisOperator):
    """Discrete quantum Fourier basis using Qiskit's positive-phase convention."""

    name = "qft"
    description = "Quantum Fourier basis over the complete Hilbert space."

    def __init__(self, *, inverse: bool = False) -> None:
        self.inverse = bool(inverse)
        if self.inverse:
            self.name = "inverse_qft"
            self.description = (
                "Inverse quantum Fourier basis over the complete Hilbert space."
            )

    def unitary(self, dimension: int) -> np.ndarray:
        _require_power_of_two(dimension, self.name)
        indices = np.arange(dimension, dtype=float)
        sign = -1.0 if self.inverse else 1.0
        phases = np.exp(
            sign * 2j * np.pi * np.outer(indices, indices) / dimension
        )
        return phases / np.sqrt(dimension)

    def metadata(self, dimension: int) -> dict[str, Any]:
        metadata = super().metadata(dimension)
        metadata["inverse"] = self.inverse
        return metadata


def _canonicalize_eigenvector_phases(eigenvectors: np.ndarray) -> np.ndarray:
    """Choose reproducible phases by making each largest component real."""
    result = np.array(eigenvectors, dtype=complex, copy=True)
    for column in range(result.shape[1]):
        vector = result[:, column]
        pivot = int(np.argmax(np.abs(vector)))
        if abs(vector[pivot]) > 0:
            result[:, column] *= np.exp(-1j * np.angle(vector[pivot]))
    return result


class HamiltonianEigenbasis(BasisOperator):
    """Representation whose coordinates are ordered Hamiltonian eigenvectors."""

    name = "hamiltonian_eigenbasis"
    description = "Energy eigenbasis ordered by ascending Hamiltonian eigenvalue."

    def __init__(self, hamiltonian: Any) -> None:
        matrix = square_matrix(hamiltonian, name="hamiltonian")
        if not np.allclose(matrix, matrix.conj().T, atol=1e-10, rtol=0.0):
            raise ValueError("hamiltonian must be Hermitian")
        eigenvalues, eigenvectors = np.linalg.eigh(matrix)
        eigenvectors = _canonicalize_eigenvector_phases(eigenvectors)
        # Columns of V are eigenvectors in canonical coordinates.  V† maps
        # canonical coordinates into energy-eigenbasis coordinates.
        self._hamiltonian = np.array(matrix, copy=True)
        self._eigenvalues = np.asarray(eigenvalues, dtype=float)
        self._unitary = eigenvectors.conj().T

    @property
    def hamiltonian(self) -> np.ndarray:
        return np.array(self._hamiltonian, copy=True)

    @property
    def eigenvalues(self) -> np.ndarray:
        return np.array(self._eigenvalues, copy=True)

    def unitary(self, dimension: int) -> np.ndarray:
        if self._unitary.shape != (dimension, dimension):
            raise ValueError(
                "Hamiltonian dimension "
                f"{self._unitary.shape[0]} does not match density dimension "
                f"{dimension}"
            )
        return np.array(self._unitary, copy=True)

    def metadata(self, dimension: int) -> dict[str, Any]:
        metadata = super().metadata(dimension)
        metadata["eigenvalues"] = self._eigenvalues.tolist()
        return metadata


def transverse_ising_hamiltonian(
    n_qubits: int,
    *,
    coupling: float = 0.7,
    transverse_field: float = 0.45,
    longitudinal_field: float = 0.13,
) -> np.ndarray:
    """Return a small open-chain Ising Hamiltonian for laboratory examples."""
    if n_qubits <= 0:
        raise ValueError("n_qubits must be positive")
    identity = np.eye(2, dtype=complex)
    x = np.array([[0, 1], [1, 0]], dtype=complex)
    z = np.array([[1, 0], [0, -1]], dtype=complex)

    def product_operator(placements: dict[int, np.ndarray]) -> np.ndarray:
        # Matrix order matches Qiskit's q(n-1) tensor ... tensor q0.
        factors = [placements.get(qubit, identity) for qubit in reversed(range(n_qubits))]
        operator = factors[0]
        for factor in factors[1:]:
            operator = np.kron(operator, factor)
        return operator

    dimension = 1 << n_qubits
    hamiltonian = np.zeros((dimension, dimension), dtype=complex)
    for qubit in range(n_qubits - 1):
        hamiltonian -= coupling * product_operator({qubit: x, qubit + 1: x})
    for qubit in range(n_qubits):
        hamiltonian -= transverse_field * product_operator({qubit: z})
        # A small qubit-dependent longitudinal term removes accidental
        # degeneracies and makes example eigenvectors reproducible.
        hamiltonian -= (
            longitudinal_field
            * (qubit + 1)
            / n_qubits
            * product_operator({qubit: x})
        )
    return hamiltonian
