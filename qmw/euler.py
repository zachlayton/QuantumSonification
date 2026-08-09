"""Shared one-qubit Euler decomposition data for QMW circuit workflows.

The canonical visual basis is ZXZ because it maps directly to a time-ordered
ZX wire:

    input -- Z(lambda) -- X(theta) -- Z(phi) -- output

Qiskit's matrix convention is
``exp(i*gamma) * RZ(phi) @ RX(theta) @ RZ(lambda)``; the right-most
``RZ(lambda)`` therefore acts first.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import math
from typing import Any, Iterable

import numpy as np


EULER_BASES = ("ZYZ", "ZXZ", "XYX", "XZX")


def wrap_angle(angle: float) -> float:
    """Wrap a radian angle to ``[-pi, pi)`` for display only."""
    return float((float(angle) + math.pi) % (2.0 * math.pi) - math.pi)


def _rotation(axis: str, angle: float) -> np.ndarray:
    half = 0.5 * float(angle)
    cosine = math.cos(half)
    sine = math.sin(half)
    identity = np.eye(2, dtype=np.complex128)
    pauli = {
        "X": np.array([[0, 1], [1, 0]], dtype=np.complex128),
        "Y": np.array([[0, -1j], [1j, 0]], dtype=np.complex128),
        "Z": np.array([[1, 0], [0, -1]], dtype=np.complex128),
    }[axis]
    return cosine * identity - 1j * sine * pauli


def reconstruct_euler(
    theta: float,
    phi: float,
    lam: float,
    gamma: float,
    *,
    basis: str = "ZXZ",
) -> np.ndarray:
    """Reconstruct a one-qubit matrix using Qiskit's Euler convention."""
    normalized = str(basis).strip().upper()
    axes = {
        "ZYZ": ("Z", "Y", "Z"),
        "ZXZ": ("Z", "X", "Z"),
        "XYX": ("X", "Y", "X"),
        "XZX": ("X", "Z", "X"),
    }.get(normalized)
    if axes is None:
        raise ValueError(
            f"Euler basis must be one of {', '.join(EULER_BASES)}"
        )
    return (
        np.exp(1j * float(gamma))
        * _rotation(axes[0], phi)
        @ _rotation(axes[1], theta)
        @ _rotation(axes[2], lam)
    )


@dataclass(frozen=True)
class OneQubitEuler:
    """Verified numerical Euler description of one 2x2 unitary."""

    basis: str
    theta: float
    phi: float
    lam: float
    gamma: float
    verified: bool
    absolute_error: float
    zx_scalar_phase: float

    @property
    def visual_phases(self) -> tuple[float, float, float]:
        """Return left-to-right temporal phases: lambda, theta, phi."""
        return (self.lam, self.theta, self.phi)

    @property
    def visual_axes(self) -> tuple[str, str, str]:
        """Return the left-to-right temporal axes for the Euler basis."""
        return (self.basis[2], self.basis[1], self.basis[0])

    @property
    def wrapped(self) -> tuple[float, float, float, float]:
        return tuple(
            wrap_angle(value)
            for value in (self.theta, self.phi, self.lam, self.gamma)
        )

    def reconstruct(self) -> np.ndarray:
        return reconstruct_euler(
            self.theta,
            self.phi,
            self.lam,
            self.gamma,
            basis=self.basis,
        )

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["lambda"] = payload.pop("lam")
        payload["visual_phases"] = list(self.visual_phases)
        payload["visual_axes"] = list(self.visual_axes)
        payload["wrapped"] = list(self.wrapped)
        return payload


def decompose_one_qubit(
    unitary: Any,
    *,
    basis: str = "ZXZ",
    atol: float = 1e-10,
) -> OneQubitEuler:
    """Decompose and independently verify a numeric 2x2 unitary."""
    normalized = str(basis).strip().upper()
    if normalized not in EULER_BASES:
        raise ValueError(
            f"Euler basis must be one of {', '.join(EULER_BASES)}"
        )
    matrix = np.asarray(unitary, dtype=np.complex128)
    if matrix.shape != (2, 2):
        raise ValueError("one-qubit Euler decomposition requires a 2x2 matrix")
    if not np.all(np.isfinite(matrix)):
        raise ValueError("unitary contains non-finite values")
    unity_error = float(
        np.linalg.norm(matrix.conj().T @ matrix - np.eye(2, dtype=complex))
    )
    if unity_error > float(atol) * 10.0:
        raise ValueError(
            f"matrix is not unitary; ||U†U-I||={unity_error:.6g}"
        )

    try:
        from qiskit.synthesis import OneQubitEulerDecomposer
    except ImportError as exc:
        raise ModuleNotFoundError(
            "Euler decomposition requires qiskit"
        ) from exc

    theta, phi, lam, gamma = (
        float(value)
        for value in OneQubitEulerDecomposer(
            basis=normalized
        ).angles_and_phase(matrix)
    )
    reconstructed = reconstruct_euler(
        theta,
        phi,
        lam,
        gamma,
        basis=normalized,
    )
    absolute_error = float(np.linalg.norm(matrix - reconstructed))
    scale = max(1.0, float(np.linalg.norm(matrix)))
    verified = absolute_error <= float(atol) * scale
    zx_scalar_phase = float(
        gamma - 0.5 * (phi + theta + lam)
    )
    return OneQubitEuler(
        normalized,
        theta,
        phi,
        lam,
        gamma,
        verified,
        absolute_error,
        zx_scalar_phase,
    )


