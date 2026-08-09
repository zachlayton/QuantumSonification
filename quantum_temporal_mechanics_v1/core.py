"""Finite-dimensional, operational mechanics of relational quantum time.

Coordinate time appears only in ``build_history_state`` as a convenient way
to prepare a model.  All observations made by ``QuantumTemporalMechanics``
are conditional probabilities read from the joint clock-system state.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import math
from typing import Any

import numpy as np


def density_matrix(state: np.ndarray) -> np.ndarray:
    """Return a normalized density matrix from a ket or density matrix."""
    value = np.asarray(state, dtype=np.complex128)
    if value.ndim == 1:
        norm = float(np.vdot(value, value).real)
        if norm <= 1e-15:
            raise ValueError("state vector has zero norm")
        value = np.outer(value, value.conj()) / norm
    if value.ndim != 2 or value.shape[0] != value.shape[1]:
        raise ValueError("state must be a ket or square density matrix")
    value = 0.5 * (value + value.conj().T)
    trace = np.trace(value)
    if abs(trace) <= 1e-15:
        raise ValueError("density matrix has zero trace")
    value = value / trace
    eigenvalues = np.linalg.eigvalsh(value)
    if float(eigenvalues.min()) < -1e-9:
        raise ValueError("density matrix is not positive semidefinite")
    return value


def _unitary(hamiltonian: np.ndarray, duration: float) -> np.ndarray:
    values, vectors = np.linalg.eigh(np.asarray(hamiltonian, dtype=np.complex128))
    return (vectors * np.exp(-1j * values * duration)) @ vectors.conj().T


def _von_neumann_entropy(rho: np.ndarray) -> float:
    values = np.clip(np.linalg.eigvalsh(density_matrix(rho)).real, 0.0, 1.0)
    nonzero = values[values > 1e-15]
    return float(-np.sum(nonzero * np.log2(nonzero)))


def _fidelity(rho: np.ndarray, sigma: np.ndarray) -> float:
    """Uhlmann fidelity, including its conventional outer square."""
    rho = density_matrix(rho)
    sigma = density_matrix(sigma)
    values, vectors = np.linalg.eigh(rho)
    root = (vectors * np.sqrt(np.clip(values, 0.0, None))) @ vectors.conj().T
    middle = 0.5 * (root @ sigma @ root + (root @ sigma @ root).conj().T)
    return float(np.clip(np.sum(np.sqrt(np.clip(np.linalg.eigvalsh(middle), 0.0, None))) ** 2, 0.0, 1.0))


@dataclass(frozen=True)
class ClockReading:
    tick: int
    phase: float
    coordinate: float
    probability: float
    conditional_state: np.ndarray


@dataclass(frozen=True)
class EventTimeEstimate:
    label: str
    probability: float
    tick_distribution: tuple[float, ...]
    mean_phase: float
    concentration: float
    entropy_bits: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class DurationEstimate:
    first: str
    second: str
    forward_ticks: int
    duration: float
    lag_distribution: tuple[float, ...]
    confidence: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class TemporalDiagnostics:
    transition_fidelities: tuple[float, ...]
    mean_transition_fidelity: float
    closure_fidelity: float
    clock_entropy_bits: float
    clock_effect_completeness_error: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class FiniteQuantumClock:
    """A periodic clock represented by a covariant discrete phase POVM.

    With ``dimension`` equally spaced readings, the phase states form an
    orthonormal Fourier basis.  The clock is necessarily periodic; it cannot
    count cycles without an additional memory register.
    """

    def __init__(self, dimension: int, period: float = math.tau) -> None:
        if dimension < 2:
            raise ValueError("clock dimension must be at least two")
        if period <= 0:
            raise ValueError("clock period must be positive")
        self.dimension = int(dimension)
        self.period = float(period)

    @property
    def resolution(self) -> float:
        return self.period / self.dimension

    def phase(self, tick: int) -> float:
        return math.tau * (tick % self.dimension) / self.dimension

    def coordinate(self, tick: int) -> float:
        return self.period * (tick % self.dimension) / self.dimension

    def ket(self, tick: int) -> np.ndarray:
        n = np.arange(self.dimension)
        return np.exp(-1j * n * self.phase(tick)) / math.sqrt(self.dimension)

    def effect(self, tick: int) -> np.ndarray:
        ket = self.ket(tick)
        return np.outer(ket, ket.conj())

    def translation(self, ticks: int) -> np.ndarray:
        """Clock-frame translation in the clock energy basis."""
        n = np.arange(self.dimension)
        return np.diag(np.exp(-1j * n * self.phase(ticks)))


def build_history_state(
    clock: FiniteQuantumClock,
    initial_system_state: np.ndarray,
    system_hamiltonian: np.ndarray,
) -> np.ndarray:
    """Prepare |History> = sum_k |tau_k> U(tau_k)|psi_0>/sqrt(d).

    This preparation helper uses a coordinate parameter.  Once the joint
    state is built, relational observations do not consult that parameter.
    """
    initial = np.asarray(initial_system_state, dtype=np.complex128)
    if initial.ndim != 1:
        raise ValueError("history builder currently requires a pure initial ket")
    initial = initial / np.linalg.norm(initial)
    hamiltonian = np.asarray(system_hamiltonian, dtype=np.complex128)
    if hamiltonian.shape != (len(initial), len(initial)):
        raise ValueError("Hamiltonian and system-state dimensions disagree")
    history = np.zeros(clock.dimension * len(initial), dtype=np.complex128)
    for tick in range(clock.dimension):
        system = _unitary(hamiltonian, clock.coordinate(tick)) @ initial
        history += np.kron(clock.ket(tick), system) / math.sqrt(clock.dimension)
    return density_matrix(history)


class QuantumTemporalMechanics:
    """Ask clock-neutral relational questions of a clock-system state."""

    def __init__(self, clock: FiniteQuantumClock, joint_state: np.ndarray) -> None:
        self.clock = clock
        self.joint_state = density_matrix(joint_state)
        if self.joint_state.shape[0] % clock.dimension:
            raise ValueError("joint dimension is not divisible by clock dimension")
        self.system_dimension = self.joint_state.shape[0] // clock.dimension
        self._tensor = self.joint_state.reshape(
            clock.dimension,
            self.system_dimension,
            clock.dimension,
            self.system_dimension,
        )

    def reading(self, tick: int) -> ClockReading:
        ket = self.clock.ket(tick)
        unnormalized = np.einsum("a,aibj,b->ij", ket.conj(), self._tensor, ket, optimize=True)
        probability = float(max(0.0, np.trace(unnormalized).real))
        if probability <= 1e-15:
            raise ValueError(f"clock reading {tick} has zero probability")
        return ClockReading(
            tick=tick % self.clock.dimension,
            phase=self.clock.phase(tick),
            coordinate=self.clock.coordinate(tick),
            probability=probability,
            conditional_state=density_matrix(unnormalized / probability),
        )

    def readings(self) -> tuple[ClockReading, ...]:
        return tuple(self.reading(tick) for tick in range(self.clock.dimension))

    def event_time(self, effect: np.ndarray, label: str = "event") -> EventTimeEstimate:
        """Infer P(clock tick | event) using the joint Born rule."""
        effect = np.asarray(effect, dtype=np.complex128)
        if effect.shape != (self.system_dimension, self.system_dimension):
            raise ValueError("event effect has the wrong system dimension")
        eigenvalues = np.linalg.eigvalsh(0.5 * (effect + effect.conj().T)).real
        if eigenvalues.min() < -1e-9 or eigenvalues.max() > 1.0 + 1e-9:
            raise ValueError("event effect must satisfy 0 <= effect <= I")
        joint = []
        for reading in self.readings():
            likelihood = float(max(0.0, np.trace(effect @ reading.conditional_state).real))
            joint.append(reading.probability * likelihood)
        event_probability = float(sum(joint))
        if event_probability <= 1e-15:
            raise ValueError("event has zero probability")
        distribution = np.asarray(joint, dtype=float) / event_probability
        phasor = np.sum(distribution * np.exp(1j * math.tau * np.arange(self.clock.dimension) / self.clock.dimension))
        entropy = float(-np.sum(distribution[distribution > 0] * np.log2(distribution[distribution > 0])))
        return EventTimeEstimate(
            label=label,
            probability=event_probability,
            tick_distribution=tuple(float(x) for x in distribution),
            mean_phase=float(np.angle(phasor) % math.tau),
            concentration=float(abs(phasor)),
            entropy_bits=entropy,
        )

    def duration(self, first: EventTimeEstimate, second: EventTimeEstimate) -> DurationEstimate:
        """Return the cyclic relative-lag likelihood between two event records.

        This is an operational cross-correlation of event-time distributions,
        not a claim that two incompatible measurements possess joint values.
        """
        a = np.asarray(first.tick_distribution)
        b = np.asarray(second.tick_distribution)
        if len(a) != self.clock.dimension or len(b) != self.clock.dimension:
            raise ValueError("event estimates belong to a different clock")
        lag = np.array([sum(a[k] * b[(k + delta) % len(a)] for k in range(len(a))) for delta in range(len(a))])
        lag /= lag.sum()
        peak = int(np.argmax(lag))
        ordered = np.sort(lag)
        confidence = float(ordered[-1] - ordered[-2]) if len(ordered) > 1 else 1.0
        return DurationEstimate(
            first=first.label,
            second=second.label,
            forward_ticks=peak,
            duration=peak * self.clock.resolution,
            lag_distribution=tuple(float(x) for x in lag),
            confidence=confidence,
        )

    def diagnostics(self, system_hamiltonian: np.ndarray) -> TemporalDiagnostics:
        """Measure local dynamical consistency and finite-clock closure."""
        hamiltonian = np.asarray(system_hamiltonian, dtype=np.complex128)
        if hamiltonian.shape != (self.system_dimension, self.system_dimension):
            raise ValueError("Hamiltonian has the wrong system dimension")
        readings = self.readings()
        step = _unitary(hamiltonian, self.clock.resolution)
        fidelities = []
        for left, right in zip(readings[:-1], readings[1:]):
            predicted = step @ left.conditional_state @ step.conj().T
            fidelities.append(_fidelity(predicted, right.conditional_state))
        predicted_closure = step @ readings[-1].conditional_state @ step.conj().T
        closure = _fidelity(predicted_closure, readings[0].conditional_state)
        probabilities = np.array([r.probability for r in readings])
        probabilities /= probabilities.sum()
        clock_entropy = float(-np.sum(probabilities[probabilities > 0] * np.log2(probabilities[probabilities > 0])))
        completeness = sum((self.clock.effect(k) for k in range(self.clock.dimension)), np.zeros((self.clock.dimension, self.clock.dimension), dtype=np.complex128))
        return TemporalDiagnostics(
            transition_fidelities=tuple(float(x) for x in fidelities),
            mean_transition_fidelity=float(np.mean(fidelities)) if fidelities else 1.0,
            closure_fidelity=closure,
            clock_entropy_bits=clock_entropy,
            clock_effect_completeness_error=float(np.linalg.norm(completeness - np.eye(self.clock.dimension))),
        )

    def translated_frame(self, ticks: int) -> "QuantumTemporalMechanics":
        """Describe the same joint state after a clock-origin gauge shift."""
        translation = self.clock.translation(ticks)
        transform = np.kron(translation, np.eye(self.system_dimension))
        shifted = transform @ self.joint_state @ transform.conj().T
        return QuantumTemporalMechanics(self.clock, shifted)
