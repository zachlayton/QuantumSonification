"""Deterministic geometric graphs for procedural composition."""

from __future__ import annotations

import math

import networkx as nx


def build_regular_polygon_graph(
    sides: int = 8,
    radius: float = 1.0,
    phase: float = math.pi / 2.0,
) -> nx.Graph:
    """Return a cycle graph embedded as a regular polygon.

    Nodes are integers in counterclockwise order. Each node stores its polar
    ``angle`` and Cartesian ``position``. Each edge stores its Euclidean
    ``distance`` so later layers can use geometry without recomputing it.

    ``phase`` rotates the polygon; by default node 0 is at the top.
    """
    if isinstance(sides, bool) or not isinstance(sides, int) or sides < 3:
        raise ValueError("sides must be an integer of at least 3")
    if not math.isfinite(radius) or radius <= 0.0:
        raise ValueError("radius must be a finite positive number")
    if not math.isfinite(phase):
        raise ValueError("phase must be finite")

    graph = nx.Graph(
        geometry="regular_polygon",
        sides=sides,
        radius=float(radius),
        phase=float(phase),
    )

    for node in range(sides):
        angle = phase + math.tau * node / sides
        position = (radius * math.cos(angle), radius * math.sin(angle))
        graph.add_node(node, angle=angle % math.tau, position=position)

    for node in range(sides):
        neighbor = (node + 1) % sides
        start = graph.nodes[node]["position"]
        end = graph.nodes[neighbor]["position"]
        graph.add_edge(node, neighbor, distance=math.dist(start, end))

    return graph


def build_quantized_cycle_graph(
    node_count: int = 24,
    pitch_divisions: int = 24,
    rhythm_subdivisions: int = 8,
    root_pitch_space: float = 60.0,
    radius: float = 1.0,
    phase: float = math.pi / 2.0,
) -> nx.Graph:
    """Return a cycle with independent pitch and rhythmic resolutions.

    ``pitch_divisions=24`` gives 24-EDO (50-cent steps).
    ``rhythm_subdivisions=8`` gives eight ticks per quarter note, making one
    tick a 32nd note. Node count remains independent so the topology can later
    grow without changing either musical resolution.
    """
    for name, value in (
        ("node_count", node_count),
        ("pitch_divisions", pitch_divisions),
        ("rhythm_subdivisions", rhythm_subdivisions),
    ):
        if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
            raise ValueError(f"{name} must be a positive integer")
    if node_count < 3:
        raise ValueError("node_count must be at least 3")
    if not math.isfinite(root_pitch_space):
        raise ValueError("root_pitch_space must be finite")

    graph = build_regular_polygon_graph(node_count, radius, phase)
    cents_per_step = 1200.0 / pitch_divisions
    pitch_space_per_step = 12.0 / pitch_divisions
    quarter_length_per_tick = 1.0 / rhythm_subdivisions
    note_value = 4 * rhythm_subdivisions

    graph.graph.update(
        pitch_system=f"{pitch_divisions}-EDO",
        pitch_divisions=pitch_divisions,
        cents_per_pitch_step=cents_per_step,
        root_pitch_space=float(root_pitch_space),
        rhythm_subdivisions_per_quarter=rhythm_subdivisions,
        rhythm_note_value=note_value,
        quarter_length_per_tick=quarter_length_per_tick,
    )

    for sequence_index, node_id in enumerate(graph.nodes):
        pitch_step = sequence_index % pitch_divisions
        graph.nodes[node_id].update(
            pitch_step=pitch_step,
            cents_from_root=pitch_step * cents_per_step,
            pitch_space=root_pitch_space + pitch_step * pitch_space_per_step,
            onset_tick=sequence_index,
            duration_ticks=1,
            quarter_length=quarter_length_per_tick,
        )

    return graph


def build_tetrahedron_graph(radius: float = 1.0) -> nx.Graph:
    """Return the edge graph of a regular tetrahedron embedded in 3D.

    Node 0 is the apex. Nodes 1--3 form an equilateral base in the xy-plane
    below the origin. Every node lies on the requested circumsphere radius.
    """
    if not math.isfinite(radius) or radius <= 0.0:
        raise ValueError("radius must be a finite positive number")

    base_radius = radius * 2.0 * math.sqrt(2.0) / 3.0
    base_z = -radius / 3.0
    positions = {0: (0.0, 0.0, radius)}
    for node_id in range(1, 4):
        angle = math.tau * (node_id - 1) / 3.0
        positions[node_id] = (
            base_radius * math.cos(angle),
            base_radius * math.sin(angle),
            base_z,
        )

    graph = nx.complete_graph(4)
    graph.graph.update(
        geometry="regular_tetrahedron",
        dimension=3,
        radius=float(radius),
    )
    for node_id, position in positions.items():
        graph.nodes[node_id].update(
            role="apex" if node_id == 0 else "base",
            position=position,
        )
    for start, end in graph.edges:
        graph.edges[start, end]["distance"] = math.dist(
            positions[start], positions[end]
        )
    return graph


def build_dodecahedron_graph(radius: float = 1.0) -> nx.Graph:
    """Return the edge graph of a regular dodecahedron embedded in 3D."""
    if not math.isfinite(radius) or radius <= 0.0:
        raise ValueError("radius must be a finite positive number")

    phi = (1.0 + math.sqrt(5.0)) / 2.0
    inverse_phi = 1.0 / phi
    raw_positions: list[tuple[float, float, float]] = []

    for x in (-1.0, 1.0):
        for y in (-1.0, 1.0):
            for z in (-1.0, 1.0):
                raw_positions.append((x, y, z))
    for y in (-inverse_phi, inverse_phi):
        for z in (-phi, phi):
            raw_positions.append((0.0, y, z))
    for x in (-inverse_phi, inverse_phi):
        for y in (-phi, phi):
            raw_positions.append((x, y, 0.0))
    for x in (-phi, phi):
        for z in (-inverse_phi, inverse_phi):
            raw_positions.append((x, 0.0, z))

    scale = radius / math.sqrt(3.0)
    positions = {
        node_id: tuple(scale * coordinate for coordinate in point)
        for node_id, point in enumerate(raw_positions)
    }
    distances = [
        math.dist(positions[start], positions[end])
        for start in positions
        for end in positions
        if start < end
    ]
    edge_length = min(distance for distance in distances if distance > 1e-12)

    graph = nx.Graph(
        geometry="regular_dodecahedron",
        dimension=3,
        radius=float(radius),
        golden_ratio=phi,
        edge_length=edge_length,
    )
    for node_id, position in positions.items():
        graph.add_node(node_id, position=position)
    for start in positions:
        for end in positions:
            if start >= end:
                continue
            distance = math.dist(positions[start], positions[end])
            if math.isclose(distance, edge_length, rel_tol=1e-9, abs_tol=1e-9):
                graph.add_edge(start, end, distance=distance)

    if graph.number_of_edges() != 30 or any(degree != 3 for _, degree in graph.degree):
        raise RuntimeError("failed to construct a regular dodecahedron")
    return graph
