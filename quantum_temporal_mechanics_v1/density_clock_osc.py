#!/usr/bin/env python3
"""Receive canonical-engine density states and publish intrinsic-time pulses."""

from __future__ import annotations

import argparse
import queue
import signal
import threading

import numpy as np
from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import ThreadingOSCUDPServer
from pythonosc.udp_client import SimpleUDPClient

from .density_clock import DensityMatrixClock


SOURCE_ADDRESS = "/qmw/temporal/source/density"
ROOT = "/qmw/temporal-mechanics/v1"
DISTANCE_CONTROL_ADDRESS = f"{ROOT}/control/distance"
MODE_CONTROL_ADDRESS = f"{ROOT}/control/mode"
COHERENCE_DEPTH_CONTROL_ADDRESS = f"{ROOT}/control/coherence-depth"


def decode_density_payload(values) -> tuple[int, np.ndarray]:
    if len(values) < 4:
        raise ValueError("density payload is too short")
    revision = int(values[0])
    dimension = int(values[1])
    raw = np.asarray(values[2:], dtype=float)
    if raw.size != 2 * dimension * dimension:
        raise ValueError("density payload dimension does not match its data")
    complex_values = raw[0::2] + 1j * raw[1::2]
    return revision, complex_values.reshape(dimension, dimension)


class DensityClockBridge:
    def __init__(
        self,
        output_host: str,
        output_port: int,
        distance_per_pulse: float,
        mode: str = "poisson",
        seed: int = 23,
        coherence_depth: float = 0.35,
    ) -> None:
        self.clock = DensityMatrixClock(
            distance_per_pulse=distance_per_pulse,
            mode=mode,
            seed=seed,
            coherence_depth=coherence_depth,
        )
        self.output = SimpleUDPClient(output_host, output_port)
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

    def receive_distance(self, _address: str, *values) -> None:
        try:
            if not values:
                raise ValueError("distance control requires one value")
            distance = self.clock.set_distance_per_pulse(float(values[0]))
        except (TypeError, ValueError) as exc:
            self.output.send_message(f"{ROOT}/density-clock/error", str(exc))
            return
        self.output.send_message(
            f"{ROOT}/density-clock/config",
            ["distance_per_pulse", distance],
        )

    def receive_mode(self, _address: str, *values) -> None:
        try:
            if not values:
                raise ValueError("mode control requires poisson or fixed")
            mode = self.clock.set_mode(str(values[0]))
        except ValueError as exc:
            self.output.send_message(f"{ROOT}/density-clock/error", str(exc))
            return
        self.output.send_message(
            f"{ROOT}/density-clock/config",
            ["mode", mode],
        )

    def receive_coherence_depth(self, _address: str, *values) -> None:
        try:
            if not values:
                raise ValueError("coherence-depth control requires one value")
            depth = self.clock.set_coherence_depth(float(values[0]))
        except (TypeError, ValueError) as exc:
            self.output.send_message(f"{ROOT}/density-clock/error", str(exc))
            return
        self.output.send_message(
            f"{ROOT}/density-clock/config",
            ["coherence_depth", depth],
        )

    def process(self, revision: int, rho: np.ndarray) -> None:
        reading = self.clock.update(rho, revision)
        self.output.send_message(
            f"{ROOT}/density-clock/state",
            [
                reading.source_revision,
                reading.record_index,
                reading.intrinsic_time,
                reading.delta_bures,
                reading.remainder,
                reading.phase,
                reading.coherence,
                reading.purity,
                reading.population_flux,
                reading.coherence_flux,
                reading.coherence_flux_ema,
                reading.coherence_gain,
                reading.hazard_increment,
                reading.negativity,
                reading.projection_error,
                reading.next_record_distance,
            ],
        )
        first_record = reading.record_index - reading.pulses + 1
        for record in range(first_record, reading.record_index + 1):
            self.output.send_message(
                f"{ROOT}/density-clock/pulse",
                [
                    record,
                    reading.intrinsic_time,
                    reading.delta_bures,
                    reading.phase,
                    reading.coherence,
                    reading.population_flux,
                    reading.coherence_flux,
                    reading.purity,
                    reading.negativity,
                    reading.projection_error,
                    reading.coherence_gain,
                    reading.hazard_increment,
                ],
            )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Density-matrix-driven relational clock")
    parser.add_argument("--input-host", default="127.0.0.1")
    parser.add_argument("--input-port", type=int, default=7444)
    parser.add_argument("--output-host", default="127.0.0.1")
    parser.add_argument("--output-port", type=int, default=7400)
    parser.add_argument("--distance-per-pulse", type=float, default=0.025)
    parser.add_argument("--mode", choices=("poisson", "fixed"), default="poisson")
    parser.add_argument("--seed", type=int, default=23)
    parser.add_argument("--coherence-depth", type=float, default=0.35)
    args = parser.parse_args(argv)

    bridge = DensityClockBridge(
        args.output_host,
        args.output_port,
        args.distance_per_pulse,
        mode=args.mode,
        seed=args.seed,
        coherence_depth=args.coherence_depth,
    )
    dispatcher = Dispatcher()
    dispatcher.map(SOURCE_ADDRESS, bridge.receive)
    dispatcher.map(DISTANCE_CONTROL_ADDRESS, bridge.receive_distance)
    dispatcher.map(MODE_CONTROL_ADDRESS, bridge.receive_mode)
    dispatcher.map(COHERENCE_DEPTH_CONTROL_ADDRESS, bridge.receive_coherence_depth)
    server = ThreadingOSCUDPServer((args.input_host, args.input_port), dispatcher)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    print(
        f"Density clock: {args.input_host}:{args.input_port} -> "
        f"{args.output_host}:{args.output_port}; quantum={args.distance_per_pulse:g}",
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
            bridge.process(revision, rho)
        except (ValueError, np.linalg.LinAlgError) as exc:
            bridge.output.send_message(f"{ROOT}/density-clock/error", str(exc))
    server.shutdown()
    server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
