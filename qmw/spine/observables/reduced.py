"""Reduced views of rho: local Bloch vectors and pairwise correlations.

rho_i = Tr_{not i}(rho) is a projection of the full entangled state, not the
state of qubit i in isolation -- these functions never invent a second
trajectory, they only read rho_i off the one sealed rho.
"""
from __future__ import annotations

import numpy as np

from qmw.spine.quantum.pauli import pauli_expectation
from qmw.spine.quantum.state import purity, von_neumann_entropy

_AXES = ("X", "Y", "Z")


def partial_trace(rho: np.ndarray, keep: tuple[int, ...], n_qubits: int) -> np.ndarray:
    """Tr_{not keep}(rho) for a system of n_qubits qubits, each dimension 2."""
    keep = tuple(sorted(keep))
    tensor = rho.reshape([2] * (2 * n_qubits))
    letters = [chr(ord("a") + i) for i in range(2 * n_qubits + 2)]
    row_labels = letters[:n_qubits]
    col_labels: list[str] = []
    free = n_qubits
    for q in range(n_qubits):
        if q in keep:
            col_labels.append(letters[free])
            free += 1
        else:
            col_labels.append(row_labels[q])
    subscript_in = "".join(row_labels) + "".join(col_labels)
    out_row = "".join(row_labels[q] for q in keep)
    out_col = "".join(col_labels[q] for q in keep)
    reduced_tensor = np.einsum(f"{subscript_in}->{out_row}{out_col}", tensor)
    d_keep = 2 ** len(keep)
    return reduced_tensor.reshape(d_keep, d_keep)


def reduced_state(rho: np.ndarray, qubit: int, n_qubits: int) -> np.ndarray:
    return partial_trace(rho, (qubit,), n_qubits)


def bloch_vector(rho_i: np.ndarray) -> np.ndarray:
    """r_i = (x, y, z) for a single-qubit reduced state rho_i = (I + x X + y Y + z Z) / 2."""
    return np.array([pauli_expectation(rho_i, axis) for axis in _AXES])


def local_bloch_vectors(rho: np.ndarray, n_qubits: int) -> dict[int, np.ndarray]:
    return {q: bloch_vector(reduced_state(rho, q, n_qubits)) for q in range(n_qubits)}


def local_purity(rho: np.ndarray, qubit: int, n_qubits: int) -> float:
    return purity(reduced_state(rho, qubit, n_qubits))


def local_entropy(rho: np.ndarray, qubit: int, n_qubits: int) -> float:
    return von_neumann_entropy(reduced_state(rho, qubit, n_qubits))


def pair_correlation_tensor(
    rho: np.ndarray, i: int, j: int, n_qubits: int, connected: bool = True
) -> np.ndarray:
    """T_ab^(ij) = <sigma_a^i sigma_b^j>, or the connected tensor C = T - r_i (x) r_j."""
    if i == j:
        raise ValueError("pair_correlation_tensor requires two distinct qubits")

    def label(a: str | None, b: str | None) -> str:
        chars = ["I"] * n_qubits
        if a is not None:
            chars[i] = a
        if b is not None:
            chars[j] = b
        return "".join(chars)

    T = np.array(
        [[pauli_expectation(rho, label(a, b)) for b in _AXES] for a in _AXES]
    )
    if not connected:
        return T
    single_i = np.array([pauli_expectation(rho, label(a, None)) for a in _AXES])
    single_j = np.array([pauli_expectation(rho, label(None, b)) for b in _AXES])
    return T - np.outer(single_i, single_j)
