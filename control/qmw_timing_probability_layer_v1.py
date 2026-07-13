#!/usr/bin/env python3
"""
qmw_timing_probability_layer_v1.py

Quantum Material Workbench
Timing + Probability Layer for Quantum Parametric Composition.

Purpose
-------
Receives continuous Pauli/Bloch synthesis-control streams from
qmw_complex_pauli_synth_v1.py and converts them into musical event streams:

    - probabilistic triggers
    - gates
    - accents
    - durations
    - grain clocks
    - articulation events
    - correlation/pair events
    - optional morpher advance commands

It also passes the continuous Pauli streams through to Max, so Max can listen
to this layer as the final OSC source.

Recommended chain
-----------------
Terminal 1:
    python control/qmw_operator_preset_morpher_v1.py --out-port 7410 --in-port 7404

Terminal 2:
    python synth/qmw_complex_pauli_synth_v1.py --in-port 7410 --out-port 7420

Terminal 3:
    python control/qmw_timing_probability_layer_v1.py --in-port 7420 --out-port 7403 --morph-port 7404 --mode prob

Max:
    udpreceive 7403

Dependency
----------
    pip install python-osc

Core principle
--------------
The clock does not trigger sound directly.
The clock tests probability fields derived from Pauli/Bloch data.

Continuous Pauli data:
    x, y, z, amp, phase, bright, entropy, coherence

becomes event behavior:
    rhythm, grain density, articulation, accents, gates, morphing.
"""

from __future__ import annotations

import argparse
import math
import random
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
CORR_PAIRS = ["01", "02", "03", "12", "13", "23"]
CORR_TERMS = ["xx", "yy", "zz", "xy", "yx"]


def clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, float(x)))


def clamp01(x: float) -> float:
    return clamp(x, 0.0, 1.0)


def lerp(a: float, b: float, t: float) -> float:
    return (1.0 - t) * a + t * b


def prob_from_rate(rate_hz: float, dt: float) -> float:
    """
    Convert a continuous event rate into a per-frame probability.

        p = 1 - exp(-lambda * dt)

    where lambda is events per second.
    """
    rate_hz = max(0.0, float(rate_hz))
    return clamp01(1.0 - math.exp(-rate_hz * dt))


@dataclass
class LaneClock:
    name: str
    interval_ms: float
    probability_bias: float = 1.0
    enabled: bool = True
    elapsed_ms: float = 0.0
    gate_remaining_ms: float = 0.0
    counter: int = 0

    def tick(self, dt_ms: float) -> bool:
        if not self.enabled:
            return False

        self.elapsed_ms += dt_ms

        if self.elapsed_ms >= self.interval_ms:
            self.elapsed_ms %= max(1.0, self.interval_ms)
            self.counter += 1
            return True

        return False

    def update_gate(self, dt_ms: float) -> int:
        if self.gate_remaining_ms > 0.0:
            self.gate_remaining_ms = max(0.0, self.gate_remaining_ms - dt_ms)
            return 1
        return 0

    def open_gate(self, duration_ms: float) -> None:
        self.gate_remaining_ms = max(self.gate_remaining_ms, max(1.0, duration_ms))


@dataclass
class PauliSnapshot:
    global_values: Dict[str, float] = field(default_factory=lambda: {
        "density": 0.5,
        "entropy": 0.0,
        "entropy_bias": 0.5,
        "noise": 0.0,
        "harmonicity": 0.75,
        "inharmonicity": 0.25,
        "articulation": 0.4,
        "spatial_spread": 0.5,
        "mapping_depth": 0.85,
    })

    macro_values: Dict[str, float] = field(default_factory=lambda: {
        "coherence": 0.0,
        "noisiness": 0.0,
        "population_polarity": 0.0,
    })

    qubits: List[Dict[str, float]] = field(default_factory=lambda: [
        {
            "x": 0.0,
            "y": 0.0,
            "z": 1.0,
            "amp": 0.0,
            "phase_norm": 0.0,
            "freq": 55.0,
            "bright": 0.5,
            "pan": 0.5,
            "phasor_amp": 0.0,
            "harmonic_weight": 0.75,
        }
        for _ in range(N_QUBITS)
    ])

    corr: Dict[str, Dict[str, float]] = field(default_factory=lambda: {
        pair: {term: 0.0 for term in CORR_TERMS} for pair in CORR_PAIRS
    })

    strings: Dict[str, float] = field(default_factory=dict)


