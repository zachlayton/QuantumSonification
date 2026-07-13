#!/usr/bin/env python3
"""
qmw_complex_pauli_synth_v1.py

Quantum Material Workbench
Complex Pauli Oscillator / Circuit-Controlled Coherence Synthesis layer.

Purpose
-------
Receives continuous operator-control OSC streams from the QMW operator preset
morpher, evolves four local complex qubit states, derives Pauli/Bloch data,
then exposes the complex coherence phasor as an oscillator object for Max or
a downstream audio engine.

Concept
-------
    quantum circuit / operator presets
        -> smooth operator controls
        -> complex qubit state evolution
        -> Pauli expectation values
        -> complex coherence phasors
        -> oscillator render parameters

Core oscillator idea
--------------------
For each qubit:

    c = alpha* beta
    x = 2 Re(c)
    y = 2 Im(c)
    z = population polarity
    phasor = x + i*y
    audio = amp * cos(2*pi*freq*t + phase)

Here X/Y are not only modulation streams. They are the real and imaginary
parts of a Bloch-plane oscillator coefficient.

This version is intentionally local and playable.
It does NOT require IBM hardware.
It does NOT synthesize audio directly.
It outputs musical control streams for Max.

Recommended chain
-----------------
Terminal 1:
    python control/qmw_operator_preset_morpher_v1.py --out-port 7410 --in-port 7404

Terminal 2:
    python synth/qmw_complex_pauli_synth_v1.py --in-port 7410 --out-port 7403

Optional circuit-analysis input:
    /qmw/circuit/q0/bloch x y z
    /qmw/circuit/q0/entropy s
    /qmw/circuit/correlation/0_1 xx xy yx yy zz

Max:
    udpreceive 7403

Primary Max-facing outputs:
    /qmw/q0/x
    /qmw/q0/y
    /qmw/q0/z
    /qmw/q0/coherence/re
    /qmw/q0/coherence/im
    /qmw/q0/coherence/amp
    /qmw/q0/coherence/phase
    /qmw/q0/coherence/dphase
    /qmw/q0/amp
    /qmw/q0/phase
    /qmw/q0/freq
    /qmw/q0/audio_phase
    /qmw/q0/sample
    /qmw/corr/0/1/zz
    /qmw/time/q/0/trig
    /qmw/time/q/0/gate
    /qmw/time/q/0/probability
    /qmw/time/q/0/velocity
    /qmw/time/q/0/accent
    /qmw/time/q/0/dur_ms
    /qmw/time/grain/trig
    /qmw/time/grain/voice
    /qmw/time/articulation/trig
    /qmw/time/corr/01/trig

Dependency
----------
    pip install python-osc
"""

from __future__ import annotations

import argparse
import math
import signal
import sys
import threading
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

try:
    from pythonosc.dispatcher import Dispatcher
    from pythonosc.osc_server import ThreadingOSCUDPServer
    from pythonosc.udp_client import SimpleUDPClient
except ImportError as exc:
    raise SystemExit(
        "Missing dependency: python-osc. Install with: pip install python-osc"
    ) from exc


N_QUBITS = 4

DEFAULT_RATIOS = [1.0, 5.0 / 4.0, 3.0 / 2.0, 7.0 / 4.0]

LOCAL_X_TERMS = ["XIII", "IXII", "IIXI", "IIIX"]
LOCAL_Y_TERMS = ["YIII", "IYII", "IIYI", "IIIY"]
LOCAL_Z_TERMS = ["ZIII", "IZII", "IIZI", "IIIZ"]

DEFAULT_STRING_TERMS = [
    "ZIII", "IZII", "IIZI", "IIIZ",
    "XIII", "IXII", "IIXI", "IIIX",
    "YIII", "IYII", "IIYI", "IIIY",
    "ZZII", "IZZI", "IIZZ", "ZIIZ",
    "XXII", "IXXI", "IIXX", "XIIX",
    "YYII", "IYYI", "IIYY", "YIIY",
    "XYII", "YXII", "IXYI", "IYXI",
    "XXXX", "YYYY", "ZZZZ",
    "XXYY", "YYXX", "XYXY", "YXYX",
]

CORR_PAIRS = ["01", "02", "03", "12", "13", "23"]
CORR_TERMS = ["xx", "yy", "zz", "xy", "yx"]


def clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, float(x)))


def clamp01(x: float) -> float:
    return clamp(x, 0.0, 1.0)


def wrap_pi(x: float) -> float:
    return (x + math.pi) % (2.0 * math.pi) - math.pi


def norm_phase_01(rad: float) -> float:
    return (rad % (2.0 * math.pi)) / (2.0 * math.pi)


