"""Backend-independent model for two coupled truncated bosonic modes."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .model import OscillatorSpec
from .operators import oscillator_operators


@dataclass(frozen=True)
class CoupledOscillatorSpec:
    """Definition of two modes coupled by excitation exchange.

    Each dimension is an independent Fock cutoff. The composite basis ordering
    is ``|n_a, n_b>`` with flat index ``n_a * dimension_b + n_b``.
    """

    dimension_a: int = 4
    dimension_b: int = 4
    omega_a: float = 1.0
    omega_b: float = 1.0
    coupling: float = 0.1
    hbar: float = 1.0

    def __post_init__(self) -> None:
        if self.dimension_a < 2 or self.dimension_b < 2:
            raise ValueError("each mode dimension must be at least 2")
        frequencies = (self.omega_a, self.omega_b, self.hbar)
        if not np.isfinite(frequencies).all() or any(x <= 0.0 for x in frequencies):
            raise ValueError("frequencies and hbar must be finite and positive")
        if not np.isfinite(self.coupling):
            raise ValueError("coupling must be finite")

    @property
    def total_dimension(self) -> int:
        return self.dimension_a * self.dimension_b

    def basis_index(self, n_a: int, n_b: int) -> int:
        if not 0 <= n_a < self.dimension_a:
            raise ValueError("n_a lies outside mode-a cutoff")
        if not 0 <= n_b < self.dimension_b:
            raise ValueError("n_b lies outside mode-b cutoff")
        return n_a * self.dimension_b + n_b


@dataclass(frozen=True)
class CoupledOscillatorOperators:
    annihilation_a: np.ndarray
    creation_a: np.ndarray
    annihilation_b: np.ndarray
    creation_b: np.ndarray
    number_a: np.ndarray
    number_b: np.ndarray
    total_number: np.ndarray
    x_a: np.ndarray
    p_a: np.ndarray
    x_b: np.ndarray
    p_b: np.ndarray
    free_hamiltonian: np.ndarray
    interaction_hamiltonian: np.ndarray
    hamiltonian: np.ndarray
    exchange: np.ndarray
    identity: np.ndarray


@dataclass(frozen=True)
class CoupledOscillatorModel:
    spec: CoupledOscillatorSpec
    operators: CoupledOscillatorOperators

    @classmethod
    def from_spec(
        cls, spec: CoupledOscillatorSpec | None = None
    ) -> "CoupledOscillatorModel":
        resolved = spec or CoupledOscillatorSpec()
        ops_a = oscillator_operators(
            OscillatorSpec(
                dimension=resolved.dimension_a,
                omega=resolved.omega_a,
                hbar=resolved.hbar,
            )
        )
        ops_b = oscillator_operators(
            OscillatorSpec(
                dimension=resolved.dimension_b,
                omega=resolved.omega_b,
                hbar=resolved.hbar,
            )
        )
        identity_a = ops_a.identity
        identity_b = ops_b.identity
        identity = np.kron(identity_a, identity_b)
        annihilation_a = np.kron(ops_a.annihilation, identity_b)
        annihilation_b = np.kron(identity_a, ops_b.annihilation)
        creation_a = annihilation_a.conj().T
        creation_b = annihilation_b.conj().T
        number_a = creation_a @ annihilation_a
        number_b = creation_b @ annihilation_b
        exchange = creation_a @ annihilation_b + annihilation_a @ creation_b
        free_hamiltonian = np.kron(ops_a.hamiltonian, identity_b) + np.kron(
            identity_a, ops_b.hamiltonian
        )
        interaction_hamiltonian = resolved.hbar * resolved.coupling * exchange
        operators = CoupledOscillatorOperators(
            annihilation_a=annihilation_a,
            creation_a=creation_a,
            annihilation_b=annihilation_b,
            creation_b=creation_b,
            number_a=number_a,
            number_b=number_b,
            total_number=number_a + number_b,
            x_a=np.kron(ops_a.x, identity_b),
            p_a=np.kron(ops_a.p, identity_b),
            x_b=np.kron(identity_a, ops_b.x),
            p_b=np.kron(identity_a, ops_b.p),
            free_hamiltonian=free_hamiltonian,
            interaction_hamiltonian=interaction_hamiltonian,
            hamiltonian=free_hamiltonian + interaction_hamiltonian,
            exchange=exchange,
            identity=identity,
        )
        return cls(spec=resolved, operators=operators)


__all__ = [
    "CoupledOscillatorModel",
    "CoupledOscillatorOperators",
    "CoupledOscillatorSpec",
]
