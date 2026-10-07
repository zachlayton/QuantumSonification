from __future__ import annotations

from collections.abc import Sequence

import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector

from ..models import QuantumMaterialFrame
from ..operators import QMWOperator
from .base import QuantumExecutionProvider, normalized_probabilities, validate_observables


class StatevectorProvider(QuantumExecutionProvider):
    def __init__(self, *, seed: int | None = None) -> None:
        self.seed = seed

    def run_expectations(
        self, circuit: QuantumCircuit, observables: Sequence[QMWOperator], *, time: float = 0.0
    ) -> QuantumMaterialFrame:
        validate_observables(circuit, observables)
        state = Statevector.from_instruction(circuit.remove_final_measurements(inplace=False))
        expectations = {
            op.name: float(np.real_if_close(state.expectation_value(op.to_sparse_pauli_op())))
            for op in observables
        }
        variances = {
            op.name: float(
                np.real_if_close(
                    state.expectation_value(op.to_sparse_pauli_op() @ op.to_sparse_pauli_op())
                    - expectations[op.name] ** 2
                )
            )
            for op in observables
        }
        return QuantumMaterialFrame(
            time=time,
            expectations=expectations,
            variances=variances,
            backend={"provider": "statevector", "ideal": True, "shots": None},
        )

    def run_samples(
        self, circuit: QuantumCircuit, *, shots: int = 1024, time: float = 0.0
    ) -> QuantumMaterialFrame:
        if shots < 1:
            raise ValueError("shots must be positive")
        state = Statevector.from_instruction(circuit.remove_final_measurements(inplace=False))
        if self.seed is not None:
            state.seed(self.seed)
        counts = {str(k): int(v) for k, v in state.sample_counts(shots).items()}
        return QuantumMaterialFrame(
            time=time,
            samples=counts,
            backend={
                "provider": "statevector", "ideal": True, "shots": shots,
                "probabilities": normalized_probabilities(counts, shots),
            },
        )
