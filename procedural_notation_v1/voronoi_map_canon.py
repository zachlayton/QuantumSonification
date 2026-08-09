"""A twelve-voice adjacency canon derived from a centroidal Voronoi map."""

from __future__ import annotations

import math

import networkx as nx
from music21 import pitch

from procedural_notation_v1.density_matrix_canon import DEFAULT_FIXED_TRANSPOSITIONS
from procedural_notation_v1.surface_mesh_ensemble import _nearest_registered_pitch
from procedural_notation_v1.surface_mesh_polyphony import TORUS_PENTATONIC_SET


def build_voronoi_adjacency_canon(
    voronoi_graph: nx.Graph,
    cycles: int = 5,
) -> nx.DiGraph:
    """Turn each Voronoi cell and its neighbors into a local canonic orbit."""
    if voronoi_graph.graph.get("site_count") != 12:
        raise ValueError("Voronoi adjacency canon requires twelve regions")
    if isinstance(cycles, bool) or not isinstance(cycles, int) or cycles != 5:
        raise ValueError("this study uses five cycles, one per fixed transposition")
    if not nx.is_connected(voronoi_graph):
        raise ValueError("Voronoi region graph must be connected")

    areas = [data["normalized_area"] for _, data in voronoi_graph.nodes(data=True)]
    area_min = min(areas)
    area_max = max(areas)
    regions_by_area = sorted(
        voronoi_graph.nodes,
        key=lambda node_id: (
            voronoi_graph.nodes[node_id]["normalized_area"],
            node_id,
        ),
    )
    area_levels = {
        node_id: 1 + min(2, rank * 3 // len(regions_by_area))
        for rank, node_id in enumerate(regions_by_area)
    }
    maximum_boundary = max(
        data["shared_boundary"] for _, _, data in voronoi_graph.edges(data=True)
    )
    angular_order = sorted(
        voronoi_graph.nodes,
        key=lambda node_id: math.atan2(
            voronoi_graph.nodes[node_id]["site"][1] - 0.5,
            voronoi_graph.nodes[node_id]["site"][0] - 0.5,
        ),
    )
    entry_rank = {node_id: rank for rank, node_id in enumerate(angular_order)}

    canon = nx.DiGraph()
    voices = []
    for home_region in angular_order:
        voice_id = f"region_{home_region + 1:02d}"
        voices.append(voice_id)
        neighbors = sorted(
            voronoi_graph.neighbors(home_region),
            key=lambda neighbor: math.atan2(
                voronoi_graph.nodes[neighbor]["site"][1]
                - voronoi_graph.nodes[home_region]["site"][1],
                voronoi_graph.nodes[neighbor]["site"][0]
                - voronoi_graph.nodes[home_region]["site"][0],
            ),
        )
        _add_region_voice(
            canon,
            voronoi_graph,
            voice_id=voice_id,
            home_region=home_region,
            neighbors=neighbors,
            entry_index=entry_rank[home_region] * 2,
            cycles=cycles,
            area_min=area_min,
            area_max=area_max,
            area_levels=area_levels,
            maximum_boundary=maximum_boundary,
        )

    voice_end_ticks = {}
    for voice_id in voices:
        events = [data for _, data in canon.nodes(data=True) if data["voice"] == voice_id]
        voice_end_ticks[voice_id] = max(
            data["onset_tick"] + data["duration_ticks"] for data in events
        )
    canon.graph.update(
        geometry="centroidal_voronoi_12_voice_adjacency_canon",
        source_geometry=voronoi_graph.graph.get("geometry"),
        voices=tuple(voices),
        voice_count=12,
        cycles=cycles,
        pitch_collection=TORUS_PENTATONIC_SET,
        fixed_transpositions=DEFAULT_FIXED_TRANSPOSITIONS,
        voice_end_ticks=voice_end_ticks,
        rhythm_subdivisions_per_quarter=8,
        total_ticks=max(voice_end_ticks.values()),
    )
    return canon


def _add_region_voice(
    destination: nx.DiGraph,
    source: nx.Graph,
    voice_id: str,
    home_region: int,
    neighbors: list[int],
    entry_index: int,
    cycles: int,
    area_min: float,
    area_max: float,
    area_levels: dict[int, int],
    maximum_boundary: float,
) -> None:
    onset_tick = entry_index
    previous_event = None
    for cycle_index in range(cycles):
        ordered_neighbors = (
            neighbors if (home_region + cycle_index) % 2 == 0 else list(reversed(neighbors))
        )
        motif = [home_region]
        for neighbor in ordered_neighbors:
            motif.extend((neighbor, home_region))
        transposition = DEFAULT_FIXED_TRANSPOSITIONS[cycle_index]
        for motif_index, visited_region in enumerate(motif):
            region_data = source.nodes[visited_region]
            normalized_area = (
                (region_data["normalized_area"] - area_min) / (area_max - area_min)
                if area_max > area_min
                else 0.5
            )
            repetition_count = area_levels[visited_region]
            x, y = region_data["site"]
            home_x, home_y = source.nodes[home_region]["site"]
            distance_from_home = math.hypot(x - home_x, y - home_y)
            degree_index = (
                int(3.0 * x + 2.0 * y) + cycle_index
            ) % len(TORUS_PENTATONIC_SET)
            transposed_pitch_class = pitch.Pitch(
                TORUS_PENTATONIC_SET[degree_index]
            ).transpose(transposition).name
            register_target = 48.0 + 24.0 * y + 10.0 * distance_from_home
            musical_pitch = _nearest_registered_pitch(
                transposed_pitch_class,
                register_target,
            )
            if visited_region == home_region:
                boundary_strength = 1.0
            else:
                boundary_strength = (
                    source.edges[home_region, visited_region]["shared_boundary"]
                    / maximum_boundary
                )
            rest_after = int(boundary_strength < 0.9)
            for repetition_index in range(repetition_count):
                event_id = (
                    voice_id,
                    cycle_index,
                    motif_index,
                    repetition_index,
                )
                destination.add_node(
                    event_id,
                    pitch=musical_pitch.nameWithOctave,
                    pitch_space=musical_pitch.ps,
                    onset_tick=onset_tick,
                    duration_ticks=1,
                    voice=voice_id,
                    home_region=home_region,
                    visited_region=visited_region,
                    cycle_index=cycle_index,
                    canon_entry_index=entry_index,
                    transposition_semitones=transposition,
                    degree_index=degree_index,
                    normalized_area=normalized_area,
                    repetition_count=repetition_count,
                    repetition_index=repetition_index,
                    distance_from_home=distance_from_home,
                    boundary_strength=boundary_strength,
                    rest_after_ticks=(
                        rest_after if repetition_index == repetition_count - 1 else 0
                    ),
                )
                if previous_event is not None:
                    destination.add_edge(previous_event, event_id)
                previous_event = event_id
                onset_tick += 1
            onset_tick += rest_after

        if cycle_index < cycles - 1:
            cycle_rest = 1 + round(2.0 * source.nodes[home_region]["compactness"])
            destination.nodes[previous_event]["cycle_rest_after_ticks"] = cycle_rest
            onset_tick += cycle_rest
