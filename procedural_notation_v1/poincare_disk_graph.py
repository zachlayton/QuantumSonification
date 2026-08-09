"""Finite hyperbolic meshes embedded in the Poincare disk."""

from __future__ import annotations

import math

import networkx as nx
import numpy as np


DEFAULT_RING_COUNTS = (1, 8, 16, 24)
DEFAULT_HYPERBOLIC_RADII = (0.0, 0.8, 1.6, 2.4)


def build_poincare_disk_graph(
    ring_counts: tuple[int, ...] = DEFAULT_RING_COUNTS,
    hyperbolic_radii: tuple[float, ...] = DEFAULT_HYPERBOLIC_RADII,
    eigenmode_index: int = 7,
) -> nx.Graph:
    """Return a radially expanding graph with true hyperbolic edge lengths."""
    if ring_counts != DEFAULT_RING_COUNTS:
        raise ValueError("this first Poincare study uses rings of 1, 8, 16, and 24 nodes")
    if len(hyperbolic_radii) != len(ring_counts):
        raise ValueError("hyperbolic_radii must provide one value per ring")
    if hyperbolic_radii[0] != 0.0 or any(
        not math.isfinite(value) or value < 0.0
        for value in hyperbolic_radii
    ) or any(left >= right for left, right in zip(hyperbolic_radii, hyperbolic_radii[1:])):
        raise ValueError("hyperbolic radii must increase outward from zero")
    node_count = sum(ring_counts)
    if (
        isinstance(eigenmode_index, bool)
        or not isinstance(eigenmode_index, int)
        or not 0 < eigenmode_index < node_count
    ):
        raise ValueError("eigenmode_index must select a nonconstant graph mode")

    graph = nx.Graph()
    for ring_index, (count, hyperbolic_radius) in enumerate(
        zip(ring_counts, hyperbolic_radii, strict=True)
    ):
        euclidean_radius = math.tanh(hyperbolic_radius / 2.0)
        for angular_index in range(count):
            angle = 0.0 if count == 1 else math.tau * angular_index / count
            graph.add_node(
                (ring_index, angular_index),
                position=(
                    euclidean_radius * math.cos(angle),
                    euclidean_radius * math.sin(angle),
                ),
                ring_index=ring_index,
                angular_index=angular_index,
                angular_coordinate=angle,
                euclidean_radius=euclidean_radius,
                hyperbolic_radius=hyperbolic_radius,
            )

    graph.add_edges_from(
        ((0, 0), (1, angular_index))
        for angular_index in range(ring_counts[1])
    )
    for ring_index in range(1, len(ring_counts)):
        count = ring_counts[ring_index]
        for angular_index in range(count):
            graph.add_edge(
                (ring_index, angular_index),
                (ring_index, (angular_index + 1) % count),
                edge_role="circumferential",
            )
    for outer_ring in range(2, len(ring_counts)):
        inner_ring = outer_ring - 1
        inner_count = ring_counts[inner_ring]
        outer_count = ring_counts[outer_ring]
        for outer_index in range(outer_count):
            scaled_index = outer_index * inner_count / outer_count
            inner_indices = {
                math.floor(scaled_index) % inner_count,
                math.ceil(scaled_index) % inner_count,
            }
            for inner_index in inner_indices:
                graph.add_edge(
                    (inner_ring, inner_index),
                    (outer_ring, outer_index),
                    edge_role="radial",
                )

    for start, end, data in graph.edges(data=True):
        start_position = graph.nodes[start]["position"]
        end_position = graph.nodes[end]["position"]
        hyperbolic_length = poincare_distance(start_position, end_position)
        data.setdefault("edge_role", "radial")
        data["hyperbolic_length"] = hyperbolic_length
        data["coupling"] = 1.0 / hyperbolic_length

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
        geometry="poincare_disk_hyperbolic_rings",
        dimension=2,
        curvature=-1.0,
        topology="disk",
        ring_counts=ring_counts,
        hyperbolic_radii=hyperbolic_radii,
        euclidean_radii=tuple(math.tanh(value / 2.0) for value in hyperbolic_radii),
        eigenmode_index=eigenmode_index,
        eigenvalue=float(eigenvalues[eigenmode_index]),
        node_order=tuple(node_order),
    )
    return graph


def poincare_distance(
    left: tuple[float, float],
    right: tuple[float, float],
) -> float:
    """Return distance in the unit-disk model with curvature minus one."""
    left_vector = np.asarray(left, dtype=float)
    right_vector = np.asarray(right, dtype=float)
    numerator = 2.0 * float(np.sum((left_vector - right_vector) ** 2))
    denominator = (
        (1.0 - float(np.sum(left_vector * left_vector)))
        * (1.0 - float(np.sum(right_vector * right_vector)))
    )
    return math.acosh(1.0 + numerator / denominator)
