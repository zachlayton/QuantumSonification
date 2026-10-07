"""QMW Unified Instrument V3 — Relational Resonant Field contracts.

V3 is an additive, read-only observer chain over the authoritative QMW
density-matrix engine.  It intentionally contains no DSP server, OSC
transport, or output-device policy: those are adapters layered on top of the
published frames.
"""

from importlib import import_module

from .boundary_hilbert import (
    BoundaryHilbertFrame,
    observe_acoustic_boundary_hilbert,
    observe_boundary_hilbert_field,
    synthesize_boundary_field,
)
from .frames import (
    AcousticFieldFrame,
    GeometryBoundaryFrame,
    ModalResonanceFrame,
    RelationalGeometryFrame,
    RelationalSpectralControlFrame,
    StereoObservationFrame,
    TuningGeometryFrame,
)
from .stereo import observe_mid_side_stereo
from .relational_geometry import (
    RelationalGeometryConfig,
    connected_pauli_correlation_tensors,
    observe_relational_geometry,
)
from .geometry_boundary import (
    GeometryBoundaryConfig,
    observe_geometry_boundary,
    real_fourier_boundary_basis,
)
from .tuning_geometry import (
    TuningGeometryConfig,
    lift_geometry_spectrum,
    observe_tuning_geometry,
)
from .modal_resonance import (
    ModalResonanceConfig,
    modal_shape_membership,
    observe_modal_resonance,
)
from .relational_spectral import (
    RelationalSpectralConfig,
    observe_relational_spectral_control,
)
from .relational_spectral_osc import (
    QMW_RELATIONAL_SPECTRAL_OSC_PORT,
    QMW_RELATIONAL_SPECTRAL_OSC_ROOT,
    QMW_RELATIONAL_SPECTRAL_OSC_SCHEMA,
    RelationalSpectralOSCPublisher,
)
from .acoustic_field import (
    AcousticFieldConfig,
    FlowExcitationFrame,
    PerformerEmphasisFrame,
    observe_acoustic_field,
)
from .matrix import (
    MatrixDomain,
    MatrixPort,
    MatrixRoute,
    MatrixSnapshot,
    PortType,
    VOICE_DECAY_IDS,
    normal_stereo_snapshot,
    route_voice_decays,
    voice_decay_ports,
)


# Modal geometry is an optional, separately packaged observer.  Importing the
# relational contracts used by the live Hilbert coordinator must not require
# its repository-only ``engine`` and Wilson/Scala dependencies.  These names
# retain their public API and load the modal package only when requested.
_LAZY_MODAL_EXPORTS = {
    "ModalGeometryConfig": (".modal_geometry", "ModalGeometryConfig"),
    "ModalGeometryFrame": (".modal_geometry", "ModalGeometryFrame"),
    "build_static_modal_geometry": (".modal_geometry", "build_static_modal_geometry"),
    "canonical_dodecahedral_topology": (".modal_geometry", "canonical_dodecahedral_topology"),
    "ModalGeometryOSCPublisher": (".modal_geometry_osc", "ModalGeometryOSCPublisher"),
    "QMW_MODAL_GEOMETRY_OSC_PORT": (".modal_geometry_osc", "QMW_MODAL_GEOMETRY_OSC_PORT"),
    "QMW_MODAL_GEOMETRY_OSC_ROOT": (".modal_geometry_osc", "QMW_MODAL_GEOMETRY_OSC_ROOT"),
    "QMW_MODAL_GEOMETRY_OSC_SCHEMA": (".modal_geometry_osc", "QMW_MODAL_GEOMETRY_OSC_SCHEMA"),
}


def __getattr__(name: str):
    target = _LAZY_MODAL_EXPORTS.get(name)
    if target is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    module_name, attribute = target
    value = getattr(import_module(module_name, __name__), attribute)
    globals()[name] = value
    return value

__all__ = [
    "AcousticFieldFrame",
    "AcousticFieldConfig",
    "BoundaryHilbertFrame",
    "FlowExcitationFrame",
    "GeometryBoundaryFrame",
    "GeometryBoundaryConfig",
    "ModalResonanceFrame",
    "ModalResonanceConfig",
    "MatrixDomain",
    "MatrixPort",
    "MatrixRoute",
    "MatrixSnapshot",
    "ModalGeometryConfig",
    "ModalGeometryFrame",
    "ModalGeometryOSCPublisher",
    "RelationalGeometryFrame",
    "RelationalSpectralControlFrame",
    "RelationalSpectralConfig",
    "RelationalGeometryConfig",
    "PerformerEmphasisFrame",
    "PortType",
    "StereoObservationFrame",
    "TuningGeometryFrame",
    "TuningGeometryConfig",
    "VOICE_DECAY_IDS",
    "observe_acoustic_boundary_hilbert",
    "observe_boundary_hilbert_field",
    "connected_pauli_correlation_tensors",
    "observe_mid_side_stereo",
    "observe_relational_geometry",
    "observe_relational_spectral_control",
    "QMW_RELATIONAL_SPECTRAL_OSC_PORT",
    "QMW_RELATIONAL_SPECTRAL_OSC_ROOT",
    "QMW_RELATIONAL_SPECTRAL_OSC_SCHEMA",
    "RelationalSpectralOSCPublisher",
    "QMW_MODAL_GEOMETRY_OSC_PORT",
    "QMW_MODAL_GEOMETRY_OSC_ROOT",
    "QMW_MODAL_GEOMETRY_OSC_SCHEMA",
    "observe_geometry_boundary",
    "observe_tuning_geometry",
    "observe_modal_resonance",
    "observe_acoustic_field",
    "modal_shape_membership",
    "normal_stereo_snapshot",
    "route_voice_decays",
    "voice_decay_ports",
    "real_fourier_boundary_basis",
    "lift_geometry_spectrum",
    "build_static_modal_geometry",
    "canonical_dodecahedral_topology",
    "synthesize_boundary_field",
]
