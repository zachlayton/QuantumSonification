"""Renderer adapter for authoritative four-qubit GRW events.

The physics channel owns state transitions.  This module performs no collapse
and never mutates ``rho``; it projects a committed :class:`GRWEvent` into one
canonical frame shared by Max, SuperCollider, and Processing.

Mapping contract
----------------
trace distance       -> internal excitation amplitude
fractional coherence loss -> bandwidth and grain structure
affected qubit       -> one of four resonator branches
dominant Pauli delta -> signed XYZ coupling orientation
post-event rho       -> continuing branch and complex resonant condition
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Any, Iterable, Protocol

import numpy as np

from density.grw_event_channel_v1 import GRWEvent


class OSCClient(Protocol):
    def send_message(self, address: str, value: Any) -> None: ...


PAULI_AXES = {"I": 0, "X": 1, "Y": 2, "Z": 3}
_PAULI_MATRICES = {
    "X": np.array([[0.0, 1.0], [1.0, 0.0]], dtype=np.complex128),
    "Y": np.array([[0.0, -1.0j], [1.0j, 0.0]], dtype=np.complex128),
    "Z": np.array([[1.0, 0.0], [0.0, -1.0]], dtype=np.complex128),
}
_IDENTITY = np.eye(2, dtype=np.complex128)


@dataclass(frozen=True)
class GRWSonificationConfig:
    """Musical scaling without changing the physical event descriptors."""

    excitation_gain: float = 1.0
    bandwidth_floor: float = 0.04
    bandwidth_ceiling: float = 1.0
    grain_floor: float = 0.0
    grain_ceiling: float = 1.0

    def __post_init__(self) -> None:
        if self.excitation_gain < 0.0:
            raise ValueError("excitation_gain must be non-negative")
        for name in (
            "bandwidth_floor",
            "bandwidth_ceiling",
            "grain_floor",
            "grain_ceiling",
        ):
            value = float(getattr(self, name))
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{name} must lie in [0, 1]")
        if self.bandwidth_floor > self.bandwidth_ceiling:
            raise ValueError("bandwidth_floor cannot exceed bandwidth_ceiling")
        if self.grain_floor > self.grain_ceiling:
            raise ValueError("grain_floor cannot exceed grain_ceiling")


@dataclass(frozen=True)
class GRWSonificationFrame:
    event_id: int
    logical_time: float
    revision: int
    audible: bool
    excitation_amplitude: float
    coherence_loss: float
    coherence_loss_fraction: float
    bandwidth: float
    grain_structure: float
    branch: int
    branch_levels: tuple[float, float, float, float]
    dominant_pauli: str
    dominant_pauli_delta: float
    pauli_axis: str
    pauli_axis_code: int
    orientation: tuple[float, float, float]
    orientation_sign: float
    post_population: tuple[float, ...]
    post_rho_real: tuple[float, ...]
    post_rho_imag: tuple[float, ...]
    post_rho_magnitude: tuple[float, ...]
    post_rho_phase: tuple[float, ...]
    delta_rho_real: tuple[float, ...]
    delta_rho_imag: tuple[float, ...]
    delta_rho_magnitude: tuple[float, ...]
    delta_rho_phase: tuple[float, ...]
    delta_peak: float

    def event_packet(self) -> list[Any]:
        """Compact event packet; matrix condition is published separately."""

        return [
            self.event_id,
            self.branch,
            self.excitation_amplitude,
            self.coherence_loss_fraction,
            self.bandwidth,
            self.grain_structure,
            self.pauli_axis_code,
            self.orientation_sign,
            self.dominant_pauli_delta,
            int(self.audible),
        ]


def _clip01(value: float) -> float:
    return float(np.clip(value, 0.0, 1.0))


def _lerp(low: float, high: float, amount: float) -> float:
    return float(low + (high - low) * _clip01(amount))


def _local_pauli_expectation(rho: np.ndarray, qubit: int, axis: str) -> float:
    operators = [_IDENTITY] * 4
    operators[qubit] = _PAULI_MATRICES[axis]
    operator = operators[0]
    for factor in operators[1:]:
        operator = np.kron(operator, factor)
    return float(np.trace(rho @ operator).real)


def _branch_levels(rho: np.ndarray) -> tuple[float, float, float, float]:
    """Local Bloch lengths become persistent four-branch resonance levels."""

    levels = []
    for qubit in range(4):
        components = [
            _local_pauli_expectation(rho, qubit, axis)
            for axis in ("X", "Y", "Z")
        ]
        levels.append(_clip01(math.sqrt(sum(value * value for value in components))))
    return tuple(levels)  # type: ignore[return-value]


def _coupling_orientation(event: GRWEvent) -> tuple[str, float, tuple[float, float, float]]:
    term = str(event.dominant_pauli_delta).upper()
    axis = term[event.qubit] if len(term) == 4 and term[event.qubit] != "I" else "I"
    if axis == "I":
        axis = next((symbol for symbol in term if symbol in "XYZ"), "X")
    sign = -1.0 if event.dominant_pauli_delta_value < 0.0 else 1.0
    orientation = {
        "X": (sign, 0.0, 0.0),
        "Y": (0.0, sign, 0.0),
        "Z": (0.0, 0.0, sign),
    }[axis]
    return axis, sign, orientation


def _normalized_complex_fields(matrix: np.ndarray) -> tuple[
    tuple[float, ...],
    tuple[float, ...],
    tuple[float, ...],
    tuple[float, ...],
    float,
]:
    values = np.asarray(matrix, dtype=np.complex128)
    magnitude = np.abs(values)
    peak = float(np.max(magnitude))
    normalized = magnitude / peak if peak > 1e-15 else np.zeros_like(magnitude)
    phase = np.angle(values) / math.pi
    return (
        tuple(float(value) for value in values.real.reshape(-1)),
        tuple(float(value) for value in values.imag.reshape(-1)),
        tuple(float(value) for value in normalized.reshape(-1)),
        tuple(float(value) for value in phase.reshape(-1)),
        peak,
    )


def frame_from_grw_event(
    event: GRWEvent,
    config: GRWSonificationConfig = GRWSonificationConfig(),
) -> GRWSonificationFrame:
    """Project one already-committed GRW event into renderer controls."""

    rho_after = np.asarray(event.rho_after, dtype=np.complex128)
    delta_rho = np.asarray(event.delta_rho, dtype=np.complex128)
    if rho_after.shape != (16, 16) or delta_rho.shape != (16, 16):
        raise ValueError("GRW sonification v1 requires 16x16 matrices")

    excitation = _clip01(event.trace_distance * config.excitation_gain)
    coherence_loss = max(0.0, event.coherence_before - event.coherence_after)
    coherence_fraction = _clip01(
        coherence_loss / max(abs(event.coherence_before), 1e-12)
    )
    bandwidth = _lerp(
        config.bandwidth_floor,
        config.bandwidth_ceiling,
        math.sqrt(coherence_fraction),
    )
    grain = _lerp(
        config.grain_floor,
        config.grain_ceiling,
        coherence_fraction,
    )
    axis, sign, orientation = _coupling_orientation(event)

    post_real, post_imag, post_magnitude, post_phase, _ = (
        _normalized_complex_fields(rho_after)
    )
    delta_real, delta_imag, delta_magnitude, delta_phase, delta_peak = (
        _normalized_complex_fields(delta_rho)
    )
    population = tuple(
        float(np.clip(value, 0.0, 1.0))
        for value in np.real(np.diag(rho_after))
    )

    return GRWSonificationFrame(
        event_id=int(event.event_id),
        logical_time=float(event.logical_time),
        revision=int(event.revision_after),
        audible=bool(event.audible),
        excitation_amplitude=excitation,
        coherence_loss=float(coherence_loss),
        coherence_loss_fraction=coherence_fraction,
        bandwidth=bandwidth,
        grain_structure=grain,
        branch=int(event.qubit),
        branch_levels=_branch_levels(rho_after),
        dominant_pauli=str(event.dominant_pauli_delta),
        dominant_pauli_delta=float(event.dominant_pauli_delta_value),
        pauli_axis=axis,
        pauli_axis_code=PAULI_AXES[axis],
        orientation=orientation,
        orientation_sign=sign,
        post_population=population,
        post_rho_real=post_real,
        post_rho_imag=post_imag,
        post_rho_magnitude=post_magnitude,
        post_rho_phase=post_phase,
        delta_rho_real=delta_real,
        delta_rho_imag=delta_imag,
        delta_rho_magnitude=delta_magnitude,
        delta_rho_phase=delta_phase,
        delta_peak=delta_peak,
    )


class GRWSonificationAdapter:
    """Publish identical GRW render frames to any number of OSC clients."""

    PREFIX = "/qmw/grw/sonification"

    def __init__(
        self,
        clients: Iterable[OSCClient] = (),
        config: GRWSonificationConfig = GRWSonificationConfig(),
    ) -> None:
        self.clients = tuple(client for client in clients if client is not None)
        self.config = config
        self.last_signature: tuple[int, int, float] | None = None

    def reset(self) -> None:
        self.last_signature = None

    def _send(self, suffix: str, value: Any) -> None:
        address = f"{self.PREFIX}/{suffix}"
        for client in self.clients:
            client.send_message(address, value)

    def publish_event(self, event: GRWEvent) -> GRWSonificationFrame | None:
        signature = (
            int(event.event_id),
            int(event.revision_after),
            float(event.logical_time),
        )
        if signature == self.last_signature:
            return None
        frame = frame_from_grw_event(event, self.config)

        # Publish the continuing condition before the final event/trigger packet.
        self._send("post/population", list(frame.post_population))
        self._send("post/branch_levels", list(frame.branch_levels))
        self._send("post/rho_real", list(frame.post_rho_real))
        self._send("post/rho_imag", list(frame.post_rho_imag))
        self._send("post/rho_magnitude", list(frame.post_rho_magnitude))
        self._send("post/rho_phase", list(frame.post_rho_phase))
        self._send("delta/real", list(frame.delta_rho_real))
        self._send("delta/imag", list(frame.delta_rho_imag))
        self._send("delta/magnitude", list(frame.delta_rho_magnitude))
        self._send("delta/phase", list(frame.delta_rho_phase))
        self._send("delta/peak", frame.delta_peak)
        self._send("orientation", list(frame.orientation))
        self._send(
            "pauli",
            [frame.dominant_pauli, frame.pauli_axis, frame.dominant_pauli_delta],
        )
        self._send("event", frame.event_packet())
        self.last_signature = signature
        return frame


__all__ = [
    "GRWSonificationAdapter",
    "GRWSonificationConfig",
    "GRWSonificationFrame",
    "frame_from_grw_event",
]
