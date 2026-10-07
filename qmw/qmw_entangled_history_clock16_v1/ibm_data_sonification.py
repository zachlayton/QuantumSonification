"""Direct sonification of returned IBM history-clock shot records.

The renderer preserves the sampler's returned shot order.  It does not claim
that this ordering is a calibrated wall-clock trace of processor execution.
No regular musical grid is added: circular changes between measured clock
values determine elapsed milliseconds between successive events.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Mapping, Sequence
import json

import numpy as np

from .granular_sonification import _grain_window, _normalize, _place_grain


@dataclass(frozen=True)
class IBMDataSonificationConfig:
    sample_rate: int = 48_000
    minimum_interval_ms: float = 12.0
    maximum_interval_ms: float = 48.0
    interval_curve: float = 0.72
    grain_seconds: float = 0.011
    computational_base_frequency: float = 185.0
    fourier_base_frequency: float = 640.0
    ab_gap_seconds: float = 1.25
    ideal_seed: int = 260802


@dataclass(frozen=True)
class IBMDataSonificationRender:
    ibm_computational: np.ndarray
    ibm_clock_fourier: np.ndarray
    ibm_combined: np.ndarray
    ideal_combined: np.ndarray
    ibm_then_ideal: np.ndarray
    report: Mapping[str, object]


def decode_shot(bitstring: str) -> tuple[int, int]:
    bits = str(bitstring).replace(" ", "")
    if len(bits) != 10 or any(bit not in "01" for bit in bits):
        raise ValueError(f"unexpected ten-qubit shot {bitstring!r}")
    return int(bits[:6], 2), int(bits[6:], 2)


def _circular_distance(left: int, right: int, dimension: int) -> int:
    direct = abs(int(left) - int(right))
    return int(min(direct, int(dimension) - direct))


def _interval_ms(
    previous_clock: int,
    clock: int,
    config: IBMDataSonificationConfig,
    *,
    fourier: bool,
) -> float:
    if fourier:
        previous_pair = previous_clock % 32
        pair = clock % 32
        distance = _circular_distance(previous_pair, pair, 32)
        normalized = distance / 16.0
        hemisphere_change = (previous_clock // 32) != (clock // 32)
        normalized = min(1.0, normalized + (0.18 if hemisphere_change else 0.0))
    else:
        normalized = _circular_distance(previous_clock, clock, 64) / 32.0
    shaped = normalized ** config.interval_curve
    return float(
        config.minimum_interval_ms
        + shaped * (config.maximum_interval_ms - config.minimum_interval_ms)
    )


def _event_grain(
    clock: int,
    system: int,
    *,
    fourier: bool,
    config: IBMDataSonificationConfig,
) -> tuple[np.ndarray, float, float]:
    samples = int(round(config.sample_rate * config.grain_seconds))
    time = np.arange(samples, dtype=float) / config.sample_rate
    window = _grain_window(samples)
    if fourier:
        pair = clock % 32
        upper = clock >= 32
        frequency = config.fourier_base_frequency * 2.0 ** (
            pair / 24.0 + (1.0 if upper else 0.0)
        )
        pan = 0.76 if upper else -0.76
        phase = 2.0 * np.pi * pair / 32.0
        signal = (
            np.sin(2.0 * np.pi * frequency * time + phase)
            + 0.24 * np.sin(2.0 * np.pi * 1.61 * frequency * time)
        )
        amplitude = 0.16 * (0.82 + 0.18 * system.bit_count() / 4.0)
    else:
        expected_system = 0 if clock % 2 == 0 else 15
        valid = system == expected_system
        frequency = config.computational_base_frequency * 2.0 ** (
            (clock % 16) / 18.0
        )
        pan = -0.58 if clock % 2 == 0 else 0.58
        carrier = np.sin(2.0 * np.pi * frequency * time)
        if valid:
            signal = carrier + 0.18 * np.sin(2.0 * np.pi * 2.03 * frequency * time)
            amplitude = 0.13
        else:
            seed = 65537 * clock + 257 * system
            noise = np.random.default_rng(seed).standard_normal(samples)
            signal = 0.48 * carrier + 0.52 * noise
            amplitude = 0.21
    attack = np.minimum(1.0, 3000.0 * time)
    decay = np.exp(-170.0 * time)
    return attack * decay * window * signal, float(amplitude), float(pan)


def _schedule(
    shots: Sequence[str],
    config: IBMDataSonificationConfig,
    *,
    fourier: bool,
) -> tuple[list[tuple[float, int, int]], np.ndarray]:
    if not shots:
        raise ValueError("shot sequence must not be empty")
    decoded = [decode_shot(shot) for shot in shots]
    events: list[tuple[float, int, int]] = []
    intervals: list[float] = []
    onset = 0.04
    previous_clock = decoded[0][0]
    for clock, system in decoded:
        events.append((onset, clock, system))
        interval = _interval_ms(
            previous_clock,
            clock,
            config,
            fourier=fourier,
        )
        intervals.append(interval)
        onset += interval / 1000.0
        previous_clock = clock
    return events, np.asarray(intervals, dtype=float)


def _render_events(
    events: Sequence[tuple[float, int, int]],
    config: IBMDataSonificationConfig,
    *,
    fourier: bool,
    total_samples: int,
) -> np.ndarray:
    output = np.zeros((total_samples, 2), dtype=float)
    for onset, clock, system in events:
        grain, amplitude, pan = _event_grain(
            clock,
            system,
            fourier=fourier,
            config=config,
        )
        _place_grain(
            output,
            grain,
            onset,
            sample_rate=config.sample_rate,
            amplitude=amplitude,
            pan=pan,
        )
    return output


def _shot_string(clock: int, system: int) -> str:
    return f"{int(clock):06b}{int(system):04b}"


def ideal_shot_sequences(
    shots: int,
    ideal_fourier_probabilities: Sequence[float],
    *,
    seed: int,
) -> dict[str, list[str]]:
    rng = np.random.default_rng(int(seed))
    clocks = rng.integers(0, 64, int(shots))
    computational = [
        _shot_string(clock, 0 if clock % 2 == 0 else 15)
        for clock in clocks
    ]
    probabilities = np.asarray(ideal_fourier_probabilities, dtype=float)
    probabilities /= probabilities.sum()
    fourier_clocks = rng.choice(64, int(shots), p=probabilities)
    # The clock marginal is the target of this circuit.  System zero is used
    # only as a neutral timbral value in the matched reference.
    fourier = [_shot_string(clock, 0) for clock in fourier_clocks]
    return {"computational": computational, "clock_fourier": fourier}


def render_ibm_data(
    shot_sequences: Mapping[str, Sequence[str]],
    ideal_fourier_probabilities: Sequence[float],
    config: IBMDataSonificationConfig | None = None,
) -> IBMDataSonificationRender:
    settings = config or IBMDataSonificationConfig()
    computational_shots = list(shot_sequences["computational"])
    fourier_shots = list(shot_sequences["clock_fourier"])
    if len(computational_shots) != len(fourier_shots):
        raise ValueError("the two IBM circuits must have equal shot counts")

    computational_events, computational_intervals = _schedule(
        computational_shots,
        settings,
        fourier=False,
    )
    fourier_events, fourier_intervals = _schedule(
        fourier_shots,
        settings,
        fourier=True,
    )
    duration = max(
        computational_events[-1][0],
        fourier_events[-1][0],
    ) + settings.grain_seconds + 0.05
    total_samples = int(np.ceil(duration * settings.sample_rate))
    computational = _render_events(
        computational_events,
        settings,
        fourier=False,
        total_samples=total_samples,
    )
    fourier = _render_events(
        fourier_events,
        settings,
        fourier=True,
        total_samples=total_samples,
    )
    computational = _normalize(computational, 0.78)
    fourier = _normalize(fourier, 0.78)
    combined = _normalize(0.72 * computational + 0.72 * fourier, 0.92)

    ideal_sequences = ideal_shot_sequences(
        len(computational_shots),
        ideal_fourier_probabilities,
        seed=settings.ideal_seed,
    )
    ideal_comp_events, _ = _schedule(
        ideal_sequences["computational"], settings, fourier=False
    )
    ideal_fourier_events, _ = _schedule(
        ideal_sequences["clock_fourier"], settings, fourier=True
    )
    ideal_duration = max(
        ideal_comp_events[-1][0], ideal_fourier_events[-1][0]
    ) + settings.grain_seconds + 0.05
    ideal_samples = int(np.ceil(ideal_duration * settings.sample_rate))
    ideal_comp = _render_events(
        ideal_comp_events,
        settings,
        fourier=False,
        total_samples=ideal_samples,
    )
    ideal_fourier = _render_events(
        ideal_fourier_events,
        settings,
        fourier=True,
        total_samples=ideal_samples,
    )
    ideal = _normalize(0.72 * ideal_comp + 0.72 * ideal_fourier, 0.92)

    gap = np.zeros((int(round(settings.ab_gap_seconds * settings.sample_rate)), 2))
    ab = np.concatenate((combined, gap, ideal), axis=0)
    decoded_computational = [decode_shot(shot) for shot in computational_shots]
    valid_count = sum(
        system == (0 if clock % 2 == 0 else 15)
        for clock, system in decoded_computational
    )

    def stats(intervals: np.ndarray) -> dict[str, float]:
        return {
            "mean_ms": float(np.mean(intervals)),
            "standard_deviation_ms": float(np.std(intervals)),
            "coefficient_of_variation": float(
                np.std(intervals) / np.mean(intervals)
            ),
            "minimum_ms": float(np.min(intervals)),
            "maximum_ms": float(np.max(intervals)),
        }

    report: dict[str, object] = {
        "protocol_kind": "qmw.ibm_history_clock64_direct_shot_sonification.v1",
        "scientific_status": (
            "one event per returned IBM sampler shot; sampler record order is "
            "preserved but is not interpreted as calibrated processor time; "
            "pitch, timbre, panning, and interval mappings are auditory transducers"
        ),
        "config": asdict(settings),
        "shots_per_circuit": len(computational_shots),
        "computational_historical_consistency": (
            valid_count / len(computational_shots)
        ),
        "computational_forbidden_shots": (
            len(computational_shots) - valid_count
        ),
        "ibm_duration_seconds": duration,
        "ideal_duration_seconds": ideal_duration,
        "computational_interval_statistics": stats(computational_intervals),
        "fourier_interval_statistics": stats(fourier_intervals),
        "mapping": {
            "interval": "circular distance between consecutive returned clock values",
            "computational_clean_click": "expected even/0000 or odd/1111 history",
            "computational_fractured_click": "forbidden clock-system history",
            "fourier_pitch": "clock bins k and k+32 share pitch class with octave displacement",
            "fourier_pan": "lower 32 bins left, upper 32 bins right",
            "ab_order": "IBM hardware first, silence, ideal 512-shot reference second",
        },
    }
    return IBMDataSonificationRender(
        ibm_computational=computational,
        ibm_clock_fourier=fourier,
        ibm_combined=combined,
        ideal_combined=ideal,
        ibm_then_ideal=ab,
        report=report,
    )


def write_ibm_data_sonification(
    render: IBMDataSonificationRender,
    output_directory: str | Path,
    *,
    sample_rate: int,
) -> dict[str, Path]:
    import soundfile as sf

    directory = Path(output_directory)
    directory.mkdir(parents=True, exist_ok=True)
    signals = {
        "ibm_computational_shots": render.ibm_computational,
        "ibm_clock_fourier_shots": render.ibm_clock_fourier,
        "ibm_combined": render.ibm_combined,
        "ideal_combined_reference": render.ideal_combined,
        "ibm_then_ideal_ab": render.ibm_then_ideal,
    }
    paths: dict[str, Path] = {}
    for name, signal in signals.items():
        path = directory / f"{name}.wav"
        sf.write(path, signal.astype(np.float32), int(sample_rate), subtype="FLOAT")
        paths[name] = path
    report_path = directory / "ibm_data_sonification_report.json"
    report_path.write_text(json.dumps(render.report, indent=2) + "\n")
    paths["report"] = report_path
    return paths
