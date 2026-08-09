#!/usr/bin/env python3
"""Clear one-qubit version of Heisenberg's three measurement protocols."""

from __future__ import annotations

import argparse
import math
import threading
import time
from typing import Any

import numpy as np
from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import ThreadingOSCUDPServer
from pythonosc.udp_client import SimpleUDPClient

from .three_experiments import ExperimentMode, computational_projectors, run_three_experiments


I2 = np.eye(2, dtype=np.complex128)
X = np.asarray([[0, 1], [1, 0]], dtype=np.complex128)
Y = np.asarray([[0, -1j], [1j, 0]], dtype=np.complex128)
Z = np.asarray([[1, 0], [0, -1]], dtype=np.complex128)
OBSERVABLE = (X + Z) / math.sqrt(2.0)
CELL_FREQUENCIES = np.asarray([[110.0, 440.0], [440.0, 165.0]])
CELL_PAN = np.asarray([[-0.8, -0.45], [0.45, 0.8]])


def rotation_y(theta: float) -> np.ndarray:
    return math.cos(theta / 2.0) * I2 - 1j * math.sin(theta / 2.0) * Y


def contribution_matrix(rho: np.ndarray) -> np.ndarray:
    """Cell (m,n) contributes rho[m,n] A[n,m] to Tr(rho A)."""
    return np.asarray(rho) * OBSERVABLE.T


def bloch_vector(rho: np.ndarray) -> tuple[float, float, float]:
    return tuple(float(np.trace(rho @ operator).real) for operator in (X, Y, Z))


def purity(rho: np.ndarray) -> float:
    return float(np.trace(rho @ rho).real)


class ClearMeasurementLab:
    root = "/qmw/heisenberg_clear"

    def __init__(self, client: Any, seed: int = 1933) -> None:
        self.client = client
        self.rng = np.random.default_rng(seed)
        self.mode = ExperimentMode.COHERENT
        self.revision = 0
        self.lock = threading.RLock()
        self.initial_rho = np.asarray([[1, 0], [0, 0]], dtype=np.complex128)
        self.first = rotation_y(math.pi / 2.0)
        self.second = rotation_y(-math.pi / 2.0)
        self.projectors = computational_projectors(2)
        self.results = None
        self.refresh_recorded_outcome()

    def refresh_recorded_outcome(self) -> None:
        with self.lock:
            self.results = run_three_experiments(
                self.initial_rho,
                self.first,
                self.second,
                self.projectors,
                rng=self.rng,
            )
            self.revision += 1

    def set_mode(self, value: str | int) -> None:
        with self.lock:
            if isinstance(value, (int, np.integer)):
                self.mode = tuple(ExperimentMode)[int(value) % 3]
            else:
                self.mode = ExperimentMode(str(value).strip().lower())
        self.publish()

    def publish(self) -> None:
        with self.lock:
            ordered = (self.results.coherent, self.results.unread, self.results.recorded)
            for result in ordered:
                self._publish_case(f"{self.root}/{result.mode.value}", result)
                if result.mode is self.mode:
                    self._publish_case(f"{self.root}/active", result)

    def _publish_case(self, prefix: str, result: Any) -> None:
        rho = result.final_rho
        cells = contribution_matrix(rho)
        expectation = np.trace(rho @ OBSERVABLE)
        bx, by, bz = bloch_vector(rho)
        self.revision += 1
        self.client.send_message(f"{prefix}/mode", result.mode.value)
        self.client.send_message(f"{prefix}/outcome", -1 if result.outcome is None else result.outcome)
        self.client.send_message(f"{prefix}/measurement_probabilities", list(result.outcome_probabilities))
        self.client.send_message(f"{prefix}/final_probabilities", [float(rho[0, 0].real), float(rho[1, 1].real)])
        self.client.send_message(f"{prefix}/bloch", [bx, by, bz])
        self.client.send_message(f"{prefix}/purity", purity(rho))
        self.client.send_message(f"{prefix}/coherence", float(np.sum(np.abs(rho - np.diag(np.diag(rho))))))
        self.client.send_message(f"{prefix}/disturbance", float(result.measurement_disturbance))
        self.client.send_message(f"{prefix}/expectation", float(expectation.real))
        self.client.send_message(f"{prefix}/matrix/begin", [self.revision, 2])
        self.client.send_message(f"{prefix}/matrix/real", cells.real.reshape(-1).tolist())
        self.client.send_message(f"{prefix}/matrix/imag", cells.imag.reshape(-1).tolist())
        self.client.send_message(f"{prefix}/matrix/magnitude", np.abs(cells).reshape(-1).tolist())
        self.client.send_message(f"{prefix}/matrix/phase", np.angle(cells).reshape(-1).tolist())
        self.client.send_message(f"{prefix}/matrix/frequency_hz", CELL_FREQUENCIES.reshape(-1).tolist())
        self.client.send_message(f"{prefix}/matrix/pan", CELL_PAN.reshape(-1).tolist())
        self.client.send_message(f"{prefix}/matrix/end", self.revision)


def start_control_server(lab: ClearMeasurementLab, host: str, port: int) -> ThreadingOSCUDPServer:
    dispatcher = Dispatcher()
    dispatcher.map("/qmw/heisenberg_clear/mode", lambda _address, value: lab.set_mode(value))

    def record(_address, *_values) -> None:
        lab.refresh_recorded_outcome()
        lab.publish()

    dispatcher.map("/qmw/heisenberg_clear/record", record)
    server = ThreadingOSCUDPServer((host, int(port)), dispatcher)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--output-port", type=int, default=7420)
    parser.add_argument("--control-port", type=int, default=7421)
    parser.add_argument("--publish-hz", type=float, default=2.0)
    parser.add_argument("--seed", type=int, default=1933)
    args = parser.parse_args()
    lab = ClearMeasurementLab(SimpleUDPClient(args.host, args.output_port), seed=args.seed)
    server = start_control_server(lab, args.host, args.control_port)
    print(f"Clear Heisenberg Lab: 2x2 field -> udp/{args.output_port}, controls <- udp/{args.control_port}")
    try:
        while True:
            lab.publish()
            time.sleep(1.0 / max(0.1, args.publish_hz))
    except KeyboardInterrupt:
        server.shutdown(); server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
