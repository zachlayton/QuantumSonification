"""Gross--Pitaevskii field helpers kept separate from transport and sound."""

from .observables import (
    GPEBoundaryFlux2D,
    GPEFlowFrame2D,
    FlowFrame2D,
    GPEModalProjection,
    GPEObservables,
    flow_from_wavefunction_2d,
    observe_gpe_field,
    project_gpe_modes,
)
from .geometry_engine import GeometryEigenbasis2D, GeometryPotential2D, GeometryPotentialEngine2D
from .modal_engine import GPEModalFrame, GPEModalProjector2D, ModalProjectorConfig
from .basis_engine import FourierBasis, FourierModeFrame, project_fourier_modes
from .geometry_mode_basis import GeometryModeBasis2D, GeometryModeFrame, separable_periodic_eigenbasis
from .field_frame import FieldFrame, observe_field_frame
from .density_matrix_coupling import DensityMatrixGPEControl2D, density_matrix_to_gpe_control_2d
from .dynamic_interaction import (
    CoherenceInteractionConfig,
    CoherenceInteractionControl,
    density_coherence_to_interaction,
    global_coherence_metric,
)
from .canonical_experiments import (
    CanonicalExperimentConfig,
    GPEExperimentResult,
    PhaseCollisionSweep,
    free_packet_experiment,
    harmonic_trap_experiment,
    phase_collision_experiment,
    repulsive_field_experiment,
)
from .vortices import (
    GPEVortex,
    GPEVortexFrame,
    detect_vortices_2d,
    vortex_pair_state_2d,
    vortex_state_2d,
)
from .solvers import GPEConfig, GPEEngine, GPEState
from .feedback import GPEFeedbackCommand, OptInGPEFeedbackController
from .phase_collision import PhaseCollisionExperiment2D, PhaseCollisionParameters
from .phase_collision_i import PhaseCollisionIConfig, PhaseCollisionITrace, PhaseCollisionISweep, phase_collision_i
from .region_flow import RegionFluxFrame, boundary_flux, observe_region_flux, region_population

__all__ = [
    "GPEModalProjection",
    "GPEObservables",
    "GPEBoundaryFlux2D",
    "GPEFlowFrame2D",
    "FlowFrame2D",
    "flow_from_wavefunction_2d",
    "observe_gpe_field",
    "project_gpe_modes",
    "GeometryPotential2D",
    "GeometryPotentialEngine2D",
    "GeometryEigenbasis2D",
    "GPEModalFrame",
    "GPEModalProjector2D",
    "ModalProjectorConfig",
    "FourierBasis",
    "FourierModeFrame",
    "project_fourier_modes",
    "GeometryModeBasis2D",
    "GeometryModeFrame",
    "separable_periodic_eigenbasis",
    "FieldFrame",
    "observe_field_frame",
    "DensityMatrixGPEControl2D",
    "density_matrix_to_gpe_control_2d",
    "CoherenceInteractionConfig",
    "CoherenceInteractionControl",
    "density_coherence_to_interaction",
    "global_coherence_metric",
    "CanonicalExperimentConfig",
    "GPEExperimentResult",
    "PhaseCollisionSweep",
    "free_packet_experiment",
    "harmonic_trap_experiment",
    "phase_collision_experiment",
    "repulsive_field_experiment",
    "GPEVortex",
    "GPEVortexFrame",
    "detect_vortices_2d",
    "vortex_pair_state_2d",
    "vortex_state_2d",
    "GPEConfig",
    "GPEEngine",
    "GPEState",
    "GPEFeedbackCommand",
    "OptInGPEFeedbackController",
    "PhaseCollisionExperiment2D",
    "PhaseCollisionParameters",
    "PhaseCollisionIConfig",
    "PhaseCollisionITrace",
    "PhaseCollisionISweep",
    "phase_collision_i",
    "RegionFluxFrame",
    "boundary_flux",
    "observe_region_flux",
    "region_population",
]
