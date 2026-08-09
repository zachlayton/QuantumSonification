"""Subharmonic Pythagorean Quantum Time (SPQT) reference implementation.

This module implements an exact rational geometry of recurrence:

    period ratio     tau_(p:q) = (p/q) T
    response rate    omega     = (q/p) Omega
    phase per tick   Delta phi = 2*pi*q/p

The ratios are explicit compositional clocks.  They may parameterize a
Hamiltonian, but that programmed recurrence must be distinguished from an
emergent Floquet time-crystalline response.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from math import gcd, log2, pi
from typing import Iterable, Mapping, Sequence

import numpy as np

try:
    from .qmw_temporal_core16_v1 import (
        DIM,
        as_complex_matrix,
        least_common_multiple,
    )
except ImportError:  # pragma: no cover
    from qmw_temporal_core16_v1 import (
        DIM,
        as_complex_matrix,
        least_common_multiple,
    )


@dataclass(frozen=True, order=True)
class TemporalRatio:
    """Reduced period ratio p:q with p stroboscopic positions and q windings."""

    p: int
    q: int
    name: str = ""

    def __post_init__(self) -> None:
        p = int(self.p)
        q = int(self.q)
        if p <= 0 or q <= 0:
            raise ValueError("ratio terms must be positive")
        divisor = gcd(p, q)
        object.__setattr__(self, "p", p // divisor)
        object.__setattr__(self, "q", q // divisor)

    @property
    def label(self) -> str:
        return self.name or f"{self.p}:{self.q}"

    @property
    def period_ratio(self) -> Fraction:
        return Fraction(self.p, self.q)

    @property
    def frequency_ratio(self) -> Fraction:
        return Fraction(self.q, self.p)

    @property
    def orbit_length(self) -> int:
        return self.p

    @property
    def winding_number(self) -> int:
        return self.q

    def phase_fraction(self, tick: int) -> Fraction:
        return Fraction((int(tick) * self.q) % self.p, self.p)

    def phase_radians(self, tick: int) -> float:
        return 2.0 * pi * float(self.phase_fraction(tick))

    def position(self, tick: int) -> int:
        return (int(tick) * self.q) % self.p


DEFAULT_RATIOS = (
    TemporalRatio(2, 1, "octave_subharmonic"),
    TemporalRatio(3, 2, "pythagorean_fifth_time"),
    TemporalRatio(4, 3, "pythagorean_fourth_time"),
    TemporalRatio(9, 8, "whole_tone_time"),
)


@dataclass(frozen=True)
class RatioSnapshot:
    label: str
    p: int
    q: int
    position: int
    orbit_length: int
    winding_number: int
    phase_fraction: Fraction
    phase_radians: float
    cosine: float
    sine: float


@dataclass(frozen=True)
class SPQTSnapshot:
    tick: int
    macrocycle_position: int
    macrocycle_length: int
    ratios: tuple[RatioSnapshot, ...]
    protocol_kind: str = "programmed_rational_ratio_clock"


class SubharmonicPythagoreanClock:
    """Exact integer/rational phase clock with no cumulative float drift."""

    protocol_kind = "programmed_rational_ratio_clock"

    def __init__(
        self,
        ratios: Sequence[TemporalRatio] = DEFAULT_RATIOS,
        *,
        tick: int = 0,
        include_basis_clock: int | None = 16,
        include_lfsr_period: int | None = None,
    ):
        if not ratios:
            raise ValueError("at least one temporal ratio is required")
        self.ratios = tuple(ratios)
        self._tick = int(tick)
        periods = [ratio.orbit_length for ratio in self.ratios]
        if include_basis_clock is not None:
            periods.append(int(include_basis_clock))
        if include_lfsr_period is not None:
            periods.append(int(include_lfsr_period))
        self._macrocycle_length = least_common_multiple(periods)

    @property
    def tick(self) -> int:
        return self._tick

    @property
    def macrocycle_length(self) -> int:
        return self._macrocycle_length

    def snapshot(self) -> SPQTSnapshot:
        snapshots: list[RatioSnapshot] = []
        for ratio in self.ratios:
            phase_fraction = ratio.phase_fraction(self._tick)
            phase = 2.0 * pi * float(phase_fraction)
            snapshots.append(
                RatioSnapshot(
                    label=ratio.label,
                    p=ratio.p,
                    q=ratio.q,
                    position=ratio.position(self._tick),
                    orbit_length=ratio.orbit_length,
                    winding_number=ratio.winding_number,
                    phase_fraction=phase_fraction,
                    phase_radians=phase,
                    cosine=float(np.cos(phase)),
                    sine=float(np.sin(phase)),
                )
            )
        return SPQTSnapshot(
            tick=self._tick,
            macrocycle_position=self._tick % self._macrocycle_length,
            macrocycle_length=self._macrocycle_length,
            ratios=tuple(snapshots),
        )

    def advance(self, steps: int = 1) -> SPQTSnapshot:
        self._tick += int(steps)
        return self.snapshot()

    def reset(self, tick: int = 0) -> SPQTSnapshot:
        self._tick = int(tick)
        return self.snapshot()

    def complex_phases(self) -> dict[str, complex]:
        snapshot = self.snapshot()
        return {
            ratio.label: complex(ratio.cosine, ratio.sine)
            for ratio in snapshot.ratios
        }


class PythagoreanHamiltonianCoupler:
    """Convert rational clock phases into an explicitly programmed H(tick)."""

    protocol_kind = "programmed_pythagorean_hamiltonian_drive"

    def __init__(
        self,
        base_hamiltonian: np.ndarray,
        operators: Mapping[str, np.ndarray],
        *,
        amplitudes: Mapping[str, float] | None = None,
        quadrature_operators: Mapping[str, np.ndarray] | None = None,
    ):
        self.base_hamiltonian = as_complex_matrix(base_hamiltonian)
        self.operators = {
            str(name): as_complex_matrix(operator)
            for name, operator in operators.items()
        }
        self.quadrature_operators = {
            str(name): as_complex_matrix(operator)
            for name, operator in (quadrature_operators or {}).items()
        }
        self.amplitudes = {
            str(name): float(value) for name, value in (amplitudes or {}).items()
        }
        for name, operator in {
            **self.operators,
            **self.quadrature_operators,
        }.items():
            if not np.allclose(operator, operator.conj().T, atol=1e-10):
                raise ValueError(f"operator {name!r} must be Hermitian")

    def hamiltonian(self, snapshot: SPQTSnapshot) -> np.ndarray:
        result = np.array(self.base_hamiltonian, copy=True)
        ratios = {ratio.label: ratio for ratio in snapshot.ratios}
        for name, operator in self.operators.items():
            if name not in ratios:
                raise KeyError(f"SPQT snapshot has no ratio named {name!r}")
            amplitude = self.amplitudes.get(name, 1.0)
            result += amplitude * ratios[name].cosine * operator
            quadrature = self.quadrature_operators.get(name)
            if quadrature is not None:
                result += amplitude * ratios[name].sine * quadrature
        return (result + result.conj().T) * 0.5


def combined_return_ticks(*periods: int) -> int:
    return least_common_multiple(periods)


def pythagorean_comma() -> Fraction:
    """Exact ratio (3/2)^12 / 2^7."""

    return Fraction(3, 2) ** 12 / (Fraction(2, 1) ** 7)


def pythagorean_comma_cents() -> float:
    return 1200.0 * log2(float(pythagorean_comma()))


def ratio_table(
    ratios: Sequence[TemporalRatio] = DEFAULT_RATIOS,
) -> tuple[dict[str, object], ...]:
    return tuple(
        {
            "label": ratio.label,
            "period_ratio": f"{ratio.p}/{ratio.q}",
            "frequency_ratio": f"{ratio.q}/{ratio.p}",
            "orbit_length": ratio.orbit_length,
            "winding_number": ratio.winding_number,
        }
        for ratio in ratios
    )
