from __future__ import annotations

import numpy as np

from qmw.core.quantum_frame import QuantumFrame

I2 = np.eye(2, dtype=complex)
X = np.array([[0, 1], [1, 0]], dtype=complex)
Y = np.array([[0, -1j], [1j, 0]], dtype=complex)
Z = np.array([[1, 0], [0, -1]], dtype=complex)

NQ = 4
DIM = 2 ** NQ


def kron_all(ops):
    out = np.array([[1.0 + 0.0j]])
    for op in ops:
        out = np.kron(out, op)
    return out


def op_on_qubit(op, site):
    ops = [I2] * NQ
    ops[site] = op
    return kron_all(ops)


Xq = [op_on_qubit(X, i) for i in range(NQ)]
Yq = [op_on_qubit(Y, i) for i in range(NQ)]
Zq = [op_on_qubit(Z, i) for i in range(NQ)]
Nq = [(np.eye(DIM, dtype=complex) - Zq[i]) / 2 for i in range(NQ)]


def ket(bitstring: str) -> np.ndarray:
    if len(bitstring) != NQ or any(c not in "01" for c in bitstring):
        raise ValueError("bitstring must contain four bits")
    v = np.zeros(DIM, dtype=complex)
    v[int(bitstring, 2)] = 1.0
    return v


def build_hamiltonian(omega=None, J=None) -> np.ndarray:
    omega = np.ones(4) if omega is None else np.asarray(omega, dtype=float)
    J = np.ones(3) if J is None else np.asarray(J, dtype=float)

    H = np.zeros((DIM, DIM), dtype=complex)
    for i in range(4):
        H += 0.5 * omega[i] * Zq[i]
    for i in range(3):
        H += 0.5 * J[i] * (Xq[i] @ Xq[i+1] + Yq[i] @ Yq[i+1])
    return H


def expectation(states, operator):
    return np.real(np.einsum("ti,ij,tj->t", states.conj(), operator, states))


def run_xy_quantum_frame(
    omega=None,
    J=None,
    duration: float = 12.0,
    samples: int = 2048,
    initial: str = "1000",
) -> QuantumFrame:
    omega = np.ones(4) if omega is None else np.asarray(omega, dtype=float)
    J = np.ones(3) if J is None else np.asarray(J, dtype=float)

    H = build_hamiltonian(omega, J)
    t = np.linspace(0.0, duration, samples)
    psi0 = ket(initial)

    # Exact unitary evolution from Hermitian eigendecomposition.
    evals, evecs = np.linalg.eigh(H)
    coeff = evecs.conj().T @ psi0
    phases = np.exp(-1j * np.outer(t, evals))
    psi = (phases * coeff[None, :]) @ evecs.T
    rho = np.einsum("ti,tj->tij", psi, psi.conj())

    populations = np.column_stack([expectation(psi, Nq[i]) for i in range(4)])
    pauli_x = np.column_stack([expectation(psi, Xq[i]) for i in range(4)])
    pauli_y = np.column_stack([expectation(psi, Yq[i]) for i in range(4)])
    pauli_z = np.column_stack([expectation(psi, Zq[i]) for i in range(4)])

    # Single-excitation amplitudes in spatial order q0 -> q3.
    single_exc_indices = [8, 4, 2, 1]
    amps = psi[:, single_exc_indices]
    currents = np.zeros((samples, 3), dtype=float)
    for i in range(3):
        currents[:, i] = 2.0 * J[i] * np.imag(np.conj(amps[:, i]) * amps[:, i + 1])

    energy = np.real(np.einsum("ti,ij,tj->t", psi.conj(), H, psi))

    comm = H[None, :, :] @ rho - rho @ H[None, :, :]
    activity = np.linalg.norm(comm.reshape(samples, -1), axis=1)

    return QuantumFrame(
        t=t,
        psi=psi,
        rho=rho,
        observables={
            "site_populations": populations,
            "pauli_x": pauli_x,
            "pauli_y": pauli_y,
            "pauli_z": pauli_z,
            "edge_currents": currents,
        },
        diagnostics={
            "energy": energy,
            "commutator_activity": activity,
            "hamiltonian_eigenvalues": evals,
        },
        metadata={
            "model": "four_qubit_xy_chain",
            "backend": "numpy_exact_eigendecomposition",
            "initial_state": initial,
            "omega": omega.copy(),
            "J": J.copy(),
            "samples": samples,
            "duration": duration,
            "hbar": 1.0,
        },
    )
