"""Playable density-matrix representations over the Full4Q Pauli pipeline."""

from .basis_operator import (
    BasisOperator,
    validate_density_matrix,
    validate_unitary,
)
from .bases import (
    HadamardBasis,
    HamiltonianEigenbasis,
    IdentityBasis,
    QFTBasis,
    transverse_ising_hamiltonian,
)
from .laboratory import (
    BasisLaboratoryResult,
    ObservableComparison,
    density_from_preset,
    run_basis_laboratory,
    save_laboratory_result,
    tomography_from_density,
)

__all__ = [
    "BasisLaboratoryResult",
    "BasisOperator",
    "HadamardBasis",
    "HamiltonianEigenbasis",
    "IdentityBasis",
    "ObservableComparison",
    "QFTBasis",
    "density_from_preset",
    "run_basis_laboratory",
    "save_laboratory_result",
    "tomography_from_density",
    "transverse_ising_hamiltonian",
    "validate_density_matrix",
    "validate_unitary",
]
