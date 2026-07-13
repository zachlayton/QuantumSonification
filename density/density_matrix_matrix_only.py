# density_matrix_matrix_only.py
#
# Matrix-only density-matrix engine.
#
# Python -> Max: port 7400
# Max -> Python: port 7401
#
# Max controls:
#
# /noise  /dephase       0.0 - 1.0
# /noise  /damping       0.0 - 1.0
# /noise  /depolarize    0.0 - 1.0
#
# /field  /feedback      0.0 - 1.0
# /field  /coupling      0.0 - 2.0
# /field  /speed         0.0 - 2.0
# /field  /x0            -1.0 - 1.0
# /field  /y0            -1.0 - 1.0
# /field  /z0            -1.0 - 1.0
# /field  /x1            -1.0 - 1.0
# /field  /y1            -1.0 - 1.0
# /field  /z1            -1.0 - 1.0
#
# /engine /freeze        0 or 1
# /engine /reset
#
# Max sending structure:
#
# [flonum]
# |
# [prepend /feedback]
# |
# [prepend /field]
# |
# [OSC-send 127.0.0.1 7401]


import time
import threading
import numpy as np

from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import ThreadingOSCUDPServer
from pythonosc.udp_client import SimpleUDPClient


# ------------------------------------------------------------
# OSC configuration
# ------------------------------------------------------------

OSC_SEND_HOST = "127.0.0.1"
OSC_SEND_PORT = 7400

OSC_RECEIVE_HOST = "127.0.0.1"
OSC_RECEIVE_PORT = 7401

UPDATE_RATE_HZ = 30.0
DT = 1.0 / UPDATE_RATE_HZ


# ------------------------------------------------------------
# Quantum matrices
# ------------------------------------------------------------

I2 = np.eye(2, dtype=complex)

X = np.array([
    [0, 1],
    [1, 0],
], dtype=complex)

Y = np.array([
    [0, -1j],
    [1j, 0],
], dtype=complex)

Z = np.array([
    [1, 0],
    [0, -1],
], dtype=complex)


def kron(a, b):
    return np.kron(a, b)


XI = kron(X, I2)
YI = kron(Y, I2)
ZI = kron(Z, I2)

IX = kron(I2, X)
IY = kron(I2, Y)
IZ = kron(I2, Z)

XX = kron(X, X)
YY = kron(Y, Y)
ZZ = kron(Z, Z)

XY = kron(X, Y)
YX = kron(Y, X)


# ------------------------------------------------------------
# Controls
# ------------------------------------------------------------

DEFAULT_CONTROLS = {
    "dephase": 0.0,
    "damping": 0.0,
    "depolarize": 0.0,

    "feedback": 0.55,
    "coupling": 0.65,
    "speed": 0.80,

    "x0": 0.24,
    "y0": 0.13,
    "z0": 0.18,

    "x1": -0.18,
    "y1": 0.22,
    "z1": 0.12,

    "freeze": 0.0,
}

controls = DEFAULT_CONTROLS.copy()
controls_lock = threading.Lock()

engine_reset_requested = threading.Event()


def clamp(value, low=0.0, high=1.0):
    return max(low, min(high, float(value)))


def clamp_bipolar(value):
    return max(-1.0, min(1.0, float(value)))


def reset_controls():
    with controls_lock:
        controls.clear()
        controls.update(DEFAULT_CONTROLS)


def get_controls():
    with controls_lock:
        return dict(controls)


# ------------------------------------------------------------
# OSC controls from Max
# ------------------------------------------------------------

def set_noise_parameter(address, parameter, value):
    parameter = str(parameter).lstrip("/").lower()
    value = clamp(value)

    with controls_lock:
        if parameter in ("dephase", "damping", "depolarize"):
            controls[parameter] = value
        else:
            print("Unknown noise parameter:", parameter)
            return

    print(f"noise {parameter}: {value:.3f}")


def set_field_parameter(address, parameter, value):
    parameter = str(parameter).lstrip("/").lower()

    bipolar = {"x0", "y0", "z0", "x1", "y1", "z1"}

    with controls_lock:
        if parameter in bipolar:
            controls[parameter] = clamp_bipolar(value)

        elif parameter == "coupling":
            controls[parameter] = clamp(value, 0.0, 2.0)

        elif parameter in ("feedback", "speed"):
            controls[parameter] = clamp(value, 0.0, 2.0)

        else:
            print("Unknown field parameter:", parameter)
            return

    print(f"field {parameter}: {controls[parameter]:.3f}")


