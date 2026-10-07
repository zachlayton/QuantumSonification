"""Module 5 — Measurement: repeated shots reveal classical uncertainty."""

from __future__ import annotations

import argparse

import numpy as np
from qiskit import QuantumCircuit

from workshop_audio import (
    add_listening_arguments,
    print_probabilities,
    render_probabilities,
    statevector_for,
    play_wav,
)


# CHANGE THIS: compare 8, 32, and 256 shots.
SHOTS = 32
SEED = 11


def positive_int(value: str) -> int:
    parsed = int(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("shots must be a positive integer")
    return parsed


def build_circuit() -> QuantumCircuit:
    circuit = QuantumCircuit(1)
    circuit.h(0)
    return circuit


def shannon_entropy(probabilities: np.ndarray) -> float:
    nonzero = probabilities[probabilities > 0]
    return float(-np.sum(nonzero * np.log2(nonzero)))


def main() -> None:
    parser = add_listening_arguments(
        argparse.ArgumentParser(description=__doc__),
        "05_entropy_and_measurement.wav",
    )
    parser.add_argument(
        "--shots",
        type=positive_int,
        default=SHOTS,
        help="number of repeated measurements (default: 32)",
    )
    args = parser.parse_args()

    state = statevector_for(build_circuit())
    state.seed(SEED)
    counts = state.sample_counts(shots=args.shots)
    friendly_counts = {str(key): int(value) for key, value in counts.items()}
    measured = np.array(
        [friendly_counts.get("0", 0), friendly_counts.get("1", 0)],
        dtype=np.float64,
    )
    measured /= measured.sum()
    wav_path = render_probabilities(measured, args.output)

    measured_circuit = build_circuit()
    measured_circuit.measure_all()
    print("\nModule 5: Entropy and measurement")
    print(measured_circuit.draw(output="text"))
    print(f"Selected: shots = {args.shots}")
    print(f"Counts from {args.shots} shots: {friendly_counts}")
    print("Measured frequencies:")
    print_probabilities(measured)
    print(f"Observe: Shannon entropy = {shannon_entropy(measured):.3f} bits")

    played = not args.no_play and play_wav(wav_path)
    if played:
        print(f"Played: {wav_path}")
    else:
        print(f"WAV ready: {wav_path}")
        if not args.no_play:
            print("Automatic playback was unavailable; open the WAV in any player.")

    if args.osc_port is not None:
        # Send the pre-measurement state to the established QMW interface.
        from workshop_audio import publish_qmw

        publish_qmw(state, port=args.osc_port)
        print(f"Sent the existing QMW circuit messages to UDP port {args.osc_port}.")

    print("Reflect: why do a few shots vary more than a few hundred?")


if __name__ == "__main__":
    main()
