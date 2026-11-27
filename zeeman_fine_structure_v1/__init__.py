"""Zeeman field and Sommerfeld-style fine structure for the 4-qubit QMW engine."""

from .engine_bridge import ZeemanFineLayer, attach, detach
from .model import (
    PRESETS,
    Line,
    ZeemanFineConfig,
    ZeemanFrame,
    directivity_ambisonics,
    dipole_pattern,
    frame,
    hamiltonian,
    hanle_polarization,
    merge_lines,
    quantum_beats,
    sweep,
)

__all__ = [
    "PRESETS", "Line", "ZeemanFineConfig", "ZeemanFrame", "ZeemanFineLayer",
    "attach", "detach", "directivity_ambisonics", "dipole_pattern", "frame",
    "hamiltonian", "hanle_polarization", "merge_lines", "quantum_beats", "sweep",
]
