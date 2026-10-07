"""Local-Pauli classical shadows for four-qubit Pauli estimation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

from full4q_tomography_v1 import PAULI_LABELS

from ..adapters import FULL4Q_DIMENSION, measurement_probabilities
from ..core import (
    MeasurementProtocol,
    MeasurementRecord,
    SamplingPolicy,
    SamplingResolution,
    validate_density_matrix,
)


@dataclass(frozen=True)
class ClassicalShadowOutput:
    schema: str
    source: str
    preset: str
    transform: str
    shots: int
    seed: int
    setting_histogram: dict[str, int]
    observable_estimates: dict[str, float]


class ClassicalShadowTomography(MeasurementProtocol):
    name = "classical_shadows_local_pauli"
    description = "Random local-Pauli classical shadows over four qubits."

    def __init__(self, *, sampling: SamplingPolicy | None = None) -> None:
        super().__init__(sampling)

    def measure(
        self,
        rho: Any,
        *,
        preset: str,
        representation: str,
        shots: int,
        sampling: SamplingResolution,
        source: str,
    ) -> MeasurementRecord:
        density = validate_density_matrix(rho)
        if density.shape != (FULL4Q_DIMENSION, FULL4Q_DIMENSION):
            raise ValueError(
                "ClassicalShadowTomography requires a 16x16 density matrix"
            )
        if shots <= 0:
            raise ValueError("shots must be positive")
        random = np.random.default_rng(sampling.resolved_seed)
        axes = np.asarray(["X", "Y", "Z"])
        chosen = random.integers(0, 3, size=(shots, 4))
        outcomes = np.zeros(shots, dtype=int)
        histogram: dict[str, int] = {}
        probability_cache: dict[str, np.ndarray] = {}
        for index in range(shots):
            setting = "".join(axes[chosen[index]])
            histogram[setting] = histogram.get(setting, 0) + 1
            probabilities = probability_cache.get(setting)
            if probabilities is None:
                probabilities = measurement_probabilities(density, setting)
                probability_cache[setting] = probabilities
            outcomes[index] = int(random.choice(16, p=probabilities))

        estimates: dict[str, float] = {}
        for label in PAULI_LABELS:
            if label == "IIII":
                estimates[label] = 1.0
                continue
            support = [
                qubit for qubit, axis in enumerate(label) if axis != "I"
            ]
            total = 0.0
            for shot in range(shots):
                if any(
                    axes[chosen[shot, qubit]] != label[qubit]
                    for qubit in support
                ):
                    continue
                sign = 1.0
                for qubit in support:
                    sign *= 1.0 if not (outcomes[shot] >> qubit) & 1 else -1.0
                total += (3.0 ** len(support)) * sign
            estimates[label] = total / shots

        output = ClassicalShadowOutput(
            schema="qmw.classical_shadows.v4",
            source=source,
            preset=preset,
            transform=representation,
            shots=shots,
            seed=sampling.resolved_seed,
            setting_histogram=histogram,
            observable_estimates=estimates,
        )
        return MeasurementRecord(
            observable_estimates=estimates,
            total_shots=shots,
            output=output,
            metadata={
                "settings_observed": len(histogram),
                "observables": 255,
                "shots_total": shots,
                "shot_semantics": "total_random_snapshots",
            },
            sampling=sampling,
        )

    def metadata(self) -> dict[str, Any]:
        metadata = super().metadata()
        metadata.update(
            dimension=16,
            non_identity_observable_count=255,
            ensemble="independent_local_pauli",
            sampling_mode=self.sampling_policy.mode.value,
            shot_semantics="total_random_snapshots",
        )
        return metadata
