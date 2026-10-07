"""Hermitian Hamiltonian decomposition in the canonical Pauli basis."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np

from .pauli_basis import Array, pauli_basis, pauli_weight


@dataclass(frozen=True)
class PauliTerm:
    label: str
    coefficient: float
    matrix: Array

    @property
    def weight(self) -> int:
        return pauli_weight(self.label)


def pauli_decomposition(hamiltonian: object, *, tolerance: float = 1.0e-10) -> tuple[PauliTerm, ...]:
    matrix = np.asarray(hamiltonian, dtype=np.complex128)
    if matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1]:
        raise ValueError("hamiltonian must be square.")
    dimension = matrix.shape[0]
    if dimension < 2 or dimension & (dimension - 1):
        raise ValueError("hamiltonian dimension must be a power of two.")
    if tolerance < 0.0 or not np.all(np.isfinite(matrix)):
        raise ValueError("hamiltonian and tolerance must be finite.")
    if not np.allclose(matrix, matrix.conj().T, rtol=0.0, atol=tolerance):
        raise ValueError("hamiltonian must be Hermitian.")
    terms: list[PauliTerm] = []
    for label, operator in pauli_basis(dimension.bit_length() - 1, include_identity=True):
        coefficient = complex(np.trace(operator @ matrix) / dimension)
        if abs(coefficient.imag) > tolerance:
            raise ValueError("a Hermitian Pauli coefficient was unexpectedly complex.")
        if abs(coefficient.real) > tolerance:
            terms.append(PauliTerm(label, float(coefficient.real), operator))
    return tuple(terms)


def reconstruct_pauli_sum(terms: Iterable[PauliTerm]) -> Array:
    items = tuple(terms)
    if not items:
        raise ValueError("at least one Pauli term is required.")
    dimension = items[0].matrix.shape[0]
    result = np.zeros((dimension, dimension), dtype=np.complex128)
    for term in items:
        if term.matrix.shape != result.shape:
            raise ValueError("all Pauli terms must share a dimension.")
        result += term.coefficient * term.matrix
    return result


__all__ = ["PauliTerm", "pauli_decomposition", "reconstruct_pauli_sum"]
