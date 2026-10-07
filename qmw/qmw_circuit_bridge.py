#!/usr/bin/env python3
"""Circuit / pilot-wave bridge for Quantum Population v5.

Drop this module beside quantum_population_v5.py. It provides:
- editable 4-qubit circuit grid (received over OSC)
- unitary circuit-column application to a density matrix
- a pilot-wave-inspired current graph computed from H and rho
- OSC control receiver and OSC feature broadcaster

The GUI is intentionally a separate process. It sends edits to port 9002;
this bridge broadcasts data to Max/QMW on port 9001.

Dependencies: numpy, python-osc
"""
from __future__ import annotations

import ast
from collections import deque
from dataclasses import dataclass, field
import json
import math
import threading
from typing import Callable, Deque, Dict, List, Optional, Sequence, Tuple

import numpy as np

from qasm_circuit_bridge_v1 import (
    ComposerCircuit,
    MeasurementRoute,
    default_measurement_osc_route,
    normalize_register_bus_name,
)

try:
    from pythonosc.dispatcher import Dispatcher
    from pythonosc.osc_server import BlockingOSCUDPServer
    from pythonosc.udp_client import SimpleUDPClient
except ImportError as exc:
    raise RuntimeError("Install dependency: pip install python-osc") from exc

I2 = np.eye(2, dtype=np.complex128)
X = np.array([[0, 1], [1, 0]], dtype=np.complex128)
Y = np.array([[0, -1j], [1j, 0]], dtype=np.complex128)
Z = np.array([[1, 0], [0, -1]], dtype=np.complex128)
H = np.array([[1, 1], [1, -1]], dtype=np.complex128) / math.sqrt(2.0)
S = np.array([[1, 0], [0, 1j]], dtype=np.complex128)
T = np.array([[1, 0], [0, np.exp(1j * math.pi / 4)]], dtype=np.complex128)
SINGLE_QUBIT_GATES = {"I": I2, "H": H, "X": X, "Y": Y, "Z": Z, "S": S, "T": T}
VALID_GATES = set(SINGLE_QUBIT_GATES) | {"•", "⊕"}
REGISTRY_GRID_GATES = {
    "H": "h",
    "X": "x",
    "Y": "y",
    "Z": "z",
    "S": "s",
    "T": "t",
}
LIVE_GRID_LABELS = {value: key for key, value in REGISTRY_GRID_GATES.items()}
LIVE_GRID_LABELS.update({"cx": "cx"})


def parse_osc_list(value: object) -> List[object]:
    if value is None:
        return []

    if isinstance(value, str):
        text = value.strip()
        if not text or text.lower() in {"none", "null", "-"}:
            return []
        return [part.strip() for part in text.split(",") if part.strip()]
    if isinstance(value, (list, tuple)):
        return list(value)
    return [value]


def parse_qubit_refs(value: object) -> List[int | str]:
    refs: List[int | str] = []
    for item in parse_osc_list(value):
        text = str(item).strip()
        try:
            refs.append(int(text))
        except ValueError:
            refs.append(text)
    return refs


def parse_param_value(value: object) -> float | int | str:
    if isinstance(value, (int, float)):
        return value

    text = str(value).strip()
    if not text:
        return text

    try:
        return int(text)
    except ValueError:
        pass

    try:
        return float(text)
    except ValueError:
        pass

    try:
        return float(eval_numeric_expr(text))
    except Exception:
        return text


def parse_params(value: object) -> List[float | int | str]:
    return [parse_param_value(item) for item in parse_osc_list(value)]


def parse_optional_text(args: Sequence[object], index: int) -> Optional[str]:
    if len(args) <= index:
        return None

    text = str(args[index]).strip()
    if not text:
        return None

    return text


def parse_optional_int_text(value: Optional[str]) -> Optional[int]:
    if value is None:
        return None

    try:
        return int(value)
    except ValueError:
        return None


def eval_numeric_expr(text: str) -> float:
    tree = ast.parse(text, mode="eval")

    def visit(node: ast.AST) -> float:
        if isinstance(node, ast.Expression):
            return visit(node.body)
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return float(node.value)
        if isinstance(node, ast.Name) and node.id in {"pi", "tau", "e"}:
            return float({"pi": math.pi, "tau": math.tau, "e": math.e}[node.id])
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
            value = visit(node.operand)
            return value if isinstance(node.op, ast.UAdd) else -value
        if isinstance(node, ast.BinOp) and isinstance(
            node.op,
            (ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Pow),
        ):
            left = visit(node.left)
            right = visit(node.right)
            if isinstance(node.op, ast.Add):
                return left + right
            if isinstance(node.op, ast.Sub):
                return left - right
            if isinstance(node.op, ast.Mult):
                return left * right
            if isinstance(node.op, ast.Div):
                return left / right
            return left ** right
        raise ValueError(f"Unsupported numeric expression: {text}")

    return visit(tree)


def apply_single_qubit_operator(op: np.ndarray, gate: np.ndarray, qubit: int, n_qubits: int) -> np.ndarray:
    """Apply a 2x2 operator to q[qubit] of a state vector or density tensor.

    This helper applies to a ket state vector only; density evolution uses
    full unitary construction below for clarity and numerical safety.
    """
    tensor = op.reshape((2,) * n_qubits)
    tensor = np.moveaxis(tensor, qubit, 0)
    result = np.tensordot(gate, tensor, axes=(1, 0))
    return np.moveaxis(result, 0, qubit).reshape(-1)


def single_qubit_unitary(gate: np.ndarray, qubit: int, n_qubits: int) -> np.ndarray:
    """Construct full 2**n unitary for a single-qubit gate."""
    dim = 2 ** n_qubits
    full = np.zeros((dim, dim), dtype=np.complex128)
    bit = n_qubits - 1 - qubit
    for col in range(dim):
        input_bit = (col >> bit) & 1
        for output_bit in (0, 1):
            row = (col & ~(1 << bit)) | (output_bit << bit)
            full[row, col] = gate[output_bit, input_bit]
    return full


