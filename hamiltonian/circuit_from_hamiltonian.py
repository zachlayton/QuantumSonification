import math
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector
import numpy as np


def circuit_from_hamiltonian(h):
    qc = QuantumCircuit(1)

    # Interpret Pauli weights as rotation strengths.
    qc.rx(math.pi * h.x, 0)
    qc.ry(math.pi * h.y, 0)
    qc.rz(math.pi * h.z, 0)

    return qc

def density_matrix_from_circuit(qc):
    state = Statevector.from_instruction(qc)
    psi = state.data.reshape((-1, 1))
    rho = psi @ np.conjugate(psi.T)
    return rho


def bloch_from_circuit(qc):
    state = Statevector.from_instruction(qc)

    alpha = state.data[0]
    beta = state.data[1]

    x = 2 * np.real(np.conj(alpha) * beta)
    y = 2 * np.imag(np.conj(alpha) * beta)
    z = abs(alpha) ** 2 - abs(beta) ** 2

    return float(x), float(y), float(z)