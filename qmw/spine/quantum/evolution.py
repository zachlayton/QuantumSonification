"""Von Neumann evolution: rho_dot = -i[H, rho] (hbar = 1), plus its integrators.

The unitary propagator rho_{n+1} = U rho_n U^dagger, U = expm(-i H dt), is the
canonical reference integrator: it preserves trace, hermiticity, and
positivity to numerical precision by construction, which is why it is used
even where a cheaper first-order step would do.
"""
from __future__ import annotations

import numpy as np
from scipy.linalg import expm

from qmw.spine.quantum.hamiltonian import Hamiltonian


def commutator(A: np.ndarray, B: np.ndarray) -> np.ndarray:
    return A @ B - B @ A


def unitary_velocity(H: np.ndarray, rho: np.ndarray) -> np.ndarray:
    """rho_dot_unitary = -i[H, rho], hbar = 1."""
    return -1j * commutator(H, rho)


def commutator_norm(H: np.ndarray, rho: np.ndarray) -> float:
    """||[H, rho]||_F -- constant over a closed, time-independent trajectory."""
    return float(np.linalg.norm(commutator(H, rho)))


def propagator(H: np.ndarray, dt: float) -> np.ndarray:
    """U = exp(-i H dt) for a time-independent generator over one short step."""
    return expm(-1j * H * dt)


def evolve_unitary_step(rho: np.ndarray, H: np.ndarray, dt: float) -> np.ndarray:
    """rho_{n+1} = U rho_n U^dagger."""
    U = propagator(H, dt)
    return U @ rho @ U.conj().T


def evolve_unitary_trajectory(
    rho0: np.ndarray,
    hamiltonian: Hamiltonian,
    dt: float,
    steps: int,
    t0: float = 0.0,
) -> list[tuple[float, np.ndarray]]:
    """[(t0, rho0), (t0+dt, rho1), ...] via the unitary propagator at each step.

    For a time-dependent H, U_n = expm(-i H(t_n) dt) is recomputed every step
    (valid for dt small enough that H is approximately constant over the step).
    """
    trajectory = [(t0, rho0)]
    rho = rho0
    t = t0
    for _ in range(steps):
        H = hamiltonian.matrix(t)
        rho = evolve_unitary_step(rho, H, dt)
        t += dt
        trajectory.append((t, rho))
    return trajectory
