from pathlib import Path
import tempfile
import unittest

import numpy as np

from algebraic_surface_pipeline_v1 import (
    AlgebraicSurfaceConfig,
    generate_candidate,
    marching_tetrahedra,
)
from grasshopper_geometry_bridge_v1 import (
    GrasshopperMeshCandidate,
    MeshValidationPolicy,
)


class AlgebraicSurfacePipelineTests(unittest.TestCase):
    def test_tanglecube_is_closed_connected_manifold(self) -> None:
        config = AlgebraicSurfaceConfig(resolution=16, radius_m=0.2)
        vertices, faces = marching_tetrahedra(config)
        candidate = GrasshopperMeshCandidate(
            revision=1,
            vertices=vertices,
            faces=faces,
            source="test",
        )
        diagnostics = candidate.validate(
            MeshValidationPolicy(require_closed=True)
        )
        self.assertEqual(diagnostics.connected_components, 1)
        self.assertEqual(diagnostics.boundary_edge_count, 0)
        self.assertEqual(diagnostics.nonmanifold_edge_count, 0)
        self.assertTrue(
            np.isclose(np.max(np.linalg.norm(vertices, axis=1)), 0.2)
        )

    def test_candidate_and_obj_are_exported(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            candidate, paths = generate_candidate(
                AlgebraicSurfaceConfig(resolution=14, radius_m=0.1),
                Path(directory),
            )
            restored = GrasshopperMeshCandidate.load_json(
                paths["candidate_json"]
            )
            self.assertEqual(restored.geometry_hash, candidate.geometry_hash)
            self.assertTrue(
                paths["obj"].read_text(encoding="utf-8").startswith(
                    "# QMW procedural algebraic surface"
                )
            )
            self.assertTrue(paths["rhino_mm_obj"].exists())
            meter_vertex = candidate.vertices[0]
            rhino_vertex_line = next(
                line
                for line in paths["rhino_mm_obj"]
                .read_text(encoding="utf-8")
                .splitlines()
                if line.startswith("v ")
            )
            rhino_vertex = np.asarray(
                [float(value) for value in rhino_vertex_line.split()[1:]],
                dtype=np.float64,
            )
            np.testing.assert_allclose(rhino_vertex, meter_vertex * 1000.0)


if __name__ == "__main__":
    unittest.main()
