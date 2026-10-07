from __future__ import annotations

import unittest

import numpy as np

from quantum_resonant_membrane.engine import QuantumResonantMembraneEngine
from quantum_resonant_membrane.geometry import build_icosphere_geometry


class GeometryFlowMembraneTests(unittest.TestCase):
    def test_fixed_sphere_and_mass_orthogonal_modes(self) -> None:
        geometry = build_icosphere_geometry(subdivisions=1, modes=20)
        self.assertEqual(geometry.vertices.shape, (42, 3))
        self.assertEqual(geometry.faces.shape, (80, 3))
        self.assertEqual(set(geometry.regions.tolist()), {0, 1, 2, 3})
        gram = geometry.mode_shapes.T @ (
            geometry.vertex_area[:, None] * geometry.mode_shapes
        )
        self.assertTrue(np.allclose(gram, np.eye(20), atol=1.0e-9))
        self.assertTrue(np.all(np.diff(geometry.eigenvalues) >= -1.0e-12))

    def test_flow_is_conservative_and_identified(self) -> None:
        engine = QuantumResonantMembraneEngine(modes=20, crossing_threshold=1.0e-5)
        frame = engine.step(1.0 / 30.0)
        self.assertAlmostEqual(float(np.sum(frame.flow.divergence)), 0.0, places=12)
        self.assertTrue(np.allclose(frame.flow.region_flux, -frame.flow.divergence))
        self.assertEqual(frame.flow.current_kind, "quantum_probability_unitary")
        for crossing in frame.flow.crossings:
            self.assertGreaterEqual(crossing.contact_vertex, 0)
            self.assertLess(crossing.contact_vertex, len(engine.geometry.vertices))

    def test_membrane_matrices_are_positive_and_output_is_finite(self) -> None:
        engine = QuantumResonantMembraneEngine(modes=20)
        for _ in range(30):
            frame = engine.step(1.0 / 120.0)
        self.assertGreater(float(np.min(np.linalg.eigvalsh(frame.membrane.modal_mass))), 0.0)
        self.assertGreater(float(np.min(np.linalg.eigvalsh(frame.membrane.modal_stiffness))), 0.0)
        self.assertTrue(np.isfinite(frame.membrane.audible_amplitudes).all())
        self.assertTrue(np.isfinite(frame.membrane.frequency_ratios).all())
        self.assertTrue(np.all(frame.membrane.frequency_ratios > 0.0))
        self.assertEqual(
            frame.membrane.provenance, "geometry_native_effective_membrane"
        )
        self.assertGreater(frame.membrane.omega_max, 0.0)
        self.assertGreater(frame.membrane.stability_dt_limit, 0.0)
        self.assertGreaterEqual(frame.membrane.substeps, 1)
        self.assertLessEqual(
            frame.membrane.actual_substep,
            min(
                frame.membrane.effective_dt_cap,
                frame.membrane.stability_dt_limit,
            )
            + 1.0e-15,
        )

    def test_field_bus_changes_continuously_without_crossing_events(self) -> None:
        engine = QuantumResonantMembraneEngine(
            modes=20, crossing_threshold=10.0
        )
        engine.prepare("coherent")
        first = engine.step(1.0 / 30.0)
        for _ in range(30):
            later = engine.step(1.0 / 30.0)
        self.assertEqual(first.flow.event_bus.crossings, ())
        self.assertEqual(later.flow.event_bus.crossings, ())
        self.assertEqual(later.membrane.injected_energy, 0.0)
        self.assertTrue(np.allclose(later.membrane.force, 0.0))
        field = later.flow.field_bus
        self.assertEqual(field.provenance, "continuous_effective_mesoscopic_field")
        self.assertEqual(field.modal_frequency_offset_fraction.shape, (20,))
        self.assertEqual(field.intermodal_coupling.shape, (20, 20))
        self.assertTrue(np.allclose(field.intermodal_coupling, field.intermodal_coupling.T))
        self.assertTrue(np.allclose(np.diag(field.intermodal_coupling), 0.0))
        self.assertTrue(np.all((field.modal_susceptibility >= 0.0) & (field.modal_susceptibility <= 1.0)))
        self.assertTrue(np.all(field.modal_quality_factor > 0.0))
        self.assertGreater(
            float(np.max(np.abs(
                later.flow.field_bus.modal_frequency_offset_fraction
                - first.flow.field_bus.modal_frequency_offset_fraction
            ))),
            0.0,
        )

    def test_crossing_event_injects_energy_without_becoming_a_continuous_force(self) -> None:
        engine = QuantumResonantMembraneEngine(
            modes=20, crossing_threshold=0.003
        )
        engine.prepare("coherent")
        for _ in range(120):
            frame = engine.step(1.0 / 30.0)
            if frame.flow.event_bus.crossings:
                break
        self.assertTrue(frame.flow.event_bus.crossings)
        self.assertEqual(
            frame.flow.event_bus.provenance, "boundary_flux_energy_injection"
        )
        self.assertGreater(frame.flow.event_bus.transported_probability, 0.0)
        self.assertTrue(np.allclose(frame.membrane.force, 0.0))
        self.assertGreater(float(np.linalg.norm(frame.membrane.event_impulse)), 0.0)
        self.assertGreater(frame.membrane.injected_energy, 0.0)

    def test_event_threshold_retains_fractional_rhythmic_phase(self) -> None:
        engine = QuantumResonantMembraneEngine(modes=20, crossing_threshold=0.003)
        engine.prepare("coherent")
        for _ in range(12):
            frame = engine.step(1.0 / 30.0)
        old_fill = frame.flow.event_bus.accumulator_peak_fraction
        engine.flow.set_threshold(0.0015)
        frame = engine.step(0.0)
        self.assertAlmostEqual(frame.flow.event_bus.threshold, 0.0015)
        self.assertAlmostEqual(
            frame.flow.event_bus.accumulator_peak_fraction, old_fill, places=10
        )
        self.assertGreaterEqual(frame.flow.event_bus.accumulator_peak_fraction, 0.0)
        self.assertLessEqual(frame.flow.event_bus.accumulator_peak_fraction, 1.0)


if __name__ == "__main__":
    unittest.main()
