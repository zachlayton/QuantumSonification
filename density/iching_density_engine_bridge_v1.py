"""Live, causal bridge from I Ching network frames to DensityMatrixEngine.

OSC callbacks only stage and validate candidates.  ``step`` must be called by
the density engine's existing state-owning simulation thread; it commits the
new density state and activates the projected phase Hamiltonian atomically.
"""
from __future__ import annotations

from dataclasses import dataclass, field
import math
import queue
import threading
from typing import Callable

import numpy as np

from density.density_state_injection import (
    qac_lsb_to_engine_density,
    validate_density_matrix,
)

NETWORK_ROOT = "/qmw/iching/network"
VISIBLE_LINE_QUBITS = (0, 2, 3, 5)
HEXAGRAM_DIMENSION = 64
DENSITY_DIMENSION = 16
EXPECTED_EDGES = 64 * 6 // 2
EXPECTED_FLUXES = 6 * 5 // 2


class IChingBridgeError(ValueError):
    """An I Ching frame is stale, incomplete, inconsistent, or unphysical."""


@dataclass
class _Candidate:
    revision: int
    seed: int
    reading: tuple[int, int, int, int] | None = None
    metrics: tuple[float, float, float] | None = None
    primary_phase: tuple[float, float] | None = None
    pauli: tuple[str, float] | None = None
    line_phases: dict[int, tuple[float, float, float]] = field(default_factory=dict)
    edges: dict[tuple[int, int], tuple[int, float, float]] = field(default_factory=dict)
    fluxes: dict[tuple[int, int], tuple[float, float]] = field(default_factory=dict)
    density_real_rows: dict[int, np.ndarray] = field(default_factory=dict)
    density_imag_rows: dict[int, np.ndarray] = field(default_factory=dict)


@dataclass(frozen=True)
class CommittedIChingFrame:
    revision: int
    seed: int
    primary: int
    moving_mask: int
    transformed: int
    change_register: int
    mutual_information_bits: float
    change_entropy_bits: float
    source_density_purity: float
    primary_phase_radians: float
    primary_path_strength: float
    pauli_operator: str
    pauli_expectation: float
    density_q0_lsb: np.ndarray
    magnetic_laplacian_64: np.ndarray
    hamiltonian_16: np.ndarray


def visible_hexagram_index(hexagram: int) -> int:
    """Pack line qubits (0,2,3,5) into q0-LSB four-qubit order."""
    return sum(((int(hexagram) >> source_q) & 1) << target_q
               for target_q, source_q in enumerate(VISIBLE_LINE_QUBITS))


def hexagram_projection() -> np.ndarray:
    """Isometric coarse-graining from 16 visible states into 64 hexagrams."""
    projection = np.zeros((HEXAGRAM_DIMENSION, DENSITY_DIMENSION), dtype=np.float64)
    # Four hexagrams share each visible state; 1/sqrt(4) makes P^dagger P = I.
    for hexagram in range(HEXAGRAM_DIMENSION):
        projection[hexagram, visible_hexagram_index(hexagram)] = 0.5
    return projection


def project_laplacian_to_hamiltonian(laplacian: np.ndarray) -> np.ndarray:
    """Project L64, remove global energy, and normalize spectral radius."""
    matrix = np.asarray(laplacian, dtype=np.complex128)
    if matrix.shape != (64, 64):
        raise IChingBridgeError(f"Expected a 64x64 Laplacian; got {matrix.shape}")
    if not np.allclose(matrix, matrix.conj().T, atol=1e-9):
        raise IChingBridgeError("Magnetic Laplacian is not Hermitian")
    projection = hexagram_projection()
    projected = projection.conj().T @ matrix @ projection
    projected = (projected + projected.conj().T) / 2
    projected -= np.trace(projected).real / DENSITY_DIMENSION * np.eye(DENSITY_DIMENSION)
    radius = float(np.max(np.abs(np.linalg.eigvalsh(projected))))
    if radius > 1e-12:
        projected /= radius
    return projected


