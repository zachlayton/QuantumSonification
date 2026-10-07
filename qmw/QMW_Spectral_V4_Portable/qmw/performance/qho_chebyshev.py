"""Read-only QHO-to-Chebyshev excitation mapping.

The canonical oscillator frame remains authoritative.  This module only
constructs a downstream sound descriptor for an active actuator.  QHO Fock
level ``n`` is mapped by convention to audio harmonic ``n + 1``; that is a
sonification choice, not a claim that the oscillator emits that harmonic.

For a unit circular carrier, ``T_k(cos(theta)) = cos(k * theta)``.  The
descriptor therefore contains harmonic amplitudes and phases that can be
rendered either as an explicit Chebyshev waveshaper or as its exactly
equivalent band-limited harmonic bank.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import math

import numpy as np

from qmw.qho.schema import OscillatorFrame


Array = np.ndarray
DIMENSION = 16
EPS = 1.0e-12
REFERENCE_CONTACT_SECONDS = 0.012


class ExcitationMode(str, Enum):
    """Physical contact or explicitly active signed actuator force."""

    IMPACT = "impact"
    ACTUATOR = "actuator"


class CalibrationMode(str, Enum):
    """Physical comparison or Parseval/L2 energy comparison."""

    PHYSICAL = "physical"
    ENERGY = "energy"


@dataclass(frozen=True)
class ChebyshevExcitationSettingsV1:
    order: int = DIMENSION
    coherence_depth: float = 1.0
    excitation_mode: ExcitationMode = ExcitationMode.ACTUATOR
    calibration_mode: CalibrationMode = CalibrationMode.ENERGY
    contact_seconds: float = REFERENCE_CONTACT_SECONDS
    incidence_radians: float = 0.0

    def __post_init__(self) -> None:
        if not 1 <= int(self.order) <= DIMENSION:
            raise ValueError(f"order must lie in [1, {DIMENSION}]")
        if not math.isfinite(float(self.coherence_depth)) or not 0.0 <= self.coherence_depth <= 1.0:
            raise ValueError("coherence_depth must lie in [0, 1]")
        if not math.isfinite(float(self.contact_seconds)) or not 0.001 <= self.contact_seconds <= 0.5:
            raise ValueError("contact_seconds must lie in [0.001, 0.5]")
        if not math.isfinite(float(self.incidence_radians)) or not 0.0 <= self.incidence_radians <= math.pi / 2:
            raise ValueError("incidence_radians must lie in [0, pi/2]")
        object.__setattr__(self, "order", int(self.order))
        object.__setattr__(self, "coherence_depth", float(self.coherence_depth))
        object.__setattr__(self, "contact_seconds", float(self.contact_seconds))
        object.__setattr__(self, "incidence_radians", float(self.incidence_radians))
        object.__setattr__(self, "excitation_mode", ExcitationMode(self.excitation_mode))
        object.__setattr__(self, "calibration_mode", CalibrationMode(self.calibration_mode))


@dataclass(frozen=True)
class QHOChebyshevDescriptorV1:
    amplitudes: Array
    relative_phases: Array
    coherence_reliability: Array
    complex_coefficients: Array
    active_population: float
    incidence_gain: float
    duration_gain: float
    mapping_id: str = "qmw_qho_fock_to_chebyshev_harmonic_v1"
    provenance: str = "read_only_perceptual_mapping_not_qho_emission_physics"


def _validated_density(frame: OscillatorFrame) -> Array:
    if frame.dimension != DIMENSION:
        raise ValueError(f"QHO Chebyshev mapping requires dimension {DIMENSION}")
    if frame.rho is None:
        raise ValueError("QHO Chebyshev phase mapping requires frame.rho")
    rho = np.asarray(frame.rho, dtype=np.complex128)
    if rho.shape != (DIMENSION, DIMENSION) or not np.all(np.isfinite(rho)):
        raise ValueError("frame.rho must be a finite 16 x 16 density matrix")
    return rho


def duration_calibration_gain(settings: ChebyshevExcitationSettingsV1) -> float:
    """Return contact-duration calibration without claiming false equivalence.

    In physical mode, a passive impact is approximately impulse matched by
    inverse-duration scaling.  A signed active actuator instead keeps peak
    drive fixed because its net impulse may be zero.  Energy mode uses the
    inverse square root required for an L2/Parseval comparison.
    """

    ratio = REFERENCE_CONTACT_SECONDS / settings.contact_seconds
    if settings.calibration_mode is CalibrationMode.ENERGY:
        return math.sqrt(ratio)
    if settings.excitation_mode is ExcitationMode.IMPACT:
        return ratio
    return 1.0


def observe_qho_chebyshev(
    frame: OscillatorFrame,
    settings: ChebyshevExcitationSettingsV1 | None = None,
) -> QHOChebyshevDescriptorV1:
    """Map one immutable QHO frame to a harmonic excitation descriptor.

    Adjacent coherences form a declared phase chain.  For a pure state this
    reconstructs neighboring coefficient phases.  For a mixed state it is an
    explicit sonification of the adjacent coherence band, not a hidden claim
    that one global state-vector phase exists.  The influence of each angle is
    faded by ``|rho[n,n+1]| / sqrt(p[n] p[n+1])`` and vanishes safely when the
    corresponding coherence is absent.
    """

    settings = settings or ChebyshevExcitationSettingsV1()
    rho = _validated_density(frame)
    populations = np.real(np.diag(rho)).clip(0.0, None)
    population_total = float(np.sum(populations))
    if population_total <= EPS:
        raise ValueError("QHO populations have zero total weight")
    populations = populations / population_total

    active = np.zeros(DIMENSION, dtype=float)
    active[: settings.order] = 1.0
    amplitudes = np.sqrt(populations) * active
    active_population = float(np.sum(amplitudes**2))
    if (
        settings.calibration_mode is CalibrationMode.ENERGY
        and active_population > EPS
    ):
        amplitudes = amplitudes / math.sqrt(active_population)

    relative_phases = np.zeros(DIMENSION, dtype=float)
    reliability = np.zeros(DIMENSION - 1, dtype=float)
    for index in range(DIMENSION - 1):
        denominator = math.sqrt(float(populations[index] * populations[index + 1]))
        if denominator <= EPS:
            continue
        coherence = complex(rho[index, index + 1])
        reliability[index] = float(np.clip(abs(coherence) / denominator, 0.0, 1.0))
        relative_phases[index + 1] = (
            relative_phases[index]
            - np.angle(coherence) * reliability[index] * settings.coherence_depth
        )

    coefficients = amplitudes * np.exp(1j * relative_phases)
    for array in (amplitudes, relative_phases, reliability, coefficients):
        array.flags.writeable = False
    return QHOChebyshevDescriptorV1(
        amplitudes=amplitudes,
        relative_phases=relative_phases,
        coherence_reliability=reliability,
        complex_coefficients=coefficients,
        active_population=active_population,
        incidence_gain=math.cos(settings.incidence_radians),
        duration_gain=duration_calibration_gain(settings),
    )


__all__ = [
    "CalibrationMode",
    "ChebyshevExcitationSettingsV1",
    "DIMENSION",
    "ExcitationMode",
    "QHOChebyshevDescriptorV1",
    "duration_calibration_gain",
    "observe_qho_chebyshev",
]
