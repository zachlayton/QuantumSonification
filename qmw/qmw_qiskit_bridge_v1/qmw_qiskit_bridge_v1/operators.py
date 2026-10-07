from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping

import numpy as np
from qiskit.quantum_info import SparsePauliOp


@dataclass(frozen=True)
class PauliTerm:
    label: str
    coefficient: complex

    def __post_init__(self) -> None:
        label = self.label.upper()
        if not label or any(symbol not in "IXYZ" for symbol in label):
            raise ValueError(f"invalid Pauli label: {self.label!r}")
        object.__setattr__(self, "label", label)
        object.__setattr__(self, "coefficient", complex(self.coefficient))


@dataclass(frozen=True)
class QMWOperator:
    """Named Pauli sum using Qiskit's |q(n-1)...q0> label convention."""

    name: str
    terms: tuple[PauliTerm, ...]

    def __post_init__(self) -> None:
        terms = tuple(self.terms)
        if not terms:
            raise ValueError("an operator needs at least one Pauli term")
        widths = {len(term.label) for term in terms}
        if len(widths) != 1:
            raise ValueError("all Pauli labels must have the same width")
        object.__setattr__(self, "terms", terms)

    @property
    def n_qubits(self) -> int:
        return len(self.terms[0].label)

    def to_sparse_pauli_op(self) -> SparsePauliOp:
        return SparsePauliOp.from_list(
            [(term.label, term.coefficient) for term in self.terms]
        ).simplify()

    def matrix(self) -> np.ndarray:
        return np.asarray(self.to_sparse_pauli_op().to_matrix(), dtype=np.complex128)

    @classmethod
    def from_mapping(cls, name: str, terms: Mapping[str, complex]) -> "QMWOperator":
        return cls(name, tuple(PauliTerm(label, coefficient) for label, coefficient in terms.items()))

    @classmethod
    def from_terms(cls, name: str, terms: Iterable[tuple[str, complex]]) -> "QMWOperator":
        return cls(name, tuple(PauliTerm(*term) for term in terms))
