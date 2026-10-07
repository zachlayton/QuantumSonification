"""Module 3 — Circuit design: combine simple gates to reach a target."""

from __future__ import annotations

import argparse

from qiskit import QuantumCircuit

from workshop_audio import add_listening_arguments, listen


# CHANGE THIS: try one preset or enter a short sequence with --gates.
# H → Z → H is the starter because it acts like X on every one-qubit state.
GATE_ORDER = ["h", "z", "h"]
GATES = ("h", "x", "y", "z")
PRESETS = {
    "starter": ["h", "z", "h"],
    "flip-x": ["x"],
    "flip-y": ["y"],
    "phase": ["h", "z"],
    "return": ["x", "x"],
    "compare-x": ["h", "x", "h"],
    "compare-y": ["h", "y", "h"],
}


def build_circuit(gate_order: list[str] | tuple[str, ...] = GATE_ORDER) -> QuantumCircuit:
    circuit = QuantumCircuit(1)
    for gate in gate_order:
        if gate not in GATES:
            raise ValueError("This activity uses only H, X, Y, and Z.")
        getattr(circuit, gate)(0)
    return circuit


def main() -> None:
    parser = add_listening_arguments(
        argparse.ArgumentParser(description=__doc__),
        "03_circuit_design.wav",
    )
    choice = parser.add_mutually_exclusive_group()
    choice.add_argument(
        "--gates",
        nargs="+",
        choices=GATES,
        help="Gate order from left to right, e.g. --gates h z h.",
    )
    choice.add_argument(
        "--preset",
        choices=tuple(PRESETS),
        help="Named short sequence (default: starter).",
    )
    args = parser.parse_args()
    gates = args.gates or PRESETS[args.preset or "starter"]

    result = listen(
        build_circuit(gates),
        label="Module 3: Circuit design",
        output_path=args.output,
        play=not args.no_play,
        osc_port=args.osc_port,
    )
    print(f"Gates: {' → '.join(gate.upper() for gate in gates)}")
    if float(result.probabilities.max()) > 1.0 - 1e-7:
        winner = int(result.probabilities.argmax())
        print(f"Observe: the certain output is |{winner}>.")
    else:
        possible = [
            f"|{index}>"
            for index, probability in enumerate(result.probabilities)
            if probability > 1e-7
        ]
        print(f"Observe: possible outputs are {' and '.join(possible)}.")
    print("Challenge: reach |1>, then add gates that return the state to |0>.")
    print(
        "Try next: --preset compare-x and --preset compare-y reveal how X and Y "
        "differ on a superposition."
    )
    print("Reflect: how can H-Z-H match X while H-Z leaves a different state?")


if __name__ == "__main__":
    main()