@dataclass(frozen=True)
class EulerInstruction:
    instruction_index: int
    operation: str
    qubit: int
    decomposition: OneQubitEuler

    def to_dict(self) -> dict[str, Any]:
        return {
            "instruction_index": self.instruction_index,
            "operation": self.operation,
            "qubit": self.qubit,
            "decomposition": self.decomposition.to_dict(),
        }


@dataclass(frozen=True)
class SkippedEulerInstruction:
    instruction_index: int
    operation: str
    qubits: tuple[int, ...]
    reason: str

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["qubits"] = list(self.qubits)
        return payload


@dataclass(frozen=True)
class CircuitEulerReport:
    basis: str
    circuit_name: str
    n_qubits: int
    instruction_count: int
    decompositions: tuple[EulerInstruction, ...]
    skipped: tuple[SkippedEulerInstruction, ...]

    @property
    def verified(self) -> bool:
        return all(
            item.decomposition.verified for item in self.decompositions
        )

    @property
    def maximum_error(self) -> float:
        return max(
            (
                item.decomposition.absolute_error
                for item in self.decompositions
            ),
            default=0.0,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "basis": self.basis,
            "circuit_name": self.circuit_name,
            "n_qubits": self.n_qubits,
            "instruction_count": self.instruction_count,
            "decompositions": [
                item.to_dict() for item in self.decompositions
            ],
            "skipped": [item.to_dict() for item in self.skipped],
            "verified": self.verified,
            "maximum_error": self.maximum_error,
        }


def decompose_qiskit_circuit(
    circuit: Any,
    *,
    basis: str = "ZXZ",
    atol: float = 1e-10,
) -> CircuitEulerReport:
    """Describe every numeric one-qubit instruction in a Qiskit circuit."""
    if not hasattr(circuit, "data") or not hasattr(circuit, "find_bit"):
        raise TypeError("circuit must be a Qiskit QuantumCircuit-like object")
    try:
        from qiskit.quantum_info import Operator
    except ImportError as exc:
        raise ModuleNotFoundError(
            "circuit Euler decomposition requires qiskit"
        ) from exc

    decompositions: list[EulerInstruction] = []
    skipped: list[SkippedEulerInstruction] = []
    for index, instruction in enumerate(circuit.data):
        operation = instruction.operation
        name = str(operation.name)
        qubits = tuple(
            int(circuit.find_bit(qubit).index)
            for qubit in instruction.qubits
        )
        if instruction.clbits:
            skipped.append(
                SkippedEulerInstruction(
                    index, name, qubits, "classical or measurement instruction"
                )
            )
            continue
        if len(qubits) != 1:
            skipped.append(
                SkippedEulerInstruction(
                    index, name, qubits, "not a one-qubit instruction"
                )
            )
            continue
        parameters = getattr(operation, "params", ())
        if any(getattr(value, "parameters", set()) for value in parameters):
            skipped.append(
                SkippedEulerInstruction(
                    index, name, qubits, "contains unresolved parameters"
                )
            )
            continue
        try:
            matrix = np.asarray(Operator(operation).data, dtype=np.complex128)
            decomposition = decompose_one_qubit(
                matrix,
                basis=basis,
                atol=atol,
            )
        except (TypeError, ValueError) as exc:
            skipped.append(
                SkippedEulerInstruction(index, name, qubits, str(exc))
            )
            continue
        decompositions.append(
            EulerInstruction(index, name, qubits[0], decomposition)
        )

    return CircuitEulerReport(
        str(basis).strip().upper(),
        str(getattr(circuit, "name", "")),
        int(circuit.num_qubits),
        len(circuit.data),
        tuple(decompositions),
        tuple(skipped),
    )


def euler_osc_messages(
    report: CircuitEulerReport,
    *,
    revision: int,
    prefix: str = "/qmw/circuit/euler",
) -> Iterable[tuple[str, Any]]:
    """Yield a bounded OSC transaction for a circuit Euler report."""
    root = str(prefix).rstrip("/")
    yield (
        f"{root}/begin",
        [
            int(revision),
            len(report.decompositions),
            report.basis,
            report.n_qubits,
        ],
    )
    for item in report.decompositions:
        value = item.decomposition
        yield (
            f"{root}/gate",
            [
                int(revision),
                item.instruction_index,
                item.operation,
                item.qubit,
                value.theta,
                value.phi,
                value.lam,
                value.gamma,
                value.zx_scalar_phase,
                int(value.verified),
                value.absolute_error,
            ],
        )
    yield (
        f"{root}/end",
        [
            int(revision),
            len(report.decompositions),
            int(report.verified),
            report.maximum_error,
            len(report.skipped),
        ],
    )
