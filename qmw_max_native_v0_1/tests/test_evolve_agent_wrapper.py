import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "source" / "qmw.evolve" / "qmw.evolve.cpp"


class EvolveWrapperContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = SOURCE.read_text(encoding="utf-8")

    def test_public_object_and_inputs_are_explicit(self):
        self.assertIn('"qmw.evolve"', self.source)
        for selector in (
            '"rho_real"',
            '"rho_imag"',
            '"hamiltonian_real"',
            '"hamiltonian_imag"',
            '"evolve"',
        ):
            self.assertIn(selector, self.source)
        self.assertIn(
            "evolve candidate_revision state_revision hamiltonian_revision dt time_unit hbar",
            self.source,
        )

    def test_candidate_pair_remains_qmw_state_compatible(self):
        self.assertIn('gensym("real")', self.source)
        self.assertIn('gensym("imag")', self.source)
        self.assertIn("request.candidate_revision", self.source)

    def test_no_hidden_clock_measurement_randomness_or_sound_mapping(self):
        lowered = self.source.lower()
        for forbidden in (
            "clock_new",
            "schedule_delay",
            "random_device",
            "mt19937",
            "dsp_setup",
            "class_dspinit",
            "outlet_new(object, \"signal\")",
        ):
            self.assertNotIn(forbidden, lowered)

    def test_revision_mismatch_and_stale_candidate_are_visible(self):
        for detail in (
            "state_revision_mismatch",
            "hamiltonian_revision_mismatch",
            "stale_candidate_revision",
        ):
            self.assertIn(detail, self.source)


if __name__ == "__main__":
    unittest.main()
