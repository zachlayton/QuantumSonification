#!/usr/bin/env python3
import pathlib
import sys
import unittest

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from qmw_iching_dynamic_density_oracle8_v4 import DynamicIChingDensityOracleV4, V4_ROOT
from qmw_iching_v4_live_service import V4LiveService


class FakeClient:
    def __init__(self): self.messages = []
    def send_message(self, address, arguments): self.messages.append((address, arguments))


class FakeAudioPlayer:
    def __init__(self): self.calls = []; self.stopped = False; self.closed = False
    def play(self, frame, laplacian): self.calls.append((frame, laplacian.copy()))
    def stop(self, *_args): self.stopped = True
    def close(self): self.closed = True


class V4LiveServiceTests(unittest.TestCase):
    def make_service(self):
        client = FakeClient()
        player = FakeAudioPlayer()
        oracle = DynamicIChingDensityOracleV4(seed=71, dephasing_rate=0.03)
        service = V4LiveService(
            oracle, [client], seed=71, audio_player=player,
            inter_message_delay=0.0,
        )
        return service, client, player

    def test_evolution_publishes_one_complete_atomic_revision(self):
        service, client, _player = self.make_service()
        frame = service.observe_and_publish()
        self.assertEqual(client.messages[0][0], V4_ROOT + "/begin")
        self.assertEqual(client.messages[-1], (V4_ROOT + "/end", [frame.revision]))
        self.assertTrue(all(args[0] == frame.revision for _path, args in client.messages))
        client.messages.clear()
        evolved = service.evolve_once()
        self.assertGreater(evolved.time, frame.time)
        self.assertEqual(client.messages[0][0], V4_ROOT + "/begin")
        self.assertEqual(client.messages[-1], (V4_ROOT + "/end", [evolved.revision]))

    def test_consultation_sounds_premeasurement_laplacian(self):
        service, client, player = self.make_service()
        pre = service.observe_and_publish()
        expected = pre.gauge.laplacian.copy()
        density_before = service.oracle.density_matrix()
        client.messages.clear()
        service.handle_request("/qmw/iching/consult/request", 1234)
        self.assertEqual(len(player.calls), 1)
        audio_frame, sounded_laplacian = player.calls[0]
        np.testing.assert_allclose(sounded_laplacian, expected, atol=1e-12)
        self.assertEqual(audio_frame.revision, pre.revision)
        self.assertEqual(audio_frame.transformed, audio_frame.primary ^ audio_frame.moving_mask)
        routes = [address for address, _args in client.messages]
        self.assertEqual(routes[0], "/qmw/iching/consult/accepted")
        self.assertIn(V4_ROOT + "/consult", routes)
        self.assertIn(V4_ROOT + "/begin", routes)
        self.assertIn(V4_ROOT + "/end", routes)
        self.assertEqual(routes[-1], "/qmw/iching/consult/published")
        self.assertIsNone(service.current_frame)
        np.testing.assert_allclose(
            service.oracle.density_matrix(), density_before, atol=1e-12
        )

    def test_repeated_consultations_do_not_reuse_collapsed_graph(self):
        service, _client, player = self.make_service()
        pre = service.observe_and_publish()
        service.handle_request("/qmw/iching/consult/request", 1)
        service.handle_request("/qmw/iching/consult/request", 2)
        self.assertEqual(len(player.calls), 2)
        np.testing.assert_allclose(player.calls[0][1], pre.gauge.laplacian, atol=1e-12)
        np.testing.assert_allclose(player.calls[1][1], pre.gauge.laplacian, atol=1e-12)

    def test_audio_stop_and_close_are_forwarded(self):
        service, _client, player = self.make_service()
        service.stop_audio()
        self.assertTrue(player.stopped)
        service.close()
        self.assertTrue(player.closed)


if __name__ == "__main__":
    unittest.main()
