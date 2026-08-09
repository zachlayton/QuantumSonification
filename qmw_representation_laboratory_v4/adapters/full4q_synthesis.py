"""Adapter from a density matrix to the established Full4Q result contract."""

from __future__ import annotations

from dataclasses import replace
from typing import Any

import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import DensityMatrix, state_fidelity

from full4q_tomography_v1 import SETTINGS, reconstruct_tomography

from ..core import validate_density_matrix


FULL4Q_DIMENSION = 16


def measurement_probabilities(rho: np.ndarray, axes: str) -> np.ndarray:
    rotation = QuantumCircuit(4)
    for qubit, axis in enumerate(axes):
        if axis == "X":
            rotation.h(qubit)
        elif axis == "Y":
            rotation.sdg(qubit)
            rotation.h(qubit)
        elif axis != "Z":
            raise ValueError(f"invalid measurement axis {axis!r}")
    probabilities = np.asarray(
        DensityMatrix(rho).evolve(rotation).probabilities(),
        dtype=float,
    )
    probabilities[np.abs(probabilities) < 1e-15] = 0.0
    probabilities = np.clip(probabilities, 0.0, None)
    total = float(np.sum(probabilities))
    if total <= 0.0:
        raise ValueError("measurement probabilities have zero total")
    return probabilities / total


class Full4QSynthesisAdapter:
    dimension = FULL4Q_DIMENSION
    setting_count = 81
    observable_count = 255

    def run(
        self,
        rho: Any,
        *,
        preset: str,
        representation: str,
        shots: int,
        seed: int,
        source: str,
    ):
        density = validate_density_matrix(rho)
        if density.shape != (FULL4Q_DIMENSION, FULL4Q_DIMENSION):
            raise ValueError(
                "Full4Q synthesis requires a 16x16 four-qubit density matrix"
            )
        if shots <= 0:
            raise ValueError("shots must be positive")
        random = np.random.default_rng(seed)
        rows = [
            [
                int(value)
                for value in random.multinomial(
                    shots,
                    measurement_probabilities(density, axes),
                )
            ]
            for axes in SETTINGS
        ]
        result = reconstruct_tomography(
            rows,
            preset=preset,
            transform="none",
            shots=shots,
            seed=seed,
            source=source,
        )
        reconstructed = np.asarray(
            result.density_physical_real, dtype=float
        ) + 1j * np.asarray(result.density_physical_imag, dtype=float)
        fidelity = float(
            state_fidelity(
                DensityMatrix(density),
                DensityMatrix(reconstructed),
                validate=False,
            )
        )
        metrics = dict(result.metrics)
        metrics["fidelity_to_local_ideal"] = fidelity
        metrics["fidelity_to_representation_target"] = fidelity
        return replace(
            result,
            source=source,
            transform=representation,
            metrics=metrics,
        )
