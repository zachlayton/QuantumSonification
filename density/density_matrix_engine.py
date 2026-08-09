# density_matrix_osc_v2.py
#
# Density Matrix OSC Engine v2.0
#
# Python -> Max: port 7400
# Max -> Python: port 7401
#
# Max control protocol:
#
# [flonum]
# |
# [prepend /damping]
# |
# [prepend /noise]
# |
# [OSC-send 127.0.0.1 7401]
#
# Noise parameters:
# /noise /dephase      0.0 - 1.0
# /noise /damping      0.0 - 1.0
# /noise /depolarize   0.0 - 1.0
#
# Field / Hamiltonian parameters:
# /field /x0           -1.0 - 1.0
# /field /y0           -1.0 - 1.0
# /field /z0           -1.0 - 1.0
# /field /x1           -1.0 - 1.0
# /field /y1           -1.0 - 1.0
# /field /z1           -1.0 - 1.0
# /field /coupling      0.0 - 2.0
# /field /drift         0.0 - 1.0
# /field /feedback      0.0 - 1.0
#
# Engine commands:
# /engine /reset
# /engine /freeze       0 or 1


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

ZZ = kron(Z, Z)
XX = kron(X, X)
YY = kron(Y, Y)


# ------------------------------------------------------------
# Shared control state
# ------------------------------------------------------------

controls = {
    "dephase": 0.05,
    "damping": 0.02,
    "depolarize": 0.01,

    "x0": 0.35,
    "y0": 0.10,
    "z0": 0.20,

    "x1": 0.20,
    "y1": -0.15,
    "z1": 0.30,

    "coupling": 0.70,
    "drift": 0.25,
    "feedback": 0.35,

    "freeze": 0.0,
}

controls_lock = threading.Lock()
engine_reset_requested = threading.Event()


def clamp(value, low=0.0, high=1.0):
    return max(low, min(high, float(value)))


def clamp_bipolar(value):
    return max(-1.0, min(1.0, float(value)))


def reset_controls():
    with controls_lock:
        controls["dephase"] = 0.05
        controls["damping"] = 0.02
        controls["depolarize"] = 0.01

        controls["x0"] = 0.35
        controls["y0"] = 0.10
        controls["z0"] = 0.20

        controls["x1"] = 0.20
        controls["y1"] = -0.15
        controls["z1"] = 0.30

        controls["coupling"] = 0.70
        controls["drift"] = 0.25
        controls["feedback"] = 0.35
        controls["freeze"] = 0.0


def get_controls():
    with controls_lock:
        return dict(controls)


# ------------------------------------------------------------
# OSC input handlers
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

    bipolar_parameters = {"x0", "y0", "z0", "x1", "y1", "z1"}

    with controls_lock:
        if parameter in bipolar_parameters:
            controls[parameter] = clamp_bipolar(value)

        elif parameter == "coupling":
            controls[parameter] = clamp(value, 0.0, 2.0)

        elif parameter in ("drift", "feedback"):
            controls[parameter] = clamp(value)

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

    # Max sends:
    # /noise "/damping" 0.2
    # /field "/coupling" 0.8
    # /engine "/reset"
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
# Density matrix functions
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
    eigenvalues = np.linalg.eigvalsh(rho).real
    eigenvalues = np.clip(eigenvalues, 1e-12, 1.0)

    return float(-np.sum(eigenvalues * np.log2(eigenvalues)))


def bloch_vector(single_qubit_rho):
    x = float(np.trace(single_qubit_rho @ X).real)
    y = float(np.trace(single_qubit_rho @ Y).real)
    z = float(np.trace(single_qubit_rho @ Z).real)

    return x, y, z


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
# Quantum channels
# ------------------------------------------------------------

def apply_kraus_channel(rho, kraus_ops, qubit):
    result = np.zeros_like(rho, dtype=complex)

    for k in kraus_ops:
        if qubit == 0:
            full_k = kron(k, I2)
        else:
            full_k = kron(I2, k)

        result += full_k @ rho @ full_k.conj().T

    return normalize_density(result)


def dephasing_channel(rho, amount, qubit):
    """
    amount = 0.0: no dephasing
    amount = 1.0: complete loss of local phase coherence
    """
    amount = clamp(amount)

    coherence_retention = 1.0 - amount

    k0 = np.sqrt((1.0 + coherence_retention) / 2.0) * I2
    k1 = np.sqrt((1.0 - coherence_retention) / 2.0) * Z

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
# Recursive Hamiltonian engine
# ------------------------------------------------------------

