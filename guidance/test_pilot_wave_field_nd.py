import unittest

import numpy as np

from guidance.pilot_wave_field_nd import (
    PilotWaveFieldND,
    normalize_wavefunction,
    split_step_fourier,
)
from guidance.schrodinger_pilot_1d_v2 import gaussian_wavepacket_1d


class PilotWaveFieldNDTests(unittest.TestCase):
    def test_plane_wave_velocity_and_quantum_potential(self):
        x = np.linspace(-4.0, 4.0, 64, endpoint=False)
        y = np.linspace(-3.0, 3.0, 48, endpoint=False)
        kx = 2.0 * np.pi * 2 / 8.0
        ky = -2.0 * np.pi / 6.0
        xx, yy = np.meshgrid(x, y, indexing="ij")
        field = PilotWaveFieldND(
            (x, y),
            np.exp(1j * (kx * xx + ky * yy)),
            mass=2.0,
            hbar=1.5,
            normalize=True,
        )
        np.testing.assert_allclose(field.velocity[0], 1.5 * kx / 2.0, atol=1e-12)
        np.testing.assert_allclose(field.velocity[1], 1.5 * ky / 2.0, atol=1e-12)
        np.testing.assert_allclose(field.quantum_potential, 0.0, atol=2e-12)
        self.assertAlmostEqual(field.norm, 1.0, places=13)

    def test_nodes_are_declared_and_do_not_create_infinite_velocity(self):
        x = np.linspace(-np.pi, np.pi, 128, endpoint=False)
        field = PilotWaveFieldND((x,), np.sin(x), normalize=True)
        node = int(np.argmin(np.abs(x)))
        self.assertFalse(field.valid_mask[node])
        self.assertEqual(field.velocity[0][node], 0.0)
        self.assertTrue(np.all(np.isfinite(field.velocity[0])))
        self.assertTrue(np.all(np.isfinite(field.quantum_potential)))

    def test_seeded_born_sampling_is_deterministic(self):
        x = np.linspace(-6.0, 6.0, 128, endpoint=False)
        psi = gaussian_wavepacket_1d(x, center=1.0, sigma=0.7, momentum=0.0)
        field = PilotWaveFieldND((x,), psi, normalize=True)
        first = field.sample_positions(500, seed=82)
        second = field.sample_positions(500, seed=82)
        np.testing.assert_array_equal(first, second)
        self.assertAlmostEqual(float(np.mean(first)), 1.0, delta=0.09)

    def test_boundary_rules_are_explicit(self):
        x = np.linspace(0.0, 1.0, 32, endpoint=False)
        psi = np.ones(32, dtype=complex)
        periodic = PilotWaveFieldND((x,), psi, boundary="periodic", normalize=True)
        reflected = PilotWaveFieldND((x,), psi, boundary="reflecting", normalize=True)
        absorbed = PilotWaveFieldND((x,), psi, boundary="absorbing", normalize=True)
        self.assertAlmostEqual(float(periodic.apply_boundary(np.array([1.1]))[0][0]), 0.1)
        self.assertAlmostEqual(float(reflected.apply_boundary(np.array([1.1]))[0][0]), 0.8375)
        _position, active = absorbed.apply_boundary(np.array([1.1]))
        self.assertFalse(bool(active))

    def test_continuity_residual_for_free_packet_is_small(self):
        x = np.linspace(-12.0, 12.0, 256, endpoint=False)
        dx = float(x[1] - x[0])
        initial = normalize_wavefunction(
            gaussian_wavepacket_1d(x, center=-2.0, sigma=1.0, momentum=2.0),
            (dx,),
        )
        dt = 0.002
        midpoint = split_step_fourier(initial, (x,), 0.5 * dt)
        final = split_step_fourier(initial, (x,), dt)
        field = PilotWaveFieldND((x,), midpoint)
        residual = field.continuity_residual(
            np.abs(initial) ** 2,
            np.abs(final) ** 2,
            dt,
        )
        self.assertLess(float(np.sqrt(np.mean(residual**2))), 1e-5)

    def test_guidance_agrees_when_extra_dimensions_are_constant(self):
        x = np.linspace(-4.0, 4.0, 64, endpoint=False)
        y = np.linspace(-3.0, 3.0, 32, endpoint=False)
        z = np.linspace(-2.0, 2.0, 24, endpoint=False)
        wave = np.exp(1j * (2.0 * np.pi * 2 / 8.0) * x)
        field_1d = PilotWaveFieldND((x,), wave, normalize=True)
        field_2d = PilotWaveFieldND(
            (x, y), wave[:, None] * np.ones((1, len(y))), normalize=True
        )
        field_3d = PilotWaveFieldND(
            (x, y, z),
            wave[:, None, None] * np.ones((1, len(y), len(z))),
            normalize=True,
        )
        point_1d = np.array([0.37])
        point_2d = np.array([0.37, -0.41])
        point_3d = np.array([0.37, -0.41, 0.28])
        v1 = field_1d.velocity_at(point_1d)[0]
        v2 = field_2d.velocity_at(point_2d)[0]
        v3 = field_3d.velocity_at(point_3d)[0]
        self.assertAlmostEqual(float(v1[0]), float(v2[0]), places=12)
        self.assertAlmostEqual(float(v2[0]), float(v3[0]), places=12)
        np.testing.assert_allclose(v2[1:], 0.0, atol=1e-12)
        np.testing.assert_allclose(v3[1:], 0.0, atol=1e-12)


if __name__ == "__main__":
    unittest.main()

