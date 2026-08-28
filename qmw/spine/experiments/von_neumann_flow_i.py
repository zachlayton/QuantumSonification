"""Von Neumann Flow I: the first integrated build of the dynamical spine.

    H = omega_1 ZI + omega_2 IZ + J XX,   |psi_0> = |+>|0>

No projector, no geometry, no dissipation -- the question this experiment
answers is whether Hamiltonian-generated density-matrix dynamics alone
produce compelling structure: energy and ZZ are conserved, local purity and
entropy develop as the XX coupling entangles the pair, and the constant
commutator norm reorganizes itself across the Pauli sectors.
"""
from __future__ import annotations

import numpy as np

from qmw.spine.frame import QuantumFrame, build_frame
from qmw.spine.quantum import Hamiltonian, PauliTerm
from qmw.spine.quantum.evolution import evolve_unitary_trajectory

N_QUBITS = 2
DEFAULT_OMEGA_1 = 1.3
DEFAULT_OMEGA_2 = 0.7
DEFAULT_COUPLING = 0.5


def build_generator(
    omega_1: float = DEFAULT_OMEGA_1,
    omega_2: float = DEFAULT_OMEGA_2,
    coupling: float = DEFAULT_COUPLING,
) -> Hamiltonian:
    return Hamiltonian(
        N_QUBITS,
        [
            PauliTerm("ZI", omega_1),
            PauliTerm("IZ", omega_2),
            PauliTerm("XX", coupling),
        ],
    )


def initial_state() -> np.ndarray:
    """rho0 = |+>|0><+|<0|, i.e. (|00> + |10>) / sqrt(2)."""
    plus = np.array([1, 1], dtype=complex) / np.sqrt(2)
    zero = np.array([1, 0], dtype=complex)
    psi0 = np.kron(plus, zero)
    return np.outer(psi0, psi0.conj())


def run(
    steps: int = 200,
    dt: float = 0.05,
    omega_1: float = DEFAULT_OMEGA_1,
    omega_2: float = DEFAULT_OMEGA_2,
    coupling: float = DEFAULT_COUPLING,
) -> list[QuantumFrame]:
    hamiltonian = build_generator(omega_1, omega_2, coupling)
    trajectory = evolve_unitary_trajectory(initial_state(), hamiltonian, dt, steps)
    return [
        build_frame(
            t=t,
            dt=dt,
            rho=rho,
            hamiltonian=hamiltonian,
            frame_id=frame_id,
            state_epoch=0,
            basis_id="computational",
            source={"experiment": "von_neumann_flow_i"},
        )
        for frame_id, (t, rho) in enumerate(trajectory)
    ]
