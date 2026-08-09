#!/usr/bin/env python3
"""Generate a closed algebraic surface and run the living spectral pipeline.

The first surface is the tanglecube

    x^4 - 5 x^2 + y^4 - 5 y^2 + z^4 - 5 z^2 + a = 0

with ``a = 11.8`` by default.  Meshing uses marching tetrahedra so this file
does not require scikit-image or trimesh.  Output geometry is written both as
OBJ and as the validated mesh-candidate JSON already consumed by the QMW
Grasshopper/living-geometry bridge.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
import argparse
import json
import time
from typing import Callable

import numpy as np

from geometry_acoustics_bridge_v2 import AcousticBridgeConfig
if __package__:
    from .grasshopper_geometry_bridge_v1 import (
        GrasshopperMeshCandidate,
        MeshValidationPolicy,
    )
    from .living_spectral_geometry_v1 import (
        LivingSpectralConfig,
        LivingSpectralGeometry,
    )
    from .spectral_geometry_v1 import SpectralGeometryConfig
else:  # Direct-script compatibility.
    from grasshopper_geometry_bridge_v1 import (
        GrasshopperMeshCandidate,
        MeshValidationPolicy,
    )
    from living_spectral_geometry_v1 import (
        LivingSpectralConfig,
        LivingSpectralGeometry,
    )
    from spectral_geometry_v1 import SpectralGeometryConfig
from surface_material_models_v1 import (
    SurfaceMaterialConfig,
    damping_rate_from_t60,
)


FieldFunction = Callable[[np.ndarray, np.ndarray, np.ndarray], np.ndarray]


@dataclass(frozen=True)
class AlgebraicSurfaceConfig:
    surface: str = "tanglecube"
    parameter: float = 11.8
    resolution: int = 34
    bound: float = 3.0
    level: float = 0.0
    radius_m: float = 0.25
    revision: int = 1


@dataclass(frozen=True)
class PipelineRenderConfig:
    modes: int = 24
    material_model: str = "surface_laplacian"
    effective_wave_speed: float = 120.0
    t60_seconds: float = 4.0
    ir_duration_seconds: float = 8.0
    sample_rate: int = 48000


def algebraic_field(config: AlgebraicSurfaceConfig) -> FieldFunction:
    name = config.surface.strip().lower()
    if name == "tanglecube":
        a = float(config.parameter)

        def field(x: np.ndarray, y: np.ndarray, z: np.ndarray) -> np.ndarray:
            return (
                x**4
                - 5.0 * x**2
                + y**4
                - 5.0 * y**2
                + z**4
                - 5.0 * z**2
                + a
            )

        return field
    if name == "heart":

        def field(x: np.ndarray, y: np.ndarray, z: np.ndarray) -> np.ndarray:
            q = x**2 + 2.25 * y**2 + z**2 - 1.0
            return q**3 - x**2 * z**3 - 0.1125 * y**2 * z**3

        return field
    raise ValueError("surface must be 'tanglecube' or 'heart'")


# Six tetrahedra around the same cube body diagonal.  Using one decomposition
# throughout the grid makes shared cube faces agree and prevents cracks.
_CUBE_CORNERS = np.asarray(
    [
        [0, 0, 0],
        [1, 0, 0],
        [1, 1, 0],
        [0, 1, 0],
        [0, 0, 1],
        [1, 0, 1],
        [1, 1, 1],
        [0, 1, 1],
    ],
    dtype=np.int64,
)
_CUBE_TETRAHEDRA = (
    (0, 1, 2, 6),
    (0, 2, 3, 6),
    (0, 3, 7, 6),
    (0, 7, 4, 6),
    (0, 4, 5, 6),
    (0, 5, 1, 6),
)


def _edge_intersection(
    p0: np.ndarray,
    p1: np.ndarray,
    v0: float,
    v1: float,
    level: float,
) -> np.ndarray:
    denominator = v1 - v0
    if abs(denominator) <= 1.0e-15:
        fraction = 0.5
    else:
        fraction = float(np.clip((level - v0) / denominator, 0.0, 1.0))
    return p0 + fraction * (p1 - p0)


def _tetrahedron_triangles(
    points: np.ndarray,
    values: np.ndarray,
    level: float,
) -> list[tuple[np.ndarray, np.ndarray, np.ndarray]]:
    inside = [index for index, value in enumerate(values) if value <= level]
    outside = [index for index, value in enumerate(values) if value > level]
    if len(inside) in (0, 4):
        return []

    def crossing(a: int, b: int) -> np.ndarray:
        return _edge_intersection(
            points[a], points[b], float(values[a]), float(values[b]), level
        )

    if len(inside) == 1:
        a = inside[0]
        p = [crossing(a, b) for b in outside]
        return [(p[0], p[1], p[2])]
    if len(inside) == 3:
        a = outside[0]
        p = [crossing(a, b) for b in inside]
        return [(p[0], p[1], p[2])]

    a, b = inside
    c, d = outside
    ac = crossing(a, c)
    ad = crossing(a, d)
    bc = crossing(b, c)
    bd = crossing(b, d)
    return [(ac, bc, bd), (ac, bd, ad)]


def _orient_faces_outward(
    vertices: np.ndarray,
    faces: np.ndarray,
    field: FieldFunction,
    epsilon: float,
) -> np.ndarray:
    triangles = vertices[faces]
    centroids = np.mean(triangles, axis=1)
    x, y, z = centroids.T
    ex = np.full(len(centroids), epsilon, dtype=np.float64)
    gradient = np.column_stack(
        (
            (field(x + ex, y, z) - field(x - ex, y, z)) / (2.0 * epsilon),
            (field(x, y + ex, z) - field(x, y - ex, z)) / (2.0 * epsilon),
            (field(x, y, z + ex) - field(x, y, z - ex)) / (2.0 * epsilon),
        )
    )
    normals = np.cross(triangles[:, 1] - triangles[:, 0], triangles[:, 2] - triangles[:, 0])
    result = faces.copy()
    flip = np.einsum("ij,ij->i", normals, gradient) < 0.0
    result[flip, 1], result[flip, 2] = (
        result[flip, 2].copy(),
        result[flip, 1].copy(),
    )
    return result


def marching_tetrahedra(
    config: AlgebraicSurfaceConfig,
) -> tuple[np.ndarray, np.ndarray]:
    if config.resolution < 8:
        raise ValueError("resolution must be at least 8")
    if config.bound <= 0.0 or config.radius_m <= 0.0:
        raise ValueError("bound and radius_m must be positive")

    field = algebraic_field(config)
    axis = np.linspace(-config.bound, config.bound, config.resolution)
    x, y, z = np.meshgrid(axis, axis, axis, indexing="ij")
    samples = field(x, y, z)
    spacing = float(axis[1] - axis[0])
    quantization = spacing * 1.0e-7
    vertex_lookup: dict[tuple[int, int, int], int] = {}
    vertices: list[np.ndarray] = []
    faces: list[tuple[int, int, int]] = []

    def vertex_index(point: np.ndarray) -> int:
        key = tuple(np.rint(point / quantization).astype(np.int64).tolist())
        index = vertex_lookup.get(key)
        if index is None:
            index = len(vertices)
            vertex_lookup[key] = index
            vertices.append(point)
        return index

    for i in range(config.resolution - 1):
        for j in range(config.resolution - 1):
            for k in range(config.resolution - 1):
                indices = _CUBE_CORNERS + np.asarray([i, j, k])
                corner_values = samples[
                    indices[:, 0], indices[:, 1], indices[:, 2]
                ]
                if np.all(corner_values <= config.level) or np.all(
                    corner_values > config.level
                ):
                    continue
                corner_points = np.column_stack(
                    (
                        axis[indices[:, 0]],
                        axis[indices[:, 1]],
                        axis[indices[:, 2]],
                    )
                )
                for tetrahedron in _CUBE_TETRAHEDRA:
                    tetra = np.asarray(tetrahedron, dtype=np.int64)
                    for triangle in _tetrahedron_triangles(
                        corner_points[tetra], corner_values[tetra], config.level
                    ):
                        face = tuple(vertex_index(point) for point in triangle)
                        if len(set(face)) == 3:
                            faces.append(face)

    if not vertices or not faces:
        raise ValueError(
            "the algebraic level set did not intersect the sampling volume"
        )
    vertex_array = np.asarray(vertices, dtype=np.float64)
    face_array = np.asarray(faces, dtype=np.int64)

    # Remove exact duplicate triangles before validation.
    canonical = np.sort(face_array, axis=1)
    _, unique_indices = np.unique(canonical, axis=0, return_index=True)
    face_array = face_array[np.sort(unique_indices)]
    face_array = _orient_faces_outward(
        vertex_array, face_array, field, max(1.0e-5, spacing * 1.0e-3)
    )

    center = 0.5 * (np.min(vertex_array, axis=0) + np.max(vertex_array, axis=0))
    vertex_array -= center
    current_radius = float(np.max(np.linalg.norm(vertex_array, axis=1)))
    vertex_array *= config.radius_m / max(current_radius, 1.0e-15)
    return vertex_array, face_array


def write_obj(
    path: str | Path,
    vertices: np.ndarray,
    faces: np.ndarray,
    *,
    units: str = "meters",
) -> Path:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# QMW procedural algebraic surface",
        f"# units: {units}",
    ]
    lines.extend("v {:.12g} {:.12g} {:.12g}".format(*vertex) for vertex in vertices)
    lines.extend(
        "f {} {} {}".format(int(face[0]) + 1, int(face[1]) + 1, int(face[2]) + 1)
        for face in faces
    )
    destination.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return destination


def generate_candidate(
    config: AlgebraicSurfaceConfig,
    output_directory: str | Path,
) -> tuple[GrasshopperMeshCandidate, dict[str, Path]]:
    output = Path(output_directory)
    output.mkdir(parents=True, exist_ok=True)
    vertices, faces = marching_tetrahedra(config)
    equation = (
        "x^4-5x^2+y^4-5y^2+z^4-5z^2+a=0"
        if config.surface == "tanglecube"
        else "(x^2+2.25y^2+z^2-1)^3-x^2z^3-0.1125y^2z^3=0"
    )
    candidate = GrasshopperMeshCandidate(
        revision=config.revision,
        vertices=vertices,
        faces=faces,
        source="procedural_algebraic_surface",
        units="meters",
        metadata={
            "generator": "algebraic_surface_pipeline_v1",
            "surface": config.surface,
            "equation": equation,
            "parameter": config.parameter,
            "resolution": config.resolution,
            "sampling_bound": config.bound,
            "radius_m": config.radius_m,
        },
    )
    diagnostics = candidate.validate(
        MeshValidationPolicy(
            require_connected=True,
            require_manifold=True,
            require_closed=True,
        )
    )
    stem = "{}_r{:06d}".format(config.surface, config.revision)
    paths = {
        "candidate_json": candidate.save_json(output / f"{stem}_candidate.json"),
        # The canonical OBJ stays in meters for Max/Python and spectral tools.
        "obj": write_obj(
            output / f"{stem}.obj", vertices, faces, units="meters"
        ),
        # Wavefront OBJ does not standardize units.  Rhino documents commonly
        # use millimeters, so provide a correctly scaled companion file.
        "rhino_mm_obj": write_obj(
            output / f"{stem}_rhino_mm.obj",
            vertices * 1000.0,
            faces,
            units="millimeters",
        ),
    }
    diagnostics_path = output / f"{stem}_diagnostics.json"
    diagnostics_path.write_text(
        json.dumps(diagnostics.to_dict(), indent=2), encoding="utf-8"
    )
    paths["diagnostics_json"] = diagnostics_path
    return candidate, paths


def run_living_pipeline(
    candidate: GrasshopperMeshCandidate,
    output_directory: str | Path,
    config: PipelineRenderConfig,
):
    if config.t60_seconds <= 0.0:
        raise ValueError("t60_seconds must be positive")
    spectral = SpectralGeometryConfig(
        n_modes=config.modes,
        effective_wave_speed=config.effective_wave_speed,
    )
    material = SurfaceMaterialConfig(
        model=config.material_model,
        n_modes=config.modes,
        effective_wave_speed=config.effective_wave_speed,
        damping_base=damping_rate_from_t60(config.t60_seconds),
    )
    acoustic = AcousticBridgeConfig(
        sample_rate=config.sample_rate,
        duration_seconds=config.ir_duration_seconds,
    )
    living_config = LivingSpectralConfig(
        spectral=spectral,
        material=material,
        acoustic=acoustic,
    )
    with LivingSpectralGeometry(
        candidate.vertices_m,
        candidate.faces,
        output_directory,
        config=living_config,
    ) as living:
        return living.recompute_now(reason="procedural algebraic surface")


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--surface", choices=("tanglecube", "heart"), default="tanglecube")
    parser.add_argument("--parameter", type=float, default=11.8)
    parser.add_argument("--resolution", type=int, default=34)
    parser.add_argument("--bound", type=float, default=3.0)
    parser.add_argument("--radius-m", type=float, default=0.25)
    parser.add_argument("--revision", type=int, default=1)
    parser.add_argument("--output", default="algebraic_surface_output")
    parser.add_argument("--geometry-only", action="store_true")
    parser.add_argument("--modes", type=int, default=24)
    parser.add_argument("--model", default="surface_laplacian")
    parser.add_argument("--wave-speed", type=float, default=120.0)
    parser.add_argument("--t60", type=float, default=4.0)
    parser.add_argument("--ir-duration", type=float, default=8.0)
    parser.add_argument("--sample-rate", type=int, default=48000)
    return parser


def main() -> int:
    args = build_argument_parser().parse_args()
    surface_config = AlgebraicSurfaceConfig(
        surface=args.surface,
        parameter=args.parameter,
        resolution=args.resolution,
        bound=args.bound,
        radius_m=args.radius_m,
        revision=args.revision,
    )
    output = Path(args.output).expanduser().resolve()
    started = time.monotonic()
    candidate, paths = generate_candidate(surface_config, output)
    summary: dict[str, object] = {
        "surface": asdict(surface_config),
        "geometry_hash": candidate.geometry_hash,
        "vertex_count": int(len(candidate.vertices)),
        "face_count": int(len(candidate.faces)),
        "paths": {name: str(path) for name, path in paths.items()},
    }
    if not args.geometry_only:
        render_config = PipelineRenderConfig(
            modes=args.modes,
            material_model=args.model,
            effective_wave_speed=args.wave_speed,
            t60_seconds=args.t60,
            ir_duration_seconds=args.ir_duration,
            sample_rate=args.sample_rate,
        )
        state = run_living_pipeline(candidate, output / "living", render_config)
        summary["render"] = asdict(render_config)
        summary["living_state"] = state.to_dict()
    summary["elapsed_seconds"] = time.monotonic() - started
    summary_path = output / "algebraic_surface_run.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
