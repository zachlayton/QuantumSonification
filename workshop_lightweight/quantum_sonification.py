#!/usr/bin/env python3
"""Small, transparent examples for a quantum-sonification workshop.

This is a classical simulation of one qubit.  It uses quantum observables as
inputs to explicit sound-design mappings; it does not claim that a qubit has
an intrinsic sound or that convolution is performed on quantum hardware.
"""

from __future__ import annotations

import argparse
import math
import wave
from pathlib import Path

import numpy as np


SAMPLE_RATE = 44_100
OUTPUT_DIR = Path(__file__).resolve().parent / "generated_audio"


def qubit(theta: np.ndarray | float, phi: np.ndarray | float = 0.0):
    """Return alpha and beta for cos(theta/2)|0> + exp(i phi)sin(theta/2)|1>."""
    alpha = np.cos(np.asarray(theta) / 2.0)
    beta = np.exp(1j * np.asarray(phi)) * np.sin(np.asarray(theta) / 2.0)
    return alpha, beta


def observables(alpha, beta):
    """Return probabilities and Pauli expectation values for a pure qubit."""
    p0 = np.abs(alpha) ** 2
    p1 = np.abs(beta) ** 2
    cross = np.conjugate(alpha) * beta
    x = 2.0 * np.real(cross)
    y = 2.0 * np.imag(cross)
    z = p0 - p1
    return p0, p1, x, y, z


def two_qubit_state(name: str):
    """Return amplitudes ordered as |00>, |01>, |10>, |11>."""
    states = {
        "00": np.array([1, 0, 0, 0], dtype=complex),
        "plus_zero": np.array([1, 0, 1, 0], dtype=complex) / np.sqrt(2.0),
        "plus_plus": np.ones(4, dtype=complex) / 2.0,
        "bell": np.array([1, 0, 0, 1], dtype=complex) / np.sqrt(2.0),
    }
    return states[name].copy()


def two_qubit_observables(state: np.ndarray):
    """Return joint probabilities, local P(1)s, and the Z-Z correlation."""
    probabilities = np.abs(state) ** 2
    p1_a = float(probabilities[2] + probabilities[3])
    p1_b = float(probabilities[1] + probabilities[3])
    zz = float(probabilities[0] - probabilities[1] - probabilities[2] + probabilities[3])
    return probabilities, p1_a, p1_b, zz


def amplitudes_to_wavetable(amplitudes: np.ndarray, size: int = 256):
    """Map complex basis amplitudes to successive harmonic coefficients.

    Basis amplitude k controls harmonic k + 1. Its magnitude controls harmonic
    magnitude and its complex argument controls harmonic phase. This is an
    illustrative synthesis mapping, not a physical quantum waveform.
    """
    phase = 2.0 * np.pi * np.arange(size) / size
    table = np.zeros(size)
    for index, amplitude in enumerate(np.asarray(amplitudes, dtype=complex)):
        table += abs(amplitude) * np.sin(
            (index + 1) * phase + float(np.angle(amplitude))
        )
    # Remove numerical DC and leave headroom for a synthesizer oscillator.
    table -= np.mean(table)
    return normalize(table, peak=0.95)


def wavetable_preview(table: np.ndarray, frequency: float = 110.0, duration: float = 3.0):
    """Play a single-cycle table with linear interpolation."""
    count = int(duration * SAMPLE_RATE)
    positions = (np.arange(count) * frequency * len(table) / SAMPLE_RATE) % len(table)
    left = np.floor(positions).astype(int)
    fraction = positions - left
    right = (left + 1) % len(table)
    audio = table[left] * (1.0 - fraction) + table[right] * fraction
    return audio * envelope(count, attack=0.03, release=0.08)


def envelope(length: int, attack: float = 0.015, release: float = 0.04):
    env = np.ones(length)
    a = min(length, int(attack * SAMPLE_RATE))
    r = min(length, int(release * SAMPLE_RATE))
    if a:
        env[:a] = np.linspace(0.0, 1.0, a)
    if r:
        env[-r:] = np.linspace(1.0, 0.0, r)
    return env


