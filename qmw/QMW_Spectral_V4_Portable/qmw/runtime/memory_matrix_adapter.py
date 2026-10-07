"""Runtime step-13 observer adapter for MemoryMatrixEngine."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, replace

from qmw.quantum import QuantumFrame
from qmw_memory_matrix import MemoryDensityProjection, MemoryMatrixEngine

from .frame import QMWFrame, RuntimeStep
from .scheduler import QMWRuntimeScheduler


MemoryDensityProjector = Callable[[QuantumFrame], MemoryDensityProjection]


@dataclass(frozen=True)
class MemoryMatrixRuntimeAdapter:
    """Observe current memory; never acquire or admit a measured response."""

    engine: MemoryMatrixEngine
    density_projector: MemoryDensityProjector | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.engine, MemoryMatrixEngine):
            raise TypeError("engine must be a MemoryMatrixEngine")
        if self.density_projector is not None and not callable(self.density_projector):
            raise TypeError("density_projector must be callable")

    def _projection(self, quantum: QuantumFrame) -> MemoryDensityProjection:
        if self.density_projector is None:
            if quantum.rho.shape != (self.engine.nodes, self.engine.nodes):
                raise ValueError(
                    "quantum rho does not match memory nodes; provide an explicit named density_projector"
                )
            projection = MemoryDensityProjection(
                rho=quantum.rho,
                basis_label=self.engine.basis_label,
                quantum_revision=quantum.frame_index,
                provenance="direct_authoritative_density_in_declared_memory_basis_v1",
            )
        else:
            projection = self.density_projector(quantum)
        if not isinstance(projection, MemoryDensityProjection):
            raise TypeError("density_projector must return MemoryDensityProjection")
        if projection.quantum_revision != quantum.frame_index:
            raise ValueError("memory density projection must cite the current quantum revision")
        return projection

    def __call__(self, frame: QMWFrame) -> QMWFrame:
        if not isinstance(frame.quantum, QuantumFrame):
            raise TypeError("QMWFrame.quantum must be an authoritative QuantumFrame")
        projection = self._projection(frame.quantum)
        memory = self.engine.observe(time=frame.time, projection=projection)
        diagnostics = dict(frame.diagnostics)
        diagnostics.update(
            {
                "memory_provenance": memory.provenance,
                "memory_basis": projection.basis_label,
                "memory_measurement_acquisition_wired": False,
                "memory_admitted_measurement_count": self.engine.adaptive_memory.update_count,
            }
        )
        return frame.with_updates(
            memory=memory,
            revisions=replace(frame.revisions, memory=memory.revision),
            dirty=frame.dirty.clear("memory"),
            diagnostics=diagnostics,
        )


def register_memory_matrix_engine(
    scheduler: QMWRuntimeScheduler,
    engine: MemoryMatrixEngine,
    *,
    density_projector: MemoryDensityProjector | None = None,
) -> MemoryMatrixRuntimeAdapter:
    if not isinstance(scheduler, QMWRuntimeScheduler):
        raise TypeError("scheduler must be a QMWRuntimeScheduler")
    adapter = MemoryMatrixRuntimeAdapter(engine, density_projector)
    scheduler.register(RuntimeStep.UPDATE_MEMORY_MATRIX, adapter)
    return adapter


__all__ = [
    "MemoryDensityProjector",
    "MemoryMatrixRuntimeAdapter",
    "register_memory_matrix_engine",
]
