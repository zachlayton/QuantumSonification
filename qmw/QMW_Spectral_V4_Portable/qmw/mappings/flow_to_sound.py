"""Explicit downstream mapping of GPE flow observations to renderer controls."""

from __future__ import annotations

from dataclasses import dataclass
import numpy as np

from qmw.gpe.field_frame import FieldFrame
from qmw.qmw_probability_flow import FlowFrame2D


@dataclass(frozen=True)
class GPEFlowSoundControls:
    """Continuous flow controls; they do not alter transport or Hamiltonian physics."""

    time: float
    pan: float
    motion: float
    boundary_flux: float


def flow_to_sound(frame: FieldFrame | FlowFrame2D) -> GPEFlowSoundControls:
    """Derive bounded renderer controls from observed probability current."""

    flow = frame.flow if isinstance(frame, FieldFrame) else frame
    if not isinstance(flow, FlowFrame2D):
        raise ValueError("flow_to_sound currently accepts a two-dimensional GPE flow frame.")
    velocity = flow.current / (flow.density[None, ...] + 1.0e-12)
    return GPEFlowSoundControls(
        time=float(flow.time), pan=float(np.tanh(np.mean(flow.current[0]))),
        motion=float(np.tanh(np.mean(np.linalg.norm(velocity, axis=0)))),
        boundary_flux=float(sum(item.magnitude for item in flow.boundary_fluxes)),
    )


__all__ = ["GPEFlowSoundControls", "flow_to_sound"]
