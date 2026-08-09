from __future__ import annotations

from pathlib import Path
import json

import numpy as np

from geometry_acoustics_bridge_v2 import AcousticBridgeConfig
if __package__:
    from .grasshopper_geometry_bridge_v1 import (
        GrasshopperGeometryBridge,
        GrasshopperMeshCandidate,
    )
    from .living_spectral_geometry_v1 import (
        DirtyDomain,
        LivingEventType,
        LivingOperatorEvent,
        LivingSpectralConfig,
        LivingSpectralGeometry,
    )
    from .spectral_geometry_v1 import SpectralGeometryConfig
else:  # Direct-test compatibility.
    from grasshopper_geometry_bridge_v1 import (
        GrasshopperGeometryBridge,
        GrasshopperMeshCandidate,
    )
    from living_spectral_geometry_v1 import (
        DirtyDomain,
        LivingEventType,
        LivingOperatorEvent,
        LivingSpectralConfig,
        LivingSpectralGeometry,
    )
    from spectral_geometry_v1 import SpectralGeometryConfig
from quantum_eigenfield_engine_v1 import (
    QuantumEigenfieldConfig,
    demo_density_matrix,
)
from surface_material_models_v1 import SurfaceMaterialConfig


def grid_mesh(size: int = 7) -> tuple[np.ndarray, np.ndarray]:
    yy, xx = np.mgrid[0:size, 0:size]
    vertices = np.column_stack(
        (
            xx.reshape(-1),
            yy.reshape(-1),
            0.12 * np.sin(xx.reshape(-1)) * np.cos(yy.reshape(-1)),
        )
    ).astype(np.float64)
    faces: list[tuple[int, int, int]] = []
    for y in range(size - 1):
        for x in range(size - 1):
            a = y * size + x
            b = a + 1
            c = a + size
            d = c + 1
            faces.extend(((a, b, d), (a, d, c)))
    return vertices, np.asarray(faces, dtype=np.int64)


def living_config(debounce_ms: float = 15.0) -> LivingSpectralConfig:
    return LivingSpectralConfig(
        spectral=SpectralGeometryConfig(
            n_modes=6,
            effective_wave_speed=90.0,
        ),
        material=SurfaceMaterialConfig(
            model="surface_laplacian",
            n_modes=6,
            effective_wave_speed=90.0,
            damping_base=0.3,
        ),
        quantum=QuantumEigenfieldConfig(n_geometric_modes=6),
        acoustic=AcousticBridgeConfig(
            sample_rate=8000,
            duration_seconds=0.04,
            highpass_hz=5.0,
            seed=61,
        ),
        debounce_ms=debounce_ms,
        spectral_history_depth=3,
    )


def assert_state_artifacts(state) -> None:
    for path in state.paths.values():
        if path == state.paths["directory"]:
            assert Path(path).is_dir()
        else:
            assert Path(path).exists(), path
    with np.load(state.paths["bundle_npz"], allow_pickle=False) as bundle:
        assert int(bundle["revision"]) == state.revision
        assert len(bundle["frequencies_hz"]) == state.mode_count
    with np.load(state.paths["ir_npz"], allow_pickle=False) as acoustic:
        assert acoustic["impulse_response"].shape == (320, 2)
    with np.load(
        state.paths["spectral_history_npz"], allow_pickle=False
    ) as history:
        assert history["magnitudes"].shape[1] == state.mode_count
        assert history["phase_deltas"].shape == history["magnitudes"].shape
        assert str(history["phase_domain"]) == "complex_eigenfield_mode"


def test_grasshopper_candidate_enters_living_pipeline(tmp_path: Path) -> None:
    vertices, faces = grid_mesh()
    with LivingSpectralGeometry(
        vertices,
        faces,
        tmp_path,
        config=living_config(),
        rho=demo_density_matrix(3),
    ) as living:
        living.recompute_now("initial state")
        mutated = vertices.copy()
        mutated[:, 2] += 0.025 * np.sin(mutated[:, 0] + mutated[:, 1])
        candidate = GrasshopperMeshCandidate(
            41,
            mutated,
            faces,
            units="meters",
            metadata={"definition": "integration-test"},
        )
        acceptance = GrasshopperGeometryBridge(living).accept(
            candidate, schedule=False
        )
        assert acceptance.status == "accepted"
        assert living.dirty_domains & DirtyDomain.GEOMETRY
        state = living.recompute_now("Grasshopper geometry commit")
        assert "geometry" in state.invalidated_domains
        assert state.reason == "Grasshopper geometry commit"
        assert_state_artifacts(state)


