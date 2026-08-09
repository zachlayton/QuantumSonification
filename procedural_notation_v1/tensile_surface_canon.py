"""A 32-voice reflecting canon woven through a tensile saddle mesh."""

from __future__ import annotations

import math

import networkx as nx

from procedural_notation_v1.surface_mesh_ensemble import _nearest_registered_pitch
from procedural_notation_v1.surface_mesh_graph import TORUS_HEXATONIC_SET
from procedural_notation_v1.surface_mesh_polyphony import TORUS_PENTATONIC_SET


TENSILE_RHYTHMIC_SUBJECT = (1, 1, 2, 1, 3, 1, 2, 1, 1, 2, 3, 1, 2, 1, 1, 2)
TENSILE_REST_SUBJECT = (0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 2, 0, 1, 0, 0)
TENSILE_MENSURATIONS = (1, 1, 2, 2)


def build_tensile_saddle_32_voice_canon(
    surface: nx.Graph,
    passes: int = 4,
) -> nx.DiGraph:
    """Interpret warp and weft cables as interleaved reflecting canons."""
    if surface.graph.get("rows") != 16 or surface.graph.get("columns") != 16:
        raise ValueError("32-voice tensile canon requires a 16 by 16 mesh")
    if isinstance(passes, bool) or not isinstance(passes, int) or passes < 2:
        raise ValueError("passes must be an integer of at least 2")

    canon = nx.DiGraph()
    voices = []
    for fixed_index in range(16):
        voice_id = f"A_warp_{fixed_index + 1:02d}"
        voices.append(voice_id)
        _add_cable_voice(
            canon,
            surface,
            voice_id=voice_id,
            family="warp",
            fixed_index=fixed_index,
            entry_index=2 * fixed_index,
            mensuration=TENSILE_MENSURATIONS[fixed_index % 4],
            passes=passes,
        )
    for fixed_index in range(16):
        voice_id = f"B_weft_{fixed_index + 1:02d}"
        voices.append(voice_id)
        _add_cable_voice(
            canon,
            surface,
            voice_id=voice_id,
            family="weft",
            fixed_index=fixed_index,
            entry_index=2 * fixed_index + 1,
            mensuration=TENSILE_MENSURATIONS[fixed_index % 4],
            passes=passes,
        )

    voice_end_ticks = {}
    for voice_id in voices:
        events = [data for _, data in canon.nodes(data=True) if data["voice"] == voice_id]
        voice_end_ticks[voice_id] = max(
            data["onset_tick"] + data["duration_ticks"] for data in events
        )
    _validate_cable_paths(canon, surface, passes)
    canon.graph.update(
        geometry="tensile_saddle_32_voice_reflection_canon",
        source_geometry=surface.graph.get("geometry"),
        form="32-entry double reflection canon",
        voices=tuple(voices),
        voice_count=32,
        passes=passes,
        events_per_voice=16 * passes,
        rhythmic_subject=TENSILE_RHYTHMIC_SUBJECT,
        rest_subject=TENSILE_REST_SUBJECT,
        mensuration_factors=TENSILE_MENSURATIONS,
        warp_pitch_collection=TORUS_HEXATONIC_SET,
        weft_pitch_collection=TORUS_PENTATONIC_SET,
        voice_end_ticks=voice_end_ticks,
        rhythm_subdivisions_per_quarter=8,
        total_ticks=max(voice_end_ticks.values()),
    )
    return canon


