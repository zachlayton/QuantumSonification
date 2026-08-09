"""Pauli observables used by the current Full4Q comparison adapter."""

from __future__ import annotations

from collections.abc import Iterable

import numpy as np

from full4q_tomography_v1 import PAULI_LABELS

from .core import square_matrix


PAULI_MATRICES = {
    "I": np.array([[1, 0], [0, 1]], dtype=complex),
    "X": np.array([[0, 1], [1, 0]], dtype=complex),
    "Y": np.array([[0, -1j], [1j, 0]], dtype=complex),
    "Z": np.array([[1, 0], [0, -1]], dtype=complex),
}


def pauli_matrix(label: str) -> np.ndarray:
    normalized = str(label).upper()
    if not normalized or any(axis not in PAULI_MATRICES for axis in normalized):
        raise ValueError(f"invalid Pauli label {label!r}")
    operator = PAULI_MATRICES[normalized[-1]]
    for logical_qubit in reversed(range(len(normalized) - 1)):
        operator = np.kron(
            operator,
            PAULI_MATRICES[normalized[logical_qubit]],
        )
    return operator


def pauli_expectation(rho: np.ndarray, label: str) -> float:
    density = square_matrix(rho, name="rho")
    operator = pauli_matrix(label)
    if density.shape != operator.shape:
        raise ValueError(
            f"Pauli label {label!r} has dimension {operator.shape[0]}, "
            f"but rho has dimension {density.shape[0]}"
        )
    value = complex(np.trace(density @ operator))
    if abs(value.imag) > 1e-9:
        raise ValueError(
            f"Pauli expectation for {label!r} is unexpectedly complex"
        )
    return float(value.real)


def pauli_expectations(
    rho: np.ndarray,
    labels: Iterable[str] = PAULI_LABELS,
) -> dict[str, float]:
    return {label: pauli_expectation(rho, label) for label in labels}
