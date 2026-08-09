import unittest
from types import SimpleNamespace
from unittest.mock import patch

import numpy as np

from density.grw_event_channel_v1 import ghz_density
from density.measurement_instrument_v1 import ProjectiveMeasurementInstrument


def ket_density(index: int) -> np.ndarray:
    ket = np.zeros(16, dtype=np.complex128)
    ket[index] = 1.0
    return np.outer(ket, ket.conj())


class ProjectiveMeasurementInstrumentTests(unittest.TestCase):
    def test_probe_samples_without_changing_state_or_revision(self):
        rho = ghz_density()
        instrument = ProjectiveMeasurementInstrument(seed=8)
        event = instrument.measure(
            rho,
            basis="Y",
            mode="probe",
            logical_time=2.5,
            revision_before=17,
            request_id=91,
        )
        np.testing.assert_allclose(event.rho_after, rho, atol=1e-13)
        np.testing.assert_allclose(event.delta_rho, 0.0, atol=1e-13)
        self.assertEqual(event.revision_after, 17)
        self.assertFalse(event.changed_state)

    def test_collapse_is_projective_and_revisioned(self):
        instrument = ProjectiveMeasurementInstrument(seed=2)
        event = instrument.measure(
            ghz_density(),
            basis="Z",
            mode="collapse",
            logical_time=1.0,
            revision_before=4,
        )
        self.assertIn(event.outcome, (0, 15))
        np.testing.assert_allclose(event.rho_after, ket_density(event.outcome), atol=1e-13)
        self.assertEqual(event.revision_after, 5)
        self.assertTrue(event.changed_state)
        self.assertGreater(event.trace_distance, 0.70)


class _RecordingClient:
    instances = []

    def __init__(self, *_args, **_kwargs):
        self.messages = []
        self.__class__.instances.append(self)

    def send_message(self, address, value):
        self.messages.append((address, value))


class _Bridge:
    def __init__(self):
        self.client = _RecordingClient()
        self.registry_circuit = SimpleNamespace(active_measurement_bases=lambda: [])


class AuthoritativeMeasurementEngineTests(unittest.TestCase):
    def setUp(self):
        from density.density_matrix_engine_4q import DensityMatrixEngine

        self.engine = DensityMatrixEngine(enable_circuit_bridge_control=False)
        old_socket = getattr(self.engine.qmw_bridge.client, "_sock", None)
        if old_socket is not None:
            old_socket.close()
        self.engine.qmw_bridge = _Bridge()

    def test_engine_owns_collapse_and_publishes_legacy_addresses(self):
        self.engine.rho = ghz_density()
        revision_before = self.engine.state_revision
        event = self.engine.perform_measurement(
            basis="Z", mode="collapse", request_id=12
        )

        self.assertIs(event, self.engine.last_measurement_event)
        np.testing.assert_allclose(self.engine.rho, event.rho_after)
        self.assertEqual(self.engine.state_revision, revision_before + 1)
        self.assertEqual(self.engine.last_event_type, "explicit_measurement")
        addresses = {address for address, _value in self.engine.qmw_bridge.client.messages}
        self.assertIn("/quantum/measurement/outcome", addresses)
        self.assertIn("/quantum/measurement/flash", addresses)
        self.assertIn("/quantum/state/event/measurement", addresses)

    def test_engine_probe_does_not_change_authoritative_state(self):
        rho_before = self.engine.rho.copy()
        revision_before = self.engine.state_revision
        event = self.engine.perform_measurement(
            basis="X", mode="probe", request_id=13
        )
        np.testing.assert_allclose(self.engine.rho, rho_before)
        self.assertEqual(self.engine.state_revision, revision_before)
        self.assertEqual(event.revision_after, revision_before)
        self.assertEqual(self.engine.last_event_type, "measurement_probe")

    def test_osc_request_replies_with_event_and_canonical_rho(self):
        _RecordingClient.instances.clear()
        rho_before = self.engine.rho.copy()
        with patch("pythonosc.udp_client.SimpleUDPClient", _RecordingClient):
            self.engine._osc_measure(
                "/quantum/state/control/measure",
                "Z",
                "collapse",
                77,
                7451,
                "127.0.0.1",
            )
            # The threaded callback must not mutate canonical state.
            np.testing.assert_allclose(self.engine.rho, rho_before)
            self.engine._drain_measurement_requests()
        reply = _RecordingClient.instances[-1]
        addresses = [address for address, _value in reply.messages]
        self.assertEqual(
            addresses,
            ["/quantum/state/event/measurement", "/quantum/state/event/rho"],
        )
        rho_payload = reply.messages[-1][1]
        self.assertEqual(rho_payload[0], self.engine.state_revision)
        self.assertEqual(rho_payload[1], 16)
        self.assertEqual(len(rho_payload), 2 + 2 * 16 * 16)

    def test_invalid_queued_request_does_not_crash_state_thread(self):
        self.engine._osc_measure(
            "/quantum/state/control/measure",
            "INVALID",
            "collapse",
            88,
        )
        events = self.engine._drain_measurement_requests()
        self.assertEqual(events, [])
        address, payload = self.engine.qmw_bridge.client.messages[-1]
        self.assertEqual(address, "/quantum/measurement/error")
        self.assertEqual(payload[0], 88)


if __name__ == "__main__":
    unittest.main()
