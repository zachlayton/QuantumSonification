from __future__ import annotations

import numpy as np

from qmw.manifolds.quantum_matrix_manifold import QuantumMatrixManifold


def test_eta_derivative_agrees_with_centered_difference(
    hermitian_matrix, unitary_pair
) -> None:
    manifold = QuantumMatrixManifold(hermitian_matrix, *unitary_pair)
    eta = 0.37
    step = 1e-6
    finite_difference = (
        manifold.matrix_at(eta + step) - manifold.matrix_at(eta - step)
    ) / (2.0 * step)
    np.testing.assert_allclose(
        manifold.derivative_at(eta), finite_difference, atol=3e-8, rtol=3e-8
    )


def test_point_gradient_matches_local_finite_differences(
    hermitian_matrix, unitary_pair
) -> None:
    manifold = QuantumMatrixManifold(hermitian_matrix, *unitary_pair)
    m, n, eta = 5.25, 11.4, 0.37
    gradient = manifold.gradient(m, n, eta)
    step = 1e-6

    dm = (
        manifold.sample(m + step, n, eta) - manifold.sample(m - step, n, eta)
    ) / (2.0 * step)
    dn = (
        manifold.sample(m, n + step, eta) - manifold.sample(m, n - step, eta)
    ) / (2.0 * step)
    de = (
        manifold.sample(m, n, eta + step) - manifold.sample(m, n, eta - step)
    ) / (2.0 * step)
    np.testing.assert_allclose(gradient.as_tuple(), (dm, dn, de), atol=5e-8, rtol=5e-8)

