from __future__ import annotations

import math
import unittest

from heisenberg_instrument_v1.qmb_conductor_density_bridge_v1 import (
    BridgeConfig,
    CELL_COUNT,
    ConductorDensityQMBBridge,
)


class Client:
    def __init__(self) -> None:
        self.messages: list[tuple[str, object]] = []

    def send_message(self, address: str, value: object) -> None:
        self.messages.append((address, value))


class BridgeTests(unittest.TestCase):
    def test_atomic_frame_and_rate_limit(self) -> None:
        client = Client()
        bridge = ConductorDensityQMBBridge(client, BridgeConfig(output_hz=5.0))
        bridge.set_observable_enabled(0)
        real = [0.0] * CELL_COUNT
        imag = [0.0] * CELL_COUNT
        real[0] = 0.5
        imag[1] = -0.25
        bridge.accept_harmonics(1.0, 1.5, 2.0, 3.0)
        bridge.accept_real(*real)
        self.assertTrue(bridge.accept_imag(*imag, now=1.0))
        self.assertFalse(bridge.accept_imag(*imag, now=1.1))
        self.assertTrue(bridge.accept_imag(*imag, now=1.21))
        bridge.set_output_hz(10.0)
        self.assertTrue(bridge.accept_imag(*imag, now=1.32))

        first = client.messages[:8]
        self.assertEqual(first[0], ("/qmw/heisenberg/active/matrix/begin", [1, 16]))
        self.assertEqual(first[-1], ("/qmw/heisenberg/active/matrix/end", 1))
        self.assertEqual(len(first[1][1]), CELL_COUNT)
        self.assertEqual(len(first[6][1]), CELL_COUNT)
        self.assertAlmostEqual(first[3][1][1], 0.25)
        self.assertAlmostEqual(first[4][1][1], -math.pi / 2.0)

    def test_frequency_and_pan_matrices(self) -> None:
        bridge = ConductorDensityQMBBridge(Client())
        bridge.accept_harmonics(1.0, 2.0, 4.0)
        frequency = bridge._frequency_matrix()
        pan = bridge._pan_matrix()
        self.assertEqual(len(frequency), CELL_COUNT)
        self.assertEqual(len(pan), CELL_COUNT)
        self.assertAlmostEqual(frequency[0], 27.5)
        self.assertAlmostEqual(frequency[1], 55.0)
        self.assertAlmostEqual(frequency[2], 110.0)
        self.assertAlmostEqual(pan[0], 0.0)
        self.assertAlmostEqual(pan[15], 1.0)
        self.assertAlmostEqual(pan[15 * 16], -1.0)

    def test_grid_reconstruction_and_phase_observable(self) -> None:
        client = Client()
        bridge = ConductorDensityQMBBridge(client)
        grid = []
        for index in range(CELL_COUNT):
            grid.extend([1.0 if index in (0, 1) else 0.0, 0.5 if index == 1 else 0.0, 0.0])
        bridge.set_observable_phase(0.25)  # pi/2, the Y direction
        self.assertTrue(bridge.accept_grid(*grid, now=1.0))
        frame = dict(client.messages[:8])
        real = frame["/qmw/heisenberg/active/matrix/real"]
        imag = frame["/qmw/heisenberg/active/matrix/imag"]
        self.assertAlmostEqual(real[0], math.sqrt(0.5))
        self.assertAlmostEqual(real[1], -math.sqrt(0.5) / sum(bridge.observable_weights))
        self.assertAlmostEqual(imag[1], 0.0)
        self.assertEqual(sum(value != 0.0 for value in real[2:]), 0)

    def test_four_qubit_observable_activates_four_flip_bands(self) -> None:
        bridge = ConductorDensityQMBBridge(Client())
        real = [0.0] * CELL_COUNT
        imag = [0.0] * CELL_COUNT
        for column in (0, 1, 2, 4, 8):
            real[column] = 1.0
        observed_real, observed_imag = bridge._apply_phase_observable(real, imag)
        for column in (0, 1, 2, 4, 8):
            self.assertGreater(math.hypot(observed_real[column], observed_imag[column]), 0.0)
        self.assertEqual(
            sum(math.hypot(re, im) > 0.0 for re, im in zip(observed_real, observed_imag)),
            5,
        )

    def test_named_observables_switch_live_geometry(self) -> None:
        bridge = ConductorDensityQMBBridge(Client())
        bridge.set_observable("Y0")
        self.assertEqual(bridge.observable_weights, [1.0, 0.0, 0.0, 0.0])
        self.assertAlmostEqual(bridge.observable_tilt_radians, math.pi / 2.0)
        self.assertAlmostEqual(bridge.observable_phase_radians, math.pi / 2.0)
        bridge.set_observable("FOUR")
        self.assertEqual(bridge.observable_weights, bridge.four_qubit_weights)

    def test_complex_grid_smoothing_is_time_correct(self) -> None:
        bridge = ConductorDensityQMBBridge(Client())
        bridge.set_smoothing_ms(100.0)
        on = [item for index in range(CELL_COUNT) for item in (1.0 if index == 0 else 0.0, 0.0, 0.0)]
        off = [0.0] * (CELL_COUNT * 3)
        bridge.accept_grid(*on, now=1.0)
        bridge.accept_grid(*off, now=1.1)
        self.assertAlmostEqual(bridge.real[0], math.exp(-1.0), places=6)
        self.assertAlmostEqual(bridge.imag[0], 0.0)


if __name__ == "__main__":
    unittest.main()
