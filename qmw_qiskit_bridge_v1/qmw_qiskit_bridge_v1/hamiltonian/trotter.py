from __future__ import annotations

from collections.abc import Iterable, Sequence

from qiskit import QuantumCircuit
from qiskit.circuit.library import PauliEvolutionGate
from qiskit.synthesis import LieTrotter, SuzukiTrotter

from ..models import QuantumMaterialFrame
from ..operators import QMWOperator
from ..providers.base import QuantumExecutionProvider


def trotter_circuit(
    hamiltonian: QMWOperator,
    time: float,
    *,
    initial_circuit: QuantumCircuit | None = None,
    order: int = 2,
    reps: int = 1,
) -> QuantumCircuit:
    if time < 0:
        raise ValueError("time must be non-negative")
    if order < 1 or (order > 1 and order % 2):
        raise ValueError("Suzuki order must be 1 or a positive even integer")
    if reps < 1:
        raise ValueError("reps must be positive")
    circuit = (
        initial_circuit.copy()
        if initial_circuit is not None
        else QuantumCircuit(hamiltonian.n_qubits)
    )
    if circuit.num_qubits != hamiltonian.n_qubits:
        raise ValueError("initial circuit width must equal Hamiltonian width")
    if time:
        synthesis = (
            LieTrotter(reps=reps, preserve_order=True)
            if order == 1
            else SuzukiTrotter(order=order, reps=reps, preserve_order=True)
        )
        circuit.append(PauliEvolutionGate(hamiltonian.to_sparse_pauli_op(), time, synthesis=synthesis), range(circuit.num_qubits))
    return circuit


def expectation_trajectory(
    provider: QuantumExecutionProvider,
    hamiltonian: QMWOperator,
    observables: Sequence[QMWOperator],
    times: Iterable[float],
    *,
    initial_circuit: QuantumCircuit | None = None,
    order: int = 2,
    reps: int = 1,
) -> tuple[QuantumMaterialFrame, ...]:
    return tuple(
        provider.run_expectations(
            trotter_circuit(
                hamiltonian, float(time), initial_circuit=initial_circuit,
                order=order, reps=reps,
            ),
            observables,
            time=float(time),
        )
        for time in times
    )
