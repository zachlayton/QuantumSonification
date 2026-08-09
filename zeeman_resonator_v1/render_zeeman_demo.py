#!/usr/bin/env python3
"""Render a short stereo audition of the three Zeeman Resonator presets."""

from __future__ import annotations

import math
import struct
import wave
from pathlib import Path

try:
    from .zeeman_model import PRESETS
except ImportError:  # Direct execution from this directory.
    from zeeman_model import PRESETS


SAMPLE_RATE = 48_000
CARRIER_HZ = 220.0
SPREAD_HZ_PER_T = 36.0
SEGMENTS = ("normal", "sodium_d1", "sodium_d2")
SECONDS_PER_SEGMENT = 4.0
OUTPUT = Path(__file__).with_name("zeeman_resonator_demo.wav")


def render() -> None:
    total_frames = int(SAMPLE_RATE * SECONDS_PER_SEGMENT * len(SEGMENTS))
    carrier_phase = 0.0
    modulator_phases = [0.0] * 8

    with wave.open(str(OUTPUT), "wb") as audio:
        audio.setnchannels(2)
        audio.setsampwidth(2)
        audio.setframerate(SAMPLE_RATE)

        block = bytearray()
        for frame in range(total_frames):
            absolute_time = frame / SAMPLE_RATE
            segment_index = min(int(absolute_time / SECONDS_PER_SEGMENT), len(SEGMENTS) - 1)
            local_time = absolute_time - segment_index * SECONDS_PER_SEGMENT
            preset = PRESETS[SEGMENTS[segment_index]]
            amplitudes = preset.normalized_amplitudes()

            # Every section opens from B=0 to 4 T. Integrating phase keeps the
            # moving sidebands continuous during the field sweep.
            field_t = 4.0 * local_time / SECONDS_PER_SEGMENT
            carrier_phase += 2.0 * math.pi * CARRIER_HZ / SAMPLE_RATE
            carrier_cos = math.cos(carrier_phase)
            carrier_sin = math.sin(carrier_phase)
            left = 0.22 * preset.dry_pi_strength * carrier_cos
            right = left

            for voice, (component, amplitude) in enumerate(zip(preset.components, amplitudes)):
                shift_hz = component.audible_shift_hz(field_t, SPREAD_HZ_PER_T)
                modulator_phases[voice] += 2.0 * math.pi * shift_hz / SAMPLE_RATE
                mod_cos = math.cos(modulator_phases[voice])
                mod_sin = math.sin(modulator_phases[voice])
                ring_cos = carrier_cos * mod_cos
                ring_sin = carrier_sin * mod_sin
                gain = 0.34 * amplitude
                left += gain * (ring_cos + ring_sin)
                right += gain * (ring_cos - ring_sin)

            edge = min(local_time, SECONDS_PER_SEGMENT - local_time)
            fade = min(1.0, max(0.0, edge / 0.04))
            left = math.tanh(left * fade)
            right = math.tanh(right * fade)
            block.extend(struct.pack("<hh", int(left * 32767), int(right * 32767)))

            if len(block) >= 32_768:
                audio.writeframesraw(block)
                block.clear()
        if block:
            audio.writeframesraw(block)

    print(f"rendered {OUTPUT}")


if __name__ == "__main__":
    render()
