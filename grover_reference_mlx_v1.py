"""Exact statevector Grover search implemented with MLX.

Computational-basis labels follow Qiskit's convention: for ``n`` qubits,
``|q[n-1] ... q[0]>`` is converted directly to its integer basis index.
The simulator is exact in the statevector sense (there is no shot sampling),
with numerical precision determined by MLX's complex64 dtype.
"""

from __future__ import annotations

import argparse
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Sequence

import mlx.core as mx
import numpy as np


BasisState = int | str


@dataclass(frozen=True)
class GroverResult:
    """Statevector history and metrics from one Grover run.

    ``states[0]`` is the uniform superposition before any Grover iteration;
    ``states[k]`` is the state after ``k`` oracle/diffusion pairs.
    """

    n_qubits: int
    marked_indices: tuple[int, ...]
    iterations: int
    states: tuple[Any, ...]
    marked_probabilities: tuple[float, ...]

    @property
    def final_state(self) -> Any:
        return self.states[-1]

    @property
    def success_probability(self) -> float:
        return self.marked_probabilities[-1]


def basis_index(state: BasisState, n_qubits: int) -> int:
    """Validate a basis-state label and return its integer index."""
    if n_qubits < 1:
        raise ValueError("n_qubits must be at least 1")

    dimension = 1 << n_qubits
    if isinstance(state, bool):
        raise TypeError("a marked state must be an integer or binary string")
    if isinstance(state, int):
        index = state
    elif isinstance(state, str):
        if len(state) != n_qubits or any(bit not in "01" for bit in state):
            raise ValueError(
                f"binary state labels must contain exactly {n_qubits} bits"
            )
        index = int(state, 2)
    else:
        raise TypeError("a marked state must be an integer or binary string")

    if not 0 <= index < dimension:
        raise ValueError(f"basis-state index must be in [0, {dimension})")
    return index


def _marked_indices(
    marked_states: BasisState | Iterable[BasisState], n_qubits: int
) -> tuple[int, ...]:
    if isinstance(marked_states, (int, str)) and not isinstance(marked_states, bool):
        raw_states: Sequence[BasisState] = (marked_states,)
    else:
        try:
            raw_states = tuple(marked_states)  # type: ignore[arg-type]
        except TypeError as exc:
            raise TypeError(
                "marked_states must be a state or a non-empty iterable of states"
            ) from exc

    indices = tuple(sorted({basis_index(state, n_qubits) for state in raw_states}))
    if not indices:
        raise ValueError("at least one marked state is required")
    if len(indices) == 1 << n_qubits:
        raise ValueError("Grover search requires at least one unmarked state")
    return indices


def uniform_state(n_qubits: int) -> Any:
    """Return |s>, the uniform superposition over all basis states."""
    if n_qubits < 1:
        raise ValueError("n_qubits must be at least 1")
    dimension = 1 << n_qubits
    return mx.ones((dimension,), dtype=mx.complex64) / math.sqrt(dimension)


def oracle_operator(
    n_qubits: int, marked_states: BasisState | Iterable[BasisState]
) -> Any:
    """Return the phase oracle I - 2 * sum(|marked><marked|)."""
    indices = set(_marked_indices(marked_states, n_qubits))
    phases = [-1.0 if index in indices else 1.0 for index in range(1 << n_qubits)]
    # MLX Metal's diagonal scatter kernel currently accepts real but not
    # complex updates. Build this real-valued reflection first, then promote
    # the completed operator for complex statevector evolution.
    return mx.diag(mx.array(phases, dtype=mx.float32)).astype(mx.complex64)


def oracle_phases(
    n_qubits: int, marked_states: BasisState | Iterable[BasisState]
) -> Any:
    """Return the oracle's diagonal for memory-efficient state evolution."""
    indices = set(_marked_indices(marked_states, n_qubits))
    phases = [-1.0 if index in indices else 1.0 for index in range(1 << n_qubits)]
    return mx.array(phases, dtype=mx.complex64)


