import numpy as np
import pytest

from qmw_metric.grid import Grid2D
from qmw_metric.quantum_projector import QuantumSpatialProjector, localized_gaussian_basis


def setup_projector():
    grid = Grid2D.periodic((16, 16))
    basis = localized_gaussian_basis(grid, 16)
    return grid, basis, QuantumSpatialProjector(basis, grid)


def test_trace_one_state_produces_normalized_nonnegative_density():
    grid, basis, projector = setup_projector()
    rho = np.eye(16, dtype=np.complex128) / 16.0
    density = projector.density(rho)
    expected = np.sum(np.abs(basis) ** 2, axis=0) / 16.0
    assert np.min(density) >= 0.0
    assert np.sum(density) * grid.cell_area == pytest.approx(1.0, abs=1e-12)
    assert np.allclose(density, expected)


def test_localized_projection_sites_are_metric_orthonormal():
    grid, basis, _ = setup_projector()
    flat = basis.reshape(16, -1)
    gram = (flat @ flat.conj().T) * grid.cell_area
    assert np.allclose(gram, np.eye(16), atol=1e-10)


def test_coherence_changes_spatial_interference():
    _, _, projector = setup_projector()
    incoherent = np.zeros((16, 16), dtype=np.complex128)
    incoherent[0, 0] = incoherent[1, 1] = 0.5
    psi = np.zeros(16, dtype=np.complex128)
    psi[:2] = 1.0 / np.sqrt(2.0)
    coherent = np.outer(psi, psi.conj())
    assert not np.allclose(projector.density(incoherent), projector.density(coherent))


def test_invalid_density_matrix_is_rejected():
    _, _, projector = setup_projector()
    rho = np.eye(16, dtype=np.complex128) / 16.0
    rho[0, 1] = 0.2
    with pytest.raises(ValueError, match="Hermitian"):
        projector.density(rho)
