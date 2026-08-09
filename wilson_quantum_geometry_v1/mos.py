"""Moments of Symmetry and Wilson Scale-Tree coordinates."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from math import isfinite, log


@dataclass(frozen=True)
class ScaleTreePosition:
    """A reduced fraction and its ancestry in the Stern-Brocot/Scale Tree."""

    fraction: Fraction
    path: str
    ancestors: tuple[Fraction, ...]
    lower_parent: Fraction
    upper_parent: Fraction

    @property
    def generator_coordinates(self) -> tuple[int, int]:
        return self.lower_parent.numerator, self.upper_parent.numerator

    @property
    def period_coordinates(self) -> tuple[int, int]:
        return self.lower_parent.denominator, self.upper_parent.denominator


@dataclass(frozen=True)
class MOSScale:
    """A finite generated scale, classified by the number of step sizes."""

    generator_ratio: float
    period: float
    size: int
    generator_fraction: float
    generator_degree: int
    positions: tuple[float, ...]
    ratios: tuple[float, ...]
    steps: tuple[float, ...]
    step_sizes: tuple[float, ...]

    @property
    def is_moment_of_symmetry(self) -> bool:
        return len(self.step_sizes) == 2

    @property
    def scale_type(self) -> Fraction:
        return Fraction(self.generator_degree, self.size)


def scale_tree_position(numerator: int, denominator: int) -> ScaleTreePosition:
    """Locate a positive reduced fraction by mediants.

    The final bounding fractions are its Scale-Tree parents.  Their numerators
    and denominators are Wilson's generalized-keyboard coordinates for the
    generator and period respectively.
    """
    target = Fraction(int(numerator), int(denominator))
    if not 0 < target < 1:
        raise ValueError("keyboard Scale-Tree fraction must lie between 0 and 1")
    left = Fraction(0, 1)
    right_num, right_den = 1, 0
    path: list[str] = []
    ancestors: list[Fraction] = []
    while True:
        mediant = Fraction(left.numerator + right_num, left.denominator + right_den)
        ancestors.append(mediant)
        if mediant == target:
            return ScaleTreePosition(
                fraction=target,
                path="".join(path),
                ancestors=tuple(ancestors),
                lower_parent=left,
                upper_parent=Fraction(right_num, right_den),
            )
        if target < mediant:
            path.append("L")
            right_num, right_den = mediant.numerator, mediant.denominator
        else:
            path.append("R")
            left = mediant


def make_mos(
    generator_ratio: float,
    size: int,
    *,
    period: float = 2.0,
    tolerance: float = 1e-10,
) -> MOSScale:
    """Generate and classify a linear scale inside one period.

    Positions use logarithmic period coordinates.  A genuine MOS has exactly
    two distinct circular step sizes (within ``tolerance``).
    """
    generator_ratio = float(generator_ratio)
    period = float(period)
    size = int(size)
    if not isfinite(generator_ratio) or generator_ratio <= 0:
        raise ValueError("generator_ratio must be finite and positive")
    if not isfinite(period) or period <= 1:
        raise ValueError("period must be finite and greater than one")
    if size < 2:
        raise ValueError("size must be at least two")
    generator_fraction = log(generator_ratio) / log(period)
    generator_fraction %= 1.0
    if generator_fraction < tolerance or 1.0 - generator_fraction < tolerance:
        raise ValueError("generator cannot be equivalent to the period or unison")
    positions = tuple(sorted((index * generator_fraction) % 1.0 for index in range(size)))
    steps = tuple(
        positions[index + 1] - positions[index]
        for index in range(size - 1)
    ) + (1.0 - positions[-1] + positions[0],)
    distinct: list[float] = []
    for step in sorted(steps):
        if not distinct or abs(step - distinct[-1]) > tolerance:
            distinct.append(step)
    generator_degree = sum(position < generator_fraction - tolerance for position in positions)
    return MOSScale(
        generator_ratio=generator_ratio,
        period=period,
        size=size,
        generator_fraction=generator_fraction,
        generator_degree=generator_degree,
        positions=positions,
        ratios=tuple(period**position for position in positions),
        steps=steps,
        step_sizes=tuple(distinct),
    )
