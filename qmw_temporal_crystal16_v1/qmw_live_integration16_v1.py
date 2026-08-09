"""Live QMW adapter for the temporal-crystal reference models.

The standalone :class:`TemporalEngine16` owns a revisioned density state for
experiments and demos.  The production QMW density engine already owns that
state, so this adapter deliberately does not keep a second copy.  It accepts
the current canonical rho, proposes one temporal evolution, and returns a
revision-aligned immutable frame for the caller to commit.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

import numpy as np

from .qmw_floquet_time_crystal16_v1 import FloquetTimeCrystal16
from .qmw_lfsr_clock4_v1 import LFSRClock4
from .qmw_subharmonic_pythagorean_quantum_time_v1 import (
    DEFAULT_RATIOS,
    PythagoreanHamiltonianCoupler,
    SubharmonicPythagoreanClock,
)
from .qmw_temporal_core16_v1 import (
    DIM,
    X,
    Z,
    BasisClock16,
    ClockFrame,
    HistoryBank,
    as_complex_matrix,
    operator_on_qubit,
    validate_density_matrix,
)
from .qmw_temporal_engine16_v1 import (
    DensityEvolver,
    FloquetEvolver,
    LFSRPermutationEvolver,
    ObserverEvolver,
    PythagoreanEvolver,
    TemporalEventDetector,
    TemporalStepContext,
)
from .qmw_temporal_osc16_v1 import frame_messages

TEMPORAL_CRYSTAL_MODES = ("observer", "floquet", "lfsr", "pythagorean")


@dataclass(frozen=True)
class LiveTemporalStep:
    """One proposed temporal update for the canonical live density state."""

    frame: ClockFrame
    mutated: bool


class LiveTemporalLayer16:
    """Clock and evolve the live rho without becoming another state writer.

    ``revision`` passed to :meth:`step` is the live engine's current revision.
    A state-changing temporal map predicts exactly one additional revision;
    observer-only frames preserve the supplied revision.
    """

    def __init__(
        self,
        *,
        evolver: DensityEvolver | None = None,
        basis_clock: BasisClock16 | None = None,
        lfsr_clock: LFSRClock4 | None = None,
        spqt_clock: SubharmonicPythagoreanClock | None = None,
        event_detector: TemporalEventDetector | None = None,
        history_capacity: int = 240,
        rate_hz: float | None = None,
        max_catch_up_steps: int = 256,
    ):
        if rate_hz is not None and float(rate_hz) <= 0.0:
            raise ValueError("rate_hz must be positive when supplied")
        if int(max_catch_up_steps) <= 0:
            raise ValueError("max_catch_up_steps must be positive")
        self.evolver = evolver or ObserverEvolver()
        self.basis_clock = basis_clock or BasisClock16()
        self.lfsr_clock = lfsr_clock
        self.spqt_clock = spqt_clock
        self.event_detector = event_detector or TemporalEventDetector()
        self.history = HistoryBank(history_capacity)
        self.rate_hz = None if rate_hz is None else float(rate_hz)
        self.max_catch_up_steps = int(max_catch_up_steps)
        self.simulation_time = 0.0
        self.scheduler_elapsed = 0.0
        self.dropped_temporal_steps = 0
        self.last_step: LiveTemporalStep | None = None

    @staticmethod
    def _mapping(value: Any) -> dict[str, Any]:
        return asdict(value)

    def _clock_mapping(self) -> dict[str, Any]:
        mapping: dict[str, Any] = {
            "basis": self._mapping(self.basis_clock.snapshot())
        }
        if self.lfsr_clock is not None:
            mapping["lfsr"] = self._mapping(self.lfsr_clock.snapshot())
        if self.spqt_clock is not None:
            mapping["spqt"] = self._mapping(self.spqt_clock.snapshot())
        return mapping

    def _context(self, dt: float) -> TemporalStepContext:
        return TemporalStepContext(
            tick=self.basis_clock.tick,
            simulation_time=self.simulation_time,
            dt=dt,
            basis_clock=self._mapping(self.basis_clock.snapshot()),
            lfsr_clock=(
                self._mapping(self.lfsr_clock.snapshot())
                if self.lfsr_clock is not None
                else None
            ),
            spqt_clock=(
                self.spqt_clock.snapshot()
                if self.spqt_clock is not None
                else None
            ),
        )

    def step(
        self,
        rho: Any,
        *,
        dt: float,
        revision: int,
    ) -> LiveTemporalStep:
        """Propose and record one temporal frame from the live canonical rho."""

        interval = float(dt)
        if interval <= 0.0:
            raise ValueError("dt must be positive")
        if int(revision) < 0:
            raise ValueError("revision must be nonnegative")

        previous = as_complex_matrix(rho)
        validate_density_matrix(previous, raise_on_error=True)
        result = self.evolver.evolve(previous, self._context(interval))
        next_rho = as_complex_matrix(result.rho)
        validate_density_matrix(next_rho, raise_on_error=True)
        mutated = not np.allclose(
            next_rho,
            previous,
            rtol=1e-10,
            atol=1e-12,
        )
        events = self.event_detector.observe(previous, next_rho)

        self.basis_clock.advance()
        if self.lfsr_clock is not None:
            self.lfsr_clock.advance()
        if self.spqt_clock is not None:
            self.spqt_clock.advance()
        self.simulation_time += interval

        metadata = dict(result.metadata)
        metadata.update(
            {
                "mutated": mutated,
                "canonical_state_owner": "density.DensityMatrixEngine",
            }
        )
        frame = ClockFrame(
            tick=self.basis_clock.tick,
            simulation_time=self.simulation_time,
            revision=int(revision) + int(mutated),
            rho=next_rho,
            protocol=result.protocol.value,
            clock=self._clock_mapping(),
            events=events,
            metadata=metadata,
        )
        live_step = LiveTemporalStep(frame=frame, mutated=mutated)
        self.history.append(frame)
        self.last_step = live_step
        return live_step

    def advance(
        self,
        rho: Any,
        *,
        dt: float,
        revision: int,
    ) -> tuple[LiveTemporalStep, ...]:
        """Advance at ``rate_hz`` independently of the caller's frame rate.

        With no configured rate, every caller frame is one temporal step for
        backward compatibility. At a fixed rate, elapsed caller intervals are
        accumulated and zero or more exact logical periods are emitted.
        """

        interval = float(dt)
        if interval <= 0.0:
            raise ValueError("dt must be positive")
        if self.rate_hz is None:
            return (self.step(rho, dt=interval, revision=revision),)

        period = 1.0 / self.rate_hz
        self.scheduler_elapsed += interval
        due = int(np.floor((self.scheduler_elapsed + 1e-12) / period))
        if due <= 0:
            return ()
        if due > self.max_catch_up_steps:
            self.dropped_temporal_steps += due - self.max_catch_up_steps
            due = self.max_catch_up_steps
            self.scheduler_elapsed %= period
        else:
            self.scheduler_elapsed -= due * period
            if self.scheduler_elapsed < 0.0:
                self.scheduler_elapsed = 0.0

        updates: list[LiveTemporalStep] = []
        current_rho = as_complex_matrix(rho)
        current_revision = int(revision)
        for _ in range(due):
            update = self.step(
                current_rho,
                dt=period,
                revision=current_revision,
            )
            updates.append(update)
            current_rho = update.frame.rho
            current_revision = update.frame.revision
        return tuple(updates)

    @staticmethod
    def publish_frame(client: Any, frame: ClockFrame) -> None:
        """Publish descriptors through an existing python-osc-compatible client."""

        for message in frame_messages(frame):
            arguments: Any
            if len(message.arguments) == 1:
                arguments = message.arguments[0]
            else:
                arguments = list(message.arguments)
            client.send_message(message.address, arguments)


def build_live_temporal_layer(
    mode: str = "observer",
    *,
    rate_hz: float = 2.0,
) -> LiveTemporalLayer16:
    """Build one documented live temporal protocol with conservative defaults."""

    normalized = str(mode).strip().lower()
    if normalized not in TEMPORAL_CRYSTAL_MODES:
        choices = ", ".join(TEMPORAL_CRYSTAL_MODES)
        raise ValueError(f"temporal mode must be one of: {choices}")
    rate = float(rate_hz)
    if rate <= 0.0:
        raise ValueError("rate_hz must be positive")

    if normalized == "observer":
        return LiveTemporalLayer16(rate_hz=rate)

    if normalized == "floquet":
        model = FloquetTimeCrystal16()
        return LiveTemporalLayer16(
            evolver=FloquetEvolver(model),
            rate_hz=rate,
        )

    if normalized == "lfsr":
        lfsr = LFSRClock4()
        return LiveTemporalLayer16(
            evolver=LFSRPermutationEvolver(lfsr),
            lfsr_clock=lfsr,
            rate_hz=rate,
        )

    spqt = SubharmonicPythagoreanClock()
    amplitude = 1.0 / len(DEFAULT_RATIOS)
    operators = {
        ratio.label: operator_on_qubit(Z, qubit)
        for qubit, ratio in enumerate(DEFAULT_RATIOS)
    }
    quadratures = {
        ratio.label: operator_on_qubit(X, qubit)
        for qubit, ratio in enumerate(DEFAULT_RATIOS)
    }
    coupler = PythagoreanHamiltonianCoupler(
        np.zeros((DIM, DIM), dtype=np.complex128),
        operators,
        amplitudes={
            ratio.label: amplitude for ratio in DEFAULT_RATIOS
        },
        quadrature_operators=quadratures,
    )
    return LiveTemporalLayer16(
        evolver=PythagoreanEvolver(coupler),
        spqt_clock=spqt,
        rate_hz=rate,
    )
