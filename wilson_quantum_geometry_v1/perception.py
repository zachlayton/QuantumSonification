"""Perceptual harmonic-space utilities after James Tenney's provisional model."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from math import isfinite, log2


@dataclass(frozen=True)
class TuneabilityReport:
    """Register-dependent bounds for directly tuning a rational dyad."""

    ratio: Fraction
    lower_frequency: float
    periodicity_pitch: float
    least_common_partial: float
    tuneable: bool
    failures: tuple[str, ...]


def prime_coordinates(
    ratio: int | float | Fraction,
    *,
    collapse_octaves: bool = False,
) -> tuple[tuple[int, int], ...]:
    """Return signed prime exponents for a positive rational interval.

    Numerator exponents are positive and denominator exponents negative.
    With ``collapse_octaves``, the 2-coordinate is removed to form Tenney's
    octave-equivalent pitch-class projection.
    """
    value = _as_fraction(ratio)
    coordinates: dict[int, int] = {}
    for prime, exponent in _factor_integer(value.numerator).items():
        coordinates[prime] = coordinates.get(prime, 0) + exponent
    for prime, exponent in _factor_integer(value.denominator).items():
        coordinates[prime] = coordinates.get(prime, 0) - exponent
    if collapse_octaves:
        coordinates.pop(2, None)
    return tuple(sorted((prime, exponent) for prime, exponent in coordinates.items() if exponent))


def harmonic_distance(
    first: int | float | Fraction,
    second: int | float | Fraction = 1,
) -> float:
    """Return Tenney's logarithmic harmonic distance between two ratios.

    If the reduced interval is ``a/b``, the distance is ``log2(a*b)``.  This
    is a city-block metric when each prime axis is weighted by ``log2(prime)``.
    """
    interval = _as_fraction(first) / _as_fraction(second)
    interval = abs(interval)
    return log2(interval.numerator * interval.denominator)


def harmonic_intersection(ratio: int | float | Fraction) -> float:
    """Return Tenney's dyadic harmonic-intersection measure.

    For reduced ``b/a``, this is ``(a + b - 1) / (a*b)``: the proportion of
    partials belonging to either tone up to their least common partial.
    Unlike harmonic distance it distinguishes reciprocal/otonal orientation.
    """
    value = _as_fraction(ratio)
    numerator = value.numerator
    denominator = value.denominator
    return (denominator + numerator - 1) / (denominator * numerator)


def interval_tuneability(
    ratio: int | float | Fraction,
    lower_frequency: float,
    *,
    minimum_periodicity_pitch: float = 20.0,
    maximum_common_partial: float = 6000.0,
) -> TuneabilityReport:
    """Evaluate Nicholson/Sabat's approximate register-dependent bounds.

    ``ratio`` is upper frequency divided by lower and must be at least unison.
    A dyad is potentially tuneable when its periodicity pitch is at least 20 Hz
    and its least common partial is no higher than 6000 Hz. These configurable
    empirical bounds are performance guidance, not universal thresholds.
    """
    value = _as_fraction(ratio)
    lower_frequency = float(lower_frequency)
    if value < 1:
        raise ValueError("ratio must express upper frequency over lower frequency")
    if not isfinite(lower_frequency) or lower_frequency <= 0:
        raise ValueError("lower_frequency must be finite and positive")
    if minimum_periodicity_pitch <= 0 or maximum_common_partial <= 0:
        raise ValueError("tuneability bounds must be positive")
    periodicity_pitch = lower_frequency / value.denominator
    least_common_partial = lower_frequency * value.numerator
    failures = []
    if periodicity_pitch < minimum_periodicity_pitch:
        failures.append("periodicity_pitch_below_bound")
    if least_common_partial > maximum_common_partial:
        failures.append("common_partial_above_bound")
    return TuneabilityReport(
        ratio=value,
        lower_frequency=lower_frequency,
        periodicity_pitch=periodicity_pitch,
        least_common_partial=least_common_partial,
        tuneable=not failures,
        failures=tuple(failures),
    )


def simplest_ratio_within_tolerance(
    ratio: float,
    tolerance_cents: float,
    *,
    max_denominator: int = 256,
) -> Fraction:
    """Find the lowest-complexity rational inside a cents tolerance window.

    Complexity is Tenney harmonic distance from 1/1.  Ties prefer the smaller
    tuning error and then the smaller denominator.  This makes the tolerance
    operation explicit instead of treating every measured frequency as an
    unlimited-dimensional rational point.
    """
    ratio = float(ratio)
    tolerance_cents = float(tolerance_cents)
    max_denominator = int(max_denominator)
    if not isfinite(ratio) or ratio <= 0:
        raise ValueError("ratio must be finite and positive")
    if not isfinite(tolerance_cents) or tolerance_cents < 0:
        raise ValueError("tolerance_cents must be finite and non-negative")
    if max_denominator < 1:
        raise ValueError("max_denominator must be positive")

    candidates: set[Fraction] = set()
    for denominator in range(1, max_denominator + 1):
        center = ratio * denominator
        for numerator in {max(1, int(center)), max(1, int(center) + 1)}:
            candidate = Fraction(numerator, denominator)
            error = abs(1200.0 * log2(float(candidate) / ratio))
            if error <= tolerance_cents + 1e-12:
                candidates.add(candidate)
    if not candidates:
        raise ValueError("no rational found inside tolerance; increase max_denominator")
    return min(
        candidates,
        key=lambda candidate: (
            harmonic_distance(candidate),
            abs(1200.0 * log2(float(candidate) / ratio)),
            candidate.denominator,
            candidate.numerator,
        ),
    )


def _as_fraction(value: int | float | Fraction) -> Fraction:
    if isinstance(value, Fraction):
        result = value
    elif isinstance(value, int):
        result = Fraction(value)
    else:
        numeric = float(value)
        if not isfinite(numeric):
            raise ValueError("ratio must be finite")
        result = Fraction(numeric).limit_denominator(1_000_000)
    if result <= 0:
        raise ValueError("ratio must be positive")
    return result


def _factor_integer(value: int) -> dict[int, int]:
    remaining = int(value)
    factors: dict[int, int] = {}
    prime = 2
    while prime * prime <= remaining:
        while remaining % prime == 0:
            factors[prime] = factors.get(prime, 0) + 1
            remaining //= prime
        prime = 3 if prime == 2 else prime + 2
    if remaining > 1:
        factors[remaining] = factors.get(remaining, 0) + 1
    return factors
