import math
import unittest

import numpy as np

from guidance.four_qubit_configuration_guidance_v1 import (
    ConfigurationEnsemble,
    current_matrix,
    evolve_ensemble,
    transition_rates,
)


class FourQubitConfigurationGuidanceTests(unittest.TestCase):
    def test_current_is_antisymmetric_and_orientation_is_explicit(self):
        h = np.array([[0.0, 1.0], [1.0, 0.0]], dtype=complex)
        psi = np.array([1.0, 1j]) / math.sqrt(2.0)
        rho = np.outer(psi, psi.conj())
        currents = current_matrix(h, rho)
        np.testing.assert_allclose(currents, -currents.T, atol=1e-14)
        self.assertGreater(currents[0, 1], 0.0)  # flow 1 -> 0
        self.assertEqual(transition_rates(h, rho)[1, 0], 0.0)

    def test_two_level_equivariance(self):
        h = np.array([[0.0, 1.0], [1.0, 0.0]], dtype=complex)
        rho0 = np.array([[1.0, 0.0], [0.0, 0.0]], dtype=complex)
        ensemble = ConfigurationEnsemble.from_rho(rho0, 30_000, seed=18)
        rho1 = evolve_ensemble(rho0, h, ensemble, duration=0.7, microsteps=280)
        np.testing.assert_allclose(
            ensemble.distribution(2),
            np.real(np.diag(rho1)),
            atol=0.012,
        )

    def test_four_qubit_dimension_and_beable_basis(self):
        rho = np.eye(16, dtype=complex) / 16.0
        ensemble = ConfigurationEnsemble.from_rho(rho, 100, seed=3)
        self.assertEqual(ensemble.beable_basis, "computational_z")
        self.assertEqual(ensemble.distribution(16).shape, (16,))


if __name__ == "__main__":
    unittest.main()
