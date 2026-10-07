"""Qiskit circuit-synthesis commands for the QMW circuit and OSC ecosystem.

Qiskit owns the discrete synthesis algorithms. This module reduces their
output to QMW's canonical gate basis and imports it as a ``ComposerCircuit``
that can feed the existing local simulators, Max composer, and state buses.
"""

from __future__ import annotations

import argparse
from fractions import Fraction
import json
import threading
import time as time_module
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence

import numpy as np

from qasm_circuit_bridge_v1 import ComposerCircuit


QMW_QISKIT_BASIS = (
    "id",
    "x",
    "y",
    "z",
    "h",
    "s",
    "sdg",
    "t",
    "tdg",
    "sx",
    "rx",
    "ry",
    "rz",
    "p",
    "u",
    "cx",
    "cy",
    "cz",
    "cp",
    "crx",
    "cry",
    "crz",
    "ch",
    "swap",
    "ccx",
    "cswap",
)

_REVISION_LOCK = threading.Lock()
_LAST_REVISION = 0


@dataclass(frozen=True)
class SynthesisResult:
    kind: str
    source_circuit: Any
    qiskit_circuit: Any
    composer_circuit: ComposerCircuit
    metadata: dict[str, Any]

    def qasm3(self) -> str:
        """Serialize the normalized Qiskit circuit as standards-compliant QASM 3."""
        from qiskit import qasm3

        return qasm3.dumps(self.qiskit_circuit)

    def summary(self) -> dict[str, Any]:
        return {
            "kind": self.kind,
            "qubits": self.qiskit_circuit.num_qubits,
            "depth": self.qiskit_circuit.depth(),
            "size": self.qiskit_circuit.size(),
            "operations": {
                str(name): int(count)
                for name, count in self.qiskit_circuit.count_ops().items()
            },
            **self.metadata,
        }


@dataclass(frozen=True)
class SynthesisStateFrame:
    """Input-state-dependent quantum metrics after one synthesized operation."""

    index: int
    operation: str
    qubits: tuple[int, ...]
    expected_basis_index: float
    dominant_basis_index: int
    normalized_coherence: float
    population_entropy: float
    mean_qubit_entropy: float
    relative_phase: float
    basis_probabilities: tuple[float, ...]
    basis_relative_phases: tuple[float, ...]


@dataclass(frozen=True)
class TonnetzNode:
    """One coherently aggregated vertex in QMW's four-qubit Tonnetz projection."""

    fifth_coordinate: int
    third_coordinate: int
    pitch_offset: int
    probability: float
    relative_phase: float


@dataclass(frozen=True)
class WilsonCPSNode:
    """A four-qubit basis vertex in the 0)4..4)4 1-3-5-7 CPS aggregate."""

    basis_index: int
    cps_grade: int
    factors: tuple[int, ...]
    complement_basis_index: int
    ratio_numerator: int
    ratio_denominator: int
    probability: float
    relative_phase: float

    @property
    def ratio(self) -> float:
        return self.ratio_numerator / self.ratio_denominator


def project_frame_to_wilson_cps(
    frame: SynthesisStateFrame,
    *,
    generators: tuple[int, int, int, int] = (1, 3, 5, 7),
) -> list[WilsonCPSNode]:
    """Embed a four-qubit state in Wilson's complete tetradic CPS aggregate.

    Each computational basis bit selects one generator. Hamming-weight two is
    the 2)4 Hexany; bitwise complement supplies the self-mirroring vertex.
    Ratios share a global division by the largest generator and are reduced
    into one octave without erasing their factored CPS identity.
    """
    if len(frame.basis_probabilities) != 16:
        raise ValueError("the tetradic Wilson CPS projection requires four qubits")
    if len(generators) != 4 or any(int(value) <= 0 for value in generators):
        raise ValueError("generators must contain four positive integers")
    generators = tuple(int(value) for value in generators)
    reference = max(generators)
    nodes: list[WilsonCPSNode] = []
    for basis_index, (probability, phase) in enumerate(
        zip(frame.basis_probabilities, frame.basis_relative_phases)
    ):
        factors = tuple(
            generators[qubit]
            for qubit in range(4)
            if (basis_index >> qubit) & 1
        )
        product = 1
        for factor in factors:
            product *= factor
        ratio = Fraction(product, reference)
        while ratio < 1:
            ratio *= 2
        while ratio >= 2:
            ratio /= 2
        nodes.append(
            WilsonCPSNode(
                basis_index=basis_index,
                cps_grade=len(factors),
                factors=factors,
                complement_basis_index=basis_index ^ 0b1111,
                ratio_numerator=ratio.numerator,
                ratio_denominator=ratio.denominator,
                probability=float(probability),
                relative_phase=float(phase),
            )
        )
    return sorted(nodes, key=lambda node: node.probability, reverse=True)


