"""Phase 4 compositional navigation for Wilson quantum geometry.

MOS navigation controls melodic resolution while stable generator-power IDs
prevent voices from being reassigned when notes enter or leave a Scale-Tree
ancestor/descendant morph.  Constant Structure validation remains a separate
test on an ordered rational scale.  CPS subspaces describe orchestration inside
larger Pascal instruments such as the 3)6 Eikosany.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from heapq import heappop, heappush
from math import cos, pi, sin
from typing import Iterable, Sequence

from .cps import CombinationProductSet, PascalCPSShell, pascal_cps_row
from .mos import MOSScale, make_mos, scale_tree_position


def _fold(value: Fraction, period: Fraction) -> Fraction:
    while value < 1:
        value *= period
    while value >= period:
        value /= period
    return value


@dataclass(frozen=True)
class ConstantStructureOccurrence:
    source_degree: int
    target_degree: int
    steps: int


@dataclass(frozen=True)
class ConstantStructureViolation:
    interval: Fraction
    step_counts: tuple[int, ...]
    occurrences: tuple[ConstantStructureOccurrence, ...]


@dataclass(frozen=True)
class ConstantStructureReport:
    ordered_ratios: tuple[Fraction, ...]
    period: Fraction
    interval_class_count: int
    violations: tuple[ConstantStructureViolation, ...]

    @property
    def is_constant_structure(self) -> bool:
        return not self.violations


def validate_constant_structure(
    ordered_ratios: Iterable[int | Fraction],
    *,
    period: int | Fraction = 2,
) -> ConstantStructureReport:
    """Test Wilson's exact interval/step-count invariance.

    Ratios must be supplied in ascending pitch order within one period.  Every
    directed interval occurrence is period-folded; a scale fails exactly when
    one interval class occurs with more than one circular scale-step count.
    """
    period_fraction = Fraction(period)
    if period_fraction <= 1:
        raise ValueError("period must be greater than one")
    ratios = tuple(_fold(Fraction(value), period_fraction) for value in ordered_ratios)
    if len(ratios) < 2:
        raise ValueError("a candidate scale must contain at least two ratios")
    if len(set(ratios)) != len(ratios):
        raise ValueError("candidate scale ratios must be unique within the period")
    if any(left >= right for left, right in zip(ratios, ratios[1:])):
        raise ValueError("candidate ratios must be in ascending pitch order")

    occurrences: dict[Fraction, list[ConstantStructureOccurrence]] = {}
    size = len(ratios)
    for source in range(size):
        for target in range(size):
            if source == target:
                continue
            interval = _fold(ratios[target] / ratios[source], period_fraction)
            steps = (target - source) % size
            occurrences.setdefault(interval, []).append(
                ConstantStructureOccurrence(source, target, steps)
            )

    violations = []
    for interval, items in sorted(occurrences.items()):
        step_counts = tuple(sorted({item.steps for item in items}))
        if len(step_counts) > 1:
            violations.append(
                ConstantStructureViolation(
                    interval=interval,
                    step_counts=step_counts,
                    occurrences=tuple(items),
                )
            )
    return ConstantStructureReport(
        ordered_ratios=ratios,
        period=period_fraction,
        interval_class_count=len(occurrences),
        violations=tuple(violations),
    )


@dataclass(frozen=True)
class MOSVoiceFrame:
    """One stable generator-power identity during a Scale-Tree morph."""

    voice_id: int
    generator_power: int
    position: float
    ratio: float
    activation: float
    source_order: int | None
    target_order: int | None


@dataclass(frozen=True)
class MOSMorphFrame:
    source: Fraction
    target: Fraction
    progress: float
    source_scale: MOSScale
    target_scale: MOSScale
    voices: tuple[MOSVoiceFrame, ...]

    @property
    def active_voice_count(self) -> float:
        return sum(voice.activation for voice in self.voices)


def _generator_order(scale: MOSScale) -> dict[int, int]:
    pairs = sorted(
        (power, (power * scale.generator_fraction) % 1.0)
        for power in range(scale.size)
    )
    pairs.sort(key=lambda item: item[1])
    return {power: order for order, (power, _position) in enumerate(pairs)}


class MOSScaleTreeNavigator:
    """Voice-stable navigation between related MOS Scale-Tree positions."""

    def __init__(
        self,
        generator_ratio: float,
        initial: Fraction | tuple[int, int],
        *,
        period: float = 2.0,
    ) -> None:
        self.generator_ratio = float(generator_ratio)
        self.period = float(period)
        self.current = self._fraction(initial)
        self._scale(self.current)
        self.source = self.current
        self.target = self.current
        self.progress = 1.0

    @staticmethod
    def _fraction(value: Fraction | tuple[int, int]) -> Fraction:
        return value if isinstance(value, Fraction) else Fraction(*value)

    def _scale(self, position: Fraction) -> MOSScale:
        if not 0 < position < 1 or position.denominator < 2:
            raise ValueError("MOS Scale-Tree positions must have size at least two")
        scale = make_mos(self.generator_ratio, position.denominator, period=self.period)
        if not scale.is_moment_of_symmetry or scale.scale_type != position:
            raise ValueError(
                f"{position} is not a MOS position for generator {self.generator_ratio}"
            )
        return scale

    @staticmethod
    def _related(left: Fraction, right: Fraction) -> bool:
        left_ancestors = scale_tree_position(left.numerator, left.denominator).ancestors
        right_ancestors = scale_tree_position(right.numerator, right.denominator).ancestors
        return left in right_ancestors or right in left_ancestors

    def begin(self, target: Fraction | tuple[int, int]) -> MOSMorphFrame:
        requested = self._fraction(target)
        self._scale(requested)
        if not self._related(self.current, requested):
            raise ValueError("MOS morph target must be an ancestor or descendant")
        self.source = self.current
        self.target = requested
        self.progress = 0.0
        return self.frame()

    def set_progress(self, progress: float) -> MOSMorphFrame:
        self.progress = max(0.0, min(1.0, float(progress)))
        frame = self.frame()
        if self.progress >= 1.0:
            self.current = self.target
        return frame

    def frame(self) -> MOSMorphFrame:
        source_scale = self._scale(self.source)
        target_scale = self._scale(self.target)
        source_order = _generator_order(source_scale)
        target_order = _generator_order(target_scale)
        progress = self.progress
        enter_gain = sin(progress * pi / 2.0) ** 2
        leave_gain = cos(progress * pi / 2.0) ** 2
        voices = []
        for power in range(max(source_scale.size, target_scale.size)):
            in_source = power < source_scale.size
            in_target = power < target_scale.size
            if in_source and in_target:
                activation = 1.0
            elif in_target:
                activation = enter_gain
            else:
                activation = leave_gain
            position = (power * target_scale.generator_fraction) % 1.0
            voices.append(
                MOSVoiceFrame(
                    voice_id=power,
                    generator_power=power,
                    position=position,
                    ratio=self.period**position,
                    activation=activation,
                    source_order=source_order.get(power),
                    target_order=target_order.get(power),
                )
            )
        return MOSMorphFrame(
            source=self.source,
            target=self.target,
            progress=progress,
            source_scale=source_scale,
            target_scale=target_scale,
            voices=tuple(voices),
        )


@dataclass(frozen=True)
class CPSSubspace:
    parent_name: str
    fixed_included: tuple[int, ...]
    fixed_excluded: tuple[int, ...]
    residual_cps: CombinationProductSet
    parent_tone_indices: tuple[int, ...]

    @property
    def dimension(self) -> int:
        return len(self.parent_tone_indices)


def cps_subspace(
    parent: CombinationProductSet,
    *,
    fixed_included: Sequence[int] = (),
    fixed_excluded: Sequence[int] = (),
) -> CPSSubspace:
    """Describe a lower-dimensional CPS obtained by fixing factor occupancy."""
    included = tuple(sorted(int(index) for index in fixed_included))
    excluded = tuple(sorted(int(index) for index in fixed_excluded))
    universe = set(range(len(parent.factors)))
    if set(included) & set(excluded):
        raise ValueError("included and excluded factor positions must be disjoint")
    if not set(included).issubset(universe) or not set(excluded).issubset(universe):
        raise ValueError("fixed factor position is outside the parent CPS")
    residual_indices = tuple(sorted(universe.difference(included).difference(excluded)))
    residual_grade = parent.grade - len(included)
    if not 1 <= residual_grade < len(residual_indices):
        raise ValueError("fixed occupancy does not leave a nontrivial residual CPS")
    residual = CombinationProductSet(
        tuple(parent.factors[index] for index in residual_indices),
        residual_grade,
        period=parent.period,
    )
    selected = tuple(
        tone.index
        for tone in parent.tones
        if set(included).issubset(tone.factor_indices)
        and not set(excluded).intersection(tone.factor_indices)
    )
    if len(selected) != residual.dimension:
        raise RuntimeError("residual CPS dimension does not match selected parent tones")
    return CPSSubspace(
        parent_name=parent.name,
        fixed_included=included,
        fixed_excluded=excluded,
        residual_cps=residual,
        parent_tone_indices=selected,
    )


class PascalInstrumentation:
    """Treat every grade of one factor set as an addressable instrument."""

    def __init__(self, factors: Sequence[int], *, period: int | Fraction = 2) -> None:
        self.factors = tuple(int(value) for value in factors)
        self.period = Fraction(period)
        self.row = pascal_cps_row(len(self.factors))
        self.selected_grade = len(self.factors) // 2

    def select_grade(self, grade: int) -> PascalCPSShell:
        selected = int(grade)
        if not 0 <= selected <= len(self.factors):
            raise ValueError("grade is outside the Pascal instrument")
        self.selected_grade = selected
        return self.row[selected]

    def cps(self, grade: int | None = None) -> CombinationProductSet:
        selected = self.selected_grade if grade is None else int(grade)
        if selected in {0, len(self.factors)}:
            raise ValueError("Pascal poles are one-tone shells, not nontrivial CPS graphs")
        return CombinationProductSet(self.factors, selected, period=self.period)

    def eikosany_subspaces(self) -> dict[str, tuple[CPSSubspace, ...]]:
        if len(self.factors) != 6 or self.selected_grade != 3:
            raise ValueError("Eikosany subspaces require selected grade 3)6")
        parent = self.cps()
        dekany_2_5 = tuple(
            cps_subspace(parent, fixed_included=(index,)) for index in range(6)
        )
        dekany_3_5 = tuple(
            cps_subspace(parent, fixed_excluded=(index,)) for index in range(6)
        )
        hexanies = tuple(
            cps_subspace(parent, fixed_included=(included,), fixed_excluded=(excluded,))
            for included in range(6)
            for excluded in range(6)
            if included != excluded
        )
        return {
            "dekany_2_5": dekany_2_5,
            "dekany_3_5": dekany_3_5,
            "hexany_2_4": hexanies,
        }


@dataclass(frozen=True)
class CPSPathEvent:
    """One vertex arrival shared by pitch, geometry, and timing layers."""

    order: int
    tone_index: int
    bitmask: int
    ratio: Fraction
    spectral_position: float
    arrival_ms: float
    duration_ms: float
    eigenfield_weight: float


@dataclass(frozen=True)
class CPSPathTimeline:
    cps_name: str
    vertex_indices: tuple[int, ...]
    total_duration_ms: float
    events: tuple[CPSPathEvent, ...]


def plan_cps_graph_path(
    cps: CombinationProductSet,
    source: int,
    target: int,
    *,
    total_duration_ms: float = 1000.0,
    eigenfield_values: Sequence[float] | None = None,
) -> CPSPathTimeline:
    """Find a minimum-harmonic-distance path and place it in musical time.

    Every transition remains a Johnson-graph factor exchange.  Tenney harmonic
    distance chooses the route.  Optional eigenfield magnitudes locally dilate
    time: weak regions last longer and strong regions move faster.  The result
    contains exact CPS ratios plus normalized log-period spectral positions, so
    one path can drive pitch, spectral geometry, and an external timing layer.
    """
    start = int(source)
    finish = int(target)
    if not 0 <= start < cps.dimension or not 0 <= finish < cps.dimension:
        raise ValueError("CPS path endpoint is outside the graph")
    total = float(total_duration_ms)
    if total <= 0:
        raise ValueError("total_duration_ms must be positive")
    if eigenfield_values is None:
        field = (1.0,) * cps.dimension
    else:
        if len(eigenfield_values) != cps.dimension:
            raise ValueError("eigenfield_values must contain one value per CPS vertex")
        field = tuple(abs(float(value)) for value in eigenfield_values)

    adjacency: dict[int, list[tuple[int, float]]] = {
        index: [] for index in range(cps.dimension)
    }
    for edge in cps.perceptual_edges():
        adjacency[edge.source].append((edge.target, edge.harmonic_distance))
        adjacency[edge.target].append((edge.source, edge.harmonic_distance))
    distances = [float("inf")] * cps.dimension
    predecessor: list[int | None] = [None] * cps.dimension
    distances[start] = 0.0
    queue: list[tuple[float, int]] = [(0.0, start)]
    while queue:
        distance, vertex = heappop(queue)
        if distance != distances[vertex]:
            continue
        if vertex == finish:
            break
        for neighbor, cost in sorted(adjacency[vertex]):
            candidate = distance + cost
            if candidate < distances[neighbor] - 1e-12:
                distances[neighbor] = candidate
                predecessor[neighbor] = vertex
                heappush(queue, (candidate, neighbor))

    path = [finish]
    while path[-1] != start:
        previous = predecessor[path[-1]]
        if previous is None:
            raise RuntimeError("CPS graph endpoints are disconnected")
        path.append(previous)
    path.reverse()

    edge_cost = {
        frozenset((edge.source, edge.target)): edge.harmonic_distance
        for edge in cps.perceptual_edges()
    }
    raw_durations = []
    for left, right in zip(path, path[1:]):
        strength = max(1e-6, (field[left] + field[right]) / 2.0)
        raw_durations.append(edge_cost[frozenset((left, right))] / strength)
    raw_total = sum(raw_durations)
    durations = (
        [total]
        if len(path) == 1
        else [total * value / raw_total for value in raw_durations]
    )

    arrivals = [0.0]
    for duration in durations[:-1] if len(path) == 1 else durations:
        arrivals.append(arrivals[-1] + duration)
    events = []
    for order, vertex in enumerate(path):
        tone = cps.tones[vertex]
        duration = durations[order] if order < len(durations) else 0.0
        events.append(
            CPSPathEvent(
                order=order,
                tone_index=vertex,
                bitmask=tone.bitmask,
                ratio=Fraction(tone.ratio_numerator, tone.ratio_denominator),
                spectral_position=tone.cents / 1200.0,
                arrival_ms=arrivals[order],
                duration_ms=duration,
                eigenfield_weight=field[vertex],
            )
        )
    return CPSPathTimeline(
        cps_name=cps.name,
        vertex_indices=tuple(path),
        total_duration_ms=total,
        events=tuple(events),
    )


__all__ = [
    "CPSSubspace",
    "CPSPathEvent",
    "CPSPathTimeline",
    "ConstantStructureOccurrence",
    "ConstantStructureReport",
    "ConstantStructureViolation",
    "MOSMorphFrame",
    "MOSScaleTreeNavigator",
    "MOSVoiceFrame",
    "PascalInstrumentation",
    "cps_subspace",
    "plan_cps_graph_path",
    "validate_constant_structure",
]
