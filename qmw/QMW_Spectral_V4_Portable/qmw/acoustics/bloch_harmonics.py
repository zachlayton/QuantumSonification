"""Map reduced-qubit Bloch vectors onto acoustic spherical harmonics."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Iterable, Sequence


_EPSILON = 1.0e-12


@dataclass(frozen=True)
class BlochSphericalCoordinates:
    """A physical Bloch vector expressed using acoustic angle conventions.

    ``theta`` is inclination from +Z in [0, pi]. ``phi`` is azimuth from +X
    toward +Y in [0, 2*pi). The radius is clamped to the physical range [0, 1].
    """

    r: float
    theta: float
    phi: float

    @classmethod
    def from_cartesian(
        cls, vector: Sequence[float]
    ) -> "BlochSphericalCoordinates":
        if len(vector) != 3:
            raise ValueError("a Bloch vector must contain exactly x, y, z")
        x, y, z = (float(axis) for axis in vector)
        if not all(math.isfinite(axis) for axis in (x, y, z)):
            raise ValueError("Bloch-vector components must be finite")

        raw_radius = math.sqrt(x * x + y * y + z * z)
        radius = min(1.0, raw_radius)
        if raw_radius <= _EPSILON:
            return cls(r=0.0, theta=0.0, phi=0.0)

        theta = math.acos(max(-1.0, min(1.0, z / raw_radius)))
        phi = math.atan2(y, x) % math.tau
        return cls(r=radius, theta=theta, phi=phi)

    @classmethod
    def from_spherical(
        cls, r: float, theta: float, phi: float
    ) -> "BlochSphericalCoordinates":
        r, theta, phi = float(r), float(theta), float(phi)
        if not all(math.isfinite(value) for value in (r, theta, phi)):
            raise ValueError("Bloch spherical coordinates must be finite")
        if r < 0.0:
            raise ValueError("Bloch radius cannot be negative")
        if not 0.0 <= theta <= math.pi:
            raise ValueError("theta must be in [0, pi]")
        return cls(r=min(1.0, r), theta=theta, phi=phi % math.tau)

    def cartesian(self) -> tuple[float, float, float]:
        sin_theta = math.sin(self.theta)
        return (
            self.r * sin_theta * math.cos(self.phi),
            self.r * sin_theta * math.sin(self.phi),
            self.r * math.cos(self.theta),
        )


@dataclass(frozen=True)
class HarmonicComponent:
    degree: int
    order: int
    quadrature: str
    value: float

    @property
    def name(self) -> str:
        if self.order == 0:
            return f"Y_{self.degree}_0"
        suffix = "c" if self.quadrature == "cosine" else "s"
        return f"Y_{self.degree}_{self.order}{suffix}"


@dataclass(frozen=True)
class BlochHarmonicFrame:
    coordinates: BlochSphericalCoordinates
    components: tuple[HarmonicComponent, ...]
    backend: str = "python-acoustics"

    def values(self) -> dict[str, float]:
        return {component.name: component.value for component in self.components}

    def to_dict(self) -> dict[str, object]:
        return {
            "bloch": {
                "r": self.coordinates.r,
                "theta": self.coordinates.theta,
                "phi": self.coordinates.phi,
            },
            "backend": self.backend,
            "harmonics": self.values(),
        }


def _acoustic_spherical_harmonic(
    theta: float, phi: float, *, order: int, degree: int
) -> float:
    """Evaluate through python-acoustics, with a fallback for archived builds."""
    try:
        from acoustics.directivity import spherical_harmonic

        return float(spherical_harmonic(theta, phi, m=order, n=degree))
    except ImportError as error:
        # python-acoustics 0.2.6 imports scipy.special.sph_harm, removed in
        # modern SciPy. This keeps the bridge portable if the environment-level
        # compatibility patch has not yet been applied.
        if "sph_harm" not in str(error):
            raise
        from scipy.special import sph_harm_y

        return float(sph_harm_y(degree, order, theta, phi).real)


def evaluate_real_component(
    coordinates: BlochSphericalCoordinates,
    *,
    degree: int,
    order: int = 0,
    quadrature: str = "cosine",
    radial_power: float = 1.0,
) -> HarmonicComponent:
    """Evaluate one orthonormal real spherical-harmonic component.

    Positive orders have cosine and sine quadratures. The sine component is
    evaluated through python-acoustics by rotating azimuth by pi/(2m). Radius
    weighting makes mixed-state contraction audible and removes the undefined
    direction at the center of the Bloch ball.
    """
    if not isinstance(degree, int) or degree < 0:
        raise ValueError("degree must be a non-negative integer")
    if not isinstance(order, int) or not 0 <= order <= degree:
        raise ValueError("order must be an integer in [0, degree]")
    if quadrature not in {"cosine", "sine"}:
        raise ValueError("quadrature must be 'cosine' or 'sine'")
    if order == 0 and quadrature != "cosine":
        raise ValueError("order zero has only a cosine/axial component")
    if not math.isfinite(radial_power) or radial_power < 0.0:
        raise ValueError("radial_power must be finite and non-negative")

    phi = coordinates.phi
    normalization = 1.0
    if order > 0:
        normalization = math.sqrt(2.0)
        if quadrature == "sine":
            phi = (phi - math.pi / (2.0 * order)) % math.tau

    angular = normalization * _acoustic_spherical_harmonic(
        coordinates.theta,
        phi,
        order=order,
        degree=degree,
    )
    value = (coordinates.r**radial_power) * angular
    return HarmonicComponent(degree, order, quadrature, float(value))


def harmonic_bank(
    coordinates: BlochSphericalCoordinates,
    *,
    degrees: Iterable[int] = (1, 2, 3),
    radial_power: float = 1.0,
) -> BlochHarmonicFrame:
    """Evaluate a complete real basis for each requested degree."""
    components: list[HarmonicComponent] = []
    seen: set[int] = set()
    for degree in degrees:
        if not isinstance(degree, int) or degree < 0:
            raise ValueError("degrees must contain non-negative integers")
        if degree in seen:
            continue
        seen.add(degree)
        components.append(
            evaluate_real_component(
                coordinates,
                degree=degree,
                radial_power=radial_power,
            )
        )
        for order in range(1, degree + 1):
            for quadrature in ("cosine", "sine"):
                components.append(
                    evaluate_real_component(
                        coordinates,
                        degree=degree,
                        order=order,
                        quadrature=quadrature,
                        radial_power=radial_power,
                    )
                )
    return BlochHarmonicFrame(coordinates, tuple(components))


def harmonics_from_bloch(
    vector: Sequence[float],
    *,
    degrees: Iterable[int] = (1, 2, 3),
    radial_power: float = 1.0,
) -> BlochHarmonicFrame:
    """Convert a Cartesian Bloch vector directly into acoustic harmonics."""
    return harmonic_bank(
        BlochSphericalCoordinates.from_cartesian(vector),
        degrees=degrees,
        radial_power=radial_power,
    )


def harmonics_from_spherical(
    r: float,
    theta: float,
    phi: float,
    *,
    degrees: Iterable[int] = (1, 2, 3),
    radial_power: float = 1.0,
) -> BlochHarmonicFrame:
    """Use the spherical values already emitted by the spin OSC engines."""
    return harmonic_bank(
        BlochSphericalCoordinates.from_spherical(r, theta, phi),
        degrees=degrees,
        radial_power=radial_power,
    )
