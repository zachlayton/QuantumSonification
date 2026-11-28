"""Audio renders for the three listening modes.

voices     each qubit is a voice; its bit picks the fundamental or the fifth.
           Bell pair: the two always move together (unison of chance).
           Independent: they part ways and the fifth appears against itself.
agreement  each qubit alone is a noise click (pure chance, left and right);
           a sustained tone sounds only on shots where the two agree.
sweep      B's measurement angle turns from 0 to 180 degrees; agreement falls
           along cos^2(theta/2), heard as unisons giving way to fifths.

All renders are stereo WAV, A left and B right, at 44.1 kHz.
"""

from __future__ import annotations

import wave
from pathlib import Path
from typing import Sequence

import numpy as np

from .source import ShotRun

SR = 44_100
F0 = 220.0
FIFTH = F0 * 1.5


def _pluck(freq: float, n: int, decay: float = 7.0) -> np.ndarray:
    t = np.arange(n) / SR
    env = np.exp(-decay * t) * np.minimum(1.0, t * 400.0)
    return env * (np.sin(2 * np.pi * freq * t) + 0.3 * np.sin(4 * np.pi * freq * t))


def _click(n: int, rng: np.random.Generator) -> np.ndarray:
    m = min(n, int(0.03 * SR))
    burst = rng.standard_normal(m) * np.exp(-np.arange(m) / (0.004 * SR))
    out = np.zeros(n)
    out[:m] = burst
    return out


def render_voices(runs: Sequence[ShotRun], rate: float = 6.0) -> np.ndarray:
    step = int(SR / rate)
    shots = np.vstack([r.shots for r in runs])
    out = np.zeros((len(shots) * step + SR, 2))
    for k, (a, b) in enumerate(shots):
        i = k * step
        out[i:i + 2 * step, 0] += _pluck(FIFTH if a else F0, 2 * step)
        out[i:i + 2 * step, 1] += _pluck(FIFTH if b else F0, 2 * step)
    return out


def render_agreement(runs: Sequence[ShotRun], rate: float = 10.0, seed: int = 0) -> np.ndarray:
    rng = np.random.default_rng(seed)
    step = int(SR / rate)
    shots = np.vstack([r.shots for r in runs])
    n = len(shots) * step + SR
    out = np.zeros((n, 2))
    gate = np.zeros(n)
    for k, (a, b) in enumerate(shots):
        i = k * step
        out[i:i + step, 0] += 0.5 * _click(step, rng) * (1.0 if a else 0.6)
        out[i:i + step, 1] += 0.5 * _click(step, rng) * (1.0 if b else 0.6)
        if a == b:
            gate[i:i + step] = 1.0
    # smooth the gate so consecutive agreements join into one held tone
    k = int(0.02 * SR)
    gate = np.convolve(gate, np.ones(k) / k, mode="same")
    t = np.arange(n) / SR
    tone = gate * (np.sin(2 * np.pi * F0 * t) + 0.5 * np.sin(2 * np.pi * 2 * F0 * t)) * 0.35
    out += tone[:, None]
    return out


def render_sweep(runs: Sequence[ShotRun], rate: float = 12.0) -> np.ndarray:
    """runs ordered by angle; voices mode, so agreement is heard as unison."""
    return render_voices(runs, rate)


def write_wav(path: Path, audio: np.ndarray) -> Path:
    audio = 0.85 * audio / (np.max(np.abs(audio)) + 1e-12)
    pcm = (audio * 32767).astype("<i2")
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    return Path(path)
