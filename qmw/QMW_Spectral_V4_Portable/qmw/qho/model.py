"""Canonical finite-dimensional quantum harmonic oscillator model."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class OscillatorSpec:
    """Backend-independent definition of one truncated bosonic mode.

    ``dimension`` is a numerical cutoff, not a claim that the oscillator is a
    collection of qubits.  Backends may encode this Hilbert space differently.
    """

    dimension: int = 16
    omega: float = 1.0
    hbar: float = 1.0

    def __post_init__(self) -> None:
        if self.dimension < 2:
            raise ValueError("dimension must be at least 2")
        if not np.isfinite(self.omega) or self.omega <= 0.0:
            raise ValueError("omega must be finite and positive")
        if not np.isfinite(self.hbar) or self.hbar <= 0.0:
            raise ValueError("hbar must be finite and positive")


@dataclass(frozen=True)
class OscillatorOperators:
    annihilation: np.ndarray
    creation: np.ndarray
    number: np.ndarray
    hamiltonian: np.ndarray
    x: np.ndarray
    p: np.ndarray
    identity: np.ndarray


@dataclass(frozen=True)
class OscillatorModel:
    """A spec paired with its canonical dense operators."""

    spec: OscillatorSpec
    operators: OscillatorOperators

    @classmethod
    def from_spec(cls, spec: OscillatorSpec | None = None) -> "OscillatorModel":
        from .operators import oscillator_operators

        resolved = spec or OscillatorSpec()
        return cls(spec=resolved, operators=oscillator_operators(resolved))


__all__ = ["OscillatorModel", "OscillatorOperators", "OscillatorSpec"]
