"""Finite-register Quantum Phase Estimation model for sonification.

For U|u_j> = exp(2*pi*i*phi_j)|u_j>, an m-qubit phase register has
N=2**m outcomes.  This module evaluates the exact Dirichlet-kernel outcome
law, rather than rounding phases by hand.  A superposition of orthogonal
eigenstates is sampled using its Born weights.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Sequence

import numpy as np


@dataclass(frozen=True)
class Eigenstate:
    """One eigencomponent of the trial state."""

    phase: float
    amplitude: complex
    label: str = ""

    @property
    def born_weight(self) -> float:
        return float(abs(self.amplitude) ** 2)


@dataclass(frozen=True)
class QPEShot:
    """One joint measurement of the phase and system registers."""

    eigenstate_index: int
    eigenstate_label: str
    exact_phase: float
    measured_integer: int
    measured_phase: float
    signed_error: float
    register_probabilities: np.ndarray

    @property
    def bits(self) -> int:
        return int(round(math.log2(len(self.register_probabilities))))

    @property
    def bitstring(self) -> str:
        return format(self.measured_integer, f"0{self.bits}b")


def _validate_bits(bits: int) -> None:
    if not isinstance(bits, int) or not 1 <= bits <= 16:
        raise ValueError("bits must be an integer in [1, 16]")


def wrapped_phase_error(measured: float, exact: float) -> float:
    """Return the signed shortest displacement on the unit phase circle."""

    return (float(measured) - float(exact) + 0.5) % 1.0 - 0.5


def phase_distribution(phase: float, bits: int) -> np.ndarray:
    """Exact QPE register probabilities for one eigenphase.

    The stable sinc-ratio form implements
    |N^-1 sum_k exp(2*pi*i*k*(phi-y/N))|^2.
    """

    _validate_bits(bits)
    if not math.isfinite(phase):
        raise ValueError("phase must be finite")
    phase = float(phase) % 1.0
    size = 1 << bits
    outcomes = np.arange(size, dtype=float) / size
    delta = phase - outcomes
    # np.sinc(x) = sin(pi*x)/(pi*x), including the removable x=0 case.
    probabilities = (np.sinc(size * delta) / np.sinc(delta)) ** 2
    probabilities = np.maximum(probabilities, 0.0)
    probabilities /= float(np.sum(probabilities))
    return probabilities


def normalized_weights(eigenstates: Sequence[Eigenstate]) -> np.ndarray:
    if not eigenstates:
        raise ValueError("at least one eigenstate is required")
    weights = np.array([state.born_weight for state in eigenstates], dtype=float)
    if np.any(~np.isfinite(weights)):
        raise ValueError("amplitudes must be finite")
    total = float(np.sum(weights))
    if total <= 0.0:
        raise ValueError("the trial state cannot have zero norm")
    return weights / total


def mixture_distribution(eigenstates: Sequence[Eigenstate], bits: int) -> np.ndarray:
    """Marginal phase-register law for a trial-state superposition."""

    weights = normalized_weights(eigenstates)
    mixture = np.zeros(1 << bits, dtype=float)
    for weight, state in zip(weights, eigenstates):
        mixture += weight * phase_distribution(state.phase, bits)
    mixture /= float(np.sum(mixture))
    return mixture


def conditional_eigenstate_probabilities(
    eigenstates: Sequence[Eigenstate],
    bits: int,
    measured_integer: int,
) -> np.ndarray:
    """Return P(eigenstate j | measured phase-register integer).

    This is the system-register state after measuring only the QPE register.
    When several eigenphases are unresolved at finite precision, it correctly
    retains all compatible eigenmodes instead of forcing a false hard choice.
    """

    _validate_bits(bits)
    size = 1 << bits
    if not isinstance(measured_integer, (int, np.integer)) or not 0 <= measured_integer < size:
        raise ValueError("measured_integer is outside the phase register")
    priors = normalized_weights(eigenstates)
    likelihoods = np.array(
        [phase_distribution(state.phase, bits)[int(measured_integer)] for state in eigenstates],
        dtype=float,
    )
    posterior = priors * likelihoods
    evidence = float(np.sum(posterior))
    if evidence <= 0.0:
        raise ValueError("measured outcome has zero probability")
    return posterior / evidence


def run_qpe(eigenstates: Sequence[Eigenstate], bits: int, rng: object) -> QPEShot:
    """Sample one physically valid joint QPE measurement."""

    _validate_bits(bits)
    weights = normalized_weights(eigenstates)
    index = int(rng.choice(len(eigenstates), p=weights))
    state = eigenstates[index]
    probabilities = phase_distribution(state.phase, bits)
    measured_integer = int(rng.choice(len(probabilities), p=probabilities))
    measured_phase = measured_integer / len(probabilities)
    exact_phase = float(state.phase) % 1.0
    return QPEShot(
        eigenstate_index=index,
        eigenstate_label=state.label or f"u{index}",
        exact_phase=exact_phase,
        measured_integer=measured_integer,
        measured_phase=measured_phase,
        signed_error=wrapped_phase_error(measured_phase, exact_phase),
        register_probabilities=probabilities,
    )


def phase_to_frequency(
    phase: float,
    *,
    root_hz: float = 55.0,
    span_octaves: float = 4.0,
) -> float:
    """Map the unit phase circle exponentially onto an audible pitch span."""

    if root_hz <= 0.0 or span_octaves <= 0.0:
        raise ValueError("root_hz and span_octaves must be positive")
    return float(root_hz * 2.0 ** (span_octaves * (float(phase) % 1.0)))
