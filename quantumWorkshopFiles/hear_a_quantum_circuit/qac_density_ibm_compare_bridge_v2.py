#!/usr/bin/env python3
"""Compare an ideal four-qubit density matrix with IBM measurement data.

The bridge accepts the workshop's existing chunked QAC/QASM protocol on UDP
7413.  It always publishes the ideal statevector density matrix immediately.
When IBM is armed from Max, the next QASM revision is also submitted to one
IBM Quantum backend.  Its sixteen computational-basis probabilities define
the explicitly labelled diagonal estimate ``rho_diag``.

One measurement basis cannot reconstruct the hardware's off-diagonal
coherences.  Full hardware density-matrix tomography is deliberately outside
this compact workshop comparison.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass, field
import threading
import time
from urllib.parse import unquote

import numpy as np
from pythonosc import dispatcher, osc_server
from pythonosc.udp_client import SimpleUDPClient

try:
    from .qac_density_morph_bridge_v1 import (
        NUM_QUBITS,
        TABLE_SIZE,
        RenderConfig,
        circuit_density,
        density_metrics,
        density_to_table,
        evolve_density_matrix,
        make_hamiltonian,
        probabilities_to_table,
    )
    from .qac_ibm_counts_bridge_v1 import (
        ACCOUNT_NAME,
        ordered_counts,
        probabilities_from_counts,
        result_counts,
        submit_ibm,
    )
except ImportError:
    from qac_density_morph_bridge_v1 import (
        NUM_QUBITS,
        TABLE_SIZE,
        RenderConfig,
        circuit_density,
        density_metrics,
        density_to_table,
        evolve_density_matrix,
        make_hamiltonian,
        probabilities_to_table,
    )
    from qac_ibm_counts_bridge_v1 import (
        ACCOUNT_NAME,
        ordered_counts,
        probabilities_from_counts,
        result_counts,
        submit_ibm,
    )


@dataclass
class Transfer:
    revision: int
    total: int
    chunks: dict[int, str] = field(default_factory=dict)

    def add(self, index: int, total: int, text: str) -> None:
        if int(total) != self.total or not 0 <= int(index) < self.total:
            raise ValueError("Invalid QASM chunk metadata")
        self.chunks[int(index)] = str(text)

    def assemble(self) -> str:
        missing = [index for index in range(self.total) if index not in self.chunks]
        if missing:
            raise ValueError(f"Incomplete QASM transfer; missing chunks {missing}")
        return unquote("".join(self.chunks[index] for index in range(self.total)))


def diagonal_density(probabilities) -> np.ndarray:
    """Return the measurement-derived diagonal density estimate."""

    values = np.asarray(probabilities, dtype=np.float64).reshape(-1)
    if values.shape != (1 << NUM_QUBITS,):
        raise ValueError("Expected exactly sixteen basis probabilities")
    if np.any(values < -1.0e-12):
        raise ValueError("Probabilities must be nonnegative")
    total = float(np.sum(values))
    if total <= 0.0:
        raise ValueError("Probability total must be positive")
    values = np.clip(values / total, 0.0, None)
    return np.diag(values.astype(np.complex128))


def total_variation_distance(reference, observed) -> float:
    """Return the directly comparable population distance in [0, 1]."""

    ideal = np.asarray(reference, dtype=np.float64).reshape(-1)
    hardware = np.asarray(observed, dtype=np.float64).reshape(-1)
    if ideal.shape != hardware.shape:
        raise ValueError("Probability vectors must have matching shapes")
    return float(np.clip(0.5 * np.sum(np.abs(ideal - hardware)), 0.0, 1.0))


class DensityIBMCompareBridge:
    def __init__(self, args: argparse.Namespace):
        self.args = args
        self.client = SimpleUDPClient(args.out_host, args.out_port)
        self.v1_client = SimpleUDPClient(args.out_host, args.v1_out_port)
        self.config = RenderConfig(
            n_qubits=NUM_QUBITS,
            wavetable_size=TABLE_SIZE,
            mapping="real",
            frames_per_second=args.fps,
            seed=args.seed,
            hamiltonian_scale=args.hamiltonian_scale,
            drive_strength=args.drive_strength,
            decoherence=args.decoherence,
        )
        self.hamiltonian = make_hamiltonian(
            self.config,
            np.random.default_rng(args.seed),
        )
        self.lock = threading.RLock()
        self.transfer: Transfer | None = None
        self.latest_revision = -1
        self.ibm_armed = False
        self.ibm_jobs_started = 0
        self.ibm_in_flight: int | None = None
        self.ideal_probabilities: dict[int, np.ndarray] = {}
        self.v1_rho: np.ndarray | None = None
        self.v1_initial_rho: np.ndarray | None = None
        self.v1_frame = 0
        self.v1_logical_time = 0.0
        self.v1_playing = False
        self.v1_rate = 1.0
        self.ibm_rho: np.ndarray | None = None
        self.ibm_initial_rho: np.ndarray | None = None
        self.ibm_frame = 0
        self.ibm_logical_time = 0.0
        self.stopping = threading.Event()

        routes = dispatcher.Dispatcher()
        routes.map("/qmw/qac/begin", self.begin)
        routes.map("/qmw/qac/chunk", self.chunk)
        routes.map("/qmw/qac/end", self.end)
        routes.map("/qmw/qac/qasm", self.qasm)
        routes.map(
            "/qmw/density_compare/control/ibm",
            self.set_ibm_armed,
        )
        routes.map("/qmw/density_compare/ping", self.ping)
        routes.map("/qmw/density_compare/reset", self.reset)
        routes.map("/qmw/density/control/play", self.set_v1_play)
        routes.map("/qmw/density/control/rate", self.set_v1_rate)
        routes.map("/qmw/density/control/reset", self.reset_v1)
        routes.map("/qmw/density/ping", self.ping_v1)
        self.server = osc_server.ThreadingOSCUDPServer(
            (args.in_host, args.in_port),
            routes,
        )

    def send(self, address: str, values) -> None:
        self.client.send_message(address, values)

    def send_v1(self, address: str, values) -> None:
        """Publish V1 compatibility to both normal and side-by-side ports."""

        self.client.send_message(address, values)
        if self.args.v1_out_port != self.args.out_port:
            self.v1_client.send_message(address, values)

    def status(self, *values) -> None:
        self.send("/qmw/density_compare/status", list(values))

    def error(self, message: str) -> None:
        print(f"[density IBM comparison] {message}")
        self.send("/qmw/density_compare/error", str(message))

    def begin(self, _address: str, revision: int, total: int) -> None:
        try:
            revision, total = int(revision), int(total)
            with self.lock:
                if revision <= self.latest_revision:
                    raise ValueError(f"Stale QASM revision {revision}")
                if not 1 <= total <= 4096:
                    raise ValueError("QASM transfer must contain 1..4096 chunks")
                self.transfer = Transfer(revision, total)
            self.status("receiving_qasm", revision)
        except Exception as exc:
            self.error(str(exc))

    def chunk(
        self,
        _address: str,
        revision: int,
        index: int,
        total: int,
        text: str,
    ) -> None:
        try:
            with self.lock:
                if self.transfer is None or self.transfer.revision != int(revision):
                    raise ValueError(f"No active transfer for revision {revision}")
                self.transfer.add(index, total, text)
        except Exception as exc:
            self.error(str(exc))

    def end(self, _address: str, revision: int) -> None:
        try:
            with self.lock:
                if self.transfer is None or self.transfer.revision != int(revision):
                    raise ValueError(f"No active transfer for revision {revision}")
                qasm = self.transfer.assemble()
                self.transfer = None
            self.accept(int(revision), qasm)
        except Exception as exc:
            self.error(str(exc))

    def qasm(self, _address: str, revision: int, text: str) -> None:
        try:
            self.accept(int(revision), unquote(str(text)))
        except Exception as exc:
            self.error(str(exc))

    def accept(self, revision: int, qasm: str) -> None:
        probabilities, ideal_rho = circuit_density(qasm)
        ibm_skip_reason = None
        with self.lock:
            if revision <= self.latest_revision:
                raise ValueError(f"Stale QASM revision {revision}")
            self.latest_revision = revision
            self.ideal_probabilities[revision] = probabilities.copy()
            launch_ibm = self.ibm_armed
            if launch_ibm:
                if not self.args.confirm_ibm:
                    launch_ibm = False
                    ibm_skip_reason = "restart_bridge_with_--confirm-ibm"
                elif self.ibm_in_flight is not None:
                    launch_ibm = False
                    ibm_skip_reason = f"job_{self.ibm_in_flight}_still_running"
                elif self.ibm_jobs_started >= self.args.ibm_max_jobs:
                    launch_ibm = False
                    ibm_skip_reason = "session_job_limit_reached"
                else:
                    self.ibm_in_flight = revision
                    self.ibm_jobs_started += 1

        self.publish_density(revision, "ideal", ideal_rho)
        ideal_harmonic = probabilities_to_table(probabilities)
        self.send(
            "/qmw/density_compare/ideal_harmonic",
            [revision, *ideal_harmonic.tolist()],
        )
        self.send(
            "/qmw/density_compare/probabilities",
            [revision, "ideal", *probabilities.tolist()],
        )
        self.seed_v1_compatibility(revision, probabilities, ideal_rho)
        self.status("ideal_ready", revision)

        if launch_ibm:
            threading.Thread(
                target=self.run_ibm,
                args=(revision, qasm),
                daemon=True,
            ).start()
        elif ibm_skip_reason:
            self.status("local_only", revision, ibm_skip_reason)
        else:
            self.status("local_only", revision, "toggle_ibm_then_send_qasm")

    def run_ibm(self, revision: int, qasm: str) -> None:
        try:
            self.status("selecting_backend", revision)
            submission = submit_ibm(
                qasm,
                self.args.shots,
                self.args.account,
                self.args.backend,
            )
            self.status(
                "submitted",
                revision,
                submission.backend_name,
                submission.job_id,
                self.args.shots,
            )
            print(
                "IBM comparison job submitted: "
                f"revision={revision} backend={submission.backend_name} "
                f"id={submission.job_id} shots={self.args.shots}"
            )
            result = submission.job.result()[0]
            counts = ordered_counts(result_counts(result))
            probabilities = np.asarray(
                probabilities_from_counts(counts),
                dtype=np.float64,
            )
            rho_diag = diagonal_density(probabilities)
            with self.lock:
                ideal = self.ideal_probabilities.get(revision)
                self.ibm_rho = rho_diag.copy()
                self.ibm_initial_rho = rho_diag.copy()
                self.ibm_frame = 0
                self.ibm_logical_time = 0.0
            if ideal is None:
                raise RuntimeError("Ideal reference was lost before IBM completed")
            distance = total_variation_distance(ideal, probabilities)
            self.send(
                "/qmw/density_compare/counts",
                [revision, self.args.shots, *counts],
            )
            self.send(
                "/qmw/density_compare/probabilities",
                [revision, "ibm", *probabilities.tolist()],
            )
            self.publish_density(revision, "ibm_diag", rho_diag)
            self.publish_ibm_frame(
                revision,
                density_to_table(rho_diag, self.config),
                density_metrics(rho_diag),
            )
            hardware_harmonic = probabilities_to_table(probabilities)
            self.send(
                "/qmw/density_compare/ibm_harmonic",
                [revision, *hardware_harmonic.tolist()],
            )
            self.send(
                "/qmw/density_compare/comparison",
                [revision, distance],
            )
            self.send(
                "/qmw/density_compare/result",
                [
                    revision,
                    submission.backend_name,
                    submission.job_id,
                    self.args.shots,
                ],
            )
            self.status(
                "ibm_ready",
                revision,
                submission.backend_name,
                f"population_tvd={distance:.6f}",
            )
        except Exception as exc:
            self.error(f"IBM revision {revision}: {exc}")
        finally:
            with self.lock:
                if self.ibm_in_flight == revision:
                    self.ibm_in_flight = None

    def publish_density(
        self,
        revision: int,
        source: str,
        rho: np.ndarray,
    ) -> None:
        table = density_to_table(rho, self.config)
        metrics = density_metrics(rho)
        address = (
            "/qmw/density_compare/ideal"
            if source == "ideal"
            else "/qmw/density_compare/ibm"
        )
        self.send(address, [revision, *table.tolist()])
        self.send(
            "/qmw/density_compare/metrics",
            [revision, source, *metrics],
        )

    def seed_v1_compatibility(
        self,
        revision: int,
        probabilities: np.ndarray,
        ideal_rho: np.ndarray,
    ) -> None:
        """Publish the same circuit to the V1 density-morph protocol."""

        static_table = probabilities_to_table(probabilities)
        with self.lock:
            self.v1_rho = ideal_rho.copy()
            self.v1_initial_rho = ideal_rho.copy()
            self.v1_frame = 0
            self.v1_logical_time = 0.0
            self.v1_playing = False
            table = density_to_table(self.v1_rho, self.config)
            metrics = density_metrics(self.v1_rho)
        self.send_v1(
            "/qmw/density/static",
            [revision, *static_table.tolist()],
        )
        self.publish_v1_frame(revision, table, metrics)
        self.send_v1(
            "/qmw/density/status",
            ["seeded_by_shared_bridge", revision, "paused"],
        )

    def publish_v1_frame(
        self,
        revision: int,
        table: np.ndarray,
        metrics: tuple[float, float, float],
    ) -> None:
        self.send_v1(
            "/qmw/density/frame",
            [
                revision,
                self.v1_frame,
                *np.asarray(table, dtype=float).tolist(),
            ],
        )
        self.send_v1(
            "/qmw/density/metrics",
            [revision, self.v1_frame, *metrics],
        )
        self.send(
            "/qmw/density_compare/ideal_frame",
            [
                revision,
                self.v1_frame,
                *metrics,
                *np.asarray(table, dtype=float).tolist(),
            ],
        )

    def publish_ibm_frame(
        self,
        revision: int,
        table: np.ndarray,
        metrics: tuple[float, float, float],
    ) -> None:
        self.send(
            "/qmw/density_compare/ibm_frame",
            [
                revision,
                self.ibm_frame,
                *metrics,
                *np.asarray(table, dtype=float).tolist(),
            ],
        )

    def set_v1_play(self, _address: str, value: int | float) -> None:
        with self.lock:
            self.v1_playing = bool(int(value)) and self.v1_rho is not None
            playing = self.v1_playing
            revision, frame = self.latest_revision, self.v1_frame
        self.send_v1(
            "/qmw/density/status",
            ["playing" if playing else "paused", revision, frame],
        )
        self.status("playing" if playing else "paused", revision, frame)

    def set_v1_rate(self, _address: str, value: float) -> None:
        with self.lock:
            self.v1_rate = float(np.clip(float(value), 0.1, 4.0))
            rate = self.v1_rate
        self.send_v1("/qmw/density/status", ["rate", rate])
        self.status("rate", rate)

    def reset_v1(self, _address: str, *_args) -> None:
        with self.lock:
            if self.v1_initial_rho is None:
                self.error("Build a circuit before resetting V1")
                return
            self.v1_rho = self.v1_initial_rho.copy()
            self.v1_frame = 0
            self.v1_logical_time = 0.0
            self.v1_playing = False
            table = density_to_table(self.v1_rho, self.config)
            metrics = density_metrics(self.v1_rho)
            revision = self.latest_revision
            ibm_payload = None
            if self.ibm_initial_rho is not None:
                self.ibm_rho = self.ibm_initial_rho.copy()
                self.ibm_frame = 0
                self.ibm_logical_time = 0.0
                ibm_payload = (
                    density_to_table(self.ibm_rho, self.config),
                    density_metrics(self.ibm_rho),
                )
        self.publish_v1_frame(revision, table, metrics)
        if ibm_payload is not None:
            self.publish_ibm_frame(revision, *ibm_payload)
        self.send_v1("/qmw/density/status", ["reset", revision, 0])
        self.status("reset", revision, 0)

    def ping_v1(self, _address: str, *_args) -> None:
        self.send_v1(
            "/qmw/density/status",
            ["ready_shared_bridge", self.latest_revision, self.v1_frame],
        )

    def evolve_v1_loop(self) -> None:
        interval = 1.0 / self.args.fps
        while not self.stopping.wait(interval):
            with self.lock:
                if not self.v1_playing or self.v1_rho is None:
                    continue
                dt = interval * self.v1_rate
                self.v1_rho = evolve_density_matrix(
                    self.v1_rho,
                    self.hamiltonian,
                    self.v1_logical_time,
                    dt,
                    self.config,
                )
                self.v1_logical_time += dt
                self.v1_frame += 1
                table = density_to_table(self.v1_rho, self.config)
                metrics = density_metrics(self.v1_rho)
                revision = self.latest_revision
                ibm_payload = None
                if self.ibm_rho is not None:
                    self.ibm_rho = evolve_density_matrix(
                        self.ibm_rho,
                        self.hamiltonian,
                        self.ibm_logical_time,
                        dt,
                        self.config,
                    )
                    self.ibm_logical_time += dt
                    self.ibm_frame += 1
                    ibm_payload = (
                        density_to_table(self.ibm_rho, self.config),
                        density_metrics(self.ibm_rho),
                    )
            self.publish_v1_frame(revision, table, metrics)
            if ibm_payload is not None:
                self.publish_ibm_frame(revision, *ibm_payload)

    def set_ibm_armed(self, _address: str, value: int | float) -> None:
        armed = bool(int(value))
        with self.lock:
            if not armed and self.ibm_in_flight is not None:
                self.ibm_armed = False
                self.status(
                    "local_selected_job_continues",
                    self.ibm_in_flight,
                )
                return
            self.ibm_armed = armed
        if armed and not self.args.confirm_ibm:
            self.status("ibm_unavailable", "restart_with_--confirm-ibm")
        elif armed:
            self.status("ibm_armed", "next_send_qasm_submits_one_job")
        else:
            self.status("local_selected")

    def ping(self, _address: str, *_args) -> None:
        self.status(
            "ready",
            "ibm_capable" if self.args.confirm_ibm else "local_safe",
            self.latest_revision,
        )

    def reset(self, _address: str, *_args) -> None:
        with self.lock:
            if self.ibm_in_flight is not None:
                self.error("Cannot reset while an IBM job is running")
                return
            self.transfer = None
            self.latest_revision = -1
            self.ibm_armed = False
            self.ideal_probabilities.clear()
            self.v1_rho = None
            self.v1_initial_rho = None
            self.v1_frame = 0
            self.v1_logical_time = 0.0
            self.v1_playing = False
            self.ibm_rho = None
            self.ibm_initial_rho = None
            self.ibm_frame = 0
            self.ibm_logical_time = 0.0
        self.status("reset", "local_selected")

    def serve(self) -> None:
        worker = threading.Thread(target=self.evolve_v1_loop, daemon=True)
        worker.start()
        print(
            f"QAC + mode input: udp://{self.args.in_host}:{self.args.in_port}\n"
            f"density comparison: udp://{self.args.out_host}:{self.args.out_port}\n"
            f"V1 side-by-side return: "
            f"udp://{self.args.out_host}:{self.args.v1_out_port}\n"
            f"shots={self.args.shots} IBM capability="
            f"{'armed by Max toggle' if self.args.confirm_ibm else 'disabled'}\n"
            "hardware mapping: 16 measured populations -> diagonal rho estimate\n"
            "shared mode: V1 density evolution and V2 IBM comparison"
        )
        self.ping("")
        try:
            self.server.serve_forever()
        finally:
            self.stopping.set()
            self.server.server_close()
            worker.join(timeout=1.0)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--confirm-ibm",
        action="store_true",
        help="allow the Max IBM toggle to submit a real hardware job",
    )
    parser.add_argument("--shots", type=int, default=1024)
    parser.add_argument("--backend", help="IBM backend name; default selects least busy")
    parser.add_argument("--account", default=ACCOUNT_NAME)
    parser.add_argument("--ibm-max-jobs", type=int, default=1)
    parser.add_argument("--fps", type=float, default=15.0)
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--hamiltonian-scale", type=float, default=1.0)
    parser.add_argument("--drive-strength", type=float, default=0.20)
    parser.add_argument("--decoherence", type=float, default=0.015)
    parser.add_argument("--in-host", default="127.0.0.1")
    parser.add_argument("--in-port", type=int, default=7413)
    parser.add_argument("--out-host", default="127.0.0.1")
    parser.add_argument("--out-port", type=int, default=7412)
    parser.add_argument("--v1-out-port", type=int, default=7422)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.shots < 1:
        raise SystemExit("--shots must be at least 1")
    if args.ibm_max_jobs < 1:
        raise SystemExit("--ibm-max-jobs must be at least 1")
    if not 1.0 <= args.fps <= 30.0:
        raise SystemExit("--fps must be between 1 and 30")
    try:
        DensityIBMCompareBridge(args).serve()
    except KeyboardInterrupt:
        pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
