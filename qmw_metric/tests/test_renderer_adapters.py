import json
from pathlib import Path

from qmw_metric import (
    OVERLAY_IDS,
    QuantumMetricConfig,
    build_controlled_scientific_scenes,
    export_scientific_visualizer,
)
from qmw_metric.live_transport import RevisionGate


ROOT = Path(__file__).parents[1]


def test_threejs_reference_has_all_overlays_live_gate_and_pinned_runtime():
    html = (ROOT / "visualizer/index.html").read_text(encoding="utf-8")
    app = (ROOT / "visualizer/app.js").read_text(encoding="utf-8")
    live = (ROOT / "visualizer/live_frame_client.js").read_text(encoding="utf-8")
    assert "three@0.160.0" in html
    assert "new T.WebGLRenderer" in app
    assert "new T.PlaneGeometry" in app
    assert "trajectory_positions" in app
    assert 'id="provenance"' in html
    assert "projection_basis" in app
    for overlay in OVERLAY_IDS:
        assert overlay in app
    assert "stale frame rejected" in live
    assert "setTimeout(()=>this.connect()" in live


def test_max_patch_is_valid_json_and_keeps_view_control_separate():
    directory = ROOT / "max_jitter"
    patch = json.loads((directory / "QMW_Quantum_Metric_Field_Jitter_v1.maxpat").read_text())
    text = json.dumps(patch)
    assert "node.script live_client.js" in text
    assert "js frame_to_jitter.js" in text
    assert "qmw.metric.visual.control" in text
    assert "qmw.metric.visual.command" in text
    assert text.count("qmw_metric_overlay.maxpat") == 11
    adapter = (directory / "frame_to_jitter.js").read_text()
    assert "qmw_metric.shader_frame.v1" in adapter
    assert "p.revision<=lastRevision" in adapter
    assert "publishTrajectory" in adapter
    assert 'outlet(0,"commit",p.revision)' in adapter
    controls = (directory / "qmw_metric_visual_controls.js").read_text()
    for overlay in OVERLAY_IDS:
        assert overlay in controls
    display_patch = json.loads((directory / "qmw_metric_display.maxpat").read_text())
    display_text = json.dumps(display_patch)
    for route in (
        "tri_grid", "surface_color", "contours", "metric_grid",
        "hessian_glyphs", "current_glyphs", "connection_glyphs",
        "line_strip", "trajectory_alpha",
    ):
        assert route in display_text
    display_source = (directory / "qmw_metric_display_geometry.js").read_text()
    for field in (
        "density", "potential", "lapse", "curvature", "vorticity",
        "eigenmode_", "metric_00", "metric_11", "hessian_00",
        "hessian_01", "hessian_11", "probability_current",
        "phase_connection", "trajectory",
    ):
        assert field in display_source


def test_controlled_fixture_uses_live_contract_and_monotonic_revisions(tmp_path):
    config = QuantumMetricConfig(grid_size=(10, 10), mode_count=3)
    scenes = build_controlled_scientific_scenes(config)
    export_scientific_visualizer(scenes, tmp_path, config.extent)
    fixture = json.loads((tmp_path / "qmw_metric_fixture_frames.json").read_text())
    assert fixture["fixture_contract"] == "qmw_metric.controlled_scenes.transport_fixture.v1"
    assert [item["scene_name"] for item in fixture["frames"]] == [
        scene.name for scene in scenes.ordered()
    ]
    gate = RevisionGate()
    assert all(gate.accept(frame) for frame in fixture["frames"])
    assert [frame["revision"] for frame in fixture["frames"]] == [1, 2, 3, 4]


def test_touchdesigner_scaffold_is_contract_consumer_only():
    callbacks = (ROOT / "touchdesigner/qmw_metric_websocket_callbacks.py").read_text()
    assert 'CONTRACT = "qmw_metric.shader_frame.v1"' in callbacks
    assert "stale frame rejected" in callbacks
    for forbidden in ("np.gradient", "np.linalg.eigh", "fft2(", "solve_poisson"):
        assert forbidden not in callbacks.lower()