def project_frame_to_tonnetz(frame: SynthesisStateFrame) -> list[TonnetzNode]:
    """Project four-qubit amplitudes onto a signed fifth/major-third lattice.

    q0/q1 encode positive/negative fifth motion and q2/q3 encode
    positive/negative major-third motion. Basis states landing on the same
    vertex are added as complex amplitudes, preserving quantum interference.
    """
    if len(frame.basis_probabilities) != 16:
        raise ValueError("the signed Tonnetz projection requires exactly four qubits")
    amplitudes: dict[tuple[int, int], complex] = {}
    for basis_index, (probability, phase) in enumerate(
        zip(frame.basis_probabilities, frame.basis_relative_phases)
    ):
        bits = tuple((basis_index >> qubit) & 1 for qubit in range(4))
        coordinate = (bits[0] - bits[1], bits[2] - bits[3])
        amplitude = np.sqrt(probability) * np.exp(1j * phase)
        amplitudes[coordinate] = amplitudes.get(coordinate, 0j) + amplitude

    total_weight = float(sum(abs(amplitude) ** 2 for amplitude in amplitudes.values()))
    if total_weight <= 1e-15:
        return []
    nodes = [
        TonnetzNode(
            fifth_coordinate=fifth,
            third_coordinate=third,
            pitch_offset=7 * fifth + 4 * third,
            probability=float(abs(amplitude) ** 2 / total_weight),
            relative_phase=float(np.angle(amplitude)),
        )
        for (fifth, third), amplitude in amplitudes.items()
        if abs(amplitude) > 1e-12
    ]
    return sorted(nodes, key=lambda node: node.probability, reverse=True)


