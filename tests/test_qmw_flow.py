import math
from types import SimpleNamespace
import unittest

import numpy as np

from engine.qmw_flow import (
    GraphProbabilityFlow,
    ProbabilityFlow1D,
    build_flow_frame_1d,
    build_graph_flow_frame,
    graph_probability_current,
    normalize_wavefunction_1d,
    project_smooth_region_1d,
)


def gaussian_packet(
    coordinates,
    time,
    *,
    sigma=0.8,
    wave_number=1.7,
    hbar=1.0,
    mass=1.0,
):
    velocity = hbar * wave_number / mass
    center = velocity * time
    envelope = np.exp(-((coordinates - center) ** 2) / (4.0 * sigma**2))
    omega = hbar * wave_number**2 / (2.0 * mass)
    phase = np.exp(1j * ((wave_number * coordinates) - (omega * time)))
    return normalize_wavefunction_1d(envelope * phase, coordinates)


class ContinuousFlowTests(unittest.TestCase):
    def test_plane_wave_has_expected_phase_gradient_and_current(self):
        coordinates = np.linspace(-math.pi, math.pi, 4001)
        wave_number = 2.25
        hbar = 1.3
        mass = 0.7
        length = coordinates[-1] - coordinates[0]
        psi = np.exp(1j * wave_number * coordinates) / math.sqrt(length)

        frame = build_flow_frame_1d(
            psi=psi,
            coordinates=coordinates,
            hbar=hbar,
            mass=mass,
        )
        expected_current = (hbar * wave_number / mass) / length

        np.testing.assert_allclose(
            frame.phase_gradient[10:-10],
            wave_number,
            rtol=1.0e-5,
            atol=1.0e-7,
        )
        np.testing.assert_allclose(
            frame.current[10:-10],
            expected_current,
            rtol=1.0e-5,
            atol=1.0e-7,
        )
        self.assertAlmostEqual(frame.total_probability, 1.0, places=10)

    def test_global_phase_does_not_change_density_or_flow(self):
        coordinates = np.linspace(-8.0, 8.0, 3001)
        psi = gaussian_packet(coordinates, 0.0)
        rotated = psi * np.exp(1j * 1.2345)

        first = build_flow_frame_1d(psi=psi, coordinates=coordinates)
        second = build_flow_frame_1d(psi=rotated, coordinates=coordinates)

        np.testing.assert_allclose(first.density, second.density, atol=1.0e-13)
        np.testing.assert_allclose(
            first.phase_gradient, second.phase_gradient, atol=1.0e-11
        )
        np.testing.assert_allclose(first.current, second.current, atol=1.0e-12)

    def test_real_stationary_packet_has_zero_current(self):
        coordinates = np.linspace(-8.0, 8.0, 3001)
        psi = normalize_wavefunction_1d(
            np.exp(-(coordinates**2) / (4.0 * 0.9**2)),
            coordinates,
        )
        frame = build_flow_frame_1d(psi=psi, coordinates=coordinates)
        self.assertLess(float(np.max(np.abs(frame.current))), 1.0e-12)
        self.assertLess(abs(frame.mean_velocity), 1.0e-12)

    def test_translated_gaussian_satisfies_continuity_equation(self):
        coordinates = np.linspace(-8.0, 8.0, 6001)
        engine = ProbabilityFlow1D()
        engine.compute(
            psi=gaussian_packet(coordinates, 0.0),
            coordinates=coordinates,
            time=0.0,
        )
        frame = engine.compute(
            psi=gaussian_packet(coordinates, 0.001),
            coordinates=coordinates,
            time=0.001,
        )

        self.assertIsNotNone(frame.continuity_residual)
        self.assertIsNotNone(frame.continuity.local_l2)
        self.assertLess(frame.continuity.local_l2, 2.0e-5)
        self.assertLess(frame.continuity.local_linf, 4.0e-5)
        self.assertLess(abs(frame.continuity.global_residual), 1.0e-9)

    def test_wavefunction_frame_adapter_preserves_specialized_current(self):
        coordinates = np.linspace(-1.0, 1.0, 101)
        psi = normalize_wavefunction_1d(np.ones_like(coordinates), coordinates)
        supplied_current = np.linspace(-0.2, 0.2, coordinates.size)
        source_frame = SimpleNamespace(
            dimension=1,
            coordinates=(coordinates,),
            probability_current=(supplied_current,),
            psi=psi,
            time=0.0,
        )

        frame = ProbabilityFlow1D().from_wavefunction_frame(source_frame)
        self.assertEqual(frame.current_model, "override")
        np.testing.assert_allclose(frame.current, supplied_current)

    def test_smooth_region_flux_matches_population_change(self):
        coordinates = np.linspace(-8.0, 8.0, 6001)
        dt = 0.001
        membership = 0.5 * (1.0 + np.tanh(coordinates / 0.2))

        frame_before = build_flow_frame_1d(
            psi=gaussian_packet(coordinates, -0.5 * dt),
            coordinates=coordinates,
            time=-0.5 * dt,
        )
        frame_midpoint = build_flow_frame_1d(
            psi=gaussian_packet(coordinates, 0.0),
            coordinates=coordinates,
            time=0.0,
        )
        frame_after = build_flow_frame_1d(
            psi=gaussian_packet(coordinates, 0.5 * dt),
            coordinates=coordinates,
            time=0.5 * dt,
        )

        projection_before = project_smooth_region_1d(
            frame_before, membership
        )
        projection_midpoint = project_smooth_region_1d(
            frame_midpoint, membership
        )
        projection_after = project_smooth_region_1d(
            frame_after, membership
        )
        observed_rate = (
            projection_after.population - projection_before.population
        ) / dt

        self.assertAlmostEqual(
            projection_midpoint.total_population_rate,
            observed_rate,
            delta=1.0e-5,
        )
        self.assertGreater(projection_midpoint.interface_flux, 0.0)
        self.assertLess(
            abs(projection_midpoint.domain_boundary_flux), 1.0e-12
        )


