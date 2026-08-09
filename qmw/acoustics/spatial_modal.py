"""Bounded Spat and modal-reverb controls derived from Bloch harmonics."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Sequence

from qmw.acoustics.bloch_harmonics import BlochHarmonicFrame, harmonics_from_bloch


def _clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, float(value)))


@dataclass(frozen=True)
class SpatSourceControl:
    azimuth_degrees: float
    elevation_degrees: float
    distance_metres: float
    aperture_degrees: float
    spread_percent: float

    @property
    def aed(self) -> tuple[float, float, float]:
        return (
            self.azimuth_degrees,
            self.elevation_degrees,
            self.distance_metres,
        )


@dataclass(frozen=True)
class ReverbModalControl:
    resonance: float
    decay: float
    damping: float
    spectral_tilt: float
    modal_warp: float
    mode_weights: tuple[float, ...]


@dataclass(frozen=True)
class SpatialModalControlFrame:
    harmonics: BlochHarmonicFrame
    spat: SpatSourceControl
    reverb: ReverbModalControl


def controls_from_bloch(
    vector: Sequence[float], *, mode_count: int = 8
) -> SpatialModalControlFrame:
    """Create stable spatial and modal controls from one Bloch vector.

    Degree one controls position, degree two controls broad resonance and
    spectral anisotropy, and degree three distributes excitation across modes.
    All feedback-related values are bounded before they reach an audio engine.
    """
    if not isinstance(mode_count, int) or mode_count < 1:
        raise ValueError("mode_count must be a positive integer")

    frame = harmonics_from_bloch(vector, degrees=(1, 2, 3))
    coordinates = frame.coordinates
    values = frame.values()
    x, y, _ = coordinates.cartesian()

    azimuth = math.degrees(math.atan2(y, x)) if coordinates.r > 1.0e-12 else 0.0
    elevation = 90.0 - math.degrees(coordinates.theta)
    radius = coordinates.r
    spat = SpatSourceControl(
        azimuth_degrees=azimuth,
        elevation_degrees=elevation,
        distance_metres=1.0 + 1.5 * (1.0 - radius),
        aperture_degrees=20.0 + 140.0 * (1.0 - radius),
        spread_percent=100.0 * (1.0 - radius),
    )

    q20 = math.tanh(3.0 * values["Y_2_0"])
    q21 = math.tanh(2.5 * (values["Y_2_1c"] + values["Y_2_1s"]))
    q22 = math.tanh(2.5 * (values["Y_2_2c"] - values["Y_2_2s"]))
    resonance = _clamp(0.20 + 0.70 * radius + 0.08 * q21, 0.0, 1.0)
    decay = _clamp(0.62 + 0.30 * radius + 0.045 * q20, 0.45, 0.97)
    damping = _clamp(0.16 + 0.52 * (1.0 - radius) - 0.10 * q20, 0.05, 0.90)
    spectral_tilt = _clamp(q20 + 0.25 * q21, -1.0, 1.0)
    modal_warp = _clamp(0.70 * q22 + 0.20 * q21, -1.0, 1.0)

    shaping_names = (
        "Y_3_0",
        "Y_3_1c",
        "Y_3_1s",
        "Y_3_2c",
        "Y_3_2s",
        "Y_3_3c",
        "Y_3_3s",
        "Y_2_2c",
    )
    raw_weights = [
        _clamp(1.0 + 0.58 * radius * math.tanh(3.0 * values[name]), 0.35, 1.65)
        for name in shaping_names
    ]
    weights = tuple(raw_weights[index % len(raw_weights)] for index in range(mode_count))
    mean_square = sum(weight * weight for weight in weights) / len(weights)
    normalization = math.sqrt(max(mean_square, 1.0e-12))
    normalized_weights = tuple(
        _clamp(weight / normalization, 0.35, 1.65) for weight in weights
    )

    return SpatialModalControlFrame(
        harmonics=frame,
        spat=spat,
        reverb=ReverbModalControl(
            resonance=resonance,
            decay=decay,
            damping=damping,
            spectral_tilt=spectral_tilt,
            modal_warp=modal_warp,
            mode_weights=normalized_weights,
        ),
    )
