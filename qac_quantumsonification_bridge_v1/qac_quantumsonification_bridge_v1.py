#!/usr/bin/env python3
"""QAC Toolkit -> QuantumSonification bridge v1.

Receives OpenQASM exported by ``och.microqiskit`` in Max, simulates the
four-qubit pure state, derives density/Pauli/correlation material, and sends
that material back to Max over OSC.

Conventions
-----------
* Max q0 -> simulator q0 -> least-significant computational-basis bit.
* Basis labels are displayed as |q3 q2 q1 q0> for the default four qubits.
* OSC input defaults to 127.0.0.1:7401; output defaults to 127.0.0.1:7400.
* A new circuit revision is published atomically. Older revisions are rejected.

The bridge uses the shared ``qmw.euler`` service when Euler reporting is
enabled, so QAC, the conductor, Processing, and Max receive the same angle and
verification conventions. NumPy is required. ``python-osc`` is required only
for OSC server operation.
"""

from __future__ import annotations

import argparse
import ast
import json
import math
import re
import sys
import threading
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Iterable, Sequence
from urllib.parse import unquote

import numpy as np

try:
    from qmw.euler import (
        CircuitEulerReport,
        EulerInstruction,
        SkippedEulerInstruction,
        decompose_one_qubit,
        euler_osc_messages,
    )
except ModuleNotFoundError:
    # Keep direct ``python qac_quantumsonification_bridge_v1.py`` launches
    # working when the shell is inside this versioned bundle.
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from qmw.euler import (
        CircuitEulerReport,
        EulerInstruction,
        SkippedEulerInstruction,
        decompose_one_qubit,
        euler_osc_messages,
    )

try:
    from pythonosc import dispatcher, osc_server
    from pythonosc.udp_client import SimpleUDPClient
except ImportError:  # Unit tests and offline validation remain available.
    dispatcher = None
    osc_server = None
    SimpleUDPClient = None


VERSION = "1.2.0"
DEFAULT_IN_HOST = "127.0.0.1"
DEFAULT_IN_PORT = 7401
DEFAULT_OUT_HOST = "127.0.0.1"
DEFAULT_OUT_PORT = 7400
DEFAULT_ENGINE_CONTROL_PORT = 7402
DEFAULT_QUBITS = 4
MAX_QUBITS = 10
LIVE_GATE_ARITY = {
    "i": 1,
    "id": 1,
    "h": 1,
    "x": 1,
    "y": 1,
    "z": 1,
    "s": 1,
    "t": 1,
    "cx": 2,
    "cnot": 2,
}


class QASMError(ValueError):
    """OpenQASM syntax or circuit validation error."""


@dataclass(frozen=True)
class Operation:
    name: str
    qubits: tuple[int, ...] = ()
    params: tuple[float, ...] = ()


@dataclass(frozen=True)
class ParsedCircuit:
    n_qubits: int
    n_clbits: int
    operations: tuple[Operation, ...]
    measurements: tuple[tuple[int, int], ...] = ()


@dataclass(frozen=True)
class QuantumFrame:
    revision: int
    circuit: ParsedCircuit
    statevector: np.ndarray
    rho: np.ndarray
    probabilities: np.ndarray
    bloch: np.ndarray
    qubit_entropy: np.ndarray
    mutual_information: dict[str, float]
    pauli: dict[str, float]
    purity: float
    entropy: float
    coherence_l1: float
    dominant_index: int
    dominant_label: str
    dominant_probability: float
    counts: dict[str, int]
    euler: CircuitEulerReport | None = None


_NAME_RE = r"[A-Za-z_][A-Za-z0-9_]*"
_QREF_RE = re.compile(rf"^({_NAME_RE})\s*\[\s*(\d+)\s*\]$")
_DECL_QASM2_RE = re.compile(rf"^qreg\s+({_NAME_RE})\s*\[\s*(\d+)\s*\]$", re.I)
_DECL_C_QASM2_RE = re.compile(rf"^creg\s+({_NAME_RE})\s*\[\s*(\d+)\s*\]$", re.I)
_DECL_QASM3_RE = re.compile(rf"^qubit\s*\[\s*(\d+)\s*\]\s+({_NAME_RE})$", re.I)
_DECL_C_QASM3_RE = re.compile(rf"^bit\s*\[\s*(\d+)\s*\]\s+({_NAME_RE})$", re.I)


def _strip_comments(qasm: str) -> str:
    qasm = re.sub(r"/\*.*?\*/", "", qasm, flags=re.S)
    return re.sub(r"//[^\n\r]*", "", qasm)


def _statements(qasm: str) -> list[str]:
    """Split the supported flat OpenQASM subset without losing gate commas."""
    cleaned = _strip_comments(qasm).replace("\r", "\n")
    if "{" in cleaned or "}" in cleaned:
        raise QASMError(
            "Custom gate bodies and OpenQASM control-flow blocks are not supported in v1. "
            "Export a flattened circuit from QAC."
        )
    return [s.strip() for s in cleaned.split(";") if s.strip()]


