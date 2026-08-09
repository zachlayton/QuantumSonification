"""Read, write, and project Scala ``.scl`` tuning files."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
import math
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class ScalaScale:
    description: str
    ratios: tuple[float, ...]
    tokens: tuple[str, ...]

    def __post_init__(self) -> None:
        if len(self.ratios) != len(self.tokens):
            raise ValueError("Scala ratios and tokens must have equal length")
        if any(not math.isfinite(ratio) or ratio <= 0.0 for ratio in self.ratios):
            raise ValueError("Scala pitch ratios must be finite and positive")

    @property
    def size(self) -> int:
        return len(self.ratios)

    @property
    def period(self) -> float:
        return self.ratios[-1] if self.ratios else 2.0

    @property
    def pitch_classes(self) -> tuple[float, ...]:
        if not self.ratios:
            return (1.0,)
        explicit = self.ratios[:-1] if self.period > 1.0 else self.ratios
        return (1.0, *explicit)


@dataclass(frozen=True)
class ScalaConstantStructureAnalysis:
    """Tolerance-aware constant-structure result for an imported Scala scale."""

    is_constant_structure: bool
    interval_class_count: int
    conflicting_class_count: int
    tolerance_cents: float


def analyze_scala_constant_structure(
    scale: ScalaScale,
    *,
    tolerance_cents: float = 0.1,
) -> ScalaConstantStructureAnalysis:
    """Test whether each sounding interval always spans one generic distance.

    Scala files may contain decimal cents, so interval equality is clustered
    using a small cents tolerance rather than requiring identical floats.
    """
    pitches = scale.pitch_classes
    size = len(pitches)
    if size < 2:
        raise ValueError("constant-structure analysis needs at least two degrees")
    period_cents = 1200.0 * math.log2(scale.period)
    if period_cents <= 0.0:
        raise ValueError("constant-structure analysis requires a positive period")

    occurrences: list[tuple[float, int]] = []
    for source in range(size):
        for target in range(size):
            if source == target:
                continue
            cents = (
                1200.0 * math.log2(pitches[target] / pitches[source])
            ) % period_cents
            steps = (target - source) % size
            occurrences.append((cents, steps))

    occurrences.sort()
    classes: list[tuple[float, set[int]]] = []
    for cents, steps in occurrences:
        if not classes or cents - float(classes[-1][0]) > tolerance_cents:
            classes.append((cents, {steps}))
        else:
            classes[-1][1].add(steps)
    if (
        len(classes) > 1
        and float(classes[0][0]) + period_cents - float(classes[-1][0])
        <= tolerance_cents
    ):
        classes[0][1].update(classes[-1][1])
        classes.pop()
    conflicts = sum(len(step_counts) > 1 for _, step_counts in classes)
    return ScalaConstantStructureAnalysis(
        is_constant_structure=conflicts == 0,
        interval_class_count=len(classes),
        conflicting_class_count=conflicts,
        tolerance_cents=tolerance_cents,
    )


def _pitch_token(token: str) -> float:
    if "." in token:
        cents = float(token)
        return 2.0 ** (cents / 1200.0)
    if "/" in token:
        if token.count("/") != 1:
            raise ValueError(f"invalid Scala ratio: {token}")
        value = Fraction(token)
        if value <= 0:
            raise ValueError("Scala ratios must be positive")
        return float(value)
    value = int(token)
    if value <= 0:
        raise ValueError("Scala integer ratios must be positive")
    return float(value)


def parse_scl(text: str) -> ScalaScale:
    """Parse one Scala scale, preserving each original pitch token."""
    lines = [
        line.rstrip("\r\n")
        for line in text.splitlines()
        if not line.lstrip().startswith("!")
    ]
    if len(lines) < 2:
        raise ValueError("Scala file needs a description and note count")
    description = lines[0].strip()
    try:
        count = int(lines[1].strip().split()[0])
    except (IndexError, ValueError) as exc:
        raise ValueError("invalid Scala note count") from exc
    if count < 0:
        raise ValueError("Scala note count cannot be negative")

    tokens: list[str] = []
    for line in lines[2:]:
        fields = line.strip().split()
        if fields:
            tokens.append(fields[0])
        if len(tokens) == count:
            break
    if len(tokens) != count:
        raise ValueError(f"Scala file declares {count} pitches but contains {len(tokens)}")
    ratios = tuple(_pitch_token(token) for token in tokens)
    return ScalaScale(description=description, ratios=ratios, tokens=tuple(tokens))


def load_scl(path: str | Path) -> ScalaScale:
    return parse_scl(Path(path).read_text(encoding="latin-1"))


def format_scl(scale: ScalaScale, *, filename: str = "qmw_export.scl") -> str:
    lines = [
        f"! {Path(filename).name}",
        "!",
        scale.description,
        f" {scale.size}",
        "!",
    ]
    lines.extend(f" {token}" for token in scale.tokens)
    return "\n".join(lines) + "\n"


def save_scl(path: str | Path, scale: ScalaScale) -> Path:
    output = Path(path)
    if output.suffix.lower() != ".scl":
        output = output.with_suffix(".scl")
    output.write_text(format_scl(scale, filename=output.name), encoding="latin-1")
    return output


def scala_scale_from_ratios(
    ratios: Iterable[float],
    *,
    description: str,
    tolerance: float = 1e-9,
) -> ScalaScale:
    """Build a sorted octave scale, using exact-looking ratios when possible."""
    folded = []
    for raw_ratio in ratios:
        ratio = float(raw_ratio)
        while ratio < 1.0:
            ratio *= 2.0
        while ratio >= 2.0:
            ratio /= 2.0
        if ratio > 1.0 + tolerance:
            folded.append(ratio)
    unique: list[float] = []
    for ratio in sorted(folded):
        if not unique or abs(math.log2(ratio / unique[-1])) > tolerance:
            unique.append(ratio)
    unique.append(2.0)

    tokens = []
    for ratio in unique:
        rational = Fraction(ratio).limit_denominator(1_000_000)
        if abs(float(rational) - ratio) <= tolerance:
            tokens.append(f"{rational.numerator}/{rational.denominator}")
        else:
            tokens.append(f"{1200.0 * math.log2(ratio):.8f}")
    return ScalaScale(description, tuple(unique), tuple(tokens))


def project_ratio_index_to_scala(ratio: float, scale: ScalaScale) -> int:
    """Return the nearest periodic Scala degree for a harmonic ratio."""
    period = scale.period
    if period <= 1.0:
        raise ValueError("Scala projection requires a period greater than one")
    value = float(ratio)
    while value < 1.0:
        value *= period
    while value >= period:
        value /= period
    position = math.log(value) / math.log(period)

    def distance(candidate: float) -> float:
        candidate_position = math.log(candidate) / math.log(period)
        delta = (candidate_position - position + 0.5) % 1.0 - 0.5
        return abs(delta)

    return min(
        range(len(scale.pitch_classes)),
        key=lambda index: distance(scale.pitch_classes[index]),
    )


def project_ratio_to_scala(ratio: float, scale: ScalaScale) -> float:
    """Project a harmonic ratio onto the nearest degree of a periodic scale."""
    return scale.pitch_classes[project_ratio_index_to_scala(ratio, scale)]
