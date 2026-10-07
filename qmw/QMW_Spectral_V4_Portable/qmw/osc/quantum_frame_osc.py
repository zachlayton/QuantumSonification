"""Bounded, revision-aware OSC publication for sealed quantum frames.

This adapter has no packet queue.  A frame is either sent immediately as one
ordered transaction or dropped before any message is emitted.  Consequently a
slow receiver never receives an accumulating backlog of obsolete state
snapshots.  The authoritative density matrix and Hamiltonian stay in-process.
"""

from __future__ import annotations

import math
from time import monotonic
from typing import Any, Callable, Iterable

import numpy as np

from qmw.quantum.dynamics import Hamiltonian, QuantumFrame, conserved_pauli_labels
from qmw.quantum.temporal import BuresClockReading, BuresFrameClock


QMW_QUANTUM_FRAME_OSC_ROOT = "/qmw/quantum/v1"
QMW_QUANTUM_FRAME_OSC_SCHEMA = "qmw.quantum_frame.osc.v1"
QMW_QUANTUM_FRAME_OSC_PORT = 17875


class QuantumFrameOSCPublisher:
    """Send compact observables from immutable :class:`QuantumFrame` values.

    Frames must have strictly increasing revisions.  The optional rate gate
    drops too-soon frames rather than buffering them, so the next accepted
    publication is always current at send time.
    """

    def __init__(
        self,
        clients: Iterable[object] = (),
        *,
        pauli_limit: int = 16,
        population_limit: int = 16,
        current_limit: int = 16,
        minimum_interval_seconds: float = 1.0 / 60.0,
        monotonic_clock: Callable[[], float] = monotonic,
        temporal_clock: BuresFrameClock | None = None,
    ) -> None:
        for name, value in (
            ("pauli_limit", pauli_limit),
            ("population_limit", population_limit),
            ("current_limit", current_limit),
        ):
            if int(value) != value or value < 1:
                raise ValueError(f"{name} must be a positive integer.")
        interval = float(minimum_interval_seconds)
        if not math.isfinite(interval) or interval < 0.0:
            raise ValueError("minimum_interval_seconds must be finite and nonnegative.")
        if not callable(monotonic_clock):
            raise ValueError("monotonic_clock must be callable.")
        self.clients = tuple(client for client in clients if client is not None)
        if any(not hasattr(client, "send_message") for client in self.clients):
            raise ValueError("OSC clients must expose send_message(address, payload).")
        self.pauli_limit = int(pauli_limit)
        self.population_limit = int(population_limit)
        self.current_limit = int(current_limit)
        self.minimum_interval_seconds = interval
        self._clock = monotonic_clock
        if temporal_clock is not None and not isinstance(temporal_clock, BuresFrameClock):
            raise TypeError("temporal_clock must be a BuresFrameClock or None.")
        self.temporal_clock = temporal_clock
        self._last_published_revision = -1
        self._last_published_at: float | None = None
        self._conserved_cache: list[tuple[Hamiltonian, frozenset[str]]] = []
        self.dropped_stale_frames = 0
        self.dropped_rate_frames = 0

    @classmethod
    def from_udp(
        cls,
        host: str = "127.0.0.1",
        port: int = QMW_QUANTUM_FRAME_OSC_PORT,
        **kwargs: Any,
    ) -> "QuantumFrameOSCPublisher":
        """Create the publisher's sole UDP client only when live transport is wanted."""

        from pythonosc.udp_client import SimpleUDPClient

        return cls((SimpleUDPClient(host, int(port)),), **kwargs)

    @property
    def last_published_revision(self) -> int:
        return self._last_published_revision

    def reset_revision_gate(self) -> None:
        """Allow a newly launched receiver to accept a fresh revision sequence."""

        self._last_published_revision = -1
        self._last_published_at = None

    def _pauli_indices(self, frame: QuantumFrame) -> np.ndarray:
        velocity = np.abs(frame.pauli.velocity)
        # Stable lexical tie-breaking makes equal-zero lanes deterministic.
        ordered = sorted(range(len(frame.pauli.labels)), key=lambda index: (-velocity[index], frame.pauli.labels[index]))
        return np.asarray(ordered[: self.pauli_limit], dtype=int)

    def _population_indices(self, frame: QuantumFrame) -> np.ndarray:
        ordered = sorted(range(frame.populations.size), key=lambda index: (-frame.populations[index], index))
        return np.asarray(ordered[: self.population_limit], dtype=int)

    def _current_entries(self, frame: QuantumFrame) -> tuple[tuple[int, int, float], ...]:
        """Return bounded directed ``destination <- source`` current lanes."""

        current = frame.basis_current_inflow
        entries: list[tuple[int, int, float]] = []
        for left in range(current.shape[0]):
            for right in range(left + 1, current.shape[1]):
                value = float(current[left, right])
                if abs(value) <= 1.0e-15:
                    continue
                destination, source = (left, right) if value > 0.0 else (right, left)
                entries.append((destination, source, abs(value)))
        return tuple(sorted(entries, key=lambda item: (-item[2], item[0], item[1]))[: self.current_limit])

    def _conserved_labels(self, hamiltonian: Hamiltonian) -> frozenset[str]:
        for cached_hamiltonian, labels in self._conserved_cache:
            if cached_hamiltonian is hamiltonian:
                return labels
        labels = frozenset(conserved_pauli_labels(hamiltonian))
        self._conserved_cache.insert(0, (hamiltonian, labels))
        del self._conserved_cache[8:]
        return labels

    def messages(
        self, frame: QuantumFrame, *, temporal: BuresClockReading | None = None,
    ) -> list[tuple[str, list[Any]]]:
        """Build, but do not send, the complete bounded transaction."""

        if not isinstance(frame, QuantumFrame):
            raise ValueError("publish requires a QuantumFrame.")
        revision = int(frame.frame_index)
        pauli_indices = self._pauli_indices(frame)
        population_indices = self._population_indices(frame)
        current_entries = self._current_entries(frame)
        conserved = self._conserved_labels(frame.hamiltonian)
        messages: list[tuple[str, list[Any]]] = [
            (
                f"{QMW_QUANTUM_FRAME_OSC_ROOT}/frame/begin",
                [
                    revision, float(frame.time), QMW_QUANTUM_FRAME_OSC_SCHEMA,
                    frame.hamiltonian.qubits, len(population_indices),
                    len(pauli_indices), len(current_entries),
                ],
            ),
            (
                f"{QMW_QUANTUM_FRAME_OSC_ROOT}/diagnostics",
                [
                    revision, frame.trace, frame.purity, frame.minimum_eigenvalue,
                    frame.hermiticity_error, frame.commutator_norm, frame.energy,
                    float(np.linalg.norm(frame.rho_dot_unitary, ord="fro")),
                    float(np.linalg.norm(frame.rho_dot_dissipative, ord="fro")),
                ],
            ),
        ]
        if temporal is not None:
            if temporal.revision != revision:
                raise ValueError("temporal reading must belong to the published frame.")
            messages.append((
                f"{QMW_QUANTUM_FRAME_OSC_ROOT}/metric/bures",
                [
                    revision, temporal.delta, temporal.intrinsic_length,
                    temporal.remainder, temporal.pulses,
                    temporal.distance_per_pulse, temporal.clock_scale,
                ],
            ))
        for lane, index in enumerate(population_indices):
            messages.append((
                f"{QMW_QUANTUM_FRAME_OSC_ROOT}/population",
                [revision, lane, int(index), float(frame.populations[index]), float(frame.population_rate[index])],
            ))
        for lane, index in enumerate(pauli_indices):
            label = frame.pauli.labels[index]
            messages.append((
                f"{QMW_QUANTUM_FRAME_OSC_ROOT}/pauli",
                [
                    revision, lane, label, float(frame.pauli.values[index]),
                    float(frame.pauli.unitary_velocity[index]),
                    float(frame.pauli.dissipative_velocity[index]),
                    float(frame.pauli.velocity[index]), int(label in conserved),
                ],
            ))
        for lane, (destination, source, magnitude) in enumerate(current_entries):
            messages.append((
                f"{QMW_QUANTUM_FRAME_OSC_ROOT}/current",
                [revision, lane, destination, source, magnitude],
            ))
        messages.append((f"{QMW_QUANTUM_FRAME_OSC_ROOT}/frame/end", [revision]))
        return messages

    def publish(self, frame: QuantumFrame) -> int | None:
        """Send one current transaction or drop it before any transport occurs."""

        if not isinstance(frame, QuantumFrame):
            raise ValueError("publish requires a QuantumFrame.")
        revision = int(frame.frame_index)
        if revision <= self._last_published_revision:
            self.dropped_stale_frames += 1
            return None
        now = float(self._clock())
        if not math.isfinite(now):
            raise ValueError("monotonic_clock must return a finite value.")
        if self._last_published_at is not None and now - self._last_published_at < self.minimum_interval_seconds:
            self.dropped_rate_frames += 1
            return None
        temporal = self.temporal_clock.observe(frame) if self.temporal_clock is not None else None
        transaction = self.messages(frame, temporal=temporal)
        for address, payload in transaction:
            for client in self.clients:
                client.send_message(address, payload)
        self._last_published_revision = revision
        self._last_published_at = now
        return revision


__all__ = [
    "QMW_QUANTUM_FRAME_OSC_PORT", "QMW_QUANTUM_FRAME_OSC_ROOT",
    "QMW_QUANTUM_FRAME_OSC_SCHEMA", "QuantumFrameOSCPublisher",
]
