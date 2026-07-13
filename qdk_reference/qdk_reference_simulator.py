"""Independent NumPy reference simulator for the QDK 4q/16-step circuit.

Purpose
-------
Validate the circuit semantics used by the live MLX density-matrix engine.
It does not send OSC and should never sit in the audio/control-rate loop.

Convention
----------
Qubit 0 is the most-significant tensor factor:
    |q0 q1 q2 q3>
Thus the state-vector index is q0*8 + q1*4 + q2*2 + q3.
Keep this convention aligned with the MLX engine before using comparisons.
"""

from __future__ import annotations
import numpy as np

N_QUBITS = 4
DIM = 2 ** N_QUBITS

# One record per visible QASM operation. Step numbers are canonical.
CIRCUIT_SCORE = (
    ("h",  (0,),       None),
    ("ry", (1,),       0.37),
    ("rx", (2,),      -0.51),
    ("rz", (3,),       0.29),
    ("cx", (0, 1),     None),
    ("rz", (1,),       0.73),
    ("cx", (1, 2),     None),
    ("ry", (2,),      -0.44),
    ("cx", (2, 3),     None),
    ("rx", (3,),       0.61),
    ("cz", (3, 0),     None),
    ("ry", (0,),       0.22),
    ("cx", (0, 2),     None),
    ("rz", (2,),      -0.68),
    ("cx", (1, 3),     None),
    ("h",  (3,),       None),
)

I2 = np.eye(2, dtype=np.complex128)
X = np.array([[0, 1], [1, 0]], dtype=np.complex128)
Z = np.array([[1, 0], [0, -1]], dtype=np.complex128)
H = np.array([[1, 1], [1, -1]], dtype=np.complex128) / np.sqrt(2.0)


def rx(theta: float) -> np.ndarray:
    return np.cos(theta / 2) * I2 - 1j * np.sin(theta / 2) * X


def ry(theta: float) -> np.ndarray:
    return np.array(
        [[np.cos(theta / 2), -np.sin(theta / 2)],
         [np.sin(theta / 2),  np.cos(theta / 2)]],
        dtype=np.complex128,
    )


def rz(theta: float) -> np.ndarray:
    return np.array(
        [[np.exp(-0.5j * theta), 0],
         [0, np.exp(0.5j * theta)]],
        dtype=np.complex128,
    )


def _bit(index: int, qubit: int) -> int:
    """Extract q[qubit] using QASM-style q0 as the most-significant bit."""
    return (index >> (N_QUBITS - 1 - qubit)) & 1


def single_qubit_unitary(gate: np.ndarray, target: int) -> np.ndarray:
    factors = [gate if q == target else I2 for q in range(N_QUBITS)]
    result = factors[0]
    for factor in factors[1:]:
        result = np.kron(result, factor)
    return result


def controlled_unitary(control: int, target: int, target_gate: np.ndarray) -> np.ndarray:
    unitary = np.zeros((DIM, DIM), dtype=np.complex128)
    for col in range(DIM):
        if _bit(col, control) == 0:
            unitary[col, col] = 1.0
            continue
        input_bits = [_bit(col, q) for q in range(N_QUBITS)]
        in_target = input_bits[target]
        for out_target in (0, 1):
            coefficient = target_gate[out_target, in_target]
            if coefficient == 0:
                continue
            output_bits = input_bits.copy()
            output_bits[target] = out_target
            row = sum(bit << (N_QUBITS - 1 - q) for q, bit in enumerate(output_bits))
            unitary[row, col] += coefficient
    return unitary


def cz_unitary(control: int, target: int) -> np.ndarray:
    diagonal = np.ones(DIM, dtype=np.complex128)
    for index in range(DIM):
        if _bit(index, control) and _bit(index, target):
            diagonal[index] = -1.0
    return np.diag(diagonal)


