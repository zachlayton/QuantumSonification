"""Typed Feynman-inspired process graphs for QMW interaction adapters.

The graph records operational topology: declared external legs, typed internal
propagators, vertices, loop order, and an optional symbolic complex weight. It
is not a claim that QMW has evaluated a renormalised quantum-field-theory
amplitude. A concrete field-theory backend must supply any physical vertex,
propagator, integration, and symmetry-factor calculation it wants to claim.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Literal, Mapping, Sequence

import numpy as np


LegDirection = Literal["incoming", "outgoing"]
LineKind = Literal["fermion", "boson", "modal"]


def _identifier(name: str, value: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a nonempty string.")
    return value


@dataclass(frozen=True)
class ExternalLeg:
    """A declared external process port, never an inferred oscillator value."""

    identifier: str
    vertex: str
    direction: LegDirection
    species: str
    line_kind: LineKind = "modal"

    def __post_init__(self) -> None:
        _identifier("external-leg identifier", self.identifier)
        _identifier("external-leg vertex", self.vertex)
        _identifier("external-leg species", self.species)
        if self.direction not in ("incoming", "outgoing"):
            raise ValueError("external-leg direction must be incoming or outgoing.")
        if self.line_kind not in ("fermion", "boson", "modal"):
            raise ValueError("external-leg line_kind must be fermion, boson, or modal.")


@dataclass(frozen=True)
class ProcessVertex:
    """A typed interaction insertion with declared coupling order."""

    identifier: str
    coupling_label: str
    coupling_order: int = 1

    def __post_init__(self) -> None:
        _identifier("vertex identifier", self.identifier)
        _identifier("vertex coupling_label", self.coupling_label)
        if int(self.coupling_order) != self.coupling_order or self.coupling_order < 1:
            raise ValueError("vertex coupling_order must be a positive integer.")


@dataclass(frozen=True)
class InternalLine:
    """One internal propagator joining two declared vertices.

    ``start`` and ``end`` retain line orientation where the species requires
    it. The undirected edge is used only for graph topology and loop counting.
    """

    identifier: str
    start: str
    end: str
    species: str
    line_kind: LineKind = "modal"
    propagator_label: str | None = None

    def __post_init__(self) -> None:
        _identifier("internal-line identifier", self.identifier)
        _identifier("internal-line start", self.start)
        _identifier("internal-line end", self.end)
        _identifier("internal-line species", self.species)
        if self.line_kind not in ("fermion", "boson", "modal"):
            raise ValueError("internal-line line_kind must be fermion, boson, or modal.")
        if self.propagator_label is not None:
            _identifier("internal-line propagator_label", self.propagator_label)


@dataclass(frozen=True)
class ProcessGraph:
    """A connected interaction topology with coherent-amplitude metadata."""

    identifier: str
    vertices: tuple[ProcessVertex, ...]
    external_legs: tuple[ExternalLeg, ...]
    internal_lines: tuple[InternalLine, ...] = ()
    symmetry_factor: float = 1.0
    model_level: Literal["symbolic", "backend_evaluated"] = "symbolic"

    def __post_init__(self) -> None:
        _identifier("graph identifier", self.identifier)
        if not self.vertices:
            raise ValueError("a process graph needs at least one vertex.")
        if not math.isfinite(float(self.symmetry_factor)) or self.symmetry_factor <= 0.0:
            raise ValueError("symmetry_factor must be finite and positive.")
        if self.model_level not in ("symbolic", "backend_evaluated"):
            raise ValueError("model_level must be symbolic or backend_evaluated.")
        vertex_names = [vertex.identifier for vertex in self.vertices]
        if len(set(vertex_names)) != len(vertex_names):
            raise ValueError("process-graph vertex identifiers must be unique.")
        leg_names = [leg.identifier for leg in self.external_legs]
        if len(set(leg_names)) != len(leg_names):
            raise ValueError("process-graph external-leg identifiers must be unique.")
        line_names = [line.identifier for line in self.internal_lines]
        if len(set(line_names)) != len(line_names):
            raise ValueError("process-graph internal-line identifiers must be unique.")
        vertex_set = set(vertex_names)
        if any(leg.vertex not in vertex_set for leg in self.external_legs):
            raise ValueError("every external leg must attach to a declared vertex.")
        if any(line.start not in vertex_set or line.end not in vertex_set for line in self.internal_lines):
            raise ValueError("every internal line must join declared vertices.")
        if not self.external_legs:
            raise ValueError("a process graph needs declared external legs.")
        if self.connected_components != 1:
            raise ValueError("a process graph must be connected through its internal topology.")

    @property
    def connected_components(self) -> int:
        """Connected components of vertices under undirected internal lines."""

        pending = {vertex.identifier for vertex in self.vertices}
        neighbours = {vertex: set() for vertex in pending}
        for line in self.internal_lines:
            neighbours[line.start].add(line.end)
            neighbours[line.end].add(line.start)
        components = 0
        while pending:
            components += 1
            stack = [pending.pop()]
            while stack:
                vertex = stack.pop()
                linked = neighbours[vertex] & pending
                pending -= linked
                stack.extend(linked)
        return components

    @property
    def loop_order(self) -> int:
        """Topological loop number ``I - V + C`` (here ``C`` is one)."""

        return len(self.internal_lines) - len(self.vertices) + self.connected_components

    @property
    def coupling_order(self) -> int:
        return int(sum(vertex.coupling_order for vertex in self.vertices))

    @property
    def input_count(self) -> int:
        return sum(leg.direction == "incoming" for leg in self.external_legs)

    @property
    def output_count(self) -> int:
        return sum(leg.direction == "outgoing" for leg in self.external_legs)

    @property
    def external_signature(self) -> tuple[tuple[str, str, str], ...]:
        """Comparable external process signature, independent of vertex layout."""

        return tuple(sorted((leg.direction, leg.species, leg.line_kind) for leg in self.external_legs))

    def symbolic_weight(
        self,
        couplings: Mapping[str, complex],
        propagators: Mapping[str, complex] | None = None,
    ) -> complex:
        """Multiply supplied complex rules, retaining phase through the graph.

        This is bookkeeping for an explicitly provided model. It does not
        integrate momenta, calculate a Green function, or infer a symmetry
        factor; callers supply those values and choose ``backend_evaluated``
        only when such a backend actually exists.
        """

        amplitude = complex(1.0 / self.symmetry_factor)
        for vertex in self.vertices:
            if vertex.coupling_label not in couplings:
                raise ValueError(f"missing coupling for vertex rule {vertex.coupling_label!r}.")
            coupling = complex(couplings[vertex.coupling_label])
            if not np.isfinite(coupling):
                raise ValueError("couplings must be finite complex values.")
            amplitude *= coupling
        propagators = {} if propagators is None else propagators
        for line in self.internal_lines:
            label = line.propagator_label or line.identifier
            if label not in propagators:
                raise ValueError(f"missing propagator for internal line {label!r}.")
            propagator = complex(propagators[label])
            if not np.isfinite(propagator):
                raise ValueError("propagators must be finite complex values.")
            amplitude *= propagator
        return amplitude


@dataclass(frozen=True)
class GraphContribution:
    """One graph's complex contribution to a declared external process."""

    graph: ProcessGraph
    amplitude: complex