_ALLOWED_BINOPS: dict[type[ast.operator], Callable[[float, float], float]] = {
    ast.Add: lambda a, b: a + b,
    ast.Sub: lambda a, b: a - b,
    ast.Mult: lambda a, b: a * b,
    ast.Div: lambda a, b: a / b,
    ast.Pow: lambda a, b: a**b,
}


def eval_angle(expression: str) -> float:
    """Safely evaluate numeric OpenQASM angle expressions containing pi."""
    try:
        node = ast.parse(expression.strip(), mode="eval").body
    except SyntaxError as exc:
        raise QASMError(f"Invalid angle expression: {expression!r}") from exc

    def visit(item: ast.AST) -> float:
        if isinstance(item, ast.Constant) and isinstance(item.value, (int, float)):
            return float(item.value)
        if isinstance(item, ast.Name) and item.id.lower() == "pi":
            return math.pi
        if isinstance(item, ast.UnaryOp) and isinstance(item.op, (ast.UAdd, ast.USub)):
            value = visit(item.operand)
            return value if isinstance(item.op, ast.UAdd) else -value
        if isinstance(item, ast.BinOp) and type(item.op) in _ALLOWED_BINOPS:
            return _ALLOWED_BINOPS[type(item.op)](visit(item.left), visit(item.right))
        raise QASMError(f"Unsupported angle expression: {expression!r}")

    value = visit(node)
    if not math.isfinite(value):
        raise QASMError(f"Non-finite angle expression: {expression!r}")
    return value


def _split_arguments(text: str) -> list[str]:
    result: list[str] = []
    start = 0
    depth = 0
    for index, char in enumerate(text):
        if char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
        elif char == "," and depth == 0:
            result.append(text[start:index].strip())
            start = index + 1
    result.append(text[start:].strip())
    return [item for item in result if item]


def parse_qasm(qasm: str, *, expected_qubits: int | None = DEFAULT_QUBITS) -> ParsedCircuit:
    """Parse the flattened QASM 2/QASM 3 subset emitted by QAC.

    Supported gates: id/i, x, y, z, h, s, sdg, t, tdg, sx, rx, ry, rz,
    p/u1, u/u3, cx/cnot, cy, cz, ch, swap, ccx/toffoli, barrier, measure.
    Final measurements are recorded but do not collapse the analytical state.
    """
    qregs: dict[str, tuple[int, int]] = {}
    cregs: dict[str, tuple[int, int]] = {}
    n_qubits = 0
    n_clbits = 0
    operations: list[Operation] = []
    measurements: list[tuple[int, int]] = []

    def qindex(token: str) -> int:
        match = _QREF_RE.fullmatch(token.strip())
        if not match or match.group(1) not in qregs:
            raise QASMError(f"Unknown qubit reference: {token!r}")
        name, local_text = match.groups()
        offset, size = qregs[name]
        local = int(local_text)
        if local >= size:
            raise QASMError(f"Qubit index out of range: {token!r}")
        return offset + local

    def cindex(token: str) -> int:
        match = _QREF_RE.fullmatch(token.strip())
        if not match or match.group(1) not in cregs:
            raise QASMError(f"Unknown classical-bit reference: {token!r}")
        name, local_text = match.groups()
        offset, size = cregs[name]
        local = int(local_text)
        if local >= size:
            raise QASMError(f"Classical-bit index out of range: {token!r}")
        return offset + local

    for statement in _statements(qasm):
        lower = statement.lower()
        if lower.startswith("openqasm") or lower.startswith("include"):
            continue
        if match := _DECL_QASM2_RE.fullmatch(statement):
            name, size_text = match.groups()
            size = int(size_text)
            qregs[name] = (n_qubits, size)
            n_qubits += size
            continue
        if match := _DECL_C_QASM2_RE.fullmatch(statement):
            name, size_text = match.groups()
            size = int(size_text)
            cregs[name] = (n_clbits, size)
            n_clbits += size
            continue
        if match := _DECL_QASM3_RE.fullmatch(statement):
            size_text, name = match.groups()
            size = int(size_text)
            qregs[name] = (n_qubits, size)
            n_qubits += size
            continue
        if match := _DECL_C_QASM3_RE.fullmatch(statement):
            size_text, name = match.groups()
            size = int(size_text)
            cregs[name] = (n_clbits, size)
            n_clbits += size
            continue
        if lower.startswith("barrier"):
            continue
        if lower.startswith("reset"):
            raise QASMError("reset is non-unitary and is reserved for the density-matrix backend")

        # QASM 3: c[0] = measure q[0]; QASM 2: measure q[0] -> c[0];
        match3 = re.fullmatch(rf"({_NAME_RE}\s*\[\s*\d+\s*\])\s*=\s*measure\s+(.+)", statement, re.I)
        match2 = re.fullmatch(r"measure\s+(.+?)\s*->\s*(.+)", statement, re.I)
        if match3:
            measurements.append((qindex(match3.group(2)), cindex(match3.group(1))))
            continue
        if match2:
            measurements.append((qindex(match2.group(1)), cindex(match2.group(2))))
            continue

        gate_match = re.fullmatch(rf"({_NAME_RE})(?:\s*\((.*)\))?\s+(.+)", statement, re.I)
        if not gate_match:
            raise QASMError(f"Unsupported statement: {statement!r}")
        name, params_text, args_text = gate_match.groups()
        canonical = {"i": "id", "cnot": "cx", "toffoli": "ccx", "u1": "p", "u3": "u"}.get(
            name.lower(), name.lower()
        )
        supported = {
            "id", "x", "y", "z", "h", "s", "sdg", "t", "tdg", "sx",
            "rx", "ry", "rz", "p", "u", "cx", "cy", "cz", "ch", "swap", "ccx",
        }
        if canonical not in supported:
            raise QASMError(f"Unsupported gate {name!r}; flatten or transpile the QAC circuit")
        args = tuple(qindex(token) for token in _split_arguments(args_text))
        params = tuple(eval_angle(token) for token in _split_arguments(params_text or ""))
        expected_args = 3 if canonical == "ccx" else 2 if canonical in {"cx", "cy", "cz", "ch", "swap"} else 1
        expected_params = 3 if canonical == "u" else 1 if canonical in {"rx", "ry", "rz", "p"} else 0
        if len(args) != expected_args or len(params) != expected_params:
            raise QASMError(
                f"Gate {name!r} expects {expected_args} qubit(s) and {expected_params} parameter(s)"
            )
        if len(set(args)) != len(args):
            raise QASMError(f"Gate {name!r} repeats a qubit: {args}")
        operations.append(Operation(canonical, args, params))

    if not qregs:
        raise QASMError("No qreg or qubit declaration found")
    if n_qubits > MAX_QUBITS:
        raise QASMError(f"Circuit has {n_qubits} qubits; safety maximum is {MAX_QUBITS}")
    if expected_qubits is not None and n_qubits != expected_qubits:
        raise QASMError(f"Expected {expected_qubits} qubits, received {n_qubits}")
    return ParsedCircuit(n_qubits, n_clbits, tuple(operations), tuple(measurements))


