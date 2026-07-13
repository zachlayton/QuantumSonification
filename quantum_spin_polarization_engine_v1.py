 #!/usr/bin/env python3
"""
quantum_spin_polarization_engine_v1.py

Standalone spin / polarization / superposition OSC engine.

Purpose:
    - Evolve a small quantum state vector.
    - Compute per-qubit Pauli expectation values <X>, <Y>, <Z>.
    - Interpret those as normalized Stokes / polarization coordinates.
    - Send OSC streams to Max.

This file is intentionally standalone so it does not disturb:
    - quantum_population_osc_v5.py
    - quantum_population_osc_v6_shadow.py
    - density_matrix engines
    - mutator / shadowmutator files

Author: Zach Layton / ChatGPT collaboration
"""

from __future__ import annotations

import argparse
import math
import time
from dataclasses import dataclass
from typing import Dict, List, Tuple

import numpy as np

try:
    from pythonosc.udp_client import SimpleUDPClient
except ImportError as exc:
    raise ImportError(
        "Missing dependency: python-osc. Install with:\n"
        "    pip install python-osc"
    ) from exc


# ------------------------------------------------------------
# Basic quantum operators
# ------------------------------------------------------------

I2 = np.array(
    [
        [1.0, 0.0],
        [0.0, 1.0],
    ],
    dtype=np.complex128,
)

X = np.array(
    [
        [0.0, 1.0],
        [1.0, 0.0],
    ],
    dtype=np.complex128,
)

Y = np.array(
    [
        [0.0, -1.0j],
        [1.0j, 0.0],
    ],
    dtype=np.complex128,
)

Z = np.array(
    [
        [1.0, 0.0],
        [0.0, -1.0],
    ],
    dtype=np.complex128,
)

PAULI = {
    "i": I2,
    "x": X,
    "y": Y,
    "z": Z,
}


# ------------------------------------------------------------
# Data containers
# ------------------------------------------------------------

@dataclass
class QubitSpinPolarization:
    qubit: int

    x: float
    y: float
    z: float

    # Polarization/Stokes interpretation.
    s1: float  # H/V-like contrast, mapped from Z
    s2: float  # diagonal/anti-diagonal-like contrast, mapped from X
    s3: float  # right/left circular-like contrast, mapped from Y

    degree: float
    azimuth: float
    ellipticity_angle: float
    circularity: float
    linearity: float


@dataclass
class EngineConfig:
    n_qubits: int = 4
    osc_host: str = "127.0.0.1"
    osc_port: int = 7400
    interval: float = 0.05

    # Evolution controls.
    base_rx: float = 0.013
    base_ry: float = 0.021
    base_rz: float = 0.034
    coupling: float = 0.018

    # Slow modulation.
    lfo_rate: float = 0.07
    lfo_depth: float = 0.75

    # Output scaling.
    clamp: float = 1.0


# ------------------------------------------------------------
# Utility functions
# ------------------------------------------------------------

def kron_all(ops: List[np.ndarray]) -> np.ndarray:
    """Kronecker product of a list of matrices."""
    result = ops[0]
    for op in ops[1:]:
        result = np.kron(result, op)
    return result


def single_qubit_operator(
    n_qubits: int,
    qubit_index: int,
    op: np.ndarray,
) -> np.ndarray:
    """
    Build an operator acting on one qubit and identity elsewhere.

    Qubit indexing convention:
        qubit_index = 0 is the leftmost / most significant qubit.
    """
    ops = []
    for i in range(n_qubits):
        ops.append(op if i == qubit_index else I2)
    return kron_all(ops)


def two_qubit_operator(
    n_qubits: int,
    q_a: int,
    op_a: np.ndarray,
    q_b: int,
    op_b: np.ndarray,
) -> np.ndarray:
    """Build a two-qubit Pauli product operator."""
    ops = []
    for i in range(n_qubits):
        if i == q_a:
            ops.append(op_a)
        elif i == q_b:
            ops.append(op_b)
        else:
            ops.append(I2)
    return kron_all(ops)


def expectation(
    state: np.ndarray,
    operator: np.ndarray,
) -> float:
    """Compute real expectation value <psi|O|psi>."""
    value = np.vdot(state, operator @ state)
    return float(np.real_if_close(value))


def normalize_state(state: np.ndarray) -> np.ndarray:
    norm = np.linalg.norm(state)
    if norm <= 0.0:
        raise ValueError("Cannot normalize zero state.")
    return state / norm


