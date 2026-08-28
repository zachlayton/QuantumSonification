"""Regression tests for the Von Neumann Flow I experiment and the spine kernel it exercises.

These encode the invariant table from the spec: trace/hermiticity/positivity
and global purity must hold at every frame; energy and <ZZ> must be conserved
because [H, ZZ] == 0; the commutator norm must stay constant for this closed,
time-independent generator; local purity must actually move (entanglement
developing through the XX coupling); and the exact discrete continuity
equation (J_{i<-j}) and the Pauli-velocity field must both agree with direct
numerical checks, independent of the analytic derivation.
"""
from __future__ import annotations

import numpy as np
import pytest

from qmw.spine.experiments.von_neumann_flow_i import build_generator, initial_state, run
from qmw.spine.flow.basis_flow import basis_current, populations, region_flux
from qmw.spine.frame import build_frame
from qmw.spine.observables.reduced import local_purity
from qmw.spine.quantum.evolution import evolve_unitary_step
from qmw.spine.quantum.pauli import all_pauli_labels, decompose

STEPS = 200
DT = 0.05


@pytest.fixture(scope="module")
def frames():
    return run(steps=STEPS, dt=DT)


def test_state_invariants_hold_across_trajectory(frames):
    for frame in frames:
        d = frame.diagnostics
        assert abs(d.trace - 1.0) < 1e-8
        assert d.is_hermitian
        assert d.is_positive_semidefinite


def test_global_purity_is_conserved(frames):
    purities = np.array([frame.purity for frame in frames])
    assert np.allclose(purities, 1.0, atol=1e-7)


def test_energy_is_conserved(frames):
    energies = np.array([frame.energy for frame in frames])
    assert np.allclose(energies, energies[0], atol=1e-6)


def test_commutator_norm_is_constant(frames):
    norms = np.array([frame.commutator_norm for frame in frames])
    assert np.allclose(norms, norms[0], atol=1e-6)
    assert norms[0] > 0.0


def test_zz_is_conserved(frames):
    zz_values = np.array([frame.pauli["ZZ"] for frame in frames])
    zz_velocities = np.array([frame.pauli_velocity["ZZ"] for frame in frames])
    assert np.allclose(zz_values, zz_values[0], atol=1e-6)
    assert np.allclose(zz_velocities, 0.0, atol=1e-6)


def test_local_purity_develops_and_is_not_constant(frames):
    local_purities = np.array(
        [local_purity(frame.rho, qubit=0, n_qubits=2) for frame in frames]
    )
    assert local_purities[0] > 1 - 1e-9
    assert local_purities.min() < 0.999


def test_basis_current_satisfies_discrete_continuity(frames):
    frame = frames[len(frames) // 2]
    H, rho = frame.hamiltonian_matrix, frame.rho
    J = basis_current(H, rho)

    assert np.allclose(J, -J.T, atol=1e-9)
    assert np.allclose(np.diag(J), 0.0, atol=1e-9)

    dot_p = np.real(np.diag(frame.rho_dot_unitary))
    assert np.allclose(J.sum(axis=1), dot_p, atol=1e-9)

    region = (0, 1)
    other = tuple(i for i in range(J.shape[0]) if i not in region)
    dot_n_region = sum(dot_p[i] for i in region)
    assert np.isclose(dot_n_region, -region_flux(J, region), atol=1e-9)
    dot_n_other = sum(dot_p[i] for i in other)
    assert np.isclose(dot_n_region, -dot_n_other, atol=1e-9)


def test_pauli_velocity_matches_finite_difference():
    hamiltonian = build_generator()
    dt = 1e-5
    trajectory = [(0.0, initial_state())]
    rho = trajectory[0][1]
    for _ in range(2):
        rho = evolve_unitary_step(rho, hamiltonian.matrix(0.0), dt)
        trajectory.append((trajectory[-1][0] + dt, rho))

    labels = ("XI", "IX", "XX", "ZZ", "ZI")
    frame_mid = build_frame(
        t=trajectory[1][0],
        dt=dt,
        rho=trajectory[1][1],
        hamiltonian=hamiltonian,
        frame_id=1,
        state_epoch=0,
        pauli_labels=all_pauli_labels(2),
    )

    p_minus = decompose(trajectory[0][1], labels)
    p_plus = decompose(trajectory[2][1], labels)
    for label in labels:
        finite_difference = (p_plus[label] - p_minus[label]) / (2 * dt)
        assert np.isclose(finite_difference, frame_mid.pauli_velocity[label], atol=1e-6)


def test_basis_populations_sum_to_one(frames):
    for frame in frames:
        assert np.isclose(populations(frame.rho).sum(), 1.0, atol=1e-8)
