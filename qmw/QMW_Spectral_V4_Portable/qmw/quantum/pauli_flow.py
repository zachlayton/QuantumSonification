"""Pauli-coordinate activity derived from rho and H; never a state evolution."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np

from .hilbert_current import hermitian_matrix, pauli_resolved_current
from .observables import observable_derivative, pauli_expectation
from .pauli_basis import pauli_basis, pauli_weight
from .pauli_decompose import pauli_decomposition


@dataclass(frozen=True)
class PauliActivity:
    label: str
    weight: int
    expectation: float
    derivative: float
    h_coefficient: float
    transport_activity: float

    @property
    def score(self) -> float:
        return abs(self.derivative) + self.transport_activity


def pauli_activities(rho: object, hamiltonian: object, *, hbar: float = 1.0, tolerance: float = 1.0e-9) -> tuple[PauliActivity, ...]:
    density = hermitian_matrix("rho", rho, tolerance=tolerance)
    generator = hermitian_matrix("hamiltonian", hamiltonian, tolerance=tolerance)
    if density.shape != generator.shape or density.shape[0] & (density.shape[0] - 1):
        raise ValueError("rho and hamiltonian must share a power-of-two dimension.")
    terms = {term.label: term for term in pauli_decomposition(generator, tolerance=tolerance)}
    result: list[PauliActivity] = []
    for label, operator in pauli_basis(density.shape[0].bit_length() - 1):
        term = terms.get(label)
        coefficient = 0.0 if term is None else term.coefficient
        transport = 0.0
        if term is not None:
            contribution = pauli_resolved_current(density, operator, coefficient, hbar=hbar, tolerance=tolerance)
            transport = float(np.sum(np.abs(contribution))) / 2.0
        result.append(PauliActivity(
            label, pauli_weight(label), pauli_expectation(density, operator, tolerance=tolerance),
            observable_derivative(density, generator, operator, hbar=hbar, tolerance=tolerance),
            coefficient, transport,
        ))
    return tuple(result)


def rank_pauli_activity(activities: Iterable[PauliActivity], *, top_k: int = 8) -> tuple[PauliActivity, ...]:
    if int(top_k) != top_k or top_k < 1:
        raise ValueError("top_k must be a positive integer.")
    return tuple(sorted(tuple(activities), key=lambda item: (-item.score, item.label))[: int(top_k)])


__all__ = ["PauliActivity", "pauli_activities", "rank_pauli_activity"]
