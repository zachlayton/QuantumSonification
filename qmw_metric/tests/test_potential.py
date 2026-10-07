import numpy as np

from qmw_metric.config import PotentialConfig
from qmw_metric.grid import Grid2D
from qmw_metric.potential_solver import ScreenedPoissonSolver


def test_screened_poisson_residual_is_small_and_well_is_negative():
    grid = Grid2D.periodic((32, 32))
    xx, yy = grid.mesh()
    density = np.exp(-(xx**2 + yy**2) / 0.08)
    density /= density.sum() * grid.cell_area
    solver = ScreenedPoissonSolver(grid, PotentialConfig(screening_length=0.3))
    potential = solver.solve(density)
    residual = solver.residual(density, potential)
    assert np.max(np.abs(residual)) < 1e-10
    assert potential[0, 0] > potential[16, 16]
    assert abs(potential.mean()) < 1e-12


def test_centered_source_gives_symmetric_well():
    grid = Grid2D.periodic((32, 32))
    density = np.zeros(grid.shape)
    density[16, 16] = 1.0 / grid.cell_area
    potential = ScreenedPoissonSolver(grid).solve(density)
    assert np.allclose(potential[16, 15], potential[16, 17])
    assert np.allclose(potential[15, 16], potential[17, 16])
