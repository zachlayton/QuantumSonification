"""Optional Qiskit Nature matter-Hamiltonian adapter."""
from __future__ import annotations
import numpy as np


def second_q_to_matrix(second_q_operator, mapper=None) -> np.ndarray:
    try:
        from qiskit_nature.second_q.mappers import JordanWignerMapper
    except ImportError as exc:
        raise ImportError("install qiskit-nature to use this reference adapter") from exc
    mapped=(mapper or JordanWignerMapper()).map(second_q_operator)
    return np.asarray(mapped.to_matrix(),dtype=np.complex128)


def embed_or_reduce_matter(matrix: np.ndarray, dimension: int = 16) -> np.ndarray:
    """Validate a matter operator for the first 16-dimensional universe."""
    matrix=np.asarray(matrix,dtype=np.complex128)
    if matrix.shape != (dimension,dimension):
        raise ValueError(f"matter operator must be {dimension} x {dimension}; choose an active space before adaptation")
    return 0.5*(matrix+matrix.conj().T)
