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
from typing import Dict, List, Sequence, Tuple

import numpy as np

try:
    from pythonosc.udp_client import SimpleUDPClient
except ImportError:
    SimpleUDPClient = None


# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------
N_QUBITS = 3
N_STEPS = 12
OSC_HOST = "127.0.0.1"
OSC_PORT = 9001

GATE_LABELS: Tuple[str, ...] = ("I", "H", "X", "Y", "Z", "S", "T", "•", "⊕")

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
    basis_probabilities: np.ndarray
    bloch_vectors: List[Tuple[float, float, float]]
    local_entropies: List[float]
    pair_correlations: Dict[Tuple[int, int], Tuple[float, float, float, float, float]]


class CircuitProgram:
    """Editable gate grid plus state evolution."""

    def __init__(self, n_qubits: int = N_QUBITS, n_steps: int = N_STEPS) -> None:
        self.n_qubits = n_qubits
        self.n_steps = n_steps
        self.grid: List[List[str]] = [
            ["I" for _ in range(n_steps)] for _ in range(n_qubits)
        ]
        self.make_bell_preset()

    def clear(self) -> None:
        self.grid = [["I" for _ in range(self.n_steps)] for _ in range(self.n_qubits)]

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

            # Protect against accumulated numerical drift.
            norm = np.linalg.norm(state)
            if norm > 0.0:
                state = state / norm

            reduced = [
                one_qubit_reduced_density(state, q, self.n_qubits)
                for q in range(self.n_qubits)
            ]
            frames.append(
                CircuitFrame(
                    column=column,
                    state=state.copy(),
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


# -----------------------------------------------------------------------------
# Tk GUI
# -----------------------------------------------------------------------------
class CircuitBuilderApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("QMW — Interactive Circuit Builder")
        self.resizable(True, True)

        self.program = CircuitProgram()
        self.osc = OSCBridge()
        self.selected_gate = tk.StringVar(value="H")
        self.status = tk.StringVar()
        self.metrics = tk.StringVar()
        self.interval_ms = tk.IntVar(value=250)
        self.running = False
        self.playhead = 0
        self.cells: List[List[tk.Button]] = []

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
                "Choose a gate, click a cell to place it, then Run to stream the evolving state to Max/QMW. "
                "Right-click a cell to clear it.  • + ⊕ in one column form a CNOT."
            ),
            justify="left",
            wraplength=980,
        )
        subtitle.pack(anchor="w", pady=(2, 10))

        palette = ttk_frame(root)
        palette.pack(fill="x", pady=(0, 8))
        tk.Label(palette, text="Gate palette:", font=("Helvetica", 12, "bold")).pack(side="left", padx=(0, 8))
        for gate in GATE_LABELS:
            tk.Radiobutton(
                palette,
                text=gate,
                value=gate,
                variable=self.selected_gate,
                indicatoron=False,
                width=3,
                pady=4,
            ).pack(side="left", padx=2)

        grid_frame = ttk_frame(root)
        grid_frame.pack(fill="both", expand=True)
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
                    command=lambda q=qubit, c=column: self.place_gate(q, c),
                )
                button.bind("<Button-3>", lambda event, q=qubit, c=column: self.clear_cell(q, c))
                button.grid(row=qubit + 1, column=column + 1, padx=2, pady=2)
                button_row.append(button)
            self.cells.append(button_row)

        controls = ttk_frame(root)
        controls.pack(fill="x", pady=(10, 6))
        tk.Button(controls, text="Run", width=8, command=self.run).pack(side="left", padx=(0, 4))
        tk.Button(controls, text="Stop", width=8, command=self.stop).pack(side="left", padx=4)
        tk.Button(controls, text="Step", width=8, command=self.step_once).pack(side="left", padx=4)
        tk.Button(controls, text="Bell preset", width=12, command=self.bell_preset).pack(side="left", padx=(14, 4))
        tk.Button(controls, text="Clear", width=8, command=self.clear_all).pack(side="left", padx=4)
        tk.Label(controls, text="Frame interval (ms):").pack(side="left", padx=(20, 4))
        tk.Spinbox(controls, from_=40, to=2000, increment=10, textvariable=self.interval_ms, width=6).pack(side="left")

        tk.Label(root, textvariable=self.status, justify="left", anchor="w", wraplength=980).pack(
            fill="x", pady=(4, 2)
        )
        tk.Label(root, textvariable=self.metrics, justify="left", anchor="w", wraplength=980, font=("Menlo", 10)).pack(
            fill="x", pady=(2, 0)
        )

    def place_gate(self, qubit: int, column: int) -> None:
        self.program.set_gate(qubit, column, self.selected_gate.get())
        self.playhead = min(self.playhead, self.program.n_steps - 1)
        self.refresh_view()
        self.update_preview()

    def clear_cell(self, qubit: int, column: int) -> str:
        self.program.clear_cell(qubit, column)
        self.refresh_view()
        self.update_preview()
        return "break"

    def clear_all(self) -> None:
        self.stop()
        self.program.clear()
        self.playhead = 0
        self.refresh_view()
        self.update_preview()

    def bell_preset(self) -> None:
        self.stop()
        self.program.make_bell_preset()
        self.playhead = 0
        self.refresh_view()
        self.update_preview()

    def refresh_view(self) -> None:
        for qubit in range(self.program.n_qubits):
            for column in range(self.program.n_steps):
                label = self.program.grid[qubit][column]
                button = self.cells[qubit][column]
                button.configure(text=label)
                button.configure(relief="sunken" if column == self.playhead else "raised")

    def update_preview(self) -> None:
        frames, warnings = self.program.evolve()
        frame = frames[self.playhead]
        osc_text = f"OSC → {self.osc.host}:{self.osc.port}" if self.osc.available else "OSC disabled: install python-osc"
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

    def emit_current_frame(self) -> None:
        frames, _ = self.program.evolve()
        frame = frames[self.playhead]
        self.osc.send_frame(frame)
        self.update_preview()

    def step_once(self) -> None:
        self.emit_current_frame()
        self.playhead = (self.playhead + 1) % self.program.n_steps
        self.refresh_view()
        self.update_preview()

    def run(self) -> None:
        if not self.running:
            self.running = True
            self._tick()

    def stop(self) -> None:
        self.running = False

    def _tick(self) -> None:
        if not self.running:
            return
        self.emit_current_frame()
        self.playhead = (self.playhead + 1) % self.program.n_steps
        self.refresh_view()
        self.after(max(40, int(self.interval_ms.get())), self._tick)


def ttk_frame(parent: tk.Misc) -> tk.Frame:
    """A neutral frame helper; avoids external GUI dependencies."""
    return tk.Frame(parent)


if __name__ == "__main__":
    app = CircuitBuilderApp()
    app.mainloop()
