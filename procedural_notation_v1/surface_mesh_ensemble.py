"""Large ensembles whose independent voices constitute a surface mesh."""

from __future__ import annotations

import math

import networkx as nx
from music21 import note

from procedural_notation_v1.surface_mesh_graph import TORUS_HEXATONIC_SET
from procedural_notation_v1.surface_mesh_polyphony import TORUS_PENTATONIC_SET


def build_torus_32_voice_mesh(torus_mesh: nx.Graph) -> nx.DiGraph:
    """Return 16 ring voices crossed with 16 meridian voices.

    At time slice ``t``, the sounding vertices satisfy ``i + j = t (mod 16)``.
    Consequently, each surface vertex is sounded simultaneously by its ring
    voice and its meridian voice: the vertical sonorities are literal mesh
    intersections rather than two paths laid over one another.
    """
    major_segments = torus_mesh.graph.get("major_segments")
    minor_segments = torus_mesh.graph.get("minor_segments")
    if major_segments != 16 or minor_segments != 16:
        raise ValueError("32-voice torus ensemble requires a 16 by 16 surface mesh")

    ensemble = nx.DiGraph()
    voices = []
    for minor_index in range(16):
        voice_id = f"A_ring_{minor_index + 1:02d}"
        voices.append(voice_id)
        previous_event = None
        for time_slice in range(16):
            major_index = (time_slice - minor_index) % 16
            source_node = (minor_index, major_index)
            event_id = (voice_id, time_slice)
            pitch_class_index = (
                int(major_index * len(TORUS_HEXATONIC_SET) / 16) + minor_index
            ) % len(TORUS_HEXATONIC_SET)
            target = _coordinate_register_target(
                torus_mesh,
                source_node,
                family="ring",
            )
            musical_pitch = _nearest_registered_pitch(
                TORUS_HEXATONIC_SET[pitch_class_index],
                target,
            )
            ensemble.add_node(
                event_id,
                pitch=musical_pitch.nameWithOctave,
                pitch_space=musical_pitch.ps,
                onset_tick=2 * time_slice,
                duration_ticks=1,
                source_vertex=source_node,
                voice=voice_id,
                voice_family="ring",
                fixed_coordinate_index=minor_index,
                moving_coordinate_index=major_index,
                time_slice=time_slice,
                pitch_degree=pitch_class_index,
                register_target=target,
                octave_displacement=musical_pitch.octave - 4,
            )
            if previous_event is not None:
                ensemble.add_edge(previous_event, event_id)
            previous_event = event_id

    for major_index in range(16):
        voice_id = f"B_meridian_{major_index + 1:02d}"
        voices.append(voice_id)
        previous_event = None
        for time_slice in range(16):
            minor_index = (time_slice - major_index) % 16
            source_node = (minor_index, major_index)
            event_id = (voice_id, time_slice)
            pitch_class_index = (
                int(minor_index * len(TORUS_PENTATONIC_SET) / 16) + major_index
            ) % len(TORUS_PENTATONIC_SET)
            target = _coordinate_register_target(
                torus_mesh,
                source_node,
                family="meridian",
            )
            musical_pitch = _nearest_registered_pitch(
                TORUS_PENTATONIC_SET[pitch_class_index],
                target,
            )
            ensemble.add_node(
                event_id,
                pitch=musical_pitch.nameWithOctave,
                pitch_space=musical_pitch.ps,
                onset_tick=2 * time_slice,
                duration_ticks=1,
                source_vertex=source_node,
                voice=voice_id,
                voice_family="meridian",
                fixed_coordinate_index=major_index,
                moving_coordinate_index=minor_index,
                time_slice=time_slice,
                pitch_degree=pitch_class_index,
                register_target=target,
                octave_displacement=musical_pitch.octave - 4,
            )
            if previous_event is not None:
                ensemble.add_edge(previous_event, event_id)
            previous_event = event_id

    _validate_mesh_intersections(ensemble, torus_mesh)
    ensemble.graph.update(
        geometry="quartic_torus_32_voice_mesh",
        source_geometry=torus_mesh.graph.get("geometry"),
        source_eigenmode=torus_mesh.graph.get("eigenmode_index"),
        source_eigenvalue=torus_mesh.graph.get("eigenvalue"),
        voices=tuple(voices),
        voice_count=32,
        ring_voice_count=16,
        meridian_voice_count=16,
        ring_pitch_collection=TORUS_HEXATONIC_SET,
        meridian_pitch_collection=TORUS_PENTATONIC_SET,
        time_slicing="i + j = t (mod 16)",
        rhythm_subdivisions_per_quarter=8,
        total_ticks=32,
    )
    return ensemble


def _coordinate_register_target(
    graph: nx.Graph,
    node_id: tuple[int, int],
    family: str,
) -> float:
    x, y, z = graph.nodes[node_id]["position"]
    major_radius = graph.graph["major_radius"]
    minor_radius = graph.graph["minor_radius"]
    normalized_height = z / minor_radius
    normalized_radial_offset = (math.hypot(x, y) - major_radius) / minor_radius
    if family == "ring":
        return 64.0 + 18.0 * normalized_height + 5.0 * normalized_radial_offset
    if family == "meridian":
        return 52.0 + 18.0 * normalized_height - 5.0 * normalized_radial_offset
    raise ValueError(f"unknown coordinate family {family!r}")


def _nearest_registered_pitch(pitch_class: str, target_pitch_space: float):
    candidates = [note.Note(f"{pitch_class}{octave}").pitch for octave in range(1, 8)]
    return min(candidates, key=lambda pitch: (abs(pitch.ps - target_pitch_space), pitch.ps))


def _validate_mesh_intersections(ensemble: nx.DiGraph, source: nx.Graph) -> None:
    events_by_vertex: dict[tuple[int, int], list[dict]] = {}
    for _, data in ensemble.nodes(data=True):
        events_by_vertex.setdefault(data["source_vertex"], []).append(data)
    if set(events_by_vertex) != set(source.nodes):
        raise RuntimeError("ensemble does not cover every surface vertex")
    for source_vertex, events in events_by_vertex.items():
        if len(events) != 2 or {event["voice_family"] for event in events} != {
            "ring",
            "meridian",
        }:
            raise RuntimeError(f"vertex {source_vertex!r} is not a two-family intersection")
        if len({event["onset_tick"] for event in events}) != 1:
            raise RuntimeError(f"vertex {source_vertex!r} is not simultaneous in both voices")
