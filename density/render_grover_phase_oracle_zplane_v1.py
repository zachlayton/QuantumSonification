#!/usr/bin/env python3
"""Render continuous Grover phase-oracle sweeps with complex Z-plane voices.

Eight population voices and 28 independent coherence voices represent the
upper triangle of a three-qubit density matrix. During each oracle gesture,
the complex coherence state is multiplied by the unit-magnitude rotator

    exp(-i * pi * s(t) * (marked_i - marked_j)),  s(t): 0 -> 1.

This preserves population and coherence magnitude while rotating phase. A
short diffusion strike follows each sweep, making the phase-to-amplitude step
audible as a distinct event.
"""

from __future__ import annotations

import argparse
import math
import wave
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from density.density_matrix_modal_renderer_v2 import write_wav
from density.grover_density_operator_v1 import diffusion_operator, oracle_operator
from density.render_grover_density_modal_v1 import GroverModalConfig, grover_modal_trajectory


@dataclass(frozen=True)
class ZPlanePhaseRenderConfig:
    output_path: Path = Path("output/grover_phase_oracle_zplane_v1.wav")
    sample_rate: int = 44_100
    duration_seconds: float = 12.0
    oracle_fraction: float = 0.62
    diffusion_fraction: float = 0.20
    modal_gain: float = 0.075
    output_ceiling: float = 0.78

    def __post_init__(self) -> None:
        if self.sample_rate < 8_000:
            raise ValueError("sample_rate must be at least 8000 Hz")
        if not math.isfinite(self.duration_seconds) or self.duration_seconds <= 0.0:
            raise ValueError("duration_seconds must be positive")
        if not 0.0 < self.oracle_fraction < 1.0:
            raise ValueError("oracle_fraction must lie in (0, 1)")
        if not 0.0 < self.diffusion_fraction < 1.0:
            raise ValueError("diffusion_fraction must lie in (0, 1)")
        if self.oracle_fraction + self.diffusion_fraction >= 1.0:
            raise ValueError("oracle and diffusion fractions must leave settling time")


def coherence_pairs(dimension: int) -> tuple[tuple[int, int], ...]:
    return tuple((row, column) for row in range(dimension) for column in range(row + 1, dimension))


def smooth_oracle_strength(n_samples: int) -> np.ndarray:
    """Raised-cosine interpolation from an un-applied to completed oracle."""
    if n_samples < 1:
        raise ValueError("n_samples must be positive")
    position = np.linspace(0.0, 1.0, n_samples)
    return 0.5 - 0.5 * np.cos(math.pi * position)


def oracle_sweep_density(
    rho: np.ndarray,
    n_qubits: int,
    marked_states: tuple[str, ...],
    strength: float,
) -> np.ndarray:
    """Return O(strength) rho O(strength)^dagger."""
    oracle = oracle_operator(n_qubits, marked_states, strength)
    return oracle @ rho @ oracle.conj().T


