"""Rotating radial canons on a Poincare disk using modular pitch sieves."""

from __future__ import annotations

import math

import networkx as nx
from music21 import pitch

from procedural_notation_v1.xenakis_sieve import (
    DEFAULT_PARENT_PITCH_CLASSES,
    modular_pitch_sieve,
    pitch_digit,
)
from procedural_notation_v1.quantum_dynamic_field import apply_quantum_dynamic_contrast


def build_poincare_sieve_canon(
    disk_graph: nx.Graph,
    voice_count: int = 8,
    rotations: int = 8,
) -> nx.DiGraph:
    """Breathe eight voices through successively rotated hyperbolic rays."""
    if disk_graph.graph.get("ring_counts") != (1, 8, 16, 24):
        raise ValueError("sieve canon requires the 1-8-16-24 Poincare graph")
    if voice_count != 8 or rotations != 8:
        raise ValueError("this study uses eight voices and eight angular rotations")

    canon = nx.DiGraph()
    voices = []
    for voice_index in range(voice_count):
        voice_id = f"ray_{voice_index + 1:02d}"
        voices.append(voice_id)
        _add_ray_voice(
            canon,
            disk_graph,
            voice_id=voice_id,
            voice_index=voice_index,
            rotations=rotations,
        )
    voice_end_ticks = {}
    for voice_id in voices:
        events = [data for _, data in canon.nodes(data=True) if data["voice"] == voice_id]
        voice_end_ticks[voice_id] = max(
            data["onset_tick"] + data["duration_ticks"] for data in events
        )
    _validate_radial_paths(canon, disk_graph, rotations)
    canon = apply_quantum_dynamic_contrast(canon)
    canon.graph.update(
        geometry="poincare_disk_xenakis_sieve_canon",
        source_geometry=disk_graph.graph.get("geometry"),
        voices=tuple(voices),
        voice_count=voice_count,
        rotations=rotations,
        sieve_formula="ten-digit parent lattice filtered by (7@0 union 7@2) union 9@1",
        digit_pitch_classes=DEFAULT_PARENT_PITCH_CLASSES,
        base_sieve=modular_pitch_sieve(),
        rhythm_subdivisions_per_quarter=8,
        voice_end_ticks=voice_end_ticks,
        total_ticks=max(voice_end_ticks.values()),
    )
    return canon


def _add_ray_voice(
    destination: nx.DiGraph,
    source: nx.Graph,
    voice_id: str,
    voice_index: int,
    rotations: int,
) -> None:
    onset_tick = 2 * voice_index
    previous_event = None
    for rotation_index in range(rotations):
        sector = (voice_index + rotation_index) % 8
        path = (
            (0, 0),
            (1, sector),
            (2, 2 * sector),
            (3, 3 * sector),
            (2, 2 * sector),
            (1, sector),
            (0, 0),
        )
        residue_shift_7 = sector % 7
        residue_shift_9 = (2 * sector + rotation_index) % 9
        sieve = modular_pitch_sieve(
            residue_shift_7=residue_shift_7,
            residue_shift_9=residue_shift_9,
        )
        for path_index, source_node in enumerate(path):
            ring_index = source_node[0]
            radial_fraction = ring_index / 3.0
            angular_wave = 0.18 * math.sin(
                math.tau * sector / 8.0 + rotation_index * math.pi / 4.0
            )
            target_fraction = min(
                1.0,
                max(0.0, 0.2 + 0.6 * radial_fraction + angular_wave),
            )
            sieve_index = round(target_fraction * (len(sieve) - 1))
            midi_pitch = sieve[sieve_index]
            musical_pitch = pitch.Pitch()
            musical_pitch.midi = midi_pitch
            duration_ticks = 1 + ring_index
            measure_offset = onset_tick % 32
            if measure_offset + duration_ticks > 32:
                onset_tick += 32 - measure_offset
            event_id = (voice_id, rotation_index, path_index)
            destination.add_node(
                event_id,
                pitch=musical_pitch.nameWithOctave,
                pitch_space=musical_pitch.ps,
                onset_tick=onset_tick,
                duration_ticks=duration_ticks,
                source_vertex=source_node,
                field_value=source.nodes[source_node]["field_value"],
                voice=voice_id,
                canon_entry_index=voice_index,
                rotation_index=rotation_index,
                sector=sector,
                path_index=path_index,
                radial_direction=(
                    "outward" if path_index < 3 else "boundary" if path_index == 3 else "inward"
                ),
                hyperbolic_radius=source.nodes[source_node]["hyperbolic_radius"],
                residue_shift_7=residue_shift_7,
                residue_shift_9=residue_shift_9,
                sieve_size=len(sieve),
                sieve_index=sieve_index,
                selected_midi=midi_pitch,
                pitch_digit=pitch_digit(midi_pitch),
                duration_dilation=duration_ticks,
            )
            if previous_event is not None:
                destination.add_edge(previous_event, event_id)
            previous_event = event_id
            onset_tick += duration_ticks
        rotation_rest = 1 + rotation_index % 3
        destination.nodes[previous_event]["rotation_rest_after_ticks"] = rotation_rest
        onset_tick += rotation_rest


def _validate_radial_paths(
    canon: nx.DiGraph,
    source: nx.Graph,
    rotations: int,
) -> None:
    voices = sorted({data["voice"] for _, data in canon.nodes(data=True)})
    if len(voices) != 8:
        raise RuntimeError("Poincare canon must contain eight voices")
    for voice_id in voices:
        events = sorted(
            (data for _, data in canon.nodes(data=True) if data["voice"] == voice_id),
            key=lambda data: data["onset_tick"],
        )
        if len(events) != 7 * rotations:
            raise RuntimeError(f"voice {voice_id!r} has an incomplete radial path")
        for left, right in zip(events, events[1:]):
            same_vertex = left["source_vertex"] == right["source_vertex"]
            if not same_vertex and not source.has_edge(
                left["source_vertex"], right["source_vertex"]
            ):
                raise RuntimeError(f"voice {voice_id!r} left the Poincare mesh")