def analyze_synthesis_state(
    result: SynthesisResult,
    *,
    initial_basis_index: int = 0,
) -> list[SynthesisStateFrame]:
    """Analyze the state trajectory produced by a synthesized unitary circuit.

    Phase is measured relative to the dominant basis amplitude, so the metric
    is invariant under physically irrelevant global phase. Coherence and
    entropies are normalized to the interval 0..1.
    """
    from qiskit.quantum_info import Statevector, entropy, partial_trace

    circuit = result.qiskit_circuit
    n_qubits = int(circuit.num_qubits)
    dimension = 1 << n_qubits
    initial_basis_index = int(initial_basis_index)
    if not 0 <= initial_basis_index < dimension:
        raise ValueError(
            f"initial_basis_index must be in 0..{dimension - 1} for {n_qubits} qubits"
        )

    state = Statevector.from_int(initial_basis_index, dimension)
    basis_indices = np.arange(dimension, dtype=float)
    frames: list[SynthesisStateFrame] = []
    for index, instruction in enumerate(circuit.data):
        if instruction.operation.name == "barrier":
            continue
        if instruction.operation.name == "measure":
            raise ValueError("state trajectory analysis requires a unitary circuit")
        qubits = tuple(circuit.find_bit(q).index for q in instruction.qubits)
        state = state.evolve(instruction.operation, qargs=list(qubits))
        amplitudes = np.asarray(state.data, dtype=np.complex128)
        probabilities = np.abs(amplitudes) ** 2
        dominant = int(np.argmax(probabilities))
        reference_phase = float(np.angle(amplitudes[dominant]))
        relative_phases = np.angle(amplitudes) - reference_phase
        relative_phases = np.angle(np.exp(1j * relative_phases))
        relative_phases = np.where(np.abs(amplitudes) > 1e-12, relative_phases, 0.0)
        relative_phasors = np.exp(1j * relative_phases)
        circular_phase = np.sum(probabilities * relative_phasors)
        relative_phase = (
            float(np.angle(circular_phase)) if abs(circular_phase) > 1e-12 else 0.0
        )
        coherence = (
            (float(np.sum(np.abs(amplitudes))) ** 2 - 1.0) / (dimension - 1)
            if dimension > 1
            else 0.0
        )
        nonzero = probabilities[probabilities > 1e-15]
        population_entropy = (
            float(-np.sum(nonzero * np.log2(nonzero)) / np.log2(dimension))
            if dimension > 1
            else 0.0
        )
        qubit_entropies = []
        for retained_qubit in range(n_qubits):
            traced_out = [q for q in range(n_qubits) if q != retained_qubit]
            reduced = partial_trace(state, traced_out)
            qubit_entropies.append(float(entropy(reduced, base=2)))

        frames.append(
            SynthesisStateFrame(
                index=index,
                operation=str(instruction.operation.name),
                qubits=qubits,
                expected_basis_index=float(np.dot(basis_indices, probabilities)),
                dominant_basis_index=dominant,
                normalized_coherence=float(np.clip(coherence, 0.0, 1.0)),
                population_entropy=float(np.clip(population_entropy, 0.0, 1.0)),
                mean_qubit_entropy=float(
                    np.clip(np.mean(qubit_entropies), 0.0, 1.0)
                ),
                relative_phase=relative_phase,
                basis_probabilities=tuple(float(value) for value in probabilities),
                basis_relative_phases=tuple(float(value) for value in relative_phases),
            )
        )
    return frames


def next_synthesis_revision() -> int:
    """Return a process-monotonic OSC-safe signed 32-bit revision."""
    global _LAST_REVISION
    with _REVISION_LOCK:
        candidate = int(time_module.time())
        _LAST_REVISION = max(_LAST_REVISION + 1, candidate)
        if _LAST_REVISION > 2_147_483_647:
            raise OverflowError("OSC synthesis revision exhausted signed 32-bit range")
        return _LAST_REVISION


def operation_osc_args(operation: Any) -> list[object]:
    """Encode a CircuitOperation for QMW's registry-backed OSC protocol."""
    step = int(operation.step if operation.step is not None else 0)
    args: list[object] = [
        step,
        str(operation.name),
        ",".join(str(qubit) for qubit in operation.qubits),
        ",".join(str(param) for param in operation.params),
        "" if operation.classical_target is None else str(operation.classical_target),
    ]
    route = operation.measurement_route
    if route is not None:
        args.extend(
            [
                route.target_register,
                "" if route.register_bit is None else int(route.register_bit),
                route.osc_route,
                route.persistence,
                int(route.shots),
            ]
        )
    return args


class SynthesisOSCPublisher:
    """Atomically load a synthesized ComposerCircuit into a QMW receiver."""

    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 7401,
        *,
        client: Any | None = None,
    ) -> None:
        if client is None:
            from pythonosc.udp_client import SimpleUDPClient

            client = SimpleUDPClient(host, int(port))
        self.client = client

    def publish(
        self,
        result: SynthesisResult,
        *,
        revision: int | None = None,
    ) -> int:
        selected_revision = (
            next_synthesis_revision() if revision is None else int(revision)
        )
        if not 0 <= selected_revision <= 2_147_483_647:
            raise ValueError("revision must fit a non-negative signed OSC int32")

        circuit = result.composer_circuit
        operations = circuit.operations
        self.client.send_message(
            "/qmw/circuit/load/begin",
            [
                selected_revision,
                int(circuit.n_qubits),
                int(circuit.n_bits),
                len(operations),
                result.kind,
            ],
        )
        try:
            for operation in operations:
                self.client.send_message(
                    "/qmw/circuit/load/op",
                    [selected_revision, *operation_osc_args(operation)],
                )
            self.client.send_message(
                "/qmw/circuit/load/metadata",
                [selected_revision, json.dumps(result.summary(), sort_keys=True)],
            )
            self.client.send_message(
                "/qmw/circuit/load/commit",
                selected_revision,
            )
        except Exception:
            self.client.send_message(
                "/qmw/circuit/load/abort",
                selected_revision,
            )
            raise
        return selected_revision


