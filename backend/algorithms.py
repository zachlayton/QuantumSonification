# qmw/backend/algorithms.py

from dataclasses import dataclass, field
from qiskit import QuantumCircuit
from .qmw_backend import QuantumBackend


@dataclass
class QuantumResult:
    algorithm: str
    bitstring: str
    counts: dict
    metadata: dict = field(default_factory=dict)


def bernstein_vazirani_circuit(secret: str) -> QuantumCircuit:
    """
    secret: binary string, e.g. "10110110"
    Returns a Bernstein-Vazirani circuit.
    """
    n = len(secret)
    qc = QuantumCircuit(n + 1, n)

    answer = n

    qc.x(answer)
    qc.h(answer)

    for q in range(n):
        qc.h(q)

    # Oracle: if secret bit is 1, CNOT input q -> answer
    # Reverse bit order so written string maps musically left-to-right.
    for q, bit in enumerate(reversed(secret)):
        if bit == "1":
            qc.cx(q, answer)

    for q in range(n):
        qc.h(q)

    for q in range(n):
        qc.measure(q, q)

    return qc


def run_bernstein_vazirani(secret: str, backend: QuantumBackend) -> QuantumResult:
    measured, counts = backend.bernstein_vazirani(secret)

    return QuantumResult(
        algorithm="bernstein_vazirani",
        bitstring=measured,
        counts=counts,
        metadata={"secret": secret, "num_qubits": len(secret)}
    )
