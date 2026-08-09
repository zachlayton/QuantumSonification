from __future__ import annotations

from collections import Counter
import unittest

import networkx as nx
from music21 import converter, note

from procedural_notation_v1.generate_voronoi_map_canon_score import main as generate_score
from procedural_notation_v1.voronoi_map_canon import build_voronoi_adjacency_canon
from procedural_notation_v1.voronoi_map_graph import build_centroidal_voronoi_map


class CentroidalVoronoiMapTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.map = build_centroidal_voronoi_map()
        cls.canon = build_voronoi_adjacency_canon(cls.map)

    def test_map_has_twelve_connected_nearly_regular_regions(self) -> None:
        self.assertEqual(self.map.number_of_nodes(), 12)
        self.assertTrue(nx.is_connected(self.map))
        self.assertTrue(nx.check_planarity(self.map)[0])
        self.assertEqual(
            sum(data["grid_area"] for _, data in self.map.nodes(data=True)),
            24 * 24,
        )
        areas = [data["grid_area"] for _, data in self.map.nodes(data=True)]
        self.assertLess(max(areas) / min(areas), 1.8)
        self.assertTrue(
            all(data["shared_boundary"] > 0.0 for _, _, data in self.map.edges(data=True))
        )

    def test_each_voice_orbits_one_region_and_its_actual_neighbors(self) -> None:
        voice_counts = Counter(data["voice"] for _, data in self.canon.nodes(data=True))

        self.assertEqual(len(voice_counts), 12)
        self.assertGreater(max(voice_counts.values()), min(voice_counts.values()))
        for _, data in self.canon.nodes(data=True):
            self.assertTrue(
                data["visited_region"] == data["home_region"]
                or self.map.has_edge(data["home_region"], data["visited_region"])
            )

    def test_area_boundary_and_distance_have_separate_musical_roles(self) -> None:
        data = [item for _, item in self.canon.nodes(data=True)]

        self.assertEqual({item["repetition_count"] for item in data}, {1, 2, 3})
        self.assertEqual({item["rest_after_ticks"] for item in data}, {0, 1})
        self.assertGreater(max(item["distance_from_home"] for item in data), 0.0)
        self.assertEqual(
            {item["transposition_semitones"] for item in data},
            {0, 2, 4, 7, 9},
        )

    def test_musicxml_contains_twelve_variable_region_parts(self) -> None:
        score = converter.parse(generate_score())

        self.assertEqual(len(score.parts), 12)
        attack_counts = [
            len(part.recurse().getElementsByClass(note.Note)) for part in score.parts
        ]
        self.assertGreater(max(attack_counts), min(attack_counts))
        self.assertTrue(all(count > 0 for count in attack_counts))


if __name__ == "__main__":
    unittest.main()
