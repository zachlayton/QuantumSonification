"""Map a 3D dodecahedron into 24-EDO pitch and quantized musical time."""

from __future__ import annotations

import math

import networkx as nx
from music21 import pitch


TEMPORAL_AXIS = (1.0, math.sqrt(2.0), (1.0 + math.sqrt(5.0)) / 2.0)
ROTATED_PENTATONIC_NAMES = (
    ("C", "D", "E", "G", "A"),
    ("C", "D", "E", "G", "A"),
    ("C", "D", "E", "G", "A"),
)


def apply_dodecahedron_mapping(
    graph: nx.Graph,
    measures: int = 4,
    beats_per_measure: int = 4,
    ticks_per_quarter: int = 8,
    pitch_divisions: int = 24,
    root_pitch_space: float = 60.0,
    minimum_onset_spacing_ticks: int = 2,
) -> nx.Graph:
    """Return a graph whose 3D coordinates control pitch and onset time."""
    if graph.graph.get("geometry") != "regular_dodecahedron":
        raise ValueError("graph must be a regular dodecahedron")
    for name, value in (
        ("measures", measures),
        ("beats_per_measure", beats_per_measure),
        ("ticks_per_quarter", ticks_per_quarter),
        ("pitch_divisions", pitch_divisions),
        ("minimum_onset_spacing_ticks", minimum_onset_spacing_ticks),
    ):
        if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
            raise ValueError(f"{name} must be a positive integer")

    mapped = graph.copy()
    total_ticks = measures * beats_per_measure * ticks_per_quarter
    positions = nx.get_node_attributes(mapped, "position")
    projections = {
        node_id: sum(coordinate * axis for coordinate, axis in zip(position, TEMPORAL_AXIS, strict=True))
        for node_id, position in positions.items()
    }
    projection_min = min(projections.values())
    projection_max = max(projections.values())
    z_values = [position[2] for position in positions.values()]
    z_min, z_max = min(z_values), max(z_values)
    x_values = [position[0] for position in positions.values()]
    x_min, x_max = min(x_values), max(x_values)

    preferred_ticks = {
        node_id: round(
            (projection - projection_min)
            / (projection_max - projection_min)
            * (total_ticks - 1)
        )
        for node_id, projection in projections.items()
    }
    used_ticks: set[int] = set()
    assigned_ticks: dict[int, int] = {}
    for node_id in sorted(preferred_ticks, key=lambda item: (preferred_ticks[item], item)):
        assigned = _nearest_spaced_tick(
            preferred_ticks[node_id],
            used_ticks,
            total_ticks,
            minimum_onset_spacing_ticks,
        )
        assigned_ticks[node_id] = assigned
        used_ticks.add(assigned)

    nodes_by_onset = sorted(assigned_ticks, key=lambda item: assigned_ticks[item])
    duration_ticks: dict[int, int] = {}
    preferred_duration_ticks: dict[int, int] = {}
    for sequence_index, node_id in enumerate(nodes_by_onset):
        normalized_x = (positions[node_id][0] - x_min) / (x_max - x_min)
        preferred_duration = 1 + round(normalized_x * (ticks_per_quarter - 1))
        next_onset = (
            assigned_ticks[nodes_by_onset[sequence_index + 1]]
            if sequence_index + 1 < len(nodes_by_onset)
            else total_ticks
        )
        available_before_rest = max(1, next_onset - assigned_ticks[node_id] - 1)
        preferred_duration_ticks[node_id] = preferred_duration
        duration_ticks[node_id] = min(preferred_duration, available_before_rest)

    for node_id, position in positions.items():
        normalized_height = (position[2] - z_min) / (z_max - z_min)
        pitch_step = round(normalized_height * pitch_divisions)
        pitch_space = root_pitch_space + pitch_step * 12.0 / pitch_divisions
        musical_pitch = pitch.Pitch()
        musical_pitch.ps = pitch_space
        mapped.nodes[node_id].update(
            time_projection=projections[node_id],
            preferred_onset_tick=preferred_ticks[node_id],
            onset_tick=assigned_ticks[node_id],
            duration_projection=position[0],
            preferred_duration_ticks=preferred_duration_ticks[node_id],
            duration_ticks=duration_ticks[node_id],
            pitch_step=pitch_step,
            cents_from_root=pitch_step * 1200.0 / pitch_divisions,
            pitch_space=pitch_space,
            pitch=musical_pitch.nameWithOctave,
        )

    mapped.graph.update(
        pitch_system=f"{pitch_divisions}-EDO",
        pitch_divisions=pitch_divisions,
        root_pitch_space=float(root_pitch_space),
        temporal_axis=TEMPORAL_AXIS,
        measures=measures,
        beats_per_measure=beats_per_measure,
        rhythm_subdivisions_per_quarter=ticks_per_quarter,
        rhythm_note_value=4 * ticks_per_quarter,
        total_ticks=total_ticks,
        minimum_onset_spacing_ticks=minimum_onset_spacing_ticks,
    )
    return mapped