def normalize(audio: np.ndarray, peak: float = 0.92):
    maximum = float(np.max(np.abs(audio))) if audio.size else 0.0
    return audio if maximum == 0.0 else audio * (peak / maximum)


def write_wav(path: Path, audio: np.ndarray):
    path.parent.mkdir(parents=True, exist_ok=True)
    audio = normalize(np.asarray(audio, dtype=float))
    pcm = np.clip(audio * 32767.0, -32768, 32767).astype("<i2")
    channels = 1 if pcm.ndim == 1 else pcm.shape[1]
    with wave.open(str(path), "wb") as output:
        output.setnchannels(channels)
        output.setsampwidth(2)
        output.setframerate(SAMPLE_RATE)
        output.writeframes(pcm.tobytes())
    print(f"wrote {path}")


def state_tone(theta: float, phi: float, duration: float = 2.0):
    """Map sqrt probabilities to two tone amplitudes and phase to stereo."""
    alpha, beta = qubit(theta, phi)
    p0, p1, x, y, z = observables(alpha, beta)
    t = np.arange(int(duration * SAMPLE_RATE)) / SAMPLE_RATE
    low = math.sqrt(float(p0)) * np.sin(2 * np.pi * 220.0 * t)
    high = math.sqrt(float(p1)) * np.sin(2 * np.pi * 440.0 * t + phi)
    pan = 0.5 + 0.45 * float(y)
    mono = (low + high) * envelope(len(t))
    stereo = np.column_stack((mono * math.sqrt(1.0 - pan), mono * math.sqrt(pan)))
    return stereo, (float(p0), float(p1), float(x), float(y), float(z))


def render_states(output_dir: Path):
    states = {
        "state_0": (0.0, 0.0),
        "state_1": (np.pi, 0.0),
        "state_plus": (np.pi / 2.0, 0.0),
        "state_y_plus": (np.pi / 2.0, np.pi / 2.0),
    }
    for name, (theta, phi) in states.items():
        audio, values = state_tone(theta, phi)
        p0, p1, x, y, z = values
        print(f"{name:12s} P(0)={p0:.2f} P(1)={p1:.2f} <X,Y,Z>=({x:.2f},{y:.2f},{z:.2f})")
        write_wav(output_dir / f"{name}.wav", audio)


def render_sweep(output_dir: Path, duration: float = 10.0):
    """Sonify a smooth RY rotation from 0 to 2pi."""
    count = int(duration * SAMPLE_RATE)
    t = np.arange(count) / SAMPLE_RATE
    theta = np.linspace(0.0, 2.0 * np.pi, count)
    alpha, beta = qubit(theta)
    p0, p1, _, _, _ = observables(alpha, beta)
    low = np.sqrt(p0) * np.sin(2 * np.pi * 220.0 * t)
    high = np.sqrt(p1) * np.sin(2 * np.pi * 440.0 * t)
    audio = (low + high) * envelope(count, attack=0.05, release=0.1)
    write_wav(output_dir / "qubit_rotation.wav", audio)


def click(frequency: float, duration: float = 0.075):
    t = np.arange(int(duration * SAMPLE_RATE)) / SAMPLE_RATE
    return np.sin(2 * np.pi * frequency * t) * np.exp(-45.0 * t)


def render_measurements(output_dir: Path, shots: int = 64, seed: int = 7):
    """Render sampled measurements of |+> as low/high percussive events."""
    rng = np.random.default_rng(seed)
    outcomes = rng.choice([0, 1], size=shots, p=[0.5, 0.5])
    spacing = int(0.14 * SAMPLE_RATE)
    audio = np.zeros(spacing * shots)
    for index, outcome in enumerate(outcomes):
        event = click(300.0 if outcome == 0 else 750.0)
        start = index * spacing
        audio[start : start + len(event)] += event
    zeros = int(np.sum(outcomes == 0))
    print(f"measurement counts: 0={zeros}, 1={shots - zeros}, shots={shots}, seed={seed}")
    write_wav(output_dir / f"measurements_{shots}_shots.wav", audio)


