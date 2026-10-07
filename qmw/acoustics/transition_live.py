"""Live controls over paired QMW snapshots; musical scheduling stays downstream.

Reuses the note/body snapshot, queue, geometry, and pitch contracts. No source
state or Hamiltonian is changed. Every wire packet is a complete observation.
"""
from dataclasses import asdict, dataclass, replace, field
import hashlib
import json
from threading import Lock

import numpy as np

from qmw.core.transition import TransitionEngine, readonly
from qmw.acoustics.note_timbre import QuantumTimbreProjector, TransitionPitchProjector, RatioField
from qmw.acoustics.note_timbre_live import SourceSnapshot, LatestSnapshotSlot, LiveWorker, make_geometry, RATIOS

from qmw.acoustics.transition_harmony import chord_matrix, HARMONY_COUNT, validate_harmony_arguments

FRAME_ADDRESS = "/qmw/transitions/v3/frame"
CONTROL_ADDRESS = "/qmw/transitions/v2/config"
FRAME_PORT, CONTROL_PORT = 17934, 17935
HEADER_COUNT, BODY_COUNT, CELL_FIELDS, DIMENSION = 24, 64, 6, 16
MATRIX_END = HEADER_COUNT + BODY_COUNT + CELL_FIELDS * DIMENSION**2
ARGUMENT_COUNT = MATRIX_END + 2  # timing mode and candidate count
CANDIDATE_FIELDS = 5  # source, target, pitch Hz, diagnostic strength, duration


@dataclass(frozen=True)
class TransitionControls:
    revision: int = 0
    scope: int = 0  # local, collective mean, adjacent pair
    qubit: int = 0
    axis: int = 2  # X,Y,Z
    blend: float = 0.0  # primary axis -> next cyclic axis
    amplitude_threshold: float = 1e-8
    activity_threshold: float = 1e-8
    hold: bool = False
    selection: int = 0  # strongest, cycle, selected cell
    source: int = 0
    target: int = 1
    rate_hz: float = 2.0  # musical wall-clock rate cap
    base_hz: float = 220.0
    octave: int = 0
    duration: float = .25
    voices: int = 4
    basis: int = 0
    excitation: int = 1  # broad strike or pitched note
    timing: int = 0  # independent pulse / follow rendered QMW events

    def __post_init__(self):
        for name, lo, hi in [("revision", 0, 2**30), ("scope", 0, 2), ("qubit", 0, 3),
                             ("axis", 0, 2), ("selection", 0, 2), ("source", 0, 15),
                             ("target", 0, 15), ("octave", -2, 2), ("voices", 1, 8),
                             ("basis", 0, 1), ("excitation", 0, 1), ("timing", 0, 1)]:
            value = getattr(self, name)
            if type(value) is not int or not lo <= value <= hi:
                raise ValueError(f"{name} must be an integer in [{lo}, {hi}]")
        for name, lo, hi in [("blend", 0, 1), ("amplitude_threshold", 0, 1),
                             ("activity_threshold", 0, 1), ("rate_hz", .25, 10),
                             ("base_hz", 55, 880), ("duration", .01, 2)]:
            value = getattr(self, name)
            if isinstance(value, bool) or not np.isfinite(value) or not lo <= value <= hi:
                raise ValueError(f"{name} must be finite in [{lo}, {hi}]")
        if type(self.hold) is not bool:
            raise ValueError("hold must be boolean")

    def arguments(self):
        return [int(value) if isinstance(value, bool) else value for value in asdict(self).values()]

    @classmethod
    def from_arguments(cls, args):
        if len(args) not in (18, 19) or type(args[7]) is not int or args[7] not in (0, 1):
            raise ValueError("configuration requires 18 or 19 atomic values with a 0/1 hold flag")
        values = list(args)
        values[7] = bool(values[7])
        return cls(*values)


