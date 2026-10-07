"""Read-only QFT V4.2 adapter for QMW Unified Quantum Instrument v1."""

from __future__ import annotations

from typing import Any

from qmw.qft.gaussian_temporal import GaussianFieldTemporalFrame
from qmw.qft.schema import ScalarFieldFrame
from qmw.qmw_probability_flow import FlowFrame

from ..envelope import (
    Authority,
    BasisDescriptor,
    EnvelopeHeader,
    EventStreamEnvelope,
    ObserverAttachment,
    PerformanceEvent,
    PerformanceSnapshot,
    StateEnvelope,
    StateKind,
)
from ..registry import SourceDescriptor


SOURCE_ID = "qmw.qft.v4_2"
NATIVE_STATE_SCHEMA = "qmw.scalar_field_frame.v3"
TEMPORAL_SCHEMA = "qmw.gaussian_field_temporal.v1"
ENERGY_FLOW_SCHEMA = "qmw.scalar_field.first_moment_flow.v4_1"
PROBABILITY_FLOW_SCHEMA = "qmw.probability_flow.v1"
SKIN_SCHEMA = "qmw.skin_encounter.v1"

CAPABILITIES = frozenset(
    {
        "state.scalar_field",
        "basis.periodic_site",
        "basis.real_fourier_mode",
        "observer.gaussian_temporal",
        "observer.energy_flow",
        "observer.probability_flow",
        "observer.skin_encounter",
        "events.temporal",
        "events.probability_flow",
        "timing.quantum",
        "timing.steady",
        "timing.euclidean",
        "timing.q_euclidean",
        "timing.q_geodesic",
        "timing.q_recursive",
        "audio.logical_lanes.16",
    }
)

SOURCE_DESCRIPTOR = SourceDescriptor(
    source_id=SOURCE_ID,
    label="QMW Gaussian Scalar Field V4.2",
    state_kinds=frozenset({StateKind.SCALAR_FIELD, StateKind.EVENT_STREAM}),
    capabilities=CAPABILITIES,
    logical_audio_lanes=16,
    legacy_contracts=(
        "qmw.scalar_field.osc.v4@udp:17860",
        "qmw.scalar_field.first_moment_flow.v4_1@udp:17862",
        "qmw.probability_flow.osc.v1@udp:17863",
    ),
)


def _event_id(revision: int, event_type: str, lane: int | None, ordinal: int) -> str:
    lane_token = "global" if lane is None else str(lane)
    return f"{SOURCE_ID}:{revision}:{event_type}:{lane_token}:{ordinal}"


def _temporal_events(
    temporal: GaussianFieldTemporalFrame | None,
    *,
    source_revision: int,
) -> list[PerformanceEvent]:
    if temporal is None:
        return []
    result: list[PerformanceEvent] = []
    ordinal = 0
    for reading in temporal.site_clocks:
        for offset in range(reading.pulses):
            record_index = reading.record_index - reading.pulses + offset + 1
            result.append(
                PerformanceEvent(
                    event_id=_event_id(source_revision, "temporal.gaussian_record", reading.site, ordinal),
                    event_type="temporal.gaussian_record",
                    source_id=SOURCE_ID,
                    source_revision=source_revision,
                    logical_time=reading.intrinsic_time,
                    time_domain="gaussian_bures_intrinsic_time",
                    lane=reading.site,
                    payload={
                        "native_source_revision": temporal.source_revision,
                        "record_index": record_index,
                        "delta_bures": reading.delta_bures,
                        "mean_phi": reading.mean_phi,
                        "mean_pi": reading.mean_pi,
                        "local_energy": reading.local_energy,
                    },
                )
            )
            ordinal += 1
    for reading in temporal.geodesic_site_clocks:
        for offset in range(reading.pulses):
            record_index = reading.record_index - reading.pulses + offset + 1
            result.append(
                PerformanceEvent(
                    event_id=_event_id(source_revision, "temporal.gaussian_geodesic", reading.site, ordinal),
                    event_type="temporal.gaussian_geodesic",
                    source_id=SOURCE_ID,
                    source_revision=source_revision,
                    logical_time=reading.intrinsic_length,
                    time_domain="gaussian_geodesic_intrinsic_length",
                    lane=reading.site,
                    payload={
                        "native_source_revision": temporal.source_revision,
                        "record_index": record_index,
                        "triangle_defect": reading.triangle_defect,
                        "normalized_bending": reading.normalized_bending,
                        "weighted_increment": reading.weighted_increment,
                    },
                )
            )
            ordinal += 1
    return result


