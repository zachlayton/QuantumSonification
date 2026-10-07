"""Capability-gated read-only bridges from a sealed :class:`QuantumFrame`.

These adapters preserve the density-matrix spine as the only authority.  They
do not promote a generic computational basis to configuration space, invent a
gauge connection, pad a two-qubit state into four qubits, or alter the source
frame.  Every unavailable target is returned as an explicit capability record
rather than an exception or a coerced representation.
"""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping, Sequence

import numpy as np

from qmw.flow.gauge_transport import GaugeFlowFrame, GaugeGraphConnection, gauge_flow_from_density_matrix
from qmw.qmw_emergent_geometry import (
    EmergentGeometryFrame,
    EntanglementGeometryConfig,
    observe_emergent_geometry,
)
from qmw.qmw_probability_flow import FlowFrame, flow_from_density_matrix_graph

from .dynamics import QuantumFrame, _readonly


_EPS = 1.0e-12


@dataclass(frozen=True)
class AdapterCapability:
    """Availability of one native downstream observer contract."""

    name: str
    available: bool
    reason: str


@dataclass(frozen=True)
class QuantumFrameAdapterConfig:
    """Explicit optional declarations needed by downstream observer targets.

    A gauge connection is an observer descriptor.  Leaving it ``None`` does
    not manufacture a zero-phase graph.  ``flow_regions`` label the existing
    computational-basis graph nodes and have no configuration-space meaning.
    """

    gauge_connection: GaugeGraphConnection | None = None
    gauge_cycles: Mapping[str, Sequence[int]] | None = None
    flow_regions: Sequence[int] | np.ndarray | None = None
    geometry_config: EntanglementGeometryConfig | None = None

    def __post_init__(self) -> None:
        if self.gauge_connection is not None and not isinstance(self.gauge_connection, GaugeGraphConnection):
            raise TypeError("gauge_connection must be GaugeGraphConnection or None.")
        if self.geometry_config is not None and not isinstance(self.geometry_config, EntanglementGeometryConfig):
            raise TypeError("geometry_config must be EntanglementGeometryConfig or None.")
        cycles = None if self.gauge_cycles is None else MappingProxyType({
            str(name): tuple(int(node) for node in nodes)
            for name, nodes in dict(self.gauge_cycles).items()
        })
        if cycles is not None and any(len(nodes) < 3 for nodes in cycles.values()):
            raise ValueError("gauge cycles must each contain at least three nodes.")
        regions = None
        if self.flow_regions is not None:
            raw = np.asarray(self.flow_regions, dtype=int)
            if raw.ndim != 1 or np.any(raw < 0):
                raise ValueError("flow_regions must be a one-dimensional nonnegative label array.")
            regions = _readonly(raw, dtype=int)
        object.__setattr__(self, "gauge_cycles", cycles)
        object.__setattr__(self, "flow_regions", regions)


@dataclass(frozen=True)
class QuantumFrameAdapterFrame:
    """Read-only collection of capability-gated observations of one frame."""

    frame_index: int
    time: float
    capabilities: Mapping[str, AdapterCapability]
    hilbert_flow: FlowFrame
    gauge_flow: GaugeFlowFrame | None
    relational_geometry: EmergentGeometryFrame | None
    dissipative_population_rate: np.ndarray
    provenance: str = "read_only_sealed_quantumframe_capability_adapters_v1"

    @property
    def supports_gauge(self) -> bool:
        return self.capabilities["gauge"].available

    @property
    def supports_relational_geometry(self) -> bool:
        return self.capabilities["relational_geometry_4q"].available


def _gauge_capability(frame: QuantumFrame, connection: GaugeGraphConnection | None) -> AdapterCapability:
    if connection is None:
        return AdapterCapability(
            "gauge", False,
            "requires an explicit GaugeGraphConnection; no connection was inferred from rho or H.",
        )
    if connection.node_count != frame.hamiltonian.dimension:
        return AdapterCapability(
            "gauge", False,
            "connection node count must match the QuantumFrame Hilbert dimension.",
        )
    allowed = np.eye(connection.node_count, dtype=bool)
    if connection.edge_indices.size:
        source, destination = connection.edge_indices.T
        allowed[source, destination] = True
        allowed[destination, source] = True
    if np.any(np.abs(frame.hamiltonian.matrix[~allowed]) > _EPS):
        return AdapterCapability(
            "gauge", False,
            "connection topology does not cover every nonzero Hamiltonian coupling.",
        )
    suffix = (
        " Gauge current is the unitary component; the sealed frame retains its separate dissipative rate."
        if frame.channels else ""
    )
    return AdapterCapability("gauge", True, "explicit connection topology matches H." + suffix)


