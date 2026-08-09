"""Compile a tagged visual ZX diagram into a bounded density candidate."""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Any

import numpy as np

from density.density_state_injection import validate_density_matrix


PAULI_X = np.asarray([[0, 1], [1, 0]], dtype=np.complex128)
PAULI_Y = np.asarray([[0, -1j], [1j, 0]], dtype=np.complex128)
PAULI_Z = np.asarray([[1, 0], [0, -1]], dtype=np.complex128)


@dataclass(frozen=True)
class ZXDensityFrame:
    revision: int
    qubit_count: int
    rho: np.ndarray
    mode: str
    success_probability: float
    trace: float
    purity: float
    coherence_l1: float
    entropy: float
    minimum_eigenvalue: float
    probabilities: tuple[float, ...]
    local_bloch: tuple[tuple[float, float, float], ...]
    local_purity: tuple[float, ...]
    local_entropy: tuple[float, ...]
    message: str


def _entropy(matrix: np.ndarray) -> float:
    values = np.clip(np.linalg.eigvalsh(matrix).real, 0.0, 1.0)
    values = values[values > 1e-12]
    return float(-np.sum(values * np.log2(values))) if values.size else 0.0


def _reduced_q0_lsb(rho: np.ndarray, qubit: int) -> np.ndarray:
    """Reduce a q0-LSB density matrix to one logical qubit."""
    dimension = int(rho.shape[0])
    qubit_count = int(round(math.log2(dimension)))
    if rho.shape != (dimension, dimension) or (1 << qubit_count) != dimension:
        raise ValueError("density matrix dimension must be a power of two")
    if qubit not in range(qubit_count):
        raise ValueError(
            f"{qubit_count}-qubit density qubit must be in 0..{qubit_count - 1}"
        )
    reduced = np.zeros((2, 2), dtype=np.complex128)
    bit = 1 << qubit
    for base in range(dimension):
        if base & bit:
            continue
        indices = (base, base | bit)
        for row_bit in (0, 1):
            for column_bit in (0, 1):
                reduced[row_bit, column_bit] += rho[
                    indices[row_bit],
                    indices[column_bit],
                ]
    return reduced


def _boundary_layout(graph: Any) -> tuple[list[Any], list[Any]]:
    boundaries = [node for node in graph.nodes.values() if node.kind == "B"]
    if not boundaries:
        raise ValueError(
            "density mode needs one to eight tagged output boundaries"
        )
    if any(
        node.boundary_role not in {"input", "output"}
        or node.boundary_index < 0
        for node in boundaries
    ):
        raise ValueError(
            "density mode requires every boundary to be tagged input/output q0..qN"
        )

    inputs = [node for node in boundaries if node.boundary_role == "input"]
    outputs = [node for node in boundaries if node.boundary_role == "output"]
    output_indices = {node.boundary_index for node in outputs}
    input_indices = {node.boundary_index for node in inputs}
    qubit_count = len(outputs)
    if (
        qubit_count not in range(1, 9)
        or output_indices != set(range(qubit_count))
    ):
        raise ValueError(
            "dense mode needs one to eight contiguous outputs q0..qN"
        )
    if inputs and (
        len(inputs) != qubit_count
        or input_indices != set(range(qubit_count))
    ):
        raise ValueError(
            "process mode inputs must match the contiguous output qubits q0..qN"
        )
    return inputs, outputs


