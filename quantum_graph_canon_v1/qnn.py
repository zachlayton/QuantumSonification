"""Topology-preserving SamplerQNN integration for Quantum Graph Canon v1."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import math
from typing import Any, Sequence

import networkx as nx
import numpy as np

from procedural_notation_v1.density_matrix_canon import (
    build_density_matrix_cable_net_canon,
)
from procedural_notation_v1.tensile_surface_graph import build_tensile_saddle_mesh
from quantum_graph_canon_v1.core import (
    QuantumGraphCanonConfig,
    QuantumGraphCanonExperiment,
    build_default_source_graph,
    build_four_region_quotient_graph,
    build_graph_conditioned_density_snapshots,
    build_quantum_graph_canon_score,
    encode_quotient_graph,
    experiment_manifest,
)


@dataclass(frozen=True)
class QuantumGraphQNNConfig:
    """Controls for the graph-topology SamplerQNN decision layer."""

    feature_reps: int = 2
    ansatz_reps: int = 2
    shots: int = 4096
    sampler_seed: int = 17
    weight_seed: int = 23
    untrained_weight_scale: float = 0.15
    input_mapping: str = "hybrid"
    activation_floor: float = 0.20

    def __post_init__(self) -> None:
        for name, value in (
            ("feature_reps", self.feature_reps),
            ("ansatz_reps", self.ansatz_reps),
            ("shots", self.shots),
        ):
            if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
                raise ValueError(f"{name} must be a positive integer")
        for name, value in (
            ("sampler_seed", self.sampler_seed),
            ("weight_seed", self.weight_seed),
        ):
            if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                raise ValueError(f"{name} must be a nonnegative integer")
        if (
            not math.isfinite(self.untrained_weight_scale)
            or self.untrained_weight_scale < 0.0
        ):
            raise ValueError("untrained_weight_scale must be finite and nonnegative")
        if self.input_mapping not in {"hybrid", "eigenfield"}:
            raise ValueError("input_mapping must be 'hybrid' or 'eigenfield'")
        if not math.isfinite(self.activation_floor) or not 0.0 <= self.activation_floor <= 1.0:
            raise ValueError("activation_floor must lie in [0, 1]")


@dataclass
class QuantumGraphSamplerQNN:
    """A SamplerQNN together with its graph and parameter provenance."""

    config: QuantumGraphQNNConfig
    graph_edges: tuple[tuple[int, int], ...]
    circuit: Any
    network: Any
    input_parameters: tuple[Any, ...]
    weight_parameters: tuple[Any, ...]


@dataclass(frozen=True)
class QuantumGraphQNNResult:
    """One forward pass interpreted as four-region activation probabilities."""

    input_data: tuple[float, ...]
    weights: tuple[float, ...]
    weight_provenance: str
    probabilities: tuple[float, ...]
    activation_marginals: tuple[float, ...]
    selected_mask: int
    selected_region_bits: tuple[int, ...]
    distribution_entropy_bits: float


@dataclass
class QuantumGraphQNNExperiment:
    """A QNN decision layer and the canon it conditions."""

    canon_experiment: QuantumGraphCanonExperiment
    qnn_model: QuantumGraphSamplerQNN
    qnn_result: QuantumGraphQNNResult


def build_topology_preserving_sampler_qnn(
    encoded_graph: nx.Graph,
    config: QuantumGraphQNNConfig | None = None,
) -> QuantumGraphSamplerQNN:
    """Build a four-qubit QNN whose feature and ansatz edges match NetworkX."""
    from qiskit import QuantumCircuit
    from qiskit.circuit.library import real_amplitudes, zz_feature_map
    from qiskit.primitives import StatevectorSampler
    from qiskit_machine_learning.neural_networks import SamplerQNN

    selected = config or QuantumGraphQNNConfig()
    _validate_encoded_graph(encoded_graph)
    graph_edges = tuple(
        (int(start), int(end)) for start, end in sorted(encoded_graph.edges)
    )
    if not graph_edges:
        raise ValueError("encoded_graph must contain at least one edge")
    ansatz_entanglement = [list(edge) for edge in graph_edges]
    # Qiskit 2.4's functional Pauli feature map expects a mapping keyed by
    # Pauli-term size when a custom topology is supplied. Retain all local Z
    # terms while restricting the two-qubit ZZ terms to the NetworkX edges.
    feature_entanglement = {
        1: [(qubit,) for qubit in range(4)],
        2: graph_edges,
    }
    feature_map = zz_feature_map(
        feature_dimension=4,
        reps=selected.feature_reps,
        entanglement=feature_entanglement,
    )
    ansatz = real_amplitudes(
        num_qubits=4,
        reps=selected.ansatz_reps,
        entanglement=ansatz_entanglement,
    )
    circuit = QuantumCircuit(4, name="quantum_graph_sampler_qnn")
    circuit.compose(feature_map, inplace=True)
    circuit.compose(ansatz, inplace=True)
    circuit.metadata = {
        "experiment": "quantum_graph_canon_v1",
        "role": "topology_preserving_sampler_qnn",
        "graph_edges": [list(edge) for edge in graph_edges],
    }
    input_parameters = tuple(feature_map.parameters)
    weight_parameters = tuple(ansatz.parameters)
    network = SamplerQNN(
        circuit=circuit,
        sampler=StatevectorSampler(
            default_shots=selected.shots,
            seed=selected.sampler_seed,
        ),
        input_params=input_parameters,
        weight_params=weight_parameters,
    )
    return QuantumGraphSamplerQNN(
        config=selected,
        graph_edges=graph_edges,
        circuit=circuit,
        network=network,
        input_parameters=input_parameters,
        weight_parameters=weight_parameters,
    )


def graph_qnn_input_vector(
    encoded_graph: nx.Graph,
    mapping: str = "hybrid",
) -> tuple[float, ...]:
    """Compress each quotient region to one bounded feature-map angle."""
    _validate_encoded_graph(encoded_graph)
    if mapping not in {"hybrid", "eigenfield"}:
        raise ValueError("mapping must be 'hybrid' or 'eigenfield'")
    values = []
    for qubit in range(4):
        data = encoded_graph.nodes[qubit]
        field = float(data["field_unit"])
        if mapping == "eigenfield":
            unit_value = field
        else:
            onset = float(data["onset_unit"])
            pitch = float((data["pitch_space_mean"] % 12.0) / 12.0)
            position = float((data["position_phase"] + math.pi) / math.tau)
            unit_value = 0.40 * field + 0.25 * onset + 0.20 * pitch + 0.15 * position
        values.append(math.pi * float(np.clip(unit_value, 0.0, 1.0)))
    return tuple(values)


def seeded_untrained_weights(
    model: QuantumGraphSamplerQNN,
) -> tuple[float, ...]:
    """Return a reproducible small random initialization, not learned weights."""
    generator = np.random.default_rng(model.config.weight_seed)
    weights = generator.uniform(
        -model.config.untrained_weight_scale,
        model.config.untrained_weight_scale,
        len(model.weight_parameters),
    )
    return tuple(float(value) for value in weights)


def run_graph_sampler_qnn(
    model: QuantumGraphSamplerQNN,
    encoded_graph: nx.Graph,
    weights: Sequence[float] | None = None,
    weight_provenance: str | None = None,
) -> QuantumGraphQNNResult:
    """Run the QNN and derive little-endian activation marginals for four regions."""
    input_data = graph_qnn_input_vector(
        encoded_graph,
        mapping=model.config.input_mapping,
    )
    if weights is None:
        selected_weights = seeded_untrained_weights(model)
        provenance = weight_provenance or "seeded_untrained"
    else:
        selected_weights = tuple(float(value) for value in weights)
        provenance = weight_provenance or "external_unspecified"
    if len(selected_weights) != len(model.weight_parameters):
        raise ValueError(
            f"weights must contain {len(model.weight_parameters)} values, "
            f"received {len(selected_weights)}"
        )
    if any(not math.isfinite(value) for value in selected_weights):
        raise ValueError("weights must all be finite")

    raw = np.asarray(
        model.network.forward(
            input_data=np.asarray(input_data, dtype=float),
            weights=np.asarray(selected_weights, dtype=float),
        ),
        dtype=float,
    ).reshape(-1)
    if raw.shape != (16,):
        raise RuntimeError(f"SamplerQNN returned unexpected output shape {raw.shape}")
    probabilities = np.clip(raw, 0.0, None)
    probability_sum = float(np.sum(probabilities))
    if probability_sum <= 0.0:
        raise RuntimeError("SamplerQNN returned no probability mass")
    probabilities /= probability_sum
    selected_mask = int(np.argmax(probabilities))
    activation_marginals = tuple(
        float(
            sum(
                probabilities[mask]
                for mask in range(16)
                if (mask >> qubit) & 1
            )
        )
        for qubit in range(4)
    )
    nonzero = probabilities[probabilities > 1e-15]
    entropy = float(-np.sum(nonzero * np.log2(nonzero)))
    return QuantumGraphQNNResult(
        input_data=input_data,
        weights=selected_weights,
        weight_provenance=provenance,
        probabilities=tuple(float(value) for value in probabilities),
        activation_marginals=activation_marginals,
        selected_mask=selected_mask,
        selected_region_bits=tuple((selected_mask >> qubit) & 1 for qubit in range(4)),
        distribution_entropy_bits=entropy,
    )


def condition_graph_with_qnn(
    encoded_graph: nx.Graph,
    result: QuantumGraphQNNResult,
    activation_floor: float = 0.20,
) -> nx.Graph:
    """Scale local rotations and graph-edge interactions by QNN marginals."""
    _validate_encoded_graph(encoded_graph)
    if not math.isfinite(activation_floor) or not 0.0 <= activation_floor <= 1.0:
        raise ValueError("activation_floor must lie in [0, 1]")
    if len(result.activation_marginals) != 4:
        raise ValueError("QNN result must contain four activation marginals")

    conditioned = encoded_graph.copy()
    effective_activations = []
    for qubit, marginal in enumerate(result.activation_marginals):
        activation = activation_floor + (1.0 - activation_floor) * marginal
        effective_activations.append(activation)
        data = conditioned.nodes[qubit]
        data["qnn_activation_marginal"] = marginal
        data["qnn_effective_activation"] = activation
        for rotation in ("rotation_x", "rotation_y", "rotation_z"):
            original_key = f"pre_qnn_{rotation}"
            original = float(data.get(original_key, data[rotation]))
            data[original_key] = original
            data[rotation] = original * activation

    for start, end, data in conditioned.edges(data=True):
        edge_activation = math.sqrt(
            effective_activations[start] * effective_activations[end]
        )
        original = float(data.get("pre_qnn_entangling_angle", data["entangling_angle"]))
        data.update(
            pre_qnn_entangling_angle=original,
            qnn_edge_activation=edge_activation,
            entangling_angle=original * edge_activation,
        )
    conditioned.graph.update(
        qnn_conditioned=True,
        qnn_output_mode="16_region_activation_masks",
        qnn_weight_provenance=result.weight_provenance,
        qnn_selected_mask=result.selected_mask,
        qnn_selected_region_bits=result.selected_region_bits,
        qnn_activation_marginals=result.activation_marginals,
        qnn_activation_floor=float(activation_floor),
    )
    return conditioned


def build_qnn_conditioned_experiment(
    canon_config: QuantumGraphCanonConfig | None = None,
    qnn_config: QuantumGraphQNNConfig | None = None,
    weights: Sequence[float] | None = None,
    weight_provenance: str | None = None,
) -> QuantumGraphQNNExperiment:
    """Run the full QNN-conditioned graph-to-MusicXML experiment in memory."""
    selected_canon = canon_config or QuantumGraphCanonConfig()
    selected_qnn = qnn_config or QuantumGraphQNNConfig()
    source = build_default_source_graph()
    quotient = build_four_region_quotient_graph(
        source,
        selected_canon.partition_seed,
    )
    encoded = encode_quotient_graph(
        quotient,
        selected_canon.entanglement_scale,
    )
    model = build_topology_preserving_sampler_qnn(encoded, selected_qnn)
    result = run_graph_sampler_qnn(
        model,
        encoded,
        weights=weights,
        weight_provenance=weight_provenance,
    )
    conditioned = condition_graph_with_qnn(
        encoded,
        result,
        selected_qnn.activation_floor,
    )
    densities, circuits = build_graph_conditioned_density_snapshots(
        conditioned,
        selected_canon,
    )
    canon = build_density_matrix_cable_net_canon(
        build_tensile_saddle_mesh(),
        densities,
        coherence_threshold=selected_canon.coherence_threshold,
        slot_ticks=selected_canon.slot_ticks,
        snapshot_gap_ticks=selected_canon.snapshot_gap_ticks,
    )
    canon.graph.update(
        quantum_graph_canon_version=1,
        source_graph=source.graph.get("experiment_source"),
        quotient_method=conditioned.graph["partition_method"],
        circuit_mode="qnn_conditioned_entangled",
        circuit_layers=selected_canon.layers,
        density_provenance="exact_statevector_plus_explicit_dephasing",
        explicit_dephasing=selected_canon.dephasing,
        qnn_conditioned=True,
        qnn_weight_provenance=result.weight_provenance,
        qnn_selected_mask=result.selected_mask,
        qnn_activation_marginals=result.activation_marginals,
    )
    canon_experiment = QuantumGraphCanonExperiment(
        config=selected_canon,
        source_graph=source,
        quotient_graph=conditioned,
        circuits=circuits,
        density_snapshots=densities,
        canon_graph=canon,
    )
    return QuantumGraphQNNExperiment(
        canon_experiment=canon_experiment,
        qnn_model=model,
        qnn_result=result,
    )


def build_qnn_conditioned_score(experiment: QuantumGraphQNNExperiment):
    """Render a QNN-conditioned experiment as a 32-part score."""
    status = (
        "Untrained Seed"
        if experiment.qnn_result.weight_provenance == "seeded_untrained"
        else "External Weights"
    )
    return build_quantum_graph_canon_score(
        experiment.canon_experiment,
        title=f"Quartic-Torus Quantum Graph Canon No. 15 — QNN {status}",
    )


def qnn_experiment_manifest(
    experiment: QuantumGraphQNNExperiment,
) -> dict[str, Any]:
    """Extend the base research manifest with complete QNN provenance."""
    manifest = experiment_manifest(experiment.canon_experiment)
    model = experiment.qnn_model
    result = experiment.qnn_result
    top_outcomes = sorted(
        enumerate(result.probabilities),
        key=lambda item: (-item[1], item[0]),
    )[:8]
    manifest["experiment"] = "Quantum Graph Canon v1 — SamplerQNN-conditioned"
    manifest["provenance"].update(
        qnn_sampler="Qiskit StatevectorSampler with finite shots",
        qnn_training_status=(
            "untrained" if result.weight_provenance == "seeded_untrained" else "unspecified"
        ),
    )
    manifest["qnn"] = {
        "config": asdict(model.config),
        "topology_edges": [list(edge) for edge in model.graph_edges],
        "input_parameter_count": len(model.input_parameters),
        "weight_parameter_count": len(model.weight_parameters),
        "input_data": list(result.input_data),
        "weights": list(result.weights),
        "weight_provenance": result.weight_provenance,
        "output_semantics": "integer masks 0..15; bit q activates quotient region q",
        "probabilities": list(result.probabilities),
        "distribution_entropy_bits": result.distribution_entropy_bits,
        "selected_mask": result.selected_mask,
        "selected_bitstring_q3_to_q0": f"{result.selected_mask:04b}",
        "selected_region_bits_q0_to_q3": list(result.selected_region_bits),
        "activation_marginals_q0_to_q3": list(result.activation_marginals),
        "top_outcomes": [
            {
                "mask": mask,
                "bitstring_q3_to_q0": f"{mask:04b}",
                "probability": probability,
            }
            for mask, probability in top_outcomes
        ],
        "circuit": {
            "depth": model.circuit.depth(),
            "operation_counts": {
                str(name): int(count)
                for name, count in model.circuit.count_ops().items()
            },
        },
    }
    return manifest


def _validate_encoded_graph(encoded_graph: nx.Graph) -> None:
    if encoded_graph.is_directed():
        raise ValueError("encoded_graph must be undirected")
    if set(encoded_graph.nodes) != {0, 1, 2, 3}:
        raise ValueError("encoded_graph nodes must be qubit ids 0 through 3")
    required = {
        "field_unit",
        "onset_unit",
        "pitch_space_mean",
        "position_phase",
        "rotation_x",
        "rotation_y",
        "rotation_z",
    }
    for node_id in range(4):
        if not required <= encoded_graph.nodes[node_id].keys():
            raise ValueError(f"encoded graph node {node_id} lacks QNN features")
