"""Core graph, circuit, and score stages for Quantum Graph Canon v1."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import math
from typing import Any

import networkx as nx
import numpy as np

from procedural_notation_v1 import build_polyphonic_timed_score
from procedural_notation_v1.density_matrix_canon import (
    build_density_matrix_cable_net_canon,
)
from procedural_notation_v1.surface_mesh_graph import (
    apply_torus_hexatonic_mapping,
    build_quartic_torus_mesh,
)
from procedural_notation_v1.tensile_surface_graph import build_tensile_saddle_mesh


@dataclass(frozen=True)
class QuantumGraphCanonConfig:
    """Reproducible controls for the graph-conditioned circuit experiment."""

    layers: int = 4
    partition_seed: int = 17
    entangled: bool = True
    entanglement_scale: float = 0.85
    dephasing: float = 0.12
    coherence_threshold: float = 0.08
    slot_ticks: int = 4
    snapshot_gap_ticks: int = 4

    def __post_init__(self) -> None:
        if isinstance(self.layers, bool) or not isinstance(self.layers, int) or self.layers <= 0:
            raise ValueError("layers must be a positive integer")
        if (
            isinstance(self.partition_seed, bool)
            or not isinstance(self.partition_seed, int)
            or self.partition_seed < 0
        ):
            raise ValueError("partition_seed must be a nonnegative integer")
        if not isinstance(self.entangled, bool):
            raise ValueError("entangled must be a boolean")
        if not math.isfinite(self.entanglement_scale) or self.entanglement_scale < 0.0:
            raise ValueError("entanglement_scale must be finite and nonnegative")
        if not math.isfinite(self.dephasing) or not 0.0 <= self.dephasing <= 1.0:
            raise ValueError("dephasing must lie in [0, 1]")
        if (
            not math.isfinite(self.coherence_threshold)
            or not 0.0 <= self.coherence_threshold < 1.0
        ):
            raise ValueError("coherence_threshold must lie in [0, 1)")
        for name, value in (
            ("slot_ticks", self.slot_ticks),
            ("snapshot_gap_ticks", self.snapshot_gap_ticks),
        ):
            if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
                raise ValueError(f"{name} must be a positive integer")


@dataclass
class QuantumGraphCanonExperiment:
    """All stages needed to inspect or reproduce one generated score."""

    config: QuantumGraphCanonConfig
    source_graph: nx.Graph
    quotient_graph: nx.Graph
    circuits: tuple[Any, ...]
    density_snapshots: tuple[np.ndarray, ...]
    canon_graph: nx.DiGraph


def build_default_source_graph() -> nx.Graph:
    """Return the attributed quartic-torus graph used by the first study."""
    mesh = build_quartic_torus_mesh(
        major_segments=12,
        minor_segments=8,
        eigenmode_index=7,
    )
    source = apply_torus_hexatonic_mapping(mesh)
    source.graph.update(
        experiment_source="quartic_torus_hexatonic_graph",
        quantum_graph_canon_version=1,
    )
    return source


def build_four_region_quotient_graph(
    source_graph: nx.Graph,
    seed: int = 17,
) -> nx.Graph:
    """Recursively bisect a connected source graph into four musical regions.

    The quotient nodes retain aggregate pitch, time, eigenfield, curvature, and
    position features. Quotient edges count and weight source edges crossing
    between regions. These four nodes become four qubits in the next stage.
    """
    if source_graph.is_directed():
        raise ValueError("source_graph must be undirected")
    if source_graph.number_of_nodes() < 4:
        raise ValueError("source_graph must contain at least four nodes")
    if not nx.is_connected(source_graph):
        raise ValueError("source_graph must be connected")
    if isinstance(seed, bool) or not isinstance(seed, int) or seed < 0:
        raise ValueError("seed must be a nonnegative integer")

    first_pair = nx.community.kernighan_lin_bisection(
        source_graph,
        weight="coupling",
        seed=seed,
    )
    communities: list[set[Any]] = []
    for offset, parent in enumerate(_ordered_communities(first_pair), start=1):
        child_pair = nx.community.kernighan_lin_bisection(
            source_graph.subgraph(parent),
            weight="coupling",
            seed=seed + offset,
        )
        communities.extend(set(child) for child in child_pair)
    communities = _ordered_communities(communities)

    quotient = nx.Graph(
        geometry="four_region_quotient",
        partition_method="recursive_kernighan_lin",
        partition_seed=seed,
        source_geometry=source_graph.graph.get("geometry"),
        source_node_count=source_graph.number_of_nodes(),
        source_edge_count=source_graph.number_of_edges(),
    )
    node_to_region: dict[Any, int] = {}
    for region_id, members in enumerate(communities):
        ordered_members = tuple(sorted(members, key=repr))
        for member in ordered_members:
            node_to_region[member] = region_id
        centroid = _position_centroid(source_graph, ordered_members)
        quotient.add_node(
            region_id,
            source_members=ordered_members,
            source_member_count=len(ordered_members),
            pitch_space_mean=_mean_attribute(source_graph, ordered_members, "pitch_space", 60.0),
            onset_tick_mean=_mean_attribute(source_graph, ordered_members, "onset_tick", 0.0),
            duration_ticks_mean=_mean_attribute(
                source_graph,
                ordered_members,
                "duration_ticks",
                1.0,
            ),
            eigenfield_mean=_mean_attribute(source_graph, ordered_members, "field_value", 0.0),
            curvature_mean=_mean_attribute(
                source_graph,
                ordered_members,
                "gaussian_curvature",
                0.0,
            ),
            source_degree_mean=float(
                np.mean([source_graph.degree(member) for member in ordered_members])
            ),
            position_centroid=centroid,
            position_phase=float(math.atan2(centroid[1], centroid[0])),
            internal_edge_count=0,
            boundary_edge_count=0,
        )

    for start, end, data in source_graph.edges(data=True):
        start_region = node_to_region[start]
        end_region = node_to_region[end]
        if start_region == end_region:
            quotient.nodes[start_region]["internal_edge_count"] += 1
            continue
        quotient.nodes[start_region]["boundary_edge_count"] += 1
        quotient.nodes[end_region]["boundary_edge_count"] += 1
        edge_key = tuple(sorted((start_region, end_region)))
        coupling = float(data.get("coupling", data.get("weight", 1.0)))
        if quotient.has_edge(*edge_key):
            quotient.edges[edge_key]["cut_edge_count"] += 1
            quotient.edges[edge_key]["coupling_sum"] += coupling
        else:
            quotient.add_edge(
                *edge_key,
                cut_edge_count=1,
                coupling_sum=coupling,
            )

    if quotient.number_of_nodes() != 4 or not nx.is_connected(quotient):
        raise RuntimeError("recursive bisection did not produce a connected four-node quotient")
    quotient.graph["communities"] = tuple(
        quotient.nodes[node_id]["source_members"] for node_id in quotient.nodes
    )
    return quotient


def encode_quotient_graph(
    quotient_graph: nx.Graph,
    entanglement_scale: float = 0.85,
) -> nx.Graph:
    """Map quotient features to local rotations and weighted RZZ angles."""
    if set(quotient_graph.nodes) != {0, 1, 2, 3}:
        raise ValueError("quotient_graph nodes must be the four integer qubit ids 0 through 3")
    if not math.isfinite(entanglement_scale) or entanglement_scale < 0.0:
        raise ValueError("entanglement_scale must be finite and nonnegative")

    encoded = quotient_graph.copy()
    node_order = tuple(sorted(encoded.nodes))
    field_units = _unit_interval(
        [encoded.nodes[node_id]["eigenfield_mean"] for node_id in node_order]
    )
    onset_units = _unit_interval(
        [encoded.nodes[node_id]["onset_tick_mean"] for node_id in node_order]
    )
    degree_units = _unit_interval(
        [encoded.nodes[node_id]["source_degree_mean"] for node_id in node_order]
    )

    for index, node_id in enumerate(node_order):
        data = encoded.nodes[node_id]
        pitch_phase = math.tau * ((data["pitch_space_mean"] % 12.0) / 12.0)
        data.update(
            qubit=node_id,
            field_unit=field_units[index],
            onset_unit=onset_units[index],
            degree_unit=degree_units[index],
            rotation_y=math.pi / 6.0 + 2.0 * math.pi * field_units[index] / 3.0,
            rotation_z=pitch_phase + 0.5 * data["position_phase"],
            rotation_x=math.pi / 12.0 + math.pi * (onset_units[index] + degree_units[index]) / 6.0,
        )

    maximum_coupling = max(
        (float(data["coupling_sum"]) for _, _, data in encoded.edges(data=True)),
        default=1.0,
    )
    if maximum_coupling <= 0.0:
        maximum_coupling = 1.0
    for _, _, data in encoded.edges(data=True):
        normalized = float(data["coupling_sum"]) / maximum_coupling
        data.update(
            normalized_coupling=normalized,
            entangling_angle=entanglement_scale * math.pi * normalized / 2.0,
        )
    encoded.graph.update(
        node_encoding="eigenfield->RY; pitch+position->RZ; onset+degree->RX",
        edge_encoding="normalized crossing coupling->RZZ",
        entanglement_scale=float(entanglement_scale),
    )
    return encoded


def build_graph_conditioned_density_snapshots(
    encoded_graph: nx.Graph,
    config: QuantumGraphCanonConfig,
) -> tuple[tuple[np.ndarray, ...], tuple[Any, ...]]:
    """Build cumulative circuit layers and return dephased density snapshots."""
    from qiskit import QuantumCircuit
    from qiskit.quantum_info import Statevector

    for node_id in range(4):
        if node_id not in encoded_graph:
            raise ValueError("encoded_graph must contain qubits 0 through 3")
        required = {"rotation_x", "rotation_y", "rotation_z"}
        if not required <= encoded_graph.nodes[node_id].keys():
            raise ValueError(f"quotient node {node_id} has not been encoded")

    circuit = QuantumCircuit(4, name="quantum_graph_canon_v1")
    snapshots: list[np.ndarray] = []
    circuits: list[Any] = []
    layer_divisor = float(config.layers)
    for layer_index in range(config.layers):
        for node_id in range(4):
            data = encoded_graph.nodes[node_id]
            circuit.ry(data["rotation_y"] / layer_divisor, node_id)
            circuit.rz(data["rotation_z"] / layer_divisor, node_id)
            circuit.rx(data["rotation_x"] / layer_divisor, node_id)
        if config.entangled:
            for start, end, data in sorted(encoded_graph.edges(data=True)):
                circuit.rzz(data["entangling_angle"] / layer_divisor, start, end)

        state = np.asarray(Statevector.from_instruction(circuit).data, dtype=np.complex128)
        pure_density = np.outer(state, state.conj())
        population_density = np.diag(np.diag(pure_density)).astype(np.complex128)
        density = (
            (1.0 - config.dephasing) * pure_density
            + config.dephasing * population_density
        )
        density /= np.trace(density)
        snapshots.append(density)
        mode = "entangled" if config.entangled else "local"
        snapshot_circuit = circuit.copy(
            name=f"quantum_graph_canon_{mode}_layer_{layer_index + 1}"
        )
        snapshot_circuit.metadata = {
            "experiment": "quantum_graph_canon_v1",
            "layer": layer_index + 1,
            "entangled": config.entangled,
            "density_provenance": "exact_statevector_plus_explicit_dephasing",
        }
        circuits.append(snapshot_circuit)

    return tuple(snapshots), tuple(circuits)


def build_default_experiment(
    config: QuantumGraphCanonConfig | None = None,
) -> QuantumGraphCanonExperiment:
    """Run the complete graph-to-circuit-to-canon pipeline in memory."""
    selected = config or QuantumGraphCanonConfig()
    source = build_default_source_graph()
    quotient = build_four_region_quotient_graph(source, selected.partition_seed)
    encoded = encode_quotient_graph(quotient, selected.entanglement_scale)
    densities, circuits = build_graph_conditioned_density_snapshots(encoded, selected)
    canon = build_density_matrix_cable_net_canon(
        build_tensile_saddle_mesh(),
        densities,
        coherence_threshold=selected.coherence_threshold,
        slot_ticks=selected.slot_ticks,
        snapshot_gap_ticks=selected.snapshot_gap_ticks,
    )
    canon.graph.update(
        quantum_graph_canon_version=1,
        source_graph=source.graph.get("experiment_source"),
        quotient_method=encoded.graph["partition_method"],
        circuit_mode="entangled" if selected.entangled else "local_unentangled",
        circuit_layers=selected.layers,
        density_provenance="exact_statevector_plus_explicit_dephasing",
        explicit_dephasing=selected.dephasing,
    )
    return QuantumGraphCanonExperiment(
        config=selected,
        source_graph=source,
        quotient_graph=encoded,
        circuits=circuits,
        density_snapshots=densities,
        canon_graph=canon,
    )


def build_quantum_graph_canon_score(
    experiment: QuantumGraphCanonExperiment,
    title: str | None = None,
):
    """Render an experiment's event graph as a 32-part music21 score."""
    canon = experiment.canon_graph
    measures = math.ceil(canon.graph["total_ticks"] / 32)
    selected_title = title or (
        "Quartic-Torus Quantum Graph Canon No. 14 — "
        + ("Entangled" if experiment.config.entangled else "Local Control")
    )
    score = build_polyphonic_timed_score(
        canon,
        measures=measures,
        beats_per_measure=4,
        ticks_per_quarter=8,
        title=selected_title,
        include_node_labels=False,
    )
    first_event_by_voice: dict[str, dict[str, Any]] = {}
    for _, data in canon.nodes(data=True):
        first_event_by_voice.setdefault(data["voice"], data)
    for part, voice_id in zip(score.parts, sorted(canon.graph["voices"]), strict=True):
        data = first_event_by_voice[voice_id]
        family, number = voice_id.split("_")[1:]
        part.partName = (
            f"QGC {family.title()} {int(number)} — entry {data['canon_entry_index'] + 1}"
        )
    return score


