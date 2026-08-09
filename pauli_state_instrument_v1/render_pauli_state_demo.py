#!/usr/bin/env python3
"""Render the ledger, spinor, and antisymmetry studies as a stereo WAV."""

from __future__ import annotations

import math
from pathlib import Path
import struct
import wave

try:
    from .pauli_state_model import strong_field_audio_frequency, two_p_addresses
except ImportError:  # Direct execution from this directory.
    from pauli_state_model import strong_field_audio_frequency, two_p_addresses


SAMPLE_RATE = 48_000
SECTION_SECONDS = 5.0
OUTPUT = Path(__file__).with_name("pauli_state_instrument_demo.wav")


def equal_power_pan(value: float) -> tuple[float, float]:
    value = max(-1.0, min(1.0, value))
    return math.sqrt((1.0 - value) / 2.0), math.sqrt((1.0 + value) / 2.0)


def render() -> None:
    addresses = two_p_addresses()
    carrier_phase = 0.0
    modulator_phases = [0.0] * len(addresses)
    total_frames = round(3.0 * SECTION_SECONDS * SAMPLE_RATE)
    frames = bytearray()

    with wave.open(str(OUTPUT), "wb") as audio:
        audio.setnchannels(2)
        audio.setsampwidth(2)
        audio.setframerate(SAMPLE_RATE)

        for frame in range(total_frames):
            time_seconds = frame / SAMPLE_RATE
            section = min(int(time_seconds / SECTION_SECONDS), 2)
            local = time_seconds - section * SECTION_SECONDS
            progress = local / SECTION_SECONDS
            left = 0.0
            right = 0.0

            if section == 0:
                # Closed 2p shell unfolded by quadrature SSB ring multiplication.
                field_t = 2.0 * progress
                carrier_phase += 2.0 * math.pi * 220.0 / SAMPLE_RATE
                fm_index = 4.0 * progress
                for voice, address in enumerate(addresses):
                    frequency = strong_field_audio_frequency(
                        address,
                        base_hz=220.0,
                        orbital_spacing_hz=24.0,
                        field_t=field_t,
                        zeeman_hz_per_t=30.0,
                    )
                    displacement = frequency - 220.0
                    modulator_phases[voice] += 2.0 * math.pi * abs(displacement) / SAMPLE_RATE
                    mod_cos = math.cos(modulator_phases[voice])
                    mod_sin = math.sin(modulator_phases[voice])
                    phase_modulation = fm_index * mod_sin
                    carrier_cos = math.cos(carrier_phase + phase_modulation)
                    carrier_sin = math.sin(carrier_phase + phase_modulation)
                    ring_cos = carrier_cos * mod_cos
                    ring_sin = carrier_sin * mod_sin
                    # Raw real multiplication retains both fc-fm and fc+fm.
                    signal = 0.16 * math.sqrt(2.0) * ring_cos
                    pan = max(-0.95, min(0.95, 0.62 * address.m_l + 0.16 * address.spin_twice))
                    pan_left, pan_right = equal_power_pan(pan)
                    left += signal * pan_left
                    right += signal * pan_right
            elif section == 1:
                # Coherent reference intensity for a spinor rotated through 4pi.
                angle = progress * 4.0 * math.pi
                intensity = 0.5 * (1.0 + math.cos(angle / 2.0))
                amplitude = 0.42 * math.sqrt(max(0.0, intensity))
                signal = amplitude * math.sin(2.0 * math.pi * 110.0 * local)
                left = signal
                right = signal
            else:
                # Norm of a normalized Slater wedge as overlap approaches one.
                overlap = progress
                wedge_norm = math.sqrt(max(0.0, 1.0 - overlap * overlap))
                signal = 0.42 * wedge_norm * math.sin(2.0 * math.pi * 330.0 * local)
                left = signal
                right = signal

            edge = min(local, SECTION_SECONDS - local)
            fade = min(1.0, max(0.0, edge / 0.04))
            left = math.tanh(0.72 * left * fade)
            right = math.tanh(0.72 * right * fade)
            frames.extend(struct.pack("<hh", round(left * 32767), round(right * 32767)))

            if len(frames) >= 32_768:
                audio.writeframesraw(frames)
                frames.clear()
        if frames:
            audio.writeframesraw(frames)

    print(f"rendered {OUTPUT}")


if __name__ == "__main__":
    render()
