"""Read-only polygonal geometry providers for graph gauge connections.

The graph connection does not manufacture topology.  This module adapts a
declared surface mesh into its canonical edge set and its oriented face cycles;
therefore triangles, square lattices, cubes, and every Platonic solid use the
same connection and holonomy contract.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import math
from typing import Any, Literal, Mapping, Sequence

import numpy as np

from .gauge_transport import GaugeConnection
from .geometry_gauge_phase import ExplicitGeometryGaugePhaseConfig, apply_explicit_geometry_gauge_phase


Array = np.ndarray
CouplingMode = Literal["uniform", "inverse_edge_length"]


@dataclass(frozen=True)
class MeshGaugeTopologyConfig:
    """Explicit mesh-to-connection choices; no connection is inferred from rho."""

    coupling_scale: float = 1.0
    coupling_mode: CouplingMode = "uniform"
    connection_phase_by_oriented_edge: Mapping[tuple[int, int], float] = field(default_factory=dict)
    geometry_phase_config: ExplicitGeometryGaugePhaseConfig | None = None

    def __post_init__(self) -> None:
        if not math.isfinite(float(self.coupling_scale)) or float(self.coupling_scale) < 0.0:
            raise ValueError("coupling_scale must be finite and nonnegative.")
        if self.coupling_mode not in ("uniform", "inverse_edge_length"):
            raise ValueError("coupling_mode must be 'uniform' or 'inverse_edge_length'.")
        if self.geometry_phase_config is not None and not isinstance(self.geometry_phase_config, ExplicitGeometryGaugePhaseConfig):
            raise TypeError("geometry_phase_config must be ExplicitGeometryGaugePhaseConfig or None.")
        if self.geometry_phase_config is not None and self.connection_phase_by_oriented_edge:
            raise ValueError("use either geometry_phase_config or connection_phase_by_oriented_edge, not both.")
        for edge, phase in self.connection_phase_by_oriented_edge.items():
            if len(edge) != 2 or int(edge[0]) == int(edge[1]) or not math.isfinite(float(phase)):
                raise ValueError("connection phases need finite oriented pairs of distinct vertex indices.")


@dataclass(frozen=True)
class MeshGaugeTopologyFrame:
    """A geometry-owned edge/coupling/face-cycle descriptor for GaugeConnection."""

    vertices: Array
    face_cycles: Mapping[str, tuple[int, ...]]
    connection: GaugeConnection
    coupling_mode: CouplingMode
    provenance: str = "declared_polygonal_mesh_to_read_only_u1_gauge_connection"

    @property
    def face_holonomies(self) -> Mapping[str, float]:
        return {name: self.connection.holonomy(cycle) for name, cycle in self.face_cycles.items()}


def mesh_gauge_topology(
    vertices: Any,
    faces: Sequence[Sequence[int]] | Array,
    *,
    config: MeshGaugeTopologyConfig | None = None,
    provenance: str = "declared_polygonal_mesh_to_read_only_u1_gauge_connection",
) -> MeshGaugeTopologyFrame:
    """Construct a connection directly from declared polygonal geometry.

    ``faces`` retains its polygons: a square remains a four-edge holonomy,
    rather than silently being subdivided into two triangular loops.  The
    default coupling is uniform and topological.  Inverse-length coupling is
    available only as an explicit geometry model choice.
    """

    choices = config or MeshGaugeTopologyConfig()
    points = np.asarray(vertices, dtype=float)
    if points.ndim != 2 or points.shape[0] < 3 or points.shape[1] < 2 or not np.all(np.isfinite(points)):
        raise ValueError("vertices must be a finite array shaped (vertex_count, coordinate_dimension >= 2).")
    cycles = _face_cycles(faces, points.shape[0])
    edges = sorted({_canonical_edge(source, destination) for cycle in cycles for source, destination in _cycle_edges(cycle)})
    edge_array = np.asarray(edges, dtype=int)
    coupling = _edge_couplings(points, edge_array, choices)
    phases = _edge_phases(edge_array, choices.connection_phase_by_oriented_edge)
    connection = GaugeConnection(points.shape[0], edge_array, phases, coupling=coupling)
    if choices.geometry_phase_config is not None:
        connection = apply_explicit_geometry_gauge_phase(connection, choices.geometry_phase_config)
    return MeshGaugeTopologyFrame(
        vertices=np.array(points, copy=True),
        face_cycles={f"face:{index}": cycle for index, cycle in enumerate(cycles)},
        connection=connection,
        coupling_mode=choices.coupling_mode,
        provenance=provenance,
    )


def relational_surface_mesh_to_gauge_connection(
    mesh: Any,
    *,
    config: MeshGaugeTopologyConfig | None = None,
) -> MeshGaugeTopologyFrame:
    """Adapt a :class:`RelationalSurfaceMesh` without changing its embodiment."""

    if not hasattr(mesh, "vertices") or not hasattr(mesh, "faces"):
        raise TypeError("mesh must provide vertices and polygon faces.")
    revision = getattr(mesh, "source_revision", "unknown")
    return mesh_gauge_topology(
        mesh.vertices,
        mesh.faces,
        config=config,
        provenance=f"relational_surface_mesh_revision_{revision}_to_read_only_u1_gauge_connection",
    )


def cube_gauge_topology(*, config: MeshGaugeTopologyConfig | None = None) -> MeshGaugeTopologyFrame:
    """Return the declared six-square-face cube topology used for demonstrations."""

    vertices = np.asarray(
        ((0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (1.0, 1.0, 0.0), (0.0, 1.0, 0.0),
         (0.0, 0.0, 1.0), (1.0, 0.0, 1.0), (1.0, 1.0, 1.0), (0.0, 1.0, 1.0)),
        dtype=float,
    )
    # Outward-oriented cycles: bottom, top, front, right, back, left.
    faces = ((0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7))
    return mesh_gauge_topology(vertices, faces, config=config, provenance="declared_cube_square_faces_to_read_only_u1_gauge_connection")


def _face_cycles(faces: Sequence[Sequence[int]] | Array, vertex_count: int) -> tuple[tuple[int, ...], ...]:
    try:
        raw_faces = tuple(faces)
    except TypeError as error:
        raise ValueError("faces must be a sequence of polygon vertex cycles.") from error
    if not raw_faces:
        raise ValueError("at least one polygon face is required.")
    cycles: list[tuple[int, ...]] = []
    for index, raw in enumerate(raw_faces):
        cycle = tuple(int(vertex) for vertex in raw)
        if len(cycle) < 3 or len(set(cycle)) != len(cycle):
            raise ValueError(f"face {index} must be a simple polygon cycle with at least three vertices.")
        if any(vertex < 0 or vertex >= vertex_count for vertex in cycle):
            raise ValueError(f"face {index} references a vertex outside the mesh.")
        cycles.append(cycle)
    return tuple(cycles)


def _cycle_edges(cycle: Sequence[int]) -> tuple[tuple[int, int], ...]:
    return tuple(zip(cycle, cycle[1:] + cycle[:1]))


def _canonical_edge(source: int, destination: int) -> tuple[int, int]:
    return (source, destination) if source < destination else (destination, source)


def _edge_couplings(vertices: Array, edges: Array, config: MeshGaugeTopologyConfig) -> Array:
    if config.coupling_mode == "uniform":
        return np.full(edges.shape[0], float(config.coupling_scale), dtype=float)
    lengths = np.linalg.norm(vertices[edges[:, 1]] - vertices[edges[:, 0]], axis=1)
    if np.any(~np.isfinite(lengths)) or np.any(lengths <= 0.0):
        raise ValueError("inverse_edge_length coupling requires distinct finite mesh vertices.")
    return float(config.coupling_scale) / lengths


def _edge_phases(edges: Array, mapping: Mapping[tuple[int, int], float]) -> Array:
    resolved = np.zeros(edges.shape[0], dtype=float)
    declared = {(int(source), int(destination)): float(phase) for (source, destination), phase in mapping.items()}
    valid = {tuple(edge) for edge in edges.tolist()} | {(right, left) for left, right in edges.tolist()}
    unknown = set(declared).difference(valid)
    if unknown:
        raise ValueError(f"connection phase references an edge absent from the mesh: {sorted(unknown)!r}.")
    for index, (source, destination) in enumerate(edges):
        forward = declared.get((int(source), int(destination)))
        backward = declared.get((int(destination), int(source)))
        if forward is not None and backward is not None and not np.isclose(forward, -backward):
            raise ValueError("opposite orientations of one mesh edge must carry opposite connection phases.")
        resolved[index] = forward if forward is not None else (-backward if backward is not None else 0.0)
    return resolved


__all__ = [
    "MeshGaugeTopologyConfig", "MeshGaugeTopologyFrame", "cube_gauge_topology",
    "mesh_gauge_topology", "relational_surface_mesh_to_gauge_connection",
]