I2 = np.eye(2, dtype=np.complex128)
X = np.array([[0, 1], [1, 0]], dtype=np.complex128)
Y = np.array([[0, -1j], [1j, 0]], dtype=np.complex128)
Z = np.array([[1, 0], [0, -1]], dtype=np.complex128)
H = np.array([[1, 1], [1, -1]], dtype=np.complex128) / math.sqrt(2.0)
S = np.diag([1, 1j]).astype(np.complex128)
T = np.diag([1, np.exp(1j * math.pi / 4)]).astype(np.complex128)
SX = 0.5 * np.array([[1 + 1j, 1 - 1j], [1 - 1j, 1 + 1j]], dtype=np.complex128)


def _single_gate(operation: Operation) -> np.ndarray:
    name = operation.name
    fixed = {
        "id": I2, "x": X, "y": Y, "z": Z, "h": H, "s": S,
        "sdg": S.conj().T, "t": T, "tdg": T.conj().T, "sx": SX,
    }
    if name in fixed:
        return fixed[name]
    if name in {"rx", "ry", "rz", "p"}:
        theta = operation.params[0]
        if name == "rx":
            return math.cos(theta / 2) * I2 - 1j * math.sin(theta / 2) * X
        if name == "ry":
            return math.cos(theta / 2) * I2 - 1j * math.sin(theta / 2) * Y
        if name == "rz":
            return np.diag([np.exp(-0.5j * theta), np.exp(0.5j * theta)])
        return np.diag([1, np.exp(1j * theta)]).astype(np.complex128)
    if name == "u":
        theta, phi, lam = operation.params
        return np.array(
            [
                [math.cos(theta / 2), -np.exp(1j * lam) * math.sin(theta / 2)],
                [np.exp(1j * phi) * math.sin(theta / 2), np.exp(1j * (phi + lam)) * math.cos(theta / 2)],
            ],
            dtype=np.complex128,
        )
    raise QASMError(f"No single-qubit matrix for {name}")


def _apply_single(state: np.ndarray, gate: np.ndarray, qubit: int) -> None:
    stride = 1 << qubit
    period = stride << 1
    for base in range(0, state.size, period):
        for offset in range(stride):
            i0 = base + offset
            i1 = i0 + stride
            a, b = state[i0], state[i1]
            state[i0] = gate[0, 0] * a + gate[0, 1] * b
            state[i1] = gate[1, 0] * a + gate[1, 1] * b


