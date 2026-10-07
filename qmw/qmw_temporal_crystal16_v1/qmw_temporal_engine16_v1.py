"""Unified logical-time engine for QMW's canonical 16 x 16 density matrix.

Only this engine commits the central rho.  Basis clocks and temporal observers
remain separate.  Each evolver declares whether recurrence is programmed,
Floquet-driven, or observer-only so a score sequence cannot be mislabeled as a
time-crystalline response.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Mapping, Protocol

import numpy as np

try:
    from .qmw_floquet_time_crystal16_v1 import (
        FloquetTimeCrystal16,
        analyze_temporal_order,
    )
    from .qmw_lfsr_clock4_v1 import LFSRClock4
    from .qmw_subharmonic_pythagorean_quantum_time_v1 import (
        PythagoreanHamiltonianCoupler,
        SPQTSnapshot,
        SubharmonicPythagoreanClock,
    )
    from .qmw_temporal_core16_v1 import (
        BasisClock16,
        ClockFrame,
        HistoryBank,
        RevisionedDensityState,
        as_complex_matrix,
        evolve_unitary,
        hermitian_unitary,
        l1_coherence,
        purity,
        trace_distance,
        validate_density_matrix,
    )
except ImportError:  # pragma: no cover
    from qmw_floquet_time_crystal16_v1 import (
        FloquetTimeCrystal16,
        analyze_temporal_order,
    )
    from qmw_lfsr_clock4_v1 import LFSRClock4
    from qmw_subharmonic_pythagorean_quantum_time_v1 import (
        PythagoreanHamiltonianCoupler,
        SPQTSnapshot,
        SubharmonicPythagoreanClock,
    )
    from qmw_temporal_core16_v1 import (
        BasisClock16,
        ClockFrame,
        HistoryBank,
        RevisionedDensityState,
        as_complex_matrix,
        evolve_unitary,
        hermitian_unitary,
        l1_coherence,
        purity,
        trace_distance,
        validate_density_matrix,
    )


class ProtocolKind(str, Enum):
    OBSERVER = "observer_no_state_mutation"
    LFSR = "programmed_maximal_lfsr_permutation"
    DEBRUIJN = "programmed_debruijn16_permutation"
    PYTHAGOREAN = "programmed_pythagorean_hamiltonian_drive"
    FLOQUET = "floquet_repeated_single_period_map"
    HYBRID = "explicit_hybrid_composition"


@dataclass(frozen=True)
class TemporalStepContext:
    tick: int
    simulation_time: float
    dt: float
    basis_clock: Mapping[str, Any]
    lfsr_clock: Mapping[str, Any] | None = None
    spqt_clock: SPQTSnapshot | None = None


@dataclass(frozen=True)
class EvolutionResult:
    rho: np.ndarray = field(repr=False)
    protocol: ProtocolKind
    metadata: Mapping[str, Any] = field(default_factory=dict)


class DensityEvolver(Protocol):
    protocol: ProtocolKind

    def evolve(self, rho: np.ndarray, context: TemporalStepContext) -> EvolutionResult:
        ...


class ObserverEvolver:
    protocol = ProtocolKind.OBSERVER

    def evolve(self, rho: np.ndarray, context: TemporalStepContext) -> EvolutionResult:
        return EvolutionResult(
            rho=as_complex_matrix(rho),
            protocol=self.protocol,
            metadata={"mutated": False},
        )


class LFSRPermutationEvolver:
    protocol = ProtocolKind.LFSR

    def __init__(self, lfsr: LFSRClock4, *, decimation: int = 1):
        self.lfsr = lfsr
        self.decimation = int(decimation)

    def evolve(self, rho: np.ndarray, context: TemporalStepContext) -> EvolutionResult:
        return EvolutionResult(
            rho=self.lfsr.apply_to_density(rho, decimation=self.decimation),
            protocol=self.protocol,
            metadata={
                "decimation": self.decimation,
                "emergent": False,
                "source": "known LFSR permutation",
            },
        )


class FloquetEvolver:
    protocol = ProtocolKind.FLOQUET

    def __init__(self, model: FloquetTimeCrystal16):
        self.model = model

    def evolve(self, rho: np.ndarray, context: TemporalStepContext) -> EvolutionResult:
        return EvolutionResult(
            rho=self.model.step_density(rho),
            protocol=self.protocol,
            metadata={
                "identical_map_each_tick": True,
                "finite_size": True,
                "emergent_order_claim": False,
            },
        )


class PythagoreanEvolver:
    protocol = ProtocolKind.PYTHAGOREAN

    def __init__(
        self,
        coupler: PythagoreanHamiltonianCoupler,
        *,
        duration_scale: float = 1.0,
    ):
        self.coupler = coupler
        self.duration_scale = float(duration_scale)

    def evolve(self, rho: np.ndarray, context: TemporalStepContext) -> EvolutionResult:
        if context.spqt_clock is None:
            raise RuntimeError("PythagoreanEvolver requires an SPQT clock")
        hamiltonian = self.coupler.hamiltonian(context.spqt_clock)
        unitary = hermitian_unitary(
            hamiltonian,
            duration=context.dt * self.duration_scale,
        )
        return EvolutionResult(
            rho=evolve_unitary(rho, unitary),
            protocol=self.protocol,
            metadata={
                "emergent": False,
                "source": "explicit rational clock phases",
                "macrocycle_position": context.spqt_clock.macrocycle_position,
            },
        )


@dataclass(frozen=True)
class EventThresholds:
    trace_distance: float = 0.10
    coherence_delta: float = 0.20
    purity_delta: float = 0.05


class TemporalEventDetector:
    """Kairos detector; read-only unless its events are explicitly routed back."""

    def __init__(self, thresholds: EventThresholds | None = None):
        self.thresholds = thresholds or EventThresholds()

    def observe(self, previous: np.ndarray, current: np.ndarray) -> tuple[dict[str, Any], ...]:
        distance = trace_distance(previous, current)
        coherence_change = l1_coherence(current) - l1_coherence(previous)
        purity_change = purity(current) - purity(previous)
        events: list[dict[str, Any]] = []
        if distance >= self.thresholds.trace_distance:
            events.append(
                {
                    "kind": "state_distance_crossing",
                    "value": distance,
                    "threshold": self.thresholds.trace_distance,
                }
            )
        if abs(coherence_change) >= self.thresholds.coherence_delta:
            events.append(
                {
                    "kind": "coherence_change",
                    "value": coherence_change,
                    "threshold": self.thresholds.coherence_delta,
                }
            )
        if abs(purity_change) >= self.thresholds.purity_delta:
            events.append(
                {
                    "kind": "purity_change",
                    "value": purity_change,
                    "threshold": self.thresholds.purity_delta,
                }
            )
        return tuple(events)


class TemporalEngine16:
    """Logical-time orchestrator with one revisioned density-state writer."""

    def __init__(
        self,
        rho0: Any,
        *,
        evolver: DensityEvolver | None = None,
        dt: float = 0.01,
        basis_clock: BasisClock16 | None = None,
        lfsr_clock: LFSRClock4 | None = None,
        spqt_clock: SubharmonicPythagoreanClock | None = None,
        event_detector: TemporalEventDetector | None = None,
        history_capacity: int = 240,
    ):
        if float(dt) <= 0.0:
            raise ValueError("dt must be positive")
        self.dt = float(dt)
        self.state = RevisionedDensityState(rho0)
        self.evolver = evolver or ObserverEvolver()
        self.basis_clock = basis_clock or BasisClock16()
        self.lfsr_clock = lfsr_clock
        self.spqt_clock = spqt_clock
        self.event_detector = event_detector or TemporalEventDetector()
        self.history = HistoryBank(history_capacity)
        self._append_initial_frame()

    @staticmethod
    def _dataclass_mapping(value: Any) -> dict[str, Any]:
        return asdict(value)

    def _clock_mapping(self) -> dict[str, Any]:
        mapping: dict[str, Any] = {
            "basis": self._dataclass_mapping(self.basis_clock.snapshot())
        }
        if self.lfsr_clock is not None:
            mapping["lfsr"] = self._dataclass_mapping(self.lfsr_clock.snapshot())
        if self.spqt_clock is not None:
            mapping["spqt"] = self._dataclass_mapping(self.spqt_clock.snapshot())
        return mapping

    def _append_initial_frame(self) -> None:
        self.history.append(
            ClockFrame(
                tick=self.basis_clock.tick,
                simulation_time=self.basis_clock.tick * self.dt,
                revision=self.state.revision,
                rho=self.state.read(),
                protocol=ProtocolKind.OBSERVER.value,
                clock=self._clock_mapping(),
                metadata={"initial": True},
            )
        )

    def _context(self) -> TemporalStepContext:
        basis = self._dataclass_mapping(self.basis_clock.snapshot())
        lfsr = (
            self._dataclass_mapping(self.lfsr_clock.snapshot())
            if self.lfsr_clock is not None
            else None
        )
        spqt = self.spqt_clock.snapshot() if self.spqt_clock is not None else None
        return TemporalStepContext(
            tick=self.basis_clock.tick,
            simulation_time=self.basis_clock.tick * self.dt,
            dt=self.dt,
            basis_clock=basis,
            lfsr_clock=lfsr,
            spqt_clock=spqt,
        )

    def step(self) -> ClockFrame:
        previous = self.state.read()
        context = self._context()
        result = self.evolver.evolve(previous, context)
        next_rho = as_complex_matrix(result.rho)
        validate_density_matrix(next_rho, raise_on_error=True)
        events = self.event_detector.observe(previous, next_rho)
        revision = self.state.commit(
            next_rho,
            expected_revision=self.state.revision,
        )

        self.basis_clock.advance()
        if self.lfsr_clock is not None:
            self.lfsr_clock.advance()
        if self.spqt_clock is not None:
            self.spqt_clock.advance()

        frame = ClockFrame(
            tick=self.basis_clock.tick,
            simulation_time=self.basis_clock.tick * self.dt,
            revision=revision,
            rho=self.state.read(),
            protocol=result.protocol.value,
            clock=self._clock_mapping(),
            events=events,
            metadata=dict(result.metadata),
        )
        self.history.append(frame)
        return frame

    def run(self, steps: int) -> tuple[ClockFrame, ...]:
        count = int(steps)
        if count < 0:
            raise ValueError("steps must be nonnegative")
        return tuple(self.step() for _ in range(count))

    def aion_order_summary(
        self,
        operator: np.ndarray,
        *,
        target_frequency: float,
        discard: int = 0,
    ) -> dict[str, Any]:
        signal = self.history.observable_series(operator)
        diagnostics = analyze_temporal_order(
            signal,
            target_frequency=target_frequency,
            discard=discard,
        )
        return {
            "protocol": self.history.latest().protocol,
            "target_frequency": diagnostics.target_frequency,
            "target_bin_frequency": diagnostics.target_bin_frequency,
            "target_amplitude": diagnostics.target_amplitude,
            "dominant_frequency": diagnostics.dominant_frequency,
            "dominant_amplitude": diagnostics.dominant_amplitude,
            "locking_error": diagnostics.locking_error,
            "peak_to_background": diagnostics.peak_to_background,
            "samples": diagnostics.samples,
            "establishes_time_crystal": False,
        }
