"""Registry-driven live transform service for the integrated v5 instrument."""

from __future__ import annotations

import threading
import time
from dataclasses import asdict, dataclass
from typing import Any

import numpy as np
from pythonosc import dispatcher, osc_server
from pythonosc.udp_client import SimpleUDPClient

from full4q_tomography_v1.osc_service import TomographyOSCPublisher
from qmw_representation_laboratory_v4.core import (
    DEFAULT_TRANSFORMS,
    RepresentationExperiment,
    SamplingPolicy,
    density_from_preset,
)
from qmw_representation_laboratory_v4.observables import pauli_expectations
from qmw_representation_laboratory_v4.protocols import FullPauliTomography
from qmw_representation_laboratory_v4.transforms import (
    EpistropheBasis,
    FloquetOperator,
    GraphLaplacianBasis,
    GroverAmplifiedBasis,
    HamiltonianBasisTracker,
    IsingHamiltonianSpec,
    complete_graph_adjacency,
    cycle_graph_adjacency,
    path_graph_adjacency,
)


CONTROL_ROOT = "/qmw/v5/transform"
PREVIEW_ROOT = "/qmw/v5/preview"
TRANSFORM_NAMES = DEFAULT_TRANSFORMS.names()


@dataclass(frozen=True)
class RepresentationLiveConfig:
    transform: str = "hamiltonian"
    coupling: float = 0.7
    transverse_field: float = 0.45
    longitudinal_field: float = 0.13
    evolution_time: float = 1.0
    boundary: str = "open"
    preset: str = "ghz"
    shots: int = 256
    sampling: str = "fixed"
    seed: int = 23
    graph: str = "cycle"
    normalized_graph: bool = False
    marked_state: int = 0
    steps: int = 1

    def validate(self) -> "RepresentationLiveConfig":
        if self.transform not in TRANSFORM_NAMES:
            raise ValueError(
                f"unknown transform {self.transform!r}; "
                f"choices: {', '.join(TRANSFORM_NAMES)}"
            )
        if self.boundary not in {"open", "periodic"}:
            raise ValueError("boundary must be open or periodic")
        if self.preset not in {"bell", "ghz", "weave"}:
            raise ValueError("preset must be bell, ghz, or weave")
        if self.sampling not in {"fixed", "resample", "sequence"}:
            raise ValueError("sampling must be fixed, resample, or sequence")
        if self.graph not in {"cycle", "path", "complete"}:
            raise ValueError("graph must be cycle, path, or complete")
        if self.shots <= 0:
            raise ValueError("shots must be positive")
        if not 0 <= self.marked_state < 16:
            raise ValueError("marked_state must be between 0 and 15")
        if self.steps < 0:
            raise ValueError("steps must not be negative")
        for field in (
            "coupling",
            "transverse_field",
            "longitudinal_field",
            "evolution_time",
        ):
            if not np.isfinite(getattr(self, field)):
                raise ValueError(f"{field} must be finite")
        return self

    def hamiltonian_spec(self) -> IsingHamiltonianSpec:
        return IsingHamiltonianSpec(
            coupling=self.coupling,
            transverse_field=self.transverse_field,
            longitudinal_field=self.longitudinal_field,
            boundary=self.boundary,
        )

    def metadata(self) -> dict[str, Any]:
        return asdict(self)


class RepresentationTransformFactory:
    def __init__(self) -> None:
        self.hamiltonian_tracker = HamiltonianBasisTracker()

    def reset_tracking(self) -> None:
        self.hamiltonian_tracker.reset()

    def build(
        self,
        config: RepresentationLiveConfig,
    ) -> tuple[Any, np.ndarray, str, dict[str, Any]]:
        name = config.transform
        tracking = {
            "tracking_applied": False,
            "minimum_matched_overlap": 1.0,
            "minimum_level_gap": 0.0,
        }
        if name == "hamiltonian":
            basis, tracking = self.hamiltonian_tracker.solve(
                config.hamiltonian_spec().matrix()
            )
            return basis, basis.eigenvalues, "energy", tracking
        if name == "floquet":
            hamiltonian = config.hamiltonian_spec().matrix()
            transform = FloquetOperator.from_hamiltonian(
                hamiltonian,
                period=config.evolution_time,
                steps=config.steps,
            )
            values = np.linalg.eigvalsh(hamiltonian)
            tracking["minimum_level_gap"] = _minimum_gap(values)
            return transform, values, "energy", tracking
        if name == "graph_laplacian":
            adjacency = {
                "cycle": cycle_graph_adjacency,
                "path": path_graph_adjacency,
                "complete": complete_graph_adjacency,
            }[config.graph](16)
            transform = GraphLaplacianBasis(
                adjacency,
                normalized=config.normalized_graph,
                graph_name=f"{config.graph}_16",
            )
            values = transform.eigenvalues
            tracking["minimum_level_gap"] = _minimum_gap(values)
            return transform, values, "graph_laplacian", tracking
        if name == "grover_amplified":
            transform = GroverAmplifiedBasis(
                [config.marked_state],
                iterations=config.steps,
            )
        elif name == "epistrophe":
            shift = np.roll(np.eye(16, dtype=complex), 1, axis=0)
            transform = EpistropheBasis(
                shift,
                returns=config.steps,
                definition="cyclic_shift_demo",
            )
        else:
            transform = DEFAULT_TRANSFORMS.create(name)
        eigenphases = np.sort(
            np.angle(np.linalg.eigvals(transform.checked_unitary(16)))
        )
        tracking["minimum_level_gap"] = _minimum_gap(eigenphases)
        return transform, eigenphases, "unitary_phase", tracking