def _apply_controlled(state: np.ndarray, gate: np.ndarray, control: int, target: int) -> None:
    target_mask = 1 << target
    control_mask = 1 << control
    for i0 in range(state.size):
        if (i0 & control_mask) and not (i0 & target_mask):
            i1 = i0 | target_mask
            a, b = state[i0], state[i1]
            state[i0] = gate[0, 0] * a + gate[0, 1] * b
            state[i1] = gate[1, 0] * a + gate[1, 1] * b


def simulate(circuit: ParsedCircuit) -> np.ndarray:
    state = np.zeros(1 << circuit.n_qubits, dtype=np.complex128)
    state[0] = 1.0
    for operation in circuit.operations:
        name, q = operation.name, operation.qubits
        if len(q) == 1:
            _apply_single(state, _single_gate(operation), q[0])
        elif name in {"cx", "cy", "cz", "ch"}:
            gate = {"cx": X, "cy": Y, "cz": Z, "ch": H}[name]
            _apply_controlled(state, gate, q[0], q[1])
        elif name == "swap":
            m0, m1 = 1 << q[0], 1 << q[1]
            for index in range(state.size):
                b0, b1 = bool(index & m0), bool(index & m1)
                if (not b0) and b1:
                    other = index ^ m0 ^ m1
                    state[index], state[other] = state[other], state[index]
        elif name == "ccx":
            c0, c1, target = q
            mt = 1 << target
            for i0 in range(state.size):
                if (i0 & (1 << c0)) and (i0 & (1 << c1)) and not (i0 & mt):
                    i1 = i0 | mt
                    state[i0], state[i1] = state[i1], state[i0]
        else:
            raise QASMError(f"Simulation not implemented for gate {name!r}")
    norm = float(np.linalg.norm(state))
    if norm <= 0 or not math.isfinite(norm):
        raise QASMError("Circuit produced an invalid statevector")
    return state / norm


def circuit_euler_report(
    circuit: ParsedCircuit,
    *,
    basis: str = "ZXZ",
) -> CircuitEulerReport:
    """Decompose every one-qubit QAC operation using the shared service."""
    decompositions: list[EulerInstruction] = []
    skipped: list[SkippedEulerInstruction] = []
    for index, operation in enumerate(circuit.operations):
        if len(operation.qubits) != 1:
            skipped.append(
                SkippedEulerInstruction(
                    index,
                    operation.name,
                    operation.qubits,
                    "not a one-qubit instruction",
                )
            )
            continue
        result = decompose_one_qubit(
            _single_gate(operation),
            basis=basis,
        )
        decompositions.append(
            EulerInstruction(
                index,
                operation.name,
                operation.qubits[0],
                result,
            )
        )
    for offset, (qubit, _clbit) in enumerate(circuit.measurements):
        skipped.append(
            SkippedEulerInstruction(
                len(circuit.operations) + offset,
                "measure",
                (qubit,),
                "classical or measurement instruction",
            )
        )
    return CircuitEulerReport(
        str(basis).strip().upper(),
        "qac",
        circuit.n_qubits,
        len(circuit.operations) + len(circuit.measurements),
        tuple(decompositions),
        tuple(skipped),
    )


def _partial_trace_keep(rho: np.ndarray, keep: Sequence[int], n_qubits: int) -> np.ndarray:
    keep_set = set(keep)
    traced = rho.reshape([2] * (2 * n_qubits))
    # Tensor axes are q(n-1)..q0 for rows, followed by q(n-1)..q0 for cols.
    remaining = list(range(n_qubits))
    for qubit in sorted((q for q in range(n_qubits) if q not in keep_set), reverse=True):
        position = remaining.index(qubit)
        row_axis = len(remaining) - 1 - position
        col_axis = row_axis + len(remaining)
        traced = np.trace(traced, axis1=row_axis, axis2=col_axis)
        remaining.remove(qubit)
    return traced.reshape(1 << len(keep), 1 << len(keep))


def von_neumann_entropy(rho: np.ndarray) -> float:
    values = np.linalg.eigvalsh((rho + rho.conj().T) * 0.5).real
    values = values[values > 1e-14]
    return float(-np.sum(values * np.log2(values))) if values.size else 0.0


def pauli_terms(n_qubits: int) -> list[str]:
    """Canonical 34-term ecology for four qubits; generalized when requested."""
    identity = "I" * n_qubits
    result = [identity]
    for qubit in range(n_qubits):
        position = n_qubits - 1 - qubit
        for axis in "XYZ":
            chars = list(identity)
            chars[position] = axis
            result.append("".join(chars))
    for a in range(n_qubits):
        for b in range(a + 1, n_qubits):
            for axis in "XYZ":
                chars = list(identity)
                chars[n_qubits - 1 - a] = axis
                chars[n_qubits - 1 - b] = axis
                result.append("".join(chars))
    result.extend(axis * n_qubits for axis in "XYZ")
    return list(dict.fromkeys(result))


def _pauli_expectation(state: np.ndarray, term: str) -> float:
    transformed = state.copy()
    n = len(term)
    for position, axis in enumerate(term):
        if axis != "I":
            qubit = n - 1 - position
            _apply_single(transformed, {"X": X, "Y": Y, "Z": Z}[axis], qubit)
    return float(np.vdot(state, transformed).real)


