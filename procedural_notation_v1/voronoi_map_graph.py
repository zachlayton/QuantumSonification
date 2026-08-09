"""Discrete centroidal Voronoi maps with region-level adjacency graphs."""

from __future__ import annotations

import math

import networkx as nx
import numpy as np


def build_centroidal_voronoi_map(
    width: int = 24,
    height: int = 24,
    site_count: int = 12,
    lloyd_iterations: int = 8,
) -> nx.Graph:
    """Return a lightly regularized twelve-region planar Voronoi graph."""
    for name, value, minimum in (
        ("width", width, 8),
        ("height", height, 8),
        ("lloyd_iterations", lloyd_iterations, 0),
    ):
        if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
            raise ValueError(f"{name} must be an integer of at least {minimum}")
    if site_count != 12:
        raise ValueError("this first Voronoi study requires exactly twelve sites")

    grid_positions = np.asarray(
        [
            ((column + 0.5) / width, (row + 0.5) / height)
            for row in range(height)
            for column in range(width)
        ],
        dtype=float,
    )
    sites = _initial_twelve_sites()
    density_weights = 1.0 + 0.45 * (
        np.cos(math.tau * grid_positions[:, 0])
        * np.cos(math.tau * grid_positions[:, 1])
    )
    for _ in range(lloyd_iterations):
        assignments = _nearest_site_assignments(grid_positions, sites)
        next_sites = sites.copy()
        for site_index in range(site_count):
            members = grid_positions[assignments == site_index]
            if len(members):
                next_sites[site_index] = np.average(
                    members,
                    axis=0,
                    weights=density_weights[assignments == site_index],
                )
        sites = next_sites
    assignments = _nearest_site_assignments(grid_positions, sites).reshape(height, width)

    region_graph = nx.Graph()
    region_members = {}
    perimeter_lengths = [0.0] * site_count
    for site_index in range(site_count):
        member_indices = np.argwhere(assignments == site_index)
        members = tuple((int(row), int(column)) for row, column in member_indices)
        if not members:
            raise RuntimeError(f"Voronoi site {site_index} has an empty region")
        region_members[site_index] = members
        centroid = np.asarray(
            [((column + 0.5) / width, (row + 0.5) / height) for row, column in members]
        ).mean(axis=0)
        region_graph.add_node(
            site_index,
            site=(float(sites[site_index, 0]), float(sites[site_index, 1])),
            centroid=(float(centroid[0]), float(centroid[1])),
            grid_area=len(members),
            normalized_area=len(members) / (width * height),
            members=members,
        )

    shared_boundaries: dict[tuple[int, int], float] = {}
    for row in range(height):
        for column in range(width):
            region = int(assignments[row, column])
            for delta_row, delta_column, side_length in (
                (-1, 0, 1.0 / width),
                (1, 0, 1.0 / width),
                (0, -1, 1.0 / height),
                (0, 1, 1.0 / height),
            ):
                neighbor_row = row + delta_row
                neighbor_column = column + delta_column
                if not 0 <= neighbor_row < height or not 0 <= neighbor_column < width:
                    perimeter_lengths[region] += side_length
                    continue
                neighbor_region = int(assignments[neighbor_row, neighbor_column])
                if neighbor_region == region:
                    continue
                perimeter_lengths[region] += side_length
                edge = tuple(sorted((region, neighbor_region)))
                shared_boundaries[edge] = shared_boundaries.get(edge, 0.0) + side_length / 2.0

    for site_index in range(site_count):
        area = region_graph.nodes[site_index]["normalized_area"]
        perimeter = perimeter_lengths[site_index]
        region_graph.nodes[site_index].update(
            perimeter=perimeter,
            compactness=4.0 * math.pi * area / (perimeter * perimeter),
        )
    for (left, right), shared_boundary in shared_boundaries.items():
        left_site = np.asarray(region_graph.nodes[left]["site"])
        right_site = np.asarray(region_graph.nodes[right]["site"])
        region_graph.add_edge(
            left,
            right,
            shared_boundary=float(shared_boundary),
            site_distance=float(np.linalg.norm(right_site - left_site)),
        )

    region_graph.graph.update(
        geometry="centroidal_voronoi_map",
        dimension=2,
        topology="disk",
        width=width,
        height=height,
        site_count=site_count,
        lloyd_iterations=lloyd_iterations,
        assignments=tuple(tuple(int(value) for value in row) for row in assignments),
        sites=tuple(tuple(float(value) for value in site) for site in sites),
        regularization="discrete Lloyd relaxation",
        sampling_density="1 + 0.45*cos(2*pi*x)*cos(2*pi*y)",
    )
    return region_graph


def _initial_twelve_sites() -> np.ndarray:
    sites = []
    for row in range(3):
        for column in range(4):
            index = row * 4 + column
            x = (column + 0.5) / 4.0 + 0.025 * math.sin(1.7 * index)
            y = (row + 0.5) / 3.0 + 0.025 * math.cos(1.3 * index)
            sites.append((x, y))
    return np.asarray(sites, dtype=float)


def _nearest_site_assignments(points: np.ndarray, sites: np.ndarray) -> np.ndarray:
    squared_distances = np.sum(
        (points[:, np.newaxis, :] - sites[np.newaxis, :, :]) ** 2,
        axis=2,
    )
    return np.argmin(squared_distances, axis=1)
