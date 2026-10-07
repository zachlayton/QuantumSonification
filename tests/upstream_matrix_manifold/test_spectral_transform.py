from __future__ import annotations

import numpy as np

from qmw.manifolds.quantum_matrix_manifold import QuantumMatrixManifold
from qmw.transforms.manifold_spectral_transform import SpectralTransformType


def test_fft_and_qft_views_do_not_mutate_manifold(
    hermitian_matrix, unitary_pair
) -> None:
    manifold = QuantumMatrixManifold(hermitian_matrix, *unitary_pair)
    before = manifold.matrix_at(0.37)
    fft_view = manifold.spectrum_at(0.37, SpectralTransformType.FFT2)
    qft_view = manifold.spectrum_at(0.37, SpectralTransformType.QFT_BASIS)
    after = manifold.matrix_at(0.37)

    assert fft_view.shape == (16, 16)
    assert qft_view.shape == (16, 16)
    assert np.array_equal(before, after)
    np.testing.assert_allclose(
        np.linalg.eigvalsh(qft_view), np.linalg.eigvalsh(before), atol=2e-10
    )


def test_orthonormal_fft_preserves_frobenius_norm(
    hermitian_matrix, unitary_pair
) -> None:
    manifold = QuantumMatrixManifold(hermitian_matrix, *unitary_pair)
    matrix = manifold.matrix_at(0.52)
    spectrum = manifold.spectrum_at(0.52)
    np.testing.assert_allclose(np.linalg.norm(spectrum), np.linalg.norm(matrix), atol=2e-10)

