"""Exact tensor-network semantics for the supported ZX fragment."""

from __future__ import annotations

from itertools import product
import math

import numpy as np

from .model import Node, ZXDiagram


COMPLEX = np.complex128
IDENTITY = np.eye(2, dtype=COMPLEX)
HADAMARD = np.array([[1.0, 1.0], [1.0, -1.0]], dtype=COMPLEX) / math.sqrt(2.0)


def spider_tensor(node: Node, degree: int) -> np.ndarray:
    """Return the standard unnormalized Z/X spider tensor."""
    if node.kind not in {"z", "x"}:
        raise ValueError("only spider nodes have tensors")
    if degree < 0:
        raise ValueError("degree cannot be negative")

    phase = np.exp(1j * float(node.phase))
    if degree == 0:
        return np.asarray(1.0 + phase, dtype=COMPLEX)

    shape = (2,) * degree
    tensor = np.zeros(shape, dtype=COMPLEX)
    if node.kind == "z":
        tensor[(0,) * degree] = 1.0
        tensor[(1,) * degree] = phase
        return tensor

    # X spiders are Z spiders expressed in the Hadamard-rotated basis.
    for bits in product((0, 1), repeat=degree):
        zero_branch = np.prod([HADAMARD[bit, 0] for bit in bits])
        one_branch = np.prod([HADAMARD[bit, 1] for bit in bits])
        tensor[bits] = zero_branch + phase * one_branch
    return tensor


def linear_map(diagram: ZXDiagram) -> np.ndarray:
    """Contract a diagram into a matrix with outputs as rows and inputs as columns.

    Standard ZX scalar factors are retained. A zero-input diagram therefore
    returns a state column, and that state is not normalized automatically.
    """
    diagram.validate()

    next_label = 0
    endpoint_labels: dict[tuple[str, str], int] = {}
    operands: list[np.ndarray] = []
    subscripts: list[list[int]] = []

    for edge in sorted(diagram.edges.values(), key=lambda item: item.edge_id):
        source_label = next_label
        target_label = next_label + 1
        next_label += 2
        endpoint_labels[(edge.edge_id, edge.source)] = source_label
        endpoint_labels[(edge.edge_id, edge.target)] = target_label
        operands.append(IDENTITY if edge.kind == "plain" else HADAMARD)
        subscripts.append([source_label, target_label])

    for node in sorted(diagram.nodes.values(), key=lambda item: item.node_id):
        if node.kind == "boundary":
            continue
        incident = diagram.incident_edges(node.node_id)
        labels = [endpoint_labels[(edge.edge_id, node.node_id)] for edge in incident]
        operands.append(spider_tensor(node, len(incident)))
        subscripts.append(labels)

    # NumPy's final tensor axis varies fastest when reshaped. Reversing each
    # boundary group therefore makes boundary 0 the least-significant basis
    # bit, matching QAC/Qiskit and the existing QMW circuit bridge.
    external_nodes = list(reversed(diagram.boundaries("output"))) + list(
        reversed(diagram.boundaries("input"))
    )
    output_labels: list[int] = []
    for node in external_nodes:
        edge = diagram.incident_edges(node.node_id)[0]
        output_labels.append(endpoint_labels[(edge.edge_id, node.node_id)])

    einsum_arguments: list[object] = []
    for operand, labels in zip(operands, subscripts):
        einsum_arguments.extend((operand, labels))
    einsum_arguments.append(output_labels)
    tensor = np.einsum(*einsum_arguments, optimize=True)

    output_dimension = 1 << len(diagram.boundaries("output"))
    input_dimension = 1 << len(diagram.boundaries("input"))
    return diagram.scalar * np.asarray(tensor, dtype=COMPLEX).reshape(
        output_dimension,
        input_dimension,
    )


def normalized_state(diagram: ZXDiagram, *, atol: float = 1e-12) -> np.ndarray:
    """Return a normalized state vector for a zero-input ZX diagram."""
    if diagram.boundaries("input"):
        raise ValueError("normalized_state requires a diagram with no inputs")
    state = linear_map(diagram).reshape(-1)
    norm = float(np.linalg.norm(state))
    if norm <= atol:
        raise ValueError("diagram denotes the zero vector")
    return state / norm
