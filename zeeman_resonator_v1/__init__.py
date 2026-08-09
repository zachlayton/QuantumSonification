"""QMW Zeeman Resonator: physically structured audible Zeeman splitting."""

from .zeeman_model import (
    BOHR_MAGNETON_OVER_H_HZ_PER_T,
    PRESETS,
    RingComponent,
    ZeemanPreset,
    lande_g,
)

__all__ = [
    "BOHR_MAGNETON_OVER_H_HZ_PER_T",
    "PRESETS",
    "RingComponent",
    "ZeemanPreset",
    "lande_g",
]
