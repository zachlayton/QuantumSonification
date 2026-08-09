"""Form-found cable-net surfaces inspired by Frei Otto's tensile structures."""

from __future__ import annotations

import math

import networkx as nx
import numpy as np


def build_tensile_saddle_mesh(
    rows: int = 16,
    columns: int = 16,
    span_x: float = 2.0,
    span_y: float = 2.0,
    rise: float = 0.9,
    eigenmode_index: int = 7,
) -> nx.Graph:
    """Return a harmonic four-anchor saddle represented as a cable net."""
    for name, value in (("rows", rows), ("columns", columns)):
        if isinstance(value, bool) or not isinstance(value, int) or value < 4:
            raise ValueError(f"{name} must be an integer of at least 4")
    for name, value in (("span_x", span_x), ("span_y", span_y), ("rise", rise)):
        if not math.isfinite(value) or value <= 0.0:
            raise ValueError(f"{name} must be a finite positive number")

    node_count = rows * columns
    if (
        isinstance(eigenmode_index, bool)
        or not isinstance(eigenmode_index, int)
        or not 0 < eigenmode_index < node_count
    ):
        raise ValueError("eigenmode_index must select a nonconstant mesh mode")

    graph = nx.Graph()
    mixed_derivative = rise / (span_x * span_y)
    for row in range(rows):
        v = -1.0 + 2.0 * row / (rows - 1)
        for column in range(columns):
            u = -1.0 + 2.0 * column / (columns - 1)
            x = span_x * u
            y = span_y * v
            z = rise * u * v
            dz_dx = rise * v / span_x
            dz_dy = rise * u / span_y
            gaussian_curvature = -(mixed_derivative * mixed_derivative) / (
                1.0 + dz_dx * dz_dx + dz_dy * dz_dy
            ) ** 2
            graph.add_node(
                (row, column),
                position=(x, y, z),
                u=u,
                v=v,
                gaussian_curvature=gaussian_curvature,
                algebraic_residual=span_x * span_y * z - rise * x * y,
                boundary=row in (0, rows - 1) or column in (0, columns - 1),
                anchor=row in (0, rows - 1) and column in (0, columns - 1),
            )

    for row in range(rows):
        for column in range(columns):
            node_id = (row, column)
            if column + 1 < columns:
                graph.add_edge(
                    node_id,
                    (row, column + 1),
                    cable_direction="warp",
                )
            if row + 1 < rows:
                graph.add_edge(
                    node_id,
                    (row + 1, column),
                    cable_direction="weft",
                )

    for start, end, data in graph.edges(data=True):
        start_position = np.asarray(graph.nodes[start]["position"])
        end_position = np.asarray(graph.nodes[end]["position"])
        length = float(np.linalg.norm(end_position - start_position))
        data["length"] = length
        data["tension_coupling"] = 1.0 / length

    node_order = sorted(graph.nodes)
    adjacency = nx.to_numpy_array(
        graph,
        nodelist=node_order,
        weight="tension_coupling",
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
        geometry="harmonic_tensile_saddle_cable_net",
        dimension=3,
        topology="disk",
        rows=rows,
        columns=columns,
        span_x=float(span_x),
        span_y=float(span_y),
        rise=float(rise),
        anchor_count=4,
        euler_characteristic=1,
        implicit_polynomial="span_x*span_y*z-rise*x*y",
        form_finding="discrete harmonic cable net with alternating corner heights",
        eigenmode_index=eigenmode_index,
        eigenvalue=float(eigenvalues[eigenmode_index]),
        node_order=tuple(node_order),
    )
    return graph