def experiment_manifest(experiment: QuantumGraphCanonExperiment) -> dict[str, Any]:
    """Return JSON-safe provenance and comparison metrics for one experiment."""
    quotient_nodes = []
    for node_id, data in experiment.quotient_graph.nodes(data=True):
        quotient_nodes.append(
            {
                "qubit": node_id,
                "source_members": [repr(member) for member in data["source_members"]],
                "source_member_count": data["source_member_count"],
                "pitch_space_mean": data["pitch_space_mean"],
                "onset_tick_mean": data["onset_tick_mean"],
                "eigenfield_mean": data["eigenfield_mean"],
                "curvature_mean": data["curvature_mean"],
                "rotation_x": data["rotation_x"],
                "rotation_y": data["rotation_y"],
                "rotation_z": data["rotation_z"],
            }
        )
    quotient_edges = [
        {
            "qubits": [start, end],
            "cut_edge_count": data["cut_edge_count"],
            "coupling_sum": data["coupling_sum"],
            "normalized_coupling": data["normalized_coupling"],
            "entangling_angle": data["entangling_angle"],
        }
        for start, end, data in experiment.quotient_graph.edges(data=True)
    ]
    snapshot_metrics = []
    for layer, (density, circuit) in enumerate(
        zip(experiment.density_snapshots, experiment.circuits, strict=True),
        start=1,
    ):
        populations = np.clip(np.real(np.diag(density)), 0.0, 1.0)
        nonzero = populations[populations > 1e-15]
        coherence_l1 = float(np.sum(np.abs(density)) - np.sum(np.abs(np.diag(density))))
        snapshot_metrics.append(
            {
                "layer": layer,
                "purity": float(np.real(np.trace(density @ density))),
                "population_entropy_bits": float(-np.sum(nonzero * np.log2(nonzero))),
                "l1_coherence": coherence_l1,
                "circuit_depth": circuit.depth(),
                "operation_counts": {
                    str(name): int(count) for name, count in circuit.count_ops().items()
                },
            }
        )
    return {
        "experiment": "Quantum Graph Canon v1",
        "config": asdict(experiment.config),
        "provenance": {
            "source": "NetworkX quartic-torus graph with graph-Laplacian eigenfield",
            "partition": "recursive Kernighan-Lin four-region quotient",
            "circuit": "Qiskit exact Statevector",
            "density": "pure density mixed with an explicit population dephasing channel",
            "hardware_measurement": False,
        },
        "source_graph": {
            "geometry": experiment.source_graph.graph.get("geometry"),
            "nodes": experiment.source_graph.number_of_nodes(),
            "edges": experiment.source_graph.number_of_edges(),
        },
        "quotient_graph": {
            "nodes": quotient_nodes,
            "edges": quotient_edges,
        },
        "snapshots": snapshot_metrics,
        "score_graph": {
            "voices": experiment.canon_graph.graph["voice_count"],
            "sounding_events": experiment.canon_graph.graph["sounding_matrix_events"],
            "possible_events": experiment.canon_graph.graph["possible_matrix_events"],
            "total_ticks": experiment.canon_graph.graph["total_ticks"],
        },
    }


