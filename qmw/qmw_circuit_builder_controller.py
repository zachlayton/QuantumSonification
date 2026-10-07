#!/usr/bin/env python3
"""
Interactive Circuit Builder — standalone prototype for Quantum Material Workbench.

A 3-qubit / 12-step editable circuit grid.  Gate edits change the simulated
state trajectory immediately, and playback emits Bloch vectors, local entropy,
and basis-state probabilities over OSC for Max/QMW.

Dependencies:
    pip install numpy python-osc

Run:
    python interactive_circuit_builder.py

In Max, receive at UDP port 9001, for example:
    [udpreceive 9001]
"""

from __future__ import annotations

import math
import tkinter as tk
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

from qasm_circuit_bridge_v1 import (
    ComposerCircuit,
    DEFAULT_REGISTER_PROCESSES,
    QMW_REGISTER_BUSES,
    default_measurement_osc_route,
    normalize_register_bus_name,
)
from qasm_gate_registry_v1 import (
    gate_menu_items,
    get_gate,
    parse_pi_param,
    validate_gate_call,
)

try:
    from pythonosc.udp_client import SimpleUDPClient
except ImportError:
    SimpleUDPClient = None


# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------
N_QUBITS = 4
N_STEPS = 16
OSC_HOST = "127.0.0.1"
OSC_PORT = 7400
CONTROL_PORT = 7403
WAVETABLE_SAMPLE_INDEX: List[int] = list(range(256))
WAVETABLE_SAMPLE_PHASE: List[float] = [
    index / 256.0
    for index in WAVETABLE_SAMPLE_INDEX
]
WAVETABLE_TABLES_PER_AXIS = 1
WAVETABLE_TABLE_SIZE = 256
WAVETABLE_TABLE_COUNT = WAVETABLE_TABLES_PER_AXIS ** 3
WAVETABLE_BANK_SIZE = WAVETABLE_TABLE_COUNT * WAVETABLE_TABLE_SIZE

# Internal symbols are retained in the grid, while the GUI exposes clear CNOT labels.
GATE_LABELS: Tuple[str, ...] = ("I", "H", "X", "Y", "Z", "S", "T", "•", "⊕")
PALETTE_GATES: Tuple[Tuple[str, str], ...] = (
    ("I", "I"), ("H", "H"), ("X", "X"), ("Y", "Y"), ("Z", "Z"),
    ("S", "S"), ("T", "T"), ("CNOT control", "•"), ("CNOT target", "⊕"),
)
MEASUREMENT_MACROS: Tuple[str, ...] = ("MZ", "MX", "MY", "MN")
DEFAULT_MEASUREMENT_PARAMS: Dict[str, Tuple[str, ...]] = {
    "MZ": (),
    "MX": (),
    "MY": (),
    "MN": ("pi/3", "pi/4"),
}
QUANTUM_DATA_OPERATORS: Tuple[str, ...] = (
    "slice_bits",
    "slice_shots",
    "post_select",
    "merge_registers",
    "expectation_values",
)
REGISTRY_MENU_ITEMS = gate_menu_items(only_qasm_exportable=True)
REGISTRY_MENU_BY_NAME = {
    str(item["name"]): item
    for item in REGISTRY_MENU_ITEMS
}
REGISTRY_GATE_OPTIONS: Tuple[str, ...] = tuple(
    item["name"]
    for item in REGISTRY_MENU_ITEMS
    if item["category"] != "measurement_macro"
)
GATE_COLORS: Dict[str, Tuple[str, str]] = {
    "H": ("#ff832b", "#161616"),
    "SX": ("#ee5396", "#161616"),
    "SXDG": ("#ee5396", "#161616"),
    "Y": ("#ee5396", "#161616"),
    "CY": ("#ee5396", "#161616"),
    "RX": ("#ee5396", "#161616"),
    "RY": ("#ee5396", "#161616"),
    "CRX": ("#ee5396", "#161616"),
    "CRY": ("#ee5396", "#161616"),
    "RXX": ("#ee5396", "#161616"),
    "U": ("#ee5396", "#161616"),
    "U1": ("#ee5396", "#161616"),
    "U2": ("#ee5396", "#161616"),
    "U3": ("#ee5396", "#161616"),
    "CU": ("#ee5396", "#161616"),
    "RCCX": ("#ee5396", "#161616"),
    "RC3X": ("#ee5396", "#161616"),
    "RZZ": ("#ee5396", "#161616"),
    "T": ("#82cfff", "#161616"),
    "S": ("#82cfff", "#161616"),
    "Z": ("#82cfff", "#161616"),
    "CZ": ("#82cfff", "#161616"),
    "TDG": ("#82cfff", "#161616"),
    "SDG": ("#82cfff", "#161616"),
    "P": ("#82cfff", "#161616"),
    "PHASE": ("#82cfff", "#161616"),
    "CP": ("#82cfff", "#161616"),
    "CPHASE": ("#82cfff", "#161616"),
    "RZ": ("#82cfff", "#161616"),
    "CRZ": ("#82cfff", "#161616"),
    "NOT": ("#4589ff", "#161616"),
    "X": ("#4589ff", "#161616"),
    "CNOT": ("#4589ff", "#161616"),
    "CX": ("#4589ff", "#161616"),
    "TOFFOLI": ("#4589ff", "#161616"),
    "CCX": ("#4589ff", "#161616"),
    "SWAP": ("#4589ff", "#161616"),
    "CSWAP": ("#4589ff", "#161616"),
    "I": ("#4589ff", "#161616"),
    "ID": ("#4589ff", "#161616"),
    "•": ("#4589ff", "#161616"),
    "⊕": ("#4589ff", "#161616"),
    "CH": ("#ff832b", "#161616"),
    "MZ": ("#ffb3b8", "#161616"),
    "MX": ("#ffb3b8", "#161616"),
    "MY": ("#ffb3b8", "#161616"),
    "MN": ("#ffb3b8", "#161616"),
    "REGISTRY": ("#be95ff", "#161616"),
}
PLAYHEAD_COLOR = "#f1c21b"
APP_BG = "#f4f4f4"
CANVAS_BG = "#ffffff"
AXIS_COLOR = "#c6c6c6"
VECTOR_COLOR = "#da1e28"
PROB_COLOR = "#4589ff"
PHASE_POS_COLOR = "#24a148"
PHASE_NEG_COLOR = "#9f1853"


def parse_csv_ints(text: str) -> List[int]:
    values: List[int] = []
    for part in text.split(","):
        stripped = part.strip()
        if stripped:
            values.append(int(stripped))
    return values


def parse_csv_params(text: str) -> List[str]:
    return [part.strip() for part in text.split(",") if part.strip()]


def default_registry_qubits(name: str) -> str:
    spec = get_gate(name)
    if spec.arity < 0:
        return "0"
    return ",".join(str(qubit) for qubit in range(min(spec.arity, N_QUBITS)))


def default_registry_params(name: str) -> str:
    spec = get_gate(name)
    defaults = {
        "theta": "pi/4",
        "phi": "pi/3",
        "lambda": "pi/4",
        "gamma": "0",
    }
    return ",".join(defaults.get(param, "pi/4") for param in spec.params)


def gate_color(label: str) -> Tuple[str, str]:
    text = str(label).strip()
    return GATE_COLORS.get(text, GATE_COLORS.get(text.upper(), GATE_COLORS["I"]))

I2 = np.eye(2, dtype=np.complex128)
X = np.array([[0, 1], [1, 0]], dtype=np.complex128)
Y = np.array([[0, -1j], [1j, 0]], dtype=np.complex128)
Z = np.array([[1, 0], [0, -1]], dtype=np.complex128)
H = (1.0 / math.sqrt(2.0)) * np.array([[1, 1], [1, -1]], dtype=np.complex128)
S = np.array([[1, 0], [0, 1j]], dtype=np.complex128)
T = np.array([[1, 0], [0, np.exp(1j * math.pi / 4.0)]], dtype=np.complex128)


SINGLE_QUBIT_GATES: Dict[str, np.ndarray] = {
    "I": I2,
    "H": H,
    "X": X,
    "Y": Y,
    "Z": Z,
    "S": S,
    "T": T,
}

