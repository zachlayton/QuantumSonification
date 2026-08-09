"""OSC publisher and control service for full four-qubit tomography."""

from __future__ import annotations

import json
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from pythonosc import dispatcher, osc_server
from pythonosc.udp_client import SimpleUDPClient

from .engine import (
    TomographyResult,
    simulate_tomography,
    tomography_result_from_dict,
)


OSC_ROOT = "/qmw/tomography"


def save_result(result: TomographyResult, destination: Path) -> Path:
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(result.to_dict(), indent=2, sort_keys=False) + "\n",
        encoding="utf-8",
    )
    return destination


class TomographyOSCPublisher:
    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 7426,
        packet_delay_ms: float = 2.0,
    ) -> None:
        self.client = SimpleUDPClient(host, port)
        self.packet_delay = max(0.0, packet_delay_ms) / 1000.0

    def _send(self, address: str, payload: list[Any]) -> None:
        self.client.send_message(f"{OSC_ROOT}/{address}", payload)
        if self.packet_delay:
            time.sleep(self.packet_delay)

    def status(self, *payload: Any) -> None:
        self._send("status", list(payload))

    def error(self, message: str) -> None:
        self._send("error", [message])

    def publish(self, result: TomographyResult, revision: int) -> None:
        """Publish a complete revision; receivers commit only after /end."""
        self._send(
            "begin",
            [
                revision,
                result.source,
                result.preset,
                result.transform,
                result.shots_per_setting,
                len(result.settings),
                16,
                len(result.paulis) - 1,
            ],
        )
        for setting in result.settings:
            self._send(
                "setting",
                [revision, setting.index, setting.axes, *setting.counts],
            )
        for pauli in result.paulis:
            if pauli.label == "IIII":
                continue
            self._send(
                "pauli",
                [
                    revision,
                    pauli.index - 1,
                    pauli.label,
                    pauli.weight,
                    pauli.expectation,
                ],
            )
        for shell in result.shells:
            self._send(
                "shell",
                [
                    revision,
                    shell.weight,
                    shell.term_count,
                    shell.rms,
                    shell.mean_abs,
                    shell.energy,
                ],
            )
        metrics = result.metrics
        self._send(
            "metrics",
            [
                revision,
                metrics["purity_physical"],
                metrics["entropy_bits_physical"],
                metrics["minimum_linear_eigenvalue"],
                metrics["fidelity_to_local_ideal"],
            ],
        )
        self._send("end", [revision, len(result.settings), len(result.paulis) - 1])


@dataclass
class ServiceConfig:
    preset: str = "ghz"
    transform: str = "none"
    shots: int = 256
    seed: int = 23


