"""Feynman-inspired, read-only interaction calculus for QMW.

This module is deliberately *not* a particle-physics simulator and it never
updates the density matrix, a GPE field, or a shared flow frame.  It is an
experimental adapter that derives selected Pauli expectations from a supplied
``rho``, uses boundary flux only to time candidate vertices, and evolves its
own bounded complex modal field.  Complex process amplitudes are accumulated
before their magnitude is observed, so alternative channels can interfere.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Iterable, Mapping, Sequence

import numpy as np

from .feynman_process_graph import ProcessGraph, exchange_graph, tree_graph


Array = np.ndarray
EPS = 1.0e-12
SCHEMA = "qmw.interaction_scattering.v1"
OSC_ROOT = "/qmw/interaction/v1"
OUTPUT_PORT = 17872


_PAULI = {
    "I": np.eye(2, dtype=np.complex128),
    "X": np.array([[0.0, 1.0], [1.0, 0.0]], dtype=np.complex128),
    "Y": np.array([[0.0, -1j], [1j, 0.0]], dtype=np.complex128),
    "Z": np.array([[1.0, 0.0], [0.0, -1.0]], dtype=np.complex128),
}


def _finite_vector(name: str, values: object, *, nonnegative: bool = False) -> Array:
    result = np.asarray(values, dtype=float)
    if result.ndim != 1 or result.size < 1 or not np.all(np.isfinite(result)):
        raise ValueError(f"{name} must be a finite one-dimensional array.")
    if nonnegative and np.any(result < 0.0):
        raise ValueError(f"{name} must be nonnegative.")
    return np.array(result, copy=True)


def _density_matrix(rho: object) -> Array:
    matrix = np.asarray(rho, dtype=np.complex128)
    if matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1] or matrix.shape[0] < 2:
        raise ValueError("rho must be a square density matrix of dimension at least two.")
    dimension = matrix.shape[0]
    if dimension & (dimension - 1):
        raise ValueError("rho dimension must be a power of two for a Pauli decomposition.")
    if not np.all(np.isfinite(matrix)):
        raise ValueError("rho must be finite.")
    if not np.allclose(matrix, matrix.conj().T, rtol=0.0, atol=1.0e-9):
        raise ValueError("rho must be Hermitian.")
    trace = np.trace(matrix)
    if not np.isclose(trace, 1.0, rtol=0.0, atol=1.0e-9):
        raise ValueError("rho must have unit trace.")
    if float(np.min(np.linalg.eigvalsh(matrix))) < -1.0e-9:
        raise ValueError("rho must be positive semidefinite.")
    return np.array(matrix, copy=True)


def pauli_operator(label: str) -> Array:
    """Return the tensor-product Pauli operator named by ``label``."""

    if not isinstance(label, str) or not label or any(symbol not in _PAULI for symbol in label):
        raise ValueError("a Pauli label must be a nonempty string over I, X, Y, Z.")
    result = _PAULI[label[0]]
    for symbol in label[1:]:
        result = np.kron(result, _PAULI[symbol])
    return result


def pauli_expectations(rho: object, labels: Iterable[str]) -> dict[str, float]:
    """Return real expectations ``Tr(rho P)`` for selected Pauli strings.

    The input density matrix is validated and copied; it is not normalized or
    otherwise modified.  Pauli strings must match its qubit count.
    """

    matrix = _density_matrix(rho)
    qubits = int(round(math.log2(matrix.shape[0])))
    result: dict[str, float] = {}
    for label in labels:
        if len(label) != qubits:
            raise ValueError(f"Pauli label {label!r} does not match rho's {qubits} qubits.")
        value = np.trace(matrix @ pauli_operator(label))
        if abs(float(value.imag)) > 1.0e-8:
            raise ValueError("a Hermitian density matrix must have real Pauli expectations.")
        result[label] = float(np.clip(value.real, -1.0, 1.0))
    return result


@dataclass(frozen=True)
class InteractionVertex:
    """A typed modal redistribution rule, not an update to quantum state."""

    kind: str
    inputs: tuple[int, ...]
    outputs: tuple[int, ...]
    pauli_label: str

    def __post_init__(self) -> None:
        supported = {(1, 1): "1_to_1", (1, 2): "1_to_2", (2, 1): "2_to_1", (2, 2): "2_to_2"}
        signature = (len(self.inputs), len(self.outputs))
        if self.kind != supported.get(signature):
            raise ValueError("kind must agree with the vertex input/output arity.")
        if not self.inputs or not self.outputs or min(*self.inputs, *self.outputs) < 0:
            raise ValueError("vertex mode indices must be nonnegative and nonempty.")
        pauli_operator(self.pauli_label)


@dataclass(frozen=True)
class InteractionChannel:
    """One Pauli-selected route through a :class:`InteractionVertex`."""

    vertex: InteractionVertex
    scale: float = 1.0
    phase_offset: float = 0.0
    process_graph: ProcessGraph | None = None

    def __post_init__(self) -> None:
        if not math.isfinite(self.scale) or self.scale < 0.0:
            raise ValueError("channel scale must be finite and nonnegative.")
        if not math.isfinite(self.phase_offset):
            raise ValueError("channel phase_offset must be finite.")
        if self.process_graph is not None:
            if not isinstance(self.process_graph, ProcessGraph):
                raise ValueError("process_graph must be a ProcessGraph when supplied.")
            if self.process_graph.input_count != len(self.vertex.inputs) or self.process_graph.output_count != len(self.vertex.outputs):
                raise ValueError("process_graph external ports must match the interaction vertex arity.")

    @property
    def label(self) -> str:
        return self.vertex.pauli_label


@dataclass(frozen=True)
class ComplexPropagator:
    """Per-mode ``exp((-damping + i frequency) dt)`` propagation."""

    frequencies: Array
    damping: Array

    def __post_init__(self) -> None:
        frequencies = _finite_vector("frequencies", self.frequencies)
        damping = _finite_vector("damping", self.damping, nonnegative=True)
        if frequencies.shape != damping.shape:
            raise ValueError("frequencies and damping must have the same shape.")
        object.__setattr__(self, "frequencies", frequencies)
        object.__setattr__(self, "damping", damping)

    def advance(self, amplitudes: object, dt: float) -> Array:
        if not math.isfinite(dt) or dt <= 0.0:
            raise ValueError("dt must be finite and positive.")
        field = np.asarray(amplitudes, dtype=np.complex128)
        if field.shape != self.frequencies.shape or not np.all(np.isfinite(field)):
            raise ValueError("amplitudes must be finite and match the propagator modes.")
        return np.array(field * np.exp((-self.damping + 1j * self.frequencies) * dt), copy=True)


@dataclass(frozen=True)
class ProcessPath:
    """One complex alternative whose outputs remain unobserved until summed."""

    channel: str
    vertex: InteractionVertex
    amplitude: complex
    output_amplitudes: tuple[complex, ...]
    graph: ProcessGraph | None = None


class AmplitudeAccumulator:
    """Accumulate complex alternatives by output mode before observation."""

    def __init__(self, modes: int) -> None:
        if int(modes) != modes or modes < 1:
            raise ValueError("modes must be a positive integer.")
        self._amplitudes = np.zeros(int(modes), dtype=np.complex128)

    def add(self, outputs: Sequence[int], amplitudes: Sequence[complex]) -> None:
        if len(outputs) != len(amplitudes):
            raise ValueError("outputs and amplitudes must have the same length.")
        for mode, amplitude in zip(outputs, amplitudes):
            if int(mode) != mode or not 0 <= int(mode) < self._amplitudes.size:
                raise ValueError("output mode is outside the accumulator.")
            if not np.isfinite(amplitude):
                raise ValueError("path amplitudes must be finite.")
            self._amplitudes[int(mode)] += complex(amplitude)

    def result(self) -> Array:
        return np.array(self._amplitudes, copy=True)


@dataclass(frozen=True)
class ModalField:
    """The engine's own complex modal adapter state.

    ``excitation`` is ``|amplitude|^2``.  ``transfer_flux`` is a discrete
    finite difference over the engine's time step, never a quantum current.
    """

    amplitudes: Array
    magnitudes: Array
    phases: Array
    excitation: Array
    transfer_flux: Array


@dataclass(frozen=True)
class InteractionFrame:
    """Read-only quantum analysis plus one adapter-side modal update."""

    time: float
    pauli_expectations: Mapping[str, float]
    couplings: Mapping[str, complex]
    flow_strength: float
    flow_phase: float
    paths: tuple[ProcessPath, ...]
    modal_field: ModalField
    propagated_excitation: float
    modal_excitation: float
    provenance: str = "feynman_inspired_read_only_interaction_adapter"


def _default_channel(
    kind: str,
    inputs: tuple[int, ...],
    outputs: tuple[int, ...],
    label: str,
    *,
    exchange: bool = False,
    loop_order: int = 0,
) -> InteractionChannel:
    vertex = InteractionVertex(kind, inputs, outputs, label)
    graph = (
        exchange_graph(
            f"qmw_{label.lower()}_{kind}_exchange",
            inputs=len(inputs), outputs=len(outputs), coupling_label=label,
            loop_order=loop_order,
        )
        if exchange
        else tree_graph(
            f"qmw_{label.lower()}_{kind}",
            inputs=len(inputs), outputs=len(outputs), coupling_label=label,
        )
    )
    return InteractionChannel(
        vertex,
        process_graph=graph,
    )


DEFAULT_CHANNELS = (
    _default_channel("2_to_2", (0, 1), (4, 5), "XYXY", exchange=True),
    _default_channel("2_to_2", (2, 3), (6, 7), "ZZXX", exchange=True),
    _default_channel("1_to_2", (4,), (0, 2), "IXXX"),
    _default_channel("2_to_1", (5, 6), (7,), "XXIX"),
)


class InteractionEngine:
    """Small complex process engine for fixed external modal identities.

    The quantum frame supplies channel availability; an optional shared flow
    frame supplies only an event-strength/time cue through its boundary flux.
    The output is a separately evolved modal field.  No supplied frame is
    mutated and no output is fed back into its source.
    """

    def __init__(
        self,
        frequencies: object,
        *,
        channels: Sequence[InteractionChannel] = DEFAULT_CHANNELS,
        damping: object | None = None,
        initial_amplitudes: object | None = None,
        transfer_maximum: float = 0.35,
        flux_scale: float = 1.0,
    ) -> None:
        frequencies_array = _finite_vector("frequencies", frequencies)
        if damping is None:
            damping = np.zeros_like(frequencies_array)
        self._base_frequencies = np.array(frequencies_array, copy=True)
        self._frequency_scale = 1.0
        self.propagator = ComplexPropagator(frequencies_array, damping)
        self.channels = tuple(channels)
        if not self.channels:
            raise ValueError("at least one interaction channel is required.")
        labels = [channel.label for channel in self.channels]
        if len(set(labels)) != len(labels):
            raise ValueError("interaction channels must use distinct Pauli labels.")
        modes = self.propagator.frequencies.size
        for channel in self.channels:
            if max(*channel.vertex.inputs, *channel.vertex.outputs) >= modes:
                raise ValueError("a vertex refers to a mode outside the propagator.")
        if not math.isfinite(transfer_maximum) or not 0.0 < transfer_maximum <= 1.0:
            raise ValueError("transfer_maximum must be in (0, 1].")
        if not math.isfinite(flux_scale) or flux_scale <= 0.0:
            raise ValueError("flux_scale must be finite and positive.")
        self.transfer_maximum = float(transfer_maximum)
        self.flux_scale = float(flux_scale)
        if initial_amplitudes is None:
            initial_amplitudes = np.zeros(modes, dtype=np.complex128)
        initial = np.asarray(initial_amplitudes, dtype=np.complex128)
        if initial.shape != (modes,) or not np.all(np.isfinite(initial)):
            raise ValueError("initial_amplitudes must be finite and match frequencies.")
        self._amplitudes = np.array(initial, copy=True)
        self._time: float | None = None

    @property
    def amplitudes(self) -> Array:
        """Return a copy of the adapter's current complex modal field."""

        return np.array(self._amplitudes, copy=True)

    @property
    def modes(self) -> int:
        """Number of fixed adapter modal identities."""

        return int(self._amplitudes.size)

    @property
    def frequency_scale(self) -> float:
        """Performance scale for this downstream interaction field only."""

        return self._frequency_scale

    def set_frequency_scale(self, value: float) -> float:
        """Scale interaction-modal frequencies without changing source physics.

        The current complex amplitudes and damping are preserved.  This is an
        adapter-field motion control, not a change to ``rho`` or its Hamiltonian.
        """

        scale = float(value)
        if not math.isfinite(scale) or not 0.1 <= scale <= 8.0:
            raise ValueError("interaction frequency scale must lie in [0.1, 8].")
        self._frequency_scale = scale
        self.propagator = ComplexPropagator(
            self._base_frequencies * scale,
            self.propagator.damping,
        )
        return scale

    def set_process_graph(self, pauli_label: str, graph: ProcessGraph) -> None:
        """Commit a compatible composer graph to one downstream Pauli channel.

        This changes only the declared process topology used by the interaction
        adapter and GUI. It never alters ``rho``, a flow frame, or source-field
        evolution. The graph must retain the channel's external modal arity.
        """

        if not isinstance(graph, ProcessGraph):
            raise ValueError("graph must be a ProcessGraph.")
        for index, channel in enumerate(self.channels):
            if channel.label == pauli_label:
                replacement = InteractionChannel(
                    channel.vertex, scale=channel.scale, phase_offset=channel.phase_offset,
                    process_graph=graph,
                )
                self.channels = self.channels[:index] + (replacement,) + self.channels[index + 1:]
                return
        raise ValueError(f"there is no configured interaction channel for {pauli_label!r}.")

    def _flow_activation(self, flow: object | None, dt: float) -> tuple[float, float]:
        if flow is None:
            return 0.0, 0.0
        boundaries = getattr(flow, "boundary_fluxes", None)
        if boundaries is None:
            raise ValueError("flow must expose the shared boundary_fluxes contract.")
        weights: list[float] = []
        phasors: list[complex] = []
        for boundary in boundaries:
            magnitude = abs(float(boundary.signed_flux))
            if not math.isfinite(magnitude):
                raise ValueError("flow boundary flux must be finite.")
            if magnitude > 0.0:
                weights.append(magnitude)
                phase = getattr(boundary, "phase", None)
                if phase is not None and math.isfinite(float(phase)):
                    phasors.append(magnitude * np.exp(1j * float(phase)))
        total_flux = float(sum(weights))
        strength = 1.0 - math.exp(-(total_flux / self.flux_scale) * dt)
        phase = float(np.angle(sum(phasors))) if phasors else 0.0
        return strength, phase

    def step(
        self,
        rho: object,
        *,
        time: float,
        dt: float,
        flow: object | None = None,
        event_strength: float | None = None,
        external_modal_drive: object | None = None,
        modal_drive_mix: float = 0.0,
    ) -> InteractionFrame:
        """Advance the adapter field one step from an authoritative ``rho``.

        Supply ``flow`` for boundary-flux-derived timing, or a dimensionless
        ``event_strength`` for a controlled test/performance gesture. The two
        controls are mutually exclusive so an event source is always explicit.
        ``external_modal_drive`` is an optional, explicitly downstream complex
        modal observation; it is mixed into this adapter field only and never
        fed back to the observed source.
        """

        if not math.isfinite(time):
            raise ValueError("time must be finite.")
        if self._time is not None and time <= self._time:
            raise ValueError("time must increase between interaction frames.")
        if event_strength is not None and flow is not None:
            raise ValueError("provide either flow or event_strength, not both.")
        if not math.isfinite(modal_drive_mix) or not 0.0 <= modal_drive_mix <= 1.0:
            raise ValueError("modal_drive_mix must be finite and in [0, 1].")
        if event_strength is None:
            strength, flow_phase = self._flow_activation(flow, dt)
        else:
            if not math.isfinite(event_strength) or not 0.0 <= event_strength <= 1.0:
                raise ValueError("event_strength must be finite and in [0, 1].")
            strength, flow_phase = float(event_strength), 0.0
        transfer = self.transfer_maximum * strength
        expectations = pauli_expectations(rho, (channel.label for channel in self.channels))
        couplings = {
            channel.label: complex(channel.scale * expectations[channel.label])
            * np.exp(1j * (channel.phase_offset + flow_phase))
            for channel in self.channels
        }
        propagated = self.propagator.advance(self._amplitudes, dt)
        if external_modal_drive is not None:
            drive = np.asarray(external_modal_drive, dtype=np.complex128)
            if drive.shape != propagated.shape or not np.all(np.isfinite(drive)):
                raise ValueError("external_modal_drive must be finite and match the engine modes.")
            propagated = ((1.0 - modal_drive_mix) * propagated) + (modal_drive_mix * drive)
        propagated_excitation = float(np.vdot(propagated, propagated).real)
        accumulator = AmplitudeAccumulator(propagated.size)
        paths: list[ProcessPath] = []
        if transfer > 0.0:
            for channel in self.channels:
                vertex = channel.vertex
                incident = sum(propagated[index] for index in vertex.inputs) / math.sqrt(len(vertex.inputs))
                amplitude = transfer * couplings[channel.label] * incident
                outputs = tuple(amplitude / math.sqrt(len(vertex.outputs)) for _ in vertex.outputs)
                # A path becomes visible only when its coherent amplitude is
                # nonzero. This keeps the diagram an observation of committed
                # interaction activity, not a catalogue of dormant rules.
                if abs(amplitude) > EPS:
                    accumulator.add(vertex.outputs, outputs)
                    paths.append(ProcessPath(channel.label, vertex, amplitude, outputs, channel.process_graph))
        alternatives = accumulator.result()
        if paths:
            # The coherent sum happens in ``alternatives``.  Normalising only
            # after that sum makes the vertex a redistribution of the existing
            # modal energy (after physical adapter damping), not an energy pump.
            candidate = ((1.0 - transfer) * propagated) + alternatives
            candidate_excitation = float(np.vdot(candidate, candidate).real)
            if candidate_excitation > EPS and propagated_excitation > EPS:
                candidate *= math.sqrt(propagated_excitation / candidate_excitation)
            else:
                candidate = propagated
        else:
            candidate = propagated
        previous_excitation = np.abs(self._amplitudes) ** 2
        excitation = np.abs(candidate) ** 2
        modal = ModalField(
            amplitudes=np.array(candidate, copy=True),
            magnitudes=np.array(np.abs(candidate), copy=True),
            phases=np.array(np.angle(candidate), copy=True),
            excitation=np.array(excitation, copy=True),
            transfer_flux=np.array((excitation - previous_excitation) / dt, copy=True),
        )
        self._amplitudes = np.array(candidate, copy=True)
        self._time = float(time)
        return InteractionFrame(
            time=float(time), pauli_expectations=dict(expectations), couplings=dict(couplings),
            flow_strength=strength, flow_phase=flow_phase, paths=tuple(paths),
            modal_field=modal, propagated_excitation=propagated_excitation,
            modal_excitation=float(np.sum(excitation)),
        )


