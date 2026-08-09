"""Paper-backed axisymmetric geometry for photoionization microscopy.

The source figures contain logarithmically color-mapped probability density,
not complex TDSE arrays.  This module therefore reconstructs an iso-density
*proxy* from the published raster and never labels the result as a wavefunction.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image


_CUBE_CORNERS = np.asarray(
    [
        (0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0),
        (0, 0, 1), (1, 0, 1), (1, 1, 1), (0, 1, 1),
    ],
    dtype=np.int64,
)

# A consistent six-tetrahedra split sharing cube diagonal 0--6.
_CUBE_TETRAHEDRA = (
    (0, 1, 2, 6), (0, 2, 3, 6), (0, 3, 7, 6),
    (0, 7, 4, 6), (0, 4, 5, 6), (0, 5, 1, 6),
)


@dataclass(frozen=True)
class RasterGeometryConfig:
    magnetic_field_t: int = 6
    relative_density_level: float = 1.0e-3
    z_min_um: float = -0.75
    z_max_um: float = 0.08
    rho_max_um: float = 0.13
    axial_resolution: int = 84
    transverse_resolution: int = 50
    display_length_mm: float = 240.0

    def __post_init__(self) -> None:
        if self.magnetic_field_t not in (0, 2, 4, 6, 8):
            raise ValueError("magnetic_field_t must be a Figure 5 anchor: 0, 2, 4, 6, or 8")
        if not 1.0e-4 < self.relative_density_level < 1.0:
            raise ValueError("relative_density_level must lie between 1e-4 and 1")
        if self.z_max_um <= self.z_min_um or self.rho_max_um <= 0.0:
            raise ValueError("physical extents must be positive")
        if self.axial_resolution < 16 or self.transverse_resolution < 16:
            raise ValueError("mesh resolutions must be at least 16")
        if self.display_length_mm <= 0.0:
            raise ValueError("display_length_mm must be positive")


@dataclass(frozen=True)
class DensityGrid:
    """Axisymmetric probability-density samples on physical rho/z axes."""

    density_rho_z: np.ndarray
    rho_um: np.ndarray
    z_um: np.ndarray
    metadata: dict[str, Any]

    def __post_init__(self) -> None:
        density = np.asarray(self.density_rho_z)
        rho = np.asarray(self.rho_um)
        z = np.asarray(self.z_um)
        if density.ndim != 2 or density.shape != (len(rho), len(z)):
            raise ValueError("density_rho_z shape must be (len(rho_um), len(z_um))")
        if len(rho) < 4 or len(z) < 4:
            raise ValueError("density grid axes must each contain at least four samples")
        if not np.all(np.isfinite(density)) or np.any(density < 0.0):
            raise ValueError("density_rho_z must be finite and non-negative")
        if not np.all(np.isfinite(rho)) or not np.all(np.diff(rho) > 0.0) or rho[0] < 0.0:
            raise ValueError("rho_um must be finite, non-negative, and strictly increasing")
        if not np.all(np.isfinite(z)) or not np.all(np.diff(z) > 0.0):
            raise ValueError("z_um must be finite and strictly increasing")
        if float(np.max(density)) <= 0.0:
            raise ValueError("density_rho_z must contain positive probability density")

    @property
    def normalized_density(self) -> np.ndarray:
        density = np.asarray(self.density_rho_z, dtype=np.float64)
        return density / float(np.max(density))


@dataclass(frozen=True)
class DensityArrayGeometryConfig:
    relative_density_level: float = 1.0e-3
    axial_resolution: int = 84
    transverse_resolution: int = 50
    display_length_mm: float = 240.0

    def __post_init__(self) -> None:
        if not 0.0 < self.relative_density_level < 1.0:
            raise ValueError("relative_density_level must lie between 0 and 1")
        if self.axial_resolution < 16 or self.transverse_resolution < 16:
            raise ValueError("mesh resolutions must be at least 16")
        if self.display_length_mm <= 0.0:
            raise ValueError("display_length_mm must be positive")


def load_density_grid_npz(path: str | Path) -> DensityGrid:
    """Load rho/z axes and density (or complex psi) from a canonical NPZ."""
    source = Path(path)
    with np.load(source, allow_pickle=False) as archive:
        keys = set(archive.files)
        missing_axes = {"rho_um", "z_um"} - keys
        if missing_axes:
            raise ValueError(f"density NPZ is missing axes: {sorted(missing_axes)}")
        if "density_rho_z" in keys:
            density = np.asarray(archive["density_rho_z"], dtype=np.float64)
            source_quantity = "density_rho_z"
        elif "psi_rho_z" in keys:
            psi = np.asarray(archive["psi_rho_z"], dtype=np.complex128)
            density = np.abs(psi) ** 2
            source_quantity = "abs(psi_rho_z)^2"
        else:
            raise ValueError("density NPZ needs density_rho_z or complex psi_rho_z")
        metadata: dict[str, Any] = {}
        if "metadata_json" in keys:
            metadata = json.loads(str(archive["metadata_json"].item()))
        metadata = {**metadata, "loaded_quantity": source_quantity, "source_npz": str(source)}
        return DensityGrid(
            density_rho_z=density,
            rho_um=np.asarray(archive["rho_um"], dtype=np.float64),
            z_um=np.asarray(archive["z_um"], dtype=np.float64),
            metadata=metadata,
        )


def _nearest_palette_coordinate(rgb: np.ndarray, palette: np.ndarray) -> np.ndarray:
    """Return each RGB pixel's nearest coordinate along the paper color bar."""
    pixels = np.asarray(rgb, dtype=np.float32).reshape(-1, 3)
    colors = np.asarray(palette, dtype=np.float32).reshape(-1, 3)
    result = np.empty(len(pixels), dtype=np.float32)
    for start in range(0, len(pixels), 4096):
        block = pixels[start : start + 4096]
        distance = np.sum((block[:, None, :] - colors[None, :, :]) ** 2, axis=2)
        result[start : start + len(block)] = np.argmin(distance, axis=1)
    denominator = max(len(colors) - 1, 1)
    return (result / denominator).reshape(rgb.shape[:2])


