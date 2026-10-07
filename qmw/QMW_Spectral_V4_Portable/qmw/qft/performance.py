"""Auditable performance capture and ensemble notation for QFT V3 pulses."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from fractions import Fraction
import json
import math
from pathlib import Path
import re
from typing import Any

import networkx as nx
import numpy as np
from music21 import clef, metadata

from .gaussian_temporal import GaussianFieldTemporalFrame
from .model import ScalarFieldModel
from .schema import ScalarFieldFrame
from .sonification import (
    gaussian_harmonic_descriptor,
    gaussian_pitch_deviation_control,
)


@dataclass(frozen=True)
class PerformanceEvent:
    onset_seconds: float
    field_time: float
    source_revision: int
    record_index: int
    site: int
    intrinsic_time: float
    delta_bures: float
    scaled_increment: float
    mean_phi: float
    mean_pi: float
    local_energy: float
    frequency_hz: float
    strength: float


@dataclass
class _NotatedPulse:
    """One downstream notation event; never a change to the pulse record."""

    event: PerformanceEvent
    onset_tick: Fraction
    duration_ticks: Fraction | None = None
    tuplet_ratio: tuple[int, int] | None = None
    tuplet_group: str | None = None


class FieldPerformanceRecorder:
    """Capture the pulse stream that also drives the SuperCollider voices."""

    def __init__(self, output_directory: Path, *, version: int = 3) -> None:
        self.output_directory = Path(output_directory)
        self.version = int(version)
        if self.version < 1:
            raise ValueError("performance schema version must be positive")
        self.sites = 8
        self.active = False
        self.events: list[PerformanceEvent] = []
        self.started_field_time = 0.0
        self.elapsed_seconds = 0.0
        self.name = "performance"
        self.take_id = "take"
        self.fundamental_hz = 72.0
        self.pitch_mode = 1
        self.pitch_deviation_cents = 0.0
        self.decay_seconds = 0.28
        self.bpm = 120.0

    def start(
        self,
        *,
        field_time: float,
        take_id: str,
        name: str,
        fundamental_hz: float,
        pitch_mode: int,
        decay_seconds: float,
        pitch_deviation_cents: float = 0.0,
        bpm: float = 120.0,
    ) -> None:
        if fundamental_hz <= 0 or decay_seconds <= 0 or bpm <= 0:
            raise ValueError("performance frequency, decay, and tempo must be positive")
        if pitch_mode not in (0, 1, 2):
            raise ValueError("pitch mode must be 0, 1, or 2")
        if not math.isfinite(pitch_deviation_cents) or not 0 <= pitch_deviation_cents <= 1200:
            raise ValueError("pitch deviation must lie in [0, 1200] cents")
        self.active = True
        self.events = []
        self.started_field_time = float(field_time)
        self.elapsed_seconds = 0.0
        self.take_id = re.sub(r"[^A-Za-z0-9_-]", "_", str(take_id)).strip("_")
        if not self.take_id:
            raise ValueError("performance take id must not be empty")
        self.name = str(name).strip() or "performance"
        self.fundamental_hz = float(fundamental_hz)
        self.pitch_mode = int(pitch_mode)
        self.pitch_deviation_cents = float(pitch_deviation_cents)
        self.decay_seconds = float(decay_seconds)
        self.bpm = float(bpm)

    def capture(
        self,
        frame: ScalarFieldFrame,
        temporal: GaussianFieldTemporalFrame,
        model: ScalarFieldModel,
        dt_seconds: float,
    ) -> None:
        if not self.active:
            return
        self.sites = int(model.spec.sites)
        if not math.isfinite(dt_seconds) or dt_seconds < 0:
            raise ValueError("performance time increment must be nonnegative")
        self.elapsed_seconds += float(dt_seconds)
        ratios = _site_pitch_ratios(model, self.pitch_mode)
        onset = self.elapsed_seconds
        for clock in temporal.site_clocks:
            first_record = clock.record_index - clock.pulses + 1
            descriptor = gaussian_harmonic_descriptor(
                clock,
                mass=model.spec.mass,
                propagation_speed=model.spec.propagation_speed,
                lattice_spacing=model.spec.lattice_spacing,
            )
            deviation_control = gaussian_pitch_deviation_control(descriptor)
            deviation_ratio = 2.0 ** (
                self.pitch_deviation_cents * deviation_control / 1200.0
            )
            strength = float(np.clip(0.12 + clock.scaled_increment * 12, 0.12, 1.5))
            for record_index in range(first_record, clock.record_index + 1):
                self.events.append(
                    PerformanceEvent(
                        onset_seconds=onset,
                        field_time=float(frame.time),
                        source_revision=int(clock.source_revision),
                        record_index=int(record_index),
                        site=int(clock.site),
                        intrinsic_time=float(clock.intrinsic_time),
                        delta_bures=float(clock.delta_bures),
                        scaled_increment=float(clock.scaled_increment),
                        mean_phi=float(clock.mean_phi),
                        mean_pi=float(clock.mean_pi),
                        local_energy=float(clock.local_energy),
                        frequency_hz=(
                            self.fundamental_hz
                            * float(ratios[clock.site])
                            * deviation_ratio
                        ),
                        strength=strength * (0.5 + 0.5 * descriptor.purity),
                    )
                )

    def configure(
        self,
        *,
        fundamental_hz: float,
        pitch_mode: int,
        decay_seconds: float,
        pitch_deviation_cents: float = 0.0,
    ) -> None:
        if fundamental_hz <= 0 or decay_seconds <= 0:
            raise ValueError("performance frequency and decay must be positive")
        if pitch_mode not in (0, 1, 2):
            raise ValueError("pitch mode must be 0, 1, or 2")
        if not math.isfinite(pitch_deviation_cents) or not 0 <= pitch_deviation_cents <= 1200:
            raise ValueError("pitch deviation must lie in [0, 1200] cents")
        self.fundamental_hz = float(fundamental_hz)
        self.pitch_mode = int(pitch_mode)
        self.pitch_deviation_cents = float(pitch_deviation_cents)
        self.decay_seconds = float(decay_seconds)

    def stop(self) -> dict[str, Any]:
        # Notation is an optional export capability, not a dependency of the
        # live field engine. Keep the import here so an installation without
        # the notation package can still run and sonify V4.2.
        from procedural_notation_v1 import write_lilypond, write_musicxml

        if not self.active:
            raise ValueError("performance recorder is not active")
        self.active = False
        self.output_directory.mkdir(parents=True, exist_ok=True)
        stem = f"qmw_qft_v{self.version}_{self.take_id}"
        json_path = self.output_directory / f"{stem}.events.json"
        musicxml_path = self.output_directory / f"{stem}.musicxml"
        lilypond_path = musicxml_path.with_suffix(".ly")
        score, notation_summary = _build_recorded_score(
            self.events,
            title=self.name,
            bpm=self.bpm,
            decay_seconds=self.decay_seconds,
            sites=self.sites,
        )
        score.metadata = metadata.Metadata()
        score.metadata.title = self.name
        score.metadata.composer = "QMW Gaussian scalar-field pulse capture"
        write_musicxml(score, musicxml_path)
        # The .ly sidecar is an engraving view of the exact same score.  The
        # event JSON remains authoritative for physical times/frequencies.
        write_lilypond(score, lilypond_path)
        capture_metadata = {
            "schema": f"qmw.scalar_field_performance.v{self.version}",
            "sites": self.sites,
            "name": self.name,
            "take_id": self.take_id,
            "fundamental_hz": self.fundamental_hz,
            "pitch_mode": self.pitch_mode,
            "pitch_deviation_cents": self.pitch_deviation_cents,
            "decay_seconds": self.decay_seconds,
            "tempo_bpm": self.bpm,
            "event_count": len(self.events),
            "events": [asdict(event) for event in self.events],
        "notation_boundary": {
            "onsets": "quantized to the nearest 64th note",
            "pitches": "nearest twelve-tone equal-tempered pitch",
            "parts": "one monophonic part per lattice site",
            "clefs": "bass below median MIDI 60, treble otherwise",
            "durations": "ordinary, dotted, and doubly-dotted values before ties",
            "tuplets": (
                "a 3-, 5-, or 7-pulse same-site quarter-beat cluster is written "
                "as 3:2, 5:4, or 7:4 only when its captured onsets fit that ratio"
            ),
            **notation_summary,
            "authoritative_event_data": str(json_path),
            },
        }
        json_path.write_text(
            json.dumps(capture_metadata, indent=2, sort_keys=True) + "\n"
        )
        return {
            "event_json": str(json_path),
            "musicxml": str(musicxml_path),
            "lilypond": str(lilypond_path),
            "event_count": len(self.events),
        }


def _site_pitch_ratios(model: ScalarFieldModel, pitch_mode: int) -> np.ndarray:
    if pitch_mode == 0:
        return model.frequencies / model.frequencies[0]
    if pitch_mode == 1:
        return np.arange(1, model.spec.sites + 1, dtype=float)
    return np.arange(1, 2 * model.spec.sites, 2, dtype=float)


def _midi_pitch(frequency_hz: float) -> tuple[str, int, int, float]:
    exact = 69.0 + 12.0 * math.log2(max(frequency_hz, 1e-9) / 440.0)
    midi = int(np.clip(round(exact), 0, 127))
    names = (("C", 0), ("C", 1), ("D", 0), ("D", 1), ("E", 0),
             ("F", 0), ("F", 1), ("G", 0), ("G", 1), ("A", 0),
             ("A", 1), ("B", 0))
    step, alter = names[midi % 12]
    return step, alter, midi // 12 - 1, 100.0 * (exact - midi)


def _build_recorded_score(
    events: list[PerformanceEvent],
    *,
    title: str,
    bpm: float,
    decay_seconds: float,
    sites: int,
) -> tuple[object, dict[str, int | float]]:
    """Build readable 64th-note notation from the captured pulse events.

    Physical event timing remains in the JSON sidecar.  This notation adapter
    only quantizes the recorded pulse onsets, preserving separate site streams
    as independent parts and never altering the scalar-field evolution.
    """
    from procedural_notation_v1 import build_polyphonic_timed_score

    ticks_per_quarter = 16
    beats_per_measure = 4
    ticks_per_second = ticks_per_quarter * bpm / 60.0
    measure_ticks = ticks_per_quarter * beats_per_measure
    decay_ticks = max(1, round(decay_seconds * ticks_per_second))

    events_by_site: dict[int, dict[int, PerformanceEvent]] = {
        site: {} for site in range(sites)
    }
    collision_count = 0
    for performance_event in events:
        if not 0 <= performance_event.site < sites:
            raise ValueError("performance event site lies outside the lattice")
        tick = max(0, round(performance_event.onset_seconds * ticks_per_second))
        previous = events_by_site[performance_event.site].get(tick)
        if previous is not None:
            collision_count += 1
            if previous.strength >= performance_event.strength:
                continue
        events_by_site[performance_event.site][tick] = performance_event

    plans_by_site = {
        site: _plan_site_rhythm(
            site,
            list(site_events.values()),
            bpm=bpm,
            ticks_per_quarter=ticks_per_quarter,
            decay_ticks=decay_ticks,
        )
        for site, site_events in events_by_site.items()
    }
    maximum_tick = max(
        (
            plan.onset_tick + (plan.duration_ticks or Fraction(decay_ticks))
            for plans in plans_by_site.values()
            for plan in plans
        ),
        default=Fraction(0),
    )
    measures = max(1, math.ceil(float(maximum_tick) / measure_ticks))
    total_ticks = measures * measure_ticks
    graph = nx.Graph()
    note_count = 0
    tuplet_group_count = 0
    for site, plans in plans_by_site.items():
        for index, plan in enumerate(plans):
            if plan.duration_ticks is None:
                raise RuntimeError("notation plan lacks a duration")
            if plan.tuplet_group is not None and (
                index == 0 or plans[index - 1].tuplet_group != plan.tuplet_group
            ):
                tuplet_group_count += 1
            graph.add_node(
                (site, index),
                voice=site,
                onset_tick=plan.onset_tick,
                duration_ticks=plan.duration_ticks,
                pitch=_pitch_name(plan.event.frequency_hz),
                dynamic_mark=_dynamic_mark(plan.event.strength),
                accent_type="accent",
                source_vertex=plan.event.record_index,
                **(
                    {
                        "tuplet_ratio": plan.tuplet_ratio,
                        "tuplet_group": plan.tuplet_group,
                    }
                    if plan.tuplet_ratio is not None
                    else {}
                ),
            )
            note_count += 1

    # Every site remains a visible, monophonic recording lane even when it did
    # not fire during this take.
    for site in range(sites):
        if not events_by_site[site]:
            graph.add_node(
                (site, "silent"),
                voice=site,
                onset_tick=0,
                duration_ticks=total_ticks,
                is_rest=True,
            )

    score = build_polyphonic_timed_score(
        graph,
        measures=measures,
        beats_per_measure=beats_per_measure,
        ticks_per_quarter=ticks_per_quarter,
        title=title,
        include_node_labels=False,
    )
    for site, part in enumerate(score.parts):
        part.id = f"P{site + 1}"
        part.partName = f"Lattice Site {site + 1}"
        part.getInstrument(returnDefault=True).partId = f"P{site + 1}"
        site_pitches = [
            69.0 + 12.0 * math.log2(event.frequency_hz / 440.0)
            for event in events_by_site[site].values()
        ]
        first_measure = part.measure(1)
        if first_measure is not None:
            first_measure.insert(
                0,
                clef.BassClef()
                if site_pitches and float(np.median(site_pitches)) < 60.0
                else clef.TrebleClef(),
            )
    return score, {
        "rhythm_subdivisions_per_quarter": ticks_per_quarter,
        "rhythm_note_value": 4 * ticks_per_quarter,
        "notated_event_count": note_count,
        "same_site_quantization_collisions": collision_count,
        "tuplet_group_count": tuplet_group_count,
    }


def _plan_site_rhythm(
    site: int,
    events: list[PerformanceEvent],
    *,
    bpm: float,
    ticks_per_quarter: int,
    decay_ticks: int,
) -> list[_NotatedPulse]:
    """Choose real tuplet groups before falling back to the 64th grid.

    A tuplet is a relationship, not a rescue label for arbitrary tiny notes.
    We therefore only use it for complete same-site clusters of 3, 5, or 7
    attacks inside one quarter-note beat whose captured onsets are already
    within one 64th note of the corresponding even ratio.
    """
    ticks_per_second = ticks_per_quarter * bpm / 60.0
    quarter_seconds = 60.0 / bpm
    buckets: dict[int, list[PerformanceEvent]] = {}
    for event in events:
        quarter_index = math.floor((event.onset_seconds / quarter_seconds) + 1e-9)
        buckets.setdefault(quarter_index, []).append(event)

    plans: list[_NotatedPulse] = []
    for quarter_index, bucket_events in sorted(buckets.items()):
        bucket_events.sort(key=lambda event: event.onset_seconds)
        ratio = _recognized_tuplet_ratio(
            bucket_events, quarter_index, quarter_seconds
        )
        if ratio is not None:
            actual, _normal = ratio
            group = f"site-{site}-quarter-{quarter_index}-{actual}"
            group_start = Fraction(quarter_index * ticks_per_quarter)
            pulse_duration = Fraction(ticks_per_quarter, actual)
            for index, event in enumerate(bucket_events):
                plans.append(
                    _NotatedPulse(
                        event=event,
                        onset_tick=group_start + index * pulse_duration,
                        duration_ticks=pulse_duration,
                        tuplet_ratio=ratio,
                        tuplet_group=group,
                    )
                )
            continue
        for event in bucket_events:
            plans.append(
                _NotatedPulse(
                    event=event,
                    onset_tick=Fraction(
                        max(0, round(event.onset_seconds * ticks_per_second))
                    ),
                )
            )

    plans.sort(key=lambda plan: plan.onset_tick)
    for index, plan in enumerate(plans):
        if plan.duration_ticks is not None:
            continue
        next_onset = (
            plans[index + 1].onset_tick
            if index + 1 < len(plans)
            else plan.onset_tick + decay_ticks
        )
        plan.duration_ticks = Fraction(
            max(1, min(decay_ticks, int(next_onset - plan.onset_tick)))
        )
    return plans


def _recognized_tuplet_ratio(
    events: list[PerformanceEvent],
    quarter_index: int,
    quarter_seconds: float,
) -> tuple[int, int] | None:
    """Return a conventional ratio only for a captured even pulse cluster."""
    actual = len(events)
    normal = {3: 2, 5: 4, 7: 4}.get(actual)
    if normal is None:
        return None
    quarter_start = quarter_index * quarter_seconds
    tolerance_seconds = quarter_seconds / 16.0
    for index, event in enumerate(events):
        target = quarter_start + (index * quarter_seconds / actual)
        if abs(event.onset_seconds - target) > tolerance_seconds:
            return None
    return actual, normal


def _pitch_name(frequency_hz: float) -> str:
    step, alter, octave, _ = _midi_pitch(frequency_hz)
    return f"{step}{'#' if alter else ''}{octave}"


def _dynamic_mark(strength: float) -> str:
    if strength < 0.2:
        return "pp"
    if strength < 0.45:
        return "p"
    if strength < 0.8:
        return "mf"
    if strength < 1.15:
        return "f"
    return "ff"


__all__ = ["FieldPerformanceRecorder", "PerformanceEvent"]
