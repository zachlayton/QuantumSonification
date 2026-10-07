"""Contracts for the phase-interference timbre projection."""
from dataclasses import replace
import unittest

import numpy as np

from qmw.acoustics.interference_timbre import (
    INTERFERENCE_TIMBRE_SCHEMA,
    InterferenceTimbreControl,
    InterferenceTimbrePacketReceiver,
    InterferenceTimbrePolicy,
    InterferenceTimbreProjector,
)


class InterferenceTimbreTests(unittest.TestCase):
    def setUp(self) -> None:
        self.base = np.full(4, 0.5)
        self.ids = tuple(f"M{index + 1}" for index in range(4))
        self.projector = InterferenceTimbreProjector()

    def project(self, control: InterferenceTimbreControl):
        return self.projector.process(
            base_amplitudes=self.base,
            mode_ids=self.ids,
            source_id="fixture",
            source_revision=7,
            control=control,
            provenance=("fixed four-mode fixture",),
        )

    def test_zero_depth_is_exactly_neutral(self) -> None:
        frame = self.project(InterferenceTimbreControl(
            revision=1,
            phase_radians=1.3,
            phase_spread_radians=-0.7,
            depth=0.0,
            slew_seconds=0.08,
        ))
        np.testing.assert_array_equal(frame.gain_factors, np.ones(4))
        np.testing.assert_array_equal(frame.output_amplitudes, self.base)
        self.assertEqual(frame.base_power, frame.output_power)
        self.assertFalse(frame.complete_cancellation)

    def test_phase_moves_power_through_modes_without_retuning(self) -> None:
        a = self.project(InterferenceTimbreControl(1, 0.0, np.pi, 1.0, 0.05))
        b = self.project(InterferenceTimbreControl(2, np.pi, np.pi, 1.0, 0.05))
        np.testing.assert_allclose(a.output_amplitudes, [2**-0.5, 0, 2**-0.5, 0], atol=1e-12)
        np.testing.assert_allclose(b.output_amplitudes, [0, 2**-0.5, 0, 2**-0.5], atol=1e-12)
        np.testing.assert_allclose(a.gain_factors, [2**0.5, 0, 2**0.5, 0], atol=1e-12)
        self.assertAlmostEqual(a.output_power, a.base_power)
        self.assertAlmostEqual(b.output_power, b.base_power)
        self.assertEqual(a.mode_ids, b.mode_ids)

    def test_complete_cancellation_is_explicit_silence(self) -> None:
        frame = self.project(InterferenceTimbreControl(1, np.pi, 0.0, 1.0, 0.05))
        np.testing.assert_array_equal(frame.gain_factors, np.zeros(4))
        np.testing.assert_array_equal(frame.output_amplitudes, np.zeros(4))
        self.assertTrue(frame.complete_cancellation)
        self.assertEqual(frame.output_power, 0.0)

    def test_zero_base_is_silence_not_a_normalization_fallback(self) -> None:
        frame = self.projector.process(
            base_amplitudes=np.zeros(3),
            mode_ids=("M1", "M2", "M3"),
            source_id="zero",
            source_revision=0,
            control=InterferenceTimbreControl(0, 0.0, 0.4, 1.0, 0.1),
        )
        np.testing.assert_array_equal(frame.gain_factors, np.zeros(3))
        self.assertTrue(frame.complete_cancellation)

        neutral = self.projector.process(
            base_amplitudes=np.zeros(3),
            mode_ids=("M1", "M2", "M3"),
            source_id="zero",
            source_revision=1,
            control=InterferenceTimbreControl(depth=0.0),
        )
        np.testing.assert_array_equal(neutral.gain_factors, np.ones(3))
        self.assertTrue(neutral.complete_cancellation)

    def test_density_coherence_supplies_phase_and_pair_visibility(self) -> None:
        state = np.array([1.0, np.exp(0.7j)]) / np.sqrt(2)
        rho = np.outer(state, state.conj())
        policy = InterferenceTimbrePolicy(
            revision=3,
            phase_offset_radians=0.2,
            phase_spread_radians=0.4,
            depth=0.75,
            slew_seconds=0.09,
            source_kind="density_coherence",
            coherence_row=0,
            coherence_column=1,
        )
        control = policy.resolve(rho)
        self.assertAlmostEqual(control.phase_radians, -0.5)
        self.assertAlmostEqual(control.depth, 0.75)
        self.assertEqual(control.phase_source, "rho[0,1]")
        self.assertIn("pair_visibility", control.provenance[-1])

        diagonal = np.diag([0.5, 0.5])
        absent = policy.resolve(diagonal)
        self.assertEqual(absent.depth, 0.0)
        self.assertAlmostEqual(absent.phase_radians, 0.2)
        np.testing.assert_array_equal(diagonal, np.diag([0.5, 0.5]))

    def test_invalid_controls_and_inputs_are_rejected_atomically(self) -> None:
        for kwargs in (
            {"revision": -1},
            {"phase_radians": np.inf},
            {"phase_spread_radians": np.nan},
            {"depth": -0.01},
            {"depth": 1.01},
            {"slew_seconds": -0.01},
        ):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                InterferenceTimbreControl(**kwargs)
        control = InterferenceTimbreControl()
        for amplitudes, ids in (([1, -1], ("M1", "M2")), ([1, np.nan], ("M1", "M2")),
                                ([1, 1], ("M1", "M1")), ([1], ("M1", "M2"))):
            with self.subTest(amplitudes=amplitudes, ids=ids), self.assertRaises(ValueError):
                self.projector.process(base_amplitudes=amplitudes, mode_ids=ids,
                    source_id="fixture", source_revision=0, control=control)

    def test_arrays_are_snapshots_and_read_only(self) -> None:
        base = self.base.copy()
        frame = self.projector.process(base_amplitudes=base, mode_ids=self.ids,
            source_id="fixture", source_revision=1,
            control=InterferenceTimbreControl(1, 0.2, 0.5, 0.8, 0.1))
        base[:] = 0
        self.assertGreater(frame.base_power, 0)
        for value in (frame.base_amplitudes, frame.phase_offsets_radians,
                      frame.raw_power_weights, frame.gain_factors,
                      frame.output_amplitudes):
            with self.assertRaises(ValueError):
                value[0] = 9

    def test_atomic_packet_receiver_rejects_stale_and_malformed_frames(self) -> None:
        frame = self.project(InterferenceTimbreControl(2, 0.2, 0.5, 0.8, 0.1))
        args = frame.osc_arguments()
        self.assertEqual(args[0], INTERFERENCE_TIMBRE_SCHEMA)
        receiver = InterferenceTimbrePacketReceiver()
        accepted = receiver.accept(args)
        self.assertIsNotNone(accepted)
        np.testing.assert_allclose(accepted["gain_factors"], frame.gain_factors)
        self.assertIsNone(receiver.accept(args))
        self.assertIsNone(InterferenceTimbrePacketReceiver().accept(args[:-1]))
        wrong = list(args)
        wrong[4] = 5
        self.assertIsNone(InterferenceTimbrePacketReceiver().accept(wrong))
        newer_control = replace(frame.control, revision=3)
        newer = self.project(newer_control)
        self.assertIsNotNone(receiver.accept(newer.osc_arguments()))


if __name__ == "__main__":
    unittest.main()
