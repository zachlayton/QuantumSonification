from pathlib import Path
import tempfile
import unittest
from types import SimpleNamespace

import numpy as np

from eigenfield_timing_layer_v1.eigenfield_timing_layer_v1 import (
    EigenfieldTimingLayer,
    EigenfieldState,
    ModePoint,
    TimingConfig,
    compare_grw_eigenfields,
)


class RecordingClient:
    def __init__(self):
        self.messages = []

    def send_message(self, address, value):
        self.messages.append((address, value))


def point(index: int, probability: float) -> ModePoint:
    return ModePoint(
        index=index,
        eigenvalue=float(index + 1),
        frequency_hz=110.0 * (index + 1),
        decay_seconds=0.5,
        damping_rate=2.0,
        material_weight=1.0,
        eigenvalue_norm=float(index),
        log_eigenvalue_norm=float(index),
        probability=probability,
        amplitude=1.0,
        phase=0.0,
        spacing=1.0,
        spacing_norm=0.5,
        cloud_x=0.0,
        cloud_y=0.0,
        cloud_z=0.0,
    )


def bare_layer(clock: str) -> EigenfieldTimingLayer:
    layer = object.__new__(EigenfieldTimingLayer)
    layer.config = TimingConfig(event_clock=clock, seed=9)
    layer.state = SimpleNamespace(
        points=[point(0, 0.5), point(1, 0.5)],
        probabilities=np.array([0.5, 0.5]),
        entropy_bits=1.0,
        channel_isometry=np.eye(2, dtype=np.complex128),
        channel_environment_dimension=1,
    )
    layer.client = RecordingClient()
    layer.rng = np.random.default_rng(9)
    layer.enabled = True
    layer.event_count = 0
    layer.last_grw_comparison = None
    layer.grw_fields = {}
    return layer


def deliver_transition(layer: EigenfieldTimingLayer) -> None:
    before = np.diag([1.0, 0.0]).astype(np.complex128)
    after = np.diag([0.0, 1.0]).astype(np.complex128)
    delta = after - before
    prefix = "/qmw/grw/sonification"
    layer._process_command(
        f"{prefix}/post/rho_real", tuple(after.real.reshape(-1))
    )
    layer._process_command(
        f"{prefix}/post/rho_imag", tuple(after.imag.reshape(-1))
    )
    layer._process_command(
        f"{prefix}/delta/real", tuple(delta.real.reshape(-1))
    )
    layer._process_command(
        f"{prefix}/delta/imag", tuple(delta.imag.reshape(-1))
    )
    layer._process_command(
        f"{prefix}/event",
        (7, 1, 0.63, 1.0, 1.0, 3.0, 1, 1.0, 0.5, 1),
    )


class GRWEigenfieldTimingTests(unittest.TestCase):
    def test_eigenfield_state_loads_saved_channel_projection(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "eigenfield.npz"
            np.savez(
                path,
                geometric_eigenvalues=np.array([1.0, 2.0]),
                mode_probabilities=np.array([0.4, 0.6]),
                mode_amplitudes=np.sqrt([0.4, 0.6]).astype(complex),
                channel_isometry=np.eye(2, dtype=complex),
                channel_environment_dimension=np.asarray(1),
            )
            state = EigenfieldState(path)
            np.testing.assert_allclose(state.channel_isometry, np.eye(2))
            self.assertEqual(state.channel_environment_dimension, 1)

    def test_config_accepts_three_clocks_and_rejects_unknown_clock(self):
        for clock in ("internal", "grw", "hybrid"):
            self.assertEqual(TimingConfig(event_clock=clock).event_clock, clock)
        with self.assertRaises(ValueError):
            TimingConfig(event_clock="random")
        positional = TimingConfig(30.0, 4.0)
        self.assertEqual(positional.control_rate_hz, 30.0)
        self.assertEqual(positional.event_rate_hz, 4.0)
        self.assertEqual(positional.event_clock, "internal")

    def test_pre_post_projection_selects_mode_with_largest_gain(self):
        before = np.diag([1.0, 0.0])
        after = np.diag([0.0, 1.0])
        comparison = compare_grw_eigenfields(
            after,
            after - before,
            np.eye(2),
            1,
            2,
            event_id=12,
            excitation_amplitude=0.7,
        )
        np.testing.assert_allclose(comparison.pre_probabilities, [1.0, 0.0])
        np.testing.assert_allclose(comparison.post_probabilities, [0.0, 1.0])
        np.testing.assert_allclose(comparison.probability_delta, [-1.0, 1.0])
        self.assertEqual(comparison.strongest_mode, 1)
        self.assertAlmostEqual(comparison.strengthening, 1.0)
        self.assertAlmostEqual(comparison.total_variation, 1.0)

    def test_grw_clock_compares_then_excites_strongest_mode(self):
        layer = bare_layer("grw")
        deliver_transition(layer)

        self.assertEqual(layer.event_count, 1)
        self.assertEqual(layer.last_grw_comparison.strongest_mode, 1)
        addresses = [address for address, _ in layer.client.messages]
        comparison_index = addresses.index("/eigenfield/time/grw/comparison")
        event_index = addresses.index("/eigenfield/time/event")
        self.assertLess(comparison_index, event_index)
        event_packet = layer.client.messages[event_index][1]
        self.assertEqual(event_packet[0], 1)
        self.assertAlmostEqual(event_packet[4], 0.63)
        self.assertEqual(event_packet[14], "grw")
        self.assertEqual(event_packet[15], 7)

    def test_internal_clock_observes_grw_comparison_without_grw_trigger(self):
        layer = bare_layer("internal")
        deliver_transition(layer)
        self.assertEqual(layer.event_count, 0)
        addresses = [address for address, _ in layer.client.messages]
        self.assertIn("/eigenfield/time/grw/comparison", addresses)
        self.assertNotIn("/eigenfield/time/event", addresses)

    def test_hybrid_clock_triggers_grw_and_preserves_internal_packet_shape(self):
        layer = bare_layer("hybrid")
        deliver_transition(layer)
        self.assertEqual(layer.event_count, 1)

        layer.trigger_event(index=0)
        packets = [
            value
            for address, value in layer.client.messages
            if address == "/eigenfield/time/event"
        ]
        self.assertEqual(len(packets), 2)
        self.assertEqual(len(packets[0]), 19)
        self.assertEqual(len(packets[1]), 14)

    def test_inaudible_grw_event_is_compared_but_not_excited(self):
        layer = bare_layer("grw")
        before = np.diag([1.0, 0.0]).astype(np.complex128)
        after = np.diag([0.0, 1.0]).astype(np.complex128)
        delta = after - before
        for suffix, values in (
            ("post/rho_real", after.real),
            ("post/rho_imag", after.imag),
            ("delta/real", delta.real),
            ("delta/imag", delta.imag),
        ):
            layer._process_grw_field(suffix, tuple(values.reshape(-1)))
        layer._process_grw_field("event", (8, 1, 0.0, 0, 0, 0, 3, 1, 0, 0))
        self.assertIsNotNone(layer.last_grw_comparison)
        self.assertEqual(layer.event_count, 0)


if __name__ == "__main__":
    unittest.main()
