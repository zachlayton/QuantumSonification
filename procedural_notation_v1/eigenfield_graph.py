"""Graph-Laplacian eigenfields for melodic line generation."""

from __future__ import annotations

import math
from typing import Sequence

import networkx as nx
import numpy as np
from music21 import note


DEFAULT_PITCH_LINE = ("C4", "D4", "E4", "G4", "A4")
OCTAVE_DISPLACED_HEXATONIC_LINE = ("C4", "D5", "E4", "F#5", "G4", "A5")


def build_laplacian_eigenfield_graph(
    rows: int = 8,
    columns: int = 8,
    mode_index: int = 7,
    horizontal_coupling: float = 1.0,
    vertical_coupling: float = math.sqrt(2.0),
) -> nx.Graph:
    """Return an anisotropic grid carrying one Laplacian eigenvector field."""
    for name, value in (("rows", rows), ("columns", columns)):
        if isinstance(value, bool) or not isinstance(value, int) or value < 2:
            raise ValueError(f"{name} must be an integer of at least 2")
    node_count = rows * columns
    if isinstance(mode_index, bool) or not isinstance(mode_index, int) or not 0 < mode_index < node_count:
        raise ValueError("mode_index must select a nonconstant graph mode")
    for name, value in (
        ("horizontal_coupling", horizontal_coupling),
        ("vertical_coupling", vertical_coupling),
    ):
        if not math.isfinite(value) or value <= 0.0:
            raise ValueError(f"{name} must be a finite positive number")

    graph = nx.grid_2d_graph(rows, columns)
    node_order = sorted(graph.nodes)
    for row, column in node_order:
        graph.nodes[row, column]["position"] = (float(column), float(rows - 1 - row))
    for start, end in graph.edges:
        same_row = start[0] == end[0]
        graph.edges[start, end]["coupling"] = (
            horizontal_coupling if same_row else vertical_coupling
        )

    adjacency = nx.to_numpy_array(graph, nodelist=node_order, weight="coupling", dtype=float)
    laplacian = np.diag(adjacency.sum(axis=1)) - adjacency
    eigenvalues, eigenvectors = np.linalg.eigh(laplacian)
    eigenfield = eigenvectors[:, mode_index].copy()
    anchor_index = int(np.argmax(np.abs(eigenfield)))
    if eigenfield[anchor_index] < 0.0:
        eigenfield *= -1.0

    for node_id, field_value in zip(node_order, eigenfield, strict=True):
        graph.nodes[node_id]["field_value"] = float(field_value)

    graph.graph.update(
        geometry="anisotropic_grid_eigenfield",
        dimension=2,
        rows=rows,
        columns=columns,
        horizontal_coupling=float(horizontal_coupling),
        vertical_coupling=float(vertical_coupling),
        eigenmode_index=mode_index,
        eigenvalue=float(eigenvalues[mode_index]),
        eigenvalues=tuple(float(value) for value in eigenvalues),
        node_order=tuple(node_order),
    )
    return graph


def serpentine_path(graph: nx.Graph) -> tuple[tuple[int, int], ...]:
    """Return a connected row-by-row scan through the grid."""
    rows = graph.graph.get("rows")
    columns = graph.graph.get("columns")
    if not isinstance(rows, int) or not isinstance(columns, int):
        raise ValueError("graph must define integer rows and columns")
    path = []
    for row in range(rows):
        column_order = range(columns) if row % 2 == 0 else range(columns - 1, -1, -1)
        path.extend((row, column) for column in column_order)
    if any(not graph.has_edge(start, end) for start, end in zip(path, path[1:])):
        raise RuntimeError("serpentine scan left the graph topology")
    return tuple(path)


def apply_eigenfield_line_mapping(
    graph: nx.Graph,
    pitches: Sequence[str] = DEFAULT_PITCH_LINE,
) -> nx.Graph:
    """Quantize the eigenfield into repeated pitches along a connected path."""
    if len(pitches) < 2:
        raise ValueError("pitches must contain at least two pitch names")
    parsed_pitches = tuple(note.Note(name).pitch for name in pitches)
    path = serpentine_path(graph)
    values = np.asarray([graph.nodes[node_id]["field_value"] for node_id in graph.nodes], dtype=float)
    field_min = float(values.min())
    field_max = float(values.max())
    if math.isclose(field_min, field_max):
        raise ValueError("eigenfield must have nonzero range")

    mapped = graph.copy()
    for onset_tick, node_id in enumerate(path):
        value = mapped.nodes[node_id]["field_value"]
        normalized = (value - field_min) / (field_max - field_min)
        pitch_band = min(len(parsed_pitches) - 1, int(normalized * len(parsed_pitches)))
        musical_pitch = parsed_pitches[pitch_band]
        mapped.nodes[node_id].update(
            normalized_field=float(normalized),
            pitch_band=pitch_band,
            pitch=musical_pitch.nameWithOctave,
            pitch_space=musical_pitch.ps,
            onset_tick=onset_tick,
            duration_ticks=1,
        )

    mapped.graph.update(
        pitch_collection=tuple(item.nameWithOctave for item in parsed_pitches),
        rhythm_subdivisions_per_quarter=8,
        rhythm_note_value=32,
        traversal="serpentine",
        traversal_path=path,
        total_ticks=len(path),
    )
    return mapped