def _ordered_communities(communities) -> list[set[Any]]:
    return sorted(
        (set(community) for community in communities),
        key=lambda community: tuple(sorted((repr(node) for node in community))),
    )


def _mean_attribute(
    graph: nx.Graph,
    members: tuple[Any, ...],
    attribute: str,
    default: float,
) -> float:
    values = [float(graph.nodes[node].get(attribute, default)) for node in members]
    return float(np.mean(values))


def _position_centroid(
    graph: nx.Graph,
    members: tuple[Any, ...],
) -> tuple[float, float, float]:
    padded_positions = []
    for node in members:
        raw_position = graph.nodes[node].get("position", (0.0, 0.0, 0.0))
        position = tuple(float(value) for value in raw_position)
        padded_positions.append((position + (0.0, 0.0, 0.0))[:3])
    centroid = np.mean(np.asarray(padded_positions, dtype=float), axis=0)
    return tuple(float(value) for value in centroid)


def _unit_interval(values: list[float]) -> tuple[float, ...]:
    array = np.asarray(values, dtype=float)
    minimum = float(np.min(array))
    maximum = float(np.max(array))
    if math.isclose(minimum, maximum):
        return tuple(0.5 for _ in values)
    return tuple(float((value - minimum) / (maximum - minimum)) for value in array)
