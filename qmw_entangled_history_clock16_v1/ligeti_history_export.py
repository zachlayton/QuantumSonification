"""Ligeti-form sixteen-clock score with MIDI and MusicXML export.

The score uses fixed independent millisecond periods, a common release, and a
finite winding budget for each computational clock-basis voice. At 60 BPM with 1000 PPQ, one
MIDI tick and one MusicXML division are exactly one millisecond.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Mapping
import json
import struct
import xml.etree.ElementTree as ET

import numpy as np

from .diagnostics import analyze_history
from .granular_sonification import _validate_rhythm_word
from .history_state import DiscreteHistoryState


@dataclass(frozen=True)
class LigetiClockConfig:
    rhythm_word: str = "10101"
    reference_interval_ms: float = 150.0
    interval_bins_per_octave: float = 16.0
    hit_budget: int = 48
    note_duration_ms: int = 28
    lowest_midi_note: int = 48
    velocity: int = 100
    ticks_per_quarter: int = 1000
    tempo_microseconds_per_quarter: int = 1_000_000


@dataclass(frozen=True)
class LigetiClockVoice:
    index: int
    interval_ms: float
    clock_probability: float
    hit_budget: int
    midi_note: int
    velocity: int
    pan: int
    onsets_ms: tuple[int, ...]


@dataclass(frozen=True)
class LigetiClockScore:
    voices: tuple[LigetiClockVoice, ...]
    config: LigetiClockConfig
    report: Mapping[str, object]


def _mode_multiplier(mode: int, dimension: int, bins_per_octave: float) -> float:
    centered = float(mode) - 0.5 * (dimension - 1)
    return float(2.0 ** (centered / bins_per_octave))


def _hit_onsets(word: str, interval_ms: float, hit_budget: int) -> tuple[int, ...]:
    cell = 0
    onsets: list[int] = []
    while len(onsets) < hit_budget:
        if word[cell % len(word)] == "1":
            onsets.append(int(round(cell * interval_ms)))
        cell += 1
    return tuple(onsets)


def build_ligeti_clock_score(
    history: DiscreteHistoryState,
    config: LigetiClockConfig | None = None,
) -> LigetiClockScore:
    settings = config or LigetiClockConfig()
    if history.clock_states != 16:
        raise ValueError("Ligeti clock score requires sixteen clock states")
    word = _validate_rhythm_word(settings.rhythm_word)
    if settings.reference_interval_ms <= 0.0:
        raise ValueError("reference interval must be positive")
    if settings.interval_bins_per_octave <= 0.0:
        raise ValueError("interval bins per octave must be positive")
    if settings.hit_budget <= 0:
        raise ValueError("hit budget must be positive")
    if not 0 < settings.note_duration_ms:
        raise ValueError("note duration must be positive")
    if settings.ticks_per_quarter != 1000:
        raise ValueError("this millisecond score requires exactly 1000 PPQ")
    if settings.tempo_microseconds_per_quarter != 1_000_000:
        raise ValueError("this millisecond score requires exactly 60 BPM")

    probabilities = history.clock_probabilities()
    qft_probabilities = analyze_history(history).clock_fourier_probabilities
    voices: list[LigetiClockVoice] = []
    for index in range(history.clock_states):
        interval_ms = settings.reference_interval_ms * _mode_multiplier(
            index,
            history.clock_states,
            settings.interval_bins_per_octave,
        )
        hit_budget = settings.hit_budget
        velocity = settings.velocity
        midi_note = settings.lowest_midi_note + index
        if midi_note > 127:
            raise ValueError("voice MIDI note exceeds 127")
        pan = int(round(64.0 + 63.0 * np.sin(
            2.0 * np.pi * index / history.clock_states
        )))
        voices.append(LigetiClockVoice(
            index=index,
            interval_ms=float(interval_ms),
            clock_probability=float(probabilities[index]),
            hit_budget=hit_budget,
            midi_note=midi_note,
            velocity=int(np.clip(velocity, 1, 127)),
            pan=int(np.clip(pan, 0, 127)),
            onsets_ms=_hit_onsets(word, interval_ms, hit_budget),
        ))

    ending_ms = max(
        voice.onsets_ms[-1] + settings.note_duration_ms for voice in voices
    )
    report: dict[str, object] = {
        "protocol_kind": "entangled_history_clock_step5_ligeti_score",
        "scientific_status": (
            "MIDI channels map one-to-one to computational clock-basis states; "
            "period spacing and finite winding are deterministic sonification "
            "controls"
        ),
        "config": asdict(settings),
        "voice_count": len(voices),
        "midi_channels": list(range(1, 17)),
        "clock_basis_labels": [
            f"|{voice.index:04b}>" for voice in voices
        ],
        "duration_ms": int(ending_ms),
        "midi_timebase": "60 BPM, 1000 PPQ, exactly 1 tick per millisecond",
        "musicxml_timebase": (
            "60 BPM, 1000 divisions per quarter, exactly 1 division per "
            "millisecond"
        ),
        "common_release_ms": 0,
        "voice_intervals_ms": [voice.interval_ms for voice in voices],
        "voice_hit_budgets": [voice.hit_budget for voice in voices],
        "voice_velocities": [voice.velocity for voice in voices],
        "clock_basis_probabilities": [
            voice.clock_probability for voice in voices
        ],
        "clock_qft_probabilities_diagnostic_only": qft_probabilities.tolist(),
        "last_event_by_voice_ms": [voice.onsets_ms[-1] for voice in voices],
        "mapping": {
            "channel_identity": (
                "MIDI channels 1-16 map to clock basis |0000>-|1111>"
            ),
            "period": (
                "clock-basis index maps to an exponential millisecond period"
            ),
            "pattern": "every voice independently repeats 10101",
            "velocity": "equal velocity preserves equal clock-basis probability",
            "winding": (
                "equal hit budgets plus unequal periods make voices exhaust "
                "at different wall-clock times"
            ),
            "form": "all clocks release together and exhaust independently",
        },
    }
    return LigetiClockScore(tuple(voices), settings, report)


def _variable_length(value: int) -> bytes:
    if value < 0:
        raise ValueError("MIDI delta time cannot be negative")
    buffer = value & 0x7F
    output = bytearray([buffer])
    while value > 0x7F:
        value >>= 7
        buffer = (value & 0x7F) | 0x80
        output.insert(0, buffer)
    return bytes(output)


def _meta(meta_type: int, payload: bytes) -> bytes:
    return bytes([0xFF, meta_type]) + _variable_length(len(payload)) + payload


def _track_chunk(events: list[tuple[int, int, bytes]]) -> bytes:
    data = bytearray()
    previous_tick = 0
    for absolute_tick, _, message in sorted(events, key=lambda item: (item[0], item[1])):
        data.extend(_variable_length(absolute_tick - previous_tick))
        data.extend(message)
        previous_tick = absolute_tick
    data.extend(b"\x00\xFF\x2F\x00")
    return b"MTrk" + struct.pack(">I", len(data)) + bytes(data)


def midi_bytes(score: LigetiClockScore) -> bytes:
    """Return a dependency-free Standard MIDI Type 1 representation."""

    conductor_events = [
        (0, 0, _meta(0x03, b"QMW Ligeti History Clock")),
        (0, 1, _meta(0x01, b"1 tick = 1 millisecond; sixteen fixed clocks")),
        (0, 2, _meta(0x51, score.config.tempo_microseconds_per_quarter.to_bytes(3, "big"))),
    ]
    tracks = [_track_chunk(conductor_events)]
    duration = score.config.note_duration_ms
    for voice in score.voices:
        channel = voice.index
        name = (
            f"Clock |{voice.index:04b}> | {voice.interval_ms:.3f} ms | "
            f"wind {voice.hit_budget}"
        ).encode("utf-8")
        events: list[tuple[int, int, bytes]] = [
            (0, 0, _meta(0x03, name)),
            (0, 1, bytes([0xB0 | channel, 10, voice.pan])),
        ]
        for onset in voice.onsets_ms:
            events.append((onset, 3, bytes([
                0x90 | channel,
                voice.midi_note,
                voice.velocity,
            ])))
            events.append((onset + duration, 2, bytes([
                0x80 | channel,
                voice.midi_note,
                0,
            ])))
        tracks.append(_track_chunk(events))
    header = b"MThd" + struct.pack(
        ">IHHH",
        6,
        1,
        len(tracks),
        score.config.ticks_per_quarter,
    )
    return header + b"".join(tracks)


_PITCH_CLASSES = (
    ("C", 0), ("C", 1), ("D", 0), ("D", 1),
    ("E", 0), ("F", 0), ("F", 1), ("G", 0),
    ("G", 1), ("A", 0), ("A", 1), ("B", 0),
)


def _append_duration_note(
    measure: ET.Element,
    *,
    duration: int,
    midi_note: int | None,
    velocity: int | None = None,
) -> None:
    if duration <= 0:
        return
    note = ET.SubElement(measure, "note")
    if midi_note is None:
        ET.SubElement(note, "rest")
    else:
        step, alter = _PITCH_CLASSES[midi_note % 12]
        pitch = ET.SubElement(note, "pitch")
        ET.SubElement(pitch, "step").text = step
        if alter:
            ET.SubElement(pitch, "alter").text = str(alter)
        ET.SubElement(pitch, "octave").text = str(midi_note // 12 - 1)
    ET.SubElement(note, "duration").text = str(duration)
    ET.SubElement(note, "voice").text = "1"
    if velocity is not None:
        note.set("dynamics", f"{100.0 * velocity / 90.0:.2f}")


def musicxml_bytes(score: LigetiClockScore) -> bytes:
    """Return a sixteen-part, millisecond-resolution MusicXML score."""

    root = ET.Element("score-partwise", version="4.0")
    work = ET.SubElement(root, "work")
    ET.SubElement(work, "work-title").text = "QMW Ligeti History Clock"
    identification = ET.SubElement(root, "identification")
    encoding = ET.SubElement(identification, "encoding")
    ET.SubElement(encoding, "software").text = "QMW entangled history clock"
    part_list = ET.SubElement(root, "part-list")
    for voice in score.voices:
        score_part = ET.SubElement(part_list, "score-part", id=f"P{voice.index + 1}")
        ET.SubElement(score_part, "part-name").text = (
            f"Clock |{voice.index:04b}> (MIDI Ch {voice.index + 1})"
        )
        abbreviation = ET.SubElement(score_part, "part-abbreviation")
        abbreviation.text = f"C{voice.index + 1:02d}"

    ending = int(score.report["duration_ms"])
    for voice in score.voices:
        part = ET.SubElement(root, "part", id=f"P{voice.index + 1}")
        measure = ET.SubElement(part, "measure", number="1", implicit="yes")
        attributes = ET.SubElement(measure, "attributes")
        ET.SubElement(attributes, "divisions").text = str(
            score.config.ticks_per_quarter
        )
        time = ET.SubElement(attributes, "time")
        ET.SubElement(time, "senza-misura")
        clef = ET.SubElement(attributes, "clef")
        ET.SubElement(clef, "sign").text = "G"
        ET.SubElement(clef, "line").text = "2"
        if voice.index == 0:
            direction = ET.SubElement(measure, "direction", placement="above")
            direction_type = ET.SubElement(direction, "direction-type")
            words = ET.SubElement(direction_type, "words")
            words.text = "1 division = 1 ms; independent fixed-period clocks"
            ET.SubElement(direction, "sound", tempo="60")
        cursor = 0
        for onset in voice.onsets_ms:
            _append_duration_note(
                measure,
                duration=onset - cursor,
                midi_note=None,
            )
            _append_duration_note(
                measure,
                duration=score.config.note_duration_ms,
                midi_note=voice.midi_note,
                velocity=voice.velocity,
            )
            cursor = onset + score.config.note_duration_ms
        _append_duration_note(
            measure,
            duration=ending - cursor,
            midi_note=None,
        )
        barline = ET.SubElement(measure, "barline", location="right")
        ET.SubElement(barline, "bar-style").text = "light-heavy"
    body = ET.tostring(root, encoding="utf-8", xml_declaration=False)
    declaration = b'<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n'
    doctype = (
        b'<!DOCTYPE score-partwise PUBLIC "-//Recordare//DTD MusicXML 4.0 '
        b'Partwise//EN" "http://www.musicxml.org/dtds/partwise.dtd">\n'
    )
    return declaration + doctype + body + b"\n"


def write_ligeti_clock_score(
    score: LigetiClockScore,
    output_directory: str | Path,
) -> dict[str, Path]:
    directory = Path(output_directory)
    directory.mkdir(parents=True, exist_ok=True)
    midi_path = directory / "history_clock_step5_ligeti_16_voices.mid"
    xml_path = directory / "history_clock_step5_ligeti_16_voices.musicxml"
    report_path = directory / "history_clock_step5_ligeti_report.json"
    midi_path.write_bytes(midi_bytes(score))
    xml_path.write_bytes(musicxml_bytes(score))
    report_path.write_text(json.dumps(score.report, indent=2) + "\n")
    return {"midi": midi_path, "musicxml": xml_path, "report": report_path}
