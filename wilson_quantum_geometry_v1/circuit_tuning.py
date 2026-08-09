"""Circuit interaction geometry as a source of Wilson tuning frames."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Any

from .cps import CombinationProductSet


@dataclass(frozen=True)
class CircuitGeometryFingerprint:
    qubit_count: int
    gate_count: int
    interaction_edges: tuple[tuple[int, int, int], ...]
    component_sizes: tuple[int, ...]
    weighted_degrees: tuple[int, ...]
    hadamard_count: int
    phase_gate_count: int
    depth: int

    @property
    def connected(self) -> bool:
        return self.component_sizes == (self.qubit_count,)


@dataclass(frozen=True)
class CircuitWilsonTuningFrame:
    family: str
    master_set: tuple[int, ...]
    mos_position: Fraction
    fingerprint: CircuitGeometryFingerprint


@dataclass(frozen=True)
class WilsonTuningVertex:
    bitmask: int
    factors: tuple[int, ...]
    product: int
    ratio: Fraction
    audition_ratio: Fraction


def _fold_fraction(value: Fraction, period: Fraction) -> Fraction:
    while value < 1:
        value *= period
    while value >= period:
        value /= period
    return value


def wilson_tuning_vertices(
    factors: tuple[int, ...],
    *,
    grade: int = 2,
    anchor_mask: int = 0b0011,
    period: int | Fraction = 2,
) -> tuple[WilsonTuningVertex, ...]:
    """Build exact display/audition labels for one active CPS tuning frame."""
    normalized = tuple(int(value) for value in factors)
    anchor_indices = tuple(
        index for index in range(len(normalized)) if (int(anchor_mask) >> index) & 1
    )
    if len(anchor_indices) != int(grade):
        raise ValueError("anchor_mask must have the selected CPS Hamming weight")
    cps = CombinationProductSet(
        normalized,
        int(grade),
        period=period,
        anchor=anchor_indices,
    )
    period_fraction = Fraction(period)
    return tuple(
        WilsonTuningVertex(
            bitmask=tone.bitmask,
            factors=tone.factors,
            product=tone.product,
            ratio=Fraction(tone.ratio_numerator, tone.ratio_denominator),
            audition_ratio=_fold_fraction(Fraction(tone.product), period_fraction),
        )
        for tone in cps.tones
    )


def circuit_geometry_fingerprint(circuit: Any) -> CircuitGeometryFingerprint:
    """Extract permutation-aware interaction structure from a Qiskit circuit."""
    qubit_count = int(circuit.num_qubits)
    edge_weights: dict[tuple[int, int], int] = {}
    degrees = [0] * qubit_count
    hadamards = 0
    phase_gates = 0
    phase_names = {"p", "phase", "s", "sdg", "t", "tdg", "z", "rz"}
    for instruction in circuit.data:
        name = str(instruction.operation.name).lower()
        indices = tuple(circuit.find_bit(qubit).index for qubit in instruction.qubits)
        if name == "h":
            hadamards += 1
        if name in phase_names:
            phase_gates += 1
        if len(indices) >= 2:
            # Multi-qubit gates contribute every pair in their interaction
            # hyperedge, retaining multiplicity as a coupling weight.
            for left_position in range(len(indices)):
                for right_position in range(left_position + 1, len(indices)):
                    edge = tuple(sorted((indices[left_position], indices[right_position])))
                    edge_weights[edge] = edge_weights.get(edge, 0) + 1
                    degrees[edge[0]] += 1
                    degrees[edge[1]] += 1

    neighbors = {index: set() for index in range(qubit_count)}
    for left, right in edge_weights:
        neighbors[left].add(right)
        neighbors[right].add(left)
    unseen = set(range(qubit_count))
    components = []
    while unseen:
        seed = min(unseen)
        stack = [seed]
        unseen.remove(seed)
        size = 0
        while stack:
            vertex = stack.pop()
            size += 1
            for neighbor in sorted(neighbors[vertex]):
                if neighbor in unseen:
                    unseen.remove(neighbor)
                    stack.append(neighbor)
        components.append(size)

    return CircuitGeometryFingerprint(
        qubit_count=qubit_count,
        gate_count=len(circuit.data),
        interaction_edges=tuple(
            (left, right, weight)
            for (left, right), weight in sorted(edge_weights.items())
        ),
        component_sizes=tuple(sorted(components, reverse=True)),
        weighted_degrees=tuple(degrees),
        hadamard_count=hadamards,
        phase_gate_count=phase_gates,
        depth=int(circuit.depth()),
    )


def circuit_wilson_tuning_frame(circuit: Any) -> CircuitWilsonTuningFrame:
    """Derive a distinct but reproducible Wilson family from circuit geometry.

    These families are a declared compositional sonification mapping, not a
    claim that quantum gates possess literal harmonic ratios. Component
    structure separates local/pair fields from globally connected fields;
    superposition and phase density separate a woven global field from a
    single-source GHZ-like propagation tree.
    """
    fingerprint = circuit_geometry_fingerprint(circuit)
    if fingerprint.qubit_count != 4:
        raise ValueError("the live circuit-tuning adapter currently requires four qubits")
    if fingerprint.gate_count == 0:
        family = "empty"
        factors = (1, 3, 5, 7)
        mos = Fraction(1, 2)
    elif not fingerprint.interaction_edges:
        family = "separable"
        factors = (1, 3, 5, 7)
        mos = Fraction(1, 2)
    elif not fingerprint.connected:
        family = "paired"
        factors = (1, 3, 5, 7)
        mos = Fraction(2, 5)
    elif fingerprint.hadamard_count > 1 or fingerprint.phase_gate_count > 0:
        family = "woven"
        factors = (1, 5, 11, 13)
        mos = Fraction(5, 12)
    else:
        family = "global"
        factors = (1, 3, 7, 11)
        mos = Fraction(3, 7)

    # Structural role, rather than raw qubit number, owns each factor. This
    # makes a topologically equivalent circuit permutation retain its family
    # while still exposing which qubits are central or peripheral.
    role_order = sorted(
        range(4),
        key=lambda qubit: (-fingerprint.weighted_degrees[qubit], qubit),
    )
    assigned = [0] * 4
    for factor, qubit in zip(factors, role_order):
        assigned[qubit] = factor
    return CircuitWilsonTuningFrame(
        family=family,
        master_set=tuple(assigned),
        mos_position=mos,
        fingerprint=fingerprint,
    )


__all__ = [
    "CircuitGeometryFingerprint",
    "CircuitWilsonTuningFrame",
    "WilsonTuningVertex",
    "circuit_geometry_fingerprint",
    "circuit_wilson_tuning_frame",
    "wilson_tuning_vertices",
]
