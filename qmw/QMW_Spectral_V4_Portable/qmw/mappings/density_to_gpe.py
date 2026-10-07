"""Explicit, non-equivalence mappings from density observables into GPE controls."""

from ..gpe.density_matrix_coupling import DensityMatrixGPEControl2D, density_matrix_to_gpe_control_2d
from ..gpe.dynamic_interaction import (
    CoherenceInteractionConfig,
    CoherenceInteractionControl,
    density_coherence_to_interaction,
    global_coherence_metric,
)

__all__ = [
    "CoherenceInteractionConfig",
    "CoherenceInteractionControl",
    "DensityMatrixGPEControl2D",
    "density_coherence_to_interaction",
    "density_matrix_to_gpe_control_2d",
    "global_coherence_metric",
]
