from __future__ import annotations

import unittest

import numpy as np
from scipy import sparse

from quantumsonification_foundations_v1.geometry.modal_subspace_tracker_v1 import (
    ModalSubspaceTracker,
    ModalTrackingConfig,
    generalized_eigen_residuals,
    mass_orthonormality_error,
)


class ModalSubspaceTrackerTests(unittest.TestCase):
    def test_sign_phase_and_solver_permutation_do_not_change_ids(self) -> None:
        tracker = ModalSubspaceTracker()
        initial = tracker.initialize(
            np.array([1.0, 2.0, 4.0]),
            np.eye(3),
        )

        permutation = np.array([2, 0, 1])
        values = np.array([1.02, 2.03, 4.04])[permutation]
        vectors = np.eye(3)[:, permutation].astype(np.complex128)
        vectors[:, 0] *= -1.0
        vectors[:, 1] *= 1j
        updated = tracker.update(values, vectors)

        self.assertEqual(updated.mode_stable_ids, initial.mode_stable_ids)
        np.testing.assert_allclose(
            updated.aligned_basis,
            initial.aligned_basis,
            atol=1e-12,
        )

    def test_rotated_degenerate_basis_tracks_invariant_subspace(self) -> None:
        tracker = ModalSubspaceTracker(
            ModalTrackingConfig(relative_gap_tolerance=1e-2)
        )
        initial = tracker.initialize(
            np.array([1.0, 1.0, 3.0]),
            np.eye(3),
        )

        angle = 0.73
        rotation = np.array(
            [
                [np.cos(angle), -np.sin(angle), 0.0],
                [np.sin(angle), np.cos(angle), 0.0],
                [0.0, 0.0, 1.0],
            ]
        )
        updated = tracker.update(
            np.array([1.0001, 0.9999, 3.05]),
            rotation,
        )

        self.assertEqual(updated.clusters[0].cluster_id, initial.clusters[0].cluster_id)
        self.assertEqual(updated.clusters[0].stable_mode_ids, (0, 1))
        self.assertTrue(updated.clusters[0].is_degenerate)
        self.assertLess(float(np.max(updated.clusters[0].principal_angles_radians)), 2e-8)
        np.testing.assert_allclose(updated.aligned_basis, initial.aligned_basis, atol=1e-12)

    def test_mass_weighted_basis_is_orthonormal(self) -> None:
        mass = np.array([1.0, 2.0, 4.0])
        raw = np.eye(3)
        tracker = ModalSubspaceTracker()
        frame = tracker.initialize(
            np.array([1.0, 2.0, 3.0]),
            raw,
            mass=mass,
        )
        self.assertLess(mass_orthonormality_error(frame.aligned_basis, mass), 1e-12)
        expected = np.diag([1.0, 1.0 / np.sqrt(2.0), 0.5])
        np.testing.assert_allclose(frame.aligned_basis, expected, atol=1e-12)

    def test_indefinite_sparse_mass_is_rejected(self) -> None:
        mass = sparse.diags([1.0, -1.0], format="csr")
        with self.assertRaisesRegex(ValueError, "positive definite"):
            ModalSubspaceTracker().initialize(
                np.array([1.0]),
                np.array([[1.0], [0.0]]),
                mass=mass,
            )

    def test_topology_change_requires_an_explicit_transfer(self) -> None:
        tracker = ModalSubspaceTracker()
        tracker.initialize(
            np.array([1.0, 2.0]),
            np.eye(2),
            topology_id="mesh-a",
        )
        with self.assertRaisesRegex(ValueError, "transfer matrix"):
            tracker.update(
                np.array([1.1, 2.1]),
                np.eye(2),
                topology_id="mesh-b",
            )

    def test_transfer_matrix_preserves_old_modes_and_adds_a_new_id(self) -> None:
        tracker = ModalSubspaceTracker()
        initial = tracker.initialize(
            np.array([1.0, 2.0, 3.0]),
            np.eye(3),
            topology_id="coarse",
        )
        transfer = np.zeros((4, 3))
        transfer[:3, :] = np.eye(3)
        new_vectors = np.eye(4)
        updated = tracker.update(
            np.array([1.01, 2.01, 3.01, 5.0]),
            new_vectors,
            topology_id="refined",
            transfer_matrix=transfer,
        )
        self.assertEqual(updated.mode_stable_ids[:3], initial.mode_stable_ids)
        self.assertNotIn(updated.mode_stable_ids[3], initial.mode_stable_ids)
        self.assertTrue(updated.metadata["topology_changed"])

    def test_generalized_eigen_residuals_are_zero_for_exact_pairs(self) -> None:
        operator = np.diag([1.0, 2.0, 4.0])
        values = np.array([1.0, 2.0, 4.0])
        vectors = np.eye(3)
        residuals = generalized_eigen_residuals(
            operator,
            None,
            values,
            vectors,
        )
        np.testing.assert_allclose(residuals, 0.0, atol=1e-15)

    def test_bad_generalized_eigenpair_has_visible_residual(self) -> None:
        operator = np.diag([1.0, 2.0])
        values = np.array([1.0, 3.0])
        residuals = generalized_eigen_residuals(
            operator,
            None,
            values,
            np.eye(2),
        )
        self.assertAlmostEqual(residuals[0], 0.0)
        self.assertGreater(residuals[1], 0.19)

    def test_input_residuals_follow_eigenvalue_sorting(self) -> None:
        tracker = ModalSubspaceTracker()
        permutation = np.array([2, 0, 1])
        frame = tracker.initialize(
            np.array([3.0, 1.0, 2.0]),
            np.eye(3)[:, permutation],
            residuals=np.array([0.3, 0.1, 0.2]),
        )
        np.testing.assert_allclose(frame.eigenvalues, [1.0, 2.0, 3.0])
        np.testing.assert_allclose(frame.residuals, [0.1, 0.2, 0.3])


if __name__ == "__main__":
    unittest.main(verbosity=2)
