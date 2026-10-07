from pathlib import Path
import unittest

from quantum_resonant_membrane.tuning import TuningDictionary, edo_scale, load_scl


PACKAGE = Path(__file__).resolve().parents[1]
ARCHIVE = PACKAGE / "tunings" / "scala_archive" / "scl"


class TuningTests(unittest.TestCase):
    def test_offline_dictionary_and_named_views_are_present(self) -> None:
        dictionary = TuningDictionary(ARCHIVE)
        self.assertGreaterEqual(len(dictionary.paths), 5_350)
        self.assertTrue(any(path.name == "wilson7.scl" for path in dictionary.select("Wilson")))
        self.assertTrue(any(path.name == "tenney1.scl" for path in dictionary.select("Tenney")))
        young = dictionary.select("La Monte Young")
        self.assertTrue(any(path.name == "young-lm_piano.scl" for path in young))
        self.assertTrue(any(path.name == "young-lm_guitar.scl" for path in young))

    def test_lamonte_young_file_parses_ratios_and_period(self) -> None:
        scale = load_scl(ARCHIVE / "young-lm_piano.scl")
        self.assertEqual(scale.description, "LaMonte Young's Well-Tuned Piano")
        self.assertAlmostEqual(scale.degrees[1], 567 / 512)
        self.assertAlmostEqual(scale.period, 2.0)
        self.assertEqual(len(scale.degrees), 12)

    def test_n_edo_and_degree_offset_are_periodic(self) -> None:
        scale = edo_scale(19)
        ratios = scale.mode_ratios(20)
        self.assertAlmostEqual(ratios[0], 1.0)
        self.assertAlmostEqual(ratios[19], 2.0)
        shifted = scale.mode_ratios(20, degree_offset=7)
        self.assertAlmostEqual(shifted[0], 1.0)
        self.assertGreater(shifted[-1], 1.0)

    def test_nonperiodic_scala_lists_are_retained(self) -> None:
        scale = load_scl(ARCHIVE / "chimes.scl")
        self.assertEqual(len(scale.degrees), 4)
        self.assertAlmostEqual(scale.degrees[-1], 16 / 29)
        self.assertEqual(scale.period, 2.0)


if __name__ == "__main__":
    unittest.main()
