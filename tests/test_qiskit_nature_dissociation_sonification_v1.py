import tempfile
import unittest
from pathlib import Path

import numpy as np

from qiskit_nature_molecular_v1.dissociation_sonification import (
    DissociationConfig,
    build_dense_dataset,
    export_study,
    relational_mapping_descriptor,
    render_relational_audio,
    extract_features,
    render_audio,
    render_uniform_downshift_audio,
    render_spectral_chamber_audio,
    chamber_mapping_descriptor,
    render_qmw_wavetable_wilson_audio,
    uniform_downshift_mapping,
)
from qiskit_nature_molecular_v1.h2_sweep import analyze_h2_point


class DissociationSonificationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.point = analyze_h2_point(0.735)
        cls.feature = extract_features(cls.point)

    def test_features_are_physical_and_unquantized(self):
        self.assertLessEqual(self.feature["correlation_energy_hartree"], 0.0)
        self.assertGreater(self.feature["natural_occupation_entropy_bits"], 0.0)
        self.assertNotIn("semitone", str(self.feature).lower())

    def test_short_render_is_stereo_finite_and_deterministic(self):
        dataset = build_dense_dataset(
            DissociationConfig(num_points=3, duration_seconds=0.1, sample_rate=8_000)
        )
        first = render_audio(dataset, "shaped")
        second = render_audio(dataset, "shaped")
        self.assertEqual(first.shape, (800, 2))
        self.assertTrue(np.all(np.isfinite(first)))
        np.testing.assert_array_equal(first, second)
        self.assertNotIn("semitone", str(dataset).lower())

    def test_export_writes_data_and_both_routes(self):
        dataset = build_dense_dataset(
            DissociationConfig(num_points=3, duration_seconds=0.1, sample_rate=8_000)
        )
        with tempfile.TemporaryDirectory() as directory:
            paths = export_study(dataset, Path(directory))
            self.assertEqual(set(paths), {"descriptor", "data", "raw_wav", "shaped_wav"})
            self.assertTrue(all(path.stat().st_size > 0 for path in paths.values()))

    def test_relational_route_has_fixed_pitch_and_state_derived_timing(self):
        dataset = build_dense_dataset(
            DissociationConfig(num_points=3, duration_seconds=0.1, sample_rate=8_000)
        )
        audio, mapping = render_relational_audio(dataset)
        self.assertEqual(audio.shape, (800, 2))
        self.assertEqual(mapping["pitch_policy"], "molecular gaps never alter carrier pitch")
        self.assertGreater(mapping["state_change_event_count"], 0)
        self.assertNotIn("semitone", str(mapping).lower())
        self.assertEqual(
            mapping["carrier_frequencies_hz"],
            relational_mapping_descriptor(dataset)["carrier_frequencies_hz"],
        )

    def test_uniform_downshift_uses_all_branches_and_one_factor(self):
        dataset = build_dense_dataset(
            DissociationConfig(num_points=3, duration_seconds=0.1, sample_rate=8_000)
        )
        audio, mapping = render_uniform_downshift_audio(dataset, sample_rate=8_000)
        self.assertEqual(audio.shape, (800, 2))
        self.assertEqual(mapping["num_excitation_branches"], 5)
        self.assertLess(mapping["audio_frequency_range_hz"][0], mapping["audio_frequency_range_hz"][1])
        self.assertAlmostEqual(mapping["audio_frequency_range_hz"][1], 3_600.0, places=9)
        self.assertEqual(
            mapping["global_division_factor"],
            uniform_downshift_mapping(dataset, sample_rate=8_000)["global_division_factor"],
        )
        self.assertIn("one constant division", mapping["ratio_policy"])

    def test_chamber_route_uses_h2_chords_recurring_gestures_and_no_note_grid(self):
        dataset = build_dense_dataset(
            DissociationConfig(num_points=3, duration_seconds=0.1, sample_rate=8_000)
        )
        audio, mapping = render_spectral_chamber_audio(
            dataset, sample_rate=8_000, duration_seconds=2.0
        )
        self.assertEqual(audio.shape, (16_000, 2))
        self.assertEqual(set(mapping["chords"]), {"compressed", "equilibrium", "dissociated"})
        self.assertGreater(mapping["state_derived_event_count"], 0)
        self.assertIn("power-of-two", mapping["frequency_policy"])
        self.assertNotIn("equal temperament", str(mapping).lower())
        self.assertEqual(
            mapping["chords"]["equilibrium"]["registered_hz"],
            chamber_mapping_descriptor(dataset)["chords"]["equilibrium"]["registered_hz"],
        )

    def test_existing_qmw_wavetable_and_wilson_material_adapter(self):
        dataset = build_dense_dataset(
            DissociationConfig(num_points=3, duration_seconds=0.1, sample_rate=8_000)
        )
        self.assertEqual(len(dataset["points"][0]["qmw_wavetable_buffer"]), 256)
        audio, mapping = render_qmw_wavetable_wilson_audio(
            dataset, sample_rate=8_000, duration_seconds=1.0
        )
        self.assertEqual(audio.shape, (8_000, 2))
        self.assertEqual(mapping["wavetable_source"]["table_size"], 256)
        self.assertEqual(len(mapping["wilson_material"]["tones"]), 6)
        self.assertIn("not an oracle consultation", mapping["wilson_material"]["status"])
        self.assertEqual(mapping["osc_compatibility"]["table_address"], "/qmw/circuit/wavetable/buffer")


if __name__ == "__main__":
    unittest.main()
