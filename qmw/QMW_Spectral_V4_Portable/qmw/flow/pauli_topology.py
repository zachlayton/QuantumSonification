"""Explicit Pauli-string controls for read-only gauge-graph topology.

A Pauli string here is a declared *control label*, not an instruction to evolve
or measure a quantum state.  It selects a fully specified graph edit and
returns a new connection frame.  No density matrix, wavefunction, GPE engine,
or resonator is accepted or mutated by this module.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import math
from types import MappingProxyType
from typing import Mapping

import numpy as np

from .gauge_transport import GaugeConnection


Edge = tuple[int, int]


def _canonical_edge(edge: Edge, phase: float = 0.0) -> tuple[Edge, float]:
    source, destination = int(edge[0]), int(edge[1])
    if source == destination:
        raise ValueError("topology edges must join distinct nodes.")
    return ((source, destination), float(phase)) if source < destination else ((destination, source), -float(phase))


def _pauli_string(value: str) -> str:
    label = str(value).strip().upper()
    if not label or any(symbol not in "IXYZ" for symbol in label):
        raise ValueError("Pauli topology labels must be nonempty strings over I, X, Y, Z.")
    return label


@dataclass(frozen=True)
class PauliTopologyEdge:
    """Explicit attributes for an edge added by a selected Pauli control."""

    coupling: float = 1.0
    connection_phase: float = 0.0

    def __post_init__(self) -> None:
        if not math.isfinite(float(self.coupling)) or float(self.coupling) < 0.0:
            raise ValueError("added-edge coupling must be finite and nonnegative.")
        if not math.isfinite(float(self.connection_phase)):
            raise ValueError("added-edge connection_phase must be finite.")


@dataclass(frozen=True)
class PauliTopologyEdit:
    """A fully declared graph edit selected by one Pauli-string control."""

    remove_edges: tuple[Edge, ...] = ()
    add_edges: Mapping[Edge, PauliTopologyEdge] = field(default_factory=dict)
    phase_offset_by_oriented_edge: Mapping[Edge, float] = field(default_factory=dict)

    def __post_init__(self) -> None:
        remove = tuple(sorted({_canonical_edge(edge)[0] for edge in self.remove_edges}))
        added: dict[Edge, PauliTopologyEdge] = {}
        for raw_edge, specification in dict(self.add_edges).items():
            edge, sign = _canonical_edge(raw_edge, 1.0)
            if not isinstance(specification, PauliTopologyEdge):
                raise TypeError("add_edges values must be PauliTopologyEdge instances.")
            candidate = PauliTopologyEdge(specification.coupling, sign * specification.connection_phase)
            if edge in added and added[edge] != candidate:
                raise ValueError("one Pauli edit supplies conflicting added-edge attributes.")
            added[edge] = candidate
        offsets: dict[Edge, float] = {}
        for raw_edge, raw_offset in dict(self.phase_offset_by_oriented_edge).items():
            edge, oriented_offset = _canonical_edge(raw_edge, float(raw_offset))
            if not math.isfinite(oriented_offset):
                raise ValueError("phase offsets must be finite.")
            if edge in offsets and not math.isclose(offsets[edge], oriented_offset, abs_tol=1.0e-12):
                raise ValueError("one Pauli edit supplies conflicting phase-offset orientations.")
            offsets[edge] = oriented_offset
        if set(remove).intersection(added):
            raise ValueError("one Pauli edit cannot add and remove the same edge.")
        object.__setattr__(self, "remove_edges", remove)
        object.__setattr__(self, "add_edges", MappingProxyType(added))
        object.__setattr__(self, "phase_offset_by_oriented_edge", MappingProxyType(offsets))


@dataclass(frozen=True)
class PauliStringTopologyConfig:
    """A transparent lookup from Pauli control labels to graph edits."""

    edits_by_pauli_string: Mapping[str, PauliTopologyEdit]
    label: str = "explicit_pauli_string_topology_controls"

    def __post_init__(self) -> None:
        if not isinstance(self.label, str) or not self.label.strip():
            raise ValueError("label must be a nonempty string.")
        edits: dict[str, PauliTopologyEdit] = {}
        for raw_label, edit in dict(self.edits_by_pauli_string).items():
            label = _pauli_string(raw_label)
            if not isinstance(edit, PauliTopologyEdit):
                raise TypeError("edits_by_pauli_string values must be PauliTopologyEdit instances.")
            edits[label] = edit
        if not edits:
            raise ValueError("at least one Pauli-string topology edit is required.")
        object.__setattr__(self, "edits_by_pauli_string", MappingProxyType(edits))
        object.__setattr__(self, "label", self.label.strip())


@dataclass(frozen=True)
class PauliTopologyFrame:
    """Read-only record of one selected symbolic topology transformation."""

    pauli_string: str
    connection: GaugeConnection
    added_edges: tuple[Edge, ...]
    removed_edges: tuple[Edge, ...]
    phase_shifted_edges: tuple[Edge, ...]
    control_label: str
    provenance: str = "explicit_pauli_string_read_only_gauge_topology_transform"


def apply_pauli_string_topology(
    connection: GaugeConnection,
    pauli_string: str,
    config: PauliStringTopologyConfig,
) -> PauliTopologyFrame:
    """Return the explicitly edited topology selected by ``pauli_string``."""

    label = _pauli_string(pauli_string)
    try:
        edit = config.edits_by_pauli_string[label]
    except KeyError as error:
        raise KeyError(f"no topology edit is declared for Pauli string {label!r}.") from error
    records = {
        tuple(edge): [float(coupling), float(phase)]
        for edge, coupling, phase in zip(connection.edge_indices.tolist(), connection.coupling, connection.connection_phases)
    }
    absent_removals = set(edit.remove_edges).difference(records)
    if absent_removals:
        raise ValueError(f"Pauli topology edit removes absent edges: {sorted(absent_removals)!r}.")
    existing_additions = set(edit.add_edges).intersection(records)
    if existing_additions:
        raise ValueError(f"Pauli topology edit adds already-present edges: {sorted(existing_additions)!r}.")
    for edge in edit.remove_edges:
        del records[edge]
    for edge, specification in edit.add_edges.items():
        if edge[0] < 0 or edge[1] >= connection.node_count:
            raise ValueError(f"Pauli topology edge {edge!r} lies outside the connection node range.")
        records[edge] = [float(specification.coupling), float(specification.connection_phase)]
    absent_offsets = set(edit.phase_offset_by_oriented_edge).difference(records)
    if absent_offsets:
        raise ValueError(f"Pauli topology phase offset references absent edges: {sorted(absent_offsets)!r}.")
    for edge, offset in edit.phase_offset_by_oriented_edge.items():
        records[edge][1] += float(offset)
    edges = sorted(records)
    edge_array = np.asarray(edges, dtype=int).reshape((-1, 2)) if edges else np.empty((0, 2), dtype=int)
    coupling = np.asarray([records[edge][0] for edge in edges], dtype=float)
    phase = np.asarray([records[edge][1] for edge in edges], dtype=float)
    return PauliTopologyFrame(
        pauli_string=label,
        connection=GaugeConnection(connection.node_count, edge_array, phase, coupling),
        added_edges=tuple(sorted(edit.add_edges)),
        removed_edges=edit.remove_edges,
        phase_shifted_edges=tuple(sorted(edit.phase_offset_by_oriented_edge)),
        control_label=config.label,
    )


__all__ = [
    "PauliStringTopologyConfig", "PauliTopologyEdge", "PauliTopologyEdit", "PauliTopologyFrame",
    "apply_pauli_string_topology",
]
