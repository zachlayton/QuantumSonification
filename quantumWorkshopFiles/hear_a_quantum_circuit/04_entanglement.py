"""Module 4 — Entanglement: a CNOT can link two qubit outcomes."""

from __future__ import annotations

import argparse

from qiskit import QuantumCircuit

from workshop_audio import add_listening_arguments, listen


# CHANGE THIS: compare False with True.
USE_CNOT = True
USE_H = True


def build_circuit(
    use_cnot: bool = USE_CNOT,
    control: int = 0,
    use_h: bool = USE_H,
) -> QuantumCircuit:
    if control not in (0, 1):
        raise ValueError("control must be 0 or 1")
    target = 1 - control
    circuit = QuantumCircuit(2)
    if use_h:
        circuit.h(0)
    if use_cnot:
        circuit.cx(control, target)
    return circuit


def main() -> None:
    parser = add_listening_arguments(
        argparse.ArgumentParser(description=__doc__),
        "04_entanglement.wav",
    )
    parser.add_argument(
        "--cnot",
        action=argparse.BooleanOptionalAction,
        default=USE_CNOT,
        help="include CNOT (use --no-cnot for the unlinked comparison)",
    )
    parser.add_argument(
        "--control",
        type=int,
        choices=(0, 1),
        default=0,
        help="CNOT control qubit: 0 or 1 (target is the other qubit)",
    )
    parser.add_argument(
        "--h",
        action=argparse.BooleanOptionalAction,
        default=USE_H,
        help="prepare q0 with H (use --no-h to hear CNOT acting on |00>)",
    )
    args = parser.parse_args()

    result = listen(
        build_circuit(args.cnot, args.control, args.h),
        label="Module 4: Entanglement",
        output_path=args.output,
        play=not args.no_play,
        osc_port=args.osc_port,
        arpeggiate=False,
    )
    matched = result.probabilities[0] + result.probabilities[3]
    print(f"CNOT gate: {'on' if args.cnot else 'off'}")
    if args.cnot:
        print(f"CNOT direction: q{args.control} -> q{1 - args.control}")
    print(f"H preparation on q0: {'on' if args.h else 'off'}")
    if args.h:
        print("Sound: both possible joint outcomes play at the same time.")
    else:
        print("Sound: the one certain joint outcome plays as a single tone.")
    print(f"Observe: probability of matching bits (00 or 11) = {matched:.1%}")
    print("Reflect: what does the CNOT change about the pair, not either bit alone?")


if __name__ == "__main__":
    main()
