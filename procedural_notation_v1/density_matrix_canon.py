"""Map a four-qubit density matrix evolution onto a 16 by 16 cable net."""

from __future__ import annotations

import math
from typing import Sequence

import networkx as nx
import numpy as np
from music21 import pitch

from procedural_notation_v1.density_matrix_field import (
    density_matrix_purity,
    weighted_z_expectation,
)
from procedural_notation_v1.surface_mesh_ensemble import _nearest_registered_pitch
from procedural_notation_v1.surface_mesh_graph import TORUS_HEXATONIC_SET
from procedural_notation_v1.surface_mesh_polyphony import TORUS_PENTATONIC_SET


DEFAULT_FIXED_TRANSPOSITIONS = (0, 2, 4, 7, 9)


def build_density_matrix_cable_net_canon(
    cable_net: nx.Graph,
    density_snapshots: Sequence[np.ndarray],
    coherence_threshold: float = 0.08,
    slot_ticks: int = 4,
    snapshot_gap_ticks: int = 4,
    transpose_collections: bool = False,
    fixed_set_transpositions: Sequence[int] | None = None,
) -> nx.DiGraph:
    """Use matrix magnitude, phase, and populations as a 32-voice score."""
    if cable_net.graph.get("rows") != 16 or cable_net.graph.get("columns") != 16:
        raise ValueError("density-matrix canon requires a 16 by 16 cable net")
    if not density_snapshots:
        raise ValueError("density_snapshots must not be empty")
    if not 0.0 <= coherence_threshold < 1.0:
        raise ValueError("coherence_threshold must lie in [0, 1)")
    for name, value in (("slot_ticks", slot_ticks), ("snapshot_gap_ticks", snapshot_gap_ticks)):
        if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
            raise ValueError(f"{name} must be a positive integer")
    for density in density_snapshots:
        _validate_density_matrix(density)
    if not isinstance(transpose_collections, bool):
        raise ValueError("transpose_collections must be a boolean")
    if fixed_set_transpositions is not None:
        if transpose_collections:
            raise ValueError(
                "chromatic phase transposition and fixed-set transposition are mutually exclusive"
            )
        if (
            len(fixed_set_transpositions) != 5
            or len(set(fixed_set_transpositions)) != 5
            or any(
                isinstance(value, bool) or not isinstance(value, int)
                for value in fixed_set_transpositions
            )
        ):
            raise ValueError("fixed_set_transpositions must contain five distinct integers")

    observable_values = tuple(
        weighted_z_expectation(density)
        for density in density_snapshots
    )
    if fixed_set_transpositions is not None:
        snapshot_transpositions = _ranked_fixed_transpositions(
            observable_values,
            fixed_set_transpositions,
        )
        transposition_mode = "fixed_full_set"
    elif transpose_collections:
        snapshot_transpositions = tuple(round(value) for value in observable_values)
        transposition_mode = "chromatic_phase"
    else:
        snapshot_transpositions = tuple(0 for _ in density_snapshots)
        transposition_mode = "none"

    canon = nx.DiGraph()
    voices = []
    for fixed_index in range(16):
        voice_id = f"A_ket_{fixed_index + 1:02d}"
        voices.append(voice_id)
        _add_density_voice(
            canon,
            cable_net,
            density_snapshots,
            voice_id=voice_id,
            family="ket",
            fixed_index=fixed_index,
            entry_index=2 * fixed_index,
            coherence_threshold=coherence_threshold,
            slot_ticks=slot_ticks,
            snapshot_gap_ticks=snapshot_gap_ticks,
            transpose_collections=transpose_collections,
            snapshot_transpositions=snapshot_transpositions,
            fixed_set_transpositions=fixed_set_transpositions,
        )
    for fixed_index in range(16):
        voice_id = f"B_bra_{fixed_index + 1:02d}"
        voices.append(voice_id)
        _add_density_voice(
            canon,
            cable_net,
            density_snapshots,
            voice_id=voice_id,
            family="bra",
            fixed_index=fixed_index,
            entry_index=2 * fixed_index + 1,
            coherence_threshold=coherence_threshold,
            slot_ticks=slot_ticks,
            snapshot_gap_ticks=snapshot_gap_ticks,
            transpose_collections=transpose_collections,
            snapshot_transpositions=snapshot_transpositions,
            fixed_set_transpositions=fixed_set_transpositions,
        )

    voice_end_ticks = {}
    for voice_id in voices:
        events = [data for _, data in canon.nodes(data=True) if data["voice"] == voice_id]
        if not events:
            raise RuntimeError(f"density gate silenced voice {voice_id!r}")
        voice_end_ticks[voice_id] = max(
            data["onset_tick"] + data["duration_ticks"] for data in events
        )
    canon.graph.update(
        geometry="four_qubit_density_matrix_cable_net",
        source_geometry=cable_net.graph.get("geometry"),
        form="32-entry bra-ket density canon",
        voices=tuple(voices),
        voice_count=32,
        snapshot_count=len(density_snapshots),
        coherence_threshold=float(coherence_threshold),
        slot_ticks=slot_ticks,
        snapshot_gap_ticks=snapshot_gap_ticks,
        snapshot_purities=tuple(
            density_matrix_purity(density) for density in density_snapshots
        ),
        transpose_collections=transpose_collections,
        transposition_mode=transposition_mode,
        fixed_set_transpositions=(
            tuple(fixed_set_transpositions)
            if fixed_set_transpositions is not None
            else None
        ),
        snapshot_observable_values=observable_values,
        snapshot_transpositions=snapshot_transpositions,
        transposition_observable="<Z0 + 2Z1 + 3Z2 + 4Z3>",
        ket_pitch_collection=TORUS_HEXATONIC_SET,
        bra_pitch_collection=TORUS_PENTATONIC_SET,
        voice_end_ticks=voice_end_ticks,
        rhythm_subdivisions_per_quarter=8,
        total_ticks=max(voice_end_ticks.values()),
        possible_matrix_events=32 * 16 * len(density_snapshots),
        sounding_matrix_events=canon.number_of_nodes(),
    )
    return canon


