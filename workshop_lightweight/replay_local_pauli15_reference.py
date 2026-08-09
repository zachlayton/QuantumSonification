#!/usr/bin/env python3
"""Generate and replay a local four-qubit Pauli-15 reference into QMW V5."""

from __future__ import annotations

import argparse
import time

from pythonosc.udp_client import SimpleUDPClient
from qiskit import QuantumCircuit, qasm2

from qac_ibm_wavetable_bridge import (
    PAULI15,
    local_pauli15,
    pauli15_quantum_features,
)


def preset_circuit(name: str) -> QuantumCircuit:
    circuit = QuantumCircuit(4, 4)
    if name == "bell":
        circuit.h(0)
        circuit.cx(0, 1)
    elif name == "ghz":
        circuit.h(0)
        circuit.cx(0, 1)
        circuit.cx(1, 2)
        circuit.cx(2, 3)
    elif name == "weave":
        for qubit in range(4):
            circuit.h(qubit)
        circuit.cx(0, 1)
        circuit.cx(2, 3)
        circuit.cx(1, 2)
        circuit.t(0)
        circuit.s(3)
    else:
        raise ValueError(f"unknown preset {name!r}")
    return circuit


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--preset", choices=("bell", "ghz", "weave"), default="bell")
    parser.add_argument("--transform", choices=("none", "qft", "iqft"), default="qft")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=7412)
    parser.add_argument("--revision", type=int)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    circuit = preset_circuit(args.preset)
    values, _qubits = local_pauli15(
        qasm2.dumps(circuit), 0, 1, args.transform
    )
    coefficients = [float(values[term]) for term in PAULI15]
    descriptors = [float(value) for value in pauli15_quantum_features(values)]
    revision = (
        args.revision
        if args.revision is not None
        else int(time.time() * 1000) % 2_000_000_000
    )
    client = SimpleUDPClient(args.host, args.port)
    client.send_message(
        "/qmw/wavetable/status",
        ["local_reference", revision, args.preset, args.transform],
    )
    client.send_message(
        "/qmw/quantum/state",
        [revision, "local", *coefficients, *descriptors],
    )
    client.send_message(
        "/qmw/quantum/features",
        [revision, *descriptors],
    )
    print(
        f"Replayed local {args.preset}/{args.transform} reference to "
        f"udp://{args.host}:{args.port} as revision {revision}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
