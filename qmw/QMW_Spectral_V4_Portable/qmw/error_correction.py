"""Auditable stabilizer syndromes and discrete Pauli recovery experiments.

This module is deliberately separate from continuous Lindblad evolution.
``ExperimentalCorruptionFrame`` is an opt-in side branch over an authoritative
``QuantumFrame``; it never edits the engine-owned density operator.  A
``RecoveryIntervention`` can be converted to the existing
``UnitaryGateControl`` when a caller deliberately chooses to commit it through
the authoritative engine on a subsequent transaction.

Version 1 supplies the three-data-qubit repetition code for deterministic
single-X experiments.  It does not claim to correct phase errors, arbitrary
channels, or unresolved syndrome mixtures.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product
import math
from threading import RLock
from types import MappingProxyType
from typing import Mapping

import numpy as np

from qmw.quantum.control import UnitaryGateControl
from qmw.quantum.dynamics import QuantumFrame
from qmw.quantum.pauli_basis import normalize_pauli_label, pauli_matrix


Array = np.ndarray
SyndromeSigns = tuple[int, ...]
_TOLERANCE = 1.0e-10


def _readonly(values: object, *, dtype: object = np.complex128) -> Array:
    result = np.array(values, dtype=dtype, copy=True)
    result.flags.writeable = False
    return result


def _density(values: object, *, tolerance: float = _TOLERANCE) -> Array:
    result = np.asarray(values, dtype=np.complex128)
    if result.ndim != 2 or result.shape[0] != result.shape[1] or result.shape[0] < 2:
        raise ValueError("rho must be a nontrivial square matrix")
    if not np.all(np.isfinite(result)):
        raise ValueError("rho must be finite")
    if not np.allclose(result, result.conj().T, atol=tolerance, rtol=0.0):
        raise ValueError("rho must be Hermitian")
    trace = complex(np.trace(result))
    if abs(trace.imag) > tolerance or not math.isclose(
        trace.real, 1.0, rel_tol=0.0, abs_tol=tolerance
    ):
        raise ValueError("rho must have unit trace")
    if float(np.min(np.linalg.eigvalsh(result))) < -tolerance:
        raise ValueError("rho must be positive semidefinite")
    return _readonly((result + result.conj().T) * 0.5)


def _pauli_commutation_sign(left: str, right: str) -> int:
    left_matrix = pauli_matrix(left)
    right_matrix = pauli_matrix(right)
    if np.allclose(left_matrix @ right_matrix, right_matrix @ left_matrix):
        return 1
    if np.allclose(left_matrix @ right_matrix, -(right_matrix @ left_matrix)):
        return -1
    raise ValueError("Pauli operators must commute or anticommute")


@dataclass(frozen=True)
class StabilizerCode:
    """One commuting Pauli-stabilizer code and an audited correction table."""

    name: str
    qubits: int
    stabilizer_labels: tuple[str, ...]
    correction_labels: Mapping[SyndromeSigns, str]
    provenance: str = "qmw_stabilizer_code_v1"

    def __post_init__(self) -> None:
        if not str(self.name):
            raise ValueError("code name must be nonempty")
        if isinstance(self.qubits, bool) or int(self.qubits) != self.qubits or self.qubits < 1:
            raise ValueError("qubits must be a positive integer")
        qubits = int(self.qubits)
        stabilizers = tuple(normalize_pauli_label(label) for label in self.stabilizer_labels)
        if not stabilizers or any(len(label) != qubits for label in stabilizers):
            raise ValueError("stabilizer labels must match the code width")
        if len(set(stabilizers)) != len(stabilizers):
            raise ValueError("stabilizer labels must be unique")
        for left_index, left in enumerate(stabilizers):
            for right in stabilizers[left_index + 1 :]:
                if _pauli_commutation_sign(left, right) != 1:
                    raise ValueError("stabilizer generators must commute")

        corrections: dict[SyndromeSigns, str] = {}
        for raw_signs, raw_label in dict(self.correction_labels).items():
            signs = tuple(int(sign) for sign in raw_signs)
            label = normalize_pauli_label(raw_label)
            if len(signs) != len(stabilizers) or any(sign not in (-1, 1) for sign in signs):
                raise ValueError("syndrome keys must contain one +/-1 sign per stabilizer")
            if len(label) != qubits:
                raise ValueError("correction labels must match the code width")
            actual = tuple(_pauli_commutation_sign(label, stabilizer) for stabilizer in stabilizers)
            if actual != signs:
                raise ValueError("correction Pauli does not match its syndrome key")
            corrections[signs] = label
        if tuple(1 for _ in stabilizers) not in corrections:
            raise ValueError("correction table must contain the no-error syndrome")
        expected_signs = set(product((-1, 1), repeat=len(stabilizers)))
        if set(corrections) != expected_signs:
            raise ValueError("correction table must cover every stabilizer syndrome")
        if not str(self.provenance):
            raise ValueError("provenance must be nonempty")
        object.__setattr__(self, "qubits", qubits)
        object.__setattr__(self, "stabilizer_labels", stabilizers)
        object.__setattr__(self, "correction_labels", MappingProxyType(corrections))

    @property
    def dimension(self) -> int:
        return 2**self.qubits

    @property
    def code_projector(self) -> Array:
        projector = np.eye(self.dimension, dtype=np.complex128)
        identity = np.eye(self.dimension, dtype=np.complex128)
        for label in self.stabilizer_labels:
            projector = projector @ ((identity + pauli_matrix(label)) * 0.5)
        return _readonly((projector + projector.conj().T) * 0.5)


def three_qubit_bit_flip_code(
    total_qubits: int = 4,
    *,
    data_qubits: tuple[int, int, int] = (0, 1, 2),
) -> StabilizerCode:
    """Return the repetition code embedded in displayed computational order."""

    if isinstance(total_qubits, bool) or int(total_qubits) != total_qubits or total_qubits < 3:
        raise ValueError("total_qubits must be an integer >= 3")
    width = int(total_qubits)
    data = tuple(int(index) for index in data_qubits)
    if len(data) != 3 or len(set(data)) != 3 or any(index < 0 or index >= width for index in data):
        raise ValueError("data_qubits must name three distinct in-range qubits")

    def label(assignments: Mapping[int, str]) -> str:
        symbols = ["I"] * width
        for index, symbol in assignments.items():
            symbols[index] = symbol
        return "".join(symbols)

    stabilizers = (
        label({data[0]: "Z", data[1]: "Z"}),
        label({data[1]: "Z", data[2]: "Z"}),
    )
    identity = "I" * width
    corrections = {
        (1, 1): identity,
        (-1, 1): label({data[0]: "X"}),
        (-1, -1): label({data[1]: "X"}),
        (1, -1): label({data[2]: "X"}),
    }
    return StabilizerCode(
        name="three_qubit_bit_flip_repetition",
        qubits=width,
        stabilizer_labels=stabilizers,
        correction_labels=corrections,
        provenance="qmw_three_qubit_bit_flip_code_v1",
    )


@dataclass(frozen=True)
class ExperimentalCorruptionRequest:
    """One explicitly requested Pauli corruption, never a Lindblad channel."""

    request_id: int
    pauli_label: str
    label: str = "experimental_pauli_corruption"
    provenance: str = "qmw_opt_in_experimental_corruption_request_v1"

    def __post_init__(self) -> None:
        if isinstance(self.request_id, bool) or int(self.request_id) != self.request_id:
            raise ValueError("request_id must be an integer")
        if self.request_id < 0:
            raise ValueError("request_id must be nonnegative")
        if not str(self.label) or not str(self.provenance):
            raise ValueError("label and provenance must be nonempty")
        object.__setattr__(self, "request_id", int(self.request_id))
        object.__setattr__(self, "pauli_label", normalize_pauli_label(self.pauli_label))


@dataclass(frozen=True)
class ExperimentalCorruptionFrame:
    """Read-only diagnostic branch produced by one opt-in corruption."""

    time: float
    runtime_tick: int
    source_quantum_revision: int
    request: ExperimentalCorruptionRequest
    rho_before: Array
    rho_corrupted: Array
    change_norm: float
    physical_decoherence: bool = False
    authoritative_state_committed: bool = False
    provenance: str = "qmw_opt_in_experimental_pauli_corruption_v1"

    def __post_init__(self) -> None:
        if not isinstance(self.request, ExperimentalCorruptionRequest):
            raise TypeError("request must be an ExperimentalCorruptionRequest")
        if self.physical_decoherence or self.authoritative_state_committed:
            raise ValueError("experimental corruption cannot claim physical or committed status")
        object.__setattr__(self, "rho_before", _density(self.rho_before))
        object.__setattr__(self, "rho_corrupted", _density(self.rho_corrupted))


@dataclass(frozen=True)
class SyndromeOutcome:
    signs: SyndromeSigns
    probability: float
    correction_label: str | None


@dataclass(frozen=True)
class SyndromeFrame:
    """Joint stabilizer-outcome probabilities for one density operator."""

    revision: int
    time: float
    runtime_tick: int
    source_quantum_revision: int
    source_kind: str
    code_name: str
    stabilizer_labels: tuple[str, ...]
    expectations: Array
    outcomes: tuple[SyndromeOutcome, ...]
    resolved_signs: SyndromeSigns | None
    resolution_tolerance: float
    code_space_probability: float
    provenance: str = "qmw_stabilizer_syndrome_observation_v1"

    def __post_init__(self) -> None:
        if self.source_kind not in {"authoritative_quantum", "experimental_corruption_branch"}:
            raise ValueError("unknown syndrome source_kind")
        expectations = _readonly(self.expectations, dtype=float)
        if expectations.shape != (len(self.stabilizer_labels),):
            raise ValueError("expectations must match stabilizer labels")
        probability_sum = sum(outcome.probability for outcome in self.outcomes)
        if not math.isclose(probability_sum, 1.0, rel_tol=0.0, abs_tol=1.0e-9):
            raise ValueError("syndrome outcome probabilities must sum to one")
        object.__setattr__(self, "expectations", expectations)
        object.__setattr__(self, "outcomes", tuple(self.outcomes))

    @property
    def resolved(self) -> bool:
        return self.resolved_signs is not None


@dataclass(frozen=True)
class RecoveryIntervention:
    """Named instantaneous unitary correction; never a continuous derivative."""

    label: str
    pauli_label: str
    syndrome_signs: SyndromeSigns
    operator: Array
    kind: str = "unitary_recovery_intervention"
    discrete: bool = True
    continuous_derivative: bool = False
    provenance: str = "qmw_named_discrete_pauli_recovery_v1"

    def __post_init__(self) -> None:
        if not str(self.label) or not str(self.provenance):
            raise ValueError("label and provenance must be nonempty")
        if not self.discrete or self.continuous_derivative:
            raise ValueError("recovery must remain a discrete intervention")
        pauli = normalize_pauli_label(self.pauli_label)
        operator = np.asarray(self.operator, dtype=np.complex128)
        if operator.shape != pauli_matrix(pauli).shape or not np.allclose(
            operator, pauli_matrix(pauli), atol=1.0e-12, rtol=0.0
        ):
            raise ValueError("operator must equal the declared Pauli")
        object.__setattr__(self, "pauli_label", pauli)
        object.__setattr__(self, "operator", _readonly(operator))

    def as_unitary_control(self, time: float) -> UnitaryGateControl:
        """Build the existing authoritative discrete-control contract."""

        return UnitaryGateControl(
            time=float(time),
            unitary=self.operator,
            label=self.label,
            kind="unitary_recovery_intervention",
        )


@dataclass(frozen=True)
class RecoveryFrame:
    """Audited result of applying a resolved correction to a sidecar state."""

    time: float
    runtime_tick: int
    source_quantum_revision: int
    syndrome_revision: int
    intervention: RecoveryIntervention
    rho_before: Array
    rho_after: Array
    correction_applied: bool
    recovery_error_to_reference: float | None
    post_code_space_probability: float
    authoritative_state_committed: bool = False
    provenance: str = "qmw_discrete_recovery_result_v1"

    def __post_init__(self) -> None:
        if self.authoritative_state_committed:
            raise ValueError("runtime recovery result is not an authoritative engine commit")
        object.__setattr__(self, "rho_before", _density(self.rho_before))
        object.__setattr__(self, "rho_after", _density(self.rho_after))


class ErrorCorrectionEngine:
    """Evaluate one stabilizer code and queue explicit corruption requests."""

    def __init__(
        self,
        code: StabilizerCode | None = None,
        *,
        resolution_tolerance: float = 1.0e-9,
    ) -> None:
        self.code = three_qubit_bit_flip_code() if code is None else code
        if not isinstance(self.code, StabilizerCode):
            raise TypeError("code must be a StabilizerCode")
        tolerance = float(resolution_tolerance)
        if not math.isfinite(tolerance) or tolerance <= 0.0 or tolerance >= 0.5:
            raise ValueError("resolution_tolerance must lie in (0, 0.5)")
        self.resolution_tolerance = tolerance
        self._lock = RLock()
        self._pending: list[ExperimentalCorruptionRequest] = []
        self._request_sequence = 0

    @property
    def pending(self) -> tuple[ExperimentalCorruptionRequest, ...]:
        with self._lock:
            return tuple(self._pending)

    def schedule_pauli_corruption(
        self,
        pauli_label: str,
        *,
        label: str = "experimental_pauli_corruption",
    ) -> ExperimentalCorruptionRequest:
        declared = normalize_pauli_label(pauli_label)
        if len(declared) != self.code.qubits:
            raise ValueError("corruption Pauli must match the code width")
        if set(declared) == {"I"}:
            raise ValueError("experimental corruption must be non-identity")
        correctable = set(self.code.correction_labels.values()).difference({"I" * self.code.qubits})
        if declared not in correctable:
            raise ValueError("experimental corruption must be in the code's declared correctable set")
        with self._lock:
            self._request_sequence += 1
            request = ExperimentalCorruptionRequest(
                request_id=self._request_sequence,
                pauli_label=declared,
                label=label,
            )
            self._pending.append(request)
            return request

    def apply_next_corruption(
        self,
        quantum: QuantumFrame,
        *,
        runtime_tick: int,
    ) -> ExperimentalCorruptionFrame:
        if not isinstance(quantum, QuantumFrame):
            raise TypeError("quantum must be a QuantumFrame")
        if quantum.rho.shape != (self.code.dimension, self.code.dimension):
            raise ValueError("quantum dimension must match the stabilizer code")
        with self._lock:
            if not self._pending:
                raise RuntimeError("no experimental corruption request is pending")
            request = self._pending.pop(0)
        operator = pauli_matrix(request.pauli_label)
        corrupted = operator @ quantum.rho @ operator.conj().T
        return ExperimentalCorruptionFrame(
            time=quantum.time,
            runtime_tick=int(runtime_tick),
            source_quantum_revision=quantum.frame_index,
            request=request,
            rho_before=quantum.rho,
            rho_corrupted=corrupted,
            change_norm=float(np.linalg.norm(corrupted - quantum.rho, ord="fro")),
        )

    def compute_syndrome(
        self,
        rho: object,
        *,
        revision: int,
        time: float,
        runtime_tick: int,
        source_quantum_revision: int,
        source_kind: str,
    ) -> SyndromeFrame:
        density = _density(rho)
        if density.shape != (self.code.dimension, self.code.dimension):
            raise ValueError("rho dimension must match the stabilizer code")
        expectations = np.array(
            [complex(np.trace(density @ pauli_matrix(label))).real for label in self.code.stabilizer_labels],
            dtype=float,
        )
        identity = np.eye(self.code.dimension, dtype=np.complex128)
        outcomes: list[SyndromeOutcome] = []
        for signs in sorted(self.code.correction_labels):
            projector = identity
            for sign, label in zip(signs, self.code.stabilizer_labels):
                projector = projector @ ((identity + sign * pauli_matrix(label)) * 0.5)
            raw_probability = complex(np.trace(projector @ density))
            if abs(raw_probability.imag) > 1.0e-9:
                raise ValueError("syndrome probability was unexpectedly complex")
            probability = float(np.clip(raw_probability.real, 0.0, 1.0))
            outcomes.append(
                SyndromeOutcome(
                    signs=signs,
                    probability=probability,
                    correction_label=self.code.correction_labels.get(signs),
                )
            )
        total = sum(outcome.probability for outcome in outcomes)
        if total <= _TOLERANCE:
            raise ValueError("syndrome probabilities had zero total")
        outcomes = [
            SyndromeOutcome(item.signs, item.probability / total, item.correction_label)
            for item in outcomes
        ]
        maximum = max(outcomes, key=lambda item: (item.probability, item.signs))
        resolved = (
            maximum.signs
            if maximum.probability >= 1.0 - self.resolution_tolerance
            else None
        )
        code_probability = complex(np.trace(self.code.code_projector @ density))
        return SyndromeFrame(
            revision=int(revision),
            time=float(time),
            runtime_tick=int(runtime_tick),
            source_quantum_revision=int(source_quantum_revision),
            source_kind=source_kind,
            code_name=self.code.name,
            stabilizer_labels=self.code.stabilizer_labels,
            expectations=expectations,
            outcomes=tuple(outcomes),
            resolved_signs=resolved,
            resolution_tolerance=self.resolution_tolerance,
            code_space_probability=float(np.clip(code_probability.real, 0.0, 1.0)),
        )

    def recover(
        self,
        rho: object,
        syndrome: SyndromeFrame,
        *,
        reference_rho: object | None = None,
    ) -> RecoveryFrame:
        if not isinstance(syndrome, SyndromeFrame):
            raise TypeError("syndrome must be a SyndromeFrame")
        if not syndrome.resolved or syndrome.resolved_signs is None:
            raise ValueError("refusing recovery because the syndrome is unresolved")
        density = _density(rho)
        label = self.code.correction_labels.get(syndrome.resolved_signs)
        if label is None:
            raise ValueError("resolved syndrome has no declared correction")
        operator = pauli_matrix(label)
        recovered = operator @ density @ operator.conj().T
        identity_label = "I" * self.code.qubits
        intervention = RecoveryIntervention(
            label=f"recover_{self.code.name}_{''.join('p' if sign > 0 else 'm' for sign in syndrome.resolved_signs)}",
            pauli_label=label,
            syndrome_signs=syndrome.resolved_signs,
            operator=operator,
        )
        post_probability = complex(np.trace(self.code.code_projector @ recovered))
        error = None
        if reference_rho is not None:
            reference = _density(reference_rho)
            if reference.shape != recovered.shape:
                raise ValueError("reference rho must match the recovered state")
            error = float(np.linalg.norm(recovered - reference, ord="fro"))
        return RecoveryFrame(
            time=syndrome.time,
            runtime_tick=syndrome.runtime_tick,
            source_quantum_revision=syndrome.source_quantum_revision,
            syndrome_revision=syndrome.revision,
            intervention=intervention,
            rho_before=density,
            rho_after=recovered,
            correction_applied=label != identity_label,
            recovery_error_to_reference=error,
            post_code_space_probability=float(np.clip(post_probability.real, 0.0, 1.0)),
        )


__all__ = [
    "ErrorCorrectionEngine",
    "ExperimentalCorruptionFrame",
    "ExperimentalCorruptionRequest",
    "RecoveryFrame",
    "RecoveryIntervention",
    "StabilizerCode",
    "SyndromeFrame",
    "SyndromeOutcome",
    "three_qubit_bit_flip_code",
]
