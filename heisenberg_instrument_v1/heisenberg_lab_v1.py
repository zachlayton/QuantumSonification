#!/usr/bin/env python3
"""Standalone live study for Heisenberg's three experiments.

The lab publishes all three cases and one selected active 16 x 16 transition
field. It is intentionally separate from the canonical engine until the
measurement protocol is auditioned and accepted.
"""

from __future__ import annotations

import argparse
import math
import threading
import time

import numpy as np
from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import ThreadingOSCUDPServer
from pythonosc.udp_client import SimpleUDPClient

from heisenberg_instrument_v1.osc_publisher import HeisenbergOSCPublisher
from heisenberg_instrument_v1.three_experiments import (
    ExperimentMode,
    run_three_experiments,
)
from heisenberg_instrument_v1.transition_matrix import transition_matrix_frame


I2 = np.eye(2, dtype=np.complex128)
X = np.asarray([[0, 1], [1, 0]], dtype=np.complex128)
Y = np.asarray([[0, -1j], [1j, 0]], dtype=np.complex128)
Z = np.asarray([[1, 0], [0, -1]], dtype=np.complex128)


def kron_all(operators: list[np.ndarray]) -> np.ndarray:
    result = operators[0]
    for operator in operators[1:]:
        result = np.kron(result, operator)
    return result


def local_operator(operator: np.ndarray, qubit: int, n_qubits: int = 4) -> np.ndarray:
    # Match the project convention: q0 is the least-significant/rightmost bit.
    operators = [I2 for _ in range(n_qubits)]
    operators[n_qubits - 1 - qubit] = operator
    return kron_all(operators)


def rotation_y(theta: float, qubit: int, n_qubits: int = 4) -> np.ndarray:
    local = math.cos(theta / 2.0) * I2 - 1j * math.sin(theta / 2.0) * Y
    return local_operator(local, qubit, n_qubits)


def qubit_projectors(qubit: int, n_qubits: int = 4) -> tuple[np.ndarray, np.ndarray]:
    axis = local_operator(Z, qubit, n_qubits)
    identity = np.eye(2**n_qubits, dtype=np.complex128)
    return 0.5 * (identity + axis), 0.5 * (identity - axis)


def demo_hamiltonian(n_qubits: int = 4) -> np.ndarray:
    hamiltonian = np.zeros((2**n_qubits, 2**n_qubits), dtype=np.complex128)
    weights = (0.73, 1.11, 1.67, 2.41)
    for qubit, weight in enumerate(weights):
        hamiltonian += weight * local_operator(Z, qubit, n_qubits)
    for qubit in range(n_qubits - 1):
        hamiltonian += 0.17 * (
            local_operator(X, qubit, n_qubits)
            @ local_operator(X, qubit + 1, n_qubits)
        )
    return 0.5 * (hamiltonian + hamiltonian.conj().T)


class HeisenbergLab:
    def __init__(self, client: SimpleUDPClient, seed: int = 1933) -> None:
        self.publisher = HeisenbergOSCPublisher(client)
        self.rng = np.random.default_rng(seed)
        self.mode = ExperimentMode.COHERENT
        self.lock = threading.RLock()
        self.revision = 0
        self.n_qubits = 4
        self.dimension = 2**self.n_qubits
        self.first = rotation_y(math.pi / 2.0, 0, self.n_qubits)
        self.second = rotation_y(-math.pi / 2.0, 0, self.n_qubits)
        self.projectors = qubit_projectors(0, self.n_qubits)
        self.hamiltonian = demo_hamiltonian(self.n_qubits)
        self.observables = {
            "X0": local_operator(X, 0, self.n_qubits),
            "Y0": local_operator(Y, 0, self.n_qubits),
            "Z0": local_operator(Z, 0, self.n_qubits),
            "XZ0": (
                local_operator(X, 0, self.n_qubits)
                + local_operator(Z, 0, self.n_qubits)
            ) / math.sqrt(2.0),
        }
        # A single tilted observable distinguishes the final states of all
        # three default protocols: Z resolves coherent vs unread, while X
        # resolves recorded vs unread. Pure X made the first two fields zero.
        self.observable_name = "XZ0"
        state = np.zeros(self.dimension, dtype=np.complex128)
        state[0] = 1.0
        self.initial_rho = np.outer(state, state.conj())
        self.results = None
        self.frames = None
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
            self._rebuild_frames()
            self.revision += 1

    def _rebuild_frames(self) -> None:
        observable = self.observables[self.observable_name]
        ordered_results = (
            self.results.coherent,
            self.results.unread,
            self.results.recorded,
        )
        self.frames = {
            result.mode: transition_matrix_frame(
                result.final_rho,
                self.hamiltonian,
                observable,
            )
            for result in ordered_results
        }

    def set_mode(self, mode: str | int) -> None:
        with self.lock:
            if isinstance(mode, (int, np.integer)):
                selected = (
                    ExperimentMode.COHERENT,
                    ExperimentMode.UNREAD,
                    ExperimentMode.RECORDED,
                )[int(mode) % 3]
            else:
                selected = ExperimentMode(str(mode).strip().lower())
            self.mode = selected
        self.publish()

    def set_observable(self, name: str) -> None:
        normalized = str(name).strip().upper()
        with self.lock:
            if normalized not in self.observables:
                raise ValueError(
                    f"unknown observable {name!r}; choose {sorted(self.observables)}"
                )
            self.observable_name = normalized
            # Choosing what to ask of the existing state must not secretly
            # perform a fresh recorded measurement.
            self._rebuild_frames()
            self.revision += 1
        self.publish()

    def publish(self) -> None:
        with self.lock:
            ordered_results = (
                self.results.coherent,
                self.results.unread,
                self.results.recorded,
            )
            for result in ordered_results:
                self.publisher.publish_case(
                    result,
                    self.frames[result.mode],
                    active=result.mode is self.mode,
                )
            root = self.publisher.root
            self.publisher.client.send_message(f"{root}/revision", self.revision)
            self.publisher.client.send_message(
                f"{root}/observable", self.observable_name
            )


def start_control_server(
    lab: HeisenbergLab, host: str, port: int
) -> ThreadingOSCUDPServer:
    dispatcher = Dispatcher()

    def set_mode(_address, value) -> None:
        lab.set_mode(value)

    def record(_address, *_values) -> None:
        lab.refresh_recorded_outcome()
        lab.publish()

    def set_observable(_address, value) -> None:
        lab.set_observable(value)

    dispatcher.map("/qmw/heisenberg/mode", set_mode)
    dispatcher.map("/qmw/heisenberg/record", record)
    dispatcher.map("/qmw/heisenberg/observable", set_observable)
    server = ThreadingOSCUDPServer((host, int(port)), dispatcher)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--output-port", type=int, default=7400)
    parser.add_argument("--control-port", type=int, default=7412)
    parser.add_argument("--publish-hz", type=float, default=2.0)
    parser.add_argument("--seed", type=int, default=1933)
    args = parser.parse_args()

    client = SimpleUDPClient(args.host, args.output_port)
    lab = HeisenbergLab(client, seed=args.seed)
    server = start_control_server(lab, args.host, args.control_port)
    print(
        "Heisenberg Laboratory v1: "
        f"16x16 field -> udp/{args.output_port}, controls <- udp/{args.control_port}"
    )
    try:
        interval = 1.0 / max(float(args.publish_hz), 0.1)
        while True:
            lab.publish()
            time.sleep(interval)
    except KeyboardInterrupt:
        pass
    finally:
        server.shutdown()
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
