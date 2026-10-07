"""Explicit geometry-owned U(1) phase declarations.

This module intentionally has no access to entropy, mutual information,
distance, adjacency weight, or a density matrix.  A geometry provider names
edges; a caller declares their connection phases.  Keeping those acts separate
prevents a visually or informationally salient geometry value from silently
becoming a physical gauge potential.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import math
from types import MappingProxyType
from typing import Mapping

import numpy as np

from .gauge_transport import GaugeConnection


@dataclass(frozen=True)
class ExplicitGeometryGaugePhaseConfig:
    """Named oriented-edge phase values supplied by a human or external model.

    Values are dimensionless connection integrals.  Reversed keys are accepted
    and canonically stored with the corresponding sign.  Unlisted edges retain
    the connection's existing value, normally the geometry adapter's explicit
    zero default.
    """

    phase_by_oriented_edge: Mapping[tuple[int, int], float] = field(default_factory=dict)
    label: str = "manual_geometry_gauge_phase"

    def __post_init__(self) -> None:
        if not isinstance(self.label, str) or not self.label.strip():
            raise ValueError("label must be a nonempty string.")
        phases: dict[tuple[int, int], float] = {}
        for edge, raw in dict(self.phase_by_oriented_edge).items():
            if not isinstance(edge, tuple) or len(edge) != 2:
                raise ValueError("phase_by_oriented_edge keys must be (source, destination) pairs.")
            source, destination = int(edge[0]), int(edge[1])
            value = float(raw)
            if source == destination or not math.isfinite(value):
                raise ValueError("geometry gauge phases need distinct nodes and finite values.")
            canonical = (min(source, destination), max(source, destination))
            oriented = value if (source, destination) == canonical else -value
            if canonical in phases and not math.isclose(phases[canonical], oriented, abs_tol=1.0e-12):
                raise ValueError("geometry gauge phase map supplies conflicting orientations for one edge.")
            phases[canonical] = oriented
        object.__setattr__(self, "phase_by_oriented_edge", MappingProxyType(phases))
        object.__setattr__(self, "label", self.label.strip())


def apply_explicit_geometry_gauge_phase(
    connection: GaugeConnection,
    config: ExplicitGeometryGaugePhaseConfig,
) -> GaugeConnection:
    """Return a replacement connection with only declared geometry phases set."""

    lookup = {tuple(edge): index for index, edge in enumerate(connection.edge_indices.tolist())}
    unknown = set(config.phase_by_oriented_edge).difference(lookup)
    if unknown:
        raise ValueError(f"geometry phase configuration references absent connection edges: {sorted(unknown)!r}.")
    phase = connection.connection_phases
    for edge, value in config.phase_by_oriented_edge.items():
        phase[lookup[edge]] = value
    return GaugeConnection(connection.node_count, connection.edge_indices, phase, connection.coupling)


__all__ = ["ExplicitGeometryGaugePhaseConfig", "apply_explicit_geometry_gauge_phase"]
