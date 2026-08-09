"""Scientifically auditable exact Fermi-Hubbard analysis.

Qiskit Nature constructs the second-quantized model and Jordan-Wigner map.
The dense solve is deliberately restricted to one particle-number sector so
that a half-filled calculation cannot silently return the global Fock-space
vacuum or a lower one-particle state.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from importlib.metadata import version
from typing import Any

import numpy as np
from qiskit_nature.second_q.hamiltonians import FermiHubbardModel
from qiskit_nature.second_q.hamiltonians.lattices import BoundaryCondition, LineLattice
from qiskit_nature.second_q.mappers import JordanWignerMapper
from qiskit_nature.second_q.operators import FermionicOp


@dataclass(frozen=True)
class HubbardConfig:
    num_sites: int = 2
    particles: int = 2
    hopping: float = 1.0
    onsite_interaction: float = 4.0
    onsite_potential: float = 0.0
    num_eigenstates: int = 6

    def validate(self) -> None:
        if self.num_sites < 2:
            raise ValueError("num_sites must be at least 2")
        if not 0 <= self.particles <= 2 * self.num_sites:
            raise ValueError("particles must lie between 0 and 2*num_sites")
        if self.hopping < 0:
            raise ValueError("hopping is the non-negative magnitude t")
        if self.num_eigenstates < 1:
            raise ValueError("num_eigenstates must be positive")


def build_fermionic_hamiltonian(config: HubbardConfig) -> FermionicOp:
    """Return H = -t hopping + v occupation + U double occupation."""
    config.validate()
    lattice = LineLattice(
        num_nodes=config.num_sites,
        boundary_condition=BoundaryCondition.OPEN,
    ).uniform_parameters(
        uniform_interaction=-float(config.hopping),
        uniform_onsite_potential=float(config.onsite_potential),
    )
    return FermiHubbardModel(
        lattice=lattice,
        onsite_interaction=float(config.onsite_interaction),
    ).second_q_op().simplify()


def _mapped_matrix(operator: FermionicOp) -> np.ndarray:
    return np.asarray(JordanWignerMapper().map(operator).to_matrix(), dtype=np.complex128)


def _number_operator(num_spin_orbitals: int) -> FermionicOp:
    return FermionicOp(
        {f"+_{mode} -_{mode}": 1.0 for mode in range(num_spin_orbitals)},
        num_spin_orbitals=num_spin_orbitals,
    )


def _expectation(state: np.ndarray, matrix: np.ndarray) -> float:
    value = np.vdot(state, matrix @ state)
    return float(np.real_if_close(value, tol=1000).real)


def _canonicalize_phase(state: np.ndarray) -> np.ndarray:
    pivot = int(np.argmax(np.abs(state)))
    if abs(state[pivot]) > 0:
        state = state * np.exp(-1j * np.angle(state[pivot]))
    return np.real_if_close(state, tol=1000)


def analyze_hubbard(config: HubbardConfig = HubbardConfig()) -> dict[str, Any]:
    """Solve a small open chain exactly and return raw physical observables."""
    fermionic_hamiltonian = build_fermionic_hamiltonian(config)
    matrix = _mapped_matrix(fermionic_hamiltonian)
    hermiticity_error = float(np.max(np.abs(matrix - matrix.conj().T)))

    num_modes = 2 * config.num_sites
    number_matrix = _mapped_matrix(_number_operator(num_modes))
    number_diagonal = np.real_if_close(np.diag(number_matrix)).real
    sector_indices = np.flatnonzero(np.isclose(number_diagonal, config.particles, atol=1e-9))
    sector_matrix = matrix[np.ix_(sector_indices, sector_indices)]
    energies, vectors = np.linalg.eigh(sector_matrix)
    order = np.argsort(energies)
    energies = np.asarray(energies[order], dtype=float)
    vectors = vectors[:, order]

    ground = np.zeros(matrix.shape[0], dtype=np.complex128)
    ground[sector_indices] = vectors[:, 0]
    ground = _canonicalize_phase(ground)

    occupations: list[float] = []
    spin_polarizations: list[float] = []
    double_occupancies: list[float] = []
    for site in range(config.num_sites):
        up = 2 * site
        down = up + 1
        n_up = _mapped_matrix(
            FermionicOp({f"+_{up} -_{up}": 1.0}, num_spin_orbitals=num_modes)
        )
        n_down = _mapped_matrix(
            FermionicOp({f"+_{down} -_{down}": 1.0}, num_spin_orbitals=num_modes)
        )
        occupations.append(_expectation(ground, n_up + n_down))
        spin_polarizations.append(_expectation(ground, n_up - n_down))
        double_occupancies.append(_expectation(ground, n_up @ n_down))

    bond_coherences: list[float] = []
    for left in range(config.num_sites - 1):
        right = left + 1
        terms: dict[str, complex] = {}
        for spin in (0, 1):
            i, j = 2 * left + spin, 2 * right + spin
            terms[f"+_{i} -_{j}"] = 1.0
            terms[f"+_{j} -_{i}"] = 1.0
        bond_op = FermionicOp(terms, num_spin_orbitals=num_modes)
        bond_coherences.append(_expectation(ground, _mapped_matrix(bond_op)))

    count = min(config.num_eigenstates, len(energies))
    selected_energies = energies[:count]
    gaps = selected_energies[1:] - selected_energies[0]
    measured_particles = _expectation(ground, number_matrix)

    return {
        "schema": "qmw.hubbard.raw.v1",
        "software": {
            "qiskit": version("qiskit"),
            "qiskit_nature": version("qiskit-nature"),
            "numpy": version("numpy"),
        },
        "config": asdict(config),
        "dimensions": {
            "spin_orbitals": num_modes,
            "full_fock_space": int(matrix.shape[0]),
            "particle_sector": int(len(sector_indices)),
        },
        "validation": {
            "hermiticity_max_error": hermiticity_error,
            "measured_particles": measured_particles,
            "particle_number_error": abs(measured_particles - config.particles),
        },
        "raw": {
            "energies": selected_energies.tolist(),
            "gaps_from_ground": gaps.tolist(),
            "site_occupations": occupations,
            "site_spin_polarizations": spin_polarizations,
            "site_double_occupancies": double_occupancies,
            "bond_coherences": bond_coherences,
            "ground_state_probabilities": np.abs(ground).astype(float).tolist(),
        },
    }
