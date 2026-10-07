from __future__ import annotations

import numpy as np

from qmw.manifolds.interpolation_types import InterpolationType
from qmw.manifolds.quantum_matrix_manifold import QuantumMatrixManifold


def test_expected_basis_endpoint_representations(
    hermitian_matrix, unitary_pair
) -> None:
    source, target = unitary_pair
    manifold = QuantumMatrixManifold(hermitian_matrix, source, target)

    np.testing.assert_allclose(
        manifold.matrix_at(0.0),
        source.conj().T @ hermitian_matrix @ source,
        atol=2e-10,
    )
    np.testing.assert_allclose(
        manifold.matrix_at(1.0),
        target.conj().T @ hermitian_matrix @ target,
        atol=2e-10,
    )


def test_hermiticity_trace_and_spectrum_are_preserved(
    hermitian_matrix, unitary_pair
) -> None:
    source, target = unitary_pair
    manifold = QuantumMatrixManifold(hermitian_matrix, source, target)
    expected_eigenvalues = np.linalg.eigvalsh(hermitian_matrix)

    for eta in np.linspace(0.0, 1.0, 9):
        matrix = manifold.matrix_at(float(eta))
        np.testing.assert_allclose(matrix, matrix.conj().T, atol=2e-10)
        np.testing.assert_allclose(np.trace(matrix), np.trace(hermitian_matrix), atol=2e-10)
        np.testing.assert_allclose(
            np.linalg.eigvalsh(matrix), expected_eigenvalues, atol=2e-10
        )


def test_interpolation_operations_have_explicitly_distinct_semantics(
    hermitian_matrix, unitary_pair
) -> None:
    source_basis, target_basis = unitary_pair
    target_state = hermitian_matrix + np.eye(16)

    state_path = QuantumMatrixManifold.from_state_endpoints(
        hermitian_matrix, target_state
    )
    eigenvalue_path = QuantumMatrixManifold.from_eigenvalue_endpoints(
        np.arange(16, dtype=float),
        np.arange(16, dtype=float) + 2.0,
        source_basis,
    )
    eigenvector_path = QuantumMatrixManifold.from_eigenvector_path(
        np.arange(16, dtype=float), source_basis, target_basis
    )

    assert state_path.interpolation_type is InterpolationType.STATE
    assert eigenvalue_path.interpolation_type is InterpolationType.EIGENVALUES
    assert eigenvector_path.interpolation_type is InterpolationType.EIGENVECTORS
    np.testing.assert_allclose(
        state_path.matrix_at(0.25), 0.75 * hermitian_matrix + 0.25 * target_state
    )
    np.testing.assert_allclose(
        np.linalg.eigvalsh(eigenvalue_path.matrix_at(0.5)),
        np.arange(16, dtype=float) + 1.0,
        atol=2e-10,
    )
    np.testing.assert_allclose(
        np.linalg.eigvalsh(eigenvector_path.matrix_at(0.61)),
        np.arange(16, dtype=float),
        atol=2e-10,
    )


def test_frame_is_fixed_four_qubit_shape(hermitian_matrix, unitary_pair) -> None:
    manifold = QuantumMatrixManifold(hermitian_matrix, *unitary_pair)
    frame = manifold.frame_at(0.37)
    assert frame.matrix.shape == (16, 16)
    assert frame.buffer_256.shape == (256,)
    assert frame.gradient_m.shape == (16, 16)
    assert frame.gradient_n.shape == (16, 16)
    assert frame.gradient_eta.shape == (16, 16)
    assert frame.diagnostics["buffer_size"] == 256

