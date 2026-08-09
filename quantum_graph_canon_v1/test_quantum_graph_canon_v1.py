from __future__ import annotations

from dataclasses import replace
from pathlib import Path
import tempfile
import unittest

from music21 import converter
import networkx as nx
import numpy as np

from procedural_notation_v1 import write_musicxml
from quantum_graph_canon_v1.core import (
    QuantumGraphCanonConfig,
    build_default_experiment,
    build_default_source_graph,
    build_four_region_quotient_graph,
    build_quantum_graph_canon_score,
    experiment_manifest,
)


class QuantumGraphCanonV1Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.base_config = QuantumGraphCanonConfig()
        cls.source = build_default_source_graph()
        cls.entangled = build_default_experiment(cls.base_config)
        cls.local = build_default_experiment(
            replace(cls.base_config, entangled=False)
        )

    def test_four_region_quotient_is_complete_partition_and_connected(self) -> None:
        quotient = build_four_region_quotient_graph(
            self.source,
            self.base_config.partition_seed,
        )
        members = [
            member
            for _, data in quotient.nodes(data=True)
            for member in data["source_members"]
        ]
        self.assertEqual(quotient.number_of_nodes(), 4)
        self.assertEqual(set(members), set(self.source.nodes))
        self.assertEqual(len(members), len(set(members)))
        self.assertTrue(nx.is_connected(quotient))
        self.assertGreater(quotient.number_of_edges(), 0)

    def test_density_snapshots_are_valid_reproducible_and_evolving(self) -> None:
        repeated = build_default_experiment(self.base_config)
        self.assertEqual(len(self.entangled.density_snapshots), 4)
        for first, second in zip(
            self.entangled.density_snapshots,
            repeated.density_snapshots,
            strict=True,
        ):
            self.assertEqual(first.shape, (16, 16))
            self.assertTrue(np.allclose(first, first.conj().T))
            self.assertTrue(np.isclose(np.trace(first), 1.0))
            self.assertGreaterEqual(float(np.min(np.linalg.eigvalsh(first))), -1e-10)
            self.assertTrue(np.allclose(first, second))
        self.assertFalse(
            np.allclose(
                self.entangled.density_snapshots[0],
                self.entangled.density_snapshots[-1],
            )
        )

    def test_entangled_circuit_differs_from_local_control(self) -> None:
        self.assertGreater(
            self.entangled.circuits[-1].count_ops().get("rzz", 0),
            0,
        )
        self.assertEqual(self.local.circuits[-1].count_ops().get("rzz", 0), 0)
        self.assertFalse(
            np.allclose(
                self.entangled.density_snapshots[-1],
                self.local.density_snapshots[-1],
            )
        )
        self.assertNotEqual(
            self.entangled.canon_graph.graph["sounding_matrix_events"],
            self.local.canon_graph.graph["sounding_matrix_events"],
        )

    def test_manifest_names_simulator_provenance_and_comparison_metrics(self) -> None:
        manifest = experiment_manifest(self.entangled)
        self.assertFalse(manifest["provenance"]["hardware_measurement"])
        self.assertEqual(len(manifest["quotient_graph"]["nodes"]), 4)
        self.assertEqual(len(manifest["snapshots"]), 4)
        self.assertTrue(
            all(snapshot["operation_counts"]["rzz"] > 0 for snapshot in manifest["snapshots"])
        )

    def test_musicxml_contains_32_quantum_graph_parts(self) -> None:
        score = build_quantum_graph_canon_score(self.entangled)
        with tempfile.TemporaryDirectory() as directory:
            path = write_musicxml(score, Path(directory) / "quantum_graph_canon.musicxml")
            parsed = converter.parse(path)
        self.assertEqual(len(parsed.parts), 32)
        self.assertTrue(all(part.partName.startswith("QGC ") for part in parsed.parts))

    def test_configuration_rejects_invalid_values(self) -> None:
        with self.assertRaises(ValueError):
            QuantumGraphCanonConfig(layers=0)
        with self.assertRaises(ValueError):
            QuantumGraphCanonConfig(dephasing=1.1)
        with self.assertRaises(ValueError):
            QuantumGraphCanonConfig(entanglement_scale=-0.1)


if __name__ == "__main__":
    unittest.main()
