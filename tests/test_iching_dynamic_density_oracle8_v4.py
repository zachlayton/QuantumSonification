#!/usr/bin/env python3
import json
import pathlib
import sys
import unittest

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from qmw_iching_dynamic_density_oracle8_v4 import (
    DynamicIChingDensityOracleV4,
    V4_ROOT,
    frame_to_jsonable,
    osc_messages,
)


class FakeClient:
    def __init__(self):
        self.messages = []

    def send_message(self, address, arguments):
        self.messages.append((address, arguments))


class DynamicDensityOracleV4Tests(unittest.TestCase):
    def test_observe_is_non_destructive_and_contains_full_gauge_field(self):
        oracle = DynamicIChingDensityOracleV4(seed=31)
        before = oracle.density_matrix()
        frame = oracle.observe()
        np.testing.assert_allclose(before, oracle.density_matrix(), atol=1e-12)
        self.assertEqual(frame.revision, 1)
        self.assertEqual(len(frame.gauge.edges), 192)
        self.assertEqual(len(frame.gauge.plaquettes), 240)
        self.assertEqual(len(frame.gauge.line_pairs), 15)
        self.assertEqual(len(frame.gauge.descriptors.low_laplacian_eigenvalues), 8)
        self.assertGreaterEqual(frame.gauge.descriptors.laplacian_minimum_eigenvalue, -1e-10)

    def test_evolution_produces_flux_trajectories(self):
        oracle = DynamicIChingDensityOracleV4(seed=32)
        rng = np.random.default_rng(32)
        state = rng.normal(size=256) + 1j * rng.normal(size=256)
        oracle.set_statevector(state)
        first = oracle.observe()
        oracle.evolve(0.025)
        second = oracle.observe()
        self.assertEqual(second.revision, first.revision + 1)
        before = np.asarray([item.flux_radians for item in first.gauge.plaquettes])
        after = np.asarray([item.flux_radians for item in second.gauge.plaquettes])
        wrapped_change = np.angle(np.exp(1j * (after - before)))
        self.assertGreater(float(np.max(np.abs(wrapped_change))), 1e-7)

    def test_atomic_osc_frame_exposes_all_240_fluxes_in_15_chunks(self):
        oracle = DynamicIChingDensityOracleV4(seed=33)
        frame = oracle.observe()
        messages = list(osc_messages(frame))
        self.assertEqual(messages[0][0], V4_ROOT + "/begin")
        self.assertEqual(messages[-1], (V4_ROOT + "/end", [frame.revision]))
        self.assertTrue(all(arguments[0] == frame.revision for _path, arguments in messages))
        chunks = [arguments for path, arguments in messages
                  if path == V4_ROOT + "/gauge/plaquette_pair"]
        edges = [arguments for path, arguments in messages
                 if path == V4_ROOT + "/gauge/edge_line"]
        summaries = [arguments for path, arguments in messages
                     if path == V4_ROOT + "/gauge/pair_summary"]
        self.assertEqual(len(chunks), 15)
        self.assertEqual(len(edges), 6)
        self.assertTrue(all(len(arguments) == 98 for arguments in edges))
        self.assertEqual(sum((len(arguments)-2)//3 for arguments in edges), 192)
        self.assertEqual(len(summaries), 15)
        self.assertTrue(all(len(arguments) == 51 for arguments in chunks))
        self.assertEqual(sum((len(arguments)-3)//3 for arguments in chunks), 240)

    def test_live_stream_uses_only_v4_atomic_routes(self):
        oracle = DynamicIChingDensityOracleV4(seed=34)
        client = FakeClient()
        oracle._osc_client = client
        frame = oracle.observe()
        self.assertEqual(client.messages, list(osc_messages(frame)))
        self.assertFalse(any("/v3/" in address for address, _ in client.messages))

    def test_consultation_preserves_xor_and_uses_v4_route(self):
        oracle = DynamicIChingDensityOracleV4(seed=35)
        client = FakeClient()
        oracle._osc_client = client
        frame = oracle.observe()
        result = oracle.consult()
        moving_mask = sum(value << line for line, value in enumerate(result.moving_lines))
        self.assertEqual(result.h1_index, result.h0_index ^ moving_mask)
        self.assertEqual(client.messages[-1][0], V4_ROOT + "/consult")
        self.assertEqual(client.messages[-1][1][0], frame.revision)

    def test_archival_payload_is_json_serializable_and_bounded(self):
        frame = DynamicIChingDensityOracleV4(seed=36).observe()
        payload = frame_to_jsonable(frame)
        encoded = json.dumps(payload)
        self.assertEqual(payload["schema"], "qmw.iching.dynamic-gauge-frame.v4")
        self.assertEqual(len(payload["gauge"]["plaquettes"]), 240)
        self.assertNotIn("adjacency", payload["gauge"])
        self.assertNotIn("laplacian", payload["gauge"])
        self.assertLess(len(encoded), 250_000)


if __name__ == "__main__":
    unittest.main()
