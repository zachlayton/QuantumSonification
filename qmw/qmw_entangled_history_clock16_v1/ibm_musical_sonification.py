"""Musically organized sonification of IBM history-clock measurements.

Unlike the direct shot renderer, this view aggregates the two IBM histograms
into sixteen clock classes ``t mod 16``.  Stable voice identity, Euclidean
cells, gradual phase displacement, registral pairing, staged entrances, and
thinning exits expose statistical relationships that are difficult to hear in
raw sampler order.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Mapping, Sequence
import json

import numpy as np

from .granular_sonification import _grain_window, _normalize, _place_grain
from .ibm_data_sonification import decode_shot


@dataclass(frozen=True)
class IBMMusicalConfig:
    sample_rate: int = 48_000
    duration_seconds: float = 36.0
    rhythm_steps: int = 16
    interval_ms_opening: float = 92.0
    interval_ms_middle: float = 71.0
    interval_ms_ending: float = 82.0
    voice_spread_octaves: float = 0.16
    grain_seconds: float = 0.024
    leakage_flam_ms: float = 9.0
    base_frequency: float = 118.0


@dataclass(frozen=True)
class IBMMusicalRender:
    musical_form: np.ndarray
    tonal_structure: np.ndarray
    forbidden_history_ghosts: np.ndarray
    voice_stems: np.ndarray
    report: Mapping[str, object]


def _euclidean_pattern(steps: int, hits: int, rotation: int) -> np.ndarray:
    """Return a deterministically rotated, maximally even binary pattern."""

    count = int(steps)
    pulses = int(np.clip(hits, 0, count))
    if pulses == 0:
        return np.zeros(count, dtype=int)
    pattern = np.asarray([
        int((index * pulses) % count < pulses) for index in range(count)
    ])
    return np.roll(pattern, int(rotation) % count)


def _tempo_interval_ms(progress: float, config: IBMMusicalConfig) -> float:
    position = float(np.clip(progress, 0.0, 1.0))
    if position < 0.58:
        local = position / 0.58
        smooth = 0.5 - 0.5 * np.cos(np.pi * local)
        return float(
            config.interval_ms_opening
            + smooth * (config.interval_ms_middle - config.interval_ms_opening)
        )
    local = (position - 0.58) / 0.42
    smooth = 0.5 - 0.5 * np.cos(np.pi * local)
    return float(
        config.interval_ms_middle
        + smooth * (config.interval_ms_ending - config.interval_ms_middle)
    )


def _spectral_click(
    voice: int,
    upper_fraction: float,
    *,
    config: IBMMusicalConfig,
) -> np.ndarray:
    samples = int(round(config.sample_rate * config.grain_seconds))
    time = np.arange(samples, dtype=float) / config.sample_rate
    harmonic_ratios = np.asarray([
        1.0, 9 / 8, 5 / 4, 4 / 3, 3 / 2, 5 / 3, 7 / 4, 2.0,
    ])
    octave = voice // 8
    frequency = (
        config.base_frequency
        * harmonic_ratios[voice % 8]
        * (2.0 ** octave)
    )
    lower = np.sin(2.0 * np.pi * frequency * time)
    upper = np.sin(2.0 * np.pi * 2.0 * frequency * time + 0.28)
    edge = 0.18 * np.sin(2.0 * np.pi * 3.07 * frequency * time + 0.51)
    decay = np.exp(-(105.0 + 3.0 * voice) * time)
    attack = np.minimum(1.0, 2100.0 * time)
    return (
        attack
        * decay
        * _grain_window(samples)
        * ((1.0 - upper_fraction) * lower + upper_fraction * upper + edge)
    )


def _ghost_grain(
    voice: int,
    *,
    config: IBMMusicalConfig,
) -> np.ndarray:
    samples = int(round(config.sample_rate * 0.012))
    time = np.arange(samples, dtype=float) / config.sample_rate
    rng = np.random.default_rng(9109 + 65537 * voice)
    noise = rng.standard_normal(samples)
    tone = np.sin(2.0 * np.pi * (1700.0 + 43.0 * voice) * time)
    return (
        np.minimum(1.0, 4200.0 * time)
        * np.exp(-310.0 * time)
        * _grain_window(samples)
        * (0.58 * noise + 0.42 * tone)
    )


def _aggregate(
    shot_sequences: Mapping[str, Sequence[str]],
) -> dict[str, np.ndarray]:
    computational = np.zeros(64, dtype=int)
    forbidden = np.zeros(64, dtype=int)
    fourier = np.zeros(64, dtype=int)
    for shot in shot_sequences["computational"]:
        clock, system = decode_shot(shot)
        computational[clock] += 1
        forbidden[clock] += int(system != (0 if clock % 2 == 0 else 15))
    for shot in shot_sequences["clock_fourier"]:
        clock, _ = decode_shot(shot)
        fourier[clock] += 1
    return {
        "computational_clock_counts": computational,
        "forbidden_clock_counts": forbidden,
        "fourier_clock_counts": fourier,
        "computational_voice_counts": np.asarray([
            np.sum(computational[voice::16]) for voice in range(16)
        ]),
        "forbidden_voice_counts": np.asarray([
            np.sum(forbidden[voice::16]) for voice in range(16)
        ]),
        "fourier_voice_counts": np.asarray([
            np.sum(fourier[voice::16]) for voice in range(16)
        ]),
    }


def render_ibm_musical_form(
    shot_sequences: Mapping[str, Sequence[str]],
    config: IBMMusicalConfig | None = None,
) -> IBMMusicalRender:
    settings = config or IBMMusicalConfig()
    if settings.sample_rate <= 0 or settings.duration_seconds <= 0.0:
        raise ValueError("sample rate and duration must be positive")
    if settings.rhythm_steps != 16:
        raise ValueError("the reference form requires sixteen-cell patterns")

    data = _aggregate(shot_sequences)
    comp = data["computational_voice_counts"].astype(float)
    leak = data["forbidden_voice_counts"].astype(float)
    fourier = data["fourier_voice_counts"].astype(float)
    fourier_bins = data["fourier_clock_counts"]
    comp_bins = data["computational_clock_counts"]

    comp_normalized = (comp - comp.min()) / max(float(np.ptp(comp)), 1.0)
    hits = np.rint(3.0 + 4.0 * comp_normalized).astype(int)
    rotations = np.asarray([
        int(np.argmax(comp_bins[voice::16])) * 4 + voice // 4
        for voice in range(16)
    ])
    patterns = np.asarray([
        _euclidean_pattern(settings.rhythm_steps, hits[voice], rotations[voice])
        for voice in range(16)
    ])

    lower_mass = np.asarray([
        fourier_bins[voice] + fourier_bins[voice + 16]
        for voice in range(16)
    ], dtype=float)
    upper_mass = np.asarray([
        fourier_bins[voice + 32] + fourier_bins[voice + 48]
        for voice in range(16)
    ], dtype=float)
    upper_fraction = upper_mass / np.maximum(lower_mass + upper_mass, 1.0)
    pair_imbalance = (upper_mass - lower_mass) / np.maximum(
        lower_mass + upper_mass, 1.0
    )
    prominence = np.sqrt(fourier / max(float(fourier.max()), 1.0))
    order = np.argsort(fourier)[::-1]
    ranks = np.empty(16, dtype=int)
    ranks[order] = np.arange(16)

    entry_times = np.asarray([
        0.45 * ranks[voice] + 0.12 * (voice % 4) for voice in range(16)
    ])
    exit_times = np.asarray([
        settings.duration_seconds - 0.48 * ranks[voice]
        for voice in range(16)
    ])
    total_samples = int(round(settings.sample_rate * settings.duration_seconds))
    tonal = np.zeros((total_samples, 2), dtype=float)
    ghosts = np.zeros_like(tonal)
    stems = np.zeros((16, total_samples, 2), dtype=float)
    grains = [
        _spectral_click(
            voice,
            float(upper_fraction[voice]),
            config=settings,
        )
        for voice in range(16)
    ]
    ghost_grains = [_ghost_grain(voice, config=settings) for voice in range(16)]

    event_counts = np.zeros(16, dtype=int)
    ghost_counts = np.zeros(16, dtype=int)
    leak_accumulators = np.zeros(16, dtype=float)
    for voice in range(16):
        onset = float(entry_times[voice])
        step = int(rotations[voice])
        local_cell_scale = 2.0 ** (
            settings.voice_spread_octaves * (voice - 7.5) / 15.0
            + 0.075 * pair_imbalance[voice]
        )
        pan_side = -1.0 if voice % 2 == 0 else 1.0
        pan_radius = 0.20 + 0.70 * ((voice // 2) + 1) / 8.0
        pan = float(pan_side * pan_radius)
        accent_values = comp_bins[voice::16].astype(float)
        accent_values /= max(float(accent_values.max()), 1.0)
        leakage_rate = leak[voice] / max(comp[voice], 1.0)

        while onset < float(exit_times[voice]):
            cell = step % settings.rhythm_steps
            if patterns[voice, cell]:
                lane = (step // settings.rhythm_steps) % 4
                section = onset / settings.duration_seconds
                # The middle of the form favors the full ensemble; entrances
                # and exits remain softer so the statistical hierarchy reads.
                arch = 0.62 + 0.38 * np.sin(np.pi * section) ** 2
                level = (
                    0.115
                    * (0.28 + 0.72 * prominence[voice])
                    * (0.62 + 0.38 * accent_values[lane])
                    * arch
                )
                _place_grain(
                    tonal,
                    grains[voice],
                    onset,
                    sample_rate=settings.sample_rate,
                    amplitude=level,
                    pan=pan,
                )
                _place_grain(
                    stems[voice],
                    grains[voice],
                    onset,
                    sample_rate=settings.sample_rate,
                    amplitude=level,
                    pan=pan,
                )
                event_counts[voice] += 1

                leak_accumulators[voice] += leakage_rate
                if leak_accumulators[voice] >= 1.0:
                    _place_grain(
                        ghosts,
                        ghost_grains[voice],
                        onset + settings.leakage_flam_ms / 1000.0,
                        sample_rate=settings.sample_rate,
                        amplitude=0.085 + 0.055 * leakage_rate,
                        pan=-0.82 * pan,
                    )
                    leak_accumulators[voice] -= 1.0
                    ghost_counts[voice] += 1

            progress = onset / settings.duration_seconds
            interval_ms = _tempo_interval_ms(progress, settings) * local_cell_scale
            onset += interval_ms / 1000.0
            step += 1

    tonal = _normalize(tonal, 0.82)
    ghosts = _normalize(ghosts, 0.54)
    combined = _normalize(0.90 * tonal + 0.46 * ghosts, 0.92)
    for voice in range(16):
        stems[voice] = _normalize(stems[voice], 0.70)

    report: dict[str, object] = {
        "protocol_kind": "qmw.ibm_history_clock64_musical_form.v1",
        "scientific_status": (
            "IBM histograms determine voice density, accents, prominence, "
            "register, phase rate, and ghost-note incidence; Euclidean cells, "
            "pitch lattice, orchestration, and sectional form are explicit "
            "musical transducers rather than additional quantum observables"
        ),
        "config": asdict(settings),
        "voice_identity": "clock class t modulo 16",
        "fourier_prominence_order": [int(value) for value in order],
        "computational_voice_counts": comp.astype(int).tolist(),
        "fourier_voice_counts": fourier.astype(int).tolist(),
        "forbidden_voice_counts": leak.astype(int).tolist(),
        "rhythm_hits_per_16_cells": hits.tolist(),
        "rhythm_rotations": rotations.tolist(),
        "rhythm_patterns": ["".join(map(str, row)) for row in patterns],
        "upper_octave_fractions": upper_fraction.tolist(),
        "pair_imbalances": pair_imbalance.tolist(),
        "entry_times_seconds": entry_times.tolist(),
        "exit_times_seconds": exit_times.tolist(),
        "rendered_event_counts": event_counts.tolist(),
        "rendered_ghost_counts": ghost_counts.tolist(),
        "mapping": {
            "density": "computational counts -> 3 to 7 hits per 16-cell pattern",
            "accent": "four clock states in each modulo-16 class -> four-cycle velocity shape",
            "prominence": "Fourier mass -> voice level and entrance/exit rank",
            "register": "lower/upper Fourier hemisphere balance -> octave color",
            "phase": "Fourier hemisphere imbalance -> local clock-rate displacement",
            "errors": "forbidden histories -> quiet fractured flams",
            "form": "strong Fourier voices enter first and remain longest",
        },
    }
    return IBMMusicalRender(
        musical_form=combined,
        tonal_structure=tonal,
        forbidden_history_ghosts=ghosts,
        voice_stems=stems,
        report=report,
    )


def write_ibm_musical_form(
    render: IBMMusicalRender,
    output_directory: str | Path,
    *,
    sample_rate: int,
) -> dict[str, Path]:
    import soundfile as sf

    directory = Path(output_directory)
    directory.mkdir(parents=True, exist_ok=True)
    paths: dict[str, Path] = {}
    signals = {
        "ibm_musical_form": render.musical_form,
        "ibm_musical_tonal_structure": render.tonal_structure,
        "ibm_musical_forbidden_ghosts": render.forbidden_history_ghosts,
    }
    for name, signal in signals.items():
        path = directory / f"{name}.wav"
        sf.write(path, signal.astype(np.float32), int(sample_rate), subtype="FLOAT")
        paths[name] = path
    stems_directory = directory / "stems"
    stems_directory.mkdir(parents=True, exist_ok=True)
    for voice, stem in enumerate(render.voice_stems):
        path = stems_directory / f"ibm_musical_voice_{voice:02d}.wav"
        sf.write(path, stem.astype(np.float32), int(sample_rate), subtype="FLOAT")
        paths[f"voice_{voice:02d}"] = path
    report_path = directory / "ibm_musical_form_report.json"
    report_path.write_text(json.dumps(render.report, indent=2) + "\n")
    paths["report"] = report_path
    return paths
