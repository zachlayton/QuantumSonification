"""Observable reduction from a Pauli spinor to AtomicOrbitalFrame."""

from __future__ import annotations

import numpy as np

from .model import AtomicManifoldModel, pauli_matrices
from .schema import AtomicOrbitalFrame
from .states import AtomicState


def _expectation(state: np.ndarray, operator: np.ndarray) -> float:
    return float(np.real_if_close(np.vdot(state, operator @ state)).real)


def observe_state(
    state: AtomicState, model: AtomicManifoldModel, *, time: float = 0.0
) -> AtomicOrbitalFrame:
    """Measure the backend-independent observables used by later adapters."""

    vector = state.validated(model).amplitudes
    coefficients = vector.reshape(model.orbital_dimension, 2)
    rho = np.outer(vector, vector.conj())
    orbital_rho = coefficients @ coefficients.conj().T
    spin_rho = coefficients.T @ coefficients.conj()
    pauli = np.asarray(
        [np.trace(spin_rho @ sigma).real for sigma in pauli_matrices()], dtype=float
    )
    mean_l = np.asarray(
        [_expectation(vector, model.operators[f"L{axis}"]) for axis in "xyz"]
    )
    mean_s = np.asarray(
        [_expectation(vector, model.operators[f"S{axis}"]) for axis in "xyz"]
    )
    mean_j = np.asarray(
        [_expectation(vector, model.operators[f"J{axis}"]) for axis in "xyz"]
    )
    mean_energy = _expectation(vector, model.hamiltonian)
    energy_second = _expectation(vector, model.hamiltonian @ model.hamiltonian)
    spin_eigenvalues = np.clip(np.linalg.eigvalsh(spin_rho).real, 0.0, 1.0)
    nonzero = spin_eigenvalues[spin_eigenvalues > 1e-15]
    entropy = float(-np.sum(nonzero * np.log2(nonzero)))
    return AtomicOrbitalFrame(
        time=float(time),
        n=model.spec.n,
        ell=model.spec.ell,
        basis_labels=model.basis_labels,
        coefficients=vector.copy(),
        orbital_populations=np.diag(orbital_rho).real.copy(),
        spin_populations=np.diag(spin_rho).real.copy(),
        pauli_vector=pauli,
        mean_l=mean_l,
        mean_s=mean_s,
        mean_j=mean_j,
        mean_l_dot_s=_expectation(vector, model.operators["LdotS"]),
        mean_energy=mean_energy,
        energy_variance=max(0.0, energy_second - mean_energy * mean_energy),
        purity=float(np.trace(rho @ rho).real),
        spin_purity=float(np.trace(spin_rho @ spin_rho).real),
        spin_orbital_entanglement_entropy=entropy,
        rho=rho,
        orbital_rho=orbital_rho,
        spin_rho=spin_rho,
        metadata={
            "manifold": "fixed_n_ell",
            "basis_order": "m_l_ascending_then_spin_up_down",
            "atomic_units": True,
            "hbar": float(model.spec.hbar),
            "spinor_components": ["up", "down"],
        },
    )


__all__ = ["observe_state"]