class GraphFlowTests(unittest.TestCase):
    def test_graph_current_matches_von_neumann_population_derivative(self):
        coupling = 0.8
        hamiltonian = np.array(
            [[0.0, coupling], [coupling, 0.0]],
            dtype=np.complex128,
        )
        state = np.array([1.0, 1j], dtype=np.complex128) / math.sqrt(2.0)
        density_matrix = np.outer(state, np.conj(state))

        current = graph_probability_current(hamiltonian, density_matrix)
        derivative = -1j * (
            (hamiltonian @ density_matrix) - (density_matrix @ hamiltonian)
        )
        expected_population_rate = np.real(np.diag(derivative))

        np.testing.assert_allclose(
            np.sum(current, axis=1),
            expected_population_rate,
            atol=1.0e-12,
        )
        np.testing.assert_allclose(current, -current.T, atol=1.0e-12)
        self.assertAlmostEqual(current[0, 1], coupling, places=12)
        self.assertAlmostEqual(float(np.sum(current)), 0.0, places=12)

    def test_graph_frame_exposes_coherence_and_conserved_flow(self):
        hamiltonian = np.array(
            [[0.0, 0.5], [0.5, 0.0]],
            dtype=np.complex128,
        )
        state = np.array([1.0, np.exp(1j * 0.7)], dtype=np.complex128)
        state /= np.linalg.norm(state)
        density_matrix = np.outer(state, np.conj(state))

        frame = build_graph_flow_frame(
            density_matrix=density_matrix,
            hamiltonian=hamiltonian,
        )

        self.assertAlmostEqual(frame.total_probability, 1.0, places=12)
        self.assertLess(frame.conservation_error, 1.0e-12)
        np.testing.assert_allclose(
            frame.coherence_magnitude,
            np.abs(density_matrix),
            atol=1.0e-12,
        )
        np.testing.assert_allclose(
            frame.coherence_phase,
            np.angle(density_matrix),
            atol=1.0e-12,
        )

    def test_graph_engine_reports_time_order_errors(self):
        hamiltonian = np.array(
            [[0.0, 1.0], [1.0, 0.0]],
            dtype=np.complex128,
        )
        density_matrix = np.eye(2, dtype=np.complex128) / 2.0
        engine = GraphProbabilityFlow()
        engine.compute(
            density_matrix=density_matrix,
            hamiltonian=hamiltonian,
            time=1.0,
        )
        with self.assertRaises(ValueError):
            engine.compute(
                density_matrix=density_matrix,
                hamiltonian=hamiltonian,
                time=1.0,
            )


if __name__ == "__main__":
    unittest.main()