def set_engine_parameter(address, parameter, *values):
    parameter = str(parameter).lstrip("/").lower()

    if parameter == "reset":
        reset_controls()
        engine_reset_requested.set()
        print("engine reset")
        return

    if parameter == "freeze" and values:
        with controls_lock:
            controls["freeze"] = 1.0 if float(values[0]) >= 0.5 else 0.0

        print(f"engine freeze: {controls['freeze']:.0f}")
        return

    print("Unknown engine parameter:", parameter)


def start_osc_control_server():
    dispatcher = Dispatcher()

    dispatcher.map("/noise", set_noise_parameter)
    dispatcher.map("/field", set_field_parameter)
    dispatcher.map("/engine", set_engine_parameter)

    server = ThreadingOSCUDPServer(
        (OSC_RECEIVE_HOST, OSC_RECEIVE_PORT),
        dispatcher,
    )

    print(
        f"Listening for Max controls on "
        f"{OSC_RECEIVE_HOST}:{OSC_RECEIVE_PORT}"
    )

    thread = threading.Thread(
        target=server.serve_forever,
        daemon=True,
    )
    thread.start()

    return server


# ------------------------------------------------------------
# Density-matrix functions
# ------------------------------------------------------------

def state_to_density(psi):
    return np.outer(psi, np.conjugate(psi))


def normalize_density(rho):
    rho = 0.5 * (rho + rho.conj().T)

    trace = np.trace(rho).real

    if trace <= 0:
        raise ValueError("Density matrix trace became non-positive.")

    return rho / trace


def partial_trace_two_qubits(rho, keep=0):
    reshaped = rho.reshape(2, 2, 2, 2)

    if keep == 0:
        return np.einsum("abcb->ac", reshaped)

    if keep == 1:
        return np.einsum("abad->bd", reshaped)

    raise ValueError("keep must be 0 or 1")


def purity(rho):
    return float(np.trace(rho @ rho).real)


def von_neumann_entropy(rho):
    values = np.linalg.eigvalsh(rho).real
    values = np.clip(values, 1e-12, 1.0)

    return float(-np.sum(values * np.log2(values)))


def bloch_vector(single_qubit_rho):
    return (
        float(np.trace(single_qubit_rho @ X).real),
        float(np.trace(single_qubit_rho @ Y).real),
        float(np.trace(single_qubit_rho @ Z).real),
    )


def excitation_probability(single_qubit_rho):
    return float(single_qubit_rho[1, 1].real)


def mutual_information(rho_ab):
    rho_a = partial_trace_two_qubits(rho_ab, keep=0)
    rho_b = partial_trace_two_qubits(rho_ab, keep=1)

    return (
        von_neumann_entropy(rho_a)
        + von_neumann_entropy(rho_b)
        - von_neumann_entropy(rho_ab)
    )


# ------------------------------------------------------------
# Deterministic open-system channels
# ------------------------------------------------------------

def apply_kraus_channel(rho, kraus_ops, qubit):
    result = np.zeros_like(rho, dtype=complex)

    for operator in kraus_ops:
        full_operator = (
            kron(operator, I2)
            if qubit == 0
            else kron(I2, operator)
        )

        result += full_operator @ rho @ full_operator.conj().T

    return normalize_density(result)


def dephasing_channel(rho, amount, qubit):
    amount = clamp(amount)

    retention = 1.0 - amount

    k0 = np.sqrt((1.0 + retention) / 2.0) * I2
    k1 = np.sqrt((1.0 - retention) / 2.0) * Z

    return apply_kraus_channel(rho, [k0, k1], qubit)


def amplitude_damping_channel(rho, gamma, qubit):
    gamma = clamp(gamma)

    k0 = np.array([
        [1, 0],
        [0, np.sqrt(1.0 - gamma)],
    ], dtype=complex)

    k1 = np.array([
        [0, np.sqrt(gamma)],
        [0, 0],
    ], dtype=complex)

    return apply_kraus_channel(rho, [k0, k1], qubit)


def depolarizing_channel(rho, probability, qubit):
    probability = clamp(probability)

    k0 = np.sqrt(1.0 - probability) * I2
    kx = np.sqrt(probability / 3.0) * X
    ky = np.sqrt(probability / 3.0) * Y
    kz = np.sqrt(probability / 3.0) * Z

    return apply_kraus_channel(rho, [k0, kx, ky, kz], qubit)


