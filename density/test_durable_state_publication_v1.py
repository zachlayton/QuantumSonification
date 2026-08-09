import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

import numpy as np

from density.durable_state_publication_v1 import (
    DurableStatePublisher,
    DurableStateReplay,
    StatePublicationConfig,
    StatePublicationError,
    rho_sha256,
)
from density.grw_event_channel_v1 import GRWConfig, ghz_density


def basis_density(index: int) -> np.ndarray:
    ket = np.zeros(16, dtype=complex)
    ket[index] = 1.0
    return np.outer(ket, ket.conj())


class DurableStatePublisherTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name) / "state"
        self.config = StatePublicationConfig(
            directory=self.root,
            checkpoint_interval_events=2,
            fsync=False,
            session_id="test-session",
        )
        self.publisher = DurableStatePublisher(self.config)

    def tearDown(self):
        self.tempdir.cleanup()

    def test_atomic_current_revision_packets_ledger_and_checkpoint(self):
        rho0 = basis_density(0)
        rho1 = basis_density(9)
        first = self.publisher.append_transition(
            event_type="reset",
            rho_after=rho0,
            revision=0,
            logical_time=0.0,
            event_id=0,
            configuration_revision=1,
            metadata={"seed": 23},
            rho_before=rho0,
            force_checkpoint=False,
        )
        second = self.publisher.append_transition(
            event_type="explicit_measurement",
            rho_after=rho1,
            revision=1,
            logical_time=0.25,
            event_id=1,
            configuration_revision=2,
            metadata={"basis": "Z", "outcome": 9},
            rho_before=rho0,
            delta_rho=rho1 - rho0,
        )

        self.assertTrue((self.root / "current_state.npz").exists())
        self.assertTrue((self.root / "current_state.json").exists())
        self.assertTrue((self.root / first["state_packet"]).exists())
        self.assertTrue((self.root / second["state_packet"]).exists())
        self.assertIsNone(first["checkpoint"])
        self.assertTrue((self.root / second["checkpoint"]).exists())

        with np.load(self.root / "current_state.npz", allow_pickle=False) as packet:
            np.testing.assert_allclose(packet["rho"], rho1)
            self.assertEqual(int(packet["revision"]), 1)
            self.assertEqual(str(packet["rho_sha256"]), rho_sha256(rho1))
        manifest = json.loads((self.root / "current_state.json").read_text())
        self.assertEqual(manifest["revision"], 1)
        self.assertEqual(manifest["event_type"], "explicit_measurement")
        self.assertEqual(len((self.root / "events.jsonl").read_text().splitlines()), 2)

    def test_revision_collision_with_different_state_is_rejected(self):
        self.publisher.publish_state(
            basis_density(0), revision=3, logical_time=0.0
        )
        with self.assertRaises(StatePublicationError):
            self.publisher.publish_state(
                basis_density(1), revision=3, logical_time=0.1
            )

    def test_reopen_recovers_sequence_and_new_session_avoids_revision_collision(self):
        self.publisher.append_transition(
            event_type="circuit_gate",
            rho_after=basis_density(0),
            revision=0,
            logical_time=0.0,
            event_id=1,
            configuration_revision=0,
        )
        other = DurableStatePublisher(
            StatePublicationConfig(
                self.root,
                fsync=False,
                session_id="second-session",
            )
        )
        record = other.append_transition(
            event_type="reset",
            rho_after=basis_density(15),
            revision=0,
            logical_time=0.0,
            event_id=0,
            configuration_revision=1,
        )
        self.assertEqual(record["sequence"], 2)
        self.assertIn("second-session", record["state_packet"])

    def test_replay_verifies_and_reconstructs_exact_states(self):
        states = [basis_density(0), basis_density(3), basis_density(15)]
        event_types = ["circuit_gate", "explicit_measurement", "spontaneous_localization"]
        for revision, (rho, event_type) in enumerate(zip(states, event_types)):
            self.publisher.append_transition(
                event_type=event_type,
                rho_after=rho,
                revision=revision,
                logical_time=revision * 0.5,
                event_id=revision + 1,
                configuration_revision=revision,
            )

        replay = DurableStateReplay(self.root, session_id="test-session")
        frames = list(replay.replay())
        self.assertEqual(replay.verify(), 3)
        self.assertEqual([frame.event_type for frame in frames], event_types)
        for frame, expected in zip(frames, states):
            np.testing.assert_array_equal(frame.rho, expected)
        np.testing.assert_array_equal(replay.current_state(), states[-1])


class _RecordingClient:
    def __init__(self):
        self.messages = []

    def send_message(self, address, value):
        self.messages.append((address, value))


class _Circuit:
    def to_openqasm2_lines(self):
        return ["OPENQASM 2.0;"]


class _Bridge:
    def __init__(self):
        self.client = _RecordingClient()
        self.circuit = _Circuit()
        self.registry_circuit = SimpleNamespace(active_measurement_bases=lambda: [])
        self.gate_due = True
        x = np.array([[0, 1], [1, 0]], dtype=complex)
        identity = np.eye(2, dtype=complex)
        self.x0 = np.kron(np.kron(np.kron(x, identity), identity), identity)

    def apply_due_circuit_column(self, rho, _dt):
        if not self.gate_due:
            return rho, None, []
        self.gate_due = False
        return self.x0 @ rho @ self.x0, 0, ["X q0"]

    def update_and_send(self, _rho, *_args):
        return {}


class DurableStateEngineIntegrationTests(unittest.TestCase):
    def test_engine_automatically_records_circuit_measurement_and_grw(self):
        from density.density_matrix_engine_4q import DensityMatrixEngine

        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir) / "history"
            engine = DensityMatrixEngine(
                enable_circuit_bridge_control=False,
                state_publication=StatePublicationConfig(
                    root,
                    checkpoint_interval_events=1,
                    fsync=False,
                    session_id="engine-test",
                ),
                grw_config=GRWConfig(
                    enabled=True,
                    rate_hz=1.0,
                    width=0.1,
                    basis_source="Z",
                    seed=55,
                ),
            )
            old_socket = getattr(engine.qmw_bridge.client, "_sock", None)
            if old_socket is not None:
                old_socket.close()
            engine.qmw_bridge = _Bridge()

            engine.step(0.01)
            engine.perform_measurement("X", "collapse", request_id=4)
            engine.grw.next_event_time = engine.logical_time + 0.005
            engine.step(0.01)

            replay = DurableStateReplay(root, session_id="engine-test")
            frames = list(replay.replay())
            event_types = [frame.event_type for frame in frames]
            self.assertIn("reset", event_types)
            self.assertIn("circuit_gate", event_types)
            self.assertIn("explicit_measurement", event_types)
            self.assertIn("spontaneous_localization", event_types)
            self.assertEqual(replay.verify(), len(frames))
            np.testing.assert_allclose(replay.current_state(), engine.rho)
            self.assertTrue(all(frame.record["checkpoint"] for frame in frames))


if __name__ == "__main__":
    unittest.main()
