"""Serializable scientific result schema for an atomic manifold."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

import numpy as np


def _complex_array(value: np.ndarray) -> dict[str, Any]:
    array = np.asarray(value, dtype=np.complex128)
    return {"real": array.real.tolist(), "imag": array.imag.tolist()}


@dataclass(frozen=True)
class AtomicOrbitalFrame:
    """One observed state in a fixed hydrogenic ``(n, ell)`` manifold."""

    time: float
    n: int
    ell: int
    basis_labels: tuple[tuple[int, str], ...]
    coefficients: np.ndarray
    orbital_populations: np.ndarray
    spin_populations: np.ndarray
    pauli_vector: np.ndarray
    mean_l: np.ndarray
    mean_s: np.ndarray
    mean_j: np.ndarray
    mean_l_dot_s: float
    mean_energy: float
    energy_variance: float
    purity: float
    spin_purity: float
    spin_orbital_entanglement_entropy: float
    rho: np.ndarray
    orbital_rho: np.ndarray
    spin_rho: np.ndarray
    backend: str = "numpy_atomic_manifold"
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self, *, include_density_matrices: bool = True) -> dict[str, Any]:
        result: dict[str, Any] = {
            "schema": "qmw.atomic_orbital_frame.v4",
            "time": float(self.time),
            "n": int(self.n),
            "ell": int(self.ell),
            "basis_labels": [list(value) for value in self.basis_labels],
            "coefficients": _complex_array(self.coefficients),
            "orbital_populations": self.orbital_populations.tolist(),
            "spin_populations": self.spin_populations.tolist(),
            "pauli_vector": self.pauli_vector.tolist(),
            "mean_l": self.mean_l.tolist(),
            "mean_s": self.mean_s.tolist(),
            "mean_j": self.mean_j.tolist(),
            "mean_l_dot_s": float(self.mean_l_dot_s),
            "mean_energy": float(self.mean_energy),
            "energy_variance": float(self.energy_variance),
            "purity": float(self.purity),
            "spin_purity": float(self.spin_purity),
            "spin_orbital_entanglement_entropy": float(
                self.spin_orbital_entanglement_entropy
            ),
            "backend": self.backend,
            "metadata": dict(self.metadata),
        }
        if include_density_matrices:
            result.update(
                rho=_complex_array(self.rho),
                orbital_rho=_complex_array(self.orbital_rho),
                spin_rho=_complex_array(self.spin_rho),
            )
        return result


__all__ = ["AtomicOrbitalFrame"]
