"""Atomic OSC performance transport for the QMW comparison instrument."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import threading
import time
from typing import Any, Protocol

import numpy as np

from ..experiments import FloquetComparison, compare_floquet_routes
from ..sonification.dual_stream import REFERENCE_ROUTE, _observables


ROOT = "/qmw/qiskit_compare"
DATA_PORT = 17670
CONTROL_PORT = 17671
DEFAULT_ROUTE = "aer_noisy"


class OSCClient(Protocol):
    def send_message(self, address: str, value: Any) -> None: ...


@dataclass(frozen=True)
class LiveFrame:
    revision: int
    tick: int
    period_count: int
    route: str
    exact_z: np.ndarray
    transformed_z: np.ndarray
    delta_z: np.ndarray
    exact_zz: np.ndarray
    transformed_zz: np.ndarray
    delta_zz: np.ndarray
    trace_distance: float
    exact_purity: float
    transformed_purity: float


def comparison_frame(
    comparison: FloquetComparison,
    transformed_route: str,
    tick: int,
    revision: int,
) -> LiveFrame:
    if transformed_route not in comparison.routes:
        raise ValueError(
            f"unknown route {transformed_route!r}; available routes: "
            f"{', '.join(comparison.routes)}"
        )
    exact = comparison.routes[REFERENCE_ROUTE]
    transformed = comparison.routes[transformed_route]
    index = int(tick)
    if not 0 <= index < len(exact.frames):
        raise ValueError(f"tick must be in [0, {len(exact.frames) - 1}]")
    exact_z, exact_zz, exact_purity = _observables(exact)
    transformed_z, transformed_zz, transformed_purity = _observables(transformed)
    rho_exact = exact.density_matrices[index]
    rho_transformed = transformed.density_matrices[index]
    delta = (rho_transformed - rho_exact + (rho_transformed - rho_exact).conj().T) * 0.5
    trace_distance = float(0.5 * np.sum(np.abs(np.linalg.eigvalsh(delta))))
    return LiveFrame(
        revision=int(revision),
        tick=index,
        period_count=len(exact.frames) - 1,
        route=transformed_route,
        exact_z=exact_z[index],
        transformed_z=transformed_z[index],
        delta_z=transformed_z[index] - exact_z[index],
        exact_zz=exact_zz[index],
        transformed_zz=transformed_zz[index],
        delta_zz=transformed_zz[index] - exact_zz[index],
        trace_distance=trace_distance,
        exact_purity=float(exact_purity[index]),
        transformed_purity=float(transformed_purity[index]),
    )


def frame_messages(frame: LiveFrame) -> tuple[tuple[str, list[Any]], ...]:
    revision = frame.revision
    return (
        (f"{ROOT}/frame/begin", [revision, frame.tick, frame.period_count, frame.route]),
        (f"{ROOT}/exact/z", [revision, *map(float, frame.exact_z)]),
        (f"{ROOT}/transformed/z", [revision, *map(float, frame.transformed_z)]),
        (f"{ROOT}/difference/z", [revision, *map(float, frame.delta_z)]),
        (f"{ROOT}/exact/zz", [revision, *map(float, frame.exact_zz)]),
        (f"{ROOT}/transformed/zz", [revision, *map(float, frame.transformed_zz)]),
        (f"{ROOT}/difference/zz", [revision, *map(float, frame.delta_zz)]),
        (
            f"{ROOT}/metrics",
            [
                revision,
                frame.trace_distance,
                frame.exact_purity,
                frame.transformed_purity,
            ],
        ),
        (f"{ROOT}/frame/end", [revision]),
    )


class QMWComparisonOSCPublisher:
    """Logical-tick publisher with staged experimental control changes."""

    def __init__(
        self,
        client: OSCClient,
        *,
        periods: int = 16,
        transformed_route: str = DEFAULT_ROUTE,
        period_seconds: float = 0.4,
        noise_scale: float = 1.0,
        loop: bool = True,
        comparison: FloquetComparison | None = None,
    ) -> None:
        if periods < 1:
            raise ValueError("periods must be positive")
        if period_seconds <= 0:
            raise ValueError("period_seconds must be positive")
        if noise_scale < 0:
            raise ValueError("noise_scale must be non-negative")
        self.client = client
        self.periods = int(periods)
        self.period_seconds = float(period_seconds)
        self.noise_scale = float(noise_scale)
        self.loop = bool(loop)
        self.comparison = comparison or self._build_comparison(self.noise_scale)
        if transformed_route not in self.comparison.routes:
            raise ValueError(f"unknown transformed route {transformed_route!r}")
        self.transformed_route = transformed_route
        self.tick = 0
        self.revision = 0
        self.running = True
        self._pending_noise_scale: float | None = None
        self._lock = threading.RLock()

    def _build_comparison(self, noise_scale: float) -> FloquetComparison:
        return compare_floquet_routes(
            periods=self.periods,
            single_qubit_error=0.0015 * noise_scale,
            two_qubit_error=0.012 * noise_scale,
        )

    def current_frame(self) -> LiveFrame:
        with self._lock:
            return comparison_frame(
                self.comparison,
                self.transformed_route,
                self.tick,
                self.revision + 1,
            )

    def publish_current(self) -> LiveFrame:
        with self._lock:
            frame = self.current_frame()
            for address, values in frame_messages(frame):
                self.client.send_message(address, values)
            self.revision = frame.revision
            return frame

    def advance(self) -> bool:
        """Advance one logical Floquet tick; return False at a non-looping end."""
        with self._lock:
            if self.tick < self.periods:
                self.tick += 1
                return True
            if not self.loop:
                self.running = False
                return False
            self.reset()
            return True

    def set_route(self, route: str) -> None:
        with self._lock:
            if route not in self.comparison.routes:
                raise ValueError(f"unknown route {route!r}")
            self.transformed_route = route

    def set_period_seconds(self, seconds: float) -> None:
        if seconds <= 0:
            raise ValueError("period_seconds must be positive")
        with self._lock:
            self.period_seconds = float(seconds)

    def stage_noise_scale(self, scale: float) -> None:
        if scale < 0:
            raise ValueError("noise_scale must be non-negative")
        with self._lock:
            self._pending_noise_scale = float(scale)

    def reset(self) -> None:
        """Apply staged noise only at the trajectory boundary, then reset tick."""
        with self._lock:
            if self._pending_noise_scale is not None:
                self.noise_scale = self._pending_noise_scale
                self.comparison = self._build_comparison(self.noise_scale)
                self._pending_noise_scale = None
            self.tick = 0

    def run(self, stop_event: threading.Event | None = None) -> None:
        stop = stop_event or threading.Event()
        deadline = time.monotonic()
        while not stop.is_set():
            if not self.running:
                stop.wait(0.02)
                deadline = time.monotonic()
                continue
            self.publish_current()
            if not self.advance():
                continue
            deadline += self.period_seconds
            stop.wait(max(0.0, deadline - time.monotonic()))


class PerformanceControls:
    def __init__(self, publisher: QMWComparisonOSCPublisher) -> None:
        self.publisher = publisher

    def start(self, _address: str, *_values: Any) -> None:
        self.publisher.running = True

    def stop(self, _address: str, *_values: Any) -> None:
        self.publisher.running = False

    def reset(self, _address: str, *_values: Any) -> None:
        self.publisher.reset()

    def route(self, _address: str, value: Any) -> None:
        self.publisher.set_route(str(value))

    def period(self, _address: str, value: Any) -> None:
        self.publisher.set_period_seconds(float(value))

    def noise_scale(self, _address: str, value: Any) -> None:
        self.publisher.stage_noise_scale(float(value))


def build_control_server(publisher: QMWComparisonOSCPublisher, host: str, port: int):
    try:
        from pythonosc.dispatcher import Dispatcher
        from pythonosc.osc_server import ThreadingOSCUDPServer
    except ImportError as exc:
        raise ImportError("real-time OSC requires python-osc") from exc
    controls = PerformanceControls(publisher)
    dispatcher = Dispatcher()
    dispatcher.map(f"{ROOT}/control/start", controls.start)
    dispatcher.map(f"{ROOT}/control/stop", controls.stop)
    dispatcher.map(f"{ROOT}/control/reset", controls.reset)
    dispatcher.map(f"{ROOT}/control/route", controls.route)
    dispatcher.map(f"{ROOT}/control/period", controls.period)
    dispatcher.map(f"{ROOT}/control/noise_scale", controls.noise_scale)
    return ThreadingOSCUDPServer((host, port), dispatcher)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--data-port", type=int, default=DATA_PORT)
    parser.add_argument("--control-port", type=int, default=CONTROL_PORT)
    parser.add_argument("--periods", type=int, default=16)
    parser.add_argument("--period-seconds", type=float, default=0.4)
    parser.add_argument("--route", default=DEFAULT_ROUTE)
    parser.add_argument("--noise-scale", type=float, default=1.0)
    parser.add_argument("--no-loop", action="store_true")
    args = parser.parse_args()

    try:
        from pythonosc.udp_client import SimpleUDPClient
    except ImportError as exc:
        raise ImportError("real-time OSC requires python-osc") from exc
    publisher = QMWComparisonOSCPublisher(
        SimpleUDPClient(args.host, args.data_port),
        periods=args.periods,
        transformed_route=args.route,
        period_seconds=args.period_seconds,
        noise_scale=args.noise_scale,
        loop=not args.no_loop,
    )
    server = build_control_server(publisher, args.host, args.control_port)
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()
    print(
        f"QMW comparison OSC: data -> {args.host}:{args.data_port}; "
        f"controls <- {args.host}:{args.control_port}; route={args.route}",
        flush=True,
    )
    try:
        publisher.run()
    except KeyboardInterrupt:
        pass
    finally:
        server.shutdown()
        server.server_close()


if __name__ == "__main__":
    main()
