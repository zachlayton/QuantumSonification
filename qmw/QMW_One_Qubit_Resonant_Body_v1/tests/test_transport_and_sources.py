from __future__ import annotations

from dataclasses import replace
from http.client import HTTPConnection
import json
from pathlib import Path
import threading
import unittest

from qmw_one_qubit.mapping import observe_one_qubit, resonant_body_frame
from qmw_one_qubit.physics import OneQubitEngine
from qmw_one_qubit.runtime import Handler, InstrumentHTTPServer, InstrumentRuntime
from qmw_one_qubit.transport import FRAME_ADDRESS, SCHEMA, frame_payload, osc_arguments


ROOT = Path(__file__).resolve().parents[1]


class TransportAndSourceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.observation = observe_one_qubit(OneQubitEngine().snapshot())
        self.body = resonant_body_frame(self.observation)

    def test_json_and_osc_are_complete_revisioned_frames(self) -> None:
        payload = frame_payload(self.observation, self.body, running=True)
        self.assertEqual(payload["schema"], SCHEMA)
        self.assertEqual(payload["revision"], self.observation.revision)
        self.assertIn("energy_gap_over_hbar_rad_per_second", payload["physics"])
        self.assertEqual(len(payload["sound_adapter"]["modes"]), 9)
        arguments = osc_arguments(self.observation, self.body)
        self.assertEqual(FRAME_ADDRESS, "/qmw/one_qubit/v1/frame")
        self.assertEqual(len(arguments), 47)
        self.assertEqual(arguments[0], self.observation.revision)

    def test_mismatched_revisions_are_rejected(self) -> None:
        mismatched = replace(self.body, observation_revision=self.observation.revision + 1)
        with self.assertRaisesRegex(ValueError, "revisions"):
            frame_payload(self.observation, mismatched, running=False)
        with self.assertRaisesRegex(ValueError, "revisions"):
            osc_arguments(self.observation, mismatched)

    def test_runtime_control_path_keeps_physics_and_sound_separate(self) -> None:
        runtime = InstrumentRuntime(osc_enabled=False)
        rho_before = runtime.engine.snapshot().rho.copy()
        runtime.apply({"action": "set_sound", "master": 0.0, "sound_locked": False})
        self.assertEqual(runtime.snapshot()["sound_adapter"]["master"], 0.0)
        self.assertEqual(runtime.snapshot()["sound_adapter"]["sound_locked"], False)
        self.assertTrue((runtime.engine.snapshot().rho == rho_before).all())
        runtime.apply({"action": "set_physics", "omega_rad_per_second": [0, 0, 2], "t1_seconds": 0, "tphi_seconds": 0})
        self.assertEqual(runtime.snapshot()["physics"]["omega_rad_per_second"], [0.0, 0.0, 2.0])

    def test_standard_library_http_state_and_control_round_trip(self) -> None:
        runtime = InstrumentRuntime(osc_enabled=False)
        runtime.running = False
        try:
            server = InstrumentHTTPServer(("127.0.0.1", 0), Handler)
        except PermissionError:
            runtime.close()
            self.skipTest("sandbox does not permit a loopback listening socket")
        server.runtime = runtime
        worker = threading.Thread(target=server.serve_forever, daemon=True)
        worker.start()
        connection = HTTPConnection("127.0.0.1", server.server_address[1], timeout=2)
        try:
            connection.request("GET", "/api/state")
            response = connection.getresponse()
            state = json.loads(response.read())
            self.assertEqual(response.status, 200)
            self.assertEqual(state["schema"], SCHEMA)
            body = json.dumps({"action": "prepare", "state": "+"})
            connection.request(
                "POST",
                "/api/control",
                body=body,
                headers={"Content-Type": "application/json"},
            )
            response = connection.getresponse()
            state = json.loads(response.read())
            self.assertEqual(response.status, 200)
            self.assertAlmostEqual(state["physics"]["bloch"][0], 1.0)
        finally:
            connection.close()
            server.shutdown()
            server.server_close()
            runtime.close()
            worker.join(timeout=2)

    def test_html_is_self_contained_and_labels_semantic_boundaries(self) -> None:
        source = (ROOT / "web" / "index.html").read_text(encoding="utf-8")
        self.assertIn("PHYSICS", source)
        self.assertIn("OBSERVABLES", source)
        self.assertIn("SOUND ADAPTER", source)
        self.assertIn("MEASURE Z", source)
        self.assertIn("state r", source)
        self.assertIn("Hamiltonian axis", source)
        self.assertIn("fetch('/api/state'", source)
        self.assertNotIn("https://", source)

    def test_supercollider_is_one_signed_modal_body_with_hard_gate(self) -> None:
        source = (ROOT / "supercollider" / "QMWOneQubitResonantBodyV1.scd").read_text(encoding="utf-8")
        self.assertIn("Ringz.ar", source)
        self.assertIn("NamedControl.kr(\\weights", source)
        self.assertIn("weights.clip(-1, 1)", source)
        self.assertIn("(1 - soundLocked.clip(0, 1)) * master.clip(0, 1)", source)
        self.assertIn("'/qmw/one_qubit/v1/frame'", source)
        self.assertIn("message.size != 48", source)
        self.assertIn("QMW_ONE_QUBIT_SC_SELF_TEST_OK", source)
        self.assertNotIn("SinOsc.ar", source)


if __name__ == "__main__":
    unittest.main()
