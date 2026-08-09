"""Kraus-outcome quantum trajectories coupled to a discrete configuration.

The selected conditional density matrices average to the original CPTP
channel.  For the local dephasing, damping, and depolarizing Kraus families
used by the four-qubit engine, the same sampled branch gives an equivariant
configuration update through ``|K_k[m, n]|^2``.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Sequence

import numpy as np


I2 = np.eye(2, dtype=np.complex128)
X = np.array([[0.0, 1.0], [1.0, 0.0]], dtype=np.complex128)
Y = np.array([[0.0, -1j], [1j, 0.0]], dtype=np.complex128)
Z = np.array([[1.0, 0.0], [0.0, -1.0]], dtype=np.complex128)


def dephasing_kraus(amount: float) -> tuple[np.ndarray, ...]:
    probability = float(np.clip(amount, 0.0, 1.0))
    return (
        np.sqrt(1.0 - probability) * I2,
        np.sqrt(probability) * Z,
    )


def amplitude_damping_kraus(gamma: float) -> tuple[np.ndarray, ...]:
    probability = float(np.clip(gamma, 0.0, 1.0))
    return (
        np.array(
            [[1.0, 0.0], [0.0, np.sqrt(1.0 - probability)]],
            dtype=np.complex128,
        ),
        np.array(
            [[0.0, np.sqrt(probability)], [0.0, 0.0]],
            dtype=np.complex128,
        ),
    )


def depolarizing_kraus(probability: float) -> tuple[np.ndarray, ...]:
    amount = float(np.clip(probability, 0.0, 1.0))
    scale = np.sqrt(amount / 3.0)
    return (
        np.sqrt(1.0 - amount) * I2,
        scale * X,
        scale * Y,
        scale * Z,
    )


def _local_operator(operator: np.ndarray, qubit: int, n_qubits: int) -> np.ndarray:
    if not 0 <= qubit < n_qubits:
        raise ValueError("qubit lies outside the register")
    result = np.array([[1.0 + 0.0j]])
    for index in range(n_qubits):
        result = np.kron(result, operator if index == qubit else I2)
    return result


def _normalize_density(rho: np.ndarray) -> np.ndarray:
    state = np.asarray(rho, dtype=np.complex128)
    state = 0.5 * (state + state.conj().T)
    trace = float(np.trace(state).real)
    if trace <= 0.0:
        raise ValueError("conditional state has non-positive trace")
    return state / trace


@dataclass(frozen=True)
class EnvironmentalTrajectoryEvent:
    event_id: int
    logical_time: float
    channel: str
    qubit: int
    outcome: int
    outcome_probability: float
    configuration_probability: float
    configuration_before: int
    configuration_after: int
    jumped: bool
    state_changed: bool
    rho_before: np.ndarray
    rho_after: np.ndarray
    delta_rho: np.ndarray

    def to_record(self, include_matrices: bool = False) -> dict:
        record = asdict(self)
        for key in ("rho_before", "rho_after", "delta_rho"):
            matrix = record.pop(key)
            if include_matrices:
                record[key] = {
                    "real": np.asarray(matrix).real.tolist(),
                    "imag": np.asarray(matrix).imag.tolist(),
                }
        record["family"] = "environmental_jump"
        return record


class OpenSystemTrajectoryInstrument:
    def __init__(self, seed: int = 37, n_qubits: int = 4) -> None:
        self.seed = int(seed)
        self.n_qubits = int(n_qubits)
        self.dimension = 2 ** self.n_qubits
        self.rng = np.random.default_rng(self.seed)
        self.event_count = 0

    def apply_local(
        self,
        rho: np.ndarray,
        kraus_operators: Sequence[np.ndarray],
        *,
        channel: str,
        qubit: int,
        configuration: int,
        logical_time: float,
    ) -> EnvironmentalTrajectoryEvent:
        state = _normalize_density(rho)
        if state.shape != (self.dimension, self.dimension):
            raise ValueError("rho dimension does not match trajectory register")
        source = int(configuration)
        if not 0 <= source < self.dimension:
            raise ValueError("configuration lies outside rho")
        full = tuple(
            _local_operator(np.asarray(operator, dtype=np.complex128), qubit, self.n_qubits)
            for operator in kraus_operators
        )
        completeness = sum(operator.conj().T @ operator for operator in full)
        if not np.allclose(completeness, np.eye(self.dimension), atol=1e-10):
            raise ValueError("Kraus operators are not trace preserving")

        # Joint branch/destination law conditioned on the actual source.  The
        # local engine Kraus operators are diagonal or monomial, so this law is
        # equivariant with each selected conditional density matrix.
        weights = np.stack(
            [np.abs(operator[:, source]) ** 2 for operator in full],
            axis=0,
        )
        total = float(np.sum(weights))
        if total <= 0.0:
            raise ValueError("configuration has no Kraus continuation")
        flat = (weights / total).reshape(-1)
        selected = int(self.rng.choice(flat.size, p=flat))
        outcome, destination = np.unravel_index(selected, weights.shape)

        probabilities = np.asarray(
            [float(np.trace(operator @ state @ operator.conj().T).real) for operator in full]
        )
        probabilities = np.maximum(probabilities, 0.0)
        probabilities /= max(float(np.sum(probabilities)), 1e-15)
        probability = float(probabilities[outcome])
        if probability <= 1e-15:
            raise RuntimeError("configuration selected a zero-Born-probability branch")
        numerator = full[outcome] @ state @ full[outcome].conj().T
        state_after = _normalize_density(numerator / probability)
        delta = state_after - state

        self.event_count += 1
        return EnvironmentalTrajectoryEvent(
            event_id=self.event_count,
            logical_time=float(logical_time),
            channel=str(channel),
            qubit=int(qubit),
            outcome=int(outcome),
            outcome_probability=probability,
            configuration_probability=float(np.sum(weights[outcome]) / total),
            configuration_before=source,
            configuration_after=int(destination),
            jumped=int(outcome) != 0,
            state_changed=not np.allclose(state_after, state, atol=1e-14),
            rho_before=state.copy(),
            rho_after=state_after.copy(),
            delta_rho=delta.copy(),
        )

