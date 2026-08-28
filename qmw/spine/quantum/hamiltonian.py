"""H(t) = sum_P h_P(t) * P: a Hamiltonian assembled from weighted Pauli strings.

Gestures modify coefficients h_P(t); they never touch rho or the sound
directly. That keeps the causal chain gesture -> h_P(t) -> H(t) -> rho(t)
-> sound intact.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Union

import numpy as np

from qmw.spine.quantum.pauli import pauli_matrix

Coefficient = Union[float, Callable[[float], float]]


@dataclass(frozen=True)
class PauliTerm:
    """One h_P(t) * P summand, e.g. PauliTerm('ZI', omega_1)."""

    label: str
    coefficient: Coefficient

    @property
    def is_time_independent(self) -> bool:
        return not callable(self.coefficient)

    def value(self, t: float) -> float:
        return self.coefficient(t) if callable(self.coefficient) else float(self.coefficient)


class Hamiltonian:
    """A sum of Pauli terms; H.matrix(t) assembles the dense generator at time t."""

    def __init__(self, n_qubits: int, terms: list[PauliTerm]):
        for term in terms:
            if len(term.label) != n_qubits:
                raise ValueError(
                    f"term '{term.label}' does not match n_qubits={n_qubits}"
                )
        self.n_qubits = n_qubits
        self.terms = list(terms)

    @property
    def dimension(self) -> int:
        return 2**self.n_qubits

    @property
    def is_time_independent(self) -> bool:
        return all(term.is_time_independent for term in self.terms)

    def matrix(self, t: float = 0.0) -> np.ndarray:
        d = self.dimension
        H = np.zeros((d, d), dtype=complex)
        for term in self.terms:
            H = H + term.value(t) * pauli_matrix(term.label)
        return H

    def coefficients(self, t: float = 0.0) -> dict[str, float]:
        return {term.label: term.value(t) for term in self.terms}

    @staticmethod
    def compose(*parts: "Hamiltonian") -> "Hamiltonian":
        """H_local + H_coupling + ... : concatenate compatible term groups."""
        if not parts:
            raise ValueError("compose() requires at least one Hamiltonian")
        n_qubits = parts[0].n_qubits
        if any(part.n_qubits != n_qubits for part in parts):
            raise ValueError("cannot compose Hamiltonians on different qubit counts")
        terms = [term for part in parts for term in part.terms]
        return Hamiltonian(n_qubits, terms)
