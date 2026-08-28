"""Basis-population current: the exact continuity equation latent in rho_dot itself.

J_{i<-j} = 2 Im(H_ij rho_ji) is antisymmetric and satisfies dot_p_i = sum_j J_{i<-j}
for ANY finite-dimensional H -- no spatial projector required. This is distinct
from both operator-space (Pauli) velocity and physical-space current: it is
population flow in whatever basis rho happens to be expressed in.
"""
from __future__ import annotations

import numpy as np


def basis_current(H: np.ndarray, rho: np.ndarray) -> np.ndarray:
    """J[i, j] = J_{i<-j} = 2 * Im(H_ij * rho_ji), hbar = 1. Antisymmetric: J[j,i] == -J[i,j]."""
    return 2.0 * np.imag(H * rho.T)


def populations(rho: np.ndarray) -> np.ndarray:
    return np.real(np.diag(rho))


def region_population(rho: np.ndarray, region: tuple[int, ...]) -> float:
    """N_R = sum_{i in R} p_i."""
    return float(sum(populations(rho)[i] for i in region))


def region_flux(J: np.ndarray, region: tuple[int, ...]) -> float:
    """Phi_R: net outward current across the boundary of R, so that dot(N_R) == -Phi_R."""
    d = J.shape[0]
    outside = [i for i in range(d) if i not in region]
    return float(sum(J[i, j] for i in outside for j in region))
