import math
import unittest

from guidance.bell_bohm_grw_experiment_v1 import run_chsh


class BellBohmGRWExperimentTests(unittest.TestCase):
    def test_guided_quantum_equilibrium_violates_chsh(self):
        result = run_chsh(trials_per_pair=16_000, microsteps=160, seed=41)
        self.assertGreater(result.s, 2.0)
        self.assertAlmostEqual(result.s, 2.0 * math.sqrt(2.0), delta=0.075)
        self.assertLess(result.max_no_signaling_error, 0.055)

    def test_localization_reduces_bell_correlation(self):
        result = run_chsh(
            trials_per_pair=16_000,
            microsteps=160,
            seed=72,
            grw_visibility=0.0,
        )
        self.assertLess(result.s, 2.0)
        self.assertAlmostEqual(result.s, math.sqrt(2.0), delta=0.075)


if __name__ == "__main__":
    unittest.main()
