"""Periodic surface meshes used as geometric score generators."""

from __future__ import annotations

import math
from typing import Sequence

import networkx as nx
import numpy as np
from music21 import note


TORUS_HEXATONIC_SET = ("C", "D", "E", "F#", "G", "A")
TORUS_RING_RESTS = (1, 2, 3, 4, 5, 4, 3, 2)


def torus_gaussian_curvature(
    minor_angle: float,
    major_radius: float,
    minor_radius: float,
) -> float:
    """Return Gaussian curvature at a torus minor-coordinate angle."""
    cosine = math.cos(minor_angle)
    return cosine / (
        minor_radius * (major_radius + minor_radius * cosine)
    )


def quartic_torus_residual(
    x: float,
    y: float,
    z: float,
    major_radius: float,
    minor_radius: float,
) -> float:
    """Evaluate the torus's implicit quartic polynomial."""
    squared_radius = x * x + y * y + z * z
    return (
        squared_radius + major_radius * major_radius - minor_radius * minor_radius
    ) ** 2 - 4.0 * major_radius * major_radius * (x * x + y * y)


def build_quartic_torus_mesh(
    major_segments: int = 12,
    minor_segments: int = 8,
    major_radius: float = 2.0,
    minor_radius: float = 0.75,
    eigenmode_index: int = 7,
) -> nx.Graph:
    """Return a weighted quadrilateral mesh sampled from an algebraic torus."""
    for name, value, minimum in (
        ("major_segments", major_segments, 6),
        ("minor_segments", minor_segments, 4),
    ):
        if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
            raise ValueError(f"{name} must be an integer of at least {minimum}")
    for name, value in (("major_radius", major_radius), ("minor_radius", minor_radius)):
        if not math.isfinite(value) or value <= 0.0:
            raise ValueError(f"{name} must be a finite positive number")
    if minor_radius >= major_radius:
        raise ValueError("minor_radius must be smaller than major_radius")

    node_count = major_segments * minor_segments
    if (
        isinstance(eigenmode_index, bool)
        or not isinstance(eigenmode_index, int)
        or not 0 < eigenmode_index < node_count
    ):
        raise ValueError("eigenmode_index must select a nonconstant mesh mode")

    graph = nx.Graph()
    for minor_index in range(minor_segments):
        phi = math.tau * minor_index / minor_segments
        for major_index in range(major_segments):
            theta = math.tau * major_index / major_segments
            radial_distance = major_radius + minor_radius * math.cos(phi)
            position = (
                radial_distance * math.cos(theta),
                radial_distance * math.sin(theta),
                minor_radius * math.sin(phi),
            )
            graph.add_node(
                (minor_index, major_index),
                position=position,
                major_angle=theta,
                minor_angle=phi,
                gaussian_curvature=torus_gaussian_curvature(
                    phi,
                    major_radius,
                    minor_radius,
                ),
                implicit_residual=quartic_torus_residual(
                    *position,
                    major_radius=major_radius,
                    minor_radius=minor_radius,
                ),
            )

    for minor_index in range(minor_segments):
        for major_index in range(major_segments):
            node_id = (minor_index, major_index)
            graph.add_edge(
                node_id,
                (minor_index, (major_index + 1) % major_segments),
                coordinate_direction="major",
            )
            graph.add_edge(
                node_id,
                ((minor_index + 1) % minor_segments, major_index),
                coordinate_direction="minor",
            )

    for start, end, data in graph.edges(data=True):
        start_position = np.asarray(graph.nodes[start]["position"])
        end_position = np.asarray(graph.nodes[end]["position"])
        edge_length = float(np.linalg.norm(end_position - start_position))
        data["length"] = edge_length
        data["coupling"] = 1.0 / edge_length

    node_order = sorted(graph.nodes)
    adjacency = nx.to_numpy_array(
        graph,
        nodelist=node_order,
        weight="coupling",
        dtype=float,
    )
    laplacian = np.diag(adjacency.sum(axis=1)) - adjacency
    eigenvalues, eigenvectors = np.linalg.eigh(laplacian)
    eigenfield = eigenvectors[:, eigenmode_index].copy()
    anchor_index = int(np.argmax(np.abs(eigenfield)))
    if eigenfield[anchor_index] < 0.0:
        eigenfield *= -1.0
    for node_id, field_value in zip(node_order, eigenfield, strict=True):
        graph.nodes[node_id]["field_value"] = float(field_value)

    graph.graph.update(
        geometry="quartic_torus_surface_mesh",
        dimension=3,
        major_segments=major_segments,
        minor_segments=minor_segments,
        rows=minor_segments,
        columns=major_segments,
        major_radius=float(major_radius),
        minor_radius=float(minor_radius),
        implicit_polynomial="(x^2+y^2+z^2+R^2-r^2)^2-4R^2(x^2+y^2)",
        topology="S1 x S1",
        euler_characteristic=0,
        eigenmode_index=eigenmode_index,
        eigenvalue=float(eigenvalues[eigenmode_index]),
        node_order=tuple(node_order),
    )
    return graph


