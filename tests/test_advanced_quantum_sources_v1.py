import unittest

import numpy as np

from excitation.advanced_quantum_sources_v1 import (
    DeltaFunctionShellSource,
    DiracHydrogenFineStructureSource,
    DiracStepKleinSource,
    HeliumVariationalTwoElectronSource,
)
from excitation.quantum_instrument_registry_v1 import (
    QUANTUM_INSTRUMENT_NAMES,
    create_quantum_instrument,
)


class AdvancedQuantumSourceTests(unittest.TestCase):
    def test_helium_screened_charge_variational_minimum(self):
        source = HeliumVariationalTwoElectronSource(n_points=48)
        frame = source.frame(0.1)
        self.assertAlmostEqual(source.effective_charge, 27.0 / 16.0, places=12)
        self.assertAlmostEqual(source.variational_energy, -729.0 / 256.0, places=12)
        self.assertAlmostEqual(frame.norm, 1.0, places=10)
        self.assertEqual(frame.metadata["spin_state"], "singlet")
        self.assertEqual(frame.metadata["total_fermion_exchange_symmetry"], "antisymmetric")

    def test_delta_shell_has_bound_state_and_derivative_jump_diagnostic(self):
        source = DeltaFunctionShellSource(n_points=96, shell_strength=-2.0)
        initial = source.frame()
        evolved = source.frame(0.3)
        self.assertAlmostEqual(evolved.norm, 1.0, places=10)
        self.assertGreaterEqual(evolved.metadata["bound_state_count"], 1)
        self.assertLess(evolved.metadata["eigenenergies"][0], 0.0)
        self.assertTrue(np.isfinite(evolved.metadata["derivative_jump_relative_residual"]))
        self.assertGreater(np.max(np.abs(evolved.probability - initial.probability)), 1e-4)

    def test_dirac_hydrogen_resolves_j_fine_structure(self):
        source = DiracHydrogenFineStructureSource(time_scale=10000.0)
        initial = source.frame()
        evolved = source.frame(0.25)
        self.assertAlmostEqual(evolved.norm, 1.0, places=12)
        self.assertGreater(evolved.fine_structure_splitting, 0.0)
        self.assertLess(evolved.binding_energies[0], evolved.binding_energies[1])
        self.assertFalse(np.allclose(initial.amplitudes, evolved.amplitudes, atol=1e-8))
        self.assertIn("Lamb shift", evolved.metadata["omissions"])

    def test_klein_step_propagator_preserves_spinor_norm_and_energy(self):
        source = DiracStepKleinSource(n_points=256)
        initial = source.frame()
        evolved = source.frame(0.05)
        self.assertTrue(evolved.metadata["klein_zone"])
        self.assertAlmostEqual(evolved.norm, 1.0, places=10)
        self.assertAlmostEqual(
            evolved.energy_expectation, initial.energy_expectation, places=8
        )
        self.assertGreater(float(np.max(evolved.probability_current)), 0.0)
        self.assertGreater(np.max(np.abs(evolved.probability - initial.probability)), 1e-4)

    def test_registry_exposes_all_remaining_engines(self):
        names = (
            "helium_variational_two_electron",
            "delta_function_shell",
            "dirac_hydrogen_fine_structure",
            "dirac_step_klein",
        )
        for name in names:
            self.assertIn(name, QUANTUM_INSTRUMENT_NAMES)
        self.assertEqual(
            create_quantum_instrument(
                "dirac_step_klein", n_points=128, extent=40.0, packet_center=-10.0
            ).frame().source,
            "dirac_step_klein",
        )


if __name__ == "__main__":
    unittest.main()
