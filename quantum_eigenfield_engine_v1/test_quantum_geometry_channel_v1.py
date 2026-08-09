from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import numpy as np

from .quantum_eigenfield_engine_v1 import (
    QuantumEigenfieldConfig,
    QuantumEigenfieldEngine,
    QuantumGeometryChannel,
    demo_density_matrix,
)


class QuantumGeometryChannelTests(unittest.TestCase):
    @staticmethod
    def geometry(mode_count: int) -> tuple[np.ndarray, np.ndarray]:
        values = np.linspace(0.5, 4.0, mode_count)
        rows = max(mode_count + 2, 8)
        raw = np.cos(
            np.pi
            * (np.arange(rows)[:, None] + 0.5)
            * (np.arange(mode_count)[None, :] + 1.0)
            / rows
        )
        vectors, _ = np.linalg.qr(raw, mode="reduced")
        return values, vectors

    def assert_density(self, state: np.ndarray) -> None:
        np.testing.assert_allclose(state, state.conj().T, atol=1e-11)
        self.assertAlmostEqual(float(np.trace(state).real), 1.0, places=11)
        self.assertGreaterEqual(float(np.min(np.linalg.eigvalsh(state))), -1e-11)

    def test_square_channel_is_exact_v_rho_v_dagger(self) -> None:
        rho = demo_density_matrix(2)
        values, vectors = self.geometry(4)
        channel = QuantumGeometryChannel(values, vectors, 4)
        projected = channel.project(rho)
        expected = projected.channel_isometry @ rho @ projected.channel_isometry.conj().T
        np.testing.assert_allclose(projected.density_matrix, expected, atol=1e-11)
        self.assertEqual(projected.environment_dimension, 1)
        self.assert_density(projected.density_matrix)

    def test_tall_isometry_preserves_trace_and_positivity(self) -> None:
        rho = demo_density_matrix(2)
        values, vectors = self.geometry(7)
        projected = QuantumGeometryChannel(values, vectors, 4).project(rho)
        self.assertEqual(projected.channel_isometry.shape, (7, 4))
        self.assert_density(projected.density_matrix)

    def test_dimension_reduction_uses_partial_trace(self) -> None:
        rho = demo_density_matrix(3)
        values, vectors = self.geometry(3)
        projected = QuantumGeometryChannel(values, vectors, 8).project(rho)
        self.assertEqual(projected.environment_dimension, 3)
        self.assertEqual(projected.channel_isometry.shape, (9, 8))
        self.assert_density(projected.density_matrix)

    def test_engine_exports_modal_density_and_channel(self) -> None:
        rho = demo_density_matrix(3)
        values, vectors = self.geometry(5)
        engine = QuantumEigenfieldEngine(
            rho,
            values,
            vectors,
            QuantumEigenfieldConfig(n_geometric_modes=5),
        )
        probabilities, _ = engine.project()
        self.assert_density(engine.modal_density_matrix)
        np.testing.assert_allclose(
            probabilities,
            np.real(np.diag(engine.modal_density_matrix)),
            atol=1e-12,
        )
        with tempfile.TemporaryDirectory() as directory:
            paths = engine.export(Path(directory) / "channel")
            with np.load(paths["npz"], allow_pickle=False) as payload:
                self.assertIn("modal_density_matrix", payload.files)
                self.assertIn("channel_isometry", payload.files)

    def test_legacy_artistic_mode_remains_available(self) -> None:
        values, vectors = self.geometry(4)
        engine = QuantumEigenfieldEngine(
            demo_density_matrix(2),
            values,
            vectors,
            QuantumEigenfieldConfig(
                n_geometric_modes=4,
                coupling_mode="legacy_artistic",
            ),
        )
        probabilities, _ = engine.project()
        self.assertAlmostEqual(float(np.sum(probabilities)), 1.0, places=12)
        self.assertIsNone(engine.modal_quantum_state)


if __name__ == "__main__":
    unittest.main(verbosity=2)
