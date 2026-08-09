from __future__ import annotations

import math
import unittest

import numpy as np

from quantum_statistics_instrument_v1.quantum_statistics_model import (
    ATOMIC_MASS,
    BOSE_CRITICAL_REDUCED_DENSITY,
    compare_statistics,
    phase_space_density,
    quantum_gas_state,
    thermal_de_broglie_wavelength,
)


class QuantumStatisticsModelTests(unittest.TestCase):
    def test_thermal_wavelength_scales_as_inverse_square_root_temperature(self) -> None:
        cold = thermal_de_broglie_wavelength(ATOMIC_MASS, 100.0)
        hot = thermal_de_broglie_wavelength(ATOMIC_MASS, 400.0)
        self.assertAlmostEqual(cold / hot, 2.0, places=12)

    def test_phase_space_density_is_n_lambda_cubed(self) -> None:
        wavelength = thermal_de_broglie_wavelength(4.0 * ATOMIC_MASS, 2.0)
        number_density = 3.5e25
        self.assertAlmostEqual(
            phase_space_density(number_density, 4.0 * ATOMIC_MASS, 2.0),
            number_density * wavelength**3,
        )

    def test_classical_limit_converges_from_opposite_sides(self) -> None:
        states = compare_statistics(1e-3)
        self.assertGreater(states["fermi"].pressure_ratio, 1.0)
        self.assertLess(states["bose"].pressure_ratio, 1.0)
        self.assertAlmostEqual(states["fermi"].pressure_ratio, 1.0, delta=2e-4)
        self.assertAlmostEqual(states["bose"].pressure_ratio, 1.0, delta=2e-4)

    def test_fermion_occupations_are_pauli_bounded(self) -> None:
        state = quantum_gas_state(20.0, "fermi")
        occupations = [state.mean_occupation(x) for x in np.linspace(0.0, 20.0, 101)]
        self.assertTrue(all(0.0 <= value <= 1.0 for value in occupations))
        self.assertGreater(state.pressure_ratio, 1.0)

    def test_bose_condensation_threshold_and_fraction(self) -> None:
        critical = BOSE_CRITICAL_REDUCED_DENSITY
        onset = quantum_gas_state(critical, "bose")
        twice = quantum_gas_state(2.0 * critical, "bose")
        self.assertAlmostEqual(onset.fugacity, 1.0)
        self.assertAlmostEqual(onset.condensate_fraction, 0.0)
        self.assertAlmostEqual(twice.condensate_fraction, 0.5)
        self.assertLess(twice.pressure_ratio, onset.pressure_ratio)

    def test_internal_degeneracy_delays_bose_condensation(self) -> None:
        density = 1.5 * BOSE_CRITICAL_REDUCED_DENSITY
        spinless = quantum_gas_state(density, "bose", internal_degeneracy=1)
        doublet = quantum_gas_state(density, "bose", internal_degeneracy=2)
        self.assertGreater(spinless.condensate_fraction, 0.0)
        self.assertEqual(doublet.condensate_fraction, 0.0)

    def test_spectral_weights_are_normalized(self) -> None:
        energies = np.linspace(0.08, 6.0, 10)
        for state in compare_statistics(2.0).values():
            weights = state.spectral_particle_weights(energies)
            self.assertAlmostEqual(float(np.sum(weights)), 1.0)
            self.assertTrue(np.all(weights >= 0.0))

    def test_detection_events_have_fermion_and_boson_number_statistics(self) -> None:
        rng = np.random.default_rng(77)
        fermi = quantum_gas_state(4.0, "fermi")
        bose = quantum_gas_state(2.0, "bose")
        f_events = np.array(
            [fermi.sample_detected_occupation(0.2, rng, detection_efficiency=0.3) for _ in range(60_000)]
        )
        b_events = np.array(
            [bose.sample_detected_occupation(0.2, rng, detection_efficiency=0.3) for _ in range(60_000)]
        )
        self.assertTrue(np.all((f_events == 0) | (f_events == 1)))
        self.assertLess(float(np.var(f_events)), float(np.mean(f_events)))
        self.assertGreater(int(np.max(b_events)), 1)
        self.assertGreater(float(np.var(b_events)), float(np.mean(b_events)))

    def test_pressure_has_correct_classical_scale(self) -> None:
        state = quantum_gas_state(1e-5, "fermi")
        pressure = state.pressure_pa(2e20, 300.0)
        expected = 2e20 * 1.380_649e-23 * 300.0
        self.assertTrue(math.isclose(pressure, expected, rel_tol=2e-6))


if __name__ == "__main__":
    unittest.main()
