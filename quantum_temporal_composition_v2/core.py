"""Correlation/differentiation clock: relational change, not tempo, makes ticks."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from itertools import combinations
import json
import math
from pathlib import Path
import time
from typing import Any

import numpy as np

from .sources import QuantumStateSource, make_source


@dataclass(frozen=True)
class SubsystemConfig:
    name: str
    rate: float
    coupling: float
    register: int


@dataclass
class TemporalV2Config:
    seed: int = 23
    observation_hz: float = 30.0
    source: str = "fallback"
    state_path: str | None = None
    clock_dim: int = 2
    change_quantum: float = 0.075
    change_deadband: float = 0.001
    max_ticks_per_edge_observation: int = 4
    log_path: str | None = "correlation_clock_snapshots_v2.jsonl"
    osc_enabled: bool = True
    osc_host: str = "127.0.0.1"
    osc_port: int = 7442
    subsystems: list[SubsystemConfig] = field(default_factory=lambda: [
        SubsystemConfig("resonance", math.sqrt(2.0), 0.19, 36),
        SubsystemConfig("memory", (1.0 + math.sqrt(5.0)) / 2.0, 0.13, 48),
        SubsystemConfig("spatial", math.pi / 2.0, 0.23, 60),
    ])

    @classmethod
    def from_json(cls, path: str | Path) -> "TemporalV2Config":
        data = json.loads(Path(path).read_text())
        data["subsystems"] = [SubsystemConfig(**item) for item in data.get("subsystems", [])]
        return cls(**data)


@dataclass
class RelationalNode:
    name: str
    phase: float
    energy: float = 0.5
    memory: float = 0.0
    drive: float = 0.0

    def evolve(self, dt: float, config: SubsystemConfig, clock_phase: float, drive: float) -> None:
        coupling = math.sin(clock_phase - self.phase)
        velocity = config.rate * (1.0 + config.coupling * coupling)
        self.phase = (self.phase + dt * velocity + 0.055 * drive) % math.tau
        phase_relation = 0.5 + 0.5 * math.cos(clock_phase - self.phase)
        self.energy = float(np.clip(0.90 * self.energy + 0.10 * phase_relation, 0.0, 1.0))
        self.memory = float(np.clip(0.95 * self.memory + 0.05 * drive, 0.0, 1.0))
        self.drive = drive


@dataclass(frozen=True)
class Tick:
    tick_id: str
    edge: str
    kind: str
    edge_time: int
    relational_time: int
    observation: int
    correlation: float
    differentiation: float
    strength: float
    midi: int
    velocity: int
    duration_ms: float


@dataclass
class EdgeClock:
    edge: str
    change_quantum: float
    deadband: float
    previous: float | None = None
    correlating_accumulator: float = 0.0
    differentiating_accumulator: float = 0.0
    edge_time: int = 0

    def sample(self, correlation: float, limit: int) -> tuple[float, list[tuple[str, float]]]:
        correlation = float(np.clip(correlation, 0.0, 1.0))
        if self.previous is None:
            self.previous = correlation
            return 0.0, []
        delta = correlation - self.previous
        self.previous = correlation
        if abs(delta) <= self.deadband:
            return delta, []
        if delta > 0.0:
            self.correlating_accumulator += delta
            kind = "correlate"
            accumulator_name = "correlating_accumulator"
        else:
            self.differentiating_accumulator += -delta
            kind = "differentiate"
            accumulator_name = "differentiating_accumulator"
        emitted: list[tuple[str, float]] = []
        accumulator = getattr(self, accumulator_name)
        while accumulator >= self.change_quantum and len(emitted) < limit:
            accumulator -= self.change_quantum
            self.edge_time += 1
            emitted.append((kind, min(1.0, abs(delta) / self.change_quantum)))
        setattr(self, accumulator_name, accumulator)
        return delta, emitted

    def inspect(self) -> dict[str, float | int | str]:
        return {
            "edge": self.edge,
            "correlation": 0.0 if self.previous is None else self.previous,
            "correlating_accumulator": self.correlating_accumulator,
            "differentiating_accumulator": self.differentiating_accumulator,
            "edge_time": self.edge_time,
        }


@dataclass(frozen=True)
class CorrelationSnapshot:
    observation: int
    wall_elapsed: float
    relational_time: int
    source: str
    clock_phase: float
    clock_confidence: float
    conditional_purity: float
    nodes: dict[str, dict[str, float]]
    relations: dict[str, dict[str, float | int | str]]
    ticks: list[Tick]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class PageWoottersConditioner:
    def __init__(self, clock_dim: int) -> None:
        self.clock_dim = clock_dim

    def condition(self, rho: np.ndarray, previous_phase: float) -> tuple[float, float, float, np.ndarray]:
        rho = _normalize_density(rho)
        dimension = rho.shape[0]
        if dimension % self.clock_dim:
            raise ValueError("density dimension is not divisible by clock_dim")
        system_dim = dimension // self.clock_dim
        tensor = rho.reshape(self.clock_dim, system_dim, self.clock_dim, system_dim)
        reduced_clock = np.trace(tensor, axis1=1, axis2=3)
        harmonic = reduced_clock[0, 1] if self.clock_dim == 2 else sum(
            reduced_clock[index, (index + 1) % self.clock_dim]
            for index in range(self.clock_dim)
        )
        confidence = float(np.clip(abs(harmonic) * self.clock_dim, 0.0, 1.0))
        phase = float((-np.angle(harmonic)) % math.tau) if abs(harmonic) > 1e-12 else previous_phase
        phase_ket = np.exp(-1j * np.arange(self.clock_dim) * phase) / math.sqrt(self.clock_dim)
        conditional = np.einsum("a,aibj,b->ij", phase_ket.conj(), tensor, phase_ket, optimize=True)
        probability = float(max(np.trace(conditional).real, 1e-15))
        conditional = _normalize_density(conditional / probability)
        return phase, confidence, probability, conditional


def _normalize_density(rho: np.ndarray) -> np.ndarray:
    rho = np.asarray(rho, dtype=np.complex128)
    if rho.ndim != 2 or rho.shape[0] != rho.shape[1]:
        raise ValueError("rho must be square")
    rho = 0.5 * (rho + rho.conj().T)
    trace = np.trace(rho)
    if abs(trace) < 1e-15:
        raise ValueError("rho has zero trace")
    return rho / trace


def relational_correlation(left: RelationalNode, right: RelationalNode) -> float:
    phase_similarity = 0.5 + 0.5 * math.cos(left.phase - right.phase)
    feature_distance = (
        abs(left.energy - right.energy)
        + abs(left.memory - right.memory)
        + abs(left.drive - right.drive)
    ) / 3.0
    return float(np.clip(0.72 * phase_similarity + 0.28 * (1.0 - feature_distance), 0.0, 1.0))


class CorrelationDifferentiationClockSystem:
    """Musical time advances only when a relation changes by one quantum."""

    def __init__(
        self,
        config: TemporalV2Config,
        source: QuantumStateSource | None = None,
        publisher: Any = None,
    ) -> None:
        self.config = config
        self.source = source or make_source(config.source, config.state_path, config.seed)
        self.publisher = publisher
        self.conditioner = PageWoottersConditioner(config.clock_dim)
        rng = np.random.default_rng(config.seed)
        self.nodes = {
            item.name: RelationalNode(item.name, float(rng.uniform(0.0, math.tau)))
            for item in config.subsystems
        }
        names = ["clock", *self.nodes]
        self.edges = {
            f"{left}:{right}": EdgeClock(
                f"{left}:{right}", config.change_quantum, config.change_deadband
            )
            for left, right in combinations(names, 2)
        }
        self.observation = 0
        self.relational_time = 0
        self.clock_phase = 0.0
        self.started = time.monotonic()
        self.last_monotonic: float | None = None

    def observe(self, dt: float | None = None) -> CorrelationSnapshot:
        now = time.monotonic()
        sample_dt = dt if dt is not None else (
            1.0 / self.config.observation_hz
            if self.last_monotonic is None
            else now - self.last_monotonic
        )
        self.last_monotonic = now
        rho, source_name = self.source.read(self.observation, sample_dt)
        phase, confidence, probability, conditional = self.conditioner.condition(
            rho, self.clock_phase
        )
        self.clock_phase = phase
        purity = float(np.trace(conditional @ conditional).real)
        populations = np.maximum(np.real(np.diag(conditional)), 0.0)
        populations /= max(float(populations.sum()), 1e-15)
        for index, item in enumerate(self.config.subsystems):
            self.nodes[item.name].evolve(
                sample_dt,
                item,
                phase,
                float(populations[index % len(populations)]),
            )
        all_nodes = {
            "clock": RelationalNode("clock", phase, confidence, purity, probability),
            **self.nodes,
        }
        relations: dict[str, dict[str, float | int | str]] = {}
        ticks: list[Tick] = []
        for edge_name, edge_clock in self.edges.items():
            left_name, right_name = edge_name.split(":", 1)
            correlation = relational_correlation(all_nodes[left_name], all_nodes[right_name])
            differentiation, emissions = edge_clock.sample(
                correlation, self.config.max_ticks_per_edge_observation
            )
            inspection = edge_clock.inspect()
            inspection["differentiation"] = differentiation
            relations[edge_name] = inspection
            for kind, strength in emissions:
                self.relational_time += 1
                ticks.append(
                    self._make_tick(
                        edge_clock, kind, correlation, differentiation, strength
                    )
                )
        node_payload = {
            name: {
                "phase": node.phase,
                "energy": node.energy,
                "memory": node.memory,
                "drive": node.drive,
            }
            for name, node in all_nodes.items()
        }
        snapshot = CorrelationSnapshot(
            self.observation,
            now - self.started,
            self.relational_time,
            source_name,
            phase,
            confidence,
            purity,
            node_payload,
            relations,
            ticks,
        )
        self._emit(snapshot)
        self.observation += 1
        return snapshot

    def _make_tick(
        self,
        edge_clock: EdgeClock,
        kind: str,
        correlation: float,
        differentiation: float,
        strength: float,
    ) -> Tick:
        scale = (0, 2, 5, 7, 9, 12)
        edge_index = list(self.edges).index(edge_clock.edge)
        left, right = edge_clock.edge.split(":", 1)
        registers = {item.name: item.register for item in self.config.subsystems}
        base = registers.get(right, registers.get(left, 48))
        contour = scale[(edge_clock.edge_time + edge_index) % len(scale)]
        separation = 6 if kind == "differentiate" else 0
        midi = int(np.clip(base + contour + separation, 24, 96))
        velocity = int(
            np.clip(42 + 70 * strength + 15 * abs(correlation - 0.5), 1, 127)
        )
        duration = float(
            np.clip(
                (180.0 + 1100.0 * correlation)
                * (1.25 if kind == "correlate" else 0.48),
                35.0,
                1800.0,
            )
        )
        return Tick(
            f"t{self.relational_time:09d}",
            edge_clock.edge,
            kind,
            edge_clock.edge_time,
            self.relational_time,
            self.observation,
            correlation,
            differentiation,
            strength,
            midi,
            velocity,
            duration,
        )

    def _emit(self, snapshot: CorrelationSnapshot) -> None:
        if self.publisher is not None:
            self.publisher.publish(snapshot)
        if self.config.log_path:
            path = Path(self.config.log_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("a", encoding="utf-8") as handle:
                handle.write(
                    json.dumps(snapshot.to_dict(), separators=(",", ":")) + "\n"
                )

    def run(
        self, observations: int | None = None, realtime: bool = True
    ) -> list[CorrelationSnapshot]:
        snapshots: list[CorrelationSnapshot] = []
        period = 1.0 / self.config.observation_hz
        deadline = time.monotonic()
        while observations is None or len(snapshots) < observations:
            snapshots.append(self.observe(period if not realtime else None))
            if realtime:
                deadline += period
                time.sleep(max(0.0, deadline - time.monotonic()))
        return snapshots
