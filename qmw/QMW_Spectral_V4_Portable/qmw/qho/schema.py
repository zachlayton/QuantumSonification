"""Backend-neutral oscillator result schema."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

import numpy as np


def _complex_matrix_payload(value: np.ndarray) -> dict[str, list[list[float]]]:
    array = np.asarray(value)
    return {"real": array.real.tolist(), "imag": array.imag.tolist()}


@dataclass(frozen=True)
class WignerGrid:
    x: np.ndarray
    p: np.ndarray
    values: np.ndarray

    def to_dict(self) -> dict[str, Any]:
        return {
            "x": np.asarray(self.x, dtype=float).tolist(),
            "p": np.asarray(self.p, dtype=float).tolist(),
            "values": np.asarray(self.values, dtype=float).tolist(),
        }


@dataclass(frozen=True)
class OscillatorFrame:
    """One common result from a bosonic, encoded-simulator, or hardware backend."""

    time: float
    dimension: int
    populations: np.ndarray
    mean_n: float
    mean_energy: float
    x: float
    p: float
    var_x: float
    var_p: float
    backend: str
    purity: float | None = None
    coherence_l1: float | None = None
    backend_metadata: Mapping[str, Any] = field(default_factory=dict)
    rho: np.ndarray | None = None
    wigner: WignerGrid | None = None

    @property
    def variances(self) -> dict[str, float]:
        return {"x": self.var_x, "p": self.var_p}

    def to_dict(self, *, include_rho: bool = True) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "schema": "qmw.oscillator_frame.v1",
            "time": self.time,
            "dimension": self.dimension,
            "populations": np.asarray(self.populations, dtype=float).tolist(),
            "mean_n": self.mean_n,
            "mean_energy": self.mean_energy,
            "x": self.x,
            "p": self.p,
            "variances": self.variances,
            "purity": self.purity,
            "coherence_l1": self.coherence_l1,
            "backend": self.backend,
            "backend_metadata": dict(self.backend_metadata),
            "wigner": None if self.wigner is None else self.wigner.to_dict(),
        }
        payload["rho"] = (
            _complex_matrix_payload(self.rho)
            if include_rho and self.rho is not None
            else None
        )
        return payload


__all__ = ["OscillatorFrame", "WignerGrid"]
