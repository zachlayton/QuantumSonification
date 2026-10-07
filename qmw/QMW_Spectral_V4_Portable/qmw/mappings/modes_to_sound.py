"""Explicit downstream mapping of complex GPE modes to renderer controls."""

from __future__ import annotations

from dataclasses import dataclass
import numpy as np

from qmw.gpe.field_frame import FieldFrame
from qmw.gpe.modal_engine import GPEModalFrame


@dataclass(frozen=True)
class GPEModeSoundControls:
    """Complex modal controls; phases remain separate from modal power."""

    time: float
    levels: np.ndarray
    phases: np.ndarray
    phase_velocity: np.ndarray


def modes_to_sound(frame: FieldFrame | GPEModalFrame) -> GPEModeSoundControls:
    """Expose complex modes to a renderer without treating them as GPE evolution."""

    if isinstance(frame, FieldFrame):
        return GPEModeSoundControls(
            time=frame.time, levels=np.sqrt(np.maximum(frame.mode_power, 0.0)),
            phases=np.array(frame.mode_phase, copy=True),
            phase_velocity=np.array(frame.mode_phase_velocity, copy=True),
        )
    return GPEModeSoundControls(
        time=frame.time, levels=np.abs(frame.amplitudes), phases=np.array(frame.phases, copy=True),
        phase_velocity=np.zeros_like(frame.phases),
    )


__all__ = ["GPEModeSoundControls", "modes_to_sound"]
