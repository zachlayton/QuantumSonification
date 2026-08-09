"""OSC mirror and semantic verifier for Processing ZX rewrite gestures."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
import math
from threading import Thread
import time
from typing import Iterable

import numpy as np

from .model import ZXDiagram
from .rewrite import fuse_spiders


@dataclass
class VisualNode:
    node_id: int
    kind: str
    x: float
    y: float
    phase: float
    boundary_role: str = ""
    boundary_index: int = -1


@dataclass(frozen=True)
class VisualEdge:
    source: int
    target: int
    kind: str = "plain"
    edge_id: int = 0

    def canonical(self) -> "VisualEdge":
        if self.source <= self.target:
            return self
        return VisualEdge(
            self.target,
            self.source,
            self.kind,
            self.edge_id,
        )


@dataclass(frozen=True)
class FusionVerification:
    keep_id: int
    removed_id: int
    verified: bool
    absolute_error: float
    fused_phase: float
    message: str


@dataclass(frozen=True)
class VisualRewriteVerification:
    rule_id: str
    verified: bool
    absolute_error: float
    message: str
    scalar: complex


class VisualGraphMirror:
    """Mirror the Processing graph closely enough to verify local rewrites."""

    def __init__(self) -> None:
        self.nodes: dict[int, VisualNode] = {}
        self.edges: list[VisualEdge] = []
        self.scalar: complex = 1.0 + 0.0j
        self._next_edge_id = 1

    def clear(self) -> None:
        self.nodes.clear()
        self.edges = []
        self.scalar = 1.0 + 0.0j
        self._next_edge_id = 1

    def add_node(
        self,
        node_id: int,
        kind: str,
        x: float,
        y: float,
        phase: float,
        boundary_role: str = "",
        boundary_index: int = -1,
    ) -> None:
        normalized_kind = str(kind).upper()
        if normalized_kind not in {"Z", "X", "H", "HB", "B", "D"}:
            raise ValueError(f"unsupported visual node kind: {kind}")
        role = str(boundary_role).strip().lower()
        index = int(boundary_index)
        if normalized_kind == "D":
            role = "discard"
            index = max(index, 0)
        elif normalized_kind == "B":
            if role not in {"", "input", "output"}:
                raise ValueError(f"unsupported boundary role: {boundary_role}")
            if role and index < 0:
                raise ValueError("tagged boundaries need a non-negative index")
        else:
            role = ""
            index = -1
        self.nodes[int(node_id)] = VisualNode(
            int(node_id),
            normalized_kind,
            float(x),
            float(y),
            float(phase),
            role,
            index,
        )

    def delete_node(self, node_id: int) -> None:
        node_id = int(node_id)
        self.nodes.pop(node_id, None)
        self.edges = [
            edge
            for edge in self.edges
            if edge.source != node_id and edge.target != node_id
        ]

    def set_position(self, node_id: int, x: float, y: float) -> None:
        node = self.nodes[int(node_id)]
        node.x = float(x)
        node.y = float(y)

    def set_phase(self, node_id: int, kind: str, phase: float) -> None:
        node = self.nodes[int(node_id)]
        if node.kind != str(kind).upper():
            raise ValueError("phase update kind does not match mirrored node")
        node.phase = float(phase)

    def add_edge(
        self,
        source: int,
        target: int,
        kind: str = "plain",
        edge_id: int | None = None,
    ) -> None:
        source = int(source)
        target = int(target)
        normalized_kind = str(kind).lower()
        if source == target:
            raise ValueError("visual self-loops are not supported")
        if source not in self.nodes or target not in self.nodes:
            raise KeyError("both visual edge endpoints must exist")
        if normalized_kind not in {"plain", "hadamard"}:
            raise ValueError("visual edge kind must be plain or hadamard")
        if edge_id is None:
            edge_id = self._next_edge_id
        edge_id = int(edge_id)
        self._next_edge_id = max(self._next_edge_id, edge_id + 1)
        self.edges.append(
            VisualEdge(
                source,
                target,
                normalized_kind,
                edge_id,
            ).canonical()
        )

    def one_qubit_chain_matrix(
        self,
        node_ids: Iterable[int],
    ):
        """Return the exact 2x2 tensor of a selected degree-two ZX chain."""
        import numpy as np

        identifiers = [int(value) for value in node_ids]
        if not identifiers:
            raise ValueError("select at least one one-wire Z, X, or H node")
        if len(set(identifiers)) != len(identifiers):
            raise ValueError("Euler selection contains duplicate nodes")
        try:
            selected = [self.nodes[node_id] for node_id in identifiers]
        except KeyError as exc:
            raise ValueError(f"Euler selection contains unknown node {exc}") from exc
        if any(node.kind not in {"Z", "X", "H"} for node in selected):
            raise ValueError("Euler selection supports only Z, X, and H nodes")

        incident: dict[int, list[VisualEdge]] = {
            node.node_id: [] for node in selected
        }
        for edge in self.edges:
            if edge.source in incident:
                incident[edge.source].append(edge)
            if edge.target in incident:
                incident[edge.target].append(edge)
        if any(len(incident[node.node_id]) != 2 for node in selected):
            raise ValueError(
                "every selected Euler node must have degree two on one wire"
            )
        if any(
            edge.kind != "plain"
            for edges in incident.values()
            for edge in edges
        ):
            raise ValueError(
                "select explicit H nodes rather than Hadamard-edge boundaries"
            )

        ordered = sorted(selected, key=lambda node: (node.x, node.node_id))
        for left, right in zip(ordered, ordered[1:]):
            if not any(
                {edge.source, edge.target}
                == {left.node_id, right.node_id}
                for edge in self.edges
            ):
                raise ValueError(
                    "selected Euler nodes must form one contiguous wire segment"
                )

        hadamard = (
            np.array([[1, 1], [1, -1]], dtype=np.complex128)
            / math.sqrt(2.0)
        )
        matrix = np.eye(2, dtype=np.complex128)
        for node in ordered:
            if node.kind == "H":
                gate = hadamard
            else:
                phase_gate = np.diag(
                    [1.0, np.exp(1j * node.phase)]
                ).astype(np.complex128)
                gate = (
                    phase_gate
                    if node.kind == "Z"
                    else hadamard @ phase_gate @ hadamard
                )
            matrix = gate @ matrix
        return matrix

    def verify_and_apply_fusion(
        self,
        keep_id: int,
        removed_id: int,
        kind: str,
        reported_phase: float,
        *,
        atol: float = 1e-10,
    ) -> FusionVerification:
        keep_id = int(keep_id)
        removed_id = int(removed_id)
        normalized_kind = str(kind).upper()
        reported_phase = float(reported_phase)

        try:
            keep = self.nodes[keep_id]
            removed = self.nodes[removed_id]
            if normalized_kind not in {"Z", "X"}:
                raise ValueError("fusion requires Z or X spiders")
            if keep.kind != normalized_kind or removed.kind != normalized_kind:
                raise ValueError("fusion requires two spiders of the same color")

            connecting_edges = [
                edge
                for edge in self.edges
                if {edge.source, edge.target} == {keep_id, removed_id}
                and edge.kind == "plain"
            ]
            if len(connecting_edges) != 1:
                raise ValueError(
                    "fusion requires exactly one plain edge between spiders"
                )
            connecting = connecting_edges[0]

            diagram = ZXDiagram(
                f"processing_local_fusion_{keep_id}_{removed_id}"
            )
            diagram.add_spider(str(keep_id), normalized_kind.lower(), keep.phase)
            diagram.add_spider(
                str(removed_id),
                normalized_kind.lower(),
                removed.phase,
            )
            diagram.connect(
                "fusion_edge",
                str(keep_id),
                str(removed_id),
            )

            external_edges = sorted(
                (
                    edge
                    for edge in self.edges
                    if edge != connecting
                    and (
                        keep_id in {edge.source, edge.target}
                        or removed_id in {edge.source, edge.target}
                    )
                ),
                key=lambda edge: (edge.source, edge.target),
            )
            for index, edge in enumerate(external_edges):
                owner = (
                    keep_id
                    if keep_id in {edge.source, edge.target}
                    else removed_id
                )
                boundary_id = f"external_{index}"
                diagram.add_boundary(boundary_id, "output", index)
                diagram.connect(
                    f"external_edge_{index}",
                    str(owner),
                    boundary_id,
                )

            report = fuse_spiders(
                diagram,
                str(keep_id),
                str(removed_id),
                atol=atol,
            )
            expected_phase = report.diagram.nodes[str(keep_id)].phase
            phase_error = abs(
                math.remainder(reported_phase - expected_phase, 2.0 * math.pi)
            )
            if phase_error > atol:
                raise ValueError(
                    "Processing reported a fused phase that does not equal "
                    "the sum of the two spider phases"
                )

            self._apply_fusion(keep_id, removed_id, expected_phase)
            return FusionVerification(
                keep_id=keep_id,
                removed_id=removed_id,
                verified=True,
                absolute_error=report.absolute_error,
                fused_phase=expected_phase,
                message="spider fusion preserved the local ZX linear map",
            )
        except (KeyError, ValueError) as exc:
            return FusionVerification(
                keep_id=keep_id,
                removed_id=removed_id,
                verified=False,
                absolute_error=math.inf,
                fused_phase=reported_phase,
                message=str(exc),
            )

    def _apply_fusion(
        self,
        keep_id: int,
        removed_id: int,
        fused_phase: float,
    ) -> None:
        keep = self.nodes[keep_id]
        removed = self.nodes[removed_id]
        keep.x = 0.5 * (keep.x + removed.x)
        keep.y = 0.5 * (keep.y + removed.y)
        keep.phase = float(fused_phase)

        rewritten: list[VisualEdge] = []
        seen: set[tuple[int, int, str]] = set()
        for edge in self.edges:
            if {edge.source, edge.target} == {keep_id, removed_id}:
                continue
            source = keep_id if edge.source == removed_id else edge.source
            target = keep_id if edge.target == removed_id else edge.target
            if source != target:
                candidate = VisualEdge(
                    source,
                    target,
                    edge.kind,
                    edge.edge_id,
                ).canonical()
                key = (candidate.source, candidate.target, candidate.kind)
                if key in seen:
                    continue
                seen.add(key)
                rewritten.append(
                    candidate
                )
        self.edges = rewritten
        del self.nodes[removed_id]

    def apply_selected_rule(
        self,
        rule_id: str,
        selected_ids: Iterable[int],
        *,
        atol: float = 1e-9,
    ) -> VisualRewriteVerification:
        """Apply a named PyZX/ZXH rewrite and commit only after tensor QA."""
        normalized_rule = str(rule_id).strip().lower()
        selected = tuple(dict.fromkeys(int(item) for item in selected_ids))
        old_nodes = dict(self.nodes)

        try:
            if not selected:
                raise ValueError("select the rule pattern before applying it")
            missing = [item for item in selected if item not in self.nodes]
            if missing:
                raise KeyError(f"unknown selected node ids: {missing}")

            before = self._to_pyzx()
            # Build twice instead of using BaseGraph.copy(), which renumbers
            # explicit visual vertex IDs on PyZX's multigraph backend.
            after = self._to_pyzx()
            applied = self._apply_pyzx_rule(
                after,
                normalized_rule,
                selected,
            )
            if not applied:
                raise ValueError(
                    f"selection does not match the {normalized_rule} rule"
                )

            from pyzx.tensor import compare_tensors, tensorfy
            import numpy as np

            if not compare_tensors(
                before,
                after,
                preserve_scalar=True,
            ):
                raise ValueError(
                    f"{normalized_rule} failed exact scalar-aware tensor QA"
                )
            before_tensor = tensorfy(before, preserve_scalar=True)
            after_tensor = tensorfy(after, preserve_scalar=True)
            absolute_error = float(
                np.linalg.norm(after_tensor - before_tensor)
            )
            if absolute_error > atol * max(
                1.0,
                float(np.linalg.norm(before_tensor)),
            ):
                raise ValueError(
                    f"{normalized_rule} tensor error exceeded tolerance"
                )

            self._replace_from_pyzx(after, old_nodes=old_nodes)
            return VisualRewriteVerification(
                rule_id=normalized_rule,
                verified=True,
                absolute_error=absolute_error,
                message=(
                    f"{normalized_rule.replace('_', ' ')} preserved the "
                    "complete ZX tensor and scalar"
                ),
                scalar=self.scalar,
            )
        except (ImportError, KeyError, TypeError, ValueError) as exc:
            return VisualRewriteVerification(
                rule_id=normalized_rule,
                verified=False,
                absolute_error=math.inf,
                message=str(exc),
                scalar=self.scalar,
            )

    def _to_pyzx(self):
        import pyzx
        from pyzx.utils import EdgeType, VertexType

        graph = pyzx.Graph("multigraph")
        graph.set_auto_simplify(False)
        boundary_nodes: list[VisualNode] = []
        for node in sorted(self.nodes.values(), key=lambda item: item.node_id):
            if node.kind in {"B", "D"}:
                vertex_type = VertexType.BOUNDARY
                phase = Fraction(0)
                boundary_nodes.append(node)
            elif node.kind == "Z":
                vertex_type = VertexType.Z
                phase = Fraction(node.phase / math.pi).limit_denominator(
                    1_000_000
                )
            elif node.kind == "X":
                vertex_type = VertexType.X
                phase = Fraction(node.phase / math.pi).limit_denominator(
                    1_000_000
                )
            elif node.kind in {"H", "HB"}:
                vertex_type = VertexType.H_BOX
                phase = Fraction(1)
            else:
                raise ValueError(f"unsupported visual kind: {node.kind}")
            graph.add_vertex(
                vertex_type,
                qubit=float(node.y),
                row=float(node.x),
                phase=phase,
                index=node.node_id,
            )

        for edge in self.edges:
            edge_type = (
                EdgeType.HADAMARD
                if edge.kind == "hadamard"
                else EdgeType.SIMPLE
            )
            graph.add_edge(
                (edge.source, edge.target),
                edgetype=edge_type,
            )

        roles_are_complete = bool(boundary_nodes) and all(
            node.boundary_role in {"input", "output"}
            and node.boundary_index >= 0
            for node in boundary_nodes
        )
        input_nodes = [
            node for node in boundary_nodes if node.boundary_role == "input"
        ]
        output_nodes = [
            node for node in boundary_nodes if node.boundary_role == "output"
        ]
        roles_are_unique = (
            len({node.boundary_index for node in input_nodes})
            == len(input_nodes)
            and len({node.boundary_index for node in output_nodes})
            == len(output_nodes)
        )
        if roles_are_complete and roles_are_unique:
            # PyZX's first tensor axis is the most-significant basis bit.
            # Descending q labels therefore produce QMW's q0-LSB ordering.
            graph.set_inputs(
                tuple(
                    node.node_id
                    for node in sorted(
                        input_nodes,
                        key=lambda item: item.boundary_index,
                        reverse=True,
                    )
                )
            )
            graph.set_outputs(
                tuple(
                    node.node_id
                    for node in sorted(
                        output_nodes,
                        key=lambda item: item.boundary_index,
                        reverse=True,
                    )
                )
            )
        else:
            graph.set_inputs(())
            graph.set_outputs(
                tuple(sorted(node.node_id for node in boundary_nodes))
            )
        graph.scalar.add_float(self.scalar)
        return graph

    def _replace_from_pyzx(
        self,
        graph,
        *,
        old_nodes: dict[int, VisualNode],
    ) -> None:
        from pyzx.utils import EdgeType, VertexType

        new_nodes: dict[int, VisualNode] = {}
        for vertex in graph.vertices():
            vertex_id = int(vertex)
            vertex_type = graph.type(vertex)
            if vertex_type == VertexType.BOUNDARY:
                previous = old_nodes.get(vertex_id)
                kind = (
                    "D"
                    if previous is not None and previous.kind == "D"
                    else "B"
                )
                phase = 0.0
            elif vertex_type == VertexType.Z:
                kind = "Z"
                phase = float(graph.phase(vertex)) * math.pi
            elif vertex_type == VertexType.X:
                kind = "X"
                phase = float(graph.phase(vertex)) * math.pi
            elif vertex_type == VertexType.H_BOX:
                previous = old_nodes.get(vertex_id)
                kind = (
                    "H"
                    if previous is not None and previous.kind == "H"
                    else "HB"
                )
                phase = math.pi
            else:
                raise ValueError(
                    f"PyZX produced unsupported vertex type {vertex_type}"
                )
            previous = old_nodes.get(vertex_id)
            new_nodes[vertex_id] = VisualNode(
                vertex_id,
                kind,
                float(graph.row(vertex)),
                float(graph.qubit(vertex)),
                phase,
                (
                    previous.boundary_role
                    if previous is not None and kind in {"B", "D"}
                    else ""
                ),
                (
                    previous.boundary_index
                    if previous is not None and kind in {"B", "D"}
                    else -1
                ),
            )

        new_edges: list[VisualEdge] = []
        for edge_id, edge in enumerate(graph.edges(), start=1):
            source, target = graph.edge_st(edge)
            kind = (
                "hadamard"
                if graph.edge_type(edge) == EdgeType.HADAMARD
                else "plain"
            )
            new_edges.append(
                VisualEdge(
                    int(source),
                    int(target),
                    kind,
                    edge_id,
                ).canonical()
            )

        self.nodes = new_nodes
        self.edges = new_edges
        self._next_edge_id = len(new_edges) + 1
        self.scalar = complex(graph.scalar.to_number())

    @staticmethod
    def _apply_pyzx_rule(graph, rule_id: str, selected: tuple[int, ...]) -> bool:
        from pyzx.rewrite_rules.bialgebra_rule import bialgebra
        from pyzx.rewrite_rules.color_change_rule import color_change
        from pyzx.rewrite_rules.copy_rule import copy as state_copy
        from pyzx.rewrite_rules.hopf_rule import hopf
        from pyzx.rewrite_rules.lcomp_rule import lcomp
        from pyzx.rewrite_rules.pivot_rule import pivot
        from pyzx.rewrite_rules.push_pauli_rule import pauli_push
        from pyzx.rewrite_rules.remove_id_rule import remove_id
        from pyzx.utils import VertexType, vertex_is_zx

        if rule_id == "identity_removal":
            return len(selected) == 1 and remove_id(graph, selected[0])

        if rule_id == "pi_copy":
            if len(selected) != 2:
                return False
            for spider, pauli in (
                (selected[0], selected[1]),
                (selected[1], selected[0]),
            ):
                if pauli_push(graph, spider, pauli):
                    return True
            return False

        if rule_id == "state_copy":
            if len(selected) not in {1, 2}:
                return False
            candidates = [
                vertex
                for vertex in selected
                if graph.vertex_degree(vertex) == 1
            ]
            return any(state_copy(graph, vertex) for vertex in candidates)

        if rule_id == "bialgebra":
            return (
                len(selected) == 2
                and bialgebra(graph, selected[0], selected[1])
            )

        if rule_id == "hopf":
            return (
                len(selected) == 2
                and hopf(graph, selected[0], selected[1])
            )

        if rule_id == "color_change":
            return len(selected) == 1 and color_change(graph, selected[0])

        if rule_id == "local_complementation":
            return len(selected) == 1 and lcomp(graph, selected[0])

        if rule_id == "pivot":
            return (
                len(selected) == 2
                and pivot(graph, selected[0], selected[1])
            )

        if rule_id == "absorb":
            if len(selected) != 2:
                return False
            h_box = next(
                (
                    vertex
                    for vertex in selected
                    if graph.type(vertex) == VertexType.H_BOX
                ),
                None,
            )
            x_state = next(
                (
                    vertex
                    for vertex in selected
                    if graph.type(vertex) == VertexType.X
                    and graph.vertex_degree(vertex) == 1
                    and math.isclose(
                        math.remainder(float(graph.phase(vertex)), 2.0),
                        1.0,
                        abs_tol=1e-10,
                    )
                ),
                None,
            )
            if (
                h_box is None
                or x_state is None
                or not graph.connected(h_box, x_state)
            ):
                return False
            graph.remove_vertex(x_state)
            graph.scalar.add_power(1)
            return True

        return False


class RewriteOSCVerifier:
    """Run a small OSC server and acknowledge Processing rewrite requests."""

    def __init__(
        self,
        *,
        listen_host: str = "127.0.0.1",
        listen_port: int = 7499,
        processing_host: str = "127.0.0.1",
        processing_port: int = 7497,
        max_density_host: str = "127.0.0.1",
        max_density_port: int = 7498,
        tomography_host: str = "127.0.0.1",
        tomography_port: int = 7426,
        engine_host: str = "127.0.0.1",
        engine_port: int = 7402,
    ) -> None:
        try:
            from pythonosc.dispatcher import Dispatcher
            from pythonosc.osc_server import BlockingOSCUDPServer
            from pythonosc.udp_client import SimpleUDPClient
        except ImportError as exc:
            raise ModuleNotFoundError(
                "python-osc is required for Processing rewrite verification"
            ) from exc

        self.graph = VisualGraphMirror()
        self.client = SimpleUDPClient(processing_host, int(processing_port))
        self.max_density_client = SimpleUDPClient(
            max_density_host,
            int(max_density_port),
        )
        self.max_density_host = str(max_density_host)
        self.max_density_port = int(max_density_port)
        self.tomography_client = SimpleUDPClient(
            tomography_host,
            int(tomography_port),
        )
        self.engine_client = SimpleUDPClient(engine_host, int(engine_port))
        self.engine_host = str(engine_host)
        self.engine_port = int(engine_port)
        self.density_frame = None
        self._density_revision = int(time.time())
        self.active_pauli_label = ""
        self.active_pauli_theta = 0.0
        self.active_pauli_central_node = -1
        self.active_pauli_verified = False
        self.pauli_score = []
        self.pauli_score_verified = False
        dispatcher = Dispatcher()
        dispatcher.map("/qmw/zx/graph/begin", self._on_graph_begin)
        dispatcher.map("/qmw/zx/graph/end", self._on_graph_end)
        dispatcher.map("/qmw/zx/node/add", self._on_node_add)
        dispatcher.map("/qmw/zx/node/delete", self._on_node_delete)
        dispatcher.map("/qmw/zx/node/position", self._on_node_position)
        dispatcher.map("/qmw/zx/node/phase", self._on_node_phase)
        dispatcher.map("/qmw/zx/graph/scalar", self._on_graph_scalar)
        dispatcher.map("/qmw/zx/edge/add", self._on_edge_add)
        dispatcher.map("/qmw/zx/rewrite/fuse", self._on_fusion)
        dispatcher.map("/qmw/zx/rewrite/apply", self._on_apply_rule)
        dispatcher.map("/qmw/zx/density/request", self._on_density_request)
        dispatcher.map("/qmw/zx/density/commit", self._on_density_commit)
        dispatcher.map("/qmw/zx/pauli/gadget", self._on_pauli_gadget)
        dispatcher.map("/qmw/zx/pauli/score", self._on_pauli_score)
        dispatcher.map("/qmw/zx/pauli/active", self._on_pauli_active)
        dispatcher.map("/qmw/zx/pauli/select", self._on_pauli_select)
        dispatcher.map("/qmw/zx/euler/request", self._on_euler_request)
        self.server = BlockingOSCUDPServer(
            (str(listen_host), int(listen_port)),
            dispatcher,
        )
        self.thread: Thread | None = None

    def start(self) -> None:
        if self.thread is not None:
            return
        self.thread = Thread(
            target=self.server.serve_forever,
            name="qmw-zx-rewrite-verifier",
            daemon=True,
        )
        self.thread.start()
        self.client.send_message("/qmw/zx/graph/request", 1)

    def stop(self) -> None:
        if self.thread is None:
            return
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2.0)
        self.thread = None

    def _on_graph_begin(
        self,
        _address: str,
        _revision: int = 0,
        scalar_real: float = 1.0,
        scalar_imag: float = 0.0,
    ) -> None:
        self.graph.clear()
        self.graph.scalar = complex(float(scalar_real), float(scalar_imag))

    def _on_graph_end(self, _address: str, revision: int = 0) -> None:
        self.client.send_message(
            "/qmw/zx/graph/synchronized",
            [int(revision), len(self.graph.nodes), len(self.graph.edges)],
        )

    def _on_node_add(
        self,
        _address: str,
        node_id: int,
        kind: str,
        x: float,
        y: float,
        phase: float,
        boundary_role: str = "",
        boundary_index: int = -1,
    ) -> None:
        self.graph.add_node(
            node_id,
            kind,
            x,
            y,
            phase,
            boundary_role,
            boundary_index,
        )

    def _on_node_delete(self, _address: str, node_id: int) -> None:
        self.graph.delete_node(node_id)

    def _on_node_position(
        self,
        _address: str,
        node_id: int,
        x: float,
        y: float,
    ) -> None:
        self.graph.set_position(node_id, x, y)

    def _on_node_phase(
        self,
        _address: str,
        node_id: int,
        kind: str,
        phase: float,
    ) -> None:
        self.graph.set_phase(node_id, kind, phase)

    def _on_graph_scalar(
        self,
        _address: str,
        scalar_real: float,
        scalar_imag: float,
    ) -> None:
        self.graph.scalar = complex(float(scalar_real), float(scalar_imag))

    def _on_edge_add(
        self,
        _address: str,
        source: int,
        target: int,
        kind: str,
    ) -> None:
        try:
            self.graph.add_edge(source, target, kind)
        except (KeyError, TypeError, ValueError) as exc:
            self.client.send_message(
                "/qmw/zx/graph/error",
                [str(exc), int(source), int(target)],
            )

    def _on_fusion(
        self,
        _address: str,
        keep_id: int,
        removed_id: int,
        kind: str,
        reported_phase: float,
    ) -> None:
        result = self.graph.verify_and_apply_fusion(
            keep_id,
            removed_id,
            kind,
            reported_phase,
        )
        self.client.send_message(
            "/qmw/zx/rewrite/result",
            [
                result.keep_id,
                result.removed_id,
                int(result.verified),
                float(result.absolute_error),
                float(result.fused_phase),
                result.message,
            ],
        )

    def _on_apply_rule(
        self,
        _address: str,
        rule_id: str,
        selected_count: int,
        *selected_ids: int,
    ) -> None:
        selected = tuple(
            int(item)
            for item in selected_ids[: max(0, int(selected_count))]
        )
        result = self.graph.apply_selected_rule(rule_id, selected)
        if result.verified:
            self._send_rewritten_graph(result)
        self.client.send_message(
            "/qmw/zx/rewrite/result_v2",
            [
                result.rule_id,
                int(result.verified),
                (
                    float(result.absolute_error)
                    if math.isfinite(result.absolute_error)
                    else 1.0e30
                ),
                result.message,
                len(self.graph.nodes),
                len(self.graph.edges),
                float(result.scalar.real),
                float(result.scalar.imag),
            ],
        )

    def _send_rewritten_graph(
        self,
        result: VisualRewriteVerification,
    ) -> None:
        self.client.send_message(
            "/qmw/zx/rewrite/graph/begin",
            [
                result.rule_id,
                float(result.scalar.real),
                float(result.scalar.imag),
            ],
        )
        for node in sorted(
            self.graph.nodes.values(),
            key=lambda item: item.node_id,
        ):
            self.client.send_message(
                "/qmw/zx/rewrite/graph/node",
                [
                    node.node_id,
                    node.kind,
                    node.x,
                    node.y,
                    node.phase,
                    node.boundary_role,
                    node.boundary_index,
                ],
            )
        for edge in self.graph.edges:
            self.client.send_message(
                "/qmw/zx/rewrite/graph/edge",
                [
                    edge.source,
                    edge.target,
                    edge.kind,
                ],
            )
        self.client.send_message(
            "/qmw/zx/rewrite/graph/end",
            [result.rule_id, result.message],
        )

    def _on_density_request(self, _address: str, *_args: object) -> None:
        from .density_bridge import density_frame_from_visual_graph

        self._density_revision += 1
        try:
            frame = density_frame_from_visual_graph(
                self.graph,
                self._density_revision,
            )
            self.density_frame = frame
            self._send_density_frame(frame)
        except (ImportError, KeyError, TypeError, ValueError) as exc:
            self._send_density_message(
                "/qmw/zx/density/error",
                str(exc),
            )

    def _density_targets(self) -> tuple[object, ...]:
        targets = [self.client]
        max_client = getattr(self, "max_density_client", None)
        if max_client is not None and max_client is not self.client:
            targets.append(max_client)
        return tuple(targets)

    def _send_density_message(self, address: str, payload: object) -> None:
        for target in self._density_targets():
            target.send_message(address, payload)

    def _send_pauli_message(self, address: str, payload: object) -> None:
        targets = list(self._density_targets())
        tomography_client = getattr(self, "tomography_client", None)
        if tomography_client is not None and tomography_client not in targets:
            targets.append(tomography_client)
        for target in targets:
            target.send_message(address, payload)

    def _send_euler_message(self, address: str, payload: object) -> None:
        self._send_pauli_message(address, payload)

    def _on_euler_request(
        self,
        _address: str,
        request_id: int,
        node_count: int,
        *node_ids: int,
    ) -> None:
        from qmw.euler import decompose_one_qubit

        request = int(request_id)
        count = int(node_count)
        try:
            if count < 1 or len(node_ids) < count:
                raise ValueError("incomplete Euler selection transaction")
            selected = [int(node_ids[index]) for index in range(count)]
            result = decompose_one_qubit(
                self.graph.one_qubit_chain_matrix(selected),
                basis="ZXZ",
            )
            self._send_euler_message(
                "/qmw/zx/euler/result",
                [
                    request,
                    "ZX selection",
                    -1,
                    result.basis,
                    result.theta,
                    result.phi,
                    result.lam,
                    result.gamma,
                    result.zx_scalar_phase,
                    int(result.verified),
                    result.absolute_error,
                ],
            )
        except (
            ImportError,
            KeyError,
            TypeError,
            ValueError,
        ) as exc:
            self._send_euler_message(
                "/qmw/zx/euler/error",
                [request, str(exc)],
            )

    def _send_density_frame(self, frame) -> None:
        dimension = int(frame.rho.shape[0])
        self._send_density_message(
            "/qmw/zx/density/begin",
            [
                frame.revision,
                frame.mode,
                dimension,
                frame.success_probability,
            ],
        )
        self._send_density_message(
            "/qmw/zx/density/meta",
            [
                frame.revision,
                frame.trace,
                frame.purity,
                frame.coherence_l1,
                frame.entropy,
                frame.minimum_eigenvalue,
                frame.success_probability,
            ],
        )
        self._send_density_message(
            "/qmw/zx/density/probabilities",
            [frame.revision, *frame.probabilities],
        )
        for row in range(dimension):
            self._send_density_message(
                "/qmw/zx/density/row",
                [
                    frame.revision,
                    row,
                    *frame.rho.real[row].astype(float).tolist(),
                    *frame.rho.imag[row].astype(float).tolist(),
                ],
            )
        for qubit in range(frame.qubit_count):
            self._send_density_message(
                "/qmw/zx/density/bloch",
                [
                    frame.revision,
                    qubit,
                    *frame.local_bloch[qubit],
                    frame.local_purity[qubit],
                    frame.local_entropy[qubit],
                ],
            )
        if dimension == 16:
            self._send_active_pauli(frame)
        self._send_density_message(
            "/qmw/zx/density/end",
            [frame.revision, frame.message],
        )

    def _on_pauli_gadget(
        self,
        _address: str,
        label: str,
        theta: float,
        central_node_id: int = -1,
    ) -> None:
        from .pauli_gadget import (
            PauliGadgetVerification,
            normalize_pauli_label,
            pauli_weight,
            verify_visual_pauli_gadget,
        )

        try:
            result = verify_visual_pauli_gadget(self.graph, label, theta)
        except (TypeError, ValueError) as exc:
            normalized = str(label).strip().upper()
            result = PauliGadgetVerification(
                normalized,
                float(theta),
                (
                    pauli_weight(normalize_pauli_label(normalized))
                    if len(normalized) == 4
                    and all(axis in "IXYZ" for axis in normalized)
                    and normalized != "IIII"
                    else 0
                ),
                False,
                math.inf,
                str(exc),
            )
        self.active_pauli_label = result.label if result.weight > 0 else ""
        self.active_pauli_theta = result.theta
        self.active_pauli_central_node = int(central_node_id)
        self.active_pauli_verified = result.verified
        error = (
            result.absolute_error
            if math.isfinite(result.absolute_error)
            else 1.0e30
        )
        self._send_pauli_message(
            "/qmw/zx/pauli/verified",
            [
                result.label,
                result.weight,
                result.theta,
                int(result.verified),
                error,
                result.message,
            ],
        )
        frame = self.density_frame
        if frame is not None and self.active_pauli_label:
            self._send_active_pauli(frame)

    def _on_pauli_select(self, _address: str, label: str) -> None:
        from .pauli_gadget import normalize_pauli_label

        try:
            normalized = normalize_pauli_label(label)
        except ValueError as exc:
            self._send_pauli_message("/qmw/zx/pauli/error", str(exc))
            return
        self.active_pauli_label = normalized
        self.client.send_message("/qmw/zx/pauli/select", normalized)
        frame = self.density_frame
        if frame is not None:
            self._send_active_pauli(frame)

    def _on_pauli_score(
        self,
        _address: str,
        gadget_count: int,
        *items: object,
    ) -> None:
        from .pauli_gadget import (
            PauliGadgetSpec,
            verify_visual_pauli_score,
        )

        count = max(0, int(gadget_count))
        try:
            if len(items) < count * 3:
                raise ValueError("incomplete Pauli score OSC transaction")
            gadgets = [
                PauliGadgetSpec(
                    int(items[index * 3]),
                    str(items[index * 3 + 1]),
                    float(items[index * 3 + 2]),
                )
                for index in range(count)
            ]
            result = verify_visual_pauli_score(self.graph, gadgets)
        except (TypeError, ValueError) as exc:
            from .pauli_gadget import PauliScoreVerification

            gadgets = []
            result = PauliScoreVerification(
                count,
                False,
                math.inf,
                str(exc),
            )
        self.pauli_score = gadgets
        self.pauli_score_verified = result.verified
        self.active_pauli_verified = result.verified
        error = (
            result.absolute_error
            if math.isfinite(result.absolute_error)
            else 1.0e30
        )
        self._send_pauli_message(
            "/qmw/zx/pauli/score_verified",
            [
                result.gadget_count,
                int(result.verified),
                error,
                result.message,
            ],
        )

    def _on_pauli_active(
        self,
        _address: str,
        gadget_id: int,
        label: str,
        theta: float,
        central_node_id: int = -1,
    ) -> None:
        from .pauli_gadget import normalize_pauli_label

        try:
            normalized = normalize_pauli_label(label)
        except ValueError as exc:
            self._send_pauli_message("/qmw/zx/pauli/error", str(exc))
            return
        self.active_pauli_label = normalized
        self.active_pauli_theta = float(theta)
        self.active_pauli_central_node = int(central_node_id)
        self.active_pauli_verified = bool(
            getattr(self, "pauli_score_verified", False)
        )
        self._send_pauli_message(
            "/qmw/zx/pauli/active",
            [
                int(gadget_id),
                normalized,
                float(theta),
                int(self.active_pauli_verified),
            ],
        )
        frame = self.density_frame
        if frame is not None:
            self._send_active_pauli(frame)

    def _send_active_pauli(self, frame) -> None:
        from .pauli_gadget import pauli_expectation, pauli_weight

        label = getattr(self, "active_pauli_label", "")
        if not label:
            return
        expectation = pauli_expectation(frame.rho, label)
        self._send_pauli_message(
            "/qmw/zx/pauli/live",
            [
                frame.revision,
                label,
                pauli_weight(label),
                expectation,
                float(getattr(self, "active_pauli_theta", 0.0)),
                int(getattr(self, "active_pauli_verified", False)),
            ],
        )

    def _on_density_commit(
        self,
        _address: str,
        revision: int,
    ) -> None:
        frame = self.density_frame
        if frame is None or frame.revision != int(revision):
            self._send_density_message(
                "/qmw/zx/density/error",
                f"no current density preview for revision {revision}",
            )
            return
        if frame.qubit_count > 4:
            self._send_density_message(
                "/qmw/zx/density/error",
                (
                    f"{frame.qubit_count}-qubit preview cannot be committed "
                    "to the existing four-qubit resonator; Max retains the "
                    "complete preview"
                ),
            )
            return
        engine_rho = np.zeros((16, 16), dtype=np.complex128)
        dimension = int(frame.rho.shape[0])
        engine_rho[:dimension, :dimension] = frame.rho
        self.engine_client.send_message(
            "/qmw/state/begin",
            [frame.revision, 4, "q0_lsb"],
        )
        self.engine_client.send_message(
            "/qmw/state/rho/real",
            [
                frame.revision,
                *engine_rho.real.reshape(-1).astype(float).tolist(),
            ],
        )
        self.engine_client.send_message(
            "/qmw/state/rho/imag",
            [
                frame.revision,
                *engine_rho.imag.reshape(-1).astype(float).tolist(),
            ],
        )
        self.engine_client.send_message(
            "/qmw/state/commit",
            frame.revision,
        )
        self._send_density_message(
            "/qmw/zx/density/commit_sent",
            [
                frame.revision,
                self.engine_host,
                self.engine_port,
                getattr(self, "max_density_host", "127.0.0.1"),
                getattr(self, "max_density_port", 7498),
            ],
        )