# Named 4-qubit / 16-step musical circuit presets. Each tuple is
# (qubit, column, gate). CNOTs are represented by a control and target
# in the same column using the existing grid symbols.
CIRCUIT_PRESETS: Dict[str, Tuple[Tuple[int, int, str], ...]] = {
    "Chain": (
        (0, 0, "H"), (1, 1, "H"), (2, 2, "S"), (3, 3, "T"),
        (0, 4, "•"), (1, 4, "⊕"),
        (1, 5, "•"), (2, 5, "⊕"),
        (2, 6, "•"), (3, 6, "⊕"),
        (3, 7, "S"),
        (3, 8, "•"), (0, 8, "⊕"),
        (0, 9, "Y"), (2, 10, "S"),
        (0, 11, "•"), (2, 11, "⊕"),
        (1, 12, "•"), (3, 12, "⊕"),
        (3, 13, "H"), (0, 14, "T"), (1, 15, "S"),
    ),
    "Dyad": (
        (0, 0, "H"), (1, 1, "H"), (2, 2, "H"), (3, 3, "H"),
        (0, 4, "•"), (1, 4, "⊕"),
        (2, 5, "•"), (3, 5, "⊕"),
        (1, 6, "T"), (3, 7, "T"),
        (1, 8, "•"), (2, 8, "⊕"),
        (0, 9, "•"), (3, 9, "⊕"),
        (0, 10, "Y"), (2, 11, "Y"),
        (0, 12, "•"), (2, 12, "⊕"),
        (1, 13, "•"), (3, 13, "⊕"),
        (0, 14, "S"), (3, 15, "H"),
    ),
    "Weave": (
        (0, 0, "H"), (1, 1, "H"), (2, 2, "H"), (3, 3, "H"),
        (0, 4, "•"), (1, 4, "⊕"),
        (1, 5, "S"),
        (1, 6, "•"), (2, 6, "⊕"),
        (2, 7, "T"),
        (2, 8, "•"), (3, 8, "⊕"),
        (3, 9, "S"),
        (3, 10, "•"), (0, 10, "⊕"),
        (0, 11, "T"),
        (0, 12, "•"), (2, 12, "⊕"),
        (1, 13, "•"), (3, 13, "⊕"),
        (0, 14, "H"), (3, 15, "H"),
    ),
    "Spiral": (
        (0, 0, "H"), (1, 1, "S"), (2, 2, "H"), (3, 3, "T"),
        (0, 4, "•"), (1, 4, "⊕"),
        (1, 5, "X"),
        (1, 6, "•"), (2, 6, "⊕"),
        (2, 7, "Y"),
        (2, 8, "•"), (3, 8, "⊕"),
        (3, 9, "S"),
        (3, 10, "•"), (0, 10, "⊕"),
        (0, 11, "T"),
        (0, 12, "•"), (2, 12, "⊕"),
        (1, 13, "H"), (2, 14, "S"), (3, 15, "H"),
    ),
    "Dissolve": (
        (0, 0, "H"), (1, 1, "H"), (2, 2, "S"), (3, 3, "T"),
        (0, 4, "•"), (1, 4, "⊕"),
        (2, 5, "•"), (3, 5, "⊕"),
        (0, 6, "T"), (1, 7, "S"), (2, 8, "T"), (3, 9, "S"),
        (1, 10, "•"), (2, 10, "⊕"),
        (0, 11, "•"), (3, 11, "⊕"),
        (0, 12, "Y"), (1, 13, "X"), (2, 14, "H"), (3, 15, "H"),
    ),
    "Return": (
        (0, 0, "H"), (1, 1, "H"), (2, 2, "H"), (3, 3, "H"),
        (0, 4, "•"), (1, 4, "⊕"),
        (1, 5, "•"), (2, 5, "⊕"),
        (2, 6, "•"), (3, 6, "⊕"),
        (3, 7, "S"), (2, 8, "T"),
        (3, 9, "•"), (0, 9, "⊕"),
        (0, 10, "•"), (2, 10, "⊕"),
        (1, 11, "•"), (3, 11, "⊕"),
        (0, 12, "H"), (1, 13, "S"), (2, 14, "H"), (3, 15, "S"),
    ),
}


# -----------------------------------------------------------------------------
# State-vector simulation
# -----------------------------------------------------------------------------
def apply_single_qubit_gate(
    state: np.ndarray, gate: np.ndarray, qubit: int, n_qubits: int
) -> np.ndarray:
    """Apply a 2x2 gate to `qubit`, where q0 is the top row / most significant bit."""
    tensor = state.reshape((2,) * n_qubits)
    tensor = np.moveaxis(tensor, qubit, 0)
    transformed = np.tensordot(gate, tensor, axes=(1, 0))
    transformed = np.moveaxis(transformed, 0, qubit)
    return transformed.reshape(-1)


def apply_cnot(
    state: np.ndarray, control: int, target: int, n_qubits: int
) -> np.ndarray:
    """Apply CNOT(control, target) using the same q0-most-significant-bit convention."""
    if control == target:
        return state.copy()

    output = np.zeros_like(state)
    target_mask = 1 << (n_qubits - 1 - target)
    control_shift = n_qubits - 1 - control

    for index, amplitude in enumerate(state):
        new_index = index
        if (index >> control_shift) & 1:
            new_index ^= target_mask
        output[new_index] += amplitude
    return output


def one_qubit_reduced_density(state: np.ndarray, qubit: int, n_qubits: int) -> np.ndarray:
    """Partial trace of all but one qubit for a pure state vector."""
    psi = state.reshape((2,) * n_qubits)
    psi = np.moveaxis(psi, qubit, 0).reshape(2, -1)
    return psi @ psi.conj().T


def von_neumann_entropy(rho: np.ndarray) -> float:
    eigenvalues = np.clip(np.linalg.eigvalsh(rho).real, 0.0, 1.0)
    nonzero = eigenvalues[eigenvalues > 1e-12]
    return float(-np.sum(nonzero * np.log2(nonzero))) if len(nonzero) else 0.0


def bloch_vector(rho: np.ndarray) -> Tuple[float, float, float]:
    return (
        float(np.trace(rho @ X).real),
        float(np.trace(rho @ Y).real),
        float(np.trace(rho @ Z).real),
    )


def full_density_matrix(state: np.ndarray) -> np.ndarray:
    """Return the pure-state density matrix |psi><psi| for the full register."""
    return np.outer(state, state.conj())


def _float_list(values: np.ndarray, low: float, high: float) -> List[float]:
    table = np.asarray(values, dtype=np.float64).reshape(-1)
    return [float(value) for value in np.clip(table, low, high)]


def _condition_bipolar_table(values: np.ndarray, gain: float = 1.0) -> List[float]:
    table = np.asarray(values, dtype=np.float64).reshape(-1)
    table = table - float(np.mean(table))
    table = table * gain
    return [float(value) for value in np.clip(table, -1.0, 1.0)]


def _density_bank_metrics(rho: np.ndarray) -> Tuple[float, float, float]:
    hermitian = 0.5 * (rho + rho.conj().T)
    purity = float(np.real(np.trace(hermitian @ hermitian)))
    off_diagonal = hermitian - np.diag(np.diag(hermitian))
    coherence = float(np.sum(np.abs(off_diagonal)))
    eigenvalues = np.clip(np.linalg.eigvalsh(hermitian).real, 1e-12, 1.0)
    entropy = float(-np.sum(eigenvalues * np.log2(eigenvalues)))
    return purity, coherence, entropy


def _axis_bin(value: float, count: int) -> int:
    return int(np.clip(np.floor(float(value) * count), 0, count - 1))


def density_bank_position(rho: np.ndarray) -> Dict[str, int | List[int] | List[float]]:
    purity, coherence, entropy = _density_bank_metrics(
        np.asarray(rho, dtype=np.complex128)
    )
    purity_norm = np.clip((purity - 1.0 / 16.0) / (1.0 - 1.0 / 16.0), 0.0, 1.0)
    coherence_norm = np.clip(coherence / 15.0, 0.0, 1.0)
    entropy_norm = np.clip(entropy / 4.0, 0.0, 1.0)

    px = _axis_bin(float(purity_norm), WAVETABLE_TABLES_PER_AXIS)
    cy = _axis_bin(float(coherence_norm), WAVETABLE_TABLES_PER_AXIS)
    ez = _axis_bin(float(entropy_norm), WAVETABLE_TABLES_PER_AXIS)
    table_index = px + WAVETABLE_TABLES_PER_AXIS * (
        cy + WAVETABLE_TABLES_PER_AXIS * ez
    )
    start = table_index * WAVETABLE_TABLE_SIZE
    end = start + WAVETABLE_TABLE_SIZE

    return {
        "table_index": int(table_index),
        "write_start": int(start),
        "write_end": int(end),
        "axis": [int(px), int(cy), int(ez)],
        "axis_values": [float(purity_norm), float(coherence_norm), float(entropy_norm)],
        "metrics": [float(purity), float(coherence), float(entropy)],
        "global_index": list(range(start, end)),
    }


def density_wavetable_channels(
    rho: np.ndarray,
) -> Dict[str, List[float] | List[int] | Dict[str, int | List[int] | List[float]]]:
    """
    Flatten a 16x16 density matrix into 256-point wavetable/control channels.

    The buffer channel is the sound-first mapping: rho is treated as compact
    complex spectral/control data, then converted into a dense single-cycle
    waveform. The raw channels preserve direct density-matrix values for
    inspection, modulation, or alternate Max mappings.
    """
    matrix = np.asarray(rho, dtype=np.complex128)
    hermitian = 0.5 * (matrix + matrix.conj().T)
    flat = hermitian.reshape(-1)

    spectral = np.fft.ifft(flat).real
    real_scan = flat.real
    imag_scan = flat.imag
    magnitude_scan = np.sqrt(np.abs(flat))
    phase_scan = np.sin(np.angle(flat))
    buffer = (
        0.56 * spectral
        + 0.20 * real_scan
        + 0.16 * imag_scan
        + 0.08 * magnitude_scan * phase_scan
    )
    buffer = buffer - float(np.mean(buffer))
    rms = float(np.sqrt(np.mean(buffer * buffer)))
    if rms > 1e-12:
        buffer = buffer / (4.0 * rms)
    peak = float(np.max(np.abs(buffer)))
    if peak > 1.0:
        buffer = buffer / peak
    buffer = np.clip(buffer, -1.0, 1.0)

    magnitude = np.abs(flat)
    mag_peak = float(np.max(magnitude))
    if mag_peak > 1e-12:
        magnitude = magnitude / mag_peak

    phase = np.zeros_like(magnitude, dtype=np.float64)
    active = magnitude > 1e-9
    phase[active] = np.angle(flat[active]) / math.pi

    return {
        "index": WAVETABLE_SAMPLE_INDEX,
        "phase_index": WAVETABLE_SAMPLE_PHASE,
        "bank": density_bank_position(hermitian),
        "buffer": _float_list(buffer, -1.0, 1.0),
        "real": _condition_bipolar_table(flat.real),
        "imag": _condition_bipolar_table(flat.imag),
        "magnitude": [float(value) for value in np.clip(magnitude, 0.0, 1.0)],
        "phase": [float(value) for value in np.clip(phase, -1.0, 1.0)],
        "raw_real": _float_list(flat.real, -1.0, 1.0),
        "raw_imag": _float_list(flat.imag, -1.0, 1.0),
        "raw_magnitude": _float_list(np.abs(flat), 0.0, 1.0),
        "raw_phase_pi": _float_list(np.angle(flat) / math.pi, -1.0, 1.0),
    }


