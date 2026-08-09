"""Authoritative live Bohm--Bell configuration guidance for four qubits.

The density engine owns the quantum state.  This module owns one actual
computational-Z configuration and moves it only with the Bell jump law

    sigma[m, n] = max(J[m, n], 0) / rho[n, n].

Circuit gates are represented by Hermitian generators and unfolded over
microsteps.  Discontinuous state changes (measurement, GRW, and environmental
Kraus outcomes) are recorded as separate causes rather than being folded into
Hamiltonian current.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Mapping

import numpy as np
from scipy.linalg import schur

from .four_qubit_configuration_guidance_v1 import (
    current_matrix,
    sample_configurations,
    transition_rates,
    unitary_step,
)


class BohmEventFamily:
    RESET = "reset"
    CIRCUIT_CURRENT = "circuit_generated_current"
    HAMILTONIAN_CURRENT = "hamiltonian_current"
    ENVIRONMENTAL_JUMP = "environmental_jump"
    EXPLICIT_MEASUREMENT = "explicit_measurement"
    SPONTANEOUS_LOCALIZATION = "spontaneous_localization"


@dataclass(frozen=True)
class BohmGuidanceConfig:
    enabled: bool = True
    seed: int = 31
    beable_basis: str = "computational_z"
    gate_duration_seconds: float = 0.125
    gate_microsteps: int = 24
    hamiltonian_microsteps: int = 8
    population_floor: float = 1e-15
    environment_trajectory_enabled: bool = False
    environment_seed: int = 37

    def __post_init__(self) -> None:
        if self.beable_basis != "computational_z":
            raise ValueError("v1 supports only the computational_z beable basis")
        if self.gate_duration_seconds <= 0.0:
            raise ValueError("gate_duration_seconds must be positive")
        if self.gate_microsteps < 1 or self.hamiltonian_microsteps < 1:
            raise ValueError("guidance microstep counts must be positive")
        if self.population_floor <= 0.0:
            raise ValueError("population_floor must be positive")


@dataclass(frozen=True)
class BohmConfigurationEvent:
    event_id: int
    family: str
    logical_time: float
    configuration_before: int
    configuration_after: int
    jumped: bool
    beable_basis: str = "computational_z"
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def to_record(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class BohmGuidanceFrame:
    family: str
    logical_time: float
    source: int
    destination: int
    jumped: bool
    current: float
    total_rate: float
    jump_probability: float
    phase_gradient: float
    branch_entropy: float
    beable_basis: str = "computational_z"

    def to_record(self) -> dict[str, Any]:
        return asdict(self)


def _validate_density(rho: np.ndarray) -> np.ndarray:
    state = np.asarray(rho, dtype=np.complex128)
    if state.ndim != 2 or state.shape[0] != state.shape[1]:
        raise ValueError("rho must be square")
    state = 0.5 * (state + state.conj().T)
    trace = float(np.trace(state).real)
    if trace <= 0.0:
        raise ValueError("rho must have positive trace")
    return state / trace


def unitary_generator(unitary: np.ndarray, duration: float = 1.0) -> np.ndarray:
    """Return Hermitian G whose duration evolution equals U up to roundoff.

    A complex Schur decomposition keeps the eigenbasis unitary even for gates
    with degenerate eigenvalues.  Principal phases select a stable, shortest
    generator; global phase is harmless for density evolution and guidance.
    """
    operation = np.asarray(unitary, dtype=np.complex128)
    if operation.ndim != 2 or operation.shape[0] != operation.shape[1]:
        raise ValueError("unitary must be square")
    if duration <= 0.0:
        raise ValueError("duration must be positive")
    identity = np.eye(operation.shape[0], dtype=np.complex128)
    if not np.allclose(operation.conj().T @ operation, identity, atol=1e-10):
        raise ValueError("operation is not unitary")
    triangular, vectors = schur(operation, output="complex")
    phases = np.angle(np.diag(triangular))
    generator = (vectors * (-phases / duration)[None, :]) @ vectors.conj().T
    return 0.5 * (generator + generator.conj().T)


class LiveBohmGuidance:
    """Own one actual configuration while the engine owns canonical rho."""

    def __init__(self, config: BohmGuidanceConfig = BohmGuidanceConfig()) -> None:
        self.config = config
        self.rng = np.random.default_rng(config.seed)
        self.configuration = 0
        self.configuration_revision = 0
        self.initialized = False
        self.event_count = 0
        self.event_history: list[BohmConfigurationEvent] = []
        self.events_this_frame: list[BohmConfigurationEvent] = []
        self.last_event: BohmConfigurationEvent | None = None
        self.last_frame: BohmGuidanceFrame | None = None

    @property
    def beable_basis(self) -> str:
        return self.config.beable_basis

    def begin_frame(self) -> None:
        self.events_this_frame = []

    def _append_event(
        self,
        family: str,
        logical_time: float,
        before: int,
        after: int,
        metadata: Mapping[str, Any] | None = None,
        *,
        force_revision: bool = False,
    ) -> BohmConfigurationEvent:
        self.event_count += 1
        event = BohmConfigurationEvent(
            event_id=self.event_count,
            family=str(family),
            logical_time=float(logical_time),
            configuration_before=int(before),
            configuration_after=int(after),
            jumped=int(before) != int(after),
            beable_basis=self.beable_basis,
            metadata=dict(metadata or {}),
        )
        self.event_history.append(event)
        self.events_this_frame.append(event)
        self.last_event = event
        if force_revision or event.jumped:
            self.configuration_revision += 1
        return event

    def reset(self, rho: np.ndarray, logical_time: float = 0.0) -> BohmConfigurationEvent:
        state = _validate_density(rho)
        before = self.configuration
        self.configuration = int(sample_configurations(state, 1, self.rng)[0])
        self.initialized = True
        return self._append_event(
            BohmEventFamily.RESET,
            logical_time,
            before,
            self.configuration,
            {"dimension": state.shape[0]},
            force_revision=True,
        )

    def record_discontinuity(
        self,
        family: str,
        rho_after: np.ndarray,
        *,
        logical_time: float,
        metadata: Mapping[str, Any] | None = None,
        configuration_after: int | None = None,
        ensure_supported: bool = False,
    ) -> BohmConfigurationEvent:
        state = _validate_density(rho_after)
        if not self.initialized:
            self.reset(state, logical_time)
        before = self.configuration
        if configuration_after is not None:
            candidate = int(configuration_after)
            if not 0 <= candidate < state.shape[0]:
                raise ValueError("configuration_after lies outside rho")
            self.configuration = candidate
        elif ensure_supported:
            population = float(np.real(state[before, before]))
            if population <= self.config.population_floor:
                self.configuration = int(
                    sample_configurations(state, 1, self.rng)[0]
                )
        return self._append_event(
            family,
            logical_time,
            before,
            self.configuration,
            metadata,
        )

    def step(
        self,
        hamiltonian: np.ndarray,
        rho: np.ndarray,
        dt: float,
        *,
        family: str,
        logical_time: float,
    ) -> BohmGuidanceFrame:
        if dt < 0.0:
            raise ValueError("dt must be non-negative")
        state = _validate_density(rho)
        if not self.initialized:
            self.reset(state, logical_time)
        source = int(self.configuration)
        destination = source
        signed_current = 0.0
        total_rate = 0.0
        jump_probability = 0.0
        branch_entropy = 0.0
        phase_gradient = 0.0

        if self.config.enabled and dt > 0.0:
            rates = transition_rates(
                hamiltonian,
                state,
                population_floor=self.config.population_floor,
            )
            outgoing = rates[:, source]
            total_rate = float(np.sum(outgoing))
            if total_rate > 0.0:
                weights = outgoing / total_rate
                positive = weights > 1e-15
                branch_entropy = float(
                    -np.sum(weights[positive] * np.log2(weights[positive]))
                )
                jump_probability = float(-np.expm1(-total_rate * dt))
                if self.rng.random() < jump_probability:
                    destination = int(self.rng.choice(len(weights), p=weights))
                    currents = current_matrix(hamiltonian, state)
                    signed_current = float(currents[destination, source])
                    coherence = state[destination, source]
                    if abs(coherence) > 1e-15:
                        phase_gradient = float(np.angle(coherence) / np.pi)
                    self.configuration = destination
                    self._append_event(
                        family,
                        logical_time,
                        source,
                        destination,
                        {
                            "current": signed_current,
                            "total_rate": total_rate,
                            "jump_probability": jump_probability,
                        },
                    )

        frame = BohmGuidanceFrame(
            family=str(family),
            logical_time=float(logical_time),
            source=source,
            destination=destination,
            jumped=source != destination,
            current=signed_current,
            total_rate=total_rate,
            jump_probability=jump_probability,
            phase_gradient=phase_gradient,
            branch_entropy=branch_entropy,
            beable_basis=self.beable_basis,
        )
        self.last_frame = frame
        return frame

    def evolve_density(
        self,
        rho: np.ndarray,
        hamiltonian: np.ndarray,
        *,
        duration: float,
        microsteps: int,
        family: str,
        logical_time_start: float,
        timeline_duration: float | None = None,
    ) -> np.ndarray:
        if duration < 0.0 or microsteps < 1:
            raise ValueError("duration must be non-negative and microsteps positive")
        state = _validate_density(rho)
        if duration == 0.0:
            return state
        dt = duration / microsteps
        half_unitary = unitary_step(hamiltonian, dt / 2.0)
        timeline = duration if timeline_duration is None else float(timeline_duration)
        for index in range(microsteps):
            midpoint = half_unitary @ state @ half_unitary.conj().T
            event_time = logical_time_start + timeline * (index + 0.5) / microsteps
            self.step(
                hamiltonian,
                midpoint,
                dt,
                family=family,
                logical_time=event_time,
            )
            state = half_unitary @ midpoint @ half_unitary.conj().T
        return _validate_density(state)

    def unfold_unitary(
        self,
        rho: np.ndarray,
        unitary: np.ndarray,
        *,
        family: str = BohmEventFamily.CIRCUIT_CURRENT,
        logical_time: float = 0.0,
    ) -> tuple[np.ndarray, np.ndarray]:
        duration = self.config.gate_duration_seconds
        generator = unitary_generator(unitary, duration=duration)
        state = self.evolve_density(
            rho,
            generator,
            duration=duration,
            microsteps=self.config.gate_microsteps,
            family=family,
            logical_time_start=logical_time,
            timeline_duration=0.0,
        )
        return state, generator
