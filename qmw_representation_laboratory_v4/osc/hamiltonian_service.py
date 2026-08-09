"""Atomic OSC preview/commit service for live Hamiltonian transformation."""

from __future__ import annotations

import threading
import time
from dataclasses import dataclass
from typing import Any

import numpy as np
from pythonosc import dispatcher, osc_server
from pythonosc.udp_client import SimpleUDPClient

from full4q_tomography_v1.osc_service import TomographyOSCPublisher

from ..core import (
    RepresentationExperiment,
    SamplingPolicy,
    density_from_preset,
)
from ..observables import pauli_expectations
from ..protocols import FullPauliTomography
from ..transforms import (
    FloquetOperator,
    HamiltonianBasisTracker,
    IdentityOperator,
    IsingHamiltonianSpec,
)


CONTROL_ROOT = "/qmw/v4/hamiltonian"
PREVIEW_ROOT = "/qmw/v4/preview"
REVISION_MODULUS = 1_000_000_000


@dataclass(frozen=True)
class HamiltonianLiveConfig:
    coupling: float = 0.7
    transverse_field: float = 0.45
    longitudinal_field: float = 0.13
    evolution_time: float = 1.0
    mode: str = "eigenbasis"
    boundary: str = "open"
    preset: str = "ghz"
    shots: int = 256
    sampling: str = "fixed"
    seed: int = 23

    def validate(self) -> "HamiltonianLiveConfig":
        if self.mode not in {"eigenbasis", "evolution"}:
            raise ValueError("mode must be eigenbasis or evolution")
        if self.boundary not in {"open", "periodic"}:
            raise ValueError("boundary must be open or periodic")
        if self.preset not in {"bell", "ghz", "weave"}:
            raise ValueError("preset must be bell, ghz, or weave")
        if self.sampling not in {"fixed", "resample", "sequence"}:
            raise ValueError("sampling must be fixed, resample, or sequence")
        if self.shots <= 0:
            raise ValueError("shots must be positive")
        for name in (
            "coupling",
            "transverse_field",
            "longitudinal_field",
            "evolution_time",
        ):
            if not np.isfinite(getattr(self, name)):
                raise ValueError(f"{name} must be finite")
        return self

    def hamiltonian_spec(self) -> IsingHamiltonianSpec:
        return IsingHamiltonianSpec(
            n_qubits=4,
            coupling=self.coupling,
            transverse_field=self.transverse_field,
            longitudinal_field=self.longitudinal_field,
            boundary=self.boundary,
        )


class HamiltonianOSCPublisher:
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

    def _send(self, path: str, payload: list[Any]) -> None:
        self.client.send_message(path, payload)
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
        config: HamiltonianLiveConfig,
        eigenvalues: np.ndarray,
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
                config.preset,
                config.mode,
                config.coupling,
                config.transverse_field,
                config.longitudinal_field,
                config.evolution_time,
                config.boundary,
                len(labels),
                len(eigenvalues),
            ],
        )
        for index, value in enumerate(eigenvalues):
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
            [revision, len(labels), len(eigenvalues)],
        )


