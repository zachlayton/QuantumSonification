"""Renderer-neutral CPS-shell adapter for QMW statevectors and density states."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
import math
from typing import Any, Iterable, Protocol, Sequence

import numpy as np

from .cps import CombinationProductSet
from .perception import harmonic_intersection


class OSCClient(Protocol):
    def send_message(self, address: str, value: Any) -> None: ...


@dataclass(frozen=True)
class WilsonAdapterConfig:
    factors: tuple[int, ...] = (1, 3, 5, 7)
    grade: int = 2
    fundamental_hz: float = 220.0
    attack_ms: float = 80.0
    persistence_ms: float = 900.0
    phase_coherence_floor: float = 1e-6

    def __post_init__(self) -> None:
        if self.fundamental_hz <= 0.0 or not math.isfinite(self.fundamental_hz):
            raise ValueError("fundamental_hz must be finite and positive")
        if self.attack_ms <= 0.0 or self.persistence_ms <= 0.0:
            raise ValueError("attack and persistence times must be positive")
        if not 0.0 <= self.phase_coherence_floor <= 1.0:
            raise ValueError("phase_coherence_floor must lie in [0, 1]")


@dataclass(frozen=True)
class WilsonVertexFrame:
    index: int
    bitmask: int
    factors: tuple[int, ...]
    complement_index: int | None
    ratio_numerator: int
    ratio_denominator: int
    frequency_hz: float
    absolute_probability: float
    conditional_probability: float
    activation: float
    relative_phase: float
    phase_coherence: float

    def packet(self, revision: int) -> list[int | float | str]:
        return [
            int(revision),
            self.index,
            self.bitmask,
            ",".join(str(value) for value in self.factors),
            self.ratio_numerator,
            self.ratio_denominator,
            self.frequency_hz,
            self.absolute_probability,
            self.conditional_probability,
            self.activation,
            self.relative_phase,
            self.phase_coherence,
            -1 if self.complement_index is None else self.complement_index,
        ]


@dataclass(frozen=True)
class WilsonCPSFrame:
    revision: int
    time: float
    dt: float
    shell_probability: float
    leakage_probability: float
    conditional_shell_purity: float
    reference_vertex: int | None
    vertices: tuple[WilsonVertexFrame, ...]

    def packet(self) -> list[int | float]:
        return [
            self.revision,
            self.time,
            self.dt,
            self.shell_probability,
            self.leakage_probability,
            self.conditional_shell_purity,
            -1 if self.reference_vertex is None else self.reference_vertex,
            len(self.vertices),
        ]


class WilsonStateAdapter:
    """Project quantum state into a CPS shell while retaining auditory memory.

    Density-matrix phase is measured from ``rho[i, reference]``.  For a pure
    state this equals the relative statevector phase.  For mixed states its
    normalized magnitude is published independently as phase coherence, so an
    incoherent mixture is never represented as a coherent chord.
    """

    def __init__(self, config: WilsonAdapterConfig = WilsonAdapterConfig()) -> None:
        self.config = config
        self.cps = CombinationProductSet(config.factors, config.grade)
        self._activation = np.zeros(self.cps.dimension, dtype=np.float64)
        self._phase_memory = np.ones(self.cps.dimension, dtype=np.complex128)
        self._revision = 0

    def reset(self) -> None:
        self._activation.fill(0.0)
        self._phase_memory.fill(1.0 + 0.0j)
        self._revision = 0

    def adapt_statevector(
        self,
        amplitudes: Sequence[complex],
        *,
        time: float,
        dt: float,
        revision: int | None = None,
    ) -> WilsonCPSFrame:
        vector = np.asarray(amplitudes, dtype=np.complex128)
        expected = 1 << len(self.config.factors)
        if vector.shape != (expected,):
            raise ValueError(f"statevector must have shape ({expected},)")
        norm = float(np.vdot(vector, vector).real)
        if not np.isclose(norm, 1.0, atol=1e-8):
            raise ValueError("statevector must have unit norm")
        return self.adapt_density_matrix(
            np.outer(vector, vector.conj()),
            time=time,
            dt=dt,
            revision=revision,
        )

    def adapt_quantum_frame(
        self,
        frame: Any,
        *,
        revision: int | None = None,
    ) -> WilsonCPSFrame:
        """Accept QMW's canonical ``QuantumStateFrame`` by structural contract."""
        return self.adapt_density_matrix(
            frame.rho,
            time=float(frame.t),
            dt=float(frame.dt),
            revision=revision,
        )

    def adapt_density_matrix(
        self,
        rho: Any,
        *,
        time: float,
        dt: float,
        revision: int | None = None,
    ) -> WilsonCPSFrame:
        matrix = self._validate_density_matrix(rho)
        time = float(time)
        dt = float(dt)
        if not math.isfinite(time):
            raise ValueError("time must be finite")
        if not math.isfinite(dt) or dt <= 0.0:
            raise ValueError("dt must be finite and positive")
        if revision is None:
            self._revision += 1
        else:
            requested = int(revision)
            if requested <= self._revision:
                raise ValueError("revision must increase monotonically")
            self._revision = requested

        masks = np.asarray([tone.bitmask for tone in self.cps.tones], dtype=np.int64)
        block = matrix[np.ix_(masks, masks)]
        populations = np.maximum(np.real(np.diag(block)), 0.0)
        shell_probability = float(np.sum(populations))
        conditional = (
            populations / shell_probability
            if shell_probability > 1e-15
            else np.zeros_like(populations)
        )
        conditional_purity = (
            float(np.real(np.trace(block @ block))) / (shell_probability**2)
            if shell_probability > 1e-15
            else 0.0
        )
        reference = int(np.argmax(populations)) if shell_probability > 1e-15 else None

        phases = np.zeros(self.cps.dimension, dtype=np.float64)
        coherences = np.zeros(self.cps.dimension, dtype=np.float64)
        if reference is not None and populations[reference] > 1e-15:
            reference_population = populations[reference]
            for index, population in enumerate(populations):
                coherence = block[index, reference]
                denominator = math.sqrt(max(population * reference_population, 0.0))
                if denominator > 1e-15:
                    coherences[index] = float(np.clip(abs(coherence) / denominator, 0.0, 1.0))
                if abs(coherence) > 1e-15:
                    phases[index] = float(np.angle(coherence))

        target_activation = np.sqrt(populations)
        for index, target in enumerate(target_activation):
            tau_ms = (
                self.config.attack_ms
                if target >= self._activation[index]
                else self.config.persistence_ms
            )
            coefficient = math.exp(-dt / (tau_ms * 0.001))
            self._activation[index] = target + coefficient * (
                self._activation[index] - target
            )
            if coherences[index] >= self.config.phase_coherence_floor:
                target_phase = np.exp(1j * phases[index])
                phase_blend = 1.0 - coefficient
                blended = (
                    (1.0 - phase_blend) * self._phase_memory[index]
                    + phase_blend * target_phase
                )
                if abs(blended) > 1e-15:
                    self._phase_memory[index] = blended / abs(blended)

        vertices = tuple(
            WilsonVertexFrame(
                index=tone.index,
                bitmask=tone.bitmask,
                factors=tone.factors,
                complement_index=tone.complement_index,
                ratio_numerator=tone.ratio_numerator,
                ratio_denominator=tone.ratio_denominator,
                frequency_hz=self.config.fundamental_hz * tone.ratio,
                absolute_probability=float(populations[tone.index]),
                conditional_probability=float(conditional[tone.index]),
                activation=float(self._activation[tone.index]),
                relative_phase=float(np.angle(self._phase_memory[tone.index])),
                phase_coherence=float(coherences[tone.index]),
            )
            for tone in self.cps.tones
        )
        return WilsonCPSFrame(
            revision=self._revision,
            time=time,
            dt=dt,
            shell_probability=float(np.clip(shell_probability, 0.0, 1.0)),
            leakage_probability=float(np.clip(1.0 - shell_probability, 0.0, 1.0)),
            conditional_shell_purity=float(np.clip(conditional_purity, 0.0, 1.0)),
            reference_vertex=reference,
            vertices=vertices,
        )

    def edge_packets(self, revision: int) -> tuple[list[int | float], ...]:
        packets = []
        for edge in self.cps.perceptual_edges():
            interval = Fraction(edge.interval_numerator, edge.interval_denominator)
            intersection = harmonic_intersection(interval)
            coupling = intersection / (1.0 + edge.harmonic_distance)
            packets.append(
                [
                    int(revision),
                    edge.source,
                    edge.target,
                    edge.interval_numerator,
                    edge.interval_denominator,
                    edge.harmonic_distance,
                    intersection,
                    coupling,
                ]
            )
        return tuple(packets)

    def _validate_density_matrix(self, rho: Any) -> np.ndarray:
        matrix = np.asarray(rho, dtype=np.complex128)
        expected = 1 << len(self.config.factors)
        if matrix.shape != (expected, expected):
            raise ValueError(f"density matrix must have shape ({expected}, {expected})")
        if not np.all(np.isfinite(matrix)):
            raise ValueError("density matrix entries must be finite")
        if not np.allclose(matrix, matrix.conj().T, atol=1e-9):
            raise ValueError("density matrix must be Hermitian")
        trace = complex(np.trace(matrix))
        if abs(trace.imag) > 1e-9 or not np.isclose(trace.real, 1.0, atol=1e-8):
            raise ValueError("density matrix must have unit trace")
        if float(np.min(np.linalg.eigvalsh(matrix))) < -1e-9:
            raise ValueError("density matrix must be positive semidefinite")
        return matrix


