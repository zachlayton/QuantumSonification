"""Tests for sixteen-channel MIDI and MusicXML history-clock export."""

from __future__ import annotations

import struct
import unittest
import xml.etree.ElementTree as ET

import numpy as np

from qmw_entangled_history_clock16_v1 import prepare_floquet_history_state
from qmw_entangled_history_clock16_v1.ligeti_history_export import (
    LigetiClockConfig,
    build_ligeti_clock_score,
    midi_bytes,
    musicxml_bytes,
)
from qmw_temporal_crystal16_v1 import FloquetTimeCrystal16
from qmw_temporal_crystal16_v1.qmw_temporal_core16_v1 import (
    computational_basis_state,
)


class LigetiHistoryExportTests(unittest.TestCase):
    def setUp(self):
        self.model = FloquetTimeCrystal16()
        self.history = prepare_floquet_history_state(
            self.model,
            computational_basis_state(0),
        )
        self.config = LigetiClockConfig(hit_budget=12)

    def test_sixteen_channels_map_to_sixteen_clock_basis_states(self):
        score = build_ligeti_clock_score(self.history, self.config)
        self.assertEqual(len(score.voices), 16)
        self.assertEqual(score.report["midi_channels"], list(range(1, 17)))
        self.assertEqual(score.report["clock_basis_labels"][0], "|0000>")
        self.assertEqual(score.report["clock_basis_labels"][-1], "|1111>")
        np.testing.assert_allclose(
            score.report["clock_basis_probabilities"],
            np.full(16, 1.0 / 16.0),
            atol=1e-12,
        )

    def test_common_release_and_equal_winding_produce_staggered_endings(self):
        score = build_ligeti_clock_score(self.history, self.config)
        self.assertTrue(all(voice.onsets_ms[0] == 0 for voice in score.voices))
        self.assertTrue(all(
            voice.hit_budget == self.config.hit_budget for voice in score.voices
        ))
        endings = [voice.onsets_ms[-1] for voice in score.voices]
        self.assertTrue(all(
            right > left for left, right in zip(endings, endings[1:])
        ))

    def test_midi_is_type_one_with_conductor_plus_sixteen_tracks(self):
        data = midi_bytes(build_ligeti_clock_score(self.history, self.config))
        self.assertEqual(data[:4], b"MThd")
        length, format_kind, track_count, division = struct.unpack(
            ">IHHH", data[4:14]
        )
        self.assertEqual(length, 6)
        self.assertEqual(format_kind, 1)
        self.assertEqual(track_count, 17)
        self.assertEqual(division, 1000)
        for channel in range(16):
            self.assertIn(bytes([0x90 | channel]), data)

    def test_musicxml_has_sixteen_named_parts_and_millisecond_divisions(self):
        data = musicxml_bytes(build_ligeti_clock_score(self.history, self.config))
        root = ET.fromstring(data)
        parts = root.findall("part")
        names = [
            element.findtext("part-name")
            for element in root.findall("./part-list/score-part")
        ]
        self.assertEqual(len(parts), 16)
        self.assertEqual(names[0], "Clock |0000> (MIDI Ch 1)")
        self.assertEqual(names[-1], "Clock |1111> (MIDI Ch 16)")
        self.assertTrue(all(
            part.findtext("./measure/attributes/divisions") == "1000"
            for part in parts
        ))

    def test_global_phase_does_not_change_exports(self):
        phased = prepare_floquet_history_state(
            self.model,
            np.exp(0.49j) * computational_basis_state(0),
        )
        first = build_ligeti_clock_score(self.history, self.config)
        second = build_ligeti_clock_score(phased, self.config)
        self.assertEqual(midi_bytes(first), midi_bytes(second))
        self.assertEqual(musicxml_bytes(first), musicxml_bytes(second))


if __name__ == "__main__":
    unittest.main()
