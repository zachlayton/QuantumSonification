#!/usr/bin/env python3
"""
qmw_operator_preset_morpher_v1.py

Quantum Material Workbench control layer.

Purpose:
    A pattr-like operator preset morpher for Quantum Parametric Composition.
    It does not synthesize audio and does not run a quantum simulation.
    It stores/recalls/interpolates observational lens states and outputs
    continuous OSC control streams for a downstream QMW quantum engine, Max
    patch, or synth.

Core idea:
    Quantum data is the source behavior. Presets are lenses: gains, routing,
    smoothing, and mapping depth used to listen to that behavior without
    generating synthetic quantum motion.

Install:
    pip install python-osc

Example:
    python control/qmw_operator_preset_morpher_v1.py

Default Complex Pauli Oscillator chain:
    morpher listens on 7404
    morpher sends to synth on 7410
    synth sends to Max on 7403

OSC control input examples:
    /qmw/morpher/advance
    /qmw/morpher/recall 7
    /qmw/morpher/recall 7 3000
    /qmw/morpher/mode fixed
    /qmw/morpher/mode prob
    /qmw/morpher/prob 0.35
    /qmw/morpher/interval 500
    /qmw/morpher/interp 2500
    /qmw/morpher/freeze 1
    /qmw/morpher/lane q0 interval 333
    /qmw/morpher/lane q1 phase 3
    /qmw/morpher/lane q2 prob 0.7
    /qmw/morpher/set/global 0 density 0.9
    /qmw/morpher/set/lens 0 smoothing_ms 500
    /qmw/morpher/set/feature 1 coherence_gain 2.0
    /qmw/morpher/set/routing 1 coherence_to_amp 1.5
    /qmw/morpher/set/qubit 0 2 rz 0.785398
    /qmw/morpher/set/ham 0 ZIII 0.7
    /qmw/morpher/set/corr 0 01 zz -0.4
    /qmw/morpher/baseline
    /qmw/lens/baseline
    /qmw/lens/store 4
    /qmw/lens/recall 4 3000
    /qmw/observe/store 7
    /qmw/observe/recall 7 5000
    /qmw/bank/save quantum_observations_01.json
    /qmw/bank/load quantum_observations_01.json
"""

from __future__ import annotations

import argparse
import copy
import json
import math
import random
import signal
import sys
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, List, MutableMapping, Optional

try:
    from pythonosc.dispatcher import Dispatcher
    from pythonosc.osc_server import ThreadingOSCUDPServer
    from pythonosc.udp_client import SimpleUDPClient
except ImportError as exc:
    raise SystemExit(
        "Missing dependency: python-osc. Install with: pip install python-osc"
    ) from exc


N_STEPS = 16
N_QUBITS = 4
LANES = ("global", "q0", "q1", "q2", "q3", "corr", "ham")

DEFAULT_HAMILTONIAN_TERMS = (
    "ZIII", "IZII", "IIZI", "IIIZ",
    "XIII", "IXII", "IIXI", "IIIX",
    "ZZII", "IZZI", "IIZZ", "ZIIZ",
    "XXII", "IXXI", "IIXX", "XIIX",
    "YYYY", "XXXX", "ZZZZ",
)

CORR_PAIRS = ("01", "02", "03", "12", "13", "23")
CORR_TERMS = ("xx", "yy", "zz", "xy", "yx")

GLOBAL_FIELDS = (
    "density",
    "entropy_bias",
    "noise",
    "harmonicity",
    "inharmonicity",
    "articulation",
    "spatial_spread",
    "mapping_depth",
)

QUBIT_FIELDS = (
    "rx", "ry", "rz",
    "mx", "my", "mz",
    "amp_depth", "phase_depth",
    "bright_depth", "pan_depth",
)

LENS_GLOBAL_FIELDS = (
    "data_gain",
    "smoothing_ms",
    "mapping_depth",
    "probability_bias",
)

LENS_FEATURE_FIELDS = (
    "bloch_x_gain",
    "bloch_y_gain",
    "bloch_z_gain",
    "coherence_gain",
    "population_gain",
    "entropy_gain",
    "pauli_string_gain",
    "density_diag_gain",
    "density_offdiag_gain",
    "hamiltonian_spectrum_gain",
)

LENS_ROUTING_FIELDS = (
    "x_to_phase",
    "y_to_quadrature",
    "z_to_brightness",
    "entropy_to_grains",
    "coherence_to_amp",
    "pauli_corr_to_coupling",
    "hamiltonian_to_pitch",
)


def clamp01(x: float) -> float:
    return max(0.0, min(1.0, float(x)))


def smoothstep(x: float) -> float:
    x = clamp01(x)
    return x * x * (3.0 - 2.0 * x)


def lerp(a: float, b: float, t: float) -> float:
    return (1.0 - t) * a + t * b


def lerp_angle(a: float, b: float, t: float) -> float:
    """Shortest-path interpolation for radians."""
    diff = (b - a + math.pi) % (2.0 * math.pi) - math.pi
    return a + diff * t


def is_angle_field(name: str) -> bool:
    return name in {"rx", "ry", "rz", "phase", "theta", "phi"}


