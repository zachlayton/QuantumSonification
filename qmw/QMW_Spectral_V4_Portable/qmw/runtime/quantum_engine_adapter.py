"""Runtime steps 1-5 over the authoritative QuantumFrameEngine."""

from __future__ import annotations

from dataclasses import dataclass, replace
import math
from threading import RLock

import numpy as np

from qmw.quantum.control import ChannelRateControl, HamiltonianControl
from qmw.quantum.dynamics import QuantumFrame
from qmw.quantum.engine import AppliedControl, QuantumFrameEngine

from .frame import QMWFrame, RuntimeStep
from .scheduler import QMWRuntimeScheduler


GeneratorControl = HamiltonianControl | ChannelRateControl


@dataclass(frozen=True)
class QuantumGeneratorControlBatch:
    """One monotonic batch containing only continuous-generator controls."""

    revision: int
    controls: tuple[GeneratorControl, ...] = ()
    provenance: str = "qmw_quantum_generator_control_batch_v1"

    def __post_init__(self) -> None:
        if isinstance(self.revision, bool) or int(self.revision) != self.revision or self.revision < 0:
            raise ValueError("revision must be a nonnegative integer")
        declared = tuple(self.controls)
        if any(not isinstance(control, (HamiltonianControl, ChannelRateControl)) for control in declared):
            raise TypeError(
                "generator batches may contain only HamiltonianControl or ChannelRateControl"
            )
        if not self.provenance:
            raise ValueError("provenance must be nonempty")
        object.__setattr__(self, "revision", int(self.revision))
        object.__setattr__(self, "controls", declared)


@dataclass(frozen=True)
class QuantumValidationFrame:
    """Numerical audit of one already-sealed authoritative QuantumFrame."""

    time: float
    quantum_revision: int
    trace_error: float
    hermiticity_error: float
    minimum_eigenvalue: float
    pauli_reconstruction_error: float
    current_antisymmetry_error: float
    continuity_error: float
    valid: bool
    tolerance: float
    provenance: str = "qmw_authoritative_quantum_validation_v1"


def validate_quantum_frame(
    frame: QuantumFrame,
    *,
    tolerance: float = 1.0e-9,
) -> QuantumValidationFrame:
    """Audit density, Pauli reconstruction, and unitary continuity invariants."""

    if not isinstance(frame, QuantumFrame):
        raise TypeError("frame must be a QuantumFrame")
    amount = float(tolerance)
    if not math.isfinite(amount) or amount <= 0.0:
        raise ValueError("tolerance must be finite and positive")
    trace_error = abs(complex(np.trace(frame.rho)) - 1.0)
    hermiticity_error = float(np.max(np.abs(frame.rho - frame.rho.conj().T)))
    minimum = float(np.min(np.linalg.eigvalsh(frame.rho)))
    pauli_error = float(np.max(np.abs(frame.pauli.reconstruct() - frame.rho)))
    antisymmetry = float(
        np.max(np.abs(frame.basis_current_inflow + frame.basis_current_inflow.T))
    )
    continuity = float(
        np.max(
            np.abs(
                np.sum(frame.basis_current_inflow, axis=1)
                - frame.population_rate_unitary
            )
        )
    )
    valid = (
        trace_error <= amount
        and hermiticity_error <= amount
        and minimum >= -amount
        and pauli_error <= amount
        and antisymmetry <= amount
        and continuity <= amount
    )
    return QuantumValidationFrame(
        time=frame.time,
        quantum_revision=frame.frame_index,
        trace_error=float(trace_error),
        hermiticity_error=hermiticity_error,
        minimum_eigenvalue=minimum,
        pauli_reconstruction_error=pauli_error,
        current_antisymmetry_error=antisymmetry,
        continuity_error=continuity,
        valid=valid,
        tolerance=amount,
    )


