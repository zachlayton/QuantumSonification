"""Module 1 — Superposition: one H gate creates two possible outcomes."""

from __future__ import annotations

import argparse

from qiskit import QuantumCircuit

from workshop_audio import add_listening_arguments, listen


# CHANGE THIS: try False, then True.
USE_H = False


def build_circuit(use_h: bool = USE_H) -> QuantumCircuit:
    circuit = QuantumCircuit(1)
    if use_h:
        circuit.h(0)
    return circuit


def main() -> None:
    parser = add_listening_arguments(
        argparse.ArgumentParser(description=__doc__),
        "01_superposition.wav",
    )
    parser.add_argument(
        "--h",
        action=argparse.BooleanOptionalAction,
        default=USE_H,
        help="include H (use --no-h for the |0> comparison)",
    )
    args = parser.parse_args()

    result = listen(
        build_circuit(args.h),
        label="Module 1: Superposition",
        output_path=args.output,
        play=not args.no_play,
        osc_port=args.osc_port,
    )
    print(f"H gate: {'on' if args.h else 'off'}")
    active = sum(probability > 1e-7 for probability in result.probabilities)
    print(f"Observe: {active} basis state(s) can be heard.")
    print("Reflect: what changed when the H gate was present?")


if __name__ == "__main__":
    main()
