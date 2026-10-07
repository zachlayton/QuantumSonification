#!/usr/bin/env python3
"""Replay a downloaded IBM Sampler job into the V1/V2 Max comparison.

The script reads IBM's downloaded ``*-info.json`` and ``*-result.json`` files,
recovers the four active logical qubits from the transpiled circuit, sends that
ideal circuit through the shared bridge, and then publishes the saved hardware
counts as the V2 diagonal density estimate.  It performs no network request
and submits no IBM job.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import time

import numpy as np
from pythonosc.udp_client import SimpleUDPClient
from qiskit import QuantumCircuit, qasm2, transpile
from qiskit_ibm_runtime import RuntimeDecoder

from qac_density_ibm_compare_bridge_v2 import (
    RenderConfig,
    circuit_density,
    density_metrics,
    density_to_table,
    diagonal_density,
    probabilities_to_table,
    total_variation_distance,
)
from qac_ibm_counts_bridge_v1 import ordered_counts, probabilities_from_counts


def downloaded_paths(directory: Path) -> tuple[Path, Path]:
    info = sorted(directory.glob("*-info.json"))
    result = sorted(directory.glob("*-result.json"))
    if len(info) != 1 or len(result) != 1:
        raise ValueError(
            "Job directory must contain exactly one *-info.json and one "
            "*-result.json"
        )
    return info[0], result[0]


def logical_four_qubit_circuit(transpiled) -> QuantumCircuit:
    """Extract operations acting on physical qubits 0..3 before measurement."""

    logical = QuantumCircuit(4)
    logical.global_phase = transpiled.global_phase
    for instruction in transpiled.data:
        operation = instruction.operation
        if operation.name in {"measure", "barrier"}:
            continue
        indices = [
            transpiled.find_bit(qubit).index
            for qubit in instruction.qubits
        ]
        if not indices or any(index >= 4 for index in indices):
            continue
        logical.append(
            operation,
            [logical.qubits[index] for index in indices],
            [],
        )
    return logical


def load_downloaded_job(
    directory: Path,
) -> tuple[dict, dict[str, int], QuantumCircuit]:
    info_path, result_path = downloaded_paths(directory)
    info = json.loads(info_path.read_text(), cls=RuntimeDecoder)
    result = json.loads(result_path.read_text(), cls=RuntimeDecoder)
    if str(info.get("status", "")).lower() != "completed":
        raise ValueError(f"IBM job is not completed: {info.get('status')}")
    transpiled = info["params"]["pubs"][0][0]
    circuit = logical_four_qubit_circuit(transpiled)
    counts = dict(result[0].data.meas.get_counts())
    return info, counts, circuit


def replay(directory: Path, host: str, in_port: int, out_port: int) -> None:
    info, raw_counts, circuit = load_downloaded_job(directory)
    counts = ordered_counts(raw_counts)
    hardware_probabilities = np.asarray(
        probabilities_from_counts(counts),
        dtype=np.float64,
    )
    portable_circuit = transpile(
        circuit,
        basis_gates=["u3", "cx"],
        optimization_level=0,
    )
    qasm = qasm2.dumps(portable_circuit)
    ideal_probabilities, _ = circuit_density(qasm)
    rho_diag = diagonal_density(hardware_probabilities)
    config = RenderConfig(n_qubits=4, wavetable_size=256, mapping="real")
    table = density_to_table(rho_diag, config)
    harmonic_table = probabilities_to_table(hardware_probabilities)
    metrics = density_metrics(rho_diag)
    distance = total_variation_distance(
        ideal_probabilities,
        hardware_probabilities,
    )
    revision = int(time.time())

    bridge = SimpleUDPClient(host, in_port)
    max_client = SimpleUDPClient(host, out_port)
    bridge.send_message("/qmw/qac/qasm", [revision, qasm])
    time.sleep(0.25)
    max_client.send_message(
        "/qmw/density_compare/ibm",
        [revision, *table.tolist()],
    )
    max_client.send_message(
        "/qmw/density_compare/ibm_harmonic",
        [revision, *harmonic_table.tolist()],
    )
    max_client.send_message(
        "/qmw/density_compare/metrics",
        [revision, "ibm_diag", *metrics],
    )
    max_client.send_message(
        "/qmw/density_compare/comparison",
        [revision, distance],
    )
    max_client.send_message(
        "/qmw/density_compare/counts",
        [revision, int(sum(counts)), *counts],
    )
    max_client.send_message(
        "/qmw/density_compare/result",
        [
            revision,
            str(info["backend"]),
            str(info["id"]),
            int(sum(counts)),
        ],
    )
    max_client.send_message(
        "/qmw/density_compare/status",
        [
            "replayed_download",
            revision,
            str(info["backend"]),
            str(info["id"]),
        ],
    )
    print(
        f"replayed job={info['id']} backend={info['backend']} "
        f"shots={sum(counts)} population_tvd={distance:.6f}"
    )
    print(f"counts={raw_counts}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("job_directory", type=Path)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--in-port", type=int, default=7413)
    parser.add_argument("--out-port", type=int, default=7412)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    replay(
        args.job_directory.expanduser().resolve(),
        args.host,
        args.in_port,
        args.out_port,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