def _sample_counts(probabilities: np.ndarray, shots: int, n_qubits: int, seed: int) -> dict[str, int]:
    if shots <= 0:
        return {}
    rng = np.random.default_rng(seed)
    samples = rng.choice(probabilities.size, size=shots, p=probabilities)
    values, frequencies = np.unique(samples, return_counts=True)
    return {format(int(value), f"0{n_qubits}b"): int(count) for value, count in zip(values, frequencies)}


def analyze(
    circuit: ParsedCircuit,
    revision: int,
    *,
    shots: int = 1024,
    seed: int = 0,
    euler_basis: str = "ZXZ",
    include_euler: bool = True,
) -> QuantumFrame:
    state = simulate(circuit)
    rho = np.outer(state, state.conj())
    probabilities = np.abs(state) ** 2
    n = circuit.n_qubits
    bloch = np.zeros((n, 3), dtype=np.float64)
    qubit_entropy = np.zeros(n, dtype=np.float64)
    reduced_single: dict[int, np.ndarray] = {}
    for q in range(n):
        reduced = _partial_trace_keep(rho, [q], n)
        reduced_single[q] = reduced
        bloch[q] = [np.trace(reduced @ axis).real for axis in (X, Y, Z)]
        qubit_entropy[q] = von_neumann_entropy(reduced)
    mutual_information: dict[str, float] = {}
    for a in range(n):
        for b in range(a + 1, n):
            pair = _partial_trace_keep(rho, [a, b], n)
            mutual_information[f"{a}{b}"] = max(
                0.0, von_neumann_entropy(reduced_single[a]) + von_neumann_entropy(reduced_single[b])
                - von_neumann_entropy(pair)
            )
    pauli = {term: _pauli_expectation(state, term) for term in pauli_terms(n)}
    purity = float(np.trace(rho @ rho).real)
    entropy = von_neumann_entropy(rho)
    coherence_l1 = float(np.sum(np.abs(rho)) - np.sum(np.abs(np.diag(rho))))
    dominant_index = int(np.argmax(probabilities))
    dominant_label = format(dominant_index, f"0{n}b")
    return QuantumFrame(
        revision=revision,
        circuit=circuit,
        statevector=state,
        rho=rho,
        probabilities=probabilities,
        bloch=bloch,
        qubit_entropy=qubit_entropy,
        mutual_information=mutual_information,
        pauli=pauli,
        purity=purity,
        entropy=entropy,
        coherence_l1=coherence_l1,
        dominant_index=dominant_index,
        dominant_label=dominant_label,
        dominant_probability=float(probabilities[dominant_index]),
        counts=_sample_counts(probabilities, shots, n, seed + revision),
        euler=(
            circuit_euler_report(circuit, basis=euler_basis)
            if include_euler
            else None
        ),
    )


@dataclass
class ChunkTransfer:
    revision: int
    total: int
    chunks: dict[int, str] = field(default_factory=dict)

    def add(self, index: int, encoded_text: str) -> None:
        if not 0 <= index < self.total:
            raise QASMError(f"Chunk {index} outside 0..{self.total - 1}")
        # Keep chunks encoded until reassembly: a Max-side character slice may
        # legally divide a percent escape such as ``%0A`` across two packets.
        self.chunks[index] = encoded_text

    @property
    def complete(self) -> bool:
        return len(self.chunks) == self.total

    def assemble(self) -> str:
        if not self.complete:
            missing = [i for i in range(self.total) if i not in self.chunks]
            raise QASMError(f"Incomplete QASM transfer; missing chunks {missing}")
        return unquote("".join(self.chunks[i] for i in range(self.total)))


