from dataclasses import asdict, dataclass
from typing import Any

import numpy as np
from scipy.optimize import linear_sum_assignment

from ..core import TransformContext, UnitaryOperator, square_matrix
from ._spectral import eigenbasis


class HamiltonianEigenbasis(UnitaryOperator):
    name = "hamiltonian_eigenbasis"
    description = "Energy representation ordered by ascending eigenvalue."

    def __init__(self, hamiltonian: Any) -> None:
        matrix = square_matrix(hamiltonian, name="hamiltonian")
        if not np.allclose(matrix, matrix.conj().T, atol=1e-10, rtol=0.0):
            raise ValueError("hamiltonian must be Hermitian")
        self._eigenvalues, vectors = eigenbasis(matrix)
        self._hamiltonian = np.array(matrix, copy=True)
        self._unitary = vectors.conj().T

    @classmethod
    def from_eigendecomposition(
        cls,
        hamiltonian: Any,
        eigenvalues: Any,
        eigenvectors: Any,
    ) -> "HamiltonianEigenbasis":
        matrix = square_matrix(hamiltonian, name="hamiltonian")
        values = np.asarray(eigenvalues, dtype=float)
        vectors = np.asarray(eigenvectors, dtype=complex)
        dimension = matrix.shape[0]
        if values.shape != (dimension,) or vectors.shape != matrix.shape:
            raise ValueError("eigendecomposition dimensions do not match")
        if not np.allclose(
            vectors.conj().T @ vectors,
            np.eye(dimension),
            atol=1e-9,
            rtol=0.0,
        ):
            raise ValueError("eigenvectors must be orthonormal")
        diagonalized = vectors.conj().T @ matrix @ vectors
        if not np.allclose(
            diagonalized,
            np.diag(values),
            atol=1e-8,
            rtol=0.0,
        ):
            raise ValueError("eigendecomposition does not diagonalize Hamiltonian")
        instance = cls.__new__(cls)
        instance._hamiltonian = np.array(matrix, copy=True)
        instance._eigenvalues = np.array(values, copy=True)
        instance._unitary = vectors.conj().T
        return instance

    @property
    def hamiltonian(self) -> np.ndarray:
        return np.array(self._hamiltonian, copy=True)

    @property
    def eigenvalues(self) -> np.ndarray:
        return np.array(self._eigenvalues, copy=True)

    def unitary(self, dimension: int, context: TransformContext = None) -> np.ndarray:
        if self._unitary.shape != (dimension, dimension):
            raise ValueError(
                f"Hamiltonian dimension {self._unitary.shape[0]} does not "
                f"match density dimension {dimension}"
            )
        return np.array(self._unitary, copy=True)

    def metadata(
        self, dimension: int, context: TransformContext = None
    ) -> dict[str, Any]:
        metadata = super().metadata(dimension, context)
        metadata["eigenvalues"] = self._eigenvalues.tolist()
        return metadata


@dataclass(frozen=True)
class IsingHamiltonianSpec:
    n_qubits: int = 4
    coupling: float = 0.7
    transverse_field: float = 0.45
    longitudinal_field: float = 0.13
    boundary: str = "open"

    def __post_init__(self) -> None:
        if self.n_qubits <= 0:
            raise ValueError("n_qubits must be positive")
        if self.boundary not in {"open", "periodic"}:
            raise ValueError("boundary must be open or periodic")
        for name in ("coupling", "transverse_field", "longitudinal_field"):
            if not np.isfinite(getattr(self, name)):
                raise ValueError(f"{name} must be finite")

    def matrix(self) -> np.ndarray:
        return transverse_ising_hamiltonian(
            self.n_qubits,
            coupling=self.coupling,
            transverse_field=self.transverse_field,
            longitudinal_field=self.longitudinal_field,
            boundary=self.boundary,
        )

    def metadata(self) -> dict[str, Any]:
        return asdict(self)