def two_qubit_reduced_density(
    state: np.ndarray,
    qubit_a: int,
    qubit_b: int,
    n_qubits: int,
) -> np.ndarray:
    """Reduced density matrix for ordered pair (qubit_a, qubit_b)."""
    if qubit_a == qubit_b:
        raise ValueError("Entanglement view needs two distinct qubits.")

    psi = state.reshape((2,) * n_qubits)
    psi = np.moveaxis(psi, (qubit_a, qubit_b), (0, 1)).reshape(4, -1)
    return psi @ psi.conj().T


def qubit_state(theta: float, phi: float) -> np.ndarray:
    return np.array(
        [
            math.cos(theta / 2.0),
            np.exp(1j * phi) * math.sin(theta / 2.0),
        ],
        dtype=np.complex128,
    )


def entanglement_sample_states(count: int = 48) -> List[Tuple[np.ndarray, str, str]]:
    states: List[Tuple[np.ndarray, str, str]] = [
        (qubit_state(math.pi / 2.0, 0.0), "X", "#da1e28"),
        (qubit_state(math.pi / 2.0, math.pi / 2.0), "Y", "#24a148"),
        (qubit_state(0.0, 0.0), "Z", "#0f62fe"),
    ]

    golden_angle = math.pi * (3.0 - math.sqrt(5.0))
    for index in range(count):
        z = 1.0 - 2.0 * (index + 0.5) / count
        theta = math.acos(float(np.clip(z, -1.0, 1.0)))
        phi = index * golden_angle
        states.append((qubit_state(theta, phi), "", "#8d8d8d"))

    return states


def conditional_target_density(
    rho_pair: np.ndarray,
    control_state: np.ndarray,
    *,
    target_first: bool,
) -> Tuple[float, np.ndarray]:
    """Project one qubit of a 2-qubit density matrix and return the other."""
    rho = rho_pair.reshape(2, 2, 2, 2)
    v = control_state

    if target_first:
        projected = np.einsum("c,icjd,d->ij", np.conj(v), rho, v)
    else:
        projected = np.einsum("c,cidj,d->ij", np.conj(v), rho, v)

    probability = float(np.trace(projected).real)
    if probability <= 1e-12:
        return 0.0, np.eye(2, dtype=np.complex128) / 2.0

    return probability, projected / probability


def conditional_bloch_cloud(
    state: np.ndarray,
    target_qubit: int,
    control_qubit: int,
    n_qubits: int,
) -> List[Tuple[float, float, float, float, str, str]]:
    """Points showing what the control qubit can tell us about the target."""
    rho_pair = two_qubit_reduced_density(
        state,
        target_qubit,
        control_qubit,
        n_qubits,
    )
    points: List[Tuple[float, float, float, float, str, str]] = []

    for control_state, label, color in entanglement_sample_states():
        probability, target_density = conditional_target_density(
            rho_pair,
            control_state,
            target_first=True,
        )
        x, y, z = bloch_vector(target_density)
        points.append((x, y, z, probability, label, color))

    return points


def conditional_bloch_probe(
    state: np.ndarray,
    target_qubit: int,
    control_qubit: int,
    n_qubits: int,
    theta: float,
    phi: float,
) -> Tuple[float, float, float, float, str, str]:
    rho_pair = two_qubit_reduced_density(
        state,
        target_qubit,
        control_qubit,
        n_qubits,
    )
    probability, target_density = conditional_target_density(
        rho_pair,
        qubit_state(theta, phi),
        target_first=True,
    )
    x, y, z = bloch_vector(target_density)
    return x, y, z, probability, "N", "#f1c21b"


def pauli_pair_correlations(
    state: np.ndarray, qubit_a: int, qubit_b: int, n_qubits: int
) -> Tuple[float, float, float, float, float]:
    """Return XX, XY, YX, YY, ZZ expectations for a pair of distinct qubits.

    These observables preserve non-local phase information that may disappear
    from individual Bloch vectors after the qubits become entangled.
    """
    values: List[float] = []
    for op_a, op_b in ((X, X), (X, Y), (Y, X), (Y, Y), (Z, Z)):
        transformed = apply_single_qubit_gate(state, op_a, qubit_a, n_qubits)
        transformed = apply_single_qubit_gate(transformed, op_b, qubit_b, n_qubits)
        values.append(float(np.vdot(state, transformed).real))
    return tuple(values)  # type: ignore[return-value]


@dataclass
class CircuitFrame:
    column: int
    state: np.ndarray
    density_matrix: np.ndarray
    basis_probabilities: np.ndarray
    bloch_vectors: List[Tuple[float, float, float]]
    local_entropies: List[float]
    pair_correlations: Dict[Tuple[int, int], Tuple[float, float, float, float, float]]


@dataclass
class RegistryPreviewOperation:
    step: int
    name: str
    qubits: Tuple[int, ...]
    params: Tuple[float | int | str, ...] = ()


@dataclass
class ClipboardCell:
    kind: str
    label: str
    source_qubit: int
    source_column: int
    offsets: Tuple[Tuple[int, str], ...]
    params: Tuple[float | int | str, ...] = ()


class CircuitProgram:
    """Editable gate grid plus state evolution."""

    def __init__(self, n_qubits: int = N_QUBITS, n_steps: int = N_STEPS) -> None:
        self.n_qubits = n_qubits
        self.n_steps = n_steps
        self.grid: List[List[str]] = [
            ["I" for _ in range(n_steps)] for _ in range(n_qubits)
        ]
        self.registry_operations: List[RegistryPreviewOperation] = []
        self.make_bell_preset()

    def clear(self) -> None:
        self.grid = [["I" for _ in range(self.n_steps)] for _ in range(self.n_qubits)]
        self.registry_operations.clear()

    def make_bell_preset(self) -> None:
        """A compact starting circuit with a Bell pair and optional phase activity on q2."""
        self.clear()
        if self.n_qubits >= 1 and self.n_steps >= 1:
            self.grid[0][0] = "H"
        if self.n_qubits >= 2 and self.n_steps >= 2:
            self.grid[0][1] = "•"
            self.grid[1][1] = "⊕"
        if self.n_qubits >= 3:
            for column, gate in ((2, "H"), (3, "T"), (4, "T"), (5, "H")):
                if column < self.n_steps:
                    self.grid[2][column] = gate
        if self.n_qubits >= 2 and self.n_steps >= 8:
            self.grid[1][7] = "X"
        if self.n_qubits >= 1 and self.n_steps >= 9:
            self.grid[0][8] = "S"

    def load_preset(self, name: str) -> None:
        """Load a named musical circuit preset into the editable gate grid."""
        if name not in CIRCUIT_PRESETS:
            raise ValueError(f"Unknown circuit preset: {name}")

        self.clear()
        for qubit, column, gate in CIRCUIT_PRESETS[name]:
            if qubit < self.n_qubits and column < self.n_steps:
                self.set_gate(qubit, column, gate)

    def set_gate(self, qubit: int, column: int, gate: str) -> None:
        if gate not in GATE_LABELS:
            raise ValueError(f"Unknown gate label: {gate}")

        # A column has at most one CNOT control and one target.
        if gate == "•":
            for row in range(self.n_qubits):
                if self.grid[row][column] == "•":
                    self.grid[row][column] = "I"
        elif gate == "⊕":
            for row in range(self.n_qubits):
                if self.grid[row][column] == "⊕":
                    self.grid[row][column] = "I"

        self.grid[qubit][column] = gate

    def clear_cell(self, qubit: int, column: int) -> None:
        self.grid[qubit][column] = "I"
        self.registry_operations = [
            op
            for op in self.registry_operations
            if not (op.step == column and qubit in op.qubits)
        ]

    def add_registry_operation(
        self,
        step: int,
        name: str,
        qubits: Sequence[int],
        params: Sequence[float | int | str] = (),
    ) -> None:
        if not (0 <= step < self.n_steps):
            raise ValueError(f"step must be 0..{self.n_steps - 1}")
        self.registry_operations = [
            op
            for op in self.registry_operations
            if not (op.step == step and any(qubit in op.qubits for qubit in qubits))
        ]
        self.registry_operations.append(
            RegistryPreviewOperation(
                step=step,
                name=get_gate(name).name,
                qubits=tuple(int(qubit) for qubit in qubits),
                params=tuple(params),
            )
        )

    def registry_operations_at(self, column: int) -> List[RegistryPreviewOperation]:
        return [op for op in self.registry_operations if op.step == column]

    def validate_column(self, column: int) -> List[str]:
        controls = [q for q in range(self.n_qubits) if self.grid[q][column] == "•"]
        targets = [q for q in range(self.n_qubits) if self.grid[q][column] == "⊕"]
        warnings: List[str] = []
        if controls and not targets:
            warnings.append(f"column {column + 1}: CNOT control has no target")
        if targets and not controls:
            warnings.append(f"column {column + 1}: CNOT target has no control")
        if controls and targets and controls[0] == targets[0]:
            warnings.append(f"column {column + 1}: CNOT control and target coincide")
        return warnings

    def to_openqasm2_lines(self) -> List[str]:
        lines = [
            "OPENQASM 2.0;",
            'include "qelib1.inc";',
            f"qreg q[{self.n_qubits}];",
            "// QMW q0 is the top row / most-significant live-engine bit.",
        ]

        for column in range(self.n_steps):
            column_lines: List[str] = []

            for qubit in range(self.n_qubits):
                gate = self.grid[qubit][column]
                if gate in SINGLE_QUBIT_GATES and gate != "I":
                    column_lines.append(f"{gate.lower()} q[{qubit}];")

            controls = [q for q in range(self.n_qubits) if self.grid[q][column] == "•"]
            targets = [q for q in range(self.n_qubits) if self.grid[q][column] == "⊕"]
            if len(controls) == 1 and len(targets) == 1 and controls[0] != targets[0]:
                column_lines.append(f"cx q[{controls[0]}],q[{targets[0]}];")
            elif controls or targets:
                column_lines.append(f"// column {column + 1}: incomplete CNOT ignored")

            if column_lines:
                lines.append(f"// column {column + 1}")
                lines.extend(column_lines)

        return lines

    def to_openqasm2(self) -> str:
        return "\n".join(self.to_openqasm2_lines())

    def evolve(self) -> Tuple[List[CircuitFrame], List[str]]:
        state = np.zeros(2 ** self.n_qubits, dtype=np.complex128)
        state[0] = 1.0 + 0.0j
        frames: List[CircuitFrame] = []
        warnings: List[str] = []

        for column in range(self.n_steps):
            warnings.extend(self.validate_column(column))

            # Single-qubit gates are applied first. Gates on separate qubits commute.
            for qubit in range(self.n_qubits):
                label = self.grid[qubit][column]
                if label in SINGLE_QUBIT_GATES and label != "I":
                    state = apply_single_qubit_gate(
                        state, SINGLE_QUBIT_GATES[label], qubit, self.n_qubits
                    )

            controls = [q for q in range(self.n_qubits) if self.grid[q][column] == "•"]
            targets = [q for q in range(self.n_qubits) if self.grid[q][column] == "⊕"]
            if len(controls) == 1 and len(targets) == 1 and controls[0] != targets[0]:
                state = apply_cnot(state, controls[0], targets[0], self.n_qubits)

            for op in self.registry_operations_at(column):
                try:
                    numeric_params = [
                        ComposerCircuit._numeric_param(param)
                        for param in op.params
                    ]
                    state = ComposerCircuit._apply_simulation_gate(
                        state,
                        op.name,
                        op.qubits,
                        numeric_params,
                        self.n_qubits,
                    )
                except NotImplementedError:
                    warnings.append(
                        f"column {column + 1}: local preview skipped {op.name}"
                    )
                except Exception as exc:
                    warnings.append(
                        f"column {column + 1}: local preview rejected {op.name}: {exc}"
                    )

            # Protect against accumulated numerical drift.
            norm = np.linalg.norm(state)
            if norm > 0.0:
                state = state / norm

            reduced = [
                one_qubit_reduced_density(state, q, self.n_qubits)
                for q in range(self.n_qubits)
            ]
            rho_full = full_density_matrix(state)
            frames.append(
                CircuitFrame(
                    column=column,
                    state=state.copy(),
                    density_matrix=rho_full,
                    basis_probabilities=np.abs(state) ** 2,
                    bloch_vectors=[bloch_vector(rho) for rho in reduced],
                    local_entropies=[von_neumann_entropy(rho) for rho in reduced],
                    pair_correlations={
                        (a, b): pauli_pair_correlations(state, a, b, self.n_qubits)
                        for a in range(self.n_qubits)
                        for b in range(a + 1, self.n_qubits)
                    },
                )
            )

        return frames, warnings


