"""Revision-aligned bridge from Hilbert Transport 4.4 to interaction V1.

The public Hilbert-transport OSC contract is bounded and does not expose a
full density matrix. This in-process bridge therefore sits next to that
publisher, consuming the same authoritative four-qubit ``rho`` before the
bounded transport observation is sent. It also consumes one synchronized,
read-only :class:`qmw.gpe.field_frame.FieldFrame` for mode identity and
boundary-flux timing. Neither source is changed or coupled back.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Literal

import numpy as np

from .gpe.field_frame import FieldFrame
from .qmw_interaction_engine import (
    InteractionEngine,
    InteractionFrame,
    InteractionOSCPublisher,
    pauli_expectations,
)


Array = np.ndarray
HILBERT_TRANSPORT_V44_ROOT = "/qmw/4_4/quantum"
HILBERT_TRANSPORT_V44_SCHEMA = "qmw.4_4.quantum_transport.osc.v1"


@dataclass(frozen=True)
class HilbertTransportSourceFrameV44:
    """Private, authoritative source retained only for a local adapter step.

    ``rho`` is never placed in the bounded Hilbert-transport OSC transaction.
    The companion transport publisher may independently emit its populations,
    selected Pauli activity, and graph current under the V4.4 contract.
    """

    revision: int
    time: float
    rho: Array
    provenance: str = "authoritative_four_qubit_density_for_hilbert_transport_v4_4"

    def __post_init__(self) -> None:
        if int(self.revision) != self.revision or self.revision < 0:
            raise ValueError("Hilbert transport revision must be a nonnegative integer.")
        if not math.isfinite(float(self.time)):
            raise ValueError("Hilbert transport time must be finite.")
        matrix = np.asarray(self.rho, dtype=np.complex128)
        # This invokes the complete physical-density validation used by the
        # interaction engine and also pins the source to four qubits.
        pauli_expectations(matrix, ("IIII",))
        if matrix.shape != (16, 16):
            raise ValueError("Hilbert Transport V4.4 requires a 16x16 four-qubit rho.")
        object.__setattr__(self, "rho", np.array(matrix, copy=True))


@dataclass(frozen=True)
class FieldFrameTransportEnvelopeV44:
    """One FieldFrame plus its emitting transaction revision."""

    revision: int
    frame: FieldFrame

    def __post_init__(self) -> None:
        if int(self.revision) != self.revision or self.revision < 0:
            raise ValueError("FieldFrame revision must be a nonnegative integer.")
        if not isinstance(self.frame, FieldFrame):
            raise ValueError("field transport input must be a synchronized FieldFrame.")


@dataclass(frozen=True)
class FieldModeMapV44:
    """Explicit map from one declared FieldFrame basis to interaction modes.

    A map never guesses whether a flattened Fourier coefficient, a field site,
    or a geometry eigenmode is intended. ``basis`` must therefore be declared
    as ``fourier`` or ``geometry`` and indices are fixed, unique source-mode
    coordinates for the lifetime of the adapter.
    """

    source_indices: tuple[int, ...]
    basis: Literal["fourier", "geometry"] = "fourier"
    gain: float = 1.0

    def __post_init__(self) -> None:
        if not self.source_indices or any(int(index) != index or index < 0 for index in self.source_indices):
            raise ValueError("source_indices must be nonempty nonnegative integer mode indices.")
        if len(set(self.source_indices)) != len(self.source_indices):
            raise ValueError("each interaction mode must have a distinct declared field-mode source.")
        if self.basis not in ("fourier", "geometry"):
            raise ValueError("basis must be 'fourier' or 'geometry'.")
        if not math.isfinite(float(self.gain)) or self.gain < 0.0:
            raise ValueError("gain must be finite and nonnegative.")

    def coefficients(self, frame: FieldFrame) -> Array:
        if self.basis == "fourier":
            source = np.asarray(frame.mode_coeffs, dtype=np.complex128).reshape(-1)
        else:
            if frame.geometry_modes is None:
                raise ValueError("a geometry FieldModeMapV44 requires FieldFrame.geometry_modes.")
            source = np.asarray(frame.geometry_modes.coefficients, dtype=np.complex128).reshape(-1)
        if max(self.source_indices) >= source.size:
            raise ValueError("FieldModeMapV44 refers to an unavailable source mode.")
        return np.array([source[index] * self.gain for index in self.source_indices], dtype=np.complex128)


@dataclass(frozen=True)
class HilbertTransportInteractionFrameV44:
    """One committed result from two revision-aligned read-only observations."""

    revision: int
    time: float
    channel_expectations: dict[str, float]
    field_basis: str
    field_source_indices: tuple[int, ...]
    modal_drive: Array
    interaction: InteractionFrame
    provenance: str = "read_only_hilbert_transport_v4_4_fieldframe_to_interaction_adapter"


class HilbertTransportInteractionAdapterV44:
    """Join equal-revision Hilbert and FieldFrame observations into V1 output."""

    def __init__(
        self,
        engine: InteractionEngine,
        mode_map: FieldModeMapV44,
        *,
        publisher: InteractionOSCPublisher | None = None,
        modal_drive_mix: float = 1.0,
        time_tolerance: float = 1.0e-8,
    ) -> None:
        if engine.modes != len(mode_map.source_indices):
            raise ValueError("the FieldModeMapV44 size must equal the interaction engine mode count.")
        if not math.isfinite(modal_drive_mix) or not 0.0 <= modal_drive_mix <= 1.0:
            raise ValueError("modal_drive_mix must be finite and in [0, 1].")
        if not math.isfinite(time_tolerance) or time_tolerance < 0.0:
            raise ValueError("time_tolerance must be finite and nonnegative.")
        self.engine = engine
        self.mode_map = mode_map
        self.publisher = publisher
        self.modal_drive_mix = float(modal_drive_mix)
        self.time_tolerance = float(time_tolerance)

    def update(
        self,
        hilbert: HilbertTransportSourceFrameV44,
        field: FieldFrameTransportEnvelopeV44,
        *,
        dt: float,
    ) -> HilbertTransportInteractionFrameV44:
        """Commit one bridge frame only when both source revisions match."""

        if not isinstance(hilbert, HilbertTransportSourceFrameV44) or not isinstance(field, FieldFrameTransportEnvelopeV44):
            raise ValueError("the adapter requires explicit V4.4 Hilbert and FieldFrame envelopes.")
        if hilbert.revision != field.revision:
            raise ValueError("Hilbert and FieldFrame revisions must match before interaction is observed.")
        if abs(float(hilbert.time) - float(field.frame.time)) > self.time_tolerance:
            raise ValueError("Hilbert and FieldFrame times must match within time_tolerance.")
        channel_values = pauli_expectations(hilbert.rho, (channel.label for channel in self.engine.channels))
        drive = self.mode_map.coefficients(field.frame)
        interaction = self.engine.step(
            hilbert.rho, time=hilbert.time, dt=dt, flow=field.frame.flow,
            external_modal_drive=drive, modal_drive_mix=self.modal_drive_mix,
        )
        # Recheck the local calculation against the committed source contract;
        # the interaction engine must never silently choose a different Pauli
        # sector than the aligned Hilbert observation.
        if interaction.pauli_expectations != channel_values:
            raise RuntimeError("interaction channel expectations disagreed with the Hilbert source frame.")
        if self.publisher is not None:
            self.publisher.publish(interaction)
        return HilbertTransportInteractionFrameV44(
            revision=hilbert.revision, time=hilbert.time,
            channel_expectations=channel_values, field_basis=self.mode_map.basis,
            field_source_indices=self.mode_map.source_indices,
            modal_drive=np.array(drive, copy=True), interaction=interaction,
        )


__all__ = [
    "FieldFrameTransportEnvelopeV44", "FieldModeMapV44", "HILBERT_TRANSPORT_V44_ROOT",
    "HILBERT_TRANSPORT_V44_SCHEMA", "HilbertTransportInteractionAdapterV44",
    "HilbertTransportInteractionFrameV44", "HilbertTransportSourceFrameV44",
]
