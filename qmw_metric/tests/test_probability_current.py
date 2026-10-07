import numpy as np

from qmw_metric.grid import Grid2D
from qmw_metric.probability_current import ProbabilityCurrentProjector
from qmw_metric.quantum_projector import QuantumSpatialProjector, localized_gaussian_basis


def test_real_incoherent_state_has_zero_current():
    grid = Grid2D.periodic((16, 16))
    basis = localized_gaussian_basis(grid, 16)
    rho = np.eye(16, dtype=np.complex128) / 16.0
    density = QuantumSpatialProjector(basis, grid).density(rho)
    current, velocity, vorticity = ProbabilityCurrentProjector(basis, grid).current(rho, density)
    assert np.allclose(current, 0.0)
    assert np.allclose(velocity, 0.0)
    assert np.allclose(vorticity, 0.0)


def test_imaginary_coherence_can_create_current():
    grid = Grid2D.periodic((16, 16))
    basis = localized_gaussian_basis(grid, 16)
    psi = np.zeros(16, dtype=np.complex128)
    psi[5], psi[6] = 1.0 / np.sqrt(2.0), 1j / np.sqrt(2.0)
    rho = np.outer(psi, psi.conj())
    density = QuantumSpatialProjector(basis, grid).density(rho)
    current, _, _ = ProbabilityCurrentProjector(basis, grid).current(rho, density)
    assert np.max(np.abs(current)) > 1e-6