# -----------------------------------------------------------------------------
# OSC output bridge
# -----------------------------------------------------------------------------
class OSCBridge:
    def __init__(self, host: str = OSC_HOST, port: int = OSC_PORT) -> None:
        self.host = host
        self.port = port
        self.client = SimpleUDPClient(host, port) if SimpleUDPClient else None
        self.wavetable_bank = np.zeros(WAVETABLE_BANK_SIZE, dtype=np.float64)
        self.wavetable_bank_write_counts = np.zeros(
            WAVETABLE_TABLE_COUNT,
            dtype=np.int64,
        )
        self.wavetable_bank_next_index = 0

    @property
    def available(self) -> bool:
        return self.client is not None

    def send_frame(self, frame: CircuitFrame) -> None:
        if not self.client:
            return

        self.client.send_message("/qmw/circuit/playhead", frame.column)
        self.client.send_message(
            "/qmw/circuit/probabilities",
            [float(value) for value in frame.basis_probabilities],
        )

        for q, ((x, y, z), entropy) in enumerate(
            zip(frame.bloch_vectors, frame.local_entropies)
        ):
            self.client.send_message(f"/qmw/circuit/q{q}/bloch", [x, y, z])
            self.client.send_message(f"/qmw/circuit/q{q}/entropy", entropy)

        for (a, b), values in frame.pair_correlations.items():
            self.client.send_message(f"/qmw/circuit/correlation/{a}_{b}", list(values))

        channels = density_wavetable_channels(frame.density_matrix)
        semantic_bank = channels["bank"]
        if not isinstance(semantic_bank, dict):
            return
        table_index = int(self.wavetable_bank_next_index)
        write_start = table_index * WAVETABLE_TABLE_SIZE
        write_end = write_start + WAVETABLE_TABLE_SIZE
        buffer = np.asarray(channels["buffer"], dtype=np.float64)
        self.wavetable_bank[write_start:write_end] = buffer
        self.wavetable_bank_write_counts[table_index] += 1
        self.wavetable_bank_next_index = (
            self.wavetable_bank_next_index + 1
        ) % WAVETABLE_TABLE_COUNT

        self.client.send_message("/qmw/circuit/wavetable/size", len(channels["real"]))
        self.client.send_message("/qmw/circuit/wavetable/index", channels["index"])
        self.client.send_message(
            "/qmw/circuit/wavetable/phase_index",
            channels["phase_index"],
        )
        self.client.send_message("/qmw/circuit/wavetable/table_index", table_index)
        self.client.send_message("/qmw/circuit/wavetable/buffer", channels["buffer"])
        self.client.send_message(
            "/qmw/circuit/wavetable/bank/tables_per_axis",
            WAVETABLE_TABLES_PER_AXIS,
        )
        self.client.send_message(
            "/qmw/circuit/wavetable/bank/table_count",
            WAVETABLE_TABLE_COUNT,
        )
        self.client.send_message(
            "/qmw/circuit/wavetable/bank/table_size",
            WAVETABLE_TABLE_SIZE,
        )
        self.client.send_message(
            "/qmw/circuit/wavetable/bank/size",
            WAVETABLE_BANK_SIZE,
        )
        self.client.send_message(
            "/qmw/circuit/wavetable/bank/table_index",
            table_index,
        )
        self.client.send_message(
            "/qmw/circuit/wavetable/bank/write_start",
            write_start,
        )
        self.client.send_message(
            "/qmw/circuit/wavetable/bank/write_end",
            write_end,
        )
        self.client.send_message(
            "/qmw/circuit/wavetable/bank/axis",
            semantic_bank["axis"],
        )
        self.client.send_message(
            "/qmw/circuit/wavetable/bank/axis_values",
            semantic_bank["axis_values"],
        )
        self.client.send_message(
            "/qmw/circuit/wavetable/bank/metrics",
            semantic_bank["metrics"],
        )
        self.client.send_message(
            "/qmw/circuit/wavetable/bank/semantic_table_index",
            int(semantic_bank["table_index"]),
        )
        self.client.send_message(
            "/qmw/circuit/wavetable/bank/semantic_write_start",
            int(semantic_bank["write_start"]),
        )
        self.client.send_message(
            "/qmw/circuit/wavetable/bank/global_index",
            list(range(write_start, write_end)),
        )
        self.client.send_message(
            "/qmw/circuit/wavetable/bank/write_buffer",
            channels["buffer"],
        )
        self.client.send_message(
            "/qmw/circuit/wavetable/bank/write_count",
            int(self.wavetable_bank_write_counts[table_index]),
        )
        self.client.send_message(
            "/qmw/circuit/wavetable/bank/write_counts",
            [int(value) for value in self.wavetable_bank_write_counts],
        )
        self.client.send_message("/qmw/circuit/wavetable/real", channels["real"])
        self.client.send_message("/qmw/circuit/wavetable/imag", channels["imag"])
        self.client.send_message(
            "/qmw/circuit/wavetable/magnitude",
            channels["magnitude"],
        )
        self.client.send_message("/qmw/circuit/wavetable/phase", channels["phase"])
        self.client.send_message(
            "/qmw/circuit/density/raw_real",
            channels["raw_real"],
        )
        self.client.send_message(
            "/qmw/circuit/density/raw_imag",
            channels["raw_imag"],
        )
        self.client.send_message(
            "/qmw/circuit/density/raw_magnitude",
            channels["raw_magnitude"],
        )
        self.client.send_message(
            "/qmw/circuit/density/raw_phase_pi",
            channels["raw_phase_pi"],
        )
        self.client.send_message(
            "/qmw/circuit/density/purity",
            float(np.real(np.trace(frame.density_matrix @ frame.density_matrix))),
        )


