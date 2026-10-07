from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Mapping, Sequence

from qiskit import QuantumCircuit

from ..models import QuantumMaterialFrame
from ..operators import QMWOperator


class QuantumExecutionProvider(ABC):
    """Stable provider contract; concrete backends may be local or remote."""

    @abstractmethod
    def run_expectations(
        self,
        circuit: QuantumCircuit,
        observables: Sequence[QMWOperator],
        *,
        time: float = 0.0,
    ) -> QuantumMaterialFrame: ...

    @abstractmethod
    def run_samples(
        self,
        circuit: QuantumCircuit,
        *,
        shots: int = 1024,
        time: float = 0.0,
    ) -> QuantumMaterialFrame: ...


def validate_observables(circuit: QuantumCircuit, observables: Sequence[QMWOperator]) -> None:
    if not observables:
        raise ValueError("at least one observable is required")
    if any(op.n_qubits != circuit.num_qubits for op in observables):
        raise ValueError("observable width must equal circuit.num_qubits")


def normalized_probabilities(counts: Mapping[str, int], shots: int) -> dict[str, float]:
    return {key: value / shots for key, value in counts.items()}