def two_qubit_chord(state: np.ndarray, duration: float = 3.0):
    """Map the four computational-basis probabilities to a four-note chord."""
    probabilities, _, _, _ = two_qubit_observables(state)
    frequencies = [220.0, 277.18, 329.63, 440.0]
    t = np.arange(int(duration * SAMPLE_RATE)) / SAMPLE_RATE
    audio = np.zeros_like(t)
    for probability, frequency in zip(probabilities, frequencies):
        audio += math.sqrt(float(probability)) * np.sin(2 * np.pi * frequency * t)
    return audio * envelope(len(t), attack=0.04, release=0.1)


def render_two_qubit_states(output_dir: Path):
    """Contrast a separable |++> state with the entangled Bell state."""
    for name in ("00", "plus_zero", "plus_plus", "bell"):
        state = two_qubit_state(name)
        probabilities, p1_a, p1_b, zz = two_qubit_observables(state)
        labels = " ".join(f"{basis}={p:.2f}" for basis, p in zip(("00", "01", "10", "11"), probabilities))
        print(f"two_qubit_{name:9s} {labels} | P(A=1)={p1_a:.2f} P(B=1)={p1_b:.2f} <ZZ>={zz:.2f}")
        write_wav(output_dir / f"two_qubit_{name}.wav", two_qubit_chord(state))


