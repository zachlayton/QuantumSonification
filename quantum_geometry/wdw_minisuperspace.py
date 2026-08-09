"""Finite Wheeler-DeWitt-inspired constraint on geometry configuration space."""
from __future__ import annotations
from dataclasses import dataclass
import importlib.util
import os
import numpy as np

HAS_MLX = importlib.util.find_spec("mlx.core") is not None


@dataclass(frozen=True)
class ConstraintSolution:
    state: np.ndarray
    eigenvalue: float
    residual_norm: float
    expectation: float
    spectrum: np.ndarray
    backend: str


def build_constraint(laplacian: np.ndarray, *, alpha: float = 1.0, geometry_potential=None, matter_hamiltonian=None) -> np.ndarray:
    l = np.asarray(laplacian, dtype=np.complex128); n = len(l)
    v = np.zeros(n) if geometry_potential is None else np.asarray(geometry_potential)
    v = np.diag(v) if v.ndim == 1 else v
    m = np.zeros((n,n)) if matter_hamiltonian is None else np.asarray(matter_hamiltonian)
    c = -float(alpha)*l + v + m
    if c.shape != (n,n) or not np.allclose(c, c.conj().T): raise ValueError("constraint terms must form an n x n Hermitian matrix")
    return c


def solve_constraint(constraint: np.ndarray, *, target: float = 0.0, prefer_mlx: bool = True) -> ConstraintSolution:
    c = np.asarray(constraint, dtype=np.complex128)
    backend = "numpy"
    if prefer_mlx and HAS_MLX and os.environ.get("QMW_DISABLE_MLX") != "1":
        try:
            import mlx.core as mx
            vals_mx, vecs_mx = mx.linalg.eigh(mx.array(c)); mx.eval(vals_mx, vecs_mx)
            vals, vecs = np.asarray(vals_mx), np.asarray(vecs_mx); backend = "mlx"
        except RuntimeError:
            # MLX may import in headless macOS sessions where Metal is absent.
            vals, vecs = np.linalg.eigh(c); backend = "numpy_mlx_unavailable"
    else:
        vals, vecs = np.linalg.eigh(c)
    idx = int(np.argmin(np.abs(vals-target))); psi = vecs[:, idx]; psi /= np.linalg.norm(psi)
    residual = c@psi - target*psi
    return ConstraintSolution(psi, float(vals[idx].real), float(np.linalg.norm(residual)), float(np.vdot(psi,c@psi).real), np.asarray(vals.real), backend)
