"""Composition of transforms, measurement, and exact/sampled comparison."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import numpy as np
from qiskit.quantum_info import Statevector

from full4q_tomography_v1 import PAULI_LABELS, build_score_circuit

from ..observables import pauli_expectations
from ..transforms.identity import IdentityOperator
from .measurement_protocol import MeasurementProtocol
from .state_transform import (
    StateTransform,
    TransformContext,
    validate_density_matrix,
)


LABORATORY_SCHEMA = "qmw.representation_laboratory.v4"


@dataclass(frozen=True)
class ObservableComparison:
    index: int
    label: str
    weight: int
    reference_exact: float
    experimental_exact: float
    reference_estimate: float
    experimental_estimate: float
    exact_delta: float
    estimated_delta: float


@dataclass(frozen=True)
class RepresentationExperimentResult:
    schema: str
    preset: str
    reference_transform: dict[str, Any]
    experimental_transform: dict[str, Any]
    measurement_protocol: dict[str, Any]
    shots_per_setting: int
    seed: int
    requested_seed: int | None
    sampling_mode: str
    reference_output: Any
    experimental_output: Any
    reference_measurement: dict[str, Any]
    experimental_measurement: dict[str, Any]
    observable_comparisons: list[ObservableComparison]
    comparison_metrics: dict[str, float]
    reference_density_real: list[list[float]]
    reference_density_imag: list[list[float]]
    experimental_density_real: list[list[float]]
    experimental_density_imag: list[list[float]]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def tomography_outputs(self) -> tuple[Any, Any]:
        return self.reference_output, self.experimental_output


def density_from_preset(preset: str = "ghz") -> np.ndarray:
    state = Statevector.from_instruction(build_score_circuit(preset))
    return np.outer(state.data, state.data.conj())


def _parts(
    matrix: np.ndarray,
) -> tuple[list[list[float]], list[list[float]]]:
    return matrix.real.tolist(), matrix.imag.tolist()


class RepresentationExperiment:
    def __init__(
        self,
        *,
        experimental: StateTransform,
        measurement: MeasurementProtocol,
        reference: StateTransform | None = None,
    ) -> None:
        self.reference = reference or IdentityOperator()
        self.experimental = experimental
        self.measurement = measurement

    def run(
        self,
        *,
        rho: Any | None = None,
        preset: str = "ghz",
        shots: int = 256,
        seed: int | None = 23,
        context: TransformContext = None,
    ) -> RepresentationExperimentResult:
        if shots <= 0:
            raise ValueError("shots must be positive")
        canonical = validate_density_matrix(
            density_from_preset(preset) if rho is None else rho
        )
        dimension = canonical.shape[0]
        reference_density = validate_density_matrix(
            self.reference.apply(canonical, context)
        )
        experimental_density = validate_density_matrix(
            self.experimental.apply(canonical, context)
        )
        if reference_density.shape != experimental_density.shape:
            raise ValueError("transforms produced different dimensions")

        # One resolution is deliberately shared by both sides. Any sampling
        # difference then comes from the representations, not different seeds.
        sampling = self.measurement.resolve_sampling(seed)
        reference_record = self.measurement.measure(
            reference_density,
            preset=preset,
            representation=self.reference.name,
            shots=shots,
            sampling=sampling,
            source="representation_reference",
        )
        experimental_record = self.measurement.measure(
            experimental_density,
            preset=preset,
            representation=self.experimental.name,
            shots=shots,
            sampling=sampling,
            source="representation_experimental",
        )

        reference_exact = pauli_expectations(reference_density)
        experimental_exact = pauli_expectations(experimental_density)
        comparisons: list[ObservableComparison] = []
        for index, label in enumerate(PAULI_LABELS):
            if label == "IIII":
                continue
            try:
                reference_estimate = reference_record.observable_estimates[label]
                experimental_estimate = (
                    experimental_record.observable_estimates[label]
                )
            except KeyError as exc:
                raise ValueError(
                    f"measurement protocol omitted required observable {label}"
                ) from exc
            comparisons.append(
                ObservableComparison(
                    index=index - 1,
                    label=label,
                    weight=sum(axis != "I" for axis in label),
                    reference_exact=reference_exact[label],
                    experimental_exact=experimental_exact[label],
                    reference_estimate=reference_estimate,
                    experimental_estimate=experimental_estimate,
                    exact_delta=(
                        experimental_exact[label] - reference_exact[label]
                    ),
                    estimated_delta=(
                        experimental_estimate - reference_estimate
                    ),
                )
            )

        exact_delta = np.asarray(
            [item.exact_delta for item in comparisons], dtype=float
        )
        estimated_delta = np.asarray(
            [item.estimated_delta for item in comparisons], dtype=float
        )
        reference_error = np.asarray(
            [
                item.reference_estimate - item.reference_exact
                for item in comparisons
            ],
            dtype=float,
        )
        experimental_error = np.asarray(
            [
                item.experimental_estimate - item.experimental_exact
                for item in comparisons
            ],
            dtype=float,
        )
        reference_real, reference_imag = _parts(reference_density)
        experimental_real, experimental_imag = _parts(experimental_density)
        return RepresentationExperimentResult(
            schema=LABORATORY_SCHEMA,
            preset=preset.lower(),
            reference_transform=self.reference.metadata(dimension, context),
            experimental_transform=self.experimental.metadata(
                dimension, context
            ),
            measurement_protocol=self.measurement.metadata(),
            shots_per_setting=shots,
            seed=sampling.resolved_seed,
            requested_seed=seed,
            sampling_mode=sampling.mode,
            reference_output=reference_record.output,
            experimental_output=experimental_record.output,
            reference_measurement=reference_record.metadata,
            experimental_measurement=experimental_record.metadata,
            observable_comparisons=comparisons,
            comparison_metrics={
                "density_frobenius_distance": float(
                    np.linalg.norm(experimental_density - reference_density)
                ),
                "observable_delta_rms_exact": float(
                    np.sqrt(np.mean(exact_delta**2))
                ),
                "observable_delta_max_abs_exact": float(
                    np.max(np.abs(exact_delta))
                ),
                "observable_delta_rms_estimated": float(
                    np.sqrt(np.mean(estimated_delta**2))
                ),
                "observable_delta_max_abs_estimated": float(
                    np.max(np.abs(estimated_delta))
                ),
                "reference_tomography_error_rms": float(
                    np.sqrt(np.mean(reference_error**2))
                ),
                "reference_tomography_error_max_abs": float(
                    np.max(np.abs(reference_error))
                ),
                "experimental_tomography_error_rms": float(
                    np.sqrt(np.mean(experimental_error**2))
                ),
                "experimental_tomography_error_max_abs": float(
                    np.max(np.abs(experimental_error))
                ),
            },
            reference_density_real=reference_real,
            reference_density_imag=reference_imag,
            experimental_density_real=experimental_real,
            experimental_density_imag=experimental_imag,
        )


def save_experiment_result(
    result: RepresentationExperimentResult,
    destination: str | Path,
) -> Path:
    path = Path(destination)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(result.to_dict(), indent=2, sort_keys=False) + "\n",
        encoding="utf-8",
    )
    return path
