"""PennyLane/PyZX import path for the ZX modular prototype."""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Any, Callable

import numpy as np

from .compiler import ModularPatchPlan, compile_modular_plan
from .model import ZXDiagram
from .semantics import linear_map


@dataclass(frozen=True)
class PyZXImportReport:
    diagram: ZXDiagram
    input_wire_to_boundary: dict[int, int]
    output_wire_to_boundary: dict[int, int]
    absolute_error: float
    relative_error: float
    verified: bool


@dataclass(frozen=True)
class PennyLaneModularResult:
    pyzx_graph: Any
    import_report: PyZXImportReport
    patch_plan: ModularPatchPlan
    vertices_before_simplification: int
    vertices_after_simplification: int


def _source_wire_map(graph: Any, vertices: tuple[Any, ...]) -> dict[int, int]:
    """Map source wire numbers to QMW's q0-LSB boundary numbers.

    PennyLane/PyZX matrices flatten their declared wire order with the first
    wire as the most-significant axis. QMW uses boundary zero as the
    least-significant bit. Reversing positions preserves the represented
    matrix while retaining labels that name each source wire.
    """
    count = len(vertices)
    result: dict[int, int] = {}
    for position, vertex in enumerate(vertices):
        source_wire = int(graph.qubit(vertex))
        result[source_wire] = count - 1 - position
    return result


def import_pyzx_graph(
    graph: Any,
    *,
    name: str = "pennylane_zx_graph",
    verify: bool = True,
    atol: float = 1e-9,
) -> PyZXImportReport:
    """Convert a PyZX graph into the local exact ZX representation."""
    try:
        from pyzx.utils import EdgeType, VertexType
    except ImportError as exc:
        raise ModuleNotFoundError(
            "PyZX is required; install qmw-zx-modular[pennylane]"
        ) from exc

    inputs = tuple(graph.inputs())
    outputs = tuple(graph.outputs())
    input_map = _source_wire_map(graph, inputs)
    output_map = _source_wire_map(graph, outputs)

    scalar_object = getattr(graph, "scalar", None)
    scalar = (
        complex(scalar_object.to_number())
        if scalar_object is not None and hasattr(scalar_object, "to_number")
        else 1.0 + 0.0j
    )
    diagram = ZXDiagram(name, scalar=scalar)
    vertex_to_node: dict[Any, str] = {}
    input_positions = {vertex: position for position, vertex in enumerate(inputs)}
    output_positions = {vertex: position for position, vertex in enumerate(outputs)}

    for vertex in graph.vertices():
        vertex_type = graph.type(vertex)
        source_wire = int(graph.qubit(vertex))
        if vertex_type == VertexType.BOUNDARY:
            if vertex in input_positions:
                boundary_index = len(inputs) - 1 - input_positions[vertex]
                node_id = f"input_wire_{source_wire}"
                diagram.add_boundary(
                    node_id,
                    "input",
                    boundary_index,
                    label=f"PennyLane input wire {source_wire}",
                )
            elif vertex in output_positions:
                boundary_index = len(outputs) - 1 - output_positions[vertex]
                node_id = f"output_wire_{source_wire}"
                diagram.add_boundary(
                    node_id,
                    "output",
                    boundary_index,
                    label=f"PennyLane output wire {source_wire}",
                )
            else:
                raise ValueError(
                    f"PyZX boundary vertex {vertex!r} is neither input nor output"
                )
        elif vertex_type in {VertexType.Z, VertexType.X}:
            color = "z" if vertex_type == VertexType.Z else "x"
            node_id = f"{color}_v{vertex}"
            try:
                phase_radians = float(graph.phase(vertex)) * math.pi
            except (TypeError, ValueError) as exc:
                raise ValueError(
                    f"symbolic PyZX phase on vertex {vertex!r} must be bound first"
                ) from exc
            diagram.add_spider(
                node_id,
                color,
                phase_radians,
                label=f"{color.upper()} spider · source wire {source_wire}",
            )
        else:
            raise ValueError(
                f"unsupported PyZX vertex type {vertex_type!r} on vertex {vertex!r}; "
                "the v1 bridge supports boundaries and Z/X spiders"
            )
        vertex_to_node[vertex] = node_id

    for index, edge in enumerate(graph.edges()):
        source, target = graph.edge_st(edge)
        edge_type = graph.edge_type(edge)
        if edge_type == EdgeType.SIMPLE:
            kind = "plain"
        elif edge_type == EdgeType.HADAMARD:
            kind = "hadamard"
        else:
            raise ValueError(f"unsupported PyZX edge type: {edge_type!r}")
        diagram.connect(
            f"edge_{index:04d}",
            vertex_to_node[source],
            vertex_to_node[target],
            kind=kind,
        )

    diagram.validate()
    source_matrix = np.asarray(
        graph.to_matrix(preserve_scalar=True),
        dtype=np.complex128,
    )
    imported_matrix = linear_map(diagram)
    if source_matrix.shape != imported_matrix.shape:
        raise ValueError(
            f"matrix shape mismatch: PyZX {source_matrix.shape}, "
            f"local {imported_matrix.shape}"
        )
    absolute = float(np.linalg.norm(imported_matrix - source_matrix))
    relative = absolute / max(float(np.linalg.norm(source_matrix)), atol)
    verified = bool(
        np.allclose(imported_matrix, source_matrix, atol=atol, rtol=atol)
    )
    if verify and not verified:
        raise ValueError(
            "PyZX import changed semantics "
            f"(absolute error={absolute:.3e}, relative error={relative:.3e})"
        )
    return PyZXImportReport(
        diagram=diagram,
        input_wire_to_boundary=input_map,
        output_wire_to_boundary=output_map,
        absolute_error=absolute,
        relative_error=relative,
        verified=verified,
    )


def pennylane_to_modular(
    quantum_function: Callable[..., Any],
    *args: Any,
    name: str = "pennylane_zx_patch",
    simplify: bool = False,
    **kwargs: Any,
) -> PennyLaneModularResult:
    """Convert a bound PennyLane quantum function to a modular patch plan."""
    try:
        import pennylane as qml
        import pyzx
    except ImportError as exc:
        raise ModuleNotFoundError(
            "PennyLane and PyZX are required; "
            "install qmw-zx-modular[pennylane]"
        ) from exc

    graph = qml.transforms.to_zx(quantum_function)(*args, **kwargs)
    before = int(graph.num_vertices())
    if simplify:
        pyzx.simplify.full_reduce(graph)
        graph.normalize()
    after = int(graph.num_vertices())
    report = import_pyzx_graph(graph, name=name)
    return PennyLaneModularResult(
        pyzx_graph=graph,
        import_report=report,
        patch_plan=compile_modular_plan(report.diagram),
        vertices_before_simplification=before,
        vertices_after_simplification=after,
    )