class GraphAmplitudeAccumulator:
    """Coherently sum only graphs with the same declared external signature."""

    def __init__(self, signature: Sequence[tuple[str, str, str]]) -> None:
        self.signature = tuple(sorted(tuple(item) for item in signature))
        self._contributions: list[GraphContribution] = []

    def add(self, contribution: GraphContribution) -> None:
        if contribution.graph.external_signature != self.signature:
            raise ValueError("only graphs with the same external process may interfere.")
        amplitude = complex(contribution.amplitude)
        if not np.isfinite(amplitude):
            raise ValueError("graph amplitude must be finite.")
        self._contributions.append(GraphContribution(contribution.graph, amplitude))

    @property
    def contributions(self) -> tuple[GraphContribution, ...]:
        return tuple(self._contributions)

    @property
    def amplitude(self) -> complex:
        return sum((item.amplitude for item in self._contributions), 0.0j)

    @property
    def intensity(self) -> float:
        return float(abs(self.amplitude) ** 2)


def tree_graph(
    identifier: str,
    *,
    inputs: int,
    outputs: int,
    coupling_label: str,
    species: str = "modal_excitation",
) -> ProcessGraph:
    """Create an explicitly modal tree-level graph for existing QMW vertices."""

    if int(inputs) != inputs or int(outputs) != outputs or inputs < 1 or outputs < 1:
        raise ValueError("tree_graph inputs and outputs must be positive integers.")
    vertex = ProcessVertex("v0", coupling_label)
    legs = tuple(
        [ExternalLeg(f"in{index}", "v0", "incoming", species) for index in range(int(inputs))]
        + [ExternalLeg(f"out{index}", "v0", "outgoing", species) for index in range(int(outputs))]
    )
    return ProcessGraph(identifier, (vertex,), legs)


def exchange_graph(
    identifier: str,
    *,
    inputs: int,
    outputs: int,
    coupling_label: str,
    loop_order: int = 0,
) -> ProcessGraph:
    """Declare a two-vertex mediator-exchange topology for a QMW process.

    The fermion/boson names here choose a *diagram vocabulary* only.  They do
    not promote QMW modal excitations to literal QED particles.  A positive
    ``loop_order`` adds a declared virtual self-propagator at the left vertex,
    allowing a renderer to show a loop correction distinctly from a tree
    exchange while retaining the graph's exact topological loop number.
    """

    if int(inputs) != inputs or int(outputs) != outputs or inputs < 1 or outputs < 1:
        raise ValueError("exchange_graph inputs and outputs must be positive integers.")
    if int(loop_order) != loop_order or loop_order < 0:
        raise ValueError("loop_order must be a nonnegative integer.")
    vertices = (
        ProcessVertex("v_left", coupling_label),
        ProcessVertex("v_right", coupling_label),
    )
    legs = tuple(
        [ExternalLeg(f"in{index}", "v_left", "incoming", "modal_in", "fermion") for index in range(int(inputs))]
        + [ExternalLeg(f"out{index}", "v_right", "outgoing", "modal_out", "fermion") for index in range(int(outputs))]
    )
    internal = [
        InternalLine("mediator", "v_left", "v_right", "modal_mediator", "boson", "D_modal"),
    ]
    for index in range(int(loop_order)):
        internal.append(
            InternalLine(
                f"virtual_loop_{index}", "v_left", "v_left",
                "virtual_modal", "fermion", f"S_virtual_{index}",
            )
        )
    return ProcessGraph(identifier, vertices, legs, tuple(internal))


__all__ = [
    "ExternalLeg", "GraphAmplitudeAccumulator", "GraphContribution", "InternalLine", "ProcessGraph",
    "ProcessVertex", "exchange_graph", "tree_graph",
]
