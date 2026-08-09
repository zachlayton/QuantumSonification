from __future__ import annotations

from collections import Counter, defaultdict
import contextlib
import io
import unittest

from music21 import converter, note

from procedural_notation_v1.generate_quartic_torus_canon_score import (
    main as generate_score,
)
from procedural_notation_v1.surface_mesh_graph import build_quartic_torus_mesh
from procedural_notation_v1.surface_mesh_motion import build_torus_32_voice_rotating_mesh


class Torus32VoiceMotionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.surface = build_quartic_torus_mesh(major_segments=16, minor_segments=16)
        cls.motion = build_torus_32_voice_rotating_mesh(cls.surface, rotations=4)

    def test_motion_preserves_32_complete_coordinate_voices(self) -> None:
        voice_counts = Counter(data["voice"] for _, data in self.motion.nodes(data=True))

        self.assertEqual(len(voice_counts), 32)
        self.assertEqual(set(voice_counts.values()), {64})
        self.assertEqual(self.motion.number_of_nodes(), 2048)
        self.assertEqual(
            Counter(data["voice_family"] for _, data in self.motion.nodes(data=True)),
            {"ring": 1024, "meridian": 1024},
        )

    def test_rhythm_contains_offset_elongation_and_accumulated_displacement(self) -> None:
        data = [item for _, item in self.motion.nodes(data=True)]

        self.assertEqual({item["base_elongation_ticks"] for item in data}, {1, 2, 3})
        self.assertEqual({item["mensuration_factor"] for item in data}, {1, 2, 3})
        self.assertEqual({item["base_internal_rest_ticks"] for item in data}, {0, 1})
        self.assertEqual({item["canon_entry_index"] for item in data}, set(range(32)))
        self.assertEqual({item["initial_offset_ticks"] for item in data}, set(range(32)))
        self.assertEqual({item["rotation_direction"] for item in data}, {-1, 1})
        base_orbital_displacements = {
            item["base_orbital_displacement_after_ticks"]
            for item in data
            if "base_orbital_displacement_after_ticks" in item
        }
        self.assertEqual(base_orbital_displacements, {1, 2, 3, 4})

    def test_register_and_pitch_collection_change_with_each_orbit(self) -> None:
        voice_orbits = defaultdict(lambda: defaultdict(set))
        for _, data in self.motion.nodes(data=True):
            voice_orbits[data["voice"]][data["orbit_index"]].add(
                (data["pitch"], data["collection_rotation"], round(data["register_spin"], 4))
            )

        for orbits in voice_orbits.values():
            self.assertEqual(set(orbits), {0, 1, 2, 3})
            self.assertGreater(len({tuple(sorted(values)) for values in orbits.values()}), 1)

    def test_musicxml_contains_32_motion_parts(self) -> None:
        with contextlib.redirect_stderr(io.StringIO()):
            score = converter.parse(generate_score())

        self.assertEqual(len(score.parts), 32)
        self.assertEqual(
            {
                sum(
                    item.tie is None or item.tie.type == "start"
                    for item in part.recurse().getElementsByClass(note.Note)
                )
                for part in score.parts
            },
            {64},
        )
        self.assertGreater(len(score.parts[0].getElementsByClass("Measure")), 4)


if __name__ == "__main__":
    unittest.main()
