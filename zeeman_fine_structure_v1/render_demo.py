#!/usr/bin/env python3
"""Offline audition: a field sweep, then quantum beats.

Part 1 (16 s): the anomalous preset under a field rising from 0 to 6 T
(audible 40 Hz/T).  Weak field: lines follow the coupled multiplets.  Strong
field: each qubit flips at its own g * nu_L (Paschen-Back analogue).  Every
line is an oscillator keyed by its tracked levels, so lines glide through the
avoided crossings without jumping.  sigma+ is placed right, sigma- left, pi
in the centre.

Part 2 (6 s): quantum beats after a coherent x-pulse at 3 T, as an amplitude
envelope on the carrier.

Usage:  python3 -m zeeman_fine_structure_v1.render_demo [OUTFILE.wav]
"""

from __future__ import annotations

import sys
import wave
from pathlib import Path

import numpy as np

from .model import PRESETS, quantum_beats, sweep

SR = 44_100
CARRIER = 220.0
BLOCK = 512


def render_sweep(seconds: float = 16.0, b_max: float = 6.0) -> np.ndarray:
    cfg = PRESETS["anomalous"]
    n_blocks = int(seconds * SR / BLOCK)
    fields = np.linspace(0.0, b_max, n_blocks) ** 1.0
    frames = sweep(cfg, fields)
    out = np.zeros((n_blocks * BLOCK, 2))
    phases: dict[tuple, float] = {}
    gains: dict[tuple, float] = {}
    t = np.arange(BLOCK) / SR
    for k, fr in enumerate(frames):
        targets: dict[tuple, tuple[float, float, float]] = {}
        for line in fr.lines:
            shift = line.shift_hz
            if line.polarization == "sigma":
                targets[("s+", line.upper, line.lower)] = (CARRIER + shift, line.strength, 1.0)
                targets[("s-", line.upper, line.lower)] = (CARRIER - shift, line.strength, -1.0)
            else:
                targets[("pi", line.upper, line.lower)] = (CARRIER + shift, line.strength, 0.0)
                targets[("pi-", line.upper, line.lower)] = (CARRIER - shift, line.strength, 0.0)
        for key in set(gains) | set(targets):
            f, s, pan = targets.get(key, (None, 0.0, 0.0))
            g0 = gains.get(key, 0.0)
            g1 = np.sqrt(s)
            if f is None:
                if g0 < 1e-4:
                    gains.pop(key, None)
                    phases.pop(key, None)
                    continue
                f = CARRIER
            ramp = np.linspace(g0, g1, BLOCK, endpoint=False)
            ph = phases.get(key, 0.0)
            sig = ramp * np.sin(ph + 2 * np.pi * f * t)
            phases[key] = (ph + 2 * np.pi * f * BLOCK / SR) % (2 * np.pi)
            gains[key] = g1
            lr = np.array([np.sqrt(0.5 * (1 - pan)), np.sqrt(0.5 * (1 + pan))])
            out[k * BLOCK:(k + 1) * BLOCK] += sig[:, None] * lr[None, :]
    return out


def render_beats(seconds: float = 6.0) -> np.ndarray:
    env = quantum_beats(PRESETS["anomalous"], 3.0, seconds, SR, decay_hz=0.4)
    env = env / (np.max(np.abs(env)) + 1e-12)
    t = np.arange(env.size) / SR
    mono = (0.5 + 0.5 * env) * np.sin(2 * np.pi * CARRIER * t)
    return np.column_stack([mono, mono])


def main(path: str | None = None) -> Path:
    out_path = Path(path) if path else Path(__file__).with_name("zeeman_fine_structure_demo.wav")
    audio = np.vstack([render_sweep(), np.zeros((SR // 2, 2)), render_beats()])
    audio = 0.8 * audio / (np.max(np.abs(audio)) + 1e-12)
    pcm = (audio * 32767).astype("<i2")
    with wave.open(str(out_path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    return out_path


if __name__ == "__main__":
    print(main(sys.argv[1] if len(sys.argv) > 1 else None))
