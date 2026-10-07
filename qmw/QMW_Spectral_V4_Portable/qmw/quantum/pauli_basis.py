"""Displayed-order tensor-Pauli basis used by integrated QMW observers."""

from __future__ import annotations

from functools import lru_cache
from itertools import product

import numpy as np


Array = np.ndarray
SINGLE_PAULI = {
    "I": np.eye(2, dtype=np.complex128),
    "X": np.array([[0, 1], [1, 0]], dtype=np.complex128),
    "Y": np.array([[0, -1j], [1j, 0]], dtype=np.complex128),
    "Z": np.array([[1, 0], [0, -1]], dtype=np.complex128),
}


def normalize_pauli_label(label: str) -> str:
    result = str(label).upper()
    if not result or any(symbol not in SINGLE_PAULI for symbol in result):
        raise ValueError("Pauli labels must be nonempty strings over I, X, Y, Z.")
    return result


@lru_cache(maxsize=None)
def pauli_matrix(label: str) -> Array:
    """Return a read-only tensor product in displayed computational-bit order."""

    normalized = normalize_pauli_label(label)
    result = SINGLE_PAULI[normalized[0]]
    for symbol in normalized[1:]:
        result = np.kron(result, SINGLE_PAULI[symbol])
    result = np.array(result, copy=True)
    result.flags.writeable = False
    return result


@lru_cache(maxsize=None)
def pauli_labels(qubits: int, *, include_identity: bool = False) -> tuple[str, ...]:
    if int(qubits) != qubits or qubits < 1:
        raise ValueError("qubits must be a positive integer.")
    labels = tuple("".join(items) for items in product("IXYZ", repeat=int(qubits)))
    return labels if include_identity else tuple(label for label in labels if set(label) != {"I"})


def pauli_weight(label: str) -> int:
    return sum(symbol != "I" for symbol in normalize_pauli_label(label))


def pauli_basis(qubits: int, *, include_identity: bool = False) -> tuple[tuple[str, Array], ...]:
    return tuple(
        (label, pauli_matrix(label))
        for label in pauli_labels(qubits, include_identity=include_identity)
    )


__all__ = [
    "Array", "SINGLE_PAULI", "normalize_pauli_label", "pauli_basis",
    "pauli_labels", "pauli_matrix", "pauli_weight",
]
