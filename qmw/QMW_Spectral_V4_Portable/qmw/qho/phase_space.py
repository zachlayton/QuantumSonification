"""Auditable finite-basis Wigner representation."""

from __future__ import annotations

import numpy as np
from scipy.linalg import expm

from .model import OscillatorModel
from .schema import WignerGrid
from .states import density_matrix


def wigner_grid(
    rho: np.ndarray,
    model: OscillatorModel,
    *,
    x: np.ndarray | None = None,
    p: np.ndarray | None = None,
) -> WignerGrid:
    """Evaluate W(x,p) via displaced parity, with [X,P]=i.

    The default grid is intentionally modest.  This is a finite-cutoff result;
    convergence should be checked by increasing both the cutoff and grid span.
    """

    state = density_matrix(rho)
    if state.shape[0] != model.spec.dimension:
        raise ValueError("rho dimension does not match oscillator model")
    x_axis = np.asarray(np.linspace(-4.0, 4.0, 65) if x is None else x, dtype=float)
    p_axis = np.asarray(np.linspace(-4.0, 4.0, 65) if p is None else p, dtype=float)
    if x_axis.ndim != 1 or p_axis.ndim != 1 or x_axis.size == 0 or p_axis.size == 0:
        raise ValueError("x and p must be nonempty one-dimensional grids")
    a = model.operators.annihilation
    adag = model.operators.creation
    parity = np.diag((-1.0) ** np.arange(model.spec.dimension))
    values = np.empty((p_axis.size, x_axis.size), dtype=float)
    for p_index, p_value in enumerate(p_axis):
        for x_index, x_value in enumerate(x_axis):
            alpha = (x_value + 1j * p_value) / np.sqrt(2.0)
            displacement = expm((-alpha) * adag + np.conj(alpha) * a)
            displaced = displacement @ state @ displacement.conj().T
            values[p_index, x_index] = float(
                np.real(np.trace(displaced @ parity)) / np.pi
            )
    return WignerGrid(x=x_axis, p=p_axis, values=values)


__all__ = ["wigner_grid"]
