"""Optional Qiskit operator conversions; never imported by the real-time core."""
from __future__ import annotations
import numpy as np


def to_sparse_pauli_op(matrix: np.ndarray):
    try:
        from qiskit.quantum_info import Operator, SparsePauliOp
    except ImportError as exc:
        raise ImportError("install qiskit to use this reference adapter") from exc
    matrix=np.asarray(matrix,dtype=np.complex128)
    n=int(round(np.log2(len(matrix))))
    if matrix.shape != (2**n,2**n): raise ValueError("operator dimension must be a power of two")
    return SparsePauliOp.from_operator(Operator(matrix)).simplify()


def from_qiskit_operator(operator) -> np.ndarray:
    try:
        from qiskit.quantum_info import Operator
    except ImportError as exc:
        raise ImportError("install qiskit to use this reference adapter") from exc
    return np.asarray(Operator(operator).data,dtype=np.complex128)