def _flow_events(flow: FlowFrame | None, *, source_revision: int, ordinal: int) -> list[PerformanceEvent]:
    if flow is None:
        return []
    result: list[PerformanceEvent] = []
    for crossing in flow.crossings:
        lane = int(crossing.destination_region)
        result.append(
            PerformanceEvent(
                event_id=_event_id(source_revision, "flow.boundary_crossing", lane, ordinal),
                event_type="flow.boundary_crossing",
                source_id=SOURCE_ID,
                source_revision=source_revision,
                logical_time=crossing.time,
                time_domain="attached_provider_model_time",
                lane=lane,
                payload={
                    "source_region": crossing.source_region,
                    "destination_region": crossing.destination_region,
                    "boundary": crossing.boundary,
                    "direction": crossing.direction,
                    "magnitude": crossing.magnitude,
                    "phase": crossing.phase,
                },
            )
        )
        ordinal += 1
    return result


def adapt_qft_v4_2(
    frame: ScalarFieldFrame,
    *,
    source_revision: int,
    temporal: GaussianFieldTemporalFrame | None = None,
    energy_flow: Any | None = None,
    probability_flow: FlowFrame | None = None,
    skin_encounter: Any | None = None,
) -> PerformanceSnapshot:
    """Wrap one V4.2 revision without modifying or replacing native payloads."""

    if frame.sites != 16:
        raise ValueError("the QFT V4.2 adapter requires exactly sixteen sites")
    source_revision = int(source_revision)
    if temporal is not None and temporal.source_revision not in {
        source_revision,
        source_revision - 1,
    }:
        raise ValueError(
            "temporal frame must cite the adapted revision or the legacy "
            "zero-based engine revision immediately before it"
        )

    observers: dict[str, ObserverAttachment] = {}
    if temporal is not None:
        observers["gaussian_temporal"] = ObserverAttachment(
            "gaussian_temporal",
            TEMPORAL_SCHEMA,
            temporal,
            source_revision=temporal.source_revision,
            provenance={
                "revision_alignment": (
                    "exact"
                    if temporal.source_revision == source_revision
                    else "legacy_zero_based_engine_to_one_based_publisher"
                )
            },
        )
    if energy_flow is not None:
        observers["energy_flow"] = ObserverAttachment(
            "energy_flow", ENERGY_FLOW_SCHEMA, energy_flow, source_revision=source_revision
        )
    if probability_flow is not None:
        observers["probability_flow"] = ObserverAttachment(
            "probability_flow", PROBABILITY_FLOW_SCHEMA, probability_flow, source_revision=source_revision
        )
    if skin_encounter is not None:
        observers["skin_encounter"] = ObserverAttachment(
            "skin_encounter", SKIN_SCHEMA, skin_encounter, source_revision=source_revision
        )

    header = EnvelopeHeader(
        source_id=SOURCE_ID,
        source_revision=source_revision,
        logical_time=frame.time,
        time_domain="qft_model_time",
        state_kind=StateKind.SCALAR_FIELD,
        native_schema=NATIVE_STATE_SCHEMA,
        basis=BasisDescriptor(
            name="periodic_site",
            semantics="sixteen local Klein-Gordon field coordinates",
            shape=(frame.sites,),
            ordering="site index 0 through 15 on a periodic one-dimensional lattice",
            alternatives=("deterministic_real_fourier_normal_modes",),
        ),
        authority=Authority.AUTHORITATIVE,
        capabilities=CAPABILITIES,
        provenance={
            "world_version": "QFT V4.2",
            "legacy_state_contract": "qmw.scalar_field.osc.v4",
            "adapter": "QMW Unified Quantum Instrument v1",
            "temporal_native_source_revision": (
                None if temporal is None else temporal.source_revision
            ),
        },
    )
    state = StateEnvelope(header=header, payload=frame, observers=observers)

    events = _temporal_events(temporal, source_revision=source_revision)
    events.extend(
        _flow_events(
            probability_flow,
            source_revision=source_revision,
            ordinal=len(events),
        )
    )
    schemas = [
        schema
        for schema, value in (
            (TEMPORAL_SCHEMA, temporal),
            (PROBABILITY_FLOW_SCHEMA, probability_flow),
        )
        if value is not None
    ]
    stream = EventStreamEnvelope(
        source_id=SOURCE_ID,
        source_revision=source_revision,
        logical_time=frame.time,
        time_domain="qft_model_time",
        events=tuple(events),
        native_schemas=tuple(schemas),
    )
    return PerformanceSnapshot(state=state, event_stream=stream)


__all__ = [
    "CAPABILITIES",
    "SOURCE_DESCRIPTOR",
    "SOURCE_ID",
    "adapt_qft_v4_2",
]
