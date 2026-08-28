"""Pauli-string algebra: the coordinate system for the dynamical spine.

Any Hermitian, trace-one operator on n qubits can be written exactly as
    rho = (1/d) * sum_P p_P * P,   p_P = Tr(rho P),   d = 2**n
over the 4**n Pauli strings P in {I, X, Y, Z}^(x n). This module builds those
strings and moves between an operator and its Pauli coordinates.
"""
from __future__ import annotations

from functools import lru_cache
from itertools import product

import numpy as np

_I = np.array([[1, 0], [0, 1]], dtype=complex)
_X = np.array([[0, 1], [1, 0]], dtype=complex)
_Y = np.array([[0, -1j], [1j, 0]], dtype=complex)
_Z = np.array([[1, 0], [0, -1]], dtype=complex)

SINGLE_QUBIT_PAULI = {"I": _I, "X": _X, "Y": _Y, "Z": _Z}


def operator_weight(label: str) -> int:
    """Number of non-identity factors in a Pauli-string label, e.g. weight('XYII') == 2."""
    return sum(1 for c in label if c != "I")


@lru_cache(maxsize=None)
def all_pauli_labels(n_qubits: int) -> tuple[str, ...]:
    """All 4**n_qubits Pauli-string labels, e.g. n_qubits=2 -> ('II','IX',...,'ZZ')."""
    return tuple("".join(chars) for chars in product("IXYZ", repeat=n_qubits))


@lru_cache(maxsize=None)
def pauli_matrix(label: str) -> np.ndarray:
    """Dense matrix for a Pauli-string label such as 'XZI' (leftmost char = qubit 0)."""
    matrix = SINGLE_QUBIT_PAULI[label[0]]
    for char in label[1:]:
        matrix = np.kron(matrix, SINGLE_QUBIT_PAULI[char])
    matrix.setflags(write=False)
    return matrix


def pauli_expectation(rho: np.ndarray, label: str) -> float:
    """p_P = Tr(rho P) for a Hermitian rho; the imaginary part is numerical noise."""
    value = np.trace(rho @ pauli_matrix(label))
    return float(value.real)


def decompose(operator: np.ndarray, labels: tuple[str, ...] | None = None) -> dict[str, float]:
    """Pauli coordinates {label: Tr(operator @ P)} of a Hermitian operator."""
    n_qubits = int(round(np.log2(operator.shape[0])))
    labels = labels if labels is not None else all_pauli_labels(n_qubits)
    return {label: pauli_expectation(operator, label) for label in labels}


def reconstruct(coefficients: dict[str, float], n_qubits: int) -> np.ndarray:
    """Invert `decompose`: rho = (1/d) * sum_P p_P * P."""
    d = 2**n_qubits
    rho = np.zeros((d, d), dtype=complex)
    for label, value in coefficients.items():
        rho = rho + value * pauli_matrix(label)
    return rho / d


def weighted_activity(field: dict[str, float]) -> dict[int, float]:
    """Group a Pauli-coordinate field by locality weight: A_k = sqrt(sum_{weight(P)=k} field[P]**2)."""
    sums: dict[int, float] = {}
    for label, value in field.items():
        k = operator_weight(label)
        sums[k] = sums.get(k, 0.0) + value * value
    return {k: float(np.sqrt(total)) for k, total in sums.items()}
