"""Result schema for the coupled-oscillator V2 reference model."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

import numpy as np


def _complex_matrix_payload(value: np.ndarray) -> dict[str, list[list[float]]]:
    array = np.asarray(value)
    return {"real": array.real.tolist(), "imag": array.imag.tolist()}


@dataclass(frozen=True)
class CoupledOscillatorFrame:
    time: float
    dimension_a: int
    dimension_b: int
    joint_populations: np.ndarray
    populations_a: np.ndarray
    populations_b: np.ndarray
    mean_n_a: float
    mean_n_b: float
    mean_total_n: float
    mean_energy: float
    x_a: float
    p_a: float
    var_x_a: float
    var_p_a: float
    x_b: float
    p_b: float
    var_x_b: float
    var_p_b: float
    exchange_coherence: complex
    global_purity: float
    local_purity_a: float
    local_purity_b: float
    reduced_entropy_a: float
    reduced_entropy_b: float
    backend: str
    backend_metadata: Mapping[str, Any] = field(default_factory=dict)
    rho: np.ndarray | None = None
    rho_a: np.ndarray | None = None
    rho_b: np.ndarray | None = None

    def to_dict(self, *, include_rho: bool = True) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "schema": "qmw.coupled_oscillator_frame.v2",
            "time": self.time,
            "dimensions": {"a": self.dimension_a, "b": self.dimension_b},
            "basis_order": "|n_a,n_b>; index=n_a*dimension_b+n_b",
            "joint_populations": np.asarray(
                self.joint_populations, dtype=float
            ).tolist(),
            "populations_a": np.asarray(self.populations_a, dtype=float).tolist(),
            "populations_b": np.asarray(self.populations_b, dtype=float).tolist(),
            "mean_n": {
                "a": self.mean_n_a,
                "b": self.mean_n_b,
                "total": self.mean_total_n,
            },
            "mean_energy": self.mean_energy,
            "quadratures": {
                "a": {
                    "x": self.x_a,
                    "p": self.p_a,
                    "var_x": self.var_x_a,
                    "var_p": self.var_p_a,
                },
                "b": {
                    "x": self.x_b,
                    "p": self.p_b,
                    "var_x": self.var_x_b,
                    "var_p": self.var_p_b,
                },
            },
            "exchange_coherence": {
                "real": float(np.real(self.exchange_coherence)),
                "imag": float(np.imag(self.exchange_coherence)),
            },
            "purity": {
                "global": self.global_purity,
                "a": self.local_purity_a,
                "b": self.local_purity_b,
            },
            "reduced_entropy": {
                "a": self.reduced_entropy_a,
                "b": self.reduced_entropy_b,
            },
            "backend": self.backend,
            "backend_metadata": dict(self.backend_metadata),
        }
        payload["rho"] = (
            _complex_matrix_payload(self.rho)
            if include_rho and self.rho is not None
            else None
        )
        payload["rho_a"] = (
            _complex_matrix_payload(self.rho_a)
            if include_rho and self.rho_a is not None
            else None
        )
        payload["rho_b"] = (
            _complex_matrix_payload(self.rho_b)
            if include_rho and self.rho_b is not None
            else None
        )
        return payload


__all__ = ["CoupledOscillatorFrame"]