class BridgeCore:
    """Thread-safe revision, transfer, parsing, and analysis core."""

    def __init__(
        self,
        *,
        expected_qubits: int = DEFAULT_QUBITS,
        shots: int = 1024,
        seed: int = 0,
        euler_basis: str = "ZXZ",
        include_euler: bool = True,
    ) -> None:
        self.expected_qubits = expected_qubits
        self.shots = shots
        self.seed = seed
        self.euler_basis = str(euler_basis).strip().upper()
        self.include_euler = bool(include_euler)
        self.revision = -1
        self.frame: QuantumFrame | None = None
        self.transfer: ChunkTransfer | None = None
        self.lock = threading.RLock()

    def begin(self, revision: int, total: int) -> None:
        with self.lock:
            if revision <= self.revision:
                raise QASMError(f"Stale revision {revision}; current revision is {self.revision}")
            if not 1 <= total <= 4096:
                raise QASMError("Chunk count must be between 1 and 4096")
            self.transfer = ChunkTransfer(revision, total)

    def chunk(self, revision: int, index: int, total: int, encoded_text: str) -> None:
        with self.lock:
            if self.transfer is None or self.transfer.revision != revision:
                self.begin(revision, total)
            assert self.transfer is not None
            if self.transfer.total != total:
                raise QASMError("Chunk total changed during transfer")
            self.transfer.add(index, encoded_text)

    def end(self, revision: int) -> QuantumFrame:
        with self.lock:
            if self.transfer is None or self.transfer.revision != revision:
                raise QASMError(f"No active QASM transfer for revision {revision}")
            qasm = self.transfer.assemble()
            self.transfer = None
        return self.submit(qasm, revision)

    def submit(self, qasm: str, revision: int | None = None) -> QuantumFrame:
        with self.lock:
            candidate_revision = self.revision + 1 if revision is None else int(revision)
            if candidate_revision <= self.revision:
                raise QASMError(f"Stale revision {candidate_revision}; current revision is {self.revision}")
        # Do expensive work before the atomic publication lock.
        circuit = parse_qasm(qasm, expected_qubits=self.expected_qubits)
        frame = analyze(
            circuit,
            candidate_revision,
            shots=self.shots,
            seed=self.seed,
            euler_basis=self.euler_basis,
            include_euler=self.include_euler,
        )
        with self.lock:
            if candidate_revision <= self.revision:
                raise QASMError(f"Revision {candidate_revision} became stale during computation")
            self.frame = frame
            self.revision = candidate_revision
        return frame

    def clear(self) -> None:
        with self.lock:
            self.frame = None
            self.transfer = None
            self.revision = -1


