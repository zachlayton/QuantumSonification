"""Semantics-checked local rewrites for the v1 ZX fragment."""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Callable

import numpy as np

from .model import Edge, ZXDiagram
from .semantics import linear_map


class SemanticMismatchError(ValueError):
    """Raised when a proposed rewrite changes the represented linear map."""


@dataclass(frozen=True)
class RewriteReport:
    rule: str
    before_name: str
    after_name: str
    absolute_error: float
    relative_error: float
    preserved: bool
    diagram: ZXDiagram


def _phase_is_zero(phase: float, atol: float) -> bool:
    return abs(math.remainder(float(phase), 2.0 * math.pi)) <= atol


def _checked_rewrite(
    diagram: ZXDiagram,
    rule: str,
    operation: Callable[[ZXDiagram], ZXDiagram],
    *,
    atol: float,
) -> RewriteReport:
    before = linear_map(diagram)
    rewritten = operation(diagram.copy(name=f"{diagram.name}__{rule}"))
    after = linear_map(rewritten)
    if before.shape != after.shape:
        raise SemanticMismatchError(
            f"{rule} changed map shape from {before.shape} to {after.shape}"
        )

    absolute = float(np.linalg.norm(after - before))
    scale = max(float(np.linalg.norm(before)), atol)
    relative = absolute / scale
    preserved = bool(np.allclose(before, after, atol=atol, rtol=atol))
    if not preserved:
        raise SemanticMismatchError(
            f"{rule} changed the ZX semantics "
            f"(absolute error={absolute:.3e}, relative error={relative:.3e})"
        )
    return RewriteReport(
        rule=rule,
        before_name=diagram.name,
        after_name=rewritten.name,
        absolute_error=absolute,
        relative_error=relative,
        preserved=True,
        diagram=rewritten,
    )


def fuse_spiders(
    diagram: ZXDiagram,
    first: str,
    second: str,
    *,
    atol: float = 1e-10,
) -> RewriteReport:
    """Fuse two same-color spiders joined by exactly one plain edge."""

    def operation(result: ZXDiagram) -> ZXDiagram:
        if first not in result.nodes or second not in result.nodes:
            raise KeyError("both spider ids must exist")
        first_node = result.nodes[first]
        second_node = result.nodes[second]
        if first_node.kind not in {"z", "x"} or first_node.kind != second_node.kind:
            raise ValueError("spider fusion requires two spiders of the same color")

        connecting = [
            edge
            for edge in result.incident_edges(first)
            if result.other_endpoint(edge, first) == second
        ]
        if len(connecting) != 1 or connecting[0].kind != "plain":
            raise ValueError(
                "spider fusion requires exactly one plain edge between the spiders"
            )

        connecting_id = connecting[0].edge_id
        result.replace_node(
            first,
            phase=math.remainder(
                float(first_node.phase) + float(second_node.phase),
                2.0 * math.pi,
            ),
            label=first_node.label or second_node.label,
        )
        del result.edges[connecting_id]

        for edge in list(result.incident_edges(second)):
            if edge.edge_id == connecting_id:
                continue
            source = first if edge.source == second else edge.source
            target = first if edge.target == second else edge.target
            result.edges[edge.edge_id] = Edge(
                edge.edge_id,
                source,
                target,
                edge.kind,
            )
        del result.nodes[second]
        return result

    return _checked_rewrite(
        diagram,
        f"fuse_{first}_{second}",
        operation,
        atol=atol,
    )


def remove_identity_spider(
    diagram: ZXDiagram,
    spider: str,
    *,
    atol: float = 1e-10,
) -> RewriteReport:
    """Remove a degree-two, zero-phase spider on two plain wires."""

    def operation(result: ZXDiagram) -> ZXDiagram:
        if spider not in result.nodes:
            raise KeyError(f"unknown spider: {spider}")
        node = result.nodes[spider]
        if node.kind not in {"z", "x"}:
            raise ValueError("identity removal requires a spider")
        if not _phase_is_zero(node.phase, atol):
            raise ValueError("identity removal requires zero phase modulo 2pi")
        incident = result.incident_edges(spider)
        if len(incident) != 2 or any(edge.kind != "plain" for edge in incident):
            raise ValueError("identity removal requires exactly two plain wires")

        left = result.other_endpoint(incident[0], spider)
        right = result.other_endpoint(incident[1], spider)
        if left == right:
            raise ValueError("identity removal would create a self-loop")
        for edge in incident:
            del result.edges[edge.edge_id]
        del result.nodes[spider]

        base = f"identity_{spider}"
        edge_id = base
        suffix = 1
        while edge_id in result.edges:
            edge_id = f"{base}_{suffix}"
            suffix += 1
        result.connect(edge_id, left, right)
        return result

    return _checked_rewrite(
        diagram,
        f"remove_identity_{spider}",
        operation,
        atol=atol,
    )
