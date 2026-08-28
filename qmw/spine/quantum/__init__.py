"""Generators and evolution: H(t), L_k(t) -> rho(t)."""

from qmw.spine.quantum.evolution import (
    commutator,
    commutator_norm,
    evolve_unitary_step,
    evolve_unitary_trajectory,
    propagator,
    unitary_velocity,
)
from qmw.spine.quantum.hamiltonian import Hamiltonian, PauliTerm
from qmw.spine.quantum.pauli import (
    all_pauli_labels,
    decompose,
    operator_weight,
    pauli_expectation,
    pauli_matrix,
    reconstruct,
    weighted_activity,
)
from qmw.spine.quantum.state import (
    StateDiagnostics,
    StateInvariantError,
    diagnose,
    purity,
    validate_density_matrix,
    von_neumann_entropy,
)

__all__ = [
    "Hamiltonian",
    "PauliTerm",
    "StateDiagnostics",
    "StateInvariantError",
    "all_pauli_labels",
    "commutator",
    "commutator_norm",
    "decompose",
    "diagnose",
    "evolve_unitary_step",
    "evolve_unitary_trajectory",
    "operator_weight",
    "pauli_expectation",
    "pauli_matrix",
    "propagator",
    "purity",
    "reconstruct",
    "unitary_velocity",
    "validate_density_matrix",
    "von_neumann_entropy",
    "weighted_activity",
]
