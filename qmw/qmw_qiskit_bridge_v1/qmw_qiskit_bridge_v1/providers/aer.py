from __future__ import annotations

from collections.abc import Sequence

from qiskit import QuantumCircuit, transpile

from ..models import QuantumMaterialFrame
from ..operators import QMWOperator
from .base import QuantumExecutionProvider, normalized_probabilities, validate_observables


class AerProvider(QuantumExecutionProvider):
    """Shot-based Aer provider; the same noise model is used for both routes."""

    def __init__(self, *, noise_model=None, shots: int = 4096, seed: int | None = None) -> None:
        try:
            from qiskit_aer import AerSimulator
        except ImportError as exc:
            raise ImportError("AerProvider requires qiskit-aer") from exc
        if shots < 1:
            raise ValueError("shots must be positive")
        self.shots = shots
        self.seed = seed
        self.backend = AerSimulator(noise_model=noise_model)
        self.noise_model = noise_model

    def _counts(self, circuit: QuantumCircuit, shots: int) -> dict[str, int]:
        measured = circuit.remove_final_measurements(inplace=False)
        measured.measure_all()
        compiled = transpile(measured, self.backend)
        result = self.backend.run(compiled, shots=shots, seed_simulator=self.seed).result()
        return {str(k).replace(" ", ""): int(v) for k, v in result.get_counts().items()}

    def run_samples(
        self, circuit: QuantumCircuit, *, shots: int = 1024, time: float = 0.0
    ) -> QuantumMaterialFrame:
        if shots < 1:
            raise ValueError("shots must be positive")
        counts = self._counts(circuit, shots)
        return QuantumMaterialFrame(
            time=time,
            samples=counts,
            backend={
                "provider": "aer", "ideal": self.noise_model is None, "shots": shots,
                "probabilities": normalized_probabilities(counts, shots),
            },
        )

    def run_expectations(
        self, circuit: QuantumCircuit, observables: Sequence[QMWOperator], *, time: float = 0.0
    ) -> QuantumMaterialFrame:
        validate_observables(circuit, observables)
        expectations: dict[str, float] = {}
        variances: dict[str, float] = {}
        # AerEstimatorV2 handles shot grouping and non-diagonal measurement bases.
        from qiskit_aer.primitives import EstimatorV2

        estimator = EstimatorV2(
            options={
                "backend_options": {"noise_model": self.noise_model},
                "run_options": {"shots": self.shots, "seed_simulator": self.seed},
            }
        )
        pubs = [(circuit, [op.to_sparse_pauli_op() for op in observables])]
        datum = estimator.run(pubs).result()[0].data
        for index, op in enumerate(observables):
            expectations[op.name] = float(datum.evs[index])
            variances[op.name] = float(datum.stds[index] ** 2)
        return QuantumMaterialFrame(
            time=time,
            expectations=expectations,
            variances=variances,
            backend={
                "provider": "aer", "ideal": self.noise_model is None, "shots": self.shots,
            },
        )
