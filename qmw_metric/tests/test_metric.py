import numpy as np
import pytest
from dataclasses import replace

from qmw_metric.config import MetricConfig
from qmw_metric.grid import Grid2D
from qmw_metric.metric_field import QuantumMetricField
from qmw_metric.engine import QuantumMetricEngine
from qmw_metric.config import QuantumMetricConfig


def test_metric_is_positive_finite_and_bounded():
    grid = Grid2D.periodic((16, 16))
    xx, yy = grid.mesh()
    metric = QuantumMetricField(grid, MetricConfig(spatial_strength=4.0, sigma_limit=0.7))
    result = metric.construct(np.sin(np.pi * xx) * np.cos(np.pi * yy))
    assert np.all(np.isfinite(result["sqrt_g"]))
    assert np.min(result["sqrt_g"]) > 0.0
    point_metrics = np.moveaxis(result["metric"], (0, 1), (-2, -1))
    assert np.min(np.linalg.eigvalsh(point_metrics)) > 0.0
    assert np.min(result["lapse"]) > 0.0
    assert np.max(np.abs(result["sigma"])) <= 0.7
    assert np.allclose(result["sqrt_g"] * result["inverse_metric_factor"], 1.0)


def test_flat_potential_produces_flat_metric_and_zero_curvature():
    grid = Grid2D.periodic((16, 16))
    result = QuantumMetricField(grid).construct(np.zeros(grid.shape))
    assert np.allclose(result["sigma"], 0.0)
    assert np.allclose(result["sqrt_g"], 1.0)
    assert np.allclose(result["lapse"], 1.0)
    assert np.allclose(result["curvature"], 0.0)


def test_direct_sigma_lapse_and_tensor_contract():
    grid = Grid2D.periodic((20, 24))
    xx, yy = grid.mesh()
    potential = 0.02 * np.sin(np.pi * xx) * np.cos(2.0 * np.pi * yy)
    config = MetricConfig(
        spatial_strength=3.0,
        lapse_strength=-2.0,
        sigma_limit=2.0,
        lapse_exponent_limit=2.0,
    )
    result = QuantumMetricField(grid, config).construct(potential)
    assert np.allclose(result["sigma"], 3.0 * potential)
    assert np.allclose(result["lapse"], np.exp(-2.0 * potential))
    identity = np.einsum(
        "ijyx,jkyx->ikyx", result["metric"], result["inverse_metric"]
    )
    expected = np.zeros_like(identity)
    expected[0, 0] = expected[1, 1] = 1.0
    assert np.allclose(identity, expected)
    assert np.allclose(result["determinant"], result["sqrt_g"] ** 2)


def test_hessian_laplacian_and_christoffel_are_consistent():
    grid = Grid2D.periodic((24, 24))
    xx, yy = grid.mesh()
    potential = 0.01 * (np.sin(np.pi * xx) + np.cos(np.pi * yy))
    result = QuantumMetricField(
        grid, MetricConfig(spatial_strength=2.5, sigma_limit=2.0)
    ).construct(potential)
    assert np.allclose(result["hessian"][0, 1], result["hessian"][1, 0])
    assert np.allclose(
        result["hessian"][0, 0] + result["hessian"][1, 1],
        result["potential_laplacian"],
    )
    grad = result["grad_sigma"]
    # Gamma^x_xx = d_x sigma; Gamma^x_yy = -d_x sigma;
    # Gamma^y_xy = d_x sigma for a conformal two-dimensional metric.
    assert np.allclose(result["christoffel"][0, 0, 0], grad[0])
    assert np.allclose(result["christoffel"][0, 1, 1], -grad[0])
    assert np.allclose(result["christoffel"][1, 0, 1], grad[0])


def test_exponential_arguments_are_clamped_before_metric_construction():
    grid = Grid2D.periodic((8, 8))
    potential = np.full(grid.shape, 100.0)
    result = QuantumMetricField(
        grid,
        MetricConfig(
            spatial_strength=10.0,
            lapse_strength=10.0,
            sigma_limit=0.6,
            lapse_exponent_limit=0.4,
        ),
    ).construct(potential)
    assert np.max(result["sigma"]) == pytest.approx(0.6)
    assert np.max(result["lapse"]) == pytest.approx(np.exp(0.4))


def test_metric_frame_rejects_non_positive_definite_tensor():
    observer = QuantumMetricEngine(
        QuantumMetricConfig(grid_size=(12, 12), mode_count=4)
    )
    rho = np.eye(16, dtype=np.complex128) / 16.0
    field = observer.update_quantum_frame(rho, time=0.0)
    invalid_metric = field.metric.copy()
    invalid_inverse = field.inverse_metric.copy()
    invalid_metric[0, 0] *= -1.0
    invalid_inverse[0, 0] *= -1.0
    with pytest.raises(ValueError, match="positive definite"):
        replace(field, metric=invalid_metric, inverse_metric=invalid_inverse)
