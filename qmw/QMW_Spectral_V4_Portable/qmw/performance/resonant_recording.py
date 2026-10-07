"""Lightweight capture for V3 resonant-membrane performance events.

The JSON event record is authoritative.  The MusicXML sidecar is a compact
cue-score acknowledgement for the V3 recording panel; it is not QMW dynamics.
This module intentionally depends only on the Python standard library so an
inactive recording control can never prevent a V3 performance session from
starting.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import json
import math
from pathlib import Path
import re
from typing import Any
from xml.etree import ElementTree as ET


@dataclass(frozen=True)
class ResonantPerformanceEvent:
    """A serializable observation of one admitted resonant membrane event."""

    time_seconds: float
    revision: int
    event_id: str
    channel: str
    kind: str
    dominant_mode: int
    contact_azimuth: float
    amplitude_real: float
    amplitude_imag: float
    membrane_energy: float


def _safe_stem(value: str, *, fallback: str) -> str:
    stem = re.sub(r"[^A-Za-z0-9_-]", "_", str(value)).strip("_")
    return stem or fallback


class ResonantPerformanceRecorder:
    """Optional V3 recording sidecar with a small, explicit public contract."""

    def __init__(self, output_directory: str | Path) -> None:
        self.output_directory = Path(output_directory)
        self.active = False
        self.events: list[ResonantPerformanceEvent] = []
        self.take_id = "take"
        self.name = "QMW resonant performance"
        self.wav_path = ""
        self.fundamental_hz = 110.0
        self.decay_seconds = 0.2
        self.bpm = 120.0
        self.pitch_ratios: tuple[float, ...] = tuple()

    def start(
        self,
        *,
        take_id: str,
        name: str,
        wav_path: str,
        fundamental_hz: float,
        decay_seconds: float,
        bpm: float,
        pitch_ratios: list[float],
    ) -> None:
        values = [fundamental_hz, decay_seconds, bpm, *pitch_ratios]
        if (
            len(pitch_ratios) != 20
            or not all(math.isfinite(float(value)) and float(value) > 0.0 for value in values)
        ):
            raise ValueError(
                "recording requires positive finite frequency/decay/tempo and twenty pitch ratios"
            )
        self.take_id = _safe_stem(take_id, fallback="take")
        self.name = str(name).strip() or "QMW resonant performance"
        self.wav_path = str(wav_path)
        self.fundamental_hz = float(fundamental_hz)
        self.decay_seconds = float(decay_seconds)
        self.bpm = float(bpm)
        self.pitch_ratios = tuple(float(value) for value in pitch_ratios)
        self.events = []
        self.active = True

    def capture(self, frame: Any) -> None:
        """Append admitted events from a ``ResonantInteractionFrameV1`` only."""

        if not self.active:
            return
        for event in frame.events:
            amplitude = complex(event.amplitude)
            self.events.append(
                ResonantPerformanceEvent(
                    time_seconds=float(frame.time),
                    revision=int(frame.revision),
                    event_id=str(event.event_id),
                    channel=str(event.channel),
                    kind=str(event.kind),
                    dominant_mode=int(event.dominant_mode),
                    contact_azimuth=float(event.contact_azimuth),
                    amplitude_real=float(amplitude.real),
                    amplitude_imag=float(amplitude.imag),
                    membrane_energy=float(sum(float(value) for value in event.membrane_energy)),
                )
            )

    def stop(self) -> dict[str, Any]:
        if not self.active:
            raise ValueError("performance recorder is not active")
        self.active = False
        self.output_directory.mkdir(parents=True, exist_ok=True)
        stem = f"qmw_resonant_v3_{self.take_id}"
        event_json = self.output_directory / f"{stem}.events.json"
        musicxml = self.output_directory / f"{stem}.musicxml"
        payload = {
            "schema": "qmw.resonant_performance.v1",
            "name": self.name,
            "take_id": self.take_id,
            "wav_path": self.wav_path,
            "fundamental_hz": self.fundamental_hz,
            "decay_seconds": self.decay_seconds,
            "bpm": self.bpm,
            "pitch_ratios": self.pitch_ratios,
            "event_count": len(self.events),
            "events": [asdict(event) for event in self.events],
        }
        event_json.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        self._write_musicxml_cue(musicxml)
        return {
            "event_count": len(self.events),
            "event_json": str(event_json),
            "musicxml": str(musicxml),
            "wav_path": self.wav_path,
        }

    def _write_musicxml_cue(self, path: Path) -> None:
        score = ET.Element("score-partwise", version="4.0")
        work = ET.SubElement(score, "work")
        ET.SubElement(work, "work-title").text = self.name
        part_list = ET.SubElement(score, "part-list")
        score_part = ET.SubElement(part_list, "score-part", id="P1")
        ET.SubElement(score_part, "part-name").text = "Resonant events"
        part = ET.SubElement(score, "part", id="P1")
        measure = ET.SubElement(part, "measure", number="1")
        attributes = ET.SubElement(measure, "attributes")
        ET.SubElement(attributes, "divisions").text = "1"
        time = ET.SubElement(attributes, "time")
        ET.SubElement(time, "beats").text = "4"
        ET.SubElement(time, "beat-type").text = "4"
        note = ET.SubElement(measure, "note")
        ET.SubElement(note, "rest")
        ET.SubElement(note, "duration").text = "4"
        direction = ET.SubElement(measure, "direction", placement="above")
        direction_type = ET.SubElement(direction, "direction-type")
        ET.SubElement(direction_type, "words").text = (
            f"{len(self.events)} admitted resonant events; see JSON sidecar for exact timing."
        )
        ET.indent(score, space="  ")
        ET.ElementTree(score).write(path, encoding="utf-8", xml_declaration=True)


__all__ = ["ResonantPerformanceEvent", "ResonantPerformanceRecorder"]
