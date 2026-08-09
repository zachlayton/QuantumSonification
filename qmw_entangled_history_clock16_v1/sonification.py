"""Offline proof-of-concept sonification for the entangled history clock.

The renderer exposes three matched views of one prepared history:

1. clock-conditioned system moments;
2. the clock-traced temporal-average system state;
3. the clock-QFT distribution carrying coherent history interference.

All system audio is derived from density operators, never from global
state-vector phase.  This keeps the render invariant under |psi> -> e^(i phi)|psi>.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Mapping
import json

import numpy as np

from .control_study import build_control_study
from .diagnostics import HistoryDiagnostics, analyze_history
from .history_state import DiscreteHistoryState


@dataclass(frozen=True)
class HistorySonificationConfig:
    sample_rate: int = 48_000
    step_duration_seconds: float = 0.5
    system_base_frequency: float = 110.0
    average_frequency_ratio: float = 0.5
    clock_center_frequency: float = 440.0
    coherence_gain: float = 0.65
    edge_limit: int = 24
    fade_seconds: float = 0.02
    shuffle_seed: int = 23

    @property
    def duration_seconds(self) -> float:
        return 16.0 * self.step_duration_seconds


@dataclass(frozen=True)
class HistoryAudioRender:
    conditional: np.ndarray
    temporal_average: np.ndarray
    clock_interference: np.ndarray
    dephased_clock_reference: np.ndarray
    combined: np.ndarray
    report: Mapping[str, object]


def _constant_power_pan(position: float) -> tuple[float, float]:
    normalized = float(np.clip(0.5 * (position + 1.0), 0.0, 1.0))
    angle = 0.5 * np.pi * normalized
    return float(np.cos(angle)), float(np.sin(angle))


def _fade(signal: np.ndarray, fade_samples: int) -> np.ndarray:
    result = np.asarray(signal, dtype=float).copy()
    count = min(max(0, int(fade_samples)), result.shape[0] // 2)
    if count:
        ramp = np.sin(np.linspace(0.0, 0.5 * np.pi, count, endpoint=True)) ** 2
        result[:count] *= ramp[:, np.newaxis]
        result[-count:] *= ramp[::-1, np.newaxis]
    return result


def _peak_normalize(signal: np.ndarray, peak: float = 0.92) -> np.ndarray:
    result = np.asarray(signal, dtype=float)
    maximum = float(np.max(np.abs(result))) if result.size else 0.0
    if maximum <= 1e-15:
        return result.copy()
    return result * (float(peak) / maximum)


def _render_density_timbre(
    density: np.ndarray,
    time_seconds: np.ndarray,
    *,
    base_frequency: float,
    coherence_gain: float,
    edge_limit: int,
) -> np.ndarray:
    """Render populations as carriers and relative coherences as side tones."""

    rho = np.asarray(density, dtype=np.complex128)
    dimension = rho.shape[0]
    if rho.shape != (dimension, dimension):
        raise ValueError("density must be square")
    frequencies = float(base_frequency) * 2.0 ** (
        np.arange(dimension, dtype=float) / 12.0
    )
    output = np.zeros((time_seconds.size, 2), dtype=float)
    weights = 0.0

    populations = np.clip(np.diag(rho).real, 0.0, None)
    for basis_index, population in enumerate(populations):
        if population <= 1e-12:
            continue
        pan = -0.82 + 1.64 * basis_index / max(1, dimension - 1)
        left, right = _constant_power_pan(pan)
        tone = float(population) * np.sin(
            2.0 * np.pi * frequencies[basis_index] * time_seconds
        )
        output[:, 0] += left * tone
        output[:, 1] += right * tone
        weights += float(population)

    edges: list[tuple[float, int, int, complex]] = []
    for left_index in range(dimension):
        for right_index in range(left_index + 1, dimension):
            value = rho[left_index, right_index]
            magnitude = float(abs(value))
            if magnitude > 1e-12:
                edges.append((magnitude, left_index, right_index, value))
    edges.sort(reverse=True, key=lambda item: item[0])
    for magnitude, left_index, right_index, value in edges[: int(edge_limit)]:
        amplitude = float(coherence_gain) * 2.0 * magnitude
        frequency = float(np.sqrt(frequencies[left_index] * frequencies[right_index]))
        phase = float(np.angle(value))
        pan = -0.82 + 1.64 * (left_index + right_index) / max(
            1,
            2 * (dimension - 1),
        )
        left, right = _constant_power_pan(pan)
        tone = amplitude * np.sin(2.0 * np.pi * frequency * time_seconds + phase)
        output[:, 0] += left * tone
        output[:, 1] += right * tone
        weights += amplitude

    if weights > 1e-15:
        output /= max(1.0, np.sqrt(weights))
    return output


def _render_clock_modes(
    probabilities: np.ndarray,
    time_seconds: np.ndarray,
    *,
    center_frequency: float,
) -> np.ndarray:
    """Render clock-QFT probabilities as an energy-normalized stereo chord."""

    values = np.asarray(probabilities, dtype=float).reshape(-1)
    if values.size == 0 or np.any(values < -1e-12):
        raise ValueError("clock probabilities must be nonnegative")
    total = float(values.sum())
    if total <= 1e-15:
        raise ValueError("clock probabilities must have positive total")
    values = np.clip(values / total, 0.0, None)
    dimension = values.size
    mode_center = 0.5 * (dimension - 1)
    frequencies = float(center_frequency) * 2.0 ** (
        (np.arange(dimension, dtype=float) - mode_center) / 24.0
    )
    output = np.zeros((time_seconds.size, 2), dtype=float)
    for mode, probability in enumerate(values):
        if probability <= 1e-12:
            continue
        amplitude = float(np.sqrt(probability))
        pan = float(np.sin(2.0 * np.pi * mode / dimension))
        left, right = _constant_power_pan(pan)
        phase = 2.0 * np.pi * mode / dimension
        tone = amplitude * np.sin(
            2.0 * np.pi * frequencies[mode] * time_seconds + phase
        )
        output[:, 0] += left * tone
        output[:, 1] += right * tone
    return output / np.sqrt(dimension)


def render_history_audio(
    history: DiscreteHistoryState,
    config: HistorySonificationConfig | None = None,
) -> HistoryAudioRender:
    """Render all proof-of-concept stems for one coherent history state."""

    settings = config or HistorySonificationConfig()
    if settings.sample_rate <= 0 or settings.step_duration_seconds <= 0.0:
        raise ValueError("sample rate and step duration must be positive")
    if history.clock_states != 16:
        raise ValueError("step-5 reference render requires sixteen clock states")

    diagnostics: HistoryDiagnostics = analyze_history(history)
    controls = build_control_study(history, shuffle_seed=settings.shuffle_seed)
    samples_per_step = int(round(
        settings.sample_rate * settings.step_duration_seconds
    ))
    total_samples = samples_per_step * history.clock_states
    global_time = np.arange(total_samples, dtype=float) / settings.sample_rate
    fade_samples = int(round(settings.fade_seconds * settings.sample_rate))

    conditional = np.zeros((total_samples, 2), dtype=float)
    for clock_index, density in enumerate(history.conditional_densities()):
        start = clock_index * samples_per_step
        stop = start + samples_per_step
        segment_time = global_time[start:stop]
        segment = _render_density_timbre(
            density,
            segment_time,
            base_frequency=settings.system_base_frequency,
            coherence_gain=settings.coherence_gain,
            edge_limit=settings.edge_limit,
        )
        conditional[start:stop] = _fade(segment, fade_samples)

    temporal_average = _render_density_timbre(
        diagnostics.system_average_density,
        global_time,
        base_frequency=(
            settings.system_base_frequency * settings.average_frequency_ratio
        ),
        coherence_gain=settings.coherence_gain,
        edge_limit=settings.edge_limit,
    )
    temporal_average = _fade(temporal_average, fade_samples * 3)

    clock_interference = _render_clock_modes(
        diagnostics.clock_fourier_probabilities,
        global_time,
        center_frequency=settings.clock_center_frequency,
    )
    clock_interference = _fade(clock_interference, fade_samples * 3)
    dephased_probabilities = np.diag(controls.incoherent_reduced_clock).real
    dephased_clock = _render_clock_modes(
        dephased_probabilities,
        global_time,
        center_frequency=settings.clock_center_frequency,
    )
    dephased_clock = _fade(dephased_clock, fade_samples * 3)

    conditional = _peak_normalize(conditional, 0.88)
    temporal_average = _peak_normalize(temporal_average, 0.72)
    clock_interference = _peak_normalize(clock_interference, 0.72)
    dephased_clock = _peak_normalize(dephased_clock, 0.72)
    combined = _peak_normalize(
        0.62 * conditional
        + 0.34 * temporal_average
        + 0.38 * clock_interference,
        0.92,
    )

    top_modes = np.argsort(
        diagnostics.clock_fourier_probabilities
    )[::-1][:5]
    report: dict[str, object] = {
        "protocol_kind": "entangled_history_clock_step5_offline_render",
        "scientific_status": "simulated coherent history; no clock measurement",
        "config": asdict(settings),
        "duration_seconds": total_samples / settings.sample_rate,
        "samples": total_samples,
        "system_time_linear_entropy": diagnostics.system_time_linear_entropy,
        "clock_purity": diagnostics.clock_purity,
        "discrete_loschmidt_echo_average": (
            diagnostics.discrete_loschmidt_echo_average
        ),
        "clock_fourier_probabilities": (
            diagnostics.clock_fourier_probabilities.tolist()
        ),
        "top_clock_modes": [
            {
                "mode": int(mode),
                "probability": float(
                    diagnostics.clock_fourier_probabilities[mode]
                ),
            }
            for mode in top_modes
        ],
        "dephased_clock_probabilities": dephased_probabilities.tolist(),
        "mapping": {
            "conditional": "system populations plus relative coherence edges",
            "temporal_average": "clock-traced system density drone",
            "clock_interference": "clock QFT probabilities as oscillator energy",
            "dephased_reference": "uniform QFT distribution after clock dephasing",
        },
    }
    return HistoryAudioRender(
        conditional=conditional,
        temporal_average=temporal_average,
        clock_interference=clock_interference,
        dephased_clock_reference=dephased_clock,
        combined=combined,
        report=report,
    )


def write_history_audio(
    render: HistoryAudioRender,
    output_directory: str | Path,
    *,
    sample_rate: int,
) -> dict[str, Path]:
    """Write stereo float WAV stems, combined mix, and a JSON report."""

    import soundfile as sf

    directory = Path(output_directory)
    directory.mkdir(parents=True, exist_ok=True)
    audio = {
        "conditional": render.conditional,
        "temporal_average": render.temporal_average,
        "clock_interference": render.clock_interference,
        "dephased_clock_reference": render.dephased_clock_reference,
        "combined": render.combined,
    }
    paths: dict[str, Path] = {}
    for name, signal in audio.items():
        path = directory / f"history_clock_step5_{name}.wav"
        sf.write(path, signal.astype(np.float32), int(sample_rate), subtype="FLOAT")
        paths[name] = path
    report_path = directory / "history_clock_step5_report.json"
    report_path.write_text(json.dumps(render.report, indent=2) + "\n")
    paths["report"] = report_path
    return paths
