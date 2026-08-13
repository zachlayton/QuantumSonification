import time
import unittest

import numpy as np

if __package__:
    from .osc_client_v1 import SonicPiOSCClient
    from .quantum_conductor_v1 import (
        QuantumConductorConfig,
        QuantumPhaseConductor,
        coherence_phase_signals,
    )
    from .realtime_bridge_v1 import (
        RealtimeSurfaceConfig,
        SonicPiModeStreamer,
        SurfaceModeCache,
        compute_modal_packet,
    )
else:  # Direct-test compatibility.
    from osc_client_v1 import SonicPiOSCClient
    from quantum_conductor_v1 import (
        QuantumConductorConfig,
        QuantumPhaseConductor,
        coherence_phase_signals,
    )
    from realtime_bridge_v1 import (
        RealtimeSurfaceConfig,
        SonicPiModeStreamer,
        SurfaceModeCache,
        compute_modal_packet,
    )


def _small_packet():
    cache = SurfaceModeCache()
    config = RealtimeSurfaceConfig(resolution=14, max_modes=8, active_modes=5)
    packet, _ = compute_modal_packet(config, cache)
    return packet


class CoherencePhaseSignalsTests(unittest.TestCase):
    def test_matches_direct_angle_of_off_diagonal_entries(self) -> None:
        rho = np.diag([0.4, 0.3, 0.2, 0.1]).astype(complex)
        rho[0, 1] = 0.1 + 0.2j
        rho[1, 0] = np.conj(rho[0, 1])
        sin, cos = coherence_phase_signals(rho, 1)
        expected = np.angle(rho[0, 1])
        self.assertAlmostEqual(sin[0], np.sin(expected))
        self.assertAlmostEqual(cos[0], np.cos(expected))

    def test_repeats_pairs_when_more_signals_requested_than_exist(self) -> None:
        rho = np.eye(2, dtype=complex)
        rho[0, 1] = 0.3j
        rho[1, 0] = -0.3j
        sin, cos = coherence_phase_signals(rho, 5)
        self.assertEqual(len(sin), 5)
        np.testing.assert_allclose(sin, sin[0])
        np.testing.assert_allclose(cos, cos[0])

    def test_zero_count_returns_empty_arrays(self) -> None:
        rho = np.eye(4, dtype=complex)
        sin, cos = coherence_phase_signals(rho, 0)
        self.assertEqual(len(sin), 0)
        self.assertEqual(len(cos), 0)


class QuantumPhaseConductorTests(unittest.TestCase):
    def _make_conductor(self, **config_overrides):
        sent: list[tuple[str, list]] = []

        class RecordingClient(SonicPiOSCClient):
            def send(self, address, arguments=()):  # type: ignore[override]
                sent.append((address, list(arguments)))

        client = RecordingClient()
        self.addCleanup(client.close)
        streamer = SonicPiModeStreamer(client)

        packet = _small_packet()
        slow_updates: list[dict] = []
        config = QuantumConductorConfig(tick_hz=40.0, slow_interval_seconds=0.1, **config_overrides)
        conductor = QuantumPhaseConductor(
            streamer=streamer,
            get_packet=lambda: packet,
            on_slow_update=slow_updates.append,
            config=config,
        )
        return conductor, sent, slow_updates, packet

    def test_start_sends_fast_updates_and_stop_halts_them(self) -> None:
        conductor, sent, slow_updates, packet = self._make_conductor()
        conductor.start()
        self.addCleanup(conductor.stop)
        try:
            deadline = time.monotonic() + 2.0
            while len(sent) < 3 and time.monotonic() < deadline:
                time.sleep(0.02)
            self.assertGreaterEqual(len(sent), 3)

            address, args = sent[0]
            self.assertEqual(address, "/algebraic/modes")
            self.assertEqual(int(args[0]), len(packet.frequencies_hz))
            self.assertEqual(len(args), 1 + 4 * len(packet.frequencies_hz))
        finally:
            conductor.stop()

        count_after_stop = len(sent)
        time.sleep(0.15)
        self.assertEqual(len(sent), count_after_stop)

    def test_slow_updates_land_within_configured_ranges(self) -> None:
        conductor, sent, slow_updates, packet = self._make_conductor(
            wave_speed_range=(50.0, 150.0),
            t60_range=(1.0, 3.0),
            damping_tilt_range=(0.1, 0.4),
        )
        conductor.start()
        try:
            deadline = time.monotonic() + 2.0
            while len(slow_updates) < 2 and time.monotonic() < deadline:
                time.sleep(0.02)
        finally:
            conductor.stop()

        self.assertGreaterEqual(len(slow_updates), 2)
        for update in slow_updates:
            self.assertGreaterEqual(update["wave_speed"], 50.0)
            self.assertLessEqual(update["wave_speed"], 150.0)
            self.assertGreaterEqual(update["t60_seconds"], 1.0)
            self.assertLessEqual(update["t60_seconds"], 3.0)
            self.assertGreaterEqual(update["damping_frequency_tilt"], 0.1)
            self.assertLessEqual(update["damping_frequency_tilt"], 0.4)

    def test_zero_modulation_depth_keeps_weights_unchanged(self) -> None:
        conductor, sent, slow_updates, packet = self._make_conductor(
            modulation_depth=0.0
        )
        conductor.start()
        try:
            deadline = time.monotonic() + 1.5
            while len(sent) < 2 and time.monotonic() < deadline:
                time.sleep(0.02)
        finally:
            conductor.stop()

        self.assertGreaterEqual(len(sent), 2)
        _, args = sent[-1]
        amplitudes = args[3::4]
        np.testing.assert_allclose(amplitudes, packet.mode_weights, rtol=1e-6)

    def test_missing_packet_is_skipped_without_raising(self) -> None:
        client = SonicPiOSCClient()
        self.addCleanup(client.close)
        streamer = SonicPiModeStreamer(client)
        conductor = QuantumPhaseConductor(
            streamer=streamer,
            get_packet=lambda: None,
            on_slow_update=lambda _u: None,
            config=QuantumConductorConfig(tick_hz=40.0),
        )
        conductor.start()
        time.sleep(0.1)
        conductor.stop()  # must not hang or raise


if __name__ == "__main__":
    unittest.main()
