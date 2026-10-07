"""Read-only observables for one- and two-dimensional GPE fields.

This is the canonical GPE-facing module.  Scalar observations and raw modal
projections remain in the compatible :mod:`qmw.gpe_observables` module; 2-D
flow is supplied only by :mod:`qmw.qmw_probability_flow`.  It exposes no
event, OSC, or synthesis behavior.
"""

from ..gpe_observables import (
    GPEBoundaryFlux2D,
    GPEFlowFrame2D,
    GPEModalProjection,
    GPEObservables,
    observe_gpe_field,
    project_gpe_modes,
)
from ..qmw_probability_flow import FlowFrame2D, flow_from_wavefunction_2d

__all__ = [
    "GPEModalProjection",
    "GPEObservables",
    "GPEBoundaryFlux2D",
    "GPEFlowFrame2D",
    "FlowFrame2D",
    "flow_from_wavefunction_2d",
    "observe_gpe_field",
    "project_gpe_modes",
]
