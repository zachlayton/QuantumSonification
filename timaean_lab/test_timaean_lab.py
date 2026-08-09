from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import numpy as np

from timaean_lab.timaean_lab import (
    cotangent_operators,
    density_states,
    laplacian_modes,
    make_icosphere,
    probability_field,
    run,
)


class TimaeanLabTests(unittest.TestCase):
    def test_icosphere_is_closed_and_unit_radius(self) -> None:
        mesh = make_icosphere(2)
        self.assertEqual(mesh.vertices.shape, (162, 3))
        self.assertEqual(mesh.faces.shape, (320, 3))
        np.testing.assert_allclose(np.linalg.norm(mesh.vertices, axis=1), 1.0)
        edges = np.sort(
            np.concatenate(
                (mesh.faces[:, (0, 1)], mesh.faces[:, (1, 2)], mesh.faces[:, (2, 0)])
            ),
            axis=1,
        )
        _, counts = np.unique(edges, axis=0, return_counts=True)
        self.assertTrue(np.all(counts == 2))

    def test_density_states_are_physical(self) -> None:
        for density in density_states(9).values():
            np.testing.assert_allclose(density, density.conjugate().T)
            self.assertAlmostEqual(float(np.trace(density).real), 1.0)
            self.assertGreaterEqual(float(np.linalg.eigvalsh(density).min()), -1e-12)

    def test_l4_states_preserve_populations_when_dephased(self) -> None:
        states = density_states(25)
        np.testing.assert_allclose(
            np.diag(states["coherent"]),
            np.diag(states["dephased"]),
        )
        self.assertGreater(float(np.sum(np.abs(states["coherent"] - states["dephased"]))), 0.0)

    def test_probability_fields_are_normalized(self) -> None:
        mesh = make_icosphere(1)
        laplacian, mass, areas = cotangent_operators(mesh)
        _, modes = laplacian_modes(laplacian, mass, 9)
        for density in density_states(9).values():
            field = probability_field(density, modes, areas)
            self.assertGreaterEqual(float(field.min()), -1e-12)
            self.assertAlmostEqual(float(np.dot(areas, field)), 1.0, places=10)

    def test_exports_and_preserves_existing_runs(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "operator_density_v1"
            first = run(output, subdivisions=1, mode_count=9)
            marker = Path(first["output_directory"]) / "keep.txt"
            marker.write_text("keep", encoding="utf-8")
            second = run(output, subdivisions=1, mode_count=9)
            self.assertEqual(second["fork"]["fork_index"], 2)
            self.assertTrue(marker.exists())
            for name in ("pure", "coherent", "dephased", "maximally_mixed"):
                self.assertTrue((output / f"{name}_rhino_mm.obj").exists())
                candidate = json.loads((output / f"{name}_candidate.json").read_text())
                self.assertEqual(candidate["schema"], "qmw.grasshopper_mesh_candidate")

    def test_l4_run_exports_coherence_only_form(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "l4_v2"
            manifest = run(
                output,
                subdivisions=2,
                mode_count=25,
                screening=8.0,
                max_displacement=0.5,
                preserve_existing=False,
                include_coherence_only=True,
            )
            derived = manifest["states"]["coherence_only"]
            self.assertTrue(derived["derived"])
            self.assertAlmostEqual(derived["max_abs_displacement"], 0.5)
            self.assertTrue((output / "coherence_only_rhino_mm.obj").exists())
            self.assertTrue((output / "coherence_only_candidate.json").exists())


if __name__ == "__main__":
    unittest.main()