def gate_unitary(name: str, qubits: tuple[int, ...], parameter: float | None) -> np.ndarray:
    if name == "h":
        return single_qubit_unitary(H, qubits[0])
    if name == "rx":
        return single_qubit_unitary(rx(float(parameter)), qubits[0])
    if name == "ry":
        return single_qubit_unitary(ry(float(parameter)), qubits[0])
    if name == "rz":
        return single_qubit_unitary(rz(float(parameter)), qubits[0])
    if name == "cx":
        return controlled_unitary(qubits[0], qubits[1], X)
    if name == "cz":
        return cz_unitary(qubits[0], qubits[1])
    raise ValueError(f"Unsupported gate: {name}")


def reference_density_matrix(
    score: tuple = CIRCUIT_SCORE,
    return_history: bool = False,
) -> np.ndarray | tuple[np.ndarray, list[np.ndarray]]:
    """Return rho after the 16 unitary steps, optionally including every step."""
    state = np.zeros(DIM, dtype=np.complex128)
    state[0] = 1.0  # |0000>
    history: list[np.ndarray] = [np.outer(state, state.conj())]

    for name, qubits, parameter in score:
        state = gate_unitary(name, qubits, parameter) @ state
        history.append(np.outer(state, state.conj()))

    rho = history[-1]
    return (rho, history) if return_history else rho


def density_metrics(rho: np.ndarray) -> dict[str, float]:
    """Minimal invariant checks for comparing simulators."""
    eigenvalues = np.linalg.eigvalsh((rho + rho.conj().T) / 2)
    positive = np.clip(eigenvalues.real, 0.0, 1.0)

    nonzero = positive[positive > 1e-15]
    entropy = -np.sum(nonzero * np.log2(nonzero))

    return {
        "trace_real": float(np.trace(rho).real),
        "purity": float(np.trace(rho @ rho).real),
        "von_neumann_entropy": float(entropy),
        "max_hermiticity_error": float(np.max(np.abs(rho - rho.conj().T))),
    }

def partial_trace(rho: np.ndarray, keep: tuple[int, ...]) -> np.ndarray:
    """
    Return the reduced density matrix for the qubits listed in `keep`.

    Example:
        partial_trace(rho, (0,))   -> 2x2 rho for q0
        partial_trace(rho, (0, 2)) -> 4x4 rho for q0-q2
    """
    keep = tuple(sorted(keep))

    if not keep:
        raise ValueError("keep must contain at least one qubit.")

    if any(q < 0 or q >= N_QUBITS for q in keep):
        raise ValueError(f"Qubits must be in range 0 to {N_QUBITS - 1}.")

    tensor = rho.reshape([2] * (2 * N_QUBITS))

    # Bra indices: 0, 1, 2, 3
    # Ket indices: 4, 5, 6, 7
    #
    # For traced-out qubits, bra and ket use the same einsum label.
    # For retained qubits, bra and ket remain independent.
    input_labels = list(range(N_QUBITS))

    for q in range(N_QUBITS):
        if q in keep:
            input_labels.append(q + N_QUBITS)
        else:
            input_labels.append(q)

    output_labels = list(keep) + [q + N_QUBITS for q in keep]

    reduced = np.einsum(tensor, input_labels, output_labels)

    dim = 2 ** len(keep)
    return reduced.reshape(dim, dim)


def partial_trace_one_qubit(rho: np.ndarray, keep: int) -> np.ndarray:
    """Return the 2x2 reduced density matrix for one qubit."""
    return partial_trace(rho, (keep,))


def entropy_from_density_matrix(rho: np.ndarray) -> float:
    """Von Neumann entropy in bits."""
    hermitian_rho = (rho + rho.conj().T) / 2
    eigenvalues = np.linalg.eigvalsh(hermitian_rho)

    positive = np.clip(eigenvalues.real, 0.0, 1.0)
    nonzero = positive[positive > 1e-15]

    return float(-np.sum(nonzero * np.log2(nonzero)))



