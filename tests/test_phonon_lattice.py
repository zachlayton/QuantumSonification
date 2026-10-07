from __future__ import annotations

from dataclasses import fields, replace
from fractions import Fraction
import unittest

import numpy as np

from qmw.acoustics.note_timbre import ModalResonatorFrame
from qmw.acoustics.phonon import PhononModalAdapter
from qmw.core.phonon import (
    PhononFrame,
    PhononLatticeEngine,
    dynamical_matrix_from_couplings,
)
from qmw.core.transition import FrameContext


class PhononLatticeTests(unittest.TestCase):
    def setUp(self) -> None:
        # Fixed-end two-site chain: K = graph Laplacian + unit pinning.
        self.couplings = np.array([[0.0, 1.0], [1.0, 0.0]])
        self.dynamical_matrix = dynamical_matrix_from_couplings(
            self.couplings,
            onsite=np.ones(2),
        )
        self.engine = PhononLatticeEngine(
            self.dynamical_matrix,
            ratio_max_denominator=12,
            provenance=("two-site analytic fixture",),
        )

    def test_frame_has_the_declared_phonon_fields(self) -> None:
        names = {item.name for item in fields(PhononFrame)}
        self.assertTrue(
            {
                "displacement",
                "velocity",
                "dynamical_matrix",
                "frequencies",
                "mode_shapes",
                "modal_positions",
                "modal_velocities",
                "modal_phases",
                "kinetic_energy",
                "potential_energy",
                "modal_energy",
                "frequency_ratios",
                "recurrence_errors",
                "occupations",
                "energy_current",
                "scattering_events",
            }
            <= names
        )

    def test_coupling_matrix_builds_graph_laplacian_plus_onsite(self) -> None:
        expected = np.array([[2.0, -1.0], [-1.0, 2.0]])
        np.testing.assert_array_equal(self.dynamical_matrix, expected)
        np.testing.assert_allclose(np.linalg.eigvalsh(self.dynamical_matrix), [1.0, 3.0])
        with self.assertRaisesRegex(ValueError, "symmetric"):
            dynamical_matrix_from_couplings(np.array([[0.0, 1.0], [0.0, 0.0]]))
        with self.assertRaisesRegex(ValueError, "nonnegative"):
            dynamical_matrix_from_couplings(np.array([[0.0, -1.0], [-1.0, 0.0]]))

    def test_modal_projection_reconstructs_state_and_pythagorean_energy(self) -> None:
        displacement = np.array([0.3, -0.7])
        velocity = np.array([1.2, 0.4])
        frame = self.engine.frame(displacement, velocity)

        np.testing.assert_allclose(frame.mode_shapes @ frame.modal_positions, displacement)
        np.testing.assert_allclose(frame.mode_shapes @ frame.modal_velocities, velocity)
        np.testing.assert_allclose(
            2.0 * frame.modal_energy,
            frame.modal_velocities**2
            + frame.frequencies**2 * frame.modal_positions**2,
        )
        self.assertAlmostEqual(
            float(np.sum(frame.kinetic_energy)),
            0.5 * float(velocity @ velocity),
        )
        self.assertAlmostEqual(
            float(np.sum(frame.potential_energy)),
            0.5 * float(displacement @ self.dynamical_matrix @ displacement),
        )
        self.assertIsNone(frame.occupations)
        self.assertEqual(frame.scattering_events, ())

    def test_closed_exact_evolution_preserves_each_modal_energy(self) -> None:
        initial = self.engine.frame(np.array([0.4, -0.2]), np.array([0.1, 0.7]))
        evolved = self.engine.evolve(initial.displacement, initial.velocity, time=9.25)
        np.testing.assert_allclose(evolved.modal_energy, initial.modal_energy, rtol=1e-12, atol=1e-12)
        self.assertAlmostEqual(evolved.total_energy, initial.total_energy, places=12)

    def test_energy_current_is_antisymmetric_and_matches_local_continuity(self) -> None:
        frame = self.engine.frame(np.array([0.5, -0.25]), np.array([0.2, 0.8]))
        np.testing.assert_allclose(frame.energy_current + frame.energy_current.T, 0.0, atol=1e-15)

        acceleration = -frame.dynamical_matrix @ frame.displacement
        local_energy_derivative = (
            frame.velocity * acceleration
            + 0.5
            * (
                frame.velocity * (frame.dynamical_matrix @ frame.displacement)
                + frame.displacement * (frame.dynamical_matrix @ frame.velocity)
            )
        )
        np.testing.assert_allclose(local_energy_derivative, -frame.energy_current.sum(axis=1))

    def test_ratios_and_recurrence_error_use_bounded_rationals(self) -> None:
        frame = self.engine.frame(np.ones(2), np.zeros(2))
        self.assertAlmostEqual(frame.frequency_ratios[1, 0], np.sqrt(3.0))
        approximation = Fraction(np.sqrt(3.0)).limit_denominator(12)
        self.assertAlmostEqual(
            frame.recurrence_errors[1, 0],
            abs(np.sqrt(3.0) - approximation.numerator / approximation.denominator),
        )

    def test_zero_translation_mode_is_supported_without_fake_ratio(self) -> None:
        free = PhononLatticeEngine.from_couplings(self.couplings)
        frame = free.evolve(np.array([0.2, 0.2]), np.array([0.1, 0.1]), time=2.0)
        self.assertAlmostEqual(frame.frequencies[0], 0.0)
        self.assertTrue(np.isnan(frame.frequency_ratios[1, 0]))
        self.assertTrue(np.isnan(frame.recurrence_errors[1, 0]))
        self.assertTrue(np.all(np.isfinite(frame.modal_phases)))

    def test_inputs_and_frame_arrays_are_snapshot_owned(self) -> None:
        displacement = np.array([0.3, -0.7])
        velocity = np.array([1.2, 0.4])
        old_displacement = displacement.copy()
        frame = self.engine.frame(displacement, velocity)
        displacement[:] = 99.0
        np.testing.assert_array_equal(frame.displacement, old_displacement)
        for item in fields(frame):
            value = getattr(frame, item.name)
            if isinstance(value, np.ndarray):
                self.assertFalse(value.flags.writeable, item.name)
        with self.assertRaises(ValueError):
            frame.displacement[0] = 1.0

    def test_invalid_dynamical_matrices_and_state_are_rejected(self) -> None:
        invalid = [
            np.ones((2, 3)),
            np.array([[1.0, 2.0], [0.0, 1.0]]),
            np.diag([1.0, -1.0]),
            np.array([[1.0, np.nan], [np.nan, 1.0]]),
        ]
        for matrix in invalid:
            with self.subTest(matrix=matrix), self.assertRaises(ValueError):
                PhononLatticeEngine(matrix)
        with self.assertRaisesRegex(ValueError, "displacement"):
            self.engine.frame(np.ones(3), np.ones(2))
        with self.assertRaisesRegex(ValueError, "occupations"):
            self.engine.frame(np.ones(2), np.ones(2), occupations=np.array([-1.0, 2.0]))


class PhononModalAdapterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = PhononLatticeEngine.from_couplings(
            np.array([[0.0, 1.0], [1.0, 0.0]]),
            onsite=np.ones(2),
            provenance=("declared scalar spring network",),
        )
        self.frame = self.engine.frame(np.array([1.0, 0.0]), np.zeros(2))
        self.context = FrameContext(
            source_id="phonon-test",
            frame_id=3,
            time=0.0,
            dt=0.01,
            basis_id="declared:lattice-sites-as-hilbert-coordinates",
            provenance=("explicit coordinate identification",),
        )

    def test_adapter_supplies_existing_geometry_projector_and_body_frame(self) -> None:
        adapter = PhononModalAdapter(
            angular_frequency_to_hz=220.0,
            quality_factors=np.array([20.0, 30.0]),
        )
        geometry = adapter.geometry_modes(
            self.frame,
            space_id=self.context.basis_id,
            geometry_id="two-site-body",
        )
        np.testing.assert_allclose(geometry.frequencies_hz, 220.0 * self.frame.frequencies)
        np.testing.assert_allclose(geometry.hilbert_vectors, self.frame.mode_shapes)
        body = adapter.project(
            self.frame,
            rho=np.diag([0.8, 0.2]),
            context=self.context,
            geometry_id="two-site-body",
        )
        self.assertIsInstance(body, ModalResonatorFrame)
        self.assertEqual(body.geometry_id, "two-site-body")
        self.assertIn("qmw.phonon_modal_adapter.v1", body.provenance)

    def test_adapter_requires_explicit_compatible_coordinate_identity(self) -> None:
        adapter = PhononModalAdapter(
            angular_frequency_to_hz=100.0,
            quality_factors=25.0,
        )
        with self.assertRaisesRegex(ValueError, "space"):
            adapter.project(
                self.frame,
                rho=np.diag([0.8, 0.2]),
                context=replace(self.context, basis_id="other-space"),
                geometry_id="two-site-body",
                space_id=self.context.basis_id,
            )

    def test_free_translation_mode_is_excluded_from_acoustic_body(self) -> None:
        free = PhononLatticeEngine.from_couplings(np.array([[0.0, 1.0], [1.0, 0.0]]))
        frame = free.frame(np.ones(2), np.zeros(2))
        adapter = PhononModalAdapter(
            angular_frequency_to_hz=100.0,
            quality_factors=25.0,
        )
        geometry = adapter.geometry_modes(
            frame,
            space_id=self.context.basis_id,
            geometry_id="free-body",
        )
        self.assertEqual(len(geometry.mode_ids), 1)
        self.assertFalse(geometry.complete)
        self.assertGreater(geometry.frequencies_hz[0], 0.0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
