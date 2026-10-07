"""Poincare-sphere coordinates and polarization-ellipse geometry."""

from __future__ import annotations

from dataclasses import dataclass
import math

from .stokes import StokesParameters


@dataclass(frozen=True, slots=True)
class PoincareState:
    """Normalized Stokes vector plus unambiguous geometric labels.

    ``rotation_direction`` describes the time-domain field as viewed in an
    x-y coordinate plane while looking along +z.  The deliberately explicit
    label avoids the mutually reversed right/left circular conventions used
    by different disciplines.
    """

    s1: float
    s2: float
    s3: float
    radius: float
    ellipse_azimuth: float
    ellipticity_angle: float
    polarization_kind: str
    rotation_direction: str

    @classmethod
    def from_stokes(
        cls, stokes: StokesParameters, *, tolerance: float = 1.0e-10
    ) -> "PoincareState":
        s1, s2, s3 = stokes.normalized()
        radius = math.sqrt(s1 * s1 + s2 * s2 + s3 * s3)
        azimuth = 0.5 * math.atan2(s2, s1)
        ellipticity = 0.5 * math.asin(max(-1.0, min(1.0, s3)))
        if abs(s3) <= tolerance:
            kind = "linear"
            direction = "none"
        elif math.hypot(s1, s2) <= tolerance:
            kind = "circular"
            direction = (
                "counterclockwise_along_plus_z"
                if s3 < 0.0
                else "clockwise_along_plus_z"
            )
        else:
            kind = "elliptical"
            direction = (
                "counterclockwise_along_plus_z"
                if s3 < 0.0
                else "clockwise_along_plus_z"
            )
        return cls(s1, s2, s3, radius, azimuth, ellipticity, kind, direction)

    def vector(self) -> tuple[float, float, float]:
        return (self.s1, self.s2, self.s3)


__all__ = ["PoincareState"]
