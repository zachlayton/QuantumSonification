from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from music21 import converter
import numpy as np

from procedural_notation_v1 import write_musicxml
from quantum_graph_canon_v1.core import (
    QuantumGraphCanonConfig,
    build_default_source_graph,
    build_four_region_quotient_graph,
    encode_quotient_graph,
)
from quantum_graph_canon_v1.qnn import (
    QuantumGraphQNNConfig,
    build_qnn_conditioned_experiment,
    build_qnn_conditioned_score,
    build_topology_preserving_sampler_qnn,
    condition_graph_with_qnn,
    graph_qnn_input_vector,
    qnn_experiment_manifest,
    run_graph_sampler_qnn,
)


class QuantumGraphQNNIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        source = build_default_source_graph()
        quotient = build_four_region_quotient_graph(source)
        cls.encoded = encode_quotient_graph(quotient)
        cls.qnn_config = QuantumGraphQNNConfig(shots=4096)
        cls.model = build_topology_preserving_sampler_qnn(
            cls.encoded,
            cls.qnn_config,
        )
        cls.result = run_graph_sampler_qnn(cls.model, cls.encoded)
        cls.experiment = build_qnn_conditioned_experiment(
            QuantumGraphCanonConfig(),
            cls.qnn_config,
        )

    def test_qnn_topology_matches_networkx_quotient(self) -> None:
        expected_edges = tuple(sorted(self.encoded.edges))
        self.assertEqual(self.model.graph_edges, expected_edges)
        self.assertEqual(len(self.model.input_parameters), 4)
        self.assertEqual(len(self.model.weight_parameters), 12)
        self.assertEqual(self.model.circuit.num_qubits, 4)

    def test_hybrid_input_contains_one_bounded_angle_per_region(self) -> None:
        inputs = graph_qnn_input_vector(self.encoded, mapping="hybrid")
        eigenfield_inputs = graph_qnn_input_vector(
            self.encoded,
            mapping="eigenfield",
        )
        self.assertEqual(len(inputs), 4)
        self.assertTrue(all(0.0 <= value <= np.pi for value in inputs))
        self.assertNotEqual(inputs, eigenfield_inputs)

    def test_forward_pass_is_normalized_and_reproducible(self) -> None:
        repeated_model = build_topology_preserving_sampler_qnn(
            self.encoded,
            self.qnn_config,
        )
        repeated = run_graph_sampler_qnn(repeated_model, self.encoded)
        self.assertEqual(len(self.result.probabilities), 16)
        self.assertTrue(np.isclose(sum(self.result.probabilities), 1.0))
        self.assertTrue(
            all(0.0 <= value <= 1.0 for value in self.result.activation_marginals)
        )
        self.assertTrue(
            np.allclose(self.result.probabilities, repeated.probabilities)
        )
        self.assertEqual(self.result.selected_mask, repeated.selected_mask)
        self.assertEqual(self.result.weight_provenance, "seeded_untrained")

    def test_qnn_conditioning_scales_rotations_without_mutating_source(self) -> None:
        original_rotation = self.encoded.nodes[0]["rotation_y"]
        conditioned = condition_graph_with_qnn(
            self.encoded,
            self.result,
            activation_floor=self.qnn_config.activation_floor,
        )
        self.assertEqual(self.encoded.nodes[0]["rotation_y"], original_rotation)
        self.assertTrue(conditioned.graph["qnn_conditioned"])
        self.assertLessEqual(
            conditioned.nodes[0]["rotation_y"],
            original_rotation,
        )
        self.assertEqual(
            conditioned.nodes[0]["pre_qnn_rotation_y"],
            original_rotation,
        )
        for _, _, data in conditioned.edges(data=True):
            self.assertLessEqual(
                data["entangling_angle"],
                data["pre_qnn_entangling_angle"],
            )

    def test_external_weights_are_validated_and_labeled(self) -> None:
        with self.assertRaises(ValueError):
            run_graph_sampler_qnn(self.model, self.encoded, weights=[0.0])
        weights = [0.0] * len(self.model.weight_parameters)
        result = run_graph_sampler_qnn(
            build_topology_preserving_sampler_qnn(
                self.encoded,
                self.qnn_config,
            ),
            self.encoded,
            weights=weights,
            weight_provenance="unit_test_weights.json",
        )
        self.assertEqual(result.weight_provenance, "unit_test_weights.json")

    def test_full_experiment_records_qnn_provenance(self) -> None:
        canon = self.experiment.canon_experiment.canon_graph
        manifest = qnn_experiment_manifest(self.experiment)
        self.assertEqual(canon.graph["voice_count"], 32)
        self.assertTrue(canon.graph["qnn_conditioned"])
        self.assertEqual(manifest["provenance"]["qnn_training_status"], "untrained")
        self.assertEqual(len(manifest["qnn"]["probabilities"]), 16)
        self.assertEqual(len(manifest["qnn"]["activation_marginals_q0_to_q3"]), 4)
        self.assertEqual(
            manifest["qnn"]["topology_edges"],
            [list(edge) for edge in self.model.graph_edges],
        )

    def test_qnn_musicxml_contains_32_parts(self) -> None:
        score = build_qnn_conditioned_score(self.experiment)
        with tempfile.TemporaryDirectory() as directory:
            path = write_musicxml(score, Path(directory) / "qnn_canon.musicxml")
            parsed = converter.parse(path)
        self.assertEqual(len(parsed.parts), 32)

    def test_qnn_configuration_rejects_invalid_values(self) -> None:
        with self.assertRaises(ValueError):
            QuantumGraphQNNConfig(shots=0)
        with self.assertRaises(ValueError):
            QuantumGraphQNNConfig(input_mapping="unknown")
        with self.assertRaises(ValueError):
            QuantumGraphQNNConfig(activation_floor=1.1)


if __name__ == "__main__":
    unittest.main()
