"""Translations between a configuration graph and density operators."""
from __future__ import annotations
import numpy as np


def validate_density(rho: np.ndarray, atol: float = 1e-9) -> np.ndarray:
    rho = np.asarray(rho, dtype=np.complex128)
    if rho.ndim != 2 or rho.shape[0] != rho.shape[1]: raise ValueError("rho must be square")
    if not np.allclose(rho, rho.conj().T, atol=atol): raise ValueError("rho must be Hermitian")
    if not np.isclose(np.trace(rho), 1.0, atol=atol): raise ValueError("rho must have unit trace")
    if np.min(np.linalg.eigvalsh(rho)) < -atol: raise ValueError("rho must be positive semidefinite")
    return rho


class GraphDensityBridge:
    @staticmethod
    def encode(laplacian: np.ndarray) -> np.ndarray:
        l = np.asarray(laplacian, dtype=np.complex128)
        tr = float(np.trace(l).real)
        if tr <= 0: raise ValueError("nontrivial Laplacian required")
        return validate_density(l/tr)

    @staticmethod
    def basis(rho: np.ndarray, laplacian: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        rho = validate_density(rho)
        eigenvalues, vectors = np.linalg.eigh(np.asarray(laplacian, dtype=np.complex128))
        return vectors.conj().T @ rho @ vectors, eigenvalues, vectors

    @staticmethod
    def evolve(rho: np.ndarray, generator: np.ndarray, dt: float) -> np.ndarray:
        rho = validate_density(rho); h = np.asarray(generator, dtype=np.complex128)
        vals, vecs = np.linalg.eigh(h)
        u = (vecs*np.exp(-1j*vals*float(dt))) @ vecs.conj().T
        return validate_density(u @ rho @ u.conj().T)

    @staticmethod
    def from_state(psi: np.ndarray) -> np.ndarray:
        psi = np.asarray(psi, dtype=np.complex128).reshape(-1)
        psi = psi / np.linalg.norm(psi)
        return validate_density(np.outer(psi, psi.conj()))
