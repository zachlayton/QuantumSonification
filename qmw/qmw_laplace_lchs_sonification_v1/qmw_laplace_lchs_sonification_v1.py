#!/usr/bin/env python3
"""Auditable sonification of an arithmetic-progression quantum Laplace query.

This is an offline, dependency-light study inspired by arXiv:2512.17980.  It
does *not* claim to simulate its complete quantum algorithm.  Instead it keeps
two independently audible and inspectable layers:

* response: direct numerical samples G(s) of a chosen Laplace transform;
* select: the binary bit-pair structure that factorizes the paper's SELECT
  operator when the evaluation points s form an arithmetic progression.

The `.npz` response is the canonical scientific output.  The WAV is a
perceptual rendering of that data, and `descriptor.json` records every mapping.
"""

from __future__ import annotations

import argparse
import json
import math
import wave
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np


@dataclass(frozen=True)
class Config:
    output_dir: Path = Path("outputs/qmw_laplace_lchs_sonification_v1")
    samples: int = 16
    sigma_start: float = 0.18
    sigma_step: float = 0.075
    omega_start: float = 0.25
    omega_step: float = 0.32
    input_decay: float = 0.34
    input_omega: float = 2.4
    integration_seconds: float = 36.0
    integration_points: int = 24_000
    duration_seconds: float = 20.0
    sample_rate: int = 44_100
    base_frequency_hz: float = 54.0
    response_mix: float = 0.82
    select_mix: float = 0.30
    ceiling: float = 0.82


def require_power_of_two(value: int) -> None:
    if value < 2 or value & (value - 1):
        raise ValueError("samples must be a power of two and at least 2")


def laplace_grid(config: Config) -> np.ndarray:
    """Arithmetic-progression evaluation points s_j = sigma_j + i omega_j."""
    require_power_of_two(config.samples)
    index = np.arange(config.samples, dtype=float)
    return (
        config.sigma_start + config.sigma_step * index
        + 1j * (config.omega_start + config.omega_step * index)
    )


def input_signal(time: np.ndarray, config: Config) -> np.ndarray:
    """g(t) = exp(-a t) sin(w t), a compact, integrable probe signal."""
    return np.exp(-config.input_decay * time) * np.sin(config.input_omega * time)


def analytical_response(s: np.ndarray, config: Config) -> np.ndarray:
    """Exact Laplace transform of exp(-a t) sin(w t)."""
    shifted = s + config.input_decay
    return config.input_omega / (shifted * shifted + config.input_omega**2)


def numerical_response(s: np.ndarray, config: Config) -> tuple[np.ndarray, np.ndarray]:
    """Numerically integrate the response; retained as the canonical result."""
    time = np.linspace(0.0, config.integration_seconds, config.integration_points)
    probe = input_signal(time, config)
    kernel = np.exp(-np.outer(s, time))
    return np.trapezoid(kernel * probe[None, :], time, axis=1), time


def normalized(values: np.ndarray) -> np.ndarray:
    maximum = float(np.max(np.abs(values)))
    return np.abs(values) / maximum if maximum > 0.0 else np.zeros_like(values, dtype=float)


def equal_power_pan(position: float) -> tuple[float, float]:
    angle = (float(np.clip(position, -1.0, 1.0)) + 1.0) * math.pi / 4.0
    return math.cos(angle), math.sin(angle)


def add_mode(
    audio: np.ndarray,
    start: int,
    frequency: float,
    amplitude: float,
    decay_seconds: float,
    phase: float,
    pan: float,
    sample_rate: int,
) -> None:
    """Add one finite resonant burst, with no continuously excited oscillator."""
    length = min(audio.shape[0] - start, max(1, int(decay_seconds * sample_rate * 5.0)))
    if start >= audio.shape[0] or length <= 0:
        return
    time = np.arange(length, dtype=float) / sample_rate
    attack = np.minimum(time / 0.012, 1.0)
    envelope = attack * np.exp(-time / max(decay_seconds, 0.005))
    signal = amplitude * envelope * np.sin(2.0 * math.pi * frequency * time + phase)
    left, right = equal_power_pan(pan)
    audio[start : start + length, 0] += left * signal
    audio[start : start + length, 1] += right * signal


