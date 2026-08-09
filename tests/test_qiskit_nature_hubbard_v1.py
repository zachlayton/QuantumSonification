import math
import unittest

import numpy as np

from qiskit_nature_hubbard_v1.mapping import musical_descriptor
from qiskit_nature_hubbard_v1.model import HubbardConfig, analyze_hubbard


class HubbardAnalysisTests(unittest.TestCase):
    def setUp(self):
        self.config = HubbardConfig()
        self.result = analyze_hubbard(self.config)

    def test_hamiltonian_is_hermitian_and_particle_sector_is_exact(self):
        validation = self.result["validation"]
        self.assertLess(validation["hermiticity_max_error"], 1e-12)
        self.assertLess(validation["particle_number_error"], 1e-12)
        self.assertEqual(self.result["dimensions"]["particle_sector"], math.comb(4, 2))

    def test_hubbard_dimer_matches_analytic_ground_energy(self):
        t = self.config.hopping
        u = self.config.onsite_interaction
        expected = 0.5 * (u - math.sqrt(u * u + 16.0 * t * t))
        self.assertAlmostEqual(self.result["raw"]["energies"][0], expected, places=11)

    def test_observables_have_physical_bounds_and_symmetry(self):
        raw = self.result["raw"]
        self.assertTrue(all(-1e-12 <= x <= 2.0 + 1e-12 for x in raw["site_occupations"]))
        self.assertTrue(all(-1e-12 <= x <= 1.0 + 1e-12 for x in raw["site_double_occupancies"]))
        self.assertAlmostEqual(sum(raw["site_occupations"]), self.config.particles, places=11)
        self.assertAlmostEqual(raw["site_occupations"][0], raw["site_occupations"][1], places=11)

    def test_descriptor_is_deterministic(self):
        again = analyze_hubbard(self.config)
        np.testing.assert_allclose(
            self.result["raw"]["ground_state_probabilities"],
            again["raw"]["ground_state_probabilities"],
            atol=0.0,
            rtol=0.0,
        )

    def test_raw_and_musical_routes_are_explicit(self):
        mapped = musical_descriptor(self.result)
        self.assertEqual(mapped["software"]["qiskit_nature"], "0.8.0")
        self.assertIn("raw", mapped)
        self.assertIn("musical", mapped)
        self.assertIn("mapping_contract", mapped)
        self.assertIn("gap_frequency_ratios", mapped["musical"])
        self.assertIn("gap_log2_ratios", mapped["musical"])
        self.assertNotIn("gap_semitones", mapped["musical"])
        self.assertTrue(all(0.0 <= x <= 1.0 for x in mapped["musical"]["voice_amplitudes"]))


if __name__ == "__main__":
    unittest.main()
