#!/usr/bin/env python3
"""Compare one frozen I Ching oracle circuit locally and on IBM hardware.

V1 uses four measurement circuits: the eight-qubit computational-basis cast
and three commuting Pauli families (ZX, XZ, YY) that recover the same eighteen
correlators used by ``qmw_iching_oracle8_v2.moving_probs``.  Local and hardware
routes remain explicit; hardware data never replaces the local reading.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import threading
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Sequence

import numpy as np

import qmw_iching_oracle8_v2 as oracle
from qmw_iching_comparison_sonification_v1 import (
    ComparisonAudioPlayer,
    ComparisonSonificationConfig,
)

ACCOUNT_NAME = "quantum-sonification-workshop"
IBM_ROOT = "/qmw/iching/ibm"
FAMILY_NAMES = ("cast", "zx", "xz", "yy")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def unsigned_int32(value: int) -> int:
    return int(value) & 0xFFFFFFFF


def signed_int32(value: int) -> int:
    value = unsigned_int32(value)
    return value if value < 0x80000000 else value - 0x100000000


def _backend_name(backend: Any) -> str:
    value = getattr(backend, "name", "unknown")
    return str(value() if callable(value) else value)


def _job_id(job: Any) -> str:
    value = getattr(job, "job_id")
    return str(value() if callable(value) else value)


def build_qiskit_oracle_circuit(seed: int, depth: int = 3):
    """Translate ``oracle.build`` gate-for-gate into a Qiskit circuit."""
    from qiskit import QuantumCircuit

    seed = unsigned_int32(seed)
    rng = np.random.default_rng(seed)
    circuit = QuantumCircuit(oracle.NQ, name=f"qmw_iching_seed_{seed}")
    for qubit in range(oracle.NQ):
        circuit.h(qubit)
        circuit.ry(rng.uniform(-np.pi, np.pi), qubit)
        circuit.rz(rng.uniform(-np.pi, np.pi), qubit)
    edges = [(0,1),(1,2),(2,0),(3,4),(4,5),(5,3),(0,3),(1,4),(2,5),
             (6,0),(6,2),(6,4),(7,1),(7,3),(7,5),(6,7)]
    for _ in range(max(1, int(depth))):
        rng.shuffle(edges)
        for control, target in edges:
            circuit.cp(rng.uniform(0.15 * np.pi, np.pi), control, target)
        for qubit in range(oracle.NQ):
            circuit.ry(rng.uniform(-0.45, 0.45), qubit)
            circuit.rz(rng.uniform(-0.45, 0.45), qubit)
    return circuit


def build_measurement_circuits(seed: int, depth: int = 3) -> dict[str, Any]:
    """Return cast plus the three commuting moving-line basis families."""
    base = build_qiskit_oracle_circuit(seed, depth)
    circuits = {}
    cast = base.copy(name="iching_cast")
    cast.measure_all()
    circuits["cast"] = cast

    zx = base.copy(name="iching_zx_family")
    zx.h(6)
    zx.measure_all()
    circuits["zx"] = zx

    xz = base.copy(name="iching_xz_family")
    xz.h(range(6))
    xz.measure_all()
    circuits["xz"] = xz

    yy = base.copy(name="iching_yy_family")
    for qubit in range(7):
        yy.sdg(qubit)
        yy.h(qubit)
    yy.measure_all()
    circuits["yy"] = yy
    return circuits


def circuit_fingerprint(seed: int, depth: int = 3) -> str:
    from qiskit import qasm3

    source = qasm3.dumps(build_qiskit_oracle_circuit(seed, depth))
    return hashlib.sha256(source.encode("utf-8")).hexdigest()


def qiskit_parity(seed: int, depth: int = 3) -> dict[str, float]:
    """Verify Qiskit and the existing NumPy oracle describe one pure state."""
    from qiskit.quantum_info import Statevector

    expected = oracle.build(unsigned_int32(seed), depth)
    actual = np.asarray(Statevector.from_instruction(
        build_qiskit_oracle_circuit(seed, depth)
    ).data)
    overlap = np.vdot(expected, actual)
    fidelity = float(abs(overlap) ** 2)
    probability_error = float(np.max(np.abs(np.abs(expected) ** 2 - np.abs(actual) ** 2)))
    return {"state_fidelity": fidelity, "max_probability_error": probability_error}


def compact_count_key(key: str, width: int = 8) -> str:
    compact = str(key).replace(" ", "")
    if len(compact) < width or any(bit not in "01" for bit in compact):
        raise ValueError(f"unexpected count key {key!r}")
    return compact[-width:]


def counts_vector(counts: dict[str, int], width: int = 8) -> np.ndarray:
    vector = np.zeros(2**width, dtype=np.float64)
    for key, count in counts.items():
        vector[int(compact_count_key(key, width), 2)] += int(count)
    total = float(vector.sum())
    if total <= 0:
        raise ValueError("counts contain no shots")
    return vector / total


def primary_distribution(distribution_8q: np.ndarray) -> np.ndarray:
    distribution = np.asarray(distribution_8q, dtype=np.float64)
    if distribution.shape != (256,):
        raise ValueError("eight-qubit distribution must contain 256 bins")
    result = np.zeros(64, dtype=np.float64)
    for index, probability in enumerate(distribution):
        result[index & 0x3F] += probability
    return result


def correlation_from_counts(counts: dict[str, int], qubit_a: int, qubit_b: int) -> float:
    total = 0
    signed = 0
    for key, count in counts.items():
        value = int(compact_count_key(key), 2)
        parity = ((value >> qubit_a) ^ (value >> qubit_b)) & 1
        signed += (-1 if parity else 1) * int(count)
        total += int(count)
    if total <= 0:
        raise ValueError("counts contain no shots")
    return float(signed / total)


def moving_probabilities_from_counts(counts_by_family: dict[str, dict[str, int]]) -> list[float]:
    missing = {"zx", "xz", "yy"} - set(counts_by_family)
    if missing:
        raise ValueError(f"missing measurement families: {sorted(missing)}")
    probabilities = []
    for line in range(6):
        correlations = (
            abs(correlation_from_counts(counts_by_family["zx"], line, 6)),
            abs(correlation_from_counts(counts_by_family["xz"], line, 7)),
            abs(correlation_from_counts(counts_by_family["yy"], line, 6)),
        )
        probabilities.append(float(np.clip(sum(correlations) / 1.5, 0.0, 1.0)))
    return probabilities


def exact_local_data(seed: int, depth: int = 3) -> tuple[np.ndarray, list[float]]:
    state = oracle.build(unsigned_int32(seed), depth)
    distribution = np.abs(state) ** 2
    return distribution, oracle.moving_probs(state)


@dataclass(frozen=True)
class RouteReading:
    primary: int
    moving_mask: int
    transformed: int
    change_register: int
    traditional_lines: tuple[int, ...]
    moving_probabilities: tuple[float, ...]


def reading_from_data(seed: int, distribution: np.ndarray,
                      moving_probabilities: Sequence[float]) -> RouteReading:
    """Apply one shared deterministic sampling stream to either route."""
    rng = np.random.default_rng(unsigned_int32(seed) ^ 0x1C41C41C)
    normalized = np.asarray(distribution, dtype=np.float64)
    normalized = normalized / normalized.sum()
    measured = int(rng.choice(len(normalized), p=normalized))
    primary = measured & 0x3F
    change = (measured >> 6) & 3
    moving = [int(rng.random() < float(probability)) for probability in moving_probabilities]
    moving_mask = sum(value << line for line, value in enumerate(moving))
    transformed = primary ^ moving_mask
    traditional = tuple(
        9 if ((primary >> line) & 1) and moving[line]
        else 7 if ((primary >> line) & 1)
        else 6 if moving[line]
        else 8
        for line in range(6)
    )
    return RouteReading(
        primary, moving_mask, transformed, change, traditional,
        tuple(float(value) for value in moving_probabilities),
    )


@dataclass(frozen=True)
class ComparisonResult:
    seed: int
    depth: int
    source: str
    backend: str
    job_id: str
    shots: int
    circuit_sha256: str
    local: RouteReading
    external: RouteReading
    primary_tvd: float
    primary_hellinger_fidelity: float
    moving_probability_mae: float

    @property
    def primary_agrees(self) -> bool:
        return self.local.primary == self.external.primary

    @property
    def moving_agrees(self) -> bool:
        return self.local.moving_mask == self.external.moving_mask

    @property
    def transformed_agrees(self) -> bool:
        return self.local.transformed == self.external.transformed

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["agreement"] = {
            "primary": self.primary_agrees,
            "moving_mask": self.moving_agrees,
            "transformed": self.transformed_agrees,
        }
        return payload


def compare_counts(seed: int, depth: int, counts_by_family: dict[str, dict[str, int]],
                   source: str, backend: str, job_id: str, shots: int) -> ComparisonResult:
    local_distribution, local_moving = exact_local_data(seed, depth)
    external_distribution = counts_vector(counts_by_family["cast"])
    external_moving = moving_probabilities_from_counts(counts_by_family)
    local_primary = primary_distribution(local_distribution)
    external_primary = primary_distribution(external_distribution)
    tvd = 0.5 * float(np.sum(np.abs(local_primary - external_primary)))
    fidelity = float(np.sum(np.sqrt(local_primary * external_primary)) ** 2)
    moving_mae = float(np.mean(np.abs(np.asarray(local_moving) - external_moving)))
    return ComparisonResult(
        seed=unsigned_int32(seed), depth=int(depth), source=source,
        backend=backend, job_id=job_id, shots=int(shots),
        circuit_sha256=circuit_fingerprint(seed, depth),
        local=reading_from_data(seed, local_distribution, local_moving),
        external=reading_from_data(seed, external_distribution, external_moving),
        primary_tvd=tvd, primary_hellinger_fidelity=fidelity,
        moving_probability_mae=moving_mae,
    )


def run_aer(seed: int, depth: int, shots: int) -> tuple[ComparisonResult, dict[str, dict[str, int]]]:
    from qiskit import transpile
    from qiskit_aer import AerSimulator

    circuits = build_measurement_circuits(seed, depth)
    simulator = AerSimulator()
    compiled = transpile(list(circuits.values()), simulator, optimization_level=1)
    result = simulator.run(compiled, shots=shots, seed_simulator=unsigned_int32(seed)).result()
    counts = {
        name: {str(key): int(value) for key, value in result.get_counts(index).items()}
        for index, name in enumerate(circuits)
    }
    return compare_counts(seed, depth, counts, "aer", "aer_simulator", "local", shots), counts


def select_backend(service, backend_name: str | None):
    return service.backend(backend_name) if backend_name else service.least_busy(
        operational=True, simulator=False, min_num_qubits=8
    )


def transpilation_report(seed: int, depth: int, backend) -> tuple[list[Any], dict[str, Any]]:
    from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager

    circuits = build_measurement_circuits(seed, depth)
    manager = generate_preset_pass_manager(backend=backend, optimization_level=2)
    isa_circuits = manager.run(list(circuits.values()))
    report = {
        "backend": _backend_name(backend),
        "num_qubits": int(backend.num_qubits),
        "circuit_sha256": circuit_fingerprint(seed, depth),
        "circuits": {
            name: {"depth": int(circuit.depth()), "operations": dict(circuit.count_ops())}
            for name, circuit in zip(circuits, isa_circuits)
        },
    }
    return isa_circuits, report


def publish_status(client, revision: int, state: str, backend: str = "", job_id: str = "") -> None:
    client.send_message(IBM_ROOT + "/status", [signed_int32(revision), state, backend, job_id])


def publish_comparison(client, revision: int, comparison: ComparisonResult) -> None:
    r = signed_int32(revision)
    client.send_message(IBM_ROOT + "/begin", [r, signed_int32(comparison.seed),
                                               comparison.source, comparison.backend,
                                               comparison.job_id, comparison.shots])
    client.send_message(IBM_ROOT + "/reading", [
        r, comparison.local.primary, comparison.local.moving_mask,
        comparison.local.transformed, comparison.external.primary,
        comparison.external.moving_mask, comparison.external.transformed,
    ])
    client.send_message(IBM_ROOT + "/metrics", [
        r, comparison.primary_tvd, comparison.primary_hellinger_fidelity,
        comparison.moving_probability_mae,
    ])
    client.send_message(IBM_ROOT + "/moving", [
        r, *comparison.local.moving_probabilities,
        *comparison.external.moving_probabilities,
    ])
    client.send_message(IBM_ROOT + "/end", [r])


def save_archive(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def run_ibm(seed: int, depth: int, shots: int, account: str,
            backend_name: str | None, save_dir: Path, submit_only: bool = False,
            status_callback=None):
    from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2

    service = QiskitRuntimeService(name=account)
    backend = select_backend(service, backend_name)
    isa_circuits, report = transpilation_report(seed, depth, backend)
    if status_callback:
        status_callback("transpiled", _backend_name(backend), "")
    job = SamplerV2(mode=backend).run(isa_circuits, shots=shots)
    current_job_id = _job_id(job)
    archive_path = save_dir / current_job_id / "iching-ibm-comparison-v1.json"
    archive = {
        "schema": "qmw.iching.ibm-comparison.v1",
        "job": {"id": current_job_id, "backend": _backend_name(backend),
                "status": str(job.status()), "shots_per_circuit": shots,
                "circuits": 4, "total_shots": 4 * shots,
                "submitted_at": utc_now()},
        "experiment": {"seed": unsigned_int32(seed), "depth": depth},
        "transpilation": report,
    }
    save_archive(archive_path, archive)
    if status_callback:
        status_callback("submitted", _backend_name(backend), current_job_id)
    if submit_only:
        return None, archive_path, current_job_id
    publications = job.result()
    counts = {
        name: {str(key): int(value) for key, value in publication.data.meas.get_counts().items()}
        for name, publication in zip(FAMILY_NAMES, publications)
    }
    comparison = compare_counts(
        seed, depth, counts, "ibm", _backend_name(backend), current_job_id, shots
    )
    archive["job"]["status"] = str(job.status())
    archive["job"]["completed_at"] = utc_now()
    archive["counts"] = counts
    archive["comparison"] = comparison.to_dict()
    save_archive(archive_path, archive)
    if status_callback:
        status_callback("done", _backend_name(backend), current_job_id)
    return comparison, archive_path, current_job_id


class IBMComparisonService:
    def __init__(self, args, client, audio_player=None, audio_stop_client=None):
        self.args = args
        self.client = client
        self.audio_player = audio_player
        self.audio_stop_client = audio_stop_client
        self._lock = threading.Lock()

    def handle_request(self, _address, revision, signed_seed, depth=3):
        if not self._lock.acquire(blocking=False):
            publish_status(self.client, int(revision), "busy")
            return
        worker = threading.Thread(
            target=self._run, args=(int(revision), unsigned_int32(signed_seed), int(depth)),
            daemon=True, name="iching-ibm-comparison",
        )
        worker.start()

    def _run(self, revision: int, seed: int, depth: int) -> None:
        try:
            publish_status(self.client, revision, "accepted")
            if self.args.confirm_ibm:
                comparison, archive_path, _job = run_ibm(
                    seed, depth, self.args.shots, self.args.account,
                    self.args.backend, self.args.save_dir,
                    status_callback=lambda state, backend, job: publish_status(
                        self.client, revision, state, backend, job
                    ),
                )
            else:
                comparison, counts = run_aer(seed, depth, self.args.shots)
                archive_path = self.args.save_dir / "aer" / f"seed-{seed}" / "comparison.json"
                save_archive(archive_path, {
                    "schema": "qmw.iching.ibm-comparison.v1",
                    "created_at": utc_now(), "counts": counts,
                    "comparison": comparison.to_dict(),
                })
            if comparison is not None:
                publish_comparison(self.client, revision, comparison)
                if self.audio_player is not None:
                    try:
                        if self.audio_stop_client is not None:
                            self.audio_stop_client.send_message("/qmw/iching/audio/stop", [revision])
                            time.sleep(0.04)
                        audio_path = archive_path.with_name("comparison-sonification-v1.wav")
                        self.audio_player.play(comparison, audio_path)
                        print(f"comparison sound LOCAL -> {comparison.source.upper()} -> difference "
                              f"audio={audio_path}", flush=True)
                    except Exception as audio_exc:
                        print(f"comparison sound error: {audio_exc}", flush=True)
                print(f"comparison source={comparison.source} seed={seed} "
                      f"TVD={comparison.primary_tvd:.4f} "
                      f"fidelity={comparison.primary_hellinger_fidelity:.4f} "
                      f"archive={archive_path}", flush=True)
        except Exception as exc:
            publish_status(self.client, revision, "error", "", str(exc)[:120])
            print(f"IBM comparison error: {exc}", flush=True)
        finally:
            self._lock.release()


def serve(args) -> None:
    from pythonosc.dispatcher import Dispatcher
    from pythonosc.osc_server import ThreadingOSCUDPServer
    from pythonosc.udp_client import SimpleUDPClient

    client = SimpleUDPClient(args.out_host, args.out_port)
    sound_enabled = not args.no_sound
    audio_player = None
    if sound_enabled:
        audio_player = ComparisonAudioPlayer(
            ComparisonSonificationConfig(
                route_seconds=args.sound_route_duration,
                base_frequency_hz=args.sound_base_frequency,
                mode_count=args.sound_modes,
            ),
            volume=args.sound_volume,
        )
    audio_stop_client = SimpleUDPClient(args.audio_host, args.audio_control_port)
    service = IBMComparisonService(args, client, audio_player, audio_stop_client)
    dispatcher = Dispatcher()
    dispatcher.map(IBM_ROOT + "/request", service.handle_request)
    server = ThreadingOSCUDPServer((args.host, args.control_port), dispatcher)
    mode = "IBM HARDWARE" if args.confirm_ibm else "AER DRY RUN"
    print(f"I Ching comparison service {mode} listening on "
          f"{args.host}:{args.control_port}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("I Ching comparison service stopped", flush=True)
    finally:
        if audio_player is not None:
            audio_player.close()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--depth", type=int, default=3)
    parser.add_argument("--shots", type=int, default=4096)
    parser.add_argument("--account", default=ACCOUNT_NAME)
    parser.add_argument("--backend")
    parser.add_argument("--inspect-backend", action="store_true")
    parser.add_argument("--confirm-ibm", action="store_true")
    parser.add_argument("--submit-only", action="store_true")
    parser.add_argument("--serve", action="store_true")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--control-port", type=int, default=7406)
    parser.add_argument("--out-host", default="127.0.0.1")
    parser.add_argument("--out-port", type=int, default=7404)
    parser.add_argument("--audio-host", default="127.0.0.1")
    parser.add_argument("--audio-control-port", type=int, default=7405)
    parser.add_argument("--no-sound", action="store_true")
    parser.add_argument("--sound-route-duration", type=float, default=7.0)
    parser.add_argument("--sound-base-frequency", type=float, default=90.0)
    parser.add_argument("--sound-modes", type=int, default=24)
    parser.add_argument("--sound-volume", type=float, default=1.0)
    parser.add_argument("--revision", type=int, default=1)
    parser.add_argument("--save-dir", type=Path,
                        default=Path("output/iching_ibm_compare_v1"))
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.shots <= 0:
        raise SystemExit("--shots must be positive")
    parity = qiskit_parity(args.seed, args.depth)
    print(json.dumps({"qiskit_parity": parity}, indent=2), flush=True)
    if parity["state_fidelity"] < 1.0 - 1e-10:
        raise SystemExit("Qiskit translation does not match the NumPy oracle")
    if args.serve:
        serve(args)
        return 0
    if args.inspect_backend:
        from qiskit_ibm_runtime import QiskitRuntimeService
        service = QiskitRuntimeService(name=args.account)
        backend = select_backend(service, args.backend)
        _circuits, report = transpilation_report(args.seed, args.depth, backend)
        print(json.dumps({"hardware_readiness": report}, indent=2), flush=True)
        if not args.confirm_ibm:
            print("Read-only inspection complete; no IBM job submitted.", flush=True)
            return 0
    if args.confirm_ibm:
        comparison, archive, job = run_ibm(
            args.seed, args.depth, args.shots, args.account, args.backend,
            args.save_dir, submit_only=args.submit_only,
        )
        print(f"IBM job={job} archive={archive}", flush=True)
        if comparison is not None:
            print(json.dumps(comparison.to_dict(), indent=2), flush=True)
        return 0
    comparison, counts = run_aer(args.seed, args.depth, args.shots)
    archive = args.save_dir / "aer" / f"seed-{unsigned_int32(args.seed)}" / "comparison.json"
    save_archive(archive, {"schema": "qmw.iching.ibm-comparison.v1",
                           "created_at": utc_now(), "counts": counts,
                           "comparison": comparison.to_dict()})
    print(json.dumps(comparison.to_dict(), indent=2), flush=True)
    print(f"Aer comparison archived: {archive}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
