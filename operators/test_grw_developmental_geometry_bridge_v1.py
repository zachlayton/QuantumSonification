from pathlib import Path
import tempfile
import unittest

import numpy as np

from operators.grw_developmental_geometry_bridge_v1 import (
    GRWDevelopmentalGeometryBridge,
    GRWFrameAssembler,
    GRWGeometryConfig,
    GeometryGRWEvent,
    GeometryProjection,
    SalienceBatcher,
)
from operators.living_spectral_geometry_osc_v1 import (
    LivingOSCConfig,
    LivingSpectralGeometryOSCPublisher,
)


class RecordingClient:
    def __init__(self):
        self.messages = []

    def send_message(self, address, value):
        self.messages.append((address, value))


class FakeLiving:
    def __init__(self):
        self.quantum_updates = []
        self.geometry_updates = []
        self.listeners = []

    def subscribe(self, listener):
        self.listeners.append(listener)
        return lambda: self.listeners.remove(listener)

    def update_quantum_state(self, rho, **kwargs):
        self.quantum_updates.append((np.asarray(rho).copy(), kwargs))

    def update_geometry(self, vertices, faces, **kwargs):
        self.geometry_updates.append(
            (np.asarray(vertices).copy(), np.asarray(faces).copy(), kwargs)
        )
        return 5


def transition(event_id: int, salience: float, received_time: float):
    before = np.diag([1.0, 0.0]).astype(complex)
    after = np.diag([0.0, 1.0]).astype(complex)
    return GeometryGRWEvent(
        event_id=event_id,
        salience=salience,
        branch=1,
        audible=True,
        rho_after=after,
        delta_rho=after - before,
        received_time=received_time,
    )


def geometry_fixture():
    vertices = np.array(
        [[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0]]
    )
    faces = np.array([[0, 1, 2]], dtype=int)
    eigenvectors = np.array(
        [[1.0, 1.0], [1.0, -0.5], [1.0, -0.5]], dtype=float
    )
    projection = GeometryProjection(
        geometric_eigenvectors=eigenvectors,
        channel_isometry=np.eye(2, dtype=complex),
        environment_dimension=1,
    )
    return vertices, faces, projection


