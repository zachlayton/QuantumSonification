"""Structural checks for the realtime Wilson Tetradic Diamond view."""

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SKETCH = ROOT / "processing/QMW_Wilson_Hexany_Flow_v1/QMW_Wilson_Hexany_Flow_v1.pde"


class TetradicDiamondTests(unittest.TestCase):
    def test_ordered_ratio_graph_is_a_cuboctahedron(self):
        vertices = [(numerator, denominator) for numerator in range(4)
                    for denominator in range(4) if numerator != denominator]
        self.assertEqual(len(vertices), 12)

        edges = {
            frozenset((left, right))
            for left in vertices
            for right in vertices
            if left < right and (left[0] == right[0] or left[1] == right[1])
        }
        self.assertEqual(len(edges), 24)
        for vertex in vertices:
            self.assertEqual(sum(vertex in edge for edge in edges), 4)

    def test_reciprocals_have_opposite_difference_coordinates(self):
        tetrahedron = ((1, 1, 1), (1, -1, -1), (-1, 1, -1), (-1, -1, 1))

        def position(numerator, denominator):
            return tuple((tetrahedron[numerator][axis] - tetrahedron[denominator][axis]) / 2
                         for axis in range(3))

        for numerator in range(4):
            for denominator in range(4):
                if numerator == denominator:
                    continue
                point = position(numerator, denominator)
                reciprocal = position(denominator, numerator)
                self.assertEqual(point, tuple(-coordinate for coordinate in reciprocal))

    def test_sketch_contains_live_view_controls_and_quantum_mapping(self):
        source = SKETCH.read_text()
        for token in (
            "VIEW_DIAMOND",
            "initializeDiamondGeometry()",
            "updateDiamondQuantumField()",
            "drawDiamondVertices()",
            "foldedDiamondRatio",
            "key == 'd'",
            "key == 'h'",
        ):
            self.assertIn(token, source)


if __name__ == "__main__":
    unittest.main()
