#!/usr/bin/env python3
"""Render a Phase-2 density-Grover trajectory through a stereo modal bank."""

from __future__ import annotations

import argparse
import math
import wave
from dataclasses import dataclass, replace
from pathlib import Path

import numpy as np

from density.density_matrix_modal_renderer_v2 import (
    RenderConfig as ModalConfig,
    modal_parameters_from_density,
    write_wav,
)
from density.grover_density_operator_v1 import (
    DecoherenceConfig,
    GroverDensityResult,
    run_density_grover,
)


@dataclass(frozen=True)
class GroverModalConfig:
    output_path: Path = Path("output/grover_density_modal_v1.wav")
    sample_rate: int = 44_100
    duration_seconds: float = 12.0
    n_qubits: int = 3
    marked_states: tuple[str, ...] = ("010", "101")
    iterations: int = 6
    oracle_strength: float = 0.82
    time_step: float = 1.0 / 30.0
    dephasing_rate: float = 0.12
    amplitude_damping_rate: float = 0.025
    depolarizing_rate: float = 0.018
    base_frequency_hz: float = 72.0
    modal_gain: float = 0.10
    minimum_brightness: float = 0.18
    maximum_brightness: float = 0.96
    output_ceiling: float = 0.78
    seed: int = 29

    def __post_init__(self) -> None:
        if self.sample_rate < 8_000:
            raise ValueError("sample_rate must be at least 8000 Hz")
        if not math.isfinite(self.duration_seconds) or self.duration_seconds <= 0.0:
            raise ValueError("duration_seconds must be positive")
        if self.iterations < 1:
            raise ValueError("iterations must be at least 1")
        if not 0.0 < self.output_ceiling <= 1.0:
            raise ValueError("output_ceiling must be in (0, 1]")
        if not 0.0 <= self.minimum_brightness <= self.maximum_brightness <= 1.0:
            raise ValueError("brightness bounds must satisfy 0 <= minimum <= maximum <= 1")


def brightness_from_coherence(
    coherence_l1: float, n_qubits: int, minimum: float, maximum: float
) -> float:
    """Map l1 coherence to modal harmonic brightness in ``[minimum, maximum]``."""
    maximum_coherence = float((1 << n_qubits) - 1)
    normalized = float(np.clip(coherence_l1 / maximum_coherence, 0.0, 1.0))
    return minimum + (maximum - minimum) * normalized


def pin_modal_root(
    frequencies: np.ndarray, intended_root_hz: float, sample_rate: int
) -> np.ndarray:
    """Pin mode one to the intended root while retaining all modal intervals."""
    values = np.asarray(frequencies, dtype=np.float64)
    if values.ndim != 1 or values.size == 0 or values[0] <= 0.0:
        raise ValueError("frequencies must be a non-empty positive vector")
    if not math.isfinite(intended_root_hz) or intended_root_hz <= 0.0:
        raise ValueError("intended_root_hz must be positive and finite")
    scaled = values * (intended_root_hz / values[0])
    scaled[0] = intended_root_hz
    return np.clip(scaled, 20.0, sample_rate * 0.45)


def _qiskit_local_operator(
    operator: np.ndarray, qubit: int, n_qubits: int
) -> np.ndarray:
    identity = np.eye(2, dtype=np.complex128)
    output = np.array([[1.0 + 0.0j]])
    for tensor_qubit in reversed(range(n_qubits)):
        output = np.kron(output, operator if tensor_qubit == qubit else identity)
    return output


def grover_modal_trajectory(config: GroverModalConfig) -> GroverDensityResult:
    """Create the deterministic open-system trajectory used by the render."""
    pauli_x = np.array([[0.0, 1.0], [1.0, 0.0]], dtype=np.complex128)
    pauli_z = np.array([[1.0, 0.0], [0.0, -1.0]], dtype=np.complex128)
    x_q0 = _qiskit_local_operator(pauli_x, 0, config.n_qubits)
    z_high = _qiskit_local_operator(pauli_z, config.n_qubits - 1, config.n_qubits)
    marked = tuple(int(label, 2) for label in config.marked_states)

    def hamiltonian(iteration: int, rho: np.ndarray) -> np.ndarray:
        populations = np.real(np.diag(rho))
        marked_population = float(np.sum(populations[list(marked)]))
        return (
            (0.13 + 0.025 * math.sin(iteration * 0.7)) * x_q0
            + (0.07 + 0.045 * marked_population) * z_high
        )

    return run_density_grover(
        config.n_qubits,
        config.marked_states,
        config.iterations,
        oracle_strength=config.oracle_strength,
        decoherence=DecoherenceConfig(
            dephasing_rate=config.dephasing_rate,
            amplitude_damping_rate=config.amplitude_damping_rate,
            depolarizing_rate=config.depolarizing_rate,
        ),
        hamiltonian=hamiltonian,
        time_step=config.time_step,
    )


