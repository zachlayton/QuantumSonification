from __future__ import annotations

import numpy as np

from qmw.manifolds.quantum_matrix_manifold import QuantumMatrixManifold
from qmw.transforms.manifold_spectral_transform import qft_matrix


def discrete_qho_basis(dimension: int = 16) -> np.ndarray:
    """Finite oscillator eigenbasis used only as a mathematical fixture."""
    x = np.linspace(-4.0, 4.0, dimension)
    dx = x[1] - x[0]
    laplacian = (
        np.diag(-2.0 * np.ones(dimension))
        + np.diag(np.ones(dimension - 1), 1)
        + np.diag(np.ones(dimension - 1), -1)
    ) / dx**2
    hamiltonian = -0.5 * laplacian + 0.5 * np.diag(x**2)
    _, eigenvectors = np.linalg.eigh(hamiltonian)
    return eigenvectors.astype(np.complex128)


def test_qho_to_qft_basis_path_is_unitary_and_spectral(rng) -> None:
    qho = discrete_qho_basis()
    qft = qft_matrix(16)
    raw = rng.normal(size=(16, 16)) + 1j * rng.normal(size=(16, 16))
    operator = 0.5 * (raw + raw.conj().T)
    manifold = QuantumMatrixManifold(
        operator,
        source_basis=qho,
        target_basis=qft,
        source_basis_name="qho",
        target_basis_name="qft",
    )

    np.testing.assert_allclose(
        manifold.matrix_at(0.0), qho.conj().T @ operator @ qho, atol=2e-10
    )
    np.testing.assert_allclose(
        manifold.matrix_at(1.0), qft.conj().T @ operator @ qft, atol=2e-10
    )
    for eta in (0.17, 0.37, 0.83):
        unitary = manifold.basis_path.unitary_at(eta)
        np.testing.assert_allclose(unitary.conj().T @ unitary, np.eye(16), atol=2e-10)
        np.testing.assert_allclose(
            np.linalg.eigvalsh(manifold.matrix_at(eta)),
            np.linalg.eigvalsh(operator),
            atol=2e-10,
        )