def observable_for(controls):
    """Hermitian convex blend. Collective mean keeps operator norm <= 1.

    Qubit 0 is least significant; strings read q3..q0. An adjacent pair uses
    the selected qubit and (qubit+1) modulo four, with the same Pauli axis.
    """
    def component(axis):
        labels = []
        for qubit in (range(4) if controls.scope == 1 else [controls.qubit]):
            chars = list("IIII")
            chars[3-qubit] = "XYZ"[axis]
            if controls.scope == 2:
                chars[3-((qubit+1) % 4)] = "XYZ"[axis]
            labels.append("".join(chars))
        pauli = {"I": np.eye(2), "X": np.array([[0, 1], [1, 0]]),
                 "Y": np.array([[0, -1j], [1j, 0]]), "Z": np.diag([1., -1.])}
        result = np.zeros((16, 16), complex)
        for label in labels:
            matrix = np.ones((1, 1))
            for char in label:
                matrix = np.kron(matrix, pauli[char])
            result += matrix / len(labels)
        return result, ("mean("+"+".join(labels)+")" if len(labels) > 1 else labels[0])
    first, label = component(controls.axis)
    second, next_label = component((controls.axis+1) % 3)
    blend = controls.blend
    name = label if blend == 0 else next_label if blend == 1 else f"{1-blend:.3f}*{label}+{blend:.3f}*{next_label}"
    return readonly((1-blend)*first + blend*second), name


@dataclass(frozen=True)
class TransitionPacket:
    sequence: int
    observed_revision: int
    config: TransitionControls
    snapshot: SourceSnapshot
    frame: object
    body: object
    note: object
    candidates: tuple = ()  # descriptors, never independent onsets

    harmony: object = field(init=False)

    def __post_init__(self):
        object.__setattr__(self, "harmony", chord_matrix(self.snapshot.rho,self.frame,
                           base_hz=self.config.base_hz,octave=self.config.octave))

    @property
    def source_digest(self):
        return hashlib.sha256(self.snapshot.H.tobytes()+self.snapshot.rho.tobytes()).hexdigest()

    def arguments(self):
        note, cfg, frame, source = self.note, self.config, self.frame, self.snapshot
        args = [3, source.session_id, self.sequence, self.observed_revision, source.context.frame_id,
                source.context.time, cfg.revision, int(cfg.hold), source.operator_label,
                len(frame.transitions), note.source_state if note else -1, note.target_state if note else -1,
                note.target_frequency_hz if note else 0., note.strength if note else 0.,
                note.duration_seconds if note else 0., cfg.excitation, cfg.voices, cfg.rate_hz,
                frame.spectrum.purity, frame.spectrum.entropy, frame.diagnostics["trace_error_abs"],
                frame.diagnostics["minimum_density_eigenvalue"], self.source_digest, frame.units.hbar]
        for row in zip(self.body.frequencies_hz, self.body.amplitude_gains,
                       self.body.decay_seconds, self.body.acoustic_phases_rad):
            args.extend(float(value) for value in row)
        cells = np.stack([frame.A_E.real, frame.A_E.imag, frame.rho_E.real, frame.rho_E.imag,
                          frame.delta_E, frame.diagnostic_activity], axis=-1)
        args.extend(cells.ravel().tolist())
        args.extend([cfg.timing, len(self.candidates)])
        for candidate in self.candidates:
            args.extend([candidate.source_state, candidate.target_state,
                         candidate.target_frequency_hz, candidate.strength,
                         candidate.duration_seconds])
        args.extend(self.harmony.arguments())
        return args

    def audit(self, *, full=False):
        result = {"schema": "qmw.transitions.audit.v3", "session": self.snapshot.session_id,
                  "sequence": self.sequence, "observed_revision": self.observed_revision,
                  "source_revision": self.snapshot.context.frame_id, "source_time": self.snapshot.context.time,
                  "config": asdict(self.config), "source_H_rho_sha256": self.source_digest,
                  "timing_source": "rendered_qmw_event" if self.config.timing else "independent_wall_clock",
                  "candidate_count": len(self.candidates),
                  "harmony": self.harmony.audit(),
                  "onset_policy": "SC QMW render callback; see transition-onsets TSV" if self.config.timing else "bounded independent pulse",
                  "operator": self.snapshot.operator_label, "eligible": len(self.frame.transitions),
                  "diagnostics": dict(self.frame.diagnostics), "provenance": self.frame.provenance,
                  "note": None if self.note is None else {
                      "source": self.note.source_state, "target": self.note.target_state,
                      "frequency_hz": self.note.target_frequency_hz, "strength": self.note.strength,
                      "duration": self.note.duration_seconds, "event_id": self.note.event_id}}
        if full:
            result["matrices"] = {name: {"real": value.real.tolist(), "imag": value.imag.tolist()}
                                  for name, value in [("H", self.snapshot.H), ("rho", self.snapshot.rho),
                                                      ("A", self.snapshot.A), ("rho_E", self.frame.rho_E),
                                                      ("A_E", self.frame.A_E)]}
            result["arguments"] = self.arguments()
        return result


