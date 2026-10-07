"""
4-qubit transition-spectrum quantum IR engine with OSC control.

Install:
    conda activate music
    pip install numpy scipy soundfile python-osc

Run:
    python quantum_ir_transition_osc.py
    python quantum_ir_transition_osc.py --input your_sound.wav
    python quantum_ir_transition_osc.py --write_ir

Max send examples:
    /quantum_ir/render
    /quantum_ir/base_freq 55
    /quantum_ir/t2 3.0
    /quantum_ir/temperature inf
    /quantum_ir/coupling_dm 0.35
    /quantum_ir/coupling_xx 0.4
    /quantum_ir/coupling_zz 0.2
    /quantum_ir/ir_seconds 5.0
"""

import argparse
import threading
import time
from math import gcd

import numpy as np
import soundfile as sf
from scipy.signal import fftconvolve, resample_poly

from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import ThreadingOSCUDPServer
from pythonosc.udp_client import SimpleUDPClient


# ----------------------------
# GLOBAL PARAMETERS
# ----------------------------

PARAMS = {
    "sr": 48000,
    "ir_seconds": 4.0,
    "base_freq": 55.0,

    # Hamiltonian controls
    "field_z0": 1.00,
    "field_z1": 1.17,
    "field_z2": 1.37,
    "field_z3": 1.61,
    "coupling_xx": 0.35,
    "coupling_zz": 0.18,
    "coupling_dm": 0.30,

    # Transition / response controls
    "temperature": "inf",   # "none", "inf", or number
    "t2": 3.0,
    "t2_freq_scaling": 0.35,
    "min_intensity": 1e-8,
    "max_lines": 64,

    # OSC
    "osc_in_port": 7410,
    "osc_out_port": 7400,
    "osc_host": "127.0.0.1",
}

PARAM_LOCK = threading.Lock()


# ----------------------------
# BASIC UTILITIES
# ----------------------------

def normalize(x):
    peak = np.max(np.abs(x))
    if peak < 1e-12:
        return x
    return x / peak


def soft_fade_in(ir, samples=256):
    fade_len = min(samples, len(ir))
    ir[:fade_len] *= np.linspace(0.0, 1.0, fade_len)
    return ir


def resample_ir_if_needed(ir, ir_sr, target_sr):
    if ir_sr == target_sr:
        return ir

    factor = gcd(ir_sr, target_sr)
    up = target_sr // factor
    down = ir_sr // factor
    return resample_poly(ir, up, down)


# ----------------------------
# PAULI / HAMILTONIAN
# ----------------------------

def pauli_matrices():
    I = np.array([[1, 0], [0, 1]], dtype=complex)
    X = np.array([[0, 1], [1, 0]], dtype=complex)
    Y = np.array([[0, -1j], [1j, 0]], dtype=complex)
    Z = np.array([[1, 0], [0, -1]], dtype=complex)
    return {"I": I, "X": X, "Y": Y, "Z": Z}


def pauli_string(label):
    mats = pauli_matrices()
    out = mats[label[0]]
    for ch in label[1:]:
        out = np.kron(out, mats[ch])
    return out


def make_four_qubit_hamiltonian(params):
    """
    Four-qubit complex-Hermitian Hamiltonian.

    Includes:
        local Z fields
        nearest-neighbor XX coupling
        nearest-neighbor ZZ coupling
        Dzyaloshinskii-Moriya-like term: XY - YX
    """
    H = np.zeros((16, 16), dtype=complex)

    fields = [
        params["field_z0"],
        params["field_z1"],
        params["field_z2"],
        params["field_z3"],
    ]

    coupling_xx = params["coupling_xx"]
    coupling_zz = params["coupling_zz"]
    coupling_dm = params["coupling_dm"]

    # Local Z fields
    for q, strength in enumerate(fields):
        label = ["I"] * 4
        label[q] = "Z"
        H += strength * pauli_string("".join(label))

    # Neighbor couplings
    for q in range(3):
        xx = ["I"] * 4
        xx[q] = "X"
        xx[q + 1] = "X"
        H += coupling_xx * pauli_string("".join(xx))

        zz = ["I"] * 4
        zz[q] = "Z"
        zz[q + 1] = "Z"
        H += coupling_zz * pauli_string("".join(zz))

        xy = ["I"] * 4
        xy[q] = "X"
        xy[q + 1] = "Y"

        yx = ["I"] * 4
        yx[q] = "Y"
        yx[q + 1] = "X"

        H += coupling_dm * (
            pauli_string("".join(xy)) - pauli_string("".join(yx))
        )

    return H


def make_dipole_operator():
    """
    Dipole/readout operator A.

    This determines which transitions are bright or dark.
    """
    A = np.zeros((16, 16), dtype=complex)

    for q in range(4):
        label = ["I"] * 4
        label[q] = "X"
        A += pauli_string("".join(label))

    return A


# ----------------------------
# TRANSITION SPECTRUM
# ----------------------------