def normalize_to_qmw(
    circuit: Any,
    *,
    optimization_level: int = 0,
) -> Any:
    """Compile a Qiskit circuit to operations understood by ComposerCircuit."""
    from qiskit import transpile

    if optimization_level not in range(4):
        raise ValueError("optimization_level must be 0, 1, 2, or 3")
    return transpile(
        circuit,
        basis_gates=list(QMW_QISKIT_BASIS),
        optimization_level=optimization_level,
    )


def _result(
    kind: str,
    source: Any,
    *,
    optimization_level: int,
    metadata: dict[str, Any] | None = None,
) -> SynthesisResult:
    normalized = normalize_to_qmw(source, optimization_level=optimization_level)
    composer = ComposerCircuit.from_qiskit_circuit(normalized)
    return SynthesisResult(
        kind=kind,
        source_circuit=source,
        qiskit_circuit=normalized,
        composer_circuit=composer,
        metadata=dict(metadata or {}),
    )


def synthesize_qft(
    num_qubits: int,
    *,
    topology: str = "full",
    do_swaps: bool = True,
    approximation_degree: int = 0,
    inverse: bool = False,
    optimization_level: int = 0,
) -> SynthesisResult:
    """Synthesize a full-connectivity or linear-nearest-neighbor QFT."""
    from qiskit.synthesis import synth_qft_full, synth_qft_line

    if num_qubits < 1:
        raise ValueError("num_qubits must be at least 1")
    if topology == "full":
        source = synth_qft_full(
            num_qubits,
            do_swaps=do_swaps,
            approximation_degree=approximation_degree,
            inverse=inverse,
        )
    elif topology == "line":
        source = synth_qft_line(
            num_qubits,
            do_swaps=do_swaps,
            approximation_degree=approximation_degree,
        )
        if inverse:
            source = source.inverse()
    else:
        raise ValueError("topology must be 'full' or 'line'")
    return _result(
        "qft",
        source,
        optimization_level=optimization_level,
        metadata={
            "topology": topology,
            "do_swaps": bool(do_swaps),
            "approximation_degree": int(approximation_degree),
            "inverse": bool(inverse),
        },
    )


def synthesize_permutation(
    pattern: Sequence[int],
    *,
    topology: str = "basic",
    optimization_level: int = 0,
) -> SynthesisResult:
    """Synthesize a qubit permutation for general or line connectivity."""
    from qiskit.synthesis import (
        synth_permutation_basic,
        synth_permutation_depth_lnn_kms,
    )

    normalized_pattern = [int(value) for value in pattern]
    if not normalized_pattern:
        raise ValueError("pattern must not be empty")
    if sorted(normalized_pattern) != list(range(len(normalized_pattern))):
        raise ValueError("pattern must be a permutation of 0..n-1")
    if topology == "basic":
        source = synth_permutation_basic(normalized_pattern)
    elif topology == "line":
        source = synth_permutation_depth_lnn_kms(normalized_pattern)
    else:
        raise ValueError("topology must be 'basic' or 'line'")
    return _result(
        "permutation",
        source,
        optimization_level=optimization_level,
        metadata={"pattern": normalized_pattern, "topology": topology},
    )