class TransitionProjector:
    def __init__(self, config=None):
        self.config = config or TransitionControls()
        self._lock = Lock()
        self._held = None
        self._sequence = 0
        self._next_event = -np.inf
        self._last_event_at = -np.inf
        self._cycle = 0
        self._last_now = -np.inf
        self.timbres = QuantumTimbreProjector()

    def configure(self, config):
        with self._lock:
            if config.revision <= self.config.revision:
                return False
            if not config.hold or not self.config.hold:
                self._held = None
            self.config = config
            self._next_event = self._last_event_at + 1/config.rate_hz
            self._cycle = 0
            return True

    def process(self, snapshot, *, now):
        if not np.isfinite(now) or now < self._last_now:
            raise ValueError("musical clock must be finite and nondecreasing")
        with self._lock:
            self._last_now = now
            cfg = self.config
            if cfg.hold and self._held is None:
                self._held = snapshot
            raw = self._held if cfg.hold else snapshot
            a, label = observable_for(cfg)
            context = replace(raw.context, provenance=tuple(item for item in raw.context.provenance
                              if not item.startswith("declared diagnostic coupling:")) +
                              (f"observer operator:{label};revision:{cfg.revision}",))
            source = replace(raw, A=a, context=context, operator_label=label, operator_revision=cfg.revision)
            frame = TransitionEngine(amplitude_threshold=cfg.amplitude_threshold,
                                     activity_threshold=cfg.activity_threshold).compute(
                                         source.H, source.rho, a, context.time, context=context)
            # Reuse the existing musical projector, with only admitted edges.
            notes = TransitionPitchProjector(
                state_degrees=tuple(j % 5 + 5*cfg.octave for j in range(16)),
                ratio_field=RatioField(RATIOS, reference_hz=cfg.base_hz, name="transition_panel_just_five"),
                min_activity=0, duration_seconds=(cfg.duration if cfg.excitation else .001),
            ).process(replace(frame, edges=frame.transitions))
            if cfg.selection == 2:
                notes = tuple(note for note in notes if (note.source_state, note.target_state) == (cfg.source, cfg.target))
            candidates = ()
            if cfg.timing and notes:
                candidates = (tuple(notes) if cfg.selection == 1 else
                              (min(notes, key=lambda item: (-item.strength, item.source_state, item.target_state)),))
            note = None
            if not cfg.timing and notes and now >= self._next_event:
                note = (notes[self._cycle % len(notes)] if cfg.selection == 1 else
                        min(notes, key=lambda item: (-item.strength, item.source_state, item.target_state)))
                self._cycle += 1
                self._last_event_at = now
                self._next_event = now + 1/cfg.rate_hz
            body = self.timbres.process(rho=source.rho, geometry_modes=make_geometry(("identity", "fourier")[cfg.basis]),
                                       context=context)
            self._sequence += 1
            return TransitionPacket(self._sequence, snapshot.context.frame_id, cfg, source, frame, body, note, candidates)


