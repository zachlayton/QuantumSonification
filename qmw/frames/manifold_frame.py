"""Synchronized data frame published by the manifold engine."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

import numpy as np


@dataclass(frozen=True)
class ManifoldFrame:
    eta: float
    matrix: np.ndarray
    magnitude: np.ndarray
    phase: np.ndarray
    buffer_256: np.ndarray
    spectrum: np.ndarray
    gradient_m: np.ndarray
    gradient_n: np.ndarray
    gradient_eta: np.ndarray
    source_basis_name: str
    target_basis_name: str
    diagnostics: Mapping[str, Any]

    def __post_init__(self) -> None:
        matrix = np.asarray(self.matrix, dtype=np.complex128)
        if matrix.shape != (16, 16):
            raise ValueError(f"ManifoldFrame.matrix must have shape (16, 16), got {matrix.shape}")
        buffer = np.asarray(self.buffer_256)
        if buffer.shape != (256,):
            raise ValueError(f"ManifoldFrame.buffer_256 must have shape (256,), got {buffer.shape}")
        array_names = (
            "matrix",
            "magnitude",
            "phase",
            "buffer_256",
            "spectrum",
            "gradient_m",
            "gradient_n",
            "gradient_eta",
        )
        for name in array_names:
            object.__setattr__(self, name, np.array(getattr(self, name), copy=True))
        object.__setattr__(self, "diagnostics", dict(self.diagnostics))

    def qmw_payload(self) -> dict[str, Any]:
        """Return named data lanes without assigning any musical semantics."""
        return {
            "eta": self.eta,
            "matrix": self.matrix.copy(),
            "magnitude": self.magnitude.copy(),
            "phase": self.phase.copy(),
            "buffer_256": self.buffer_256.copy(),
            "spectrum": self.spectrum.copy(),
            "gradient_m": self.gradient_m.copy(),
            "gradient_n": self.gradient_n.copy(),
            "gradient_eta": self.gradient_eta.copy(),
            "source_basis_name": self.source_basis_name,
            "target_basis_name": self.target_basis_name,
            "diagnostics": dict(self.diagnostics),
        }

