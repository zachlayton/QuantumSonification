#!/usr/bin/env python3
"""Bridge the conductor's canonical density stream into v2 relational ticks."""

from __future__ import annotations

import argparse
import queue
import signal
import threading

import numpy as np
from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import ThreadingOSCUDPServer
from pythonosc.udp_client import SimpleUDPClient

from .core import TemporalV2Config
from .density_correlation_clock import DensityCorrelationClockSystem
from .osc_output import CorrelationClockOSCPublisher


SOURCE_ADDRESS = "/qmw/temporal/source/density"
CONTROL_ADDRESS = "/qmw/temporal/v2/control/change-quantum"


def decode_density_payload(values) -> tuple[int, np.ndarray]:
    if len(values) < 4:
        raise ValueError("density payload is too short")
    revision = int(values[0])
    dimension = int(values[1])
    raw = np.asarray(values[2:], dtype=float)
    if raw.size != 2 * dimension * dimension:
        raise ValueError("density payload dimension does not match its data")
    return revision, (raw[0::2] + 1j * raw[1::2]).reshape(dimension, dimension)


class DensityCorrelationBridge:
    def __init__(self, output_host: str, output_port: int, change_quantum: float) -> None:
        self.output = SimpleUDPClient(output_host, output_port)
        publisher = CorrelationClockOSCPublisher(
            output_host, output_port, client=self.output
        )
        self.clock = DensityCorrelationClockSystem(
            TemporalV2Config(
                change_quantum=change_quantum,
                log_path=None,
                osc_enabled=True,
                osc_host=output_host,
                osc_port=output_port,
            ),
            publisher=publisher,
        )
        self.states: queue.Queue[tuple[int, np.ndarray]] = queue.Queue(maxsize=1)
        self.running = True

    def receive(self, _address: str, *values) -> None:
        try:
            state = decode_density_payload(values)
        except (TypeError, ValueError):
            return
        try:
            self.states.get_nowait()
        except queue.Empty:
            pass
        self.states.put_nowait(state)

    def receive_change_quantum(self, _address: str, *values) -> None:
        try:
            value = self.clock.set_change_quantum(float(values[0]))
        except (IndexError, TypeError, ValueError) as exc:
            self.output.send_message("/qmw/temporal/v2/error", str(exc))
            return
        self.output.send_message(
            "/qmw/temporal/v2/config", ["change_quantum", value]
        )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Live pairwise quantum correlation/differentiation clock"
    )
    parser.add_argument("--input-host", default="127.0.0.1")
    parser.add_argument("--input-port", type=int, default=7444)
    parser.add_argument("--output-host", default="127.0.0.1")
    parser.add_argument("--output-port", type=int, default=7442)
    parser.add_argument("--change-quantum", type=float, default=0.025)
    args = parser.parse_args(argv)
    bridge = DensityCorrelationBridge(
        args.output_host, args.output_port, args.change_quantum
    )
    dispatcher = Dispatcher()
    dispatcher.map(SOURCE_ADDRESS, bridge.receive)
    dispatcher.map(CONTROL_ADDRESS, bridge.receive_change_quantum)
    server = ThreadingOSCUDPServer((args.input_host, args.input_port), dispatcher)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    print(
        f"Correlation clock: {args.input_host}:{args.input_port} -> "
        f"{args.output_host}:{args.output_port}; quantum={args.change_quantum:g}",
        flush=True,
    )

    def stop(_signum=None, _frame=None):
        bridge.running = False

    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)
    while bridge.running:
        try:
            revision, rho = bridge.states.get(timeout=0.25)
        except queue.Empty:
            continue
        try:
            bridge.clock.update(rho, revision)
        except (ValueError, np.linalg.LinAlgError) as exc:
            bridge.output.send_message("/qmw/temporal/v2/error", str(exc))
    server.shutdown()
    server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