def parse_temperature(value):
    if value is None:
        return None

    if isinstance(value, str):
        v = value.lower()
        if v in ["none", "ground", "0"]:
            return None
        if v in ["inf", "infinity", "infinite"]:
            return np.inf
        return float(value)

    return float(value)


def thermal_populations(energies, temperature):
    """
    None = ground state only.
    inf = equal populations.
    finite = Boltzmann distribution.
    """
    n = len(energies)

    if temperature is None:
        p = np.zeros(n)
        p[0] = 1.0
        return p

    if np.isinf(temperature):
        return np.ones(n) / n

    shifted = energies - np.min(energies)
    beta = 1.0 / max(temperature, 1e-9)
    weights = np.exp(-beta * shifted)
    return weights / np.sum(weights)


def transition_spectrum(params):
    """
    Returns physically allowed transition lines.

    Frequencies are Bohr differences:
        omega_mn = E_m - E_n

    Intensities are:
        population_n * |A_mn|^2
    """
    H = make_four_qubit_hamiltonian(params)
    A = make_dipole_operator()

    # Check Hermiticity
    herm_error = np.max(np.abs(H - H.conj().T))
    if herm_error > 1e-9:
        raise ValueError(f"Hamiltonian is not Hermitian. Error: {herm_error}")

    energies, vecs = np.linalg.eigh(H)

    # Transform dipole operator into energy basis
    A_energy = vecs.conj().T @ A @ vecs

    temperature = parse_temperature(params["temperature"])
    pops = thermal_populations(energies, temperature)

    lines = []
    min_intensity = params["min_intensity"]

    for n in range(len(energies)):
        for m in range(len(energies)):
            if m <= n:
                continue

            delta_e = float(np.real(energies[m] - energies[n]))
            matrix_element = A_energy[n, m]
            intensity = pops[n] * abs(matrix_element) ** 2

            if intensity > min_intensity:
                lines.append({
                    "n": n,
                    "m": m,
                    "delta_e": delta_e,
                    "ratio": None,
                    "intensity": float(np.real(intensity)),
                    "phase": float(np.angle(matrix_element)),
                    "matrix_abs": float(abs(matrix_element)),
                    "population": float(pops[n]),
                })

    lines.sort(key=lambda x: x["delta_e"])

    if lines:
        fundamental = lines[0]["delta_e"]
        for line in lines:
            line["ratio"] = line["delta_e"] / fundamental

    max_lines = int(params["max_lines"])
    return lines[:max_lines], energies


# ----------------------------
# IR SYNTHESIS FROM C(t)
# ----------------------------

def make_transition_ir(params):
    """
    Creates real quantum-correlation-inspired impulse response:

        C(t) = Re sum_nm I_nm exp(i omega_nm t + i phase_nm) exp(-t / T2_nm)

    Then maps dimensionless Bohr frequencies to audio frequencies:
        f_nm = base_freq * ratio_nm
    """
    sr = int(params["sr"])
    ir_seconds = float(params["ir_seconds"])
    base_freq = float(params["base_freq"])
    t2 = float(params["t2"])
    t2_freq_scaling = float(params["t2_freq_scaling"])

    t = np.linspace(0, ir_seconds, int(sr * ir_seconds), endpoint=False)

    lines, energies = transition_spectrum(params)

    ir = np.zeros_like(t)

    for line in lines:
        ratio = line["ratio"]
        freq = base_freq * ratio

        intensity = line["intensity"]
        amp = np.sqrt(intensity)

        phase = line["phase"]

        # Higher transitions can dephase faster.
        effective_t2 = t2 / (1.0 + t2_freq_scaling * (ratio - 1.0))
        effective_t2 = max(effective_t2, 1e-4)

        env = np.exp(-t / effective_t2)

        ir += amp * env * np.cos(2.0 * np.pi * freq * t + phase)

    ir = soft_fade_in(ir)
    ir = normalize(ir)

    return ir, lines, energies


# ----------------------------
# AUDIO RENDERING
# ----------------------------

def convolve_audio(input_path, ir, ir_sr, output_path, wet=0.7):
    dry, audio_sr = sf.read(input_path)

    ir = resample_ir_if_needed(ir, ir_sr, audio_sr)

    if dry.ndim > 1:
        dry_mono = np.mean(dry, axis=1)
    else:
        dry_mono = dry

    wet_signal = fftconvolve(dry_mono, ir, mode="full")
    wet_signal = wet_signal[:len(dry_mono)]

    out = (1.0 - wet) * dry_mono + wet * wet_signal
    out = normalize(out)

    sf.write(output_path, out, audio_sr)
    return output_path


# ----------------------------
# OSC COMMUNICATION
# ----------------------------

def send_ir_to_max(client, ir, address="/quantum_ir/buffer"):
    chunk_size = 64

    client.send_message("/quantum_ir/clear", 1)

    for start in range(0, len(ir), chunk_size):
        chunk = ir[start:start + chunk_size].tolist()
        client.send_message(address, [start] + chunk)

    client.send_message("/quantum_ir/done", len(ir))