def cnot_unitary(control: int, target: int, n_qubits: int) -> np.ndarray:
    dim = 2 ** n_qubits
    full = np.zeros((dim, dim), dtype=np.complex128)
    cbit = n_qubits - 1 - control
    tbit = n_qubits - 1 - target
    for col in range(dim):
        row = col ^ (1 << tbit) if ((col >> cbit) & 1) else col
        full[row, col] = 1.0
    return full



def partial_trace_one_qubit(rho: np.ndarray, keep: int, n_qubits: int) -> np.ndarray:
    """Return one-qubit reduced density matrix for qubit `keep`."""
    tensor = rho.reshape((2,) * (2 * n_qubits))
    trace_axes = [q for q in range(n_qubits) if q != keep]
    # Trace in descending order to preserve axes indices.
    current_n = n_qubits
    for q in reversed(trace_axes):
        tensor = np.trace(tensor, axis1=q, axis2=q + current_n)
        current_n -= 1
    return tensor.reshape(2, 2)


def partial_trace(
    rho: np.ndarray,
    keep: Tuple[int, ...],
    n_qubits: int,
) -> np.ndarray:
    """Return the reduced density matrix retaining the requested qubits."""
    keep = tuple(sorted(keep))

    if not keep:
        raise ValueError("keep must contain at least one qubit.")

    if any(q < 0 or q >= n_qubits for q in keep):
        raise ValueError(f"Qubit indices must be between 0 and {n_qubits - 1}.")

    tensor = rho.reshape((2,) * (2 * n_qubits))

    # Give retained bra and ket indices separate labels. Traced-out qubits
    # share a label across bra/ket, which performs the partial trace.
    input_labels = list(range(n_qubits))
    for q in range(n_qubits):
        input_labels.append(q + n_qubits if q in keep else q)

    output_labels = list(keep) + [q + n_qubits for q in keep]
    reduced = np.einsum(tensor, input_labels, output_labels)

    dim = 2 ** len(keep)
    return reduced.reshape(dim, dim)


def pairwise_mutual_information(
    rho: np.ndarray,
    qubit_a: int,
    qubit_b: int,
    n_qubits: int,
) -> float:
    """Return I(A:B) = S(A) + S(B) - S(AB), in bits."""
    rho_a = partial_trace(rho, (qubit_a,), n_qubits)
    rho_b = partial_trace(rho, (qubit_b,), n_qubits)
    rho_ab = partial_trace(rho, (qubit_a, qubit_b), n_qubits)

    value = entropy(rho_a) + entropy(rho_b) - entropy(rho_ab)
    return float(max(0.0, value))


def entropy(rho: np.ndarray) -> float:
    vals = np.clip(np.linalg.eigvalsh(rho).real, 0.0, 1.0)
    vals = vals[vals > 1e-12]
    return float(-np.sum(vals * np.log2(vals))) if vals.size else 0.0


def purity(rho: np.ndarray) -> float:
    return float(np.trace(rho @ rho).real)


PAULI_AXES = (X, Y, Z)


def bloch_from_density(rho_single: np.ndarray) -> Tuple[float, float, float]:
    return (
        float(np.trace(rho_single @ X).real),
        float(np.trace(rho_single @ Y).real),
        float(np.trace(rho_single @ Z).real),
    )


def pair_spin_correlation_tensor(rho_pair: np.ndarray) -> List[float]:
    """Return flattened <sigma_i tensor sigma_j> for XX..ZZ."""
    return [
        float(np.trace(rho_pair @ np.kron(axis_a, axis_b)).real)
        for axis_a in PAULI_AXES
        for axis_b in PAULI_AXES
    ]


def coherence_l1(rho: np.ndarray) -> float:
    return float(np.sum(np.abs(rho - np.diag(np.diag(rho)))))


def normalize_density(rho: np.ndarray) -> np.ndarray:
    """Hermitize and trace-normalize to prevent accumulated numerical drift."""
    rho = 0.5 * (rho + rho.conj().T)
    trace = float(np.trace(rho).real)
    if trace <= 1e-14:
        raise ValueError("Density matrix has non-positive trace")
    return rho / trace


@dataclass
class PilotFrame:
    node: int
    next_node: int
    velocity: float
    current: float
    phase_gradient: float
    branch_entropy: float
    current_matrix: np.ndarray


