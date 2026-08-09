from __future__ import annotations

import unittest

import numpy as np

from surface_material_models_v1 import SurfaceModalPacket

from .living_spectral_geometry_v1 import track_modal_identity


def packet(values: np.ndarray, vectors: np.ndarray) -> SurfaceModalPacket:
    count = len(values)
    frequencies = np.sqrt(np.maximum(values, 0.0)) * 100.0
    return SurfaceModalPacket(
        model="surface_laplacian",
        eigenvalues=np.asarray(values),
        eigenvectors=np.asarray(vectors),
        frequencies_hz=frequencies,
        angular_frequencies=2.0 * np.pi * frequencies,
        decay_times_seconds=np.ones(count),
        damping_rates=np.ones(count),
        mode_weights=np.ones(count),
        metadata={},
    )


class LivingModalSubspaceIntegrationTests(unittest.TestCase):
    def test_degenerate_rotation_preserves_cluster_and_stable_ids(self) -> None:
        initial, score, frame = track_modal_identity(
            None,
            packet(np.array([1.0, 1.0, 3.0]), np.eye(3)),
            mass=np.ones(3),
            topology_id="mesh:test",
        )
        self.assertIsNone(score)
        angle = 0.71
        rotation = np.array(
            [
                [np.cos(angle), -np.sin(angle), 0.0],
                [np.sin(angle), np.cos(angle), 0.0],
                [0.0, 0.0, 1.0],
            ]
        )
        updated, score, next_frame = track_modal_identity(
            frame,
            packet(np.array([1.0001, 0.9999, 3.01]), rotation),
            mass=np.ones(3),
            topology_id="mesh:test",
        )
        self.assertEqual(next_frame.mode_stable_ids, frame.mode_stable_ids)
        self.assertEqual(
            next_frame.clusters[0].cluster_id,
            frame.clusters[0].cluster_id,
        )
        self.assertGreater(score, 0.999999)
        np.testing.assert_allclose(updated.eigenvectors, initial.eigenvectors, atol=1e-12)
        self.assertEqual(
            updated.metadata["mode_tracking"],
            "mass_weighted_invariant_subspace",
        )

    def test_topology_change_is_declared_and_allocates_fresh_ids(self) -> None:
        _, _, frame = track_modal_identity(
            None,
            packet(np.array([1.0, 2.0]), np.eye(2)),
            mass=np.ones(2),
            topology_id="mesh:a",
        )
        updated, score, next_frame = track_modal_identity(
            frame,
            packet(np.array([1.1, 2.1]), np.eye(2)),
            mass=np.ones(2),
            topology_id="mesh:b",
        )
        self.assertIsNone(score)
        self.assertTrue(updated.metadata["tracking_discontinuity"])
        self.assertTrue(
            set(next_frame.mode_stable_ids).isdisjoint(frame.mode_stable_ids)
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