def render_audio(response: np.ndarray, s: np.ndarray, config: Config) -> np.ndarray:
    """Render direct response and factorized SELECT layers as distinct gestures."""
    total = int(config.duration_seconds * config.sample_rate)
    audio = np.zeros((total, 2), dtype=float)
    magnitudes = normalized(response)
    phases = np.angle(response)
    n_bits = int(math.log2(config.samples))
    slot = total // config.samples

    # Direct numerical-response layer: one finite modal burst per sampled s_j.
    for j, (point, magnitude, phase) in enumerate(zip(s, magnitudes, phases, strict=True)):
        ratio = 1.0 + 0.52 * j + 0.12 * point.imag
        frequency = min(config.base_frequency_hz * ratio, config.sample_rate * 0.42)
        decay = 0.25 + 1.7 / (1.0 + point.real * 3.0)
        pan = phase / math.pi
        add_mode(
            audio, j * slot, frequency, config.response_mix * float(magnitude), decay,
            float(phase), pan, config.sample_rate,
        )

    # SELECT layer: every (time-bit, k-bit) pair is a short, audible relation.
    # Its timing is intentionally derived from bit products, not a note grid.
    pair_count = n_bits * n_bits
    for frame in range(config.samples):
        response_index = frame
        for time_bit in range(n_bits):
            for k_bit in range(n_bits):
                pair = time_bit * n_bits + k_bit
                relation = ((frame >> time_bit) & 1) * ((response_index >> k_bit) & 1)
                if not relation:
                    continue
                start = frame * slot + int((pair + 1) * slot / (pair_count + 1))
                frequency = config.base_frequency_hz * (2.0 + time_bit + 0.5 * k_bit)
                amplitude = config.select_mix * float(magnitudes[response_index]) / math.sqrt(pair_count)
                phase = float(phases[response_index] + (time_bit - k_bit) * math.pi / 5.0)
                pan = (k_bit - time_bit) / max(n_bits - 1, 1)
                add_mode(audio, start, frequency, amplitude, 0.11, phase, pan, config.sample_rate)

    # Protect the exact event structure from a hard clipping artifact.
    peak = float(np.max(np.abs(audio)))
    if peak > 1e-12:
        audio *= config.ceiling / peak
    fade = min(int(0.025 * config.sample_rate), total // 2)
    ramp = np.linspace(0.0, 1.0, fade)
    audio[:fade] *= ramp[:, None]
    audio[-fade:] *= ramp[::-1, None]
    return audio


def write_wav(path: Path, audio: np.ndarray, sample_rate: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    pcm = (np.clip(audio, -1.0, 1.0) * 32767.0).astype("<i2")
    with wave.open(str(path), "wb") as stream:
        stream.setnchannels(2)
        stream.setsampwidth(2)
        stream.setframerate(sample_rate)
        stream.writeframes(pcm.tobytes())


def build(config: Config) -> dict[str, Path]:
    s = laplace_grid(config)
    response, time = numerical_response(s, config)
    analytic = analytical_response(s, config)
    audio = render_audio(response, s, config)
    config.output_dir.mkdir(parents=True, exist_ok=True)

    npz_path = config.output_dir / "laplace_response.npz"
    wav_path = config.output_dir / "qmw_laplace_lchs_render.wav"
    json_path = config.output_dir / "descriptor.json"
    np.savez(
        npz_path,
        s=s,
        response=response,
        analytical_response=analytic,
        absolute_error=np.abs(response - analytic),
        integration_time=time,
    )
    write_wav(wav_path, audio, config.sample_rate)
    descriptor = {
        "study": "qmw_laplace_lchs_sonification_v1",
        "source_paper": "arXiv:2512.17980",
        "claim_boundary": (
            "Offline structural sonification of arithmetic-progression Laplace samples and "
            "SELECT bit-pair relations; not a quantum-circuit simulation or speedup claim."
        ),
        "config": {key: str(value) if isinstance(value, Path) else value for key, value in asdict(config).items()},
        "mapping": {
            "response_magnitude": "finite modal-burst amplitude",
            "response_phase": "stereo position and oscillator phase",
            "real_s": "modal decay",
            "imaginary_s": "modal frequency deformation",
            "select_bit_pair": "short relation burst when both binary controls are one",
        },
        "validation": {
            "max_absolute_response_error": float(np.max(np.abs(response - analytic))),
            "mean_absolute_response_error": float(np.mean(np.abs(response - analytic))),
            "audio_peak": float(np.max(np.abs(audio))),
            "audio_rms": float(np.sqrt(np.mean(audio * audio))),
        },
    }
    json_path.write_text(json.dumps(descriptor, indent=2) + "\n")
    return {"response": npz_path, "audio": wav_path, "descriptor": json_path}


def parse_args() -> Config:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=Config.output_dir)
    parser.add_argument("--samples", type=int, default=Config.samples)
    parser.add_argument("--duration", type=float, default=Config.duration_seconds)
    parser.add_argument("--sample-rate", type=int, default=Config.sample_rate)
    parser.add_argument("--input-decay", type=float, default=Config.input_decay)
    parser.add_argument("--input-omega", type=float, default=Config.input_omega)
    args = parser.parse_args()
    return Config(
        output_dir=args.output_dir, samples=args.samples, duration_seconds=args.duration,
        sample_rate=args.sample_rate, input_decay=args.input_decay, input_omega=args.input_omega,
    )


def main() -> None:
    outputs = build(parse_args())
    print("QMW Laplace/LCHS sonification complete")
    for label, path in outputs.items():
        print(f"  {label}: {path}")


if __name__ == "__main__":
    main()