class GRWDevelopmentalGeometryTests(unittest.TestCase):
    def test_generated_ir_uses_ready_crossfade_committed_activation(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            bundle = root / "living.npz"
            ir = root / "candidate.wav"
            ir.touch()
            np.savez(
                bundle,
                eigenvalues=np.array([1.0, 2.0]),
                frequencies_hz=np.array([110.0, 220.0]),
                mode_probabilities=np.array([0.4, 0.6]),
                decay_times_seconds=np.array([0.5, 0.7]),
                damping_rates=np.array([2.0, 1.4]),
                mode_weights=np.ones(2),
                mode_amplitudes=np.sqrt([0.4, 0.6]).astype(complex),
            )
            client = RecordingClient()
            publisher = LivingSpectralGeometryOSCPublisher(
                client,
                LivingOSCConfig(
                    crossfade_ms=1500.0,
                    activation_timeout_seconds=0.0,
                ),
            )
            state = {
                "revision": 3,
                "material_model": "surface_laplacian",
                "mode_count": 2,
                "paths": {
                    "bundle_npz": str(bundle),
                    "ir_wav": str(ir),
                    "directory": str(root),
                },
                "descriptors": {},
            }
            self.assertTrue(publisher.publish_state(state))
            self.assertEqual(publisher.candidate.status, "candidate")
            publisher.handle_ready("/living/ir/ready", 3)
            self.assertEqual(publisher.candidate.status, "ready")
            publisher.handle_committed("/living/ir/committed", 3)
            self.assertEqual(publisher.active.status, "committed")
            addresses = [address for address, _ in client.messages]
            self.assertLess(
                addresses.index("/living/ir/candidate"),
                addresses.index("/living/ir/crossfade/start"),
            )
            self.assertIn("/living/ir/active/revision", addresses)
            publisher.close()

    def test_frame_assembler_commits_only_after_complete_event(self):
        assembler = GRWFrameAssembler()
        before = np.diag([1.0, 0.0]).astype(complex)
        after = np.diag([0.0, 1.0]).astype(complex)
        delta = after - before
        self.assertIsNone(
            assembler.ingest("post/rho_real", tuple(after.real.reshape(-1)))
        )
        assembler.ingest("post/rho_imag", tuple(after.imag.reshape(-1)))
        assembler.ingest("delta/real", tuple(delta.real.reshape(-1)))
        with self.assertRaises(ValueError):
            assembler.ingest("event", (1, 1, 0.5, 0, 0, 0, 3, 1, 0, 1))
        assembler.ingest("delta/imag", tuple(delta.imag.reshape(-1)))
        event = assembler.ingest(
            "event", (1, 1, 0.5, 0, 0, 0, 3, 1, 0, 1), now=4.0
        )
        self.assertEqual(event.event_id, 1)
        self.assertAlmostEqual(event.salience, 0.5)
        np.testing.assert_allclose(event.rho_after, after)
        np.testing.assert_allclose(event.delta_rho, delta)

    def test_legacy_coupling_projection_supports_pre_isometry_archives(self):
        vectors = np.array([[1.0, 1.0], [1.0, -1.0], [0.5, 0.25]])
        coupling = np.random.default_rng(4).normal(size=(2, 9))
        projection = GeometryProjection(
            geometric_eigenvectors=vectors,
            coupling_matrix=coupling,
        )
        event = transition(1, 0.5, 1.0)
        comparison = projection.compare(event.rho_after, event.delta_rho)
        self.assertAlmostEqual(float(np.sum(comparison.pre_probabilities)), 1.0)
        self.assertAlmostEqual(float(np.sum(comparison.post_probabilities)), 1.0)
        self.assertEqual(len(comparison.probability_delta), 2)

    def test_batcher_accumulates_threshold_and_respects_slow_gate(self):
        config = GRWGeometryConfig(
            batch_salience_threshold=0.5,
            minimum_batch_events=2,
            regeneration_interval_seconds=10.0,
        )
        batcher = SalienceBatcher(config, start_time=0.0)
        batcher.ingest(transition(1, 0.3, 1.0))
        batcher.ingest(transition(2, 0.3, 2.0))
        self.assertFalse(batcher.ready(9.9))
        self.assertTrue(batcher.ready(10.0))
        events = batcher.take(10.0)
        self.assertEqual([event.event_id for event in events], [1, 2])
        self.assertFalse(batcher.ready(20.0))

    def test_latency_flushes_a_single_accumulated_event(self):
        config = GRWGeometryConfig(
            batch_salience_threshold=1.0,
            minimum_batch_events=2,
            maximum_batch_latency_seconds=5.0,
            regeneration_interval_seconds=0.0,
        )
        batcher = SalienceBatcher(config, start_time=0.0)
        batcher.ingest(transition(1, 0.1, 2.0))
        self.assertFalse(batcher.ready(6.9))
        self.assertTrue(batcher.ready(7.0))

    def test_two_hits_schedule_one_mesh_and_acoustic_revision(self):
        living = FakeLiving()
        client = RecordingClient()
        vertices, faces, projection = geometry_fixture()
        bridge = GRWDevelopmentalGeometryBridge(
            living,
            vertices,
            faces,
            projection,
            GRWGeometryConfig(
                batch_salience_threshold=0.5,
                minimum_batch_events=2,
                regeneration_interval_seconds=0.0,
                perturbation_gain=0.1,
                developmental_persistence=0.0,
                smoothing_iterations=0,
            ),
            status_client=client,
            clock=lambda: 0.0,
        )

        bridge.ingest(transition(1, 0.3, 1.0))
        self.assertIsNone(bridge.poll(1.0))
        self.assertEqual(len(living.geometry_updates), 0)
        bridge.ingest(transition(2, 0.3, 2.0))
        batch = bridge.poll(2.0)

        self.assertIsNotNone(batch)
        self.assertEqual(batch.event_ids, (1, 2))
        self.assertEqual(batch.strongest_mode, 1)
        self.assertEqual(batch.scheduled_revision, 5)
        self.assertEqual(len(living.quantum_updates), 1)
        self.assertEqual(len(living.geometry_updates), 1)
        deformed = living.geometry_updates[0][0]
        self.assertGreater(float(np.max(np.abs(deformed - vertices))), 0.0)
        self.assertIn(
            "/living/grw/batch",
            [address for address, _ in client.messages],
        )

    def test_inaudible_and_subfloor_events_never_enter_batch(self):
        config = GRWGeometryConfig(salience_floor=0.1)
        batcher = SalienceBatcher(config, start_time=0.0)
        quiet = transition(1, 0.05, 1.0)
        inaudible = GeometryGRWEvent(
            **{**transition(2, 0.5, 2.0).__dict__, "audible": False}
        )
        self.assertFalse(batcher.ingest(quiet))
        self.assertFalse(batcher.ingest(inaudible))
        self.assertEqual(batcher.pending, [])


if __name__ == "__main__":
    unittest.main()