class TomographyOSCService:
    def __init__(
        self,
        *,
        control_host: str = "127.0.0.1",
        control_port: int = 7425,
        output_host: str = "127.0.0.1",
        output_port: int = 7426,
        packet_delay_ms: float = 2.0,
        config: ServiceConfig | None = None,
        save_directory: Path | None = None,
    ) -> None:
        self.control_host = control_host
        self.control_port = control_port
        self.publisher = TomographyOSCPublisher(
            output_host, output_port, packet_delay_ms
        )
        self.config = config or ServiceConfig()
        self.save_directory = save_directory
        self._run_lock = threading.Lock()
        self._revision = int(time.time() * 1000) % 2_000_000_000
        self._dispatcher = dispatcher.Dispatcher()
        self._dispatcher.map(f"{OSC_ROOT}/run", self._handle_run)
        self._dispatcher.map(f"{OSC_ROOT}/rerun", self._handle_rerun)
        self._dispatcher.map(f"{OSC_ROOT}/ping", self._handle_ping)
        self._dispatcher.map(f"{OSC_ROOT}/replay", self._handle_replay)
        self.server = osc_server.ThreadingOSCUDPServer(
            (control_host, control_port), self._dispatcher
        )

    def _next_revision(self) -> int:
        self._revision += 1
        return self._revision

    def _handle_ping(self, _address: str, *_args: Any) -> None:
        self.publisher.status(
            "ready",
            self.config.preset,
            self.config.transform,
            self.config.shots,
            self.config.seed,
        )

    def _handle_rerun(self, _address: str, *_args: Any) -> None:
        self.request_run(self.config)

    def _handle_run(self, _address: str, *args: Any) -> None:
        try:
            config = ServiceConfig(
                preset=str(args[0]) if len(args) > 0 else self.config.preset,
                transform=str(args[1]) if len(args) > 1 else self.config.transform,
                shots=int(args[2]) if len(args) > 2 else self.config.shots,
                seed=int(args[3]) if len(args) > 3 else self.config.seed,
            )
            self.request_run(config)
        except (TypeError, ValueError) as exc:
            self.publisher.error(f"invalid run request: {exc}")

    def _handle_replay(self, _address: str, *args: Any) -> None:
        source = str(args[0]).lower() if args else ""
        if source not in ("local", "ibm"):
            self.publisher.error("replay source must be local or ibm")
            return
        if self._run_lock.locked():
            self.publisher.status("busy")
            return
        thread = threading.Thread(
            target=self._replay_latest, args=(source,), daemon=True
        )
        thread.start()

    def _latest_archive(self, source: str) -> Path:
        if self.save_directory is None:
            raise FileNotFoundError("the service has no --save-dir")
        if source == "ibm":
            candidates = list(
                (self.save_directory / "ibm").glob(
                    "*/job-*-full4q-archive.json"
                )
            )
        else:
            candidates = [
                path
                for path in self.save_directory.glob("*.json")
                if path.is_file()
            ]
        if not candidates:
            raise FileNotFoundError(f"no saved {source} Full4Q dataset found")
        return max(candidates, key=lambda path: path.stat().st_mtime)

    def _replay_latest(self, source: str) -> None:
        with self._run_lock:
            try:
                path = self._latest_archive(source)
                payload = json.loads(path.read_text(encoding="utf-8"))
                if source == "ibm":
                    payload = payload["result"]
                result = tomography_result_from_dict(payload)
                revision = self._next_revision()
                self.publisher.status("replaying", source, path.name)
                self.publisher.publish(result, revision)
                self.publisher.status(
                    "replay_complete", source, revision, path.name
                )
            except Exception as exc:
                self.publisher.error(f"{source} replay: {exc}")

    def request_run(self, config: ServiceConfig) -> bool:
        if self._run_lock.locked():
            self.publisher.status("busy")
            return False
        self.config = config
        thread = threading.Thread(
            target=self._run_and_publish, args=(config,), daemon=True
        )
        thread.start()
        return True

    def _run_and_publish(self, config: ServiceConfig) -> None:
        with self._run_lock:
            revision = self._next_revision()
            try:
                self.publisher.status(
                    "running",
                    revision,
                    config.preset,
                    config.transform,
                    config.shots,
                )
                result = simulate_tomography(
                    preset=config.preset,
                    transform=config.transform,
                    shots=config.shots,
                    seed=config.seed,
                )
                if self.save_directory is not None:
                    stamp = time.strftime("%Y%m%d-%H%M%S")
                    filename = (
                        f"{stamp}_{config.preset}_{config.transform}"
                        f"_{config.shots}shots.json"
                    )
                    save_result(result, self.save_directory / filename)
                self.publisher.publish(result, revision)
                self.publisher.status("complete", revision, result.total_shots)
            except Exception as exc:  # keep the OSC service alive for the next run
                self.publisher.error(str(exc))

    def serve_forever(self) -> None:
        self.publisher.status(
            "ready",
            self.config.preset,
            self.config.transform,
            self.config.shots,
            self.config.seed,
        )
        self.server.serve_forever()

    def shutdown(self) -> None:
        self.server.shutdown()
        self.server.server_close()