def pairwise_mutual_information(
    rho: np.ndarray,
    qubit_a: int,
    qubit_b: int,
) -> float:
    """
    Mutual information I(A:B) in bits.

    I(A:B) = S(A) + S(B) - S(AB)

    This measures total pairwise correlation:
    classical correlation plus quantum correlation.
    """
    rho_a = partial_trace(rho, (qubit_a,))
    rho_b = partial_trace(rho, (qubit_b,))
    rho_ab = partial_trace(rho, (qubit_a, qubit_b))

    mutual_info = (
        entropy_from_density_matrix(rho_a)
        + entropy_from_density_matrix(rho_b)
        - entropy_from_density_matrix(rho_ab)
    )

    # Remove tiny negative floating-point artifacts.
    return float(max(0.0, mutual_info))


def all_pairwise_mutual_information(rho: np.ndarray) -> dict[str, float]:
    """Return mutual information for all six pairs in a four-qubit system."""
    pairs = (
        (0, 1),
        (0, 2),
        (0, 3),
        (1, 2),
        (1, 3),
        (2, 3),
    )

    return {
        f"{a}{b}": pairwise_mutual_information(rho, a, b)
        for a, b in pairs
    }


def qubit_bloch_vector(rho: np.ndarray, qubit: int) -> dict[str, float]:
    """Bloch vector of one reduced qubit state."""
    reduced = partial_trace_one_qubit(rho, qubit)

    return {
        "x": float(np.trace(reduced @ X).real),
        "y": float(np.trace(reduced @ np.array([[0, -1j], [1j, 0]])).real),
        "z": float(np.trace(reduced @ Z).real),
    }


def reduced_entropy(rho: np.ndarray, qubit: int) -> float:
    """Von Neumann entropy of a single reduced qubit."""
    reduced = partial_trace_one_qubit(rho, qubit)
    eigvals = np.linalg.eigvalsh((reduced + reduced.conj().T) / 2)
    positive = np.clip(eigvals.real, 0.0, 1.0)
    nonzero = positive[positive > 1e-15]
    return float(-np.sum(nonzero * np.log2(nonzero)))


def basis_populations(rho: np.ndarray) -> np.ndarray:
    """Computational-basis populations from the density-matrix diagonal."""
    return np.real(np.diag(rho))


def print_step_diagnostics(history: list[np.ndarray]) -> None:
    """Print compact diagnostics for all 16 circuit steps."""
    print("\nStep diagnostics:")

    for step, rho in enumerate(history):
        if step == 0:
            gate_label = "initial |0000>"
        else:
            name, qubits, parameter = CIRCUIT_SCORE[step - 1]
            gate_label = f"{name} {qubits}"
            if parameter is not None:
                gate_label += f" ({parameter:+.3f})"

        populations = basis_populations(rho)
        top_index = int(np.argmax(populations))
        top_population = float(populations[top_index])

        entropies = [reduced_entropy(rho, q) for q in range(N_QUBITS)]
        bloch = [qubit_bloch_vector(rho, q) for q in range(N_QUBITS)]
        pairwise_mi = all_pairwise_mutual_information(rho)

        entropy_text = " ".join(
            f"q{q}={entropies[q]:.4f}"
            for q in range(N_QUBITS)
        )

        mi_text = " ".join(
            f"{pair}={value:.4f}"
            for pair, value in pairwise_mi.items()
        )

        bloch_text = ", ".join(
            f"{axis}={bloch[0][axis]:+.4f}"
            for axis in ("x", "y", "z")
        )

        print(
            f"\n{step:02d}  {gate_label}"
            f"\n    dominant basis state: |{top_index:04b}>"
            f"  population={top_population:.4f}"
            f"\n    one-qubit entropies: {entropy_text}"
            f"\n    pairwise MI: {mi_text}"
            f"\n    q0 Bloch: {bloch_text}"
        )



if __name__ == "__main__":
    rho, history = reference_density_matrix(return_history=True)

    print("Final invariant checks:")
    for key, value in density_metrics(rho).items():
        print(f"{key}: {value:.12f}")

    print_step_diagnostics(history)