# ------------------------------------------------------------
# Matrix-only recursive engine
# ------------------------------------------------------------

class MatrixOnlyDensityEngine:
    def __init__(self):
        self.memory = np.zeros(12, dtype=float)
        self.reset_state()

    def reset_state(self):
        # Phase-rich, entangled initial state.
        psi = np.array(
            [0.48, 0.22j, 0.39 - 0.12j, 0.71j],
            dtype=complex,
        )

        psi = psi / np.linalg.norm(psi)
        self.rho = state_to_density(psi)

        self.memory[:] = 0.0

        print("Matrix-only density state reset.")

    def mean_coherence(self, rho):
        pairs = [
            (0, 1),
            (0, 2),
            (0, 3),
            (1, 2),
            (1, 3),
            (2, 3),
        ]

        return float(np.mean([np.abs(rho[i, j]) for i, j in pairs]))

    def matrix_features(self):
        rho_a = partial_trace_two_qubits(self.rho, keep=0)
        rho_b = partial_trace_two_qubits(self.rho, keep=1)

        bx0, by0, bz0 = bloch_vector(rho_a)
        bx1, by1, bz1 = bloch_vector(rho_b)

        c01 = self.rho[0, 1]
        c02 = self.rho[0, 2]
        c03 = self.rho[0, 3]

        return np.array([
            bx0,
            by0,
            bz0,
            bx1,
            by1,
            bz1,
            self.mean_coherence(self.rho),
            mutual_information(self.rho),
            von_neumann_entropy(self.rho) / 2.0,
            np.real(c01),
            np.imag(c02),
            np.angle(c03) / np.pi,
        ], dtype=float)

    def update_memory(self, current_features):
        # Matrix-derived history only. No random input.
        memory_rate = 0.035
        self.memory = (
            (1.0 - memory_rate) * self.memory
            + memory_rate * current_features
        )

    def hamiltonian(self, control_values):
        f = control_values["feedback"]
        c = control_values["coupling"]

        current = self.matrix_features()
        self.update_memory(current)

        bx0, by0, bz0 = current[0:3]
        bx1, by1, bz1 = current[3:6]

        coherence = current[6]
        mutual_info = current[7]
        entropy = current[8]

        c01_real = current[9]
        c02_imag = current[10]
        c03_phase = current[11]

        mbx0, mby0, mbz0 = self.memory[0:3]
        mbx1, mby1, mbz1 = self.memory[3:6]

        memory_coherence = self.memory[6]
        memory_mutual_info = self.memory[7]

        # Each local field is driven by the other qubit,
        # global coherence, and a slow matrix-derived memory.
        x0 = (
            control_values["x0"]
            + f * (
                1.25 * by1
                + 0.80 * mbx1
                + 0.75 * c01_real
            )
        )

        y0 = (
            control_values["y0"]
            + f * (
                -1.10 * bz1
                + 0.85 * mby1
                + 0.70 * c02_imag
            )
        )

        z0 = (
            control_values["z0"]
            + f * (
                1.10 * bx1
                + 0.70 * mbz1
                - 0.90 * entropy
            )
        )

        x1 = (
            control_values["x1"]
            + f * (
                1.25 * by0
                + 0.80 * mbx0
                - 0.75 * c01_real
            )
        )

        y1 = (
            control_values["y1"]
            + f * (
                -1.10 * bz0
                + 0.85 * mby0
                - 0.70 * c02_imag
            )
        )

        z1 = (
            control_values["z1"]
            + f * (
                1.10 * bx0
                + 0.70 * mbz0
                + 0.90 * entropy
            )
        )

        coupling = (
            c
            + f * (
                2.60 * coherence
                + 1.80 * mutual_info
                + 1.20 * memory_coherence
                + 0.80 * memory_mutual_info
                - 1.75 * entropy
            )
        )

        phase_coupling = f * (
            0.80 * c03_phase
            + 0.50 * self.memory[11]
        )

        coupling = np.clip(coupling, -3.0, 3.0)
        phase_coupling = np.clip(phase_coupling, -2.0, 2.0)

        drive = 1.45

        return (
            drive * x0 * XI
            + drive * y0 * YI
            + drive * z0 * ZI
            + drive * x1 * IX
            + drive * y1 * IY
            + drive * z1 * IZ
            + coupling * ZZ
            + 0.32 * coupling * XX
            + 0.24 * coupling * YY
            + phase_coupling * XY
            - phase_coupling * YX
        )

    def unitary_step(self, hamiltonian, dt):
        eigenvalues, eigenvectors = np.linalg.eigh(hamiltonian)

        phase_factors = np.exp(-1j * eigenvalues * dt)

        unitary = (
            eigenvectors
            @ np.diag(phase_factors)
            @ eigenvectors.conj().T
        )

        self.rho = unitary @ self.rho @ unitary.conj().T
        self.rho = normalize_density(self.rho)

    def apply_noise(self, control_values):
        self.rho = dephasing_channel(
            self.rho,
            control_values["dephase"],
            qubit=0,
        )

        self.rho = dephasing_channel(
            self.rho,
            control_values["dephase"] * 0.72,
            qubit=1,
        )

        self.rho = amplitude_damping_channel(
            self.rho,
            control_values["damping"] * 0.45,
            qubit=0,
        )

        self.rho = amplitude_damping_channel(
            self.rho,
            control_values["damping"],
            qubit=1,
        )

        self.rho = depolarizing_channel(
            self.rho,
            control_values["depolarize"],
            qubit=0,
        )

    def step(self, dt):
        if engine_reset_requested.is_set():
            self.reset_state()
            engine_reset_requested.clear()

        control_values = get_controls()

        if control_values["freeze"] >= 0.5:
            return self.rho

        hamiltonian = self.hamiltonian(control_values)

        effective_dt = dt * control_values["speed"] * 3.0
        self.unitary_step(hamiltonian, effective_dt)

        self.apply_noise(control_values)

        return self.rho


