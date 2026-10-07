"""Offline geometric tuning and Scala dictionary support for QRM.

This module is a downstream pitch adapter. It never reads or mutates ``rho``.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
import math
from pathlib import Path


@dataclass(frozen=True)
class ScalaScale:
    name: str
    description: str
    degrees: tuple[float, ...]
    period: float
    path: Path | None = None

    def __post_init__(self) -> None:
        if not self.degrees:
            raise ValueError("a tuning requires at least the implicit 1/1 degree")
        values = (*self.degrees, self.period)
        if any(not math.isfinite(value) or value <= 0.0 for value in values):
            raise ValueError("tuning ratios must be finite and positive")
        if self.period <= 1.0:
            raise ValueError("tuning period must be greater than one")

    def ratio_at(self, degree: int) -> float:
        degree = int(degree)
        if degree < 0:
            raise ValueError("degree must be nonnegative")
        cycle, index = divmod(degree, len(self.degrees))
        return self.degrees[index] * self.period**cycle

    def mode_ratios(self, count: int, *, degree_offset: int = 0) -> tuple[float, ...]:
        if count < 1:
            raise ValueError("mode count must be positive")
        reference = self.ratio_at(degree_offset)
        return tuple(
            self.ratio_at(degree_offset + index) / reference
            for index in range(count)
        )


def _interval_ratio(token: str) -> float:
    if "/" in token:
        if token.count("/") != 1:
            raise ValueError(f"invalid Scala ratio {token!r}")
        value = float(Fraction(token))
    elif "." in token:
        value = 2.0 ** (float(token) / 1200.0)
    else:
        value = float(int(token))
    if not math.isfinite(value) or value <= 0.0:
        raise ValueError(f"invalid Scala interval {token!r}")
    return value


def parse_scl(text: str, *, name: str = "scala", path: Path | None = None) -> ScalaScale:
    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip() and not line.lstrip().startswith("!")
    ]
    if len(lines) < 2:
        raise ValueError("Scala file requires a description and note count")
    description = lines[0]
    try:
        count = int(lines[1].split()[0])
    except (IndexError, ValueError) as error:
        raise ValueError("invalid Scala note count") from error
    if count < 1:
        raise ValueError("QRM Scala tunings require at least one explicit interval")
    tokens = [line.split()[0] for line in lines[2 : 2 + count]]
    if len(tokens) != count:
        raise ValueError("Scala note count does not match interval data")
    ratios = tuple(_interval_ratio(token) for token in tokens)
    if ratios[-1] > 1.0:
        period = ratios[-1]
        degrees = (1.0, *ratios[:-1])
    else:
        # Scala permits non-periodic interval lists. QRM retains every entry
        # and uses 2/1 only when the 20-mode projection needs another cycle.
        period = 2.0
        degrees = (1.0, *ratios)
    return ScalaScale(name, description, degrees, period, path)


def load_scl(path: str | Path) -> ScalaScale:
    source = Path(path)
    return parse_scl(
        source.read_text(encoding="latin-1"),
        name=source.stem,
        path=source,
    )


def edo_scale(divisions: int) -> ScalaScale:
    divisions = int(divisions)
    if not 5 <= divisions <= 72:
        raise ValueError("n-EDO divisions must lie in [5, 72]")
    return ScalaScale(
        name=f"{divisions}-edo",
        description=f"{divisions} equal divisions of 2/1",
        degrees=tuple(2.0 ** (index / divisions) for index in range(divisions)),
        period=2.0,
    )


class TuningDictionary:
    """Filename-indexed, deterministic view of a local Scala archive."""

    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)
        self.paths = tuple(sorted(self.root.glob("*.scl"), key=lambda path: path.name))

    def select(self, family: str, *, query: str = "") -> tuple[Path, ...]:
        normalized = family.strip().lower()
        if normalized == "wilson":
            return tuple(path for path in self.paths if "wilson" in path.name.lower())
        if normalized == "tenney":
            return tuple(path for path in self.paths if "tenney" in path.name.lower())
        if normalized in {"la monte young", "lamonte young", "young"}:
            return tuple(
                path for path in self.paths if path.name.lower().startswith("young-lm_")
            )
        if normalized == "scala dictionary":
            needle = query.strip().lower()
            return tuple(
                path for path in self.paths if not needle or needle in path.name.lower()
            )
        raise ValueError("unknown tuning family")


__all__ = [
    "ScalaScale",
    "TuningDictionary",
    "edo_scale",
    "load_scl",
    "parse_scl",
]
