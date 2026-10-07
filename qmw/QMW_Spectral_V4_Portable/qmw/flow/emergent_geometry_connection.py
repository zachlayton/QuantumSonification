"""Read-only adapter from QMW relational geometry to a graph gauge connection.

``EmergentGeometryFrame`` is the concrete provider for this first adapter.
Its modeled relational adjacency supplies graph topology and coupling strength.
It does not itself contain a U(1) connection, so link phases are explicit
adapter configuration and default to zero; entropy or mutual information is
never silently reinterpreted as a gauge phase.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import math
from types import MappingProxyType
from typing import Mapping

import numpy as np

from qmw.flow.gauge_transport import GaugeConnection
from qmw.flow.geometry_gauge_phase import ExplicitGeometryGaugePhaseConfig, apply_explicit_geometry_gauge_phase
from qmw.qmw_emergent_geometry import EmergentGeometryFrame


@dataclass(frozen=True)
class EmergentGeometryGaugeConfig:
    """Declared model choices for relational-geometry graph transport."""

    minimum_adjacency_weight: float = 1.0e-9
    coupling_scale: float = 1.0
    connection_phase_by_edge: Mapping[tuple[int, int], float] = field(default_factory=dict)
    geometry_phase_config: ExplicitGeometryGaugePhaseConfig | None = None

    def __post_init__(self) -> None:
        threshold = float(self.minimum_adjacency_weight)
        scale = float(self.coupling_scale)
        if not math.isfinite(threshold) or threshold < 0.0:
            raise ValueError("minimum_adjacency_weight must be finite and nonnegative.")
        if not math.isfinite(scale) or scale < 0.0:
            raise ValueError("coupling_scale must be finite and nonnegative.")
        phases: dict[tuple[int, int], float] = {}
        if self.geometry_phase_config is not None and not isinstance(self.geometry_phase_config, ExplicitGeometryGaugePhaseConfig):
            raise TypeError("geometry_phase_config must be ExplicitGeometryGaugePhaseConfig or None.")
        if self.geometry_phase_config is not None and self.connection_phase_by_edge:
            raise ValueError("use either geometry_phase_config or connection_phase_by_edge, not both.")
        for edge, value in dict(self.connection_phase_by_edge).items():
            if not isinstance(edge, tuple) or len(edge) != 2:
                raise ValueError("connection_phase_by_edge keys must be (source, destination) pairs.")
            source, destination = (int(edge[0]), int(edge[1]))
            if source == destination or not math.isfinite(float(value)):
                raise ValueError("connection phase entries need distinct nodes and finite values.")
            canonical = (min(source, destination), max(source, destination))
            oriented_value = float(value) if (source, destination) == canonical else -float(value)
            if canonical in phases and not math.isclose(phases[canonical], oriented_value, abs_tol=1.0e-12):
                raise ValueError("connection phase map supplies conflicting orientations for one edge.")
            phases[canonical] = oriented_value
        object.__setattr__(self, "minimum_adjacency_weight", threshold)
        object.__setattr__(self, "coupling_scale", scale)
        object.__setattr__(self, "connection_phase_by_edge", MappingProxyType(phases))


@dataclass(frozen=True)
class EmergentGeometryGaugeFrame:
    """A relational-geometry topology observation with explicit gauge metadata."""

    revision: int
    time: float
    connection: GaugeConnection
    cycles: Mapping[str, tuple[int, ...]]
    coupling_provenance: str = "emergent_geometry_adjacency_weight_scaled"
    connection_phase_provenance: str = "explicit_zero_unless_edge_override"
    provenance: str = "read_only_emergent_geometry_to_gauge_connection"


def _triangular_cycles(node_count: int, active_edges: set[tuple[int, int]]) -> Mapping[str, tuple[int, ...]]:
    cycles: dict[str, tuple[int, ...]] = {}
    for first in range(node_count):
        for second in range(first + 1, node_count):
            for third in range(second + 1, node_count):
                triangle = ((first, second), (first, third), (second, third))
                if all(edge in active_edges for edge in triangle):
                    cycle = (first, second, third)
                    cycles[f"triangle:{first}-{second}-{third}"] = cycle
    return MappingProxyType(cycles)


def emergent_geometry_to_gauge_connection(
    geometry: EmergentGeometryFrame,
    *,
    config: EmergentGeometryGaugeConfig | None = None,
) -> EmergentGeometryGaugeFrame:
    """Construct graph topology, coupling, and triangular loops from geometry.

    ``geometry.adjacency`` is a declared relational-geometry model output, not
    a Hamiltonian and not a gauge connection.  It determines where graph
    transport may be observed; configured phase values determine ``A``.
    """
    if not isinstance(geometry, EmergentGeometryFrame):
        raise TypeError("geometry must be an EmergentGeometryFrame.")
    cfg = config or EmergentGeometryGaugeConfig()
    adjacency = np.asarray(geometry.adjacency, dtype=float)
    if adjacency.ndim != 2 or adjacency.shape[0] != adjacency.shape[1] or adjacency.shape[0] < 2:
        raise ValueError("EmergentGeometryFrame adjacency must be a square graph of at least two nodes.")
    if not np.all(np.isfinite(adjacency)) or not np.allclose(adjacency, adjacency.T, rtol=0.0, atol=1.0e-12):
        raise ValueError("EmergentGeometryFrame adjacency must be finite and symmetric.")

    edges: list[tuple[int, int]] = []
    couplings: list[float] = []
    phases: list[float] = []
    node_count = adjacency.shape[0]
    for source in range(node_count):
        for destination in range(source + 1, node_count):
            weight = float(adjacency[source, destination])
            if weight < cfg.minimum_adjacency_weight:
                continue
            edge = (source, destination)
            if edge in cfg.connection_phase_by_edge:
                phase = cfg.connection_phase_by_edge[edge]
            else:
                phase = 0.0
            edges.append(edge)
            couplings.append(cfg.coupling_scale * weight)
            phases.append(float(phase))

    edge_array = np.asarray(edges, dtype=int).reshape((-1, 2)) if edges else np.empty((0, 2), dtype=int)
    phase_array = np.asarray(phases, dtype=float)
    coupling_array = np.asarray(couplings, dtype=float)
    connection = GaugeConnection(node_count, edge_array, phase_array, coupling_array)
    if cfg.geometry_phase_config is not None:
        connection = apply_explicit_geometry_gauge_phase(connection, cfg.geometry_phase_config)
    cycles = _triangular_cycles(node_count, set(edges))
    return EmergentGeometryGaugeFrame(
        revision=geometry.revision,
        time=geometry.time,
        connection=connection,
        cycles=cycles,
        connection_phase_provenance=(
            (f"explicit_geometry_phase_config:{cfg.geometry_phase_config.label}" if cfg.geometry_phase_config is not None
             else "explicit_edge_phase_override" if cfg.connection_phase_by_edge else "explicit_zero_unless_edge_override")
        ),
    )


__all__ = [
    "EmergentGeometryGaugeConfig",
    "EmergentGeometryGaugeFrame",
    "emergent_geometry_to_gauge_connection",
]
