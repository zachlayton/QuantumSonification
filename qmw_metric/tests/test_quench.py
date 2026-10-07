import numpy as np

from qmw_metric.curved_modes import CurvedModeSolver
from qmw_metric.grid import Grid2D
from qmw_metric.quench import GeometryQuenchEngine


def test_identity_quench_preserves_modal_amplitudes():
    grid = Grid2D.periodic((12, 12))
    frame = CurvedModeSolver(grid).solve(np.ones(grid.shape), 5)
    amplitudes = np.linspace(-1.0, 1.0, 5)
    transferred = GeometryQuenchEngine(grid).transfer_energy(
        amplitudes, frame, frame, np.ones(grid.shape)
    )
    assert np.allclose(transferred, amplitudes, atol=1e-9)
