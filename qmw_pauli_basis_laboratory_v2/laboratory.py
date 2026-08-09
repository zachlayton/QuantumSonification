"""Side-by-side computational and experimental basis tomography."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, replace
from pathlib import Path
from typing import Any

import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import DensityMatrix, Statevector, state_fidelity

from full4q_tomography_v1 import (
    PAULI_LABELS,
    SETTINGS,
    TomographyResult,
    build_score_circuit,
    reconstruct_tomography,
)

from .basis_operator import BasisOperator, validate_density_matrix
from .bases import IdentityBasis
from .observables import pauli_expectations


LABORATORY_SCHEMA = "qmw.pauli_basis_laboratory.v2"
FULL4Q_DIMENSION = 16


@dataclass(frozen=True)
class ObservableComparison:
    index: int
    label: str
    weight: int
    computational_exact: float
    experimental_exact: float
    computational_estimate: float
    experimental_estimate: float
    exact_delta: float
    estimated_delta: float


@dataclass(frozen=True)
class BasisLaboratoryResult:
    """Two compatible tomography outputs derived from one canonical density."""

    schema: str
    preset: str
    basis: dict[str, Any]
    shots_per_setting: int
    seed: int
    computational_basis: TomographyResult
    experimental_basis: TomographyResult
    observable_comparisons: list[ObservableComparison]
    comparison_metrics: dict[str, float]
    canonical_density_real: list[list[float]]
    canonical_density_imag: list[list[float]]
    experimental_density_real: list[list[float]]
    experimental_density_imag: list[list[float]]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def tomography_outputs(self) -> tuple[TomographyResult, TomographyResult]:
        """Return the two unchanged downstream Full4Q result objects."""
        return self.computational_basis, self.experimental_basis


def density_from_preset(preset: str = "ghz") -> np.ndarray:
    state = Statevector.from_instruction(build_score_circuit(preset))
    return np.outer(state.data, state.data.conj())


def _measurement_probabilities(rho: np.ndarray, axes: str) -> np.ndarray:
    rotation = QuantumCircuit(4)
    for qubit, axis in enumerate(axes):
        if axis == "X":
            rotation.h(qubit)
        elif axis == "Y":
            rotation.sdg(qubit)
            rotation.h(qubit)
        elif axis != "Z":
            raise ValueError(f"invalid measurement axis {axis!r}")
    measured = DensityMatrix(rho).evolve(rotation)
    probabilities = np.asarray(measured.probabilities(), dtype=float)
    probabilities[np.abs(probabilities) < 1e-15] = 0.0
    probabilities = np.clip(probabilities, 0.0, None)
    total = float(np.sum(probabilities))
    if total <= 0:
        raise ValueError("measurement probabilities have zero total")
    return probabilities / total


def _density_from_result(result: TomographyResult) -> np.ndarray:
    return np.asarray(result.density_physical_real, dtype=float) + 1j * np.asarray(
        result.density_physical_imag,
        dtype=float,
    )


def _matrix_parts(matrix: np.ndarray) -> tuple[list[list[float]], list[list[float]]]:
    return matrix.real.tolist(), matrix.imag.tolist()


def tomography_from_density(
    rho: np.ndarray,
    *,
    preset: str,
    representation: str,
    shots: int = 256,
    seed: int = 23,
    source: str = "basis_laboratory",
) -> TomographyResult:
    """Sample one density representation through the existing Full4Q engine."""
    density = validate_density_matrix(rho)
    if density.shape != (FULL4Q_DIMENSION, FULL4Q_DIMENSION):
        raise ValueError(
            "Full4Q tomography requires a 16x16 four-qubit density matrix"
        )
    if shots <= 0:
        raise ValueError("shots must be positive")

    random = np.random.default_rng(seed)
    rows: list[list[int]] = []
    for axes in SETTINGS:
        probabilities = _measurement_probabilities(density, axes)
        rows.append(
            [
                int(value)
                for value in random.multinomial(shots, probabilities)
            ]
        )

    # Reuse the established setting -> Pauli -> shell -> physical-density
    # pipeline unchanged.  ``none`` is used only while assembling because the
    # v1 ideal-state lookup knows its original transform menu; the laboratory
    # replaces that metadata and fidelity with the supplied representation.
    result = reconstruct_tomography(
        rows,
        preset=preset,
        transform="none",
        shots=shots,
        seed=seed,
        source=source,
    )
    reconstructed_density = _density_from_result(result)
    fidelity = float(
        state_fidelity(
            DensityMatrix(density),
            DensityMatrix(reconstructed_density),
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


def run_basis_laboratory(
    basis: BasisOperator,
    *,
    rho: np.ndarray | None = None,
    preset: str = "ghz",
    shots: int = 256,
    seed: int = 23,
) -> BasisLaboratoryResult:
    """Compare canonical and transformed Pauli landscapes for one density."""
    canonical = validate_density_matrix(
        density_from_preset(preset) if rho is None else rho
    )
    if canonical.shape != (FULL4Q_DIMENSION, FULL4Q_DIMENSION):
        raise ValueError(
            "QMW Pauli Basis Laboratory v2 currently requires four qubits"
        )
    experimental = basis.transform(canonical)

    computational_result = tomography_from_density(
        canonical,
        preset=preset,
        representation=IdentityBasis.name,
        shots=shots,
        seed=seed,
        source="basis_computational",
    )
    experimental_result = tomography_from_density(
        experimental,
        preset=preset,
        representation=basis.name,
        shots=shots,
        seed=seed,
        source="basis_experimental",
    )

    computational_exact = pauli_expectations(canonical)
    experimental_exact = pauli_expectations(experimental)
    computational_estimates = {
        item.label: item.expectation for item in computational_result.paulis
    }
    experimental_estimates = {
        item.label: item.expectation for item in experimental_result.paulis
    }

    comparisons: list[ObservableComparison] = []
    for index, label in enumerate(PAULI_LABELS):
        if label == "IIII":
            continue
        computational_value = computational_exact[label]
        experimental_value = experimental_exact[label]
        computational_estimate = computational_estimates[label]
        experimental_estimate = experimental_estimates[label]
        comparisons.append(
            ObservableComparison(
                index=index - 1,
                label=label,
                weight=sum(axis != "I" for axis in label),
                computational_exact=computational_value,
                experimental_exact=experimental_value,
                computational_estimate=computational_estimate,
                experimental_estimate=experimental_estimate,
                exact_delta=experimental_value - computational_value,
                estimated_delta=(
                    experimental_estimate - computational_estimate
                ),
            )
        )

    exact_deltas = np.asarray(
        [comparison.exact_delta for comparison in comparisons], dtype=float
    )
    estimate_errors = np.asarray(
        [
            comparison.experimental_estimate
            - comparison.experimental_exact
            for comparison in comparisons
        ],
        dtype=float,
    )
    canonical_real, canonical_imag = _matrix_parts(canonical)
    experimental_real, experimental_imag = _matrix_parts(experimental)
    return BasisLaboratoryResult(
        schema=LABORATORY_SCHEMA,
        preset=preset.lower(),
        basis=basis.metadata(FULL4Q_DIMENSION),
        shots_per_setting=shots,
        seed=seed,
        computational_basis=computational_result,
        experimental_basis=experimental_result,
        observable_comparisons=comparisons,
        comparison_metrics={
            "density_frobenius_distance": float(
                np.linalg.norm(experimental - canonical)
            ),
            "observable_delta_rms_exact": float(
                np.sqrt(np.mean(exact_deltas**2))
            ),
            "observable_delta_max_abs_exact": float(
                np.max(np.abs(exact_deltas))
            ),
            "experimental_tomography_error_rms": float(
                np.sqrt(np.mean(estimate_errors**2))
            ),
            "experimental_tomography_error_max_abs": float(
                np.max(np.abs(estimate_errors))
            ),
        },
        canonical_density_real=canonical_real,
        canonical_density_imag=canonical_imag,
        experimental_density_real=experimental_real,
        experimental_density_imag=experimental_imag,
    )


def save_laboratory_result(
    result: BasisLaboratoryResult,
    destination: str | Path,
) -> Path:
    path = Path(destination)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(result.to_dict(), indent=2, sort_keys=False) + "\n",
        encoding="utf-8",
    )
    return path
