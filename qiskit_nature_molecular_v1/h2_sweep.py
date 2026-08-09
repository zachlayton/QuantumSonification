"""Exact STO-3G H2 bond sweep with explicit molecular observables."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from importlib.metadata import version
from typing import Any, Iterable

import numpy as np
from qiskit_algorithms import NumPyMinimumEigensolver
from qiskit_nature.second_q.algorithms import GroundStateEigensolver
from qiskit_nature.second_q.drivers import PySCFDriver
from qiskit_nature.second_q.mappers import JordanWignerMapper
from qiskit_nature.second_q.operators import FermionicOp
from qiskit_nature.units import DistanceUnit


@dataclass(frozen=True)
class H2SweepConfig:
    distances_angstrom: tuple[float, ...] = (0.5, 0.735, 1.0, 1.5, 2.0)
    basis: str = "sto3g"
    num_eigenstates: int = 6

    def validate(self) -> None:
        if not self.distances_angstrom:
            raise ValueError("at least one bond distance is required")
        if any(distance <= 0 for distance in self.distances_angstrom):
            raise ValueError("bond distances must be positive")
        if self.num_eigenstates < 1:
            raise ValueError("num_eigenstates must be positive")


def _mapped_matrix(operator: FermionicOp) -> np.ndarray:
    return np.asarray(JordanWignerMapper().map(operator).to_matrix(), dtype=np.complex128)


def _expectation(state: np.ndarray, operator: FermionicOp) -> complex:
    return complex(np.vdot(state, _mapped_matrix(operator) @ state))


def _number_operator(num_modes: int) -> FermionicOp:
    return FermionicOp(
        {f"+_{mode} -_{mode}": 1.0 for mode in range(num_modes)},
        num_spin_orbitals=num_modes,
    )


def _complex_array_data(values: np.ndarray) -> dict[str, Any]:
    return {
        "real": np.asarray(values.real, dtype=float).tolist(),
        "imag": np.asarray(values.imag, dtype=float).tolist(),
    }


def _reduced_density_matrices(state: np.ndarray, num_modes: int) -> tuple[np.ndarray, np.ndarray]:
    """Return spin-orbital 1- and 2-RDMs.

    gamma[p,q] = <a_p^dagger a_q>
    Gamma[p,q,r,s] = <a_p^dagger a_q^dagger a_s a_r>
    """
    rdm1 = np.empty((num_modes, num_modes), dtype=np.complex128)
    rdm2 = np.empty((num_modes, num_modes, num_modes, num_modes), dtype=np.complex128)
    for p in range(num_modes):
        for q in range(num_modes):
            rdm1[p, q] = _expectation(
                state,
                FermionicOp({f"+_{p} -_{q}": 1.0}, num_spin_orbitals=num_modes),
            )
            for r in range(num_modes):
                for s in range(num_modes):
                    rdm2[p, q, r, s] = _expectation(
                        state,
                        FermionicOp(
                            {f"+_{p} +_{q} -_{s} -_{r}": 1.0},
                            num_spin_orbitals=num_modes,
                        ),
                    )
    return rdm1, rdm2


def analyze_h2_point(distance_angstrom: float, basis: str = "sto3g", num_eigenstates: int = 6) -> dict[str, Any]:
    if distance_angstrom <= 0:
        raise ValueError("distance_angstrom must be positive")
    problem = PySCFDriver(
        atom=f"H 0 0 0; H 0 0 {distance_angstrom:.12g}",
        basis=basis,
        charge=0,
        spin=0,
        unit=DistanceUnit.ANGSTROM,
    ).run()

    mapper = JordanWignerMapper()
    ground_result = GroundStateEigensolver(mapper, NumPyMinimumEigensolver()).solve(problem)
    state = np.asarray(ground_result.raw_result.eigenstate.data, dtype=np.complex128)
    state /= np.linalg.norm(state)
    ground_density = np.outer(state, state.conj())

    electronic_op, _ = problem.second_q_ops()
    electronic_matrix = np.asarray(mapper.map(electronic_op).to_matrix(), dtype=np.complex128)
    num_modes = 2 * problem.num_spatial_orbitals
    particle_count = int(sum(problem.num_particles))
    number_matrix = _mapped_matrix(_number_operator(num_modes))
    number_diagonal = np.real_if_close(np.diag(number_matrix)).real
    sector = np.flatnonzero(np.isclose(number_diagonal, particle_count, atol=1e-9))
    sector_energies = np.linalg.eigvalsh(electronic_matrix[np.ix_(sector, sector)])
    count = min(num_eigenstates, len(sector_energies))
    electronic_energies = np.asarray(sector_energies[:count], dtype=float)
    total_energies = electronic_energies + float(problem.nuclear_repulsion_energy)

    rdm1, rdm2 = _reduced_density_matrices(state, num_modes)
    contracted_rdm2 = np.einsum("pqrq->pr", rdm2)
    contraction_target = (particle_count - 1) * rdm1
    rdm2_contraction_error = float(np.max(np.abs(contracted_rdm2 - contraction_target)))

    electronic_dipole = np.asarray(ground_result.electronic_dipole_moment[0], dtype=float)
    nuclear_dipole = np.asarray(ground_result.nuclear_dipole_moment, dtype=float)
    total_dipole_vector = nuclear_dipole - electronic_dipole

    return {
        "distance_angstrom": float(distance_angstrom),
        "basis": basis,
        "dimensions": {
            "spatial_orbitals": int(problem.num_spatial_orbitals),
            "spin_orbitals": int(num_modes),
            "particles": particle_count,
            "particle_sector": int(len(sector)),
        },
        "energies_hartree": {
            "hartree_fock_total": float(problem.reference_energy),
            "nuclear_repulsion": float(problem.nuclear_repulsion_energy),
            "electronic": electronic_energies.tolist(),
            "total": total_energies.tolist(),
            "excitation_gaps": (total_energies[1:] - total_energies[0]).tolist(),
        },
        "dipole_atomic_units": {
            "electronic": electronic_dipole.tolist(),
            "nuclear": nuclear_dipole.tolist(),
            "total_vector": total_dipole_vector.tolist(),
            "total_magnitude": float(np.linalg.norm(total_dipole_vector)),
        },
        "hartree_fock_orbital_occupations": {
            "alpha": np.asarray(problem.orbital_occupations, dtype=float).tolist(),
            "beta": np.asarray(problem.orbital_occupations_b, dtype=float).tolist(),
        },
        "ground_state_rdm": {
            "convention_1rdm": "gamma[p,q] = <a_p^dagger a_q>",
            "convention_2rdm": "Gamma[p,q,r,s] = <a_p^dagger a_q^dagger a_s a_r>",
            "spin_orbital_1rdm": _complex_array_data(rdm1),
            "spin_orbital_2rdm": _complex_array_data(rdm2),
            "natural_occupations": np.linalg.eigvalsh(rdm1).real[::-1].tolist(),
        },
        "ground_state_fock_density": {
            "basis": "Jordan-Wigner computational basis",
            "matrix": _complex_array_data(ground_density),
        },
        "validation": {
            "hamiltonian_hermiticity_max_error": float(
                np.max(np.abs(electronic_matrix - electronic_matrix.conj().T))
            ),
            "particle_number": float(np.real(np.vdot(state, number_matrix @ state))),
            "one_rdm_trace": float(np.trace(rdm1).real),
            "one_rdm_hermiticity_max_error": float(np.max(np.abs(rdm1 - rdm1.conj().T))),
            "two_rdm_contraction_max_error": rdm2_contraction_error,
        },
    }


def run_h2_sweep(config: H2SweepConfig = H2SweepConfig()) -> dict[str, Any]:
    config.validate()
    points = [
        analyze_h2_point(distance, config.basis, config.num_eigenstates)
        for distance in config.distances_angstrom
    ]
    ground_energies = np.asarray([point["energies_hartree"]["total"][0] for point in points])
    minimum_index = int(np.argmin(ground_energies))
    return {
        "schema": "qmw.qiskit_nature.h2_sweep.raw.v1",
        "software": {
            "qiskit": version("qiskit"),
            "qiskit_nature": version("qiskit-nature"),
            "qiskit_algorithms": version("qiskit-algorithms"),
            "pyscf": version("pyscf"),
            "numpy": version("numpy"),
        },
        "config": asdict(config),
        "points": points,
        "sweep_summary": {
            "sampled_minimum_distance_angstrom": points[minimum_index]["distance_angstrom"],
            "sampled_minimum_energy_hartree": float(ground_energies[minimum_index]),
        },
        "mapping_policy": "raw molecular descriptor only; no pitch or tuning quantization",
    }
