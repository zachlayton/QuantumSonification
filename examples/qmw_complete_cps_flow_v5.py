#!/usr/bin/env python3
"""Full 16-state Wilson CPS probability-flow instrument for Max."""

from __future__ import annotations

import argparse
from fractions import Fraction
import math
from pathlib import Path
import signal
import sys
import threading
import time

import numpy as np
from pythonosc.udp_client import SimpleUDPClient

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from examples.qmw_wilson_probability_flow_v4 import ProbabilityFlowWilsonMaxHost
from qmw.recursive_wilson import BasisFlow, WILSON_GENERATORS
from qmw.recursive_wilson import pascal_grade_probabilities
from wilson_quantum_geometry_v1 import (
    analyze_scala_constant_structure,
    CircuitWilsonTuningFrame,
    CombinationProductSet,
    MOSScaleTreeNavigator,
    ScalaScale,
    circuit_wilson_tuning_frame,
    load_scl,
    project_ratio_index_to_scala,
    project_ratio_to_scala,
    save_scl,
    scala_scale_from_ratios,
    validate_constant_structure,
    wilson_tuning_vertices,
)


# Ableton receives this as an MPE lower zone: channel 1 remains the master and
# every channel from 2 through 16, including 10, is available to notes.  CPS
# vertices are assigned dynamically, since a fixed 16-vertex mapping cannot
# fit into the fifteen member channels without a collision.
MPE_MEMBER_CHANNELS = tuple(range(2, 17))
TUNING_MODES = ("cps", "diamond", "mos", "scala", "equal")
PHASE_ANGLES = {"z": math.pi, "s": math.pi / 2, "t": math.pi / 4}
MODULATION_CC_MAP = {
    "entropy": 20,
    "coherence": 21,
    "entanglement": 22,
    "participation": 23,
    "phase_order": 24,
    "grade_centroid": 25,
    "hexany_mass": 26,
    "flow_strength": 27,
}


def state_modulation_metrics(state: object, *, flow_strength: float = 0.0) -> tuple[float, ...]:
    """Return eight global, bounded modulation lanes for MIDI/OSC control."""
    from qiskit.quantum_info import entropy, partial_trace

    amplitudes = np.asarray(state.data, dtype=np.complex128)
    if amplitudes.shape != (16,):
        raise ValueError("modulation metrics require a four-qubit statevector")
    probabilities = np.abs(amplitudes) ** 2
    nonzero = probabilities[probabilities > 1e-15]
    population_entropy = float(-np.sum(nonzero * np.log2(nonzero)) / 4.0)
    coherence = float(
        ((np.sum(np.abs(amplitudes)) ** 2) - 1.0) / 15.0
    )
    qubit_entropies = []
    for retained in range(4):
        reduced = partial_trace(state, [qubit for qubit in range(4) if qubit != retained])
        qubit_entropies.append(float(entropy(reduced, base=2)))
    entanglement = float(np.mean(qubit_entropies))
    inverse_participation = 1.0 / max(float(np.sum(probabilities**2)), 1e-15)
    participation = (inverse_participation - 1.0) / 15.0
    occupied = np.abs(amplitudes) > 1e-12
    phase_order = float(
        abs(np.sum(probabilities[occupied] * np.exp(1j * np.angle(amplitudes[occupied]))))
    )
    grade_centroid = float(
        sum(basis.bit_count() * probabilities[basis] for basis in range(16)) / 4.0
    )
    hexany_mass = float(
        sum(probabilities[basis] for basis in range(16) if basis.bit_count() == 2)
    )
    values = (
        population_entropy,
        coherence,
        entanglement,
        participation,
        phase_order,
        grade_centroid,
        hexany_mass,
        float(flow_strength),
    )
    return tuple(float(np.clip(value, 0.0, 1.0)) for value in values)


def basis_product(mask: int, factors: tuple[int, ...] = WILSON_GENERATORS) -> int:
    product = 1
    for qubit, generator in enumerate(factors):
        if (int(mask) >> qubit) & 1:
            product *= generator
    return product


def diamond_ratio(
    mask: int,
    factors: tuple[int, ...] = WILSON_GENERATORS,
) -> float:
    """Map four qubits onto one cell of a full 4x4 harmonic diamond.

    Qubits 0-1 select the otonal numerator and qubits 2-3 select the
    utonal denominator.  All sixteen computational states therefore remain
    present, including the four unison cells on the diamond diagonal.
    """
    if len(factors) != 4:
        raise ValueError("the four-qubit diamond requires four tuning factors")
    numerator = float(factors[int(mask) & 0b11])
    denominator = float(factors[(int(mask) >> 2) & 0b11])
    ratio = numerator / denominator
    while ratio < 1.0:
        ratio *= 2.0
    while ratio >= 2.0:
        ratio /= 2.0
    return ratio


