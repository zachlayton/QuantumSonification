#!/usr/bin/env python3
"""Small exact Grover reference used by the Max/QASM workshop patch.

The Max JavaScript performs the same literal oracle and diffusion updates.
This Python companion keeps the circuit and its expected probabilities easy
to validate without contacting IBM hardware.
"""

from __future__ import annotations

import math


MCX_DEFINITION = (
    "gate mcx q0,q1,q2,q3 { "
    "h q3; "
    "u1(pi/8) q0; u1(pi/8) q1; u1(pi/8) q2; u1(pi/8) q3; "
    "cx q0,q1; u1(-pi/8) q1; cx q0,q1; "
    "cx q1,q2; u1(-pi/8) q2; cx q0,q2; u1(pi/8) q2; "
    "cx q1,q2; u1(-pi/8) q2; cx q0,q2; "
    "cx q2,q3; u1(-pi/8) q3; cx q1,q3; u1(pi/8) q3; "
    "cx q2,q3; u1(-pi/8) q3; cx q0,q3; u1(pi/8) q3; "
    "cx q2,q3; u1(-pi/8) q3; cx q1,q3; u1(pi/8) q3; "
    "cx q2,q3; u1(-pi/8) q3; cx q0,q3; "
    "h q3; "
    "}"
)


def _check(target: int, iterations: int) -> None:
    if not 0 <= target < 16:
        raise ValueError("target must be in 0..15")
    if not 0 <= iterations <= 3:
        raise ValueError("iterations must be in 0..3")


def exact_probabilities(target: int = 9, iterations: int = 3) -> list[float]:
    """Evolve the 16 amplitudes with literal oracle/diffusion reflections."""

    _check(target, iterations)
    amplitudes = [1.0 / math.sqrt(16)] * 16
    for _ in range(iterations):
        amplitudes[target] *= -1.0
        mean = sum(amplitudes) / 16.0
        amplitudes = [2.0 * mean - amplitude for amplitude in amplitudes]
    return [amplitude * amplitude for amplitude in amplitudes]


def build_qasm(target: int = 9, iterations: int = 3) -> str:
    """Build portable OpenQASM 2 for a four-qubit, one-target Grover search."""

    _check(target, iterations)
    statements = [
        "OPENQASM 2.0;",
        'include "qelib1.inc";',
        MCX_DEFINITION,
        "qreg q[4];",
        "h q[0]; h q[1]; h q[2]; h q[3];",
    ]
    zero_bits = [qubit for qubit in range(4) if not (target >> qubit) & 1]
    flip_zeros = " ".join(f"x q[{qubit}];" for qubit in zero_bits)
    for _ in range(iterations):
        if flip_zeros:
            statements.append(flip_zeros)
        statements.append("h q[3]; mcx q[0],q[1],q[2],q[3]; h q[3];")
        if flip_zeros:
            statements.append(flip_zeros)
        statements.append(
            "h q[0]; h q[1]; h q[2]; h q[3]; "
            "x q[0]; x q[1]; x q[2]; x q[3]; "
            "h q[3]; mcx q[0],q[1],q[2],q[3]; h q[3]; "
            "x q[0]; x q[1]; x q[2]; x q[3]; "
            "h q[0]; h q[1]; h q[2]; h q[3];"
        )
    return " ".join(statements)


if __name__ == "__main__":
    probabilities = exact_probabilities()
    print(build_qasm())
    print(f"marked |1001>: {probabilities[9]:.6f}")
