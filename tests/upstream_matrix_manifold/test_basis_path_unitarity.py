from __future__ import annotations

import numpy as np

from qmw.manifolds.basis_path import BasisPath


def test_basis_path_endpoints_and_unitarity(unitary_pair) -> None:
    source, target = unitary_pair
    path = BasisPath(source, target)

    np.testing.assert_allclose(path.unitary_at(0.0), source, atol=0.0, rtol=0.0)
    np.testing.assert_allclose(path.unitary_at(1.0), target, atol=0.0, rtol=0.0)
    for eta in np.linspace(0.0, 1.0, 17):
        unitary = path.unitary_at(float(eta))
        np.testing.assert_allclose(
            unitary.conj().T @ unitary, np.eye(16), atol=2e-10, rtol=2e-10
        )
    assert path.diagnostics.endpoint_error < 1e-8


def test_negative_one_branch_is_reported_and_deterministic() -> None:
    source = np.eye(16, dtype=np.complex128)
    target = np.eye(16, dtype=np.complex128)
    target[0, 0] = -1.0
    path = BasisPath(source, target)

    assert path.diagnostics.near_branch_cut_count == 1
    assert np.isclose(np.max(path.principal_phases), np.pi)
    np.testing.assert_allclose(path.unitary_at(0.5)[0, 0], 1j, atol=1e-12)


def test_explicit_branch_shift_changes_path_but_not_endpoints() -> None:
    source = np.eye(16, dtype=np.complex128)
    phases = np.linspace(-0.8, 0.9, 16)
    target = np.diag(np.exp(1j * phases))
    principal = BasisPath(source, target)
    shifted = BasisPath(source, target, branch_shifts=[1] + [0] * 15)

    np.testing.assert_allclose(shifted.unitary_at(1.0), target, atol=0.0, rtol=0.0)
    assert not np.allclose(principal.unitary_at(0.5), shifted.unitary_at(0.5))
    assert "integer_shifts" in shifted.diagnostics.branch_convention


def test_degenerate_negative_one_subspace_closes_at_target(rng) -> None:
    raw = rng.normal(size=(16, 16)) + 1j * rng.normal(size=(16, 16))
    vectors, _ = np.linalg.qr(raw)
    phases = np.linspace(-1.1, 1.2, 16)
    phases[:3] = np.pi
    target = vectors @ np.diag(np.exp(1j * phases)) @ vectors.conj().T
    path = BasisPath(np.eye(16, dtype=np.complex128), target)

    assert path.diagnostics.near_branch_cut_count == 3
    assert path.diagnostics.endpoint_error < 1e-8
    for eta in (0.23, 0.59, 0.91):
        unitary = path.unitary_at(eta)
        np.testing.assert_allclose(unitary.conj().T @ unitary, np.eye(16), atol=2e-10)


def test_nonunitary_basis_is_rejected() -> None:
    source = np.eye(16, dtype=np.complex128)
    target = source.copy()
    target[0, 0] = 0.5
    try:
        BasisPath(source, target)
    except ValueError as error:
        assert "not unitary" in str(error)
    else:
        raise AssertionError("nonunitary target was accepted")
