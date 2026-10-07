"""Stokes parameters derived from the canonical Jones state.

Convention
----------
``S3 = 2 Im(E_x E_y*)`` with physical phasors
``Re[J exp(i(kz - omega*t))]``.  Therefore ``(1, i)/sqrt(2)`` has ``S3=-1``
and rotates from +x toward +y as time increases at fixed z.  Some optics and
IEEE sources reverse this sign; QMW never infers handedness from an unlabeled
external ``S3`` value.
"""

from __future__ import annotations

from dataclasses import dataclass
import math

from .jones import JonesState


STOKES_S3_CONVENTION = "S3=2*Im(Ex*conj(Ey)); field=Re[J*exp(i(kz-omega*t))]"


@dataclass(frozen=True, slots=True)
class StokesParameters:
    s0: float
    s1: float
    s2: float
    s3: float

    @classmethod
    def from_jones(cls, jones: JonesState) -> "StokesParameters":
        cross = jones.ex * jones.ey.conjugate()
        return cls(
            jones.intensity,
            float(abs(jones.ex) ** 2 - abs(jones.ey) ** 2),
            float(2.0 * cross.real),
            float(2.0 * cross.imag),
        )

    @property
    def polarized_intensity(self) -> float:
        return math.sqrt(self.s1**2 + self.s2**2 + self.s3**2)

    @property
    def degree_of_polarization(self) -> float:
        if self.s0 <= 0.0:
            return 0.0
        return min(1.0, self.polarized_intensity / self.s0)

    def normalized(self) -> tuple[float, float, float]:
        if self.s0 <= 0.0:
            raise ValueError("cannot normalize zero-intensity Stokes parameters")
        return (self.s1 / self.s0, self.s2 / self.s0, self.s3 / self.s0)

    def as_tuple(self) -> tuple[float, float, float, float]:
        return (self.s0, self.s1, self.s2, self.s3)


__all__ = ["STOKES_S3_CONVENTION", "StokesParameters"]