def render_two_qubit_measurements(output_dir: Path, shots: int = 64, seed: int = 17):
    """Compare independent |++> samples with correlated Bell-state samples."""
    rng = np.random.default_rng(seed)
    spacing = int(0.16 * SAMPLE_RATE)
    event_length = len(click(400.0))

    for name in ("plus_plus", "bell"):
        probabilities, _, _, _ = two_qubit_observables(two_qubit_state(name))
        outcomes = rng.choice(4, size=shots, p=probabilities)
        audio = np.zeros((spacing * shots + event_length, 2))
        for index, outcome in enumerate(outcomes):
            bit_a, bit_b = divmod(int(outcome), 2)
            start = index * spacing
            # Qubit A is heard on the left, B on the right. Bit 0 is low;
            # bit 1 is high. Bell measurements therefore move together.
            left = click(300.0 if bit_a == 0 else 750.0)
            right = click(360.0 if bit_b == 0 else 900.0)
            audio[start : start + len(left), 0] += left
            audio[start : start + len(right), 1] += right
        equal = int(np.sum((outcomes // 2) == (outcomes % 2)))
        counts = np.bincount(outcomes, minlength=4)
        print(f"{name} counts 00/01/10/11={counts.tolist()}, equal outcomes={equal}/{shots}")
        write_wav(output_dir / f"two_qubit_measurements_{name}_{shots}.wav", audio)


def render_wavetables(output_dir: Path):
    """Write exact 256-frame tables and listenable oscillator previews."""
    tables = {
        "one_qubit_0": np.array([1, 0], dtype=complex),
        "one_qubit_plus": np.array([1, 1], dtype=complex) / np.sqrt(2.0),
        "one_qubit_y_plus": np.array([1, 1j], dtype=complex) / np.sqrt(2.0),
        "two_qubit_plus_plus": two_qubit_state("plus_plus"),
        "two_qubit_bell": two_qubit_state("bell"),
    }
    for name, amplitudes in tables.items():
        table = amplitudes_to_wavetable(amplitudes, size=256)
        write_wav(output_dir / f"wavetable_256_{name}.wav", table)
        write_wav(output_dir / f"wavetable_preview_{name}.wav", wavetable_preview(table))


def dry_phrase(duration: float = 4.0):
    """Generate a short dry phrase so the reverb demo needs no media files."""
    count = int(duration * SAMPLE_RATE)
    audio = np.zeros(count)
    notes = [220.0, 277.18, 329.63, 440.0, 329.63, 277.18]
    spacing = int(0.55 * SAMPLE_RATE)
    for index, frequency in enumerate(notes):
        tone = click(frequency, duration=0.3)
        start = int(0.2 * SAMPLE_RATE) + index * spacing
        audio[start : start + len(tone)] += tone
    return audio


def procedural_ir(kind: str, seed: int):
    """Create contrasting illustrative IRs: compact/bright or long/dark."""
    rng = np.random.default_rng(seed)
    duration, decay, taps = ((0.65, 8.0, 70) if kind == "bright" else (2.4, 2.4, 240))
    count = int(duration * SAMPLE_RATE)
    ir = np.zeros(count)
    ir[0] = 1.0
    positions = rng.integers(int(0.008 * SAMPLE_RATE), count, size=taps)
    gains = rng.normal(0.0, 1.0, taps) * np.exp(-decay * positions / SAMPLE_RATE)
    if kind == "dark":
        gains *= 0.6
    np.add.at(ir, positions, gains)
    # A tiny smoothing filter makes the long room darker.
    if kind == "dark":
        ir = np.convolve(ir, np.ones(18) / 18.0, mode="same")
    return normalize(ir, peak=0.8)


def convolve(signal: np.ndarray, ir: np.ndarray):
    """FFT convolution implemented with NumPy only."""
    length = len(signal) + len(ir) - 1
    fft_length = 1 << (length - 1).bit_length()
    wet = np.fft.irfft(np.fft.rfft(signal, fft_length) * np.fft.rfft(ir, fft_length), fft_length)
    return wet[:length]


def pad(audio: np.ndarray, length: int):
    return np.pad(audio, (0, max(0, length - len(audio))))[:length]


def render_reverb(output_dir: Path, theta: float = np.pi / 2.0):
    dry = dry_phrase()
    ir_a = procedural_ir("bright", 11)
    ir_b = procedural_ir("dark", 29)
    wet_a, wet_b = convolve(dry, ir_a), convolve(dry, ir_b)
    length = max(len(wet_a), len(wet_b))
    p0, p1, *_ = observables(*qubit(theta))
    # Equal-power crossfade: amplitudes are sqrt of the qubit probabilities.
    mixed = math.sqrt(float(p0)) * pad(wet_a, length) + math.sqrt(float(p1)) * pad(wet_b, length)
    print(f"reverb mapping at theta={theta:.3f}: P(0)={float(p0):.3f}, P(1)={float(p1):.3f}")
    write_wav(output_dir / "reverb_00_dry.wav", dry)
    write_wav(output_dir / "reverb_01_bright_ir.wav", ir_a)
    write_wav(output_dir / "reverb_02_dark_ir.wav", ir_b)
    write_wav(output_dir / "reverb_03_bright_room.wav", wet_a)
    write_wav(output_dir / "reverb_04_dark_room.wav", wet_b)
    write_wav(output_dir / "reverb_05_qubit_morph.wav", mixed)


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "example",
        choices=["states", "sweep", "measure", "two-qubit", "entanglement", "wavetable", "reverb", "all"],
        nargs="?",
        default="all",
    )
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    parser.add_argument("--shots", type=int, default=64)
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--theta", type=float, default=np.pi / 2.0, help="reverb qubit angle in radians")
    return parser.parse_args()


def main():
    args = parse_args()
    if args.example in ("states", "all"):
        render_states(args.output_dir)
    if args.example in ("sweep", "all"):
        render_sweep(args.output_dir)
    if args.example in ("measure", "all"):
        render_measurements(args.output_dir, args.shots, args.seed)
    if args.example in ("two-qubit", "all"):
        render_two_qubit_states(args.output_dir)
    if args.example in ("entanglement", "all"):
        render_two_qubit_measurements(args.output_dir, args.shots, args.seed)
    if args.example in ("wavetable", "all"):
        render_wavetables(args.output_dir)
    if args.example in ("reverb", "all"):
        render_reverb(args.output_dir, args.theta)


if __name__ == "__main__":
    main()
