"""Observables and reductions for the coupled-oscillator V2 model."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import numpy as np

from .coupled_model import CoupledOscillatorModel
from .coupled_schema import CoupledOscillatorFrame
from .states import density_matrix


def partial_traces(
    rho: np.ndarray, dimension_a: int, dimension_b: int
) -> tuple[np.ndarray, np.ndarray]:
    state = density_matrix(rho)
    expected = dimension_a * dimension_b
    if state.shape != (expected, expected):
        raise ValueError("rho does not match the two-mode dimensions")
    tensor = state.reshape(dimension_a, dimension_b, dimension_a, dimension_b)
    rho_a = np.trace(tensor, axis1=1, axis2=3)
    rho_b = np.trace(tensor, axis1=0, axis2=2)
    return density_matrix(rho_a), density_matrix(rho_b)


def von_neumann_entropy(rho: np.ndarray) -> float:
    eigenvalues = np.linalg.eigvalsh(density_matrix(rho))
    positive = eigenvalues[eigenvalues > 1e-15]
    return float(-np.sum(positive * np.log(positive)))


def _expectation(rho: np.ndarray, operator: np.ndarray) -> complex:
    return complex(np.trace(np.asarray(rho) @ np.asarray(operator)))


def coupled_frame_from_density(
    rho: np.ndarray,
    model: CoupledOscillatorModel,
    *,
    time: float = 0.0,
    backend: str,
    backend_metadata: Mapping[str, Any] | None = None,
    include_rho: bool = False,
) -> CoupledOscillatorFrame:
    state = density_matrix(rho)
    spec = model.spec
    if state.shape != (spec.total_dimension, spec.total_dimension):
        raise ValueError("rho dimension does not match coupled oscillator model")
    rho_a, rho_b = partial_traces(state, spec.dimension_a, spec.dimension_b)
    ops = model.operators

    def real_expectation(operator: np.ndarray) -> float:
        value = np.real_if_close(_expectation(state, operator), tol=1000)
        if np.iscomplexobj(value):
            raise ValueError("Hermitian expectation has an imaginary residue")
        return float(value)

    x_a = real_expectation(ops.x_a)
    p_a = real_expectation(ops.p_a)
    x_b = real_expectation(ops.x_b)
    p_b = real_expectation(ops.p_b)
    diagonal = np.real(np.diag(state)).reshape(
        spec.dimension_a, spec.dimension_b
    )
    return CoupledOscillatorFrame(
        time=float(time),
        dimension_a=spec.dimension_a,
        dimension_b=spec.dimension_b,
        joint_populations=diagonal.copy(),
        populations_a=np.sum(diagonal, axis=1),
        populations_b=np.sum(diagonal, axis=0),
        mean_n_a=real_expectation(ops.number_a),
        mean_n_b=real_expectation(ops.number_b),
        mean_total_n=real_expectation(ops.total_number),
        mean_energy=real_expectation(ops.hamiltonian),
        x_a=x_a,
        p_a=p_a,
        var_x_a=max(0.0, real_expectation(ops.x_a @ ops.x_a) - x_a * x_a),
        var_p_a=max(0.0, real_expectation(ops.p_a @ ops.p_a) - p_a * p_a),
        x_b=x_b,
        p_b=p_b,
        var_x_b=max(0.0, real_expectation(ops.x_b @ ops.x_b) - x_b * x_b),
        var_p_b=max(0.0, real_expectation(ops.p_b @ ops.p_b) - p_b * p_b),
        exchange_coherence=_expectation(
            state, ops.creation_a @ ops.annihilation_b
        ),
        global_purity=float(np.real(np.trace(state @ state))),
        local_purity_a=float(np.real(np.trace(rho_a @ rho_a))),
        local_purity_b=float(np.real(np.trace(rho_b @ rho_b))),
        reduced_entropy_a=von_neumann_entropy(rho_a),
        reduced_entropy_b=von_neumann_entropy(rho_b),
        backend=backend,
        backend_metadata=dict(backend_metadata or {}),
        rho=state.copy() if include_rho else None,
        rho_a=rho_a.copy() if include_rho else None,
        rho_b=rho_b.copy() if include_rho else None,
    )


__all__ = [
    "coupled_frame_from_density",
    "partial_traces",
    "von_neumann_entropy",
]
