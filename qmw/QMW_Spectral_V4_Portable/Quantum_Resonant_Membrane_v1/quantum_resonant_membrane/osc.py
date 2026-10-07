"""Versioned OSC observer for the standalone Quantum Resonant Membrane."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from typing import Protocol, Sequence

import numpy as np

from .interference_timbre import (
    InterferenceTimbreControl,
    InterferenceTimbreProjector,
)

from .density_engine import DensityFrame
from .flow import FlowFrame
from .geometry import MembraneGeometry
from .membrane import MembraneFrame
from .temporal import BuresTemporalFrame
from .terrain import TerrainFrame


ROOT = "/qmw/qrm/v1"
SCHEMA = "qmw.quantum_resonant_membrane.osc.v1"
DEFAULT_DATA_PORT = 17920
DEFAULT_CONTROL_PORT = 17921


class OSCClient(Protocol):
    def send_message(self, address: str, value: object) -> None: ...


def _floats(values: Sequence[float] | np.ndarray) -> list[float]:
    return [float(value) for value in np.asarray(values).ravel()]


@dataclass
class MembraneOSCPublisher:
    client: OSCClient
    revision: int = 0

    def _send(self, suffix: str, values: object) -> None:
        self.client.send_message(f"{ROOT}{suffix}", values)

    def publish_geometry(self, geometry: MembraneGeometry) -> None:
        """Publish immutable geometry; receivers may ignore messages they do not draw."""
        self._send(
            "/geometry/begin",
            [geometry.schema, len(geometry.vertices), len(geometry.faces), len(geometry.frequencies)],
        )
        for index, (position, region) in enumerate(zip(geometry.vertices, geometry.regions)):
            self._send("/geometry/vertex", [index, *_floats(position), int(region)])
        for index, face in enumerate(geometry.faces):
            self._send("/geometry/face", [index, *[int(value) for value in face]])
        self._send("/geometry/frequencies", _floats(geometry.frequencies))
        self._send("/geometry/end", [len(geometry.vertices), len(geometry.faces)])

    def publish_frame(
        self,
        density: DensityFrame,
        temporal: BuresTemporalFrame,
        terrain: TerrainFrame,
        flow: FlowFrame,
        membrane: MembraneFrame,
        *,
        interference_control: InterferenceTimbreControl | None = None,
        reset_epoch: int = 0,
    ) -> int:
        """Send a complete atomic frame bracketed by matching revision messages."""
        self.revision += 1
        revision = self.revision
        control = interference_control or InterferenceTimbreControl()
        timbre = InterferenceTimbreProjector().process(
            base_amplitudes=np.abs(membrane.audible_amplitudes),
            mode_ids=tuple(f"M{index + 1}" for index in range(len(membrane.audible_amplitudes))),
            source_id="quantum_resonant_membrane_v1",
            source_revision=revision,
            control=control,
            provenance=(
                density.schema,
                membrane.provenance,
                "20 geometry-native modes; signed membrane amplitudes retained in the audio adapter",
            ),
        )
        timbre_digest = hashlib.sha256(json.dumps(
            timbre.provenance,
            separators=(",", ":"),
        ).encode()).hexdigest()
        self._send(
            "/frame/begin",
            [
                revision,
                float(density.time),
                SCHEMA,
                len(density.populations),
                len(membrane.modal_amplitudes),
                flow.current_kind,
                int(reset_epoch),
            ],
        )
        self._send("/available", [revision, 1])
        self._send(
            "/density/global",
            [
                revision,
                density.purity,
                density.entropy_bits,
                density.coherence_l1,
                density.config.dephasing_rate,
                density.config.damping_rate,
                density.config.depolarizing_rate,
                density.hamiltonian_span,
                density.substeps,
                density.actual_substep,
            ],
        )
        self._send(
            "/density/preparation",
            [revision, density.preparation_mode, density.preparation_semantics],
        )
        self._send("/density/populations", [revision, *_floats(density.populations)])
        self._send("/density/rho_real", [revision, *_floats(density.rho.real)])
        self._send("/density/rho_imag", [revision, *_floats(density.rho.imag)])
        self._send(
            "/temporal/global",
            [
                revision,
                temporal.schema,
                temporal.delta_bures,
                temporal.intrinsic_length,
                temporal.temporal_remainder,
                temporal.temporal_pulses,
                temporal.temporal_record_index,
                temporal.weighted_time,
                temporal.geodesic_remainder,
                temporal.geodesic_pulses,
                temporal.geodesic_record_index,
                temporal.chord_bures,
                temporal.triangle_defect,
                temporal.normalized_bending,
                temporal.bending_increment,
                temporal.clock_scale,
                temporal.distance_per_pulse,
                temporal.geodesic_bending_depth,
            ],
        )
        self._send(
            "/field/global",
            [
                revision,
                flow.field_bus.provenance,
                float(np.max(np.abs(flow.field_bus.modal_frequency_offset_fraction))),
                float(np.mean(flow.field_bus.modal_susceptibility)),
                float(np.min(flow.field_bus.modal_quality_factor)),
                float(np.max(flow.field_bus.modal_quality_factor)),
                float(np.max(flow.field_bus.intermodal_coupling)),
            ],
        )
        self._send(
            "/field/frequency_offsets",
            [revision, *_floats(flow.field_bus.modal_frequency_offset_fraction)],
        )
        self._send(
            "/field/susceptibility",
            [revision, *_floats(flow.field_bus.modal_susceptibility)],
        )
        self._send(
            "/field/damping",
            [revision, *_floats(flow.field_bus.modal_damping_ratio)],
        )
        self._send(
            "/field/quality_factor",
            [revision, *_floats(flow.field_bus.modal_quality_factor)],
        )
        self._send(
            "/field/phase_orientation",
            [revision, *_floats(flow.field_bus.modal_phase_orientation)],
        )
        self._send(
            "/field/spectral_gradient",
            [revision, *_floats(flow.field_bus.spectral_gradient)],
        )
        self._send(
            "/field/intermodal_coupling",
            [revision, *_floats(flow.field_bus.intermodal_coupling)],
        )
        self._send(
            "/event/global",
            [
                revision,
                flow.event_bus.provenance,
                len(flow.event_bus.crossings),
                flow.event_bus.transported_probability,
                flow.event_bus.threshold,
                flow.event_bus.accumulator_peak_fraction,
            ],
        )
        for crossing in flow.event_bus.crossings:
            self._send(
                "/event/crossing",
                [
                    revision,
                    crossing.source,
                    crossing.destination,
                    crossing.direction,
                    crossing.transported_probability,
                    crossing.magnitude,
                    crossing.phase,
                    crossing.contact_vertex,
                    crossing.persistence,
                    crossing.current_kind,
                ],
            )
        self._send("/terrain/q", [revision, *_floats(terrain.q)])
        self._send("/terrain/qdot", [revision, *_floats(terrain.qdot)])
        self._send(
            "/terrain/global",
            [
                revision,
                terrain.lagrangian,
                terrain.kinetic_energy,
                terrain.potential_energy,
                terrain.omega_max,
                terrain.stability_dt_limit,
                terrain.substeps,
                terrain.actual_substep,
            ],
        )
        self._send(
            "/flow/global",
            [revision, flow.max_current, flow.total_transport, len(flow.crossings)],
        )
        self._send("/flow/region", [revision, *_floats(flow.region_flux)])
        for boundary in flow.boundaries:
            self._send(
                "/flow/boundary",
                [
                    revision,
                    boundary.source,
                    boundary.destination,
                    boundary.direction,
                    boundary.signed_current,
                    boundary.magnitude,
                    boundary.phase,
                    boundary.contact_vertex,
                    boundary.current_kind,
                ],
            )
        self._send("/membrane/modes", [revision, *_floats(membrane.audible_amplitudes)])
        self._send("/membrane/raw_modes", [revision, *_floats(membrane.modal_amplitudes)])
        self._send("/membrane/velocities", [revision, *_floats(membrane.modal_velocities)])
        self._send("/membrane/frequency_ratios", [revision, *_floats(membrane.frequency_ratios)])
        self._send(
            "/timbre/interference",
            [
                revision,
                control.revision,
                control.phase_radians,
                control.phase_spread_radians,
                control.depth,
                control.slew_seconds,
                control.phase_source,
                int(timbre.complete_cancellation),
                timbre.base_power,
                timbre.output_power,
                timbre_digest,
            ],
        )
        self._send(
            "/timbre/gain_factors",
            [revision, *_floats(timbre.gain_factors)],
        )
        self._send(
            "/timbre/output_amplitudes",
            [revision, *_floats(timbre.output_amplitudes)],
        )
        self._send(
            "/membrane/global",
            [
                revision,
                membrane.lagrangian,
                membrane.kinetic_energy,
                membrane.potential_energy,
                membrane.total_energy,
                membrane.omega_max,
                membrane.stability_dt_limit,
                membrane.substeps,
                membrane.actual_substep,
                membrane.injected_energy,
            ],
        )
        for crossing in membrane.crossings:
            self._send(
                "/crossing",
                [
                    revision,
                    crossing.source,
                    crossing.destination,
                    crossing.direction,
                    crossing.magnitude,
                    crossing.phase,
                    crossing.contact_vertex,
                    *(_floats(crossing.contact_position)),
                    crossing.persistence,
                    crossing.current_kind,
                    *_floats(crossing.modal_weights),
                ],
            )
        self._send("/frame/end", [revision, float(density.time)])
        return revision

    def publish_unavailable(self, reason: str = "backend_stopped") -> None:
        self._send("/available", [self.revision, 0, str(reason)])


__all__ = [
    "DEFAULT_CONTROL_PORT",
    "DEFAULT_DATA_PORT",
    "MembraneOSCPublisher",
    "ROOT",
    "SCHEMA",
]
