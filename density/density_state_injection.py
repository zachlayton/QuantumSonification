"""Validated, revisioned density-state injection for the four-qubit engine."""
from __future__ import annotations

from dataclasses import dataclass, field
import threading
from typing import Callable, Sequence

import numpy as np


class DensityStateError(ValueError):
    """A candidate density transaction is incomplete, stale, or unphysical."""


def bit_reversal_permutation(n_qubits: int) -> np.ndarray:
    """Map q0-LSB basis indices to the engine's q0-most-significant axes."""
    dimension = 1 << n_qubits
    return np.asarray(
        [int(f"{index:0{n_qubits}b}"[::-1], 2) for index in range(dimension)],
        dtype=np.int64,
    )


def qac_lsb_to_engine_density(rho: np.ndarray, n_qubits: int = 4) -> np.ndarray:
    matrix = np.asarray(rho, dtype=np.complex128)
    dimension = 1 << n_qubits
    if matrix.shape != (dimension, dimension):
        raise DensityStateError(
            f"Expected a {dimension}x{dimension} density matrix; got {matrix.shape}"
        )
    permutation = bit_reversal_permutation(n_qubits)
    # engine[reverse(i), reverse(j)] = qac[i, j]
    converted = np.empty_like(matrix)
    converted[np.ix_(permutation, permutation)] = matrix
    return converted


def validate_density_matrix(
    rho: np.ndarray,
    *,
    dimension: int = 16,
    tolerance: float = 1e-8,
) -> np.ndarray:
    matrix = np.asarray(rho, dtype=np.complex128)
    if matrix.shape != (dimension, dimension):
        raise DensityStateError(
            f"Expected a {dimension}x{dimension} density matrix; got {matrix.shape}"
        )
    if not np.all(np.isfinite(matrix.real)) or not np.all(np.isfinite(matrix.imag)):
        raise DensityStateError("Density matrix contains non-finite values")
    hermitian_error = float(np.max(np.abs(matrix - matrix.conj().T)))
    if hermitian_error > tolerance:
        raise DensityStateError(
            f"Density matrix is not Hermitian (max error {hermitian_error:.3g})"
        )
    matrix = 0.5 * (matrix + matrix.conj().T)
    trace = complex(np.trace(matrix))
    if abs(trace.imag) > tolerance or abs(trace.real - 1.0) > tolerance:
        raise DensityStateError(f"Density matrix trace must be 1; got {trace}")
    eigenvalues = np.linalg.eigvalsh(matrix).real
    minimum = float(eigenvalues.min())
    if minimum < -tolerance:
        raise DensityStateError(
            f"Density matrix is not positive semidefinite (min eigenvalue {minimum:.3g})"
        )
    # Remove harmless numerical negativity, then restore exact trace one.
    values, vectors = np.linalg.eigh(matrix)
    values = np.clip(values.real, 0.0, None)
    matrix = (vectors * values) @ vectors.conj().T
    return matrix / float(np.trace(matrix).real)


@dataclass
class DensityCandidate:
    revision: int
    n_qubits: int
    source_order: str
    real: np.ndarray | None = None
    imag: np.ndarray | None = None


@dataclass
class AtomicDensityStateReceiver:
    """Collect split OSC arrays and commit only a complete newer revision."""

    commit_callback: Callable[[np.ndarray, int, str], None]
    n_qubits: int = 4
    current_revision: int = -1
    candidate: DensityCandidate | None = None
    lock: threading.RLock = field(default_factory=threading.RLock)

    @property
    def dimension(self) -> int:
        return 1 << self.n_qubits

    def begin(self, revision: int, n_qubits: int, source_order: str = "q0_lsb") -> None:
        revision, n_qubits = int(revision), int(n_qubits)
        with self.lock:
            if revision <= self.current_revision:
                raise DensityStateError(
                    f"Stale density revision {revision}; current is {self.current_revision}"
                )
            if n_qubits != self.n_qubits:
                raise DensityStateError(
                    f"Expected {self.n_qubits} qubits; got {n_qubits}"
                )
            if source_order not in {"q0_lsb", "engine"}:
                raise DensityStateError(f"Unknown density ordering: {source_order}")
            self.candidate = DensityCandidate(revision, n_qubits, source_order)

    def _set_part(self, revision: int, values: Sequence[float], part: str) -> None:
        array = np.asarray(values, dtype=np.float64)
        expected = self.dimension * self.dimension
        with self.lock:
            if self.candidate is None or self.candidate.revision != int(revision):
                raise DensityStateError(f"No density candidate for revision {revision}")
            if array.size != expected:
                raise DensityStateError(
                    f"Density {part} needs {expected} values; got {array.size}"
                )
            setattr(self.candidate, part, array.reshape(self.dimension, self.dimension))

    def set_real(self, revision: int, values: Sequence[float]) -> None:
        self._set_part(revision, values, "real")

    def set_imag(self, revision: int, values: Sequence[float]) -> None:
        self._set_part(revision, values, "imag")

    def commit(self, revision: int) -> np.ndarray:
        with self.lock:
            candidate = self.candidate
            if candidate is None or candidate.revision != int(revision):
                raise DensityStateError(f"No density candidate for revision {revision}")
            if candidate.real is None or candidate.imag is None:
                raise DensityStateError("Density candidate requires both real and imaginary parts")
            matrix = candidate.real + 1j * candidate.imag
            matrix = validate_density_matrix(matrix, dimension=self.dimension)
            if candidate.source_order == "q0_lsb":
                matrix = qac_lsb_to_engine_density(matrix, self.n_qubits)
            self.commit_callback(matrix, candidate.revision, candidate.source_order)
            self.current_revision = candidate.revision
            self.candidate = None
            return matrix
