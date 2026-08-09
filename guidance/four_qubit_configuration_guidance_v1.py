"""Discrete Bohm--Bell guidance on a finite computational basis.

The authoritative orientation used here is::

    J[m, n] = (2 / hbar) Im(H[m, n] rho[n, m])

so a positive ``J[m, n]`` is probability current from occupied
configuration ``n`` to destination ``m``.  The Bell jump rate is

    sigma[m, n] = max(J[m, n], 0) / rho[n, n].

The class intentionally contains no renderer noise, branch-entropy force, or
continuous interpolation between bit strings.  Those are presentation-layer
concerns and must not alter the beable dynamics.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np


def _validate_square(matrix: np.ndarray, name: str) -> np.ndarray:
    value = np.asarray(matrix, dtype=np.complex128)
    if value.ndim != 2 or value.shape[0] != value.shape[1]:
        raise ValueError(f"{name} must be a square matrix")
    return value


def current_matrix(
    hamiltonian: np.ndarray,
    rho: np.ndarray,
    *,
    hbar: float = 1.0,
) -> np.ndarray:
    """Return ``J[m, n]``, positive when probability flows ``n -> m``."""
    h = _validate_square(hamiltonian, "hamiltonian")
    state = _validate_square(rho, "rho")
    if h.shape != state.shape:
        raise ValueError("hamiltonian and rho must have the same shape")
    if hbar <= 0.0:
        raise ValueError("hbar must be positive")

    currents = (2.0 / hbar) * np.imag(h * state.T)
    np.fill_diagonal(currents, 0.0)
    return np.asarray(currents, dtype=np.float64)


def transition_rates(
    hamiltonian: np.ndarray,
    rho: np.ndarray,
    *,
    hbar: float = 1.0,
    population_floor: float = 1e-15,
) -> np.ndarray:
    """Return Bell rates ``rates[m, n]`` for jumps ``n -> m``."""
    state = _validate_square(rho, "rho")
    populations = np.real(np.diag(state))
    rates = np.zeros(state.shape, dtype=np.float64)
    populated = populations > population_floor
    currents = current_matrix(hamiltonian, state, hbar=hbar)
    rates[:, populated] = np.maximum(currents[:, populated], 0.0) / populations[populated]
    np.fill_diagonal(rates, 0.0)
    return rates


def sample_configurations(
    rho: np.ndarray,
    size: int,
    rng: np.random.Generator,
) -> np.ndarray:
    """Sample computational-basis configurations from ``diag(rho)``."""
    if size < 1:
        raise ValueError("size must be positive")
    state = _validate_square(rho, "rho")
    probabilities = np.maximum(np.real(np.diag(state)), 0.0)
    total = float(np.sum(probabilities))
    if total <= 0.0:
        raise ValueError("rho has no positive diagonal population")
    probabilities /= total
    return rng.choice(state.shape[0], size=size, p=probabilities).astype(np.int64)


@dataclass
class ConfigurationEnsemble:
    """An ensemble of actual configurations sharing one density operator."""

    configurations: np.ndarray
    rng: np.random.Generator
    beable_basis: str = "computational_z"

    @classmethod
    def from_rho(
        cls,
        rho: np.ndarray,
        size: int,
        *,
        seed: Optional[int] = None,
    ) -> "ConfigurationEnsemble":
        rng = np.random.default_rng(seed)
        return cls(sample_configurations(rho, size, rng), rng)

    @property
    def size(self) -> int:
        return int(self.configurations.size)

    def distribution(self, dimension: Optional[int] = None) -> np.ndarray:
        if dimension is None:
            dimension = int(np.max(self.configurations)) + 1
        return np.bincount(self.configurations, minlength=dimension).astype(float) / self.size

    def step(self, hamiltonian: np.ndarray, rho: np.ndarray, dt: float) -> None:
        """Advance by one rate-frozen microstep.

        At most one jump is made per member.  The exact probability of leaving
        a node under frozen rates is ``1-exp(-lambda*dt)``; destination weights
        are proportional to the outgoing rates.  Callers should use small
        microsteps while updating ``rho`` between calls.
        """
        if dt < 0.0:
            raise ValueError("dt must be non-negative")
        if dt == 0.0:
            return

        rates = transition_rates(hamiltonian, rho)
        for source in np.unique(self.configurations):
            member_indices = np.flatnonzero(self.configurations == source)
            outgoing = rates[:, source]
            total_rate = float(np.sum(outgoing))
            if total_rate <= 0.0:
                continue
            jump_probability = -np.expm1(-total_rate * dt)
            jump_mask = self.rng.random(member_indices.size) < jump_probability
            jump_indices = member_indices[jump_mask]
            if jump_indices.size:
                destinations = self.rng.choice(
                    outgoing.size,
                    size=jump_indices.size,
                    p=outgoing / total_rate,
                )
                self.configurations[jump_indices] = destinations


def unitary_step(hamiltonian: np.ndarray, dt: float) -> np.ndarray:
    """Compute ``exp(-i H dt)`` for a Hermitian finite-dimensional H."""
    h = _validate_square(hamiltonian, "hamiltonian")
    eigenvalues, eigenvectors = np.linalg.eigh(h)
    return (eigenvectors * np.exp(-1j * eigenvalues * dt)) @ eigenvectors.conj().T


def evolve_ensemble(
    rho: np.ndarray,
    hamiltonian: np.ndarray,
    ensemble: ConfigurationEnsemble,
    *,
    duration: float = 1.0,
    microsteps: int = 128,
) -> np.ndarray:
    """Evolve density operator and guided configurations together.

    Guidance rates are evaluated at the midpoint density for each exact
    unitary microstep.  This reduces discretization bias while preserving the
    explicit gate duration required by the model.
    """
    if duration < 0.0 or microsteps < 1:
        raise ValueError("duration must be non-negative and microsteps positive")
    state = _validate_square(rho, "rho").copy()
    h = _validate_square(hamiltonian, "hamiltonian")
    dt = duration / microsteps
    half_u = unitary_step(h, dt / 2.0)

    for _ in range(microsteps):
        midpoint = half_u @ state @ half_u.conj().T
        ensemble.step(h, midpoint, dt)
        state = half_u @ midpoint @ half_u.conj().T
    return state
