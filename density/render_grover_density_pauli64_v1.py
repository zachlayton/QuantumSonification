#!/usr/bin/env python3
"""Render all 64 three-qubit Pauli coefficients as a stereo resonator bank."""

from __future__ import annotations

import argparse
import itertools
import math
import wave
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping, Sequence

import numpy as np

from density.density_matrix_modal_renderer_v2 import write_wav
from density.render_grover_density_modal_v1 import (
    GroverModalConfig,
    grover_modal_trajectory,
)


PAULI = {
    "I": np.eye(2, dtype=np.complex128),
    "X": np.array([[0.0, 1.0], [1.0, 0.0]], dtype=np.complex128),
    "Y": np.array([[0.0, -1j], [1j, 0.0]], dtype=np.complex128),
    "Z": np.array([[1.0, 0.0], [0.0, -1.0]], dtype=np.complex128),
}


@dataclass(frozen=True)
class Pauli64RenderConfig:
    output_path: Path = Path("output/grover_density_pauli64_v1.wav")
    sample_rate: int = 44_100
    duration_seconds: float = 12.0
    modal_gain: float = 0.038
    identity_gain: float = 0.16
    output_ceiling: float = 0.78
    coefficient_curve: float = 0.72

    def __post_init__(self) -> None:
        if self.sample_rate < 8_000:
            raise ValueError("sample_rate must be at least 8000 Hz")
        if not math.isfinite(self.duration_seconds) or self.duration_seconds <= 0.0:
            raise ValueError("duration_seconds must be positive")
        if self.modal_gain <= 0.0:
            raise ValueError("modal_gain must be positive")
        if not 0.0 < self.identity_gain <= 1.0:
            raise ValueError("identity_gain must be in (0, 1]")
        if not 0.0 < self.output_ceiling <= 1.0:
            raise ValueError("output_ceiling must be in (0, 1]")
        if not 0.0 < self.coefficient_curve <= 1.0:
            raise ValueError("coefficient_curve must be in (0, 1]")


def pauli_labels(n_qubits: int) -> tuple[str, ...]:
    """Return all 4**n Pauli strings in stable lexicographic order."""
    if n_qubits < 1:
        raise ValueError("n_qubits must be positive")
    return tuple("".join(symbols) for symbols in itertools.product("IXYZ", repeat=n_qubits))


def pauli_weight(label: str) -> int:
    return sum(symbol != "I" for symbol in label)


def pauli_operator(label: str) -> np.ndarray:
    """Build a Pauli string with labels ordered q[n-1] ... q[0]."""
    if not label or any(symbol not in PAULI for symbol in label):
        raise ValueError("Pauli labels must be non-empty strings over I, X, Y, Z")
    operator = np.array([[1.0 + 0.0j]])
    for symbol in label:
        operator = np.kron(operator, PAULI[symbol])
    return operator


def pauli_coefficients(
    rho: np.ndarray, labels: Sequence[str] | None = None
) -> dict[str, float]:
    """Return exact real coefficients r_P = Tr(rho P)."""
    state = np.asarray(rho, dtype=np.complex128)
    if state.ndim != 2 or state.shape[0] != state.shape[1]:
        raise ValueError("rho must be square")
    n_qubits = int(round(math.log2(state.shape[0])))
    if 1 << n_qubits != state.shape[0]:
        raise ValueError("rho dimension must be a power of two")
    selected = tuple(labels) if labels is not None else pauli_labels(n_qubits)
    coefficients: dict[str, float] = {}
    for label in selected:
        if len(label) != n_qubits:
            raise ValueError("Pauli label length does not match rho")
        value = np.trace(state @ pauli_operator(label))
        if abs(value.imag) > 1e-9:
            raise ValueError(f"Pauli coefficient {label} is unexpectedly complex")
        coefficients[label] = float(value.real)
    return coefficients


def reconstruct_density_from_pauli(
    coefficients: Mapping[str, float], n_qubits: int
) -> np.ndarray:
    """Reconstruct rho = 2**(-n) sum_P r_P P."""
    dimension = 1 << n_qubits
    state = np.zeros((dimension, dimension), dtype=np.complex128)
    expected = set(pauli_labels(n_qubits))
    if set(coefficients) != expected:
        raise ValueError("a complete Pauli coefficient mapping is required")
    for label, value in coefficients.items():
        state += float(value) * pauli_operator(label)
    return state / dimension


def pauli_mode_frequencies(
    labels: Sequence[str], sample_rate: int
) -> dict[str, float]:
    """Place Pauli weights 0-3 in separated logarithmic spectral families."""
    nyquist_limit = sample_rate * 0.43
    bands = {
        0: (46.0, 46.0),
        1: (92.0, min(246.0, nyquist_limit)),
        2: (280.0, min(980.0, nyquist_limit)),
        3: (1100.0, min(6200.0, nyquist_limit)),
    }
    output: dict[str, float] = {}
    for weight in range(max(map(pauli_weight, labels)) + 1):
        family = [label for label in labels if pauli_weight(label) == weight]
        low, high = bands.get(weight, (1100.0, nyquist_limit))
        if high < low:
            low = max(20.0, high * 0.6)
        frequencies = (
            np.array([low])
            if len(family) == 1
            else np.geomspace(low, high, len(family))
        )
        output.update(zip(family, map(float, frequencies)))
    return output


