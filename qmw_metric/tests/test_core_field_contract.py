"""Acceptance tests for the complete Quantum Metric Field core contract."""

import numpy as np

from qmw_metric.config import MetricConfig, PotentialConfig, QuantumMetricConfig
from qmw_metric.engine import QuantumMetricEngine
from qmw_metric.grid import Grid2D
from qmw_metric.metric_field import QuantumMetricField
from qmw_metric.potential_solver import ScreenedPoissonSolver


def test_poisson_coupling_survives_direct_phi_to_sigma_mapping():
    grid = Grid2D.periodic((16, 16))
    density = np.zeros(grid.shape)
    density[4, 6] = 1.0 / grid.cell_area
    phi_one = ScreenedPoissonSolver(
        grid, PotentialConfig(coupling=1.0)
    ).solve(density)
    phi_two = ScreenedPoissonSolver(
        grid, PotentialConfig(coupling=2.0)
    ).solve(density)
    metric = QuantumMetricField(
        grid,
        MetricConfig(
            spatial_strength=0.1,
            lapse_strength=0.05,
            sigma_limit=10.0,
            lapse_exponent_limit=10.0,
        ),
    )
    fields_one = metric.construct(phi_one)
    fields_two = metric.construct(phi_two)
    assert np.allclose(phi_two, 2.0 * phi_one)
    assert np.allclose(fields_two["sigma"], 2.0 * fields_one["sigma"])


def test_lapse_and_complete_differential_geometry_are_published():
    grid = Grid2D.periodic((12, 14))
    xx, yy = grid.mesh()
    potential = 0.01 * np.sin(np.pi * xx) * np.cos(np.pi * yy)
    fields = QuantumMetricField(
        grid, MetricConfig(spatial_strength=3.0, lapse_strength=2.0)
    ).construct(potential)
    assert np.allclose(fields["sigma"], 3.0 * potential)
    assert np.allclose(fields["lapse"], np.exp(2.0 * potential))
    assert fields["grad_potential"].shape == (2, *grid.shape)
    assert fields["hessian"].shape == (2, 2, *grid.shape)
    assert fields["potential_laplacian"].shape == grid.shape
    assert fields["metric"].shape == (2, 2, *grid.shape)
    assert fields["inverse_metric"].shape == (2, 2, *grid.shape)
    assert fields["determinant"].shape == grid.shape
    assert fields["curvature"].shape == grid.shape
    assert fields["christoffel"].shape == (2, 2, 2, *grid.shape)


def test_qmw_metric_frame_revision_locks_all_observer_layers():
    engine = QuantumMetricEngine(
        QuantumMetricConfig(grid_size=(12, 12), mode_count=4)
    )
    rho = np.eye(16, dtype=np.complex128) / 16.0
    engine.update_quantum_frame(rho, time=1.0, source_revision=23)
    engine.process_control_step(0.002)
    frame = engine.system_frame
    assert frame is not None
    assert frame.source_revision == frame.shader.source_revision == 23
    assert frame.revision == frame.shader.revision
    assert frame.time == frame.shader.time == frame.trajectory.time
    assert frame.field is engine.field_frame
    assert frame.modes is engine.mode_frame
    assert frame.trajectory is engine.trajectory_frame
    assert np.array_equal(frame.shader.potential, frame.field.potential)
    assert np.array_equal(frame.shader.mode_shapes, frame.modes.modes)
    assert np.array_equal(
        frame.shader.trajectory_positions[-1], frame.trajectory.position
    )
