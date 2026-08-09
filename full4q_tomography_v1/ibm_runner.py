"""Submit, retrieve, archive, and publish the 81-setting score on IBM hardware."""

from __future__ import annotations

import argparse
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from qiskit import QuantumCircuit
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2

from .engine import SETTINGS, _apply_transform, build_score_circuit, reconstruct_tomography
from .osc_service import TomographyOSCPublisher


ACCOUNT_NAME = "quantum-sonification-workshop"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def build_measurement_circuits(
    preset: str = "ghz", transform: str = "none"
) -> list[QuantumCircuit]:
    """Build the ordered XXXX…ZZZZ circuit batch used by the local instrument."""
    base = _apply_transform(build_score_circuit(preset), transform)
    circuits: list[QuantumCircuit] = []
    for index, axes in enumerate(SETTINGS):
        circuit = base.copy(name=f"qmw_{index:02d}_{axes}")
        for qubit, axis in enumerate(axes):
            if axis == "X":
                circuit.h(qubit)
            elif axis == "Y":
                circuit.sdg(qubit)
                circuit.h(qubit)
        circuit.measure_all()
        circuits.append(circuit)
    return circuits


def counts_row(counts: dict[str, int]) -> list[int]:
    """Convert Qiskit's q3q2q1q0 count keys into the instrument's 16 bins."""
    row = [0] * 16
    for key, count in counts.items():
        compact = str(key).replace(" ", "")
        if len(compact) < 4 or any(bit not in "01" for bit in compact):
            raise ValueError(f"unexpected IBM count key {key!r}")
        row[int(compact[-4:], 2)] += int(count)
    return row


def result_count_rows(runtime_result: Any, shots: int) -> list[list[int]]:
    publications = list(runtime_result)
    if len(publications) != len(SETTINGS):
        raise ValueError(
            f"IBM returned {len(publications)} circuit results; "
            f"expected {len(SETTINGS)}"
        )
    rows: list[list[int]] = []
    for index, publication in enumerate(publications):
        bit_array = getattr(publication.data, "meas", None)
        if bit_array is None:
            raise ValueError(
                f"IBM result {index} has no measurement register named 'meas'"
            )
        row = counts_row(bit_array.get_counts())
        if sum(row) != shots:
            raise ValueError(
                f"IBM result {index} contains {sum(row)} shots; expected {shots}"
            )
        rows.append(row)
    return rows


def backend_name(backend: Any) -> str:
    value = getattr(backend, "name", "unknown")
    return str(value() if callable(value) else value)


def job_id(job: Any) -> str:
    value = getattr(job, "job_id")
    return str(value() if callable(value) else value)


def job_backend(job: Any) -> Any:
    value = getattr(job, "backend", None)
    return value() if callable(value) else value