def _geometry_capability(frame: QuantumFrame) -> AdapterCapability:
    if frame.hamiltonian.dimension != 16 or frame.hamiltonian.qubits != 4:
        return AdapterCapability(
            "relational_geometry_4q", False,
            "requires the native four-qubit 16x16 density-matrix contract; no padding or coercion is performed.",
        )
    return AdapterCapability(
        "relational_geometry_4q", True,
        "native four-qubit 16x16 density-matrix contract is present.",
    )


def observe_quantum_frame_adapters(
    frame: QuantumFrame,
    *,
    config: QuantumFrameAdapterConfig | None = None,
    previous: QuantumFrameAdapterFrame | None = None,
) -> QuantumFrameAdapterFrame:
    """Derive native flow/gauge/geometry views from one sealed frame.

    The base density-graph flow is always available for a valid
    ``QuantumFrame``.  Gauge and relational geometry are independently gated.
    ``previous`` is only used for existing observer continuity diagnostics; it
    never feeds state back into the authoritative engine.
    """

    if not isinstance(frame, QuantumFrame):
        raise TypeError("observe_quantum_frame_adapters requires a sealed QuantumFrame.")
    cfg = config or QuantumFrameAdapterConfig()
    if cfg.flow_regions is not None and cfg.flow_regions.shape != (frame.hamiltonian.dimension,):
        raise ValueError("flow_regions must have one label per Hilbert-basis node.")
    if previous is not None:
        if not isinstance(previous, QuantumFrameAdapterFrame):
            raise TypeError("previous must be QuantumFrameAdapterFrame or None.")
        if frame.time <= previous.time:
            raise ValueError("previous adapter frame must be strictly earlier.")

    prior_flow = None if previous is None else previous.hilbert_flow
    hilbert_flow = flow_from_density_matrix_graph(
        frame.rho, frame.hamiltonian.matrix, time=frame.time,
        hbar=frame.hamiltonian.hbar, regions=cfg.flow_regions, previous=prior_flow,
    )

    gauge_capability = _gauge_capability(frame, cfg.gauge_connection)
    prior_gauge = None if previous is None else previous.gauge_flow
    if prior_gauge is not None and cfg.gauge_connection is not None and not np.array_equal(
        prior_gauge.edge_indices, cfg.gauge_connection.edge_indices,
    ):
        # A changed observer topology starts a fresh gauge diagnostic series;
        # it does not invalidate the new sealed density frame.
        prior_gauge = None
    gauge_flow = None
    if gauge_capability.available:
        gauge_flow = gauge_flow_from_density_matrix(
            frame.rho, frame.hamiltonian.matrix, cfg.gauge_connection,
            time=frame.time, hbar=frame.hamiltonian.hbar,
            cycles=cfg.gauge_cycles, previous=prior_gauge, flow_frame=hilbert_flow,
        )

    geometry_capability = _geometry_capability(frame)
    relational_geometry = None
    if geometry_capability.available:
        relational_geometry = observe_emergent_geometry(
            frame.rho, revision=frame.frame_index, time=frame.time,
            config=cfg.geometry_config,
        )
    capabilities = MappingProxyType({
        "hilbert_flow": AdapterCapability("hilbert_flow", True, "native density-graph flow from sealed H and rho."),
        "gauge": gauge_capability,
        "relational_geometry_4q": geometry_capability,
    })
    return QuantumFrameAdapterFrame(
        frame_index=frame.frame_index, time=frame.time, capabilities=capabilities,
        hilbert_flow=hilbert_flow, gauge_flow=gauge_flow,
        relational_geometry=relational_geometry,
        dissipative_population_rate=_readonly(frame.population_rate_dissipative, dtype=float),
    )


__all__ = [
    "AdapterCapability", "QuantumFrameAdapterConfig", "QuantumFrameAdapterFrame",
    "observe_quantum_frame_adapters",
]
