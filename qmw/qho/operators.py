"""Dense operators for a truncated Fock basis."""

from __future__ import annotations

import numpy as np

from .model import OscillatorOperators, OscillatorSpec


def annihilation_operator(dimension: int) -> np.ndarray:
    if dimension < 2:
        raise ValueError("dimension must be at least 2")
    operator = np.zeros((dimension, dimension), dtype=np.complex128)
    levels = np.arange(1, dimension)
    operator[levels - 1, levels] = np.sqrt(levels)
    return operator


def oscillator_operators(spec: OscillatorSpec) -> OscillatorOperators:
    a = annihilation_operator(spec.dimension)
    adag = a.conj().T
    number = adag @ a
    identity = np.eye(spec.dimension, dtype=np.complex128)
    hamiltonian = spec.hbar * spec.omega * (number + 0.5 * identity)
    x = (a + adag) / np.sqrt(2.0)
    p = (a - adag) / (1j * np.sqrt(2.0))
    return OscillatorOperators(
        annihilation=a,
        creation=adag,
        number=number,
        hamiltonian=hamiltonian,
        x=x,
        p=p,
        identity=identity,
    )


__all__ = ["annihilation_operator", "oscillator_operators"]