class HamiltonianBasisTracker:
    """Align consecutive eigensystems for continuous live control."""

    def __init__(self, *, degeneracy_tolerance: float = 1e-8) -> None:
        self.degeneracy_tolerance = float(degeneracy_tolerance)
        self._previous_vectors: np.ndarray | None = None

    def reset(self) -> None:
        self._previous_vectors = None

    def solve(
        self,
        hamiltonian: Any,
    ) -> tuple[HamiltonianEigenbasis, dict[str, Any]]:
        matrix = square_matrix(hamiltonian, name="hamiltonian")
        values, vectors = np.linalg.eigh(matrix)
        tracking = False
        minimum_overlap = 1.0
        if self._previous_vectors is not None:
            if self._previous_vectors.shape != vectors.shape:
                self.reset()
            else:
                overlap = np.abs(self._previous_vectors.conj().T @ vectors)
                previous_indices, current_indices = linear_sum_assignment(-overlap)
                order = np.empty(len(values), dtype=int)
                order[previous_indices] = current_indices
                values = values[order]
                vectors = vectors[:, order]
                matched = overlap[previous_indices, current_indices]
                minimum_overlap = float(np.min(matched))
                tracking = True

                start = 0
                while start < len(values):
                    stop = start + 1
                    while (
                        stop < len(values)
                        and abs(values[stop] - values[start])
                        <= self.degeneracy_tolerance
                    ):
                        stop += 1
                    if stop - start > 1:
                        current = vectors[:, start:stop]
                        previous = self._previous_vectors[:, start:stop]
                        left, _singular, right_h = np.linalg.svd(
                            current.conj().T @ previous
                        )
                        vectors[:, start:stop] = current @ left @ right_h
                    start = stop

                for column in range(vectors.shape[1]):
                    phase = np.vdot(
                        self._previous_vectors[:, column],
                        vectors[:, column],
                    )
                    if abs(phase) > 0.0:
                        vectors[:, column] *= np.exp(-1j * np.angle(phase))

        self._previous_vectors = np.array(vectors, copy=True)
        basis = HamiltonianEigenbasis.from_eigendecomposition(
            matrix,
            values,
            vectors,
        )
        gaps = np.abs(values[:, None] - values[None, :])
        np.fill_diagonal(gaps, np.inf)
        finite_gap = float(np.min(gaps)) if len(values) > 1 else 0.0
        return basis, {
            "tracking_applied": tracking,
            "minimum_matched_overlap": minimum_overlap,
            "minimum_level_gap": finite_gap,
        }


def transverse_ising_hamiltonian(
    n_qubits: int,
    *,
    coupling: float = 0.7,
    transverse_field: float = 0.45,
    longitudinal_field: float = 0.13,
    boundary: str = "open",
) -> np.ndarray:
    if n_qubits <= 0:
        raise ValueError("n_qubits must be positive")
    identity = np.eye(2, dtype=complex)
    x = np.array([[0, 1], [1, 0]], dtype=complex)
    z = np.array([[1, 0], [0, -1]], dtype=complex)

    def product(placements: dict[int, np.ndarray]) -> np.ndarray:
        factors = [
            placements.get(qubit, identity)
            for qubit in reversed(range(n_qubits))
        ]
        result = factors[0]
        for factor in factors[1:]:
            result = np.kron(result, factor)
        return result

    if boundary not in {"open", "periodic"}:
        raise ValueError("boundary must be open or periodic")
    result = np.zeros((1 << n_qubits, 1 << n_qubits), dtype=complex)
    pairs = [(qubit, qubit + 1) for qubit in range(n_qubits - 1)]
    if boundary == "periodic" and n_qubits > 2:
        pairs.append((n_qubits - 1, 0))
    for left, right in pairs:
        result -= coupling * product({left: x, right: x})
    for qubit in range(n_qubits):
        result -= transverse_field * product({qubit: z})
        result -= (
            longitudinal_field
            * (qubit + 1)
            / n_qubits
            * product({qubit: x})
        )
    return result