# -----------------------------------------------------------------------------
# OSC control: GUI -> running QMW engine
# -----------------------------------------------------------------------------
class CircuitControlBridge:
    """Sends circuit edits to QMWCircuitBridge on UDP port 9002."""

    def __init__(self, host: str = OSC_HOST, port: int = CONTROL_PORT) -> None:
        self.host = host
        self.port = port
        self.client = SimpleUDPClient(host, port) if SimpleUDPClient else None

    @property
    def available(self) -> bool:
        return self.client is not None

    def set_gate(self, qubit: int, column: int, gate: str) -> None:
        if self.client:
            self.client.send_message("/qmw/circuit/set", [qubit, column, gate])

    def set_operation(
        self,
        step: int,
        name: str,
        qubits: Sequence[int],
        params: Sequence[float | int | str] = (),
        classical_target: int | None = None,
        target_register: Optional[str] = None,
        register_bit: Optional[int] = None,
        osc_route: Optional[str] = None,
        persistence: str = "single_shot",
        shots: int = 1,
    ) -> None:
        if not self.client:
            return

        args: List[object] = [
            int(step),
            str(name),
            ",".join(str(qubit) for qubit in qubits),
            ",".join(str(param) for param in params),
        ]
        if classical_target is not None:
            args.append(int(classical_target))
        elif target_register is not None:
            args.append("")

        if target_register is not None:
            register = normalize_register_bus_name(target_register)
            args.extend(
                [
                    register,
                    "" if register_bit is None else int(register_bit),
                    osc_route or default_measurement_osc_route(register),
                    persistence,
                    int(shots),
                ]
            )

        self.client.send_message("/qmw/circuit/op", args)

    def clear_cell(self, qubit: int, column: int) -> None:
        if self.client:
            self.client.send_message("/qmw/circuit/clear_cell", [qubit, column])

    def clear(self) -> None:
        if self.client:
            self.client.send_message("/qmw/circuit/clear", 1)

    def preset(self) -> None:
        if self.client:
            self.client.send_message("/qmw/circuit/preset", 1)

    def enabled(self, is_enabled: bool) -> None:
        if self.client:
            self.client.send_message("/qmw/circuit/enable", int(is_enabled))

    def interval(self, seconds: float) -> None:
        if self.client:
            self.client.send_message("/qmw/circuit/interval", float(seconds))
    def step(self) -> None:
        if self.client:
            self.client.send_message("/qmw/circuit/step", 1)

