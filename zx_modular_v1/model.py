"""Typed, dependency-light data model for open ZX diagrams."""

from __future__ import annotations

from dataclasses import dataclass, replace
import json
import math
from typing import Any, Literal


NodeKind = Literal["boundary", "z", "x"]
BoundaryRole = Literal["input", "output"]
EdgeKind = Literal["plain", "hadamard"]


@dataclass(frozen=True)
class Node:
    node_id: str
    kind: NodeKind
    phase: float = 0.0
    boundary_role: BoundaryRole | None = None
    boundary_index: int | None = None
    label: str | None = None

    def __post_init__(self) -> None:
        if not self.node_id:
            raise ValueError("node_id cannot be empty")
        if self.kind == "boundary":
            if self.boundary_role not in {"input", "output"}:
                raise ValueError("boundary nodes require input or output role")
            if self.boundary_index is None or int(self.boundary_index) < 0:
                raise ValueError("boundary nodes require a non-negative index")
            if abs(float(self.phase)) > 1e-15:
                raise ValueError("boundary nodes cannot carry a phase")
        else:
            if self.boundary_role is not None or self.boundary_index is not None:
                raise ValueError("only boundary nodes can carry boundary metadata")
            if not math.isfinite(float(self.phase)):
                raise ValueError("spider phase must be finite")


@dataclass(frozen=True)
class Edge:
    edge_id: str
    source: str
    target: str
    kind: EdgeKind = "plain"

    def __post_init__(self) -> None:
        if not self.edge_id:
            raise ValueError("edge_id cannot be empty")
        if not self.source or not self.target:
            raise ValueError("edge endpoints cannot be empty")
        if self.source == self.target:
            raise ValueError("self-loops are outside the v1 prototype")


class ZXDiagram:
    """An open, undirected ZX multigraph with explicit wire boundaries."""

    def __init__(
        self,
        name: str = "untitled_zx_diagram",
        *,
        scalar: complex = 1.0 + 0.0j,
    ) -> None:
        self.name = str(name)
        self.scalar = complex(scalar)
        self.nodes: dict[str, Node] = {}
        self.edges: dict[str, Edge] = {}

    def copy(self, *, name: str | None = None) -> "ZXDiagram":
        result = ZXDiagram(
            self.name if name is None else name,
            scalar=self.scalar,
        )
        result.nodes = dict(self.nodes)
        result.edges = dict(self.edges)
        return result

    def add_boundary(
        self,
        node_id: str,
        role: BoundaryRole,
        index: int,
        *,
        label: str | None = None,
    ) -> Node:
        return self.add_node(
            Node(
                node_id=node_id,
                kind="boundary",
                boundary_role=role,
                boundary_index=int(index),
                label=label,
            )
        )

    def add_spider(
        self,
        node_id: str,
        color: Literal["z", "x"],
        phase: float = 0.0,
        *,
        label: str | None = None,
    ) -> Node:
        return self.add_node(
            Node(
                node_id=node_id,
                kind=color,
                phase=float(phase),
                label=label,
            )
        )

    def add_node(self, node: Node) -> Node:
        if node.node_id in self.nodes:
            raise ValueError(f"duplicate node id: {node.node_id}")
        self.nodes[node.node_id] = node
        return node

    def connect(
        self,
        edge_id: str,
        source: str,
        target: str,
        *,
        kind: EdgeKind = "plain",
    ) -> Edge:
        if edge_id in self.edges:
            raise ValueError(f"duplicate edge id: {edge_id}")
        if source not in self.nodes or target not in self.nodes:
            raise KeyError(f"unknown edge endpoint: {source!r}, {target!r}")
        edge = Edge(edge_id, source, target, kind)
        self.edges[edge_id] = edge
        return edge

    def incident_edges(self, node_id: str) -> list[Edge]:
        if node_id not in self.nodes:
            raise KeyError(f"unknown node: {node_id}")
        return sorted(
            (
                edge
                for edge in self.edges.values()
                if edge.source == node_id or edge.target == node_id
            ),
            key=lambda edge: edge.edge_id,
        )

    def other_endpoint(self, edge: Edge, node_id: str) -> str:
        if edge.source == node_id:
            return edge.target
        if edge.target == node_id:
            return edge.source
        raise ValueError(f"edge {edge.edge_id!r} is not incident to {node_id!r}")

    def boundaries(self, role: BoundaryRole) -> list[Node]:
        return sorted(
            (
                node
                for node in self.nodes.values()
                if node.kind == "boundary" and node.boundary_role == role
            ),
            key=lambda node: (int(node.boundary_index or 0), node.node_id),
        )

    def replace_node(self, node_id: str, **changes: Any) -> Node:
        if node_id not in self.nodes:
            raise KeyError(f"unknown node: {node_id}")
        updated = replace(self.nodes[node_id], **changes)
        self.nodes[node_id] = updated
        return updated

    def validate(self) -> None:
        if not (
            math.isfinite(float(self.scalar.real))
            and math.isfinite(float(self.scalar.imag))
        ):
            raise ValueError("diagram scalar must be finite")
        for edge in self.edges.values():
            if edge.source not in self.nodes or edge.target not in self.nodes:
                raise ValueError(f"edge {edge.edge_id!r} has an unknown endpoint")

        for role in ("input", "output"):
            indices = [
                int(node.boundary_index)
                for node in self.boundaries(role)
                if node.boundary_index is not None
            ]
            if len(indices) != len(set(indices)):
                raise ValueError(f"{role} boundary indices must be unique")
            if indices and indices != list(range(len(indices))):
                raise ValueError(
                    f"{role} boundary indices must be contiguous from zero"
                )

        for node in self.nodes.values():
            degree = len(self.incident_edges(node.node_id))
            if node.kind == "boundary" and degree != 1:
                raise ValueError(
                    f"boundary {node.node_id!r} must have degree one, received {degree}"
                )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": "qmw.zx-diagram.v1",
            "name": self.name,
            "scalar": {
                "real": float(self.scalar.real),
                "imag": float(self.scalar.imag),
            },
            "nodes": [
                {
                    "id": node.node_id,
                    "kind": node.kind,
                    "phase": node.phase,
                    "boundary_role": node.boundary_role,
                    "boundary_index": node.boundary_index,
                    "label": node.label,
                }
                for node in sorted(self.nodes.values(), key=lambda item: item.node_id)
            ],
            "edges": [
                {
                    "id": edge.edge_id,
                    "source": edge.source,
                    "target": edge.target,
                    "kind": edge.kind,
                }
                for edge in sorted(self.edges.values(), key=lambda item: item.edge_id)
            ],
        }

    def to_json(self, *, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, sort_keys=True)
