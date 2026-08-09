#!/usr/bin/env python3
"""Create a durable, readable archive from IBM Runtime Pauli-15 exports."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path
from typing import Any

import numpy as np
from qiskit_ibm_runtime import RuntimeDecoder

from qac_ibm_wavetable_bridge import (
    PAULI15,
    correlation_from_counts,
    expectation_from_counts,
    pauli15_quantum_features,
)


BASES = tuple(a + b for a in "XYZ" for b in "XYZ")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def circuit_summary(circuit: Any) -> dict[str, Any]:
    physical_layout: list[int] | None = None
    layout = getattr(circuit, "layout", None)
    if layout is not None:
        try:
            physical_layout = [
                int(value)
                for value in layout.final_index_layout(filter_ancillas=True)
            ]
        except Exception:
            physical_layout = None
    return {
        "target_qubits": int(circuit.num_qubits),
        "classical_bits": int(circuit.num_clbits),
        "depth": int(circuit.depth()),
        "instruction_count": int(circuit.size()),
        "logical_to_physical_layout": physical_layout,
    }


def decode_export(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"), cls=RuntimeDecoder)


def archive_job(
    *,
    info_path: Path,
    result_path: Path,
    output_root: Path,
    transform: str,
    qubit_a: int,
    qubit_b: int,
) -> Path:
    info = decode_export(info_path)
    results = decode_export(result_path)
    job_id = str(info["id"])
    status = str(info.get("status") or info.get("state", {}).get("status", ""))
    if status.lower() != "completed":
        raise ValueError(f"job {job_id} is not completed: {status}")
    if len(results) != 9:
        raise ValueError(f"expected 9 PUB results, found {len(results)}")

    pubs = info.get("params", {}).get("pubs", [])
    if len(pubs) != 9:
        raise ValueError(f"expected 9 PUB descriptions, found {len(pubs)}")

    settings: list[dict[str, Any]] = []
    correlations: dict[str, float] = {}
    local_a = {axis: [] for axis in "XYZ"}
    local_b = {axis: [] for axis in "XYZ"}
    shots_per_setting: int | None = None

    for index, (basis, pub, result) in enumerate(zip(BASES, pubs, results)):
        counts = {
            str(key): int(value)
            for key, value in sorted(result.data.meas.get_counts().items())
        }
        shots = sum(counts.values())
        declared_shots = int(pub[2])
        if shots != declared_shots:
            raise ValueError(
                f"{basis} contains {shots} counts but declares {declared_shots} shots"
            )
        if shots_per_setting is None:
            shots_per_setting = shots
        elif shots != shots_per_setting:
            raise ValueError("PUB results do not share one shots-per-setting value")

        axis_a, axis_b = basis
        correlations[basis] = correlation_from_counts(
            counts, qubit_a, qubit_b
        )
        local_a[axis_a].append(expectation_from_counts(counts, qubit_a))
        local_b[axis_b].append(expectation_from_counts(counts, qubit_b))
        settings.append(
            {
                "index": index,
                "basis": basis,
                "shots": shots,
                "counts": counts,
                "circuit": circuit_summary(pub[0]),
            }
        )

    values = dict(correlations)
    for axis in "XYZ":
        values[axis + "I"] = float(np.mean(local_a[axis]))
        values["I" + axis] = float(np.mean(local_b[axis]))
    ordered_values = {term: float(values[term]) for term in PAULI15}
    polarization, entanglement, correlation_rms, entropy = (
        pauli15_quantum_features(ordered_values)
    )

    archive = {
        "schema": "qmw.ibm.pauli15.archive.v1",
        "job": {
            "id": job_id,
            "backend": str(info.get("backend", "")),
            "status": status,
            "created": str(info.get("created", "")),
            "program": info.get("program", {}),
            "cost_units_reported_by_ibm": info.get("cost"),
        },
        "experiment": {
            "mapping": "pauli15",
            "transform": transform,
            "logical_qubit_pair": [qubit_a, qubit_b],
            "basis_order": list(BASES),
            "shots_per_setting": shots_per_setting,
            "setting_count": len(settings),
            "total_shots": sum(setting["shots"] for setting in settings),
            "bitstring_order": "q3 q2 q1 q0; logical q0 is rightmost",
        },
        "settings": settings,
        "pauli15": ordered_values,
        "features": {
            "z_polarization": float(polarization),
            "concurrence": float(entanglement),
            "correlation_rms": float(correlation_rms),
            "entropy_bits": float(entropy),
        },
        "source_exports": {
            "info_filename": info_path.name,
            "info_sha256": sha256(info_path),
            "result_filename": result_path.name,
            "result_sha256": sha256(result_path),
        },
    }

    destination = output_root / job_id
    destination.mkdir(parents=True, exist_ok=True)
    normalized_path = destination / f"job-{job_id}-pauli15-archive.json"
    temporary_path = normalized_path.with_suffix(".json.tmp")
    temporary_path.write_text(
        json.dumps(archive, indent=2) + "\n", encoding="utf-8"
    )
    temporary_path.replace(normalized_path)
    shutil.copy2(info_path, destination / info_path.name)
    shutil.copy2(result_path, destination / result_path.name)
    return normalized_path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--info", type=Path, required=True)
    parser.add_argument("--result", type=Path, required=True)
    parser.add_argument(
        "--output-root",
        type=Path,
        default=Path(__file__).resolve().parent / "ibm_results",
    )
    parser.add_argument(
        "--transform", choices=("none", "qft", "iqft"), default="qft"
    )
    parser.add_argument("--qubit-a", type=int, default=0)
    parser.add_argument("--qubit-b", type=int, default=1)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        output = archive_job(
            info_path=args.info.expanduser().resolve(),
            result_path=args.result.expanduser().resolve(),
            output_root=args.output_root.expanduser().resolve(),
            transform=args.transform,
            qubit_a=args.qubit_a,
            qubit_b=args.qubit_b,
        )
    except Exception as exc:
        print(f"Archive failed: {exc}", file=sys.stderr)
        return 1
    payload = json.loads(output.read_text(encoding="utf-8"))
    print(f"Archived IBM job {payload['job']['id']}: {output}")
    print(
        f"{payload['experiment']['setting_count']} settings, "
        f"{payload['experiment']['total_shots']} shots, "
        f"backend={payload['job']['backend']}"
    )
    print(
        "Pauli-15: "
        + " ".join(
            f"{term}={value:+.4f}"
            for term, value in payload["pauli15"].items()
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
