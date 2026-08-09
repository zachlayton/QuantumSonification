"""Time-varying motion fields for large surface-mesh ensembles."""

from __future__ import annotations

from collections import defaultdict
import math

import networkx as nx

from procedural_notation_v1.surface_mesh_ensemble import (
    _coordinate_register_target,
    _nearest_registered_pitch,
)
from procedural_notation_v1.surface_mesh_graph import TORUS_HEXATONIC_SET
from procedural_notation_v1.surface_mesh_polyphony import TORUS_PENTATONIC_SET


CANON_MENSURATION_FACTORS = (1, 1, 2, 3)


def build_torus_32_voice_rotating_mesh(
    torus_mesh: nx.Graph,
    rotations: int = 4,
    canon_entry_ticks: int = 1,
    mensuration_factors: tuple[int, ...] = CANON_MENSURATION_FACTORS,
    curvature_motion: bool = False,
) -> nx.DiGraph:
    """Animate 32 coordinate lines as a double mensuration canon.

    Every voice remains on one torus coordinate loop, but neighboring loops
    counter-rotate.  Local surface coordinates control note length and internal
    rests; interleaved ring and meridian subjects enter one grid tick apart.
    """
    if torus_mesh.graph.get("major_segments") != 16 or torus_mesh.graph.get("minor_segments") != 16:
        raise ValueError("rotating 32-voice mesh requires a 16 by 16 torus")
    if isinstance(rotations, bool) or not isinstance(rotations, int) or rotations < 2:
        raise ValueError("rotations must be an integer of at least 2")
    if (
        isinstance(canon_entry_ticks, bool)
        or not isinstance(canon_entry_ticks, int)
        or canon_entry_ticks <= 0
    ):
        raise ValueError("canon_entry_ticks must be a positive integer")
    if not mensuration_factors or any(
        isinstance(value, bool) or not isinstance(value, int) or value <= 0
        for value in mensuration_factors
    ):
        raise ValueError("mensuration_factors must contain positive integers")
    if not isinstance(curvature_motion, bool):
        raise ValueError("curvature_motion must be a boolean")

    maximum_absolute_curvature = max(
        abs(data["gaussian_curvature"])
        for _, data in torus_mesh.nodes(data=True)
    )

    motion_graph = nx.DiGraph()
    voices = []
    for fixed_index in range(16):
        voice_id = f"A_ring_{fixed_index + 1:02d}"
        voices.append(voice_id)
        _add_rotating_voice(
            motion_graph,
            torus_mesh,
            voice_id=voice_id,
            family="ring",
            fixed_index=fixed_index,
            rotations=rotations,
            initial_offset=2 * fixed_index * canon_entry_ticks,
            direction=1 if fixed_index % 2 == 0 else -1,
            canon_entry_index=2 * fixed_index,
            mensuration_factor=mensuration_factors[
                fixed_index % len(mensuration_factors)
            ],
            curvature_motion=curvature_motion,
            maximum_absolute_curvature=maximum_absolute_curvature,
        )
    for fixed_index in range(16):
        voice_id = f"B_meridian_{fixed_index + 1:02d}"
        voices.append(voice_id)
        _add_rotating_voice(
            motion_graph,
            torus_mesh,
            voice_id=voice_id,
            family="meridian",
            fixed_index=fixed_index,
            rotations=rotations,
            initial_offset=(2 * fixed_index + 1) * canon_entry_ticks,
            direction=-1 if fixed_index % 2 == 0 else 1,
            canon_entry_index=2 * fixed_index + 1,
            mensuration_factor=mensuration_factors[
                fixed_index % len(mensuration_factors)
            ],
            curvature_motion=curvature_motion,
            maximum_absolute_curvature=maximum_absolute_curvature,
        )

    voice_end_ticks = {}
    for voice_id in voices:
        events = [data for _, data in motion_graph.nodes(data=True) if data["voice"] == voice_id]
        voice_end_ticks[voice_id] = max(
            data["onset_tick"] + data["duration_ticks"] for data in events
        )
    total_ticks = max(voice_end_ticks.values())
    _validate_motion_graph(motion_graph, torus_mesh, rotations)
    motion_graph.graph.update(
        geometry="quartic_torus_32_voice_rotating_mesh",
        source_geometry=torus_mesh.graph.get("geometry"),
        voices=tuple(voices),
        voice_count=32,
        form="32-entry double mensuration canon",
        rotations=rotations,
        events_per_voice=16 * rotations,
        canon_entry_ticks=canon_entry_ticks,
        mensuration_factors=tuple(mensuration_factors),
        curvature_motion=curvature_motion,
        maximum_absolute_curvature=maximum_absolute_curvature,
        ring_pitch_collection=TORUS_HEXATONIC_SET,
        meridian_pitch_collection=TORUS_PENTATONIC_SET,
        motion_parameters=(
            "counter_rotation",
            "canonic_entry",
            "mensuration_augmentation",
            "collection_rotation",
            "initial_offset",
            "orbital_displacement",
            "coordinate_elongation",
            "register_spin",
            "gaussian_curvature_speed" if curvature_motion else "uniform_speed_field",
        ),
        voice_end_ticks=voice_end_ticks,
        rhythm_subdivisions_per_quarter=8,
        total_ticks=total_ticks,
    )
    return motion_graph


