"""Realtime algebraic-surface sonification bridge to Sonic Pi.

Wraps the existing marching-tetrahedra / cotangent-Laplacian pipeline
(``operators.algebraic_surface_pipeline_v1``) with a geometry cache and a
minimal stdlib OSC client, so a small Tkinter GUI can stream live modal
data (frequency, decay, amplitude, pan) to a running Sonic Pi instance as
parameters are adjusted -- either by hand, or autonomously via
``quantum_conductor_v1.QuantumPhaseConductor``, which drives sound design
from a live 4-qubit density matrix instead.
"""

from .realtime_bridge_v1 import (
    MATERIAL_MODEL_NAMES,
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
    "MATERIAL_MODEL_NAMES",
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

# quantum_conductor_v1 pulls in density.density_matrix_engine_4q's full
# dependency chain (notably scikit-learn); importing it eagerly here would
# make the whole package unimportable without that chain installed, even
# for callers who never touch quantum drive. Import it lazily instead.
try:
    from .quantum_conductor_v1 import (
        QuantumConductorConfig,
        QuantumPhaseConductor,
        SlowUpdate,
        coherence_phase_signals,
    )

    __all__ += [
        "QuantumConductorConfig",
        "QuantumPhaseConductor",
        "SlowUpdate",
        "coherence_phase_signals",
    ]
except ImportError:
    pass