def synthesize_unitary(
    matrix: Any,
    *,
    optimization_level: int = 0,
) -> SynthesisResult:
    """Synthesize an arbitrary unitary with Quantum Shannon decomposition."""
    from qiskit.quantum_info import Operator
    from qiskit.synthesis import qs_decomposition

    values = np.asarray(matrix, dtype=np.complex128)
    if values.ndim != 2 or values.shape[0] != values.shape[1]:
        raise ValueError("matrix must be square")
    dimension = values.shape[0]
    if dimension < 2 or dimension & (dimension - 1):
        raise ValueError("matrix dimension must be a power of two")
    if not Operator(values).is_unitary():
        raise ValueError("matrix must be unitary")
    source = qs_decomposition(values)
    return _result(
        "unitary",
        source,
        optimization_level=optimization_level,
        metadata={"matrix_dimension": dimension},
    )


def synthesize_clifford(
    clifford: Any,
    *,
    method: str | None = None,
    optimization_level: int = 0,
) -> SynthesisResult:
    """Synthesize a Clifford object or Clifford-compatible circuit/tableau."""
    from qiskit.quantum_info import Clifford
    from qiskit.synthesis import synth_clifford_full

    if method not in {None, "AG", "greedy"}:
        raise ValueError("Clifford method must be None, 'AG', or 'greedy'")
    operator = clifford if isinstance(clifford, Clifford) else Clifford(clifford)
    source = synth_clifford_full(operator, method=method)
    return _result(
        "clifford",
        source,
        optimization_level=optimization_level,
        metadata={
            "method": method or "auto",
            "clifford_qubits": int(operator.num_qubits),
        },
    )


def load_clifford_qasm2(path: str | Path) -> Any:
    """Load a unitary Clifford from QASM 2, discarding terminal readout."""
    from qiskit import qasm2
    from qiskit.quantum_info import Clifford

    circuit = qasm2.load(path).remove_final_measurements(inplace=False)
    return Clifford(circuit)


def synthesize_evolution(
    terms: Sequence[tuple[str, complex | float]],
    time: float,
    *,
    method: str = "lie_trotter",
    reps: int = 1,
    order: int = 2,
    seed: int | None = None,
    optimization_level: int = 0,
) -> SynthesisResult:
    """Synthesize exp(-i*time*H) for a sparse Pauli Hamiltonian."""
    from qiskit import QuantumCircuit
    from qiskit.circuit.library import PauliEvolutionGate
    from qiskit.quantum_info import SparsePauliOp
    from qiskit.synthesis import LieTrotter, MatrixExponential, QDrift, SuzukiTrotter

    if not terms:
        raise ValueError("at least one Pauli term is required")
    widths = {len(str(label)) for label, _ in terms}
    if len(widths) != 1 or 0 in widths:
        raise ValueError("all Pauli labels must have the same non-zero width")
    if reps < 1:
        raise ValueError("reps must be at least 1")

    normalized_terms: list[tuple[str, float]] = []
    for label, coefficient in terms:
        numeric = complex(coefficient)
        if not np.isclose(numeric.imag, 0.0):
            raise ValueError("Pauli evolution coefficients must be real")
        normalized_terms.append((str(label).upper(), float(numeric.real)))

    constructors = {
        "lie_trotter": lambda: LieTrotter(reps=reps),
        "suzuki_trotter": lambda: SuzukiTrotter(order=order, reps=reps),
        "qdrift": lambda: QDrift(reps=reps, seed=seed),
        "matrix": MatrixExponential,
    }
    if method not in constructors:
        raise ValueError(f"unknown evolution method {method!r}")

    operator = SparsePauliOp.from_list(
        normalized_terms
    )
    gate = PauliEvolutionGate(
        operator,
        time=float(time),
        synthesis=constructors[method](),
    )
    source = QuantumCircuit(operator.num_qubits)
    source.append(gate, source.qubits)
    source = source.decompose(reps=8)
    return _result(
        "evolution",
        source,
        optimization_level=optimization_level,
        metadata={
            "terms": [[label, coefficient] for label, coefficient in normalized_terms],
            "time": float(time),
            "method": method,
            "reps": int(reps),
            "order": int(order),
            "seed": seed,
        },
    )