def apply_torus_hexatonic_mapping(
    graph: nx.Graph,
    pitch_classes: Sequence[str] = TORUS_HEXATONIC_SET,
    base_octave: int = 4,
    ring_rest_ticks: Sequence[int] = TORUS_RING_RESTS,
) -> nx.Graph:
    """Map both torus angles to pitch rotation, register, phrasing, and time."""
    major_segments = graph.graph.get("major_segments")
    minor_segments = graph.graph.get("minor_segments")
    if not isinstance(major_segments, int) or not isinstance(minor_segments, int):
        raise ValueError("graph must be a torus mesh with segment metadata")
    if len(pitch_classes) not in (5, 6):
        raise ValueError("surface pitch collection must be pentatonic or hexatonic")
    if len(ring_rest_ticks) != minor_segments or any(
        isinstance(value, bool) or not isinstance(value, int) or value <= 0
        for value in ring_rest_ticks
    ):
        raise ValueError("ring_rest_ticks must provide one positive value per minor ring")

    parsed_pitch_classes = tuple(note.Note(f"{name}4").pitch.name for name in pitch_classes)
    mapped = graph.copy()
    onset_tick = 0
    traversal = []
    for minor_index in range(minor_segments):
        major_indices = (
            range(major_segments)
            if minor_index % 2 == 0
            else range(major_segments - 1, -1, -1)
        )
        phi = math.tau * minor_index / minor_segments
        if math.sin(phi) > 0.25:
            octave_displacement = 1
        elif math.sin(phi) < -0.25:
            octave_displacement = -1
        else:
            octave_displacement = 0

        for major_index in major_indices:
            node_id = (minor_index, major_index)
            theta_band = int(major_index * len(parsed_pitch_classes) / major_segments)
            collection_rotation = minor_index % len(parsed_pitch_classes)
            degree_index = (theta_band + collection_rotation) % len(parsed_pitch_classes)
            pitch_class = parsed_pitch_classes[degree_index]
            musical_pitch = note.Note(
                f"{pitch_class}{base_octave + octave_displacement}"
            ).pitch
            mapped.nodes[node_id].update(
                pitch=musical_pitch.nameWithOctave,
                pitch_space=musical_pitch.ps,
                pitch_degree=degree_index,
                collection_rotation=collection_rotation,
                octave_displacement=octave_displacement,
                onset_tick=onset_tick,
                duration_ticks=1,
                ring_phrase=minor_index,
            )
            traversal.append(node_id)
            onset_tick += 1
        onset_tick += ring_rest_ticks[minor_index]

    if any(not mapped.has_edge(start, end) for start, end in zip(traversal, traversal[1:])):
        raise RuntimeError("surface traversal left the torus mesh")
    mapped.graph.update(
        pitch_collection=parsed_pitch_classes,
        coordinate_pitch_mapping="major angle -> degree; minor angle -> rotation/register",
        traversal="minor-ring serpentine",
        traversal_path=tuple(traversal),
        ring_rest_ticks=tuple(ring_rest_ticks),
        rhythm_subdivisions_per_quarter=8,
        total_ticks=onset_tick,
    )
    return mapped
