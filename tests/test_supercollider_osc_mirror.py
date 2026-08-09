import unittest
from unittest.mock import patch

import quantum_population_osc_v9_resonator as resonator
from quantumsonification_conductor import (
    ConductorConfig,
    OSCConfig,
    QuantumSonificationConductor,
)


class MirroredOSCClientTests(unittest.TestCase):
    def test_sends_identical_packet_to_primary_and_supercollider(self):
        with patch.object(resonator, "SimpleUDPClient") as client_factory:
            primary = unittest.mock.Mock()
            supercollider = unittest.mock.Mock()
            client_factory.side_effect = [primary, supercollider]

            client = resonator.MirroredOSCClient(
                "127.0.0.1",
                7400,
                mirror_ports=(57120,),
            )
            client.send_message("/qmw/density_field/purity", 0.75)

        self.assertEqual(
            client_factory.call_args_list,
            [
                unittest.mock.call("127.0.0.1", 7400),
                unittest.mock.call("127.0.0.1", 57120),
            ],
        )
        primary.send_message.assert_called_once_with(
            "/qmw/density_field/purity", 0.75
        )
        supercollider.send_message.assert_called_once_with(
            "/qmw/density_field/purity", 0.75
        )

    def test_deduplicates_matching_primary_and_mirror_ports(self):
        with patch.object(resonator, "SimpleUDPClient") as client_factory:
            client_factory.return_value = unittest.mock.Mock()
            resonator.MirroredOSCClient(
                "127.0.0.1",
                57120,
                mirror_ports=(57120,),
            )

        client_factory.assert_called_once_with("127.0.0.1", 57120)

    def test_conductor_forwards_optional_supercollider_port(self):
        conductor = object.__new__(QuantumSonificationConductor)
        conductor.config = ConductorConfig(
            osc=OSCConfig(supercollider_port=57120)
        )

        command = conductor._build_engine_command()

        self.assertIn("--sc-osc-port=57120", command)


if __name__ == "__main__":
    unittest.main()
