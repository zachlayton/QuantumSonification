"""Runtime steps 14-16 for opt-in stabilizer recovery experiments."""

from __future__ import annotations

from dataclasses import dataclass, replace

from qmw.error_correction import (
    ErrorCorrectionEngine,
    ExperimentalCorruptionFrame,
    RecoveryFrame,
    SyndromeFrame,
)
from qmw.quantum.dynamics import QuantumFrame

from .frame import QMWFrame, RuntimeStep
from .scheduler import QMWRuntimeScheduler


def _current_corruption(frame: QMWFrame) -> ExperimentalCorruptionFrame | None:
    """Return only a corruption branch created for this exact source tick."""

    for event in reversed(frame.events):
        if (
            isinstance(event, ExperimentalCorruptionFrame)
            and event.runtime_tick == frame.tick
            and event.source_quantum_revision == getattr(frame.quantum, "frame_index", None)
        ):
            return event
    return None


@dataclass(frozen=True)
class ErrorRecoveryRuntimeAdapter:
    """Bind an ``ErrorCorrectionEngine`` to the canonical recovery steps.

    The authoritative ``QMWFrame.quantum`` object remains unchanged.  The
    corruption and recovered states are explicit diagnostic branches.  A
    caller that chooses to commit a correction must schedule
    ``RecoveryFrame.intervention.as_unitary_control(...)`` through the
    authoritative ``QuantumFrameEngine`` on a subsequent transaction.
    """

    engine: ErrorCorrectionEngine

    def __post_init__(self) -> None:
        if not isinstance(self.engine, ErrorCorrectionEngine):
            raise TypeError("engine must be an ErrorCorrectionEngine")

    def apply_experimental_corruption(self, frame: QMWFrame) -> QMWFrame:
        if not isinstance(frame.quantum, QuantumFrame):
            raise TypeError("QMWFrame.quantum must be a QuantumFrame")
        corruption = self.engine.apply_next_corruption(
            frame.quantum,
            runtime_tick=frame.tick,
        )
        diagnostics = dict(frame.diagnostics)
        diagnostics.update(
            {
                "experimental_corruption": corruption,
                "experimental_corruption_kind": "diagnostic_pauli_side_branch",
                "physical_decoherence": False,
            }
        )
        return frame.with_updates(
            events=frame.events + (corruption,),
            triggers=frame.triggers.cleared("experimental_corruption"),
            diagnostics=diagnostics,
        )

    def compute_syndrome(self, frame: QMWFrame) -> QMWFrame:
        if not isinstance(frame.quantum, QuantumFrame):
            raise TypeError("QMWFrame.quantum must be a QuantumFrame")
        corruption = _current_corruption(frame)
        source = frame.quantum.rho if corruption is None else corruption.rho_corrupted
        source_kind = (
            "authoritative_quantum"
            if corruption is None
            else "experimental_corruption_branch"
        )
        revision = frame.revisions.syndrome + 1
        syndrome = self.engine.compute_syndrome(
            source,
            revision=revision,
            time=frame.time,
            runtime_tick=frame.tick,
            source_quantum_revision=frame.quantum.frame_index,
            source_kind=source_kind,
        )
        diagnostics = dict(frame.diagnostics)
        diagnostics.update(
            {
                "syndrome_provenance": syndrome.provenance,
                "syndrome_resolved": syndrome.resolved,
                "syndrome_source_kind": syndrome.source_kind,
            }
        )
        return frame.with_updates(
            syndrome=syndrome,
            revisions=replace(frame.revisions, syndrome=revision),
            diagnostics=diagnostics,
        )

    def apply_recovery(self, frame: QMWFrame) -> QMWFrame:
        if not isinstance(frame.quantum, QuantumFrame):
            raise TypeError("QMWFrame.quantum must be a QuantumFrame")
        if not isinstance(frame.syndrome, SyndromeFrame):
            raise TypeError("QMWFrame.syndrome must contain a SyndromeFrame")
        if frame.syndrome.runtime_tick != frame.tick:
            raise ValueError("syndrome must belong to the current runtime tick")
        corruption = _current_corruption(frame)
        source = frame.quantum.rho if corruption is None else corruption.rho_corrupted
        reference = None if corruption is None else corruption.rho_before
        recovery = self.engine.recover(
            source,
            frame.syndrome,
            reference_rho=reference,
        )
        diagnostics = dict(frame.diagnostics)
        diagnostics.update(
            {
                "recovery_provenance": recovery.provenance,
                "recovery_intervention_kind": recovery.intervention.kind,
                "recovery_authoritative_commit": False,
                "recovery_post_code_space_probability": recovery.post_code_space_probability,
            }
        )
        return frame.with_updates(
            recovery=recovery,
            events=frame.events + (recovery,),
            triggers=frame.triggers.cleared("recovery"),
            diagnostics=diagnostics,
        )


def register_error_recovery_engine(
    scheduler: QMWRuntimeScheduler,
    engine: ErrorCorrectionEngine,
) -> ErrorRecoveryRuntimeAdapter:
    """Register the opt-in corruption, syndrome, and recovery adapters."""

    if not isinstance(scheduler, QMWRuntimeScheduler):
        raise TypeError("scheduler must be a QMWRuntimeScheduler")
    adapter = ErrorRecoveryRuntimeAdapter(engine)
    scheduler.register(
        RuntimeStep.APPLY_EXPERIMENTAL_CORRUPTION,
        adapter.apply_experimental_corruption,
    )
    scheduler.register(RuntimeStep.COMPUTE_SYNDROME, adapter.compute_syndrome)
    scheduler.register(RuntimeStep.APPLY_RECOVERY, adapter.apply_recovery)
    return adapter


__all__ = ["ErrorRecoveryRuntimeAdapter", "register_error_recovery_engine"]
