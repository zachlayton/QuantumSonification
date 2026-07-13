#!/usr/bin/env python3
"""
quantum_spin_polarization_engine_v3_measurement_basis.py

Standalone Pauli spin / polarization / measurement-basis OSC engine.
Purpose:
    - Evolve a small quantum state vector.
    - Compute per-qubit Pauli expectation values <X>, <Y>, <Z>.
    - Interpret those as normalized Stokes / polarization coordinates.
    - Track per-qubit measurement/listener basis state for circuit-driven
      basis rotations and future dynamic-circuit feedforward.
    - Send OSC streams to Max.

This file is intentionally standalone so it does not disturb:
    - quantum_population_osc_v5.py
    - quantum_population_osc_v6_shadow.py
    - density_matrix engines
    - mutator / shadowmutator files

"""

from __future__ import annotations

import argparse
import math
import time
from dataclasses import dataclass
from typing import Dict, List

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
class MeasurementBasis:
    qubit: int
    label: str = "MZ"
    theta: float = 0.0
    phi: float = 0.0
    source: str = "circuit"


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

    # Bloch spherical coordinates.
    bloch_r: float
    bloch_theta: float
    bloch_phi: float

    # Moving measurement/listening basis.
    basis_theta: float
    basis_phi: float
    basis_label: str
    basis_projection: float
    measure_prob0: float
    measure_prob1: float
    measure_outcome: int
    measure_collapse: int

    # Audio-normalized descriptors.
    audio_phase: float
    audio_swirl: float
    audio_interference: float
    audio_brightness: float


@dataclass
class EngineConfig:
    n_qubits: int = 4
    osc_host: str = "127.0.0.1"
    osc_port: int = 7400
    interval: float = 0.05

    # Initial state:
    #   zero       -> |0000>
    #   plus       -> |++++>
    #   yplus      -> |y+y+y+y+>
    #   random     -> random complex normalized state
    #   ghz        -> (|0000> + |1111>) / sqrt(2)
    #   bell_pairs -> Bell pairs across (0,1), (2,3), ...
    init_state: str = "zero"

    # Motion mode:
    #   gentle   -> close to v1
    #   orbit    -> smoother Bloch orbiting
    #   tumble   -> stronger axis-mixing
    #   entangle -> stronger ZZ/XX/YY correlation behavior
    motion: str = "gentle"

    # Evolution controls.
    base_rx: float = 0.013
    base_ry: float = 0.021
    base_rz: float = 0.034
    coupling: float = 0.018

    # Slow modulation.
    lfo_rate: float = 0.07
    lfo_depth: float = 0.75

    # Measurement basis angles.
    basis_theta: float = 0.0
    basis_phi: float = 0.0
    measurement_label: str = "MZ"
    measurement_source: str = "circuit"

    # Legacy animated basis controls. These are used only when
    # measurement_source == "lfo".
    basis_rate_theta: float = 0.031
    basis_rate_phi: float = 0.047
    basis_depth_theta: float = 0.65
    basis_depth_phi: float = 1.0

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


def measurement_label(theta: float, phi: float) -> str:
    if abs(theta) < 1e-6:
        return "MZ"
    if abs(theta - math.pi / 2.0) < 1e-6:
        if abs(phi) < 1e-6:
            return "MX"
        if abs(phi - math.pi / 2.0) < 1e-6:
            return "MY"
    return "MN"


def basis_state(index: int, dim: int) -> np.ndarray:
    state = np.zeros(dim, dtype=np.complex128)
    state[index] = 1.0 + 0.0j
    return state


def product_state(single_qubit_state: np.ndarray, n_qubits: int) -> np.ndarray:
    state = single_qubit_state
    for _ in range(n_qubits - 1):
        state = np.kron(state, single_qubit_state)
    return normalize_state(state)


def random_complex_state(dim: int, seed: int | None = None) -> np.ndarray:
    rng = np.random.default_rng(seed)
    real = rng.normal(size=dim)
    imag = rng.normal(size=dim)
    state = real + 1.0j * imag
    return normalize_state(state.astype(np.complex128))