def phase_delta(a: float, b: float) -> float:
    """Shortest signed phase distance from a to b, in radians."""
    return (b - a + math.pi) % (2.0 * math.pi) - math.pi


def safe_atan2(y: float, x: float) -> float:
    if abs(x) < 1e-12 and abs(y) < 1e-12:
        return 0.0
    return math.atan2(y, x)


def shannon_binary(p: float) -> float:
    p = clamp01(p)
    if p <= 1e-12 or p >= 1.0 - 1e-12:
        return 0.0
    return -(p * math.log2(p) + (1.0 - p) * math.log2(1.0 - p))


@dataclass
class ComplexQubit:
    """
    Single-qubit complex state.

    |psi> = alpha |0> + beta |1>

    Bloch coordinates:
        x = <X> = 2 Re(alpha* beta)
        y = <Y> = 2 Im(alpha* beta)
        z = <Z> = |alpha|^2 - |beta|^2
    """

    alpha: complex = 1.0 + 0.0j
    beta: complex = 0.0 + 0.0j

    def normalize(self) -> None:
        n = math.sqrt(abs(self.alpha) ** 2 + abs(self.beta) ** 2)
        if n <= 1e-15:
            self.alpha = 1.0 + 0.0j
            self.beta = 0.0 + 0.0j
            return
        self.alpha /= n
        self.beta /= n

    def rx(self, theta: float) -> None:
        c = math.cos(theta / 2.0)
        s = math.sin(theta / 2.0)
        a = c * self.alpha - 1j * s * self.beta
        b = -1j * s * self.alpha + c * self.beta
        self.alpha, self.beta = a, b
        self.normalize()

    def ry(self, theta: float) -> None:
        c = math.cos(theta / 2.0)
        s = math.sin(theta / 2.0)
        a = c * self.alpha - s * self.beta
        b = s * self.alpha + c * self.beta
        self.alpha, self.beta = a, b
        self.normalize()

    def rz(self, theta: float) -> None:
        self.alpha *= complex(math.cos(-theta / 2.0), math.sin(-theta / 2.0))
        self.beta *= complex(math.cos(theta / 2.0), math.sin(theta / 2.0))
        self.normalize()

    def coherence(self) -> complex:
        return self.alpha.conjugate() * self.beta

    def bloch(self) -> Tuple[float, float, float]:
        coherence = self.coherence()
        x = 2.0 * coherence.real
        y = 2.0 * coherence.imag
        z = abs(self.alpha) ** 2 - abs(self.beta) ** 2
        return x, y, z

    def population_1(self) -> float:
        return abs(self.beta) ** 2

    def set_from_bloch(self, x: float, y: float, z: float) -> None:
        """
        Reconstruct a pure-state representative from a Bloch vector.

        External circuit analysis can send reduced or mixed-state vectors. This
        preserves their direction while keeping this v1 oscillator state local.
        """
        x = clamp(x, -1.0, 1.0)
        y = clamp(y, -1.0, 1.0)
        z = clamp(z, -1.0, 1.0)
        radius = min(1.0, math.sqrt(x * x + y * y + z * z))
        if radius <= 1e-12:
            self.alpha = 1.0 + 0.0j
            self.beta = 0.0 + 0.0j
            return

        zn = clamp(z / radius, -1.0, 1.0)
        theta = math.acos(zn)
        phi = safe_atan2(y, x)
        self.alpha = math.cos(theta / 2.0) + 0.0j
        self.beta = math.sin(theta / 2.0) * complex(math.cos(phi), math.sin(phi))
        self.normalize()


@dataclass
class PauliSynthControls:
    f0: float = 41.2
    master_amp: float = 1.0
    rotation_scale: float = 1.0
    ham_depth: float = 0.6
    corr_mix: float = 0.5
    freq_mod_depth: float = 0.035

    global_values: Dict[str, float] = field(default_factory=lambda: {
        "density": 0.5,
        "entropy_bias": 0.5,
        "noise": 0.0,
        "harmonicity": 0.75,
        "inharmonicity": 0.25,
        "articulation": 0.4,
        "spatial_spread": 0.5,
        "mapping_depth": 0.85,
    })

    qubits: List[Dict[str, float]] = field(default_factory=lambda: [
        {
            "rx": math.pi * 0.50,
            "ry": math.pi * 0.25,
            "rz": math.pi * 0.20,
            "mx": 0.5,
            "my": 0.5,
            "mz": 0.5,
            "amp_depth": 0.8,
            "phase_depth": 0.8,
            "bright_depth": 0.6,
            "pan_depth": 0.7,
        },
        {
            "rx": math.pi * 0.38,
            "ry": math.pi * 0.63,
            "rz": math.pi * 0.70,
            "mx": 0.5,
            "my": 0.5,
            "mz": 0.5,
            "amp_depth": 0.75,
            "phase_depth": 0.85,
            "bright_depth": 0.5,
            "pan_depth": 0.65,
        },
        {
            "rx": math.pi * 0.71,
            "ry": math.pi * 0.41,
            "rz": math.pi * 1.20,
            "mx": 0.5,
            "my": 0.5,
            "mz": 0.5,
            "amp_depth": 0.7,
            "phase_depth": 0.9,
            "bright_depth": 0.75,
            "pan_depth": 0.8,
        },
        {
            "rx": math.pi * 0.29,
            "ry": math.pi * 0.82,
            "rz": math.pi * 1.61,
            "mx": 0.5,
            "my": 0.5,
            "mz": 0.5,
            "amp_depth": 0.85,
            "phase_depth": 0.75,
            "bright_depth": 0.7,
            "pan_depth": 0.75,
        },
    ])

    ham: Dict[str, float] = field(default_factory=lambda: {
        term: 0.0 for term in DEFAULT_STRING_TERMS
    })

    corr_targets: Dict[str, Dict[str, float]] = field(default_factory=lambda: {
        pair: {term: 0.0 for term in CORR_TERMS} for pair in CORR_PAIRS
    })


