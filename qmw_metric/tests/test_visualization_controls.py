from pathlib import Path

import numpy as np
import pytest

from qmw_metric import (
    OVERLAY_IDS,
    QuantumMetricConfig,
    QuantumMetricEngine,
    analysis_visualization_controls,
    performance_visualization_controls,
)


def test_overlay_inventory_is_complete_and_independent():
    assert OVERLAY_IDS == (
        "density", "potential", "contours", "spatial_metric", "lapse",
        "curvature", "hessian_principal", "probability_current", "vorticity",
        "eigenmodes", "trajectory",
    )
    controls = analysis_visualization_controls()
    changed = controls.with_overlay("curvature", enabled=True, opacity=0.31)
    assert changed.overlays["curvature"].enabled
    assert changed.overlays["curvature"].opacity == pytest.approx(0.31)
    assert controls.overlays["curvature"].enabled is False
    for name in set(OVERLAY_IDS) - {"curvature"}:
        assert changed.overlays[name] == controls.overlays[name]


def test_analysis_and_performance_are_explicit_view_presets_only():
    analysis = analysis_visualization_controls()
    performance = performance_visualization_controls()
    assert analysis.mode == "analysis"
    assert performance.mode == "performance"
    assert tuple(analysis.overlays) == tuple(performance.overlays) == OVERLAY_IDS
    assert performance.overlays["probability_current"].enabled
    assert analysis.overlays["spatial_metric"].enabled
    with pytest.raises(ValueError, match="opacity"):
        analysis.with_overlay("density", opacity=1.01)
    with pytest.raises(KeyError, match="unknown"):
        analysis.with_overlay("not_a_field", enabled=True)


def test_shader_frame_publishes_authoritative_overlay_tensors():
    engine = QuantumMetricEngine(QuantumMetricConfig(grid_size=(12, 12), mode_count=4))
    rho = np.eye(16, dtype=np.complex128) / 16.0
    engine.update_quantum_frame(rho, 0.0, source_revision=9)
    shader = engine.system_frame.shader
    field = engine.system_frame.field
    assert np.array_equal(shader.metric, field.metric)
    assert np.array_equal(shader.inverse_metric, field.inverse_metric)
    assert np.array_equal(shader.determinant, field.determinant)
    assert np.array_equal(shader.grad_potential, field.grad_potential)
    assert np.array_equal(shader.hessian, field.hessian)
    assert np.array_equal(shader.probability_current, field.current)
    assert np.array_equal(shader.phase_connection, field.flow_velocity)
    for name in (
        "metric_00", "inverse_metric_11", "hessian_01", "grad_potential_x",
        "current_y", "phase_connection_x",
    ):
        assert name in engine.shader.textures


def test_browser_visualizer_exposes_every_overlay_control():
    assets = Path(__file__).parents[1] / "visualizer"
    html = (assets / "index.html").read_text(encoding="utf-8")
    javascript = (assets / "app.js").read_text(encoding="utf-8")
    assert 'id="analysisPreset"' in html
    assert 'id="performancePreset"' in html
    for overlay_id in OVERLAY_IDS:
        assert overlay_id in javascript
    assert "trajectory_positions" in javascript
    assert "phase_connection" in javascript
    assert "probability_current" in javascript
    for visual_primitive in (
        "LineDashedMaterial", "addSourceCores", "addOrbitalRings",
        "addCriticalLabels", "addLandscapeGrid", "crossing",
    ):
        assert visual_primitive in javascript
    for animation_contract in (
        "blendScene", "updateSurface", "updateFlowTracers",
        "liveAnimation.duration", "orbit.userData.orbitRate",
        "scene.lapse[y][x]", "positions.needsUpdate = true",
    ):
        assert animation_contract in javascript
    assert "now - liveAnimation.lastAuxiliary >= 100" in javascript


def test_shader_trajectory_history_is_bounded_for_live_transport():
    engine = QuantumMetricEngine(QuantumMetricConfig(grid_size=(10, 10), mode_count=3))
    engine.shader.trajectory_history_length = 3
    rho = np.eye(16, dtype=np.complex128) / 16.0
    engine.update_quantum_frame(rho, 0.0)
    for _ in range(6):
        engine.process_control_step(0.01)
    assert engine.system_frame.shader.trajectory_positions.shape == (3, 2)
