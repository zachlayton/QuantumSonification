"""Mass bins and a kinematic frame boundary; no quantum or sound state."""

from bisect import bisect_right
from collections import Counter
from dataclasses import asdict, dataclass
import math
import statistics

from .model import SCHEMA_VERSION, UNITS, ColliderDataset, ColliderEvent, finite_number

DEFAULT_EDGES_GEV = (340, 380, 450, 550, 700, 900, 1200, 1600)
BIN_CONVENTION = "[low, high), except the last bin includes its upper edge"


@dataclass(frozen=True)
class BinSpec:
    edges_gev: tuple[float, ...] = DEFAULT_EDGES_GEV

    def __post_init__(self):
        object.__setattr__(self, "edges_gev", tuple(self.edges_gev))
        if len(self.edges_gev) < 2:
            raise ValueError("provide at least two bin edges")
        for edge in self.edges_gev:
            finite_number(edge, "bin edge")
            if edge < 0:
                raise ValueError("mass bin edges must be nonnegative")
        if any(a >= b for a, b in zip(self.edges_gev, self.edges_gev[1:])):
            raise ValueError("bin edges must be strictly increasing")

    def locate(self, mass_gev: float) -> int | None:
        finite_number(mass_gev, "mass_gev")
        if mass_gev < self.edges_gev[0] or mass_gev > self.edges_gev[-1]:
            return None
        return min(bisect_right(self.edges_gev, mass_gev) - 1, len(self.edges_gev) - 2)


@dataclass(frozen=True)
class BinStatistics:
    count: int
    fraction_of_all_events: float
    sum_weights: float
    sum_weights_squared: float
    mean_mass_gev: float | None
    std_mass_gev: float | None
    min_mass_gev: float | None
    max_mass_gev: float | None


@dataclass(frozen=True)
class PhaseSpaceFrame:
    """A selected ensemble's kinematic summary, not a ColliderQuantumFrame."""

    dataset_id: str
    bin_index: int
    low_gev: float
    high_gev: float
    includes_upper_edge: bool
    statistics: BinStatistics
    schema_version: str = "collider-phase-space/1"
    axis: str = "m_ttbar"
    unit: str = "GeV (c=1)"


class ColliderBackend:
    def __init__(self, dataset: ColliderDataset, edges_gev=DEFAULT_EDGES_GEV):
        self.dataset = dataset
        self.bins = BinSpec(tuple(edges_gev))
        self._indices = [[] for _ in range(len(self.bins.edges_gev) - 1)]
        self.masses_gev = tuple(event.mass_gev for event in dataset.events)
        self.underflow = 0
        self.overflow = 0
        for index, mass in enumerate(self.masses_gev):
            which = self.bins.locate(mass)
            if which is None:
                if mass < self.bins.edges_gev[0]:
                    self.underflow += 1
                else:
                    self.overflow += 1
            else:
                self._indices[which].append(index)
        self._frames = tuple(self._make_frame(i) for i in range(len(self._indices)))
        self.selected_index = 0

    def _make_frame(self, index: int) -> PhaseSpaceFrame:
        rows = self._indices[index]
        masses = [self.masses_gev[i] for i in rows]
        weights = [self.dataset.events[i].weight for i in rows]
        stats = BinStatistics(
            count=len(rows), fraction_of_all_events=len(rows) / len(self.dataset.events)
            if self.dataset.events else 0.0,
            sum_weights=math.fsum(weights), sum_weights_squared=math.fsum(w*w for w in weights),
            mean_mass_gev=statistics.fmean(masses) if masses else None,
            std_mass_gev=statistics.pstdev(masses) if masses else None,
            min_mass_gev=min(masses) if masses else None,
            max_mass_gev=max(masses) if masses else None,
        )
        return PhaseSpaceFrame(self.dataset.provenance.dataset_id, index,
                               self.bins.edges_gev[index], self.bins.edges_gev[index + 1],
                               index == len(self._indices) - 1, stats)

    def select_bin(self, index: int) -> PhaseSpaceFrame:
        if type(index) is not int or not 0 <= index < len(self._frames):
            raise IndexError("bin index is out of range")
        self.selected_index = index
        return self.current_frame

    def select_mass(self, mass_gev: float) -> PhaseSpaceFrame:
        index = self.bins.locate(mass_gev)
        if index is None:
            raise ValueError("mass is outside the configured bin range")
        return self.select_bin(index)

    def step(self, delta: int) -> PhaseSpaceFrame:
        if type(delta) is not int:
            raise ValueError("step must be an integer")
        return self.select_bin(max(0, min(len(self._frames) - 1, self.selected_index + delta)))

    @property
    def current_frame(self) -> PhaseSpaceFrame:
        return self._frames[self.selected_index]

    def selected_events(self) -> tuple[ColliderEvent, ...]:
        return tuple(self.dataset.events[i] for i in self._indices[self.selected_index])

    def summary(self) -> dict:
        """Export only Python-computed aggregates to the report; no re-binning in JS."""
        return {
            "experiment": "CERN/QMW 001A", "event_schema_version": SCHEMA_VERSION,
            "units": dict(UNITS), "provenance": asdict(self.dataset.provenance),
            "input_path": self.dataset.input_path, "input_sha256": self.dataset.input_sha256,
            "total_events": len(self.dataset.events),
            "in_range_events": sum(len(x) for x in self._indices),
            "underflow": self.underflow, "overflow": self.overflow,
            "edges_gev": self.bins.edges_gev, "bin_convention": BIN_CONVENTION,
            "statistics_convention": "Unweighted mass mean and population standard deviation; "
                                     "fractions use all input events including flow bins. "
                                     "sum_weights and sum_weights_squared are separate from counts.",
            "mass_sources": dict(Counter(event.mass_source for event in self.dataset.events)),
            "selected_bin": self.selected_index,
            "bins": [asdict(frame) for frame in self._frames],
        }