@dataclass
class ComplexPauliSynth:
    osc_host: str = "127.0.0.1"
    osc_out_port: int = 7403
    osc_in_port: int = 7410
    rate_hz: float = 120.0
    controls: PauliSynthControls = field(default_factory=PauliSynthControls)
    qubits: List[ComplexQubit] = field(default_factory=lambda: [ComplexQubit() for _ in range(N_QUBITS)])
    carrier_phases: List[float] = field(default_factory=lambda: [0.0 for _ in range(N_QUBITS)])
    previous_carrier_phases: List[Optional[float]] = field(default_factory=lambda: [None for _ in range(N_QUBITS)])
    previous_coherence_phases: List[Optional[float]] = field(default_factory=lambda: [None for _ in range(N_QUBITS)])
    coherence_phase_velocities: List[float] = field(default_factory=lambda: [0.0 for _ in range(N_QUBITS)])
    gate_until: List[float] = field(default_factory=lambda: [0.0 for _ in range(N_QUBITS)])
    previous_corr_values: Dict[str, Dict[str, float]] = field(default_factory=dict)
    previous_articulation_energy: float = 0.0
    last_grain_voice: int = 0
    ratios: List[float] = field(default_factory=lambda: DEFAULT_RATIOS.copy())
    external_bloch: List[Optional[Tuple[float, float, float]]] = field(default_factory=lambda: [None for _ in range(N_QUBITS)])
    external_entropies: List[Optional[float]] = field(default_factory=lambda: [None for _ in range(N_QUBITS)])
    external_correlations: Dict[str, Dict[str, float]] = field(default_factory=dict)
    external_last_seen: float = 0.0
    external_timeout: float = 0.75
    string_divider: int = 12
    frame_count: int = 0
    running: bool = True

    def __post_init__(self) -> None:
        self.client = SimpleUDPClient(self.osc_host, self.osc_out_port)
        self.server: Optional[ThreadingOSCUDPServer] = None
        self._server_thread: Optional[threading.Thread] = None

    def send(self, addr: str, *values: Any) -> None:
        try:
            self.client.send_message(addr, list(values) if len(values) > 1 else values[0])
        except Exception as exc:
            print(f"OSC send error {addr}: {exc}", file=sys.stderr)

    # ---------------------------------------------------------------------
    # OSC input parsing
    # ---------------------------------------------------------------------

    def setup_server(self) -> None:
        dispatcher = Dispatcher()
        dispatcher.set_default_handler(self.osc_default)
        self.server = ThreadingOSCUDPServer(("0.0.0.0", self.osc_in_port), dispatcher)
        self._server_thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self._server_thread.start()

    def osc_default(self, addr: str, *args: Any) -> None:
        if not args:
            return

        parts = [p for p in addr.split("/") if p]

        if self.handle_circuit_input(parts, args):
            return

        value = args[0]

        try:
            fval = float(value)
        except Exception:
            return

        # /qmw/operator/global/density
        if len(parts) == 4 and parts[:3] == ["qmw", "operator", "global"]:
            key = parts[3]
            self.controls.global_values[key] = fval
            return

        # /qmw/operator/q/0/rx
        if len(parts) == 5 and parts[:3] == ["qmw", "operator", "q"]:
            q = int(parts[3])
            key = parts[4]
            if 0 <= q < N_QUBITS:
                self.controls.qubits[q][key] = fval
            return

        # /qmw/operator/ham/ZIII
        if len(parts) == 4 and parts[:3] == ["qmw", "operator", "ham"]:
            term = parts[3].upper()
            self.controls.ham[term] = fval
            return

        # /qmw/operator/corr/01/xx
        if len(parts) == 5 and parts[:3] == ["qmw", "operator", "corr"]:
            pair = parts[3]
            term = parts[4].lower()
            if pair not in self.controls.corr_targets:
                self.controls.corr_targets[pair] = {}
            self.controls.corr_targets[pair][term] = clamp(fval, -1.0, 1.0)
            return

        # Direct synth controls:
        # /qmw/pauli/f0 55
        # /qmw/pauli/amp 0.8
        # /qmw/pauli/rotation_scale 1.5
        # /qmw/pauli/ham_depth 0.75
        # /qmw/pauli/corr_mix 0.5
        if len(parts) == 3 and parts[:2] == ["qmw", "pauli"]:
            key = parts[2]
            if key == "f0":
                self.controls.f0 = max(0.001, fval)
            elif key == "amp":
                self.controls.master_amp = clamp01(fval)
            elif key == "rotation_scale":
                self.controls.rotation_scale = max(0.0, fval)
            elif key == "ham_depth":
                self.controls.ham_depth = max(0.0, fval)
            elif key == "corr_mix":
                self.controls.corr_mix = clamp01(fval)
            elif key == "freq_mod_depth":
                self.controls.freq_mod_depth = max(0.0, fval)
            elif key == "external_timeout":
                self.external_timeout = max(0.0, fval)
            return

        # /qmw/pauli/ratio/0 1.5
        if len(parts) == 4 and parts[:3] == ["qmw", "pauli", "ratio"]:
            q = int(parts[3])
            if 0 <= q < N_QUBITS:
                self.ratios[q] = max(0.001, fval)
            return

    @staticmethod
    def flatten_osc_values(args: Tuple[Any, ...]) -> List[Any]:
        if len(args) == 1 and isinstance(args[0], (list, tuple)):
            return list(args[0])
        return list(args)

    def handle_circuit_input(self, parts: List[str], args: Tuple[Any, ...]) -> bool:
        """
        Accept state geometry from qmw_circuit_builder_controller.py.

        When these messages arrive, the oscillator uses them as the current
        Bloch source. If they stop, it falls back to local operator evolution.
        """
        if len(parts) < 3 or parts[:2] != ["qmw", "circuit"]:
            return False

        now = time.perf_counter()

        # /qmw/circuit/q0/bloch x y z
        if len(parts) == 4 and parts[2].startswith("q") and parts[3] == "bloch":
            values = self.flatten_osc_values(args)
            try:
                q = int(parts[2][1:])
                x = float(values[0])
                y = float(values[1])
                z = float(values[2])
            except Exception:
                return True

            if 0 <= q < N_QUBITS:
                xyz = (clamp(x, -1.0, 1.0), clamp(y, -1.0, 1.0), clamp(z, -1.0, 1.0))
                self.external_bloch[q] = xyz
                self.qubits[q].set_from_bloch(*xyz)
                self.external_last_seen = now
            return True

        # /qmw/circuit/q0/entropy s
        if len(parts) == 4 and parts[2].startswith("q") and parts[3] == "entropy":
            try:
                q = int(parts[2][1:])
                value = float(args[0])
            except Exception:
                return True

            if 0 <= q < N_QUBITS:
                self.external_entropies[q] = clamp01(value)
                self.external_last_seen = now
            return True

        # /qmw/circuit/correlation/0_1 xx xy yx yy zz
        if len(parts) == 4 and parts[2] == "correlation":
            pair = parts[3].replace("_", "")
            values = self.flatten_osc_values(args)
            if len(pair) == 2 and len(values) >= 5:
                try:
                    xx, xy, yx, yy, zz = [float(v) for v in values[:5]]
                except Exception:
                    return True
                self.external_correlations[pair] = {
                    "xx": clamp(xx, -1.0, 1.0),
                    "xy": clamp(xy, -1.0, 1.0),
                    "yx": clamp(yx, -1.0, 1.0),
                    "yy": clamp(yy, -1.0, 1.0),
                    "zz": clamp(zz, -1.0, 1.0),
                }
                self.external_last_seen = now
            return True

        return False

    def using_external_state(self) -> bool:
        if self.external_last_seen <= 0.0:
            return False
        return (time.perf_counter() - self.external_last_seen) <= self.external_timeout

    # ---------------------------------------------------------------------
    # State evolution and measurement
    # ---------------------------------------------------------------------

    def local_ham(self, q: int, axis: str) -> float:
        if axis == "x":
            return self.controls.ham.get(LOCAL_X_TERMS[q], 0.0)
        if axis == "y":
            return self.controls.ham.get(LOCAL_Y_TERMS[q], 0.0)
        if axis == "z":
            return self.controls.ham.get(LOCAL_Z_TERMS[q], 0.0)
        return 0.0

    def evolve(self, dt: float) -> None:
        """
        Evolve local qubit states.

        The morpher provides smooth operator states, not one-shot gates.
        We interpret rx/ry/rz and Hamiltonian terms as continuous rotation fields.
        """

        if self.using_external_state():
            return

        density = self.controls.global_values.get("density", 0.5)
        noise = self.controls.global_values.get("noise", 0.0)
        mapping_depth = self.controls.global_values.get("mapping_depth", 0.85)

        rot_scale = self.controls.rotation_scale * (0.25 + 1.75 * mapping_depth)
        ham_depth = self.controls.ham_depth

        for q, qb in enumerate(self.qubits):
            qc = self.controls.qubits[q]

            # Center the morphed scene values so they become bidirectional rates.
            rx_scene = wrap_pi(qc.get("rx", 0.0) - math.pi / 2.0)
            ry_scene = wrap_pi(qc.get("ry", 0.0) - math.pi / 2.0)
            rz_scene = wrap_pi(qc.get("rz", 0.0) - math.pi)

            # Local Hamiltonian terms add an operator-field component.
            hx = self.local_ham(q, "x")
            hy = self.local_ham(q, "y")
            hz = self.local_ham(q, "z")

            # Small deterministic pseudo-noise derived from the current time-like phase.
            # Kept gentle; this is not the main musical source.
            n = noise * 0.05 * math.sin(time.perf_counter() * (0.71 + q * 0.13))

            dx = dt * rot_scale * (rx_scene + ham_depth * hx + n)
            dy = dt * rot_scale * (ry_scene + ham_depth * hy - n)
            dz = dt * rot_scale * (rz_scene + ham_depth * hz + density * 0.05)

            # Order matters slightly; this gives a noncommutative feeling.
            qb.rz(dz)
            qb.ry(dy)
            qb.rx(dx)

    def bloch_values(self) -> List[Tuple[float, float, float]]:
        local = [q.bloch() for q in self.qubits]
        if not self.using_external_state():
            return local
        return [
            self.external_bloch[q] if self.external_bloch[q] is not None else local[q]
            for q in range(N_QUBITS)
        ]

    def pauli_string_expectation(self, term: str, bloch: List[Tuple[float, float, float]]) -> float:
        """
        Product-state approximation for Pauli-string expectation.

        For v1, qubits are local complex states, so a Pauli string expectation is
        the product of each selected local axis expectation.

        Later v2 can replace this with a full 4-qubit state/density matrix.
        """
        term = term.upper()
        if len(term) != N_QUBITS:
            return 0.0

        val = 1.0
        for q, char in enumerate(term):
            x, y, z = bloch[q]
            if char == "I":
                continue
            if char == "X":
                val *= x
            elif char == "Y":
                val *= y
            elif char == "Z":
                val *= z
            else:
                return 0.0
        return clamp(val, -1.0, 1.0)

    def correlation_value(
        self,
        pair: str,
        term: str,
        bloch: List[Tuple[float, float, float]],
    ) -> float:
        q0 = int(pair[0])
        q1 = int(pair[1])
        x0, y0, z0 = bloch[q0]
        x1, y1, z1 = bloch[q1]

        local = {
            "xx": x0 * x1,
            "yy": y0 * y1,
            "zz": z0 * z1,
            "xy": x0 * y1,
            "yx": y0 * x1,
        }.get(term, 0.0)

        target = self.controls.corr_targets.get(pair, {}).get(term, 0.0)
        if self.using_external_state():
            target = self.external_correlations.get(pair, {}).get(term, target)
        mix = self.controls.corr_mix
        return clamp((1.0 - mix) * local + mix * target, -1.0, 1.0)

    def entropy(self) -> float:
        if self.using_external_state():
            vals = [value for value in self.external_entropies if value is not None]
            if vals:
                return sum(vals) / len(vals)
        vals = [shannon_binary(q.population_1()) for q in self.qubits]
        return sum(vals) / max(1, len(vals))

    # ---------------------------------------------------------------------
    # Mapping and OSC output
    # ---------------------------------------------------------------------

    def qubit_synth_params(
        self,
        q: int,
        x: float,
        y: float,
        z: float,
        dt: float,
    ) -> Dict[str, float]:
        g = self.controls.global_values
        qc = self.controls.qubits[q]

        density = g.get("density", 0.5)
        harmonicity = g.get("harmonicity", 0.75)
        inharmonicity = g.get("inharmonicity", 0.25)
        articulation = g.get("articulation", 0.4)
        spatial_spread = g.get("spatial_spread", 0.5)

        coherence = complex(0.5 * x, 0.5 * y)
        coherence_re = coherence.real
        coherence_im = coherence.imag
        coherence_amp = abs(coherence)
        coherence_phase = safe_atan2(coherence_im, coherence_re)
        phasor_re = x
        phasor_im = y
        phasor_amp = math.sqrt(x * x + y * y)
        phasor_phase = safe_atan2(phasor_im, phasor_re)

        previous_phase = self.previous_coherence_phases[q]
        if previous_phase is None or dt <= 0.0:
            dphase = 0.0
        else:
            dphase = phase_delta(previous_phase, coherence_phase) / dt
        self.previous_coherence_phases[q] = coherence_phase
        self.coherence_phase_velocities[q] = dphase

        amp_depth = qc.get("amp_depth", 0.8)
        phase_depth = qc.get("phase_depth", 0.8)
        bright_depth = qc.get("bright_depth", 0.6)
        pan_depth = qc.get("pan_depth", 0.7)

        amp = self.controls.master_amp * amp_depth * (0.15 + 0.85 * phasor_amp)
        amp *= 0.35 + 0.65 * density
        amp = clamp01(amp)

        # Harmonicity keeps pitch near ratio. Inharmonicity lets Z bend it.
        z_bend = self.controls.freq_mod_depth * inharmonicity * z
        freq = self.controls.f0 * self.ratios[q] * (2.0 ** z_bend)
        coherence_freq = dphase / (2.0 * math.pi)

        bright = clamp01(0.5 + 0.5 * z * bright_depth)
        phase = coherence_phase * phase_depth
        phase_norm = norm_phase_01(phase)

        # Phase-space panning: X/Y determine location, spread controls width.
        pan = 0.5 + 0.5 * spatial_spread * pan_depth * math.sin(coherence_phase)
        pan = clamp01(pan)

        # Low-rate oscillator preview. Max should render this at audio rate, but
        # the sample is useful for scopes, meters, and sanity checks.
        previous_carrier = self.carrier_phases[q]
        self.carrier_phases[q] = (previous_carrier + 2.0 * math.pi * freq * dt) % (2.0 * math.pi)
        trig = self.previous_carrier_phases[q] is not None and self.carrier_phases[q] < previous_carrier
        self.previous_carrier_phases[q] = self.carrier_phases[q]

        dur_ms = 25.0 + 275.0 * clamp01(1.0 - articulation + 0.25 * amp)
        now = time.perf_counter()
        if trig:
            self.gate_until[q] = now + dur_ms / 1000.0
        gate = 1.0 if now <= self.gate_until[q] else 0.0
        velocity = clamp01(amp)
        accent = clamp01(0.35 * abs(z) + 0.45 * phasor_amp + 0.20 * min(1.0, abs(dphase) / (2.0 * math.pi * 8.0)))
        probability = clamp01(0.60 * velocity + 0.40 * accent)

        audio_phase = (self.carrier_phases[q] + phase) % (2.0 * math.pi)
        sample = amp * math.cos(audio_phase)

        # Harmonicity can be used in Max to crossfade harmonic/inharmonic banks.
        harmonic_weight = clamp01(harmonicity * (1.0 - abs(z) * 0.2))

        return {
            "coherence_re": coherence_re,
            "coherence_im": coherence_im,
            "coherence_amp": coherence_amp,
            "coherence_phase": coherence_phase,
            "coherence_phase_norm": norm_phase_01(coherence_phase),
            "coherence_dphase": dphase,
            "coherence_freq": coherence_freq,
            "phasor_re": phasor_re,
            "phasor_im": phasor_im,
            "amp": amp,
            "phase": phase,
            "phase_norm": phase_norm,
            "freq": freq,
            "bright": bright,
            "pan": pan,
            "audio_phase": audio_phase,
            "audio_phase_norm": norm_phase_01(audio_phase),
            "sample": sample,
            "trig": float(trig),
            "gate": gate,
            "probability": probability,
            "velocity": velocity,
            "accent": accent,
            "dur_ms": dur_ms,
            "phasor_amp": phasor_amp,
            "phasor_phase": phasor_phase,
            "harmonic_weight": harmonic_weight,
        }

    def send_outputs(self, dt: float) -> None:
        bloch = self.bloch_values()
        entropy = self.entropy()
        self.frame_count += 1
        send_strings = (self.frame_count % max(1, self.string_divider)) == 0

        self.send("/qmw/pauli/global/entropy", float(entropy))
        self.send("/qmw/entropy", float(entropy))
        self.send("/qmw/source/external_circuit", int(self.using_external_state()))
        for key, value in self.controls.global_values.items():
            self.send(f"/qmw/pauli/global/{key}", float(value))

        self.send("/qmw/pauli/f0", float(self.controls.f0))
        self.send("/qmw/f0", float(self.controls.f0))

        triggered_voices: List[int] = []
        articulation_energy = 0.0

        for q, (x, y, z) in enumerate(bloch):
            params = self.qubit_synth_params(q, x, y, z, dt)
            articulation_energy += params["accent"]

            self.send(f"/qmw/pauli/q/{q}/x", float(x))
            self.send(f"/qmw/pauli/q/{q}/y", float(y))
            self.send(f"/qmw/pauli/q/{q}/z", float(z))
            self.send(f"/qmw/pauli/q/{q}/alpha_re", float(self.qubits[q].alpha.real))
            self.send(f"/qmw/pauli/q/{q}/alpha_im", float(self.qubits[q].alpha.imag))
            self.send(f"/qmw/pauli/q/{q}/beta_re", float(self.qubits[q].beta.real))
            self.send(f"/qmw/pauli/q/{q}/beta_im", float(self.qubits[q].beta.imag))

            qaddr = f"/qmw/q{q}"
            self.send(f"{qaddr}/x", float(x))
            self.send(f"{qaddr}/y", float(y))
            self.send(f"{qaddr}/z", float(z))
            self.send(f"{qaddr}/polarity", float(z))
            self.send(f"{qaddr}/alpha/re", float(self.qubits[q].alpha.real))
            self.send(f"{qaddr}/alpha/im", float(self.qubits[q].alpha.imag))
            self.send(f"{qaddr}/beta/re", float(self.qubits[q].beta.real))
            self.send(f"{qaddr}/beta/im", float(self.qubits[q].beta.imag))

            for key, value in params.items():
                self.send(f"/qmw/pauli/q/{q}/{key}", float(value))

            self.send(f"{qaddr}/coherence/re", float(params["coherence_re"]))
            self.send(f"{qaddr}/coherence/im", float(params["coherence_im"]))
            self.send(f"{qaddr}/coherence/amp", float(params["coherence_amp"]))
            self.send(f"{qaddr}/coherence/phase", float(params["coherence_phase"]))
            self.send(f"{qaddr}/coherence/phase_norm", float(params["coherence_phase_norm"]))
            self.send(f"{qaddr}/coherence/dphase", float(params["coherence_dphase"]))
            self.send(f"{qaddr}/coherence/freq", float(params["coherence_freq"]))
            self.send(f"{qaddr}/phasor/re", float(params["phasor_re"]))
            self.send(f"{qaddr}/phasor/im", float(params["phasor_im"]))
            self.send(f"{qaddr}/phasor/amp", float(params["phasor_amp"]))
            self.send(f"{qaddr}/phasor/phase", float(params["phasor_phase"]))
            self.send(f"{qaddr}/amp", float(params["amp"]))
            self.send(f"{qaddr}/phase", float(params["phase_norm"]))
            self.send(f"{qaddr}/phase_rad", float(params["phase"]))
            self.send(f"{qaddr}/freq", float(params["freq"]))
            self.send(f"{qaddr}/audio_phase", float(params["audio_phase_norm"]))
            self.send(f"{qaddr}/audio_phase_rad", float(params["audio_phase"]))
            self.send(f"{qaddr}/sample", float(params["sample"]))
            self.send(f"{qaddr}/brightness", float(params["bright"]))
            self.send(f"{qaddr}/bright", float(params["bright"]))
            self.send(f"{qaddr}/pan", float(params["pan"]))
            self.send(f"{qaddr}/harmonic_weight", float(params["harmonic_weight"]))

            if params["trig"] > 0.0:
                triggered_voices.append(q)
                self.send(f"/qmw/time/q/{q}/trig", 1)
            self.send(f"/qmw/time/q/{q}/gate", float(params["gate"]))
            self.send(f"/qmw/time/q/{q}/probability", float(params["probability"]))
            self.send(f"/qmw/time/q/{q}/velocity", float(params["velocity"]))
            self.send(f"/qmw/time/q/{q}/accent", float(params["accent"]))
            self.send(f"/qmw/time/q/{q}/dur_ms", float(params["dur_ms"]))

       
            if send_strings:
                    active_terms = set(DEFAULT_STRING_TERMS) | set(self.controls.ham.keys())
                    for term in sorted(active_terms):
                        if len(term) == N_QUBITS and all(c in "IXYZ" for c in term.upper()):
                            value = self.pauli_string_expectation(term, bloch)
                            self.send(f"/qmw/pauli/string/{term.upper()}", float(value))
                    
        # Pairwise correlations.
        for pair in CORR_PAIRS:
            q0 = pair[0]
            q1 = pair[1]
            if pair not in self.previous_corr_values:
                self.previous_corr_values[pair] = {}
            for term in CORR_TERMS:
                value = self.correlation_value(pair, term, bloch)
                self.send(f"/qmw/pauli/corr/{pair}/{term}", float(value))
                self.send(f"/qmw/corr/{q0}/{q1}/{term}", float(value))
                previous = self.previous_corr_values[pair].get(term, value)
                if abs(previous) < 0.65 <= abs(value):
                    self.send(f"/qmw/time/corr/{pair}/trig", 1)
                    self.send(f"/qmw/time/corr/{q0}/{q1}/trig", 1)
                    self.send(f"/qmw/time/corr/{pair}/term/{term}", float(value))
                self.previous_corr_values[pair][term] = value

        # Useful macro values.
        z_abs_avg = sum(abs(v[2]) for v in bloch) / N_QUBITS
        xy_avg = sum(math.sqrt(v[0] * v[0] + v[1] * v[1]) for v in bloch) / N_QUBITS
        articulation_energy /= N_QUBITS

        for voice in triggered_voices:
            self.last_grain_voice = voice
            self.send("/qmw/time/grain/trig", 1)
            self.send("/qmw/time/grain/voice", int(voice))

        if self.previous_articulation_energy < 0.55 <= articulation_energy:
            self.send("/qmw/time/articulation/trig", 1)
        self.previous_articulation_energy = articulation_energy
        self.send("/qmw/time/articulation/energy", float(articulation_energy))

        self.send("/qmw/pauli/macro/population_polarity", float(z_abs_avg))
        self.send("/qmw/pauli/macro/coherence", float(xy_avg))
        self.send("/qmw/pauli/macro/noisiness", float(clamp01(entropy + self.controls.global_values.get("noise", 0.0) * 0.5)))
        self.send("/qmw/macro/population_polarity", float(z_abs_avg))
        self.send("/qmw/macro/coherence", float(xy_avg))
        self.send("/qmw/macro/noisiness", float(clamp01(entropy + self.controls.global_values.get("noise", 0.0) * 0.5)))

    def run(self) -> None:
        self.setup_server()

        print(
            "QMW Complex Pauli Synth v1 running\n"
            f"  OSC in:   0.0.0.0:{self.osc_in_port}\n"
            f"  OSC out:  {self.osc_host}:{self.osc_out_port}\n"
            f"  rate:     {self.rate_hz:.1f} Hz\n"
            f"  f0:       {self.controls.f0:.3f} Hz\n"
            f"  ratios:   {self.ratios}\n"
            "Ctrl-C to stop."
        )

        dt = 1.0 / max(1.0, self.rate_hz)
        next_time = time.perf_counter()

        while self.running:
            now = time.perf_counter()
            if now < next_time:
                time.sleep(max(0.0, next_time - now))
                continue

            # Keep time stable even if a frame arrives late.
            next_time += dt

            self.evolve(dt)
            self.send_outputs(dt)

    def stop(self) -> None:
        self.running = False
        if self.server is not None:
            self.server.shutdown()
            self.server.server_close()


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="QMW Complex Pauli Synth v1: Bloch/Pauli phasor synth-control engine."
    )
    parser.add_argument("--host", default="127.0.0.1", help="OSC output host")
    parser.add_argument("--out-port", type=int, default=7403, help="OSC output port to Max")
    parser.add_argument("--in-port", type=int, default=7410, help="OSC input port from morpher")
    parser.add_argument("--rate", type=float, default=120.0, help="control output rate in Hz")
    parser.add_argument("--f0", type=float, default=41.2, help="fundamental frequency")
    parser.add_argument(
        "--ratios",
        default="1,1.25,1.5,1.75",
        help="comma-separated ratios for q0-q3, e.g. 1,1.25,1.5,1.75",
    )
    parser.add_argument("--string-divider", type=int, default=1, help="divider for string outputs")
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> None:
    args = parse_args(argv)

    ratios = [float(x.strip()) for x in args.ratios.split(",") if x.strip()]
    while len(ratios) < N_QUBITS:
        ratios.append(DEFAULT_RATIOS[len(ratios)])
    ratios = ratios[:N_QUBITS]

    synth = ComplexPauliSynth(
        osc_host=args.host,
        osc_out_port=args.out_port,
        osc_in_port=args.in_port,
        rate_hz=args.rate,
    )

    synth.string_divider = max(1, int(args.string_divider))
    synth.controls.f0 = args.f0
    synth.ratios = ratios

    def handle_stop(signum: int, frame: Any) -> None:
        print("\nStopping QMW Complex Pauli Synth...")
        synth.stop()

    signal.signal(signal.SIGINT, handle_stop)
    signal.signal(signal.SIGTERM, handle_stop)

    synth.run()


if __name__ == "__main__":
    main()
