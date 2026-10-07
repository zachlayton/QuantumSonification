"""Read-only registration of the canonical four-qubit density-state world."""

from __future__ import annotations

from ..bodies import FourQubitDensityState
from ..envelope import (
    Authority, BasisDescriptor, EnvelopeHeader, EventStreamEnvelope,
    PerformanceSnapshot, StateEnvelope, StateKind,
)
from ..registry import SourceDescriptor


SOURCE_ID = "qmw.four_qubit.density"
NATIVE_STATE_SCHEMA = "qmw.four_qubit.density_state.v1"
CAPABILITIES = frozenset({
    "state.density", "basis.computational_4qubit", "view.density_population",
    "view.density_coherence", "audio.logical_lanes.16",
})
SOURCE_DESCRIPTOR = SourceDescriptor(
    source_id=SOURCE_ID,
    label="QMW Four-Qubit Density State",
    state_kinds=frozenset({StateKind.DENSITY_STATE, StateKind.EVENT_STREAM}),
    capabilities=CAPABILITIES,
    logical_audio_lanes=16,
)


def adapt_four_qubit_density_state(
    state: FourQubitDensityState, *, source_revision: int, logical_time: float,
    authority: Authority = Authority.AUTHORITATIVE,
) -> PerformanceSnapshot:
    """Wrap an already validated native density state without evolving it."""

    if not isinstance(state, FourQubitDensityState):
        raise ValueError("four-qubit density adapter requires FourQubitDensityState.")
    header = EnvelopeHeader(
        source_id=SOURCE_ID, source_revision=source_revision, logical_time=logical_time,
        time_domain="four_qubit_model_time", state_kind=StateKind.DENSITY_STATE,
        native_schema=NATIVE_STATE_SCHEMA,
        basis=BasisDescriptor(
            name="computational_4qubit", shape=(16,),
            semantics="four-qubit computational-basis populations and coherences",
            ordering="binary basis words |0000> through |1111>",
        ),
        authority=authority, capabilities=CAPABILITIES,
        provenance={"adapter": "QMW Unified Quantum Instrument v1", "payload": "native_density_state"},
    )
    return PerformanceSnapshot(
        state=StateEnvelope(header=header, payload=state),
        event_stream=EventStreamEnvelope(
            source_id=SOURCE_ID, source_revision=source_revision, logical_time=logical_time,
            time_domain="four_qubit_model_time", events=(),
        ),
    )


__all__ = ["CAPABILITIES", "SOURCE_DESCRIPTOR", "SOURCE_ID", "adapt_four_qubit_density_state"]