def diffusion_operator(n_qubits: int) -> Any:
    """Return the inversion-about-the-mean operator 2|s><s| - I."""
    if n_qubits < 1:
        raise ValueError("n_qubits must be at least 1")
    dimension = 1 << n_qubits
    projector = mx.ones((dimension, dimension), dtype=mx.float32) / dimension
    reflection = 2.0 * projector - mx.eye(dimension, dtype=mx.float32)
    return reflection.astype(mx.complex64)


def optimal_iteration_count(n_qubits: int, n_marked: int = 1) -> int:
    """Return the non-negative integer nearest Grover's first maximum."""
    if n_qubits < 1:
        raise ValueError("n_qubits must be at least 1")
    dimension = 1 << n_qubits
    if not 1 <= n_marked < dimension:
        raise ValueError(f"n_marked must be in [1, {dimension})")
    theta = math.asin(math.sqrt(n_marked / dimension))
    return max(0, int(math.floor(math.pi / (4.0 * theta))))


def theoretical_success_probability(
    n_qubits: int, n_marked: int, iterations: int
) -> float:
    """Return sin^2((2k + 1) theta), the ideal Grover probability."""
    if iterations < 0:
        raise ValueError("iterations must be non-negative")
    dimension = 1 << n_qubits
    if not 1 <= n_marked < dimension:
        raise ValueError(f"n_marked must be in [1, {dimension})")
    theta = math.asin(math.sqrt(n_marked / dimension))
    return math.sin((2 * iterations + 1) * theta) ** 2


def run_grover(
    n_qubits: int,
    marked_states: BasisState | Iterable[BasisState],
    iterations: int | None = None,
) -> GroverResult:
    """Run exact Grover amplitude amplification and retain every state."""
    indices = _marked_indices(marked_states, n_qubits)
    if iterations is None:
        iterations = optimal_iteration_count(n_qubits, len(indices))
    if isinstance(iterations, bool) or not isinstance(iterations, int):
        raise TypeError("iterations must be an integer or None")
    if iterations < 0:
        raise ValueError("iterations must be non-negative")

    phases = oracle_phases(n_qubits, indices)
    state = uniform_state(n_qubits)
    mx.eval(phases, state)

    states = [state]
    probabilities = [_success_probability(state, indices)]
    for _ in range(iterations):
        # O(N) matrix-free form of D O |psi>: the phase oracle is diagonal,
        # and D|psi> = 2 mean(psi) - |psi>. This is exactly equivalent to
        # multiplying by the explicit 2|s><s| - I matrix without its O(N^2)
        # storage cost, allowing reference runs well beyond small qubit counts.
        oracle_state = phases * state
        state = 2.0 * mx.mean(oracle_state) - oracle_state
        mx.eval(state)
        states.append(state)
        probabilities.append(_success_probability(state, indices))

    return GroverResult(
        n_qubits=n_qubits,
        marked_indices=indices,
        iterations=iterations,
        states=tuple(states),
        marked_probabilities=tuple(probabilities),
    )


def _success_probability(state: Any, marked_indices: Sequence[int]) -> float:
    probabilities = mx.abs(state) ** 2
    mx.eval(probabilities)
    values = np.asarray(probabilities)
    return float(np.sum(values[list(marked_indices)], dtype=np.float64))


def qiskit_reference_statevector(
    n_qubits: int,
    marked_states: BasisState | Iterable[BasisState],
    iterations: int,
) -> np.ndarray:
    """Build and simulate the same operators using Qiskit's Statevector."""
    try:
        from qiskit import QuantumCircuit
        from qiskit.quantum_info import Statevector
    except ImportError as exc:  # pragma: no cover - environment dependent
        raise ImportError(
            "Qiskit comparison requires qiskit; install it with `pip install qiskit`."
        ) from exc

    if iterations < 0:
        raise ValueError("iterations must be non-negative")
    indices = _marked_indices(marked_states, n_qubits)
    dimension = 1 << n_qubits
    oracle = np.eye(dimension, dtype=np.complex128)
    oracle[list(indices), list(indices)] = -1.0
    uniform = np.full(dimension, 1.0 / math.sqrt(dimension), dtype=np.complex128)
    diffusion = 2.0 * np.outer(uniform, uniform.conj()) - np.eye(dimension)

    circuit = QuantumCircuit(n_qubits, name="Grover_reference")
    circuit.h(range(n_qubits))
    for step in range(iterations):
        circuit.unitary(oracle, range(n_qubits), label=f"Oracle {step + 1}")
        circuit.unitary(diffusion, range(n_qubits), label=f"Diffusion {step + 1}")
    return np.asarray(Statevector.from_instruction(circuit).data, dtype=np.complex128)


