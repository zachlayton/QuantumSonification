from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np


@dataclass
class QuantumStateFrame:
    """One observable snapshot emitted by a quantum engine tick.

    Engines produce frames. Instruments such as oscilloscopes, audio renderers,
    and visualizers consume them without owning the engine's evolution logic.
    """

    t: float
    dt: float
    rho: np.ndarray
    hamiltonian: Any | None = None
    source_name: str | None = None
    source_descriptor: Any | None = None
    observables: dict[str, Any] = field(default_factory=dict)
    arrays: dict[str, np.ndarray] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def dimension(self) -> int:
        return int(self.rho.shape[0])

    @property
    def populations(self) -> np.ndarray:
        return np.real(np.diag(self.rho))

    def array(self, name: str, default: np.ndarray | None = None) -> np.ndarray | None:
        return self.arrays.get(name, default)

    def observable(self, name: str, default: Any = None) -> Any:
        return self.observables.get(name, default)

