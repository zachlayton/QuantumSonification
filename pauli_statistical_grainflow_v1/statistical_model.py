"""Combinatorial and energy-shell model for the Grainflow scheduler."""

from __future__ import annotations

from enum import Enum
import math
import random


MAGNETIC_FACTORS = (-2.0, 0.0, -1.0, 1.0, 0.0, 2.0)


class StatisticsClass(str, Enum):
    FERMION = "fermion"
    BOSON = "boson"
    CLASSICAL = "classical"


def mode_energies(field: float) -> tuple[float, ...]:
    return tuple(field * factor for factor in MAGNETIC_FACTORS)


def accessible_modes(field: float, center: float, width: float) -> tuple[int, ...]:
    """Return mode indices inside a closed energy shell.

    If the requested window misses all modes, the closest mode is retained so
    the renderer has a defined limiting state.
    """

    energies = mode_energies(field)
    half_width = max(0.0, width) / 2.0
    selected = tuple(i for i, energy in enumerate(energies) if abs(energy - center) <= half_width)
    if selected:
        return selected
    closest = min(range(len(energies)), key=lambda i: (abs(energies[i] - center), i))
    return (closest,)


def microstate_count(statistics: StatisticsClass | str, modes: int, particles: int) -> int:
    statistics = StatisticsClass(statistics)
    if modes < 1 or particles < 0:
        return 0
    if statistics is StatisticsClass.FERMION:
        return math.comb(modes, particles) if particles <= modes else 0
    if statistics is StatisticsClass.BOSON:
        return math.comb(modes + particles - 1, particles)
    return modes**particles


def dimensionless_entropy(statistics: StatisticsClass | str, modes: int, particles: int) -> float:
    count = microstate_count(statistics, modes, particles)
    return math.log(count) if count > 0 else float("-inf")


def sample_configuration(
    statistics: StatisticsClass | str,
    accessible: tuple[int, ...],
    particles: int,
    *,
    rng: random.Random,
) -> tuple[int, ...]:
    """Return canonical occupation numbers for the six addressed modes."""

    statistics = StatisticsClass(statistics)
    occupation = [0] * len(MAGNETIC_FACTORS)
    if particles <= 0 or not accessible:
        return tuple(occupation)
    if statistics is StatisticsClass.FERMION:
        for mode in rng.sample(list(accessible), min(particles, len(accessible))):
            occupation[mode] = 1
        return tuple(occupation)
    for _ in range(particles):
        occupation[rng.choice(accessible)] += 1
    return tuple(occupation)


def normalized_occupancy(occupation: tuple[int, ...]) -> tuple[float, ...]:
    peak = max(occupation, default=0)
    if peak <= 0:
        return tuple(0.0 for _ in occupation)
    return tuple(value / peak for value in occupation)