class DensityMatrixEngine:
    def __init__(self):
       
       self.params = {
    # Noise channels
    "dephase": 0.05,
    "damping": 0.02,
    "depolarize": 0.01,

    # Local base fields
    "x0": 0.35,
    "y0": 0.10,
    "z0": 0.20,

    "x1": 0.20,
    "y1": -0.15,
    "z1": 0.30,

    "x2": -0.10,
    "y2": 0.25,
    "z2": 0.15,

    "x3": 0.15,
    "y3": -0.20,
    "z3": 0.25,

    # Global dynamical controls
    "coupling": 0.70,
    "drift": 0.25,
    "feedback": 0.35,
    "freeze": 0.0,

    # Hamiltonian response gains
    "drive": 1.35,

    "fb_x_neighbor_diff": 0.70,
    "fb_x_coherence": 0.25,

    "fb_y_neighbor_sum": 0.60,
    "fb_y_entropy": 0.25,

    "fb_z_neighbor_diff": 0.55,
    "fb_z_purity": 0.20,

    # Pair topology
    "pair_coherence_gain": 0.55,
    "pair_entropy_gain": 0.30,
    "pair_xx_ratio": 0.28,
    "pair_yy_ratio": 0.18,
    "diagonal_pair_ratio": 0.45,
}

       self.rng = np.random.default_rng()

       self.drift_state = {
                "x0": 0.0,
                "y0": 0.0,
                "z0": 0.0,
                "x1": 0.0,
                "y1": 0.0,
                "z1": 0.0,
                "coupling": 0.0,
            }

       self.reset_state()

    def reset_state(self):
        psi = np.array(
            [0.55, 0.25j, 0.35, 0.70j],
            dtype=complex,
        )

        psi = psi / np.linalg.norm(psi)
        self.rho = state_to_density(psi)

        for key in self.drift_state:
            self.drift_state[key] = 0.0

        print("Density matrix reset to active entangled state.")

    def update_drift(self, drift_amount):
        decay = 0.985
        innovation = 0.08 * drift_amount

        for key in self.drift_state:
            noise = self.rng.normal(0.0, innovation)

            self.drift_state[key] = (
                decay * self.drift_state[key] + noise
            )

            self.drift_state[key] = np.clip(
                self.drift_state[key],
                -1.0,
                1.0,
            )

    def set_param(self, name: str, value: float):
        if name not in self.params:
            raise KeyError(f"Unknown density parameter: {name}")
        self.params[name] = float(value)

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

    def hamiltonian(self, control_values):
        feedback = control_values["feedback"]

        current_entropy = von_neumann_entropy(self.rho) / 2.0
        current_coherence = self.mean_coherence(self.rho) * 4.0
        current_mutual_info = mutual_information(self.rho) / 2.0

        rho_a = partial_trace_two_qubits(self.rho, keep=0)
        rho_b = partial_trace_two_qubits(self.rho, keep=1)

        bx0, by0, bz0 = bloch_vector(rho_a)
        bx1, by1, bz1 = bloch_vector(rho_b)

        x0 = (
            control_values["x0"]
            + self.drift_state["x0"]
            + feedback * 1.8 * by1
            + feedback * 0.9 * current_coherence
        )

        y0 = (
            control_values["y0"]
            + self.drift_state["y0"]
            - feedback * 1.8 * bz1
            + feedback * 0.7 * current_mutual_info
        )

        z0 = (
            control_values["z0"]
            + self.drift_state["z0"]
            + feedback * 1.5 * bx1
            - feedback * 1.2 * current_entropy
        )

        x1 = (
            control_values["x1"]
            + self.drift_state["x1"]
            + feedback * 1.8 * by0
            - feedback * 0.9 * current_coherence
        )

        y1 = (
            control_values["y1"]
            + self.drift_state["y1"]
            - feedback * 1.8 * bz0
            - feedback * 0.7 * current_mutual_info
        )

        z1 = (
            control_values["z1"]
            + self.drift_state["z1"]
            + feedback * 1.5 * bx0
            + feedback * 1.2 * current_entropy
        )

        coupling = (
            control_values["coupling"]
            + 0.45 * self.drift_state["coupling"]
            + feedback * 2.5 * current_coherence
            + feedback * 1.8 * current_mutual_info
            - feedback * 1.5 * current_entropy
        )

        coupling = np.clip(coupling, -3.0, 3.0)

        drive = 1.7

        return (
            drive * x0 * XI
            + drive * y0 * YI
            + drive * z0 * ZI
            + drive * x1 * IX
            + drive * y1 * IY
            + drive * z1 * IZ
            + coupling * ZZ
            + 0.35 * coupling * XX
            + 0.25 * coupling * YY
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
        dephase = control_values["dephase"]
        damping = control_values["damping"]
        depolarize = control_values["depolarize"]

        self.rho = dephasing_channel(
            self.rho,
            dephase,
            qubit=0,
        )

        self.rho = dephasing_channel(
            self.rho,
            dephase * 0.75,
            qubit=1,
        )

        self.rho = amplitude_damping_channel(
            self.rho,
            damping * 0.45,
            qubit=0,
        )

        self.rho = amplitude_damping_channel(
            self.rho,
            damping,
            qubit=1,
        )

        self.rho = depolarizing_channel(
            self.rho,
            depolarize,
            qubit=0,
        )

    def step(self, dt):
       

        control_values = get_controls()
        engine_reset_requested = threading.Event()

        if control_values["freeze"] >= 0.5:
            return self.rho

        self.update_drift(control_values["drift"])

        hamiltonian = self.hamiltonian(control_values)

        self.unitary_step(hamiltonian, dt * 4.0)

        self.apply_noise(control_values)

        return self.rho

# ------------------------------------------------------------
# Sonification feature extraction
# ------------------------------------------------------------

def density_features(rho):
    rho_a = partial_trace_two_qubits(rho, keep=0)
    rho_b = partial_trace_two_qubits(rho, keep=1)

    coherence_pairs = [
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

    for i, j in coherence_pairs:
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

    engine = DensityMatrixEngine()

    print("Density Matrix OSC Engine v2.0 running.")
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
