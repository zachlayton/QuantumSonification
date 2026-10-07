#!/usr/bin/env python3
"""Send one four-qubit QAC/QASM circuit to IBM and return 16 counts.

The bridge accepts the existing chunked ``/qmw/qac`` OSC protocol from Max.
It deliberately stops at computational-basis measurement: no tomography,
Pauli reconstruction, QFT, wavetable generation, or other sonification layer
is performed here.
"""

from __future__ import annotations

import argparse
import threading
from dataclasses import dataclass, field
from urllib.parse import unquote

import numpy as np
from pythonosc import dispatcher, osc_server
from pythonosc.udp_client import SimpleUDPClient


ACCOUNT_NAME = "quantum-sonification-workshop"
NUM_QUBITS = 4
NUM_OUTCOMES = 1 << NUM_QUBITS


def load_qac_qasm(qasm: str):
    """Load flattened QAC OpenQASM 2 and remove any final measurements."""
    from qiskit import qasm2

    circuit = qasm2.loads(qasm).remove_final_measurements(inplace=False)
    if circuit.num_qubits != NUM_QUBITS:
        raise ValueError(
            f"This workshop accepts exactly {NUM_QUBITS} qubits; "
            f"received {circuit.num_qubits}"
        )
    return circuit


def ordered_counts(counts: dict[str, int]) -> list[int]:
    """Return Qiskit counts in |0000> ... |1111> display order."""
    ordered = [0] * NUM_OUTCOMES
    for label, value in counts.items():
        bits = str(label).replace(" ", "")
        if not bits or any(bit not in "01" for bit in bits):
            raise ValueError(f"Invalid IBM count label: {label!r}")
        if len(bits) > NUM_QUBITS:
            raise ValueError(f"Count label is wider than four qubits: {label!r}")
        ordered[int(bits.zfill(NUM_QUBITS), 2)] += int(value)
    return ordered


def probabilities_from_counts(counts: list[int]) -> list[float]:
    shots = sum(counts)
    if shots <= 0:
        raise ValueError("Measurement returned no counts")
    return [count / shots for count in counts]


def ideal_probabilities(qasm: str) -> list[float]:
    """Return the exact local reference without sampling."""
    from qiskit.quantum_info import Statevector

    state = Statevector.from_instruction(load_qac_qasm(qasm))
    probabilities = np.asarray(state.probabilities(), dtype=float)
    return probabilities.tolist()


def result_counts(pub_result) -> dict[str, int]:
    """Read the measurement register from a SamplerV2 PUB result."""
    data = pub_result.data
    if hasattr(data, "meas"):
        return dict(data.meas.get_counts())
    for name in dir(data):
        if name.startswith("_"):
            continue
        register = getattr(data, name)
        if hasattr(register, "get_counts"):
            return dict(register.get_counts())
    raise RuntimeError("IBM result does not contain a measurement register")


@dataclass
class IBMSubmission:
    job: object
    backend_name: str
    job_id: str


def submit_ibm(
    qasm: str,
    shots: int,
    account_name: str,
    backend_name: str | None = None,
) -> IBMSubmission:
    """Transpile and submit one four-qubit computational-basis Sampler job."""
    from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
    from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2

    circuit = load_qac_qasm(qasm)
    circuit.measure_all()
    service = QiskitRuntimeService(name=account_name)
    backend = (
        service.backend(backend_name)
        if backend_name
        else service.least_busy(
            operational=True,
            simulator=False,
            min_num_qubits=NUM_QUBITS,
        )
    )
    pass_manager = generate_preset_pass_manager(
        backend=backend,
        optimization_level=1,
    )
    isa_circuit = pass_manager.run(circuit)
    job = SamplerV2(mode=backend).run([isa_circuit], shots=shots)
    return IBMSubmission(job=job, backend_name=backend.name, job_id=job.job_id())


@dataclass
class Transfer:
    revision: int
    total: int
    chunks: dict[int, str] = field(default_factory=dict)

    def add(self, index: int, total: int, text: str) -> None:
        if total != self.total or not 0 <= index < self.total:
            raise ValueError("Invalid QASM chunk metadata")
        self.chunks[index] = text

    def assemble(self) -> str:
        missing = [index for index in range(self.total) if index not in self.chunks]
        if missing:
            raise ValueError(f"Incomplete QASM transfer; missing chunks {missing}")
        encoded = "".join(self.chunks[index] for index in range(self.total))
        return unquote(encoded)