class InteractionOSCPublisher:
    """Atomic OSC publisher for a downstream renderer; it sends no state back."""

    def __init__(self, client: object | None = None, *, host: str = "127.0.0.1", port: int = OUTPUT_PORT) -> None:
        if client is None:
            from pythonosc.udp_client import SimpleUDPClient

            client = SimpleUDPClient(host, int(port))
        self.client = client
        self.revision = 0

    def publish(self, frame: InteractionFrame) -> int:
        self.revision += 1
        revision = self.revision
        field = frame.modal_field
        self.client.send_message(f"{OSC_ROOT}/frame/begin", [revision, frame.time, SCHEMA, int(field.amplitudes.size)])
        for index, (label, expectation) in enumerate(frame.pauli_expectations.items()):
            coupling = frame.couplings[label]
            self.client.send_message(
                f"{OSC_ROOT}/channel",
                [revision, index, label, expectation, coupling.real, coupling.imag],
            )
        for index, path in enumerate(frame.paths):
            # The variable tail is intentionally self-describing, keeping the
            # OSC view independent of a fixed 1->2 or 2->2 topology.
            self.client.send_message(
                f"{OSC_ROOT}/path",
                [
                    revision, index, path.channel, path.vertex.kind,
                    path.amplitude.real, path.amplitude.imag,
                    len(path.vertex.inputs), len(path.vertex.outputs),
                    *path.vertex.inputs, *path.vertex.outputs,
                    "" if path.graph is None else path.graph.identifier,
                    -1 if path.graph is None else path.graph.loop_order,
                ],
            )
        for mode in range(field.amplitudes.size):
            self.client.send_message(
                f"{OSC_ROOT}/modal",
                [revision, mode, field.magnitudes[mode], field.phases[mode], field.excitation[mode], field.transfer_flux[mode]],
            )
        self.client.send_message(
            f"{OSC_ROOT}/global",
            [revision, frame.flow_strength, frame.flow_phase, frame.propagated_excitation, frame.modal_excitation, len(frame.paths)],
        )
        self.client.send_message(f"{OSC_ROOT}/frame/end", revision)
        return revision


__all__ = [
    "AmplitudeAccumulator", "ComplexPropagator", "DEFAULT_CHANNELS", "InteractionChannel",
    "InteractionEngine", "InteractionFrame", "InteractionOSCPublisher", "InteractionVertex",
    "ModalField", "OSC_ROOT", "OUTPUT_PORT", "ProcessPath", "SCHEMA", "pauli_expectations",
    "pauli_operator",
]
