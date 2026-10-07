from __future__ import annotations

import numpy as np

from qmw.manifolds.quantum_matrix_manifold import QuantumMatrixManifold


def test_complex_flatten_roundtrip_is_exact(rng) -> None:
    matrix = rng.normal(size=(16, 16)) + 1j * rng.normal(size=(16, 16))
    buffer = QuantumMatrixManifold.flatten(matrix)
    restored = QuantumMatrixManifold.unflatten(buffer)

    assert buffer.shape == (256,)
    assert np.iscomplexobj(buffer)
    assert np.array_equal(restored, matrix)
    assert buffer[16 * 5 + 11] == matrix[5, 11]


def test_unflatten_rejects_non_256_buffer() -> None:
    try:
        QuantumMatrixManifold.unflatten(np.zeros(255, dtype=np.complex128))
    except ValueError as error:
        assert "256" in str(error)
    else:
        raise AssertionError("invalid buffer length was accepted")