def zplane_voice_frequencies(dimension: int, sample_rate: int) -> tuple[np.ndarray, np.ndarray]:
    """Return separated population and coherence carrier frequencies."""
    population = np.geomspace(72.0, 260.0, dimension)
    coherence = np.geomspace(310.0, min(6200.0, sample_rate * 0.43), dimension * (dimension - 1) // 2)
    return population, coherence


def _static_pan(index: int, count: int, width: float = 0.82) -> float:
    if count <= 1:
        return 0.0
    return width * (2.0 * index / (count - 1) - 1.0)


def _add_density_strike(
    audio: np.ndarray,
    rho: np.ndarray,
    reference: np.ndarray,
    start: int,
    length: int,
    sample_rate: int,
    population_frequencies: np.ndarray,
    coherence_frequencies: np.ndarray,
    gain: float,
) -> None:
    """Strike voices according to diffusion-induced matrix displacement."""
    dimension = rho.shape[0]
    pairs = coherence_pairs(dimension)
    time = np.arange(length, dtype=np.float64) / sample_rate
    attack = np.minimum(1.0, time / 0.004)
    decay = attack * np.exp(-time / 0.34)
    delta = rho - reference

    for index in range(dimension):
        magnitude = abs(float(delta[index, index].real))
        if magnitude <= 1e-12:
            continue
        phase = 0.0 if delta[index, index].real >= 0.0 else math.pi
        signal = gain * magnitude**0.65 * decay * np.sin(
            2.0 * math.pi * population_frequencies[index] * time + phase
        )
        pan = _static_pan(index, dimension, 0.72)
        audio[start : start + length, 0] += math.sqrt(0.5 * (1.0 - pan)) * signal
        audio[start : start + length, 1] += math.sqrt(0.5 * (1.0 + pan)) * signal

    for index, (row, column) in enumerate(pairs):
        change = delta[row, column]
        magnitude = 2.0 * abs(change)
        if magnitude <= 1e-12:
            continue
        signal = gain * magnitude**0.65 * decay * np.sin(
            2.0 * math.pi * coherence_frequencies[index] * time + np.angle(change)
        )
        pan = _static_pan(index, len(pairs), 0.90)
        audio[start : start + length, 0] += math.sqrt(0.5 * (1.0 - pan)) * signal
        audio[start : start + length, 1] += math.sqrt(0.5 * (1.0 + pan)) * signal


def render_zplane_phase_audio(
    config: ZPlanePhaseRenderConfig,
) -> tuple[np.ndarray, dict[str, object]]:
    """Render oracle phase sweeps followed by diffusion conversion strikes."""
    trajectory_config = GroverModalConfig(
        sample_rate=config.sample_rate,
        duration_seconds=config.duration_seconds,
        oracle_strength=1.0,
    )
    trajectory = grover_modal_trajectory(trajectory_config)
    n_qubits = trajectory.n_qubits
    dimension = 1 << n_qubits
    marked = set(trajectory.marked_indices)
    pairs = coherence_pairs(dimension)
    population_frequencies, coherence_frequencies = zplane_voice_frequencies(
        dimension, config.sample_rate
    )
    total_samples = int(round(config.duration_seconds * config.sample_rate))
    audio = np.zeros((total_samples, 2), dtype=np.float64)
    intro_samples = int(round(0.16 * config.sample_rate))
    usable_samples = total_samples - intro_samples
    cycle_samples = usable_samples // trajectory_config.iterations
    phase_invariant_errors: list[float] = []
    population_invariant_errors: list[float] = []
    phase_sweeps: list[float] = []

    for cycle in range(trajectory_config.iterations):
        rho_before = trajectory.states[cycle]
        cycle_start = intro_samples + cycle * cycle_samples
        cycle_stop = (
            total_samples if cycle == trajectory_config.iterations - 1 else cycle_start + cycle_samples
        )
        this_cycle = cycle_stop - cycle_start
        oracle_samples = max(1, int(round(this_cycle * config.oracle_fraction)))
        diffusion_samples = max(1, int(round(this_cycle * config.diffusion_fraction)))
        strength = smooth_oracle_strength(oracle_samples)
        theta = math.pi * strength
        local_time = np.arange(oracle_samples, dtype=np.float64) / config.sample_rate
        fade = np.sin(math.pi * np.linspace(0.0, 1.0, oracle_samples)) ** 0.35

        # Population voices are a dry reference: a phase oracle cannot alter them.
        for index in range(dimension):
            amplitude = config.modal_gain * max(float(rho_before[index, index].real), 0.0) ** 0.65
            signal = amplitude * fade * np.sin(
                2.0 * math.pi * population_frequencies[index] * local_time
            )
            pan = _static_pan(index, dimension, 0.60)
            audio[cycle_start : cycle_start + oracle_samples, 0] += math.sqrt(
                0.5 * (1.0 - pan)
            ) * signal
            audio[cycle_start : cycle_start + oracle_samples, 1] += math.sqrt(
                0.5 * (1.0 + pan)
            ) * signal

        # Each upper-triangle coherence is a complex-pole voice. The oracle
        # rotator has unit magnitude, so only its phase and stereo trajectory move.
        for pair_index, (row, column) in enumerate(pairs):
            coherence = rho_before[row, column]
            magnitude = 2.0 * abs(coherence)
            if magnitude <= 1e-12:
                continue
            marked_difference = int(row in marked) - int(column in marked)
            quantum_phase = np.angle(coherence) - marked_difference * theta
            carrier_phase = 2.0 * math.pi * coherence_frequencies[pair_index] * local_time
            signal = (
                config.modal_gain
                * magnitude**0.65
                * fade
                * np.sin(carrier_phase + quantum_phase)
            )
            base_pan = _static_pan(pair_index, len(pairs), 0.68)
            rotating_pan = np.clip(
                base_pan + 0.25 * marked_difference * np.sin(theta), -0.92, 0.92
            )
            audio[cycle_start : cycle_start + oracle_samples, 0] += np.sqrt(
                0.5 * (1.0 - rotating_pan)
            ) * signal
            audio[cycle_start : cycle_start + oracle_samples, 1] += np.sqrt(
                0.5 * (1.0 + rotating_pan)
            ) * signal

        rho_oracle = oracle_sweep_density(
            rho_before, n_qubits, trajectory_config.marked_states, 1.0
        )
        diffusion = diffusion_operator(n_qubits)
        rho_diffusion = diffusion @ rho_oracle @ diffusion.conj().T
        population_invariant_errors.append(
            float(np.max(np.abs(np.diag(rho_oracle) - np.diag(rho_before))))
        )
        phase_invariant_errors.append(
            float(
                np.max(
                    np.abs(
                        np.sort(np.linalg.eigvalsh(rho_oracle))
                        - np.sort(np.linalg.eigvalsh(rho_before))
                    )
                )
            )
        )
        phase_sweeps.append(math.pi)

        diffusion_start = cycle_start + oracle_samples
        diffusion_length = min(diffusion_samples, total_samples - diffusion_start)
        if diffusion_length > 0:
            _add_density_strike(
                audio,
                rho_diffusion,
                rho_oracle,
                diffusion_start,
                diffusion_length,
                config.sample_rate,
                population_frequencies,
                coherence_frequencies,
                config.modal_gain * 2.5,
            )

        # A quieter post-environment strike closes the cycle and establishes
        # the density matrix from which the next oracle sweep begins.
        settle_start = diffusion_start + diffusion_length
        settle_length = min(cycle_stop - settle_start, total_samples - settle_start)
        if settle_length > 0:
            _add_density_strike(
                audio,
                trajectory.states[cycle + 1],
                rho_diffusion,
                settle_start,
                settle_length,
                config.sample_rate,
                population_frequencies,
                coherence_frequencies,
                config.modal_gain * 1.35,
            )

    audio -= np.mean(audio, axis=0, keepdims=True)
    fade_length = min(int(round(0.025 * config.sample_rate)), total_samples // 2)
    if fade_length:
        edge = np.linspace(0.0, 1.0, fade_length)
        audio[:fade_length] *= edge[:, None]
        audio[-fade_length:] *= edge[::-1, None]
    peak = float(np.max(np.abs(audio)))
    if peak > 1e-12:
        audio *= config.output_ceiling / peak
    diagnostics: dict[str, object] = {
        "population_voices": dimension,
        "coherence_voices": len(pairs),
        "oracle_sweeps": len(phase_sweeps),
        "oracle_angle_degrees": 180.0,
        "maximum_population_error": max(population_invariant_errors, default=0.0),
        "maximum_spectrum_error": max(phase_invariant_errors, default=0.0),
    }
    return np.clip(audio, -1.0, 1.0), diagnostics


def render_to_wav(config: ZPlanePhaseRenderConfig) -> dict[str, object]:
    audio, diagnostics = render_zplane_phase_audio(config)
    write_wav(config.output_path, audio, config.sample_rate)
    return diagnostics


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ZPlanePhaseRenderConfig.output_path)
    parser.add_argument("--duration", type=float, default=ZPlanePhaseRenderConfig.duration_seconds)
    parser.add_argument("--sample-rate", type=int, default=ZPlanePhaseRenderConfig.sample_rate)
    args = parser.parse_args()
    config = ZPlanePhaseRenderConfig(
        output_path=args.output,
        duration_seconds=args.duration,
        sample_rate=args.sample_rate,
    )
    diagnostics = render_to_wav(config)
    with wave.open(str(config.output_path), "rb") as wav_file:
        duration = wav_file.getnframes() / wav_file.getframerate()
    print("Grover Z-plane phase-oracle render complete")
    print(f"  output: {config.output_path.resolve()}")
    print(f"  format: stereo, {config.sample_rate} Hz, 16-bit PCM, {duration:.3f} seconds")
    for key, value in diagnostics.items():
        print(f"  {key}: {value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
