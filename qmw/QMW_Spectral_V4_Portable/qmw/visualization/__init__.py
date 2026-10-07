"""Optional visualization frontends for QMW state frames."""

from .em_polarization_viewer import EMPolarizationViewer
from .gpe_field_viewer import GPEFieldViewer, GPEFieldVisualFrame

__all__ = [
    "EMPolarizationViewer", "GPEFieldViewer", "GPEFieldVisualFrame", "GPEPhaseCollisionGUI",
    "GPEPhaseCollisionGeometryViewer", "GeometryCollisionTraceData", "geometry_collision_trace_data",
]


def __getattr__(name: str):
    """Keep the runnable GUI module unloaded until a caller requests it."""
    if name == "GPEPhaseCollisionGUI":
        from .gpe_phase_collision_gui import GPEPhaseCollisionGUI
        return GPEPhaseCollisionGUI
    if name in {"GPEPhaseCollisionGeometryViewer", "GeometryCollisionTraceData", "geometry_collision_trace_data"}:
        from .gpe_phase_collision_geometry_viewer import (
            GPEPhaseCollisionGeometryViewer, GeometryCollisionTraceData, geometry_collision_trace_data,
        )
        return {
            "GPEPhaseCollisionGeometryViewer": GPEPhaseCollisionGeometryViewer,
            "GeometryCollisionTraceData": GeometryCollisionTraceData,
            "geometry_collision_trace_data": geometry_collision_trace_data,
        }[name]
    raise AttributeError(name)
