# qmw/backend/algorithms.py

from qiskit import QuantumCircuit
from .quantum_backend import QuantumBackend, QuantumResult


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
    qc = bernstein_vazirani_circuit(secret)
    counts = backend.run_counts(qc)

    # Most frequent result
    measured = max(counts, key=counts.get)

    return QuantumResult(
        algorithm="bernstein_vazirani",
        bitstring=measured,
        counts=counts,
        metadata={"secret": secret, "num_qubits": len(secret)}
    )
