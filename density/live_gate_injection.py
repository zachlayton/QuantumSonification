"""Validated unitary gate transformations for a live four-qubit density state."""
from __future__ import annotations

from collections.abc import Sequence

import numpy as np

from density.density_state_injection import validate_density_matrix


I2 = np.eye(2, dtype=np.complex128)
X = np.array([[0, 1], [1, 0]], dtype=np.complex128)
Y = np.array([[0, -1j], [1j, 0]], dtype=np.complex128)
Z = np.array([[1, 0], [0, -1]], dtype=np.complex128)
H = np.array([[1, 1], [1, -1]], dtype=np.complex128) / np.sqrt(2.0)
S = np.array([[1, 0], [0, 1j]], dtype=np.complex128)
T = np.array([[1, 0], [0, np.exp(1j * np.pi / 4)]], dtype=np.complex128)

SINGLE_QUBIT_GATES = {
    "i": I2,
    "id": I2,
    "h": H,
    "x": X,
    "y": Y,
    "z": Z,
    "s": S,
    "t": T,
}


def _local_operator(gate: np.ndarray, qubit: int, n_qubits: int) -> np.ndarray:
    """Build an operator in engine order, where logical q0 is the MSB axis."""
    factors = [gate if axis == qubit else I2 for axis in range(n_qubits)]
    result = factors[0]
    for factor in factors[1:]:
        result = np.kron(result, factor)
    return result


def _controlled_x(control: int, target: int, n_qubits: int) -> np.ndarray:
    dimension = 1 << n_qubits
    result = np.zeros((dimension, dimension), dtype=np.complex128)
    control_mask = 1 << (n_qubits - 1 - control)
    target_mask = 1 << (n_qubits - 1 - target)
    for column in range(dimension):
        row = column ^ target_mask if column & control_mask else column
        result[row, column] = 1.0
    return result


def gate_unitary(
    name: str,
    qubits: Sequence[int],
    *,
    n_qubits: int = 4,
) -> np.ndarray:
    """Return a supported gate unitary using logical QAC/engine qubit labels."""
    gate = str(name).strip().lower()
    targets = tuple(int(qubit) for qubit in qubits)
    if any(qubit < 0 or qubit >= n_qubits for qubit in targets):
        raise ValueError(f"Gate qubits out of range for {n_qubits} qubits: {targets}")
    if gate in SINGLE_QUBIT_GATES:
        if len(targets) != 1:
            raise ValueError(f"Gate {gate} requires one qubit")
        return _local_operator(SINGLE_QUBIT_GATES[gate], targets[0], n_qubits)
    if gate in {"cx", "cnot"}:
        if len(targets) != 2 or targets[0] == targets[1]:
            raise ValueError("Gate cx requires distinct control and target qubits")
        return _controlled_x(targets[0], targets[1], n_qubits)
    raise ValueError(f"Unsupported live gate: {name}")


def apply_live_gate(
    rho: np.ndarray,
    name: str,
    qubits: Sequence[int],
    *,
    n_qubits: int = 4,
) -> tuple[np.ndarray, float]:
    """Apply ``U rho U†`` and return the validated state and change magnitude."""
    dimension = 1 << n_qubits
    before = validate_density_matrix(rho, dimension=dimension)
    unitary = gate_unitary(name, qubits, n_qubits=n_qubits)
    after = unitary @ before @ unitary.conj().T
    after = validate_density_matrix(after, dimension=dimension)
    return after, float(np.linalg.norm(after - before))