def reconstruct_axisymmetric_density(
    image_path: str | Path,
    palette_path: str | Path,
) -> np.ndarray:
    """Reconstruct a symmetric ``density[rho_index, z_index]`` proxy.

    The two signed-rho halves are combined with their pointwise minimum.  The
    paper's solution is axisymmetric; this operation suppresses asymmetric
    panel labels and most trajectory/axis annotation without inventing lobes.
    """
    rgb = np.asarray(Image.open(image_path).convert("RGB"), dtype=np.uint8)
    palette_image = np.asarray(Image.open(palette_path).convert("RGB"), dtype=np.uint8)
    if palette_image.ndim != 3 or palette_image.shape[1] < 8:
        raise ValueError("density palette must be a horizontal RGB strip")
    palette = palette_image[palette_image.shape[0] // 2]

    log_coordinate = _nearest_palette_coordinate(rgb, palette)
    density = np.power(10.0, -4.0 + 4.0 * log_coordinate)

    middle = density.shape[0] // 2
    half = min(middle, density.shape[0] - middle)
    upper = density[middle - half : middle][::-1]
    lower = density[middle : middle + half]
    symmetric = np.minimum(upper, lower)

    # A compact binomial blur reduces color-quantization terraces while keeping
    # the published nodal cavities. The sampling-volume boundary is forced low
    # so the generated level set closes cleanly.
    padded = np.pad(symmetric, ((1, 1), (1, 1)), mode="edge")
    smooth = (
        padded[:-2, :-2] + 2 * padded[:-2, 1:-1] + padded[:-2, 2:]
        + 2 * padded[1:-1, :-2] + 4 * padded[1:-1, 1:-1] + 2 * padded[1:-1, 2:]
        + padded[2:, :-2] + 2 * padded[2:, 1:-1] + padded[2:, 2:]
    ) / 16.0
    smooth[-2:, :] = 1.0e-4
    smooth[:, :2] = 1.0e-4
    smooth[:, -2:] = 1.0e-4
    # Figure 5 prints the field value in the upper-right and the panel letter
    # in the lower-right. After signed-rho symmetrization those two labels can
    # coincide and form a false torus. Their shared corner lies beyond the
    # physical B=6 T cloud radius; remove that documented annotation region.
    smooth[int(0.42 * smooth.shape[0]) :, int(0.86 * smooth.shape[1]) :] = 1.0e-4
    return smooth


def sample_axisymmetric_volume(
    density_rho_z: np.ndarray,
    config: RasterGeometryConfig,
) -> tuple[np.ndarray, tuple[np.ndarray, np.ndarray, np.ndarray]]:
    """Revolve a 2D density proxy around the paper's field/z axis."""
    margin_z = 0.02 * (config.z_max_um - config.z_min_um)
    margin_r = 0.04 * config.rho_max_um
    x_axis = np.linspace(
        config.z_min_um - margin_z,
        config.z_max_um + margin_z,
        config.axial_resolution,
    )
    y_axis = np.linspace(
        -config.rho_max_um - margin_r,
        config.rho_max_um + margin_r,
        config.transverse_resolution,
    )
    z_axis = y_axis.copy()
    x, y, z = np.meshgrid(x_axis, y_axis, z_axis, indexing="ij")
    radius = np.sqrt(y * y + z * z)

    nz = density_rho_z.shape[1]
    nr = density_rho_z.shape[0]
    xf = (x - config.z_min_um) * (nz - 1) / (config.z_max_um - config.z_min_um)
    rf = radius * (nr - 1) / config.rho_max_um
    valid = (xf >= 0.0) & (xf <= nz - 1) & (rf >= 0.0) & (rf <= nr - 1)
    x0 = np.clip(np.floor(xf).astype(np.int64), 0, nz - 1)
    r0 = np.clip(np.floor(rf).astype(np.int64), 0, nr - 1)
    x1 = np.minimum(x0 + 1, nz - 1)
    r1 = np.minimum(r0 + 1, nr - 1)
    tx = np.clip(xf - x0, 0.0, 1.0)
    tr = np.clip(rf - r0, 0.0, 1.0)
    values = (
        (1.0 - tr) * (1.0 - tx) * density_rho_z[r0, x0]
        + (1.0 - tr) * tx * density_rho_z[r0, x1]
        + tr * (1.0 - tx) * density_rho_z[r1, x0]
        + tr * tx * density_rho_z[r1, x1]
    )
    values[~valid] = 1.0e-4
    return values, (x_axis, y_axis, z_axis)


def sample_density_grid_volume(
    grid: DensityGrid,
    config: DensityArrayGeometryConfig,
) -> tuple[np.ndarray, tuple[np.ndarray, np.ndarray, np.ndarray]]:
    """Revolve a physical, possibly non-uniform rho/z density grid."""
    rho_axis = np.asarray(grid.rho_um, dtype=np.float64)
    paper_z_axis = np.asarray(grid.z_um, dtype=np.float64)
    margin_z = 0.02 * float(np.ptp(paper_z_axis))
    margin_r = 0.04 * float(rho_axis[-1])
    x_axis = np.linspace(paper_z_axis[0] - margin_z, paper_z_axis[-1] + margin_z, config.axial_resolution)
    transverse_axis = np.linspace(
        -rho_axis[-1] - margin_r,
        rho_axis[-1] + margin_r,
        config.transverse_resolution,
    )
    x, y, z = np.meshgrid(x_axis, transverse_axis, transverse_axis, indexing="ij")
    radius = np.sqrt(y * y + z * z)
    xf = np.interp(x.ravel(), paper_z_axis, np.arange(len(paper_z_axis))).reshape(x.shape)
    rf = np.interp(radius.ravel(), rho_axis, np.arange(len(rho_axis))).reshape(radius.shape)
    valid = (
        (x >= paper_z_axis[0]) & (x <= paper_z_axis[-1])
        & (radius >= rho_axis[0]) & (radius <= rho_axis[-1])
    )
    x0 = np.clip(np.floor(xf).astype(np.int64), 0, len(paper_z_axis) - 1)
    r0 = np.clip(np.floor(rf).astype(np.int64), 0, len(rho_axis) - 1)
    x1 = np.minimum(x0 + 1, len(paper_z_axis) - 1)
    r1 = np.minimum(r0 + 1, len(rho_axis) - 1)
    tx = xf - x0
    tr = rf - r0
    density = grid.normalized_density
    values = (
        (1.0 - tr) * (1.0 - tx) * density[r0, x0]
        + (1.0 - tr) * tx * density[r0, x1]
        + tr * (1.0 - tx) * density[r1, x0]
        + tr * tx * density[r1, x1]
    )
    values[~valid] = 0.0
    return values, (x_axis, transverse_axis, transverse_axis.copy())


def _edge_intersection(
    p0: np.ndarray, p1: np.ndarray, v0: float, v1: float, level: float
) -> np.ndarray:
    fraction = 0.5 if abs(v1 - v0) <= 1.0e-15 else (level - v0) / (v1 - v0)
    return p0 + float(np.clip(fraction, 0.0, 1.0)) * (p1 - p0)


def _tetrahedron_triangles(
    points: np.ndarray, values: np.ndarray, level: float
) -> list[tuple[np.ndarray, np.ndarray, np.ndarray]]:
    inside = [index for index, value in enumerate(values) if value >= level]
    outside = [index for index, value in enumerate(values) if value < level]
    if len(inside) in (0, 4):
        return []

    def crossing(a: int, b: int) -> np.ndarray:
        return _edge_intersection(points[a], points[b], float(values[a]), float(values[b]), level)

    if len(inside) == 1:
        a = inside[0]
        p = [crossing(a, b) for b in outside]
        return [(p[0], p[1], p[2])]
    if len(inside) == 3:
        a = outside[0]
        p = [crossing(a, b) for b in inside]
        return [(p[0], p[2], p[1])]
    a, b = inside
    c, d = outside
    ac, ad = crossing(a, c), crossing(a, d)
    bc, bd = crossing(b, c), crossing(b, d)
    return [(ac, bc, bd), (ac, bd, ad)]


def marching_tetrahedra(
    samples: np.ndarray,
    axes: tuple[np.ndarray, np.ndarray, np.ndarray],
    level: float,
) -> tuple[np.ndarray, np.ndarray]:
    """Extract a dependency-free triangular iso-surface from a scalar volume."""
    if samples.shape != tuple(len(axis) for axis in axes):
        raise ValueError("sample shape must match axis lengths")
    spacing = min(float(np.min(np.diff(axis))) for axis in axes)
    quantization = spacing * 1.0e-6
    lookup: dict[tuple[int, int, int], int] = {}
    vertices: list[np.ndarray] = []
    faces: list[tuple[int, int, int]] = []

    def vertex_index(point: np.ndarray) -> int:
        key = tuple(np.rint(point / quantization).astype(np.int64).tolist())
        if key not in lookup:
            lookup[key] = len(vertices)
            vertices.append(point)
        return lookup[key]

    for i in range(samples.shape[0] - 1):
        for j in range(samples.shape[1] - 1):
            for k in range(samples.shape[2] - 1):
                indices = _CUBE_CORNERS + np.asarray((i, j, k))
                values = samples[indices[:, 0], indices[:, 1], indices[:, 2]]
                if np.all(values >= level) or np.all(values < level):
                    continue
                points = np.column_stack(
                    (axes[0][indices[:, 0]], axes[1][indices[:, 1]], axes[2][indices[:, 2]])
                )
                for tetrahedron in _CUBE_TETRAHEDRA:
                    tetra = np.asarray(tetrahedron, dtype=np.int64)
                    for triangle in _tetrahedron_triangles(points[tetra], values[tetra], level):
                        face = tuple(vertex_index(point) for point in triangle)
                        if len(set(face)) == 3:
                            faces.append(face)
    if not vertices or not faces:
        raise ValueError("density level does not intersect the sampled volume")
    vertex_array = np.asarray(vertices, dtype=np.float64)
    face_array = np.asarray(faces, dtype=np.int64)
    canonical = np.sort(face_array, axis=1)
    _, unique = np.unique(canonical, axis=0, return_index=True)
    return vertex_array, face_array[np.sort(unique)]


def mesh_edge_diagnostics(faces: np.ndarray) -> dict[str, int]:
    edges = np.sort(
        np.concatenate((faces[:, (0, 1)], faces[:, (1, 2)], faces[:, (2, 0)])),
        axis=1,
    )
    _, counts = np.unique(edges, axis=0, return_counts=True)
    return {
        "boundary_edges": int(np.count_nonzero(counts == 1)),
        "nonmanifold_edges": int(np.count_nonzero(counts > 2)),
    }


def write_obj(
    path: str | Path,
    vertices: np.ndarray,
    faces: np.ndarray,
    *,
    units: str,
    source_note: str,
) -> Path:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", encoding="utf-8") as output:
        output.write("# QMW paper-backed photoionization iso-density geometry\n")
        output.write(f"# units: {units}\n# {source_note}\n")
        for vertex in vertices:
            output.write("v {:.10g} {:.10g} {:.10g}\n".format(*vertex))
        for face in faces:
            output.write("f {} {} {}\n".format(*(face + 1)))
    return destination


def write_mesh_preview(
    path: str | Path,
    vertices: np.ndarray,
    faces: np.ndarray,
    *,
    title: str,
) -> Path:
    """Render a two-view diagnostic PNG of the exported geometry."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.collections import PolyCollection

    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    figure, axes = plt.subplots(2, 1, figsize=(12, 6.5), facecolor="#05070d")
    triangle_x_y = vertices[faces][:, :, (0, 1)]
    triangle_x_r = np.stack(
        (
            vertices[faces][:, :, 0],
            np.sqrt(vertices[faces][:, :, 1] ** 2 + vertices[faces][:, :, 2] ** 2),
        ),
        axis=2,
    )
    face_position = np.mean(vertices[faces][:, :, 0], axis=1)
    normalized = (face_position - face_position.min()) / max(float(np.ptp(face_position)), 1.0e-12)
    colors = plt.get_cmap("plasma")(0.12 + 0.82 * normalized)
    for axis, triangles, label in zip(
        axes,
        (triangle_x_y, triangle_x_r),
        ("orthographic silhouette", "radial profile (rho >= 0)"),
    ):
        collection = PolyCollection(triangles, facecolors=colors, edgecolors="none", alpha=0.96)
        axis.add_collection(collection)
        axis.autoscale_view()
        axis.set_aspect("equal", adjustable="box")
        axis.set_facecolor("#05070d")
        axis.tick_params(colors="#9ca6bb", labelsize=8)
        axis.set_ylabel("transverse / radial (um)", color="#cbd3e3")
        axis.text(0.01, 0.93, label, transform=axis.transAxes, color="#e6ebf5", fontsize=9)
        for spine in axis.spines.values():
            spine.set_color("#31394b")
    axes[-1].set_xlabel("paper z-axis mapped to OBJ x (um)", color="#cbd3e3")
    figure.suptitle(title, color="white", fontsize=13)
    figure.tight_layout()
    figure.savefig(destination, dpi=180, facecolor=figure.get_facecolor())
    plt.close(figure)
    return destination


def generate_raster_proxy_geometry(
    image_path: str | Path,
    palette_path: str | Path,
    output_directory: str | Path,
    config: RasterGeometryConfig | None = None,
) -> dict[str, Path]:
    config = config or RasterGeometryConfig()
    density = reconstruct_axisymmetric_density(image_path, palette_path)
    samples, axes = sample_axisymmetric_volume(density, config)
    vertices_um, faces = marching_tetrahedra(samples, axes, config.relative_density_level)
    output = Path(output_directory)
    output.mkdir(parents=True, exist_ok=True)
    stem = f"figure5_b{config.magnetic_field_t}_density_{config.relative_density_level:g}"
    note = "digitized Deng et al. (2016) Figure 5 raster; not newly calculated TDSE data"
    physical_path = write_obj(
        output / f"{stem}_physical_um.obj", vertices_um, faces, units="micrometers", source_note=note
    )
    centered = vertices_um - 0.5 * (vertices_um.min(axis=0) + vertices_um.max(axis=0))
    scale = config.display_length_mm / float(np.ptp(centered[:, 0]))
    display_path = write_obj(
        output / f"{stem}_display_mm.obj", centered * scale, faces, units="millimeters", source_note=note
    )
    preview_path = write_mesh_preview(
        output / f"{stem}_preview.png",
        vertices_um,
        faces,
        title=(
            f"Deng et al. Figure 5 density geometry | B={config.magnetic_field_t} T | "
            f"level={config.relative_density_level:g}"
        ),
    )
    edge_diagnostics = mesh_edge_diagnostics(faces)
    metadata = {
        "schema": "qmw.photoionization_geometry.v1",
        "source": note,
        "source_image": str(Path(image_path)),
        "resonance_parabolic_quantum_numbers": [1, 28, 0],
        "magnetic_field_t": config.magnetic_field_t,
        "electric_field_v_per_cm": 808.0,
        "propagation_time_ps": 500.0,
        "construction": "nearest Figure 2 log-colorbar density proxy, signed-rho minimum, documented Figure 5 label-corner mask, axisymmetric revolution, marching tetrahedra",
        "relative_density_level": config.relative_density_level,
        "paper_coordinate_mapping_um": {
            "obj_x_is_paper_z": [config.z_min_um, config.z_max_um],
            "radial_extent": config.rho_max_um,
        },
        "display_scale": {
            "target_axial_length_mm": config.display_length_mm,
            "millimeters_per_micrometer": scale,
        },
        "mesh": {
            "vertices": int(len(vertices_um)),
            "triangles": int(len(faces)),
            **edge_diagnostics,
            "physical_bounds_um": {
                "min": vertices_um.min(axis=0).tolist(),
                "max": vertices_um.max(axis=0).tolist(),
            },
        },
        "limitations": [
            "The publication raster is logarithmically color mapped and cannot recover the complex wavefunction or phase.",
            "The mesh represents one chosen iso-density level, not an electron trajectory or hard orbital boundary.",
            "At B=0 T and B=8 T the source panels contain classical-path overlays; the symmetric reconstruction suppresses but cannot guarantee removal of all overlay pixels.",
        ],
    }
    metadata_path = output / f"{stem}_metadata.json"
    metadata_path.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    return {
        "physical_um_obj": physical_path,
        "display_mm_obj": display_path,
        "preview": preview_path,
        "metadata": metadata_path,
    }


def generate_density_array_geometry(
    density_npz: str | Path,
    output_directory: str | Path,
    config: DensityArrayGeometryConfig | None = None,
) -> dict[str, Path]:
    """Generate geometry strictly from numerical density/wavefunction arrays."""
    config = config or DensityArrayGeometryConfig()
    grid = load_density_grid_npz(density_npz)
    samples, axes = sample_density_grid_volume(grid, config)
    vertices_um, faces = marching_tetrahedra(samples, axes, config.relative_density_level)
    output = Path(output_directory)
    output.mkdir(parents=True, exist_ok=True)
    source_stem = Path(density_npz).stem.replace(" ", "_")
    stem = f"{source_stem}_density_{config.relative_density_level:g}"
    note = "generated from numerical rho/z density arrays; no raster sampling or image crossfade"
    physical_path = write_obj(
        output / f"{stem}_physical_um.obj", vertices_um, faces,
        units="micrometers", source_note=note,
    )
    centered = vertices_um - 0.5 * (vertices_um.min(axis=0) + vertices_um.max(axis=0))
    scale = config.display_length_mm / float(np.ptp(centered[:, 0]))
    display_path = write_obj(
        output / f"{stem}_display_mm.obj", centered * scale, faces,
        units="millimeters", source_note=note,
    )
    preview_path = write_mesh_preview(
        output / f"{stem}_preview.png", vertices_um, faces,
        title=f"Array-derived density geometry | level={config.relative_density_level:g}",
    )
    metadata = {
        "schema": "qmw.photoionization_geometry.v1",
        "source": note,
        "density_grid": grid.metadata,
        "relative_density_level": config.relative_density_level,
        "construction": "normalized numerical density array, axisymmetric revolution, marching tetrahedra",
        "image_sampling": False,
        "crossfading": False,
        "mesh": {
            "vertices": int(len(vertices_um)), "triangles": int(len(faces)),
            **mesh_edge_diagnostics(faces),
            "physical_bounds_um": {
                "min": vertices_um.min(axis=0).tolist(),
                "max": vertices_um.max(axis=0).tolist(),
            },
        },
        "display_scale": {
            "target_axial_length_mm": config.display_length_mm,
            "millimeters_per_micrometer": scale,
        },
    }
    metadata_path = output / f"{stem}_metadata.json"
    metadata_path.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    return {
        "physical_um_obj": physical_path, "display_mm_obj": display_path,
        "preview": preview_path, "metadata": metadata_path,
    }
