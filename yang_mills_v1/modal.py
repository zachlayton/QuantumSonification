"""Gauge-invariant field-energy excitation for QMW's sixteen modal lanes."""
from __future__ import annotations

from dataclasses import dataclass
import math
import numpy as np
from .engine import FieldSnapshot


@dataclass(frozen=True)
class ModalExcitationFrame:
    time: float
    magnitudes: np.ndarray
    speeds: np.ndarray
    field: FieldSnapshot


class ModalExcitationAdapter:
    """Fixed spatial bins, fixed absolute energy calibration, exponential smoothing.

    This does not synthesize a density matrix or reinterpret color components as
    audible phase. Pitch, decay, purity and coherence remain host controls.
    """
    def __init__(self, *, coupling: float = 0.5, energy_scale: float = 1.0,
                 smoothing_seconds: float = 0.08, motion_scale: float = 1.0) -> None:
        values = (coupling, energy_scale, smoothing_seconds, motion_scale)
        if not all(math.isfinite(v) for v in values):
            raise ValueError("adapter parameters must be finite")
        if not 0 <= coupling <= 1 or energy_scale <= 0 or smoothing_seconds < 0 or motion_scale <= 0:
            raise ValueError("invalid coupling, energy scale, smoothing or motion scale")
        self.coupling = coupling
        self.energy_scale = energy_scale
        self.smoothing_seconds = smoothing_seconds
        self.motion_scale = motion_scale
        self.reset()

    def reset(self) -> None:
        self._previous_time = None
        self._previous_energy = None
        self._magnitudes = np.zeros(16)
        self._speeds = np.zeros(16)
        self._shape = None

    def update(self, field: FieldSnapshot) -> ModalExcitationFrame:
        energy = np.asarray(field.site_energy, dtype=float)
        if energy.ndim != 2 or not np.all(np.isfinite(energy)) or np.any(energy < 0):
            raise ValueError("site energy must be a finite nonnegative 2D array")
        if not math.isfinite(field.time) or field.time < 0:
            raise ValueError("field time must be finite and nonnegative")
        if self._shape is not None and energy.shape != self._shape:
            raise ValueError("reset adapter before changing the lattice shape")
        if self._previous_time is not None and field.time <= self._previous_time:
            raise ValueError("field times must increase; reset before restarting")
        # Site (x,y) is assigned once to the corresponding 4x4 spatial bin.
        x, y = np.indices(energy.shape)
        lanes = (4 * (4 * x // energy.shape[0]) + 4 * y // energy.shape[1]).reshape(-1)
        binned = np.bincount(lanes, weights=energy.reshape(-1), minlength=16)
        target = self.coupling * np.sqrt(binned / (binned + self.energy_scale))
        if self._previous_time is None:
            dt = 0.0
            speed = np.zeros(16)
            self._magnitudes = target
        else:
            dt = field.time - self._previous_time
            rate = np.abs(binned - self._previous_energy) / dt
            speed = self.coupling * rate / (rate + self.motion_scale)
            alpha = 1.0 if self.smoothing_seconds == 0 else -math.expm1(-dt / self.smoothing_seconds)
            self._magnitudes += alpha * (target - self._magnitudes)
            self._speeds += alpha * (speed - self._speeds)
        self._previous_time = field.time
        self._previous_energy = binned
        self._shape = energy.shape
        return ModalExcitationFrame(field.time, self._magnitudes.copy(), self._speeds.copy(), field)
