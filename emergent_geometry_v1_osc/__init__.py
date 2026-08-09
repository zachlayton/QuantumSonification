"""Public package interface for Emergent Geometry Engine and OSC bridge v1."""

from .emergent_geometry_engine_v1 import (
    EmergentGeometryEngine,
    EmergentSurface,
    GeometryParameters,
    MorphogenField,
    MorphogenParameters,
    PRESETS,
)
from .emergent_geometry_osc_v1 import EmergentGeometryOSC

__all__ = [
    "EmergentGeometryEngine",
    "EmergentGeometryOSC",
    "EmergentSurface",
    "GeometryParameters",
    "MorphogenField",
    "MorphogenParameters",
    "PRESETS",
]