def nested_set(d: MutableMapping[str, Any], path: Iterable[str], value: Any) -> None:
    parts = list(path)
    cur: Any = d
    for p in parts[:-1]:
        cur = cur[p]
    cur[parts[-1]] = value


def interp_values(a: Any, b: Any, t: float, field_name: str = "") -> Any:
    """Recursively interpolate numbers in nested dictionaries/lists."""
    if isinstance(a, dict) and isinstance(b, dict):
        out: Dict[str, Any] = {}
        for key in a.keys():
            if key in b:
                out[key] = interp_values(a[key], b[key], t, str(key))
            else:
                out[key] = copy.deepcopy(a[key])
        return out

    if isinstance(a, list) and isinstance(b, list):
        return [interp_values(x, y, t, field_name) for x, y in zip(a, b)]

    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        if is_angle_field(field_name):
            return lerp_angle(float(a), float(b), t)
        return lerp(float(a), float(b), t)

    return copy.deepcopy(a if t < 0.5 else b)


@dataclass
class MorphLane:
    name: str
    current_step: int = 0
    target_step: int = 1
    phase_offset: int = 0
    interval_ms: float = 500.0
    interp_ms: float = 2000.0
    elapsed_ms: float = 0.0
    morph_ms: float = 0.0
    probability: float = 1.0
    enabled: bool = True

    def lambda_raw(self) -> float:
        if self.interp_ms <= 0:
            return 1.0
        return clamp01(self.morph_ms / self.interp_ms)

    def set_target(self, step: int, interp_ms: Optional[float] = None) -> None:
        step = int(step) % N_STEPS
        self.current_step = self.target_step if self.lambda_raw() >= 1.0 else self.current_step
        self.target_step = step
        self.morph_ms = 0.0
        if interp_ms is not None:
            self.interp_ms = max(0.0, float(interp_ms))

    def advance(self, amount: int = 1) -> None:
        next_step = (self.target_step + int(amount)) % N_STEPS
        self.set_target(next_step)

    def tick(self, dt_ms: float, mode: str, global_prob: float, frozen: bool) -> bool:
        if frozen or not self.enabled:
            return False

        self.elapsed_ms += dt_ms
        self.morph_ms += dt_ms

        advanced = False
        if self.interval_ms > 0.0 and self.elapsed_ms >= self.interval_ms:
            self.elapsed_ms %= self.interval_ms

            should_advance = mode == "fixed"
            if mode == "prob":
                p = clamp01(global_prob * self.probability)
                should_advance = random.random() < p

            if should_advance:
                self.advance(1)
                advanced = True

        return advanced


