from __future__ import annotations

from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
REPOSITORY_ROOT = HERE.parent

from eigenfield_timing_layer_v1 import EigenfieldState
from geometry_acoustics_bridge_v2 import (
    AcousticBridgeConfig,
    GeometryAcousticsBridgeV2,
)
from quantum_eigenfield_engine_v1 import (
    QuantumEigenfieldConfig,
    QuantumEigenfieldEngine,
    demo_density_matrix,
)
from surface_material_models_v1 import (
    MODEL_ORDER,
    SurfaceMaterialConfig,
    create_surface_model,
    mesh_adjacency,
)
if __package__:
    from .surface_eigenfield_pipeline_v1 import SurfaceEigenfieldPipeline
    from .spectral_geometry_v1 import (
        MeshSpectralGeometry,
        SpectralGeometryConfig,
    )
else:  # Direct-test compatibility.
    from surface_eigenfield_pipeline_v1 import SurfaceEigenfieldPipeline
    from spectral_geometry_v1 import (
        MeshSpectralGeometry,
        SpectralGeometryConfig,
    )
from molecular_geometry_layer_v1 import SpectralGeometryPacket
from developmental_fields_v1 import create_developmental_field
from emergent_geometry_v1_osc import (
    EmergentGeometryEngine,
    GeometryParameters,
    PRESETS,
)


