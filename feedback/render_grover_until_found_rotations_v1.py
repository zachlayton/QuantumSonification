#!/usr/bin/env python3
"""Render a thresholded Grover search as an explicit spatial rotation."""

from __future__ import annotations

import argparse
import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np

from density.density_matrix_modal_renderer_v2 import write_wav
from feedback.render_memory_oracle_tanglecube_v1 import (
    DEFAULT_TANGLE_PACKET,
    axis_angle_rotation,
    geometry_reverb_frequency_ratios,
    load_tanglecube_modal_field,
    orientation_sonification_controls,
    render_time_varying_modal_reverb,
    spatial_modal_coupling,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class UntilFoundResult:
    target: int
    target_bits: str
    n_qubits: int
    search_space_size: int
    theta: float
    grover_step_angle: float
    threshold: float
    found_iteration: int
    optimal_iteration: int
    probabilities: np.ndarray
    state_angles: np.ndarray


@dataclass(frozen=True)
class UntilFoundRenderConfig:
    output_path: Path = PROJECT_ROOT / "output/grover_until_found_57893_rotations_v1.wav"
    diagnostics_path: Path = PROJECT_ROOT / "output/grover_until_found_57893_rotations_v1.json"
    tangle_packet: Path = DEFAULT_TANGLE_PACKET
    target: int = 57_893
    confidence_threshold: float = 0.9999
    sample_rate: int = 48_000
    duration_seconds: float = 18.0
    root_frequency_hz: float = 48.0
    dry_gain: float = 0.36
    wet_gain: float = 0.70
    surface_depth: float = 0.70
    ring_mod_depth: float = 0.80
    ring_mod_max_hz: float = 42.0
    pan_depth: float = 0.94
    output_ceiling: float = 0.82

    def __post_init__(self) -> None:
        if isinstance(self.target, bool) or not isinstance(self.target, int) or self.target < 0:
            raise ValueError("target must be a non-negative integer")
        if not 0.0 < self.confidence_threshold < 1.0:
            raise ValueError("confidence_threshold must lie in (0, 1)")
        if self.sample_rate < 8_000 or self.duration_seconds <= 0.0:
            raise ValueError("invalid sample rate or duration")


def run_until_found(target: int, confidence_threshold: float = 0.9999) -> UntilFoundResult:
    """Return the exact one-target Grover schedule up to first threshold crossing.

    This is a simulator stopping rule. A hardware run schedules the first
    maximum and measures once; measuring after every iteration would collapse
    the evolving state.
    """
    if isinstance(target, bool) or not isinstance(target, int) or target < 0:
        raise ValueError("target must be a non-negative integer")
    if not 0.0 < confidence_threshold < 1.0:
        raise ValueError("confidence_threshold must lie in (0, 1)")
    n_qubits = max(1, target.bit_length())
    dimension = 1 << n_qubits
    theta = math.asin(1.0 / math.sqrt(dimension))
    optimal = int(math.floor(math.pi / (4.0 * theta)))
    all_angles = (2.0 * np.arange(optimal + 1) + 1.0) * theta
    all_probabilities = np.sin(all_angles) ** 2
    crossings = np.flatnonzero(all_probabilities >= confidence_threshold)
    found = int(crossings[0]) if len(crossings) else optimal
    return UntilFoundResult(
        target=target,
        target_bits=format(target, f"0{n_qubits}b"),
        n_qubits=n_qubits,
        search_space_size=dimension,
        theta=theta,
        grover_step_angle=2.0 * theta,
        threshold=confidence_threshold,
        found_iteration=found,
        optimal_iteration=optimal,
        probabilities=all_probabilities[: found + 1],
        state_angles=all_angles[: found + 1],
    )


def smooth_iteration_pulses(
    time: np.ndarray, first_event_time: float, event_spacing: float
) -> np.ndarray:
    """Continuous iteration pulses with matching value and slope at wraps."""
    if event_spacing <= 0.0:
        raise ValueError("event_spacing must be positive")
    phase = np.mod(np.asarray(time, dtype=np.float64) - first_event_time, event_spacing)
    phase /= event_spacing
    # Peak at each iteration boundary. Raising the Hann-like cycle narrows the
    # pulse while preserving zero slope and identical endpoints at the wrap.
    return np.power(0.5 + 0.5 * np.cos(2.0 * math.pi * phase), 5.0)


def _target_bit_source(
    result: UntilFoundResult,
    sample_rate: int,
    duration_seconds: float,
    root_frequency_hz: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    total_samples = int(round(sample_rate * duration_seconds))
    time = np.arange(total_samples, dtype=np.float64) / sample_rate
    event_times = np.linspace(0.18, duration_seconds * 0.82, len(result.probabilities))
    probabilities = np.interp(time, event_times, result.probabilities)
    angles = np.interp(time, event_times, result.state_angles)
    event_spacing = event_times[1] - event_times[0] if len(event_times) > 1 else duration_seconds
    pulses = smooth_iteration_pulses(time, float(event_times[0]), float(event_spacing))
    amplitude_envelope = (0.10 + 0.90 * np.sqrt(probabilities)) * (0.30 + 0.70 * pulses)

    source = np.zeros(total_samples, dtype=np.float64)
    bits = np.asarray([int(bit) for bit in result.target_bits], dtype=np.float64)
    bit_weights = 0.28 + 0.72 * bits
    bit_weights /= math.sqrt(float(np.sum(bit_weights * bit_weights)))
    for index, (bit, weight) in enumerate(zip(bits, bit_weights)):
        frequency = root_frequency_hz * (index + 1)
        phase = 0.0 if bit > 0.5 else math.pi
        source += weight * np.sin(2.0 * math.pi * frequency * time + phase)
    source *= amplitude_envelope

    # The Grover plane travels from the unmarked pole to the marked pole.
    # Doubling alpha makes that quarter-turn an unmistakable stereo half-orbit.
    pan = np.clip(-np.cos(2.0 * angles), -0.98, 0.98)
    stereo = np.column_stack(
        (source * np.sqrt(0.5 * (1.0 - pan)), source * np.sqrt(0.5 * (1.0 + pan)))
    )
    return stereo, probabilities, angles


def render_until_found_audio(
    config: UntilFoundRenderConfig,
) -> tuple[np.ndarray, dict[str, object]]:
    result = run_until_found(config.target, config.confidence_threshold)
    field = load_tanglecube_modal_field(config.tangle_packet)
    dry, sample_probabilities, sample_angles = _target_bit_source(
        result, config.sample_rate, config.duration_seconds, config.root_frequency_hz
    )
    total_samples = len(dry)
    control_count = len(result.probabilities)
    control_times = np.linspace(0.0, config.duration_seconds, control_count)
    rotation_angles = 2.0 * (result.state_angles - result.theta)
    orientations = np.asarray(
        [axis_angle_rotation(np.array([0.0, 0.0, 1.0]), angle) for angle in rotation_angles]
    )
    couplings = np.empty((control_count, len(field.frequencies_hz), 2), dtype=np.float64)
    pans = np.empty(control_count, dtype=np.float64)
    centers = np.empty(control_count, dtype=np.float64)
    for index, (orientation, rotation, probability) in enumerate(
        zip(orientations, rotation_angles, result.probabilities)
    ):
        coupling, _ = spatial_modal_coupling(
            field,
            orientation,
            np.array([0.82, 0.31, 0.48]),
            np.array([-0.38, 0.86, 0.34]),
            math.radians(13.0),
        )
        pan, center, aperture = orientation_sonification_controls(
            orientation,
            len(field.frequencies_hz),
            config.pan_depth,
            0.88,
            sonic_angle=float(rotation),
            amplification=float(probability),
        )
        coupling[:, 0] *= math.sqrt(1.0 - pan) * aperture
        coupling[:, 1] *= math.sqrt(1.0 + pan) * aperture
        couplings[index] = coupling
        pans[index] = pan
        centers[index] = center

    frequency_ratios = geometry_reverb_frequency_ratios(
        orientations,
        rotation_angles,
        len(field.frequencies_hz),
        surface_depth=config.surface_depth,
        modal_warp_depth=0.65,
    )
    mono = np.mean(dry, axis=1)
    wet = config.wet_gain * render_time_varying_modal_reverb(
        mono,
        field.frequencies_hz,
        field.decay_times_seconds,
        frequency_ratios,
        couplings,
        config.sample_rate,
        ring_mod_depth=config.ring_mod_depth,
        ring_mod_max_hz=config.ring_mod_max_hz,
    )
    audio = config.dry_gain * dry + wet

    # Arrival strike: the target's sixteen-bit spectrum rings at threshold.
    found_time = config.duration_seconds * 0.82
    start = min(total_samples - 1, int(round(found_time * config.sample_rate)))
    tail_time = np.arange(total_samples - start, dtype=np.float64) / config.sample_rate
    arrival = np.zeros_like(tail_time)
    for index, bit in enumerate(result.target_bits):
        arrival += (1.0 if bit == "1" else 0.30) * np.sin(
            2.0 * math.pi * config.root_frequency_hz * (index + 1) * tail_time
        )
    arrival *= 0.018 * np.exp(-tail_time / 1.4)
    audio[start:, :] += arrival[:, None] * math.sqrt(0.5)

    audio -= np.mean(audio, axis=0, keepdims=True)
    fade = min(total_samples // 2, int(round(0.035 * config.sample_rate)))
    if fade > 1:
        ramp = np.linspace(0.0, 1.0, fade)
        audio[:fade] *= ramp[:, None]
        audio[-fade:] *= ramp[::-1, None]
    peak = float(np.max(np.abs(audio)))
    if peak > 1e-12:
        audio *= config.output_ceiling / peak

    diagnostics: dict[str, object] = {
        "engine": "grover_until_found_rotations_v1",
        "target": result.target,
        "target_bits": result.target_bits,
        "n_qubits": result.n_qubits,
        "search_space_size": result.search_space_size,
        "confidence_threshold": result.threshold,
        "found_iteration": result.found_iteration,
        "optimal_iteration": result.optimal_iteration,
        "theta_degrees": math.degrees(result.theta),
        "rotation_per_iteration_degrees": math.degrees(result.grover_step_angle),
        "final_state_angle_degrees": math.degrees(float(result.state_angles[-1])),
        "initial_probability": float(result.probabilities[0]),
        "final_probability": float(result.probabilities[-1]),
        "probabilities": result.probabilities.tolist(),
        "pan_range": [float(np.min(pans)), float(np.max(pans))],
        "mode_center_range": [float(np.min(centers)), float(np.max(centers))],
        "frequency_ratio_range": [float(np.min(frequency_ratios)), float(np.max(frequency_ratios))],
        "wet_rms": float(np.sqrt(np.mean(wet * wet))),
        "dry_rms": float(np.sqrt(np.mean(np.square(config.dry_gain * dry)))),
        "sample_probability_final": float(sample_probabilities[-1]),
        "sample_angle_final_degrees": math.degrees(float(sample_angles[-1])),
        "iteration_pulse_shape": "periodic_raised_cosine_power_5",
    }
    return np.clip(audio, -1.0, 1.0), diagnostics


def render_to_wav(config: UntilFoundRenderConfig) -> dict[str, object]:
    audio, diagnostics = render_until_found_audio(config)
    write_wav(config.output_path, audio, config.sample_rate)
    config.diagnostics_path.parent.mkdir(parents=True, exist_ok=True)
    serializable = {
        **asdict(config),
        "output_path": str(config.output_path),
        "diagnostics_path": str(config.diagnostics_path),
        "tangle_packet": str(config.tangle_packet),
    }
    config.diagnostics_path.write_text(
        json.dumps({"config": serializable, "diagnostics": diagnostics}, indent=2),
        encoding="utf-8",
    )
    return diagnostics


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", type=int, default=UntilFoundRenderConfig.target)
    parser.add_argument("--threshold", type=float, default=UntilFoundRenderConfig.confidence_threshold)
    parser.add_argument("--output", type=Path, default=UntilFoundRenderConfig.output_path)
    parser.add_argument("--duration", type=float, default=UntilFoundRenderConfig.duration_seconds)
    args = parser.parse_args()
    config = UntilFoundRenderConfig(
        target=args.target,
        confidence_threshold=args.threshold,
        output_path=args.output,
        diagnostics_path=args.output.with_suffix(".json"),
        duration_seconds=args.duration,
    )
    diagnostics = render_to_wav(config)
    print("Grover until-found rotation render complete")
    print(f"  target: {diagnostics['target']} = {diagnostics['target_bits']}")
    print(f"  search space: {diagnostics['search_space_size']} states")
    print(f"  found: iteration {diagnostics['found_iteration']} at p={diagnostics['final_probability']:.9f}")
    print(f"  rotation: {diagnostics['rotation_per_iteration_degrees']:.6f} degrees/step")
    print(f"  output: {config.output_path.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
