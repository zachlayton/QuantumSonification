"""Translate geometric graph paths into conventional notation."""

from __future__ import annotations

import math
from pathlib import Path
from typing import Iterable, Sequence

import networkx as nx
from music21 import articulations, dynamics, instrument, metadata, meter, note, stream, tempo, tie


DEFAULT_PITCHES = ("C4", "D4", "E4", "F4", "G4", "A4", "B4", "C5")


def apply_pitch_mapping(
    graph: nx.Graph,
    pitches: Sequence[str] = DEFAULT_PITCHES,
) -> nx.Graph:
    """Return a copy of ``graph`` with one scientific pitch per node."""
    nodes = list(graph.nodes)
    if len(pitches) != len(nodes):
        raise ValueError("the pitch mapping must contain exactly one pitch per node")

    mapped = graph.copy()
    for node_id, pitch_name in zip(nodes, pitches, strict=True):
        parsed_pitch = note.Note(pitch_name).pitch
        mapped.nodes[node_id]["pitch"] = parsed_pitch.nameWithOctave
        mapped.nodes[node_id]["midi"] = parsed_pitch.midi
    return mapped


def build_score(
    graph: nx.Graph,
    node_path: Iterable[int] | None = None,
    quarter_length: float = 1.0,
    time_signature: str = "4/4",
    title: str = "Regular Octagon Study No. 1",
) -> stream.Score:
    """Build a monophonic score by reading pitches along a graph path."""
    if not math.isfinite(quarter_length) or quarter_length <= 0.0:
        raise ValueError("quarter_length must be a finite positive number")

    path = list(graph.nodes) if node_path is None else list(node_path)
    if not path:
        raise ValueError("node_path must contain at least one node")

    for node_id in path:
        if node_id not in graph:
            raise ValueError(f"node {node_id!r} is not in the graph")
        if "pitch" not in graph.nodes[node_id]:
            raise ValueError(f"node {node_id!r} has no pitch mapping")

    score = stream.Score(id="procedural-graph-score")
    score.metadata = metadata.Metadata()
    score.metadata.title = title
    score.metadata.composer = "QuantumSonification"

    part = stream.Part(id="P1")
    part.partName = "Piano"
    part.append(instrument.Piano())
    part.append(tempo.MetronomeMark(number=72, text="Andante"))
    part.append(meter.TimeSignature(time_signature))

    for node_id in path:
        musical_note = note.Note(graph.nodes[node_id]["pitch"])
        musical_note.quarterLength = quarter_length
        musical_note.addLyric(str(node_id))
        part.append(musical_note)

    part.makeMeasures(inPlace=True)
    score.append(part)
    return score


def write_musicxml(score: stream.Score, output_path: str | Path) -> Path:
    """Write ``score`` as an uncompressed MusicXML document."""
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    written_path = score.write("musicxml", fp=destination)
    return Path(written_path)