class CircuitProgram:
    """Thread-safe 4-qubit circuit grid; one column is applied at a time."""

    def __init__(
        self,
        n_qubits: int = 4,
        n_steps: int = 16,
        active_length: int | None = None,
    ) -> None:
        self.n_qubits = n_qubits
        self.n_steps = n_steps

        # Number of columns the playhead actually loops through.
        # The grid can remain 16 columns wide.
        self.active_length = (
            int(active_length)
            if active_length is not None
            else n_steps
        )

        self.active_length = max(
            1,
            min(self.active_length, n_steps),
        )

        self.grid: List[List[str]] = [
            ["I"] * n_steps
            for _ in range(n_qubits)
        ]

        self.current_column = 0
        self.enabled = True
        self._lock = threading.RLock()
        self.make_starting_program()

    def make_starting_program(self) -> None:
        with self._lock:
            self.clear()
            # H(q0) -> CNOT 0→1 -> T(q0) -> CNOT 1→2 -> H(q3)
            if self.n_qubits >= 1 and self.n_steps >= 1:
                self.grid[0][0] = "H"
            if self.n_qubits >= 2 and self.n_steps >= 2:
                self.grid[0][1], self.grid[1][1] = "•", "⊕"
            if self.n_qubits >= 1 and self.n_steps >= 3:
                self.grid[0][2] = "T"
            if self.n_qubits >= 3 and self.n_steps >= 4:
                self.grid[1][3], self.grid[2][3] = "•", "⊕"
            if self.n_qubits >= 4 and self.n_steps >= 5:
                self.grid[3][4] = "H"

    def clear(self) -> None:
        with self._lock:
            self.grid = [["I"] * self.n_steps for _ in range(self.n_qubits)]
            self.current_column = 0

    def set_gate(self, qubit: int, column: int, gate: str) -> None:
        gate = str(gate)
        if gate not in VALID_GATES:
            raise ValueError(f"Unknown gate: {gate}")
        if not (0 <= qubit < self.n_qubits and 0 <= column < self.n_steps):
            raise IndexError("Circuit cell is out of range")
        with self._lock:
            if gate in {"•", "⊕"}:
                for q in range(self.n_qubits):
                    if self.grid[q][column] == gate:
                        self.grid[q][column] = "I"
            self.grid[qubit][column] = gate

    def clear_cell(self, qubit: int, column: int) -> None:
        with self._lock:
            self.grid[qubit][column] = "I"

    def column_unitary(self, column: int) -> Tuple[np.ndarray, List[str]]:
        dim = 2 ** self.n_qubits
        unitary = np.eye(dim, dtype=np.complex128)
        messages: List[str] = []
        with self._lock:
            cells = [self.grid[q][column] for q in range(self.n_qubits)]

        for q, gate_name in enumerate(cells):
            if gate_name in SINGLE_QUBIT_GATES and gate_name != "I":
                unitary = single_qubit_unitary(SINGLE_QUBIT_GATES[gate_name], q, self.n_qubits) @ unitary

        controls = [q for q, value in enumerate(cells) if value == "•"]
        targets = [q for q, value in enumerate(cells) if value == "⊕"]
        if len(controls) == 1 and len(targets) == 1:
            unitary = cnot_unitary(controls[0], targets[0], self.n_qubits) @ unitary
            messages.append(f"CNOT {controls[0]}->{targets[0]}")
        elif controls or targets:
            messages.append("Incomplete CNOT ignored")
        return unitary, messages

    def take_next_column(self) -> Tuple[np.ndarray, int, List[str]]:
        """Advance the playhead and return the column unitary without applying it.

        Density engines that own an actual configuration use this API to unfold
        the gate through its Hermitian generator.  ``apply_next_column`` remains
        as the backwards-compatible instantaneous wrapper.
        """
        if not self.enabled:
            return (
                np.eye(2 ** self.n_qubits, dtype=np.complex128),
                self.current_column,
                [],
            )
        with self._lock:
            column = self.current_column
            self.current_column = (self.current_column + 1) % self.active_length
        unitary, labels = self.column_unitary(column)
        labels = [f"column {column}"] + labels
        return unitary, column, labels

    def apply_next_column(self, rho: np.ndarray) -> Tuple[np.ndarray, int, List[str]]:
        unitary, column, labels = self.take_next_column()
        return normalize_density(unitary @ rho @ unitary.conj().T), column, labels

    def to_openqasm2_lines(self) -> List[str]:
        with self._lock:
            grid = [row[:] for row in self.grid]

        lines = [
            "OPENQASM 2.0;",
            'include "qelib1.inc";',
            f"qreg q[{self.n_qubits}];",
            "// QMW q0 is the top row / most-significant live-engine bit.",
        ]

        for column in range(self.n_steps):
            cells = [grid[q][column] for q in range(self.n_qubits)]
            column_lines: List[str] = []

            for qubit, gate_name in enumerate(cells):
                if gate_name in SINGLE_QUBIT_GATES and gate_name != "I":
                    column_lines.append(f"{gate_name.lower()} q[{qubit}];")

            controls = [q for q, value in enumerate(cells) if value == "•"]
            targets = [q for q, value in enumerate(cells) if value == "⊕"]
            if len(controls) == 1 and len(targets) == 1:
                column_lines.append(f"cx q[{controls[0]}],q[{targets[0]}];")
            elif controls or targets:
                column_lines.append(f"// column {column + 1}: incomplete CNOT ignored")

            if column_lines:
                lines.append(f"// column {column + 1}")
                lines.extend(column_lines)

        return lines

    def to_openqasm2(self) -> str:
        return "\n".join(self.to_openqasm2_lines())


@dataclass
class PendingCircuitLoad:
    """Circuit score assembled off to the side until an OSC commit arrives."""

    revision: int
    expected_operations: int
    kind: str
    circuit: ComposerCircuit
    metadata: dict[str, object] = field(default_factory=dict)


class PilotWaveGraph:
    """Discrete guidance dynamics derived from quantum probability current.

    J_ij = 2 Im(H_ij rho_ji). Positive outgoing currents from the active node
    form a stochastic guidance distribution. The oscillator-friendly continuous
    values are derived from that directed current field.
    """

    def __init__(self, n_nodes: int, seed: Optional[int] = None) -> None:
        self.node = 0
        self.rng = np.random.default_rng(seed)
        self.n_nodes = n_nodes
        self._initialized = False
        

    def update(self, rho: np.ndarray, hamiltonian: np.ndarray, dt: float) -> PilotFrame:
        currents = 2.0 * np.imag(hamiltonian * rho.T)
        np.fill_diagonal(currents, 0.0)
        populations = np.clip(np.real(np.diag(rho)), 0.0, None)
        population_total = float(populations.sum())
        if not self._initialized:
            probabilities = (
                populations / population_total
                if population_total > 1e-12
                else np.ones(self.n_nodes) / self.n_nodes
            )
            self.node = int(self.rng.choice(self.n_nodes, p=probabilities))
            self._initialized = True

        source = self.node
        source_population = float(populations[source])
        outgoing_current = np.maximum(currents[:, source], 0.0)
        outgoing_rates = (
            outgoing_current / source_population
            if source_population > 1e-15
            else np.zeros(self.n_nodes, dtype=float)
        )
        total_rate = float(outgoing_rates.sum())
        next_node = source
        signed_current = 0.0

        if total_rate > 1e-12:
            weights = outgoing_rates / total_rate
            branch_entropy = float(-np.sum(weights[weights > 1e-12] * np.log2(weights[weights > 1e-12])))
            jump_probability = float(-np.expm1(-total_rate * max(dt, 0.0)))
            if self.rng.random() < jump_probability:
                next_node = int(self.rng.choice(self.n_nodes, p=weights))
                signed_current = float(currents[next_node, source])
                self.node = next_node
            velocity = float(min(1.0, total_rate * max(dt, 0.0)))
        else:
            # Zero current means zero motion. Population and entropy remain
            # descriptors; they do not create a random walk.
            branch_entropy = 0.0
            velocity = 0.0

        phase_gradient = float(np.angle(rho[next_node, source])) if abs(rho[next_node, source]) > 1e-12 else 0.0
        return PilotFrame(
            node=source,
            next_node=next_node,
            velocity=velocity,
            current=signed_current,
            phase_gradient=phase_gradient / math.pi,
            branch_entropy=branch_entropy,
            current_matrix=currents,
        )


