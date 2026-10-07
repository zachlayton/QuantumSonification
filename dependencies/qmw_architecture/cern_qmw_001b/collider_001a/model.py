"""Versioned, format-independent data contract. Natural units c=1, metric +---."""

from dataclasses import dataclass, field
import math

SCHEMA_VERSION = "collider-event/1"
UNITS = {"energy": "GeV", "momentum": "GeV", "mass": "GeV",
         "natural_units": "c=1", "metric": "+---"}


def finite_number(value: float, name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(f"{name} must be a finite number")


def nonempty_text(value: str, name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be nonempty text")


@dataclass(frozen=True)
class FourMomentum:
    """E, px, py, pz in GeV with c=1; order differs from ROOT's px,py,pz,E."""

    energy_gev: float
    px_gev: float
    py_gev: float
    pz_gev: float

    def __post_init__(self):
        for name, value in vars(self).items():
            finite_number(value, name)
        if self.energy_gev < 0:
            raise ValueError("energy_gev must be nonnegative")

    def __add__(self, other: "FourMomentum") -> "FourMomentum":
        return FourMomentum(self.energy_gev + other.energy_gev,
                            self.px_gev + other.px_gev,
                            self.py_gev + other.py_gev,
                            self.pz_gev + other.pz_gev)

    @property
    def mass_gev(self) -> float:
        # Scale before squaring to avoid overflow. Reject spacelike vectors,
        # except cancellation compatible with floating-point roundoff.
        scale = max(abs(x) for x in vars(self).values())
        if scale == 0:
            return 0.0
        e, px, py, pz = (x / scale for x in vars(self).values())
        mass2 = math.fsum((e * e, -px * px, -py * py, -pz * pz))
        tolerance = 1e-12 * math.fsum((e * e, px * px, py * py, pz * pz))
        if mass2 < -tolerance:
            raise ValueError("spacelike four-momentum: E² - |p|² < 0")
        return scale * math.sqrt(max(0.0, mass2))


def invariant_mass(top: FourMomentum, antitop: FourMomentum) -> float:
    """sqrt((E_t+E_tbar)^2 - |p_t+p_tbar|^2), in GeV (c=1)."""
    return (top + antitop).mass_gev


@dataclass(frozen=True)
class ColliderEvent:
    """One event; source_entry is zero-based in the declared source.

    Supply both parent four-vectors OR a precomputed mass. If both are supplied,
    four-vectors are authoritative and the stored mass is cross-checked.
    Weights may be signed; raw counts always count each record exactly once.
    """

    event_id: str
    source_entry: int
    top: FourMomentum | None = None
    antitop: FourMomentum | None = None
    m_ttbar_gev: float | None = None
    weight: float = 1.0

    def __post_init__(self):
        nonempty_text(self.event_id, "event_id")
        if type(self.source_entry) is not int or self.source_entry < 0:
            raise ValueError("source_entry must be a nonnegative integer")
        finite_number(self.weight, "weight")
        if not math.isfinite(self.weight * self.weight):
            raise ValueError("weight is too large for sumw2")
        if (self.top is None) != (self.antitop is None):
            raise ValueError("top and antitop must be provided together")
        if self.top is None and self.m_ttbar_gev is None:
            raise ValueError("provide parent four-vectors or m_ttbar_gev")
        if self.m_ttbar_gev is not None:
            finite_number(self.m_ttbar_gev, "m_ttbar_gev")
            if self.m_ttbar_gev < 0:
                raise ValueError("m_ttbar_gev must be nonnegative")
        if self.top is not None:
            for parent in (self.top, self.antitop):
                if not isinstance(parent, FourMomentum):
                    raise ValueError("parents must be FourMomentum objects")
                if parent.energy_gev <= 0 or parent.mass_gev <= 0:
                    raise ValueError("top parents must be future-directed and massive")
            computed = invariant_mass(self.top, self.antitop)
            if self.m_ttbar_gev is not None and not math.isclose(
                computed, self.m_ttbar_gev, rel_tol=1e-6, abs_tol=1e-6
            ):
                raise ValueError("stored m_ttbar_gev disagrees with parent four-vectors")

    @property
    def mass_gev(self) -> float:
        if self.top is not None:
            return invariant_mass(self.top, self.antitop)
        return self.m_ttbar_gev

    @property
    def mass_source(self) -> str:
        return "computed_from_parents" if self.top is not None else "read_from_dataset"


@dataclass(frozen=True)
class Provenance:
    dataset_id: str
    source_kind: str
    source_uri: str
    description: str
    selection: str
    generator: dict = field(default_factory=dict)

    def __post_init__(self):
        for name in ("dataset_id", "source_uri", "description", "selection"):
            nonempty_text(getattr(self, name), name)
        if self.source_kind not in ("synthetic", "mock", "simulation", "data"):
            raise ValueError("source_kind must be synthetic, mock, simulation, or data")
        if not isinstance(self.generator, dict):
            raise ValueError("generator must be a JSON object")


@dataclass(frozen=True)
class ColliderDataset:
    provenance: Provenance
    events: tuple[ColliderEvent, ...]
    input_path: str | None = None
    input_sha256: str | None = None

    def __post_init__(self):
        if not isinstance(self.provenance, Provenance):
            raise ValueError("provenance must be a Provenance object")
        object.__setattr__(self, "events", tuple(self.events))
        seen = set()
        for event in self.events:
            if not isinstance(event, ColliderEvent):
                raise ValueError("events must be ColliderEvent objects")
            if event.event_id in seen:
                raise ValueError(f"duplicate event_id: {event.event_id}")
            seen.add(event.event_id)
