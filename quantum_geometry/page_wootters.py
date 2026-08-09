"""Discrete Page-Wootters history states and conditional geometry states."""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np


@dataclass(frozen=True)
class ConditionalGeometryHistory:
    times: np.ndarray
    states: np.ndarray
    density_matrices: np.ndarray
    weights: np.ndarray
    history_state: np.ndarray
    clock_probabilities: np.ndarray


def conditional_history(initial_state: np.ndarray, hamiltonian: np.ndarray, *, steps: int = 16, dt: float = 0.25) -> ConditionalGeometryHistory:
    psi0 = np.asarray(initial_state, dtype=np.complex128).reshape(-1); psi0 /= np.linalg.norm(psi0)
    h = np.asarray(hamiltonian, dtype=np.complex128)
    if h.shape != (len(psi0),len(psi0)) or steps < 2: raise ValueError("invalid Hamiltonian or clock size")
    vals, vecs = np.linalg.eigh(h); times = np.arange(steps,dtype=float)*float(dt)
    states = np.stack([(vecs*np.exp(-1j*vals*t))@vecs.conj().T@psi0 for t in times])
    rhos = np.einsum("ti,tj->tij", states, states.conj())
    weights = np.maximum(np.real(np.diagonal(rhos,axis1=1,axis2=2)),0); weights /= weights.sum(axis=1,keepdims=True)
    history = states.reshape(-1)/np.sqrt(steps)
    return ConditionalGeometryHistory(times, states, rhos, weights, history, np.full(steps,1/steps))


def condition_clock(history_state: np.ndarray, clock_index: int, *, clock_steps: int, system_dimension: int) -> np.ndarray:
    joint = np.asarray(history_state).reshape(clock_steps,system_dimension)
    psi = joint[int(clock_index)]; norm = np.linalg.norm(psi)
    if norm == 0: raise ValueError("clock outcome has zero probability")
    return psi/norm
