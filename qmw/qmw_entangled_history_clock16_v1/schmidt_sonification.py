"""Granular sonification of the clock's Schmidt temporal modes.

Clock labels remain the represented time coordinates.  Independent musical
voices are instead assigned to the nonzero eigenmodes of the reduced clock
density matrix.  This distinguishes the number of encoded moments from the
number of genuinely independent system--time correlations.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Mapping
import json

import numpy as np

from .diagnostics import analyze_history
from .granular_sonification import _grain_window, _normalize, _place_grain
from .history_state import DiscreteHistoryState


@dataclass(frozen=True)
class SchmidtRhythmConfig:
    sample_rate: int = 48_000
    duration_seconds: float = 10.0
    clock_interval_ms_start: float = 62.0
    clock_interval_ms_end: float = 43.0
    grain_seconds: float = 0.026
    phase_microtiming_fraction: float = 0.32
    base_frequency: float = 880.0
    max_modes: int = 16
    eigenvalue_tolerance: float = 1e-10
    coefficient_tolerance: float = 1e-10


@dataclass(frozen=True)
class SchmidtRhythmRender:
    coherent_phase_rhythm: np.ndarray
    magnitude_only_control: np.ndarray
    mode_stems: np.ndarray
    report: Mapping[str, object]


def _mode_grain(
    mode: int,
    *,
    samples: int,
    sample_rate: int,
    base_frequency: float,
) -> np.ndarray:
    time = np.arange(int(samples), dtype=float) / float(sample_rate)
    frequency = float(base_frequency) * 2.0 ** (float(mode) / 7.0)
    carrier = np.sin(2.0 * np.pi * frequency * time)
    overtone = 0.28 * np.sin(2.0 * np.pi * 1.73 * frequency * time + 0.4)
    attack = np.minimum(1.0, time * 2400.0)
    return attack * (carrier + overtone) * _grain_window(time.size)


def _clock_grid(
    config: SchmidtRhythmConfig,
    clock_states: int,
) -> list[tuple[int, float, float]]:
    """Return ``(clock_index, onset_seconds, interval_seconds)`` entries."""

    entries: list[tuple[int, float, float]] = []
    onset = 0.0
    step = 0
    while onset < config.duration_seconds:
        progress = min(1.0, onset / config.duration_seconds)
        interval_ms = (
            config.clock_interval_ms_start
            + progress
            * (config.clock_interval_ms_end - config.clock_interval_ms_start)
        )
        interval = interval_ms / 1000.0
        entries.append((step % clock_states, onset, interval))
        onset += interval
        step += 1
    return entries


def render_schmidt_rhythm(
    history: DiscreteHistoryState,
    config: SchmidtRhythmConfig | None = None,
) -> SchmidtRhythmRender:
    """Render nonzero Schmidt modes as phase-shaped granular voices."""

    settings = config or SchmidtRhythmConfig()
    if settings.sample_rate <= 0 or settings.duration_seconds <= 0.0:
        raise ValueError("sample rate and duration must be positive")
    if (
        settings.clock_interval_ms_start <= 0.0
        or settings.clock_interval_ms_end <= 0.0
        or settings.grain_seconds <= 0.0
    ):
        raise ValueError("clock intervals and grain duration must be positive")
    if not 0.0 <= settings.phase_microtiming_fraction < 0.5:
        raise ValueError("phase microtiming fraction must be in [0, 0.5)")
    if settings.max_modes <= 0:
        raise ValueError("max_modes must be positive")

    diagnostics = analyze_history(history)
    eigenvalues = diagnostics.clock_schmidt_eigenvalues
    active = np.flatnonzero(eigenvalues > settings.eigenvalue_tolerance)
    active = active[: min(settings.max_modes, history.system_dimension)]
    if active.size == 0:
        raise RuntimeError("history has no active Schmidt modes")
    modes = diagnostics.clock_schmidt_modes[active]
    weights = eigenvalues[active]

    total_samples = int(round(settings.sample_rate * settings.duration_seconds))
    coherent = np.zeros((total_samples, 2), dtype=float)
    control = np.zeros_like(coherent)
    stems = np.zeros((active.size, total_samples, 2), dtype=float)
    grain_samples = int(round(settings.sample_rate * settings.grain_seconds))
    grains = [
        _mode_grain(
            voice,
            samples=grain_samples,
            sample_rate=settings.sample_rate,
            base_frequency=settings.base_frequency,
        )
        for voice in range(active.size)
    ]
    grid = _clock_grid(settings, history.clock_states)

    event_counts = np.zeros(active.size, dtype=int)
    clock_supports: list[list[int]] = [[] for _ in range(active.size)]
    for clock_index, onset, interval in grid:
        for voice, (weight, mode, grain) in enumerate(
            zip(weights, modes, grains)
        ):
            coefficient = mode[clock_index]
            probability = float(abs(coefficient) ** 2)
            if probability <= settings.coefficient_tolerance:
                continue
            relative_level = float(np.sqrt(
                weight * history.clock_states * probability
            ))
            phase = float(np.angle(coefficient))
            phase_offset = (
                settings.phase_microtiming_fraction * interval * phase / np.pi
            )
            pan = (
                0.0
                if active.size == 1
                else -0.78 + 1.56 * voice / float(active.size - 1)
            )
            amplitude = 0.20 * relative_level
            _place_grain(
                coherent,
                grain,
                onset + phase_offset,
                sample_rate=settings.sample_rate,
                amplitude=amplitude,
                pan=pan,
            )
            _place_grain(
                stems[voice],
                grain,
                onset + phase_offset,
                sample_rate=settings.sample_rate,
                amplitude=amplitude,
                pan=pan,
            )
            _place_grain(
                control,
                grain,
                onset,
                sample_rate=settings.sample_rate,
                amplitude=amplitude,
                pan=pan,
            )
            event_counts[voice] += 1
            if clock_index not in clock_supports[voice]:
                clock_supports[voice].append(clock_index)

    coherent = _normalize(coherent, 0.92)
    control = _normalize(control, 0.92)
    for voice in range(active.size):
        stems[voice] = _normalize(stems[voice], 0.82)

    report: dict[str, object] = {
        "protocol_kind": "qmw.schmidt_temporal_mode_sonification.v1",
        "scientific_status": (
            "clock positions are encoded moments; voices are nonzero Schmidt "
            "modes; eigenvector phase is an auditory microtiming transducer"
        ),
        "config": asdict(settings),
        "clock_states": history.clock_states,
        "system_dimension": history.system_dimension,
        "maximum_possible_schmidt_rank": min(
            history.clock_states,
            history.system_dimension,
        ),
        "effective_schmidt_rank": diagnostics.effective_schmidt_rank,
        "rendered_mode_count": int(active.size),
        "clock_purity": diagnostics.clock_purity,
        "linear_entropy_E2": diagnostics.system_time_linear_entropy,
        "schmidt_participation_number": (
            diagnostics.schmidt_participation_number
        ),
        "schmidt_von_neumann_entropy_bits": (
            diagnostics.schmidt_von_neumann_entropy_bits
        ),
        "active_eigenvalues": [float(value) for value in weights],
        "mode_event_counts": [int(value) for value in event_counts],
        "mode_clock_supports": clock_supports,
        "mapping": {
            "voice_identity": "one voice per nonzero clock Schmidt mode",
            "event_location": "nonzero mode coefficient at clock position t",
            "event_level": "sqrt(lambda_k * N * |v_k(t)|^2)",
            "microtiming": "bounded mapping of arg(v_k(t)) within clock cell",
            "control": "same eigenvalues, magnitudes, clock grid, and grains; phase microtiming removed",
        },
    }
    return SchmidtRhythmRender(
        coherent_phase_rhythm=coherent,
        magnitude_only_control=control,
        mode_stems=stems,
        report=report,
    )


def write_schmidt_rhythm(
    render: SchmidtRhythmRender,
    output_directory: str | Path,
    *,
    sample_rate: int,
) -> dict[str, Path]:
    import soundfile as sf

    directory = Path(output_directory)
    directory.mkdir(parents=True, exist_ok=True)
    paths: dict[str, Path] = {}
    for name, signal in {
        "schmidt_coherent_phase_rhythm": render.coherent_phase_rhythm,
        "schmidt_magnitude_only_control": render.magnitude_only_control,
    }.items():
        path = directory / f"{name}.wav"
        sf.write(path, signal.astype(np.float32), int(sample_rate), subtype="FLOAT")
        paths[name] = path
    for voice, stem in enumerate(render.mode_stems):
        path = directory / f"schmidt_mode_{voice + 1:02d}.wav"
        sf.write(path, stem.astype(np.float32), int(sample_rate), subtype="FLOAT")
        paths[f"mode_{voice + 1:02d}"] = path
    report_path = directory / "schmidt_rhythm_report.json"
    report_path.write_text(json.dumps(render.report, indent=2) + "\n")
    paths["report"] = report_path
    return paths