def send_spectrum_to_max(client, lines):
    client.send_message("/quantum_ir/spectrum/clear", 1)

    for i, line in enumerate(lines):
        client.send_message(
            "/quantum_ir/spectrum/line",
            [
                i,
                int(line["n"]),
                int(line["m"]),
                float(line["ratio"]),
                float(line["intensity"]),
                float(line["phase"]),
                float(line["matrix_abs"]),
                float(line["population"]),
            ],
        )

    client.send_message("/quantum_ir/spectrum/done", len(lines))


def print_spectrum(lines):
    print("\nTransition spectrum:")
    print("idx | n->m | ratio | intensity | phase | |A_nm| | pop")
    print("-" * 68)

    for i, line in enumerate(lines):
        print(
            f"{i:02d}  | "
            f"{line['n']:02d}->{line['m']:02d} | "
            f"{line['ratio']:6.3f} | "
            f"{line['intensity']:.6f} | "
            f"{line['phase']:+.3f} | "
            f"{line['matrix_abs']:.6f} | "
            f"{line['population']:.4f}"
        )

    print()


def render_and_send(client=None, write_ir=False, input_path=None):
    with PARAM_LOCK:
        params = dict(PARAMS)

    ir, lines, energies = make_transition_ir(params)

    print_spectrum(lines)

    if write_ir:
        sf.write("q_transition_ir.wav", ir, int(params["sr"]))
        print("Wrote q_transition_ir.wav")

    if input_path:
        convolve_audio(
            input_path,
            ir,
            int(params["sr"]),
            "wet_transition_ir.wav",
            wet=0.7,
        )
        print("Wrote wet_transition_ir.wav")

    if client is not None:
        send_ir_to_max(client, ir)
        send_spectrum_to_max(client, lines)
        client.send_message("/quantum_ir/status", "rendered")

    return ir, lines


def set_param(name, value):
    with PARAM_LOCK:
        if name not in PARAMS:
            print(f"Unknown parameter: {name}")
            return

        current = PARAMS[name]

        if isinstance(current, str):
            PARAMS[name] = str(value)
        elif isinstance(current, int):
            PARAMS[name] = int(value)
        else:
            PARAMS[name] = float(value)

        print(f"{name} = {PARAMS[name]}")


def make_param_handler(param_name, client, write_ir, input_path):
    def handler(address, *args):
        if not args:
            return

        set_param(param_name, args[0])

        # Auto-render after each param change
        render_and_send(
            client=client,
            write_ir=write_ir,
            input_path=input_path,
        )

    return handler


def start_osc_server(client, write_ir=False, input_path=None):
    dispatcher = Dispatcher()

    # Render manually
    dispatcher.map(
        "/quantum_ir/render",
        lambda address, *args: render_and_send(
            client=client,
            write_ir=write_ir,
            input_path=input_path,
        ),
    )

    # Parameter controls
    controllable = [
        "ir_seconds",
        "base_freq",
        "field_z0",
        "field_z1",
        "field_z2",
        "field_z3",
        "coupling_xx",
        "coupling_zz",
        "coupling_dm",
        "temperature",
        "t2",
        "t2_freq_scaling",
        "min_intensity",
        "max_lines",
    ]

    for name in controllable:
        dispatcher.map(
            f"/quantum_ir/{name}",
            make_param_handler(name, client, write_ir, input_path),
        )

    server = ThreadingOSCUDPServer(
        ("0.0.0.0", int(PARAMS["osc_in_port"])),
        dispatcher,
    )

    print(f"Listening for OSC on port {PARAMS['osc_in_port']}")
    print(f"Sending OSC to {PARAMS['osc_host']}:{PARAMS['osc_out_port']}")
    server.serve_forever()


# ----------------------------
# MAIN
# ----------------------------

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--input", type=str, default=None)
    parser.add_argument("--write_ir", action="store_true")
    parser.add_argument("--no_osc", action="store_true")

    parser.add_argument("--sr", type=int, default=48000)
    parser.add_argument("--osc_in_port", type=int, default=7410)
    parser.add_argument("--osc_out_port", type=int, default=7400)
    parser.add_argument("--osc_host", type=str, default="127.0.0.1")

    args = parser.parse_args()

    PARAMS["sr"] = args.sr
    PARAMS["osc_in_port"] = args.osc_in_port
    PARAMS["osc_out_port"] = args.osc_out_port
    PARAMS["osc_host"] = args.osc_host

    client = SimpleUDPClient(args.osc_host, args.osc_out_port)

    # Initial render
    render_and_send(
        client=None if args.no_osc else client,
        write_ir=args.write_ir,
        input_path=args.input,
    )

    if args.no_osc:
        return

    start_osc_server(
        client=client,
        write_ir=args.write_ir,
        input_path=args.input,
    )


if __name__ == "__main__":
    main()
