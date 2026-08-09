#!/usr/bin/env python3
"""Batch salient GRW transitions into slow living-geometry revisions.

This module is deliberately a bridge between two existing authorities:

* GRW remains owned by the four-qubit density engine.
* Mesh, spectrum, acoustic IR generation, and IR activation remain owned by
  ``LivingSpectralGeometry`` and ``LivingSpectralGeometryOSCPublisher``.

No geometry is rebuilt in an OSC callback.  Hits accumulate until a bounded
batch is due; one developmental perturbation then schedules one asynchronous
living-geometry revision.  The existing publisher stages its IR as an inactive
candidate and activates it only through ready/crossfade/committed handshakes.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import argparse
import json
import math
import queue
import signal
import threading
import time
from typing import Any, Callable

import numpy as np
from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import ThreadingOSCUDPServer
from pythonosc.udp_client import SimpleUDPClient

from eigenfield_timing_layer_v1 import compare_grw_eigenfields
from geometry_acoustics_bridge_v2 import AcousticBridgeConfig
from operators.living_spectral_geometry_osc_v1 import (
    LivingOSCConfig,
    LivingSpectralGeometryOSCPublisher,
)
from operators.living_spectral_geometry_v1 import (
    LivingSpectralConfig,
    LivingSpectralGeometry,
    LivingSpectralState,
)
from operators.spectral_geometry_v1 import SpectralGeometryConfig
from quantum_eigenfield_engine_v1 import (
    QuantumEigenfieldConfig,
    density_descriptors,
    pauli_expectations,
    validate_density_matrix,
)
from surface_material_models_v1 import SurfaceMaterialConfig


@dataclass(frozen=True)
class GRWGeometryConfig:
    salience_floor: float = 0.002
    batch_salience_threshold: float = 0.12
    minimum_batch_events: int = 2
    maximum_batch_events: int = 32
    maximum_batch_latency_seconds: float = 12.0
    regeneration_interval_seconds: float = 30.0
    perturbation_gain: float = 0.012
    maximum_displacement: float = 0.08
    developmental_persistence: float = 0.82
    smoothing_iterations: int = 3

    def __post_init__(self) -> None:
        if self.salience_floor < 0.0 or self.batch_salience_threshold < 0.0:
            raise ValueError("salience controls must be non-negative")
        if self.minimum_batch_events < 1:
            raise ValueError("minimum_batch_events must be positive")
        if self.maximum_batch_events < self.minimum_batch_events:
            raise ValueError("maximum_batch_events must not be smaller than minimum")
        if self.maximum_batch_latency_seconds <= 0.0:
            raise ValueError("maximum_batch_latency_seconds must be positive")
        if self.regeneration_interval_seconds < 0.0:
            raise ValueError("regeneration_interval_seconds must be non-negative")
        if self.perturbation_gain < 0.0 or self.maximum_displacement < 0.0:
            raise ValueError("displacement controls must be non-negative")
        if not 0.0 <= self.developmental_persistence < 1.0:
            raise ValueError("developmental_persistence must lie in [0, 1)")
        if self.smoothing_iterations < 0:
            raise ValueError("smoothing_iterations must be non-negative")


@dataclass(frozen=True)
class GeometryGRWEvent:
    event_id: int
    salience: float
    branch: int
    audible: bool
    rho_after: np.ndarray
    delta_rho: np.ndarray
    received_time: float


@dataclass(frozen=True)
class GRWGeometryBatch:
    batch_id: int
    event_ids: tuple[int, ...]
    event_count: int
    accumulated_salience: float
    strongest_mode: int
    strongest_mode_gain: float
    total_variation: float
    scheduled_revision: int | None
    displacement_rms: float
    displacement_peak: float


@dataclass(frozen=True)
class GeometryModalComparison:
    pre_probabilities: np.ndarray
    post_probabilities: np.ndarray
    probability_delta: np.ndarray
    strongest_mode: int
    strengthening: float
    total_variation: float


@dataclass(frozen=True)
class GeometryProjection:
    geometric_eigenvectors: np.ndarray
    channel_isometry: np.ndarray | None = None
    environment_dimension: int = 1
    coupling_matrix: np.ndarray | None = None
    temperature: float = 1.0
    purity_sharpness: float = 1.0
    entropy_spread: float = 1.0

    @property
    def mode_count(self) -> int:
        return int(self.geometric_eigenvectors.shape[1])

    @classmethod
    def from_quantum_npz(cls, path: str | Path) -> "GeometryProjection":
        source = Path(path)
        with np.load(source, allow_pickle=False) as payload:
            required = {"geometric_eigenvectors"}
            missing = required.difference(payload.files)
            if missing:
                raise ValueError(
                    f"quantum eigenfield state missing fields: {sorted(missing)}"
                )
            vectors = np.asarray(
                payload["geometric_eigenvectors"], dtype=np.float64
            )
            isometry = (
                np.asarray(payload["channel_isometry"], dtype=np.complex128)
                if "channel_isometry" in payload.files
                else None
            )
            environment = (
                int(np.asarray(payload["channel_environment_dimension"]).item())
                if "channel_environment_dimension" in payload.files
                else 1
            )
            coupling = (
                np.asarray(payload["coupling_matrix"], dtype=np.float64)
                if "coupling_matrix" in payload.files
                else None
            )
        if vectors.ndim != 2 or vectors.shape[1] < 1:
            raise ValueError("geometric_eigenvectors must be vertices x modes")
        if isometry is not None and isometry.shape[0] != vectors.shape[1] * environment:
            raise ValueError("channel isometry does not match geometric modes")
        if isometry is None and (
            coupling is None or coupling.shape[0] != vectors.shape[1]
        ):
            raise ValueError(
                "legacy eigenfield state requires a mode-aligned coupling_matrix"
            )
        config: dict[str, Any] = {}
        descriptor_path = source.with_suffix(".json")
        if descriptor_path.exists():
            try:
                config = dict(
                    json.loads(descriptor_path.read_text(encoding="utf-8")).get(
                        "config", {}
                    )
                )
            except (OSError, TypeError, ValueError, json.JSONDecodeError):
                config = {}
        return cls(
            vectors,
            isometry,
            environment,
            coupling,
            float(config.get("temperature", 1.0)),
            float(config.get("purity_sharpness", 1.0)),
            float(config.get("entropy_spread", 1.0)),
        )

    def _legacy_probabilities(self, rho: np.ndarray) -> np.ndarray:
        if self.coupling_matrix is None:
            raise ValueError("legacy projection has no coupling matrix")
        state = validate_density_matrix(rho)
        descriptors = density_descriptors(state)
        values = np.sort(np.linalg.eigvalsh(state).real)[::-1]
        entropy_normalized = descriptors.entropy_bits / max(
            descriptors.max_mixed_entropy_bits, 1e-12
        )
        coherence_normalized = descriptors.coherence_l1 / max(
            descriptors.dimension - 1, 1
        )
        features = list(values)
        features.extend(
            [
                descriptors.purity,
                entropy_normalized,
                coherence_normalized,
                descriptors.dominant_population,
            ]
        )
        features.extend(pauli_expectations(state).values())
        vector = np.asarray(features, dtype=np.float64)
        vector /= max(float(np.linalg.norm(vector)), 1e-12)
        if self.coupling_matrix.shape[1] != len(vector):
            raise ValueError("legacy coupling matrix feature count is incompatible")
        temperature = max(
            1e-4,
            self.temperature
            * (1.0 + self.entropy_spread * entropy_normalized)
            / (1.0 + self.purity_sharpness * descriptors.purity),
        )
        logits = self.coupling_matrix @ vector / temperature
        logits -= float(np.max(logits))
        probabilities = np.exp(logits)
        return probabilities / max(float(np.sum(probabilities)), 1e-15)

    def compare(
        self, rho_after: np.ndarray, delta_rho: np.ndarray
    ) -> GeometryModalComparison:
        if self.channel_isometry is not None:
            comparison = compare_grw_eigenfields(
                rho_after,
                delta_rho,
                self.channel_isometry,
                self.environment_dimension,
                self.mode_count,
            )
            return GeometryModalComparison(
                comparison.pre_probabilities,
                comparison.post_probabilities,
                comparison.probability_delta,
                comparison.strongest_mode,
                comparison.strengthening,
                comparison.total_variation,
            )
        after = validate_density_matrix(rho_after)
        before = validate_density_matrix(after - np.asarray(delta_rho))
        pre = self._legacy_probabilities(before)
        post = self._legacy_probabilities(after)
        change = post - pre
        strongest = int(np.argmax(change))
        return GeometryModalComparison(
            pre,
            post,
            change,
            strongest,
            max(0.0, float(change[strongest])),
            float(0.5 * np.sum(np.abs(change))),
        )


class GRWFrameAssembler:
    """Collect the split GRW OSC frame and emit only complete events."""

    MATRIX_FIELDS = {
        "post/rho_real",
        "post/rho_imag",
        "delta/real",
        "delta/imag",
    }

    def __init__(self) -> None:
        self.fields: dict[str, tuple[Any, ...]] = {}

    @staticmethod
    def _matrix(real: tuple[Any, ...], imag: tuple[Any, ...]) -> np.ndarray:
        real_values = np.asarray(real, dtype=np.float64).reshape(-1)
        imag_values = np.asarray(imag, dtype=np.float64).reshape(-1)
        if real_values.size != imag_values.size:
            raise ValueError("GRW real/imaginary matrix lengths differ")
        dimension = int(round(math.sqrt(real_values.size)))
        if dimension * dimension != real_values.size:
            raise ValueError("GRW matrix payload is not square")
        return (real_values + 1j * imag_values).reshape(dimension, dimension)

    def ingest(
        self,
        suffix: str,
        args: tuple[Any, ...],
        *,
        now: float | None = None,
    ) -> GeometryGRWEvent | None:
        if suffix in self.MATRIX_FIELDS:
            self.fields[suffix] = args
            return None
        if suffix != "event":
            return None
        missing = self.MATRIX_FIELDS.difference(self.fields)
        if missing:
            raise ValueError(f"GRW event missing matrix fields: {sorted(missing)}")
        rho_after = self._matrix(
            self.fields["post/rho_real"], self.fields["post/rho_imag"]
        )
        delta_rho = self._matrix(
            self.fields["delta/real"], self.fields["delta/imag"]
        )
        event = GeometryGRWEvent(
            event_id=int(args[0]) if args else 0,
            branch=int(args[1]) if len(args) > 1 else 0,
            salience=float(np.clip(float(args[2]), 0.0, 1.0)) if len(args) > 2 else 0.0,
            audible=bool(int(args[9])) if len(args) > 9 else True,
            rho_after=rho_after,
            delta_rho=delta_rho,
            received_time=time.monotonic() if now is None else float(now),
        )
        self.fields.clear()
        return event


class SalienceBatcher:
    def __init__(
        self,
        config: GRWGeometryConfig,
        *,
        start_time: float | None = None,
    ) -> None:
        self.config = config
        self.pending: list[GeometryGRWEvent] = []
        self.accumulated_salience = 0.0
        self.last_regeneration_time = (
            time.monotonic() if start_time is None else float(start_time)
        )

    def ingest(self, event: GeometryGRWEvent) -> bool:
        if not event.audible or event.salience < self.config.salience_floor:
            return False
        self.pending.append(event)
        self.accumulated_salience += event.salience
        return True

    def ready(self, now: float | None = None) -> bool:
        if not self.pending:
            return False
        current = time.monotonic() if now is None else float(now)
        if current - self.last_regeneration_time < self.config.regeneration_interval_seconds:
            return False
        count = len(self.pending)
        oldest_age = current - self.pending[0].received_time
        threshold_batch = (
            count >= self.config.minimum_batch_events
            and self.accumulated_salience >= self.config.batch_salience_threshold
        )
        return bool(
            threshold_batch
            or count >= self.config.maximum_batch_events
            or oldest_age >= self.config.maximum_batch_latency_seconds
        )

    def take(self, now: float | None = None) -> tuple[GeometryGRWEvent, ...]:
        current = time.monotonic() if now is None else float(now)
        events = tuple(self.pending)
        self.pending.clear()
        self.accumulated_salience = 0.0
        self.last_regeneration_time = current
        return events


def _vertex_normals(vertices: np.ndarray, faces: np.ndarray) -> np.ndarray:
    normals = np.zeros_like(vertices, dtype=np.float64)
    triangles = np.asarray(faces, dtype=np.int64)
    for face in triangles:
        if len(face) < 3:
            continue
        a, b, c = (int(face[0]), int(face[1]), int(face[2]))
        normal = np.cross(vertices[b] - vertices[a], vertices[c] - vertices[a])
        normals[a] += normal
        normals[b] += normal
        normals[c] += normal
    lengths = np.linalg.norm(normals, axis=1)
    fallback = np.array([0.0, 0.0, 1.0])
    normals[lengths <= 1e-15] = fallback
    lengths = np.linalg.norm(normals, axis=1)
    return normals / np.maximum(lengths[:, None], 1e-15)


def _smooth_vertex_field(
    values: np.ndarray,
    faces: np.ndarray,
    iterations: int,
) -> np.ndarray:
    result = np.asarray(values, dtype=np.float64).copy()
    neighbors: list[set[int]] = [set() for _ in range(len(result))]
    for face in np.asarray(faces, dtype=np.int64):
        indices = [int(index) for index in face]
        for index in indices:
            neighbors[index].update(other for other in indices if other != index)
    for _ in range(iterations):
        previous = result.copy()
        for index, adjacent in enumerate(neighbors):
            if adjacent:
                result[index] = 0.55 * previous[index] + 0.45 * float(
                    np.mean(previous[list(adjacent)])
                )
    return result


class GRWDevelopmentalGeometryBridge:
    """Accumulate GRW salience and schedule one living revision per batch."""

    def __init__(
        self,
        living: Any,
        vertices: np.ndarray,
        faces: np.ndarray,
        projection: GeometryProjection,
        config: GRWGeometryConfig = GRWGeometryConfig(),
        *,
        status_client: Any | None = None,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        self.living = living
        self.original_vertices = np.asarray(vertices, dtype=np.float64).copy()
        self.faces = np.asarray(faces, dtype=np.int64).copy()
        self.projection = projection
        self.config = config
        self.status_client = status_client
        self.clock = clock
        if projection.geometric_eigenvectors.shape[0] != len(self.original_vertices):
            raise ValueError("projection vertex count does not match geometry")
        self.batcher = SalienceBatcher(config, start_time=clock())
        self.developmental_field = np.zeros(len(self.original_vertices), dtype=np.float64)
        self.batch_count = 0
        self.last_batch: GRWGeometryBatch | None = None
        self._unsubscribe = None
        if hasattr(living, "subscribe"):
            self._unsubscribe = living.subscribe(self._living_state_changed)

    def _send(self, suffix: str, value: Any) -> None:
        if self.status_client is not None:
            self.status_client.send_message(f"/living/grw/{suffix}", value)

    def _living_state_changed(self, state: LivingSpectralState) -> None:
        path = dict(state.paths).get("quantum_npz")
        if path:
            try:
                projection = GeometryProjection.from_quantum_npz(path)
                if projection.geometric_eigenvectors.shape[0] == len(self.original_vertices):
                    self.projection = projection
            except (OSError, TypeError, ValueError):
                pass

    def ingest(self, event: GeometryGRWEvent) -> bool:
        accepted = self.batcher.ingest(event)
        self._send("pending/events", len(self.batcher.pending))
        self._send("pending/salience", self.batcher.accumulated_salience)
        return accepted

    def poll(self, now: float | None = None) -> GRWGeometryBatch | None:
        current = self.clock() if now is None else float(now)
        if not self.batcher.ready(current):
            return None
        return self._flush(self.batcher.take(current))

    def _flush(
        self, events: tuple[GeometryGRWEvent, ...]
    ) -> GRWGeometryBatch | None:
        if not events:
            return None
        modal_delta = np.zeros(self.projection.mode_count, dtype=np.float64)
        total_variation = 0.0
        total_salience = 0.0
        for event in events:
            comparison = self.projection.compare(
                event.rho_after, event.delta_rho
            )
            modal_delta += event.salience * comparison.probability_delta
            total_variation += event.salience * comparison.total_variation
            total_salience += event.salience
        modal_delta /= max(total_salience, 1e-15)
        total_variation /= max(total_salience, 1e-15)
        strongest_mode = int(np.argmax(modal_delta))
        strongest_gain = max(0.0, float(modal_delta[strongest_mode]))

        strengthened = np.maximum(modal_delta, 0.0)
        if float(np.sum(strengthened)) <= 1e-15:
            return None
        drive = self.projection.geometric_eigenvectors @ strengthened
        drive = _smooth_vertex_field(
            drive, self.faces, self.config.smoothing_iterations
        )
        drive -= float(np.mean(drive))
        peak = float(np.max(np.abs(drive)))
        if peak > 1e-15:
            drive /= peak
        salience_scale = float(np.clip(total_salience, 0.0, 1.0))
        persistence = self.config.developmental_persistence
        self.developmental_field = np.clip(
            persistence * self.developmental_field
            + (1.0 - persistence) * salience_scale * drive,
            -1.0,
            1.0,
        )

        extent = np.ptp(self.original_vertices, axis=0)
        geometry_scale = max(float(np.linalg.norm(extent)), 1e-12)
        maximum = self.config.maximum_displacement * geometry_scale
        scalar_displacement = np.clip(
            self.config.perturbation_gain
            * geometry_scale
            * self.developmental_field,
            -maximum,
            maximum,
        )
        normals = _vertex_normals(self.original_vertices, self.faces)
        vertices = self.original_vertices + normals * scalar_displacement[:, None]

        # Both mutations are staged before the single scheduled geometry
        # invalidation, so one batch produces one mesh/acoustic recomputation.
        self.living.update_quantum_state(
            events[-1].rho_after,
            schedule=False,
            reason="GRW geometry batch quantum state",
        )
        revision = self.living.update_geometry(
            vertices,
            self.faces,
            schedule=True,
            reason=(
                f"GRW developmental batch {self.batch_count + 1}: "
                f"{len(events)} events, salience {total_salience:.6f}"
            ),
        )
        self.batch_count += 1
        batch = GRWGeometryBatch(
            batch_id=self.batch_count,
            event_ids=tuple(event.event_id for event in events),
            event_count=len(events),
            accumulated_salience=float(total_salience),
            strongest_mode=strongest_mode,
            strongest_mode_gain=strongest_gain,
            total_variation=float(total_variation),
            scheduled_revision=revision,
            displacement_rms=float(np.sqrt(np.mean(scalar_displacement**2))),
            displacement_peak=float(np.max(np.abs(scalar_displacement))),
        )
        self.last_batch = batch
        self._send(
            "batch",
            [
                batch.batch_id,
                batch.event_count,
                batch.accumulated_salience,
                batch.strongest_mode,
                batch.strongest_mode_gain,
                -1 if revision is None else revision,
                batch.displacement_rms,
                batch.displacement_peak,
            ],
        )
        return batch

    def close(self) -> None:
        if self._unsubscribe is not None:
            self._unsubscribe()
            self._unsubscribe = None


class GRWGeometryOSCService:
    def __init__(
        self,
        bridge: GRWDevelopmentalGeometryBridge,
        host: str = "127.0.0.1",
        port: int = 7462,
    ) -> None:
        self.bridge = bridge
        self.assembler = GRWFrameAssembler()
        self.commands: queue.SimpleQueue[tuple[str, tuple[Any, ...]]] = queue.SimpleQueue()
        dispatcher = Dispatcher()
        dispatcher.set_default_handler(self._enqueue)
        self.server = ThreadingOSCUDPServer((host, port), dispatcher)
        self.thread = threading.Thread(
            target=self.server.serve_forever,
            name="grw-geometry-osc",
            daemon=True,
        )

    def _enqueue(self, address: str, *args: Any) -> None:
        self.commands.put((address, tuple(args)))

    def start(self) -> None:
        self.thread.start()

    def poll(self) -> GRWGeometryBatch | None:
        prefix = "/qmw/grw/sonification/"
        while True:
            try:
                address, args = self.commands.get_nowait()
            except queue.Empty:
                break
            if not address.startswith(prefix):
                continue
            event = self.assembler.ingest(address[len(prefix):], args)
            if event is not None:
                self.bridge.ingest(event)
        return self.bridge.poll()

    def close(self) -> None:
        self.server.shutdown()
        self.server.server_close()
        if self.thread is not threading.current_thread():
            self.thread.join(timeout=2.0)


def _resolved_state_path(state_file: Path, value: str) -> Path:
    path = Path(value)
    if path.exists():
        return path
    candidate = state_file.parent / path.name
    if candidate.exists():
        return candidate
    candidate = state_file.parent / path.parent.name / path.name
    if candidate.exists():
        return candidate
    raise FileNotFoundError(path)


def _load_living_from_state(
    state_file: Path,
) -> tuple[LivingSpectralGeometry, np.ndarray, np.ndarray, GeometryProjection]:
    payload = json.loads(state_file.read_text(encoding="utf-8"))
    paths = dict(payload["paths"])
    spectral_path = _resolved_state_path(state_file, paths["spectral_npz"])
    quantum_path = _resolved_state_path(state_file, paths["quantum_npz"])
    with np.load(spectral_path, allow_pickle=False) as spectral:
        vertices = np.asarray(spectral["vertices"], dtype=np.float64)
        faces = np.asarray(spectral["faces"], dtype=np.int64)
    with np.load(quantum_path, allow_pickle=False) as quantum:
        rho = np.asarray(quantum["rho"], dtype=np.complex128)
    mode_count = int(payload["mode_count"])
    acoustic = dict(payload.get("descriptors", {}).get("acoustics", {}))
    config = LivingSpectralConfig(
        spectral=SpectralGeometryConfig(n_modes=mode_count),
        material=SurfaceMaterialConfig(
            model=str(payload["material_model"]), n_modes=mode_count
        ),
        quantum=QuantumEigenfieldConfig(n_geometric_modes=mode_count),
        acoustic=AcousticBridgeConfig(
            sample_rate=int(acoustic.get("sample_rate", 48_000)),
            duration_seconds=float(acoustic.get("duration_seconds", 6.0)),
        ),
    )
    living = LivingSpectralGeometry(
        vertices,
        faces,
        state_file.parent,
        config=config,
        rho=rho,
    )
    return living, vertices, faces, GeometryProjection.from_quantum_npz(quantum_path)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("state", type=Path, help="living current_state.json")
    parser.add_argument("--grw-host", default="127.0.0.1")
    parser.add_argument("--grw-port", type=int, default=7462)
    parser.add_argument("--out-host", default="127.0.0.1")
    parser.add_argument("--out-port", type=int, default=7460)
    parser.add_argument("--ack-host", default="127.0.0.1")
    parser.add_argument("--ack-port", type=int, default=7461)
    parser.add_argument("--crossfade-ms", type=float, default=1500.0)
    parser.add_argument("--salience-threshold", type=float, default=0.12)
    parser.add_argument("--batch-latency", type=float, default=12.0)
    parser.add_argument("--regeneration-interval", type=float, default=30.0)
    args = parser.parse_args()

    living, vertices, faces, projection = _load_living_from_state(args.state)
    client = SimpleUDPClient(args.out_host, args.out_port)
    publisher = LivingSpectralGeometryOSCPublisher(
        client,
        LivingOSCConfig(crossfade_ms=args.crossfade_ms),
    )
    publisher.attach(living)
    publisher.start_ack_server(args.ack_host, args.ack_port)
    bridge = GRWDevelopmentalGeometryBridge(
        living,
        vertices,
        faces,
        projection,
        GRWGeometryConfig(
            batch_salience_threshold=args.salience_threshold,
            maximum_batch_latency_seconds=args.batch_latency,
            regeneration_interval_seconds=args.regeneration_interval,
        ),
        status_client=client,
    )
    service = GRWGeometryOSCService(bridge, args.grw_host, args.grw_port)
    service.start()
    stop = threading.Event()

    def request_stop(*_: Any) -> None:
        stop.set()

    signal.signal(signal.SIGINT, request_stop)
    signal.signal(signal.SIGTERM, request_stop)
    print("GRW Developmental Geometry Bridge v1")
    print(f"  living state: {args.state}")
    print(f"  GRW input:    {args.grw_host}:{args.grw_port}")
    print(f"  IR output:    {args.out_host}:{args.out_port}")
    print(f"  IR ack:       {args.ack_host}:{args.ack_port}")
    try:
        while not stop.wait(0.05):
            service.poll()
    finally:
        service.close()
        bridge.close()
        publisher.close()
        living.close()


if __name__ == "__main__":
    main()