def save_archive(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run all 81 Full4Q tomography settings on IBM hardware."
    )
    parser.add_argument("--preset", choices=("bell", "ghz", "weave"), default="ghz")
    parser.add_argument("--transform", choices=("none", "qft", "iqft"), default="none")
    parser.add_argument("--shots", type=int, default=256)
    parser.add_argument("--backend", help="IBM backend name; default selects least busy")
    parser.add_argument("--account", default=ACCOUNT_NAME)
    parser.add_argument("--job-id", help="Retrieve an already-submitted 81-circuit job")
    parser.add_argument(
        "--confirm-ibm",
        action="store_true",
        help="Required for a new hardware submission.",
    )
    parser.add_argument(
        "--submit-only",
        action="store_true",
        help="Submit and archive the job ID without waiting for its result.",
    )
    parser.add_argument("--out-host", default="127.0.0.1")
    parser.add_argument("--out-port", type=int, default=7426)
    parser.add_argument("--packet-delay-ms", type=float, default=2.0)
    parser.add_argument(
        "--save-dir",
        type=Path,
        default=Path("full4q_tomography_v1/runs/ibm"),
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.shots <= 0:
        raise SystemExit("--shots must be positive")
    if not args.job_id and not args.confirm_ibm:
        raise SystemExit(
            "A new IBM hardware submission requires --confirm-ibm."
        )

    publisher = TomographyOSCPublisher(
        args.out_host, args.out_port, args.packet_delay_ms
    )
    service = QiskitRuntimeService(name=args.account)
    submitted_at: str | None = None

    if args.job_id:
        job = service.job(args.job_id)
        selected_backend = job_backend(job)
        selected_backend_name = backend_name(selected_backend)
        current_job_id = args.job_id
        print(
            f"Retrieving IBM Full4Q job: id={current_job_id} "
            f"backend={selected_backend_name}",
            flush=True,
        )
    else:
        circuits = build_measurement_circuits(args.preset, args.transform)
        selected_backend = (
            service.backend(args.backend)
            if args.backend
            else service.least_busy(
                operational=True,
                simulator=False,
                min_num_qubits=4,
            )
        )
        selected_backend_name = backend_name(selected_backend)
        print(
            f"Transpiling {len(circuits)} four-qubit circuits for "
            f"{selected_backend_name}…",
            flush=True,
        )
        pass_manager = generate_preset_pass_manager(
            backend=selected_backend, optimization_level=1
        )
        isa_circuits = pass_manager.run(circuits)
        sampler = SamplerV2(mode=selected_backend)
        job = sampler.run(isa_circuits, shots=args.shots)
        current_job_id = job_id(job)
        submitted_at = utc_now()
        print(
            f"IBM Full4Q job submitted: id={current_job_id} "
            f"backend={selected_backend_name} circuits={len(circuits)} "
            f"shots_per_setting={args.shots} total_shots={len(circuits) * args.shots}",
            flush=True,
        )
        publisher.status(
            "ibm_submitted",
            current_job_id,
            selected_backend_name,
            len(circuits),
            args.shots,
        )

    archive_path = args.save_dir / current_job_id / (
        f"job-{current_job_id}-full4q-archive.json"
    )
    archive: dict[str, Any] = {
        "schema": "qmw.full4q.tomography.ibm.v1",
        "job": {
            "id": current_job_id,
            "backend": selected_backend_name,
            "status": str(job.status()),
            "submitted_at": submitted_at,
            "circuits": len(SETTINGS),
            "shots_per_setting": args.shots,
            "total_shots": len(SETTINGS) * args.shots,
        },
        "score": {
            "preset": args.preset,
            "transform": args.transform,
            "settings": list(SETTINGS),
        },
    }
    save_archive(archive_path, archive)
    print(f"Saved job record: {archive_path.resolve()}", flush=True)
    if args.submit_only:
        return 0

    print("Waiting for IBM hardware result; the job ID is already saved.", flush=True)
    runtime_result = job.result()
    rows = result_count_rows(runtime_result, args.shots)
    result = reconstruct_tomography(
        rows,
        preset=args.preset,
        transform=args.transform,
        shots=args.shots,
        source="ibm_hardware",
    )
    archive["job"]["status"] = "DONE"
    archive["job"]["completed_at"] = utc_now()
    archive["raw_counts"] = [
        {"index": index, "axes": axes, "counts": row}
        for index, (axes, row) in enumerate(zip(SETTINGS, rows))
    ]
    archive["result"] = result.to_dict()
    save_archive(archive_path, archive)

    revision = int(time.time() * 1000) % 2_000_000_000
    publisher.publish(result, revision)
    publisher.status(
        "ibm_complete",
        current_job_id,
        selected_backend_name,
        result.total_shots,
    )
    print(
        f"IBM Full4Q complete: id={current_job_id} "
        f"fidelity={result.metrics['fidelity_to_local_ideal']:.6f}",
        flush=True,
    )
    print(f"Archived and published: {archive_path.resolve()}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