class QACOSCBridge:
    def __init__(
        self,
        *,
        in_host: str = DEFAULT_IN_HOST,
        in_port: int = DEFAULT_IN_PORT,
        out_host: str = DEFAULT_OUT_HOST,
        out_port: int = DEFAULT_OUT_PORT,
        expected_qubits: int = DEFAULT_QUBITS,
        shots: int = 1024,
        seed: int = 0,
        engine_control_host: str | None = None,
        engine_control_port: int = DEFAULT_ENGINE_CONTROL_PORT,
        euler_basis: str = "ZXZ",
        include_euler: bool = True,
        euler_mirror_host: str | None = None,
        euler_mirror_port: int | None = None,
    ) -> None:
        if dispatcher is None or osc_server is None or SimpleUDPClient is None:
            raise RuntimeError("OSC mode requires python-osc: python -m pip install python-osc")
        self.in_host, self.in_port = in_host, in_port
        self.out_host, self.out_port = out_host, out_port
        self.core = BridgeCore(
            expected_qubits=expected_qubits,
            shots=shots,
            seed=seed,
            euler_basis=euler_basis,
            include_euler=include_euler,
        )
        self.client = SimpleUDPClient(out_host, out_port)
        self.euler_client = (
            SimpleUDPClient(euler_mirror_host, int(euler_mirror_port))
            if euler_mirror_host is not None and euler_mirror_port is not None
            and (euler_mirror_host, int(euler_mirror_port))
            != (out_host, int(out_port))
            else None
        )
        self.engine_client = (
            SimpleUDPClient(engine_control_host, engine_control_port)
            if engine_control_host
            else None
        )
        self.engine_control_host = engine_control_host
        self.engine_control_port = engine_control_port
        self.live_gate_revision = -1
        self.live_gate_lock = threading.RLock()
        routes = dispatcher.Dispatcher()
        routes.map("/qmw/qac/qasm", self._qasm)
        routes.map("/qmw/qac/begin", self._begin)
        routes.map("/qmw/qac/chunk", self._chunk)
        routes.map("/qmw/qac/end", self._end)
        routes.map("/qmw/qac/run", self._run)
        routes.map("/qmw/qac/clear", self._clear)
        routes.map("/qmw/qac/shots", self._shots)
        routes.map("/qmw/qac/ping", self._ping)
        routes.map("/qmw/qac/gate", self._gate)
        self.server = osc_server.ThreadingOSCUDPServer((in_host, in_port), routes)

    def send(self, address: str, value: Any) -> None:
        self.client.send_message(address, value)

    def send_euler(self, address: str, value: Any) -> None:
        self.send(address, value)
        if self.euler_client is not None:
            self.euler_client.send_message(address, value)

    def _guard(self, fn: Callable[[], Any]) -> Any:
        try:
            return fn()
        except Exception as exc:
            self.send("/qmw/qac/error", str(exc))
            print(f"[QAC bridge error] {exc}")
            return None

    def _qasm(self, _address: str, *args: Any) -> None:
        def work() -> None:
            if not args:
                raise QASMError("/qmw/qac/qasm requires QASM text")
            if isinstance(args[0], int) and len(args) > 1:
                revision, qasm = int(args[0]), " ".join(map(str, args[1:]))
            else:
                revision, qasm = None, " ".join(map(str, args))
            self.publish(self.core.submit(unquote(qasm), revision))
        self._guard(work)

    def _begin(self, _address: str, revision: int, total: int) -> None:
        self._guard(lambda: self.core.begin(int(revision), int(total)))

    def _chunk(self, _address: str, revision: int, index: int, total: int, encoded_text: str) -> None:
        self._guard(lambda: self.core.chunk(int(revision), int(index), int(total), str(encoded_text)))

    def _end(self, _address: str, revision: int) -> None:
        def work() -> None:
            self.publish(self.core.end(int(revision)))
        self._guard(work)

    def _run(self, _address: str, *_args: Any) -> None:
        def work() -> None:
            if self.core.frame is None:
                raise QASMError("No accepted QASM circuit to run")
            self.publish(self.core.frame)
        self._guard(work)

    def _clear(self, _address: str, *_args: Any) -> None:
        self.core.clear()
        self.send("/qmw/qac/status", ["cleared", VERSION])

    def _shots(self, _address: str, shots: int) -> None:
        def work() -> None:
            value = int(shots)
            if not 0 <= value <= 1_000_000:
                raise QASMError("shots must be between 0 and 1000000")
            self.core.shots = value
            self.send("/qmw/qac/shots", value)
        self._guard(work)

    def _ping(self, _address: str, *_args: Any) -> None:
        self.send("/qmw/qac/status", ["ready", VERSION, self.core.revision])

    def _gate(self, _address: str, event_id: int, gate: str, *qubits: int) -> None:
        """Validate and relay one gate onto the engine's evolving density state."""
        def work() -> None:
            if self.engine_client is None:
                raise QASMError("Live gate requires an engine control connection")
            revision = int(event_id)
            name = str(gate).strip().lower()
            if name not in LIVE_GATE_ARITY:
                raise QASMError(f"Unsupported live gate: {gate}")
            logical_qubits = tuple(int(qubit) for qubit in qubits)
            if len(logical_qubits) != LIVE_GATE_ARITY[name]:
                raise QASMError(
                    f"Gate {name} requires {LIVE_GATE_ARITY[name]} qubits; "
                    f"got {len(logical_qubits)}"
                )
            if any(qubit < 0 or qubit >= self.core.expected_qubits for qubit in logical_qubits):
                raise QASMError(f"Live-gate qubit out of range: {logical_qubits}")
            if len(set(logical_qubits)) != len(logical_qubits):
                raise QASMError(f"Live-gate qubits must be distinct: {logical_qubits}")
            with self.live_gate_lock:
                if revision <= self.live_gate_revision:
                    raise QASMError(
                        f"Stale live-gate revision {revision}; "
                        f"current is {self.live_gate_revision}"
                    )
                self.engine_client.send_message(
                    "/qmw/state/gate",
                    [revision, name, *logical_qubits, "q0_lsb"],
                )
                self.live_gate_revision = revision
            self.send(
                "/qmw/qac/gate/forwarded",
                [revision, name, *logical_qubits],
            )
        self._guard(work)

    def publish(self, frame: QuantumFrame) -> None:
        n = frame.circuit.n_qubits
        self.send("/qmw/qac/revision", frame.revision)
        self.send("/qmw/qac/statevector/real", frame.statevector.real.tolist())
        self.send("/qmw/qac/statevector/imag", frame.statevector.imag.tolist())
        self.send("/qmw/qac/probabilities", frame.probabilities.tolist())
        self.send("/qmw/qac/rho/real", frame.rho.real.reshape(-1).tolist())
        self.send("/qmw/qac/rho/imag", frame.rho.imag.reshape(-1).tolist())
        self.send("/qmw/qac/global/purity", frame.purity)
        self.send("/qmw/qac/global/entropy", frame.entropy)
        self.send("/qmw/qac/global/coherence_l1", frame.coherence_l1)
        self.send(
            "/qmw/qac/dominant",
            [frame.dominant_index, frame.dominant_label, frame.dominant_probability],
        )
        for q in range(n):
            self.send(f"/qmw/qac/qubit/{q}/bloch", frame.bloch[q].tolist())
            self.send(f"/qmw/qac/qubit/{q}/entropy", float(frame.qubit_entropy[q]))
        for pair, value in frame.mutual_information.items():
            self.send(f"/qmw/qac/mi/{pair}", value)
        for term, value in frame.pauli.items():
            self.send(f"/qmw/qac/pauli/{term}", value)
        if frame.euler is not None:
            for address, payload in euler_osc_messages(
                frame.euler,
                revision=frame.revision,
            ):
                self.send_euler(address, payload)
        counts_flat: list[Any] = []
        for label, count in sorted(frame.counts.items()):
            counts_flat.extend([label, count])
        self.send("/qmw/qac/counts", counts_flat)
        self.send(
            "/qmw/qac/accepted",
            [frame.revision, n, len(frame.circuit.operations), len(frame.circuit.measurements)],
        )
        self.inject_density(frame)

    def inject_density(self, frame: QuantumFrame) -> None:
        """Send one atomic q0-LSB density candidate to the resonator control port."""
        if self.engine_client is None:
            return
        revision = int(frame.revision)
        self.engine_client.send_message(
            "/qmw/state/begin", [revision, frame.circuit.n_qubits, "q0_lsb"]
        )
        self.engine_client.send_message(
            "/qmw/state/rho/real", [revision, *frame.rho.real.reshape(-1).tolist()]
        )
        self.engine_client.send_message(
            "/qmw/state/rho/imag", [revision, *frame.rho.imag.reshape(-1).tolist()]
        )
        self.engine_client.send_message("/qmw/state/commit", revision)
        self.send(
            "/qmw/qac/state_candidate",
            [revision, self.engine_control_host, self.engine_control_port],
        )

    def serve_forever(self) -> None:
        print(f"QAC -> QuantumSonification bridge v{VERSION}")
        print(f"  OSC in:   {self.in_host}:{self.in_port}")
        print(f"  OSC out:  {self.out_host}:{self.out_port}")
        print(f"  qubits:   {self.core.expected_qubits}")
        print("  ordering: |q3 q2 q1 q0> (q0 is LSB)")
        if self.engine_client is not None:
            print(
                f"  inject:   {self.engine_control_host}:{self.engine_control_port} "
                "(atomic density seed)"
            )
        self.send("/qmw/qac/status", ["ready", VERSION, self.core.revision])
        try:
            self.server.serve_forever()
        except KeyboardInterrupt:
            pass
        finally:
            self.server.shutdown()
            self.server.server_close()