def basis_midi(
    mask: int,
    factors: tuple[int, ...] = WILSON_GENERATORS,
    *,
    ratio_override: float | None = None,
) -> tuple[int, int, float]:
    """Map CPS rank to register and subset product to exact octave ratio."""
    rank = int(mask).bit_count()
    ratio = (
        float(basis_product(mask, factors))
        if ratio_override is None
        else float(ratio_override)
    )
    while ratio < 1.0:
        ratio *= 2.0
    while ratio >= 2.0:
        ratio /= 2.0
    fractional_pitch = 36.0 + 12.0 * rank + 12.0 * math.log2(ratio)
    note = int(round(fractional_pitch))
    deviation = fractional_pitch - note
    bend = int(round(8192 + (deviation / 2.0) * 8191))
    return note, max(0, min(16383, bend)), ratio


def mos_morph_projection(ratio: float, frame: object) -> tuple[float, float]:
    """Project one Wilson ratio through a voice-stable MOS Scale-Tree morph.

    The harmonic ratio selects its nearest generator-power identity in each
    MOS.  Pitch travels between those identities in logarithmic period space;
    activation follows the navigator's equal-power enter/leave crossfade.
    """
    base_position = math.log2(float(ratio)) % 1.0
    if frame.source == frame.target:
        return 2.0**base_position, 1.0

    def circular_delta(source: float, target: float) -> float:
        return (target - source + 0.5) % 1.0 - 0.5

    def nearest_voice(attribute: str) -> object:
        candidates = [
            voice for voice in frame.voices if getattr(voice, attribute) is not None
        ]
        return min(
            candidates,
            key=lambda voice: abs(circular_delta(base_position, voice.position)),
        )

    source_voice = nearest_voice("source_order")
    target_voice = nearest_voice("target_order")
    progress = float(np.clip(frame.progress, 0.0, 1.0))
    blend = math.sin(progress * math.pi / 2.0) ** 2
    position = (
        source_voice.position
        + blend * circular_delta(source_voice.position, target_voice.position)
    ) % 1.0
    activation = (
        (1.0 - blend) * source_voice.activation
        + blend * target_voice.activation
    )
    return 2.0**position, float(np.clip(activation, 0.0, 1.0))


def probability_current_velocity(strength: float, peak_strength: float) -> int:
    """Make probability current audible as a clearly differentiated attack.

    ``strength`` retains the quantum meaning of the event.  ``peak_strength``
    supplies only a local dynamic reference: the strongest audible current in
    an evolution step establishes that step's ceiling, while its absolute
    magnitude still determines how high that ceiling can rise.
    """
    current = float(np.clip(strength, 0.0, 1.0))
    peak = float(np.clip(max(current, peak_strength), 0.0, 1.0))
    if peak <= 1e-15 or current <= 1e-15:
        return 1
    relative_current = current / peak
    step_ceiling = 72.0 + 53.0 * math.sqrt(peak)
    velocity = 18.0 + (step_ceiling - 18.0) * relative_current**0.75
    return max(1, min(127, int(round(velocity))))


