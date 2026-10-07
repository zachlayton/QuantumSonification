import numpy as np

from qmw_metric.curved_modes import CurvedModeSolver
from qmw_metric.frames import CurvedModeFrame
from qmw_metric.grid import Grid2D
from qmw_metric.mode_tracker import ModeTracker


def test_modes_are_nonnegative_and_metric_orthonormal():
    grid = Grid2D.periodic((12, 12))
    xx, yy = grid.mesh()
    weight = np.exp(0.4 * np.sin(np.pi * xx) * np.cos(np.pi * yy))
    frame = CurvedModeSolver(grid).solve(weight, 6)
    flattened = frame.modes.reshape(6, -1)
    gram = (flattened * (weight.ravel() * grid.cell_area)) @ flattened.T
    assert np.min(frame.eigenvalues) >= 0.0
    assert np.allclose(gram, np.eye(6), atol=1e-9)


def test_flat_spectrum_starts_with_periodic_fundamental():
    grid = Grid2D.periodic((12, 12))
    frame = CurvedModeSolver(grid).solve(np.ones(grid.shape), 4)
    expected = 4.0 * np.sin(np.pi / 12.0) ** 2 / grid.dx**2
    assert np.allclose(frame.eigenvalues, expected, rtol=1e-8)


def test_tracker_corrects_permutation_and_sign():
    grid = Grid2D.periodic((12, 12))
    previous = CurvedModeSolver(grid).solve(np.ones(grid.shape), 4)
    permutation = np.array((2, 0, 3, 1))
    current = CurvedModeFrame(
        time=1.0,
        eigenvalues=previous.eigenvalues[permutation],
        frequencies=previous.frequencies[permutation],
        modes=previous.modes[permutation] * np.array((-1, 1, -1, 1))[:, None, None],
        damping=previous.damping[permutation],
        gains=previous.gains[permutation],
        basis_derivative_overlap=np.zeros((4, 4)),
        metric_rate_overlap=np.zeros((4, 4)),
        intermodal_connection=np.zeros((4, 4)),
    )
    matched = ModeTracker(grid).match(previous, current, np.ones(grid.shape))
    gram = (previous.modes.reshape(4, -1) * grid.cell_area) @ matched.modes.reshape(4, -1).T
    assert np.allclose(np.abs(gram), np.eye(4), atol=1e-8)


def test_time_dependent_mode_terms_preserve_raw_and_antisymmetric_parts():
    grid = Grid2D.periodic((12, 12))
    xx, yy = grid.mesh()
    previous_weight = np.ones(grid.shape)
    current_weight = np.exp(0.02 * np.sin(np.pi * xx) * np.cos(np.pi * yy))
    solver = CurvedModeSolver(grid)
    previous = solver.solve(previous_weight, 5, time=0.0)
    current = solver.solve(current_weight, 5, time=0.1)
    matched = ModeTracker(grid).match(
        previous, current, current_weight, previous_weight
    )
    derivative = (matched.modes - previous.modes).reshape(5, -1) / 0.1
    current_flat = matched.modes.reshape(5, -1)
    raw_expected = (
        current_flat * (current_weight.ravel() * grid.cell_area)
    ) @ derivative.T
    weight_rate = (current_weight - previous_weight).ravel() / 0.1
    metric_rate_expected = (
        current_flat * (weight_rate * grid.cell_area)
    ) @ current_flat.T
    assert np.allclose(matched.basis_derivative_overlap, raw_expected)
    assert np.allclose(matched.metric_rate_overlap, metric_rate_expected)
    assert np.allclose(
        matched.intermodal_connection,
        0.5 * (raw_expected - raw_expected.T),
    )
    assert np.allclose(
        matched.intermodal_connection,
        -matched.intermodal_connection.T,
        atol=1e-12,
    )


def test_unchanged_aligned_modes_have_zero_connection():
    grid = Grid2D.periodic((12, 12))
    previous = CurvedModeSolver(grid).solve(np.ones(grid.shape), 4, time=0.0)
    current = CurvedModeFrame(
        time=0.2,
        eigenvalues=previous.eigenvalues,
        frequencies=previous.frequencies,
        modes=previous.modes,
        damping=previous.damping,
        gains=previous.gains,
        basis_derivative_overlap=np.zeros((4, 4)),
        metric_rate_overlap=np.zeros((4, 4)),
        intermodal_connection=np.zeros((4, 4)),
    )
    matched = ModeTracker(grid).match(previous, current, np.ones(grid.shape))
    assert np.allclose(matched.basis_derivative_overlap, 0.0, atol=1e-12)
    assert np.allclose(matched.metric_rate_overlap, 0.0, atol=1e-12)
    assert np.allclose(matched.intermodal_connection, 0.0, atol=1e-12)