def compare_with_qiskit(result: GroverResult) -> dict[str, float]:
    """Compare the final MLX state with Qiskit, accounting for global phase."""
    reference = qiskit_reference_statevector(
        result.n_qubits, result.marked_indices, result.iterations
    )
    candidate = np.asarray(result.final_state, dtype=np.complex128)
    overlap = np.vdot(reference, candidate)
    fidelity = float(abs(overlap) ** 2)
    if abs(overlap) > 0.0:
        candidate = candidate * np.exp(-1j * np.angle(overlap))
    return {
        "state_fidelity": fidelity,
        "max_amplitude_error": float(np.max(np.abs(reference - candidate))),
        "probability_l1_error": float(
            np.sum(np.abs(np.abs(reference) ** 2 - np.abs(candidate) ** 2))
        ),
    }


def plot_amplitude_amplification(
    result: GroverResult, output_path: str | Path
) -> Path:
    """Render marked probability and all basis probabilities over iterations."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    probability_history = np.stack(
        [np.abs(np.asarray(state, dtype=np.complex128)) ** 2 for state in result.states]
    )
    steps = np.arange(result.iterations + 1)

    figure, (axis_total, axis_basis) = plt.subplots(
        2, 1, figsize=(10, 7), constrained_layout=True, height_ratios=(1.0, 1.35)
    )
    axis_total.plot(
        steps,
        result.marked_probabilities,
        color="#d1495b",
        marker="o",
        linewidth=2.4,
        label="marked-state probability",
    )
    axis_total.set(title="Grover amplitude amplification", ylabel="probability")
    axis_total.set_ylim(-0.025, 1.025)
    axis_total.grid(alpha=0.25)
    axis_total.legend(loc="best")

    image = axis_basis.imshow(
        probability_history.T,
        origin="lower",
        aspect="auto",
        interpolation="nearest",
        cmap="magma",
        vmin=0.0,
        vmax=float(np.max(probability_history)),
    )
    axis_basis.set(
        xlabel="Grover iteration",
        ylabel="basis-state index",
        xticks=steps,
        title="Computational-basis probability distribution",
    )
    figure.colorbar(image, ax=axis_basis, label="probability")
    figure.savefig(output, dpi=160)
    plt.close(figure)
    return output


def _parse_cli_state(label: str, n_qubits: int) -> BasisState:
    if len(label) == n_qubits and set(label) <= {"0", "1"}:
        return label
    try:
        return int(label)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            f"{label!r} is not a {n_qubits}-bit string or integer index"
        ) from exc


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--qubits", type=int, default=3)
    parser.add_argument(
        "--marked",
        nargs="+",
        help="binary labels or integer indices (default: the all-ones state)",
    )
    parser.add_argument("--iterations", type=int)
    parser.add_argument("--plot", type=Path)
    parser.add_argument("--skip-qiskit", action="store_true")
    args = parser.parse_args(argv)

    raw_marked = args.marked or ["1" * args.qubits]
    marked = [_parse_cli_state(label, args.qubits) for label in raw_marked]
    result = run_grover(args.qubits, marked, args.iterations)
    labels = [format(index, f"0{args.qubits}b") for index in result.marked_indices]
    print(f"marked states: {', '.join(labels)}")
    print(f"iterations: {result.iterations}")
    for step, probability in enumerate(result.marked_probabilities):
        print(f"iteration {step}: marked probability = {probability:.9f}")

    if not args.skip_qiskit:
        comparison = compare_with_qiskit(result)
        print("Qiskit comparison:")
        for name, value in comparison.items():
            print(f"  {name}: {value:.12e}")
    if args.plot:
        print(f"plot: {plot_amplitude_amplification(result, args.plot)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