def _add_rotating_voice(
    destination: nx.DiGraph,
    source: nx.Graph,
    voice_id: str,
    family: str,
    fixed_index: int,
    rotations: int,
    initial_offset: int,
    direction: int,
    canon_entry_index: int,
    mensuration_factor: int,
    curvature_motion: bool,
    maximum_absolute_curvature: float,
) -> None:
    pitch_collection = (
        TORUS_HEXATONIC_SET if family == "ring" else TORUS_PENTATONIC_SET
    )
    onset_tick = initial_offset
    previous_event = None
    for orbit_index in range(rotations):
        for local_step in range(16):
            global_step = orbit_index * 16 + local_step
            moving_index = (fixed_index + direction * global_step) % 16
            source_node = (
                (fixed_index, moving_index)
                if family == "ring"
                else (moving_index, fixed_index)
            )
            moving_angle = math.tau * moving_index / 16
            fixed_angle = math.tau * fixed_index / 16
            base_elongation_ticks = 1 + int(
                2.0 * abs(math.sin(moving_angle + orbit_index * math.pi / 4.0))
                + 1e-9
            )
            gaussian_curvature = source.nodes[source_node]["gaussian_curvature"]
            normalized_curvature = gaussian_curvature / maximum_absolute_curvature
            curvature_time_scale = (
                1.0 - 0.5 * normalized_curvature
                if curvature_motion
                else 1.0
            )
            elongation_ticks = max(
                1,
                round(
                    base_elongation_ticks
                    * mensuration_factor
                    * curvature_time_scale
                ),
            )
            base_internal_rest_ticks = int(
                math.cos(
                    moving_angle
                    - direction * fixed_angle
                    + orbit_index * math.pi / 4.0
                )
                < -0.35
            )
            curvature_rest_units = int(
                curvature_motion and normalized_curvature < -0.35
            )
            internal_rest_ticks = (
                base_internal_rest_ticks + curvature_rest_units
            ) * mensuration_factor
            coordinate_band = int(
                moving_index * len(pitch_collection) / 16
            )
            collection_rotation = (
                fixed_index + orbit_index * (1 if family == "ring" else 2)
            ) % len(pitch_collection)
            pitch_degree = (coordinate_band + collection_rotation) % len(
                pitch_collection
            )
            register_spin = 6.0 * math.sin(
                moving_angle + direction * orbit_index * math.pi / 4.0
            )
            register_target = (
                _coordinate_register_target(source, source_node, family)
                + register_spin
            )
            musical_pitch = _nearest_registered_pitch(
                pitch_collection[pitch_degree],
                register_target,
            )
            event_id = (voice_id, orbit_index, local_step)
            destination.add_node(
                event_id,
                pitch=musical_pitch.nameWithOctave,
                pitch_space=musical_pitch.ps,
                onset_tick=onset_tick,
                duration_ticks=elongation_ticks,
                source_vertex=source_node,
                field_value=source.nodes[source_node]["field_value"],
                gaussian_curvature=gaussian_curvature,
                normalized_curvature=normalized_curvature,
                curvature_time_scale=curvature_time_scale,
                curvature_motion=curvature_motion,
                voice=voice_id,
                voice_family=family,
                fixed_coordinate_index=fixed_index,
                moving_coordinate_index=moving_index,
                orbit_index=orbit_index,
                local_step=local_step,
                rotation_direction=direction,
                canon_entry_index=canon_entry_index,
                initial_offset_ticks=initial_offset,
                mensuration_factor=mensuration_factor,
                collection_rotation=collection_rotation,
                pitch_degree=pitch_degree,
                register_target=register_target,
                register_spin=register_spin,
                octave_displacement=musical_pitch.octave - 4,
                base_elongation_ticks=base_elongation_ticks,
                elongation_ticks=elongation_ticks,
                base_internal_rest_ticks=base_internal_rest_ticks,
                curvature_rest_units=curvature_rest_units,
                internal_rest_ticks=internal_rest_ticks,
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
            onset_tick += elongation_ticks + internal_rest_ticks

        if orbit_index < rotations - 1:
            base_orbital_displacement = 1 + (fixed_index + 2 * orbit_index) % 4
            last_time_scale = destination.nodes[previous_event]["curvature_time_scale"]
            orbital_displacement = max(
                1,
                round(
                    base_orbital_displacement
                    * mensuration_factor
                    * last_time_scale
                ),
            )
            destination.nodes[previous_event][
                "orbital_displacement_after_ticks"
            ] = orbital_displacement
            destination.nodes[previous_event][
                "base_orbital_displacement_after_ticks"
            ] = base_orbital_displacement
            onset_tick += orbital_displacement


def _validate_motion_graph(
    graph: nx.DiGraph,
    source: nx.Graph,
    rotations: int,
) -> None:
    events_by_voice = defaultdict(list)
    for event_id, data in graph.nodes(data=True):
        events_by_voice[data["voice"]].append((event_id, data))
    if len(events_by_voice) != 32:
        raise RuntimeError("motion mesh must contain exactly 32 voices")
    for voice_id, events in events_by_voice.items():
        ordered = sorted(events, key=lambda item: item[1]["onset_tick"])
        if len(ordered) != 16 * rotations:
            raise RuntimeError(f"voice {voice_id!r} has an incomplete orbit")
        for (_, left), (_, right) in zip(ordered, ordered[1:]):
            if left["onset_tick"] + left["duration_ticks"] > right["onset_tick"]:
                raise RuntimeError(f"voice {voice_id!r} contains overlapping events")
            if not source.has_edge(left["source_vertex"], right["source_vertex"]):
                raise RuntimeError(f"voice {voice_id!r} left its coordinate line")
