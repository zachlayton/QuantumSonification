from __future__ import annotations

import math
import unittest

import numpy as np

from quantum_resonant_membrane.density_engine import DensityMatrixEngine
from quantum_resonant_membrane.numerics import stability_diagnostics
from quantum_resonant_membrane.terrain import DensityTerrain, TerrainConfig


class NumericalStabilityTests(unittest.TestCase):
    def test_spectral_bound_tightens_when_stiffness_grows(self) -> None:
        mass = np.eye(2)
        damping = np.zeros((2, 2))
        low = stability_diagnostics(
            mass, np.eye(2), damping, dt=0.1, max_substep=0.01
        )
        high = stability_diagnostics(
            mass, np.eye(2) * 1.0e8, damping, dt=0.1, max_substep=0.01
        )
        self.assertAlmostEqual(low.omega_max, 1.0)
        self.assertAlmostEqual(high.omega_max, 1.0e4)
        self.assertEqual(low.substeps, 10)
        self.assertGreater(high.substeps, low.substeps)
        self.assertLess(high.effective_dt_cap, 0.01)
        self.assertLessEqual(high.actual_substep, high.spectral_dt_limit)

    def test_runtime_coherence_stiffness_can_override_fixed_cap(self) -> None:
        density_engine = DensityMatrixEngine()
        density_engine.prepare("coherent")
        density = density_engine.step(0.0)
        dt = 0.02
        fixed_cap = 1.0 / 60.0
        terrain = DensityTerrain(
            TerrainConfig(
                coherence_coupling=1.0e8,
                max_substep=fixed_cap,
                stability_safety=0.8,
            )
        ).step(density.rho, time=0.0, dt=dt)
        fixed_only_count = math.ceil(dt / fixed_cap)
        self.assertGreater(terrain.substeps, fixed_only_count)
        self.assertLess(terrain.effective_dt_cap, fixed_cap)
        self.assertLessEqual(terrain.actual_substep, terrain.stability_dt_limit)
        self.assertTrue(np.isfinite(terrain.q).all())


if __name__ == "__main__":
    unittest.main()
