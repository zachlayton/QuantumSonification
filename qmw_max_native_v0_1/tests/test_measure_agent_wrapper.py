import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "source" / "qmw.measure" / "qmw.measure.cpp"


class MeasureWrapperContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = SOURCE.read_text(encoding="utf-8")

    def test_measurement_is_an_explicit_intervention_on_an_atomic_rho(self):
        for token in (
            '"rho_real"',
            '"rho_imag"',
            '"rho_accepted"',
            '"sample"',
            '"condition"',
            '"measurement_begin"',
            '"measurement_accepted"',
        ):
            self.assertIn(token, self.source)
        self.assertIn("Admission never triggers measurement", self.source)

    def test_record_distinguishes_candidate_probability_rng_and_provenance(self):
        for token in (
            '"probabilities_exact"',
            '"measurement_record"',
            '"rng"',
            '"data_semantics"',
            '"provenance"',
            '"posterior_candidate_real"',
            '"posterior_candidate_imag"',
            '"posterior_candidate_not_committed"',
            '"one_u64_upper_53_bits_to_unit_interval"',
        ):
            self.assertIn(token, self.source)

    def test_wrapper_has_no_commit_evolution_or_audio_surface(self):
        self.assertNotIn('gensym("commit")', self.source)
        self.assertNotIn('gensym("evolve")', self.source)
        self.assertNotIn("dsp_setup", self.source)
        self.assertNotIn("class_dspinit", self.source)
        self.assertNotIn("qmw.state", self.source)


if __name__ == "__main__":
    unittest.main()
