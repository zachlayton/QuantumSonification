"""Module 2 — Bloch sphere: one angle chooses a one-qubit direction."""

from __future__ import annotations

import argparse
import math
import re

from qiskit import QuantumCircuit

from workshop_audio import (
    BLOCH_ANCHOR_HZ,
    add_listening_arguments,
    bloch_vectors,
    play_wav,
    print_probabilities,
    probabilities_for,
    publish_qmw,
    render_bloch_state,
    statevector_for,
)


# CHANGE THIS: try theta = 0, pi/2, or pi; then try phi = pi/2.
THETA = math.pi / 2
PHI = 0.0


def parse_angle(value: str) -> float:
    """Read decimals or simple multiples/fractions of pi without eval."""

    text = value.strip().lower().replace("π", "pi").replace(" ", "")
    try:
        return float(text)
    except ValueError:
        pass
    match = re.fullmatch(
        r"(?P<sign>[+-]?)(?:(?P<num>\d+(?:\.\d+)?)\*?)?pi"
        r"(?:/(?P<den>\d+(?:\.\d+)?))?",
        text,
    )
    if match is None:
        raise argparse.ArgumentTypeError(
            "use a decimal or a readable pi value such as 0, pi/2, -pi/2, or pi"
        )
    numerator = float(match.group("num") or 1.0)
    denominator = float(match.group("den") or 1.0)
    if denominator == 0:
        raise argparse.ArgumentTypeError("the pi denominator cannot be zero")
    sign = -1.0 if match.group("sign") == "-" else 1.0
    return sign * numerator * math.pi / denominator


def build_circuit(
    theta: float = THETA,
    phi: float = PHI,
    axis: str = "ry",
) -> QuantumCircuit:
    circuit = QuantumCircuit(1)
    getattr(circuit, axis)(theta, 0)
    circuit.rz(phi, 0)
    return circuit


def main() -> None:
    parser = add_listening_arguments(
        argparse.ArgumentParser(description=__doc__),
        "02_bloch_sphere.wav",
    )
    parser.add_argument(
        "--theta",
        type=parse_angle,
        default=THETA,
        help="north-to-south angle, e.g. 0, pi/2, pi (default: pi/2)",
    )
    parser.add_argument(
        "--axis",
        choices=("rx", "ry", "rz"),
        default="ry",
        help="rotation gate used for theta (default: ry)",
    )
    parser.add_argument(
        "--phi",
        type=parse_angle,
        default=PHI,
        help="angle around the equator, e.g. 0 or pi/2 (default: 0)",
    )
    args = parser.parse_args()

    circuit = build_circuit(args.theta, args.phi, args.axis)
    state = statevector_for(circuit)
    probabilities = probabilities_for(state)
    (
        wav_path,
        polar_frequency,
        polar_angle,
        phase_frequency,
        relative_phase,
        coherence,
    ) = render_bloch_state(
        state,
        args.output,
    )

    print("\nModule 2: Bloch sphere")
    print(circuit.draw(output="text"))
    print("Probabilities:")
    print_probabilities(probabilities)
    x, y, z = bloch_vectors(state)[0]
    print(
        f"Selected: axis = {args.axis.upper()}, "
        f"theta = {args.theta:.3f} rad, phi = {args.phi:.3f} rad"
    )
    print(f"Observe: Bloch vector = ({x:+.2f}, {y:+.2f}, {z:+.2f})")
    print(
        "Sound mapping: "
        f"|0> = {BLOCH_ANCHOR_HZ[0]:.0f} Hz, "
        f"|1> = {BLOCH_ANCHOR_HZ[1]:.0f} Hz (one octave); "
        "probabilities control their balance."
    )
    print(
        f"Theta cue: {polar_frequency:.2f} Hz at steady level from the actual "
        f"Bloch polar angle {polar_angle:.3f} rad."
    )
    print(
        "Theta formula: 220 * 2^(polar angle / pi). "
        "The cue is continuous, not equal-tempered."
    )
    if relative_phase is None or phase_frequency is None:
        print(
            "Phi cue: absent at this pole because Bloch azimuth is undefined "
            "when one basis amplitude is zero."
        )
    else:
        print(
            f"Phi cue: {phase_frequency:.2f} Hz with a brighter, steady-level "
            f"timbre from azimuth/relative phase {relative_phase:+.3f} rad."
        )
        print(
            "Formula: 220 * 2^(wrapped relative phase / 2pi). "
            "Phi changes this cue, not the Z-basis probabilities."
        )
        print(f"Coherence = {coherence:.2f}; global phase is not encoded.")
    print("\nAudition order (short noise clicks label each event):")
    print("  1 click  — probability anchors: |0> then |1>, weighted by probability")
    print("  2 clicks — steady sine-like theta cue")
    print("  3 clicks — brighter phi cue (silent at a pole)")
    print("  4 clicks — final probability-anchor chord; invariant under phi")
    if args.axis == "rz":
        print(
            "Teaching note: RZ on the initial |0> changes only global phase, "
            "so the Bloch vector and all state-derived cues stay unchanged."
        )
    played = not args.no_play and play_wav(wav_path)
    if played:
        print(f"Played: {wav_path}")
    else:
        print(f"WAV ready: {wav_path}")
        if not args.no_play:
            print("Automatic playback was unavailable; open the WAV in any player.")
    if args.osc_port is not None:
        publish_qmw(state, port=args.osc_port)
        print(f"Sent the existing QMW circuit messages to UDP port {args.osc_port}.")
    print("Reflect: what can phi change even when the two pitch levels stay balanced?")


if __name__ == "__main__":
    main()