@dataclass
class OperatorPresetMorpher:
    osc_host: str = "127.0.0.1"
    osc_out_port: int = 7410
    osc_in_port: int = 7404
    send_rate_hz: float = 60.0
    mode: str = "fixed"
    frozen: bool = False
    probability_source: float = 0.5
    curve: str = "smoothstep"
    presets: List[Dict[str, Any]] = field(default_factory=list)
    observation_presets: List[Dict[str, Any]] = field(default_factory=list)
    lanes: Dict[str, MorphLane] = field(default_factory=dict)
    observation_lane: MorphLane = field(default_factory=lambda: MorphLane(
        name="observe",
        current_step=0,
        target_step=0,
        interval_ms=0.0,
        interp_ms=0.0,
    ))
    raw_observation: Dict[str, Any] = field(default_factory=dict)
    running: bool = True

    def __post_init__(self) -> None:
        if not self.presets:
            self.presets = make_default_presets()
        if not self.observation_presets:
            self.observation_presets = make_default_observation_presets()
        if not self.lanes:
            self.lanes = self.make_default_lanes()
        if not self.raw_observation:
            self.raw_observation = make_neutral_observation("raw_uninitialized")
        self.client = SimpleUDPClient(self.osc_host, self.osc_out_port)
        self.server: Optional[ThreadingOSCUDPServer] = None
        self._server_thread: Optional[threading.Thread] = None

    def make_default_lanes(self) -> Dict[str, MorphLane]:
        defaults = {
            "global": 800.0,
            "q0": 500.0,
            "q1": 625.0,
            "q2": 700.0,
            "q3": 875.0,
            "corr": 1100.0,
            "ham": 1400.0,
        }
        lanes: Dict[str, MorphLane] = {}
        for name in LANES:
            current = 0
            lanes[name] = MorphLane(
                name=name,
                current_step=current,
                target_step=current,
                phase_offset=0,
                interval_ms=defaults[name],
                interp_ms=2200.0,
                probability=1.0,
            )
        return lanes

    def curve_value(self, x: float) -> float:
        x = clamp01(x)
        if self.curve == "linear":
            return x
        return smoothstep(x)

    def lane_state(self, lane_name: str) -> Dict[str, Any]:
        lane = self.lanes[lane_name]
        a = self.presets[lane.current_step]
        b = self.presets[lane.target_step]
        t = self.curve_value(lane.lambda_raw())
        return interp_values(a, b, t)

    def current_operator_state(self) -> Dict[str, Any]:
        """Assemble one state from independently clocked lanes."""
        global_state = self.lane_state("global")
        q0_state = self.lane_state("q0")
        q1_state = self.lane_state("q1")
        q2_state = self.lane_state("q2")
        q3_state = self.lane_state("q3")
        corr_state = self.lane_state("corr")
        ham_state = self.lane_state("ham")

        return {
            "name": global_state.get("name", "unnamed_lens"),
            "lens": global_state.get("lens", {}),
            "features": global_state.get("features", {}),
            "routing": global_state.get("routing", {}),
            "global": global_state["global"],
            "qubits": [
                q0_state["qubits"][0],
                q1_state["qubits"][1],
                q2_state["qubits"][2],
                q3_state["qubits"][3],
            ],
            "corr": corr_state["corr"],
            "ham": ham_state["ham"],
        }

    def current_observation_state(self) -> Dict[str, Any]:
        """Interpolate between captured quantum observations."""
        lane = self.observation_lane
        a = self.observation_presets[lane.current_step]
        b = self.observation_presets[lane.target_step]
        t = self.curve_value(lane.lambda_raw())
        return interp_values(a, b, t)

    def current_lensed_observation(self) -> Dict[str, Any]:
        """Apply the current listening lens to the latest raw observation."""
        lens_state = self.current_operator_state()
        observation = copy.deepcopy(self.raw_observation)
        lens = lens_state.get("lens", {})
        features = lens_state.get("features", {})
        data_gain = float(lens.get("data_gain", 1.0))
        density_gain = data_gain * float(features.get("density_diag_gain", 1.0))
        coherence_gain = data_gain * float(features.get("coherence_gain", 1.0))
        entropy_gain = data_gain * float(features.get("entropy_gain", 1.0))
        pauli_gain = data_gain * float(features.get("pauli_string_gain", 1.0))
        ham_gain = data_gain * float(features.get("hamiltonian_spectrum_gain", 1.0))
        bloch_x_gain = data_gain * float(features.get("bloch_x_gain", 1.0))
        bloch_y_gain = data_gain * float(features.get("bloch_y_gain", 1.0))
        bloch_z_gain = data_gain * float(features.get("bloch_z_gain", 1.0))

        if "density" in observation["global"]:
            observation["global"]["density"] *= density_gain
        if "coherence" in observation["global"]:
            observation["global"]["coherence"] *= coherence_gain
        if "entropy_bias" in observation["global"]:
            observation["global"]["entropy_bias"] *= entropy_gain
        if "entropy" in observation["global"]:
            observation["global"]["entropy"] *= entropy_gain

        for qstate in observation["qubits"]:
            if "mx" in qstate:
                qstate["mx"] *= bloch_x_gain
            if "my" in qstate:
                qstate["my"] *= bloch_y_gain
            if "mz" in qstate:
                qstate["mz"] *= bloch_z_gain

        for terms in observation["corr"].values():
            for term in terms:
                terms[term] *= pauli_gain

        for pauli in observation["ham"]:
            observation["ham"][pauli] *= ham_gain

        observation["name"] = f"{observation.get('name', 'raw')}_through_{lens_state.get('name', 'lens')}"
        observation["lens_name"] = lens_state.get("name", "unnamed_lens")
        return observation

    def send(self, addr: str, *values: Any) -> None:
        try:
            self.client.send_message(addr, list(values) if len(values) > 1 else values[0])
        except Exception as exc:
            print(f"OSC send error {addr}: {exc}", file=sys.stderr)

    def send_observation(self, prefix: str, observation: Dict[str, Any]) -> None:
        self.send(f"{prefix}/name", str(observation.get("name", "unnamed_observation")))
        self.send(f"{prefix}/captured", int(bool(observation.get("captured", False))))

        for key, value in observation.get("global", {}).items():
            self.send(f"{prefix}/global/{key}", float(value))

        for q, qstate in enumerate(observation.get("qubits", [])):
            for key, value in qstate.items():
                self.send(f"{prefix}/q/{q}/{key}", float(value))

        for pair, terms in observation.get("corr", {}).items():
            for term, value in terms.items():
                self.send(f"{prefix}/corr/{pair}/{term}", float(value))

        for pauli, value in observation.get("ham", {}).items():
            self.send(f"{prefix}/ham/{pauli}", float(value))

    def send_state(self) -> None:
        state = self.current_operator_state()
        captured = self.current_observation_state()
        lensed = self.current_lensed_observation()

        self.send("/qmw/operator/mode", self.mode)
        self.send("/qmw/operator/frozen", int(self.frozen))
        self.send("/qmw/operator/prob", float(self.probability_source))
        self.send("/qmw/capture/lane/current", int(self.observation_lane.current_step))
        self.send("/qmw/capture/lane/target", int(self.observation_lane.target_step))
        self.send("/qmw/capture/lane/lambda", float(self.curve_value(self.observation_lane.lambda_raw())))
        self.send("/qmw/capture/lane/interp_ms", float(self.observation_lane.interp_ms))

        for lane_name, lane in self.lanes.items():
            self.send(f"/qmw/operator/lane/{lane_name}/current", int(lane.current_step))
            self.send(f"/qmw/operator/lane/{lane_name}/target", int(lane.target_step))
            self.send(f"/qmw/operator/lane/{lane_name}/lambda", float(self.curve_value(lane.lambda_raw())))
            self.send(f"/qmw/operator/lane/{lane_name}/interval_ms", float(lane.interval_ms))
            self.send(f"/qmw/operator/lane/{lane_name}/interp_ms", float(lane.interp_ms))

        self.send("/qmw/lens/name", str(state["name"]))
        for key, value in state["lens"].items():
            self.send(f"/qmw/lens/global/{key}", float(value))

        for key, value in state["features"].items():
            self.send(f"/qmw/lens/features/{key}", float(value))

        for key, value in state["routing"].items():
            self.send(f"/qmw/lens/routing/{key}", float(value))

        for key, value in state["global"].items():
            self.send(f"/qmw/operator/global/{key}", float(value))

        for q, qstate in enumerate(state["qubits"]):
            for key, value in qstate.items():
                self.send(f"/qmw/operator/q/{q}/{key}", float(value))

        for pair, terms in state["corr"].items():
            for term, value in terms.items():
                self.send(f"/qmw/operator/corr/{pair}/{term}", float(value))

        for pauli, value in state["ham"].items():
            self.send(f"/qmw/operator/ham/{pauli}", float(value))

        self.send_observation("/qmw/raw", self.raw_observation)
        self.send_observation("/qmw/capture/current", captured)
        self.send_observation("/qmw/lens/out", lensed)

    def setup_server(self) -> None:
        dispatcher = Dispatcher()
        dispatcher.map("/qmw/morpher/advance", self.osc_advance)
        dispatcher.map("/qmw/morpher/recall", self.osc_recall)
        dispatcher.map("/qmw/morpher/mode", self.osc_mode)
        dispatcher.map("/qmw/morpher/prob", self.osc_probability)
        dispatcher.map("/qmw/morpher/interval", self.osc_interval)
        dispatcher.map("/qmw/morpher/interp", self.osc_interp)
        dispatcher.map("/qmw/morpher/curve", self.osc_curve)
        dispatcher.map("/qmw/morpher/freeze", self.osc_freeze)
        dispatcher.map("/qmw/morpher/lane", self.osc_lane)
        dispatcher.map("/qmw/morpher/set/global", self.osc_set_global)
        dispatcher.map("/qmw/morpher/set/lens", self.osc_set_lens)
        dispatcher.map("/qmw/morpher/set/feature", self.osc_set_feature)
        dispatcher.map("/qmw/morpher/set/routing", self.osc_set_routing)
        dispatcher.map("/qmw/morpher/set/qubit", self.osc_set_qubit)
        dispatcher.map("/qmw/morpher/set/ham", self.osc_set_ham)
        dispatcher.map("/qmw/morpher/set/corr", self.osc_set_corr)
        dispatcher.map("/qmw/morpher/randomize", self.osc_randomize)
        dispatcher.map("/qmw/morpher/baseline", self.osc_baseline)
        dispatcher.map("/qmw/lens/baseline", self.osc_baseline)
        dispatcher.map("/qmw/lens/store", self.osc_lens_store)
        dispatcher.map("/qmw/lens/recall", self.osc_recall)
        dispatcher.map("/qmw/observe/store", self.osc_observe_store)
        dispatcher.map("/qmw/observe/recall", self.osc_observe_recall)
        dispatcher.map("/qmw/bank/save", self.osc_bank_save)
        dispatcher.map("/qmw/bank/load", self.osc_bank_load)
        dispatcher.map("/qmw/raw/global", self.osc_raw_global)
        dispatcher.map("/qmw/raw/q", self.osc_raw_qubit)
        dispatcher.map("/qmw/raw/ham", self.osc_raw_ham)
        dispatcher.map("/qmw/raw/corr", self.osc_raw_corr)
        dispatcher.set_default_handler(self.osc_default)

        self.server = ThreadingOSCUDPServer(("0.0.0.0", self.osc_in_port), dispatcher)
        self._server_thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self._server_thread.start()

    def osc_default(self, addr: str, *args: Any) -> None:
        if self.ingest_raw_address(addr, args):
            return
        print(f"unhandled OSC: {addr} {args}")

    def osc_advance(self, addr: str, *args: Any) -> None:
        amount = int(args[0]) if args else 1
        for lane in self.lanes.values():
            lane.advance(amount)

    def osc_recall(self, addr: str, *args: Any) -> None:
        if not args:
            return
        step = int(args[0]) % N_STEPS
        interp_ms = float(args[1]) if len(args) > 1 else None
        for lane in self.lanes.values():
            lane.set_target(step, interp_ms)

    def osc_baseline(self, addr: str, *args: Any) -> None:
        """
        Recall the neutral/pass-through baseline.
        /qmw/morpher/baseline
        /qmw/morpher/baseline 3000
        User-facing Preset 1 = internal step 0.
        """
        interp_ms = float(args[0]) if args else 0.0
        for lane in self.lanes.values():
            lane.current_step = 0
            lane.target_step = 0
            lane.morph_ms = 0.0
            lane.interp_ms = max(0.0, interp_ms)

    def osc_lens_store(self, addr: str, *args: Any) -> None:
        if not args:
            return
        step = int(args[0]) % N_STEPS
        state = self.current_operator_state()
        state["name"] = f"stored_lens_{step + 1:02d}"
        self.presets[step] = copy.deepcopy(state)
        print(f"stored lens preset {step + 1}")

    def osc_observe_store(self, addr: str, *args: Any) -> None:
        if not args:
            return
        step = int(args[0]) % N_STEPS
        observation = copy.deepcopy(self.raw_observation)
        observation["name"] = f"observed_snapshot_{step + 1:02d}"
        observation["captured"] = True
        observation["captured_unix"] = time.time()
        self.observation_presets[step] = observation
        print(f"stored observation preset {step + 1}")

    def osc_observe_recall(self, addr: str, *args: Any) -> None:
        if not args:
            return
        step = int(args[0]) % N_STEPS
        interp_ms = float(args[1]) if len(args) > 1 else None
        self.observation_lane.set_target(step, interp_ms)

    def osc_bank_save(self, addr: str, *args: Any) -> None:
        if not args:
            return
        path = self.bank_path(str(args[0]))
        payload = {
            "version": 1,
            "lens_presets": self.presets,
            "observation_presets": self.observation_presets,
        }
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        print(f"saved banks to {path}")

    def osc_bank_load(self, addr: str, *args: Any) -> None:
        if not args:
            return
        path = self.bank_path(str(args[0]))
        payload = json.loads(path.read_text(encoding="utf-8"))
        if "lens_presets" in payload:
            self.presets = normalize_bank(payload["lens_presets"], make_default_presets())
        if "observation_presets" in payload:
            self.observation_presets = normalize_bank(
                payload["observation_presets"],
                make_default_observation_presets(),
            )
        print(f"loaded banks from {path}")

    def bank_path(self, filename: str) -> Path:
        path = Path(filename)
        if not path.is_absolute():
            path = Path.cwd() / path
        return path

    def osc_raw_global(self, addr: str, *args: Any) -> None:
        if len(args) < 2:
            return
        self.raw_observation["global"][str(args[0])] = float(args[1])
        self.raw_observation["captured"] = False

    def osc_raw_qubit(self, addr: str, *args: Any) -> None:
        if len(args) < 3:
            return
        q = int(args[0]) % N_QUBITS
        self.raw_observation["qubits"][q][str(args[1])] = float(args[2])
        self.raw_observation["captured"] = False

    def osc_raw_ham(self, addr: str, *args: Any) -> None:
        if len(args) < 2:
            return
        self.raw_observation["ham"][str(args[0]).upper()] = float(args[1])
        self.raw_observation["captured"] = False

    def osc_raw_corr(self, addr: str, *args: Any) -> None:
        if len(args) < 3:
            return
        pair = str(args[0])
        term = str(args[1]).lower()
        if pair not in self.raw_observation["corr"]:
            self.raw_observation["corr"][pair] = {k: 0.0 for k in CORR_TERMS}
        self.raw_observation["corr"][pair][term] = float(args[2])
        self.raw_observation["captured"] = False

    def ingest_raw_address(self, addr: str, args: Iterable[Any]) -> bool:
        parts = addr.strip("/").split("/")
        values = list(args)
        if len(parts) < 4 or parts[0:2] != ["qmw", "raw"] or not values:
            return False

        try:
            if parts[2] == "global" and len(parts) == 4:
                self.raw_observation["global"][parts[3]] = float(values[0])
            elif parts[2] == "q" and len(parts) == 5:
                q = int(parts[3]) % N_QUBITS
                self.raw_observation["qubits"][q][parts[4]] = float(values[0])
            elif parts[2] == "ham" and len(parts) == 4:
                self.raw_observation["ham"][parts[3].upper()] = float(values[0])
            elif parts[2] == "corr" and len(parts) == 5:
                pair = parts[3]
                term = parts[4].lower()
                if pair not in self.raw_observation["corr"]:
                    self.raw_observation["corr"][pair] = {k: 0.0 for k in CORR_TERMS}
                self.raw_observation["corr"][pair][term] = float(values[0])
            else:
                return False
        except (TypeError, ValueError):
            return False

        self.raw_observation["captured"] = False
        return True

    def osc_mode(self, addr: str, *args: Any) -> None:
        if not args:
            return
        mode = str(args[0]).lower()
        if mode in {"fixed", "prob"}:
            self.mode = mode
            print(f"mode = {self.mode}")
        else:
            print("mode must be 'fixed' or 'prob'")

    def osc_probability(self, addr: str, *args: Any) -> None:
        if args:
            self.probability_source = clamp01(float(args[0]))

    def osc_interval(self, addr: str, *args: Any) -> None:
        if args:
            interval = max(1.0, float(args[0]))
            for lane in self.lanes.values():
                lane.interval_ms = interval

    def osc_interp(self, addr: str, *args: Any) -> None:
        if args:
            interp = max(0.0, float(args[0]))
            for lane in self.lanes.values():
                lane.interp_ms = interp

    def osc_curve(self, addr: str, *args: Any) -> None:
        if not args:
            return
        curve = str(args[0]).lower()
        if curve in {"linear", "smoothstep"}:
            self.curve = curve

    def osc_freeze(self, addr: str, *args: Any) -> None:
        if args:
            self.frozen = bool(int(float(args[0])))

    def osc_lane(self, addr: str, *args: Any) -> None:
        """
        /qmw/morpher/lane q0 interval 333
        /qmw/morpher/lane q1 interp 2500
        /qmw/morpher/lane q2 prob 0.5
        /qmw/morpher/lane q3 phase 7
        /qmw/morpher/lane ham enable 0
        """
        if len(args) < 3:
            return
        lane_name = str(args[0]).lower()
        param = str(args[1]).lower()
        value = args[2]
        if lane_name not in self.lanes:
            print(f"unknown lane: {lane_name}")
            return
        lane = self.lanes[lane_name]
        if param == "interval":
            lane.interval_ms = max(1.0, float(value))
        elif param == "interp":
            lane.interp_ms = max(0.0, float(value))
        elif param == "prob":
            lane.probability = clamp01(float(value))
        elif param == "phase":
            lane.phase_offset = int(value) % N_STEPS
            lane.current_step = lane.phase_offset
            lane.target_step = (lane.phase_offset + 1) % N_STEPS
            lane.morph_ms = 0.0
        elif param == "enable":
            lane.enabled = bool(int(float(value)))

    def osc_set_global(self, addr: str, *args: Any) -> None:
        if len(args) < 3:
            return
        step = int(args[0]) % N_STEPS
        field_name = str(args[1])
        if field_name not in GLOBAL_FIELDS:
            print(f"unknown global field: {field_name}")
            return
        self.presets[step]["global"][field_name] = float(args[2])

    def osc_set_lens(self, addr: str, *args: Any) -> None:
        if len(args) < 3:
            return
        step = int(args[0]) % N_STEPS
        field_name = str(args[1])
        if field_name not in LENS_GLOBAL_FIELDS:
            print(f"unknown lens field: {field_name}")
            return
        self.presets[step]["lens"][field_name] = max(0.0, float(args[2]))

    def osc_set_feature(self, addr: str, *args: Any) -> None:
        if len(args) < 3:
            return
        step = int(args[0]) % N_STEPS
        field_name = str(args[1])
        if field_name not in LENS_FEATURE_FIELDS:
            print(f"unknown feature field: {field_name}")
            return
        self.presets[step]["features"][field_name] = max(0.0, float(args[2]))

    def osc_set_routing(self, addr: str, *args: Any) -> None:
        if len(args) < 3:
            return
        step = int(args[0]) % N_STEPS
        field_name = str(args[1])
        if field_name not in LENS_ROUTING_FIELDS:
            print(f"unknown routing field: {field_name}")
            return
        self.presets[step]["routing"][field_name] = max(0.0, float(args[2]))

    def osc_set_qubit(self, addr: str, *args: Any) -> None:
        if len(args) < 4:
            return
        step = int(args[0]) % N_STEPS
        q = int(args[1]) % N_QUBITS
        field_name = str(args[2])
        if field_name not in QUBIT_FIELDS:
            print(f"unknown qubit field: {field_name}")
            return
        self.presets[step]["qubits"][q][field_name] = float(args[3])

    def osc_set_ham(self, addr: str, *args: Any) -> None:
        if len(args) < 3:
            return
        step = int(args[0]) % N_STEPS
        pauli = str(args[1]).upper()
        self.presets[step]["ham"][pauli] = float(args[2])

    def osc_set_corr(self, addr: str, *args: Any) -> None:
        if len(args) < 4:
            return
        step = int(args[0]) % N_STEPS
        pair = str(args[1])
        term = str(args[2]).lower()
        value = float(args[3])
        if pair not in self.presets[step]["corr"]:
            self.presets[step]["corr"][pair] = {k: 0.0 for k in CORR_TERMS}
        self.presets[step]["corr"][pair][term] = value

    def osc_randomize(self, addr: str, *args: Any) -> None:
        strength = clamp01(float(args[0])) if args else 0.25
        self.randomize_presets(strength)

    def randomize_presets(self, strength: float = 0.25) -> None:
        # Preserve Preset 1 / internal index 0 as the raw observation baseline.
        # Randomize only lens controls; do not invent operator, Pauli, Hamiltonian,
        # or correlation material inside the morpher.
        for preset in self.presets[1:]:
            for key in LENS_GLOBAL_FIELDS:
                if key == "smoothing_ms":
                    preset["lens"][key] = max(
                        0.0,
                        min(2000.0, preset["lens"][key] + random.uniform(-500.0, 500.0) * strength),
                    )
                else:
                    preset["lens"][key] = max(
                        0.0,
                        min(3.0, preset["lens"][key] + random.uniform(-strength, strength)),
                    )
            for key in LENS_FEATURE_FIELDS:
                preset["features"][key] = max(
                    0.0,
                    min(3.0, preset["features"][key] + random.uniform(-strength, strength)),
                )
            for key in LENS_ROUTING_FIELDS:
                preset["routing"][key] = max(
                    0.0,
                    min(3.0, preset["routing"][key] + random.uniform(-strength, strength)),
                )

    def run(self) -> None:
        self.setup_server()
        print(
            "QMW Operator Preset Morpher v1 running\n"
            f"  OSC out: {self.osc_host}:{self.osc_out_port}\n"
            f"  OSC in:  0.0.0.0:{self.osc_in_port}\n"
            f"  rate:    {self.send_rate_hz:.1f} Hz\n"
            f"  mode:    {self.mode}\n"
            "Ctrl-C to stop."
        )

        dt = 1.0 / max(1.0, self.send_rate_hz)
        dt_ms = dt * 1000.0
        next_time = time.perf_counter()

        while self.running:
            now = time.perf_counter()
            if now < next_time:
                time.sleep(max(0.0, next_time - now))
                continue
            next_time += dt

            for lane in self.lanes.values():
                lane.tick(dt_ms, self.mode, self.probability_source, self.frozen)
            if not self.frozen:
                self.observation_lane.morph_ms += dt_ms
            self.send_state()

    def stop(self) -> None:
        self.running = False
        if self.server is not None:
            self.server.shutdown()
            self.server.server_close()