def pauli_pan(label: str) -> float:
    """Map X left, Y center, and Z right, with qubit position as a perturbation."""
    active = [(index, symbol) for index, symbol in enumerate(label) if symbol != "I"]
    if not active:
        return 0.0
    axis = {"X": -0.82, "Y": 0.0, "Z": 0.82}
    axis_position = float(np.mean([axis[symbol] for _, symbol in active]))
    if len(label) > 1:
        qubit_position = float(
            np.mean([2.0 * index / (len(label) - 1) - 1.0 for index, _ in active])
        )
    else:
        qubit_position = 0.0
    return float(np.clip(0.82 * axis_position + 0.18 * qubit_position, -0.92, 0.92))


def pauli_decay_seconds(label: str, purity: float, magnitude: float) -> float:
    """Give higher-order correlations shorter, more articulated resonances."""
    base = {0: 3.4, 1: 2.7, 2: 1.85, 3: 1.15}.get(pauli_weight(label), 0.9)
    return base * (0.72 + 0.28 * purity) * (0.78 + 0.22 * math.sqrt(magnitude))


def render_pauli64_audio(
    config: Pauli64RenderConfig,
) -> tuple[np.ndarray, tuple[dict[str, float], ...]]:
    """Render exact Pauli coefficient snapshots as 64 struck resonators."""
    trajectory_config = GroverModalConfig(
        sample_rate=config.sample_rate,
        duration_seconds=config.duration_seconds,
    )
    result = grover_modal_trajectory(trajectory_config)
    labels = pauli_labels(trajectory_config.n_qubits)
    frequencies = pauli_mode_frequencies(labels, config.sample_rate)
    coefficients = tuple(pauli_coefficients(rho, labels) for rho in result.states)
    total_samples = int(round(config.duration_seconds * config.sample_rate))
    audio = np.zeros((total_samples, 2), dtype=np.float64)
    event_times = np.linspace(0.18, config.duration_seconds * 0.82, len(result.states))
    previous = {label: 0.0 for label in labels}

    for event_time, current, metrics in zip(event_times, coefficients, result.metrics):
        start = min(total_samples - 1, int(round(event_time * config.sample_rate)))
        for label in labels:
            value = current[label]
            magnitude = abs(value)
            change = abs(value - previous[label])
            # The absolute coefficient keeps the current operator present;
            # coefficient motion gives changing correlations a sharper strike.
            drive = 0.18 * magnitude + 0.82 * change
            if drive <= 1e-12:
                continue
            amplitude = config.modal_gain * drive ** config.coefficient_curve
            if label == "I" * trajectory_config.n_qubits:
                amplitude *= config.identity_gain
            phase = 0.0 if value >= 0.0 else math.pi
            decay = pauli_decay_seconds(label, metrics.purity, magnitude)
            length = min(
                total_samples - start,
                max(1, int(round(5.5 * decay * config.sample_rate))),
            )
            time = np.arange(length, dtype=np.float64) / config.sample_rate
            attack = np.minimum(1.0, time / 0.005)
            envelope = attack * np.exp(-time / decay)
            signal = amplitude * envelope * np.sin(
                2.0 * math.pi * frequencies[label] * time + phase
            )
            pan = pauli_pan(label)
            left = math.sqrt(0.5 * (1.0 - pan))
            right = math.sqrt(0.5 * (1.0 + pan))
            audio[start : start + length, 0] += left * signal
            audio[start : start + length, 1] += right * signal
        previous = current

    audio -= np.mean(audio, axis=0, keepdims=True)
    fade_length = min(int(round(0.025 * config.sample_rate)), total_samples // 2)
    if fade_length:
        fade = np.linspace(0.0, 1.0, fade_length)
        audio[:fade_length] *= fade[:, None]
        audio[-fade_length:] *= fade[::-1, None]
    peak = float(np.max(np.abs(audio)))
    if peak > 1e-12:
        audio *= config.output_ceiling / peak
    return np.clip(audio, -1.0, 1.0), coefficients


def render_to_wav(config: Pauli64RenderConfig) -> tuple[dict[str, float], ...]:
    audio, coefficients = render_pauli64_audio(config)
    write_wav(config.output_path, audio, config.sample_rate)
    return coefficients


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Pauli64RenderConfig.output_path)
    parser.add_argument("--duration", type=float, default=Pauli64RenderConfig.duration_seconds)
    parser.add_argument("--sample-rate", type=int, default=Pauli64RenderConfig.sample_rate)
    args = parser.parse_args()
    config = Pauli64RenderConfig(
        output_path=args.output,
        duration_seconds=args.duration,
        sample_rate=args.sample_rate,
    )
    coefficient_history = render_to_wav(config)
    labels = pauli_labels(3)
    maximum_reconstruction_error = 0.0
    trajectory = grover_modal_trajectory(
        GroverModalConfig(sample_rate=config.sample_rate, duration_seconds=config.duration_seconds)
    )
    for rho, coefficients in zip(trajectory.states, coefficient_history):
        reconstructed = reconstruct_density_from_pauli(coefficients, 3)
        maximum_reconstruction_error = max(
            maximum_reconstruction_error,
            float(np.max(np.abs(rho - reconstructed))),
        )
    with wave.open(str(config.output_path), "rb") as wav_file:
        frames = wav_file.getnframes()
        duration = frames / wav_file.getframerate()
    active_counts = [sum(abs(values[label]) > 1e-6 for label in labels) for values in coefficient_history]
    print("Grover density Pauli-64 render complete")
    print(f"  output: {config.output_path.resolve()}")
    print(f"  format: stereo, {config.sample_rate} Hz, 16-bit PCM, {duration:.3f} seconds")
    print(f"  resonators: {len(labels)}")
    print("  active coefficients: " + " -> ".join(map(str, active_counts)))
    print(f"  maximum rho reconstruction error: {maximum_reconstruction_error:.3e}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