# ------------------------------------------------------------
# Output features
# ------------------------------------------------------------

def density_features(rho):
    rho_a = partial_trace_two_qubits(rho, keep=0)
    rho_b = partial_trace_two_qubits(rho, keep=1)

    pairs = [
        (0, 1),
        (0, 2),
        (0, 3),
        (1, 2),
        (1, 3),
        (2, 3),
    ]

    coherences = []
    phase_sin = []
    phase_cos = []

    for i, j in pairs:
        value = rho[i, j]
        phase = np.angle(value)

        coherences.append(float(np.abs(value)))
        phase_sin.append(float(np.sin(phase)))
        phase_cos.append(float(np.cos(phase)))

    return {
        "purity": purity(rho),
        "entropy": von_neumann_entropy(rho),
        "coherence_mean": float(np.mean(coherences)),
        "coherences": coherences,
        "phase_sin": phase_sin,
        "phase_cos": phase_cos,
        "q0_excitation": excitation_probability(rho_a),
        "q1_excitation": excitation_probability(rho_b),
        "q0_bloch": bloch_vector(rho_a),
        "q1_bloch": bloch_vector(rho_b),
        "mutual_information": mutual_information(rho),
    }


# ------------------------------------------------------------
# OSC output to Max
# ------------------------------------------------------------

def send_features(client, features):
    client.send_message("/density/global/purity", features["purity"])
    client.send_message("/density/global/entropy", features["entropy"])
    client.send_message(
        "/density/global/coherence_mean",
        features["coherence_mean"],
    )

    client.send_message(
        "/density/pair/mutual_information",
        features["mutual_information"],
    )

    client.send_message(
        "/density/qubit/0/excitation",
        features["q0_excitation"],
    )

    client.send_message(
        "/density/qubit/1/excitation",
        features["q1_excitation"],
    )

    client.send_message(
        "/density/qubit/0/bloch",
        list(features["q0_bloch"]),
    )

    client.send_message(
        "/density/qubit/1/bloch",
        list(features["q1_bloch"]),
    )

    client.send_message(
        "/density/pair/coherence",
        features["coherences"],
    )

    client.send_message(
        "/density/pair/phase_sin",
        features["phase_sin"],
    )

    client.send_message(
        "/density/pair/phase_cos",
        features["phase_cos"],
    )


# ------------------------------------------------------------
# Main
# ------------------------------------------------------------

def main():
    client = SimpleUDPClient(OSC_SEND_HOST, OSC_SEND_PORT)
    server = start_osc_control_server()

    engine = MatrixOnlyDensityEngine()

    print("Matrix-only density engine running.")
    print(f"Sending density data to {OSC_SEND_HOST}:{OSC_SEND_PORT}")

    try:
        while True:
            rho = engine.step(DT)
            features = density_features(rho)
            send_features(client, features)

            time.sleep(DT)

    except KeyboardInterrupt:
        print("\nStopped.")

    finally:
        server.shutdown()
        server.server_close()


if __name__ == "__main__":
    main()