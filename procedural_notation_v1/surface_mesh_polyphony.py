"""Contrapuntal traversals of periodic surface meshes."""

from __future__ import annotations

import math
from typing import Sequence

import networkx as nx
from music21 import note

from procedural_notation_v1.surface_mesh_graph import (
    TORUS_HEXATONIC_SET,
    TORUS_RING_RESTS,
    apply_torus_hexatonic_mapping,
)


TORUS_PENTATONIC_SET = ("C", "D", "E", "G", "A")
TORUS_MERIDIAN_RESTS = (1, 2, 3, 2, 1, 3, 3, 1, 2, 3, 2, 1)


def build_torus_dual_cycle_polyphony(
    torus_mesh: nx.Graph,
    major_cycle_pitches: Sequence[str] = TORUS_HEXATONIC_SET,
    minor_cycle_pitches: Sequence[str] = TORUS_PENTATONIC_SET,
    major_cycle_rests: Sequence[int] = TORUS_RING_RESTS,
    minor_cycle_rests: Sequence[int] = TORUS_MERIDIAN_RESTS,
) -> nx.DiGraph:
    """Read the two independent torus cycles as simultaneous musical voices."""
    major_segments = torus_mesh.graph.get("major_segments")
    minor_segments = torus_mesh.graph.get("minor_segments")
    if not isinstance(major_segments, int) or not isinstance(minor_segments, int):
        raise ValueError("torus_mesh must define major and minor segment counts")
    if len(minor_cycle_pitches) != 5:
        raise ValueError("minor-cycle voice requires a pentatonic collection")
    if len(minor_cycle_rests) != major_segments or any(
        isinstance(value, bool) or not isinstance(value, int) or value <= 0
        for value in minor_cycle_rests
    ):
        raise ValueError("minor_cycle_rests must provide one positive value per meridian")

    major_voice = apply_torus_hexatonic_mapping(
        torus_mesh,
        pitch_classes=major_cycle_pitches,
        base_octave=4,
        ring_rest_ticks=major_cycle_rests,
    )
    polyphony = nx.DiGraph()
    _copy_major_cycle_voice(polyphony, major_voice)
    _add_minor_cycle_voice(
        polyphony,
        torus_mesh,
        pitches=minor_cycle_pitches,
        rest_ticks=minor_cycle_rests,
    )
    polyphony.graph.update(
        geometry="quartic_torus_dual_cycle_polyphony",
        source_geometry=torus_mesh.graph.get("geometry"),
        source_eigenmode=torus_mesh.graph.get("eigenmode_index"),
        source_eigenvalue=torus_mesh.graph.get("eigenvalue"),
        voices=("major_cycle", "minor_cycle"),
        major_cycle_pitch_collection=tuple(major_cycle_pitches),
        minor_cycle_pitch_collection=tuple(minor_cycle_pitches),
        major_cycle_rests=tuple(major_cycle_rests),
        minor_cycle_rests=tuple(minor_cycle_rests),
        rhythm_subdivisions_per_quarter=8,
        total_ticks=120,
    )
    return polyphony


def _copy_major_cycle_voice(destination: nx.DiGraph, source: nx.Graph) -> None:
    previous_event = None
    for source_node in source.graph["traversal_path"]:
        event_id = ("major_cycle", *source_node)
        source_data = source.nodes[source_node]
        destination.add_node(
            event_id,
            **source_data,
            source_vertex=source_node,
            voice="major_cycle",
            coordinate_cycle="major",
        )
        if previous_event is not None:
            destination.add_edge(previous_event, event_id)
        previous_event = event_id


def _add_minor_cycle_voice(
    destination: nx.DiGraph,
    source: nx.Graph,
    pitches: Sequence[str],
    rest_ticks: Sequence[int],
) -> None:
    major_segments = source.graph["major_segments"]
    minor_segments = source.graph["minor_segments"]
    parsed_pitch_classes = tuple(note.Note(f"{name}4").pitch.name for name in pitches)
    onset_tick = 0
    previous_event = None
    for major_index in range(major_segments):
        minor_indices = (
            range(minor_segments)
            if major_index % 2 == 0
            else range(minor_segments - 1, -1, -1)
        )
        theta = math.tau * major_index / major_segments
        octave_displacement = 1 if math.cos(theta) < -0.25 else 0
        for minor_index in minor_indices:
            source_node = (minor_index, major_index)
            event_id = ("minor_cycle", minor_index, major_index)
            phi_band = int(minor_index * len(parsed_pitch_classes) / minor_segments)
            collection_rotation = major_index % len(parsed_pitch_classes)
            degree_index = (phi_band + collection_rotation) % len(parsed_pitch_classes)
            musical_pitch = note.Note(
                f"{parsed_pitch_classes[degree_index]}{3 + octave_displacement}"
            ).pitch
            destination.add_node(
                event_id,
                pitch=musical_pitch.nameWithOctave,
                pitch_space=musical_pitch.ps,
                onset_tick=onset_tick,
                duration_ticks=1,
                source_vertex=source_node,
                field_value=source.nodes[source_node]["field_value"],
                voice="minor_cycle",
                coordinate_cycle="minor",
                pitch_degree=degree_index,
                collection_rotation=collection_rotation,
                octave_displacement=octave_displacement,
                meridian_phrase=major_index,
            )
            if previous_event is not None:
                destination.add_edge(previous_event, event_id)
            previous_event = event_id
            onset_tick += 1
        onset_tick += rest_ticks[major_index]
    if onset_tick != 120:
        raise ValueError("minor-cycle design must fill exactly 120 thirty-second-note ticks")