def _minimum_gap(values: np.ndarray) -> float:
    ordered = np.sort(np.asarray(values, dtype=float))
    return float(np.min(np.abs(np.diff(ordered)))) if len(ordered) > 1 else 0.0


class RepresentationV5Publisher:
    def __init__(
        self,
        host: str,
        port: int,
        *,
        packet_delay_ms: float = 1.0,
    ) -> None:
        self.client = SimpleUDPClient(host, port)
        self.packet_delay = max(0.0, packet_delay_ms) / 1000.0
        self.tomography = TomographyOSCPublisher(
            host,
            port,
            packet_delay_ms,
        )

    def _send(self, address: str, payload: list[Any]) -> None:
        self.client.send_message(address, payload)
        if self.packet_delay:
            time.sleep(self.packet_delay)

    def status(self, *payload: Any) -> None:
        self._send(f"{CONTROL_ROOT}/status", list(payload))

    def error(self, message: str) -> None:
        self._send(f"{CONTROL_ROOT}/error", [message])

    def preview(
        self,
        *,
        revision: int,
        config: RepresentationLiveConfig,
        spectrum: np.ndarray,
        spectrum_kind: str,
        reference: dict[str, float],
        experimental: dict[str, float],
        density_distance: float,
        tracking: dict[str, Any],
    ) -> None:
        labels = [label for label in reference if label != "IIII"]
        deltas = np.asarray(
            [experimental[label] - reference[label] for label in labels],
            dtype=float,
        )
        self._send(
            f"{PREVIEW_ROOT}/begin",
            [
                revision,
                config.transform,
                config.preset,
                spectrum_kind,
                len(labels),
                len(spectrum),
            ],
        )
        for index, value in enumerate(spectrum):
            self._send(
                f"{PREVIEW_ROOT}/spectrum",
                [revision, index, float(value)],
            )
        for index, label in enumerate(labels):
            left = reference[label]
            right = experimental[label]
            self._send(
                f"{PREVIEW_ROOT}/pauli",
                [
                    revision,
                    index,
                    label,
                    sum(axis != "I" for axis in label),
                    left,
                    right,
                    right - left,
                ],
            )
        self._send(
            f"{PREVIEW_ROOT}/metrics",
            [
                revision,
                density_distance,
                float(np.sqrt(np.mean(deltas**2))),
                float(np.max(np.abs(deltas))),
                float(tracking["minimum_level_gap"]),
                float(tracking["minimum_matched_overlap"]),
                int(bool(tracking["tracking_applied"])),
            ],
        )
        self._send(
            f"{PREVIEW_ROOT}/end",
            [revision, len(labels), len(spectrum)],
        )