def _add_density_voice(
    destination: nx.DiGraph,
    cable_net: nx.Graph,
    density_snapshots: Sequence[np.ndarray],
    voice_id: str,
    family: str,
    fixed_index: int,
    entry_index: int,
    coherence_threshold: float,
    slot_ticks: int,
    snapshot_gap_ticks: int,
    transpose_collections: bool,
    snapshot_transpositions: Sequence[int],
    fixed_set_transpositions: Sequence[int] | None,
) -> None:
    collection = TORUS_HEXATONIC_SET if family == "ket" else TORUS_PENTATONIC_SET
    previous_event = None
    snapshot_span = 16 * slot_ticks + snapshot_gap_ticks
    for snapshot_index, density in enumerate(density_snapshots):
        maximum_magnitude = float(np.max(np.abs(density)))
        moving_indices = (
            range(16)
            if (snapshot_index + fixed_index) % 2 == 0
            else range(15, -1, -1)
        )
        for local_step, moving_index in enumerate(moving_indices):
            row, column = (
                (fixed_index, moving_index)
                if family == "ket"
                else (moving_index, fixed_index)
            )
            matrix_element = density[row, column]
            magnitude = float(abs(matrix_element))
            normalized_magnitude = magnitude / maximum_magnitude
            diagonal_population = row == column
            if not diagonal_population and normalized_magnitude < coherence_threshold:
                continue

            raw_phase = float(np.angle(matrix_element))
            applied_phase = raw_phase if family == "ket" else -raw_phase
            phase_fraction = (applied_phase + math.pi) / math.tau
            phase_offset_ticks = int(phase_fraction >= 0.5)
            duration_ticks = 1 + int(2.0 * math.sqrt(normalized_magnitude))
            if diagonal_population:
                duration_ticks = max(duration_ticks, 3)
            onset_tick = (
                entry_index
                + snapshot_index * snapshot_span
                + local_step * slot_ticks
                + phase_offset_ticks
            )
            coordinate_band = int(moving_index * len(collection) / 16)
            phase_rotation = (
                0
                if transpose_collections or fixed_set_transpositions is not None
                else int(phase_fraction * len(collection)) % len(collection)
            )
            pitch_degree = (
                coordinate_band + fixed_index + snapshot_index + phase_rotation
            ) % len(collection)
            snapshot_transposition = (
                snapshot_transpositions[snapshot_index]
                if transpose_collections or fixed_set_transpositions is not None
                else 0
            )
            coherence_transposition = (
                round(6.0 * applied_phase / math.pi)
                if transpose_collections and fixed_set_transpositions is None
                else 0
            )
            total_transposition = snapshot_transposition + coherence_transposition
            base_pitch_class = collection[pitch_degree]
            transposed_pitch_class = pitch.Pitch(base_pitch_class).transpose(
                total_transposition
            ).name
            source_node = (row, column)
            _, _, z = cable_net.nodes[source_node]["position"]
            normalized_height = z / cable_net.graph["rise"]
            register_target = (
                (64.0 if family == "ket" else 52.0)
                + 18.0 * normalized_height
                + 6.0 * (normalized_magnitude - 0.5)
                + 4.0 * math.sin(applied_phase)
            )
            musical_pitch = _nearest_registered_pitch(
                transposed_pitch_class,
                register_target,
            )
            event_id = (voice_id, snapshot_index, local_step)
            destination.add_node(
                event_id,
                pitch=musical_pitch.nameWithOctave,
                pitch_space=musical_pitch.ps,
                onset_tick=onset_tick,
                duration_ticks=duration_ticks,
                source_vertex=source_node,
                voice=voice_id,
                voice_family=family,
                canon_entry_index=entry_index,
                snapshot_index=snapshot_index,
                local_step=local_step,
                matrix_row=row,
                matrix_column=column,
                matrix_magnitude=magnitude,
                normalized_magnitude=normalized_magnitude,
                matrix_phase=raw_phase,
                applied_phase=applied_phase,
                phase_rotation=phase_rotation,
                base_pitch_class=base_pitch_class,
                snapshot_transposition_semitones=snapshot_transposition,
                coherence_transposition_semitones=coherence_transposition,
                total_transposition_semitones=total_transposition,
                collection_transposition_scope=(
                    "snapshot"
                    if fixed_set_transpositions is not None
                    else "matrix_element"
                    if transpose_collections
                    else "none"
                ),
                transposed_pitch_class=transposed_pitch_class,
                phase_offset_ticks=phase_offset_ticks,
                diagonal_population=diagonal_population,
                pitch_degree=pitch_degree,
                register_target=register_target,
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


def _ranked_fixed_transpositions(
    observable_values: Sequence[float],
    transpositions: Sequence[int],
) -> tuple[int, ...]:
    """Quantize ordered observable values into a fixed transposition palette."""
    snapshot_count = len(observable_values)
    if snapshot_count == 1:
        return (transpositions[len(transpositions) // 2],)
    ranking = sorted(
        range(snapshot_count),
        key=lambda index: (observable_values[index], index),
    )
    result = [0] * snapshot_count
    for rank, snapshot_index in enumerate(ranking):
        palette_index = round(
            rank * (len(transpositions) - 1) / (snapshot_count - 1)
        )
        result[snapshot_index] = transpositions[palette_index]
    return tuple(result)


def _validate_density_matrix(density: np.ndarray) -> None:
    if density.shape != (16, 16):
        raise ValueError("every density matrix must have shape 16 by 16")
    if not np.allclose(density, density.conj().T):
        raise ValueError("density matrix must be Hermitian")
    if not np.isclose(np.trace(density), 1.0):
        raise ValueError("density matrix must have trace one")
    if float(np.min(np.linalg.eigvalsh(density))) < -1e-10:
        raise ValueError("density matrix must be positive semidefinite")