class FourQubitCountsBridge:
    def __init__(self, args: argparse.Namespace):
        self.args = args
        self.client = SimpleUDPClient(args.out_host, args.out_port)
        self.transfer: Transfer | None = None
        self.latest_revision = -1
        self.jobs_started = 0
        self.job_in_flight: int | None = None
        self.lock = threading.RLock()

        routes = dispatcher.Dispatcher()
        routes.map("/qmw/qac/begin", self.begin)
        routes.map("/qmw/qac/chunk", self.chunk)
        routes.map("/qmw/qac/end", self.end)
        routes.map("/qmw/qac/qasm", self.qasm)
        routes.map("/qmw/ibm/ping", self.ping)
        routes.map("/qmw/ibm/reset", self.reset)
        self.server = osc_server.ThreadingOSCUDPServer(
            (args.in_host, args.in_port),
            routes,
        )

    def send(self, address: str, value) -> None:
        self.client.send_message(address, value)

    def status(self, *values) -> None:
        self.send("/qmw/ibm/status", list(values))

    def error(self, message: str) -> None:
        print(f"[four-qubit IBM bridge] {message}")
        self.send("/qmw/ibm/error", str(message))

    def begin(self, _address: str, revision: int, total: int) -> None:
        try:
            revision = int(revision)
            total = int(total)
            with self.lock:
                if revision <= self.latest_revision:
                    raise ValueError(f"Stale revision {revision}")
                if total < 1 or total > 4096:
                    raise ValueError("QASM transfer must contain 1..4096 chunks")
                self.transfer = Transfer(revision, total)
            self.status("receiving_qasm", revision, total)
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
                self.transfer.add(int(index), int(total), str(text))
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
        load_qac_qasm(qasm)
        with self.lock:
            if revision <= self.latest_revision:
                raise ValueError(f"Stale revision {revision}")
            self.latest_revision = revision
            if self.args.mode == "ibm":
                if self.job_in_flight is not None:
                    raise ValueError(
                        f"IBM job for revision {self.job_in_flight} is still running"
                    )
                if self.jobs_started >= self.args.ibm_max_jobs:
                    raise ValueError(
                        "IBM job limit reached; restart the bridge for another "
                        "deliberate submission"
                    )
                self.job_in_flight = revision
                self.jobs_started += 1

        self.status("qasm_validated", revision, NUM_QUBITS)
        if self.args.mode == "local":
            probabilities = ideal_probabilities(qasm)
            self.publish_probabilities(
                revision,
                "local",
                probabilities,
                "statevector",
                "none",
                0,
            )
            return

        threading.Thread(
            target=self.run_ibm,
            args=(revision, qasm),
            daemon=True,
        ).start()

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
                "IBM job submitted: "
                f"revision={revision} backend={submission.backend_name} "
                f"id={submission.job_id} shots={self.args.shots}"
            )
            result = submission.job.result()[0]
            counts = ordered_counts(result_counts(result))
            probabilities = probabilities_from_counts(counts)
            self.send(
                "/qmw/ibm/counts",
                [revision, "ibm", self.args.shots, *counts],
            )
            self.publish_probabilities(
                revision,
                "ibm",
                probabilities,
                submission.backend_name,
                submission.job_id,
                self.args.shots,
            )
        except Exception as exc:
            self.error(f"IBM revision {revision}: {exc}")
        finally:
            with self.lock:
                if self.job_in_flight == revision:
                    self.job_in_flight = None

    def publish_probabilities(
        self,
        revision: int,
        source: str,
        probabilities: list[float],
        backend: str,
        job_id: str,
        shots: int,
    ) -> None:
        if len(probabilities) != NUM_OUTCOMES:
            raise ValueError("Expected exactly 16 basis probabilities")
        self.send(
            "/qmw/ibm/probabilities",
            [revision, source, *probabilities],
        )
        self.send(
            "/qmw/ibm/result",
            [revision, source, backend, job_id, shots],
        )
        self.status("complete", revision, source)
        print(
            f"published 16 outcomes: revision={revision} source={source} "
            f"backend={backend} job={job_id}"
        )

    def ping(self, _address: str, *_args) -> None:
        self.status("ready", self.args.mode, self.latest_revision)

    def reset(self, _address: str, *_args) -> None:
        with self.lock:
            if self.job_in_flight is not None:
                self.error("Cannot reset while an IBM job is running")
                return
            self.transfer = None
            self.latest_revision = -1
        self.status("reset", self.args.mode, -1)

    def serve(self) -> None:
        print(
            f"QAC/QASM input: udp://{self.args.in_host}:{self.args.in_port}\n"
            f"16-outcome output: udp://{self.args.out_host}:{self.args.out_port}\n"
            f"mode={self.args.mode} shots={self.args.shots} "
            f"max_ibm_jobs={self.args.ibm_max_jobs}"
        )
        self.status("ready", self.args.mode, self.latest_revision)
        self.server.serve_forever()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("local", "ibm"), default="local")
    parser.add_argument(
        "--confirm-ibm",
        action="store_true",
        help="required acknowledgement before a real hardware job can be submitted",
    )
    parser.add_argument("--shots", type=int, default=256)
    parser.add_argument("--backend", help="IBM backend name; default selects least busy")
    parser.add_argument("--account", default=ACCOUNT_NAME)
    parser.add_argument("--ibm-max-jobs", type=int, default=1)
    parser.add_argument("--in-host", default="127.0.0.1")
    parser.add_argument("--in-port", type=int, default=7401)
    parser.add_argument("--out-host", default="127.0.0.1")
    parser.add_argument("--out-port", type=int, default=7412)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    if args.mode == "ibm" and not args.confirm_ibm:
        raise SystemExit(
            "IBM mode requires --confirm-ibm. Use --mode local for rehearsal."
        )
    if args.shots < 1:
        raise SystemExit("--shots must be at least 1")
    if args.ibm_max_jobs < 1:
        raise SystemExit("--ibm-max-jobs must be at least 1")
    try:
        FourQubitCountsBridge(args).serve()
    except KeyboardInterrupt:
        print("\nbridge stopped")


if __name__ == "__main__":
    main()