def rotation(op: np.ndarray, angle: float) -> np.ndarray:
    """
    Single-qubit unitary rotation:

        R_op(angle) = exp(-i angle op / 2)

    For Pauli matrices:
        R = cos(angle/2) I - i sin(angle/2) op
    """
    return (
        math.cos(angle / 2.0) * I2
        - 1.0j * math.sin(angle / 2.0) * op
    )


def clamp_float(value: float, limit: float = 1.0) -> float:
    return max(-limit, min(limit, float(value)))


def safe_asin(value: float) -> float:
    return math.asin(max(-1.0, min(1.0, value)))


# ------------------------------------------------------------
# Main engine
# ------------------------------------------------------------

class QuantumSpinPolarizationEngine:
    def __init__(self, config: EngineConfig) -> None:
        self.config = config
        self.n = config.n_qubits
        self.dim = 2 ** self.n
        self.client = SimpleUDPClient(config.osc_host, config.osc_port)

        self.t = 0.0
        self.step_count = 0

        # Start in |000...0>
        self.state = np.zeros(self.dim, dtype=np.complex128)
        self.state[0] = 1.0 + 0.0j

        # Precompute per-qubit Pauli operators.
        self.x_ops = [
            single_qubit_operator(self.n, q, X)
            for q in range(self.n)
        ]
        self.y_ops = [
            single_qubit_operator(self.n, q, Y)
            for q in range(self.n)
        ]
        self.z_ops = [
            single_qubit_operator(self.n, q, Z)
            for q in range(self.n)
        ]

        # Simple neighbor coupling operators.
        self.zz_couplings = []
        for q in range(self.n - 1):
            self.zz_couplings.append(
                two_qubit_operator(self.n, q, Z, q + 1, Z)
            )

    # --------------------------------------------------------
    # State evolution
    # --------------------------------------------------------

    def apply_single_qubit_gate(
        self,
        qubit: int,
        gate: np.ndarray,
    ) -> None:
        full_gate = single_qubit_operator(self.n, qubit, gate)
        self.state = full_gate @ self.state
        self.state = normalize_state(self.state)

    def evolve(self, dt: float) -> None:
        """
        Lightweight internal evolution.

        This is not meant to be a physically exact Hamiltonian solver yet.
        It is an exploratory spin/polarization oscillator:
            - each qubit receives small X/Y/Z rotations
            - neighboring qubits receive a mild ZZ phase coupling
        """

        self.t += dt
        self.step_count += 1

        cfg = self.config

        slow_lfo = 1.0 + cfg.lfo_depth * math.sin(
            2.0 * math.pi * cfg.lfo_rate * self.t
        )

        for q in range(self.n):
            q_phase = 0.37 * q

            rx_angle = cfg.base_rx * slow_lfo * math.sin(self.t * 0.71 + q_phase)
            ry_angle = cfg.base_ry * slow_lfo * math.cos(self.t * 0.53 + q_phase)
            rz_angle = cfg.base_rz * slow_lfo * math.sin(self.t * 0.41 + q_phase)

            self.apply_single_qubit_gate(q, rotation(X, rx_angle))
            self.apply_single_qubit_gate(q, rotation(Y, ry_angle))
            self.apply_single_qubit_gate(q, rotation(Z, rz_angle))

        # Apply simple ZZ coupling as phase evolution.
        # U ≈ exp(-i * coupling * ZZ)
        for zz in self.zz_couplings:
            angle = cfg.coupling * slow_lfo
            unitary = (
                math.cos(angle) * np.eye(self.dim, dtype=np.complex128)
                - 1.0j * math.sin(angle) * zz
            )
            self.state = unitary @ self.state
            self.state = normalize_state(self.state)

    # --------------------------------------------------------
    # Analysis
    # --------------------------------------------------------

    def qubit_spin_polarization(
        self,
        qubit: int,
    ) -> QubitSpinPolarization:
        """
        Compute per-qubit spin expectations and Stokes-style descriptors.

        Mapping:
            <Z> -> S1  horizontal / vertical contrast
            <X> -> S2  diagonal / anti-diagonal contrast
            <Y> -> S3  circular / quadrature contrast
        """

        x = expectation(self.state, self.x_ops[qubit])
        y = expectation(self.state, self.y_ops[qubit])
        z = expectation(self.state, self.z_ops[qubit])

        x = clamp_float(x, self.config.clamp)
        y = clamp_float(y, self.config.clamp)
        z = clamp_float(z, self.config.clamp)

        s1 = z
        s2 = x
        s3 = y

        degree = math.sqrt(s1 * s1 + s2 * s2 + s3 * s3)
        degree = max(0.0, min(1.0, degree))

        # Polarization azimuth:
        #   psi = 1/2 atan2(S2, S1)
        azimuth = 0.5 * math.atan2(s2, s1)

        # Ellipticity angle:
        #   chi = 1/2 asin(S3 / degree)
        if degree > 1e-9:
            ellipticity_angle = 0.5 * safe_asin(s3 / degree)
        else:
            ellipticity_angle = 0.0

        circularity = abs(s3)
        linearity = math.sqrt(s1 * s1 + s2 * s2)

        return QubitSpinPolarization(
            qubit=qubit,
            x=x,
            y=y,
            z=z,
            s1=s1,
            s2=s2,
            s3=s3,
            degree=degree,
            azimuth=azimuth,
            ellipticity_angle=ellipticity_angle,
            circularity=circularity,
            linearity=linearity,
        )

    def all_qubit_spin_polarizations(
        self,
    ) -> List[QubitSpinPolarization]:
        return [
            self.qubit_spin_polarization(q)
            for q in range(self.n)
        ]

    def selected_pauli_strings(self) -> Dict[str, float]:
        """
        A small first set of multi-qubit spin-correlation observables.

        These are useful for later entanglement / correlation mapping.
        """

        values: Dict[str, float] = {}

        if self.n >= 2:
            values["ZZII"] = expectation(
                self.state,
                two_qubit_operator(self.n, 0, Z, 1, Z),
            )
            values["XXII"] = expectation(
                self.state,
                two_qubit_operator(self.n, 0, X, 1, X),
            )
            values["YYII"] = expectation(
                self.state,
                two_qubit_operator(self.n, 0, Y, 1, Y),
            )

        if self.n >= 4:
            values["ZIZI"] = expectation(
                self.state,
                two_qubit_operator(self.n, 0, Z, 2, Z),
            )
            values["IZIZ"] = expectation(
                self.state,
                two_qubit_operator(self.n, 1, Z, 3, Z),
            )
            values["ZZZZ"] = expectation(
                self.state,
                kron_all([Z, Z, Z, Z]),
            )
            values["XXXX"] = expectation(
                self.state,
                kron_all([X, X, X, X]),
            )
            values["YYYY"] = expectation(
                self.state,
                kron_all([Y, Y, Y, Y]),
            )

        return {
            key: clamp_float(value, self.config.clamp)
            for key, value in values.items()
        }

    # --------------------------------------------------------
    # OSC output
    # --------------------------------------------------------

    def send_qubit_osc(
        self,
        data: QubitSpinPolarization,
    ) -> None:
        q = data.qubit

        # Direct Pauli expectations.
        self.client.send_message(f"/qubit/{q}/x", data.x)
        self.client.send_message(f"/qubit/{q}/y", data.y)
        self.client.send_message(f"/qubit/{q}/z", data.z)

        # Stokes-style polarization coordinates.
        self.client.send_message(f"/qubit/{q}/stokes/s1", data.s1)
        self.client.send_message(f"/qubit/{q}/stokes/s2", data.s2)
        self.client.send_message(f"/qubit/{q}/stokes/s3", data.s3)

        # Derived polarization descriptors.
        self.client.send_message(f"/qubit/{q}/polarization/degree", data.degree)
        self.client.send_message(f"/qubit/{q}/polarization/azimuth", data.azimuth)
        self.client.send_message(
            f"/qubit/{q}/polarization/ellipticity",
            data.ellipticity_angle,
        )
        self.client.send_message(
            f"/qubit/{q}/polarization/circularity",
            data.circularity,
        )
        self.client.send_message(
            f"/qubit/{q}/polarization/linearity",
            data.linearity,
        )

    def send_global_osc(
        self,
        qubit_data: List[QubitSpinPolarization],
        pauli_strings: Dict[str, float],
    ) -> None:
        # Global averages.
        avg_x = float(np.mean([q.x for q in qubit_data]))
        avg_y = float(np.mean([q.y for q in qubit_data]))
        avg_z = float(np.mean([q.z for q in qubit_data]))

        avg_circularity = float(np.mean([q.circularity for q in qubit_data]))
        avg_linearity = float(np.mean([q.linearity for q in qubit_data]))
        avg_degree = float(np.mean([q.degree for q in qubit_data]))

        self.client.send_message("/global/spin/x", avg_x)
        self.client.send_message("/global/spin/y", avg_y)
        self.client.send_message("/global/spin/z", avg_z)

        self.client.send_message("/global/polarization/degree", avg_degree)
        self.client.send_message("/global/polarization/circularity", avg_circularity)
        self.client.send_message("/global/polarization/linearity", avg_linearity)

        # Pauli-string correlations.
        for name, value in pauli_strings.items():
            self.client.send_message(f"/pauli/{name}", value)

        self.client.send_message("/engine/time", self.t)
        self.client.send_message("/engine/step", self.step_count)

    def send_osc(self) -> None:
        qubit_data = self.all_qubit_spin_polarizations()
        pauli_strings = self.selected_pauli_strings()

        for data in qubit_data:
            self.send_qubit_osc(data)

        self.send_global_osc(qubit_data, pauli_strings)

    # --------------------------------------------------------
    # Console status
    # --------------------------------------------------------

    def print_status(self) -> None:
        qubits = self.all_qubit_spin_polarizations()

        parts = []
        for q in qubits:
            parts.append(
                f"q{q.qubit}: "
                f"X={q.x:+.3f} "
                f"Y={q.y:+.3f} "
                f"Z={q.z:+.3f} "
                f"circ={q.circularity:.3f}"
            )

        print(" | ".join(parts), flush=True)

    # --------------------------------------------------------
    # Main loop
    # --------------------------------------------------------

    def run(self) -> None:
        cfg = self.config

        print()
        print("Quantum Spin / Polarization Engine v1")
        print("-------------------------------------")
        print(f"qubits:      {cfg.n_qubits}")
        print(f"osc target:  {cfg.osc_host}:{cfg.osc_port}")
        print(f"interval:    {cfg.interval:.3f} sec")
        print()
        print("Sending:")
        print("  /qubit/<i>/x")
        print("  /qubit/<i>/y")
        print("  /qubit/<i>/z")
        print("  /qubit/<i>/stokes/s1")
        print("  /qubit/<i>/stokes/s2")
        print("  /qubit/<i>/stokes/s3")
        print("  /qubit/<i>/polarization/degree")
        print("  /qubit/<i>/polarization/azimuth")
        print("  /qubit/<i>/polarization/ellipticity")
        print("  /qubit/<i>/polarization/circularity")
        print("  /qubit/<i>/polarization/linearity")
        print("  /global/spin/x")
        print("  /global/spin/y")
        print("  /global/spin/z")
        print("  /global/polarization/degree")
        print("  /global/polarization/circularity")
        print("  /global/polarization/linearity")
        print("  /pauli/<STRING>")
        print()

        last_print = time.time()

        try:
            while True:
                self.evolve(cfg.interval)
                self.send_osc()

                now = time.time()
                if now - last_print >= 1.0:
                    self.print_status()
                    last_print = now

                time.sleep(cfg.interval)

        except KeyboardInterrupt:
            print()
            print("Stopped.")