def test_living_synchronous_mutations_publish_coherent_states(
    tmp_path: Path,
) -> None:
    vertices, faces = grid_mesh()
    published = []
    with LivingSpectralGeometry(
        vertices,
        faces,
        tmp_path,
        config=living_config(),
        rho=demo_density_matrix(3),
    ) as living:
        living.subscribe(published.append)
        first = living.recompute_now("initial living state")
        assert first.revision == 1
        assert first.material_model == "surface_laplacian"
        assert_state_artifacts(first)

        living.update_material(
            schedule=False,
            model="elastic_shell",
            surface_tension=2400.0,
            surface_density=1.2,
            bending_stiffness=18.0,
        )
        assert living.dirty_domains & DirtyDomain.MATERIAL
        second = living.recompute_now("elastic shell mutation")
        assert second.revision == 2
        assert second.material_model == "elastic_shell"
        assert "geometry" not in second.invalidated_domains
        assert second.mode_tracking_score is not None
        assert second.mode_tracking_score > 0.99
        assert first.frequency_max_hz != second.frequency_max_hz
        assert_state_artifacts(second)

        height = vertices[:, 2].reshape(7, 7) + 0.03 * np.eye(7)
        living.apply_event(
            LivingOperatorEvent(
                LivingEventType.GEOMETRY,
                {"height": height, "spatial_scale": 1.0},
                "developmental pulse",
            ),
            schedule=False,
        )
        third = living.recompute_now("developmental pulse")
        assert third.revision == 3
        assert "geometry" in third.invalidated_domains
        assert third.mode_tracking_score is not None
        assert_state_artifacts(third)

        current = json.loads((tmp_path / "current_state.json").read_text())
        assert current["revision"] == third.revision
        assert current["paths"]["ir_wav"] == third.paths["ir_wav"]
        assert [state.revision for state in published] == [1, 2, 3]
        with np.load(
            third.paths["spectral_history_npz"], allow_pickle=False
        ) as history:
            assert history["revisions"].tolist() == [1, 2, 3]
            assert history["magnitudes"].shape == (3, third.mode_count)
            assert np.allclose(history["phase_deltas"][0], 0.0)
            assert np.all(history["transients"] >= 0.0)
            assert np.all(history["transients"] <= 1.0)
        spectral_history = third.descriptors["spectral_history"]
        assert spectral_history["frame_count"] == 3
        assert spectral_history["depth"] == 3
        assert spectral_history["phase_domain"] == "complex_eigenfield_mode"


def test_spectral_history_continues_across_process_restart(tmp_path: Path) -> None:
    vertices, faces = grid_mesh()
    with LivingSpectralGeometry(
        vertices, faces, tmp_path, config=living_config()
    ) as first_process:
        first = first_process.recompute_now("first process")

    with LivingSpectralGeometry(
        vertices, faces, tmp_path, config=living_config()
    ) as second_process:
        second = second_process.recompute_now("second process")

    assert second.revision == first.revision + 1
    with np.load(
        second.paths["spectral_history_npz"], allow_pickle=False
    ) as history:
        assert history["revisions"].tolist() == [first.revision, second.revision]
        assert history["magnitudes"].shape == (2, second.mode_count)


def test_living_measurement_and_debounce_publish_latest_revision(
    tmp_path: Path,
) -> None:
    vertices, faces = grid_mesh()
    with LivingSpectralGeometry(
        vertices,
        faces,
        tmp_path,
        config=living_config(debounce_ms=25.0),
    ) as living:
        living.recompute_now()
        measured_rho = np.diag([0.7, 0.1, 0.1, 0.1]).astype(np.complex128)
        measurement_revision = living.apply_event(
            LivingOperatorEvent(
                LivingEventType.MEASUREMENT,
                {"rho": measured_rho, "outcome": 0},
                "measurement outcome 0",
            )
        )
        measured = living.wait(timeout=5.0)
        assert measured.revision == measurement_revision
        assert measured.reason == "measurement outcome 0"
        assert "quantum" in measured.invalidated_domains
        assert abs(measured.descriptors["quantum"]["purity"] - 0.52) < 1e-12

        superseded = living.update_material(
            damping_base=0.41,
            reason="first damping update",
        )
        latest = living.update_material(
            damping_base=0.57,
            reason="coalesced damping update",
        )
        assert latest is not None and superseded is not None
        assert latest > superseded
        final = living.wait(timeout=5.0)
        assert final.revision == latest
        assert final.reason == "coalesced damping update"
        with np.load(final.paths["bundle_npz"], allow_pickle=False) as bundle:
            damping = bundle["damping_rates"]
            assert np.all(damping > 0.0)
            assert abs(float(np.median(damping)) - 0.57) < 0.2


def test_measurement_event_requires_density_matrix(tmp_path: Path) -> None:
    vertices, faces = grid_mesh()
    with LivingSpectralGeometry(
        vertices, faces, tmp_path, config=living_config()
    ) as living:
        try:
            living.apply_event(
                LivingOperatorEvent(LivingEventType.MEASUREMENT, {"outcome": 1})
            )
        except ValueError as exc:
            assert "requires rho" in str(exc)
        else:
            raise AssertionError("measurement without rho should fail")