def render_grover_modal_audio(
    config: GroverModalConfig,
) -> tuple[np.ndarray, GroverDensityResult]:
    """Strike a modal resonator bank once for every Grover density state."""
    result = grover_modal_trajectory(config)
    sample_rate = config.sample_rate
    total_samples = int(round(config.duration_seconds * sample_rate))
    audio = np.zeros((total_samples, 2), dtype=np.float64)
    rng = np.random.default_rng(config.seed)
    event_times = np.linspace(0.18, config.duration_seconds * 0.82, len(result.states))
    previous_probability = result.metrics[0].marked_probability

    modal_base = ModalConfig(
        sample_rate=sample_rate,
        duration_seconds=config.duration_seconds,
        n_qubits=config.n_qubits,
        base_frequency_hz=config.base_frequency_hz,
        frequency_spread=4.2,
        min_decay_seconds=0.12,
        max_decay_seconds=3.4,
        modal_gain=config.modal_gain,
        brightness=0.72,
        stereo_width=0.90,
        normalize_output=False,
    )

    for event_index, (event_time, rho, metrics) in enumerate(
        zip(event_times, result.states, result.metrics)
    ):
        probability_delta = abs(metrics.marked_probability - previous_probability)
        pitch_lift = 0.82 + 0.42 * metrics.marked_probability
        brightness = brightness_from_coherence(
            metrics.coherence_l1,
            config.n_qubits,
            config.minimum_brightness,
            config.maximum_brightness,
        )
        event_modal_config = replace(
            modal_base,
            base_frequency_hz=config.base_frequency_hz * pitch_lift,
            brightness=brightness,
        )
        frequencies, amplitudes, decays, phases, pans = modal_parameters_from_density(
            rho, event_modal_config
        )
        frequencies = pin_modal_root(frequencies, event_modal_config.base_frequency_hz, sample_rate)

        # Amplification gives the resonator a stronger strike; large changes
        # add transient emphasis so Grover's return/overshoot cycle is audible.
        excitation = (
            0.22
            + 0.78 * math.sqrt(max(metrics.marked_probability, 0.0))
            + 0.48 * probability_delta
        )
        excitation *= 0.72 + 0.28 * metrics.purity
        start = min(total_samples - 1, int(round(event_time * sample_rate)))

        for mode, (frequency, amplitude, decay, phase, pan) in enumerate(
            zip(frequencies, amplitudes, decays, phases, pans)
        ):
            # Retain enough of every decay to overlap successive Grover states.
            length = min(total_samples - start, max(1, int(round(5.5 * decay * sample_rate))))
            local_time = np.arange(length, dtype=np.float64) / sample_rate
            attack = np.minimum(1.0, local_time / 0.006)
            envelope = attack * np.exp(-local_time / decay)
            phase_jitter = rng.uniform(-0.035, 0.035) if mode else 0.0
            oscillator = np.sin(
                2.0 * math.pi * frequency * local_time + phase + phase_jitter
            )
            signal = excitation * amplitude * envelope * oscillator
            left = math.sqrt(0.5 * (1.0 - pan))
            right = math.sqrt(0.5 * (1.0 + pan))
            audio[start : start + length, 0] += left * signal
            audio[start : start + length, 1] += right * signal

        previous_probability = metrics.marked_probability

    audio -= np.mean(audio, axis=0, keepdims=True)
    fade_length = min(int(round(0.025 * sample_rate)), total_samples // 2)
    if fade_length:
        fade = np.linspace(0.0, 1.0, fade_length)
        audio[:fade_length] *= fade[:, None]
        audio[-fade_length:] *= fade[::-1, None]
    peak = float(np.max(np.abs(audio)))
    if peak > 1e-12:
        audio *= config.output_ceiling / peak
    return np.clip(audio, -1.0, 1.0), result


def render_to_wav(config: GroverModalConfig) -> GroverDensityResult:
    audio, result = render_grover_modal_audio(config)
    write_wav(config.output_path, audio, config.sample_rate)
    return result


def _wav_diagnostics(path: Path) -> tuple[int, int, int, float]:
    with wave.open(str(path), "rb") as wav_file:
        frames = wav_file.getnframes()
        return (
            wav_file.getnchannels(),
            wav_file.getframerate(),
            frames,
            frames / wav_file.getframerate(),
        )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=GroverModalConfig.output_path)
    parser.add_argument("--duration", type=float, default=GroverModalConfig.duration_seconds)
    parser.add_argument("--sample-rate", type=int, default=GroverModalConfig.sample_rate)
    args = parser.parse_args()
    config = GroverModalConfig(
        output_path=args.output,
        duration_seconds=args.duration,
        sample_rate=args.sample_rate,
    )
    result = render_to_wav(config)
    channels, sample_rate, frames, duration = _wav_diagnostics(config.output_path)
    print("Grover density modal render complete")
    print(f"  output: {config.output_path.resolve()}")
    print(f"  format: {channels} channels, {sample_rate} Hz, 16-bit PCM")
    print(f"  frames: {frames}; duration: {duration:.3f} seconds")
    print(
        "  marked probability: "
        + " -> ".join(f"{item.marked_probability:.3f}" for item in result.metrics)
    )
    print(
        f"  purity: {result.metrics[0].purity:.3f} -> "
        f"{result.final_metrics.purity:.3f}"
    )
    print(
        "  brightness: "
        + " -> ".join(
            f"{brightness_from_coherence(item.coherence_l1, config.n_qubits, config.minimum_brightness, config.maximum_brightness):.3f}"
            for item in result.metrics
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
