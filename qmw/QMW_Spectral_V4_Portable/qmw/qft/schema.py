"""Backend-independent frame schema for the QMW scalar field V3."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

import numpy as np


@dataclass(frozen=True)
class ScalarFieldFrame:
    time: float
    sites: int
    mean_phi: np.ndarray
    mean_pi: np.ndarray
    covariance_phi: np.ndarray
    covariance_pi: np.ndarray
    covariance_phi_pi: np.ndarray
    frequencies: np.ndarray
    mode_occupations: np.ndarray
    local_energy_density: np.ndarray
    mean_energy: float
    purity: float
    backend: str
    backend_metadata: Mapping[str, Any] = field(default_factory=dict)
    rho: np.ndarray | None = None

    @property
    def connected_field_correlator(self) -> np.ndarray:
        return self.covariance_phi

    def to_dict(self, *, include_covariance: bool = True) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "schema": "qmw.scalar_field_frame.v3",
            "time": self.time,
            "sites": self.sites,
            "mean_phi": np.asarray(self.mean_phi, dtype=float).tolist(),
            "mean_pi": np.asarray(self.mean_pi, dtype=float).tolist(),
            "frequencies": np.asarray(self.frequencies, dtype=float).tolist(),
            "mode_occupations": np.asarray(
                self.mode_occupations, dtype=float
            ).tolist(),
            "local_energy_density": np.asarray(
                self.local_energy_density, dtype=float
            ).tolist(),
            "mean_energy": self.mean_energy,
            "purity": self.purity,
            "backend": self.backend,
            "backend_metadata": dict(self.backend_metadata),
        }
        payload["covariance"] = (
            {
                "phi": np.asarray(self.covariance_phi, dtype=float).tolist(),
                "pi": np.asarray(self.covariance_pi, dtype=float).tolist(),
                "phi_pi": np.asarray(
                    self.covariance_phi_pi, dtype=float
                ).tolist(),
            }
            if include_covariance
            else None
        )
        payload["rho"] = (
            {
                "real": np.asarray(self.rho).real.tolist(),
                "imag": np.asarray(self.rho).imag.tolist(),
            }
            if include_covariance and self.rho is not None
            else None
        )
        return payload


__all__ = ["ScalarFieldFrame"]