def frame_to_json(frame: QuantumFrame) -> dict[str, Any]:
    return {
        "revision": frame.revision,
        "n_qubits": frame.circuit.n_qubits,
        "operations": len(frame.circuit.operations),
        "measurements": list(frame.circuit.measurements),
        "statevector": {
            "real": frame.statevector.real.tolist(),
            "imag": frame.statevector.imag.tolist(),
        },
        "probabilities": frame.probabilities.tolist(),
        "rho": {"real": frame.rho.real.tolist(), "imag": frame.rho.imag.tolist()},
        "bloch": frame.bloch.tolist(),
        "qubit_entropy": frame.qubit_entropy.tolist(),
        "mutual_information": frame.mutual_information,
        "pauli": frame.pauli,
        "purity": frame.purity,
        "entropy": frame.entropy,
        "coherence_l1": frame.coherence_l1,
        "dominant": {
            "index": frame.dominant_index,
            "label": frame.dominant_label,
            "probability": frame.dominant_probability,
        },
        "counts": frame.counts,
        "euler": None if frame.euler is None else frame.euler.to_dict(),
    }


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--qasm", type=Path, help="analyze one QASM file and exit")
    parser.add_argument("--json-out", type=Path, help="write offline analysis as JSON")
    parser.add_argument("--in-host", default=DEFAULT_IN_HOST)
    parser.add_argument("--in-port", type=int, default=DEFAULT_IN_PORT)
    parser.add_argument("--out-host", default=DEFAULT_OUT_HOST)
    parser.add_argument("--out-port", type=int, default=DEFAULT_OUT_PORT)
    parser.add_argument(
        "--engine-control-host",
        default=None,
        help="inject accepted density states into this resonator host; disabled by default",
    )
    parser.add_argument(
        "--engine-control-port", type=int, default=DEFAULT_ENGINE_CONTROL_PORT
    )
    parser.add_argument("--qubits", type=int, default=DEFAULT_QUBITS)
    parser.add_argument("--shots", type=int, default=1024)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--euler-basis", default="ZXZ")
    parser.add_argument(
        "--no-euler",
        action="store_true",
        help="disable shared one-qubit Euler reporting",
    )
    parser.add_argument("--euler-mirror-host", default=None)
    parser.add_argument("--euler-mirror-port", type=int, default=None)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_arg_parser().parse_args(argv)
    if args.qasm:
        circuit = parse_qasm(args.qasm.read_text(encoding="utf-8"), expected_qubits=args.qubits)
        payload = frame_to_json(
            analyze(
                circuit,
                0,
                shots=args.shots,
                seed=args.seed,
                euler_basis=args.euler_basis,
                include_euler=not args.no_euler,
            )
        )
        text = json.dumps(payload, indent=2)
        if args.json_out:
            args.json_out.write_text(text + "\n", encoding="utf-8")
            print(args.json_out)
        else:
            print(text)
        return 0
    bridge = QACOSCBridge(
        in_host=args.in_host,
        in_port=args.in_port,
        out_host=args.out_host,
        out_port=args.out_port,
        expected_qubits=args.qubits,
        shots=args.shots,
        seed=args.seed,
        engine_control_host=args.engine_control_host,
        engine_control_port=args.engine_control_port,
        euler_basis=args.euler_basis,
        include_euler=not args.no_euler,
        euler_mirror_host=args.euler_mirror_host,
        euler_mirror_port=args.euler_mirror_port,
    )
    bridge.serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
