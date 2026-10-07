"""Declared perceptual mapping from GPE observations to sound controls.

This module does not evolve a field and never feeds data back into a GPE
engine. It gives SuperCollider, Max, or another renderer one compact,
inspectable control frame derived from physical observables.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from qmw.gpe.modal_engine import GPEModalFrame
from qmw.qmw_gpe import GPEState
from qmw.qmw_probability_flow import FlowFrame2D


@dataclass(frozen=True)
class GPESoundControls:
    """A renderer-facing control frame, explicitly not a GPE state."""

    time: float
    density_level: float
    density_peak: float
    flow_pan: float
    flow_motion: float
    modal_levels: np.ndarray
    modal_phases: np.ndarray


def gpe_observables_to_sound(
    state: GPEState,
    *,
    flow: FlowFrame2D | None = None,
    modal: GPEModalFrame | None = None,
) -> GPESoundControls:
    """Map observations to bounded audio controls without changing ``state``.

    Density controls amplitude; signed mean x-current controls stereo pan;
    mean speed controls timbral motion. Modal magnitudes and phases remain
    separate so a renderer can choose its own resonator bank.
    """

    if flow is not None and not np.isclose(flow.time, state.time):
        raise ValueError("flow and GPE state must have the same observation time.")
    if modal is not None and not np.isclose(modal.time, state.time):
        raise ValueError("modal frame and GPE state must have the same observation time.")
    if flow is None:
        flow_pan = flow_motion = 0.0
    else:
        velocity = np.divide(flow.current, flow.density[None, ...], out=np.zeros_like(flow.current), where=flow.density[None, ...] > 1.0e-12)
        flow_pan = float(np.tanh(np.mean(flow.current[0])))
        flow_motion = float(np.tanh(np.mean(np.linalg.norm(velocity, axis=0))))
    if modal is None:
        modal_levels, modal_phases = np.empty(0, dtype=float), np.empty(0, dtype=float)
    else:
        modal_levels = np.array(np.abs(modal.amplitudes), dtype=float, copy=True)
        modal_phases = np.array(modal.phases, dtype=float, copy=True)
    return GPESoundControls(
        time=float(state.time), density_level=float(np.sqrt(max(0.0, np.mean(state.density)))),
        density_peak=float(np.sqrt(max(0.0, np.max(state.density)))), flow_pan=flow_pan,
        flow_motion=flow_motion, modal_levels=modal_levels, modal_phases=modal_phases,
    )


__all__ = ["GPESoundControls", "gpe_observables_to_sound"]
