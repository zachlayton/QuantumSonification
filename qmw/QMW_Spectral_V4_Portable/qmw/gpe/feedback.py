"""Explicit, opt-in control actions that modify a GPE engine.

Sound or event systems may request a control action, but no feedback exists
until a host creates an enabled controller and calls ``apply``. Applying one
changes future evolution and is therefore distinct from observation.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import numpy as np

from qmw.qmw_gpe import GPEEngine, GPEState

Target = Literal["potential", "interaction", "wavefunction"]
Operation = Literal["set", "add", "scale"]
Origin = Literal["event", "sound"]


@dataclass(frozen=True)
class GPEFeedbackCommand:
    """A declared intervention, never an implicit consequence of sound."""
    target: Target
    operation: Operation
    value: float | complex | np.ndarray
    origin: Origin
    reason: str


class OptInGPEFeedbackController:
    """Apply validated event/sound interventions only after explicit opt-in."""
    def __init__(self, engine: GPEEngine, *, enabled: bool = False) -> None:
        self.engine = engine
        self.enabled = bool(enabled)
        self.applied_commands: list[GPEFeedbackCommand] = []

    def apply(self, command: GPEFeedbackCommand) -> GPEState:
        if not self.enabled:
            raise PermissionError("GPE feedback is disabled; enable it explicitly before applying commands.")
        if not command.reason.strip():
            raise ValueError("feedback commands require a nonempty reason.")
        state = self.engine.state()
        if command.target == "potential":
            if command.operation not in ("set", "add"):
                raise ValueError("potential feedback permits only set or add.")
            value = np.asarray(command.value, dtype=float)
            result = self.engine.set_potential(value if command.operation == "set" else state.potential + value)
        elif command.target == "interaction":
            if command.operation not in ("set", "scale"):
                raise ValueError("interaction feedback permits only set or scale.")
            value = np.asarray(command.value, dtype=float)
            result = self.engine.set_interaction(value if command.operation == "set" else state.interaction_field * value)
        elif command.target == "wavefunction":
            if command.operation not in ("set", "add", "scale"):
                raise ValueError("wavefunction feedback permits set, add, or scale.")
            value = np.asarray(command.value, dtype=np.complex128)
            next_value = value if command.operation == "set" else (state.psi + value if command.operation == "add" else state.psi * value)
            result = self.engine.set_wavefunction(next_value)
        else:
            raise ValueError(f"unrecognized feedback target: {command.target!r}")
        self.applied_commands.append(command)
        return result


__all__ = ["GPEFeedbackCommand", "OptInGPEFeedbackController"]