def _pauli_term(text: str) -> tuple[str, float]:
    separator = ":" if ":" in text else "="
    if separator not in text:
        raise argparse.ArgumentTypeError("use PAULI:COEFFICIENT, for example XX:0.7")
    label, coefficient = text.split(separator, 1)
    try:
        return label.strip().upper(), float(coefficient)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"invalid Pauli term {text!r}") from exc


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--optimization-level", type=int, default=0, choices=range(4))
    parser.add_argument("--qasm-out", type=Path)
    parser.add_argument("--publish", action="store_true")
    parser.add_argument("--osc-host", default="127.0.0.1")
    parser.add_argument("--osc-port", type=int, default=7401)
    parser.add_argument("--revision", type=int)
    subparsers = parser.add_subparsers(dest="command", required=True)

    qft = subparsers.add_parser("qft")
    qft.add_argument("--qubits", type=int, required=True)
    qft.add_argument("--topology", choices=("full", "line"), default="full")
    qft.add_argument("--approximation-degree", type=int, default=0)
    qft.add_argument("--no-swaps", action="store_true")
    qft.add_argument("--inverse", action="store_true")

    permutation = subparsers.add_parser("permutation")
    permutation.add_argument("--pattern", type=int, nargs="+", required=True)
    permutation.add_argument("--topology", choices=("basic", "line"), default="basic")

    unitary = subparsers.add_parser("unitary")
    unitary.add_argument("--matrix", type=Path, required=True)

    clifford = subparsers.add_parser("clifford")
    clifford_source = clifford.add_mutually_exclusive_group(required=True)
    clifford_source.add_argument("--qasm2", type=Path)
    clifford_source.add_argument("--random-qubits", type=int)
    clifford.add_argument("--seed", type=int)
    clifford.add_argument("--method", choices=("AG", "greedy"))

    evolution = subparsers.add_parser("evolution")
    evolution.add_argument("--term", type=_pauli_term, action="append", required=True)
    evolution.add_argument("--time", type=float, required=True)
    evolution.add_argument(
        "--method",
        choices=("lie_trotter", "suzuki_trotter", "qdrift", "matrix"),
        default="lie_trotter",
    )
    evolution.add_argument("--reps", type=int, default=1)
    evolution.add_argument("--order", type=int, default=2)
    evolution.add_argument("--seed", type=int)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    common = {"optimization_level": args.optimization_level}
    if args.command == "qft":
        result = synthesize_qft(
            args.qubits,
            topology=args.topology,
            do_swaps=not args.no_swaps,
            approximation_degree=args.approximation_degree,
            inverse=args.inverse,
            **common,
        )
    elif args.command == "permutation":
        result = synthesize_permutation(args.pattern, topology=args.topology, **common)
    elif args.command == "unitary":
        result = synthesize_unitary(np.load(args.matrix), **common)
    elif args.command == "clifford":
        from qiskit.quantum_info import random_clifford

        if args.qasm2 is not None:
            clifford_input = load_clifford_qasm2(args.qasm2)
        else:
            if args.random_qubits < 1:
                raise ValueError("--random-qubits must be at least 1")
            clifford_input = random_clifford(args.random_qubits, seed=args.seed)
        result = synthesize_clifford(
            clifford_input,
            method=args.method,
            **common,
        )
    else:
        result = synthesize_evolution(
            args.term,
            args.time,
            method=args.method,
            reps=args.reps,
            order=args.order,
            seed=args.seed,
            **common,
        )

    if args.qasm_out:
        args.qasm_out.write_text(result.qasm3(), encoding="utf-8")
    summary = result.summary()
    if args.publish:
        summary["osc_revision"] = SynthesisOSCPublisher(
            args.osc_host,
            args.osc_port,
        ).publish(result, revision=args.revision)
        summary["osc_destination"] = f"{args.osc_host}:{args.osc_port}"
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
