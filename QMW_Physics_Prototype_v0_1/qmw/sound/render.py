"""Offline, deterministic harmonic pluck rendering for an inspectable preview."""
from __future__ import annotations
import wave
from pathlib import Path
import numpy as np
from qmw.core.frame import SoundEvent


def render(sound_events: list[SoundEvent], duration: float, sample_rate: int = 48000) -> np.ndarray:
    """Render events at their simulation timestamps to floating-point stereo.

    Harmonic partials have 1/k weights and progressively shorter decays. A 2 ms
    onset prevents hard discontinuities. Partial frequencies above 0.45 fs are
    omitted. A final common peak reduction preserves stereo balance.
    """
    if not np.isfinite(duration) or duration <= 0:
        raise ValueError("Duration must be finite and positive")
    if isinstance(sample_rate, bool) or not isinstance(sample_rate, int) or sample_rate < 8000:
        raise ValueError("Sample rate must be an integer >= 8000")
    audio = np.zeros((int(np.ceil(duration * sample_rate)), 2), dtype=np.float64)
    for event in sound_events:
        values = [event.t, event.frequency_hz, event.amplitude, event.decay_s, event.pan]
        if not np.isfinite(values).all() or event.frequency_hz <= 0 or event.decay_s <= 0 or event.amplitude < 0:
            raise ValueError("Invalid sound event")
        if event.t >= duration:
            continue
        onset = int(round(event.t * sample_rate))
        start = max(0, onset)
        stop = min(len(audio), onset + int(np.ceil(8 * event.decay_s * sample_rate)))
        if stop <= start:
            continue
        times = (np.arange(start, stop) - onset) / sample_rate
        partial_count = min(8, int(np.floor(0.45 * sample_rate / event.frequency_hz)))
        if partial_count < 1:
            continue
        weights = 1.0 / np.arange(1, partial_count + 1)
        signal = np.zeros(len(times))
        for harmonic, weight in enumerate(weights, 1):
            signal += weight * np.sin(2 * np.pi * harmonic * event.frequency_hz * times) * np.exp(
                -times * np.sqrt(harmonic) / event.decay_s)
        signal *= (1 - np.exp(-times / 0.002)) * event.amplitude / weights.sum()
        pan = np.clip(event.pan, -1.0, 1.0)
        angle = (pan + 1) * np.pi / 4
        audio[start:stop, 0] += signal * np.cos(angle)
        audio[start:stop, 1] += signal * np.sin(angle)
    peak = float(np.max(np.abs(audio)))
    if peak > 0.95:
        audio *= 0.95 / peak
    return audio


def write_wav(path: str | Path, audio: np.ndarray, sample_rate: int = 48000):
    """Write a 16-bit PCM stereo WAV; never silently wrap overflowing samples."""
    a = np.asarray(audio, dtype=float)
    if a.ndim != 2 or a.shape[1] != 2 or not np.isfinite(a).all():
        raise ValueError("WAV audio must be a finite Nx2 stereo array")
    if sample_rate < 8000:
        raise ValueError("Sample rate must be >= 8000")
    pcm = np.round(np.clip(a, -1, 1) * 32767).astype("<i2")
    with wave.open(str(path), "wb") as out:
        out.setnchannels(2)
        out.setsampwidth(2)
        out.setframerate(sample_rate)
        out.writeframes(pcm.tobytes())
