from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol

import numpy as np

from qmw.core.domain import Domain
from qmw.core.field_frame import ConservationData, ObservableData, StateData
from qmw.core.module_spec import ModuleSpec


@dataclass
class ControlState:
    """Performance controls for one tick. `potential` replaces V(x) when given;
    `params` carries model-specific controls."""
    potential: np.ndarray | None = None
    params: dict[str, Any] = field(default_factory=dict)


class PhysicsModel(Protocol):
    model_id: str
    domain: Domain
    specs: dict[str, ModuleSpec]

    def initialize(self) -> StateData: ...

    def apply_controls(self, state: StateData, controls: ControlState) -> float:
        """Apply controls before a step; return external work done on the system."""

    def step(self, state: StateData, dt: float) -> StateData: ...

    def compute_observables(self, state: StateData) -> ObservableData: ...

    def conserved_quantities(self, state: StateData, observables: ObservableData) -> ConservationData: ...

    def continuity_residual(self, before: StateData, after: StateData, dt: float) -> float | None: ...
