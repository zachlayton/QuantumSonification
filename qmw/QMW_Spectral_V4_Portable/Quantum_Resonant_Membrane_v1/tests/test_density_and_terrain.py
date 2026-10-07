from __future__ import annotations

import unittest

import numpy as np

from quantum_resonant_membrane.density_engine import (
    PREPARATION_MODES,
    DensityConfig,
    DensityMatrixEngine,
)
from quantum_resonant_membrane.terrain import DensityTerrain


class DensityAndTerrainTests(unittest.TestCase):
    def test_named_preparations_are_physical_and_report_their_semantics(self) -> None:
        engine = DensityMatrixEngine()
        for mode in PREPARATION_MODES:
            engine.prepare(mode)
            frame = engine.step(0.0)
            self.assertEqual(frame.preparation_mode, mode)
            self.assertTrue(frame.preparation_semantics)
            self.assertAlmostEqual(float(np.trace(frame.rho).real), 1.0, places=10)
            self.assertTrue(np.allclose(frame.rho, frame.rho.conj().T, atol=1.0e-10))
            self.assertGreaterEqual(float(np.min(np.linalg.eigvalsh(frame.rho))), -1.0e-10)

    def test_preparations_have_distinct_finite_two_qubit_meanings(self) -> None:
        engine = DensityMatrixEngine()
        engine.prepare("localized")
        self.assertTrue(np.allclose(np.diag(engine.rho), [1.0, 0.0, 0.0, 0.0]))
        engine.prepare("coherent")
        self.assertGreater(float(np.sum(np.abs(engine.rho - np.diag(np.diag(engine.rho))))), 0.0)
        engine.prepare("squeezed")
        self.assertAlmostEqual(float(engine.rho[1, 1].real), 0.0, places=12)
        self.assertAlmostEqual(float(engine.rho[2, 2].real), 0.0, places=12)
        self.assertGreater(abs(engine.rho[0, 3]), 0.0)
        engine.prepare("thermal")
        self.assertLess(float(np.trace(engine.rho @ engine.rho).real), 1.0)
        engine.prepare("vacuum")
        vacuum_rho = engine.rho.copy()
        engine.reset()
        self.assertEqual(engine.preparation_mode, "vacuum")
        self.assertTrue(np.allclose(engine.rho, vacuum_rho))

    def test_density_remains_physical_under_open_evolution(self) -> None:
        engine = DensityMatrixEngine()
        for _ in range(120):
            frame = engine.step(1.0 / 120.0)
        self.assertTrue(np.allclose(frame.rho, frame.rho.conj().T, atol=1.0e-10))
        self.assertAlmostEqual(float(np.trace(frame.rho).real), 1.0, places=10)
        self.assertGreaterEqual(float(np.min(np.linalg.eigvalsh(frame.rho))), -1.0e-10)
        self.assertGreaterEqual(frame.purity, 0.25 - 1.0e-10)
        self.assertLessEqual(frame.purity, 1.0 + 1.0e-10)

    def test_freeze_stops_rho_but_not_observation_time(self) -> None:
        engine = DensityMatrixEngine()
        before = engine.rho.copy()
        engine.set_config(freeze=True)
        frame = engine.step(0.2)
        self.assertTrue(np.allclose(before, frame.rho))
        self.assertAlmostEqual(frame.time, 0.2)

    def test_terrain_is_read_only_and_positive(self) -> None:
        density = DensityMatrixEngine().step(0.01)
        before = density.rho.copy()
        terrain = DensityTerrain().step(density.rho, time=density.time, dt=0.01)
        self.assertTrue(np.array_equal(before, density.rho))
        self.assertTrue(np.all(terrain.mass > 0.0))
        self.assertTrue(np.all(terrain.frequency > 0.0))
        self.assertTrue(np.all(terrain.coupling >= 0.0))
        self.assertEqual(terrain.provenance, "effective_mesoscopic_terrain")

    def test_hamiltonian_drive_refines_density_substeps(self) -> None:
        common = dict(
            coupling=0.0,
            dephasing_rate=0.0,
            damping_rate=0.0,
            depolarizing_rate=0.0,
            max_hamiltonian_phase_step=0.15,
        )
        low = DensityMatrixEngine(DensityConfig(drive=1.0, **common)).step(0.02)
        high = DensityMatrixEngine(DensityConfig(drive=50.0, **common)).step(0.02)
        self.assertGreater(high.substeps, low.substeps)
        self.assertLessEqual(
            high.hamiltonian_span * high.actual_substep,
            high.config.max_hamiltonian_phase_step + 1.0e-3,
        )


if __name__ == "__main__":
    unittest.main()
