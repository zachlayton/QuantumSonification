from __future__ import annotations

import unittest
from types import SimpleNamespace

import numpy as np

from qmw.core.state_frame import QuantumStateFrame
from qmw.graph import GraphProjector


def _reference_frame() -> QuantumStateFrame:
    hamiltonian = np.zeros((16, 16), dtype=complex)
    hamiltonian[0, 1] = hamiltonian[1, 0] = 1.0
    hamiltonian[2, 3] = hamiltonian[3, 2] = 0.25
    state = np.zeros(16, dtype=complex)
    state[0] = 1.0 / np.sqrt(2.0)
    state[1] = 1j / np.sqrt(2.0)
    density = np.outer(state, state.conj())
    return QuantumStateFrame(
        t=1.25,
        dt=0.01,
        rho=density,
        hamiltonian=hamiltonian,
        source_name="graph-projector-test",
        metadata={"revision": 7},
    )


class GraphProjectorTests(unittest.TestCase):
    def test_projector_keeps_the_three_graph_layers_distinct(self) -> None:
        frame = _reference_frame()
        projected = GraphProjector().project(frame)

        self.assertEqual(projected.revision, 0)
        self.assertEqual(projected.source_revision, 7)
        self.assertEqual(projected.dimension, 16)
        self.assertEqual(projected.node_labels[0], "|0000>")
        self.assertEqual(projected.node_labels[-1], "|1111>")
        self.assertEqual(
            {(edge.source, edge.target) for edge in projected.coupling_edges},
            {(0, 1), (2, 3)},
        )
        self.assertEqual(
            {(edge.source, edge.target) for edge in projected.coherence_edges},
            {(0, 1)},
        )

        # Positive J[0, 1] means flow 1 -> 0 in QMW's destination<-source
        # convention.  This is the edge direction, not a musical schedule.
        self.assertEqual(len(projected.current_edges), 1)
        current = projected.current_edges[0]
        self.assertEqual((current.source, current.target), (1, 0))
        self.assertAlmostEqual(current.magnitude, 1.0, places=12)
        self.assertAlmostEqual(projected.basis_current_inflow[0, 1], 1.0, places=12)
        self.assertAlmostEqual(projected.basis_current_inflow[1, 0], -1.0, places=12)
        np.testing.assert_allclose(
            np.sum(projected.basis_current_inflow, axis=1),
            projected.population_rate_unitary,
            atol=1.0e-12,
        )
        self.assertLess(projected.diagnostics["continuity_error"], 1.0e-12)
        self.assertEqual(projected.provenance["event_policy"], "no_event_generation_or_scheduling")

    def test_coupling_laplacian_and_gft_are_separate_from_energy_modes(self) -> None:
        projected = GraphProjector().project(_reference_frame())
        expected_adjacency = np.zeros((16, 16), dtype=float)
        expected_adjacency[0, 1] = expected_adjacency[1, 0] = 1.0
        expected_adjacency[2, 3] = expected_adjacency[3, 2] = 0.25
        np.testing.assert_allclose(projected.coupling_adjacency, expected_adjacency)
        np.testing.assert_allclose(
            projected.coupling_eigenvectors @ projected.population_graph_coefficients,
            projected.populations,
            atol=1.0e-12,
        )
        self.assertIn("not energy spectrum", projected.diagnostics["spectrum_convention"])

    def test_outputs_are_copied_read_only_and_revisions_advance(self) -> None:
        frame = _reference_frame()
        projector = GraphProjector()
        first = projector.project(frame)
        frame.rho[0, 0] = 0.25
        frame.rho[2, 2] = 0.25
        self.assertFalse(first.populations.flags.writeable)
        self.assertFalse(first.basis_current_inflow.flags.writeable)
        self.assertAlmostEqual(first.populations[0], 0.5, places=12)
        self.assertEqual(projector.project(_reference_frame()).revision, 1)

    def test_native_hamiltonian_value_supplies_the_current_units(self) -> None:
        reference = _reference_frame()
        frame = SimpleNamespace(
            time=reference.t,
            dt=reference.dt,
            rho=reference.rho,
            hamiltonian=SimpleNamespace(matrix=reference.hamiltonian, hbar=2.0),
            frame_index=11,
        )
        projected = GraphProjector().project(frame)
        self.assertEqual(projected.source_revision, 11)
        self.assertAlmostEqual(projected.basis_current_inflow[0, 1], 0.5, places=12)
        self.assertEqual(projected.diagnostics["hbar"], 2.0)
        with self.assertRaisesRegex(ValueError, "must match"):
            GraphProjector(hbar=1.0).project(frame)

    def test_only_native_four_qubit_density_pairs_are_accepted(self) -> None:
        bad_frame = QuantumStateFrame(
            t=0.0,
            dt=0.0,
            rho=np.eye(4, dtype=complex) / 4.0,
            hamiltonian=np.eye(4, dtype=complex),
        )
        with self.assertRaisesRegex(ValueError, "exact 16x16"):
            GraphProjector().project(bad_frame)

        frame = _reference_frame()
        frame.hamiltonian[0, 1] = 1.0 + 0.1j
        with self.assertRaisesRegex(ValueError, "Hermitian"):
            GraphProjector().project(frame)


if __name__ == "__main__":
    unittest.main()
