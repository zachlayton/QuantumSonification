from __future__ import annotations

import math
import random
import unittest

from pauli_state_instrument_v1.pauli_state_model import (
    CoupledAddress,
    ElectronAddress,
    PauliStateLedger,
    Spinor,
    antisymmetric_norm,
    coupled_components,
    strong_field_audio_frequency,
)


class PauliStateModelTests(unittest.TestCase):
    def test_duplicate_complete_address_is_excluded(self) -> None:
        ledger = PauliStateLedger()
        address = ElectronAddress(2, 1, 0, 1)
        self.assertTrue(ledger.occupy(address).accepted)
        result = ledger.occupy(address)
        self.assertFalse(result.accepted)
        self.assertEqual(len(ledger.occupied), 1)
        self.assertEqual(ledger.rejected_attempts, 1)

    def test_closed_p_subshell_has_six_distinct_states(self) -> None:
        ledger = PauliStateLedger()
        results = ledger.fill_subshell(2, 1)
        self.assertEqual(sum(result.accepted for result in results), 6)
        self.assertTrue(ledger.subshell_closed(2, 1))

    def test_coupled_extremal_state_has_one_component(self) -> None:
        state = CoupledAddress(2, 1, 3, 3)
        components = coupled_components(state)
        self.assertEqual(components, ((ElectronAddress(2, 1, 1, 1), 1.0),))

    def test_coupled_components_are_normalized(self) -> None:
        for j_twice in (1, 3):
            for mj_twice in range(-j_twice, j_twice + 1, 2):
                components = coupled_components(CoupledAddress(2, 1, j_twice, mj_twice))
                self.assertAlmostEqual(sum(amplitude * amplitude for _, amplitude in components), 1.0)

    def test_j_manifolds_with_same_mj_are_orthogonal(self) -> None:
        upper = dict(coupled_components(CoupledAddress(2, 1, 3, 1)))
        lower = dict(coupled_components(CoupledAddress(2, 1, 1, 1)))
        inner = sum(upper.get(address, 0.0) * lower.get(address, 0.0) for address in set(upper) | set(lower))
        self.assertAlmostEqual(inner, 0.0)

    def test_spinor_requires_four_pi_for_same_vector(self) -> None:
        initial = Spinor()
        after_two_pi = initial.rotate_y(2.0 * math.pi)
        after_four_pi = initial.rotate_y(4.0 * math.pi)
        self.assertAlmostEqual(after_two_pi.alpha.real, -1.0)
        self.assertAlmostEqual(after_two_pi.coherent_reference_intensity(initial), 0.0)
        self.assertAlmostEqual(after_four_pi.alpha.real, 1.0)
        self.assertAlmostEqual(after_four_pi.coherent_reference_intensity(initial), 1.0)

    def test_measurement_probabilities_depend_on_axis(self) -> None:
        up = Spinor()
        self.assertEqual(up.measurement_probabilities(0.0, 0.0), (1.0, 0.0))
        plus_x, minus_x = up.measurement_probabilities(math.pi / 2.0, 0.0)
        self.assertAlmostEqual(plus_x, 0.5)
        self.assertAlmostEqual(minus_x, 0.5)
        outcome, collapsed = up.measure(math.pi / 2.0, 0.0, random.Random(2))
        self.assertIn(outcome, (-1, 1))
        probabilities = collapsed.measurement_probabilities(math.pi / 2.0, 0.0)
        self.assertAlmostEqual(max(probabilities), 1.0)

    def test_slater_norm_vanishes_for_identical_state(self) -> None:
        up = Spinor()
        down = Spinor(0.0, 1.0)
        self.assertAlmostEqual(antisymmetric_norm(up, up), 0.0)
        self.assertAlmostEqual(antisymmetric_norm(up, down), 1.0)

    def test_strong_field_mapping_resolves_spin(self) -> None:
        down = ElectronAddress(2, 1, 0, -1)
        up = ElectronAddress(2, 1, 0, 1)
        self.assertEqual(strong_field_audio_frequency(down, base_hz=220.0, orbital_spacing_hz=20.0, field_t=1.0, zeeman_hz_per_t=30.0), 190.0)
        self.assertEqual(strong_field_audio_frequency(up, base_hz=220.0, orbital_spacing_hz=20.0, field_t=1.0, zeeman_hz_per_t=30.0), 250.0)


if __name__ == "__main__":
    unittest.main()