def adjacency_and_laplacian(edges: dict[tuple[int, int], tuple[int, float, float]]):
    if len(edges) != EXPECTED_EDGES:
        raise IChingBridgeError(f"Expected {EXPECTED_EDGES} graph edges; got {len(edges)}")
    adjacency = np.zeros((64, 64), dtype=np.complex128)
    for (source, target), (line, weight, phase) in edges.items():
        if not (0 <= source < target < 64):
            raise IChingBridgeError(f"Invalid canonical edge {source}->{target}")
        if target != source ^ (1 << (line - 1)):
            raise IChingBridgeError("Edge line does not match its hexagram transition")
        if not (math.isfinite(weight) and weight >= 0 and math.isfinite(phase)):
            raise IChingBridgeError("Edge weight/phase must be finite and weight non-negative")
        value = weight * np.exp(1j * phase)
        adjacency[source, target] = value
        adjacency[target, source] = value.conjugate()
    degree = np.sum(np.abs(adjacency), axis=1)
    laplacian = np.diag(degree) - adjacency
    if np.linalg.eigvalsh(laplacian).min() < -1e-9:
        raise IChingBridgeError("Magnetic Laplacian is not positive semidefinite")
    return adjacency, laplacian


class IChingNetworkFrameAssembler:
    """Thread-safe atomic receiver for `/qmw/iching/network/*` messages."""

    def __init__(self, commit_callback: Callable[[CommittedIChingFrame], None]):
        self.commit_callback = commit_callback
        self.current_revision = -1
        self.candidate: _Candidate | None = None
        self.lock = threading.RLock()

    @staticmethod
    def _revision(args):
        if not args:
            raise IChingBridgeError("Message is missing its revision")
        return int(args[0])

    def _candidate_for(self, args) -> _Candidate:
        revision = self._revision(args)
        candidate = self.candidate
        if candidate is None or candidate.revision != revision:
            raise IChingBridgeError(f"No active I Ching candidate for revision {revision}")
        return candidate

    def begin(self, _address, *args):
        if len(args) != 4:
            raise IChingBridgeError("begin expects revision, seed, 64, 4")
        revision, seed, graph_dimension, density_qubits = map(int, args)
        with self.lock:
            if revision <= self.current_revision:
                raise IChingBridgeError(f"Stale I Ching revision {revision}")
            if graph_dimension != 64 or density_qubits != 4:
                raise IChingBridgeError("Unsupported graph or density dimensions")
            self.candidate = _Candidate(revision, seed)

    def reading(self, _address, *args):
        with self.lock:
            candidate = self._candidate_for(args)
            if len(args) != 5:
                raise IChingBridgeError("reading expects revision and four values")
            primary, mask, transformed, change = map(int, args[1:])
            if transformed != primary ^ mask:
                raise IChingBridgeError("Transformed hexagram does not equal H0 XOR M")
            if not all(0 <= value < 64 for value in (primary, mask, transformed)):
                raise IChingBridgeError("Hexagram values must fit six bits")
            if not 0 <= change < 4:
                raise IChingBridgeError("Change register must fit two bits")
            candidate.reading = primary, mask, transformed, change

    def metrics(self, _address, *args):
        with self.lock:
            candidate = self._candidate_for(args)
            if len(args) != 4:
                raise IChingBridgeError("metrics expects revision and three values")
            values = tuple(map(float, args[1:]))
            if not all(math.isfinite(value) for value in values):
                raise IChingBridgeError("Metrics must be finite")
            candidate.metrics = values

    def primary_phase(self, _address, *args):
        with self.lock:
            candidate = self._candidate_for(args)
            if len(args) != 3:
                raise IChingBridgeError("primary_phase expects revision, phase, strength")
            candidate.primary_phase = float(args[1]), float(args[2])

    def pauli(self, _address, *args):
        with self.lock:
            candidate = self._candidate_for(args)
            if len(args) != 3:
                raise IChingBridgeError("pauli expects revision, word, expectation")
            word, expectation = str(args[1]), float(args[2])
            if len(word) != 4 or any(letter not in "XYZ" for letter in word):
                raise IChingBridgeError("Pauli word must be in {X,Y,Z}^4")
            candidate.pauli = word, expectation

    def line_phase(self, _address, *args):
        with self.lock:
            candidate = self._candidate_for(args)
            if len(args) != 5:
                raise IChingBridgeError("line_phase expects five values")
            line = int(args[1]); values = tuple(map(float, args[2:]))
            if not 1 <= line <= 6:
                raise IChingBridgeError("Line must be in 1..6")
            candidate.line_phases[line] = values

    def edge(self, _address, *args):
        with self.lock:
            candidate = self._candidate_for(args)
            if len(args) != 6:
                raise IChingBridgeError("edge expects six values")
            source, target, line = map(int, args[1:4])
            weight, phase = map(float, args[4:])
            key = (min(source, target), max(source, target))
            candidate.edges[key] = line, weight, phase if source < target else -phase

    def flux(self, _address, *args):
        with self.lock:
            candidate = self._candidate_for(args)
            if len(args) != 5:
                raise IChingBridgeError("flux expects five values")
            line_a, line_b = map(int, args[1:3])
            candidate.fluxes[(line_a, line_b)] = float(args[3]), float(args[4])

    def density_real_row(self, _address, *args):
        self._density_row(args, "real")

    def density_imag_row(self, _address, *args):
        self._density_row(args, "imag")

    def _density_row(self, args, part):
        with self.lock:
            candidate = self._candidate_for(args)
            if len(args) != 18:
                raise IChingBridgeError(f"density {part} row expects revision, row, 16 values")
            row = int(args[1])
            if not 0 <= row < 16:
                raise IChingBridgeError("Density row must be in 0..15")
            values = np.asarray(args[2:], dtype=np.float64)
            if not np.all(np.isfinite(values)):
                raise IChingBridgeError("Density row contains non-finite values")
            getattr(candidate, f"density_{part}_rows")[row] = values

    def end(self, _address, *args):
        with self.lock:
            candidate = self._candidate_for(args)
            if len(args) != 1:
                raise IChingBridgeError("end expects only revision")
            missing = []
            for name in ("reading", "metrics", "primary_phase", "pauli"):
                if getattr(candidate, name) is None: missing.append(name)
            if len(candidate.line_phases) != 6: missing.append("six line phases")
            if len(candidate.fluxes) != EXPECTED_FLUXES: missing.append("15 cycle fluxes")
            if len(candidate.density_real_rows) != 16: missing.append("16 real density rows")
            if len(candidate.density_imag_rows) != 16: missing.append("16 imaginary density rows")
            if missing:
                raise IChingBridgeError("Incomplete I Ching frame: " + ", ".join(missing))
            real = np.vstack([candidate.density_real_rows[row] for row in range(16)])
            imag = np.vstack([candidate.density_imag_rows[row] for row in range(16)])
            density = validate_density_matrix(real + 1j * imag, dimension=16)
            _adjacency, laplacian = adjacency_and_laplacian(candidate.edges)
            hamiltonian = project_laplacian_to_hamiltonian(laplacian)
            primary, mask, transformed, change = candidate.reading
            mutual_information, change_entropy, purity = candidate.metrics
            phase, strength = candidate.primary_phase
            pauli_word, pauli_expectation = candidate.pauli
            committed = CommittedIChingFrame(
                candidate.revision, candidate.seed, primary, mask, transformed, change,
                mutual_information, change_entropy, purity, phase, strength,
                pauli_word, pauli_expectation, density, laplacian, hamiltonian,
            )
            self.current_revision = candidate.revision
            self.candidate = None
        self.commit_callback(committed)
        return committed

    def register(self, qmw_bridge):
        routes = {
            "/begin": self.begin, "/reading": self.reading, "/metrics": self.metrics,
            "/primary_phase": self.primary_phase, "/pauli": self.pauli,
            "/line_phase": self.line_phase, "/edge": self.edge, "/flux": self.flux,
            "/density/real_row": self.density_real_row,
            "/density/imag_row": self.density_imag_row, "/end": self.end,
        }
        for suffix, handler in routes.items():
            qmw_bridge.add_control_handler(NETWORK_ROOT + suffix, handler)


