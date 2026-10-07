#!/usr/bin/env python3
"""Quantum Relations OSC v1.

Computes basis-dependent superposition, subsystem correlations, and measurement
events from a density matrix, then broadcasts them for the eigenfield timing
layer and Processing visualizer.

Default OSC:
    output: 7450
    control: 7451

Dependencies:
    numpy
    python-osc
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path
import argparse
import queue
import signal
import threading
import time
from typing import Any

import numpy as np
from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import ThreadingOSCUDPServer
from pythonosc.udp_client import SimpleUDPClient


I2 = np.eye(2, dtype=np.complex128)
H = np.array([[1, 1], [1, -1]], dtype=np.complex128) / np.sqrt(2.0)
SDG = np.array([[1, 0], [0, -1j]], dtype=np.complex128)


@dataclass(frozen=True)
class RelationConfig:
    rate_hz: float = 30.0
    measurement_mode: str = "probe"
    basis: str = "Z"
    seed: int = 23
    watch_file: bool = True


def validate_rho(rho: np.ndarray) -> np.ndarray:
    rho = np.asarray(rho, dtype=np.complex128)
    if rho.ndim != 2 or rho.shape[0] != rho.shape[1]:
        raise ValueError("rho must be square")
    rho = 0.5 * (rho + rho.conj().T)
    trace = np.trace(rho)
    if abs(trace) < 1e-12:
        raise ValueError("rho has zero trace")
    rho /= trace
    values, vectors = np.linalg.eigh(rho)
    values = np.clip(values.real, 0.0, None)
    values /= max(float(np.sum(values)), 1e-15)
    return (vectors * values[None, :]) @ vectors.conj().T


def infer_qubits(dimension: int) -> int:
    n = int(round(np.log2(dimension)))
    if 2**n != dimension:
        raise ValueError("density-matrix dimension must be a power of two")
    return n


def entropy(rho: np.ndarray) -> float:
    values = np.clip(np.linalg.eigvalsh(rho).real, 1e-15, 1.0)
    return float(-np.sum(values * np.log2(values)))


def partial_trace(rho: np.ndarray, keep: list[int], n_qubits: int) -> np.ndarray:
    keep = sorted(keep)
    trace_out = [q for q in range(n_qubits) if q not in keep]
    tensor = rho.reshape([2] * (2 * n_qubits))
    current_n = n_qubits
    for q in sorted(trace_out, reverse=True):
        tensor = np.trace(tensor, axis1=q, axis2=q + current_n)
        current_n -= 1
    dimension = 2 ** len(keep)
    return tensor.reshape(dimension, dimension)


def kron_all(operators: list[np.ndarray]) -> np.ndarray:
    result = np.array([[1.0 + 0.0j]])
    for operator in operators:
        result = np.kron(result, operator)
    return result


def basis_unitary(basis: str, n_qubits: int) -> np.ndarray:
    basis = basis.upper()
    if basis == "Z":
        single = I2
    elif basis == "X":
        single = H
    elif basis == "Y":
        single = H @ SDG
    else:
        raise ValueError("basis must be X, Y, or Z")
    return kron_all([single] * n_qubits)


def basis_probabilities(rho: np.ndarray, basis: str) -> np.ndarray:
    n = infer_qubits(rho.shape[0])
    unitary = basis_unitary(basis, n)
    rotated = unitary @ rho @ unitary.conj().T
    probabilities = np.clip(np.real(np.diag(rotated)), 0.0, None)
    return probabilities / max(float(np.sum(probabilities)), 1e-15)


def superposition_metrics(rho: np.ndarray, basis: str) -> dict[str, float]:
    p = basis_probabilities(rho, basis)
    h = float(-np.sum(p * np.log2(np.maximum(p, 1e-15))))
    maximum = float(np.log2(len(p)))
    participation = float(1.0 / max(np.sum(p**2), 1e-15))
    return {
        "entropy_bits": h,
        "entropy_normalized": h / max(maximum, 1e-15),
        "participation": participation,
        "participation_normalized": participation / len(p),
    }


def pair_mutual_information(
    rho: np.ndarray, i: int, j: int, n_qubits: int
) -> float:
    rho_i = partial_trace(rho, [i], n_qubits)
    rho_j = partial_trace(rho, [j], n_qubits)
    rho_ij = partial_trace(rho, [i, j], n_qubits)
    return entropy(rho_i) + entropy(rho_j) - entropy(rho_ij)


def concurrence_two_qubit(rho: np.ndarray) -> float:
    if rho.shape != (4, 4):
        return 0.0
    sy = np.array([[0, -1j], [1j, 0]], dtype=np.complex128)
    yy = np.kron(sy, sy)
    flipped = yy @ rho.conj() @ yy
    eigenvalues = np.linalg.eigvals(rho @ flipped)
    roots = np.sort(np.sqrt(np.clip(np.real(eigenvalues), 0.0, None)))[::-1]
    return float(max(0.0, roots[0] - np.sum(roots[1:])))


def relation_metrics(rho: np.ndarray) -> dict[str, Any]:
    n = infer_qubits(rho.shape[0])
    purity = float(np.real(np.trace(rho @ rho)))
    global_entropy = entropy(rho)

    local_entropies = []
    for q in range(n):
        local_entropies.append(entropy(partial_trace(rho, [q], n)))

    mutual_information = np.zeros((n, n), dtype=np.float64)
    concurrence = np.zeros((n, n), dtype=np.float64)
    for i in range(n):
        for j in range(i + 1, n):
            mutual_information[i, j] = mutual_information[j, i] = (
                pair_mutual_information(rho, i, j, n)
            )
            pair = partial_trace(rho, [i, j], n)
            concurrence[i, j] = concurrence[j, i] = concurrence_two_qubit(pair)

    return {
        "n_qubits": n,
        "purity": purity,
        "global_entropy_bits": global_entropy,
        "local_entropies": np.asarray(local_entropies),
        "mutual_information": mutual_information,
        "concurrence": concurrence,
        "superposition": {
            basis: superposition_metrics(rho, basis)
            for basis in ("X", "Y", "Z")
        },
    }


class QuantumRelationsOSC:
    def __init__(
        self,
        rho_path: Path,
        rho_key: str,
        out_host: str,
        out_port: int,
        control_host: str,
        control_port: int,
        config: RelationConfig,
    ) -> None:
        self.rho_path = rho_path
        self.rho_key = rho_key
        self.client = SimpleUDPClient(out_host, out_port)
        self.config = config
        self.rng = np.random.default_rng(config.seed)
        self.rho = self._load_rho()
        self.modified_time = rho_path.stat().st_mtime
        self.metrics = relation_metrics(self.rho)

        self.alive = True
        self.commands: queue.SimpleQueue[tuple[str, tuple[Any, ...]]] = queue.SimpleQueue()
        dispatcher = Dispatcher()
        dispatcher.set_default_handler(self._enqueue)
        self.server = ThreadingOSCUDPServer((control_host, control_port), dispatcher)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)

    def _load_rho(self) -> np.ndarray:
        payload = np.load(self.rho_path)
        if isinstance(payload, np.ndarray):
            rho = payload
        elif self.rho_key in payload:
            rho = payload[self.rho_key]
        else:
            candidates = [k for k in payload.files if payload[k].ndim == 2]
            if not candidates:
                raise ValueError("no matrix found in density-matrix file")
            rho = payload[candidates[0]]
        return validate_rho(rho)

    def _enqueue(self, address: str, *args: Any) -> None:
        self.commands.put((address, tuple(args)))

    def _projector(self, outcome: int, basis: str) -> np.ndarray:
        n = infer_qubits(self.rho.shape[0])
        ket = np.zeros(2**n, dtype=np.complex128)
        ket[outcome] = 1.0
        unitary = basis_unitary(basis, n)
        basis_ket = unitary.conj().T @ ket
        return np.outer(basis_ket, basis_ket.conj())

    def measure(self, basis: str | None = None, mode: str | None = None) -> None:
        basis = (basis or self.config.basis).upper()
        mode = (mode or self.config.measurement_mode).lower()
        probabilities = basis_probabilities(self.rho, basis)
        outcome = int(self.rng.choice(len(probabilities), p=probabilities))
        probability = float(probabilities[outcome])

        self.client.send_message("/quantum/measurement/basis", basis)
        self.client.send_message("/quantum/measurement/outcome", outcome)
        self.client.send_message("/quantum/measurement/probability", probability)
        self.client.send_message("/quantum/measurement/mode", mode)
        self.client.send_message(
            "/quantum/measurement/bitstring",
            format(outcome, f"0{infer_qubits(self.rho.shape[0])}b"),
        )
        self.client.send_message("/quantum/measurement/flash", 1)

        if mode == "collapse":
            projector = self._projector(outcome, basis)
            numerator = projector @ self.rho @ projector
            self.rho = validate_rho(numerator / max(probability, 1e-15))
            self.metrics = relation_metrics(self.rho)
            self.send_metrics()

    def _process(self, address: str, args: tuple[Any, ...]) -> None:
        prefix = "/quantum/relations/control/"
        if not address.startswith(prefix):
            return
        command = address[len(prefix):]

        if command == "basis":
            value = str(args[0]).upper()
            if value not in {"X", "Y", "Z"}:
                raise ValueError("basis must be X, Y, or Z")
            self.config = replace(self.config, basis=value)
        elif command == "measurement_mode":
            value = str(args[0]).lower()
            if value not in {"probe", "collapse"}:
                raise ValueError("measurement mode must be probe or collapse")
            self.config = replace(self.config, measurement_mode=value)
        elif command == "measure":
            basis = str(args[0]).upper() if args else self.config.basis
            self.measure(basis=basis)
        elif command == "reload":
            self.rho = self._load_rho()
            self.metrics = relation_metrics(self.rho)
            self.send_metrics()
        elif command == "status":
            self.send_metrics()
        elif command == "quit":
            self.alive = False
        else:
            raise ValueError(f"unknown command {address}")

    def drain(self) -> None:
        while True:
            try:
                address, args = self.commands.get_nowait()
            except queue.Empty:
                return
            try:
                self._process(address, args)
            except Exception as exc:
                self.client.send_message("/quantum/relations/error", str(exc))

    def send_metrics(self) -> None:
        m = self.metrics
        n = m["n_qubits"]
        self.client.send_message("/quantum/global/purity", m["purity"])
        self.client.send_message(
            "/quantum/global/entropy_bits", m["global_entropy_bits"]
        )

        for basis in ("X", "Y", "Z"):
            s = m["superposition"][basis]
            low = basis.lower()
            self.client.send_message(
                f"/quantum/superposition/{low}", s["entropy_normalized"]
            )
            self.client.send_message(
                f"/quantum/participation/{low}",
                s["participation_normalized"],
            )

        for q, value in enumerate(m["local_entropies"]):
            self.client.send_message(
                f"/quantum/entanglement/q/{q}", float(value)
            )

        for i in range(n):
            for j in range(i + 1, n):
                self.client.send_message(
                    f"/quantum/mutual_information/{i}/{j}",
                    float(m["mutual_information"][i, j]),
                )
                self.client.send_message(
                    f"/quantum/concurrence/{i}/{j}",
                    float(m["concurrence"][i, j]),
                )

        # Compact flattened matrices for visualization.
        self.client.send_message(
            "/quantum/mutual_information/matrix",
            m["mutual_information"].reshape(-1).tolist(),
        )
        self.client.send_message(
            "/quantum/concurrence/matrix",
            m["concurrence"].reshape(-1).tolist(),
        )
        self.client.send_message("/quantum/relations/qubits", n)

    def run(self) -> None:
        self.thread.start()
        self.send_metrics()
        print("Quantum Relations OSC v1")
        print(f"  rho:      {self.rho_path}")
        print(f"  qubits:   {self.metrics['n_qubits']}")
        print(f"  basis:    {self.config.basis}")
        print(f"  mode:     {self.config.measurement_mode}")

        next_tick = time.perf_counter()
        try:
            while self.alive:
                self.drain()
                if self.config.watch_file:
                    modified = self.rho_path.stat().st_mtime
                    if modified > self.modified_time:
                        self.modified_time = modified
                        self.rho = self._load_rho()
                        self.metrics = relation_metrics(self.rho)
                        self.send_metrics()

                next_tick += 1.0 / max(self.config.rate_hz, 1.0)
                delay = next_tick - time.perf_counter()
                if delay > 0:
                    time.sleep(delay)
                else:
                    next_tick = time.perf_counter()
        finally:
            self.server.shutdown()
            self.server.server_close()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("rho", type=Path)
    parser.add_argument("--rho-key", default="rho")
    parser.add_argument("--out-host", default="127.0.0.1")
    parser.add_argument("--out-port", type=int, default=7450)
    parser.add_argument("--control-host", default="127.0.0.1")
    parser.add_argument("--control-port", type=int, default=7451)
    parser.add_argument("--basis", choices=["X", "Y", "Z"], default="Z")
    parser.add_argument(
        "--measurement-mode",
        choices=["probe", "collapse"],
        default="probe",
    )
    parser.add_argument("--rate", type=float, default=30.0)
    parser.add_argument("--seed", type=int, default=23)
    parser.add_argument("--no-watch", action="store_true")
    args = parser.parse_args()

    app = QuantumRelationsOSC(
        rho_path=args.rho,
        rho_key=args.rho_key,
        out_host=args.out_host,
        out_port=args.out_port,
        control_host=args.control_host,
        control_port=args.control_port,
        config=RelationConfig(
            rate_hz=args.rate,
            measurement_mode=args.measurement_mode,
            basis=args.basis,
            seed=args.seed,
            watch_file=not args.no_watch,
        ),
    )

    def stop(_signum: int, _frame: Any) -> None:
        app.alive = False

    signal.signal(signal.SIGINT, stop)
    signal.signal(signal.SIGTERM, stop)
    app.run()


if __name__ == "__main__":
    main()
