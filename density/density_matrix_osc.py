# density_matrix_osc.py
#
# Sends density-matrix features to Max on port 7400.
# Receives live noise controls from Max on port 7401.
#
# Max -> Python controls:
# /noise/dephase      0.0 to 1.0
# /noise/damping      0.0 to 1.0
# /noise/depolarize   0.0 to 1.0
#
# Optional:
# /noise/reset
#
# Python -> Max feature output:
# /density/global/purity
# /density/global/entropy
# /density/global/coherence_mean
# /density/pair/mutual_information
# /density/qubit/0/excitation
# /density/qubit/1/excitation
# /density/qubit/0/bloch
# /density/qubit/1/bloch
# /density/pair/coherence
# /density/pair/phase

import time
import threading
import numpy as np
import socket

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

UPDATE_RATE_HZ = 20.0


# ------------------------------------------------------------
# OSC control input from Max
# ------------------------------------------------------------

noise_controls = {
    "dephase": 0.20,
    "damping": 0.05,
    "depolarize": 0.02,
}

controls_lock = threading.Lock()


def clamp(value, low=0.0, high=1.0):
    return max(low, min(high, float(value)))


def set_noise_parameter(address, parameter, value):
    parameter = str(parameter).lstrip("/").lower()
    value = clamp(value)

    with controls_lock:
        if parameter == "dephase":
            noise_controls["dephase"] = value

        elif parameter == "damping":
            noise_controls["damping"] = value

        elif parameter == "depolarize":
            noise_controls["depolarize"] = value

        else:
            print("Unknown noise parameter:", parameter)
            return

    print(f"{parameter}: {value:.3f}")


def reset_noise(address, *args):
    with controls_lock:
        noise_controls["dephase"] = 0.20
        noise_controls["damping"] = 0.05
        noise_controls["depolarize"] = 0.02

    print("noise controls reset")


def get_noise_controls():
    with controls_lock:
        return dict(noise_controls)


def start_osc_control_server():
    dispatcher = Dispatcher()

    # Max sends: /noise "/damping" 0.12
    dispatcher.map("/noise", set_noise_parameter)
    dispatcher.map("/noise/reset", reset_noise)

    server = ThreadingOSCUDPServer(
        (OSC_RECEIVE_HOST, OSC_RECEIVE_PORT),
        dispatcher,
    )

    print(
        f"Listening for Max noise controls on "
        f"{OSC_RECEIVE_HOST}:{OSC_RECEIVE_PORT}"
    )

    thread = threading.Thread(
        target=server.serve_forever,
        daemon=True,
    )
    thread.start()

    return server


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

H = (1 / np.sqrt(2)) * np.array([
    [1, 1],
    [1, -1],
], dtype=complex)

CNOT = np.array([
    [1, 0, 0, 0],
    [0, 1, 0, 0],
    [0, 0, 0, 1],
    [0, 0, 1, 0],
], dtype=complex)


def kron(a, b):
    return np.kron(a, b)


def ry(theta):
    return np.array([
        [np.cos(theta / 2), -np.sin(theta / 2)],
        [np.sin(theta / 2), np.cos(theta / 2)],
    ], dtype=complex)


def rz(phi):
    return np.array([
        [np.exp(-1j * phi / 2), 0],
        [0, np.exp(1j * phi / 2)],
    ], dtype=complex)


# ------------------------------------------------------------
# Density-matrix functions
# ------------------------------------------------------------

def state_to_density(psi):
    return np.outer(psi, np.conjugate(psi))


def apply_unitary(rho, unitary):
    return unitary @ rho @ unitary.conj().T


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


def von_neumann_entropy(rho):
    eigenvalues = np.linalg.eigvalsh(rho).real
    eigenvalues = np.clip(eigenvalues, 1e-12, 1.0)

    return float(-np.sum(eigenvalues * np.log2(eigenvalues)))


def purity(rho):
    return float(np.trace(rho @ rho).real)


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
# Quantum noise channels
# ------------------------------------------------------------

def apply_kraus_channel(rho, kraus_ops, qubit):
    result = np.zeros_like(rho, dtype=complex)

    for k in kraus_ops:
        if qubit == 0:
            full_k = kron(k, I2)
        elif qubit == 1:
            full_k = kron(I2, k)
        else:
            raise ValueError("qubit must be 0 or 1")

        result += full_k @ rho @ full_k.conj().T

    return normalize_density(result)