class CompleteCPSFlowMaxHost(ProbabilityFlowWilsonMaxHost):
    """Sound every rank of the four-generator CPS/Boolean lattice."""

    def __init__(
        self,
        *args,
        flow_articulation: str = "arrival",
        tuning_mode: str = "cps",
        scala_file: str | Path | None = None,
        supercollider_host: str = "127.0.0.1",
        supercollider_port: int | None = None,
        **kwargs,
    ) -> None:
        kwargs.setdefault("max_flows_per_step", 4)
        super().__init__(*args, **kwargs)
        self.supercollider_client = (
            None
            if supercollider_port is None or int(supercollider_port) <= 0
            else SimpleUDPClient(supercollider_host, int(supercollider_port))
        )
        self.flow_articulation = self._validate_flow_articulation(flow_articulation)
        self.scala_scale: ScalaScale | None = None
        self.scala_path: Path | None = None
        if scala_file is not None:
            self.scala_path = Path(scala_file)
            self.scala_scale = load_scl(self.scala_path)
        self.tuning_mode = self._validate_tuning_mode(tuning_mode)
        if self.tuning_mode == "scala" and self.scala_scale is None:
            raise ValueError("Scala tuning mode requires --scala-file or an OSC load")
        self._mpe_channel_cursor = 0
        self._mpe_busy_until = {channel: 0.0 for channel in MPE_MEMBER_CHANNELS}
        self._mpe_active_notes: list[tuple[float, int, int]] = []
        self._mpe_channel_lock = threading.Lock()
        self.instrument_grade = -1
        self.mos_navigator = MOSScaleTreeNavigator(4 / 3, (3, 7))
        self.circuit_tuning_enabled = True
        self.tuning_frame: CircuitWilsonTuningFrame | None = None
        self.tuning_factors = WILSON_GENERATORS
        self._tuning_revision = 0
        self._scala_revision = 0
        self.last_flow_strength = 0.0
        self.bridge.add_control_handler(
            "/qmw/recursive/articulation", self._osc_articulation
        )
        self.bridge.add_control_handler(
            "/qmw/wilson/navigation/grade", self._osc_navigation_grade
        )
        self.bridge.add_control_handler(
            "/qmw/wilson/navigation/mos_target", self._osc_mos_target
        )
        self.bridge.add_control_handler(
            "/qmw/wilson/navigation/mos_progress", self._osc_mos_progress
        )
        self.bridge.add_control_handler(
            "/qmw/wilson/tuning/enabled", self._osc_tuning_enabled
        )
        self.bridge.add_control_handler(
            "/qmw/wilson/tuning/mode", self._osc_tuning_mode
        )
        self.bridge.add_control_handler(
            "/qmw/wilson/tuning/scala/load", self._osc_scala_load
        )
        self.bridge.add_control_handler(
            "/qmw/wilson/tuning/scala/save", self._osc_scala_save
        )
        # v5 is a circuit instrument, not the autonomous Hexany probe. An
        # empty programmer must therefore mean |0000> and silence.
        self.engine.clear_circuit()
        self.circuit_active = False
        self._retune_from_circuit(publish=False)

    def _send(self, address: str, values: object) -> None:
        """Send to Max and mirror the compact audio protocol to SuperCollider."""
        super()._send(address, values)
        client = getattr(self, "supercollider_client", None)
        if client is not None and address in {
            "/qmw/recursive/cps_flow_note",
            "/qmw/recursive/modulation",
            "/qmw/recursive/running",
        }:
            try:
                client.send_message(address, values)
            except OSError as exc:
                print(f"SuperCollider OSC mirror failed: {exc}")

    def _send_visual(self, address: str, values: object) -> None:
        """Mirror state/geometry packets to Processing and SuperCollider."""
        self.visual_client.send_message(address, values)
        if self.supercollider_client is not None:
            try:
                self.supercollider_client.send_message(address, values)
            except OSError as exc:
                print(f"SuperCollider geometry mirror failed: {exc}")

    @staticmethod
    def _validate_flow_articulation(value: str) -> str:
        normalized = str(value).strip().lower()
        if normalized not in {"arrival", "dyad", "gesture"}:
            raise ValueError("flow articulation must be arrival, dyad, or gesture")
        return normalized

    @staticmethod
    def _validate_tuning_mode(value: str) -> str:
        normalized = str(value).strip().lower().replace("12-tet", "equal")
        if normalized not in TUNING_MODES:
            raise ValueError(f"tuning mode must be one of {', '.join(TUNING_MODES)}")
        return normalized

    def _osc_articulation(self, _address: str, value: str) -> None:
        try:
            self.flow_articulation = self._validate_flow_articulation(value)
            self._send(
                "/qmw/recursive/articulation",
                self.flow_articulation,
            )
        except Exception as exc:
            self._error(exc)

    def _osc_navigation_grade(self, _address: str, value: int) -> None:
        try:
            selected = int(value)
            if selected not in {-1, 0, 1, 2, 3, 4}:
                raise ValueError("instrument grade must be -1 (all) or 0 through 4")
            with self._lock:
                self._panic()
                self.instrument_grade = selected
                self._publish_navigation()
        except Exception as exc:
            self._error(exc)

    def _osc_mos_target(self, _address: str, numerator: int, denominator: int) -> None:
        try:
            with self._lock:
                self.mos_navigator.begin((int(numerator), int(denominator)))
                self._publish_navigation()
        except Exception as exc:
            self._error(exc)

    def _osc_mos_progress(self, _address: str, value: float) -> None:
        try:
            with self._lock:
                self.mos_navigator.set_progress(float(value))
                self._publish_navigation()
        except Exception as exc:
            self._error(exc)

    def _osc_tuning_enabled(self, _address: str, value: int) -> None:
        try:
            with self._lock:
                self._panic()
                self.circuit_tuning_enabled = bool(int(value))
                self._retune_from_circuit()
        except Exception as exc:
            self._error(exc)

    def _osc_tuning_mode(self, _address: str, value: str) -> None:
        try:
            with self._lock:
                self._panic()
                requested = self._validate_tuning_mode(value)
                if requested == "scala" and self.scala_scale is None:
                    raise ValueError("load a Scala .scl file before selecting scala mode")
                self.tuning_mode = requested
                self._publish_tuning_mode()
                if requested == "scala":
                    self._publish_scala_geometry()
        except Exception as exc:
            self._error(exc)

    def _osc_scala_load(self, _address: str, value: str) -> None:
        try:
            path = Path(str(value)).expanduser()
            scale = load_scl(path)
            with self._lock:
                self._panic()
                self.scala_path = path
                self.scala_scale = scale
                self.tuning_mode = "scala"
                self._publish_tuning_mode()
                self._publish_scala_geometry()
                payload = [scale.description, scale.size, str(path)]
                self._send("/qmw/wilson/tuning/scala/loaded", payload)
                self._send_visual(
                    "/qmw/wilson/tuning/scala/loaded", payload
                )
        except Exception as exc:
            self._error(exc)

    def _osc_scala_save(self, _address: str, value: str) -> None:
        try:
            path = Path(str(value)).expanduser()
            with self._lock:
                scale = self._active_scala_export()
                output = save_scl(path, scale)
                payload = [scale.description, scale.size, str(output)]
                self._send("/qmw/wilson/tuning/scala/saved", payload)
                self._send_visual(
                    "/qmw/wilson/tuning/scala/saved", payload
                )
        except Exception as exc:
            self._error(exc)

    def _publish_tuning_mode(self) -> None:
        scala_name = "" if self.scala_scale is None else self.scala_scale.description
        payload = [
            self.engine.generation,
            self.tuning_mode,
            scala_name,
            *self.tuning_factors,
        ]
        self._send("/qmw/wilson/tuning/mode", payload)
        self._send_visual("/qmw/wilson/tuning/mode", payload)

    def _mode_ratio_for_basis(self, basis: int) -> tuple[float, float]:
        base_ratio = float(basis_product(basis, self.tuning_factors))
        if self.tuning_mode == "diamond":
            return diamond_ratio(basis, self.tuning_factors), 1.0
        if self.tuning_mode == "mos":
            return mos_morph_projection(base_ratio, self.mos_navigator.frame())
        if self.tuning_mode == "scala":
            if self.scala_scale is None:
                raise RuntimeError("Scala mode has no loaded scale")
            return project_ratio_to_scala(base_ratio, self.scala_scale), 1.0
        return base_ratio, 1.0

    def _active_scala_export(self) -> ScalaScale:
        if self.tuning_mode == "scala" and self.scala_scale is not None:
            return self.scala_scale
        if self.tuning_mode == "equal":
            ratios = tuple(2.0 ** (step / 12.0) for step in range(13))
        else:
            ratios = tuple(self._mode_ratio_for_basis(basis)[0] for basis in range(16))
        factors = "-".join(str(factor) for factor in self.tuning_factors)
        return scala_scale_from_ratios(
            ratios,
            description=f"QMW {self.tuning_mode} factors {factors}",
        )

    def _publish_scala_geometry(self) -> None:
        if self.scala_scale is None:
            return
        self._scala_revision += 1
        revision = self._scala_revision
        scale = self.scala_scale
        degrees = scale.pitch_classes
        path = "" if self.scala_path is None else str(self.scala_path)
        packets: list[tuple[str, list[object]]] = [
            (
                "/qmw/wilson/tuning/scala/begin",
                [
                    revision,
                    self.engine.generation,
                    scale.description,
                    len(degrees),
                    scale.period,
                    path,
                ],
            )
        ]
        for index, ratio in enumerate(degrees):
            token = "1/1" if index == 0 else scale.tokens[index - 1]
            packets.append(
                (
                    "/qmw/wilson/tuning/scala/degree",
                    [revision, index, ratio, 1200.0 * math.log2(ratio), token],
                )
            )
        for basis in range(16):
            harmonic_ratio = float(basis_product(basis, self.tuning_factors))
            degree = project_ratio_index_to_scala(harmonic_ratio, scale)
            packets.append(
                (
                    "/qmw/wilson/tuning/scala/assignment",
                    [revision, basis, degree],
                )
            )
        structure = analyze_scala_constant_structure(scale)
        packets.append(
            (
                "/qmw/wilson/tuning/scala/constant-structure",
                [
                    revision,
                    int(structure.is_constant_structure),
                    structure.interval_class_count,
                    structure.conflicting_class_count,
                    structure.tolerance_cents,
                ],
            )
        )
        packets.append(
            (
                "/qmw/wilson/tuning/scala/end",
                [revision, len(degrees), 16],
            )
        )
        for address, payload in packets:
            self._send(address, payload)
            self._send_visual(address, payload)

    def _retune_from_circuit(self, *, publish: bool = True) -> None:
        self.tuning_frame = circuit_wilson_tuning_frame(self.engine.logical_circuit)
        self.tuning_factors = (
            self.tuning_frame.master_set
            if self.circuit_tuning_enabled
            else WILSON_GENERATORS
        )
        if self.circuit_tuning_enabled:
            target = self.tuning_frame.mos_position
            if target != self.mos_navigator.current:
                self.mos_navigator.begin(target)
                self.mos_navigator.set_progress(1.0)
        if publish:
            self._publish_tuning()
            self._publish_navigation()

    def _publish_tuning(self) -> None:
        if self.tuning_frame is None:
            return
        self._publish_tuning_mode()
        if self.tuning_mode == "scala":
            self._publish_scala_geometry()
        fingerprint = self.tuning_frame.fingerprint
        payload: list[object] = [
            self.engine.generation,
            self.tuning_frame.family,
            int(self.circuit_tuning_enabled),
            self.tuning_frame.mos_position.numerator,
            self.tuning_frame.mos_position.denominator,
            fingerprint.gate_count,
            len(fingerprint.interaction_edges),
            fingerprint.hadamard_count,
            fingerprint.phase_gate_count,
            fingerprint.depth,
            *fingerprint.component_sizes,
            -1,
            *self.tuning_factors,
        ]
        self._send("/qmw/wilson/tuning/frame", payload)
        self._send_visual("/qmw/wilson/tuning/frame", payload)
        vertices = wilson_tuning_vertices(
            self.tuning_factors,
            grade=2,
            anchor_mask=0b0011,
        )
        self._tuning_revision += 1
        revision = self._tuning_revision
        packets: list[tuple[str, list[object]]] = [
            (
                "/qmw/wilson/tuning/begin",
                [revision, self.engine.generation, self.tuning_frame.family, 0b0011, len(vertices)],
            )
        ]
        for vertex in vertices:
            packets.append(
                (
                    "/qmw/wilson/tuning/vertex",
                    [
                        revision,
                        self.engine.generation,
                        vertex.bitmask,
                        vertex.factors[0],
                        vertex.factors[1],
                        vertex.product,
                        vertex.ratio.numerator,
                        vertex.ratio.denominator,
                        vertex.audition_ratio.numerator,
                        vertex.audition_ratio.denominator,
                    ],
                )
            )
        packets.append(
            (
                "/qmw/wilson/tuning/end",
                [revision, self.engine.generation, len(vertices)],
            )
        )
        for address, vertex_payload in packets:
            self._send(address, vertex_payload)
            self._send_visual(address, vertex_payload)

    def _basis_allowed(self, basis: int) -> bool:
        return self.instrument_grade < 0 or int(basis).bit_count() == self.instrument_grade

    def _constant_structure_state(self) -> int:
        if self.instrument_grade in {-1, 0, 4}:
            return -1
        cps = CombinationProductSet(self.tuning_factors, self.instrument_grade)
        ratios = tuple(
            sorted(Fraction(tone.ratio_numerator, tone.ratio_denominator) for tone in cps.tones)
        )
        try:
            return int(validate_constant_structure(ratios).is_constant_structure)
        except ValueError:
            return 0

    def _publish_navigation(self) -> None:
        frame = self.mos_navigator.frame()
        header = [
            self.engine.generation,
            frame.source.numerator,
            frame.source.denominator,
            frame.target.numerator,
            frame.target.denominator,
            frame.progress,
            frame.active_voice_count,
            self.instrument_grade,
            self._constant_structure_state(),
        ]
        packets: list[tuple[str, list[object]]] = [
            ("/qmw/wilson/navigation/frame", header)
        ]
        for voice in frame.voices:
            packets.append(
                (
                    "/qmw/wilson/navigation/voice",
                    [
                        self.engine.generation,
                        voice.voice_id,
                        voice.generator_power,
                        voice.position,
                        voice.ratio,
                        voice.activation,
                        -1 if voice.source_order is None else voice.source_order,
                        -1 if voice.target_order is None else voice.target_order,
                    ],
                )
            )
        packets.append(
            ("/qmw/wilson/navigation/end", [self.engine.generation, len(frame.voices)])
        )
        for address, payload in packets:
            self._send(address, payload)
            self._send_visual(address, payload)

    def _cancel_flow_timers(self) -> None:
        for timer in self._flow_timers:
            timer.cancel()
        self._flow_timers.clear()

    def start(self) -> None:
        super().start()
        with self._lock:
            self._publish_tuning()
            self._publish_navigation()

    def _panic(self) -> None:
        """Stop notes on the exact member channels allocated to them."""
        now = time.monotonic()
        with self._mpe_channel_lock:
            active_notes = list(self._mpe_active_notes)
            self._mpe_active_notes.clear()
            for channel in MPE_MEMBER_CHANNELS:
                self._mpe_busy_until[channel] = now
        for _deadline, basis, channel in active_notes:
            self._send(
                "/qmw/recursive/cps_flow_note",
                self._basis_note_payload(
                    generation=self.engine.generation,
                    role=3,
                    basis=basis,
                    partner=basis,
                    velocity=0,
                    duration_ms=1,
                    strength=0.0,
                    theta=0.0,
                    beta=0.0,
                    phase=0.0,
                    channel=channel,
                ),
            )

    def _allocate_mpe_channel(
        self,
        *,
        basis: int,
        hold_ms: int,
    ) -> int:
        """Allocate one of the fifteen MPE member channels to a sounding event."""
        now = time.monotonic()
        with self._mpe_channel_lock:
            self._mpe_active_notes = [
                entry for entry in self._mpe_active_notes if entry[0] > now
            ]
            chosen = None
            for offset in range(len(MPE_MEMBER_CHANNELS)):
                index = (self._mpe_channel_cursor + offset) % len(MPE_MEMBER_CHANNELS)
                candidate = MPE_MEMBER_CHANNELS[index]
                if self._mpe_busy_until[candidate] <= now:
                    chosen = candidate
                    self._mpe_channel_cursor = (index + 1) % len(MPE_MEMBER_CHANNELS)
                    break
            if chosen is None:
                # This can occur only if more than fifteen notes overlap.  The
                # current instrument emits at most four arrivals per step, but
                # choosing the earliest release gives deterministic voice stealing.
                chosen = min(MPE_MEMBER_CHANNELS, key=self._mpe_busy_until.get)
                self._mpe_active_notes = [
                    entry for entry in self._mpe_active_notes if entry[2] != chosen
                ]
                self._mpe_channel_cursor = (
                    MPE_MEMBER_CHANNELS.index(chosen) + 1
                ) % len(MPE_MEMBER_CHANNELS)
            deadline = now + max(1, int(hold_ms)) / 1000.0 + 0.02
            self._mpe_busy_until[chosen] = deadline
            self._mpe_active_notes.append((deadline, int(basis), chosen))
            return chosen

    def _osc_reset(self, _address: str, *_args: object) -> None:
        """CLEAR/RESET means empty circuit and silence in v5."""
        try:
            self.stop_recursion()
            with self._lock:
                self._cancel_flow_timers()
                self._panic()
                self.engine.clear_circuit()
                self.circuit_active = False
                self.last_flow_strength = 0.0
                self._retune_from_circuit()
                self._publish_state(publish_circuit=True)
        except Exception as exc:
            self._error(exc)

    def _osc_seed(self, _address: str, value: int) -> None:
        """Change the recursive RNG without replacing the loaded circuit."""
        try:
            with self._lock:
                self.engine.configure(seed=int(value))
                self._publish_state(publish_circuit=False)
        except Exception as exc:
            self._error(exc)

    def _publish_state(self, *, publish_circuit: bool) -> None:
        """Publish legacy geometry packets plus one atomic sixteen-state frame."""
        super()._publish_state(publish_circuit=publish_circuit)
        amplitudes = self.engine.state.data
        probabilities = [float(abs(amplitude) ** 2) for amplitude in amplitudes]
        phases = [float(math.atan2(amplitude.imag, amplitude.real)) for amplitude in amplitudes]
        grades = pascal_grade_probabilities(self.engine.state)
        self._send_visual(
            "/qmw/wilson/state16",
            [self.engine.generation, *probabilities, *phases, *grades],
        )
        modulation = state_modulation_metrics(
            self.engine.state,
            flow_strength=self.last_flow_strength,
        )
        self._send(
            "/qmw/recursive/modulation",
            [self.engine.generation, *modulation],
        )
        self._send_visual(
            "/qmw/wilson/modulation",
            [self.engine.generation, *modulation],
        )

    def _osc_qasm_begin(self, address: str, revision: int, total: int) -> None:
        self.stop_recursion()
        with self._lock:
            self._cancel_flow_timers()
            self._panic()
            self.circuit_active = False
            self.last_flow_strength = 0.0
        super()._osc_qasm_begin(address, revision, total)

    def _osc_qasm_end(self, address: str, revision: int) -> None:
        """Load the circuit, then articulate its occupied-state fingerprint."""
        super()._osc_qasm_end(address, revision)
        if self._qasm_transfer is None and self.engine.logical_circuit.data:
            self.circuit_active = True
            self._retune_from_circuit()
            self._publish_state_signature()

    def _publish_state_signature(self) -> None:
        """Audition final populations after a bulk Bell/GHZ/QASM load.

        The flow instrument otherwise has no event at QASM commit time. A
        short population signature makes different prepared circuits audible
        without turning the final state into a continuous background drone.
        """
        amplitudes = self.engine.state.data
        for basis, amplitude in enumerate(amplitudes):
            if not self._basis_allowed(basis):
                continue
            probability = float(abs(amplitude) ** 2)
            if probability <= 1e-9:
                continue
            phase = float(math.atan2(amplitude.imag, amplitude.real))
            self._send(
                "/qmw/recursive/cps_flow_note",
                self._basis_note_payload(
                    generation=self.engine.generation,
                    role=4,
                    basis=basis,
                    partner=basis,
                    velocity=max(1, min(127, int(round(118 * math.sqrt(probability))))),
                    duration_ms=max(180, min(650, self.interval_ms + 120)),
                    strength=probability,
                    theta=0.0,
                    beta=0.0,
                    phase=phase,
                ),
            )

    def _basis_note_payload(
        self,
        *,
        generation: int,
        role: int,
        basis: int,
        partner: int,
        velocity: int,
        duration_ms: int,
        strength: float,
        theta: float,
        beta: float,
        phase: float,
        channel: int | None = None,
        channel_hold_ms: int | None = None,
    ) -> list[object]:
        ratio, mos_activation = self._mode_ratio_for_basis(basis)
        note, bend, sounding_ratio = basis_midi(
            basis,
            self.tuning_factors,
            ratio_override=ratio,
        )
        if self.tuning_mode == "equal":
            bend = 8192
        velocity = max(1, min(127, int(round(velocity * mos_activation))))
        if channel is None:
            channel = self._allocate_mpe_channel(
                basis=basis,
                hold_ms=duration_ms if channel_hold_ms is None else channel_hold_ms,
            )
        cc74 = int(round((phase + math.pi) * 127 / (2 * math.pi)))
        fractional_pitch = (
            float(note)
            if self.tuning_mode == "equal"
            else 36.0
            + 12.0 * int(basis).bit_count()
            + 12.0 * math.log2(sounding_ratio)
        )
        frequency_hz = 440.0 * 2.0 ** ((fractional_pitch - 69.0) / 12.0)
        return [
            generation,
            role,
            basis,
            note,
            velocity,
            duration_ms,
            strength,
            theta,
            beta,
            phase,
            bend,
            max(0, min(127, cc74)),
            channel,
            partner,
            sounding_ratio,
            frequency_hz,
        ]

    def _publish_basis_flows(
        self,
        flows: tuple[BasisFlow, ...],
        *,
        generation: int,
        theta: float,
        beta: float,
    ) -> None:
        audible_flows = []
        for flow in flows[: self.max_flows_per_step]:
            departure_allowed = self._basis_allowed(flow.source_basis_index)
            arrival_allowed = self._basis_allowed(flow.destination_basis_index)
            if self.flow_articulation == "arrival" and not arrival_allowed:
                continue
            if self.flow_articulation != "arrival" and not (departure_allowed or arrival_allowed):
                continue
            audible_flows.append((flow, departure_allowed, arrival_allowed))

        peak_strength = min(
            1.0,
            max((flow.probability_flow for flow, _, _ in audible_flows), default=0.0),
        )
        for flow, departure_allowed, arrival_allowed in audible_flows:
            strength = min(1.0, flow.probability_flow)
            arrival_velocity = probability_current_velocity(strength, peak_strength)
            departure_velocity = max(8, int(round(arrival_velocity * 0.52)))
            travel_ms = int(round(24 + 180 * min(1.0, abs(theta) / math.pi)))
            duration_ms = max(70, min(self.interval_ms, travel_ms + 80))
            phase = math.atan2(
                math.sin(flow.relative_phase + beta),
                math.cos(flow.relative_phase + beta),
            )
            def flow_payload(
                *,
                role: int,
                basis: int,
                partner: int,
                velocity: int,
                channel_hold_ms: int | None = None,
            ) -> list[object]:
                return self._basis_note_payload(
                    generation=generation,
                    role=role,
                    basis=basis,
                    partner=partner,
                    velocity=velocity,
                    duration_ms=duration_ms,
                    strength=strength,
                    theta=theta,
                    beta=beta,
                    phase=phase,
                    channel_hold_ms=channel_hold_ms,
                )
            self._send_visual(
                "/qmw/wilson/flow",
                [
                    generation,
                    flow.source_basis_index,
                    flow.destination_basis_index,
                    strength,
                    theta,
                    beta,
                    phase,
                ],
            )
            if self.flow_articulation == "arrival":
                # A single immediate destination attack exposes harmonic and
                # circuit differences without imposing a grace-note rhythm.
                self._send(
                    "/qmw/recursive/cps_flow_note",
                    flow_payload(
                        role=1,
                        basis=flow.destination_basis_index,
                        partner=flow.source_basis_index,
                        velocity=arrival_velocity,
                    ),
                )
            elif self.flow_articulation == "dyad":
                if departure_allowed:
                    self._send(
                        "/qmw/recursive/cps_flow_note",
                        flow_payload(
                            role=0,
                            basis=flow.source_basis_index,
                            partner=flow.destination_basis_index,
                            velocity=departure_velocity,
                        ),
                    )
                if arrival_allowed:
                    self._send(
                        "/qmw/recursive/cps_flow_note",
                        flow_payload(
                            role=1,
                            basis=flow.destination_basis_index,
                            partner=flow.source_basis_index,
                            velocity=arrival_velocity,
                        ),
                    )
            else:
                # Historical source→destination gesture: useful when desired,
                # but no longer the default articulation of every event.
                if departure_allowed:
                    departure = flow_payload(
                        role=0,
                        basis=flow.source_basis_index,
                        partner=flow.destination_basis_index,
                        velocity=departure_velocity,
                    )
                    self._send("/qmw/recursive/cps_flow_note", departure)
                if arrival_allowed:
                    arrival = flow_payload(
                        role=1,
                        basis=flow.destination_basis_index,
                        partner=flow.source_basis_index,
                        velocity=arrival_velocity,
                        channel_hold_ms=travel_ms + duration_ms,
                    )
                    timer = threading.Timer(
                        travel_ms / 1000.0,
                        self._send,
                        args=("/qmw/recursive/cps_flow_note", arrival),
                    )
                    timer.daemon = True
                    timer.start()
                    self._flow_timers.append(timer)
        self._flow_timers = [timer for timer in self._flow_timers if timer.is_alive()]

    def _publish_phase_gate(self, gate: str, qubit: int) -> None:
        angle = PHASE_ANGLES[gate]
        probabilities = [abs(amplitude) ** 2 for amplitude in self.engine.state.data]
        candidates = [basis for basis in range(16) if (basis >> qubit) & 1]
        candidates = [basis for basis in candidates if self._basis_allowed(basis)]
        if not candidates:
            return
        basis = max(candidates, key=lambda index: probabilities[index])
        occupied_probability = float(probabilities[basis])
        if occupied_probability <= 1e-12:
            return
        strength = occupied_probability * abs(angle) / math.pi
        payload = self._basis_note_payload(
            generation=self.engine.generation,
            role=2,
            basis=basis,
            partner=basis,
            velocity=max(8, min(127, int(round(28 + 99 * math.sqrt(strength))))),
            duration_ms=110,
            strength=strength,
            theta=0.0,
            beta=angle,
            phase=angle,
        )
        self._send("/qmw/recursive/cps_flow_note", payload)
        self._send_visual(
            "/qmw/wilson/phase",
            [self.engine.generation, basis, strength, angle],
        )

    def _publish_flow(self, step) -> None:
        self._publish_basis_flows(
            step.basis_flows,
            generation=step.generation,
            theta=step.theta,
            beta=step.beta,
        )

    def _apply_intervention(self, gate: str, qubits: tuple[int, ...]) -> None:
        gate = str(gate).lower()
        with self._lock:
            flows = self.engine.apply_gate(gate, qubits)
            self.circuit_active = True
            self.last_flow_strength = min(
                1.0, max((flow.probability_flow for flow in flows), default=0.0)
            )
            self._retune_from_circuit()
            self._publish_state(publish_circuit=True)
            if flows:
                self._publish_basis_flows(
                    flows,
                    generation=self.engine.generation,
                    theta=math.pi / 2,
                    beta=0.0,
                )
            elif gate in PHASE_ANGLES:
                self._publish_phase_gate(gate, int(qubits[0]))

    def advance(self) -> None:
        with self._lock:
            # An empty programmer remains silent.  Once a circuit is active,
            # temperature samples the complete 16-vertex Boolean/CPS lattice;
            # high temperature approaches Pascal multiplicities 1:4:6:4:1.
            step = (
                self.engine.next_complete_cps()
                if self.circuit_active
                else self.engine.next()
            )
            flows = step.basis_flows
            motion = step.motion
            # The complete Boolean/CPS lattice needs both tangent motion
            # within a Pascal grade and transverse motion between grades.
            # GHZ's |0000> and |1111> poles are fixed points of XY exchange;
            # use a deterministic H step only for a committed circuit whose
            # exchange current is zero. An actually empty circuit stays mute.
            if self.circuit_active and motion == "XY" and not flows:
                transverse_qubit = (step.generation - 1) % 4
                flows = self.engine.apply_gate("h", (transverse_qubit,))
                motion = f"H-fallback(q{transverse_qubit})"
            self.last_flow_strength = min(
                1.0, max((flow.probability_flow for flow in flows), default=0.0)
            )
            self._publish_state(
                publish_circuit=(step.generation <= self.full_circuit_generation_limit)
            )
            self._send_visual(
                "/qmw/wilson/pascal_step",
                [
                    step.generation,
                    step.selected_basis,
                    step.selected_grade,
                    motion,
                    *step.grade_probabilities,
                ],
            )
            self._publish_navigation()
            self._publish_basis_flows(
                flows,
                generation=step.generation,
                theta=math.pi / 2 if motion.startswith("H") else step.theta,
                beta=step.beta,
            )
        strongest = flows[0].probability_flow if flows else 0.0
        grade_text = (
            f" grade={step.selected_grade} vertex={step.selected_basis:04b}"
            if step.selected_basis >= 0
            else ""
        )
        print(
            f"complete-CPS generation={step.generation} {motion} {step.qubits}{grade_text} "
            f"current={strongest:.6f} shell={step.shell_probability:.6f}"
        )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--control-port", type=int, default=7403)
    parser.add_argument("--max-port", type=int, default=7410)
    parser.add_argument("--visual-port", type=int, default=7411)
    parser.add_argument("--supercollider-port", type=int, default=57120)
    parser.add_argument("--seed", type=int, default=23)
    parser.add_argument("--temperature", type=float, default=0.65)
    parser.add_argument("--max-depth", type=int, default=32)
    parser.add_argument("--interval-ms", type=int, default=240)
    parser.add_argument("--max-flows-per-step", type=int, default=4)
    parser.add_argument(
        "--flow-articulation",
        choices=("arrival", "dyad", "gesture"),
        default="arrival",
    )
    parser.add_argument(
        "--tuning-mode",
        choices=TUNING_MODES,
        default="cps",
    )
    parser.add_argument("--scala-file", type=Path)
    args = parser.parse_args()
    host = CompleteCPSFlowMaxHost(
        control_port=args.control_port,
        max_port=args.max_port,
        visual_port=args.visual_port,
        supercollider_port=args.supercollider_port,
        seed=args.seed,
        temperature=args.temperature,
        max_depth=args.max_depth,
        interval_ms=args.interval_ms,
        max_flows_per_step=args.max_flows_per_step,
        flow_articulation=args.flow_articulation,
        tuning_mode=args.tuning_mode,
        scala_file=args.scala_file,
    )
    stop_event = threading.Event()
    signal.signal(signal.SIGINT, lambda *_args: stop_event.set())
    signal.signal(signal.SIGTERM, lambda *_args: stop_event.set())
    host.start()
    print("QMW complete CPS flow instrument v5 ready")
    stop_event.wait()
    host.stop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
