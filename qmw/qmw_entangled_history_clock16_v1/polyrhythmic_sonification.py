"""Sixteen-voice independent-clock projection of an entangled history.

Each clock branch and clock-QFT mode receives its own repeating binary word
and millisecond interval. QFT modes separated by N/2 have a sqrt(2) period
ratio for N=16. These pulse trains are a sonification projection, not hidden
classical clocks asserted to exist inside the quantum state.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Mapping
import json

import numpy as np

from .control_study import build_control_study
from .diagnostics import analyze_history
from .granular_sonification import (
    _clock_grain,
    _density_grain,
    _normalize,
    _place_grain,
    _validate_rhythm_word,
)
from .history_state import DiscreteHistoryState


@dataclass(frozen=True)
class PolyrhythmicHistoryConfig:
    sample_rate: int = 48_000
    duration_seconds: float = 10.0
    rhythm_word: str = "10101"
    reference_interval_ms_start: float = 150.0
    reference_interval_ms_end: float = 112.0
    interval_bins_per_octave: float = 16.0
    conditional_grain_seconds: float = 0.042
    clock_grain_seconds: float = 0.032
    conditional_base_frequency: float = 110.0
    clock_center_frequency: float = 620.0
    coherence_gain: float = 0.65


@dataclass(frozen=True)
class PolyrhythmicHistoryRender:
    conditional_polycloud: np.ndarray
    coherent_clock_polyrhythm: np.ndarray
    dephased_clock_polyrhythm: np.ndarray
    combined: np.ndarray
    report: Mapping[str, object]


def _mode_multiplier(
    mode: int,
    dimension: int,
    bins_per_octave: float,
) -> float:
    centered = float(mode) - 0.5 * (dimension - 1)
    return float(2.0 ** (centered / float(bins_per_octave)))


def _local_clock_onsets(
    word: str,
    *,
    duration_seconds: float,
    interval_ms_start: float,
    interval_ms_end: float,
) -> np.ndarray:
    """Return sounding-cell onsets for one independently evolving voice."""

    pattern = _validate_rhythm_word(word)
    onset = 0.0
    cell = 0
    sounding: list[float] = []
    while onset < duration_seconds:
        if pattern[cell % len(pattern)] == "1":
            sounding.append(onset)
        progress = min(1.0, onset / duration_seconds)
        interval_ms = (
            interval_ms_start
            + progress * (interval_ms_end - interval_ms_start)
        )
        onset += interval_ms / 1000.0
        cell += 1
    return np.asarray(sounding, dtype=float)


def render_polyrhythmic_history(
    history: DiscreteHistoryState,
    config: PolyrhythmicHistoryConfig | None = None,
) -> PolyrhythmicHistoryRender:
    """Render sixteen branch voices and sixteen matched QFT-mode voices."""

    settings = config or PolyrhythmicHistoryConfig()
    if history.clock_states != 16:
        raise ValueError("polyrhythmic reference requires a sixteen-state clock")
    if settings.sample_rate <= 0 or settings.duration_seconds <= 0.0:
        raise ValueError("sample rate and duration must be positive")
    if (
        settings.reference_interval_ms_start <= 0.0
        or settings.reference_interval_ms_end <= 0.0
        or settings.interval_bins_per_octave <= 0.0
    ):
        raise ValueError("clock interval parameters must be positive")
    word = _validate_rhythm_word(settings.rhythm_word)
    total_samples = int(round(settings.sample_rate * settings.duration_seconds))
    conditional = np.zeros((total_samples, 2), dtype=float)
    coherent = np.zeros_like(conditional)
    dephased = np.zeros_like(conditional)
    diagnostics = analyze_history(history)
    controls = build_control_study(history)

    multipliers = np.asarray([
        _mode_multiplier(
            mode,
            history.clock_states,
            settings.interval_bins_per_octave,
        )
        for mode in range(history.clock_states)
    ])
    intervals_start = settings.reference_interval_ms_start * multipliers
    intervals_end = settings.reference_interval_ms_end * multipliers
    fastest_seconds = float(min(
        np.min(intervals_start),
        np.min(intervals_end),
    )) / 1000.0
    if max(
        settings.conditional_grain_seconds,
        settings.clock_grain_seconds,
    ) >= fastest_seconds:
        raise ValueError("grains must be shorter than the fastest local clock")

    onsets_by_voice = [
        _local_clock_onsets(
            word,
            duration_seconds=settings.duration_seconds,
            interval_ms_start=float(intervals_start[voice]),
            interval_ms_end=float(intervals_end[voice]),
        )
        for voice in range(history.clock_states)
    ]

    conditional_samples = int(round(
        settings.sample_rate * settings.conditional_grain_seconds
    ))
    conditional_grains = [
        _density_grain(
            density,
            samples=conditional_samples,
            sample_rate=settings.sample_rate,
            base_frequency=settings.conditional_base_frequency,
            coherence_gain=settings.coherence_gain,
        )
        for density in history.conditional_densities()
    ]
    conditional_events = 0
    for voice, onsets in enumerate(onsets_by_voice):
        pan = float(np.sin(2.0 * np.pi * voice / history.clock_states))
        echo = float(diagnostics.loschmidt_echoes[voice])
        amplitude = 0.075 * (0.72 + 0.28 * (1.0 - echo))
        for onset in onsets:
            _place_grain(
                conditional,
                conditional_grains[voice],
                float(onset),
                sample_rate=settings.sample_rate,
                amplitude=amplitude,
                pan=pan,
            )
            conditional_events += 1

    clock_samples = int(round(
        settings.sample_rate * settings.clock_grain_seconds
    ))
    mode_grains = [
        _clock_grain(
            mode,
            history.clock_states,
            samples=clock_samples,
            sample_rate=settings.sample_rate,
            center_frequency=settings.clock_center_frequency,
        )
        for mode in range(history.clock_states)
    ]
    coherent_probabilities = diagnostics.clock_fourier_probabilities
    dephased_probabilities = np.diag(controls.incoherent_reduced_clock).real
    clock_events = 0
    for voice, onsets in enumerate(onsets_by_voice):
        pan = float(np.sin(2.0 * np.pi * voice / history.clock_states))
        coherent_amplitude = 0.44 * np.sqrt(coherent_probabilities[voice])
        dephased_amplitude = 0.44 * np.sqrt(dephased_probabilities[voice])
        for onset in onsets:
            _place_grain(
                coherent,
                mode_grains[voice],
                float(onset),
                sample_rate=settings.sample_rate,
                amplitude=coherent_amplitude,
                pan=pan,
            )
            _place_grain(
                dephased,
                mode_grains[voice],
                float(onset),
                sample_rate=settings.sample_rate,
                amplitude=dephased_amplitude,
                pan=pan,
            )
            clock_events += 1

    conditional = _normalize(conditional, 0.82)
    coherent = _normalize(coherent, 0.78)
    dephased = _normalize(dephased, 0.78)
    combined = _normalize(0.64 * conditional + 0.72 * coherent, 0.92)
    dominant_modes = np.argsort(coherent_probabilities)[::-1][:4]
    report: dict[str, object] = {
        "protocol_kind": "entangled_history_clock_step5_polyrhythmic_render",
        "scientific_status": (
            "QFT probabilities come from the coherent history; independent "
            "millisecond pulse trains are a classical sonification projection"
        ),
        "config": asdict(settings),
        "voice_count": history.clock_states,
        "event_counts": {
            "conditional": conditional_events,
            "clock_per_condition": clock_events,
        },
        "voice_interval_ms_start": intervals_start.tolist(),
        "voice_interval_ms_end": intervals_end.tolist(),
        "voice_sounding_event_counts": [
            int(onsets.size) for onsets in onsets_by_voice
        ],
        "clock_fourier_probabilities": coherent_probabilities.tolist(),
        "dephased_clock_probabilities": dephased_probabilities.tolist(),
        "dominant_modes": [int(mode) for mode in dominant_modes],
        "dominant_mode_probabilities": [
            float(coherent_probabilities[mode]) for mode in dominant_modes
        ],
        "pi_pair_interval_ratio": float(
            intervals_start[9] / intervals_start[1]
        ),
        "mapping": {
            "binary_word": (
                "each of sixteen voices independently repeats 10101"
            ),
            "conditional": (
                "each conditioned history branch occupies its own local "
                "millisecond clock"
            ),
            "clock_interference": (
                "each QFT mode occupies the matching local clock and is "
                "weighted by its coherent QFT probability"
            ),
            "polyrhythm": (
                "exponential interval spacing makes modes eight bins apart "
                "run at a sqrt(2) period ratio"
            ),
        },
    }
    return PolyrhythmicHistoryRender(
        conditional_polycloud=conditional,
        coherent_clock_polyrhythm=coherent,
        dephased_clock_polyrhythm=dephased,
        combined=combined,
        report=report,
    )


def write_polyrhythmic_history(
    render: PolyrhythmicHistoryRender,
    output_directory: str | Path,
    *,
    sample_rate: int,
) -> dict[str, Path]:
    import soundfile as sf

    directory = Path(output_directory)
    directory.mkdir(parents=True, exist_ok=True)
    signals = {
        "conditional_polycloud": render.conditional_polycloud,
        "coherent_clock_polyrhythm": render.coherent_clock_polyrhythm,
        "dephased_clock_polyrhythm": render.dephased_clock_polyrhythm,
        "combined_polyrhythmic": render.combined,
    }
    paths: dict[str, Path] = {}
    for name, signal in signals.items():
        path = directory / f"history_clock_step5_{name}.wav"
        sf.write(path, signal.astype(np.float32), int(sample_rate), subtype="FLOAT")
        paths[name] = path
    report_path = directory / "history_clock_step5_polyrhythmic_report.json"
    report_path.write_text(json.dumps(render.report, indent=2) + "\n")
    paths["report"] = report_path
    return paths