@dataclass
class TimingProbabilityLayer:
    osc_host: str = "127.0.0.1"
    osc_in_port: int = 7420
    osc_out_port: int = 7403
    morph_host: str = "127.0.0.1"
    morph_port: int = 7404
    rate_hz: float = 120.0

    mode: str = "prob"  # fixed, prob, hybrid, off
    pass_through: bool = True
    running: bool = True

    probability_scale: float = 1.0
    density_weight: float = 0.35
    entropy_weight: float = 0.25
    coherence_weight: float = 0.25
    articulation_weight: float = 0.15

    min_grain_rate_hz: float = 0.5
    max_grain_rate_hz: float = 45.0

    auto_morph_enabled: bool = False
    morph_interval_ms: float = 2000.0
    morph_probability_bias: float = 0.35
    morph_elapsed_ms: float = 0.0

    snapshot: PauliSnapshot = field(default_factory=PauliSnapshot)
    lanes: Dict[str, LaneClock] = field(default_factory=dict)

    previous_phase_norm: List[float] = field(default_factory=lambda: [0.0 for _ in range(N_QUBITS)])
    previous_z: List[float] = field(default_factory=lambda: [1.0 for _ in range(N_QUBITS)])
    previous_coherence: float = 0.0
    event_counter: int = 0

    lock: threading.RLock = field(default_factory=threading.RLock)

    def __post_init__(self) -> None:
        self.client = SimpleUDPClient(self.osc_host, self.osc_out_port)
        self.morph_client = SimpleUDPClient(self.morph_host, self.morph_port)
        self.server: Optional[ThreadingOSCUDPServer] = None
        self._server_thread: Optional[threading.Thread] = None

        if not self.lanes:
            self.lanes = self.make_default_lanes()

    def make_default_lanes(self) -> Dict[str, LaneClock]:
        """
        Incommensurate-ish defaults so the layer does not collapse into a
        simple 16-step drum-machine grid.
        """
        return {
            "q0": LaneClock("q0", interval_ms=230.0, probability_bias=0.85),
            "q1": LaneClock("q1", interval_ms=310.0, probability_bias=0.75),
            "q2": LaneClock("q2", interval_ms=430.0, probability_bias=0.65),
            "q3": LaneClock("q3", interval_ms=590.0, probability_bias=0.55),
            "grain": LaneClock("grain", interval_ms=50.0, probability_bias=1.0),
            "corr": LaneClock("corr", interval_ms=700.0, probability_bias=0.65),
            "articulation": LaneClock("articulation", interval_ms=370.0, probability_bias=0.7),
        }

    # ------------------------------------------------------------------
    # OSC send helpers
    # ------------------------------------------------------------------

    def send(self, addr: str, *values: Any) -> None:
        try:
            if len(values) == 0:
                self.client.send_message(addr, 1)
            elif len(values) == 1:
                self.client.send_message(addr, values[0])
            else:
                self.client.send_message(addr, list(values))
        except Exception as exc:
            print(f"OSC send error {addr}: {exc}", file=sys.stderr)

    def send_morph(self, addr: str, *values: Any) -> None:
        try:
            if len(values) == 0:
                self.morph_client.send_message(addr, 1)
            elif len(values) == 1:
                self.morph_client.send_message(addr, values[0])
            else:
                self.morph_client.send_message(addr, list(values))
        except Exception as exc:
            print(f"OSC morph send error {addr}: {exc}", file=sys.stderr)

    def pass_message(self, addr: str, *args: Any) -> None:
        if not self.pass_through:
            return
        if not addr.startswith("/qmw/"):
            return
        if addr.startswith("/qmw/time/control/"):
            return

        try:
            if len(args) == 0:
                return
            if len(args) == 1:
                self.client.send_message(addr, args[0])
            else:
                self.client.send_message(addr, list(args))
        except Exception as exc:
            print(f"OSC pass-through error {addr}: {exc}", file=sys.stderr)

    # ------------------------------------------------------------------
    # OSC input
    # ------------------------------------------------------------------

    def setup_server(self) -> None:
        dispatcher = Dispatcher()
        dispatcher.set_default_handler(self.osc_default)
        self.server = ThreadingOSCUDPServer(("0.0.0.0", self.osc_in_port), dispatcher)
        self.server.timeout = 0.1
        self._server_thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self._server_thread.start()

    def osc_default(self, addr: str, *args: Any) -> None:
        if addr.startswith("/qmw/time/control/"):
            self.handle_control(addr, *args)
            return

        self.parse_pauli_message(addr, *args)
        self.pass_message(addr, *args)

    def handle_control(self, addr: str, *args: Any) -> None:
        parts = [p for p in addr.split("/") if p]

        # /qmw/time/control/mode prob
        if len(parts) == 4 and parts[3] == "mode" and args:
            mode = str(args[0]).lower()
            if mode in {"fixed", "prob", "hybrid", "off"}:
                self.mode = mode
                print(f"timing mode = {self.mode}")
            return

        # /qmw/time/control/pass 1
        if len(parts) == 4 and parts[3] == "pass" and args:
            self.pass_through = bool(int(float(args[0])))
            return

        # /qmw/time/control/prob_scale 0.8
        if len(parts) == 4 and parts[3] == "prob_scale" and args:
            self.probability_scale = max(0.0, float(args[0]))
            return

        # /qmw/time/control/grain_rate 0.5 60
        if len(parts) == 4 and parts[3] == "grain_rate" and len(args) >= 2:
            self.min_grain_rate_hz = max(0.0, float(args[0]))
            self.max_grain_rate_hz = max(self.min_grain_rate_hz, float(args[1]))
            return

        # /qmw/time/control/lane q0 interval 333
        # /qmw/time/control/lane q1 prob 0.7
        # /qmw/time/control/lane grain enable 0
        if len(parts) == 4 and parts[3] == "lane" and len(args) >= 3:
            lane_name = str(args[0])
            param = str(args[1]).lower()
            value = args[2]

            if lane_name in self.lanes:
                lane = self.lanes[lane_name]

                if param == "interval":
                    lane.interval_ms = max(1.0, float(value))
                elif param == "prob":
                    lane.probability_bias = max(0.0, float(value))
                elif param == "enable":
                    lane.enabled = bool(int(float(value)))

            return

        # /qmw/time/control/morph enable 1
        # /qmw/time/control/morph interval 3000
        # /qmw/time/control/morph prob 0.45
        if len(parts) == 4 and parts[3] == "morph" and len(args) >= 2:
            param = str(args[0]).lower()
            value = args[1]

            if param == "enable":
                self.auto_morph_enabled = bool(int(float(value)))
            elif param == "interval":
                self.morph_interval_ms = max(1.0, float(value))
            elif param == "prob":
                self.morph_probability_bias = clamp01(float(value))

            return

        # /qmw/time/control/seed 1234
        if len(parts) == 4 and parts[3] == "seed" and args:
            random.seed(int(float(args[0])))
            return

        # /qmw/time/control/reset
        if len(parts) == 4 and parts[3] == "reset":
            self.reset()
            return

    def parse_pauli_message(self, addr: str, *args: Any) -> None:
        if not args:
            return

        try:
            value = float(args[0])
        except Exception:
            return

        parts = [p for p in addr.split("/") if p]

        with self.lock:
            # /qmw/pauli/global/entropy
            if len(parts) == 4 and parts[:3] == ["qmw", "pauli", "global"]:
                self.snapshot.global_values[parts[3]] = value
                return

            # /qmw/pauli/macro/coherence
            if len(parts) == 4 and parts[:3] == ["qmw", "pauli", "macro"]:
                self.snapshot.macro_values[parts[3]] = value
                return

            # /qmw/pauli/q/0/amp
            if len(parts) == 5 and parts[:3] == ["qmw", "pauli", "q"]:
                try:
                    q = int(parts[3])
                except ValueError:
                    return

                key = parts[4]
                if 0 <= q < N_QUBITS:
                    self.snapshot.qubits[q][key] = value
                return

            # /qmw/pauli/corr/01/zz
            if len(parts) == 5 and parts[:3] == ["qmw", "pauli", "corr"]:
                pair = parts[3]
                term = parts[4]

                if pair not in self.snapshot.corr:
                    self.snapshot.corr[pair] = {}

                self.snapshot.corr[pair][term] = value
                return

            # /qmw/pauli/string/XXXX
            if len(parts) == 4 and parts[:3] == ["qmw", "pauli", "string"]:
                self.snapshot.strings[parts[3]] = value
                return

    # ------------------------------------------------------------------
    # Probability model
    # ------------------------------------------------------------------

    def base_probability(self, q: int) -> float:
        g = self.snapshot.global_values
        m = self.snapshot.macro_values
        qd = self.snapshot.qubits[q]

        density = clamp01(g.get("density", 0.5))
        entropy = clamp01(g.get("entropy", g.get("entropy_bias", 0.0)))
        coherence = clamp01(m.get("coherence", 0.0))
        articulation = clamp01(g.get("articulation", 0.4))
        amp = clamp01(qd.get("amp", 0.0))
        bright = clamp01(qd.get("bright", 0.5))
        z = abs(clamp(qd.get("z", 0.0), -1.0, 1.0))

        p = (
            self.density_weight * density
            + self.entropy_weight * entropy
            + self.coherence_weight * coherence
            + self.articulation_weight * articulation
        )

        p *= 0.35 + 0.65 * amp
        p *= 0.85 + 0.30 * bright
        p *= 1.0 - 0.25 * z

        lane = self.lanes[f"q{q}"]
        p *= lane.probability_bias
        p *= self.probability_scale

        return clamp01(p)

    def grain_probability_per_frame(self, dt: float) -> float:
        g = self.snapshot.global_values
        m = self.snapshot.macro_values

        density = clamp01(g.get("density", 0.5))
        entropy = clamp01(g.get("entropy", g.get("entropy_bias", 0.0)))
        noisiness = clamp01(m.get("noisiness", 0.0))
        articulation = clamp01(g.get("articulation", 0.4))

        field = clamp01(
            0.45 * density
            + 0.30 * entropy
            + 0.20 * noisiness
            + 0.05 * articulation
        )

        rate_hz = lerp(self.min_grain_rate_hz, self.max_grain_rate_hz, field)
        return prob_from_rate(rate_hz, dt)

    def strongest_correlation(self) -> Tuple[str, str, float]:
        best_pair = "01"
        best_term = "zz"
        best_value = 0.0

        for pair, terms in self.snapshot.corr.items():
            for term, value in terms.items():
                if abs(value) > abs(best_value):
                    best_pair = pair
                    best_term = term
                    best_value = value

        return best_pair, best_term, best_value

    # ------------------------------------------------------------------
    # Event emission
    # ------------------------------------------------------------------

    def trigger_qubit(self, q: int, probability: float, source: str = "clock") -> None:
        qd = self.snapshot.qubits[q]
        g = self.snapshot.global_values
        m = self.snapshot.macro_values

        amp = clamp01(qd.get("amp", 0.0))
        bright = clamp01(qd.get("bright", 0.5))
        z = clamp(qd.get("z", 0.0), -1.0, 1.0)
        coherence = clamp01(m.get("coherence", 0.0))
        density = clamp01(g.get("density", 0.5))
        articulation = clamp01(g.get("articulation", 0.4))
        noisiness = clamp01(m.get("noisiness", 0.0))

        velocity = clamp01(0.10 + 0.65 * amp + 0.25 * probability)
        accent = clamp01(0.25 * articulation + 0.35 * abs(z) + 0.40 * amp)

        # Dense/noisy fields produce shorter gestures; coherent fields sustain.
        dur_ms = lerp(40.0, 900.0, clamp01(0.55 * coherence + 0.45 * (1.0 - density)))
        dur_ms *= lerp(1.15, 0.45, noisiness)
        dur_ms = max(10.0, dur_ms)

        lane = self.lanes[f"q{q}"]
        lane.open_gate(dur_ms)

        self.event_counter += 1

        self.send(f"/qmw/time/q/{q}/trig", 1)
        self.send(f"/qmw/time/q/{q}/source", source)
        self.send(f"/qmw/time/q/{q}/event_index", self.event_counter)
        self.send(f"/qmw/time/q/{q}/prob", float(probability))
        self.send(f"/qmw/time/q/{q}/probability", float(probability))
        self.send(f"/qmw/time/q/{q}/velocity", float(velocity))
        self.send(f"/qmw/time/q/{q}/accent", float(accent))
        self.send(f"/qmw/time/q/{q}/dur_ms", float(dur_ms))
        self.send(f"/qmw/time/q/{q}/bright", float(bright))

    def trigger_grain(self, probability: float) -> None:
        g = self.snapshot.global_values
        m = self.snapshot.macro_values

        density = clamp01(g.get("density", 0.5))
        entropy = clamp01(g.get("entropy", g.get("entropy_bias", 0.0)))
        noisiness = clamp01(m.get("noisiness", 0.0))
        coherence = clamp01(m.get("coherence", 0.0))

        amps = [clamp01(q.get("amp", 0.0)) + 0.01 for q in self.snapshot.qubits]
        total = sum(amps)
        r = random.random() * total
        acc = 0.0
        voice = 0

        for i, a in enumerate(amps):
            acc += a
            if r <= acc:
                voice = i
                break

        grain_dur_ms = lerp(15.0, 260.0, clamp01(0.65 * coherence + 0.35 * (1.0 - noisiness)))
        grain_rate = lerp(self.min_grain_rate_hz, self.max_grain_rate_hz, density)

        self.send("/qmw/time/grain/trig", 1)
        self.send("/qmw/time/grain/voice", int(voice))
        self.send("/qmw/time/grain/prob", float(probability))
        self.send("/qmw/time/grain/density", float(density))
        self.send("/qmw/time/grain/entropy", float(entropy))
        self.send("/qmw/time/grain/noisiness", float(noisiness))
        self.send("/qmw/time/grain/dur_ms", float(grain_dur_ms))
        self.send("/qmw/time/grain/rate_hz", float(grain_rate))

    def trigger_correlation(self, source: str = "clock") -> None:
        pair, term, value = self.strongest_correlation()
        probability = clamp01(abs(value) * self.lanes["corr"].probability_bias * self.probability_scale)

        if self.mode == "fixed" or random.random() < probability:
            self.send(f"/qmw/time/corr/{pair}/trig", 1)
            self.send(f"/qmw/time/corr/{pair}/term", term)
            self.send(f"/qmw/time/corr/{pair}/value", float(value))
            self.send(f"/qmw/time/corr/{pair}/prob", float(probability))
            self.send(f"/qmw/time/corr/{pair}/source", source)

    def trigger_articulation(self, source: str = "clock") -> None:
        g = self.snapshot.global_values
        m = self.snapshot.macro_values

        articulation = clamp01(g.get("articulation", 0.4))
        coherence = clamp01(m.get("coherence", 0.0))
        noisiness = clamp01(m.get("noisiness", 0.0))

        p = clamp01((0.5 * articulation + 0.3 * coherence + 0.2 * noisiness) * self.probability_scale)

        if self.mode == "fixed" or random.random() < p:
            self.send("/qmw/time/articulation/trig", 1)
            self.send("/qmw/time/articulation/prob", float(p))
            self.send("/qmw/time/articulation/coherence", float(coherence))
            self.send("/qmw/time/articulation/noisiness", float(noisiness))
            self.send("/qmw/time/articulation/source", source)

    def maybe_advance_morpher(self, dt_ms: float) -> None:
        if not self.auto_morph_enabled:
            return

        self.morph_elapsed_ms += dt_ms

        if self.morph_elapsed_ms < self.morph_interval_ms:
            return

        self.morph_elapsed_ms %= self.morph_interval_ms

        g = self.snapshot.global_values
        m = self.snapshot.macro_values

        entropy = clamp01(g.get("entropy", g.get("entropy_bias", 0.0)))
        coherence = clamp01(m.get("coherence", 0.0))
        noisiness = clamp01(m.get("noisiness", 0.0))

        p = clamp01(
            self.morph_probability_bias
            * self.probability_scale
            * (0.40 + 0.30 * entropy + 0.20 * noisiness + 0.10 * coherence)
        )

        if self.mode == "fixed" or random.random() < p:
            self.send("/qmw/time/morph/advance", 1)
            self.send("/qmw/time/morph/prob", float(p))
            self.send_morph("/qmw/morpher/advance", 1)

    # ------------------------------------------------------------------
    # Threshold and phase-derived events
    # ------------------------------------------------------------------

    def detect_threshold_events(self) -> None:
        coherence = clamp01(self.snapshot.macro_values.get("coherence", 0.0))

        # Coherence threshold crossing.
        if self.previous_coherence < 0.72 <= coherence:
            self.send("/qmw/time/coherence/cross_high", 1)
            self.send("/qmw/time/coherence/value", float(coherence))
            self.trigger_articulation(source="coherence_cross")

        self.previous_coherence = coherence

        for q in range(N_QUBITS):
            qd = self.snapshot.qubits[q]
            phase = clamp01(qd.get("phase_norm", 0.0))
            z = clamp(qd.get("z", 0.0), -1.0, 1.0)

            prev_phase = self.previous_phase_norm[q]
            prev_z = self.previous_z[q]

            # Phase wrap: useful for articulation that follows the Bloch phasor.
            if prev_phase > 0.80 and phase < 0.20:
                p = self.base_probability(q)
                if self.mode in {"fixed", "hybrid"} or random.random() < p:
                    self.trigger_qubit(q, p, source="phase_wrap")

            # Z zero-crossing: population-polarity articulation.
            if (prev_z < 0.0 <= z) or (prev_z > 0.0 >= z):
                p = clamp01(self.base_probability(q) * 0.75)
                if self.mode in {"fixed", "hybrid"} or random.random() < p:
                    self.trigger_qubit(q, p, source="z_cross")

            self.previous_phase_norm[q] = phase
            self.previous_z[q] = z

    # ------------------------------------------------------------------
    # Main timing loop
    # ------------------------------------------------------------------

    def update_lanes(self, dt: float) -> None:
        dt_ms = dt * 1000.0

        with self.lock:
            if self.mode == "off":
                return

            # Clocked qubit lanes.
            for q in range(N_QUBITS):
                lane = self.lanes[f"q{q}"]
                gate = lane.update_gate(dt_ms)
                self.send(f"/qmw/time/q/{q}/gate", int(gate))

                p = self.base_probability(q)

                # Continuous probability monitor for Max.
                self.send(f"/qmw/time/q/{q}/prob_current", float(p))
                self.send(f"/qmw/time/q/{q}/probability_current", float(p))

                # Also send /prob continuously so Max can use one address
                # whether or not a trigger has happened.
                self.send(f"/qmw/time/q/{q}/prob", float(p))
                self.send(f"/qmw/time/q/{q}/probability", float(p))

                # Bundled state packet:
                # probability, gate, amp, z
                self.send(
                    f"/qmw/time/q/{q}/state",
                    float(p),
                    int(gate),
                    float(self.snapshot.qubits[q].get("amp", 0.0)),
                    float(self.snapshot.qubits[q].get("z", 0.0)),
                )

                if lane.tick(dt_ms):
                    self.send(f"/qmw/time/lane/q{q}/tick", int(lane.counter))

                    if self.mode == "fixed":
                        self.trigger_qubit(q, p, source="fixed_clock")
                    elif self.mode in {"prob", "hybrid"}:
                        if random.random() < p:
                            self.trigger_qubit(q, p, source="prob_clock")

            # Grain Poisson process.
            self.lanes["grain"].update_gate(dt_ms)
            grain_p = self.grain_probability_per_frame(dt)
            self.send("/qmw/time/grain/prob_current", float(grain_p))

            if self.lanes["grain"].enabled and random.random() < grain_p:
                self.trigger_grain(grain_p)

            # Correlation lane.
            if self.lanes["corr"].tick(dt_ms):
                self.send("/qmw/time/lane/corr/tick", int(self.lanes["corr"].counter))
                self.trigger_correlation(source="corr_clock")

            # Articulation lane.
            if self.lanes["articulation"].tick(dt_ms):
                self.send(
                    "/qmw/time/lane/articulation/tick",
                    int(self.lanes["articulation"].counter),
                )
                self.trigger_articulation(source="articulation_clock")

            # Threshold events.
            self.detect_threshold_events()

            # Optional feedback to morpher.
            self.maybe_advance_morpher(dt_ms)

            # Global time values useful in Max.
            self.send_global_state()

    def send_global_state(self) -> None:
        g = self.snapshot.global_values
        m = self.snapshot.macro_values

        self.send("/qmw/time/mode", self.mode)
        self.send("/qmw/time/probability_scale", float(self.probability_scale))
        self.send("/qmw/time/pass_through", int(self.pass_through))
        self.send("/qmw/time/auto_morph_enabled", int(self.auto_morph_enabled))

        self.send("/qmw/time/global/density", float(clamp01(g.get("density", 0.5))))
        self.send("/qmw/time/global/entropy", float(clamp01(g.get("entropy", g.get("entropy_bias", 0.0)))))
        self.send("/qmw/time/global/noise", float(clamp01(g.get("noise", 0.0))))
        self.send("/qmw/time/global/articulation", float(clamp01(g.get("articulation", 0.4))))
        self.send("/qmw/time/global/harmonicity", float(clamp01(g.get("harmonicity", 0.75))))
        self.send("/qmw/time/global/inharmonicity", float(clamp01(g.get("inharmonicity", 0.25))))

        self.send("/qmw/time/macro/coherence", float(clamp01(m.get("coherence", 0.0))))
        self.send("/qmw/time/macro/noisiness", float(clamp01(m.get("noisiness", 0.0))))
        self.send("/qmw/time/macro/population_polarity", float(clamp01(m.get("population_polarity", 0.0))))

    def reset(self) -> None:
        with self.lock:
            for lane in self.lanes.values():
                lane.elapsed_ms = 0.0
                lane.gate_remaining_ms = 0.0
                lane.counter = 0

            self.previous_phase_norm = [0.0 for _ in range(N_QUBITS)]
            self.previous_z = [1.0 for _ in range(N_QUBITS)]
            self.previous_coherence = 0.0
            self.event_counter = 0
            self.morph_elapsed_ms = 0.0

        print("timing layer reset")

    def run(self) -> None:
        self.setup_server()

        print(
            "QMW Timing + Probability Layer v1 running\n"
            f"  OSC in:        0.0.0.0:{self.osc_in_port}\n"
            f"  OSC out:       {self.osc_host}:{self.osc_out_port}\n"
            f"  Morpher out:   {self.morph_host}:{self.morph_port}\n"
            f"  rate:          {self.rate_hz:.1f} Hz\n"
            f"  mode:          {self.mode}\n"
            f"  pass-through:  {self.pass_through}\n"
            f"  auto morph:    {self.auto_morph_enabled}\n"
            "Ctrl-C to stop."
        )

        dt = 1.0 / max(1.0, self.rate_hz)
        next_time = time.perf_counter()

        while self.running:
            now = time.perf_counter()

            if now < next_time:
                time.sleep(max(0.0, next_time - now))
                continue

            next_time += dt
            self.update_lanes(dt)

    def stop(self) -> None:
        self.running = False

        # Avoid blocking forever on OSC server shutdown.
        try:
            if self.server is not None:
                self.server.server_close()
        except Exception as exc:
            print(f"OSC server close warning: {exc}", file=sys.stderr)


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="QMW Timing + Probability Layer v1.")

    parser.add_argument("--host", default="127.0.0.1", help="OSC output host for Max")
    parser.add_argument("--in-port", type=int, default=7420, help="OSC input from Pauli synth")
    parser.add_argument("--out-port", type=int, default=7403, help="OSC output to Max")
    parser.add_argument("--morph-host", default="127.0.0.1", help="OSC host for morpher control")
    parser.add_argument("--morph-port", type=int, default=7404, help="OSC port for morpher control")
    parser.add_argument("--rate", type=float, default=120.0, help="control rate in Hz")
    parser.add_argument("--mode", choices=("fixed", "prob", "hybrid", "off"), default="prob")
    parser.add_argument("--no-pass", action="store_true", help="disable Pauli pass-through")
    parser.add_argument("--auto-morph", action="store_true", help="enable probabilistic morpher advance")
    parser.add_argument("--prob-scale", type=float, default=1.0, help="global probability scale")
    parser.add_argument("--seed", type=int, default=None, help="random seed")

    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> None:
    args = parse_args(argv)

    if args.seed is not None:
        random.seed(args.seed)

    layer = TimingProbabilityLayer(
        osc_host=args.host,
        osc_in_port=args.in_port,
        osc_out_port=args.out_port,
        morph_host=args.morph_host,
        morph_port=args.morph_port,
        rate_hz=args.rate,
        mode=args.mode,
        pass_through=not args.no_pass,
        auto_morph_enabled=args.auto_morph,
        probability_scale=max(0.0, args.prob_scale),
    )

    def handle_stop(signum: int, frame: Any) -> None:
        print("\nStopping QMW Timing + Probability Layer...")
        layer.stop()

    signal.signal(signal.SIGINT, handle_stop)
    signal.signal(signal.SIGTERM, handle_stop)

    layer.run()


if __name__ == "__main__":
    main()
