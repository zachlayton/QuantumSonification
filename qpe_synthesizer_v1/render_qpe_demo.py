#!/usr/bin/env python3
"""Render a deterministic stereo demonstration of QPE as a synthesizer."""

from __future__ import annotations

import math
from pathlib import Path
import struct
import wave

import numpy as np

try:
    from .qpe_model import Eigenstate, phase_to_frequency, run_qpe
except ImportError:
    from qpe_model import Eigenstate, phase_to_frequency, run_qpe


SAMPLE_RATE = 48_000
DURATION = 18.0
OUTPUT = Path(__file__).with_name("qpe_synthesizer_demo.wav")
STATES = [
    Eigenstate(0.125, math.sqrt(0.42), "u0"),
    Eigenstate(0.301, math.sqrt(0.27) * 1j, "u1"),
    Eigenstate(0.547, math.sqrt(0.20), "u2"),
    Eigenstate(0.823, -math.sqrt(0.11), "u3"),
]


def precision_at(time_seconds: float) -> int:
    return min(8, 3 + int(time_seconds // 3.0))


def pan_gains(pan: float) -> tuple[float, float]:
    return math.sqrt((1.0 - pan) * 0.5), math.sqrt((1.0 + pan) * 0.5)


def render() -> Path:
    rng = np.random.default_rng(20260718)
    total = round(DURATION * SAMPLE_RATE)
    output = np.zeros((total, 2), dtype=np.float64)
    beat_seconds = 60.0 / 116.0 / 2.0
    note_times = np.arange(0.25, DURATION - 0.2, beat_seconds)

    for note_number, onset in enumerate(note_times):
        bits = precision_at(float(onset))
        shot = run_qpe(STATES, bits, rng)
        frequency = phase_to_frequency(shot.measured_phase, root_hz=55.0, span_octaves=4.0)
        start = round(float(onset) * SAMPLE_RATE)
        length = min(round(0.62 * SAMPLE_RATE), total - start)
        t = np.arange(length) / SAMPLE_RATE
        attack = np.minimum(1.0, t / 0.008)
        envelope = attack * np.exp(-t / (0.20 + 0.035 * bits))
        error = min(1.0, abs(shot.signed_error) * (1 << bits))
        phase = 2.0 * math.pi * frequency * t
        # Precision removes inharmonic haze; the selected eigenstate sets color.
        tone = np.sin(phase)
        tone += (0.34 - 0.22 * error) * np.sin(2.0 * phase + 0.7 * shot.eigenstate_index)
        tone += 0.18 * error * np.sin(phase * (1.0 + 0.03125 * (1 << (8 - bits))))
        amplitude = 0.24 / math.sqrt(1.0 + 0.25 * bits)
        pan = -0.75 + 1.5 * shot.exact_phase
        left, right = pan_gains(pan)
        output[start : start + length, 0] += amplitude * envelope * tone * left
        output[start : start + length, 1] += amplitude * envelope * tone * right

    peak = float(np.max(np.abs(output)))
    output = np.tanh(1.35 * output / max(0.5, peak)) * 0.82
    fade = round(0.04 * SAMPLE_RATE)
    output[:fade] *= np.linspace(0.0, 1.0, fade)[:, None]
    output[-fade:] *= np.linspace(1.0, 0.0, fade)[:, None]

    frames = bytearray()
    with wave.open(str(OUTPUT), "wb") as audio:
        audio.setnchannels(2)
        audio.setsampwidth(2)
        audio.setframerate(SAMPLE_RATE)
        for left, right in output:
            frames.extend(struct.pack("<hh", round(left * 32767), round(right * 32767)))
            if len(frames) >= 65_536:
                audio.writeframesraw(frames)
                frames.clear()
        if frames:
            audio.writeframesraw(frames)
    print(f"rendered {OUTPUT}")
    return OUTPUT


if __name__ == "__main__":
    render()
