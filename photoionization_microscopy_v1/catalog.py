"""Hydrogen Stark resonance catalog transcribed from Deng et al. Table I."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final


@dataclass(frozen=True)
class StarkResonance:
    n1_tilde: int
    n2_tilde: int
    m: int
    energy_cm_inverse: float
    family: str

    @property
    def label(self) -> str:
        return f"({self.n1_tilde},{self.n2_tilde},{self.m})"


RESONANCE_CATALOG: Final[tuple[StarkResonance, ...]] = (
    StarkResonance(0, 29, 0, -172.810, "red"),
    StarkResonance(1, 28, 0, -169.617, "red"),
    StarkResonance(2, 27, 0, -166.426, "red"),
    StarkResonance(3, 26, 0, -163.240, "red"),
    StarkResonance(4, 24, 0, -164.623, "red"),
    StarkResonance(3, 25, 0, -167.645, "red"),
    StarkResonance(4, 23, 0, -170.655, "red"),
    StarkResonance(2, 26, 0, -170.662, "red"),
    StarkResonance(3, 24, 0, -173.554, "red"),
    StarkResonance(1, 27, 0, -173.676, "red"),
    StarkResonance(23, 0, 0, -162.791, "blue"),
    StarkResonance(22, 1, 0, -165.312, "blue"),
    StarkResonance(21, 2, 0, -167.831, "blue"),
    StarkResonance(20, 3, 0, -170.348, "blue"),
)


def resonance_by_label(label: str) -> StarkResonance:
    for resonance in RESONANCE_CATALOG:
        if resonance.label == label:
            return resonance
    raise KeyError(f"Unknown Deng et al. Table I resonance: {label}")
