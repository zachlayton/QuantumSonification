"""Typed event observations from spatial or Hilbert current."""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Iterable

from qmw.quantum.hilbert_current import CurrentEdge


@dataclass(frozen=True)
class CurrentEvent:
    source: int
    destination: int
    magnitude: float
    phase: float | None
    domain: str
    provenance: str

    def __post_init__(self) -> None:
        if self.source < 0 or self.destination < 0 or self.source == self.destination:
            raise ValueError("current event endpoints must be distinct and nonnegative.")
        if not math.isfinite(self.magnitude) or self.magnitude < 0.0:
            raise ValueError("current event magnitude must be finite and nonnegative.")


def events_from_hilbert_edges(edges: Iterable[CurrentEdge]) -> tuple[CurrentEvent, ...]:
    return tuple(CurrentEvent(
        edge.source, edge.destination, edge.magnitude, None, "hilbert_graph",
        "computational_basis_probability_current",
    ) for edge in edges)


def events_from_boundary_fluxes(boundaries: Iterable[object]) -> tuple[CurrentEvent, ...]:
    result: list[CurrentEvent] = []
    for boundary in boundaries:
        result.append(CurrentEvent(
            int(boundary.source_region), int(boundary.destination_region),
            float(boundary.magnitude), float(boundary.phase), "spatial_region",
            "spatial_probability_boundary_flux",
        ))
    return tuple(result)


__all__ = ["CurrentEvent", "events_from_boundary_fluxes", "events_from_hilbert_edges"]