def make_initial_state(init_state: str, n_qubits: int) -> np.ndarray:
    dim = 2 ** n_qubits
    init = init_state.lower().strip()

    zero = np.array([1.0, 0.0], dtype=np.complex128)
    plus = np.array([1.0, 1.0], dtype=np.complex128) / math.sqrt(2.0)
    yplus = np.array([1.0, 1.0j], dtype=np.complex128) / math.sqrt(2.0)

    if init == "zero":
        return basis_state(0, dim)

    if init == "plus":
        return product_state(plus, n_qubits)

    if init == "yplus":
        return product_state(yplus, n_qubits)

    if init == "random":
        return random_complex_state(dim)

    if init == "ghz":
        state = np.zeros(dim, dtype=np.complex128)
        state[0] = 1.0 / math.sqrt(2.0)
        state[-1] = 1.0 / math.sqrt(2.0)
        return normalize_state(state)

    if init == "bell_pairs":
        if n_qubits % 2 != 0:
            raise ValueError("--init bell_pairs requires an even number of qubits")

        bell = np.array(
            [1.0, 0.0, 0.0, 1.0],
            dtype=np.complex128,
        ) / math.sqrt(2.0)

        state = bell
        for _ in range((n_qubits // 2) - 1):
            state = np.kron(state, bell)

        return normalize_state(state)

    raise ValueError(
        f"Unknown init state: {init_state}. "
        "Use zero, plus, yplus, random, ghz, or bell_pairs."
    )




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
        self.rng = np.random.default_rng()

        # Configurable initial state.
        self.state = make_initial_state(config.init_state, self.n)
        self.measurement_bases = [
            MeasurementBasis(
                qubit=q,
                label=config.measurement_label,
                theta=config.basis_theta,
                phi=config.basis_phi,
                source=config.measurement_source,
            )
            for q in range(self.n)
        ]

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


        self.t += dt
        self.step_count += 1

        cfg = self.config
        motion = cfg.motion.lower().strip()

        if motion == "gentle":
            rx_scale = 1.0
            ry_scale = 1.0
            rz_scale = 1.0
            coupling_scale = 1.0

        elif motion == "orbit":
            rx_scale = 1.4
            ry_scale = 1.8
            rz_scale = 0.8
            coupling_scale = 0.7

        elif motion == "tumble":
            rx_scale = 2.4
            ry_scale = 2.1
            rz_scale = 1.9
            coupling_scale = 1.2

        elif motion == "entangle":
            rx_scale = 1.2
            ry_scale = 1.2
            rz_scale = 0.8
            coupling_scale = 2.6

        else:
            raise ValueError(
                f"Unknown motion mode: {cfg.motion}. "
                "Use gentle, orbit, tumble, or entangle."
            )

        slow_lfo = 1.0 + cfg.lfo_depth * math.sin(
            2.0 * math.pi * cfg.lfo_rate * self.t
        )

        for q in range(self.n):
            q_phase = 0.37 * q

            if motion == "orbit":
                rx_angle = cfg.base_rx * rx_scale * slow_lfo * math.sin(
                    self.t * 0.61 + q_phase
                )
                ry_angle = cfg.base_ry * ry_scale * slow_lfo * math.cos(
                    self.t * 0.61 + q_phase
                )
                rz_angle = cfg.base_rz * rz_scale * slow_lfo * math.sin(
                    self.t * 0.19 + q_phase
                )

            elif motion == "tumble":
                rx_angle = cfg.base_rx * rx_scale * slow_lfo * (
                    math.sin(self.t * 0.71 + q_phase)
                    + 0.37 * math.sin(self.t * 1.37 + 0.11 * q)
                )
                ry_angle = cfg.base_ry * ry_scale * slow_lfo * (
                    math.cos(self.t * 0.53 + q_phase)
                    + 0.29 * math.sin(self.t * 1.11 + 0.23 * q)
                )
                rz_angle = cfg.base_rz * rz_scale * slow_lfo * (
                    math.sin(self.t * 0.41 + q_phase)
                    + 0.31 * math.cos(self.t * 1.73 + 0.17 * q)
                )

            else:
                rx_angle = cfg.base_rx * rx_scale * slow_lfo * math.sin(
                    self.t * 0.71 + q_phase
                )
                ry_angle = cfg.base_ry * ry_scale * slow_lfo * math.cos(
                    self.t * 0.53 + q_phase
                )
                rz_angle = cfg.base_rz * rz_scale * slow_lfo * math.sin(
                    self.t * 0.41 + q_phase
                )

            self.apply_single_qubit_gate(q, rotation(X, rx_angle))
            self.apply_single_qubit_gate(q, rotation(Y, ry_angle))
            self.apply_single_qubit_gate(q, rotation(Z, rz_angle))

        # Pair couplings.
        angle = cfg.coupling * coupling_scale * slow_lfo

        for q in range(self.n - 1):
            zz = two_qubit_operator(self.n, q, Z, q + 1, Z)
            unitary = (
                math.cos(angle) * np.eye(self.dim, dtype=np.complex128)
                - 1.0j * math.sin(angle) * zz
            )
            self.state = unitary @ self.state
            self.state = normalize_state(self.state)

            if motion == "entangle":
                xx = two_qubit_operator(self.n, q, X, q + 1, X)
                yy = two_qubit_operator(self.n, q, Y, q + 1, Y)

                xx_unitary = (
                    math.cos(angle * 0.55) * np.eye(self.dim, dtype=np.complex128)
                    - 1.0j * math.sin(angle * 0.55) * xx
                )
                yy_unitary = (
                    math.cos(angle * 0.35) * np.eye(self.dim, dtype=np.complex128)
                    - 1.0j * math.sin(angle * 0.35) * yy
                )

                self.state = xx_unitary @ self.state
                self.state = yy_unitary @ self.state
                self.state = normalize_state(self.state)

    # --------------------------------------------------------
    # Analysis
    # --------------------------------------------------------

    def current_basis_angles(self) -> tuple[float, float]:
        """
        Global measurement basis angles for compatibility.

        In v3 the default basis is held in per-qubit MeasurementBasis state.
        The old LFO basis is available only with --measurement-source lfo.
        """
        return self.measurement_basis_for_qubit(0).theta, self.measurement_basis_for_qubit(0).phi

    def lfo_basis_for_qubit(self, qubit: int) -> MeasurementBasis:
        cfg = self.config

        theta = cfg.basis_theta + cfg.basis_depth_theta * math.sin(
            2.0 * math.pi * cfg.basis_rate_theta * self.t + 0.13 * qubit
        )

        phi = cfg.basis_phi + cfg.basis_depth_phi * math.sin(
            2.0 * math.pi * cfg.basis_rate_phi * self.t + 0.21 * qubit
        )

        return MeasurementBasis(
            qubit=qubit,
            label=measurement_label(theta, phi),
            theta=theta,
            phi=phi,
            source="lfo",
        )

    def measurement_basis_for_qubit(self, qubit: int) -> MeasurementBasis:
        source = self.config.measurement_source.lower().strip()
        if source == "lfo":
            return self.lfo_basis_for_qubit(qubit)
        return self.measurement_bases[qubit]

    def set_measurement_basis(
        self,
        q: int,
        label: str,
        theta: float,
        phi: float,
    ) -> None:
        if not (0 <= q < self.n):
            raise IndexError(f"Qubit index {q} is out of range.")

        self.measurement_bases[q] = MeasurementBasis(
            qubit=q,
            label=str(label),
            theta=float(theta),
            phi=float(phi),
            source=self.config.measurement_source,
        )

    def basis_projection(
        self,
        x: float,
        y: float,
        z: float,
        theta: float,
        phi: float,
    ) -> float:
        """
        Project the Bloch vector onto an arbitrary measurement axis:

            n = (sin(theta)cos(phi), sin(theta)sin(phi), cos(theta))

            projection = r · n
        """

        nx = math.sin(theta) * math.cos(phi)
        ny = math.sin(theta) * math.sin(phi)
        nz = math.cos(theta)

        return clamp_float(x * nx + y * ny + z * nz, self.config.clamp)

    def measurement_projection(self, q: int) -> float:
        """Project simulated circuit-state Bloch data onto the listener basis."""
        if not (0 <= q < self.n):
            raise IndexError(f"Qubit index {q} is out of range.")

        # The quantum state is simulation data. The basis is external listener
        # state, normally supplied by a circuit measurement gate.
        basis = self.measurement_basis_for_qubit(q)
        x = expectation(self.state, self.x_ops[q])
        y = expectation(self.state, self.y_ops[q])
        z = expectation(self.state, self.z_ops[q])
        return self.basis_projection(x, y, z, basis.theta, basis.phi)

    def measurement_probabilities(self, q: int) -> tuple[float, float]:
        projection = self.measurement_projection(q)
        prob0 = float(np.clip(0.5 * (projection + 1.0), 0.0, 1.0))
        return prob0, 1.0 - prob0

    def sample_measurement_outcome(self, prob0: float, prob1: float) -> int:
        return int(self.rng.choice([0, 1], p=[prob0, prob1]))

    def measurement_axis_operator(self, q: int) -> np.ndarray:
        basis = self.measurement_basis_for_qubit(q)
        axis = (
            math.sin(basis.theta) * math.cos(basis.phi) * X
            + math.sin(basis.theta) * math.sin(basis.phi) * Y
            + math.cos(basis.theta) * Z
        )
        return single_qubit_operator(self.n, q, axis)

    def apply_projective_measurement(self, q: int) -> int:
        if not (0 <= q < self.n):
            raise IndexError(f"Qubit index {q} is out of range.")

        prob0, prob1 = self.measurement_probabilities(q)
        outcome = self.sample_measurement_outcome(prob0, prob1)
        axis = self.measurement_axis_operator(q)
        identity = np.eye(self.dim, dtype=np.complex128)

        projector = (
            0.5 * (identity + axis)
            if outcome == 0
            else 0.5 * (identity - axis)
        )
        self.state = projector @ self.state
        self.state = normalize_state(self.state)
        return outcome

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

        # Bloch spherical coordinates.
        bloch_r = degree

        if bloch_r > 1e-9:
            bloch_theta = math.acos(max(-1.0, min(1.0, z / bloch_r)))
            bloch_phi = math.atan2(y, x)
        else:
            bloch_theta = 0.0
            bloch_phi = 0.0

        basis = self.measurement_basis_for_qubit(qubit)
        basis_proj = self.basis_projection(
            x=x,
            y=y,
            z=z,
            theta=basis.theta,
            phi=basis.phi,
        )
        measure_prob0 = 0.5 * (basis_proj + 1.0)
        measure_prob0 = max(0.0, min(1.0, measure_prob0))
        measure_prob1 = 1.0 - measure_prob0
        measure_outcome = self.sample_measurement_outcome(
            measure_prob0,
            measure_prob1,
        )

        # Audio descriptors:
        #   phase:         normalized Bloch azimuth, -1..1
        #   swirl:         circular/quadrature emphasis
        #   interference:  real coherence emphasis
        #   brightness:    positive-normalized Z
        audio_phase = bloch_phi / math.pi
        audio_swirl = y
        audio_interference = x
        audio_brightness = 0.5 * (z + 1.0)

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
            bloch_r=bloch_r,
            bloch_theta=bloch_theta,
            bloch_phi=bloch_phi,
            basis_theta=basis.theta,
            basis_phi=basis.phi,
            basis_label=basis.label,
            basis_projection=basis_proj,
            measure_prob0=measure_prob0,
            measure_prob1=measure_prob1,
            measure_outcome=measure_outcome,
            measure_collapse=0,
            audio_phase=audio_phase,
            audio_swirl=audio_swirl,
            audio_interference=audio_interference,
            audio_brightness=audio_brightness,
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

        # Bloch coordinates.
        self.client.send_message(f"/qubit/{q}/bloch/r", data.bloch_r)
        self.client.send_message(f"/qubit/{q}/bloch/theta", data.bloch_theta)
        self.client.send_message(f"/qubit/{q}/bloch/phi", data.bloch_phi)

        # Measurement/listening basis outputs.
        self.client.send_message(f"/qubit/{q}/basis/theta", data.basis_theta)
        self.client.send_message(f"/qubit/{q}/basis/phi", data.basis_phi)
        self.client.send_message(
            f"/qubit/{q}/basis/projection",
            data.basis_projection,
        )
        self.client.send_message(f"/basis/{q}/theta", data.basis_theta)
        self.client.send_message(f"/basis/{q}/phi", data.basis_phi)
        self.client.send_message(
            f"/basis/{q}/projection",
            data.basis_projection,
        )
        self.client.send_message(
            f"/qubit/{q}/measure/basis/theta",
            data.basis_theta,
        )
        self.client.send_message(
            f"/qubit/{q}/measure/basis/phi",
            data.basis_phi,
        )
        self.client.send_message(
            f"/qubit/{q}/measure/basis/label",
            data.basis_label,
        )
        self.client.send_message(
            f"/qubit/{q}/measure/projection",
            data.basis_projection,
        )
        self.client.send_message(f"/qubit/{q}/measure/prob0", data.measure_prob0)
        self.client.send_message(f"/qubit/{q}/measure/prob1", data.measure_prob1)
        self.client.send_message(
            f"/qubit/{q}/measure/outcome",
            data.measure_outcome,
        )
        self.client.send_message(
            f"/qubit/{q}/measure/collapse",
            data.measure_collapse,
        )

        # Audio-oriented outputs.
        self.client.send_message(f"/qubit/{q}/audio/phase", data.audio_phase)
        self.client.send_message(f"/qubit/{q}/audio/swirl", data.audio_swirl)
        self.client.send_message(
            f"/qubit/{q}/audio/interference",
            data.audio_interference,
        )
        self.client.send_message(
            f"/qubit/{q}/audio/brightness",
            data.audio_brightness,
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
        avg_basis_projection = float(np.mean([q.basis_projection for q in qubit_data]))
        active = max(qubit_data, key=lambda q: abs(q.basis_projection))
        avg_audio_phase = float(np.mean([q.audio_phase for q in qubit_data]))
        avg_audio_swirl = float(np.mean([q.audio_swirl for q in qubit_data]))
        avg_audio_interference = float(
            np.mean([q.audio_interference for q in qubit_data])
        )
        avg_audio_brightness = float(
            np.mean([q.audio_brightness for q in qubit_data])
        )

        self.client.send_message("/global/spin/x", avg_x)
        self.client.send_message("/global/spin/y", avg_y)
        self.client.send_message("/global/spin/z", avg_z)

        self.client.send_message("/global/polarization/degree", avg_degree)
        self.client.send_message("/global/polarization/circularity", avg_circularity)
        self.client.send_message("/global/polarization/linearity", avg_linearity)

        theta, phi = self.current_basis_angles()
        self.client.send_message("/global/basis/theta", theta)
        self.client.send_message("/global/basis/phi", phi)
        self.client.send_message("/global/basis/projection", avg_basis_projection)
        self.client.send_message(
            "/circuit/measurement/active_qubit",
            active.qubit,
        )
        self.client.send_message(
            "/circuit/measurement/active_basis",
            active.basis_label,
        )
        self.client.send_message("/circuit/measurement/step", self.step_count)
        self.client.send_message(
            "/circuit/measurement/mode",
            self.config.measurement_source,
        )

        self.client.send_message("/global/audio/phase", avg_audio_phase)
        self.client.send_message("/global/audio/swirl", avg_audio_swirl)
        self.client.send_message(
            "/global/audio/interference",
            avg_audio_interference,
        )
        self.client.send_message(
            "/global/audio/brightness",
            avg_audio_brightness,
        )

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
                f"basis={q.basis_projection:+.3f} "
                f"theta={q.basis_theta:+.3f} "
                f"phi={q.basis_phi:+.3f} "
                f"swirl={q.audio_swirl:+.3f}"
            )

        print(" | ".join(parts), flush=True)

    # --------------------------------------------------------
    # Main loop
    # --------------------------------------------------------

    def run(self) -> None:
        cfg = self.config

        print()
        print("Quantum Spin / Polarization Engine v3 Measurement Basis")
        print("-------------------------------------------------------")
        print(f"qubits:      {cfg.n_qubits}")
        print(f"osc target:  {cfg.osc_host}:{cfg.osc_port}")
        print(f"interval:    {cfg.interval:.3f} sec")
        print(f"init state:  {cfg.init_state}")
        print(f"motion:      {cfg.motion}")
        print(f"measurement: {cfg.measurement_source}")
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
        print("  /qubit/<i>/bloch/r")
        print("  /qubit/<i>/bloch/theta")
        print("  /qubit/<i>/bloch/phi")
        print("  /qubit/<i>/basis/theta")
        print("  /qubit/<i>/basis/phi")
        print("  /qubit/<i>/basis/projection")
        print("  /basis/<i>/theta")
        print("  /basis/<i>/phi")
        print("  /basis/<i>/projection")
        print("  /qubit/<i>/measure/basis/theta")
        print("  /qubit/<i>/measure/basis/phi")
        print("  /qubit/<i>/measure/basis/label")
        print("  /qubit/<i>/measure/projection")
        print("  /qubit/<i>/measure/prob0")
        print("  /qubit/<i>/measure/prob1")
        print("  /qubit/<i>/measure/outcome")
        print("  /qubit/<i>/measure/collapse")
        print("  /qubit/<i>/audio/phase")
        print("  /qubit/<i>/audio/swirl")
        print("  /qubit/<i>/audio/interference")
        print("  /qubit/<i>/audio/brightness")
        print("  /global/spin/x")
        print("  /global/spin/y")
        print("  /global/spin/z")
        print("  /global/polarization/degree")
        print("  /global/polarization/circularity")
        print("  /global/polarization/linearity")
        print("  /global/basis/theta")
        print("  /global/basis/phi")
        print("  /global/basis/projection")
        print("  /circuit/measurement/active_qubit")
        print("  /circuit/measurement/active_basis")
        print("  /circuit/measurement/step")
        print("  /circuit/measurement/mode")
        print("  /global/audio/phase")
        print("  /global/audio/swirl")
        print("  /global/audio/interference")
        print("  /global/audio/brightness")
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
        description="Quantum spin / polarization OSC engine with measurement-basis state."
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
        "--init",
        type=str,
        default="zero",
        choices=["zero", "plus", "yplus", "random", "ghz", "bell_pairs"],
        help="Initial state. Default: zero.",
    )

    parser.add_argument(
        "--motion",
        type=str,
        default="gentle",
        choices=["gentle", "orbit", "tumble", "entangle"],
        help="Bloch exploration motion mode. Default: gentle.",
    )

    parser.add_argument(
        "--basis-theta",
        type=float,
        default=0.0,
        help="Base measurement basis theta angle in radians. Default: 0.0.",
    )

    parser.add_argument(
        "--basis-phi",
        type=float,
        default=0.0,
        help="Base measurement basis phi angle in radians. Default: 0.0.",
    )

    parser.add_argument(
        "--measurement-source",
        type=str,
        default="circuit",
        choices=["lfo", "circuit", "pauli", "max"],
        help=(
            "Measurement basis source. Default: circuit. "
            "Use lfo for the legacy animated basis."
        ),
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
        init_state=args.init,
        motion=args.motion,
        base_rx=args.rx,
        base_ry=args.ry,
        base_rz=args.rz,
        coupling=args.coupling,
        basis_theta=args.basis_theta,
        basis_phi=args.basis_phi,
        measurement_source=args.measurement_source,
    )

    engine = QuantumSpinPolarizationEngine(config)
    engine.run()


if __name__ == "__main__":
    main()
