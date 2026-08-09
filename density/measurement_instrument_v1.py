"""Authoritative four-qubit projective measurement instrument.

The instrument samples both non-mutating probes and state-changing explicit
measurements.  It contains no OSC or visualization behavior; the density
engine owns the state and installs ``rho_after`` only for collapse mode.
"""

from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np


I2 = np.eye(2, dtype=np.complex128)
H = np.array([[1.0, 1.0], [1.0, -1.0]], dtype=np.complex128) / math.sqrt(2.0)
S_DAGGER = np.diag([1.0, -1j]).astype(np.complex128)


def validate_four_qubit_rho(rho: np.ndarray) -> np.ndarray:
    state = np.asarray(rho, dtype=np.complex128)
    if state.shape != (16, 16):
        raise ValueError("measurement v1 requires a 16x16 four-qubit rho")
    state = 0.5 * (state + state.conj().T)
    trace = float(np.trace(state).real)
    if trace <= 0.0:
        raise ValueError("rho must have positive trace")
    state /= trace
    values, vectors = np.linalg.eigh(state)
    values = np.maximum(values.real, 0.0)
    values /= max(float(np.sum(values)), 1e-15)
    return (vectors * values[None, :]) @ vectors.conj().T


def _kron_all(operators: list[np.ndarray]) -> np.ndarray:
    result = np.array([[1.0 + 0.0j]])
    for operator in operators:
        result = np.kron(result, operator)
    return result


def basis_unitary(basis: str) -> np.ndarray:
    """Return U such that measuring ``basis`` equals applying U then Z."""
    label = str(basis).upper()
    if label == "Z":
        single = I2
    elif label == "X":
        single = H
    elif label == "Y":
        single = H @ S_DAGGER
    else:
        raise ValueError("basis must be X, Y, or Z")
    return _kron_all([single] * 4)


def basis_probabilities(rho: np.ndarray, basis: str) -> np.ndarray:
    state = validate_four_qubit_rho(rho)
    unitary = basis_unitary(basis)
    rotated = unitary @ state @ unitary.conj().T
    probabilities = np.maximum(np.real(np.diag(rotated)), 0.0)
    return probabilities / max(float(np.sum(probabilities)), 1e-15)


def _trace_distance(rho_a: np.ndarray, rho_b: np.ndarray) -> float:
    singular_values = np.linalg.svd(rho_a - rho_b, compute_uv=False)
    return float(0.5 * np.sum(singular_values))


@dataclass(frozen=True)
class MeasurementEvent:
    event_id: int
    request_id: int
    logical_time: float
    revision_before: int
    revision_after: int
    mode: str
    basis: str
    outcome: int
    bitstring: str
    probability: float
    trace_distance: float
    rho_before: np.ndarray
    rho_after: np.ndarray
    delta_rho: np.ndarray

    @property
    def changed_state(self) -> bool:
        return self.mode == "collapse"

    def osc_payload(self) -> list[object]:
        return [
            self.request_id,
            self.event_id,
            self.revision_before,
            self.revision_after,
            self.mode,
            self.basis,
            self.outcome,
            self.bitstring,
            self.probability,
            self.trace_distance,
            int(self.changed_state),
        ]


class ProjectiveMeasurementInstrument:
    def __init__(self, seed: int = 29) -> None:
        self.seed = int(seed)
        self.rng = np.random.default_rng(self.seed)
        self.event_count = 0

    def measure(
        self,
        rho: np.ndarray,
        *,
        basis: str,
        mode: str,
        logical_time: float,
        revision_before: int,
        request_id: int = 0,
    ) -> MeasurementEvent:
        state_before = validate_four_qubit_rho(rho)
        label = str(basis).upper()
        operation = str(mode).lower()
        if operation not in ("probe", "collapse"):
            raise ValueError("measurement mode must be probe or collapse")

        probabilities = basis_probabilities(state_before, label)
        outcome = int(self.rng.choice(16, p=probabilities))
        probability = float(probabilities[outcome])

        if operation == "collapse":
            z_ket = np.zeros(16, dtype=np.complex128)
            z_ket[outcome] = 1.0
            basis_ket = basis_unitary(label).conj().T @ z_ket
            projector = np.outer(basis_ket, basis_ket.conj())
            numerator = projector @ state_before @ projector
            state_after = validate_four_qubit_rho(
                numerator / max(probability, 1e-15)
            )
            revision_after = int(revision_before) + 1
        else:
            state_after = state_before.copy()
            revision_after = int(revision_before)

        self.event_count += 1
        delta = state_after - state_before
        return MeasurementEvent(
            event_id=self.event_count,
            request_id=int(request_id),
            logical_time=float(logical_time),
            revision_before=int(revision_before),
            revision_after=revision_after,
            mode=operation,
            basis=label,
            outcome=outcome,
            bitstring=format(outcome, "04b"),
            probability=probability,
            trace_distance=_trace_distance(state_before, state_after),
            rho_before=state_before.copy(),
            rho_after=state_after.copy(),
            delta_rho=delta.copy(),
        )
