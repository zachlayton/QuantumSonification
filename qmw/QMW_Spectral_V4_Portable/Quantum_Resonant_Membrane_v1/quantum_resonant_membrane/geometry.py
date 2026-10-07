"""Fixed triangulated sphere, four regions, and auditable membrane modes."""

from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np


Array = np.ndarray


@dataclass(frozen=True)
class MembraneGeometry:
    vertices: Array
    faces: Array
    edges: Array
    vertex_area: Array
    regions: Array
    stiffness: Array
    mode_shapes: Array
    eigenvalues: Array
    frequencies: Array
    boundary_vertices: dict[tuple[int, int], tuple[int, ...]]
    schema: str = "qmw.quantum_resonant_membrane.geometry.v1"

    def contact_vertex(self, source: int, destination: int, phase: float) -> int:
        pair = tuple(sorted((int(source), int(destination))))
        candidates = self.boundary_vertices.get(pair)
        if not candidates:
            candidates = tuple(np.flatnonzero(self.regions == int(destination)).tolist())
        if not candidates:
            return 0
        wrapped = (float(phase) + math.pi) % (2.0 * math.pi)
        index = min(len(candidates) - 1, int(wrapped / (2.0 * math.pi) * len(candidates)))
        return int(candidates[index])


def _icosahedron() -> tuple[list[Array], list[tuple[int, int, int]]]:
    golden = (1.0 + math.sqrt(5.0)) / 2.0
    raw = [
        (-1, golden, 0), (1, golden, 0), (-1, -golden, 0), (1, -golden, 0),
        (0, -1, golden), (0, 1, golden), (0, -1, -golden), (0, 1, -golden),
        (golden, 0, -1), (golden, 0, 1), (-golden, 0, -1), (-golden, 0, 1),
    ]
    vertices = [np.asarray(value, dtype=float) / np.linalg.norm(value) for value in raw]
    faces = [
        (0, 11, 5), (0, 5, 1), (0, 1, 7), (0, 7, 10), (0, 10, 11),
        (1, 5, 9), (5, 11, 4), (11, 10, 2), (10, 7, 6), (7, 1, 8),
        (3, 9, 4), (3, 4, 2), (3, 2, 6), (3, 6, 8), (3, 8, 9),
        (4, 9, 5), (2, 4, 11), (6, 2, 10), (8, 6, 7), (9, 8, 1),
    ]
    return vertices, faces


def _subdivide(
    vertices: list[Array], faces: list[tuple[int, int, int]]
) -> tuple[list[Array], list[tuple[int, int, int]]]:
    midpoint_cache: dict[tuple[int, int], int] = {}

    def midpoint(left: int, right: int) -> int:
        key = tuple(sorted((left, right)))
        cached = midpoint_cache.get(key)
        if cached is not None:
            return cached
        value = vertices[left] + vertices[right]
        value /= np.linalg.norm(value)
        vertices.append(value)
        result = len(vertices) - 1
        midpoint_cache[key] = result
        return result

    refined: list[tuple[int, int, int]] = []
    for a, b, c in faces:
        ab, bc, ca = midpoint(a, b), midpoint(b, c), midpoint(c, a)
        refined.extend(((a, ab, ca), (b, bc, ab), (c, ca, bc), (ab, bc, ca)))
    return vertices, refined


def build_icosphere_geometry(*, subdivisions: int = 1, modes: int = 20) -> MembraneGeometry:
    if subdivisions < 0 or subdivisions > 3:
        raise ValueError("subdivisions must be between zero and three")
    vertices_list, faces_list = _icosahedron()
    for _ in range(subdivisions):
        vertices_list, faces_list = _subdivide(vertices_list, faces_list)
    vertices = np.asarray(vertices_list, dtype=float)
    faces = np.asarray(faces_list, dtype=int)
    if modes < 1 or modes > vertices.shape[0]:
        raise ValueError("modes must fit the geometry vertex count")

    edge_set: set[tuple[int, int]] = set()
    area = np.zeros(vertices.shape[0], dtype=float)
    for face in faces:
        a, b, c = (int(value) for value in face)
        edge_set.update((tuple(sorted(pair)) for pair in ((a, b), (b, c), (c, a))))
        face_area = 0.5 * np.linalg.norm(np.cross(vertices[b] - vertices[a], vertices[c] - vertices[a]))
        area[[a, b, c]] += face_area / 3.0
    area /= float(np.mean(area))
    edges = np.asarray(sorted(edge_set), dtype=int)

    tetrahedra = np.asarray(
        ((1, 1, 1), (1, -1, -1), (-1, 1, -1), (-1, -1, 1)),
        dtype=float,
    )
    tetrahedra /= np.linalg.norm(tetrahedra, axis=1)[:, None]
    regions = np.argmax(vertices @ tetrahedra.T, axis=1).astype(int)

    laplacian = np.zeros((vertices.shape[0], vertices.shape[0]), dtype=float)
    boundary: dict[tuple[int, int], set[int]] = {}
    for left, right in edges:
        distance = float(np.linalg.norm(vertices[left] - vertices[right]))
        weight = 1.0 / max(distance, 1.0e-9)
        laplacian[left, left] += weight
        laplacian[right, right] += weight
        laplacian[left, right] -= weight
        laplacian[right, left] -= weight
        if regions[left] != regions[right]:
            key = tuple(sorted((int(regions[left]), int(regions[right]))))
            boundary.setdefault(key, set()).update((int(left), int(right)))
    stiffness = laplacian + 0.04 * np.diag(area)
    inverse_root_mass = 1.0 / np.sqrt(area)
    symmetric = inverse_root_mass[:, None] * stiffness * inverse_root_mass[None, :]
    eigenvalues, vectors = np.linalg.eigh(symmetric)
    order = np.argsort(eigenvalues)[:modes]
    eigenvalues = np.maximum(eigenvalues[order], 1.0e-12)
    shapes = inverse_root_mass[:, None] * vectors[:, order]
    for mode in range(shapes.shape[1]):
        anchor = int(np.argmax(np.abs(shapes[:, mode])))
        if shapes[anchor, mode] < 0.0:
            shapes[:, mode] *= -1.0
    return MembraneGeometry(
        vertices=vertices,
        faces=faces,
        edges=edges,
        vertex_area=area,
        regions=regions,
        stiffness=stiffness,
        mode_shapes=shapes,
        eigenvalues=eigenvalues,
        frequencies=np.sqrt(eigenvalues),
        boundary_vertices={key: tuple(sorted(value)) for key, value in boundary.items()},
    )


__all__ = ["MembraneGeometry", "build_icosphere_geometry"]