class LiveIChingDensityEngineBridge:
    """Apply complete I Ching frames only at density-engine step boundaries."""

    def __init__(self, engine, *, density_mix=1.0, laplacian_gain=1.0,
                 density_enabled=True, laplacian_enabled=True):
        self.engine = engine
        self.pending: queue.SimpleQueue[CommittedIChingFrame] = queue.SimpleQueue()
        self.assembler = IChingNetworkFrameAssembler(self.pending.put)
        self.density_mix = float(np.clip(density_mix, 0.0, 1.0))
        self.laplacian_gain = max(0.0, float(laplacian_gain))
        self.density_enabled = bool(density_enabled)
        self.laplacian_enabled = bool(laplacian_enabled)
        self.active_frame: CommittedIChingFrame | None = None
        self.applied_revision = -1

    def register(self):
        self.assembler.register(self.engine.qmw_bridge)
        controls = {
            "/qmw/iching/density/enabled": self._osc_density_enabled,
            "/qmw/iching/density/mix": self._osc_density_mix,
            "/qmw/iching/laplacian/enabled": self._osc_laplacian_enabled,
            "/qmw/iching/laplacian/gain": self._osc_laplacian_gain,
        }
        for route, handler in controls.items():
            self.engine.qmw_bridge.add_control_handler(route, handler)
        return self

    def _osc_density_enabled(self, _address, value): self.density_enabled = bool(int(value))
    def _osc_density_mix(self, _address, value): self.density_mix = float(np.clip(value, 0, 1))
    def _osc_laplacian_enabled(self, _address, value): self.laplacian_enabled = bool(int(value))
    def _osc_laplacian_gain(self, _address, value): self.laplacian_gain = max(0.0, float(value))

    def drain_pending(self):
        newest = None
        while True:
            try: candidate = self.pending.get_nowait()
            except queue.Empty: break
            if candidate.revision > self.applied_revision:
                newest = candidate
        if newest is not None:
            self._commit_on_engine_thread(newest)
        return newest

    def _commit_on_engine_thread(self, frame: CommittedIChingFrame):
        engine = self.engine
        before = np.asarray(engine.rho, dtype=np.complex128).copy()
        if self.density_enabled:
            incoming = qac_lsb_to_engine_density(frame.density_q0_lsb, n_qubits=4)
            mixed = (1.0 - self.density_mix) * before + self.density_mix * incoming
            engine.rho = validate_density_matrix(mixed, dimension=16)
            engine.state_revision += 1
            engine.last_event_type = "iching_density_commit"
            if hasattr(engine, "bohm") and hasattr(engine.bohm, "reset"):
                engine.bohm.reset(engine.rho, logical_time=engine.logical_time)
                if hasattr(engine.bohm, "configuration_revision"):
                    engine.configuration_revision = engine.bohm.configuration_revision
            persist = getattr(engine, "_persist_transition", None)
            if callable(persist):
                persist(event_type="iching_density_commit", rho_after=engine.rho,
                        event_id=getattr(engine, "last_event_id", 0),
                        metadata={"iching_revision": frame.revision, "seed": frame.seed,
                                  "primary": frame.primary, "moving_mask": frame.moving_mask,
                                  "transformed": frame.transformed,
                                  "density_mix": self.density_mix},
                        rho_before=before, delta_rho=engine.rho - before)
        self.active_frame = frame
        self.applied_revision = frame.revision

    def effective_hamiltonian(self):
        frame = self.active_frame
        if frame is None or not self.laplacian_enabled:
            return np.zeros((16, 16), dtype=np.complex128)
        # I(L:U) is at most six bits; bound the relational modulation to [0,1].
        relational_gain = float(np.clip(frame.mutual_information_bits / 6.0, 0.0, 1.0))
        return self.laplacian_gain * relational_gain * frame.hamiltonian_16

    def step(self, dt):
        """Replace calls to engine.step(dt) with this state-owner-thread call."""
        self.drain_pending()
        original_hamiltonian = self.engine.hamiltonian
        addition = self.effective_hamiltonian()
        if np.any(addition):
            self.engine.hamiltonian = lambda: original_hamiltonian() + addition
        try:
            return self.engine.step(dt)
        finally:
            self.engine.hamiltonian = original_hamiltonian
