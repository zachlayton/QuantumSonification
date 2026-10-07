from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping


def _frozen_map(value: Mapping[str, Any] | None) -> Mapping[str, Any]:
    return MappingProxyType(dict(value or {}))


@dataclass(frozen=True)
class QuantumMaterialFrame:
    """Backend-neutral quantum data delivered to QMW's sonic/spatial layer."""

    time: float
    expectations: Mapping[str, float] = field(default_factory=dict)
    samples: Mapping[str, int] = field(default_factory=dict)
    variances: Mapping[str, float] = field(default_factory=dict)
    correlations: Mapping[str, float] = field(default_factory=dict)
    backend: Mapping[str, Any] = field(default_factory=dict)
    error_metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.time < 0:
            raise ValueError("time must be non-negative")
        for name in (
            "expectations", "samples", "variances", "correlations",
            "backend", "error_metadata",
        ):
            object.__setattr__(self, name, _frozen_map(getattr(self, name)))

    def as_dict(self) -> dict[str, Any]:
        return {
            "time": self.time,
            "expectations": dict(self.expectations),
            "samples": dict(self.samples),
            "variances": dict(self.variances),
            "correlations": dict(self.correlations),
            "backend": dict(self.backend),
            "error_metadata": dict(self.error_metadata),
        }