def dephasing_channel(rho, strength, qubit=0):
    strength = np.clip(strength, 0.0, 1.0)

    k0 = np.sqrt(1.0 - strength) * I2
    k1 = np.sqrt(strength) * Z

    return apply_kraus_channel(rho, [k0, k1], qubit)


def amplitude_damping_channel(rho, gamma, qubit=0):
    gamma = np.clip(gamma, 0.0, 1.0)

    k0 = np.array([
        [1, 0],
        [0, np.sqrt(1.0 - gamma)],
    ], dtype=complex)

    k1 = np.array([
        [0, np.sqrt(gamma)],
        [0, 0],
    ], dtype=complex)

    return apply_kraus_channel(rho, [k0, k1], qubit)


def depolarizing_channel(rho, probability, qubit=0):
    probability = np.clip(probability, 0.0, 1.0)

    k0 = np.sqrt(1.0 - probability) * I2
    kx = np.sqrt(probability / 3.0) * X
    ky = np.sqrt(probability / 3.0) * Y
    kz = np.sqrt(probability / 3.0) * Z

    return apply_kraus_channel(rho, [k0, kx, ky, kz], qubit)


# ------------------------------------------------------------
# Feature extraction
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
    phases = []

    for i, j in coherence_pairs:
        value = rho[i, j]
        coherences.append(float(np.abs(value)))
        phases.append(float(np.angle(value)))

    return {
        "purity": purity(rho),
        "entropy": von_neumann_entropy(rho),
        "coherence_mean": float(np.mean(coherences)),
        "coherences": coherences,
        "phases": phases,
        "q0_excitation": excitation_probability(rho_a),
        "q1_excitation": excitation_probability(rho_b),
        "q0_bloch": bloch_vector(rho_a),
        "q1_bloch": bloch_vector(rho_b),
        "mutual_information": mutual_information(rho),
    }


# ------------------------------------------------------------
# Evolving two-qubit state
# ------------------------------------------------------------

def make_entangled_state(time_seconds):
    theta_a = 0.7 * np.sin(time_seconds * 0.31)
    theta_b = 0.9 * np.sin(time_seconds * 0.17 + 1.2)

    phi_a = time_seconds * 0.29
    phi_b = time_seconds * 0.43

    psi_00 = np.array([1, 0, 0, 0], dtype=complex)
    rho = state_to_density(psi_00)

    u0 = kron(H @ ry(theta_a) @ rz(phi_a), I2)
    u1 = kron(I2, ry(theta_b) @ rz(phi_b))

    rho = apply_unitary(rho, u0)
    rho = apply_unitary(rho, u1)
    rho = apply_unitary(rho, CNOT)

    return rho


def apply_live_noise(rho):
    controls = get_noise_controls()

    dephase = controls["dephase"]
    damping = controls["damping"]
    depolarize = controls["depolarize"]

    rho = dephasing_channel(rho, dephase, qubit=0)
    rho = dephasing_channel(rho, dephase * 0.7, qubit=1)

    rho = amplitude_damping_channel(rho, damping, qubit=1)

    rho = depolarizing_channel(rho, depolarize, qubit=0)

    return rho


# ------------------------------------------------------------
# Send density features to Max
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
        "/density/pair/phase",
        features["phases"],
    )


# ------------------------------------------------------------
# Main
# ------------------------------------------------------------

def main():
    client = SimpleUDPClient(OSC_SEND_HOST, OSC_SEND_PORT)
    server = start_osc_control_server()
    

    print("Density-matrix OSC engine running.")
    print(f"Sending density data to {OSC_SEND_HOST}:{OSC_SEND_PORT}")

    start_time = time.time()
    interval = 1.0 / UPDATE_RATE_HZ

    try:
        while True:
            now = time.time() - start_time

            rho = make_entangled_state(now)
            rho = apply_live_noise(rho)

            features = density_features(rho)
            send_features(client, features)

            time.sleep(interval)

    except KeyboardInterrupt:
        print("\nStopped.")

    finally:
        server.shutdown()
        server.server_close()


if __name__ == "__main__":
    main()