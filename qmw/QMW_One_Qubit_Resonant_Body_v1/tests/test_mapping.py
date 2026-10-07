from __future__ import annotations

import unittest

import numpy as np

from qmw_one_qubit.frames import SoundAdapterControls
from qmw_one_qubit.mapping import observe_one_qubit, resonant_body_frame, signed_body_weights
from qmw_one_qubit.physics import OneQubitEngine


class ResonantBodyMappingTests(unittest.TestCase):
    def observation(self, preparation: str):
        return observe_one_qubit(OneQubitEngine(preparation=preparation).snapshot())

    def test_maximally_mixed_state_is_the_monopole(self) -> None:
        weights = signed_body_weights(self.observation("mixed"), body_detail=0.45)
        np.testing.assert_allclose(weights, [1, 0, 0, 0, 0, 0, 0, 0, 0], atol=1e-12)

    def test_north_and_south_poles_preserve_signed_z_dipole(self) -> None:
        north = signed_body_weights(self.observation("0"), body_detail=0.45)
        south = signed_body_weights(self.observation("1"), body_detail=0.45)
        self.assertGreater(north[3], 0)
        self.assertLess(south[3], 0)
        self.assertAlmostEqual(north[8], south[8], places=12)
        self.assertAlmostEqual(float(north @ north), 1.0, places=12)
        self.assertAlmostEqual(float(south @ south), 1.0, places=12)

    def test_equatorial_x_and_y_states_are_distinct_and_normalized(self) -> None:
        x_weights = signed_body_weights(self.observation("+"), body_detail=0.45)
        y_weights = signed_body_weights(self.observation("+i"), body_detail=0.45)
        self.assertFalse(np.allclose(x_weights, y_weights))
        self.assertGreater(x_weights[1], 0)
        self.assertGreater(y_weights[2], 0)
        self.assertAlmostEqual(float(x_weights @ x_weights), 1.0, places=12)
        self.assertAlmostEqual(float(y_weights @ y_weights), 1.0, places=12)

    def test_body_frame_is_immutable_and_acoustic_controls_are_exact(self) -> None:
        observation = self.observation("+")
        controls = SoundAdapterControls(
            base_frequency_hz=100,
            base_decay_seconds=1.2,
            decay_tilt=0,
            body_detail=0.25,
        )
        body = resonant_body_frame(observation, controls)
        self.assertEqual(body.observation_revision, observation.revision)
        self.assertEqual(body.frequencies_hz[0], 100)
        np.testing.assert_allclose(body.decay_seconds, 1.2)
        self.assertFalse(body.signed_weights.flags.writeable)
        with self.assertRaises(ValueError):
            body.signed_weights[0] = 0


if __name__ == "__main__":
    unittest.main()
