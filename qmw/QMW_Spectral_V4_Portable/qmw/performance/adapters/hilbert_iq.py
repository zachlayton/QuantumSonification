"""Read-only registration of an explicit sixteen-lane Hilbert I/Q world."""

from __future__ import annotations

from ..bodies import HilbertIQFrame
from ..envelope import (
    Authority, BasisDescriptor, EnvelopeHeader, EventStreamEnvelope,
    PerformanceSnapshot, StateEnvelope, StateKind,
)
from ..registry import SourceDescriptor


SOURCE_ID = "qmw.hilbert.iq"
NATIVE_STATE_SCHEMA = "qmw.hilbert_iq_frame.v1"
CAPABILITIES = frozenset({
    "state.hilbert_iq", "basis.computational_4qubit", "view.hilbert_iq",
    "audio.logical_lanes.16",
})
SOURCE_DESCRIPTOR = SourceDescriptor(
    source_id=SOURCE_ID,
    label="QMW Hilbert I/Q",
    state_kinds=frozenset({StateKind.HILBERT_IQ, StateKind.EVENT_STREAM}),
    capabilities=CAPABILITIES,
    logical_audio_lanes=16,
)


def adapt_hilbert_iq(
    frame: HilbertIQFrame, *, source_revision: int, logical_time: float,
    authority: Authority = Authority.DERIVED_OBSERVER,
) -> PerformanceSnapshot:
    """Wrap declared I/Q values; callers own their source and normalization."""

    if not isinstance(frame, HilbertIQFrame):
        raise ValueError("Hilbert I/Q adapter requires HilbertIQFrame.")
    header = EnvelopeHeader(
        source_id=SOURCE_ID, source_revision=source_revision, logical_time=logical_time,
        time_domain="hilbert_iq_observation_time", state_kind=StateKind.HILBERT_IQ,
        native_schema=NATIVE_STATE_SCHEMA,
        basis=BasisDescriptor(
            name="computational_4qubit", shape=(16,),
            semantics="declared in-phase and quadrature values in the four-qubit computational basis",
            ordering="binary basis words |0000> through |1111>",
        ),
        authority=authority, capabilities=CAPABILITIES,
        provenance={"adapter": "QMW Unified Quantum Instrument v1", "payload": "explicit_hilbert_iq"},
    )
    return PerformanceSnapshot(
        state=StateEnvelope(header=header, payload=frame),
        event_stream=EventStreamEnvelope(
            source_id=SOURCE_ID, source_revision=source_revision, logical_time=logical_time,
            time_domain="hilbert_iq_observation_time", events=(),
        ),
    )


__all__ = ["CAPABILITIES", "SOURCE_DESCRIPTOR", "SOURCE_ID", "adapt_hilbert_iq"]
