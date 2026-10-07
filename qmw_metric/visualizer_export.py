"""Export revision-locked metric frames to the standalone browser visualizer."""

from __future__ import annotations

import json
from pathlib import Path
import shutil

import numpy as np

from .config import LorentzConfig
from .curved_lorentz import CurvedLorentzEngine, ParticleState
from .grid import Grid2D
from .scientific_scenes import ControlledScientificScenes, ScientificScene
from .visualization_controls import (
    OVERLAY_IDS,
    VisualizationControls,
    analysis_visualization_controls,
    performance_visualization_controls,
)


def _actual_trajectory(scene: ScientificScene, grid: Grid2D, steps: int = 180) -> np.ndarray:
    """Integrate the declared explicit-force model through this frozen field."""
    engine = CurvedLorentzEngine(grid, LorentzConfig(topography_mode="explicit_force"))
    particle = ParticleState(
        position=np.array((-0.78, -0.58)),
        velocity=np.array((0.62, 0.31)),
        mass=1.0,
        charge=1.0,
    )
    positions = [particle.position.copy()]
    for index in range(steps):
        particle, _ = engine.step(
            particle, scene.frame.field, 0.0125, time=(index + 1) * 0.0125
        )
        positions.append(particle.position.copy())
    return np.asarray(positions)


def _array(value: np.ndarray) -> list:
    return np.asarray(value, dtype=np.float64).tolist()


def _scene_payload(scene: ScientificScene, grid: Grid2D) -> dict[str, object]:
    shader = scene.frame.shader
    trajectory = shader.trajectory_positions
    if trajectory.size == 0:
        trajectory = _actual_trajectory(scene, grid)
    return {
        "name": scene.name,
        "controlled_change": scene.controlled_change,
        "revision": shader.revision,
        "source_revision": shader.source_revision,
        "time": shader.time,
        "coherence_l1": scene.coherence_l1,
        "purity": scene.purity,
        "potential_coupling": scene.potential_coupling,
        "model_label": shader.model_label,
        "provenance": scene.frame.provenance,
        "projection_basis": scene.frame.projection_basis,
        "potential_model": scene.frame.potential_model,
        "metric_model": scene.frame.metric_model,
        "topography_mode": scene.frame.topography_mode,
        "density": _array(shader.density),
        "potential": _array(shader.potential),
        "sigma": _array(shader.sigma),
        "lapse": _array(shader.lapse),
        "metric": _array(shader.metric),
        "inverse_metric": _array(shader.inverse_metric),
        "determinant": _array(shader.determinant),
        "grad_potential": _array(shader.grad_potential),
        "curvature": _array(shader.curvature),
        "potential_laplacian": _array(shader.potential_laplacian),
        "hessian": _array(shader.hessian),
        "probability_current": _array(shader.probability_current),
        "phase_connection": _array(shader.phase_connection),
        "vorticity": _array(shader.vorticity),
        "mode_shapes": _array(shader.mode_shapes),
        "trajectory_positions": _array(trajectory),
    }


def _control_payload(controls: VisualizationControls) -> dict[str, object]:
    return {
        "enabled": [name for name, item in controls.overlays.items() if item.enabled],
        "opacity": {name: item.opacity for name, item in controls.overlays.items()},
        "selected_mode_index": controls.selected_mode_index,
        "contour_count": controls.contour_count,
        "vector_stride": controls.vector_stride,
        "trajectory_length": controls.trajectory_length,
        "height_scale": controls.height_scale,
    }


def export_scientific_visualizer(
    scenes: ControlledScientificScenes,
    output_directory: str | Path,
    extent: tuple[float, float, float, float],
) -> Path:
    """Write a file-URL-safe visualizer with embedded controlled-scene data."""
    output = Path(output_directory)
    output.mkdir(parents=True, exist_ok=True)
    first = scenes.ordered()[0].frame.shader.density
    grid = Grid2D.periodic(first.shape, extent)
    payload = {
        "contract": "qmw_metric.visualizer.v1",
        "extent": list(extent),
        "overlay_ids": list(OVERLAY_IDS),
        "presets": {
            "analysis": _control_payload(analysis_visualization_controls()),
            "performance": _control_payload(performance_visualization_controls()),
        },
        "scenes": [_scene_payload(scene, grid) for scene in scenes.ordered()],
    }
    assets = Path(__file__).with_name("visualizer")
    for name in (
        "index.html", "app.js", "styles.css", "live.css", "live_frame_client.js"
    ):
        shutil.copyfile(assets / name, output / name)
    encoded = json.dumps(payload, separators=(",", ":"), allow_nan=False)
    (output / "scene_data.js").write_text(
        "window.QMW_METRIC_DATA=" + encoded + ";\n", encoding="utf-8"
    )
    array_names = (
        "density", "potential", "sigma", "lapse", "metric", "inverse_metric",
        "determinant", "grad_potential", "hessian", "curvature",
        "potential_laplacian", "probability_current", "phase_connection",
        "vorticity", "mode_shapes", "trajectory_positions",
    )
    fixture = {
        "fixture_contract": "qmw_metric.controlled_scenes.transport_fixture.v1",
        "frames": [
            {
                "contract": "qmw_metric.shader_frame.v1",
                "revision": scene["source_revision"],
                "source_revision": scene["source_revision"],
                "time": scene["time"],
                "model_label": scene["model_label"],
                "scene_name": scene["name"],
                "origin_frame_revision": scene["revision"],
                "arrays": {name: scene[name] for name in array_names},
            }
            for scene in payload["scenes"]
        ],
    }
    (output / "qmw_metric_fixture_frames.json").write_text(
        json.dumps(fixture, separators=(",", ":"), allow_nan=False), encoding="utf-8"
    )
    return output / "index.html"
