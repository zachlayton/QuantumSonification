"""Exact finite-manifold evolution for AtomicOrbitalFrame V4."""

from __future__ import annotations

import numpy as np

from .model import AtomicManifoldModel
from .states import AtomicState


def evolve_state(
    state: AtomicState, model: AtomicManifoldModel, time: float
) -> AtomicState:
    initial = state.validated(model)
    time = float(time)
    if not np.isfinite(time):
        raise ValueError("evolution time must be finite")
    eigenvalues, eigenvectors = np.linalg.eigh(model.hamiltonian)
    modal = eigenvectors.conj().T @ initial.amplitudes
    phase = np.exp(-1j * eigenvalues * time / model.spec.hbar)
    return AtomicState(eigenvectors @ (phase * modal)).validated(model)


__all__ = ["evolve_state"]