class TransitionWorker(LiveWorker):
    """Reuse latest-only queue and worker shutdown; all analysis is off source thread."""
    def __init__(self, *, sender, config=None, error_handler=print):
        super().__init__(sender=sender, error_handler=error_handler)
        self.projector = TransitionProjector(config)


def validate_arguments(args):
    """Complete-packet numerical contract, also exercised through OSC on the wire."""
    if len(args) < ARGUMENT_COUNT+HARMONY_COUNT or args[0] != 3:
        raise ValueError("wrong frame schema or length")
    strings = {1, 8, 22}
    if any(not isinstance(args[i], str) or not args[i] for i in strings):
        raise ValueError("frame identity must be text")
    if any(not isinstance(value, (int, float)) or not np.isfinite(value)
           for index, value in enumerate(args) if index not in strings):
        raise ValueError("frame contains nonfinite numeric fields")
    for index in (2, 3, 4, 6, 9):
        if args[index] < 0 or args[index] != int(args[index]):
            raise ValueError("invalid revision or transition count")
    if args[4] > args[3] or args[9] > 240 or args[23] != 1 or len(args[22]) != 64:
        raise ValueError("invalid source metadata")
    if args[7] not in (0, 1) or args[15] not in (0, 1) or args[16] not in range(1, 9):
        raise ValueError("invalid controls")
    if not .25 <= args[17] <= 10:
        raise ValueError("invalid event-rate cap")
    if args[10] == -1:
        if args[11] != -1 or args[12] != 0 or args[13] != 0 or args[14] != 0:
            raise ValueError("invalid no-note sentinel")
    else:
        if any(args[i] != int(args[i]) or not 0 <= args[i] < 16 for i in (10, 11)) or args[10] == args[11]:
            raise ValueError("invalid note endpoints")
        if not 0 < args[12] < 18000 or not 0 < args[13] <= 1.000001 or not .001 <= args[14] <= 2:
            raise ValueError("invalid note parameters")
    body = np.asarray(args[24:88]).reshape(16, 4)
    if (np.any(body[:, 0] <= 0) or np.any(body[:, 0] >= 18000) or
        np.any(body[:, 1] < 0) or np.any(body[:, 1] > 1.000001) or
        np.any(body[:, 2] <= 0) or np.any(body[:, 2] > 2) or np.any(body[:, 3] != 0)):
        raise ValueError("invalid modal body")
    if np.any(np.asarray(args[88:MATRIX_END]).reshape(16, 16, 6)[:, :, 5] < 0):
        raise ValueError("negative diagnostic activity")
    mode, count = args[MATRIX_END:ARGUMENT_COUNT]
    if mode not in (0, 1) or count != int(count) or not 0 <= count <= 240:
        raise ValueError("invalid timing/candidate metadata")
    if len(args) != ARGUMENT_COUNT + CANDIDATE_FIELDS * count + HARMONY_COUNT:
        raise ValueError("incomplete candidate list")
    if (mode == 1 and args[10] != -1) or (mode == 0 and count != 0):
        raise ValueError("timing modes cannot create competing onsets")
    seen = set()
    candidate_end=ARGUMENT_COUNT+CANDIDATE_FIELDS*int(count)
    validate_harmony_arguments(args[candidate_end:])
    for i in range(ARGUMENT_COUNT, candidate_end, CANDIDATE_FIELDS):
        n, m, hz, strength, duration = args[i:i+CANDIDATE_FIELDS]
        if (n != int(n) or m != int(m) or not 0 <= n < 16 or not 0 <= m < 16 or n == m
                or not 0 < hz < 18000 or not 0 < strength <= 1.000001 or not .001 <= duration <= 2):
            raise ValueError("invalid candidate descriptor")
        if (n, m) in seen:
            raise ValueError("duplicate candidate")
        seen.add((n, m))
        if not np.isclose(strength, args[88 + (int(m)*16+int(n))*6 + 5], rtol=1e-5, atol=1e-12):
            raise ValueError("candidate strength must match diagnostic activity")
    return True
