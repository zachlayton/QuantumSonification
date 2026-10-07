"""Canonical oscillator observables and frame assembly."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import numpy as np

from .model import OscillatorModel
from .schema import OscillatorFrame
from .states import density_matrix


def expectation(rho: np.ndarray, operator: np.ndarray) -> float:
    value = np.trace(np.asarray(rho) @ np.asarray(operator))
    result = np.real_if_close(value, tol=1000)
    if np.iscomplexobj(result):
        raise ValueError("expectation value has a significant imaginary component")
    return float(result)


def frame_from_density(
    rho: np.ndarray,
    model: OscillatorModel,
    *,
    time: float = 0.0,
    backend: str,
    backend_metadata: Mapping[str, Any] | None = None,
    include_rho: bool = False,
    include_wigner: bool = False,
    wigner_x: np.ndarray | None = None,
    wigner_p: np.ndarray | None = None,
) -> OscillatorFrame:
    state = density_matrix(rho)
    if state.shape != (model.spec.dimension, model.spec.dimension):
        raise ValueError("rho dimension does not match oscillator model")
    ops = model.operators
    mean_x = expectation(state, ops.x)
    mean_p = expectation(state, ops.p)
    x2 = expectation(state, ops.x @ ops.x)
    p2 = expectation(state, ops.p @ ops.p)
    wigner = None
    if include_wigner:
        from .phase_space import wigner_grid

        wigner = wigner_grid(state, model, x=wigner_x, p=wigner_p)
    purity = float(np.real(np.trace(state @ state)))
    coherence_l1 = float(
        np.sum(np.abs(state)) - np.sum(np.abs(np.diag(state)))
    )
    return OscillatorFrame(
        time=float(time),
        dimension=model.spec.dimension,
        populations=np.real(np.diag(state)).copy(),
        mean_n=expectation(state, ops.number),
        mean_energy=expectation(state, ops.hamiltonian),
        x=mean_x,
        p=mean_p,
        var_x=max(0.0, x2 - mean_x * mean_x),
        var_p=max(0.0, p2 - mean_p * mean_p),
        backend=backend,
        purity=purity,
        coherence_l1=max(0.0, coherence_l1),
        backend_metadata=dict(backend_metadata or {}),
        rho=state.copy() if include_rho else None,
        wigner=wigner,
    )


__all__ = ["expectation", "frame_from_density"]
