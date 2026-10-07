"""Volumetric 3-D embodiment of a QMW relational-geometry observation.

The quantum data in :mod:`qmw.qmw_emergent_geometry` remain authoritative
observations. This module makes explicitly modeled choices: a fixed tetrahedral
embedding, lobe radii, neck radii, and an implicit-surface transfer function.
It never changes ``rho`` or claims that its mesh is a reconstructed spacetime.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from pathlib import Path
from typing import Iterable

import numpy as np

from .qmw_emergent_geometry import EmergentGeometryFrame


Array = np.ndarray
_TETRAHEDRA = (
    (0, 5, 1, 6), (0, 1, 2, 6), (0, 2, 3, 6),
    (0, 3, 7, 6), (0, 7, 4, 6), (0, 4, 5, 6),
)
_CUBE_OFFSETS = np.asarray(
    ((0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0),
     (0, 0, 1), (1, 0, 1), (1, 1, 1), (0, 1, 1)),
    dtype=int,
)


def _finite(name: str, value: float, *, positive: bool = False, nonnegative: bool = False) -> float:
    value = float(value)
    valid = value > 0.0 if positive else (value >= 0.0 if nonnegative else True)
    if not math.isfinite(value) or not valid:
        raise ValueError(f"{name} must be finite" + (" and positive." if positive else " and nonnegative." if nonnegative else "."))
    return value


@dataclass(frozen=True)
class RelationalMeshConfig:
    """Declared 3-D embodiment choices, separate from quantum observables."""

    resolution: int = 30
    lobe_radius: float = 0.36
    entropy_radius_gain: float = 0.12
    neck_radius_gain: float = 0.30
    bounds_padding: float = 0.18
    minimum_edge_weight: float = 1.0e-5
    maximum_necks: int | None = None

    def __post_init__(self) -> None:
        if int(self.resolution) != self.resolution or not 10 <= self.resolution <= 64:
            raise ValueError("resolution must be an integer in [10, 64].")
        _finite("lobe_radius", self.lobe_radius, positive=True)
        _finite("entropy_radius_gain", self.entropy_radius_gain, nonnegative=True)
        _finite("neck_radius_gain", self.neck_radius_gain, positive=True)
        _finite("bounds_padding", self.bounds_padding, nonnegative=True)
        _finite("minimum_edge_weight", self.minimum_edge_weight, positive=True)
        if self.maximum_necks is not None and (int(self.maximum_necks) != self.maximum_necks or self.maximum_necks < 1):
            raise ValueError("maximum_necks must be a positive integer or None.")


@dataclass(frozen=True)
class RelationalSurfaceMesh:
    """A triangle surface created from a declared relational field model."""

    vertices: Array
    faces: Array
    centers: Array
    lobe_radii: Array
    neck_radii: Array
    connected_components: int
    source_revision: int
    provenance: str = "modeled_implicit_lobes_and_entanglement_necks_v1"

    def is_watertight(self) -> bool:
        """Return whether every undirected triangle edge occurs exactly twice."""

        edges = np.sort(np.concatenate((self.faces[:, (0, 1)], self.faces[:, (1, 2)], self.faces[:, (2, 0)])), axis=1)
        _, counts = np.unique(edges, axis=0, return_counts=True)
        return bool(counts.size and np.all(counts == 2))

    def vertex_normals(self) -> Array:
        """Return area-weighted smooth normals for a presentation renderer.

        These normals are derived solely from the already-generated modeled
        surface; they have no quantum-information meaning.
        """

        normals = np.zeros_like(self.vertices)
        triangles = self.vertices[self.faces]
        face_normals = np.cross(triangles[:, 1] - triangles[:, 0], triangles[:, 2] - triangles[:, 0])
        for corner in range(3):
            np.add.at(normals, self.faces[:, corner], face_normals)
        lengths = np.linalg.norm(normals, axis=1)
        active = lengths > 1.0e-14
        normals[active] /= lengths[active, None]
        normals[~active] = (0.0, 0.0, 1.0)
        return normals

    def subdivision_skin(self, *, iterations: int = 1) -> "RelationalSurfaceMesh":
        """Return a smooth Loop-style *presentation skin* over this solid.

        It refines and smooths only the exported surface.  The quantum frame,
        relational measurements, topology, and lobe/neck construction are not
        changed.  A closed two-manifold is required so the skin stays sealed.
        """

        if int(iterations) != iterations or not 1 <= iterations <= 3:
            raise ValueError("iterations must be an integer in [1, 3].")
        if not self.is_watertight():
            raise ValueError("subdivision skin requires a watertight two-manifold.")
        vertices = np.array(self.vertices, dtype=float, copy=True)
        faces = np.array(self.faces, dtype=int, copy=True)
        for _ in range(iterations):
            neighbours = [set() for _ in range(vertices.shape[0])]
            opposite: dict[tuple[int, int], list[int]] = {}
            for first, second, third in faces:
                for left, right, other in ((first, second, third), (second, third, first), (third, first, second)):
                    key = tuple(sorted((int(left), int(right))))
                    neighbours[left].add(int(right))
                    neighbours[right].add(int(left))
                    opposite.setdefault(key, []).append(int(other))
            smoothed = np.empty_like(vertices)
            for index, adjacent in enumerate(neighbours):
                count = len(adjacent)
                beta = 3.0 / 16.0 if count == 3 else 3.0 / (8.0 * count)
                smoothed[index] = (1.0 - count * beta) * vertices[index] + beta * np.sum(vertices[list(adjacent)], axis=0)
            edge_index: dict[tuple[int, int], int] = {}
            new_vertices = list(smoothed)
            for key, others in opposite.items():
                if len(others) != 2:
                    raise ValueError("subdivision skin requires exactly two faces per edge.")
                left, right = key
                edge_index[key] = len(new_vertices)
                new_vertices.append(0.375 * (vertices[left] + vertices[right]) + 0.125 * (vertices[others[0]] + vertices[others[1]]))
            new_faces: list[tuple[int, int, int]] = []
            for first, second, third in faces:
                first_second = edge_index[tuple(sorted((int(first), int(second))))]
                second_third = edge_index[tuple(sorted((int(second), int(third))))]
                third_first = edge_index[tuple(sorted((int(third), int(first))))]
                new_faces.extend(((int(first), first_second, third_first), (int(second), second_third, first_second),
                                  (int(third), third_first, second_third), (first_second, second_third, third_first)))
            vertices = np.asarray(new_vertices, dtype=float)
            faces = np.asarray(new_faces, dtype=int)
        return RelationalSurfaceMesh(vertices=vertices, faces=faces, centers=np.array(self.centers, copy=True),
            lobe_radii=np.array(self.lobe_radii, copy=True), neck_radii=np.array(self.neck_radii, copy=True),
            connected_components=self.connected_components, source_revision=self.source_revision,
            provenance=f"{self.provenance}_loop_presentation_skin_{iterations}")

    def export_obj(self, path: str | Path, *, smooth_normals: bool = True, material_name: str = "QMW_RelationalGeometry") -> Path:
        """Write a portable, smooth-lit OBJ plus an optional Phong material.

        The material is a presentation adapter only.  It does not alter the
        mesh, observer frame, or any quantum measurement.
        """

        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        material = target.with_suffix(".mtl")
        material.write_text(
            "# QMW relational geometry presentation material\\n"
            f"newmtl {material_name}\\nKa 0.035 0.055 0.085\\nKd 0.100 0.420 0.680\\n"
            "Ks 0.650 0.820 1.000\\nNs 96.000\\nd 1.000\\nillum 2\\n",
            encoding="utf-8",
        )
        normals = self.vertex_normals() if smooth_normals else None
        with target.open("w", encoding="utf-8") as handle:
            handle.write("# QMW relational geometry mesh v1\n")
            handle.write(f"# source revision {self.source_revision}\n")
            handle.write(f"mtllib {material.name}\nusemtl {material_name}\ns 1\n")
            for vertex in self.vertices:
                handle.write(f"v {vertex[0]:.9g} {vertex[1]:.9g} {vertex[2]:.9g}\n")
            if normals is not None:
                for normal in normals:
                    handle.write(f"vn {normal[0]:.9g} {normal[1]:.9g} {normal[2]:.9g}\n")
            for face in self.faces:
                if normals is None:
                    handle.write(f"f {face[0] + 1} {face[1] + 1} {face[2] + 1}\n")
                else:
                    handle.write("f " + " ".join(f"{index + 1}//{index + 1}" for index in face) + "\n")
        return target


def default_tetrahedral_centers() -> Array:
    """Return the fixed v1 four-site embedding; it is a model convention."""

    return np.asarray(
        ((-0.62, -0.42, -0.36), (0.62, -0.42, -0.36),
         (0.00, 0.64, -0.36), (0.00, 0.00, 0.72)),
        dtype=float,
    )


def fibonacci_sphere_centers(count: int, *, radius: float = 1.15) -> Array:
    """Return a declared, even 3-D placement for more than four sites.

    This is only an embedding convention; it is not inferred from ``rho``.
    """

    if int(count) != count or count < 2:
        raise ValueError("count must be an integer of at least two.")
    _finite("radius", radius, positive=True)
    indices = np.arange(int(count), dtype=float)
    y = 1.0 - 2.0 * (indices + 0.5) / count
    radial = np.sqrt(np.maximum(0.0, 1.0 - y * y))
    angle = math.pi * (3.0 - math.sqrt(5.0)) * indices
    return radius * np.column_stack((np.cos(angle) * radial, y, np.sin(angle) * radial))


def _active_edges(geometry: EmergentGeometryFrame, config: RelationalMeshConfig) -> tuple:
    edges = [edge for edge in geometry.edges if edge.adjacency_weight > config.minimum_edge_weight]
    # A sparsification cap is a display/embodiment choice, never a claim that
    # omitted quantum correlations vanish.
    if config.maximum_necks is not None:
        edges.sort(key=lambda edge: (-edge.adjacency_weight, edge.left, edge.right))
        edges = edges[:config.maximum_necks]
    return tuple(edges)


def _segment_distance(points: Array, start: Array, end: Array) -> Array:
    direction = end - start
    length_squared = float(np.dot(direction, direction))
    if length_squared <= 0.0:
        return np.linalg.norm(points - start, axis=-1)
    fraction = np.clip(np.sum((points - start) * direction, axis=-1) / length_squared, 0.0, 1.0)
    nearest = start + fraction[..., None] * direction
    return np.linalg.norm(points - nearest, axis=-1)


def relational_signed_field(points: Array, geometry: EmergentGeometryFrame, config: RelationalMeshConfig, *, centers: Array | None = None) -> Array:
    """Evaluate the modeled lobe-plus-neck implicit field at 3-D points.

    Positive values are inside the embodied geometry. The lobe/neck relation is
    an artistic/modeling transfer function, not a physical spacetime metric.
    """

    count = int(np.asarray(geometry.node_entropy_bits).size)
    sites = (default_tetrahedral_centers() if count == 4 else fibonacci_sphere_centers(count)) if centers is None else np.asarray(centers, dtype=float)
    if sites.shape != (count, 3) or not np.all(np.isfinite(sites)):
        raise ValueError("centers must be a finite (node_count, 3) array.")
    values = np.asarray(points, dtype=float)
    if values.shape[-1] != 3 or not np.all(np.isfinite(values)):
        raise ValueError("points must be finite with final dimension 3.")
    entropy = np.asarray(geometry.node_entropy_bits, dtype=float)
    radii = config.lobe_radius + config.entropy_radius_gain * np.clip(entropy, 0.0, 1.0)
    field = np.max(np.stack([radius - np.linalg.norm(values - center, axis=-1) for center, radius in zip(sites, radii)]), axis=0)
    for edge in _active_edges(geometry, config):
        # MI activates a connection. The local entropy limits its size so a
        # trivially pure endpoint cannot acquire a large volumetric throat.
        endpoint_entropy = min(float(entropy[edge.left]), float(entropy[edge.right]))
        neck_radius = config.neck_radius_gain * edge.adjacency_weight * (0.25 + 0.75 * endpoint_entropy)
        field = np.maximum(field, neck_radius - _segment_distance(values, sites[edge.left], sites[edge.right]))
    return field


def _add_vertex(vertices: list[Array], cache: dict[tuple[float, float, float], int], point: Array) -> int:
    key = tuple(np.round(point, decimals=10).tolist())
    index = cache.get(key)
    if index is None:
        index = len(vertices)
        vertices.append(np.asarray(point, dtype=float))
        cache[key] = index
    return index


def _interpolate(point_a: Array, value_a: float, point_b: Array, value_b: float) -> Array:
    denominator = value_a - value_b
    fraction = 0.5 if abs(denominator) <= 1.0e-14 else np.clip(value_a / denominator, 0.0, 1.0)
    return point_a + fraction * (point_b - point_a)


def _polygonize_tetrahedron(points: Array, values: Array, vertices: list[Array], cache: dict[tuple[float, float, float], int], faces: list[tuple[int, int, int]]) -> None:
    inside = [index for index, value in enumerate(values) if value >= 0.0]
    outside = [index for index in range(4) if index not in inside]
    if len(inside) in (0, 4):
        return
    if len(inside) in (1, 3):
        pivot = inside[0] if len(inside) == 1 else outside[0]
        others = outside if len(inside) == 1 else inside
        indices = [_add_vertex(vertices, cache, _interpolate(points[pivot], values[pivot], points[item], values[item])) for item in others]
        if len(inside) == 1:
            faces.append((indices[0], indices[1], indices[2]))
        else:
            faces.append((indices[0], indices[2], indices[1]))
        return
    first, second = inside
    third, fourth = outside
    p00 = _add_vertex(vertices, cache, _interpolate(points[first], values[first], points[third], values[third]))
    p01 = _add_vertex(vertices, cache, _interpolate(points[first], values[first], points[fourth], values[fourth]))
    p10 = _add_vertex(vertices, cache, _interpolate(points[second], values[second], points[third], values[third]))
    p11 = _add_vertex(vertices, cache, _interpolate(points[second], values[second], points[fourth], values[fourth]))
    faces.extend(((p00, p01, p11), (p00, p11, p10)))


def _surface_components(vertex_count: int, faces: Array) -> int:
    if vertex_count == 0:
        return 0
    neighbours: list[set[int]] = [set() for _ in range(vertex_count)]
    for first, second, third in faces:
        neighbours[first].update((second, third))
        neighbours[second].update((first, third))
        neighbours[third].update((first, second))
    remaining = set(range(vertex_count))
    components = 0
    while remaining:
        components += 1
        stack = [remaining.pop()]
        while stack:
            node = stack.pop()
            adjacent = neighbours[node] & remaining
            stack.extend(adjacent)
            remaining.difference_update(adjacent)
    return components


def _orient_faces_outward(vertices: Array, faces: Array, geometry: EmergentGeometryFrame, config: RelationalMeshConfig, centers: Array, step: float) -> Array:
    """Orient faces toward decreasing implicit field (the exterior)."""

    oriented = np.array(faces, dtype=int, copy=True)
    triangle = vertices[oriented]
    centers_of_faces = np.mean(triangle, axis=1)
    gradients = np.empty_like(centers_of_faces)
    delta = max(float(step) * 0.2, 1.0e-5)
    for axis in range(3):
        displacement = np.zeros(3, dtype=float)
        displacement[axis] = delta
        gradients[:, axis] = (
            relational_signed_field(centers_of_faces + displacement, geometry, config, centers=centers)
            - relational_signed_field(centers_of_faces - displacement, geometry, config, centers=centers)
        ) / (2.0 * delta)
    face_normals = np.cross(triangle[:, 1] - triangle[:, 0], triangle[:, 2] - triangle[:, 0])
    # The modeled field is positive inside, so its negative gradient points out.
    reverse = np.einsum("ij,ij->i", face_normals, -gradients) < 0.0
    swapped = np.array(oriented[reverse, 1], copy=True)
    oriented[reverse, 1] = oriented[reverse, 2]
    oriented[reverse, 2] = swapped
    return oriented


def build_relational_surface_mesh(geometry: EmergentGeometryFrame, config: RelationalMeshConfig | None = None, *, centers: Array | None = None) -> RelationalSurfaceMesh:
    """Generate a 3-D triangle mesh from lobes and MI-controlled necks."""

    cfg = config or RelationalMeshConfig()
    count = int(np.asarray(geometry.node_entropy_bits).size)
    sites = (default_tetrahedral_centers() if count == 4 else fibonacci_sphere_centers(count)) if centers is None else np.asarray(centers, dtype=float)
    if sites.shape != (count, 3) or not np.all(np.isfinite(sites)):
        raise ValueError("centers must be a finite (node_count, 3) array.")
    entropy = np.asarray(geometry.node_entropy_bits, dtype=float)
    if entropy.shape != (count,) or not np.all(np.isfinite(entropy)):
        raise ValueError("geometry must contain finite node entropies matching centers.")
    lobe_radii = cfg.lobe_radius + cfg.entropy_radius_gain * np.clip(entropy, 0.0, 1.0)
    max_radius = max(float(np.max(lobe_radii)), cfg.neck_radius_gain) + cfg.bounds_padding
    lower, upper = np.min(sites, axis=0) - max_radius, np.max(sites, axis=0) + max_radius
    axes = [np.linspace(lower[axis], upper[axis], int(cfg.resolution)) for axis in range(3)]
    x, y, z = np.meshgrid(*axes, indexing="ij")
    grid = np.stack((x, y, z), axis=-1)
    field = relational_signed_field(grid, geometry, cfg, centers=sites)
    vertices: list[Array] = []
    cache: dict[tuple[float, float, float], int] = {}
    faces: list[tuple[int, int, int]] = []
    for ix in range(cfg.resolution - 1):
        for iy in range(cfg.resolution - 1):
            for iz in range(cfg.resolution - 1):
                cube_points = np.asarray([grid[ix + dx, iy + dy, iz + dz] for dx, dy, dz in _CUBE_OFFSETS])
                cube_values = np.asarray([field[ix + dx, iy + dy, iz + dz] for dx, dy, dz in _CUBE_OFFSETS])
                if np.all(cube_values >= 0.0) or np.all(cube_values < 0.0):
                    continue
                for tetrahedron in _TETRAHEDRA:
                    _polygonize_tetrahedron(cube_points[list(tetrahedron)], cube_values[list(tetrahedron)], vertices, cache, faces)
    if not vertices or not faces:
        raise RuntimeError("implicit surface extraction produced an empty mesh; increase resolution or lobe radius.")
    vertex_array = np.asarray(vertices, dtype=float)
    face_array = _orient_faces_outward(
        vertex_array, np.asarray(faces, dtype=int), geometry, cfg, sites,
        min(float(axis[1] - axis[0]) for axis in axes),
    )
    neck_radii = np.zeros((count, count), dtype=float)
    for edge in _active_edges(geometry, cfg):
        endpoint_entropy = min(float(entropy[edge.left]), float(entropy[edge.right]))
        neck_radii[edge.left, edge.right] = neck_radii[edge.right, edge.left] = (
            cfg.neck_radius_gain * edge.adjacency_weight * (0.25 + 0.75 * endpoint_entropy)
        )
    return RelationalSurfaceMesh(
        vertices=vertex_array, faces=face_array, centers=np.array(sites, copy=True),
        lobe_radii=np.array(lobe_radii, copy=True), neck_radii=neck_radii,
        connected_components=_surface_components(vertex_array.shape[0], face_array),
        source_revision=geometry.revision,
    )


__all__ = [
    "RelationalMeshConfig", "RelationalSurfaceMesh", "build_relational_surface_mesh",
    "default_tetrahedral_centers", "fibonacci_sphere_centers", "relational_signed_field",
]
