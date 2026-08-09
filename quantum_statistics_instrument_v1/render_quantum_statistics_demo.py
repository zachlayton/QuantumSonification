#!/usr/bin/env python3
"""Render a stereo sweep from the Maxwell-Boltzmann limit into degeneracy."""

from __future__ import annotations

import math
from pathlib import Path
import struct
import wave

import numpy as np

try:
    from .quantum_statistics_model import compare_statistics
except ImportError:
    from quantum_statistics_model import compare_statistics


SAMPLE_RATE = 48_000
DURATION_SECONDS = 24.0
OUTPUT = Path(__file__).with_name("quantum_statistics_instrument_demo.wav")
ENERGIES = np.linspace(0.08, 6.0, 10)


def equal_power_pan(pan: float) -> tuple[float, float]:
    pan = max(-1.0, min(1.0, pan))
    return math.sqrt((1.0 - pan) * 0.5), math.sqrt((1.0 + pan) * 0.5)


def build_table() -> list[dict[str, object]]:
    rows = []
    for log_density in np.linspace(-3.0, 2.0, 401):
        states = compare_statistics(10.0**log_density)
        fermi = states["fermi"]
        bose = states["bose"]
        rows.append(
            {
                "fp": fermi.pressure_ratio,
                "bp": bose.pressure_ratio,
                "cond": bose.condensate_fraction,
                "fo": np.array([fermi.mean_occupation(float(x)) for x in ENERGIES]),
                "bo": np.array([bose.mean_occupation(float(x)) for x in ENERGIES]),
                "fw": fermi.spectral_particle_weights(ENERGIES),
                "bw": bose.spectral_particle_weights(ENERGIES),
            }
        )
    return rows


def log_density_at(time_seconds: float) -> float:
    if time_seconds < 4.0:
        return -1.0
    if time_seconds < 20.0:
        return -1.0 + 3.0 * (time_seconds - 4.0) / 16.0
    return math.log10(20.0)


def render() -> None:
    table = build_table()
    fermi_phases = np.zeros(10)
    bose_phases = np.zeros(10)
    fermi_envelopes = np.zeros(10)
    bose_envelopes = np.zeros(10)
    fermi_decay = np.full(10, math.exp(-1.0 / (0.014 * SAMPLE_RATE)))
    bose_decay = np.full(10, math.exp(-1.0 / (0.045 * SAMPLE_RATE)))
    condensate_phase = 0.0
    rng = np.random.default_rng(20260718)
    detector_period_frames = round(0.020 * SAMPLE_RATE)
    detection_efficiency = 0.30
    frames = bytearray()
    total_frames = round(DURATION_SECONDS * SAMPLE_RATE)

    with wave.open(str(OUTPUT), "wb") as audio:
        audio.setnchannels(2)
        audio.setsampwidth(2)
        audio.setframerate(SAMPLE_RATE)
        for frame in range(total_frames):
            t = frame / SAMPLE_RATE
            table_position = (log_density_at(t) + 3.0) * 80.0
            lo = max(0, min(400, int(math.floor(table_position))))
            hi = min(400, lo + 1)
            mix = table_position - lo
            left = 0.0
            right = 0.0

            fp = (1.0 - mix) * float(table[lo]["fp"]) + mix * float(table[hi]["fp"])
            bp = (1.0 - mix) * float(table[lo]["bp"]) + mix * float(table[hi]["bp"])
            condensate = (1.0 - mix) * float(table[lo]["cond"]) + mix * float(table[hi]["cond"])
            fw = (1.0 - mix) * table[lo]["fw"] + mix * table[hi]["fw"]
            bw = (1.0 - mix) * table[lo]["bw"] + mix * table[hi]["bw"]
            fo = (1.0 - mix) * table[lo]["fo"] + mix * table[hi]["fo"]
            bo = (1.0 - mix) * table[lo]["bo"] + mix * table[hi]["bo"]

            if frame % detector_period_frames == 0:
                for index in range(10):
                    # One fermionic state has the Bernoulli law n in {0,1}.
                    if rng.random() < min(1.0, detection_efficiency * float(fo[index])):
                        fermi_envelopes[index] += 0.12 + 0.22 * math.sqrt(float(fw[index]))

                    # One bosonic state has the geometric law n in {0,1,2,...}.
                    bose_mean = detection_efficiency * max(0.0, 1.0 - condensate) * float(bo[index])
                    if bose_mean > 0.0:
                        ratio = bose_mean / (1.0 + bose_mean)
                        count = min(32, int(math.log(1.0 - rng.random()) / math.log(ratio)))
                        if count > 0:
                            burst = math.sqrt(count) / math.sqrt(1.0 + 0.35 * count)
                            bose_envelopes[index] += (0.10 + 0.20 * math.sqrt(float(bw[index]))) * burst
                            decay_seconds = min(0.260, 0.034 + 0.014 * count)
                            bose_decay[index] = math.exp(-1.0 / (decay_seconds * SAMPLE_RATE))

            for index in range(10):
                fermi_frequency = 110.0 + index * 38.0 * fp
                bose_frequency = 110.0 + index * 38.0 * bp
                fermi_phases[index] += 2.0 * math.pi * fermi_frequency / SAMPLE_RATE
                bose_phases[index] += 2.0 * math.pi * bose_frequency / SAMPLE_RATE
                fermi_signal = fermi_envelopes[index] * math.sin(fermi_phases[index])
                bose_signal = bose_envelopes[index] * math.sin(bose_phases[index])
                fl, fr = equal_power_pan(-0.88 + 0.34 * index / 9.0)
                bl, br = equal_power_pan(0.54 + 0.34 * index / 9.0)
                left += fermi_signal * fl + bose_signal * bl
                right += fermi_signal * fr + bose_signal * br
                fermi_envelopes[index] *= fermi_decay[index]
                bose_envelopes[index] *= bose_decay[index]

            condensate_phase += 2.0 * math.pi * 55.0 / SAMPLE_RATE
            condensate_signal = 0.30 * math.sqrt(max(0.0, condensate)) * math.sin(condensate_phase)
            left += condensate_signal / math.sqrt(2.0)
            right += condensate_signal / math.sqrt(2.0)

            edge = min(t, DURATION_SECONDS - t)
            fade = min(1.0, max(0.0, edge / 0.04))
            left = math.tanh(0.48 * fade * left)
            right = math.tanh(0.48 * fade * right)
            frames.extend(struct.pack("<hh", round(left * 32767), round(right * 32767)))
            if len(frames) >= 65_536:
                audio.writeframesraw(frames)
                frames.clear()
        if frames:
            audio.writeframesraw(frames)
    print(f"rendered {OUTPUT}")


if __name__ == "__main__":
    render()
