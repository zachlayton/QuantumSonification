from __future__ import annotations

import json
import unittest
from pathlib import Path

import numpy as np

from qmw_representation_laboratory_v4.core import density_from_preset
from qmw_representation_laboratory_v5.osc_service import (
    RepresentationLiveConfig,
    RepresentationTransformFactory,
    RepresentationV5OSCService,
    TRANSFORM_NAMES,
)

ROOT = Path(__file__).resolve().parents[1]
MAX = ROOT / "max"
CONTROL = MAX / "QMW_Transform_Control_v5.maxpat"
LABORATORY = MAX / "QMW_Representation_Laboratory_v5.maxpat"


def boxes(path: Path) -> list[dict]:
    document = json.loads(path.read_text(encoding="utf-8"))
    return [item["box"] for item in document["patcher"]["boxes"]]


class IntegratedV5ArtifactTests(unittest.TestCase):
    def test_control_is_presentation_ready_and_persistent(self) -> None:
        document = json.loads(CONTROL.read_text(encoding="utf-8"))
        self.assertEqual(document["patcher"]["openinpresentation"], 1)
        values = boxes(CONTROL)
        texts = {item.get("text", "") for item in values}
        varnames = {item.get("varname", "") for item in values}
        self.assertIn(
            "pattrstorage qmw_v5_transform_presets @autorestore 0",
            texts,
        )
        self.assertIn("o.pack /qmw/v5/transform/preview", texts)
        self.assertIn("o.pack /qmw/v5/transform/commit", texts)
        self.assertNotIn("loadmess hamiltonian", texts)
        self.assertNotIn("loadmess open", texts)
        self.assertNotIn("loadmess ghz", texts)
        self.assertNotIn("loadmess fixed", texts)
        self.assertNotIn("loadmess cycle", texts)
        self.assertIn("loadmess 4", texts)
        self.assertTrue(
            {
                "hamiltonian_j",
                "hamiltonian_ht",
                "hamiltonian_hl",
                "hamiltonian_time",
                "representation_transform",
                "hamiltonian_boundary",
                "hamiltonian_preset",
                "hamiltonian_shots",
                "hamiltonian_sampling",
                "hamiltonian_seed",
                "representation_graph",
                "representation_normalized_graph",
                "representation_marked_state",
                "representation_steps",
            }.issubset(varnames)
        )

    def test_parent_embeds_control_and_removes_v3_launchers(self) -> None:
        document = json.loads(LABORATORY.read_text(encoding="utf-8"))
        values = boxes(LABORATORY)
        texts = {item.get("text", "") for item in values}
        bpatchers = [
            item for item in values if item["maxclass"] == "bpatcher"
        ]
        self.assertEqual(len(bpatchers), 1)
        self.assertEqual(
            bpatchers[0]["name"],
            "QMW_Transform_Control_v5.maxpat",
        )
        self.assertEqual(bpatchers[0]["embed"], 1)
        self.assertIn("patcher", bpatchers[0])
        embedded_varnames = {
            item["box"].get("varname", "")
            for item in bpatchers[0]["patcher"]["boxes"]
        }
        self.assertIn("representation_transform", embedded_varnames)
        self.assertNotIn("o.pack /qmw/basis/run", texts)
        self.assertNotIn("udpsend 127.0.0.1 7435", texts)
        self.assertIn("udpreceive 7436", texts)
        self.assertEqual(
            sum(item["maxclass"] == "jit.pwindow" for item in values),
            2,
        )
        dependencies = {
            item["name"] for item in document["patcher"]["dependency_cache"]
        }
        self.assertIn(
            "QMW_Transform_Control_v5.maxpat",
            dependencies,
        )


class RegistryDrivenServiceTests(unittest.TestCase):
    def test_every_registered_transform_builds_for_full4q(self) -> None:
        factory = RepresentationTransformFactory()
        rho = density_from_preset("ghz")
        expected = {
            "identity",
            "hadamard",
            "qft",
            "inverse_qft",
            "hamiltonian",
            "graph_laplacian",
            "floquet",
            "grover_amplified",
            "epistrophe",
        }
        self.assertEqual(set(TRANSFORM_NAMES), expected)
        for name in TRANSFORM_NAMES:
            with self.subTest(transform=name):
                transform, spectrum, kind, _tracking = factory.build(
                    RepresentationLiveConfig(transform=name)
                )
                transformed = transform.apply(rho)
                self.assertEqual(transformed.shape, (16, 16))
                self.assertEqual(len(spectrum), 16)
                self.assertIn(
                    kind,
                    {"energy", "graph_laplacian", "unitary_phase"},
                )
                self.assertAlmostEqual(
                    float(np.trace(transformed).real),
                    1.0,
                    places=9,
                )

    def test_atomic_max_bundle_selects_transform_and_parameters(self) -> None:
        service = RepresentationV5OSCService.__new__(
            RepresentationV5OSCService
        )
        service.config = RepresentationLiveConfig()
        service._revision = 1
        revision, config = service._parse(
            (
                77,
                "grover_amplified",
                0.9,
                0.6,
                -0.1,
                2.0,
                "periodic",
                "weave",
                128,
                "resample",
                41,
                "path",
                1,
                7,
                3,
            )
        )
        self.assertEqual(revision, 77)
        self.assertEqual(config.transform, "grover_amplified")
        self.assertEqual(config.marked_state, 7)
        self.assertEqual(config.steps, 3)
        self.assertTrue(config.normalized_graph)


if __name__ == "__main__":
    unittest.main()
