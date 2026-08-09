"""Relational-time engine: independent processes, conditional states, events."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
import json
import math
from pathlib import Path
import time
from typing import Any

import numpy as np

from .history import BranchTracker
from .quantum_sources import QuantumStateSource, make_source


@dataclass
class ProcessConfig:
    name: str
    rate: float
    coupling: float = 0.2
    threshold: float = 0.55
    midi_min: int = 36
    midi_max: int = 84


@dataclass
class TemporalConfig:
    seed: int = 23
    observation_hz: float = 30.0
    source: str = "fallback"
    state_path: str | None = None
    clock_dim: int = 2
    branch_tracking: bool = False
    branch_threshold: float = 0.72
    log_path: str | None = "relational_time_snapshots.jsonl"
    osc_enabled: bool = True
    osc_host: str = "127.0.0.1"
    osc_port: int = 7442
    processes: list[ProcessConfig] = field(default_factory=lambda: [
        ProcessConfig("resonance", math.sqrt(2.0), 0.19, 0.52, 36, 60),
        ProcessConfig("memory", (1.0 + math.sqrt(5.0)) / 2.0, 0.13, 0.58, 48, 72),
        ProcessConfig("spatial", math.pi / 2.0, 0.23, 0.62, 60, 84),
    ])

    @classmethod
    def from_json(cls, path: str | Path) -> "TemporalConfig":
        data = json.loads(Path(path).read_text())
        data["processes"] = [ProcessConfig(**p) for p in data.get("processes", [])]
        return cls(**data)


@dataclass
class LocalProcess:
    config: ProcessConfig
    phase: float
    energy: float = 0.5
    memory: float = 0.0

    def evolve(self, local_dt: float, quantum_drive: float, clock_phase: float) -> None:
        relation = math.cos(clock_phase - self.phase)
        velocity = self.config.rate * (1.0 + self.config.coupling * relation)
        self.phase = (self.phase + local_dt * velocity + 0.08 * quantum_drive) % math.tau
        self.energy = float(np.clip(0.88 * self.energy + 0.12 * (0.5 + 0.5 * relation), 0, 1))
        self.memory = 0.94 * self.memory + 0.06 * quantum_drive


@dataclass(frozen=True)
class RelationalSnapshot:
    observation: int
    wall_elapsed: float
    clock_phase: float
    clock_confidence: float
    clock_probability: float
    conditional_purity: float
    source: str
    processes: dict[str, dict[str, float]]
    events: list[dict[str, Any]]
    branches: list[dict[str, Any]]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class PageWoottersEstimator:
    """Condition a system state on a phase POVM of a designated clock factor."""

    def __init__(self, clock_dim: int = 2) -> None:
        self.clock_dim = clock_dim

    def estimate(self, rho: np.ndarray, previous_phase: float = 0.0) -> tuple[float, float, float, np.ndarray]:
        rho = _normalize_density(rho)
        dim = rho.shape[0]
        if dim % self.clock_dim:
            raise ValueError(f"density dimension {dim} is not divisible by clock_dim={self.clock_dim}")
        system_dim = dim // self.clock_dim
        tensor = rho.reshape(self.clock_dim, system_dim, self.clock_dim, system_dim)
        clock_rho = np.trace(tensor, axis1=1, axis2=3)
        harmonics = clock_rho[0, 1] if self.clock_dim == 2 else sum(
            clock_rho[j, (j + 1) % self.clock_dim] for j in range(self.clock_dim)
        )
        confidence = float(np.clip(abs(harmonics) * self.clock_dim, 0.0, 1.0))
        phase = float((-np.angle(harmonics)) % math.tau) if abs(harmonics) > 1e-12 else previous_phase
        ket = np.exp(-1j * np.arange(self.clock_dim) * phase) / math.sqrt(self.clock_dim)
        conditional = np.einsum("a,aibj,b->ij", ket.conj(), tensor, ket, optimize=True)
        probability = float(max(np.trace(conditional).real, 1e-15))
        conditional = _normalize_density(conditional / probability)
        return phase, confidence, probability, conditional


def _normalize_density(rho: np.ndarray) -> np.ndarray:
    rho = np.asarray(rho, dtype=np.complex128)
    if rho.ndim != 2 or rho.shape[0] != rho.shape[1]:
        raise ValueError("rho must be a square matrix")
    rho = (rho + rho.conj().T) * 0.5
    trace = np.trace(rho)
    if abs(trace) < 1e-15:
        raise ValueError("rho has zero trace")
    return rho / trace


class QuantumTemporalCompositionSystem:
    def __init__(self, config: TemporalConfig, source: QuantumStateSource | None = None, publisher: Any = None) -> None:
        self.config = config
        self.rng = np.random.default_rng(config.seed)
        self.source = source or make_source(config.source, config.state_path, config.seed)
        self.publisher = publisher
        self.estimator = PageWoottersEstimator(config.clock_dim)
        self.processes = [LocalProcess(p, float(self.rng.uniform(0, math.tau))) for p in config.processes]
        self.branches = BranchTracker(config.branch_tracking, config.branch_threshold)
        self.observation = 0
        self.clock_phase = 0.0
        self._last_monotonic: float | None = None
        self._started = time.monotonic()

    def observe(self, local_dt: float | None = None) -> RelationalSnapshot:
        now = time.monotonic()
        dt = local_dt if local_dt is not None else (1.0 / self.config.observation_hz if self._last_monotonic is None else now - self._last_monotonic)
        self._last_monotonic = now
        rho, source_name = self.source.read(self.observation, dt)
        phase, confidence, probability, conditional = self.estimator.estimate(rho, self.clock_phase)
        self.clock_phase = phase
        populations = np.maximum(np.real(np.diag(conditional)), 0.0)
        populations /= max(float(populations.sum()), 1e-15)
        coherence = float(np.sum(np.abs(conditional - np.diag(np.diag(conditional)))) / max(1, conditional.shape[0] - 1))
        process_data: dict[str, dict[str, float]] = {}
        candidates: list[tuple[float, LocalProcess, float]] = []
        for index, process in enumerate(self.processes):
            drive = float(populations[index % len(populations)])
            # Each process receives its own proper-time increment; observation is sampling, not transport.
            proper_dt = dt * (0.75 + 0.5 * drive) * process.config.rate
            process.evolve(proper_dt, drive, phase)
            correlation = 0.5 + 0.5 * math.cos(process.phase - phase)
            salience = float(np.clip(correlation * (0.45 + 0.35 * confidence + 0.20 * coherence), 0, 1))
            process_data[process.config.name] = {"phase": process.phase, "proper_dt": proper_dt, "energy": process.energy, "correlation": correlation, "salience": salience, "quantum_drive": drive}
            candidates.append((salience, process, drive))
        events = self._events(candidates, coherence)
        branches = self.branches.update(self.observation, candidates, events)
        snapshot = RelationalSnapshot(self.observation, now - self._started, phase, confidence, probability, float(np.trace(conditional @ conditional).real), source_name, process_data, events, branches)
        self._emit(snapshot)
        self.observation += 1
        return snapshot

    def _events(self, candidates: list[tuple[float, LocalProcess, float]], coherence: float) -> list[dict[str, Any]]:
        events = []
        for salience, process, drive in candidates:
            excess = max(0.0, salience - process.config.threshold)
            probability = float(np.clip(excess / max(1e-9, 1.0 - process.config.threshold), 0, 1))
            if self.rng.random() >= probability:
                continue
            span = process.config.midi_max - process.config.midi_min
            note = process.config.midi_min + int(round(span * ((process.phase % math.tau) / math.tau)))
            events.append({"id": f"e{self.observation:08d}-{process.config.name}", "process": process.config.name, "relational_phase": self.clock_phase, "correlation": salience, "probability": probability, "midi": note, "velocity": int(round(35 + 92 * salience)), "duration_ms": float(40 + 1760 * (0.35 * drive + 0.65 * process.energy)), "coherence": coherence})
        return events

    def _emit(self, snapshot: RelationalSnapshot) -> None:
        if self.publisher is not None:
            self.publisher.publish(snapshot)
        if self.config.log_path:
            path = Path(self.config.log_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(snapshot.to_dict(), separators=(",", ":")) + "\n")

    def run(self, observations: int | None = None, realtime: bool = True) -> list[RelationalSnapshot]:
        snapshots = []
        period = 1.0 / self.config.observation_hz
        deadline = time.monotonic()
        while observations is None or len(snapshots) < observations:
            snapshots.append(self.observe(period if not realtime else None))
            if realtime:
                deadline += period
                time.sleep(max(0.0, deadline - time.monotonic()))
        return snapshots
