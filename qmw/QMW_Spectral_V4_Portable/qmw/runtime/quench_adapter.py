"""Gated runtime-step adapter for explicit field quenches."""

from __future__ import annotations

from dataclasses import dataclass, replace

from qmw.quench import QuenchEngine
from qmw.quantum_field import QuantumFieldFrame

from .frame import QMWFrame, RuntimeStep
from .scheduler import QMWRuntimeScheduler


@dataclass(frozen=True)
class QuenchRuntimeAdapter:
    engine: QuenchEngine

    def __post_init__(self) -> None:
        if not isinstance(self.engine, QuenchEngine):
            raise TypeError("engine must be a QuenchEngine")

    def __call__(self, frame: QMWFrame) -> QMWFrame:
        if not isinstance(frame.field, QuantumFieldFrame):
            raise TypeError("QMWFrame.field must contain a QuantumFieldFrame before quench")
        if frame.field is not self.engine.field_engine.snapshot():
            raise ValueError("QMWFrame.field must be the current field-engine snapshot")
        event, field = self.engine.apply_next(time=frame.time)
        diagnostics = dict(frame.diagnostics)
        diagnostics.update(
            {
                "quench_provenance": event.provenance,
                "quench_request_id": event.request.request_id,
                "quench_injected_work": event.injected_work,
            }
        )
        return frame.with_updates(
            field=field,
            events=frame.events + (event,),
            revisions=replace(frame.revisions, field=field.revision),
            dirty=frame.dirty.clear("field").invalidate_memory(),
            triggers=frame.triggers.cleared("quench"),
            diagnostics=diagnostics,
        )


def register_quench_engine(
    scheduler: QMWRuntimeScheduler,
    engine: QuenchEngine,
) -> QuenchRuntimeAdapter:
    if not isinstance(scheduler, QMWRuntimeScheduler):
        raise TypeError("scheduler must be a QMWRuntimeScheduler")
    adapter = QuenchRuntimeAdapter(engine)
    scheduler.register(RuntimeStep.APPLY_QUENCH, adapter)
    return adapter


__all__ = ["QuenchRuntimeAdapter", "register_quench_engine"]
