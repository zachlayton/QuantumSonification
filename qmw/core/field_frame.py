"""FieldFrame: a snapshot of a simulated physical system at one control tick.

Not to be confused with `PhysicsFrame` (alias `PhysicsTrajectory`), which is a
2048-sample *time trajectory* block. A FieldFrame is one instant of a field over
an explicit spatial Domain, plus its observables, conservation diagnostics and
regional projection. It contains no audio parameters.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np

from qmw.core.domain import Domain


@dataclass
class StateData:
    psi: np.ndarray | None = None      # wavefunction (Schrödinger)
    rho: np.ndarray | None = None      # density matrix (Lindblad)
    phi: np.ndarray | None = None      # scalar field
    pi: np.ndarray | None = None       # conjugate momentum of phi


@dataclass
class ObservableData:
    """Per-node densities live on the Domain's nodes; `*_edges` arrays live on the
    links between nodes (length n+1 for Dirichlet, n for periodic)."""
    probability_density: np.ndarray | None = None
    phase: np.ndarray | None = None
    probability_current: np.ndarray | None = None
    probability_current_edges: np.ndarray | None = None
    kinetic_energy_density: np.ndarray | None = None
    potential_energy_density: np.ndarray | None = None
    total_energy_density: np.ndarray | None = None
    energy_flux: np.ndarray | None = None
    norm: float | None = None
    total_energy: float | None = None
    kinetic_energy: float | None = None
    potential_energy: float | None = None
    position_mean: float | None = None
    position_spread: float | None = None


@dataclass
class ConservationData:
    norm: float | None = None
    energy: float | None = None
    charge: float | None = None
    absorbed_probability: float = 0.0      # physical sink (absorbing boundary)
    external_work: float = 0.0             # physical source (time-dependent potential)


@dataclass
class Diagnostics:
    """Separates numerical error from physical dissipation.

    norm_error     = N + absorbed - N0              (should stay at round-off)
    energy_drift   = (E - E0 - work) / |E0|         (None when an absorber is active)
    probability_continuity_error = max |d rho/dt + div j + sink| / max |d rho/dt|
    """
    norm_error: float = 0.0
    energy_drift: float | None = None
    probability_continuity_error: float | None = None
    energy_continuity_error: float | None = None
    step_seconds: float | None = None


@dataclass
class RegionalData:
    probability: np.ndarray
    energy: np.ndarray
    kinetic_energy: np.ndarray
    potential_energy: np.ndarray
    probability_inflow: np.ndarray | None = None   # d/dt of regional probability, from div j
    energy_inflow: np.ndarray | None = None        # regional energy inflow, from div S
    centroids: np.ndarray | None = None


@dataclass
class FieldFrame:
    t: float
    dt: float
    step: int
    model_id: str
    domain: Domain
    state: StateData
    observables: ObservableData
    conservation: ConservationData
    diagnostics: Diagnostics
    regions: RegionalData | None = None
    events: list[Any] = field(default_factory=list)   # filled by event detectors (stage 5)
    metadata: dict[str, Any] = field(default_factory=dict)