class QuantumEngineRuntimeAdapter:
    """Coordinate generator controls and one authoritative density transaction."""

    def __init__(
        self,
        engine: QuantumFrameEngine,
        *,
        validation_tolerance: float = 1.0e-9,
    ) -> None:
        if not isinstance(engine, QuantumFrameEngine):
            raise TypeError("engine must be a QuantumFrameEngine")
        amount = float(validation_tolerance)
        if not math.isfinite(amount) or amount <= 0.0:
            raise ValueError("validation_tolerance must be finite and positive")
        self.engine = engine
        self.validation_tolerance = amount
        self._lock = RLock()
        self._last_batch_revision = -1
        self._last_batch: QuantumGeneratorControlBatch | None = None

    def receive_controls(self, frame: QMWFrame) -> QMWFrame:
        """Admit one new direct QuantumGeneratorControlBatch, if supplied."""

        batch = frame.controls
        if batch is None or not isinstance(batch, QuantumGeneratorControlBatch):
            return frame
        with self._lock:
            if batch.revision < self._last_batch_revision:
                raise ValueError("quantum generator control batch revision is stale")
            if batch.revision == self._last_batch_revision:
                if batch is not self._last_batch:
                    raise ValueError("quantum generator control batch revision was reused")
                return frame
            for control in batch.controls:
                self.engine.schedule(control)
            self._last_batch_revision = batch.revision
            self._last_batch = batch
            diagnostics = dict(frame.diagnostics)
            diagnostics.update(
                {
                    "quantum_control_batch_revision": batch.revision,
                    "quantum_generator_controls_received": len(batch.controls),
                }
            )
            return frame.with_updates(diagnostics=diagnostics)

    def update_generators(self, frame: QMWFrame) -> QMWFrame:
        """Declare pending piecewise generators; application remains atomic."""

        diagnostics = dict(frame.diagnostics)
        diagnostics["quantum_generator_controls_pending"] = len(
            self.engine.scheduled_controls
        )
        diagnostics["quantum_generator_application"] = (
            "piecewise_inside_authoritative_rho_integration"
        )
        return frame.with_updates(diagnostics=diagnostics)

    def integrate_rho(self, frame: QMWFrame) -> QMWFrame:
        """Advance the engine from time-dt to the synchronized target time."""

        target = frame.time
        expected_start = target - frame.dt
        state = self.engine.state
        if math.isclose(state.time, target, rel_tol=0.0, abs_tol=1.0e-12):
            quantum = state.frame
        elif math.isclose(state.time, expected_start, rel_tol=0.0, abs_tol=1.0e-12):
            if frame.dt <= 0.0:
                raise ValueError("positive dt is required when quantum integration is pending")
            quantum = self.engine.step(frame.dt, publish=False)
        else:
            raise ValueError(
                "quantum engine time must equal QMWFrame.time or QMWFrame.time - dt"
            )
        if not math.isclose(quantum.time, target, rel_tol=0.0, abs_tol=1.0e-12):
            raise RuntimeError("authoritative quantum integration did not reach QMWFrame.time")
        controls: tuple[AppliedControl, ...] = self.engine.state.last_controls
        diagnostics = dict(frame.diagnostics)
        diagnostics.update(
            {
                "quantum_provenance": quantum.provenance,
                "quantum_controls_applied": len(controls),
                "quantum_integration": "authoritative_cptp_piecewise_generator_v1",
            }
        )
        source_revision = getattr(frame.quantum, "frame_index", None)
        dirty = frame.dirty
        if source_revision != quantum.frame_index:
            dirty = dirty.invalidate_geometry()
        return frame.with_updates(
            quantum=quantum,
            events=frame.events + controls,
            revisions=replace(frame.revisions, quantum=quantum.frame_index),
            dirty=dirty,
            diagnostics=diagnostics,
        )

    def validate_rho(self, frame: QMWFrame) -> QMWFrame:
        if not isinstance(frame.quantum, QuantumFrame):
            raise TypeError("QMWFrame.quantum must be a QuantumFrame after integration")
        validation = validate_quantum_frame(
            frame.quantum,
            tolerance=self.validation_tolerance,
        )
        if not validation.valid:
            raise ValueError("authoritative QuantumFrame failed runtime validation")
        diagnostics = dict(frame.diagnostics)
        diagnostics["quantum_validation"] = validation
        return frame.with_updates(diagnostics=diagnostics)

    def compute_observables(self, frame: QMWFrame) -> QMWFrame:
        if not isinstance(frame.quantum, QuantumFrame):
            raise TypeError("QMWFrame.quantum must be a QuantumFrame")
        return frame.with_updates(
            observables=frame.quantum.pauli,
            revisions=replace(
                frame.revisions,
                observables=frame.quantum.frame_index,
            ),
        )


def register_quantum_engine(
    scheduler: QMWRuntimeScheduler,
    engine: QuantumFrameEngine,
    *,
    validation_tolerance: float = 1.0e-9,
) -> QuantumEngineRuntimeAdapter:
    """Register the authoritative density transaction at steps 1 through 5."""

    if not isinstance(scheduler, QMWRuntimeScheduler):
        raise TypeError("scheduler must be a QMWRuntimeScheduler")
    adapter = QuantumEngineRuntimeAdapter(
        engine,
        validation_tolerance=validation_tolerance,
    )
    scheduler.register(RuntimeStep.RECEIVE_CONTROLS, adapter.receive_controls)
    scheduler.register(RuntimeStep.UPDATE_GENERATORS, adapter.update_generators)
    scheduler.register(RuntimeStep.INTEGRATE_RHO, adapter.integrate_rho)
    scheduler.register(RuntimeStep.VALIDATE_RHO, adapter.validate_rho)
    scheduler.register(RuntimeStep.COMPUTE_OBSERVABLES, adapter.compute_observables)
    return adapter


__all__ = [
    "QuantumEngineRuntimeAdapter",
    "QuantumGeneratorControlBatch",
    "QuantumValidationFrame",
    "register_quantum_engine",
    "validate_quantum_frame",
]
