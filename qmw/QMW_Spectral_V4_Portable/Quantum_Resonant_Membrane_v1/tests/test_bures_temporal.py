from __future__ import annotations

import math
import unittest

import numpy as np

from quantum_resonant_membrane.density_engine import DensityMatrixEngine
from quantum_resonant_membrane.temporal import BuresTemporalObserver, bures_angle


class BuresTemporalTests(unittest.TestCase):
    def test_bures_angle_is_zero_for_identical_states_and_symmetric(self) -> None:
        density = DensityMatrixEngine()
        first = density.rho.copy()
        density.step(0.1)
        second = density.rho.copy()
        self.assertAlmostEqual(bures_angle(first, first), 0.0, places=12)
        self.assertAlmostEqual(
            bures_angle(first, second), bures_angle(second, first), places=12
        )
        self.assertGreater(bures_angle(first, second), 0.0)

    def test_clock_scale_changes_records_not_intrinsic_bures_distance(self) -> None:
        density = DensityMatrixEngine()
        states = [density.rho.copy()]
        for _ in range(12):
            states.append(density.step(1.0 / 30.0).rho.copy())
        normal = BuresTemporalObserver(distance_per_pulse=0.01, clock_scale=1.0)
        double = BuresTemporalObserver(distance_per_pulse=0.01, clock_scale=2.0)
        for state in states:
            normal_frame = normal.observe(state)
            double_frame = double.observe(state)
        self.assertAlmostEqual(
            normal_frame.intrinsic_length, double_frame.intrinsic_length, places=12
        )
        self.assertGreaterEqual(
            double_frame.temporal_record_index, normal_frame.temporal_record_index
        )

    def test_reset_rebases_without_a_preparation_jump(self) -> None:
        density = DensityMatrixEngine()
        observer = BuresTemporalObserver()
        observer.observe(density.rho)
        density.prepare("squeezed")
        observer.reset()
        frame = observer.observe(density.rho)
        self.assertEqual(frame.delta_bures, 0.0)
        self.assertEqual(frame.temporal_pulses, 0)
        self.assertTrue(np.isfinite(frame.normalized_bending))

    def test_geodesic_weight_does_not_amplify_nearly_static_roundoff(self) -> None:
        observer = BuresTemporalObserver(
            distance_per_pulse=0.001,
            geodesic_bending_depth=100.0,
        )
        rho = np.diag([0.25, 0.25, 0.25, 0.25]).astype(np.complex128)
        frame = observer.observe(rho)
        for index in range(1, 200):
            epsilon = index * 1.0e-12
            perturbed = rho.copy()
            perturbed[0, 0] += epsilon
            perturbed[1, 1] -= epsilon
            frame = observer.observe(perturbed)
        self.assertTrue(np.isfinite(frame.weighted_time))
        self.assertLess(frame.weighted_time, 1.0e-4)
        self.assertLessEqual(frame.normalized_bending, 1.0)

    def test_geodesic_bending_weight_is_sampling_rate_invariant(self) -> None:
        def state(time: float) -> np.ndarray:
            vector = np.array(
                [
                    1.0,
                    0.55 * np.exp(1j * time),
                    0.35 * np.exp(2.3j * time),
                    0.20 * np.exp(-0.7j * time),
                ],
                dtype=np.complex128,
            )
            vector /= np.linalg.norm(vector)
            return np.outer(vector, vector.conj())

        def bending_ratio(rate: float) -> float:
            observer = BuresTemporalObserver(
                distance_per_pulse=0.2,
                geodesic_bending_depth=1.0,
                max_pulses_per_frame=1,
            )
            step = 1.0 / rate
            for time in (0.0, step, 2.0 * step):
                frame = observer.observe(state(time))
            return frame.bending_increment / frame.delta_bures

        ratios = [bending_ratio(rate) for rate in (30.0, 120.0, 480.0)]
        self.assertGreater(min(ratios), 0.0)
        self.assertLess(max(ratios) - min(ratios), 1.0e-4)
        self.assertTrue(all(math.isfinite(value) for value in ratios))


if __name__ == "__main__":
    unittest.main()
