"""Native frame contracts for quantum engines beyond scalar psi(x)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

import numpy as np


Array = np.ndarray


@dataclass(frozen=True)
class SpinorFrame:
    spinor: Array
    density_matrix: Array
    probabilities_z: tuple[float, float]
    bloch_vector: tuple[float, float, float]
    magnetic_field: tuple[float, float, float]
    larmor_vector: tuple[float, float, float]
    larmor_angular_frequency: float
    energy_expectation: float
    relative_phase: float
    time: float
    norm: float
    source: str
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class JointWavefunctionFrame:
    psi: Array
    probability: Array
    coordinates: tuple[Array, Array]
    marginal_a: Array
    marginal_b: Array
    exchange_symmetry: str
    swap_expectation: float
    coincidence_probability: float
    one_body_purity: float
    time: float
    norm: float
    source: str
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class EntangledQubitFrame:
    state: Array
    density_matrix: Array
    reduced_a: Array
    reduced_b: Array
    bloch_a: tuple[float, float, float]
    bloch_b: tuple[float, float, float]
    conditional_a_given_b_x_plus: tuple[float, float, float]
    conditional_b_given_a_x_plus: tuple[float, float, float]
    correlation_tensor: Array
    concurrence: float
    chsh_maximum: float
    time: float
    norm: float
    source: str
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class RelativisticLevelFrame:
    amplitudes: Array
    probabilities: Array
    quantum_numbers: tuple[tuple[int, int, float], ...]
    total_energies: Array
    binding_energies: Array
    energy_expectation: float
    fine_structure_splitting: float
    time: float
    norm: float
    source: str
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class DiracSpinorFieldFrame:
    spinor: Array
    probability: Array
    probability_current: Array
    coordinates: Array
    potential: Array
    energy_expectation: float
    left_probability: float
    right_probability: float
    time: float
    norm: float
    source: str
    metadata: Mapping[str, Any] = field(default_factory=dict)


__all__ = [
    "DiracSpinorFieldFrame",
    "EntangledQubitFrame",
    "JointWavefunctionFrame",
    "RelativisticLevelFrame",
    "SpinorFrame",
]
