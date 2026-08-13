import unittest

import numpy as np

try:  # Only used to independently verify wire-format correctness.
    from pythonosc.osc_packet import OscPacket

    _HAVE_PYTHON_OSC = True
except ImportError:  # pragma: no cover - exercised when python-osc is absent
    _HAVE_PYTHON_OSC = False

if __package__:
    from .osc_client_v1 import SonicPiOSCClient, encode_osc_message
    from .realtime_bridge_v1 import (
        MATERIAL_MODEL_NAMES,
        SILENCE_ADDRESS,
        SURFACE_NAMES,
        RealtimeSurfaceConfig,
        SonicPiModeStreamer,
        SurfaceModeCache,
        build_mode_payload,
        compute_modal_packet,
    )
else:  # Direct-test compatibility.
    from osc_client_v1 import SonicPiOSCClient, encode_osc_message
    from realtime_bridge_v1 import (
        MATERIAL_MODEL_NAMES,
        SILENCE_ADDRESS,
        SURFACE_NAMES,
        RealtimeSurfaceConfig,
        SonicPiModeStreamer,
        SurfaceModeCache,
        build_mode_payload,
        compute_modal_packet,
    )


class SurfaceModeCacheTests(unittest.TestCase):
    def test_acoustic_only_change_reuses_geometry(self) -> None:
        cache = SurfaceModeCache()
        base = RealtimeSurfaceConfig(resolution=14, max_modes=8, active_modes=6)
        _, solve_a = compute_modal_packet(base, cache)

        acoustic_variant = RealtimeSurfaceConfig(
            resolution=14,
            max_modes=8,
            active_modes=3,
            t60_seconds=0.5,
            effective_wave_speed=300.0,
        )
        _, solve_b = compute_modal_packet(acoustic_variant, cache)
        self.assertIs(solve_a, solve_b)

    def test_geometry_change_invalidates_cache(self) -> None:
        cache = SurfaceModeCache()
        base = RealtimeSurfaceConfig(resolution=14, max_modes=8, active_modes=6)
        _, solve_a = compute_modal_packet(base, cache)

        geometry_variant = RealtimeSurfaceConfig(
            resolution=14, max_modes=8, active_modes=6, parameter=9.0
        )
        _, solve_b = compute_modal_packet(geometry_variant, cache)
        self.assertIsNot(solve_a, solve_b)


class ModalPacketTests(unittest.TestCase):
    def test_all_exposed_surfaces_and_models_produce_audible_positive_modes(
        self,
    ) -> None:
        for surface in SURFACE_NAMES:
            cache = SurfaceModeCache()
            for model in MATERIAL_MODEL_NAMES:
                config = RealtimeSurfaceConfig(
                    surface=surface,
                    resolution=14,
                    max_modes=6,
                    active_modes=4,
                    material_model=model,
                )
                packet, _ = compute_modal_packet(config, cache)
                with self.subTest(surface=surface, model=model):
                    self.assertGreater(len(packet.frequencies_hz), 0)
                    self.assertTrue(np.all(packet.frequencies_hz >= 0.0))
                    self.assertTrue(np.all(packet.decay_times_seconds > 0.0))


class OSCEncodingTests(unittest.TestCase):
    @unittest.skipUnless(_HAVE_PYTHON_OSC, "python-osc not installed")
    def test_encode_osc_message_round_trips_through_python_osc(self) -> None:
        message = encode_osc_message("/algebraic/modes", [2, 440.0, 1.5, 0.8, -0.2])
        parsed = OscPacket(message).messages[0].message
        self.assertEqual(parsed.address, "/algebraic/modes")
        self.assertEqual(parsed.params[0], 2)
        self.assertAlmostEqual(parsed.params[1], 440.0, places=3)

    def test_encode_osc_message_rejects_bad_address(self) -> None:
        with self.assertRaises(ValueError):
            encode_osc_message("algebraic/modes", [1])

    def test_build_mode_payload_length_matches_four_fields_per_mode(self) -> None:
        cache = SurfaceModeCache()
        config = RealtimeSurfaceConfig(resolution=14, max_modes=6, active_modes=4)
        packet, _ = compute_modal_packet(config, cache)
        payload = build_mode_payload(packet, seed=1, stereo_width=0.85)
        self.assertEqual(len(payload), 4 * len(packet.frequencies_hz))
        pans = payload[3::4]
        self.assertTrue(all(-1.0 <= pan <= 1.0 for pan in pans))


class SonicPiModeStreamerTests(unittest.TestCase):
    def test_send_packet_sends_one_flattened_message(self) -> None:
        sent: list[tuple[str, list]] = []

        class RecordingClient(SonicPiOSCClient):
            def send(self, address, arguments=()):  # type: ignore[override]
                sent.append((address, list(arguments)))

        cache = SurfaceModeCache()
        config = RealtimeSurfaceConfig(resolution=14, max_modes=6, active_modes=3)
        packet, _ = compute_modal_packet(config, cache)

        client = RecordingClient()
        self.addCleanup(client.close)
        streamer = SonicPiModeStreamer(client)
        count = streamer.send_packet(packet)

        self.assertEqual(count, len(packet.frequencies_hz))
        self.assertEqual(len(sent), 1)
        address, args = sent[0]
        self.assertEqual(address, "/algebraic/modes")
        self.assertEqual(args[0], count)
        self.assertEqual(len(args), 1 + 4 * count)

    def test_send_silence_sends_dedicated_address(self) -> None:
        sent: list[tuple[str, list]] = []

        class RecordingClient(SonicPiOSCClient):
            def send(self, address, arguments=()):  # type: ignore[override]
                sent.append((address, list(arguments)))

        client = RecordingClient()
        self.addCleanup(client.close)
        streamer = SonicPiModeStreamer(client)
        streamer.send_silence()
        self.assertEqual(sent, [(SILENCE_ADDRESS, [])])


if __name__ == "__main__":
    unittest.main()