def make_neutral_observation(name: str = "empty_observation") -> Dict[str, Any]:
    """Create an explicit empty slot for observed quantum data."""
    qubits: List[Dict[str, float]] = []
    for _ in range(N_QUBITS):
        qubits.append({
            "mx": 0.0,
            "my": 0.0,
            "mz": 0.0,
            "rx": math.pi / 2.0,
            "ry": math.pi / 2.0,
            "rz": math.pi,
        })
    return {
        "name": name,
        "captured": False,
        "global": {
            "density": 0.0,
            "coherence": 0.0,
            "entropy": 0.0,
            "entropy_bias": 0.0,
            "purity": 0.0,
        },
        "qubits": qubits,
        "ham": {term: 0.0 for term in DEFAULT_HAMILTONIAN_TERMS},
        "corr": {
            pair: {term: 0.0 for term in CORR_TERMS}
            for pair in CORR_PAIRS
        },
    }


def make_default_observation_presets() -> List[Dict[str, Any]]:
    """Create empty observation slots; they become meaningful only after capture."""
    return [
        make_neutral_observation(f"empty_observation_{step + 1:02d}")
        for step in range(N_STEPS)
    ]


def normalize_bank(incoming: Any, defaults: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Load up to 16 preset dictionaries, filling missing slots with defaults."""
    bank = copy.deepcopy(defaults)
    if not isinstance(incoming, list):
        return bank
    for index, preset in enumerate(incoming[:N_STEPS]):
        if isinstance(preset, dict):
            bank[index] = preset
    return bank


def make_neutral_preset() -> Dict[str, Any]:
    """
    Preset 1 / internal index 0.
    Raw observation / pass-through lens state.
    This should minimally color the downstream Pauli synth:
        - no Hamiltonian coefficients
        - no correlation targets
        - neutral rotation fields
        - neutral/global mapping values
        - all lens gains and routings at unity
    Note:
        The Pauli synth interprets:
            rx_scene = rx - pi/2
            ry_scene = ry - pi/2
            rz_scene = rz - pi
        Therefore neutral rotation values are:
            rx = pi/2
            ry = pi/2
            rz = pi
    """
    global_state = {
        "density": 0.5,
        "entropy_bias": 0.0,
        "noise": 0.0,
        "harmonicity": 1.0,
        "inharmonicity": 0.0,
        "articulation": 0.0,
        "spatial_spread": 0.5,
        "mapping_depth": 1.0,
    }
    qubits: List[Dict[str, float]] = []
    for _ in range(N_QUBITS):
        qubits.append({
            "rx": math.pi / 2.0,
            "ry": math.pi / 2.0,
            "rz": math.pi,
            "mx": 0.5,
            "my": 0.5,
            "mz": 0.5,
            "amp_depth": 1.0,
            "phase_depth": 1.0,
            "bright_depth": 1.0,
            "pan_depth": 1.0,
        })
    ham = {term: 0.0 for term in DEFAULT_HAMILTONIAN_TERMS}
    corr: Dict[str, Dict[str, float]] = {}
    for pair in CORR_PAIRS:
        corr[pair] = {term: 0.0 for term in CORR_TERMS}
    return {
        "name": "raw_baseline",
        "lens": {
            "data_gain": 1.0,
            "smoothing_ms": 0.0,
            "mapping_depth": 1.0,
            "probability_bias": 1.0,
        },
        "features": {field: 1.0 for field in LENS_FEATURE_FIELDS},
        "routing": {field: 1.0 for field in LENS_ROUTING_FIELDS},
        "global": global_state,
        "qubits": qubits,
        "ham": ham,
        "corr": corr,
    }


def make_lens_preset(
    name: str,
    lens: Optional[Dict[str, float]] = None,
    features: Optional[Dict[str, float]] = None,
    routing: Optional[Dict[str, float]] = None,
) -> Dict[str, Any]:
    """Build a preset as an observational lens over incoming quantum data."""
    preset = make_neutral_preset()
    preset["name"] = name
    if lens:
        for key, value in lens.items():
            if key in preset["lens"]:
                preset["lens"][key] = float(value)
    if features:
        for key, value in features.items():
            if key in preset["features"]:
                preset["features"][key] = float(value)
    if routing:
        for key, value in routing.items():
            if key in preset["routing"]:
                preset["routing"][key] = float(value)
    return preset


def make_default_presets() -> List[Dict[str, Any]]:
    """Create 16 observational lens states without synthetic motion."""
    presets = [
        make_neutral_preset(),
        make_lens_preset(
            "coherence_lens",
            features={"coherence_gain": 2.0, "population_gain": 0.6},
            routing={"coherence_to_amp": 1.7, "entropy_to_grains": 0.5},
        ),
        make_lens_preset(
            "population_lens",
            features={"population_gain": 2.0, "coherence_gain": 0.6, "bloch_z_gain": 1.7},
            routing={"z_to_brightness": 1.7, "coherence_to_amp": 0.7},
        ),
        make_lens_preset(
            "density_offdiag_lens",
            features={"density_offdiag_gain": 2.2, "density_diag_gain": 0.5, "coherence_gain": 1.5},
            routing={"coherence_to_amp": 1.5, "y_to_quadrature": 1.3},
        ),
        make_lens_preset(
            "pauli_string_lens",
            features={
                "pauli_string_gain": 2.5,
                "bloch_x_gain": 0.7,
                "bloch_y_gain": 0.7,
                "bloch_z_gain": 0.7,
            },
            routing={"pauli_corr_to_coupling": 2.0},
        ),
        make_lens_preset(
            "entanglement_correlation_lens",
            features={"pauli_string_gain": 1.8, "coherence_gain": 1.4, "density_offdiag_gain": 1.4},
            routing={"pauli_corr_to_coupling": 2.3, "coherence_to_amp": 1.2},
        ),
        make_lens_preset(
            "entropy_lens",
            features={"entropy_gain": 2.0, "coherence_gain": 0.7, "population_gain": 0.8},
            routing={"entropy_to_grains": 2.0, "coherence_to_amp": 0.7},
        ),
        make_lens_preset(
            "hamiltonian_spectrum_lens",
            features={"hamiltonian_spectrum_gain": 2.0, "pauli_string_gain": 1.3},
            routing={"hamiltonian_to_pitch": 2.0, "pauli_corr_to_coupling": 1.3},
        ),
        make_lens_preset(
            "bloch_x_lens",
            features={"bloch_x_gain": 2.0, "bloch_y_gain": 0.6, "bloch_z_gain": 0.6},
            routing={"x_to_phase": 1.8},
        ),
        make_lens_preset(
            "bloch_y_lens",
            features={"bloch_y_gain": 2.0, "bloch_x_gain": 0.6, "bloch_z_gain": 0.6},
            routing={"y_to_quadrature": 1.8},
        ),
        make_lens_preset(
            "bloch_z_lens",
            features={"bloch_z_gain": 2.0, "bloch_x_gain": 0.6, "bloch_y_gain": 0.6},
            routing={"z_to_brightness": 1.8},
        ),
        make_lens_preset(
            "diagonal_density_lens",
            features={"density_diag_gain": 2.0, "density_offdiag_gain": 0.6, "population_gain": 1.6},
            routing={"z_to_brightness": 1.4},
        ),
        make_lens_preset(
            "phase_quadrature_lens",
            features={"bloch_x_gain": 1.4, "bloch_y_gain": 1.4, "coherence_gain": 1.3},
            routing={"x_to_phase": 1.8, "y_to_quadrature": 1.8},
        ),
        make_lens_preset(
            "smoothed_observation_lens",
            lens={"smoothing_ms": 500.0},
            features={"coherence_gain": 1.2, "population_gain": 1.2},
        ),
        make_lens_preset(
            "deep_mapping_lens",
            lens={"data_gain": 1.3, "mapping_depth": 1.5},
            features={"coherence_gain": 1.3, "population_gain": 1.3, "pauli_string_gain": 1.3},
            routing={"coherence_to_amp": 1.4, "pauli_corr_to_coupling": 1.4},
        ),
        make_lens_preset(
            "comparison_lens",
            lens={"data_gain": 0.8, "smoothing_ms": 150.0},
            features={"entropy_gain": 1.3, "density_diag_gain": 1.3, "density_offdiag_gain": 1.3},
            routing={"entropy_to_grains": 1.3, "coherence_to_amp": 1.3},
        ),
    ]
    return presets


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="QMW pattr-like operator preset morpher for quantum-parametric composition."
    )
    parser.add_argument("--host", default="127.0.0.1", help="OSC output host")
    parser.add_argument("--out-port", type=int, default=7410, help="OSC output port")
    parser.add_argument("--in-port", type=int, default=7404, help="OSC control input port")
    parser.add_argument("--rate", type=float, default=60.0, help="OSC send rate in Hz")
    parser.add_argument("--mode", choices=("fixed", "prob"), default="fixed")
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> None:
    args = parse_args(argv)
    morpher = OperatorPresetMorpher(
        osc_host=args.host,
        osc_out_port=args.out_port,
        osc_in_port=args.in_port,
        send_rate_hz=args.rate,
        mode=args.mode,
    )

    def handle_sigint(signum: int, frame: Any) -> None:
        print("\nStopping QMW Operator Preset Morpher...")
        morpher.stop()

    signal.signal(signal.SIGINT, handle_sigint)
    signal.signal(signal.SIGTERM, handle_sigint)
    morpher.run()


if __name__ == "__main__":
    main()
