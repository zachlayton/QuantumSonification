from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol

import numpy as np

from qmw.core.measurement_event import (
    BitArray,
    ClassicalRegister,
    MeasurementStats,
    ShotBitArray,
)

DEFAULT_QMW_REGISTERS = (
    "pitch",
    "energy",
    "spin",
    "parity",
    "ancilla",
    "hamiltonian",
    "notation",
)


@dataclass
class EstimatorRequest:
    """Primitive 1: circuit + observable -> expectation value.

    This mirrors Qiskit's Estimator shape without depending on Qiskit. The
    circuit can be a ComposerCircuit, Qiskit circuit, QASM string, or any local
    circuit representation accepted by the chosen backend adapter.
    """

    circuit: Any
    observable: Any
    observable_name: str | None = None
    parameters: dict[str, float] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class EstimatorResult:
    expectation_value: float
    variance: float | None = None
    observable_name: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class EstimatorBatchRequest:
    """Multiple observable expectations for the same circuit.

    Typical QMW observables:
        X, Y, Z, XX, ZZZZ
    """

    circuit: Any
    observables: dict[str, Any]
    parameters: dict[str, float] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class EstimatorBatchResult:
    values: dict[str, EstimatorResult]
    metadata: dict[str, Any] = field(default_factory=dict)

    def expectation(self, name: str) -> float:
        return self.values[name].expectation_value


@dataclass
class SamplerRequest:
    """Primitive 2: circuit -> BitArray/count statistics."""

    circuit: Any
    shots: int = 1024
    registers: tuple[str, ...] = DEFAULT_QMW_REGISTERS
    parameters: dict[str, float] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class SamplerResult:
    stats: MeasurementStats
    registers: dict[str, ClassicalRegister] = field(default_factory=dict)
    register_shots: dict[str, ShotBitArray] = field(default_factory=dict)
    bit_arrays: list[BitArray] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __getattr__(self, name: str) -> ClassicalRegister | ShotBitArray:
        if name in self.register_shots:
            return self.register_shots[name]
        if name in self.registers:
            return self.registers[name]

        alias = legacy_measurement_register_alias(name)
        if alias in self.register_shots:
            return self.register_shots[alias]
        if alias in self.registers:
            return self.registers[alias]

        raise AttributeError(name)

    @property
    def meas(self) -> BitArray | ShotBitArray | None:
        shot_register = self.register_shots.get("meas")
        if shot_register is not None:
            return shot_register

        register = self.registers.get("meas")
        if register is not None:
            return register.bit_array

        if self.bit_arrays:
            return self.bit_arrays[0]

        return None

    def register(self, name: str) -> ClassicalRegister | ShotBitArray:
        if name in self.register_shots:
            return self.register_shots[name]
        if name in self.registers:
            return self.registers[name]

        alias = legacy_measurement_register_alias(name)
        if alias in self.register_shots:
            return self.register_shots[alias]
        return self.registers[alias]


def legacy_measurement_register_alias(name: str) -> str:
    aliases = {
        "measurement_pitch": "pitch",
        "measurement_rhythm": "parity",
        "measurement_space": "spin",
        "measurement_spatial": "spin",
        "measurement_texture": "energy",
        "measurement_spectral": "energy",
        "measurement_timbre": "energy",
        "measurement_lighting": "spin",
        "measurement_control": "ancilla",
        "measurement_ancilla": "ancilla",
        "measurement_energy": "energy",
        "measurement_spin": "spin",
        "measurement_parity": "parity",
        "measurement_hamiltonian": "hamiltonian",
        "measurement_notation": "notation",
        "rhythm": "parity",
        "space": "spin",
        "spatial": "spin",
        "texture": "energy",
        "spectral": "energy",
        "timbre": "energy",
        "lighting": "spin",
        "visual": "spin",
        "control": "ancilla",
        "branch": "ancilla",
        "branching": "ancilla",
    }
    return aliases.get(name, name.removeprefix("measurement_"))


class EstimatorPrimitive(Protocol):
    def run(self, request: EstimatorRequest) -> EstimatorResult:
        ...


class SamplerPrimitive(Protocol):
    def run(self, request: SamplerRequest) -> SamplerResult:
        ...


def expectation_from_statevector(
    state: np.ndarray,
    observable: np.ndarray,
    observable_name: str | None = None,
) -> EstimatorResult:
    """Evaluate <psi|O|psi> for a local simulator adapter."""
    value = np.vdot(state, observable @ state)
    squared = np.vdot(state, (observable @ observable) @ state)
    expectation = float(np.real_if_close(value))
    second_moment = float(np.real_if_close(squared))
    variance = max(0.0, second_moment - expectation * expectation)
    return EstimatorResult(
        expectation_value=expectation,
        variance=variance,
        observable_name=observable_name,
    )


def batch_expectation_from_statevector(
    state: np.ndarray,
    observables: dict[str, np.ndarray],
) -> EstimatorBatchResult:
    return EstimatorBatchResult(
        values={
            name: expectation_from_statevector(
                state,
                observable,
                observable_name=name,
            )
            for name, observable in observables.items()
        }
    )
