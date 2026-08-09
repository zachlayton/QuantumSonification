"""Rhythmic granular sonification for the entangled history clock.

A binary word is interpreted literally on a millisecond clock: ``1`` launches
a short history-state grain cloud and ``0`` is silence for one complete clock
cell.  Each launch contains all sixteen conditioned moments, while the
temporal-average and clock-QFT layers use the same gate.  The interval may
evolve, but it stretches the clock without changing the word or event order.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Mapping
import json

import numpy as np

from .control_study import build_control_study
from .diagnostics import (
    analyze_history,
    deterministic_density_eigendecomposition,
)
from .history_state import DiscreteHistoryState


@dataclass(frozen=True)
class GranularHistoryConfig:
    sample_rate: int = 48_000
    duration_seconds: float = 8.0
    rhythm_word: str = "10101"
    clock_interval_ms_start: float = 140.0
    clock_interval_ms_end: float = 110.0
    conditional_grain_seconds: float = 0.060
    average_grain_seconds: float = 0.070
    clock_grain_seconds: float = 0.045
    onset_spread_fraction: float = 0.08
    rhythm_pulse_seconds: float = 0.024
    conditional_base_frequency: float = 110.0
    average_base_frequency: float = 73.416
    clock_center_frequency: float = 440.0
    coherence_gain: float = 0.65
    seed: int = 23


@dataclass(frozen=True)
class GranularHistoryRender:
    rhythm_grid: np.ndarray
    conditional_cloud: np.ndarray
    temporal_average_cloud: np.ndarray
    clock_interference_cloud: np.ndarray
    dephased_clock_cloud: np.ndarray
    combined: np.ndarray
    report: Mapping[str, object]


def _pan(position: float) -> tuple[float, float]:
    normalized = float(np.clip(0.5 * (position + 1.0), 0.0, 1.0))
    angle = normalized * 0.5 * np.pi
    return float(np.cos(angle)), float(np.sin(angle))


def _grain_window(samples: int) -> np.ndarray:
    count = max(2, int(samples))
    phase = np.linspace(0.0, np.pi, count, endpoint=True)
    return np.sin(phase) ** 2


def _density_grain(
    density: np.ndarray,
    *,
    samples: int,
    sample_rate: int,
    base_frequency: float,
    coherence_gain: float,
) -> np.ndarray:
    """Synthesize one mono grain from populations and relative coherences."""

    rho = np.asarray(density, dtype=np.complex128)
    dimension = rho.shape[0]
    if rho.shape != (dimension, dimension):
        raise ValueError("density must be square")
    time = np.arange(int(samples), dtype=float) / float(sample_rate)
    frequencies = float(base_frequency) * 2.0 ** (
        np.arange(dimension, dtype=float) / 12.0
    )
    signal = np.zeros(time.size, dtype=float)
    populations = np.clip(np.diag(rho).real, 0.0, None)
    for basis_index, population in enumerate(populations):
        if population > 1e-12:
            signal += float(population) * np.sin(
                2.0 * np.pi * frequencies[basis_index] * time
            )

    edges: list[tuple[float, int, int, complex]] = []
    for left in range(dimension):
        for right in range(left + 1, dimension):
            value = rho[left, right]
            if abs(value) > 1e-12:
                edges.append((float(abs(value)), left, right, value))
    # Many coherences can have exactly the same physical magnitude.  Round
    # before sorting and use basis indices as deterministic tie breakers so
    # numerical noise from a global state phase cannot change the selected
    # subset of edges.
    edges.sort(key=lambda item: (
        -round(item[0], 12),
        item[1],
        item[2],
    ))
    for magnitude, left, right, value in edges[:24]:
        frequency = float(np.sqrt(frequencies[left] * frequencies[right]))
        signal += (
            float(coherence_gain)
            * 2.0
            * magnitude
            * np.sin(2.0 * np.pi * frequency * time + float(np.angle(value)))
        )
    maximum = float(np.max(np.abs(signal)))
    if maximum > 1e-15:
        signal /= maximum
    return signal * _grain_window(signal.size)


def _clock_grain(
    mode: int,
    dimension: int,
    *,
    samples: int,
    sample_rate: int,
    center_frequency: float,
) -> np.ndarray:
    time = np.arange(int(samples), dtype=float) / float(sample_rate)
    centered_mode = float(mode) - 0.5 * (dimension - 1)
    frequency = float(center_frequency) * 2.0 ** (centered_mode / 24.0)
    phase = 2.0 * np.pi * float(mode) / float(dimension)
    return (
        np.sin(2.0 * np.pi * frequency * time + phase)
        * _grain_window(time.size)
    )


def _rhythm_pulse(samples: int, sample_rate: int) -> np.ndarray:
    """A deterministic, dry transient that makes the bit gate explicit."""

    time = np.arange(int(samples), dtype=float) / float(sample_rate)
    envelope = np.exp(-55.0 * time)
    attack = np.minimum(1.0, time * 1600.0)
    return attack * envelope * (
        np.sin(2.0 * np.pi * 1450.0 * time)
        + 0.35 * np.sin(2.0 * np.pi * 2330.0 * time)
    )


def _place_grain(
    output: np.ndarray,
    grain: np.ndarray,
    onset_seconds: float,
    *,
    sample_rate: int,
    amplitude: float,
    pan: float,
) -> None:
    start = int(round(float(onset_seconds) * int(sample_rate)))
    stop = start + grain.size
    source_start = 0
    source_stop = grain.size
    if start < 0:
        source_start = -start
        start = 0
    if stop > output.shape[0]:
        source_stop -= stop - output.shape[0]
        stop = output.shape[0]
    if stop <= start or source_stop <= source_start:
        return
    left, right = _pan(pan)
    segment = float(amplitude) * grain[source_start:source_stop]
    output[start:stop, 0] += left * segment
    output[start:stop, 1] += right * segment


def _normalize(signal: np.ndarray, peak: float) -> np.ndarray:
    result = np.asarray(signal, dtype=float)
    maximum = float(np.max(np.abs(result)))
    return result.copy() if maximum <= 1e-15 else result * (peak / maximum)


def _validate_rhythm_word(word: str) -> str:
    normalized = "".join(str(word).split())
    if not normalized or any(bit not in "01" for bit in normalized):
        raise ValueError("rhythm_word must contain only 0 and 1")
    if "1" not in normalized:
        raise ValueError("rhythm_word must contain at least one sounding step")
    return normalized


def _millisecond_grid(
    config: GranularHistoryConfig,
) -> list[tuple[int, float, float, float, int]]:
    """Return (cell, onset, duration, interval_ms, bit) for the clock."""

    word = _validate_rhythm_word(config.rhythm_word)
    if (
        config.clock_interval_ms_start <= 0.0
        or config.clock_interval_ms_end <= 0.0
    ):
        raise ValueError("clock intervals must be positive")
    grid: list[tuple[int, float, float, float, int]] = []
    onset = 0.0
    step = 0
    while onset < config.duration_seconds:
        progress = min(1.0, onset / config.duration_seconds)
        interval_ms = (
            config.clock_interval_ms_start
            + progress
            * (config.clock_interval_ms_end - config.clock_interval_ms_start)
        )
        step_duration = interval_ms / 1000.0
        grid.append((
            step,
            onset,
            step_duration,
            interval_ms,
            int(word[step % len(word)]),
        ))
        onset += step_duration
        step += 1
    return grid


def render_granular_history(
    history: DiscreteHistoryState,
    config: GranularHistoryConfig | None = None,
) -> GranularHistoryRender:
    """Render concurrent conditional, average, and interference grain clouds."""

    settings = config or GranularHistoryConfig()
    if history.clock_states != 16:
        raise ValueError("granular reference requires a sixteen-state clock")
    if settings.sample_rate <= 0 or settings.duration_seconds <= 0.0:
        raise ValueError("sample rate and duration must be positive")
    total_samples = int(round(settings.sample_rate * settings.duration_seconds))
    rhythm = np.zeros((total_samples, 2), dtype=float)
    conditional = np.zeros((total_samples, 2), dtype=float)
    average = np.zeros_like(conditional)
    clock = np.zeros_like(conditional)
    dephased = np.zeros_like(conditional)
    diagnostics = analyze_history(history)
    controls = build_control_study(history, shuffle_seed=settings.seed)
    grid = _millisecond_grid(settings)
    sounding_steps = [entry for entry in grid if entry[4] == 1]
    minimum_step_seconds = min(entry[2] for entry in grid)
    maximum_layer_extent = max(
        settings.conditional_grain_seconds,
        settings.average_grain_seconds,
        settings.clock_grain_seconds,
        settings.rhythm_pulse_seconds,
    ) + settings.onset_spread_fraction * minimum_step_seconds
    if maximum_layer_extent >= minimum_step_seconds:
        raise ValueError(
            "grain duration plus onset spread must be shorter than the "
            "shortest clock interval so 0 remains a true rest"
        )

    pulse = _rhythm_pulse(
        int(round(settings.sample_rate * settings.rhythm_pulse_seconds)),
        settings.sample_rate,
    )
    for _, onset, _, _, _ in sounding_steps:
        _place_grain(
            rhythm,
            pulse,
            onset,
            sample_rate=settings.sample_rate,
            amplitude=0.32,
            pan=0.0,
        )

    conditional_densities = history.conditional_densities()
    conditional_grain_samples = int(round(
        settings.sample_rate * settings.conditional_grain_seconds
    ))
    conditional_grains = [
        _density_grain(
            density,
            samples=conditional_grain_samples,
            sample_rate=settings.sample_rate,
            base_frequency=settings.conditional_base_frequency,
            coherence_gain=settings.coherence_gain,
        )
        for density in conditional_densities
    ]
    conditional_events = 0
    for gate_index, (_, gate_onset, step_seconds, _, _) in enumerate(sounding_steps):
        # Every sounding step contains all moments. Rotation prevents their
        # tiny within-grain offset from masquerading as chronological order.
        rotation = (5 * gate_index) % history.clock_states
        for slot in range(history.clock_states):
            clock_index = (slot + rotation) % history.clock_states
            phase_position = float(
                np.sin(2.0 * np.pi * clock_index / history.clock_states)
            )
            spread = (
                settings.onset_spread_fraction
                * step_seconds
                * slot
                / history.clock_states
            )
            echo = float(diagnostics.loschmidt_echoes[clock_index])
            amplitude = 0.13 * (0.72 + 0.28 * (1.0 - echo))
            _place_grain(
                conditional,
                conditional_grains[clock_index],
                gate_onset + spread,
                sample_rate=settings.sample_rate,
                amplitude=amplitude,
                pan=phase_position,
            )
            conditional_events += 1

    # The reduced state is treated as a reservoir of eigenstate grains. This
    # preserves its mixed-state meaning without turning it into a sustained pad.
    eigenvalues, eigenmodes = deterministic_density_eigendecomposition(
        diagnostics.system_average_density
    )
    reservoir = [
        (float(eigenvalues[index]), np.outer(
            eigenmodes[index],
            eigenmodes[index].conj(),
        ))
        for index in range(eigenvalues.size)
        if eigenvalues[index] > 1e-10
    ]
    average_grain_samples = int(round(
        settings.sample_rate * settings.average_grain_seconds
    ))
    reservoir_grains = [
        _density_grain(
            density,
            samples=average_grain_samples,
            sample_rate=settings.sample_rate,
            base_frequency=settings.average_base_frequency,
            coherence_gain=settings.coherence_gain,
        )
        for _, density in reservoir
    ]
    average_events = 0
    cumulative = np.cumsum([weight for weight, _ in reservoir])
    cumulative /= cumulative[-1]
    golden = 0.6180339887498949
    for event_index, (_, onset, _, _, _) in enumerate(sounding_steps):
        quantile = (0.5 + event_index * golden) % 1.0
        reservoir_index = int(np.searchsorted(cumulative, quantile, side="right"))
        reservoir_index = min(reservoir_index, len(reservoir_grains) - 1)
        weight = reservoir[reservoir_index][0]
        _place_grain(
            average,
            reservoir_grains[reservoir_index],
            onset,
            sample_rate=settings.sample_rate,
            amplitude=0.34 * np.sqrt(weight),
            pan=-0.65 + 1.3 * ((event_index * golden) % 1.0),
        )
        average_events += 1

    # Coherent and dephased clock clouds share exactly the same event lattice.
    # Their only difference is the QFT-mode probability distribution.
    coherent_probabilities = diagnostics.clock_fourier_probabilities
    dephased_probabilities = np.diag(controls.incoherent_reduced_clock).real
    clock_grain_samples = int(round(
        settings.sample_rate * settings.clock_grain_seconds
    ))
    mode_grains = [
        _clock_grain(
            mode,
            history.clock_states,
            samples=clock_grain_samples,
            sample_rate=settings.sample_rate,
            center_frequency=settings.clock_center_frequency,
        )
        for mode in range(history.clock_states)
    ]
    clock_events = 0
    for _, gate_onset, step_seconds, _, _ in sounding_steps:
        for mode in range(history.clock_states):
            # Bins separated by N/2 share a micro-onset, making pi-paired
            # energy explicit as simultaneous but spectrally separated grains.
            pair_slot = mode % (history.clock_states // 2)
            onset = (
                gate_onset
                + settings.onset_spread_fraction
                * step_seconds
                * pair_slot
                / (history.clock_states // 2)
            )
            pan = float(np.sin(2.0 * np.pi * mode / history.clock_states))
            _place_grain(
                clock,
                mode_grains[mode],
                onset,
                sample_rate=settings.sample_rate,
                amplitude=0.42 * np.sqrt(coherent_probabilities[mode]),
                pan=pan,
            )
            _place_grain(
                dephased,
                mode_grains[mode],
                onset,
                sample_rate=settings.sample_rate,
                amplitude=0.42 * np.sqrt(dephased_probabilities[mode]),
                pan=pan,
            )
            clock_events += 1

    rhythm = _normalize(rhythm, 0.72)
    conditional = _normalize(conditional, 0.86)
    average = _normalize(average, 0.72)
    clock = _normalize(clock, 0.74)
    dephased = _normalize(dephased, 0.74)
    combined = _normalize(
        0.25 * rhythm + 0.66 * conditional + 0.38 * average + 0.48 * clock,
        0.92,
    )
    report: dict[str, object] = {
        "protocol_kind": "entangled_history_clock_step5_rhythmic_granular_render",
        "scientific_status": (
            "simulated coherent history; the binary rhythm word and tempo "
            "curve are classical audition controls, not quantum measurement"
        ),
        "config": asdict(settings),
        "event_counts": {
            "grid_steps": len(grid),
            "sounding_steps": len(sounding_steps),
            "rests": len(grid) - len(sounding_steps),
            "conditional": conditional_events,
            "temporal_average": average_events,
            "clock": clock_events,
        },
        "system_time_linear_entropy": diagnostics.system_time_linear_entropy,
        "clock_purity": diagnostics.clock_purity,
        "discrete_loschmidt_echo_average": (
            diagnostics.discrete_loschmidt_echo_average
        ),
        "clock_fourier_probabilities": coherent_probabilities.tolist(),
        "dephased_clock_probabilities": dephased_probabilities.tolist(),
        "mapping": {
            "rhythm": (
                "rhythm_word repeats on a millisecond clock: 1 launches all "
                "layers and 0 is silent for one complete clock interval"
            ),
            "conditional": (
                "all sixteen density-conditioned grains on every 1 step"
            ),
            "temporal_average": (
                "eigenvalue-weighted grains from the clock-traced reservoir"
            ),
            "clock_interference": (
                "QFT-weighted mode grains on 1 steps; bins separated by eight "
                "share micro-onsets"
            ),
            "clock_interval": (
                "linear millisecond-interval evolution stretches clock cells "
                "without changing the bit sequence; note values are optional "
                "external interpretations only"
            ),
        },
    }
    return GranularHistoryRender(
        rhythm_grid=rhythm,
        conditional_cloud=conditional,
        temporal_average_cloud=average,
        clock_interference_cloud=clock,
        dephased_clock_cloud=dephased,
        combined=combined,
        report=report,
    )


def write_granular_history(
    render: GranularHistoryRender,
    output_directory: str | Path,
    *,
    sample_rate: int,
) -> dict[str, Path]:
    import soundfile as sf

    directory = Path(output_directory)
    directory.mkdir(parents=True, exist_ok=True)
    signals = {
        "rhythm_grid": render.rhythm_grid,
        "conditional_cloud": render.conditional_cloud,
        "temporal_average_cloud": render.temporal_average_cloud,
        "clock_interference_cloud": render.clock_interference_cloud,
        "dephased_clock_cloud": render.dephased_clock_cloud,
        "combined_granular": render.combined,
    }
    paths: dict[str, Path] = {}
    for name, signal in signals.items():
        path = directory / f"history_clock_step5_{name}.wav"
        sf.write(path, signal.astype(np.float32), int(sample_rate), subtype="FLOAT")
        paths[name] = path
    report_path = directory / "history_clock_step5_granular_report.json"
    report_path.write_text(json.dumps(render.report, indent=2) + "\n")
    paths["report"] = report_path
    return paths