# -----------------------------------------------------------------------------
# Tk GUI
# -----------------------------------------------------------------------------
class CircuitBuilderApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("QMW — Interactive Circuit Builder")
        self.geometry("1200x760")
        self.resizable(True, True)
        self.configure(bg=APP_BG)

        self.program = CircuitProgram()
        self.osc = OSCBridge()
        self.control = CircuitControlBridge()
        self.selected_gate = tk.StringVar(value="H")
        self.registry_gate = tk.StringVar(value="rx")
        self.registry_step = tk.IntVar(value=0)
        self.registry_qubits = tk.StringVar(value=default_registry_qubits("rx"))
        self.registry_params = tk.StringVar(value=default_registry_params("rx"))
        self.measurement_basis = tk.StringVar(value="MZ")
        self.measurement_step = tk.IntVar(value=0)
        self.measurement_qubit = tk.IntVar(value=0)
        self.measurement_register = tk.StringVar(value="pitch")
        self.measurement_bit = tk.IntVar(value=0)
        self.measurement_theta = tk.StringVar(value="pi/3")
        self.measurement_phi = tk.StringVar(value="pi/4")
        self.measurement_persistence = tk.StringVar(value="single_shot")
        self.measurement_shots = tk.IntVar(value=1)
        self.data_operator = tk.StringVar(value=QUANTUM_DATA_OPERATORS[0])
        self.preset_name = tk.StringVar(value="Chain")
        self.entanglement_target = tk.IntVar(value=0)
        self.entanglement_control = tk.IntVar(value=1)
        self.status = tk.StringVar()
        self.metrics = tk.StringVar()
        self.interval_ms = tk.IntVar(value=250)
        self.running = False
        self.playhead = 0
        self.selected_cell: Tuple[int, int] = (0, 0)
        self.cell_clipboard: Optional[ClipboardCell] = None
        self.cells: List[List[tk.Button]] = []
        self.measurement_cells: Dict[Tuple[int, int], str] = {}
        self.registry_cells: Dict[Tuple[int, int], str] = {}
        self.bloch_canvas: tk.Canvas | None = None
        self.entanglement_canvas: tk.Canvas | None = None
        self.state_canvas: tk.Canvas | None = None
        self.registry_gate.trace_add("write", self._on_registry_gate_changed)
        self.bind_all("<Command-c>", self.copy_selected_cell)
        self.bind_all("<Command-v>", self.paste_to_selected_cell)
        self.bind_all("<Control-c>", self.copy_selected_cell)
        self.bind_all("<Control-v>", self.paste_to_selected_cell)

        self._build_ui()
        self.refresh_view()
        self.update_preview()

    def _build_ui(self) -> None:
        root = ttk_frame(self)
        root.pack(fill="both", expand=True, padx=12, pady=12)

        title = tk.Label(root, text="Interactive Circuit Builder", font=("Helvetica", 18, "bold"))
        title.pack(anchor="w")
        subtitle = tk.Label(
            root,
            text=(
                "Choose a gate and click a cell. Edits are sent live to Quantum Population v5 on UDP 7403; "
                "the engine evolves the density matrix and streams features to Max on UDP 7400. "
                "Right-click clears a cell. CNOT: place control then target in the same column."
            ),
            justify="left",
            wraplength=980,
        )
        subtitle.pack(anchor="w", pady=(2, 10))

        palette = ttk_frame(root)
        palette.pack(fill="x", pady=(0, 8))
        tk.Label(palette, text="Gate palette:", font=("Helvetica", 12, "bold")).pack(side="left", padx=(0, 8))
        for display_name, gate in PALETTE_GATES:
            # Wider labels make CNOT construction visible even on systems whose
            # installed font lacks the • / ⊕ glyphs.
            bg, fg = gate_color(gate)
            tk.Radiobutton(
                palette,
                text=display_name,
                value=gate,
                variable=self.selected_gate,
                indicatoron=False,
                width=max(3, len(display_name) + 1),
                pady=4,
                bg=bg,
                fg=fg,
                selectcolor=bg,
                activebackground=bg,
                activeforeground=fg,
                highlightbackground=bg,
                highlightcolor=bg,
            ).pack(side="left", padx=2)

        material = ttk_frame(root)
        material.pack(fill="x", pady=(0, 8))
        tk.Label(
            material,
            text="Material measurement:",
            font=("Helvetica", 12, "bold"),
        ).pack(side="left", padx=(0, 8))
        tk.Label(material, text="basis").pack(side="left")
        tk.OptionMenu(material, self.measurement_basis, *MEASUREMENT_MACROS).pack(side="left", padx=(2, 6))
        tk.Label(material, text="step").pack(side="left")
        tk.Spinbox(
            material,
            from_=0,
            to=N_STEPS - 1,
            width=4,
            textvariable=self.measurement_step,
        ).pack(side="left", padx=(2, 6))
        tk.Label(material, text="q").pack(side="left")
        tk.Spinbox(
            material,
            from_=0,
            to=N_QUBITS - 1,
            width=3,
            textvariable=self.measurement_qubit,
        ).pack(side="left", padx=(2, 6))
        tk.Label(material, text="register").pack(side="left")
        tk.OptionMenu(material, self.measurement_register, *QMW_REGISTER_BUSES).pack(side="left", padx=(2, 6))
        tk.Label(material, text="bit").pack(side="left")
        tk.Spinbox(
            material,
            from_=0,
            to=7,
            width=3,
            textvariable=self.measurement_bit,
        ).pack(side="left", padx=(2, 6))
        tk.Label(material, text="θ").pack(side="left")
        tk.Entry(material, width=7, textvariable=self.measurement_theta).pack(side="left", padx=(2, 4))
        tk.Label(material, text="φ").pack(side="left")
        tk.Entry(material, width=7, textvariable=self.measurement_phi).pack(side="left", padx=(2, 6))
        tk.Button(
            material,
            text="Send M→register",
            command=self.send_measurement_operation,
        ).pack(side="left", padx=(4, 0))

        material_row_2 = ttk_frame(root)
        material_row_2.pack(fill="x", pady=(0, 8))
        tk.Label(
            material_row_2,
            text="Registry op:",
            font=("Helvetica", 12, "bold"),
        ).pack(side="left", padx=(0, 8))
        tk.OptionMenu(material_row_2, self.registry_gate, *REGISTRY_GATE_OPTIONS).pack(side="left", padx=(0, 6))
        tk.Label(material_row_2, text="step").pack(side="left")
        tk.Spinbox(
            material_row_2,
            from_=0,
            to=N_STEPS - 1,
            width=4,
            textvariable=self.registry_step,
        ).pack(side="left", padx=(2, 6))
        tk.Label(material_row_2, text="qubits").pack(side="left")
        tk.Entry(material_row_2, width=8, textvariable=self.registry_qubits).pack(side="left", padx=(2, 6))
        tk.Label(material_row_2, text="params").pack(side="left")
        tk.Entry(material_row_2, width=14, textvariable=self.registry_params).pack(side="left", padx=(2, 6))
        tk.Button(
            material_row_2,
            text="Send op",
            command=self.send_registry_operation,
        ).pack(side="left", padx=(4, 12))
        tk.Label(
            material_row_2,
            text="Data operator:",
            font=("Helvetica", 11, "bold"),
        ).pack(side="left", padx=(0, 6))
        tk.OptionMenu(material_row_2, self.data_operator, *QUANTUM_DATA_OPERATORS).pack(side="left", padx=(0, 6))
        tk.Label(
            material_row_2,
            text="first-class BitArray operators for Max/QMW routing",
            fg="#525252",
        ).pack(side="left")

        controls = ttk_frame(root)
        controls.pack(fill="x", pady=(0, 10))

        controls_row_1 = ttk_frame(controls)
        controls_row_1.pack(fill="x", pady=(0, 4))
        tk.Button(controls_row_1, text="Run", width=8, command=self.run).pack(side="left", padx=(0, 4))
        tk.Button(controls_row_1, text="Stop", width=8, command=self.stop).pack(side="left", padx=4)
        tk.Button(controls_row_1, text="Step", width=8, command=self.step_once).pack(side="left", padx=4)
        tk.Button(controls_row_1, text="Bell preset", width=12, command=self.bell_preset).pack(side="left", padx=(14, 4))
        tk.Button(controls_row_1, text="Clear", width=8, command=self.clear_all).pack(side="left", padx=4)
        tk.Button(controls_row_1, text="Copy QASM", width=10, command=self.copy_qasm).pack(side="left", padx=4)

        controls_row_2 = ttk_frame(controls)
        controls_row_2.pack(fill="x")
        tk.Label(controls_row_2, text="Musical preset:", font=("Helvetica", 11, "bold")).pack(side="left", padx=(0, 6))
        tk.OptionMenu(
            controls_row_2,
            self.preset_name,
            *CIRCUIT_PRESETS.keys(),
        ).pack(side="left", padx=(0, 6))
        tk.Button(
            controls_row_2,
            text="Load preset",
            width=12,
            command=self.load_named_preset,
        ).pack(side="left", padx=4)
        tk.Label(controls_row_2, text="Frame interval (ms):").pack(side="left", padx=(20, 4))
        tk.Spinbox(
            controls_row_2,
            from_=40,
            to=2000,
            increment=10,
            textvariable=self.interval_ms,
            width=6,
        ).pack(side="left")

        workbench = ttk_frame(root)
        workbench.pack(fill="both", expand=True)

        grid_frame = ttk_frame(workbench)
        grid_frame.pack(fill="x", anchor="w")
        tk.Label(grid_frame, text="qubit / step", font=("Helvetica", 10, "bold")).grid(
            row=0, column=0, padx=4, pady=4, sticky="nsew"
        )
        for column in range(self.program.n_steps):
            tk.Label(grid_frame, text=str(column + 1), font=("Helvetica", 10, "bold")).grid(
                row=0, column=column + 1, padx=2, pady=4
            )

        for qubit in range(self.program.n_qubits):
            tk.Label(grid_frame, text=f"q{qubit}", font=("Helvetica", 11, "bold")).grid(
                row=qubit + 1, column=0, padx=4, pady=3, sticky="e"
            )
            button_row: List[tk.Button] = []
            for column in range(self.program.n_steps):
                button = tk.Button(
                    grid_frame,
                    width=4,
                    height=2,
                    font=("Menlo", 14, "bold"),
                    borderwidth=2,
                    highlightthickness=2,
                    command=lambda q=qubit, c=column: self.place_gate(q, c),
                )
                button.bind("<Button-3>", lambda event, q=qubit, c=column: self.clear_cell(q, c))
                button.bind("<Option-Button-1>", lambda event, q=qubit, c=column: self.select_cell(q, c))
                button.bind("<Alt-Button-1>", lambda event, q=qubit, c=column: self.select_cell(q, c))
                button.grid(row=qubit + 1, column=column + 1, padx=2, pady=2)
                button_row.append(button)
            self.cells.append(button_row)

        analysis_frame = ttk_frame(root)
        analysis_frame.pack(fill="x", pady=(8, 6))

        bloch_panel = ttk_frame(analysis_frame)
        bloch_panel.pack(side="left", padx=(0, 10), anchor="n")
        tk.Label(
            bloch_panel,
            text="Bloch vectors",
            font=("Helvetica", 11, "bold"),
        ).pack(anchor="w")
        self.bloch_canvas = tk.Canvas(
            bloch_panel,
            width=300,
            height=250,
            bg=CANVAS_BG,
            highlightthickness=1,
            highlightbackground="#e0e0e0",
        )
        self.bloch_canvas.pack(pady=(4, 0))

        entanglement_panel = ttk_frame(analysis_frame)
        entanglement_panel.pack(side="left", padx=(0, 10), anchor="n")
        entanglement_header = ttk_frame(entanglement_panel)
        entanglement_header.pack(fill="x")
        tk.Label(
            entanglement_header,
            text="Entanglement cloud",
            font=("Helvetica", 11, "bold"),
        ).pack(side="left")
        tk.Label(entanglement_header, text="target").pack(side="left", padx=(12, 2))
        target_spin = tk.Spinbox(
            entanglement_header,
            from_=0,
            to=N_QUBITS - 1,
            width=3,
            textvariable=self.entanglement_target,
            command=self.update_preview,
        )
        target_spin.pack(side="left")
        tk.Label(entanglement_header, text="control").pack(side="left", padx=(8, 2))
        control_spin = tk.Spinbox(
            entanglement_header,
            from_=0,
            to=N_QUBITS - 1,
            width=3,
            textvariable=self.entanglement_control,
            command=self.update_preview,
        )
        control_spin.pack(side="left")
        self.entanglement_canvas = tk.Canvas(
            entanglement_panel,
            width=300,
            height=250,
            bg=CANVAS_BG,
            highlightthickness=1,
            highlightbackground="#e0e0e0",
        )
        self.entanglement_canvas.pack(pady=(4, 0))

        state_panel = ttk_frame(analysis_frame)
        state_panel.pack(side="left", anchor="n")
        tk.Label(
            state_panel,
            text="State vector probabilities",
            font=("Helvetica", 11, "bold"),
        ).pack(anchor="w")
        self.state_canvas = tk.Canvas(
            state_panel,
            width=300,
            height=250,
            bg=CANVAS_BG,
            highlightthickness=1,
            highlightbackground="#e0e0e0",
        )
        self.state_canvas.pack(pady=(4, 0))

        tk.Label(root, textvariable=self.status, justify="left", anchor="w", wraplength=980).pack(
            fill="x", pady=(4, 2)
        )
        tk.Label(root, textvariable=self.metrics, justify="left", anchor="w", wraplength=980, font=("Menlo", 10)).pack(
            fill="x", pady=(2, 0)
        )

    def place_gate(self, qubit: int, column: int) -> None:
        self.selected_cell = (qubit, column)
        gate = self.selected_gate.get()
        self.measurement_cells.pop((qubit, column), None)
        self.registry_cells.pop((qubit, column), None)
        self.program.set_gate(qubit, column, gate)
        self.control.set_gate(qubit, column, gate)
        self.playhead = min(self.playhead, self.program.n_steps - 1)
        self.refresh_view()
        self.update_preview()

    def select_cell(self, qubit: int, column: int) -> None:
        self.selected_cell = (qubit, column)
        self.refresh_view()

    def _on_registry_gate_changed(self, *_: object) -> None:
        name = self.registry_gate.get()
        try:
            self.registry_qubits.set(default_registry_qubits(name))
            self.registry_params.set(default_registry_params(name))
        except Exception as exc:
            self.status.set(f"Registry gate metadata unavailable: {exc}")

    def copy_selected_cell(self, _event: object | None = None) -> str:
        qubit, column = self.selected_cell
        copied = self._copy_cell(qubit, column)
        if copied is None:
            self.status.set(f"Nothing to copy at q{qubit}, step {column + 1}.")
        else:
            self.cell_clipboard = copied
            self.status.set(
                f"Copied {copied.label} from q{qubit}, step {column + 1}."
            )
        return "break"

    def paste_to_selected_cell(self, _event: object | None = None) -> str:
        if self.cell_clipboard is None:
            self.status.set("Clipboard is empty.")
            return "break"

        qubit, column = self.selected_cell
        try:
            self._paste_cell(self.cell_clipboard, qubit, column)
            self.status.set(
                f"Pasted {self.cell_clipboard.label} to q{qubit}, step {column + 1}."
            )
            self.refresh_view()
            self.update_preview()
        except Exception as exc:
            self.status.set(f"Paste rejected: {exc}")
        return "break"

    def _copy_cell(self, qubit: int, column: int) -> Optional[ClipboardCell]:
        measurement_label = self.measurement_cells.get((qubit, column))
        if measurement_label is not None:
            return ClipboardCell(
                kind="measurement",
                label=measurement_label,
                source_qubit=qubit,
                source_column=column,
                offsets=((0, measurement_label),),
            )

        for op in self.program.registry_operations:
            if op.step == column and qubit in op.qubits:
                return ClipboardCell(
                    kind="registry",
                    label=op.name.upper(),
                    source_qubit=qubit,
                    source_column=column,
                    offsets=tuple((q - qubit, op.name.upper()) for q in op.qubits),
                    params=op.params,
                )

        label = self.program.grid[qubit][column]
        if label == "I":
            return None

        if label in {"•", "⊕"}:
            controls = [q for q in range(self.program.n_qubits) if self.program.grid[q][column] == "•"]
            targets = [q for q in range(self.program.n_qubits) if self.program.grid[q][column] == "⊕"]
            if len(controls) == 1 and len(targets) == 1:
                return ClipboardCell(
                    kind="grid_pair",
                    label="CX",
                    source_qubit=qubit,
                    source_column=column,
                    offsets=(
                        (controls[0] - qubit, "•"),
                        (targets[0] - qubit, "⊕"),
                    ),
                )

        return ClipboardCell(
            kind="grid",
            label=label,
            source_qubit=qubit,
            source_column=column,
            offsets=((0, label),),
        )

    def _paste_cell(self, copied: ClipboardCell, qubit: int, column: int) -> None:
        targets = [(qubit + offset, label) for offset, label in copied.offsets]
        if any(q < 0 or q >= self.program.n_qubits for q, _label in targets):
            raise ValueError("paste would move part of the operation outside the grid")

        for target_qubit, _label in targets:
            self.measurement_cells.pop((target_qubit, column), None)
            self.registry_cells.pop((target_qubit, column), None)
            self.program.clear_cell(target_qubit, column)
            self.control.clear_cell(target_qubit, column)

        if copied.kind == "measurement":
            label = copied.label.upper()
            self.measurement_cells[(qubit, column)] = label
            params: List[str] = []
            if label == "MN":
                params = [
                    self.measurement_theta.get().strip() or "pi/3",
                    self.measurement_phi.get().strip() or "pi/4",
                ]
            self.control.set_operation(column, label, [qubit], params=params)
            return

        if copied.kind == "registry":
            paste_qubits = [target_qubit for target_qubit, _label in targets]
            self.program.add_registry_operation(
                column,
                copied.label.lower(),
                paste_qubits,
                params=copied.params,
            )
            self.control.set_operation(
                column,
                copied.label.lower(),
                paste_qubits,
                params=copied.params,
            )
            for target_qubit, _label in targets:
                self.registry_cells[(target_qubit, column)] = copied.label.upper()
            return

        for target_qubit, label in targets:
            self.program.set_gate(target_qubit, column, label)
            self.control.set_gate(target_qubit, column, label)

    def send_measurement_operation(self) -> None:
        name = self.measurement_basis.get()
        step = int(self.measurement_step.get())
        qubit = int(self.measurement_qubit.get())
        register = normalize_register_bus_name(self.measurement_register.get())
        register_bit = int(self.measurement_bit.get())
        params: List[str] = []
        if name.upper() == "MN":
            params = [
                self.measurement_theta.get().strip() or "pi/3",
                self.measurement_phi.get().strip() or "pi/4",
            ]

        self.measurement_cells[(qubit, step)] = name.upper()
        self.registry_cells.pop((qubit, step), None)
        self.control.set_operation(
            step,
            name,
            [qubit],
            params=params,
            target_register=register,
            register_bit=register_bit,
            persistence=self.measurement_persistence.get(),
            shots=int(self.measurement_shots.get()),
        )
        process = DEFAULT_REGISTER_PROCESSES.get(register, register)
        self.status.set(
            f"Sent {name.upper()} q{qubit} → {register}[{register_bit}] "
            f"({process}) on UDP {self.control.port}."
        )
        self.refresh_view()
        self.update_preview()

    def send_registry_operation(self) -> None:
        try:
            step = int(self.registry_step.get())
            name = self.registry_gate.get()
            spec = get_gate(name)
            qubits = parse_csv_ints(self.registry_qubits.get())
            params = parse_csv_params(self.registry_params.get()) if spec.params else []
            validate_gate_call(name, qubits, params)
            self.control.set_operation(step, name, qubits, params=params)
            self.program.add_registry_operation(step, name, qubits, params=params)
            for qubit in qubits:
                self.registry_cells[(qubit, step)] = name.upper()
            self.status.set(
                f"Sent registry op {name} q={qubits} params={params} "
                f"to UDP {self.control.port}."
            )
            self.refresh_view()
            self.update_preview()
        except Exception as exc:
            self.status.set(f"Registry op rejected locally: {exc}")

    def clear_cell(self, qubit: int, column: int) -> str:
        self.measurement_cells.pop((qubit, column), None)
        self.registry_cells.pop((qubit, column), None)
        self.program.clear_cell(qubit, column)
        self.control.clear_cell(qubit, column)
        self.refresh_view()
        self.update_preview()
        return "break"

    def clear_all(self) -> None:
        self.stop()
        self.program.clear()
        self.measurement_cells.clear()
        self.registry_cells.clear()
        self.control.clear()
        self.playhead = 0
        self.refresh_view()
        self.update_preview()

    def bell_preset(self) -> None:
        self.stop()
        self.program.make_bell_preset()
        self.measurement_cells.clear()
        self.registry_cells.clear()
        self.control.preset()
        self.playhead = 0
        self.refresh_view()
        self.update_preview()

    def load_named_preset(self) -> None:
        """Load a named score locally and transmit its complete grid to QMW."""
        self.stop()
        name = self.preset_name.get()
        self.program.load_preset(name)
        self.measurement_cells.clear()
        self.registry_cells.clear()

        # The live engine only needs its existing clear/set OSC protocol.
        self.control.clear()
        for qubit in range(self.program.n_qubits):
            for column in range(self.program.n_steps):
                gate = self.program.grid[qubit][column]
                if gate != "I":
                    self.control.set_gate(qubit, column, gate)

        self.playhead = 0
        self.refresh_view()
        self.update_preview()
        self.status.set(
            f"Loaded {name} preset and sent its 16-step score to QMW on UDP {self.control.port}."
        )

    def copy_qasm(self) -> None:
        qasm = self.program.to_openqasm2()
        self.clipboard_clear()
        self.clipboard_append(qasm)
        self.status.set("OpenQASM 2.0 copied to clipboard.")

    def refresh_view(self) -> None:
        for qubit in range(self.program.n_qubits):
            for column in range(self.program.n_steps):
                label = self.program.grid[qubit][column]
                measurement_label = self.measurement_cells.get((qubit, column))
                registry_label = self.registry_cells.get((qubit, column))
                button = self.cells[qubit][column]
                # Use ASCII fallbacks in cells: these remain readable in any Tk font.
                visible_label = (
                    measurement_label
                    or registry_label
                    or {"•": "CTRL", "⊕": "XOR"}.get(label, label)
                )
                color_key = measurement_label or registry_label or label
                bg, fg = gate_color(color_key)
                if column == self.playhead and measurement_label is None and registry_label is None:
                    bg = PLAYHEAD_COLOR
                    fg = "#161616"
                button.configure(
                    text=visible_label,
                    bg=bg,
                    fg=fg,
                    activebackground=bg,
                    activeforeground=fg,
                    highlightbackground=bg,
                    highlightcolor=bg,
                )
                if (qubit, column) == self.selected_cell:
                    button.configure(relief="solid", borderwidth=4)
                else:
                    button.configure(
                        relief="sunken" if column == self.playhead else "raised",
                        borderwidth=2,
                    )

    def update_preview(self) -> None:
        frames, warnings = self.program.evolve()
        frame = frames[self.playhead]
        osc_text = (f"QMW control → {self.control.host}:{self.control.port}; engine/Max output → {self.osc.host}:{self.osc.port}" if self.control.available else "OSC disabled: install python-osc")
        warning_text = " | ".join(warnings) if warnings else "circuit valid"
        self.status.set(f"{osc_text}   •   {warning_text}")

        basis = " ".join(f"{value:.2f}" for value in frame.basis_probabilities)
        bloch = "  ".join(
            f"q{q}=({x:+.2f}, {y:+.2f}, {z:+.2f}), S={entropy:.2f}"
            for q, ((x, y, z), entropy) in enumerate(zip(frame.bloch_vectors, frame.local_entropies))
        )
        correlation = frame.pair_correlations.get((0, 1))
        corr_text = ""
        if correlation is not None:
            xx, xy, yx, yy, zz = correlation
            corr_text = f"\nq0–q1 correlations [XX, XY, YX, YY, ZZ] = [{xx:+.2f}, {xy:+.2f}, {yx:+.2f}, {yy:+.2f}, {zz:+.2f}]"
        self.metrics.set(
            f"step {frame.column + 1}/{self.program.n_steps}   basis probabilities: [{basis}]\n{bloch}{corr_text}"
        )
        self.draw_visual_state(frame, frames)

    def draw_visual_state(
        self,
        frame: CircuitFrame,
        frames: Optional[Sequence[CircuitFrame]] = None,
    ) -> None:
        self.draw_bloch_vectors(frame, frames or ())
        self.draw_entanglement_cloud(frame)
        self.draw_state_vector(frame)

    def draw_bloch_vectors(
        self,
        frame: CircuitFrame,
        frames: Sequence[CircuitFrame] = (),
    ) -> None:
        if self.bloch_canvas is None:
            return

        canvas = self.bloch_canvas
        canvas.delete("all")
        width = int(canvas["width"])
        radius = 40
        centers = [(78, 68), (222, 68), (78, 174), (222, 174)]

        for q, ((x, y, z), entropy) in enumerate(
            zip(frame.bloch_vectors, frame.local_entropies)
        ):
            cx, cy = centers[q]
            canvas.create_oval(
                cx - radius,
                cy - radius,
                cx + radius,
                cy + radius,
                outline="#8d8d8d",
                width=2,
            )
            canvas.create_line(cx - radius, cy, cx + radius, cy, fill=AXIS_COLOR)
            canvas.create_line(cx, cy - radius, cx, cy + radius, fill=AXIS_COLOR)
            canvas.create_text(cx - radius - 10, cy, text="-X", fill="#6f6f6f", font=("Menlo", 8))
            canvas.create_text(cx + radius + 10, cy, text="+X", fill="#6f6f6f", font=("Menlo", 8))
            canvas.create_text(cx, cy - radius - 10, text="+Z", fill="#6f6f6f", font=("Menlo", 8))
            canvas.create_text(cx, cy + radius + 10, text="-Z", fill="#6f6f6f", font=("Menlo", 8))

            trail_points = []
            for index, past in enumerate(frames[: self.playhead + 1]):
                if q >= len(past.bloch_vectors):
                    continue
                tx, ty, tz = past.bloch_vectors[q]
                trail_points.append((cx + tx * radius, cy - tz * radius, ty, index))

            for (x0, y0, depth, index), (x1, y1, _depth1, _index1) in zip(
                trail_points,
                trail_points[1:],
            ):
                shade = 130 + int(90 * (index / max(1, len(trail_points) - 1)))
                color = f"#{shade:02x}{shade:02x}{shade:02x}"
                canvas.create_line(x0, y0, x1, y1, fill=color, width=2)

            vx = cx + x * radius
            vy = cy - z * radius
            depth_color = PHASE_POS_COLOR if y >= 0.0 else PHASE_NEG_COLOR
            depth_size = 4 + int(4 * min(1.0, abs(y)))
            canvas.create_line(cx, cy, vx, vy, fill=VECTOR_COLOR, width=3, arrow=tk.LAST)
            canvas.create_oval(
                vx - depth_size,
                vy - depth_size,
                vx + depth_size,
                vy + depth_size,
                fill=depth_color,
                outline="#161616",
            )
            spin_phase = math.atan2(y, x)
            canvas.create_text(
                cx,
                cy + radius + 18,
                text=f"q{q} y={y:+.2f} phase={spin_phase:+.2f} S={entropy:.2f}",
                fill="#161616",
                font=("Menlo", 8),
            )

        canvas.create_text(
            width // 2,
            18,
            text="spin XZ projection; dot color/size shows Y depth; grey trail shows motion",
            fill="#525252",
            font=("Helvetica", 9),
        )

    def draw_entanglement_cloud(self, frame: CircuitFrame) -> None:
        if self.entanglement_canvas is None:
            return

        canvas = self.entanglement_canvas
        canvas.delete("all")
        width = int(canvas["width"])
        height = int(canvas["height"])
        cx = width // 2
        cy = height // 2 + 6
        radius = 82

        try:
            target = int(self.entanglement_target.get())
            control = int(self.entanglement_control.get())
            if target == control:
                raise ValueError("choose two distinct qubits")
            if not (0 <= target < self.program.n_qubits and 0 <= control < self.program.n_qubits):
                raise ValueError("qubit out of range")
            points = conditional_bloch_cloud(
                frame.state,
                target,
                control,
                self.program.n_qubits,
            )
            theta_text = self.measurement_theta.get().strip() or "pi/3"
            phi_text = self.measurement_phi.get().strip() or "pi/4"
            theta = parse_pi_param(theta_text)
            phi = parse_pi_param(phi_text)
            if theta is None or phi is None:
                raise ValueError(f"bad probe angle θ={theta_text!r} φ={phi_text!r}")
            probe = conditional_bloch_probe(
                frame.state,
                target,
                control,
                self.program.n_qubits,
                theta,
                phi,
            )
        except Exception as exc:
            canvas.create_text(
                cx,
                cy,
                text=f"Entanglement cloud unavailable\n{exc}",
                fill="#525252",
                font=("Helvetica", 10),
                justify="center",
            )
            return

        root_x, root_y, root_z = frame.bloch_vectors[target]
        root_px = cx + root_x * radius
        root_py = cy - root_y * radius

        canvas.create_oval(
            cx - radius,
            cy - radius,
            cx + radius,
            cy + radius,
            outline="#8d8d8d",
            width=2,
        )
        canvas.create_line(cx - radius, cy, cx + radius, cy, fill=AXIS_COLOR)
        canvas.create_line(cx, cy - radius, cx, cy + radius, fill=AXIS_COLOR)
        canvas.create_text(cx - radius - 12, cy, text="-X", fill="#6f6f6f", font=("Menlo", 8))
        canvas.create_text(cx + radius + 12, cy, text="+X", fill="#6f6f6f", font=("Menlo", 8))
        canvas.create_text(cx, cy - radius - 12, text="+Y", fill="#6f6f6f", font=("Menlo", 8))
        canvas.create_text(cx, cy + radius + 12, text="-Y", fill="#6f6f6f", font=("Menlo", 8))

        unlabeled = [point for point in points if not point[4]]
        labeled = [point for point in points if point[4]]
        spread = 0.0
        for x, y, z, probability, _label, color in unlabeled:
            px = cx + x * radius
            py = cy - y * radius
            size = 2.0 + 4.0 * max(0.0, min(1.0, abs(z)))
            spread = max(spread, math.sqrt(x * x + y * y + z * z))
            canvas.create_oval(
                px - size,
                py - size,
                px + size,
                py + size,
                fill=color,
                outline="",
                stipple="gray50" if probability < 0.20 else "",
            )

        canvas.create_oval(
            root_px - 5,
            root_py - 5,
            root_px + 5,
            root_py + 5,
            fill="#f1c21b",
            outline="#161616",
        )

        for x, y, z, _probability, label, color in labeled:
            px = cx + x * radius
            py = cy - y * radius
            spread = max(spread, math.sqrt(x * x + y * y + z * z))
            canvas.create_line(root_px, root_py, px, py, fill=color, width=2)
            canvas.create_oval(
                px - 6,
                py - 6,
                px + 6,
                py + 6,
                fill=color,
                outline="#161616",
            )
            canvas.create_text(
                px,
                py - 13,
                text=label,
                fill="#161616",
                font=("Menlo", 9, "bold"),
            )

        x, y, z, probability, label, color = probe
        px = cx + x * radius
        py = cy - y * radius
        spread = max(spread, math.sqrt(x * x + y * y + z * z))
        canvas.create_line(root_px, root_py, px, py, fill=color, width=3, dash=(4, 3))
        canvas.create_oval(
            px - 7,
            py - 7,
            px + 7,
            py + 7,
            fill=color,
            outline="#161616",
            width=2,
        )
        canvas.create_text(
            px,
            py - 16,
            text=label,
            fill="#161616",
            font=("Menlo", 10, "bold"),
        )

        canvas.create_text(
            cx,
            16,
            text=(
                f"q{control} informs q{target}  N=({theta_text},{phi_text}) "
                f"p={probability:.2f}"
            ),
            fill="#161616",
            font=("Helvetica", 9, "bold"),
        )
        canvas.create_text(
            cx,
            height - 12,
            text="point/line/ball: separable → correlated → entangled",
            fill="#525252",
            font=("Helvetica", 8),
        )

    def draw_state_vector(self, frame: CircuitFrame) -> None:
        if self.state_canvas is None:
            return

        canvas = self.state_canvas
        canvas.delete("all")
        width = int(canvas["width"])
        height = int(canvas["height"])
        margin_left = 54
        margin_bottom = 28
        chart_top = 28
        chart_height = height - margin_bottom - chart_top
        probs = frame.basis_probabilities
        max_prob = max(float(np.max(probs)), 1e-9)
        bar_gap = 2
        bar_width = max(6, int((width - margin_left - 12) / len(probs)) - bar_gap)

        canvas.create_line(
            margin_left,
            chart_top,
            margin_left,
            height - margin_bottom,
            fill=AXIS_COLOR,
        )
        canvas.create_line(
            margin_left,
            height - margin_bottom,
            width - 8,
            height - margin_bottom,
            fill=AXIS_COLOR,
        )
        canvas.create_text(28, chart_top + 4, text="P", fill="#525252", font=("Menlo", 9))

        for index, probability in enumerate(probs):
            x0 = margin_left + index * (bar_width + bar_gap)
            bar_height = (float(probability) / max_prob) * (chart_height - 8)
            y0 = height - margin_bottom - bar_height
            x1 = x0 + bar_width
            y1 = height - margin_bottom
            amplitude = frame.state[index]
            phase = math.atan2(float(amplitude.imag), float(amplitude.real))
            fill = PROB_COLOR if phase >= 0 else "#6929c4"
            canvas.create_rectangle(x0, y0, x1, y1, fill=fill, outline="")

            if probability > 0.08 or index in (0, len(probs) - 1):
                label = format(index, f"0{self.program.n_qubits}b")
                canvas.create_text(
                    x0 + bar_width / 2,
                    height - 12,
                    text=label,
                    angle=90,
                    fill="#525252",
                    font=("Menlo", 7),
                )

        canvas.create_text(
            width // 2,
            14,
            text=f"basis probabilities  max={max_prob:.3f}",
            fill="#161616",
            font=("Helvetica", 9, "bold"),
        )

    def emit_current_frame(self) -> None:
        frames, _ = self.program.evolve()
        frame = frames[self.playhead]
        self.osc.send_frame(frame)
        self.update_preview()

    def step_once(self) -> None:
        # Tell the real density engine to apply one circuit column.
        self.control.step()
        # Advance local display in the same direction.

        self.playhead = (
            self.playhead + 1
        ) % self.program.n_steps

        frames, _ = self.program.evolve()
        self.osc.send_frame(frames[self.playhead])
        self.refresh_view()
        self.update_preview()

    def run(self) -> None:
        """Start the controller-owned transport using explicit OSC step events."""
        if self.running:
            return

        self.control.interval(max(0.01, float(self.interval_ms.get()) / 1000.0))
        # The GUI sends one explicit step per tick. Keep the engine's autonomous
        # circuit clock disabled so columns cannot advance twice.
        self.control.enabled(False)
        self.running = True
        self.status.set("Running controller transport.")
        self._tick()

    def stop(self) -> None:
        self.running = False
        self.control.enabled(False)
        self.status.set("Controller transport stopped.")

    def _tick(self) -> None:
        if not self.running:
            return

        # This is the same live-engine command used by the manual Step button.
        self.control.step()
        self.playhead = (self.playhead + 1) % self.program.n_steps
        frames, _ = self.program.evolve()
        self.osc.send_frame(frames[self.playhead])
        self.refresh_view()
        self.update_preview()

        interval = max(40, int(self.interval_ms.get()))
        self.after(interval, self._tick)


def ttk_frame(parent: tk.Misc) -> tk.Frame:
    """A neutral frame helper; avoids external GUI dependencies."""
    return tk.Frame(parent, bg=APP_BG)


if __name__ == "__main__":
    app = CircuitBuilderApp()
    app.mainloop()
