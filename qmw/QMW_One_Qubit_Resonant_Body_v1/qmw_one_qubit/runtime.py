"""Small local HTTP/JSON and OSC runtime for the instrument.

The browser polls one complete JSON frame and posts explicit controls. This
avoids a WebSocket dependency while preserving atomic, revisioned snapshots.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict, replace
import errno
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import subprocess
import threading
import time
from typing import Any

from .frames import SoundAdapterControls
from .mapping import observe_one_qubit, resonant_body_frame
from .physics import OneQubitEngine, OneQubitPhysicsControls
from .transport import FRAME_ADDRESS, frame_payload, osc_arguments


WEB_ROOT = Path(__file__).resolve().parents[1] / "web"
DEFAULT_HTTP_PORT = 8765
DEFAULT_OSC_PORT = 17910


class InstrumentRuntime:
    def __init__(
        self,
        *,
        rate_hz: float = 30.0,
        osc_host: str = "127.0.0.1",
        osc_port: int = DEFAULT_OSC_PORT,
        osc_enabled: bool = True,
    ) -> None:
        if rate_hz <= 0.0:
            raise ValueError("rate_hz must be positive")
        self.engine = OneQubitEngine()
        self.sound = SoundAdapterControls()
        self.running = True
        self.rate_hz = float(rate_hz)
        self.last_measurement: dict[str, Any] | None = None
        self._frame_revision = 0
        self._lock = threading.RLock()
        self._stop = threading.Event()
        self._osc = None
        if osc_enabled:
            try:
                from pythonosc.udp_client import SimpleUDPClient

                self._osc = SimpleUDPClient(osc_host, int(osc_port))
            except ImportError as error:
                raise RuntimeError(
                    "python-osc is required unless --no-osc is selected"
                ) from error

    def snapshot(self) -> dict[str, Any]:
        with self._lock:
            quantum = self.engine.snapshot()
            observation = observe_one_qubit(quantum)
            body = resonant_body_frame(
                observation, self.sound, revision=self._frame_revision
            )
            return frame_payload(
                observation,
                body,
                running=self.running,
                measurement=self.last_measurement,
            )

    def _publish(self) -> None:
        quantum = self.engine.snapshot()
        observation = observe_one_qubit(quantum)
        body = resonant_body_frame(
            observation, self.sound, revision=self._frame_revision
        )
        if self._osc is not None:
            self._osc.send_message(FRAME_ADDRESS, osc_arguments(observation, body))

    def run_loop(self) -> None:
        period = 1.0 / self.rate_hz
        deadline = time.monotonic()
        while not self._stop.is_set():
            with self._lock:
                if self.running:
                    self.engine.step(period)
                    self._frame_revision += 1
                self._publish()
            deadline += period
            self._stop.wait(max(0.0, deadline - time.monotonic()))
            if time.monotonic() - deadline > period:
                deadline = time.monotonic()

    def close(self) -> None:
        self._stop.set()

    def apply(self, command: dict[str, Any]) -> dict[str, Any]:
        with self._lock:
            action = str(command.get("action", ""))
            if action == "run":
                self.running = bool(command["value"])
                self._frame_revision += 1
            elif action == "prepare":
                self.engine.prepare(str(command["state"]))
                self.last_measurement = None
                self._frame_revision += 1
            elif action == "measure_z":
                event, _ = self.engine.measure_z()
                self.last_measurement = asdict(event)
                self._frame_revision += 1
            elif action == "set_physics":
                omega = command["omega_rad_per_second"]
                if not isinstance(omega, list) or len(omega) != 3:
                    raise ValueError("omega_rad_per_second must contain x, y, z")
                self.engine.set_controls(
                    OneQubitPhysicsControls(
                        omega_x=float(omega[0]),
                        omega_y=float(omega[1]),
                        omega_z=float(omega[2]),
                        t1_seconds=_optional_time(command.get("t1_seconds")),
                        tphi_seconds=_optional_time(command.get("tphi_seconds")),
                    )
                )
                self._frame_revision += 1
            elif action == "set_sound":
                permitted = {
                    "base_frequency_hz",
                    "probe_rate_hz",
                    "probe_brightness",
                    "body_detail",
                    "base_decay_seconds",
                    "decay_tilt",
                    "master",
                    "sound_locked",
                }
                updates = {key: value for key, value in command.items() if key in permitted}
                self.sound = replace(self.sound, **updates).validated()
                self._frame_revision += 1
            else:
                raise ValueError(f"unknown action: {action}")
            self._publish()
            return self.snapshot()


def _optional_time(value: Any) -> float | None:
    if value is None or float(value) == 0.0:
        return None
    return float(value)


class InstrumentHTTPServer(ThreadingHTTPServer):
    runtime: InstrumentRuntime


class Handler(BaseHTTPRequestHandler):
    server: InstrumentHTTPServer

    def log_message(self, format_string: str, *args: object) -> None:
        # The browser polls this endpoint as a meter stream; logging every
        # frame would bury meaningful control and error messages.
        if self.path == "/api/state":
            return
        print("HTTP " + (format_string % args), flush=True)

    def _send(self, status: HTTPStatus, data: bytes, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler API
        if self.path in ("/", "/index.html"):
            self._send(
                HTTPStatus.OK,
                (WEB_ROOT / "index.html").read_bytes(),
                "text/html; charset=utf-8",
            )
        elif self.path == "/api/state":
            encoded = json.dumps(self.server.runtime.snapshot()).encode("utf-8")
            self._send(HTTPStatus.OK, encoded, "application/json")
        else:
            self._send(HTTPStatus.NOT_FOUND, b"not found\n", "text/plain")

    def do_POST(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler API
        if self.path != "/api/control":
            self._send(HTTPStatus.NOT_FOUND, b"not found\n", "text/plain")
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length <= 0 or length > 65536:
                raise ValueError("request body must contain a small JSON object")
            command = json.loads(self.rfile.read(length))
            if not isinstance(command, dict):
                raise ValueError("command must be a JSON object")
            result = self.server.runtime.apply(command)
            self._send(
                HTTPStatus.OK,
                json.dumps(result).encode("utf-8"),
                "application/json",
            )
        except (KeyError, TypeError, ValueError, json.JSONDecodeError) as error:
            self._send(
                HTTPStatus.BAD_REQUEST,
                json.dumps({"error": str(error)}).encode("utf-8"),
                "application/json",
            )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--rate-hz", type=float, default=30.0)
    parser.add_argument("--osc-host", default="127.0.0.1")
    parser.add_argument("--osc-port", type=int, default=57120)
    parser.add_argument("--no-osc", action="store_true")
    parser.add_argument("--open-browser", action="store_true")
    args = parser.parse_args()

    runtime = InstrumentRuntime(
        rate_hz=args.rate_hz,
        osc_host=args.osc_host,
        osc_port=args.osc_port,
        osc_enabled=not args.no_osc,
    )
    server = InstrumentHTTPServer((args.host, args.port), Handler)
    server.runtime = runtime
    worker = threading.Thread(target=runtime.run_loop, name="qmw-one-qubit", daemon=True)
    worker.start()
    url = f"http://{args.host}:{args.port}/"
    print(f"QMW One-Qubit Resonant Body V1: {url}", flush=True)
    print(
        f"OSC {FRAME_ADDRESS} -> {args.osc_host}:{args.osc_port}"
        if not args.no_osc
        else "OSC disabled",
        flush=True,
    )
    if args.open_browser:
        subprocess.Popen(("open", url))
    try:
        server.serve_forever(poll_interval=0.25)
    except KeyboardInterrupt:
        pass
    finally:
        server.shutdown()
        runtime.close()
        worker.join(timeout=2.0)
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
