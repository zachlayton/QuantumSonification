from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class QuantumDescriptor:
    """Canonical compact descriptor for QMW quantum sources."""

    energy: float
    phase: float
    probability: float
    coherence: float
    entanglement: float
    spin: float
    topology: float
    curvature: float