def density_frame_from_visual_graph(
    graph: Any,
    revision: int,
    *,
    atol: float = 1e-12,
) -> ZXDensityFrame:
    """Return a physical density matrix from a tagged visual graph.

    A zero-input graph with one to eight outputs prepares a pure state. A map
    with matching inputs and outputs is applied to its all-zero input. General
    nonunitary maps are normalized explicitly and expose their
    pre-normalization success weight.
    """
    inputs, outputs = _boundary_layout(graph)
    discards = sorted(
        (node for node in graph.nodes.values() if node.kind == "D"),
        key=lambda item: item.node_id,
    )
    for discard in discards:
        degree = sum(
            1
            for edge in graph.edges
            if discard.node_id in {edge.source, edge.target}
        )
        if degree != 1:
            raise ValueError(
                f"discard node {discard.node_id} must terminate exactly one wire"
            )

    from pyzx.tensor import tensorfy

    pyzx_graph = graph._to_pyzx()
    system_outputs = tuple(
        node.node_id
        for node in sorted(
            outputs,
            key=lambda item: item.boundary_index,
            reverse=True,
        )
    )
    environment_outputs = tuple(node.node_id for node in discards)
    input_order = tuple(
        node.node_id
        for node in sorted(
            inputs,
            key=lambda item: item.boundary_index,
            reverse=True,
        )
    )
    pyzx_graph.set_outputs(system_outputs + environment_outputs)
    pyzx_graph.set_inputs(input_order)
    tensor = np.asarray(
        tensorfy(pyzx_graph, preserve_scalar=True),
        dtype=np.complex128,
    )
    qubit_count = len(outputs)
    system_dimension = 1 << qubit_count
    input_dimension = 1 << len(inputs)
    environment_dimension = 1 << len(discards)
    if not inputs:
        base_mode = (
            "discard_cpm_state"
            if discards
            else "state_preparation"
        )
        raw_amplitudes = tensor.reshape(
            system_dimension,
            environment_dimension,
        )
    else:
        base_mode = (
            "discard_cpm_map_on_zero"
            if discards
            else "map_on_zero"
        )
        operator = tensor.reshape(
            system_dimension,
            environment_dimension,
            input_dimension,
        )
        raw_amplitudes = operator[:, :, 0]

    amplitudes = raw_amplitudes
    mode = base_mode

    unnormalized_rho = amplitudes @ amplitudes.conj().T
    success_probability = float(np.trace(unnormalized_rho).real)
    if (
        not math.isfinite(success_probability)
        or success_probability <= atol
    ):
        raise ValueError("ZX diagram produces the zero or a non-finite state")
    rho = unnormalized_rho / success_probability
    rho = validate_density_matrix(rho, dimension=system_dimension)

    eigenvalues = np.linalg.eigvalsh(rho).real
    trace = float(np.trace(rho).real)
    purity = float(np.trace(rho @ rho).real)
    off_diagonal = rho - np.diag(np.diag(rho))
    coherence = float(np.sum(np.abs(off_diagonal)))
    entropy = _entropy(rho)

    local_bloch: list[tuple[float, float, float]] = []
    local_purity: list[float] = []
    local_entropy: list[float] = []
    for qubit in range(qubit_count):
        reduced = _reduced_q0_lsb(rho, qubit)
        local_bloch.append(
            (
                float(np.trace(reduced @ PAULI_X).real),
                float(np.trace(reduced @ PAULI_Y).real),
                float(np.trace(reduced @ PAULI_Z).real),
            )
        )
        local_purity.append(float(np.trace(reduced @ reduced).real))
        local_entropy.append(_entropy(reduced))

    if base_mode == "discard_cpm_state":
        message = (
            "discard-ZX dilation doubled and environment traced"
        )
    elif base_mode == "discard_cpm_map_on_zero":
        message = (
            "discard-ZX CPM map applied to the all-zero input"
        )
    elif base_mode == "state_preparation":
        message = (
            f"{qubit_count}-qubit ZX pure state embedded as a density matrix"
        )
    else:
        message = (
            f"{qubit_count}-qubit ZX map applied to its all-zero input"
        )
    return ZXDensityFrame(
        revision=int(revision),
        qubit_count=qubit_count,
        rho=rho,
        mode=mode,
        success_probability=success_probability,
        trace=trace,
        purity=purity,
        coherence_l1=coherence,
        entropy=entropy,
        minimum_eigenvalue=float(eigenvalues.min()),
        probabilities=tuple(float(value) for value in np.diag(rho).real),
        local_bloch=tuple(local_bloch),
        local_purity=tuple(local_purity),
        local_entropy=tuple(local_entropy),
        message=message,
    )
