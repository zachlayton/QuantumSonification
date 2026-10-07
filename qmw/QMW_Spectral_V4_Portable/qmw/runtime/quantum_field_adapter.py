"""Runtime-step adapter for the independent free scalar field engine."""

from __future__ import annotations

from dataclasses import dataclass, replace

from qmw.quantum_field import QuantumFieldEngine

from .frame import QMWFrame, RuntimeStep
from .scheduler import QMWRuntimeScheduler


@dataclass(frozen=True)
class QuantumFieldRuntimeAdapter:
    """Advance a field to the QMW tick time without touching other payloads."""

    engine: QuantumFieldEngine

    def __post_init__(self) -> None:
        if not isinstance(self.engine, QuantumFieldEngine):
            raise TypeError("engine must be a QuantumFieldEngine")

    def __call__(self, frame: QMWFrame) -> QMWFrame:
        if not isinstance(frame, QMWFrame):
            raise TypeError("frame must be a QMWFrame")
        field = self.engine.advance_to(frame.time)
        diagnostics = dict(frame.diagnostics)
        diagnostics.update(
            {
                "field_provenance": field.provenance,
                "field_independent_of_qubit_rho": True,
                "field_independent_of_gpe_psi": True,
            }
        )
        return frame.with_updates(
            field=field,
            revisions=replace(frame.revisions, field=field.revision),
            dirty=frame.dirty.clear("field"),
            diagnostics=diagnostics,
        )


def register_quantum_field_engine(
    scheduler: QMWRuntimeScheduler,
    engine: QuantumFieldEngine,
) -> QuantumFieldRuntimeAdapter:
    """Register the engine at canonical runtime step 11."""

    if not isinstance(scheduler, QMWRuntimeScheduler):
        raise TypeError("scheduler must be a QMWRuntimeScheduler")
    adapter = QuantumFieldRuntimeAdapter(engine)
    scheduler.register(RuntimeStep.UPDATE_QUANTUM_FIELD, adapter)
    return adapter


__all__ = ["QuantumFieldRuntimeAdapter", "register_quantum_field_engine"]
