from __future__ import annotations

import math
import unittest

import numpy as np

from feedback.grover_statevector_osc_v1 import (
    ExactGroverStatevectorEngine,
    GroverOSCAdapter,
    run_stream,
)


class RecordingClient:
    def __init__(self) -> None:
        self.messages: list[tuple[str, object]] = []

    def send_message(self, address: str, value: object) -> None:
        self.messages.append((address, value))


class ExactGroverStatevectorEngineTests(unittest.TestCase):
    def test_rejects_nonphysical_backend_shortcut(self) -> None:
        with self.assertRaisesRegex(ValueError, "backend"):
            ExactGroverStatevectorEngine(3, 5, modes=8, backend="analytic")

    def test_operator_frames_match_exact_small_grover_state(self) -> None:
        engine = ExactGroverStatevectorEngine(3, 5, modes=8)
        prepared = engine.frame("prepared")
        oracle = engine.apply_oracle()
        diffusion = engine.apply_diffusion()

        self.assertAlmostEqual(prepared.success_probability, 1.0 / 8.0, places=6)
        self.assertAlmostEqual(oracle.success_probability, 1.0 / 8.0, places=6)
        self.assertAlmostEqual(diffusion.success_probability, 0.78125, places=6)
        self.assertAlmostEqual(diffusion.norm, 1.0, places=6)
        np.testing.assert_allclose(
            abs(diffusion.marked_amplitude) ** 2,
            diffusion.success_probability,
            atol=1e-6,
        )

    def test_walsh_modes_are_literal_orthogonal_projection(self) -> None:
        engine = ExactGroverStatevectorEngine(3, 5, modes=8)
        prepared = engine.frame("prepared")
        self.assertAlmostEqual(abs(prepared.walsh_coefficients[0]), 1.0, places=6)
        np.testing.assert_allclose(prepared.walsh_coefficients[1:], 0.0, atol=1e-6)
        self.assertAlmostEqual(prepared.represented_energy, 1.0, places=6)

        oracle = engine.apply_oracle()
        self.assertTrue(np.all(np.abs(oracle.walsh_coefficients[1:]) > 0.0))
        self.assertAlmostEqual(
            oracle.represented_energy + oracle.residual_energy, oracle.norm, places=6
        )

    def test_adapter_emits_complex_modes_and_operator_metrics(self) -> None:
        client = RecordingClient()
        adapter = GroverOSCAdapter(client)
        frame = ExactGroverStatevectorEngine(3, 5, modes=8).frame("prepared")
        adapter.publish_frame(frame)
        addresses = [address for address, _ in client.messages]
        self.assertEqual(
            addresses,
            ["/qmw/grover/statevector/frame", "/qmw/grover/statevector/modes"],
        )
        self.assertEqual(len(client.messages[1][1]), 2 + 2 * 8)  # type: ignore[arg-type]

    def test_run_stream_stops_from_computed_probability_and_holds(self) -> None:
        client = RecordingClient()
        adapter = GroverOSCAdapter(client)
        engine = ExactGroverStatevectorEngine(6, 37, modes=8)
        result = run_stream(adapter, engine, 0.0, threshold=0.99)
        self.assertGreaterEqual(result.success_probability, 0.99)
        states = [value for address, value in client.messages if address.endswith("/state")]
        self.assertEqual(states[0], "SEARCHING")
        self.assertEqual(states[-3:], ["FOUND", "STABILIZING", "HELD"])
        self.assertEqual(states.count("APPROACHING"), 1)
        self.assertTrue(math.isfinite(result.grover_plane_angle))


if __name__ == "__main__":
    unittest.main()
