from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Any, Optional
import numpy as np


@dataclass
class QuantumFrame:
    """
    Canonical QMW 2048-sample quantum trajectory container.

    Physics remains backend-independent:
      solver/backend -> QuantumFrame -> projectors -> sound/visualization

    Default shapes for a 4-qubit frame:
      t:                  (2048,)
      psi:                (2048, 16)              optional
      rho:                (2048, 16, 16)
      observables[name]:  (2048, ...)
      diagnostics[name]:  (2048, ...) or static metadata
    """
    t: np.ndarray
    rho: np.ndarray
    psi: Optional[np.ndarray] = None
    observables: Dict[str, np.ndarray] = field(default_factory=dict)
    diagnostics: Dict[str, np.ndarray] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.t = np.asarray(self.t, dtype=float)
        self.rho = np.asarray(self.rho, dtype=complex)

        if self.t.ndim != 1:
            raise ValueError("t must be one-dimensional")
        if self.rho.ndim != 3:
            raise ValueError("rho must have shape (samples, dim, dim)")
        if self.rho.shape[0] != self.t.shape[0]:
            raise ValueError("rho sample count must match t")
        if self.rho.shape[1] != self.rho.shape[2]:
            raise ValueError("rho matrices must be square")

        if self.psi is not None:
            self.psi = np.asarray(self.psi, dtype=complex)
            if self.psi.ndim != 2:
                raise ValueError("psi must have shape (samples, dim)")
            if self.psi.shape[0] != self.t.shape[0]:
                raise ValueError("psi sample count must match t")
            if self.psi.shape[1] != self.rho.shape[1]:
                raise ValueError("psi Hilbert dimension must match rho")

        for name, value in list(self.observables.items()):
            arr = np.asarray(value)
            if arr.shape[0] != self.samples:
                raise ValueError(f"observable '{name}' must begin with sample dimension")
            self.observables[name] = arr

        self.metadata.setdefault("samples", self.samples)
        self.metadata.setdefault("hilbert_dim", self.hilbert_dim)

    @property
    def samples(self) -> int:
        return int(self.t.shape[0])

    @property
    def hilbert_dim(self) -> int:
        return int(self.rho.shape[1])

    @property
    def duration(self) -> float:
        if self.samples < 2:
            return 0.0
        return float(self.t[-1] - self.t[0])

    def trace(self) -> np.ndarray:
        return np.trace(self.rho, axis1=1, axis2=2)

    def purity(self) -> np.ndarray:
        return np.real(np.einsum("tij,tji->t", self.rho, self.rho))

    def eigenvalues(self) -> np.ndarray:
        """Density-matrix eigenvalues for every frame sample."""
        return np.linalg.eigvalsh(self.rho)

    def expectation(self, operator: np.ndarray) -> np.ndarray:
        operator = np.asarray(operator, dtype=complex)
        if operator.shape != (self.hilbert_dim, self.hilbert_dim):
            raise ValueError("operator dimension does not match frame Hilbert space")
        return np.real(np.einsum("tij,ji->t", self.rho, operator))

    def add_observable(self, name: str, values: np.ndarray) -> None:
        values = np.asarray(values)
        if values.shape[0] != self.samples:
            raise ValueError("observable sample count must match frame")
        self.observables[name] = values

    def normalized_observable(
        self,
        name: str,
        lo: float = 0.0,
        hi: float = 1.0,
        eps: float = 1e-12,
    ) -> np.ndarray:
        x = np.asarray(self.observables[name], dtype=float)
        xmin = np.nanmin(x)
        xmax = np.nanmax(x)
        if xmax - xmin < eps:
            return np.full_like(x, (lo + hi) * 0.5, dtype=float)
        y = (x - xmin) / (xmax - xmin)
        return lo + y * (hi - lo)

    def validate(self, atol: float = 1e-9) -> Dict[str, float | bool]:
        trace = self.trace()
        hermitian_err = np.max(
            np.linalg.norm(
                self.rho - np.swapaxes(self.rho.conj(), 1, 2),
                axis=(1, 2),
            )
        )
        eigs = self.eigenvalues()

        result = {
            "trace_error_max": float(np.max(np.abs(trace - 1.0))),
            "hermiticity_error_max": float(hermitian_err),
            "min_density_eigenvalue": float(np.min(eigs)),
            "positive_semidefinite": bool(np.min(eigs) >= -atol),
        }

        if self.psi is not None:
            norms = np.sum(np.abs(self.psi) ** 2, axis=1)
            result["state_norm_error_max"] = float(np.max(np.abs(norms - 1.0)))

        return result

    def to_npz(self, path: str) -> None:
        """
        Portable numerical export.
        Dicts are stored as object arrays; intended for trusted QMW files.
        """
        np.savez_compressed(
            path,
            t=self.t,
            rho=self.rho,
            psi=self.psi if self.psi is not None else np.array([]),
            observables=np.array([self.observables], dtype=object),
            diagnostics=np.array([self.diagnostics], dtype=object),
            metadata=np.array([self.metadata], dtype=object),
        )

    @classmethod
    def from_npz(cls, path: str) -> "QuantumFrame":
        d = np.load(path, allow_pickle=True)
        psi = d["psi"]
        if psi.size == 0:
            psi = None
        return cls(
            t=d["t"],
            rho=d["rho"],
            psi=psi,
            observables=d["observables"][0],
            diagnostics=d["diagnostics"][0],
            metadata=d["metadata"][0],
        )
