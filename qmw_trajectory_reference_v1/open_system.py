"""Declared GKSL pure-dephasing reference for the four-qubit XY chain."""
from __future__ import annotations
import numpy as np
from scipy.sparse.linalg import expm_multiply
from .xy import FourQubitXYModel, QuantumTrajectory

def run_xy_dephasing_trajectory(*, gamma_phi: float, samples: int = 2048, duration: float = 24.0, model: FourQubitXYModel | None = None) -> QuantumTrajectory:
    """Solve dot(rho)=-i[H,rho]+gamma sum_i(Z_i rho Z_i-rho), hbar=1."""
    if not np.isfinite(gamma_phi) or gamma_phi < 0.0:
        raise ValueError("gamma_phi must be finite and nonnegative.")
    selected = model or FourQubitXYModel()
    if int(samples) != samples or samples < 2 or not np.isfinite(duration) or duration <= 0.0:
        raise ValueError("samples must be >=2 and duration must be positive.")
    hamiltonian = selected.hamiltonian
    dimension = selected.dimension
    identity = np.eye(dimension, dtype=complex)
    generator = -1j / selected.hbar * (np.kron(identity, hamiltonian) - np.kron(hamiltonian.T, identity))
    for number in selected.site_number_operators:
        z = identity - 2.0 * number
        generator += gamma_phi * (np.kron(z.T, z) - np.eye(dimension * dimension, dtype=complex))
    time = np.linspace(0.0, duration, int(samples))
    rho0 = np.outer(selected.initial_state, selected.initial_state.conj()).reshape(-1, order="F")
    rho = expm_multiply(generator, rho0, start=0.0, stop=duration, num=int(samples)).reshape((int(samples), dimension, dimension), order="F")
    rho = (rho + rho.swapaxes(1, 2).conj()) * 0.5
    populations = np.stack([np.real(np.einsum("tij,ji->t", rho, operator)) for operator in selected.site_number_operators], axis=1)
    currents = []
    for bond, number_left in zip(selected.bond_hamiltonians, selected.site_number_operators):
        derivative = -1j / selected.hbar * (bond @ rho - rho @ bond)
        currents.append(-np.real(np.einsum("tij,ji->t", derivative, number_left)))
    return QuantumTrajectory(time=time, state=None, rho=rho, site_populations=populations,
        edge_current_left_to_right=np.stack(currents, axis=1), hamiltonian=hamiltonian, model=selected,
        metadata={"backend": "numpy_gksl_expm_multiply", "channel": "local_pure_dephasing", "gamma_phi": float(gamma_phi)})
