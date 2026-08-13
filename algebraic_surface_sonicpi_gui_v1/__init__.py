"""Realtime algebraic-surface sonification bridge to Sonic Pi.

Wraps the existing marching-tetrahedra / cotangent-Laplacian pipeline
(``operators.algebraic_surface_pipeline_v1``) with a geometry cache and a
minimal stdlib OSC client, so a small Tkinter GUI can stream live modal
data (frequency, decay, amplitude, pan) to a running Sonic Pi instance as
parameters are adjusted.
"""

from .realtime_bridge_v1 import (
    MODES_ADDRESS,
    SILENCE_ADDRESS,
    SURFACE_NAMES,
    GeometrySolve,
    RealtimeSurfaceConfig,
    SonicPiModeStreamer,
    SurfaceModeCache,
    compute_modal_packet,
)
from .osc_client_v1 import SonicPiOSCClient, encode_osc_message

__all__ = [
    "MODES_ADDRESS",
    "SILENCE_ADDRESS",
    "SURFACE_NAMES",
    "GeometrySolve",
    "RealtimeSurfaceConfig",
    "SonicPiModeStreamer",
    "SurfaceModeCache",
    "SonicPiOSCClient",
    "compute_modal_packet",
    "encode_osc_message",
]
