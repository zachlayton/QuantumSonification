"""Explicit perceptual mappings from Gaussian field data to sound controls."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import math

import numpy as np

from .gaussian_temporal import GaussianSiteClockReading


@dataclass(frozen=True)
class GaussianHarmonicDescriptor:
    """Three-coordinate control surface for the eight-partial QMW voice.

    These values are not Bloch coordinates. They are bounded audio controls
    derived from a site's canonical means and covariance.
    """

    x: float
    y: float
    z: float
    purity: float
    covariance_correlation: float
    entropy_control: float
    reference_frequency: float

    def to_dict(self) -> dict[str, float]:
        return asdict(self)


def gaussian_harmonic_descriptor(
    reading: GaussianSiteClockReading,
    *,
    mass: float,
    propagation_speed: float,
    lattice_spacing: float = 1.0,
    hbar: float = 1.0,
) -> GaussianHarmonicDescriptor:
    """Map one raw Gaussian marginal to bounded GenExpr-style controls."""

    values = np.asarray(
        [mass, propagation_speed, lattice_spacing, hbar], dtype=float
    )
    if not np.isfinite(values).all() or float(np.min(values)) <= 0.0:
        raise ValueError("field scales and hbar must be finite and positive")
    reference = math.sqrt(
        mass * mass + 2.0 * (propagation_speed / lattice_spacing) ** 2
    )
    dimensionless_phi = math.sqrt(reference / hbar) * reading.mean_phi
    dimensionless_pi = reading.mean_pi / math.sqrt(hbar * reference)
    variance_x = reference * reading.variance_phi / hbar
    variance_p = reading.variance_pi / (hbar * reference)
    covariance_xp = reading.covariance_phi_pi / hbar
    determinant = variance_x * variance_p - covariance_xp * covariance_xp
    determinant = max(determinant, 0.25)
    symplectic_eigenvalue = math.sqrt(determinant)
    purity = float(np.clip(0.5 / symplectic_eigenvalue, 0.0, 1.0))
    occupation = max(symplectic_eigenvalue - 0.5, 0.0)
    if occupation <= 1e-15:
        entropy = 0.0
    else:
        entropy = (occupation + 1.0) * math.log(occupation + 1.0)
        entropy -= occupation * math.log(occupation)
    entropy_control = entropy / (1.0 + entropy)
    variance_sum = max(variance_x + variance_p, 1e-15)
    anisotropy = (variance_p - variance_x) / variance_sum
    covariance_correlation = abs(covariance_xp) / math.sqrt(
        max(variance_x * variance_p, 1e-15)
    )
    return GaussianHarmonicDescriptor(
        x=math.tanh(dimensionless_phi),
        y=math.tanh(dimensionless_pi),
        z=float(np.clip(anisotropy, -1.0, 1.0)),
        purity=purity,
        covariance_correlation=float(
            np.clip(covariance_correlation, 0.0, 1.0)
        ),
        entropy_control=float(np.clip(entropy_control, 0.0, 1.0)),
        reference_frequency=reference,
    )


def gaussian_pitch_deviation_control(
    descriptor: GaussianHarmonicDescriptor,
) -> float:
    """Return the signed site-local control used by the pitch adapter.

    The projection deliberately combines local field mean, momentum mean, and
    covariance anisotropy. It is a bounded musical mapping, not a physical
    frequency or a modification of the Gaussian state.
    """

    value = 0.5 * descriptor.x + 0.3 * descriptor.y + 0.2 * descriptor.z
    return float(np.clip(value, -1.0, 1.0))


__all__ = [
    "GaussianHarmonicDescriptor",
    "gaussian_harmonic_descriptor",
    "gaussian_pitch_deviation_control",
]
