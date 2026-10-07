"""Typed, source-neutral envelopes for QMW performance state and events.

The envelope supplies identity, timing, provenance, basis, and capability
metadata without flattening native scientific payloads into one ambiguous
array.  Payload ownership remains with the source model; this module neither
evolves nor mutates quantum state.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
import math
from types import MappingProxyType
from typing import Any, Mapping


SCHEMA = "qmw.performance.envelope.v1"


class StateKind(str, Enum):
    DENSITY_STATE = "DensityState"
    HILBERT_IQ = "HilbertIQ"
    SCALAR_FIELD = "ScalarField"
    SPINOR_FIELD = "SpinorField"
    JOINT_PARTICLE_FIELD = "JointParticleField"
    ENTANGLED_QUBIT_STATE = "EntangledQubitState"
    RELATIVISTIC_LEVELS = "RelativisticLevels"
    TOMOGRAPHY_RESULT = "TomographyResult"
    TRANSITION_CATALOG = "TransitionCatalog"
    EVENT_STREAM = "EventStream"


class Authority(str, Enum):
    AUTHORITATIVE = "authoritative"
    DERIVED_OBSERVER = "derived_observer"
    MEASURED = "measured"
    PERCEPTUAL_ADAPTER = "perceptual_adapter"


def _immutable_mapping(values: Mapping[str, Any] | None) -> Mapping[str, Any]:
    return MappingProxyType(dict(values or {}))


@dataclass(frozen=True)
class BasisDescriptor:
    """The declared meaning and ordering of one native state basis."""

    name: str
    semantics: str
    shape: tuple[int, ...]
    ordering: str
    alternatives: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.name.strip() or not self.semantics.strip() or not self.ordering.strip():
            raise ValueError("basis name, semantics, and ordering must be nonempty")
        if not self.shape or any(int(value) < 1 for value in self.shape):
            raise ValueError("basis shape must contain positive dimensions")


@dataclass(frozen=True)
class EnvelopeHeader:
    source_id: str
    source_revision: int
    logical_time: float
    time_domain: str
    state_kind: StateKind
    native_schema: str
    basis: BasisDescriptor
    authority: Authority
    capabilities: frozenset[str] = frozenset()
    provenance: Mapping[str, Any] = field(default_factory=dict)
    confidence: float = 1.0
    complete: bool = True
    envelope_schema: str = SCHEMA

    def __post_init__(self) -> None:
        if not self.source_id.strip() or not self.native_schema.strip() or not self.time_domain.strip():
            raise ValueError("source_id, native_schema, and time_domain must be nonempty")
        if int(self.source_revision) < 0:
            raise ValueError("source_revision must be nonnegative")
        if not math.isfinite(float(self.logical_time)):
            raise ValueError("logical_time must be finite")
        if not math.isfinite(float(self.confidence)) or not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be finite and between zero and one")
        object.__setattr__(self, "source_revision", int(self.source_revision))
        object.__setattr__(self, "logical_time", float(self.logical_time))
        object.__setattr__(self, "confidence", float(self.confidence))
        object.__setattr__(self, "capabilities", frozenset(self.capabilities))
        object.__setattr__(self, "provenance", _immutable_mapping(self.provenance))


@dataclass(frozen=True)
class ObserverAttachment:
    """A read-only observer payload with explicit native revision provenance."""

    name: str
    native_schema: str
    payload: Any
    authority: Authority = Authority.DERIVED_OBSERVER
    source_revision: int | None = None
    provenance: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.name.strip() or not self.native_schema.strip():
            raise ValueError("observer name and schema must be nonempty")
        if self.source_revision is not None and int(self.source_revision) < 0:
            raise ValueError("observer source_revision must be nonnegative when present")
        object.__setattr__(
            self,
            "source_revision",
            None if self.source_revision is None else int(self.source_revision),
        )
        object.__setattr__(self, "provenance", _immutable_mapping(self.provenance))


@dataclass(frozen=True)
class StateEnvelope:
    """One complete native state plus optional, explicitly derived observers."""

    header: EnvelopeHeader
    payload: Any
    observers: Mapping[str, ObserverAttachment] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.header.state_kind is StateKind.EVENT_STREAM:
            raise ValueError("EventStream must use EventStreamEnvelope")
        attachments = dict(self.observers)
        if any(key != value.name for key, value in attachments.items()):
            raise ValueError("observer mapping keys must match attachment names")
        object.__setattr__(self, "observers", MappingProxyType(attachments))


@dataclass(frozen=True)
class PerformanceEvent:
    event_id: str
    event_type: str
    source_id: str
    source_revision: int
    logical_time: float
    time_domain: str
    lane: int | None = None
    payload: Mapping[str, Any] = field(default_factory=dict)
    authority: Authority = Authority.DERIVED_OBSERVER

    def __post_init__(self) -> None:
        if (
            not self.event_id.strip()
            or not self.event_type.strip()
            or not self.source_id.strip()
            or not self.time_domain.strip()
        ):
            raise ValueError("event identity, type, source, and time domain must be nonempty")
        if int(self.source_revision) < 0:
            raise ValueError("event source_revision must be nonnegative")
        if not math.isfinite(float(self.logical_time)):
            raise ValueError("event logical_time must be finite")
        if self.lane is not None and int(self.lane) < 0:
            raise ValueError("event lane must be nonnegative when present")
        object.__setattr__(self, "source_revision", int(self.source_revision))
        object.__setattr__(self, "logical_time", float(self.logical_time))
        object.__setattr__(self, "lane", None if self.lane is None else int(self.lane))
        object.__setattr__(self, "payload", _immutable_mapping(self.payload))


@dataclass(frozen=True)
class EventStreamEnvelope:
    source_id: str
    source_revision: int
    logical_time: float
    time_domain: str
    events: tuple[PerformanceEvent, ...]
    native_schemas: tuple[str, ...] = ()
    state_kind: StateKind = StateKind.EVENT_STREAM
    envelope_schema: str = SCHEMA

    def __post_init__(self) -> None:
        if not self.source_id.strip() or not self.time_domain.strip() or int(self.source_revision) < 0:
            raise ValueError("event stream source must be nonempty with a nonnegative revision")
        if not math.isfinite(float(self.logical_time)):
            raise ValueError("event stream logical_time must be finite")
        events = tuple(self.events)
        for event in events:
            if event.source_id != self.source_id or event.source_revision != int(self.source_revision):
                raise ValueError("every event must reference the stream source and revision")
        object.__setattr__(self, "source_revision", int(self.source_revision))
        object.__setattr__(self, "logical_time", float(self.logical_time))
        object.__setattr__(self, "events", events)
        object.__setattr__(self, "native_schemas", tuple(dict.fromkeys(self.native_schemas)))


@dataclass(frozen=True)
class PerformanceSnapshot:
    """An atomic state observation and the events derived from that revision."""

    state: StateEnvelope
    event_stream: EventStreamEnvelope

    def __post_init__(self) -> None:
        header = self.state.header
        stream = self.event_stream
        if (header.source_id, header.source_revision) != (
            stream.source_id,
            stream.source_revision,
        ):
            raise ValueError("state and event stream must share a source revision")


__all__ = [
    "Authority",
    "BasisDescriptor",
    "EnvelopeHeader",
    "EventStreamEnvelope",
    "ObserverAttachment",
    "PerformanceEvent",
    "PerformanceSnapshot",
    "SCHEMA",
    "StateEnvelope",
    "StateKind",
]