class HamiltonianOSCService:
    def __init__(
        self,
        *,
        control_host: str = "127.0.0.1",
        control_port: int = 7445,
        output_host: str = "127.0.0.1",
        output_port: int = 7436,
        packet_delay_ms: float = 1.0,
        config: HamiltonianLiveConfig | None = None,
    ) -> None:
        self.config = (config or HamiltonianLiveConfig()).validate()
        self.publisher = HamiltonianOSCPublisher(
            output_host,
            output_port,
            packet_delay_ms=packet_delay_ms,
        )
        self.tracker = HamiltonianBasisTracker()
        self._sequence_seed = self.config.seed
        self._sequence_policy = SamplingPolicy.sequence(self.config.seed)
        self._work_lock = threading.Lock()
        self._revision = int(time.time() * 1000) % REVISION_MODULUS
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
        self._revision = (self._revision + 1) % REVISION_MODULUS
        return self._revision

    def _parse(self, args: tuple[Any, ...]) -> tuple[int, HamiltonianLiveConfig]:
        current = self.config
        revision = int(args[0]) if len(args) > 0 else self._next_revision()
        if revision <= 0:
            revision = self._next_revision()
        config = HamiltonianLiveConfig(
            coupling=float(args[1]) if len(args) > 1 else current.coupling,
            transverse_field=(
                float(args[2]) if len(args) > 2 else current.transverse_field
            ),
            longitudinal_field=(
                float(args[3]) if len(args) > 3 else current.longitudinal_field
            ),
            evolution_time=(
                float(args[4]) if len(args) > 4 else current.evolution_time
            ),
            mode=str(args[5]) if len(args) > 5 else current.mode,
            boundary=str(args[6]) if len(args) > 6 else current.boundary,
            preset=str(args[7]) if len(args) > 7 else current.preset,
            shots=int(args[8]) if len(args) > 8 else current.shots,
            sampling=str(args[9]) if len(args) > 9 else current.sampling,
            seed=int(args[10]) if len(args) > 10 else current.seed,
        ).validate()
        return revision, config

    def _transform(
        self,
        config: HamiltonianLiveConfig,
    ) -> tuple[Any, np.ndarray, dict[str, Any]]:
        hamiltonian = config.hamiltonian_spec().matrix()
        if config.mode == "evolution":
            transform = FloquetOperator.from_hamiltonian(
                hamiltonian,
                period=config.evolution_time,
            )
            eigenvalues = np.linalg.eigvalsh(hamiltonian)
            tracking = {
                "tracking_applied": False,
                "minimum_matched_overlap": 1.0,
                "minimum_level_gap": float(
                    np.min(np.diff(np.sort(eigenvalues)))
                ),
            }
            return transform, eigenvalues, tracking
        basis, tracking = self.tracker.solve(hamiltonian)
        return basis, basis.eigenvalues, tracking

    def request_preview(
        self,
        revision: int,
        config: HamiltonianLiveConfig,
    ) -> bool:
        if self._work_lock.locked():
            self.publisher.status("busy", "preview", revision)
            return False
        threading.Thread(
            target=self._preview,
            args=(revision, config),
            daemon=True,
        ).start()
        return True

    def request_commit(
        self,
        revision: int,
        config: HamiltonianLiveConfig,
    ) -> bool:
        if self._work_lock.locked():
            self.publisher.status("busy", "commit", revision)
            return False
        threading.Thread(
            target=self._commit,
            args=(revision, config),
            daemon=True,
        ).start()
        return True

    def _preview(
        self,
        revision: int,
        config: HamiltonianLiveConfig,
    ) -> None:
        with self._work_lock:
            try:
                transform, eigenvalues, tracking = self._transform(config)
                canonical = IdentityOperator().apply(
                    density_from_preset(config.preset)
                )
                experimental_density = transform.apply(canonical)
                self.publisher.preview(
                    revision=revision,
                    config=config,
                    eigenvalues=eigenvalues,
                    reference=pauli_expectations(canonical),
                    experimental=pauli_expectations(experimental_density),
                    density_distance=float(
                        np.linalg.norm(experimental_density - canonical)
                    ),
                    tracking=tracking,
                )
                self.config = config
                self.publisher.status("preview_complete", revision)
            except Exception as exc:
                self.publisher.error(f"preview failed: {exc}")

    def _commit(
        self,
        revision: int,
        config: HamiltonianLiveConfig,
    ) -> None:
        with self._work_lock:
            try:
                transform, _eigenvalues, _tracking = self._transform(config)
                if config.sampling == "sequence":
                    if config.seed != self._sequence_seed:
                        self._sequence_seed = config.seed
                        self._sequence_policy = SamplingPolicy.sequence(
                            config.seed
                        )
                    policy = self._sequence_policy
                elif config.sampling == "resample":
                    policy = SamplingPolicy.resample()
                else:
                    policy = SamplingPolicy.fixed(config.seed)
                result = RepresentationExperiment(
                    experimental=transform,
                    measurement=FullPauliTomography(sampling=policy),
                ).run(
                    preset=config.preset,
                    shots=config.shots,
                    seed=None if config.sampling == "resample" else config.seed,
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
                    result.seed,
                    base,
                    base + 1,
                )
            except Exception as exc:
                self.publisher.error(f"commit failed: {exc}")

    def _handle_preview(self, _address: str, *args: Any) -> None:
        try:
            self.request_preview(*self._parse(args))
        except Exception as exc:
            self.publisher.error(f"invalid preview: {exc}")

    def _handle_commit(self, _address: str, *args: Any) -> None:
        try:
            self.request_commit(*self._parse(args))
        except Exception as exc:
            self.publisher.error(f"invalid commit: {exc}")

    def _handle_ping(self, _address: str, *_args: Any) -> None:
        self.publisher.status("ready", *self.config.__dict__.values())

    def _handle_reset(self, _address: str, *_args: Any) -> None:
        self.tracker.reset()
        self.publisher.status("tracking_reset")

    def serve_forever(self) -> None:
        self.publisher.status("ready", *self.config.__dict__.values())
        self.server.serve_forever()

    def shutdown(self) -> None:
        self.server.shutdown()
        self.server.server_close()
