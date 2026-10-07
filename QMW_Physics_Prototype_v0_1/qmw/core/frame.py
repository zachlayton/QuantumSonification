from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Protocol, Mapping
import numpy as np
from .domain import Domain

ControlState = Mapping[str, float | str | bool]


@dataclass
class StateData:
    psi: np.ndarray | None = None
    rho: np.ndarray | None = None
    phi: np.ndarray | None = None
    pi: np.ndarray | None = None

    def validate(self, domain: Domain):
        if domain.kind in ("time_history", "mode_index"):
            raise ValueError("Physics states require a spatial, graph or basis domain; history is a separate recording")
        if (self.phi is not None or self.pi is not None) and domain.kind != "space_1d":
            raise ValueError("This scalar engine requires a spatial field")
        if self.rho is not None and domain.kind not in ("basis_index", "graph"):
            raise ValueError("Density matrices require a declared finite basis or graph")
        variants = int(self.psi is not None) + int(self.rho is not None) + int(self.phi is not None or self.pi is not None)
        if variants != 1:
            raise ValueError("State must contain exactly one of psi, rho, or (phi, pi)")
        for name in ("psi", "rho", "phi", "pi"):
            value = getattr(self, name)
            if value is None: continue
            expected = (domain.size, domain.size) if name == "rho" else domain.shape
            if np.shape(value) != expected or not np.isfinite(value).all():
                raise ValueError(f"Invalid {name} shape or nonfinite state")
        if self.phi is not None and self.pi is None or self.pi is not None and self.phi is None:
            raise ValueError("Scalar field requires both phi and pi")


@dataclass
class ObservableData:
    probability_density: np.ndarray | None = None
    phase: np.ndarray | None = None
    probability_current: np.ndarray | None = None
    kinetic_energy_density: np.ndarray | None = None
    gradient_energy_density: np.ndarray | None = None
    potential_energy_density: np.ndarray | None = None
    total_energy_density: np.ndarray | None = None
    energy_flux: np.ndarray | None = None
    charge_density: np.ndarray | None = None
    charge_current: np.ndarray | None = None
    probability_rate: np.ndarray | None = None
    energy_rate: np.ndarray | None = None
    charge_rate: np.ndarray | None = None
    total_energy: float | None = None
    total_charge: float | None = None
    norm: float | None = None
    purity: float | None = None
    source_power: float = 0.0
    expectations: dict[str, float] = field(default_factory=dict)


@dataclass
class ConservationData:
    norm: float | None = None
    energy: float | None = None
    charge: float | None = None
    cumulative_work: float = 0.0
    cumulative_environment_energy: float = 0.0
    source_power: float = 0.0


@dataclass
class Diagnostics:
    norm_error: float | None = None
    energy_drift: float | None = None
    charge_drift: float | None = None
    probability_continuity_error: float | None = None
    energy_continuity_error: float | None = None
    charge_continuity_error: float | None = None
    positivity_error: float | None = None
    trace_error: float | None = None
    hermiticity_error: float | None = None
    spectral_tail_fraction: float | None = None
    notes: list[str] = field(default_factory=list)


@dataclass
class RegionalData:
    centers: np.ndarray
    probability: np.ndarray | None = None
    energy: np.ndarray | None = None
    charge: np.ndarray | None = None
    incoming_probability_flux: np.ndarray | None = None
    incoming_energy_flux: np.ndarray | None = None
    incoming_charge_flux: np.ndarray | None = None
    projection_id: str = "partition"


@dataclass
class ModalData:
    basis_id: str
    eigenvalues: np.ndarray
    coefficients: np.ndarray | None
    populations: np.ndarray
    captured_norm: float
    operator_semantics: str
    mode_labels: list[str] = field(default_factory=list)


class EventType(str, Enum):
    ENERGY_ARRIVAL = "energy_arrival"
    ENERGY_RELEASE = "energy_release"
    FLUX_CROSSING = "flux_crossing"
    MODE_CROSSING = "mode_crossing"
    LOCALIZATION = "localization"
    DELOCALIZATION = "delocalization"
    QUENCH = "quench"
    MEASUREMENT = "measurement"


@dataclass
class PhysicsEvent:
    type: EventType
    t: float
    magnitude: float
    source_observable: str
    region: int | None = None
    mode: int | None = None
    position: float | None = None
    frame_sequence: int = 0
    detail: str = ""


@dataclass
class PhysicsFrame:
    sequence: int
    t: float
    dt: float
    model_id: str
    domain: Domain
    state: StateData
    observables: ObservableData
    conservation: ConservationData = field(default_factory=ConservationData)
    regions: RegionalData | None = None
    modes: ModalData | None = None
    events: list[PhysicsEvent] = field(default_factory=list)
    diagnostics: Diagnostics = field(default_factory=Diagnostics)
    provenance: str = "simulation"
    schema_version: str = "qmw.physics/0.1"

    def validate(self):
        if not np.isfinite([self.t, self.dt]).all() or self.dt < 0 or self.sequence < 0:
            raise ValueError("Invalid simulation clock or sequence")
        self.state.validate(self.domain)
        for name, value in vars(self.observables).items():
            if isinstance(value, np.ndarray) and (value.shape != self.domain.shape or not np.isfinite(value).all()):
                raise ValueError(f"Invalid observable {name}")
            if isinstance(value, (float, int)) and not np.isfinite(value):
                raise ValueError(f"Nonfinite observable {name}")


@dataclass
class SoundEvent:
    event_id: str
    t: float
    frequency_hz: float
    amplitude: float
    decay_s: float
    pan: float
    region: int | None
    mode: int | None
    source_observable: str
    explanation: str


@dataclass
class SoundControlFrame:
    sequence: int
    t: float
    frequency_hz: np.ndarray
    amplitude: np.ndarray
    decay_s: np.ndarray
    phase: np.ndarray
    events: list[SoundEvent] = field(default_factory=list)
    mapping_id: str = "harmonic-plucks"


class PhysicsModel(Protocol):
    model_id: str
    domain: Domain
    def initialize(self, controls: ControlState | None = None) -> StateData: ...
    def step(self, state: StateData, controls: ControlState, dt: float) -> StateData: ...
    def compute_observables(self, state: StateData, controls: ControlState) -> ObservableData: ...
