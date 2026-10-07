"""Auditable density-matrix to effective-metric observer pipeline.

The package is downstream of the authoritative quantum state.  Its potential,
metric, and Lorentz-like terms are effective model fields; they are not claims
that an abstract density matrix literally creates gravity or electromagnetism.
"""

from .config import (
    LorentzConfig,
    MetricConfig,
    PotentialConfig,
    QuantumMetricConfig,
    ResonatorConfig,
)
from .curved_lorentz import CurvedLorentzEngine, ParticleState
from .curved_modes import CurvedModeSolver
from .engine import QuantumMetricEngine
from .frames import (
    CurvedModeFrame,
    MetricFieldFrame,
    MetricShaderFrame,
    QMWMetricFrame,
    TrajectoryFrame,
)
from .grid import Grid2D
from .modal_resonator import ModalResonator
from .quantum_projector import QuantumSpatialProjector, localized_gaussian_basis
from .scientific_scenes import (
    ControlledScientificScenes,
    ScientificScene,
    build_controlled_scientific_scenes,
    completely_dephase,
)
from .visualization_controls import (
    OVERLAY_IDS,
    OverlayControl,
    VisualizationControls,
    analysis_visualization_controls,
    performance_visualization_controls,
)
from .visualizer_export import export_scientific_visualizer
from .authoritative_state import (
    AuthoritativeStateSnapshot,
    DensityMatrixEngineMetricAdapter,
    RevisionedDensityPairReceiver,
    RevisionedDensitySnapshot,
)
from .audio_acceptance import AudioAcceptanceConfig, render_isolated_audio_acceptance
from .live_transport import (
    ARRAY_FIELDS,
    CONTRACT as LIVE_FRAME_CONTRACT,
    FrameContractError,
    RevisionGate,
    decode_binary_frame,
    encode_binary_frame,
    encode_json_frame,
    shader_frame_to_payload,
)
from .unified_instrument import (
    UNIFIED_METRIC_OSC_PORT,
    UNIFIED_METRIC_OSC_ROOT,
    UNIFIED_METRIC_OSC_SCHEMA,
    UnifiedMetricFrame,
    UnifiedMetricObserver,
    UnifiedMetricOSCPublisher,
)

__all__ = [
    "CurvedLorentzEngine",
    "CurvedModeFrame",
    "CurvedModeSolver",
    "ControlledScientificScenes",
    "Grid2D",
    "LorentzConfig",
    "MetricConfig",
    "MetricFieldFrame",
    "MetricShaderFrame",
    "ModalResonator",
    "ParticleState",
    "PotentialConfig",
    "QuantumMetricConfig",
    "QuantumMetricEngine",
    "QMWMetricFrame",
    "QuantumSpatialProjector",
    "ResonatorConfig",
    "ScientificScene",
    "TrajectoryFrame",
    "OVERLAY_IDS",
    "OverlayControl",
    "VisualizationControls",
    "analysis_visualization_controls",
    "performance_visualization_controls",
    "export_scientific_visualizer",
    "AuthoritativeStateSnapshot",
    "DensityMatrixEngineMetricAdapter",
    "RevisionedDensityPairReceiver",
    "RevisionedDensitySnapshot",
    "AudioAcceptanceConfig",
    "render_isolated_audio_acceptance",
    "ARRAY_FIELDS",
    "LIVE_FRAME_CONTRACT",
    "FrameContractError",
    "RevisionGate",
    "decode_binary_frame",
    "encode_binary_frame",
    "encode_json_frame",
    "shader_frame_to_payload",
    "UNIFIED_METRIC_OSC_PORT",
    "UNIFIED_METRIC_OSC_ROOT",
    "UNIFIED_METRIC_OSC_SCHEMA",
    "UnifiedMetricFrame",
    "UnifiedMetricObserver",
    "UnifiedMetricOSCPublisher",
    "localized_gaussian_basis",
    "build_controlled_scientific_scenes",
    "completely_dephase",
]
