"""Operator-space velocity: the Pauli decomposition of rho_dot IS the field of dot p_P.

d/dt Tr(rho P) = i * <[H, P]> = Tr(P @ (-i[H, rho])), so rather than forming
[H, P] separately for every P, decompose rho_dot_unitary once (see
quantum.pauli.decompose) and read every dot_p_P off the same operator.
"""
from __future__ import annotations

import numpy as np

from qmw.spine.quantum.evolution import commutator_norm, unitary_velocity
from qmw.spine.quantum.pauli import all_pauli_labels, decompose, weighted_activity


def pauli_field(rho: np.ndarray, labels: tuple[str, ...] | None = None) -> dict[str, float]:
    """{label: p_P} -- 'how much of this observable is present'."""
    return decompose(rho, labels)


def pauli_velocity_field(
    H: np.ndarray, rho: np.ndarray, labels: tuple[str, ...] | None = None
) -> dict[str, float]:
    """{label: dot_p_P} (unitary part only) -- 'how fast it is changing'."""
    rho_dot_u = unitary_velocity(H, rho)
    return decompose(rho_dot_u, labels)


def is_conserved(velocity: float, atol: float = 1e-6) -> bool:
    """[H, P] == 0 <=> dot_p_P == 0 for a closed, time-independent generator."""
    return abs(velocity) < atol


def dynamical_sectors(
    H: np.ndarray, rho: np.ndarray, n_qubits: int
) -> dict[int, float]:
    """A_k = sqrt(sum_{weight(P)=k} dot_p_P**2): activity by locality (local/pair/.../global)."""
    labels = all_pauli_labels(n_qubits)
    velocity = pauli_velocity_field(H, rho, labels)
    return weighted_activity(velocity)


def activity(H: np.ndarray, rho: np.ndarray) -> float:
    """A_H = ||[H, rho]||_F: the global dynamical-misalignment scalar."""
    return commutator_norm(H, rho)
