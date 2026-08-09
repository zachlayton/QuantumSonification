import unittest

from qiskit_nature_molecular_v1 import analyze_h2_point


class H2MolecularWorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.point = analyze_h2_point(0.735)

    def test_matches_reference_h2_ground_energy(self):
        self.assertAlmostEqual(
            self.point["energies_hartree"]["total"][0],
            -1.137306035753,
            places=10,
        )

    def test_particle_and_rdm_invariants(self):
        validation = self.point["validation"]
        self.assertLess(validation["hamiltonian_hermiticity_max_error"], 1e-12)
        self.assertAlmostEqual(validation["particle_number"], 2.0, places=11)
        self.assertAlmostEqual(validation["one_rdm_trace"], 2.0, places=11)
        self.assertLess(validation["one_rdm_hermiticity_max_error"], 1e-12)
        self.assertLess(validation["two_rdm_contraction_max_error"], 1e-11)

    def test_homonuclear_dipole_is_zero(self):
        self.assertLess(self.point["dipole_atomic_units"]["total_magnitude"], 1e-7)

    def test_excited_spectrum_and_rdm_are_present(self):
        self.assertGreaterEqual(len(self.point["energies_hartree"]["total"]), 2)
        self.assertIn("spin_orbital_1rdm", self.point["ground_state_rdm"])
        self.assertIn("spin_orbital_2rdm", self.point["ground_state_rdm"])


if __name__ == "__main__":
    unittest.main()
