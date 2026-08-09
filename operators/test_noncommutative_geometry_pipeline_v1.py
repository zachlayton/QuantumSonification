from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

import numpy as np

if __package__:
    from .algebraic_surface_pipeline_v1 import (
        AlgebraicSurfaceConfig,
        marching_tetrahedra,
    )
else:  # Direct-test compatibility.
    from algebraic_surface_pipeline_v1 import (
        AlgebraicSurfaceConfig,
        marching_tetrahedra,
    )
from noncommutative_geometry import (
    OperatorOrderConfig,
    apply_operator,
    deformation_generators,
    experiment_operators,
    reserve_output_fork,
)


class NoncommutativeGeometryPipelineTests(unittest.TestCase):
    def test_existing_output_is_preserved_by_revisioned_forks(self) -> None:
        with TemporaryDirectory() as temporary_directory:
            base = Path(temporary_directory) / "operator_order_v1"
            first, first_metadata = reserve_output_fork(base)
            marker = first / "previous_work.txt"
            marker.write_text("keep me", encoding="utf-8")

            second, second_metadata = reserve_output_fork(base)
            (second / "second_work.txt").write_text("second", encoding="utf-8")
            third, third_metadata = reserve_output_fork(base)

            self.assertEqual(first, base.resolve())
            self.assertEqual(first_metadata["fork_index"], 1)
            self.assertEqual(second.name, "operator_order_v1_fork_000002")
            self.assertEqual(second_metadata["fork_index"], 2)
            self.assertEqual(third.name, "operator_order_v1_fork_000003")
            self.assertEqual(third_metadata["fork_index"], 3)
            self.assertEqual(marker.read_text(encoding="utf-8"), "keep me")

    def test_generators_and_ordered_maps_are_noncommutative(self) -> None:
        generator_a, generator_b = deformation_generators()
        commutator = generator_a @ generator_b - generator_b @ generator_a
        self.assertGreater(float(np.linalg.norm(commutator)), 1.0e-3)
        operators = experiment_operators(OperatorOrderConfig())
        self.assertFalse(
            np.allclose(operators["A_then_B"], operators["B_then_A"])
        )
        for operator in operators.values():
            self.assertAlmostEqual(float(np.linalg.det(operator)), 1.0, places=10)

    def test_order_changes_geometry_without_changing_topology(self) -> None:
        vertices, faces = marching_tetrahedra(
            AlgebraicSurfaceConfig(resolution=14, radius_m=0.25)
        )
        operators = experiment_operators(OperatorOrderConfig())
        ab = apply_operator(vertices, operators["A_then_B"], 0.25)
        ba = apply_operator(vertices, operators["B_then_A"], 0.25)
        self.assertEqual(ab.shape, ba.shape)
        self.assertGreater(len(faces), 0)
        self.assertGreater(float(np.sqrt(np.mean((ab - ba) ** 2))), 1.0e-5)
        self.assertAlmostEqual(float(np.max(np.linalg.norm(ab, axis=1))), 0.25)
        self.assertAlmostEqual(float(np.max(np.linalg.norm(ba, axis=1))), 0.25)


if __name__ == "__main__":
    unittest.main()
