"""Combination-Product Sets as fixed-excitation quantum geometry.

Wilson's ``k)n`` CPS contains every product of ``k`` distinct members of an
``n``-factor master set.  The same combinations label the computational basis
states of ``n`` qubits having Hamming weight ``k``.  This module preserves that
identity instead of flattening the CPS onto an arbitrary chromatic scale.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import combinations
from math import comb, isfinite, log2, prod
from typing import Iterable, Sequence

from .perception import harmonic_distance, prime_coordinates


def _fold_fraction(value: Fraction, period: Fraction) -> Fraction:
    if value <= 0 or period <= 1:
        raise ValueError("ratio must be positive and period must be greater than one")
    while value < 1:
        value *= period
    while value >= period:
        value /= period
    return value


@dataclass(frozen=True)
class CPSTone:
    """One vertex of a ``k)n`` Combination-Product Set."""

    index: int
    factor_indices: tuple[int, ...]
    factors: tuple[int, ...]
    bitmask: int
    product: int
    ratio_numerator: int
    ratio_denominator: int
    cents: float
    complement_index: int | None

    @property
    def ratio(self) -> float:
        return self.ratio_numerator / self.ratio_denominator

    @property
    def pitch_class_coordinates(self) -> tuple[tuple[int, int], ...]:
        return prime_coordinates(
            Fraction(self.ratio_numerator, self.ratio_denominator),
            collapse_octaves=True,
        )


@dataclass(frozen=True)
class CPSEdge:
    """A factor-exchange edge with independent combinatorial/perceptual data."""

    source: int
    target: int
    interval_numerator: int
    interval_denominator: int
    harmonic_distance: float

    @property
    def interval(self) -> float:
        return self.interval_numerator / self.interval_denominator


@dataclass(frozen=True)
class QuantumCPSTone:
    """A CPS vertex carrying amplitude data from an ``n``-qubit state."""

    tone: CPSTone
    amplitude_real: float
    amplitude_imag: float
    probability: float
    conditional_probability: float
    relative_phase: float


@dataclass(frozen=True)
class CPSProjection:
    """Projection of a full register onto one fixed-Hamming-weight CPS shell."""

    grade: int
    shell_probability: float
    tones: tuple[QuantumCPSTone, ...]


@dataclass(frozen=True)
class PascalCPSShell:
    """One Pascal-row entry interpreted as a CPS/qubit shell."""

    qubit_count: int
    grade: int
    dimension: int
    complement_grade: int

    @property
    def is_self_complementary(self) -> bool:
        return self.grade == self.complement_grade


def pascal_cps_row(
    qubit_count: int,
    *,
    include_trivial: bool = True,
) -> tuple[PascalCPSShell, ...]:
    """Return Pascal row ``n`` as the complete registry of ``k)n`` shells.

    Grade ``k`` has dimension ``C(n, k)`` and bitwise complement maps it to
    grade ``n-k``. This lets the system select Hexanies, Dekanies, Eikosanies,
    or cross-grade fields from one common combinatorial address space.
    """
    qubit_count = int(qubit_count)
    if qubit_count < 1:
        raise ValueError("qubit_count must be positive")
    start = 0 if include_trivial else 1
    stop = qubit_count + 1 if include_trivial else qubit_count
    return tuple(
        PascalCPSShell(
            qubit_count=qubit_count,
            grade=grade,
            dimension=comb(qubit_count, grade),
            complement_grade=qubit_count - grade,
        )
        for grade in range(start, stop)
    )


class CombinationProductSet:
    """A centreless Wilson CPS with explicit combinatorial and pitch geometry.

    ``anchor`` only chooses a frequency representative for audition.  It does
    not make that tone a privileged graph centre: the CPS vertices and edges
    remain transitive under permutations of the master-set positions.
    """

    def __init__(
        self,
        factors: Sequence[int],
        grade: int,
        *,
        period: int | Fraction = 2,
        anchor: int | Sequence[int] = 0,
    ) -> None:
        normalized = tuple(int(value) for value in factors)
        if len(normalized) < 2 or any(value <= 0 for value in normalized):
            raise ValueError("factors must contain at least two positive integers")
        if len(set(normalized)) != len(normalized):
            raise ValueError("factor positions must have distinct values")
        if not 1 <= int(grade) < len(normalized):
            raise ValueError("grade must lie between 1 and n - 1")
        self.factors = normalized
        self.grade = int(grade)
        self.period = Fraction(period)
        if self.period <= 1:
            raise ValueError("period must be greater than one")

        subsets = tuple(combinations(range(len(self.factors)), self.grade))
        if isinstance(anchor, int):
            anchor_index = int(anchor)
        else:
            requested = tuple(sorted(int(value) for value in anchor))
            try:
                anchor_index = subsets.index(requested)
            except ValueError as exc:
                raise ValueError("anchor must identify one CPS factor subset") from exc
        if not 0 <= anchor_index < len(subsets):
            raise ValueError("anchor index is outside the CPS")

        products = tuple(prod(self.factors[i] for i in subset) for subset in subsets)
        anchor_product = products[anchor_index]
        subset_to_index = {subset: index for index, subset in enumerate(subsets)}
        universe = frozenset(range(len(self.factors)))
        tones: list[CPSTone] = []
        for index, (subset, product_value) in enumerate(zip(subsets, products)):
            ratio = _fold_fraction(Fraction(product_value, anchor_product), self.period)
            complement = tuple(sorted(universe.difference(subset)))
            complement_index = subset_to_index.get(complement)
            tones.append(
                CPSTone(
                    index=index,
                    factor_indices=subset,
                    factors=tuple(self.factors[i] for i in subset),
                    bitmask=sum(1 << i for i in subset),
                    product=product_value,
                    ratio_numerator=ratio.numerator,
                    ratio_denominator=ratio.denominator,
                    cents=1200.0 * log2(float(ratio)),
                    complement_index=complement_index,
                )
            )
        self.tones = tuple(tones)
        self._bitmask_to_tone = {tone.bitmask: tone for tone in self.tones}

    @property
    def name(self) -> str:
        return f"{self.grade}){len(self.factors)} " + "-".join(map(str, self.factors))

    @property
    def dimension(self) -> int:
        return comb(len(self.factors), self.grade)

    def edges(self) -> tuple[tuple[int, int], ...]:
        """Return the Johnson-graph edges (exchange exactly one factor)."""
        result = []
        for left, right in combinations(self.tones, 2):
            if len(set(left.factor_indices).symmetric_difference(right.factor_indices)) == 2:
                result.append((left.index, right.index))
        return tuple(result)

    def perceptual_edges(self) -> tuple[CPSEdge, ...]:
        """Decorate Johnson edges with Tenney harmonic distance."""
        result = []
        for source, target in self.edges():
            interval = self.interval(source, target)
            result.append(
                CPSEdge(
                    source=source,
                    target=target,
                    interval_numerator=interval.numerator,
                    interval_denominator=interval.denominator,
                    harmonic_distance=harmonic_distance(interval),
                )
            )
        return tuple(result)

    def interval(self, source: int, target: int) -> Fraction:
        """Return the octave/period-folded product ratio along a directed edge."""
        left = self.tones[int(source)]
        right = self.tones[int(target)]
        return _fold_fraction(Fraction(right.product, left.product), self.period)

    def neighbors(self, index: int) -> tuple[int, ...]:
        selected = int(index)
        return tuple(
            right if left == selected else left
            for left, right in self.edges()
            if left == selected or right == selected
        )

    def project_state(self, amplitudes: Iterable[complex]) -> CPSProjection:
        """Project a full ``2**n`` statevector onto this CPS shell.

        ``probability`` is absolute register probability.  The conditional
        value is normalized within the shell, allowing a CPS to be auditioned
        without hiding leakage into other Hamming weights.
        """
        values = tuple(complex(value) for value in amplitudes)
        expected = 1 << len(self.factors)
        if len(values) != expected:
            raise ValueError(f"statevector must contain {expected} amplitudes")
        if any(not (isfinite(value.real) and isfinite(value.imag)) for value in values):
            raise ValueError("statevector amplitudes must be finite")
        norm = sum(abs(value) ** 2 for value in values)
        if abs(norm - 1.0) > 1e-8:
            raise ValueError("statevector must have unit norm")

        selected = tuple((tone, values[tone.bitmask]) for tone in self.tones)
        shell_probability = float(sum(abs(value) ** 2 for _, value in selected))
        reference = max(selected, key=lambda item: abs(item[1]))[1]
        reference_phase = 0.0 if abs(reference) < 1e-15 else _phase(reference)
        projected = tuple(
            QuantumCPSTone(
                tone=tone,
                amplitude_real=float(value.real),
                amplitude_imag=float(value.imag),
                probability=float(abs(value) ** 2),
                conditional_probability=(
                    float(abs(value) ** 2 / shell_probability)
                    if shell_probability > 1e-15
                    else 0.0
                ),
                relative_phase=_wrap_phase(_phase(value) - reference_phase)
                if abs(value) > 1e-15
                else 0.0,
            )
            for tone, value in selected
        )
        return CPSProjection(
            grade=self.grade,
            shell_probability=shell_probability,
            tones=projected,
        )


def _phase(value: complex) -> float:
    from math import atan2

    return atan2(value.imag, value.real)


def _wrap_phase(value: float) -> float:
    from math import pi

    return (value + pi) % (2.0 * pi) - pi
