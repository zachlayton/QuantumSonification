"""Read-only regional population and boundary-flux agreement over FieldFrames."""

from __future__ import annotations

from dataclasses import dataclass
import numpy as np

from ..qmw_probability_flow import FlowFrame2D
from .field_frame import FieldFrame


@dataclass(frozen=True)
class RegionFluxFrame:
    """Region populations and two compatible views of their transport.

    ``inward_flux`` is the finite-volume current across each declared region
    boundary.  ``population_rate`` is the frame-to-frame estimate of dP/dt.
    Their difference is the regional continuity residual.  ``outward_flux``
    is supplied explicitly to retain the conventional dP/dt = -Phi_outward.
    """

    time: float
    population: np.ndarray
    inward_flux: np.ndarray
    outward_flux: np.ndarray
    population_rate: np.ndarray | None
    continuity_residual: np.ndarray | None
    continuity_rms: float | None
    provenance: str = "read_only_fieldframe_region_population_boundary_flux"


def region_population(frame: FieldFrame) -> np.ndarray:
    """Return spatially integrated population for each declared region."""

    return np.array(frame.region_population, copy=True)


def boundary_flux(frame: FieldFrame, *, outward: bool = False) -> np.ndarray:
    """Return finite-volume boundary flux; default sign is net inward."""

    return np.array(-frame.region_flux if outward else frame.region_flux, copy=True)


def observe_region_flux(frame: FieldFrame, *, previous: FieldFrame | None = None) -> RegionFluxFrame:
    """Compare a frame's current-boundary flux to change in region population."""

    if not isinstance(frame.flow, FlowFrame2D):
        raise ValueError("regional GPE flux observation currently requires a two-dimensional FieldFrame.")
    population = region_population(frame)
    inward = boundary_flux(frame)
    rate: np.ndarray | None = None
    residual: np.ndarray | None = None
    rms: float | None = None
    if previous is not None:
        if not isinstance(previous.flow, FlowFrame2D) or previous.time >= frame.time:
            raise ValueError("previous FieldFrame must be compatible and strictly earlier.")
        if not np.array_equal(previous.flow.region_index, frame.flow.region_index):
            raise ValueError("previous FieldFrame must use the same declared region geometry.")
        previous_population = region_population(previous)
        if previous_population.shape != population.shape:
            raise ValueError("previous FieldFrame must use the same declared region geometry.")
        rate = (population - previous_population) / (frame.time - previous.time)
        residual = rate - inward
        rms = float(np.sqrt(np.mean(np.square(residual))))
    return RegionFluxFrame(
        time=frame.time, population=population, inward_flux=inward,
        outward_flux=-inward, population_rate=rate, continuity_residual=residual,
        continuity_rms=rms,
    )


__all__ = ["RegionFluxFrame", "boundary_flux", "observe_region_flux", "region_population"]
