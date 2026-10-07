"""Regional summaries shared by spatial flow frames."""

from __future__ import annotations

import numpy as np

from .frame import FlowFrame, FlowFrame2D


def region_flux(frame: FlowFrame | FlowFrame2D) -> np.ndarray:
    if not isinstance(frame, (FlowFrame, FlowFrame2D)):
        raise ValueError("region_flux requires a spatial FlowFrame.")
    return np.array(frame.region_flux, copy=True)


def boundary_fluxes(frame: FlowFrame | FlowFrame2D) -> tuple[object, ...]:
    if not isinstance(frame, (FlowFrame, FlowFrame2D)):
        raise ValueError("boundary_fluxes requires a spatial FlowFrame.")
    return tuple(frame.boundary_fluxes)


__all__ = ["boundary_fluxes", "region_flux"]
