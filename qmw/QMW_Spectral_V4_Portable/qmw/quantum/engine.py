"""State-owning, synchronized runtime for authoritative quantum frames.

The engine deliberately owns the only mutable copy of ``rho``.  An accepted
step follows one transaction:

``integrate -> validate -> derive -> seal QuantumFrame -> publish``.

Publishers receive an already immutable frame and never receive a reference to
the engine's mutable state.  This is an in-process seam; OSC schemas and sound
adapters remain downstream responsibilities.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from threading import RLock
from typing import Iterable, Protocol

import numpy as np

from .dynamics import (
    Array,
    Hamiltonian,
    LindbladChannel,
    QuantumFrame,
    _density_matrix,
    _readonly,
)
from .control import ControlTransition, RuntimeControl


_EPS = 1.0e-10


class QuantumFramePublisher(Protocol):
    """A downstream recipient of complete, sealed quantum-frame revisions."""

    def publish(self, frame: QuantumFrame) -> object:
        """Publish one immutable frame transaction."""


def _positive_square_root(matrix: Array) -> Array:
    """Return the principal square root of a Hermitian PSD matrix."""

    eigenvalues, eigenvectors = np.linalg.eigh((matrix + matrix.conj().T) * 0.5)
    if float(np.min(eigenvalues)) < -_EPS:
        raise ValueError("Kraus completion became non-positive.")
    return (eigenvectors * np.sqrt(np.clip(eigenvalues, 0.0, None))) @ eigenvectors.conj().T


def _dissipation_rate_operator(channels: tuple[LindbladChannel, ...], dimension: int) -> Array:
    result = np.zeros((dimension, dimension), dtype=np.complex128)
    for channel in channels:
        if channel.operator.shape != result.shape:
            raise ValueError("every Lindblad operator must match the Hamiltonian dimension.")
        result += channel.rate * (channel.operator.conj().T @ channel.operator)
    return (result + result.conj().T) * 0.5


def _kraus_dissipative_step(
    rho: Array,
    channels: tuple[LindbladChannel, ...],
    duration: float,
    rate_operator: Array,
) -> Array:
    """One finite, trace-preserving completely-positive dissipative step."""

    if not channels:
        return np.array(rho, copy=True)
    dimension = rho.shape[0]
    completion = np.eye(dimension, dtype=np.complex128) - (duration * rate_operator)
    no_jump = _positive_square_root(completion)
    result = no_jump @ rho @ no_jump.conj().T
    for channel in channels:
        jump = math.sqrt(duration * channel.rate) * channel.operator
        result += jump @ rho @ jump.conj().T
    return (result + result.conj().T) * 0.5


def evolve_lindblad_cptp(
    rho: object,
    hamiltonian: Hamiltonian,
    channels: Iterable[LindbladChannel],
    duration: float,
    *,
    maximum_dissipative_probability: float = 0.05,
) -> Array:
    """Advance fixed ``H`` and GKSL channels with a completely-positive step.

    The coherent component is exact.  The dissipative component uses a
    finite Kraus map and is substepped so that its no-jump completion remains
    positive.  This avoids a density-matrix Euler step, which can violate
    positivity even when the continuous GKSL equation is physical.
    """

    state = _density_matrix(rho)
    if state.shape != hamiltonian.matrix.shape:
        raise ValueError("rho and hamiltonian must share a shape.")
    elapsed = float(duration)
    if not math.isfinite(elapsed) or elapsed < 0.0:
        raise ValueError("duration must be finite and nonnegative.")
    declared_channels = tuple(channels)
    if any(not isinstance(channel, LindbladChannel) for channel in declared_channels):
        raise TypeError("channels must contain LindbladChannel values.")
    probability_cap = float(maximum_dissipative_probability)
    if not math.isfinite(probability_cap) or not 0.0 < probability_cap <= 1.0:
        raise ValueError("maximum_dissipative_probability must lie in (0, 1].")
    if elapsed == 0.0 or not declared_channels:
        return hamiltonian.evolve_unitary(state, elapsed)

    rate_operator = _dissipation_rate_operator(declared_channels, hamiltonian.dimension)
    maximum_rate = max(0.0, float(np.max(np.linalg.eigvalsh(rate_operator))))
    substeps = max(1, int(math.ceil(elapsed * maximum_rate / probability_cap)))
    dt = elapsed / substeps
    # Strang splitting keeps each component physical: exact unitary half steps
    # surround a completely-positive, trace-preserving dissipative map.
    result = np.array(state, copy=True)
    for _ in range(substeps):
        result = hamiltonian.evolve_unitary(result, dt * 0.5)
        result = _kraus_dissipative_step(result, declared_channels, dt, rate_operator)
        result = hamiltonian.evolve_unitary(result, dt * 0.5)
    return _readonly(_density_matrix(result))


@dataclass(frozen=True)
class QuantumEngineState:
    """Read-only runtime bookkeeping paired with the latest sealed frame."""

    time: float
    revision: int
    frame: QuantumFrame
    last_controls: tuple["AppliedControl", ...] = ()


@dataclass(frozen=True)
class AppliedControl:
    """One committed scheduled intervention, recorded with its frame revision."""

    revision: int
    time: float
    sequence: int
    kind: str
    label: str
    measurement_probability: float | None = None


class QuantumFrameEngine:
    """Own one density operator and publish only complete derived snapshots."""

    def __init__(
        self,
        hamiltonian: Hamiltonian | object,
        rho: object,
        *,
        channels: Iterable[LindbladChannel] = (),
        time: float = 0.0,
        revision: int = 0,
        maximum_dissipative_probability: float = 0.05,
        publishers: Iterable[QuantumFramePublisher] = (),
    ) -> None:
        self._lock = RLock()
        self._hamiltonian = hamiltonian if isinstance(hamiltonian, Hamiltonian) else Hamiltonian(hamiltonian)
        self._rho = _readonly(_density_matrix(rho))
        if self._rho.shape != self._hamiltonian.matrix.shape:
            raise ValueError("rho and hamiltonian must share a shape.")
        self._channels = tuple(channels)
        if any(not isinstance(channel, LindbladChannel) for channel in self._channels):
            raise TypeError("channels must contain LindbladChannel values.")
        _dissipation_rate_operator(self._channels, self._hamiltonian.dimension)
        if len({channel.label for channel in self._channels}) != len(self._channels):
            raise ValueError("Lindblad channel labels must be unique for runtime control.")
        if not math.isfinite(float(time)):
            raise ValueError("time must be finite.")
        if int(revision) != revision or revision < 0:
            raise ValueError("revision must be a nonnegative integer.")
        probability_cap = float(maximum_dissipative_probability)
        if not math.isfinite(probability_cap) or not 0.0 < probability_cap <= 1.0:
            raise ValueError("maximum_dissipative_probability must lie in (0, 1].")
        self._time = float(time)
        self._revision = int(revision)
        self._maximum_dissipative_probability = probability_cap
        self._publishers = list(publishers)
        if any(not hasattr(publisher, "publish") for publisher in self._publishers):
            raise TypeError("publishers must expose publish(frame).")
        self._frame = self._seal_current()
        self._scheduled_controls: list[tuple[float, int, RuntimeControl]] = []
        self._control_sequence = 0
        self._last_controls: tuple[AppliedControl, ...] = ()
        self._control_history: list[AppliedControl] = []

    @property
    def hamiltonian(self) -> Hamiltonian:
        return self._hamiltonian

    @property
    def channels(self) -> tuple[LindbladChannel, ...]:
        return self._channels

    @property
    def rho(self) -> Array:
        with self._lock:
            return _readonly(self._rho)

    @property
    def latest_frame(self) -> QuantumFrame:
        with self._lock:
            return self._frame

    @property
    def state(self) -> QuantumEngineState:
        with self._lock:
            return QuantumEngineState(self._time, self._revision, self._frame, self._last_controls)

    @property
    def scheduled_controls(self) -> tuple[RuntimeControl, ...]:
        with self._lock:
            return tuple(control for _, _, control in self._scheduled_controls)

    @property
    def control_history(self) -> tuple[AppliedControl, ...]:
        with self._lock:
            return tuple(self._control_history)

    def schedule(self, control: RuntimeControl) -> None:
        """Queue one future or immediate intervention in deterministic order."""

        if not hasattr(control, "apply") or not hasattr(control, "time"):
            raise TypeError("control must expose time and apply(rho, hamiltonian, channels).")
        at = float(control.time)
        if not math.isfinite(at):
            raise ValueError("control time must be finite.")
        with self._lock:
            if at < self._time - _EPS:
                raise ValueError("cannot schedule a control in the engine past.")
            self._control_sequence += 1
            self._scheduled_controls.append((max(at, self._time), self._control_sequence, control))
            self._scheduled_controls.sort(key=lambda item: (item[0], item[1]))

    def add_publisher(self, publisher: QuantumFramePublisher) -> None:
        if not hasattr(publisher, "publish"):
            raise TypeError("publisher must expose publish(frame).")
        with self._lock:
            self._publishers.append(publisher)

    def _seal_current(self) -> QuantumFrame:
        """Validate and derive one immutable frame from the current state only."""

        self._rho = _readonly(_density_matrix(self._rho))
        return QuantumFrame.observe(
            time=self._time,
            frame_index=self._revision,
            hamiltonian=self._hamiltonian,
            rho=self._rho,
            channels=self._channels,
        )

    def publish_current(self) -> QuantumFrame:
        """Publish the latest already-sealed frame without advancing the state."""

        with self._lock:
            self._publish(self._frame)
            return self._frame

    def _publish(self, frame: QuantumFrame) -> None:
        for publisher in tuple(self._publishers):
            publisher.publish(frame)

    def step(self, duration: float, *, publish: bool = True) -> QuantumFrame:
        """Advance, validate, seal, then optionally publish one frame revision."""

        elapsed = float(duration)
        if not math.isfinite(elapsed) or elapsed <= 0.0:
            raise ValueError("duration must be finite and positive.")
        with self._lock:
            target_time = self._time + elapsed
            due = tuple(item for item in self._scheduled_controls if item[0] <= target_time + _EPS)
            remaining = [item for item in self._scheduled_controls if item[0] > target_time + _EPS]
            candidate = self._rho
            candidate_hamiltonian = self._hamiltonian
            candidate_channels = self._channels
            cursor = self._time
            applied: list[AppliedControl] = []
            for event_time, sequence, control in due:
                segment = max(0.0, event_time - cursor)
                if segment > 0.0:
                    candidate = evolve_lindblad_cptp(
                        candidate, candidate_hamiltonian, candidate_channels, segment,
                        maximum_dissipative_probability=self._maximum_dissipative_probability,
                    )
                transition: ControlTransition = control.apply(
                    candidate, candidate_hamiltonian, candidate_channels,
                )
                candidate = _readonly(_density_matrix(transition.rho))
                candidate_hamiltonian = transition.hamiltonian
                candidate_channels = tuple(transition.channels)
                _dissipation_rate_operator(candidate_channels, candidate_hamiltonian.dimension)
                if len({channel.label for channel in candidate_channels}) != len(candidate_channels):
                    raise ValueError("Lindblad channel labels must remain unique for runtime control.")
                applied.append(AppliedControl(
                    revision=self._revision + 1,
                    time=event_time,
                    sequence=sequence,
                    kind=str(control.kind),
                    label=str(control.label),
                    measurement_probability=transition.measurement_probability,
                ))
                cursor = event_time
            final_segment = max(0.0, target_time - cursor)
            if final_segment > 0.0:
                candidate = evolve_lindblad_cptp(
                    candidate, candidate_hamiltonian, candidate_channels, final_segment,
                    maximum_dissipative_probability=self._maximum_dissipative_probability,
                )
            # Commit only after physical-state validation and full frame
            # derivation have both succeeded.
            next_time = target_time
            next_revision = self._revision + 1
            candidate_frame = QuantumFrame.observe(
                time=next_time,
                frame_index=next_revision,
                hamiltonian=candidate_hamiltonian,
                rho=candidate,
                channels=candidate_channels,
            )
            self._rho = candidate
            self._hamiltonian = candidate_hamiltonian
            self._channels = candidate_channels
            self._time = next_time
            self._revision = next_revision
            self._frame = candidate_frame
            self._scheduled_controls = remaining
            self._last_controls = tuple(applied)
            self._control_history.extend(applied)
            if publish:
                self._publish(candidate_frame)
            return candidate_frame


__all__ = [
    "AppliedControl", "QuantumEngineState", "QuantumFrameEngine", "QuantumFramePublisher",
    "evolve_lindblad_cptp",
]