class QMWCircuitBridge:
    """Owns circuit control, pilot graph, and OSC I/O for a density engine."""

    def __init__(
        self,
        n_qubits: int = 4,
        n_steps: int = 16,
        active_length: int | None = None,
        osc_host: str = "127.0.0.1",
        osc_out_port: int = 7400,
        osc_control_port: int = 7401,
        circuit_interval_seconds: float = 0.20,
        osc_telemetry_hz: float | None = None,
    ) -> None:
        self.n_qubits = n_qubits
        self.dim = 2 ** n_qubits
        self.circuit = CircuitProgram(
            n_qubits,
            n_steps,
            active_length=active_length,
        )
        self.registry_circuit = ComposerCircuit(
            n_qubits=n_qubits,
            n_bits=n_qubits,
        )
        self._sync_registry_from_grid()
        self.pilot = PilotWaveGraph(self.dim)
        self.measurement_rng = np.random.default_rng()
        self.client = SimpleUDPClient(osc_host, osc_out_port)
        self.circuit_interval_seconds = circuit_interval_seconds
        self._elapsed = 0.0
        if osc_telemetry_hz is None:
            self.osc_telemetry_interval = None
        elif float(osc_telemetry_hz) <= 0.0:
            self.osc_telemetry_interval = float("inf")
        else:
            self.osc_telemetry_interval = 1.0 / float(osc_telemetry_hz)
        self._osc_telemetry_elapsed = 0.0
        self._step_requested = False
        self._spin_trails: List[Deque[Tuple[float, float, float]]] = [
            deque(maxlen=48) for _ in range(n_qubits)
        ]
        self._previous_spin_vectors: List[Optional[Tuple[float, float, float]]] = [
            None for _ in range(n_qubits)
        ]
        self._control_server: Optional[BlockingOSCUDPServer] = None
        self._control_thread: Optional[threading.Thread] = None
        self._external_control_handlers: Dict[str, Callable[..., None]] = {}
        self._circuit_load_lock = threading.RLock()
        self._pending_circuit_load: Optional[PendingCircuitLoad] = None
        self._circuit_load_revision = -1
        self._last_circuit_load_metadata: dict[str, object] = {}
        self._authoritative_pilot_frame: Optional[PilotFrame] = None
        self.osc_control_port = osc_control_port

    def set_authoritative_pilot_frame(self, frame: PilotFrame) -> None:
        """Install the state owner's latest actual-configuration transition."""
        self._authoritative_pilot_frame = frame
        self.pilot.node = int(frame.next_node)
        self.pilot._initialized = True

    def add_control_handler(self, address: str, callback: Callable[..., None]) -> None:
        """Register a conductor-owned OSC handler before the server starts."""
        if self._control_server is not None:
            raise RuntimeError("Control handlers must be registered before server start")
        self._external_control_handlers[str(address)] = callback

    def start_control_server(self, host: str = "127.0.0.1") -> None:
        dispatcher = Dispatcher()
        dispatcher.map("/qmw/circuit/set", self._osc_set_gate)
        dispatcher.map("/qmw/circuit/op", self._osc_set_operation)
        dispatcher.map("/qmw/circuit/gate", self._osc_set_operation)
        dispatcher.map("/qmw/circuit/export_qasm", self._osc_export_qasm)
        dispatcher.map("/qmw/circuit/clear_cell", self._osc_clear_cell)
        dispatcher.map("/qmw/circuit/clear", self._osc_clear)
        dispatcher.map("/qmw/circuit/enable", self._osc_enable)
        dispatcher.map("/qmw/circuit/interval", self._osc_interval)
        dispatcher.map("/qmw/circuit/preset", self._osc_preset)
        dispatcher.map("/qmw/circuit/step", self._osc_step)
        dispatcher.map("/qmw/circuit/load/begin", self._osc_load_begin)
        dispatcher.map("/qmw/circuit/load/op", self._osc_load_operation)
        dispatcher.map("/qmw/circuit/load/metadata", self._osc_load_metadata)
        dispatcher.map("/qmw/circuit/load/commit", self._osc_load_commit)
        dispatcher.map("/qmw/circuit/load/abort", self._osc_load_abort)
        for address, callback in self._external_control_handlers.items():
            dispatcher.map(address, callback)
        # Circuit-load messages form an ordered transaction. A threaded UDP
        # server can dispatch commit before earlier operation datagrams finish,
        # so consume control packets sequentially on this dedicated thread.
        self._control_server = BlockingOSCUDPServer((host, self.osc_control_port), dispatcher)
        self._control_thread = threading.Thread(target=self._control_server.serve_forever, daemon=True)
        self._control_thread.start()
        print(f"QMW circuit control listening on udp://{host}:{self.osc_control_port}")

    def _osc_step(self, _address: str, *_: object) -> None:
        self._step_requested = True
    
    def stop_control_server(self) -> None:
        if self._control_server:
            self._control_server.shutdown()
            self._control_server.server_close()
            self._control_server = None

    def _osc_set_gate(self, _address: str, qubit: int, column: int, gate: str) -> None:
        try:
            self.circuit.set_gate(int(qubit), int(column), str(gate))
            self._sync_registry_from_grid()
            self._send_registry_status()
        except Exception as exc:
            print(f"Circuit set rejected: {exc}")

    def _osc_set_operation(self, _address: str, *args: object) -> None:
        """
        Registry-backed Max menu protocol:

            /qmw/circuit/op step gate qubits params [classical_target]
                [target_register] [register_bit] [osc_route] [persistence] [shots]

        qubits and params may be comma-separated symbols, e.g.
            /qmw/circuit/op 7 MN 3 pi/3,pi/4 3
            /qmw/circuit/op 7 MN 3 pi/3,pi/4 3 pitch 0 /note single_shot 1
            /qmw/circuit/op 2 cx 0,1
        """
        try:
            op = self._add_operation_from_osc_args(self.registry_circuit, args)
            step = int(op.step if op.step is not None else 0)
            qubits = op.qubits
            self._mirror_registry_operation_to_live_grid(op.name, qubits, step)
            self._send_registry_status()
        except Exception as exc:
            print(f"Circuit operation rejected: {exc}")

    @staticmethod
    def _add_operation_from_osc_args(
        circuit: ComposerCircuit,
        args: Sequence[object],
    ):
        if len(args) < 3:
            raise ValueError("Expected: step gate qubits [params] [classical_target].")

        step = int(args[0])
        name = str(args[1])
        qubits = parse_qubit_refs(args[2])
        params = parse_params(args[3]) if len(args) >= 4 else []
        parsed_target = parse_qubit_refs(args[4]) if len(args) >= 5 else []
        classical_target = parsed_target[0] if parsed_target else None
        target_register = parse_optional_text(args, 5)
        if target_register is not None:
            target_register = normalize_register_bus_name(target_register)
        register_bit_text = parse_optional_text(args, 6)
        register_bit = parse_optional_int_text(register_bit_text)
        route_offset = 1 if register_bit is not None else 0
        osc_route = parse_optional_text(args, 6 + route_offset)
        persistence = parse_optional_text(args, 7 + route_offset) or "single_shot"
        shots_text = parse_optional_text(args, 8 + route_offset)
        shots = int(shots_text) if shots_text is not None else 1
        measurement_route = (
            MeasurementRoute(
                target_register=target_register,
                osc_route=osc_route or default_measurement_osc_route(target_register),
                persistence=persistence,
                shots=shots,
                register_bit=register_bit,
            )
            if target_register is not None
            else None
        )
        return circuit.add(
            name,
            qubits,
            params=params,
            classical_target=classical_target,
            step=step,
            measurement_route=measurement_route,
            target_register=target_register,
            register_bit=register_bit,
        )

    def _send_circuit_load_error(self, revision: int, message: str) -> None:
        print(f"Circuit load rejected: {message}")
        self.client.send_message(
            "/qmw/circuit/load/error",
            [int(revision), str(message)],
        )

    def _osc_load_begin(
        self,
        _address: str,
        revision: int,
        n_qubits: int,
        n_bits: int,
        operation_count: int,
        kind: str = "synthesis",
    ) -> None:
        revision = int(revision)
        try:
            if int(n_qubits) != self.n_qubits:
                raise ValueError(
                    f"circuit has {n_qubits} qubits; live engine requires {self.n_qubits}"
                )
            if int(n_bits) < 0 or int(operation_count) < 0:
                raise ValueError("bit and operation counts must be non-negative")
            with self._circuit_load_lock:
                current_revision = self._circuit_load_revision
                if self._pending_circuit_load is not None:
                    current_revision = max(
                        current_revision,
                        self._pending_circuit_load.revision,
                    )
                if revision <= current_revision:
                    raise ValueError(
                        f"stale revision {revision}; current is {current_revision}"
                    )
                self._pending_circuit_load = PendingCircuitLoad(
                    revision=revision,
                    expected_operations=int(operation_count),
                    kind=str(kind),
                    circuit=ComposerCircuit(
                        n_qubits=self.n_qubits,
                        n_bits=int(n_bits),
                    ),
                )
        except Exception as exc:
            self._send_circuit_load_error(revision, str(exc))

    def _osc_load_operation(
        self,
        _address: str,
        revision: int,
        *args: object,
    ) -> None:
        revision = int(revision)
        try:
            with self._circuit_load_lock:
                pending = self._pending_circuit_load
                if pending is None or pending.revision != revision:
                    raise ValueError(f"no pending load for revision {revision}")
                if len(pending.circuit.operations) >= pending.expected_operations:
                    raise ValueError("received more operations than declared")
                self._add_operation_from_osc_args(pending.circuit, args)
        except Exception as exc:
            self._send_circuit_load_error(revision, str(exc))

    def _osc_load_commit(self, _address: str, revision: int) -> None:
        revision = int(revision)
        try:
            with self._circuit_load_lock:
                pending = self._pending_circuit_load
                if pending is None or pending.revision != revision:
                    raise ValueError(f"no pending load for revision {revision}")
                actual = len(pending.circuit.operations)
                if actual != pending.expected_operations:
                    raise ValueError(
                        f"expected {pending.expected_operations} operations, received {actual}"
                    )

                # The score swap is atomic. The legacy grid is a projection of
                # the subset it can display and execute; unsupported cells do
                # not alter the canonical registry score.
                self.registry_circuit = pending.circuit
                self.circuit.clear()
                for operation in self.registry_circuit.operations:
                    if operation.step is None:
                        continue
                    self._mirror_registry_operation_to_live_grid(
                        operation.name,
                        operation.qubits,
                        int(operation.step),
                    )
                used_steps = [
                    int(operation.step)
                    for operation in self.registry_circuit.operations
                    if operation.step is not None
                ]
                if used_steps:
                    self.circuit.active_length = min(
                        self.circuit.n_steps,
                        max(used_steps) + 1,
                    )
                self._circuit_load_revision = revision
                self._last_circuit_load_metadata = dict(pending.metadata)
                self._pending_circuit_load = None

            self._send_registry_status()
            self.client.send_message(
                "/qmw/circuit/load/accepted",
                [revision, pending.kind, actual, self.n_qubits],
            )
        except Exception as exc:
            self._send_circuit_load_error(revision, str(exc))

    def _osc_load_metadata(
        self,
        _address: str,
        revision: int,
        payload: str,
    ) -> None:
        revision = int(revision)
        try:
            decoded = json.loads(str(payload))
            if not isinstance(decoded, dict):
                raise ValueError("metadata must be a JSON object")
            with self._circuit_load_lock:
                pending = self._pending_circuit_load
                if pending is None or pending.revision != revision:
                    raise ValueError(f"no pending load for revision {revision}")
                pending.metadata = decoded
        except Exception as exc:
            self._send_circuit_load_error(revision, str(exc))

    def _osc_load_abort(self, _address: str, revision: int) -> None:
        revision = int(revision)
        with self._circuit_load_lock:
            pending = self._pending_circuit_load
            if pending is not None and pending.revision == revision:
                self._pending_circuit_load = None

    def _osc_export_qasm(self, _address: str, *_: object) -> None:
        self._send_registry_status()

    def _osc_clear_cell(self, _address: str, qubit: int, column: int) -> None:
        try:
            self.circuit.clear_cell(int(qubit), int(column))
            self._sync_registry_from_grid()
            self._send_registry_status()
        except Exception as exc:
            print(f"Circuit clear cell rejected: {exc}")

    def _osc_clear(self, _address: str, *_: object) -> None:
        self.circuit.clear()
        self.registry_circuit.clear()
        self._send_registry_status()

    def _osc_enable(self, _address: str, enabled: int) -> None:
        self.circuit.enabled = bool(enabled)

    def _osc_interval(self, _address: str, seconds: float) -> None:
        self.circuit_interval_seconds = max(0.01, float(seconds))

    def _osc_preset(self, _address: str, *_: object) -> None:
        self.circuit.make_starting_program()
        self._sync_registry_from_grid()
        self._send_registry_status()

    def _sync_registry_from_grid(self) -> None:
        self.registry_circuit.clear()

        for column in range(self.circuit.n_steps):
            cells = [self.circuit.grid[q][column] for q in range(self.circuit.n_qubits)]

            for qubit, gate_name in enumerate(cells):
                registry_name = REGISTRY_GRID_GATES.get(gate_name)
                if registry_name is not None:
                    self.registry_circuit.add(registry_name, [qubit], step=column)

            controls = [q for q, value in enumerate(cells) if value == "•"]
            targets = [q for q, value in enumerate(cells) if value == "⊕"]
            if len(controls) == 1 and len(targets) == 1 and controls[0] != targets[0]:
                self.registry_circuit.add("cx", [controls[0], targets[0]], step=column)

    def _mirror_registry_operation_to_live_grid(
        self,
        name: str,
        qubits: Sequence[int | str],
        step: int,
    ) -> None:
        if not (0 <= step < self.circuit.n_steps):
            return
        if any(not isinstance(q, int) for q in qubits):
            return

        if name in LIVE_GRID_LABELS and len(qubits) == 1:
            self.circuit.set_gate(int(qubits[0]), step, LIVE_GRID_LABELS[name])
        elif name == "cx" and len(qubits) == 2 and qubits[0] != qubits[1]:
            self.circuit.set_gate(int(qubits[0]), step, "•")
            self.circuit.set_gate(int(qubits[1]), step, "⊕")

    def _send_registry_status(self) -> None:
        try:
            qasm = self.registry_circuit.to_qasm()
            self.client.send_message("/qmw/circuit/qasm3", qasm)
            self.client.send_message(
                "/qmw/circuit/op_count",
                len(self.registry_circuit.operations),
            )
            self._send_measurement_bases()
        except Exception as exc:
            print(f"Circuit registry export failed: {exc}")

    def _send_measurement_bases(
        self,
        rho: Optional[np.ndarray] = None,
        step: Optional[int] = None,
    ) -> None:
        active_items = self.registry_circuit.active_measurement_bases()
        active_routes = self.registry_circuit.active_measurement_routes()

        for qubit, basis in active_items:
            if not (0 <= qubit < self.n_qubits):
                continue

            route = active_routes.get(qubit)
            axis = basis.pauli_axis or ""
            self.client.send_message(
                f"/qmw/circuit/basis/q{qubit}",
                [basis.theta, basis.phi, basis.label, axis],
            )

            # Short JSUI-facing aliases.
            self.client.send_message(f"/basis/{qubit}/theta", basis.theta)
            self.client.send_message(f"/basis/{qubit}/phi", basis.phi)
            self.client.send_message(f"/basis/{qubit}/label", basis.label)
            self.client.send_message(f"/basis/{qubit}/axis", axis)

            # Keep parity with the spin/polarization namespace.
            self.client.send_message(f"/qubit/{qubit}/basis/theta", basis.theta)
            self.client.send_message(f"/qubit/{qubit}/basis/phi", basis.phi)
            self.client.send_message(
                f"/qubit/{qubit}/measure/basis/theta",
                basis.theta,
            )
            self.client.send_message(
                f"/qubit/{qubit}/measure/basis/phi",
                basis.phi,
            )
            self.client.send_message(
                f"/qubit/{qubit}/measure/basis/label",
                basis.label,
            )
            if route is not None:
                self.client.send_message(
                    f"/qubit/{qubit}/measure/register",
                    route.target_register,
                )
                self.client.send_message(
                    f"/qubit/{qubit}/measure/route",
                    route.osc_route,
                )
                self.client.send_message(
                    f"/qubit/{qubit}/measure/persistence",
                    route.persistence,
                )
                self.client.send_message(
                    f"/qubit/{qubit}/measure/shots",
                    int(route.shots),
                )
                self.client.send_message(
                    f"/qubit/{qubit}/measure/register_bit",
                    -1 if route.register_bit is None else int(route.register_bit),
                )
                self.client.send_message(
                    f"/qubit/{qubit}/measure/process",
                    route.process,
                )

            if rho is None:
                continue

            reduced = partial_trace_one_qubit(rho, qubit, self.n_qubits)
            bx = float(np.trace(reduced @ X).real)
            by = float(np.trace(reduced @ Y).real)
            bz = float(np.trace(reduced @ Z).real)
            nx = math.sin(basis.theta) * math.cos(basis.phi)
            ny = math.sin(basis.theta) * math.sin(basis.phi)
            nz = math.cos(basis.theta)
            projection = float(np.clip(bx * nx + by * ny + bz * nz, -1.0, 1.0))
            prob0 = float(np.clip(0.5 * (projection + 1.0), 0.0, 1.0))
            prob1 = 1.0 - prob0
            outcome = int(self.measurement_rng.choice([0, 1], p=[prob0, prob1]))

            self.client.send_message(
                f"/qubit/{qubit}/measure/projection",
                projection,
            )
            self.client.send_message(f"/qubit/{qubit}/measure/prob0", prob0)
            self.client.send_message(f"/qubit/{qubit}/measure/prob1", prob1)
            self.client.send_message(f"/qubit/{qubit}/measure/outcome", outcome)
            self.client.send_message(f"/qubit/{qubit}/measure/collapse", 0)

            if route is not None:
                bitstring = str(outcome)
                payload = [
                    bitstring,
                    outcome,
                    qubit,
                    basis.label,
                    -1 if route.register_bit is None else int(route.register_bit),
                    route.process,
                    prob0,
                    prob1,
                    projection,
                    -1 if step is None else int(step),
                ]
                self.client.send_message(route.osc_route, payload)
                self.client.send_message(
                    f"/qmw/register/{route.target_register}/bitarray",
                    bitstring,
                )
                self.client.send_message(
                    f"/qmw/register/{route.target_register}/outcome",
                    outcome,
                )
                self.client.send_message(
                    f"/qmw/register/{route.target_register}/prob0",
                    prob0,
                )
                self.client.send_message(
                    f"/qmw/register/{route.target_register}/prob1",
                    prob1,
                )
                self.client.send_message(
                    f"/qmw/register/{route.target_register}/bit",
                    -1 if route.register_bit is None else int(route.register_bit),
                )
                self.client.send_message(
                    f"/qmw/register/{route.target_register}/process",
                    route.process,
                )

        if not active_items:
            return

        active_qubit, active_basis = active_items[-1]
        active_route = active_routes.get(active_qubit)
        active_step = step
        for op in reversed(self.registry_circuit.operations):
            basis = op.measurement_basis()
            if basis is None or len(op.qubits) != 1:
                continue

            qubit = op.qubits[0]
            if not isinstance(qubit, int):
                continue

            active_qubit = qubit
            active_basis = basis
            active_route = op.measurement_route
            active_step = op.step
            break

        self.client.send_message(
            "/circuit/measurement/active_qubit",
            int(active_qubit),
        )
        self.client.send_message(
            "/circuit/measurement/active_basis",
            active_basis.label,
        )
        self.client.send_message(
            "/circuit/measurement/step",
            -1 if active_step is None else int(active_step),
        )
        if active_route is not None:
            self.client.send_message(
                "/circuit/measurement/register",
                active_route.target_register,
            )
            self.client.send_message(
                "/circuit/measurement/osc_route",
                active_route.osc_route,
            )
            self.client.send_message(
                "/circuit/measurement/persistence",
                active_route.persistence,
            )
            self.client.send_message(
                "/circuit/measurement/shots",
                int(active_route.shots),
            )
            self.client.send_message(
                "/circuit/measurement/register_bit",
                -1 if active_route.register_bit is None else int(active_route.register_bit),
            )
            self.client.send_message(
                "/circuit/measurement/process",
                active_route.process,
            )
            self.client.send_message(
                "/circuit/measurement/mode",
                active_route.persistence,
            )
        else:
            self.client.send_message("/circuit/measurement/mode", "listen")

    def take_due_circuit_column(
        self,
        dt: float,
    ) -> Tuple[Optional[np.ndarray], Optional[int], List[str]]:
        """Return a due column unitary for generator unfolding by the owner."""
        # Explicit GUI Step: apply exactly one column immediately.
        if self._step_requested:
            self._step_requested = False
            return self.circuit.take_next_column()

        # Run mode: advance according to the circuit clock.
        if not self.circuit.enabled:
            return None, None, []

        self._elapsed += dt

        if self._elapsed < self.circuit_interval_seconds:
            return None, None, []

        self._elapsed %= self.circuit_interval_seconds
        return self.circuit.take_next_column()

    def apply_due_circuit_column(
        self,
        rho: np.ndarray,
        dt: float,
    ) -> Tuple[np.ndarray, Optional[int], List[str]]:
        """Backwards-compatible instantaneous circuit-column application."""
        unitary, column, labels = self.take_due_circuit_column(dt)
        if unitary is None:
            return rho, None, []
        return normalize_density(unitary @ rho @ unitary.conj().T), column, labels

    def update_and_send(self, rho: np.ndarray, hamiltonian: np.ndarray, dt: float, column: Optional[int] = None, labels: Sequence[str] = ()) -> PilotFrame:
        frame = (
            self._authoritative_pilot_frame
            if self._authoritative_pilot_frame is not None
            else self.pilot.update(rho, hamiltonian, dt)
        )
        telemetry_dt = max(float(dt), 0.0)
        if self.osc_telemetry_interval is not None:
            self._osc_telemetry_elapsed += telemetry_dt
            if self._osc_telemetry_elapsed < self.osc_telemetry_interval:
                # Discrete circuit events must not wait for the telemetry
                # clock, but continuous state messages can be rate-limited.
                if column is not None:
                    self.client.send_message(
                        "/qmw/circuit/gate_event",
                        [int(column), *[str(x) for x in labels]],
                    )
                return frame
            telemetry_dt = self._osc_telemetry_elapsed
            self._osc_telemetry_elapsed %= self.osc_telemetry_interval

        probabilities = np.real(np.diag(rho)).clip(0.0, 1.0)
        self.client.send_message("/qmw/circuit/playhead", int(self.circuit.current_column))
        self.client.send_message("/qmw/circuit/enabled", int(self.circuit.enabled))
        self.client.send_message("/qmw/density/probabilities", probabilities.astype(float).tolist())
        self.client.send_message("/qmw/density/purity", purity(rho))
        self.client.send_message("/qmw/density/coherence", coherence_l1(rho))
        self._send_measurement_bases(rho, column)
        self.client.send_message("/qmw/pilot/node", frame.node)
        self.client.send_message("/qmw/pilot/next_node", frame.next_node)
        self.client.send_message("/qmw/pilot/velocity", frame.velocity)
        self.client.send_message("/qmw/pilot/current", frame.current)
        self.client.send_message("/qmw/pilot/phase_gradient", frame.phase_gradient)
        self.client.send_message("/qmw/pilot/branch_entropy", frame.branch_entropy)
        self.client.send_message("/qmw/pilot/configuration", frame.next_node)
        self.client.send_message("/qmw/pilot/beable_basis", "computational_z")
        if column is not None:
            self.client.send_message("/qmw/circuit/gate_event", [int(column), *[str(x) for x in labels]])

        for q in range(self.n_qubits):
            reduced = partial_trace_one_qubit(rho, q, self.n_qubits)
            bx = float(np.trace(reduced @ X).real)
            by = float(np.trace(reduced @ Y).real)
            bz = float(np.trace(reduced @ Z).real)
            self.client.send_message(f"/qmw/density/q{q}/bloch", [bx, by, bz])
            self.client.send_message(f"/qmw/density/q{q}/entropy", entropy(reduced))

        # Pairwise mutual information derived from the live QMW density matrix.
        # This reflects the actual state after circuit, Hamiltonian, and noise dynamics.
        for qubit_a in range(self.n_qubits):
            for qubit_b in range(qubit_a + 1, self.n_qubits):
                mi = pairwise_mutual_information(
                    rho,
                    qubit_a,
                    qubit_b,
                    self.n_qubits,
                )
                self.client.send_message(
                    f"/qmw/density/mi/{qubit_a}{qubit_b}",
                    mi,
                )
        self._send_spin_state(rho, telemetry_dt)
        return frame

    def _send_spin_state(self, rho: np.ndarray, dt: float) -> None:
        """
        Stream density-derived spin observables for richer live visualization.

        These messages describe the actual mixed-state engine, not the Tk
        builder's pure-state preview.
        """
        dt = max(float(dt), 1e-9)

        for qubit in range(self.n_qubits):
            reduced = partial_trace_one_qubit(rho, qubit, self.n_qubits)
            bx, by, bz = bloch_from_density(reduced)
            vector = (bx, by, bz)
            spin_length = float(np.clip(math.sqrt(bx * bx + by * by + bz * bz), 0.0, 1.0))
            spin_phase = float(math.atan2(by, bx))
            spin_purity = purity(reduced)
            spin_entropy = entropy(reduced)

            previous = self._previous_spin_vectors[qubit]
            if previous is None:
                spin_speed = 0.0
            else:
                spin_speed = float(
                    math.sqrt(
                        (bx - previous[0]) ** 2
                        + (by - previous[1]) ** 2
                        + (bz - previous[2]) ** 2
                    )
                    / dt
                )
            self._previous_spin_vectors[qubit] = vector
            self._spin_trails[qubit].append(vector)

            trail_payload: List[float] = []
            for x, y, z in self._spin_trails[qubit]:
                trail_payload.extend([x, y, z])

            self.client.send_message(f"/qmw/spin/q{qubit}/bloch", [bx, by, bz])
            self.client.send_message(f"/qmw/spin/q{qubit}/length", spin_length)
            self.client.send_message(f"/qmw/spin/q{qubit}/phase", spin_phase)
            self.client.send_message(f"/qmw/spin/q{qubit}/purity", spin_purity)
            self.client.send_message(f"/qmw/spin/q{qubit}/entropy", spin_entropy)
            self.client.send_message(f"/qmw/spin/q{qubit}/speed", spin_speed)
            self.client.send_message(f"/qmw/spin/q{qubit}/trail", trail_payload)

            # Short aliases for Max/JSUI patches that prefer flat namespaces.
            self.client.send_message(f"/spin/{qubit}/x", bx)
            self.client.send_message(f"/spin/{qubit}/y", by)
            self.client.send_message(f"/spin/{qubit}/z", bz)
            self.client.send_message(f"/spin/{qubit}/phase", spin_phase)
            self.client.send_message(f"/spin/{qubit}/speed", spin_speed)

        for qubit_a in range(self.n_qubits):
            for qubit_b in range(qubit_a + 1, self.n_qubits):
                rho_pair = partial_trace(rho, (qubit_a, qubit_b), self.n_qubits)
                tensor = pair_spin_correlation_tensor(rho_pair)
                self.client.send_message(
                    f"/qmw/spin/pair/{qubit_a}_{qubit_b}/correlation",
                    tensor,
                )
                self.client.send_message(
                    f"/qmw/spin/pair/{qubit_a}_{qubit_b}/xx_yy_zz",
                    [tensor[0], tensor[4], tensor[8]],
                )


# ---- Integration example ----------------------------------------------------
# In quantum_population_v5.py:
#
# from qmw_circuit_bridge import QMWCircuitBridge
#
# bridge = QMWCircuitBridge(n_qubits=4, osc_out_port=9001, osc_control_port=9002)
# bridge.start_control_server()
#
# Inside the engine's existing step(dt), immediately BEFORE your normal
# Hamiltonian/Lindblad integration:
#
# self.rho, circuit_column, gate_labels = bridge.apply_due_circuit_column(self.rho, dt)
# self.rho = self.apply_lindblad_step(self.rho, dt)
# pilot_frame = bridge.update_and_send(self.rho, self.hamiltonian, dt,
#                                     circuit_column, gate_labels)
#
# Then pass pilot_frame to the population guidance method instead of using
# perturbation as the primary mover.
