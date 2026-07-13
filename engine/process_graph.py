from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Literal
import json


NodeKind = Literal[
    "state", "unitary", "entangler", "measurement", "effect",
    "classical_control", "sonic", "analysis"
]


@dataclass(frozen=True)
class ProcessNode:
    """A typed operation in a compositional process graph."""
    node_id: str
    kind: NodeKind
    label: str
    qubits: tuple[int, ...] = ()
    params: Dict[str, Any] = field(default_factory=dict)
    depth: int = 0


@dataclass(frozen=True)
class ProcessEdge:
    """A directed relation between processes."""
    source: str
    target: str
    relation: Literal["sequential", "parallel", "classical", "sonic"] = "sequential"
    system: str = "quantum"


class QuantumProcessGraph:
    """
    A graph for describing process topology independently of Qiskit.

    It keeps two concerns separate:
      1. the quantum circuit/process graph;
      2. the sonic realization graph that interprets descriptors in Max.
    """

    def __init__(self, name: str = "untitled_process") -> None:
        self.name = name
        self.nodes: Dict[str, ProcessNode] = {}
        self.edges: List[ProcessEdge] = []

    def add_node(self, node: ProcessNode) -> ProcessNode:
        if node.node_id in self.nodes:
            raise ValueError(f"Node id already exists: {node.node_id}")
        self.nodes[node.node_id] = node
        return node

    def connect(
        self,
        source: str,
        target: str,
        relation: Literal["sequential", "parallel", "classical", "sonic"] = "sequential",
        system: str = "quantum",
    ) -> None:
        if source not in self.nodes:
            raise KeyError(f"Unknown source node: {source}")
        if target not in self.nodes:
            raise KeyError(f"Unknown target node: {target}")
        self.edges.append(ProcessEdge(source, target, relation, system))

    def successors(self, node_id: str) -> list[str]:
        return [edge.target for edge in self.edges if edge.source == node_id]

    def predecessors(self, node_id: str) -> list[str]:
        return [edge.source for edge in self.edges if edge.target == node_id]

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "nodes": [
                {
                    "id": n.node_id,
                    "kind": n.kind,
                    "label": n.label,
                    "qubits": list(n.qubits),
                    "params": n.params,
                    "depth": n.depth,
                }
                for n in self.nodes.values()
            ],
            "edges": [
                {
                    "source": e.source,
                    "target": e.target,
                    "relation": e.relation,
                    "system": e.system,
                }
                for e in self.edges
            ],
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)

    def validate(self) -> None:
        """Basic graph validation; cycles are allowed only in sonic relations."""
        for edge in self.edges:
            if edge.relation != "sonic" and edge.source == edge.target:
                raise ValueError("Self-loops are reserved for sonic feedback edges.")
