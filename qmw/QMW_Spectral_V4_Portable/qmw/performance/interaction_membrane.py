"""Typed scattering-to-membrane performance adapter.

The interaction engine owns eight complex adapter modes.  The Quantum
Resonant Membrane owns twenty geometry-native modes.  They are not the same
basis.  This module therefore requires an explicit complex 20 x 8 mapping and
sums complex amplitudes before observing magnitude.  Its output is a
perceptual/event adapter only; it never updates ``rho``, the GPE field, or the
membrane dynamics.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Any

import numpy as np

from qmw.qmw_interaction_engine import InteractionFrame, ProcessPath

from .envelope import Authority, EventStreamEnvelope, PerformanceEvent
from .hilbert_pluck import HilbertCurrentPluckGateV1


Array = np.ndarray
SCHEMA = "qmw.resonant_interaction.adapter.v2"
OSC_ROOT = "/qmw/resonant_interaction/v1"
OUTPUT_PORT = 17922
SOURCE_MODE_COUNT = 8
MEMBRANE_MODE_COUNT = 20
EPS = 1.0e-12


def _readonly_complex(values: object, shape: tuple[int, ...]) -> Array:
    result = np.asarray(values, dtype=np.complex128)
    if result.shape != shape or not np.all(np.isfinite(result)):
        raise ValueError(f"complex values must be finite with shape {shape}.")
    result = np.array(result, copy=True)
    result.flags.writeable = False
    return result


def _readonly_real(values: object, shape: tuple[int, ...]) -> Array:
    result = np.asarray(values, dtype=float)
    if result.shape != shape or not np.all(np.isfinite(result)):
        raise ValueError(f"real values must be finite with shape {shape}.")
    result = np.array(result, copy=True)
    result.flags.writeable = False
    return result


@dataclass(frozen=True)
class InteractionMembraneMapV1:
    """Declared non-expansive projection from interaction to membrane modes."""

    matrix: Array
    identifier: str = "qmw_linear_spectral_20x8_v1"
    provenance: str = "declared_perceptual_20x8_mapping_not_a_physical_basis_identity"

    def __post_init__(self) -> None:
        if not self.identifier.strip() or not self.provenance.strip():
            raise ValueError("mapping identifier and provenance must be nonempty.")
        matrix = _readonly_complex(
            self.matrix, (MEMBRANE_MODE_COUNT, SOURCE_MODE_COUNT)
        )
        if np.any(np.linalg.norm(matrix, axis=1) <= EPS):
            raise ValueError("every membrane mode must have a declared source mapping.")
        if np.any(np.linalg.norm(matrix, axis=0) <= EPS):
            raise ValueError("every interaction mode must reach the membrane mapping.")
        if float(np.linalg.svd(matrix, compute_uv=False)[0]) > 1.0 + 1.0e-9:
            raise ValueError("the interaction-to-membrane map must be energy non-expansive.")
        object.__setattr__(self, "matrix", matrix)

    @classmethod
    def linear_spectral(cls) -> "InteractionMembraneMapV1":
        """Return the default order-preserving, overlapping 20 x 8 map.

        Each membrane row interpolates between neighboring interaction modes.
        The whole matrix is then normalized by its largest singular value, so
        it cannot create modal energy.  Overlap is intentional: opposing
        complex alternatives can cancel before magnitude is observed.
        """

        matrix = np.zeros(
            (MEMBRANE_MODE_COUNT, SOURCE_MODE_COUNT), dtype=np.complex128
        )
        for target in range(MEMBRANE_MODE_COUNT):
            position = target * SOURCE_MODE_COUNT / MEMBRANE_MODE_COUNT
            left = int(math.floor(position)) % SOURCE_MODE_COUNT
            fraction = position - math.floor(position)
            right = (left + 1) % SOURCE_MODE_COUNT
            matrix[target, left] += 1.0 - fraction
            matrix[target, right] += fraction
        matrix /= float(np.linalg.svd(matrix, compute_uv=False)[0])
        return cls(matrix)

    def project(self, amplitudes: object) -> Array:
        source = _readonly_complex(amplitudes, (SOURCE_MODE_COUNT,))
        return _readonly_complex(
            self.matrix @ source, (MEMBRANE_MODE_COUNT,)
        )


@dataclass(frozen=True)
class MembraneInteractionEventV1:
    event_id: str
    channel: str
    kind: str
    source_inputs: tuple[int, ...]
    source_outputs: tuple[int, ...]
    amplitude: complex
    membrane_amplitudes: Array
    membrane_energy: Array
    dominant_mode: int
    contact_azimuth: float

    def __post_init__(self) -> None:
        if not self.event_id.strip() or not self.channel.strip() or not self.kind.strip():
            raise ValueError("interaction event identity must be nonempty.")
        if not np.isfinite(self.amplitude):
            raise ValueError("interaction event amplitude must be finite.")
        amplitudes = _readonly_complex(
            self.membrane_amplitudes, (MEMBRANE_MODE_COUNT,)
        )
        energy = _readonly_real(self.membrane_energy, (MEMBRANE_MODE_COUNT,))
        if np.any(energy < 0.0) or not np.allclose(
            energy, np.abs(amplitudes) ** 2, rtol=1.0e-10, atol=1.0e-12
        ):
            raise ValueError("membrane event energy must equal squared amplitude magnitude.")
        if not 0 <= int(self.dominant_mode) < MEMBRANE_MODE_COUNT:
            raise ValueError("dominant membrane mode is out of range.")
        if not math.isfinite(float(self.contact_azimuth)):
            raise ValueError("contact azimuth must be finite.")
        object.__setattr__(self, "membrane_amplitudes", amplitudes)
        object.__setattr__(self, "membrane_energy", energy)
        object.__setattr__(self, "dominant_mode", int(self.dominant_mode))
        object.__setattr__(self, "contact_azimuth", float(self.contact_azimuth))


@dataclass(frozen=True)
class ResonantInteractionFrameV1:
    revision: int
    time: float
    mapping_id: str
    source_amplitudes: Array
    membrane_amplitudes: Array
    membrane_magnitudes: Array
    membrane_phases: Array
    membrane_energy: Array
    availability: tuple["InteractionAvailabilityV1", ...]
    pluck_threshold: float
    accumulator_peak_fraction: float
    interaction_omega_scale: float
    events: tuple[MembraneInteractionEventV1, ...]
    event_stream: EventStreamEnvelope
    source_schema: str = "qmw.interaction_scattering.v1"
    provenance: str = "coherent_interaction_to_resonant_membrane_sound_adapter_v1"


@dataclass(frozen=True)
class InteractionAvailabilityV1:
    """A continuously available scattering path; never an event by itself."""

    channel: str
    kind: str
    source_inputs: tuple[int, ...]
    source_outputs: tuple[int, ...]
    amplitude: complex


def _lane_profile(source: int, destination: int) -> Array:
    positions = np.arange(MEMBRANE_MODE_COUNT, dtype=float)
    source_center = source * MEMBRANE_MODE_COUNT / 16.0
    destination_center = destination * MEMBRANE_MODE_COUNT / 16.0

    def circular_gaussian(center: float) -> Array:
        distance = np.abs(positions - center)
        distance = np.minimum(distance, MEMBRANE_MODE_COUNT - distance)
        return np.exp(-0.5 * (distance / 1.65) ** 2)

    return circular_gaussian(destination_center) + (0.35 * circular_gaussian(source_center))


def _path_source_amplitudes(path: ProcessPath) -> Array:
    result = np.zeros(SOURCE_MODE_COUNT, dtype=np.complex128)
    for output, amplitude in zip(path.vertex.outputs, path.output_amplitudes):
        if not 0 <= int(output) < SOURCE_MODE_COUNT:
            raise ValueError("an interaction path output is outside the 8-mode source basis.")
        result[int(output)] += complex(amplitude)
    return result


def _contact_azimuth(amplitudes: Array) -> float:
    weights = np.abs(amplitudes) ** 2
    angles = np.linspace(-math.pi, math.pi, MEMBRANE_MODE_COUNT, endpoint=False)
    phasor = np.sum(weights * np.exp(1j * angles))
    return 0.0 if abs(phasor) <= EPS else float(np.angle(phasor))


class InteractionToMembraneAdapterV1:
    """Observe interaction frames as a typed membrane excitation stream."""

    def __init__(
        self,
        mode_map: InteractionMembraneMapV1 | None = None,
        *,
        pluck_gate: HilbertCurrentPluckGateV1 | None = None,
    ) -> None:
        self.mode_map = mode_map or InteractionMembraneMapV1.linear_spectral()
        self.pluck_gate = pluck_gate or HilbertCurrentPluckGateV1()

    def observe(
        self,
        revision: int,
        time: float,
        interaction: InteractionFrame,
        *,
        quantum_frame: object | None = None,
        dt: float | None = None,
        interaction_omega_scale: float = 1.0,
    ) -> ResonantInteractionFrameV1:
        if int(revision) != revision or revision < 0:
            raise ValueError("revision must be a nonnegative integer.")
        if not math.isfinite(float(time)) or not math.isclose(
            float(time), interaction.time, rel_tol=0.0, abs_tol=1.0e-8
        ):
            raise ValueError("adapter time must match the interaction frame time.")
        source = _readonly_complex(
            interaction.modal_field.amplitudes, (SOURCE_MODE_COUNT,)
        )
        membrane = self.mode_map.project(source)
        magnitudes = _readonly_real(np.abs(membrane), (MEMBRANE_MODE_COUNT,))
        phases = _readonly_real(np.angle(membrane), (MEMBRANE_MODE_COUNT,))
        energy = _readonly_real(magnitudes**2, (MEMBRANE_MODE_COUNT,))
        omega_scale = float(interaction_omega_scale)
        if not math.isfinite(omega_scale) or not 0.1 <= omega_scale <= 8.0:
            raise ValueError("interaction_omega_scale must lie in [0.1, 8].")

        availability = tuple(InteractionAvailabilityV1(
            channel=path.channel,
            kind=path.vertex.kind,
            source_inputs=tuple(path.vertex.inputs),
            source_outputs=tuple(path.vertex.outputs),
            amplitude=path.amplitude,
        ) for path in interaction.paths)
        gate_frame = None
        if quantum_frame is not None or dt is not None:
            if quantum_frame is None or dt is None:
                raise ValueError("quantum_frame and dt must be supplied together.")
            gate_frame = self.pluck_gate.observe(quantum_frame, dt)

        events: list[MembraneInteractionEventV1] = []
        performance_events: list[PerformanceEvent] = []
        continuous_peak = float(np.max(magnitudes))
        availability_mask = (
            np.ones(MEMBRANE_MODE_COUNT, dtype=float)
            if continuous_peak <= EPS else 0.2 + (0.8 * magnitudes / continuous_peak)
        )
        for index, pluck in enumerate(() if gate_frame is None else gate_frame.plucks):
            weights = _lane_profile(pluck.source, pluck.destination) * availability_mask
            weights /= max(float(np.linalg.norm(weights)), EPS)
            phase_bias = math.pi if pluck.dominant_contribution < 0.0 else 0.0
            event_amplitudes = weights * np.exp(1j * (phases + phase_bias))
            event_amplitudes *= math.sqrt(pluck.transported_probability)
            event_energy = _readonly_real(
                np.abs(event_amplitudes) ** 2, (MEMBRANE_MODE_COUNT,)
            )
            dominant = int(np.argmax(event_energy))
            channel = pluck.dominant_pauli or "HILBERT_CURRENT"
            event_id = (
                f"{int(revision)}:edge:{pluck.source}:{pluck.destination}:"
                f"{pluck.sequence}"
            )
            amplitude = math.sqrt(pluck.transported_probability) * np.exp(1j * phase_bias)
            event = MembraneInteractionEventV1(
                event_id=event_id,
                channel=channel,
                kind="probability_quantum_crossing",
                source_inputs=(pluck.source,),
                source_outputs=(pluck.destination,),
                amplitude=complex(amplitude),
                membrane_amplitudes=event_amplitudes,
                membrane_energy=event_energy,
                dominant_mode=dominant,
                contact_azimuth=_contact_azimuth(event_amplitudes),
            )
            events.append(event)
            performance_events.append(
                PerformanceEvent(
                    event_id=event_id,
                    event_type="hilbert_current_probability_quantum_pluck",
                    source_id="qmw.hilbert.current.pluck",
                    source_revision=int(revision),
                    logical_time=float(time),
                    time_domain="hilbert_gpe_coordinator",
                    lane=dominant,
                    authority=Authority.PERCEPTUAL_ADAPTER,
                    payload={
                        "channel": channel,
                        "kind": "probability_quantum_crossing",
                        "mapping_id": self.mode_map.identifier,
                        "source": pluck.source,
                        "destination": pluck.destination,
                        "transported_probability": pluck.transported_probability,
                        "current_magnitude": pluck.current_magnitude,
                        "membrane_energy": float(np.sum(event_energy)),
                    },
                )
            )
        event_stream = EventStreamEnvelope(
            source_id="qmw.hilbert.current.pluck",
            source_revision=int(revision),
            logical_time=float(time),
            time_domain="hilbert_gpe_coordinator",
            events=tuple(performance_events),
            native_schemas=(interaction.provenance, SCHEMA, "qmw.4_4.quantum_frame.osc.v1"),
        )
        return ResonantInteractionFrameV1(
            revision=int(revision),
            time=float(time),
            mapping_id=self.mode_map.identifier,
            source_amplitudes=source,
            membrane_amplitudes=membrane,
            membrane_magnitudes=magnitudes,
            membrane_phases=phases,
            membrane_energy=energy,
            availability=availability,
            pluck_threshold=(
                self.pluck_gate.threshold if gate_frame is None else gate_frame.threshold
            ),
            accumulator_peak_fraction=(
                0.0 if gate_frame is None else gate_frame.accumulator_peak_fraction
            ),
            interaction_omega_scale=omega_scale,
            events=tuple(events),
            event_stream=event_stream,
        )


class ResonantInteractionOSCPublisherV1:
    """Publish one atomic mapped frame to a downstream performance renderer."""

    def __init__(
        self,
        client: Any | None = None,
        *,
        host: str = "127.0.0.1",
        port: int = OUTPUT_PORT,
    ) -> None:
        if client is None:
            from pythonosc.udp_client import SimpleUDPClient

            client = SimpleUDPClient(host, int(port))
        self.client = client

    def _send(self, suffix: str, values: Any) -> None:
        self.client.send_message(f"{OSC_ROOT}/{suffix}", values)

    def publish(self, frame: ResonantInteractionFrameV1) -> int:
        revision = frame.revision
        self._send(
            "frame/begin",
            [
                revision,
                frame.time,
                SCHEMA,
                SOURCE_MODE_COUNT,
                MEMBRANE_MODE_COUNT,
                frame.mapping_id,
                len(frame.events),
                frame.pluck_threshold,
                frame.accumulator_peak_fraction,
                "hilbert_current_probability_quantum",
                len(frame.availability),
                frame.interaction_omega_scale,
            ],
        )
        for index, path in enumerate(frame.availability):
            self._send(
                "availability",
                [
                    revision, index, path.channel, path.kind,
                    float(path.amplitude.real), float(path.amplitude.imag),
                    len(path.source_inputs), len(path.source_outputs),
                    *path.source_inputs, *path.source_outputs,
                ],
            )
        for index, amplitude in enumerate(frame.membrane_amplitudes):
            self._send(
                "drive",
                [
                    revision,
                    index,
                    float(amplitude.real),
                    float(amplitude.imag),
                    float(frame.membrane_magnitudes[index]),
                    float(frame.membrane_phases[index]),
                    float(frame.membrane_energy[index]),
                ],
            )
        for index, event in enumerate(frame.events):
            source = event.source_inputs[0] if event.source_inputs else -1
            destination = event.source_outputs[0] if event.source_outputs else -1
            self._send(
                "event",
                [
                    revision,
                    index,
                    event.event_id,
                    event.channel,
                    event.kind,
                    float(event.amplitude.real),
                    float(event.amplitude.imag),
                    float(np.sum(event.membrane_energy)),
                    event.contact_azimuth,
                    event.dominant_mode,
                    source,
                    destination,
                    *[float(value) for value in np.abs(event.membrane_amplitudes)],
                    *[float(value) for value in np.angle(event.membrane_amplitudes)],
                ],
            )
        self._send("frame/end", [revision, frame.time, len(frame.events)])
        return revision

    def publish_recording_saved(self, artifact: dict[str, Any]) -> None:
        """Acknowledge downstream notation export to the recording UI."""

        self._send(
            "recording/saved",
            [
                int(artifact["event_count"]),
                str(artifact["musicxml"]),
                str(artifact["event_json"]),
            ],
        )

__all__ = [
    "InteractionMembraneMapV1",
    "InteractionAvailabilityV1",
    "InteractionToMembraneAdapterV1",
    "MEMBRANE_MODE_COUNT",
    "MembraneInteractionEventV1",
    "OSC_ROOT",
    "OUTPUT_PORT",
    "ResonantInteractionFrameV1",
    "ResonantInteractionOSCPublisherV1",
    "SCHEMA",
    "SOURCE_MODE_COUNT",
]
