"""Canonical Jones-state representation for a transverse +z plane wave."""

from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np


def wrap_phase(value: float) -> float:
    """Wrap a phase to ``[-pi, pi)``."""

    wrapped = (float(value) + math.pi) % math.tau - math.pi
    return 0.0 if abs(wrapped) < 1.0e-15 else wrapped


def _finite_complex(name: str, value: complex) -> complex:
    result = complex(value)
    if not math.isfinite(result.real) or not math.isfinite(result.imag):
        raise ValueError(f"{name} must have finite real and imaginary parts")
    return result


@dataclass(frozen=True, slots=True)
class JonesState:
    """Two-component electric-field phasor ``(E_x, E_y)``.

    The physical field is ``Re[J exp(i(kz - omega*t))]``.  Consequently the
    relative phase is ``delta = phi_y - phi_x``.  Global phase is retained:
    it is irrelevant to Stokes quantities but required for phase-coherent
    field and audio rendering.
    """

    ex: complex
    ey: complex

    def __post_init__(self) -> None:
        object.__setattr__(self, "ex", _finite_complex("ex", self.ex))
        object.__setattr__(self, "ey", _finite_complex("ey", self.ey))
        if self.intensity <= 0.0:
            raise ValueError("a Jones state cannot have zero total intensity")

    @classmethod
    def from_amplitudes(
        cls,
        amplitude_x: float,
        amplitude_y: float,
        *,
        phase_x: float = 0.0,
        relative_phase: float = 0.0,
    ) -> "JonesState":
        amplitudes = (float(amplitude_x), float(amplitude_y))
        phases = (float(phase_x), float(relative_phase))
        if not all(math.isfinite(value) for value in amplitudes + phases):
            raise ValueError("Jones amplitudes and phases must be finite")
        if any(value < 0.0 for value in amplitudes):
            raise ValueError("Jones amplitudes cannot be negative")
        return cls(
            amplitudes[0] * np.exp(1j * phases[0]),
            amplitudes[1] * np.exp(1j * (phases[0] + phases[1])),
        )

    @property
    def intensity(self) -> float:
        return float(abs(self.ex) ** 2 + abs(self.ey) ** 2)

    @property
    def amplitude_x(self) -> float:
        return float(abs(self.ex))

    @property
    def amplitude_y(self) -> float:
        return float(abs(self.ey))

    @property
    def phase_x(self) -> float:
        return float(np.angle(self.ex)) if self.amplitude_x else 0.0

    @property
    def phase_y(self) -> float:
        return float(np.angle(self.ey)) if self.amplitude_y else 0.0

    @property
    def relative_phase(self) -> float:
        if self.amplitude_x == 0.0 or self.amplitude_y == 0.0:
            return 0.0
        return wrap_phase(float(np.angle(self.ey * self.ex.conjugate())))

    def vector(self, *, normalized: bool = False) -> np.ndarray:
        vector = np.array((self.ex, self.ey), dtype=np.complex128)
        if normalized:
            vector /= math.sqrt(self.intensity)
        vector.setflags(write=False)
        return vector

    def with_relative_phase(self, relative_phase: float) -> "JonesState":
        return JonesState.from_amplitudes(
            self.amplitude_x,
            self.amplitude_y,
            phase_x=self.phase_x,
            relative_phase=relative_phase,
        )


__all__ = ["JonesState", "wrap_phase"]
