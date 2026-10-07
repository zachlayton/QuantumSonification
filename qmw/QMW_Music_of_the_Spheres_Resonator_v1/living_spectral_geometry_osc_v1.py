#!/usr/bin/env python3
"""Thin OSC publication adapter for Living Spectral Geometry v1."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import argparse
import json
import signal
import threading
import time
from typing import Any, Mapping

import numpy as np
from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import ThreadingOSCUDPServer
from pythonosc.udp_client import SimpleUDPClient

from living_spectral_geometry_v1 import (
    LivingSpectralGeometry,
    LivingSpectralState,
)


@dataclass(frozen=True)
class LivingOSCConfig:
    version: str = "living_spectral_geometry_v1"
    crossfade_ms: float = 250.0
    poll_rate_hz: float = 20.0
    activation_timeout_seconds: float = 15.0


@dataclass(frozen=True)
class IRActivationState:
    revision: int
    path: str
    status: str
    candidate_time: float
    ready_time: float | None = None
    committed_time: float | None = None
    error: str | None = None


class LivingSpectralGeometryOSCPublisher:
    """Publish only complete, already-accepted living spectral revisions."""

    def __init__(
        self,
        client: Any,
        config: LivingOSCConfig = LivingOSCConfig(),
    ) -> None:
        self.client = client
        self.config = config
        self.last_revision = -1
        self._unsubscribe = None
        self._candidate: IRActivationState | None = None
        self._active: IRActivationState | None = None
        self._queued_payload: dict[str, Any] | None = None
        self._activation_timer: threading.Timer | None = None
        self._ack_server: ThreadingOSCUDPServer | None = None
        self._ack_thread: threading.Thread | None = None
        self._lock = threading.RLock()
        self._condition = threading.Condition(self._lock)

    @property
    def candidate(self) -> IRActivationState | None:
        with self._lock:
            return self._candidate

    @property
    def active(self) -> IRActivationState | None:
        with self._lock:
            return self._active

    def attach(self, living: LivingSpectralGeometry) -> None:
        self.detach()
        self._unsubscribe = living.subscribe(self.publish_state)
        if living.state is not None:
            self.publish_state(living.state, force=True)

    def detach(self) -> None:
        if self._unsubscribe is not None:
            self._unsubscribe()
            self._unsubscribe = None

    def _send(self, address: str, value: Any) -> None:
        self.client.send_message(address, value)

    @staticmethod
    def _state_mapping(
        state: LivingSpectralState | Mapping[str, Any],
    ) -> dict[str, Any]:
        return state.to_dict() if isinstance(state, LivingSpectralState) else dict(state)

    def publish_state(
        self,
        state: LivingSpectralState | Mapping[str, Any],
        *,
        force: bool = False,
    ) -> bool:
        payload = self._state_mapping(state)
        revision = int(payload["revision"])
        with self._lock:
            if self._candidate is not None:
                queued_revision = (
                    -1
                    if self._queued_payload is None
                    else int(self._queued_payload["revision"])
                )
                if revision <= max(self._candidate.revision, queued_revision):
                    return False
                self._queued_payload = payload
                self._send("/living/ir/queued", revision)
                return True
            if not force and revision <= self.last_revision:
                return False
        paths = dict(payload["paths"])
        bundle_path = Path(paths["bundle_npz"])
        if not bundle_path.exists():
            raise FileNotFoundError(bundle_path)
        with np.load(bundle_path, allow_pickle=False) as bundle:
            eigenvalues = np.asarray(bundle["eigenvalues"], dtype=np.float64)
            frequencies = np.asarray(bundle["frequencies_hz"], dtype=np.float64)
            probabilities = np.asarray(
                bundle["mode_probabilities"], dtype=np.float64
            )
            decay = np.asarray(
                bundle["decay_times_seconds"], dtype=np.float64
            )
            damping = np.asarray(bundle["damping_rates"], dtype=np.float64)
            weights = np.asarray(bundle["mode_weights"], dtype=np.float64)

        descriptors = dict(payload.get("descriptors", {}))
        timing = dict(descriptors.get("timing", {}))
        ir_path = str(paths["ir_wav"])
        with self._lock:
            self._candidate = IRActivationState(
                revision=revision,
                path=ir_path,
                status="candidate",
                candidate_time=time.time(),
            )
            self._start_activation_timer_locked(revision)
        self._send("/living/publication/begin", revision)
        self._send("/living/version", self.config.version)
        self._send("/living/revision", revision)
        self._send("/living/model", str(payload["material_model"]))
        self._send("/living/ir/path", ir_path)
        self._send("/living/ir/crossfade_ms", float(self.config.crossfade_ms))
        self._send(
            "/living/ir/candidate",
            [revision, ir_path, float(self.config.crossfade_ms)],
        )
        self._send("/living/ir/status", ["candidate", revision])
        self._send("/living/spectrum/eigenvalues", eigenvalues.tolist())
        self._send("/living/spectrum/frequencies", frequencies.tolist())
        self._send("/living/quantum/probabilities", probabilities.tolist())
        self._send(
            "/living/timing/entropy_bits",
            float(timing.get("entropy_bits", 0.0)),
        )
        self._send(
            "/living/timing/participation",
            float(timing.get("effective_participation", 0.0)),
        )
        self._send("/living/timing/mode_count", int(payload["mode_count"]))
        self._send("/living/timing/decay_seconds", decay.tolist())
        self._send("/living/timing/damping_rates", damping.tolist())
        self._send("/living/timing/mode_weights", weights.tolist())
        self._send("/living/state/path", str(paths["directory"]))
        self._send("/living/publication/end", revision)
        self.last_revision = revision
        return True

    def _start_activation_timer_locked(self, revision: int) -> None:
        if self._activation_timer is not None:
            self._activation_timer.cancel()
        timeout = max(0.0, self.config.activation_timeout_seconds)
        if timeout == 0.0:
            self._activation_timer = None
            return
        self._activation_timer = threading.Timer(
            timeout, self._activation_timed_out, (revision,)
        )
        self._activation_timer.daemon = True
        self._activation_timer.start()

    def _cancel_activation_timer_locked(self) -> None:
        if self._activation_timer is not None:
            self._activation_timer.cancel()
            self._activation_timer = None

    def _activation_timed_out(self, revision: int) -> None:
        self.handle_failed(
            "/living/ir/failed", revision, "activation timeout"
        )

    @staticmethod
    def _ack_revision(args: tuple[Any, ...]) -> int:
        if not args:
            raise ValueError("IR acknowledgment requires a revision")
        return int(args[0])

    def _validate_candidate_locked(
        self,
        revision: int,
        allowed_statuses: tuple[str, ...],
    ) -> IRActivationState:
        if self._candidate is None:
            raise ValueError(f"no pending IR candidate for revision {revision}")
        if revision != self._candidate.revision:
            raise ValueError(
                f"stale IR acknowledgment {revision}; "
                f"pending revision is {self._candidate.revision}"
            )
        if self._candidate.status not in allowed_statuses:
            raise ValueError(
                f"revision {revision} is {self._candidate.status}; "
                f"expected one of {allowed_statuses}"
            )
        return self._candidate

    def handle_ready(self, address: str, *args: Any) -> None:
        try:
            revision = self._ack_revision(args)
            with self._condition:
                candidate = self._validate_candidate_locked(
                    revision, ("candidate",)
                )
                self._candidate = IRActivationState(
                    revision=candidate.revision,
                    path=candidate.path,
                    status="ready",
                    candidate_time=candidate.candidate_time,
                    ready_time=time.time(),
                )
                self._start_activation_timer_locked(revision)
                self._condition.notify_all()
            self._send("/living/ir/status", ["ready", revision])
            self._send(
                "/living/ir/crossfade/start",
                [revision, float(self.config.crossfade_ms)],
            )
        except Exception as exc:
            self._send("/living/ir/ack/error", [address, str(exc)])

    def handle_committed(self, address: str, *args: Any) -> None:
        queued: dict[str, Any] | None = None
        try:
            revision = self._ack_revision(args)
            with self._condition:
                candidate = self._validate_candidate_locked(
                    revision, ("ready",)
                )
                committed = IRActivationState(
                    revision=candidate.revision,
                    path=candidate.path,
                    status="committed",
                    candidate_time=candidate.candidate_time,
                    ready_time=candidate.ready_time,
                    committed_time=time.time(),
                )
                self._active = committed
                self._candidate = None
                self._cancel_activation_timer_locked()
                queued = self._queued_payload
                self._queued_payload = None
                self._condition.notify_all()
            self._send("/living/ir/status", ["committed", revision])
            self._send("/living/ir/active/revision", revision)
            self._send("/living/ir/active/path", committed.path)
            if queued is not None:
                self.publish_state(queued, force=True)
        except Exception as exc:
            self._send("/living/ir/ack/error", [address, str(exc)])

    def handle_failed(self, address: str, *args: Any) -> None:
        queued: dict[str, Any] | None = None
        try:
            revision = self._ack_revision(args)
            message = str(args[1]) if len(args) > 1 else "Max IR activation failed"
            with self._condition:
                candidate = self._validate_candidate_locked(
                    revision, ("candidate", "ready")
                )
                self._candidate = None
                self._cancel_activation_timer_locked()
                queued = self._queued_payload
                self._queued_payload = None
                self._condition.notify_all()
            self._send("/living/ir/status", ["failed", revision, message])
            self._send("/living/ir/failed/revision", revision)
            self._send("/living/ir/failed/path", candidate.path)
            if queued is not None:
                self.publish_state(queued, force=True)
        except Exception as exc:
            self._send("/living/ir/ack/error", [address, str(exc)])

    def wait_for_commit(
        self,
        revision: int,
        timeout: float | None = None,
    ) -> IRActivationState:
        deadline = None if timeout is None else time.monotonic() + timeout
        with self._condition:
            while True:
                if self._active is not None and self._active.revision >= revision:
                    return self._active
                remaining = (
                    None
                    if deadline is None
                    else max(0.0, deadline - time.monotonic())
                )
                if remaining == 0.0:
                    raise TimeoutError(
                        f"IR revision {revision} was not committed"
                    )
                self._condition.wait(remaining)

    def start_ack_server(
        self,
        host: str = "127.0.0.1",
        port: int = 7461,
    ) -> None:
        if self._ack_server is not None:
            raise RuntimeError("IR acknowledgment server is already running")
        dispatcher = Dispatcher()
        dispatcher.map("/living/ir/ready", self.handle_ready)
        dispatcher.map("/living/ir/committed", self.handle_committed)
        dispatcher.map("/living/ir/failed", self.handle_failed)
        self._ack_server = ThreadingOSCUDPServer((host, port), dispatcher)
        self._ack_thread = threading.Thread(
            target=self._ack_server.serve_forever,
            name="living-ir-ack",
            daemon=True,
        )
        self._ack_thread.start()

    def stop_ack_server(self) -> None:
        server = self._ack_server
        thread = self._ack_thread
        self._ack_server = None
        self._ack_thread = None
        if server is not None:
            server.shutdown()
            server.server_close()
        if thread is not None and thread is not threading.current_thread():
            thread.join(timeout=2.0)

    def close(self) -> None:
        self.detach()
        self.stop_ack_server()
        with self._lock:
            self._cancel_activation_timer_locked()

    def publish_state_file(
        self,
        state_file: str | Path,
        *,
        force: bool = False,
    ) -> bool:
        path = Path(state_file)
        payload = json.loads(path.read_text(encoding="utf-8"))
        return self.publish_state(payload, force=force)

    def watch(
        self,
        state_file: str | Path,
        stop_event: threading.Event | None = None,
    ) -> None:
        path = Path(state_file)
        stop = threading.Event() if stop_event is None else stop_event
        interval = 1.0 / max(float(self.config.poll_rate_hz), 0.1)
        last_modified = -1
        while not stop.is_set():
            try:
                modified = path.stat().st_mtime_ns
                if modified != last_modified:
                    self.publish_state_file(path)
                    last_modified = modified
            except FileNotFoundError:
                pass
            stop.wait(interval)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("state", type=Path, help="current_state.json")
    parser.add_argument("--out-host", default="127.0.0.1")
    parser.add_argument("--out-port", type=int, default=7460)
    parser.add_argument("--crossfade-ms", type=float, default=250.0)
    parser.add_argument("--poll-rate", type=float, default=20.0)
    parser.add_argument("--ack-host", default="127.0.0.1")
    parser.add_argument("--ack-port", type=int, default=7461)
    parser.add_argument("--activation-timeout", type=float, default=15.0)
    parser.add_argument("--no-ack-server", action="store_true")
    parser.add_argument("--once", action="store_true")
    args = parser.parse_args()

    client = SimpleUDPClient(args.out_host, args.out_port)
    publisher = LivingSpectralGeometryOSCPublisher(
        client,
        LivingOSCConfig(
            crossfade_ms=args.crossfade_ms,
            poll_rate_hz=args.poll_rate,
            activation_timeout_seconds=args.activation_timeout,
        ),
    )
    if args.once:
        publisher.publish_state_file(args.state, force=True)
        print(f"Published {args.state} → {args.out_host}:{args.out_port}")
        return

    stop = threading.Event()

    def request_stop(*_: Any) -> None:
        stop.set()

    signal.signal(signal.SIGINT, request_stop)
    signal.signal(signal.SIGTERM, request_stop)
    print("Living Spectral Geometry OSC v1")
    print(f"  state:  {args.state}")
    print(f"  output: {args.out_host}:{args.out_port}")
    if not args.no_ack_server:
        publisher.start_ack_server(args.ack_host, args.ack_port)
        print(f"  Max ack: {args.ack_host}:{args.ack_port}")
    try:
        publisher.watch(args.state, stop)
    finally:
        publisher.close()


if __name__ == "__main__":
    main()