def grid_mesh(size: int = 7) -> tuple[np.ndarray, np.ndarray]:
    yy, xx = np.mgrid[0:size, 0:size]
    vertices = np.column_stack(
        (
            xx.reshape(-1),
            yy.reshape(-1),
            0.15 * np.sin(xx.reshape(-1)) * np.cos(yy.reshape(-1)),
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


def base_spectrum(
    vertices: np.ndarray,
    faces: np.ndarray,
    n_modes: int = 12,
) -> tuple[np.ndarray, np.ndarray]:
    adjacency = mesh_adjacency(vertices, faces)
    degree = np.asarray(adjacency.sum(axis=1)).reshape(-1)
    laplacian = np.diag(degree) - adjacency.toarray()
    values, vectors = np.linalg.eigh(laplacian)
    keep = values > 1e-8
    return values[keep][:n_modes], vectors[:, keep][:, :n_modes]


def test_all_material_packets_reach_timing_and_bridge(tmp_path: Path) -> None:
    vertices, faces = grid_mesh()
    eigenvalues, eigenvectors = base_spectrum(vertices, faces)
    voltage = np.sin(vertices[:, 0] * 0.7) + np.cos(vertices[:, 1] * 0.4)
    rho = demo_density_matrix(4)
    observed_frequency_sets: dict[str, np.ndarray] = {}

    for model_name in MODEL_ORDER:
        config = SurfaceMaterialConfig(
            model=model_name,
            n_modes=8,
            effective_wave_speed=90.0,
            surface_tension=2400.0,
            surface_density=1.2,
            bending_stiffness=18.0,
            damping_base=0.35,
        )
        model = create_surface_model(
            vertices,
            faces,
            eigenvalues,
            eigenvectors,
            config,
        )
        packet = model.solve(voltage=voltage)
        observed_frequency_sets[model_name] = packet.frequencies_hz.copy()

        engine = QuantumEigenfieldEngine(
            rho,
            modal_packet=packet,
            config=QuantumEigenfieldConfig(n_geometric_modes=8),
        )
        exported = engine.export(tmp_path / f"{model_name}_quantum")

        timing = EigenfieldState(exported["npz"])
        assert timing.material_model == model_name
        np.testing.assert_allclose(
            timing.frequencies_hz, packet.frequencies_hz
        )
        np.testing.assert_allclose(
            timing.decay_times_seconds, packet.decay_times_seconds
        )
        np.testing.assert_allclose(timing.damping_rates, packet.damping_rates)
        np.testing.assert_allclose(timing.material_weights, packet.mode_weights)

        bridge = GeometryAcousticsBridgeV2(
            exported["npz"],
            AcousticBridgeConfig(
                sample_rate=8000,
                duration_seconds=0.08,
                highpass_hz=5.0,
                seed=41,
            ),
        )
        np.testing.assert_allclose(
            bridge.packet.frequencies_hz, packet.frequencies_hz
        )
        np.testing.assert_allclose(
            bridge.packet.decay_times_seconds, packet.decay_times_seconds
        )
        np.testing.assert_allclose(bridge.packet.mode_weights, packet.mode_weights)
        assert bridge.packet.metadata == packet.metadata
        ir = bridge.synthesize_modal_ir()
        assert ir.shape == (640, 2)
        assert np.all(np.isfinite(ir))
        assert np.max(np.abs(ir)) <= 0.80001

    assert not np.allclose(
        observed_frequency_sets["tensioned_membrane"],
        observed_frequency_sets["elastic_shell"],
    )
    assert not np.allclose(
        observed_frequency_sets["surface_laplacian"],
        observed_frequency_sets["graph_diffusion"],
    )


def test_spectral_solver_matches_shared_packet_contract(tmp_path: Path) -> None:
    vertices, faces = grid_mesh()
    solver = MeshSpectralGeometry(
        vertices,
        faces,
        SpectralGeometryConfig(n_modes=8, effective_wave_speed=90.0),
    )
    solved = solver.solve(vertices[0], vertices[-1])
    path = solver.export_npz(tmp_path / "spectral_geometry.npz")
    packet = SpectralGeometryPacket.load_npz(path)

    assert packet.geometry_kind == "triangular_surface"
    assert packet.metadata["solver"] == "spectral_geometry_v1"
    np.testing.assert_allclose(packet.eigenvalues, solved.eigenvalues)
    np.testing.assert_allclose(packet.eigenvectors, solved.eigenvectors)
    np.testing.assert_allclose(packet.frequencies_hz, solved.frequencies_hz)
    np.testing.assert_allclose(packet.mode_weights, solved.mode_weights)


def test_developmental_field_drives_emergent_geometry(tmp_path: Path) -> None:
    field = create_developmental_field("turing_stripes", size=32, seed=23)
    engine = EmergentGeometryEngine(
        32,
        PRESETS["labyrinth"],
        GeometryParameters(),
        23,
        14,
        4,
        developmental_field=field,
    )
    engine.step(3)
    assert engine.descriptors()["developmental_model"] == (
        "turing_activator_inhibitor"
    )
    state_path = tmp_path / "developmental_emergent.npz"
    engine.save_state(state_path)
    with np.load(state_path, allow_pickle=False) as state:
        assert str(state["developmental_model"]) == (
            "turing_activator_inhibitor"
        )
        assert state["primary_field"].shape == (32, 32)
        assert state["secondary_field"].shape == (32, 32)


def test_molecular_damping_alias_survives_quantum_export(tmp_path: Path) -> None:
    values = np.arange(1.0, 7.0)
    vectors = np.eye(8, 6)
    damping = np.linspace(0.2, 0.7, 6)
    packet = SpectralGeometryPacket(
        geometry_kind="molecular_graph",
        vertices=np.column_stack((np.arange(8), np.zeros((8, 2)))),
        eigenvalues=values,
        eigenvectors=vectors,
        frequencies_hz=np.linspace(100.0, 600.0, 6),
        mode_weights=np.ones(6),
        damping=damping,
        metadata={"source": "molecular-test"},
    )
    engine = QuantumEigenfieldEngine(
        demo_density_matrix(2),
        modal_packet=packet,
        config=QuantumEigenfieldConfig(n_geometric_modes=4),
    )
    exported = engine.export(tmp_path / "molecular_quantum")
    with np.load(exported["npz"], allow_pickle=False) as packet:
        assert str(packet["material_model"]) == "molecular_graph"
        np.testing.assert_allclose(packet["damping_rates"], damping[:4])
        np.testing.assert_allclose(
            packet["decay_times_seconds"], 1.0 / damping[:4]
        )


def test_surface_model_sources_are_synchronized() -> None:
    root_source = HERE / "surface_material_models_v1.py"
    bundle_source = (
        REPOSITORY_ROOT
        / "surface_material_models_v1"
        / "surface_material_models_v1.py"
    )
    assert root_source.read_bytes() == bundle_source.read_bytes()


def test_quantum_engine_still_accepts_legacy_geometric_schema() -> None:
    values = np.arange(1.0, 7.0)
    vectors = np.eye(8, 6)
    engine = QuantumEigenfieldEngine(
        demo_density_matrix(2),
        modal_packet={
            "geometric_eigenvalues": values,
            "geometric_eigenvectors": vectors,
        },
        config=QuantumEigenfieldConfig(n_geometric_modes=4),
    )
    assert engine.material_model == "spectral_geometry"
    np.testing.assert_allclose(engine.geometric_eigenvalues, values[:4])


def test_one_shot_pipeline_exports_coherent_bundle(tmp_path: Path) -> None:
    vertices, faces = grid_mesh()
    eigenvalues, eigenvectors = base_spectrum(vertices, faces)
    pipeline = SurfaceEigenfieldPipeline(
        SurfaceMaterialConfig(
            model="elastic_shell",
            n_modes=8,
            effective_wave_speed=90.0,
            surface_tension=2400.0,
            surface_density=1.2,
            bending_stiffness=18.0,
            damping_base=0.35,
        ),
        QuantumEigenfieldConfig(n_geometric_modes=8),
        AcousticBridgeConfig(
            sample_rate=8000,
            duration_seconds=0.08,
            highpass_hz=5.0,
            seed=51,
        ),
    )
    paths = pipeline.run(
        {
            "vertices": vertices,
            "faces": faces,
            "eigenvalues": eigenvalues,
            "eigenvectors": eigenvectors,
        },
        tmp_path,
        demo_density_matrix(4),
    )

    assert paths["manifest"].exists()
    assert paths["acoustics"]["wav"].exists()
    with np.load(paths["bundle"]) as bundle:
        assert str(bundle["material_model"]) == "elastic_shell"
        assert bundle["frequencies_hz"].shape == (8,)
    with np.load(paths["acoustics"]["npz"]) as rendered:
        ir = rendered["impulse_response"]
        assert ir.shape == (640, 2)
        assert np.all(np.isfinite(ir))
