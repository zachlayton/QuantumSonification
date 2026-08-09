"""Deterministic four-qubit density matrices for procedural notation."""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np


IDENTITY_2 = np.eye(2, dtype=complex)
PAULI_X = np.asarray(((0, 1), (1, 0)), dtype=complex)
PAULI_Z = np.asarray(((1, 0), (0, -1)), dtype=complex)


def build_four_qubit_density_matrix(
    evolution_time: float,
    dephasing: float = 0.18,
    coupling: float = 1.0,
    transverse_field: float = 0.83,
    staggered_field: float = 0.27,
) -> np.ndarray:
    """Evolve |0000> under an interacting Hamiltonian and apply dephasing."""
    if not np.isfinite(evolution_time) or evolution_time < 0.0:
        raise ValueError("evolution_time must be a finite nonnegative number")
    if not np.isfinite(dephasing) or not 0.0 <= dephasing <= 1.0:
        raise ValueError("dephasing must lie between zero and one")

    hamiltonian = np.zeros((16, 16), dtype=complex)
    for qubit in range(4):
        next_qubit = (qubit + 1) % 4
        hamiltonian += coupling * _many_qubit_operator(
            {qubit: PAULI_Z, next_qubit: PAULI_Z}
        )
        hamiltonian += transverse_field * _many_qubit_operator({qubit: PAULI_X})
        hamiltonian += (
            staggered_field
            * (1.0 if qubit % 2 == 0 else -1.0)
            * _many_qubit_operator({qubit: PAULI_Z})
        )

    eigenvalues, eigenvectors = np.linalg.eigh(hamiltonian)
    initial_state = np.zeros(16, dtype=complex)
    initial_state[0] = 1.0
    coefficients = eigenvectors.conj().T @ initial_state
    state = eigenvectors @ (np.exp(-1j * eigenvalues * evolution_time) * coefficients)
    pure_density = np.outer(state, state.conj())
    population_density = np.diag(np.real(np.diag(pure_density))).astype(complex)
    density = (1.0 - dephasing) * pure_density + dephasing * population_density
    density /= np.trace(density)
    return density


def build_density_matrix_snapshots(
    evolution_times: Sequence[float] = (0.35, 0.8, 1.25, 1.7),
    dephasing: float = 0.18,
) -> tuple[np.ndarray, ...]:
    """Return a short, reproducible density-matrix evolution."""
    if not evolution_times:
        raise ValueError("evolution_times must not be empty")
    return tuple(
        build_four_qubit_density_matrix(time, dephasing=dephasing)
        for time in evolution_times
    )


def density_matrix_purity(density: np.ndarray) -> float:
    """Return Tr(rho squared) after validating the matrix dimensions."""
    if density.shape != (16, 16):
        raise ValueError("density matrix must have shape 16 by 16")
    return float(np.real(np.trace(density @ density)))


def weighted_z_expectation(
    density: np.ndarray,
    weights: Sequence[float] = (1.0, 2.0, 3.0, 4.0),
) -> float:
    """Return the weighted four-qubit Z magnetization of a density matrix."""
    if density.shape != (16, 16):
        raise ValueError("density matrix must have shape 16 by 16")
    if len(weights) != 4 or any(not np.isfinite(weight) for weight in weights):
        raise ValueError("weights must contain four finite numbers")
    observable = sum(
        float(weight) * _many_qubit_operator({qubit: PAULI_Z})
        for qubit, weight in enumerate(weights)
    )
    return float(np.real(np.trace(density @ observable)))


def _many_qubit_operator(operators: dict[int, np.ndarray]) -> np.ndarray:
    result = np.asarray(((1.0 + 0.0j,),), dtype=complex)
    for qubit in range(4):
        result = np.kron(result, operators.get(qubit, IDENTITY_2))
    return result