# ------------------------------------------------------------
# CLI
# ------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Quantum spin / polarization OSC engine."
    )

    parser.add_argument(
        "--qubits",
        type=int,
        default=4,
        help="Number of qubits. Default: 4.",
    )

    parser.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="OSC host. Default: 127.0.0.1.",
    )

    parser.add_argument(
        "--port",
        type=int,
        default=7400,
        help="OSC output port. Default: 7400.",
    )

    parser.add_argument(
        "--interval",
        type=float,
        default=0.05,
        help="Update interval in seconds. Default: 0.05.",
    )

    parser.add_argument(
        "--rx",
        type=float,
        default=0.013,
        help="Base X rotation amount. Default: 0.013.",
    )

    parser.add_argument(
        "--ry",
        type=float,
        default=0.021,
        help="Base Y rotation amount. Default: 0.021.",
    )

    parser.add_argument(
        "--rz",
        type=float,
        default=0.034,
        help="Base Z rotation amount. Default: 0.034.",
    )

    parser.add_argument(
        "--coupling",
        type=float,
        default=0.018,
        help="Neighbor ZZ coupling amount. Default: 0.018.",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.qubits < 1:
        raise ValueError("--qubits must be >= 1")

    if args.qubits > 8:
        raise ValueError(
            "This standalone prototype is intended for <= 8 qubits."
        )

    config = EngineConfig(
        n_qubits=args.qubits,
        osc_host=args.host,
        osc_port=args.port,
        interval=args.interval,
        base_rx=args.rx,
        base_ry=args.ry,
        base_rz=args.rz,
        coupling=args.coupling,
    )

    engine = QuantumSpinPolarizationEngine(config)
    engine.run()


if __name__ == "__main__":
    main()