def _add_cable_voice(
    destination: nx.DiGraph,
    source: nx.Graph,
    voice_id: str,
    family: str,
    fixed_index: int,
    entry_index: int,
    mensuration: int,
    passes: int,
) -> None:
    collection = TORUS_HEXATONIC_SET if family == "warp" else TORUS_PENTATONIC_SET
    onset_tick = entry_index
    previous_event = None
    for pass_index in range(passes):
        moving_indices = range(16) if (pass_index + fixed_index) % 2 == 0 else range(15, -1, -1)
        for local_step, moving_index in enumerate(moving_indices):
            source_node = (
                (fixed_index, moving_index)
                if family == "warp"
                else (moving_index, fixed_index)
            )
            rhythm_index = (
                local_step + 3 * pass_index
                if fixed_index % 2 == 0
                else 15 - local_step + 3 * pass_index
            ) % 16
            base_duration = TENSILE_RHYTHMIC_SUBJECT[rhythm_index]
            base_rest = TENSILE_REST_SUBJECT[rhythm_index]
            duration_ticks = base_duration * mensuration
            internal_rest_ticks = base_rest * mensuration
            coordinate_band = int(moving_index * len(collection) / 16)
            collection_rotation = (
                fixed_index + pass_index * (1 if family == "warp" else 2)
            ) % len(collection)
            pitch_degree = (coordinate_band + collection_rotation) % len(collection)
            x, y, z = source.nodes[source_node]["position"]
            normalized_height = z / source.graph["rise"]
            moving_coordinate = (
                x / source.graph["span_x"]
                if family == "warp"
                else y / source.graph["span_y"]
            )
            reflection_wave = 4.0 * math.sin(
                math.pi * moving_coordinate + pass_index * math.pi / 2.0
            )
            register_target = (
                (64.0 if family == "warp" else 52.0)
                + 18.0 * normalized_height
                + reflection_wave
            )
            musical_pitch = _nearest_registered_pitch(
                collection[pitch_degree],
                register_target,
            )
            event_id = (voice_id, pass_index, local_step)
            destination.add_node(
                event_id,
                pitch=musical_pitch.nameWithOctave,
                pitch_space=musical_pitch.ps,
                onset_tick=onset_tick,
                duration_ticks=duration_ticks,
                source_vertex=source_node,
                field_value=source.nodes[source_node]["field_value"],
                gaussian_curvature=source.nodes[source_node]["gaussian_curvature"],
                voice=voice_id,
                voice_family=family,
                fixed_coordinate_index=fixed_index,
                moving_coordinate_index=moving_index,
                canon_entry_index=entry_index,
                mensuration_factor=mensuration,
                pass_index=pass_index,
                reflection_direction=1 if moving_indices.start == 0 else -1,
                rhythm_subject_index=rhythm_index,
                base_duration_ticks=base_duration,
                internal_rest_ticks=internal_rest_ticks,
                collection_rotation=collection_rotation,
                pitch_degree=pitch_degree,
                register_target=register_target,
                reflection_wave=reflection_wave,
                octave_displacement=musical_pitch.octave - 4,
            )
            if previous_event is not None:
                destination.add_edge(
                    previous_event,
                    event_id,
                    temporal_gap_ticks=(
                        onset_tick
                        - destination.nodes[previous_event]["onset_tick"]
                        - destination.nodes[previous_event]["duration_ticks"]
                    ),
                )
            previous_event = event_id
            onset_tick += duration_ticks + internal_rest_ticks

        if pass_index < passes - 1:
            reflection_offset = (1 + (fixed_index + pass_index) % 4) * mensuration
            destination.nodes[previous_event]["reflection_offset_after_ticks"] = reflection_offset
            onset_tick += reflection_offset


def _validate_cable_paths(graph: nx.DiGraph, source: nx.Graph, passes: int) -> None:
    voices = sorted({data["voice"] for _, data in graph.nodes(data=True)})
    if len(voices) != 32:
        raise RuntimeError("tensile canon must contain 32 voices")
    for voice_id in voices:
        events = sorted(
            (data for _, data in graph.nodes(data=True) if data["voice"] == voice_id),
            key=lambda data: data["onset_tick"],
        )
        if len(events) != 16 * passes:
            raise RuntimeError(f"voice {voice_id!r} has an incomplete reflection path")
        for left, right in zip(events, events[1:]):
            if left["onset_tick"] + left["duration_ticks"] > right["onset_tick"]:
                raise RuntimeError(f"voice {voice_id!r} contains overlapping notes")
            same_vertex = left["source_vertex"] == right["source_vertex"]
            if not same_vertex and not source.has_edge(
                left["source_vertex"], right["source_vertex"]
            ):
                raise RuntimeError(f"voice {voice_id!r} left its cable line")