class WilsonOSCPublisher:
    """Publish a stable CPS contract to any Max/SC/geometry OSC clients."""

    PREFIX = "/qmw/wilson/cps"

    def __init__(
        self,
        adapter: WilsonStateAdapter,
        clients: Iterable[OSCClient] = (),
    ) -> None:
        self.adapter = adapter
        self.clients = tuple(client for client in clients if client is not None)
        self._definition_revision: int | None = None

    def reset_topology(self) -> None:
        """Force topology resend after the source/adapter is reset."""
        self._definition_revision = None

    def _send(self, suffix: str, value: Any) -> None:
        for client in self.clients:
            client.send_message(f"{self.PREFIX}/{suffix}", value)

    def publish(self, frame: WilsonCPSFrame) -> None:
        if self._definition_revision is None:
            self._send(
                "definition",
                [
                    frame.revision,
                    self.adapter.cps.grade,
                    len(self.adapter.cps.factors),
                    ",".join(str(value) for value in self.adapter.cps.factors),
                    self.adapter.cps.dimension,
                    self.adapter.config.fundamental_hz,
                ],
            )
            for packet in self.adapter.edge_packets(frame.revision):
                self._send("edge", packet)
            self._definition_revision = frame.revision
        self._send("frame", frame.packet())
        for vertex in frame.vertices:
            self._send("vertex", vertex.packet(frame.revision))
        self._send("end", [frame.revision, len(frame.vertices)])

    def publish_measurement(
        self,
        *,
        revision: int,
        basis_index: int,
        probability: float,
    ) -> None:
        tone = next(
            (tone for tone in self.adapter.cps.tones if tone.bitmask == int(basis_index)),
            None,
        )
        self._send(
            "measurement",
            [
                int(revision),
                int(basis_index),
                -1 if tone is None else tone.index,
                float(probability),
                int(tone is not None),
            ],
        )

    def publish_flow(
        self,
        *,
        revision: int,
        generation: int,
        source_basis_index: int,
        destination_basis_index: int,
        absolute_flow: float,
        conditional_flow: float,
        theta: float,
        beta: float,
        relative_phase: float,
    ) -> None:
        by_mask = {tone.bitmask: tone.index for tone in self.adapter.cps.tones}
        source_vertex = by_mask.get(int(source_basis_index), -1)
        destination_vertex = by_mask.get(int(destination_basis_index), -1)
        self._send(
            "flow",
            [
                int(revision),
                int(generation),
                source_vertex,
                destination_vertex,
                int(source_basis_index),
                int(destination_basis_index),
                float(absolute_flow),
                float(conditional_flow),
                float(theta),
                float(beta),
                float(relative_phase),
            ],
        )


__all__ = [
    "WilsonAdapterConfig",
    "WilsonCPSFrame",
    "WilsonOSCPublisher",
    "WilsonStateAdapter",
    "WilsonVertexFrame",
]