def apply_polyphonic_dodecahedron_mapping(
    graph: nx.Graph,
    measures: int = 6,
    beats_per_measure: int = 4,
    ticks_per_quarter: int = 8,
    pitch_divisions: int = 12,
    pentatonic_intervals: tuple[int, int, int, int, int] = (0, 2, 4, 7, 9),
    base_pitch_space: float = 36.0,
    voice_degree_rotations: tuple[int, int, int] = (0, 1, 2),
    voice_phase_offsets_ticks: tuple[int, int, int] = (0, 3, 7),
    minimum_onset_spacing_ticks: int = 2,
) -> nx.Graph:
    """Map the dodecahedron to three independent, overlapping sound fields."""
    if graph.graph.get("geometry") != "regular_dodecahedron":
        raise ValueError("graph must be a regular dodecahedron")
    if pitch_divisions != 12:
        raise ValueError("the polyphonic study currently requires 12-EDO")
    if (
        len(pentatonic_intervals) != 5
        or len(set(pentatonic_intervals)) != 5
        or any(
            isinstance(interval, bool)
            or not isinstance(interval, int)
            or not 0 <= interval < 12
            for interval in pentatonic_intervals
        )
    ):
        raise ValueError("pentatonic_intervals must contain five distinct 12-EDO steps")
    if not math.isfinite(base_pitch_space):
        raise ValueError("base_pitch_space must be finite")
    if len(voice_degree_rotations) != 3 or any(
        isinstance(rotation, bool) or not isinstance(rotation, int)
        for rotation in voice_degree_rotations
    ):
        raise ValueError("voice_degree_rotations must contain exactly three integers")
    if len(voice_phase_offsets_ticks) != 3 or any(
        isinstance(offset, bool) or not isinstance(offset, int)
        for offset in voice_phase_offsets_ticks
    ):
        raise ValueError("voice_phase_offsets_ticks must contain exactly three integers")

    total_ticks = measures * beats_per_measure * ticks_per_quarter
    positions = nx.get_node_attributes(graph, "position")
    pentatonic_degrees, faces = _pentagonal_face_coloring(graph)
    octave_layers: dict[int, int] = {}
    for degree in range(5):
        degree_nodes = sorted(
            (node_id for node_id in graph if pentatonic_degrees[node_id] == degree),
            key=lambda node_id: (
                positions[node_id][2],
                positions[node_id][1],
                positions[node_id][0],
                node_id,
            ),
        )
        if len(degree_nodes) != 4:
            raise RuntimeError("each pentatonic degree must occur at four vertices")
        octave_layers.update({node_id: layer for layer, node_id in enumerate(degree_nodes)})

    time_axes = tuple(_rotate_axis_about_z(TEMPORAL_AXIS, voice * math.tau / 3.0) for voice in range(3))
    duration_axes = tuple(_rotate_axis_about_z((1.0, 0.0, 0.0), voice * math.tau / 3.0) for voice in range(3))
    all_time_projections = [
        sum(coordinate * axis for coordinate, axis in zip(position, time_axis, strict=True))
        for position in positions.values()
        for time_axis in time_axes
    ]
    projection_min, projection_max = min(all_time_projections), max(all_time_projections)
    all_duration_projections = [
        sum(coordinate * axis for coordinate, axis in zip(position, duration_axis, strict=True))
        for position in positions.values()
        for duration_axis in duration_axes
    ]
    duration_min = min(all_duration_projections)
    duration_max = max(all_duration_projections)
    maximum_phase_offset = max(voice_phase_offsets_ticks)
    timeline_margin = ticks_per_quarter
    projection_tick_min = timeline_margin
    projection_tick_max = total_ticks - timeline_margin - maximum_phase_offset - 1
    if projection_tick_max <= projection_tick_min:
        raise ValueError("the score duration is too short for the voice phase offsets")

    mapped = nx.Graph()
    mapped.graph.update(graph.graph)
    for voice in range(3):
        projections = {
            node_id: sum(
                coordinate * axis
                for coordinate, axis in zip(position, time_axes[voice], strict=True)
            )
            for node_id, position in positions.items()
        }
        preferred_ticks = {
            node_id: round(
                projection_tick_min
                + (projection - projection_min)
                / (projection_max - projection_min)
                * (projection_tick_max - projection_tick_min)
            )
            + voice_phase_offsets_ticks[voice]
            for node_id, projection in projections.items()
        }
        assigned_ticks: dict[int, int] = {}
        used_ticks: set[int] = set()
        for node_id in sorted(graph, key=lambda item: (preferred_ticks[item], item)):
            assigned = _nearest_spaced_tick(
                preferred_ticks[node_id],
                used_ticks,
                total_ticks,
                minimum_onset_spacing_ticks,
            )
            assigned_ticks[node_id] = assigned
            used_ticks.add(assigned)

        duration_projections = {
            node_id: sum(
                coordinate * axis
                for coordinate, axis in zip(position, duration_axes[voice], strict=True)
            )
            for node_id, position in positions.items()
        }
        voice_nodes = sorted(graph, key=lambda item: assigned_ticks[item])
        duration_ticks: dict[int, int] = {}
        preferred_duration_ticks: dict[int, int] = {}
        for sequence_index, node_id in enumerate(voice_nodes):
            normalized_duration = (
                duration_projections[node_id] - duration_min
            ) / (duration_max - duration_min)
            next_onset = (
                assigned_ticks[voice_nodes[sequence_index + 1]]
                if sequence_index + 1 < len(voice_nodes)
                else total_ticks
            )
            available = max(1, next_onset - assigned_ticks[node_id])
            sound_ratio = 0.35 + 0.30 * normalized_duration
            preferred_duration = max(1, round(available * sound_ratio))
            available_before_rest = max(1, available - 1)
            preferred_duration_ticks[node_id] = preferred_duration
            duration_ticks[node_id] = min(preferred_duration, available_before_rest)

        for source_vertex, position in positions.items():
            event_id = (voice, source_vertex)
            pentatonic_degree = pentatonic_degrees[source_vertex]
            voice_degree_rotation = voice_degree_rotations[voice] % 5
            sounding_degree = (pentatonic_degree + voice_degree_rotation) % 5
            pitch_class_interval = pentatonic_intervals[sounding_degree]
            octave_layer = octave_layers[source_vertex]
            pitch_space = (
                base_pitch_space
                + 12 * octave_layer
                + pitch_class_interval
            )
            musical_pitch = pitch.Pitch()
            musical_pitch.ps = pitch_space
            if pentatonic_intervals == (0, 2, 4, 7, 9):
                spelled_name = ROTATED_PENTATONIC_NAMES[voice][sounding_degree]
                spelled_octave = int(pitch_space // 12) - 1
                musical_pitch = pitch.Pitch(f"{spelled_name}{spelled_octave}")
                if musical_pitch.ps != pitch_space:
                    raise RuntimeError("pentatonic spelling changed pitch space")
            mapped.add_node(
                event_id,
                **graph.nodes[source_vertex],
                source_vertex=source_vertex,
                voice=voice,
                time_projection=projections[source_vertex],
                preferred_onset_tick=preferred_ticks[source_vertex],
                onset_tick=assigned_ticks[source_vertex],
                duration_projection=duration_projections[source_vertex],
                preferred_duration_ticks=preferred_duration_ticks[source_vertex],
                duration_ticks=duration_ticks[source_vertex],
                pentatonic_degree=pentatonic_degree,
                voice_degree_rotation=voice_degree_rotation,
                sounding_degree=sounding_degree,
                pitch_class_interval=pitch_class_interval,
                octave_layer=octave_layer,
                pitch_space=pitch_space,
                pitch=musical_pitch.nameWithOctave,
            )
        for start, end, edge_data in graph.edges(data=True):
            mapped.add_edge(
                (voice, start),
                (voice, end),
                **edge_data,
                source_edge=(start, end),
            )

    mapped.graph.update(
        geometry="rotated_dodecahedron_event_field",
        source_geometry="regular_dodecahedron",
        spatial_node_count=graph.number_of_nodes(),
        event_node_count=mapped.number_of_nodes(),
        pitch_system="12-EDO",
        pitch_divisions=12,
        pitch_collection="major_pentatonic",
        pentatonic_intervals=pentatonic_intervals,
        base_pitch_space=float(base_pitch_space),
        pentagonal_faces=faces,
        voice_count=3,
        voice_assignment="three complete rotational projections",
        voice_degree_rotations=voice_degree_rotations,
        rotation_pitch_rule="cyclic permutation within one fixed pentatonic collection",
        voice_time_axes=time_axes,
        voice_duration_axes=duration_axes,
        voice_phase_offsets_ticks=voice_phase_offsets_ticks,
        measures=measures,
        beats_per_measure=beats_per_measure,
        rhythm_subdivisions_per_quarter=ticks_per_quarter,
        rhythm_note_value=4 * ticks_per_quarter,
        total_ticks=total_ticks,
        minimum_onset_spacing_ticks=minimum_onset_spacing_ticks,
    )
    return mapped


def _pentagonal_face_coloring(
    graph: nx.Graph,
) -> tuple[dict[int, int], tuple[tuple[int, ...], ...]]:
    """Color vertices so every pentagonal face contains degrees 0--4."""
    planar, embedding = nx.check_planarity(graph)
    if not planar:
        raise ValueError("graph must be planar")

    visited_half_edges: set[tuple[int, int]] = set()
    faces: list[tuple[int, ...]] = []
    for start, end in embedding.edges():
        if (start, end) in visited_half_edges:
            continue
        face = tuple(embedding.traverse_face(start, end, visited_half_edges))
        faces.append(_canonical_face(face))
    faces = sorted(set(faces))
    if len(faces) != 12 or any(len(face) != 5 for face in faces):
        raise RuntimeError("expected twelve pentagonal faces")

    face_clique_graph = nx.Graph()
    face_clique_graph.add_nodes_from(graph.nodes)
    for face in faces:
        for index, start in enumerate(face):
            for end in face[index + 1:]:
                face_clique_graph.add_edge(start, end)
    raw_colors = nx.coloring.greedy_color(
        face_clique_graph,
        strategy="saturation_largest_first",
    )
    if len(set(raw_colors.values())) != 5:
        raise RuntimeError("failed to find a five-color pentagonal-face mapping")

    reference_face = faces[0]
    color_to_degree = {
        raw_colors[node_id]: degree
        for degree, node_id in enumerate(reference_face)
    }
    degrees = {node_id: color_to_degree[color] for node_id, color in raw_colors.items()}
    if any({degrees[node_id] for node_id in face} != set(range(5)) for face in faces):
        raise RuntimeError("pentagonal face does not contain all five pitch degrees")
    return degrees, tuple(faces)


def _canonical_face(face: tuple[int, ...]) -> tuple[int, ...]:
    rotations = []
    for sequence in (face, tuple(reversed(face))):
        rotations.extend(
            sequence[index:] + sequence[:index]
            for index in range(len(sequence))
        )
    return min(rotations)


def _rotate_axis_about_z(
    axis: tuple[float, float, float],
    angle: float,
) -> tuple[float, float, float]:
    cosine = math.cos(angle)
    sine = math.sin(angle)
    x, y, z = axis
    return (
        x * cosine - y * sine,
        x * sine + y * cosine,
        z,
    )


def _nearest_spaced_tick(
    preferred: int,
    used_ticks: set[int],
    total_ticks: int,
    minimum_spacing: int,
) -> int:
    def is_available(candidate: int) -> bool:
        return 0 <= candidate < total_ticks and all(
            abs(candidate - used) >= minimum_spacing for used in used_ticks
        )

    for distance in range(total_ticks):
        candidates = (preferred,) if distance == 0 else (preferred - distance, preferred + distance)
        for candidate in candidates:
            if is_available(candidate):
                return candidate
    raise ValueError("the requested temporal grid cannot fit all graph nodes")