def build_timed_score(
    graph: nx.Graph,
    measures: int = 4,
    beats_per_measure: int = 4,
    ticks_per_quarter: int = 8,
    title: str = "Spatiotemporal Graph Study",
    include_node_labels: bool = True,
) -> stream.Score:
    """Build a score from node ``onset_tick``, ``duration_ticks``, and ``pitch``.

    Empty time is written as ordinary power-of-two rests on the requested tick
    grid, keeping exact graph-derived onsets legible in MusicXML.
    """
    for name, value in (
        ("measures", measures),
        ("beats_per_measure", beats_per_measure),
        ("ticks_per_quarter", ticks_per_quarter),
    ):
        if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
            raise ValueError(f"{name} must be a positive integer")

    measure_ticks = beats_per_measure * ticks_per_quarter
    total_ticks = measures * measure_ticks
    events: dict[int, tuple[int, dict]] = {}
    for node_id, data in graph.nodes(data=True):
        if not {"onset_tick", "duration_ticks", "pitch"} <= data.keys():
            raise ValueError(f"node {node_id!r} lacks timed notation parameters")
        onset = data["onset_tick"]
        duration = data["duration_ticks"]
        if not isinstance(onset, int) or not isinstance(duration, int):
            raise ValueError("onset_tick and duration_ticks must be integers")
        if onset < 0 or duration <= 0 or onset + duration > total_ticks:
            raise ValueError(f"node {node_id!r} falls outside the score duration")
        if onset in events:
            raise ValueError(f"multiple nodes share onset tick {onset}")
        events[onset] = (node_id, data)

    ordered_events = sorted(
        (onset, onset + data["duration_ticks"], node_id)
        for onset, (node_id, data) in events.items()
    )
    for (_, previous_end, previous_node), (next_start, _, next_node) in zip(
        ordered_events,
        ordered_events[1:],
        strict=False,
    ):
        if previous_end > next_start:
            raise ValueError(f"nodes {previous_node!r} and {next_node!r} overlap")

    segments_by_measure: dict[int, list[tuple[int, int, int, dict, str | None]]] = {
        index: [] for index in range(measures)
    }
    for onset, (node_id, data) in events.items():
        event_end = onset + data["duration_ticks"]
        segment_start = onset
        segments: list[tuple[int, int]] = []
        while segment_start < event_end:
            boundary = ((segment_start // measure_ticks) + 1) * measure_ticks
            segment_end = min(event_end, boundary)
            segments.append((segment_start, segment_end))
            segment_start = segment_end
        for segment_index, (segment_start, segment_end) in enumerate(segments):
            if len(segments) == 1:
                tie_type = None
            elif segment_index == 0:
                tie_type = "start"
            elif segment_index == len(segments) - 1:
                tie_type = "stop"
            else:
                tie_type = "continue"
            measure_index = segment_start // measure_ticks
            segments_by_measure[measure_index].append(
                (segment_start, segment_end, node_id, data, tie_type)
            )

    score = stream.Score(id="spatiotemporal-graph-score")
    score.metadata = metadata.Metadata()
    score.metadata.title = title
    score.metadata.composer = "QuantumSonification"
    part = stream.Part(id="P1")
    part.partName = "Piano"
    part.append(instrument.Piano())

    for measure_index in range(measures):
        musical_measure = stream.Measure(number=measure_index + 1)
        if measure_index == 0:
            musical_measure.append(tempo.MetronomeMark(number=72, text="Andante"))
            musical_measure.append(meter.TimeSignature(f"{beats_per_measure}/4"))

        measure_start = measure_index * measure_ticks
        measure_end = measure_start + measure_ticks
        cursor = measure_start
        for segment_start, segment_end, node_id, data, tie_type in sorted(
            segments_by_measure[measure_index]
        ):
            _append_grid_rests(
                musical_measure,
                start_tick=cursor - measure_start,
                end_tick=segment_start - measure_start,
                ticks_per_quarter=ticks_per_quarter,
            )
            musical_note = note.Note(data["pitch"])
            musical_note.quarterLength = (segment_end - segment_start) / ticks_per_quarter
            if tie_type is not None:
                musical_note.tie = tie.Tie(tie_type)
            if tie_type in (None, "start"):
                dynamic_mark = data.get("dynamic_mark")
                if dynamic_mark is not None:
                    musical_measure.append(dynamics.Dynamic(dynamic_mark))
                accent_type = data.get("accent_type")
                if accent_type == "accent":
                    musical_note.articulations.append(articulations.Accent())
                elif accent_type == "strong-accent":
                    musical_note.articulations.append(articulations.StrongAccent())
                elif accent_type is not None:
                    raise ValueError(f"unsupported accent_type {accent_type!r}")
            if include_node_labels and tie_type in (None, "start"):
                musical_note.addLyric(str(data.get("source_vertex", node_id)))
            musical_measure.append(musical_note)
            cursor = segment_end
        _append_grid_rests(
            musical_measure,
            start_tick=cursor - measure_start,
            end_tick=measure_ticks,
            ticks_per_quarter=ticks_per_quarter,
        )
        part.append(musical_measure)

    score.append(part)
    return score


def build_polyphonic_timed_score(
    graph: nx.Graph,
    measures: int = 4,
    beats_per_measure: int = 4,
    ticks_per_quarter: int = 8,
    title: str = "Polyphonic Spatiotemporal Graph Study",
    voice_attribute: str = "voice",
    include_node_labels: bool = True,
) -> stream.Score:
    """Build one notated part for each graph-derived voice."""
    voices = sorted({data.get(voice_attribute) for _, data in graph.nodes(data=True)})
    if not voices or None in voices:
        raise ValueError(f"every node must define {voice_attribute!r}")

    score = stream.Score(id="polyphonic-spatiotemporal-graph-score")
    score.metadata = metadata.Metadata()
    score.metadata.title = title
    score.metadata.composer = "QuantumSonification"

    for voice_index, voice_id in enumerate(voices, start=1):
        voice_nodes = [
            node_id
            for node_id, data in graph.nodes(data=True)
            if data[voice_attribute] == voice_id
        ]
        voice_graph = graph.subgraph(voice_nodes).copy()
        voice_score = build_timed_score(
            voice_graph,
            measures=measures,
            beats_per_measure=beats_per_measure,
            ticks_per_quarter=ticks_per_quarter,
            title=title,
            include_node_labels=include_node_labels,
        )
        part = voice_score.parts[0]
        part.id = f"P{voice_index}"
        part.partName = f"Voice {voice_index}"
        score.append(part)

    return score


def _append_grid_rests(
    destination: stream.Measure,
    start_tick: int,
    end_tick: int,
    ticks_per_quarter: int,
) -> None:
    """Fill a gap with binary rests, split at quarter-note boundaries."""
    cursor = start_tick
    while cursor < end_tick:
        beat_end = ((cursor // ticks_per_quarter) + 1) * ticks_per_quarter
        available = min(end_tick, beat_end) - cursor
        chunk = 1 << (available.bit_length() - 1)
        musical_rest = note.Rest()
        musical_rest.quarterLength = chunk / ticks_per_quarter
        destination.append(musical_rest)
        cursor += chunk
