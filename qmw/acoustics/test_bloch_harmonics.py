import math
import unittest
from unittest.mock import patch

from qmw.acoustics import (
    BlochSphericalCoordinates,
    harmonics_from_bloch,
    harmonics_from_spherical,
    controls_from_bloch,
)
from quantum_spin_polarization_engine_v3_measurement_basis import (
    EngineConfig,
    QuantumSpinPolarizationEngine,
    parse_harmonic_degrees,
)


class RecordingOSCClient:
    def __init__(self) -> None:
        self.messages: list[tuple[str, object]] = []

    def send_message(self, address: str, value: object) -> None:
        self.messages.append((address, value))

    def values(self) -> dict[str, object]:
        return dict(self.messages)


class BlochHarmonicsTests(unittest.TestCase):
    def test_cartesian_to_acoustic_angles(self) -> None:
        x_axis = BlochSphericalCoordinates.from_cartesian((1.0, 0.0, 0.0))
        y_axis = BlochSphericalCoordinates.from_cartesian((0.0, 1.0, 0.0))
        south = BlochSphericalCoordinates.from_cartesian((0.0, 0.0, -1.0))
        self.assertAlmostEqual(x_axis.theta, math.pi / 2.0)
        self.assertAlmostEqual(x_axis.phi, 0.0)
        self.assertAlmostEqual(y_axis.phi, math.pi / 2.0)
        self.assertAlmostEqual(south.theta, math.pi)

    def test_first_order_channels_recover_bloch_axes(self) -> None:
        x, y, z = 0.2, -0.3, 0.4
        values = harmonics_from_bloch((x, y, z), degrees=(1,)).values()
        scale = math.sqrt(3.0 / (4.0 * math.pi))
        self.assertAlmostEqual(values["Y_1_1c"], -scale * x)
        self.assertAlmostEqual(values["Y_1_1s"], -scale * y)
        self.assertAlmostEqual(values["Y_1_0"], scale * z)

    def test_radius_weights_mixed_states(self) -> None:
        pure = harmonics_from_bloch((1.0, 0.0, 0.0), degrees=(1,)).values()
        mixed = harmonics_from_bloch((0.25, 0.0, 0.0), degrees=(1,)).values()
        center = harmonics_from_bloch((0.0, 0.0, 0.0), degrees=(1,)).values()
        self.assertAlmostEqual(mixed["Y_1_1c"], 0.25 * pure["Y_1_1c"])
        self.assertTrue(all(value == 0.0 for value in center.values()))

    def test_complete_degree_bank(self) -> None:
        frame = harmonics_from_bloch((0.1, 0.2, 0.9))
        self.assertEqual(len(frame.components), 15)
        self.assertEqual(frame.backend, "python-acoustics")

    def test_existing_spherical_stream_matches_cartesian(self) -> None:
        coords = BlochSphericalCoordinates.from_cartesian((0.2, 0.3, 0.4))
        cartesian = harmonics_from_bloch((0.2, 0.3, 0.4), degrees=(1, 2))
        spherical = harmonics_from_spherical(
            coords.r, coords.theta, coords.phi, degrees=(1, 2)
        )
        for name, value in cartesian.values().items():
            self.assertAlmostEqual(value, spherical.values()[name])

    def test_nonphysical_radius_is_clamped_without_losing_direction(self) -> None:
        coords = BlochSphericalCoordinates.from_cartesian((0.0, 0.0, 1.000001))
        self.assertEqual(coords.r, 1.0)
        self.assertEqual(coords.theta, 0.0)

    def test_degree_parser(self) -> None:
        self.assertEqual(parse_harmonic_degrees("1,2,3"), (1, 2, 3))
        self.assertEqual(parse_harmonic_degrees("3,1,3"), (3, 1))
        self.assertEqual(parse_harmonic_degrees("off"), ())

    def test_spin_engine_publishes_qubit_and_global_harmonics(self) -> None:
        recorder = RecordingOSCClient()
        with patch(
            "quantum_spin_polarization_engine_v3_measurement_basis.SimpleUDPClient",
            return_value=recorder,
        ):
            engine = QuantumSpinPolarizationEngine(
                EngineConfig(n_qubits=1, init_state="plus", harmonic_degrees=(1,))
            )
        data = engine.qubit_spin_polarization(0)
        engine.send_qubit_osc(data)
        engine.send_global_osc([data], {})

        messages = recorder.values()
        scale = math.sqrt(3.0 / (4.0 * math.pi))
        self.assertAlmostEqual(messages["/qubit/0/harmonic/Y_1_1c"], -scale)
        self.assertAlmostEqual(messages["/qubit/0/harmonic/Y_1_1s"], 0.0)
        self.assertAlmostEqual(messages["/qubit/0/harmonic/Y_1_0"], 0.0)
        self.assertAlmostEqual(messages["/global/harmonic/Y_1_1c"], -scale)
        self.assertEqual(
            messages["/qmw/acoustics/spat/source/1/aed"],
            [0.0, 0.0, 1.0],
        )
        self.assertIn("/qmw/acoustics/reverb/resonance", messages)
        self.assertEqual(len(messages["/qmw/acoustics/modal/weights"]), 8)

    def test_spin_engine_can_disable_harmonics(self) -> None:
        recorder = RecordingOSCClient()
        with patch(
            "quantum_spin_polarization_engine_v3_measurement_basis.SimpleUDPClient",
            return_value=recorder,
        ):
            engine = QuantumSpinPolarizationEngine(
                EngineConfig(n_qubits=1, init_state="plus", harmonic_degrees=())
            )
        engine.send_qubit_osc(engine.qubit_spin_polarization(0))
        self.assertFalse(
            any("/harmonic/" in address for address, _ in recorder.messages)
        )

    def test_spat_coordinates_follow_bloch_direction(self) -> None:
        controls = controls_from_bloch((0.0, 1.0, 0.0))
        self.assertAlmostEqual(controls.spat.azimuth_degrees, 90.0)
        self.assertAlmostEqual(controls.spat.elevation_degrees, 0.0)
        self.assertAlmostEqual(controls.spat.aperture_degrees, 20.0)
        self.assertAlmostEqual(controls.spat.spread_percent, 0.0)

    def test_mixed_state_becomes_diffuse_and_controls_remain_bounded(self) -> None:
        controls = controls_from_bloch((0.0, 0.0, 0.0))
        self.assertEqual(controls.spat.aperture_degrees, 160.0)
        self.assertEqual(controls.spat.spread_percent, 100.0)
        self.assertTrue(0.0 <= controls.reverb.resonance <= 1.0)
        self.assertTrue(0.45 <= controls.reverb.decay <= 0.97)
        self.assertTrue(0.05 <= controls.reverb.damping <= 0.90)
        self.assertTrue(all(0.35 <= weight <= 1.65 for weight in controls.reverb.mode_weights))


if __name__ == "__main__":
    unittest.main()