class RepresentationV5OSCService:
    def __init__(
        self,
        *,
        control_host: str = "127.0.0.1",
        control_port: int = 7445,
        output_host: str = "127.0.0.1",
        output_port: int = 7436,
        packet_delay_ms: float = 1.0,
        config: RepresentationLiveConfig | None = None,
    ) -> None:
        self.config = (config or RepresentationLiveConfig()).validate()
        self.factory = RepresentationTransformFactory()
        self.publisher = RepresentationV5Publisher(
            output_host,
            output_port,
            packet_delay_ms=packet_delay_ms,
        )
        self._lock = threading.Lock()
        self._revision = int(time.time() * 1000) % 1_000_000_000
        self._sequence_seed = self.config.seed
        self._sequence_policy = SamplingPolicy.sequence(self.config.seed)
        routes = dispatcher.Dispatcher()
        routes.map(f"{CONTROL_ROOT}/preview", self._handle_preview)
        routes.map(f"{CONTROL_ROOT}/commit", self._handle_commit)
        routes.map(f"{CONTROL_ROOT}/ping", self._handle_ping)
        routes.map(f"{CONTROL_ROOT}/reset_tracking", self._handle_reset)
        self.server = osc_server.ThreadingOSCUDPServer(
            (control_host, control_port),
            routes,
        )

    def _next_revision(self) -> int:
        self._revision = (self._revision + 1) % 1_000_000_000
        return self._revision

    def _parse(self, args: tuple[Any, ...]) -> tuple[int, RepresentationLiveConfig]:
        current = self.config
        revision = int(args[0]) if args else self._next_revision()
        if revision <= 0:
            revision = self._next_revision()
        config = RepresentationLiveConfig(
            transform=str(args[1]) if len(args) > 1 else current.transform,
            coupling=float(args[2]) if len(args) > 2 else current.coupling,
            transverse_field=(
                float(args[3]) if len(args) > 3 else current.transverse_field
            ),
            longitudinal_field=(
                float(args[4]) if len(args) > 4 else current.longitudinal_field
            ),
            evolution_time=(
                float(args[5]) if len(args) > 5 else current.evolution_time
            ),
            boundary=str(args[6]) if len(args) > 6 else current.boundary,
            preset=str(args[7]) if len(args) > 7 else current.preset,
            shots=int(args[8]) if len(args) > 8 else current.shots,
            sampling=str(args[9]) if len(args) > 9 else current.sampling,
            seed=int(args[10]) if len(args) > 10 else current.seed,
            graph=str(args[11]) if len(args) > 11 else current.graph,
            normalized_graph=(
                bool(int(args[12]))
                if len(args) > 12
                else current.normalized_graph
            ),
            marked_state=(
                int(args[13]) if len(args) > 13 else current.marked_state
            ),
            steps=int(args[14]) if len(args) > 14 else current.steps,
        ).validate()
        return revision, config

    def _policy(self, config: RepresentationLiveConfig) -> SamplingPolicy:
        if config.sampling == "resample":
            return SamplingPolicy.resample()
        if config.sampling == "sequence":
            if config.seed != self._sequence_seed:
                self._sequence_seed = config.seed
                self._sequence_policy = SamplingPolicy.sequence(config.seed)
            return self._sequence_policy
        return SamplingPolicy.fixed(config.seed)

    def request(self, action: str, revision: int, config: RepresentationLiveConfig) -> bool:
        if self._lock.locked():
            self.publisher.status("busy", action, revision)
            return False
        target = self._preview if action == "preview" else self._commit
        threading.Thread(
            target=target,
            args=(revision, config),
            daemon=True,
        ).start()
        return True

    def _preview(self, revision: int, config: RepresentationLiveConfig) -> None:
        with self._lock:
            try:
                transform, spectrum, kind, tracking = self.factory.build(config)
                reference_density = density_from_preset(config.preset)
                experimental_density = transform.apply(reference_density)
                reference = pauli_expectations(reference_density)
                experimental = pauli_expectations(experimental_density)
                labels = [label for label in reference if label != "IIII"]
                deltas = np.asarray(
                    [
                        experimental[label] - reference[label]
                        for label in labels
                    ],
                    dtype=float,
                )
                density_distance = float(
                    np.linalg.norm(experimental_density - reference_density)
                )
                self.publisher.preview(
                    revision=revision,
                    config=config,
                    spectrum=spectrum,
                    spectrum_kind=kind,
                    reference=reference,
                    experimental=experimental,
                    density_distance=density_distance,
                    tracking=tracking,
                )
                self.config = config
                self.publisher.status(
                    "preview_complete",
                    revision,
                    config.transform,
                    "density_l2",
                    density_distance,
                    "pauli_rms",
                    float(np.sqrt(np.mean(deltas**2))),
                    "pauli_max",
                    float(np.max(np.abs(deltas))),
                )
            except Exception as exc:
                self.publisher.error(f"preview failed: {exc}")

    def _commit(self, revision: int, config: RepresentationLiveConfig) -> None:
        with self._lock:
            try:
                transform, _spectrum, _kind, _tracking = self.factory.build(
                    config
                )
                result = RepresentationExperiment(
                    experimental=transform,
                    measurement=FullPauliTomography(
                        sampling=self._policy(config)
                    ),
                ).run(
                    preset=config.preset,
                    shots=config.shots,
                    seed=(
                        None
                        if config.sampling == "resample"
                        else config.seed
                    ),
                )
                base = (revision * 2) % 2_000_000_000
                self.publisher.tomography.publish(result.reference_output, base)
                self.publisher.tomography.publish(
                    result.experimental_output,
                    base + 1,
                )
                self.config = config
                self.publisher.status(
                    "commit_complete",
                    revision,
                    config.transform,
                    result.seed,
                    base,
                    base + 1,
                )
            except Exception as exc:
                self.publisher.error(f"commit failed: {exc}")

    def _handle_preview(self, _address: str, *args: Any) -> None:
        try:
            self.request("preview", *self._parse(args))
        except Exception as exc:
            self.publisher.error(f"invalid preview: {exc}")

    def _handle_commit(self, _address: str, *args: Any) -> None:
        try:
            self.request("commit", *self._parse(args))
        except Exception as exc:
            self.publisher.error(f"invalid commit: {exc}")

    def _handle_ping(self, _address: str, *_args: Any) -> None:
        self.publisher.status("ready", *self.config.metadata().values())

    def _handle_reset(self, _address: str, *_args: Any) -> None:
        self.factory.reset_tracking()
        self.publisher.status("tracking_reset")

    def serve_forever(self) -> None:
        self.publisher.status("ready", *self.config.metadata().values())
        self.server.serve_forever()

    def shutdown(self) -> None:
        self.server.shutdown()
        self.server.server_close()
