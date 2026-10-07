"""Reference mathematics for the non-recursive harmonic-memory field.

This module is an analysis contract for the audio adapter, not QMW evolution.
It describes the eight-path transfer function used by the initial
Harmonic Memory Interference Field:

``H(f) = sum_k a_k exp(-i 2 pi f tau_k)``.
"""

from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np


DEFAULT_HMI_BASE_DELAY_SECONDS = 0.037
DEFAULT_HMI_RATIOS = (
    1.0, 53 / 37, 71 / 37, 89 / 37,
    113 / 37, 137 / 37, 163 / 37, 191 / 37,
)


@dataclass(frozen=True)
class HarmonicMemoryInterferenceSpec:
    """One declared eight-path coherent temporal aperture array."""

    base_delay_seconds: float = DEFAULT_HMI_BASE_DELAY_SECONDS
    ratios: tuple[float, ...] = DEFAULT_HMI_RATIOS
    harmonic_exponent: float = 1.0

    def __post_init__(self) -> None:
        if not math.isfinite(float(self.base_delay_seconds)) or not 0.020 <= float(self.base_delay_seconds) <= 0.090:
            raise ValueError("base_delay_seconds must be finite and lie in [0.020, 0.090].")
        ratios = tuple(float(value) for value in self.ratios)
        if len(ratios) != 8 or not all(math.isfinite(value) and value > 0.0 for value in ratios):
            raise ValueError("ratios must contain exactly eight finite positive values.")
        exponent = float(self.harmonic_exponent)
        if not math.isfinite(exponent) or not 0.5 <= exponent <= 3.0:
            raise ValueError("harmonic_exponent must lie in [0.5, 3.0].")
        object.__setattr__(self, "base_delay_seconds", float(self.base_delay_seconds))
        object.__setattr__(self, "ratios", ratios)
        object.__setattr__(self, "harmonic_exponent", exponent)

    @property
    def delay_seconds(self) -> np.ndarray:
        values = self.base_delay_seconds * np.asarray(self.ratios, dtype=float)
        values.setflags(write=False)
        return values

    @property
    def harmonic_weights(self) -> np.ndarray:
        raw = np.arange(1, 9, dtype=float) ** (-self.harmonic_exponent)
        values = raw / raw.sum()
        values.setflags(write=False)
        return values

    def transfer_response(self, frequencies_hz: object) -> np.ndarray:
        """Evaluate the coherent phasor sum at one or more frequencies."""

        frequencies = np.asarray(frequencies_hz, dtype=float)
        if not np.all(np.isfinite(frequencies)):
            raise ValueError("frequencies_hz must be finite.")
        phase = -2j * np.pi * np.expand_dims(frequencies, -1) * self.delay_seconds
        return np.sum(self.harmonic_weights * np.exp(phase), axis=-1)


__all__ = [
    "DEFAULT_HMI_BASE_DELAY_SECONDS", "DEFAULT_HMI_RATIOS",
    "HarmonicMemoryInterferenceSpec",
]
