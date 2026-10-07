from __future__ import annotations

import unittest

import numpy as np
from qiskit.circuit.library import QFTGate
from qiskit.quantum_info import Operator

from .core import (
    MeasurementProtocol,
    SamplingPolicy,
    StateTransform,
    UnitaryOperator,
)
from .experiment import RepresentationExperiment, density_from_preset
from .full4q import FullPauliTomography
from .protocols import ClassicalShadowTomography
from .operators import (
    EpistropheBasis,
    FloquetOperator,
    GraphLaplacianBasis,
    GroverAmplifiedBasis,
    HadamardOperator,
    HamiltonianEigenbasis,
    IdentityOperator,
    QFTOperator,
    cycle_graph_adjacency,
    transverse_ising_hamiltonian,
)
from .osc import (
    HamiltonianLiveConfig,
    HamiltonianOSCService,
    HamiltonianOSCPublisher,
)
from .observables import pauli_expectations
from .transforms import HamiltonianBasisTracker, IsingHamiltonianSpec
from .registry import TransformRegistry, build_default_registry


class CoreContractTests(unittest.TestCase):
    def test_measurement_is_not_a_state_transform(self) -> None:
        self.assertFalse(issubclass(MeasurementProtocol, StateTransform))
        self.assertTrue(issubclass(UnitaryOperator, StateTransform))

    def test_unitary_transform_preserves_density_invariants(self) -> None:
        rho = density_from_preset("ghz")
        for transform in (
            IdentityOperator(),
            HadamardOperator(),
            QFTOperator(),
            HamiltonianEigenbasis(transverse_ising_hamiltonian(4)),
        ):
            with self.subTest(transform=transform.name):
                transformed = transform.apply(rho)
                self.assertAlmostEqual(float(np.trace(transformed).real), 1.0)
                np.testing.assert_allclose(
                    transformed,
                    transformed.conj().T,
                    atol=1e-10,
                )
                np.testing.assert_allclose(
                    np.linalg.eigvalsh(transformed),
                    np.linalg.eigvalsh(rho),
                    atol=1e-10,
                )

    def test_qft_retains_established_phase_convention(self) -> None:
        expected = Operator(QFTGate(4)).data
        np.testing.assert_allclose(
            QFTOperator().unitary(16),
            expected,
            atol=1e-12,
        )


class RegistryTests(unittest.TestCase):
    def test_default_registry_resolves_aliases(self) -> None:
        registry = build_default_registry()
        self.assertIsInstance(registry.create("computational"), IdentityOperator)
        self.assertIsInstance(registry.create("h"), HadamardOperator)
        self.assertIsInstance(registry.create("iqft"), QFTOperator)
        self.assertEqual(
            registry.create("energy").name,
            "hamiltonian_eigenbasis",
        )
        self.assertIn("floquet", registry.names())
        self.assertIn("grover_amplified", registry.names())
        self.assertIn("epistrophe", registry.names())

    def test_registry_builds_parameterized_graph_operator(self) -> None:
        registry = build_default_registry()
        graph = registry.create(
            "graph",
            adjacency=cycle_graph_adjacency(16),
            graph_name="cycle_16",
        )
        self.assertIsInstance(graph, GraphLaplacianBasis)
        self.assertEqual(graph.metadata(16)["edge_count"], 16)

    def test_duplicate_alias_is_rejected(self) -> None:
        registry = TransformRegistry()
        registry.register(
            "identity",
            IdentityOperator,
            description=IdentityOperator.description,
            aliases=("none",),
        )
        with self.assertRaisesRegex(ValueError, "already registered"):
            registry.register(
                "other",
                IdentityOperator,
                description="duplicate",
                aliases=("none",),
            )


class GraphLaplacianTests(unittest.TestCase):
    def test_cycle_graph_basis_diagonalizes_laplacian(self) -> None:
        graph = GraphLaplacianBasis(
            cycle_graph_adjacency(16),
            graph_name="cycle_16",
        )
        unitary = graph.checked_unitary(16)
        transformed = unitary @ graph.laplacian @ unitary.conj().T
        np.testing.assert_allclose(
            transformed,
            np.diag(graph.eigenvalues),
            atol=1e-10,
        )
        self.assertAlmostEqual(graph.eigenvalues[0], 0.0, places=10)
        self.assertGreater(graph.metadata(16)["spectral_gap"], 0.0)
        self.assertEqual(graph.metadata(16)["connected_components"], 1)

    def test_disconnected_graph_has_zero_spectral_gap(self) -> None:
        adjacency = np.zeros((4, 4), dtype=float)
        adjacency[0, 1] = adjacency[1, 0] = 1.0
        adjacency[2, 3] = adjacency[3, 2] = 1.0
        metadata = GraphLaplacianBasis(adjacency).metadata(4)
        self.assertEqual(metadata["connected_components"], 2)
        self.assertAlmostEqual(metadata["spectral_gap"], 0.0, places=12)

    def test_degenerate_eigenspaces_are_reproducible(self) -> None:
        adjacency = cycle_graph_adjacency(16)
        first = GraphLaplacianBasis(adjacency).unitary(16)
        second = GraphLaplacianBasis(adjacency).unitary(16)
        np.testing.assert_allclose(first, second, atol=1e-12)

    def test_graph_dimension_must_match_density(self) -> None:
        graph = GraphLaplacianBasis(cycle_graph_adjacency(8))
        with self.assertRaisesRegex(ValueError, "8 nodes"):
            graph.apply(density_from_preset("ghz"))

    def test_invalid_directed_graph_is_rejected(self) -> None:
        adjacency = cycle_graph_adjacency(4)
        adjacency[0, 1] = 2.0
        with self.assertRaisesRegex(ValueError, "symmetric"):
            GraphLaplacianBasis(adjacency)


class FullExperimentTests(unittest.TestCase):
    def test_identity_produces_identical_sampled_outputs(self) -> None:
        result = RepresentationExperiment(
            experimental=IdentityOperator(),
            measurement=FullPauliTomography(),
        ).run(preset="ghz", shots=32, seed=11)
        reference, experimental = result.tomography_outputs()
        self.assertEqual(result.schema, "qmw.representation_laboratory.v4")
        self.assertEqual(
            [row.counts for row in reference.settings],
            [row.counts for row in experimental.settings],
        )
        self.assertTrue(
            all(item.exact_delta == 0.0 for item in result.observable_comparisons)
        )

    def test_graph_comparison_preserves_full4q_output_contract(self) -> None:
        graph = GraphLaplacianBasis(
            cycle_graph_adjacency(16),
            graph_name="cycle_16",
        )
        result = RepresentationExperiment(
            experimental=graph,
            measurement=FullPauliTomography(),
        ).run(preset="ghz", shots=64, seed=17)
        reference, experimental = result.tomography_outputs()
        for output in (reference, experimental):
            self.assertEqual(output.schema, "qmw.full4q.tomography.v1")
            self.assertEqual(len(output.settings), 81)
            self.assertEqual(len(output.paulis), 256)
            self.assertEqual(len(output.shells), 5)
            self.assertEqual(output.total_shots, 81 * 64)
        self.assertEqual(reference.source, "representation_reference")
        self.assertEqual(
            experimental.source,
            "representation_experimental",
        )
        self.assertEqual(experimental.transform, "graph_laplacian")
        self.assertEqual(len(result.observable_comparisons), 255)
        self.assertGreater(
            result.comparison_metrics["observable_delta_max_abs_exact"],
            0.1,
        )


class SamplingPolicyTests(unittest.TestCase):
    def test_fixed_sampling_repeats_and_sequence_advances(self) -> None:
        fixed = SamplingPolicy.fixed(41)
        self.assertEqual(fixed.resolve().resolved_seed, 41)
        self.assertEqual(fixed.resolve().resolved_seed, 41)
        sequence = SamplingPolicy.sequence(41)
        self.assertEqual(sequence.resolve().resolved_seed, 41)
        self.assertEqual(sequence.resolve().resolved_seed, 42)

    def test_experiment_shares_one_resolved_seed_between_sides(self) -> None:
        measurement = FullPauliTomography(
            sampling=SamplingPolicy.sequence(70)
        )
        experiment = RepresentationExperiment(
            experimental=QFTOperator(),
            measurement=measurement,
        )
        first = experiment.run(shots=16, seed=None)
        second = experiment.run(shots=16, seed=None)
        self.assertEqual(first.seed, 70)
        self.assertEqual(second.seed, 71)
        self.assertEqual(first.reference_output.seed, first.seed)
        self.assertEqual(first.experimental_output.seed, first.seed)

    def test_resample_records_resolved_seed(self) -> None:
        result = RepresentationExperiment(
            experimental=IdentityOperator(),
            measurement=FullPauliTomography(
                sampling=SamplingPolicy.resample()
            ),
        ).run(shots=16, seed=None)
        self.assertEqual(result.sampling_mode, "resample")
        self.assertIsInstance(result.seed, int)
        self.assertEqual(result.reference_output.seed, result.seed)


class ExtendedTransformTests(unittest.TestCase):
    def test_floquet_from_hamiltonian_is_unitary(self) -> None:
        operator = FloquetOperator.from_hamiltonian(
            transverse_ising_hamiltonian(4),
            period=0.25,
            steps=3,
        )
        unitary = operator.checked_unitary(16)
        np.testing.assert_allclose(
            unitary @ unitary.conj().T,
            np.eye(16),
            atol=1e-10,
        )
        self.assertEqual(operator.metadata(16)["steps"], 3)

    def test_grover_amplifies_marked_state_from_uniform(self) -> None:
        operator = GroverAmplifiedBasis([0], iterations=1)
        uniform = np.ones(16, dtype=complex) / 4.0
        amplified = operator.unitary(16) @ uniform
        self.assertGreater(abs(amplified[0]), abs(uniform[0]))
        operator.checked_unitary(16)

    def test_epistrophe_wraps_explicit_return_map(self) -> None:
        shift = np.roll(np.eye(16, dtype=complex), 1, axis=0)
        operator = EpistropheBasis(
            shift,
            returns=2,
            definition="test_shift",
        )
        np.testing.assert_allclose(
            operator.unitary(16),
            np.linalg.matrix_power(shift, 2),
        )
        self.assertEqual(operator.metadata(16)["definition"], "test_shift")


class ClassicalShadowTests(unittest.TestCase):
    def test_shadow_protocol_is_separate_from_state_transforms(self) -> None:
        self.assertIsInstance(
            ClassicalShadowTomography(),
            MeasurementProtocol,
        )
        self.assertNotIsInstance(
            ClassicalShadowTomography(),
            StateTransform,
        )

    def test_identity_shadow_comparison_uses_common_random_numbers(self) -> None:
        result = RepresentationExperiment(
            experimental=IdentityOperator(),
            measurement=ClassicalShadowTomography(
                sampling=SamplingPolicy.fixed(31)
            ),
        ).run(shots=256, seed=31)
        self.assertEqual(
            result.reference_output.schema,
            "qmw.classical_shadows.v4",
        )
        self.assertEqual(len(result.observable_comparisons), 255)
        self.assertTrue(
            all(
                item.estimated_delta == 0.0
                for item in result.observable_comparisons
            )
        )
        self.assertEqual(
            result.measurement_protocol["shot_semantics"],
            "total_random_snapshots",
        )


class HamiltonianLiveControlTests(unittest.TestCase):
    def test_ising_spec_exposes_all_high_level_parameters(self) -> None:
        open_spec = IsingHamiltonianSpec(
            coupling=0.8,
            transverse_field=0.5,
            longitudinal_field=-0.2,
            boundary="open",
        )
        periodic = IsingHamiltonianSpec(
            coupling=0.8,
            transverse_field=0.5,
            longitudinal_field=-0.2,
            boundary="periodic",
        )
        self.assertEqual(open_spec.metadata()["coupling"], 0.8)
        self.assertFalse(
            np.allclose(open_spec.matrix(), periodic.matrix())
        )

    def test_tracker_aligns_neighboring_hamiltonian_bases(self) -> None:
        tracker = HamiltonianBasisTracker()
        _first, initial = tracker.solve(IsingHamiltonianSpec().matrix())
        second, tracked = tracker.solve(
            IsingHamiltonianSpec(coupling=0.701).matrix()
        )
        self.assertFalse(initial["tracking_applied"])
        self.assertTrue(tracked["tracking_applied"])
        self.assertGreater(tracked["minimum_matched_overlap"], 0.999)
        second.checked_unitary(16)

    def test_live_config_rejects_invalid_atomic_bundle(self) -> None:
        with self.assertRaisesRegex(ValueError, "mode"):
            HamiltonianLiveConfig(mode="brownian").validate()
        with self.assertRaisesRegex(ValueError, "boundary"):
            HamiltonianLiveConfig(boundary="mobius").validate()

    def test_preview_publisher_emits_atomic_landscape(self) -> None:
        class CaptureClient:
            def __init__(self) -> None:
                self.messages = []

            def send_message(self, address, payload) -> None:
                self.messages.append((address, payload))

        publisher = HamiltonianOSCPublisher(
            "127.0.0.1",
            7446,
            packet_delay_ms=0,
        )
        self.addCleanup(publisher.tomography.client._sock.close)
        publisher.client._sock.close()
        capture = CaptureClient()
        publisher.client = capture
        rho = density_from_preset("ghz")
        transformed = HamiltonianEigenbasis(
            IsingHamiltonianSpec().matrix()
        ).apply(rho)
        publisher.preview(
            revision=91,
            config=HamiltonianLiveConfig(),
            eigenvalues=np.linalg.eigvalsh(IsingHamiltonianSpec().matrix()),
            reference=pauli_expectations(rho),
            experimental=pauli_expectations(transformed),
            density_distance=float(np.linalg.norm(transformed - rho)),
            tracking={
                "tracking_applied": False,
                "minimum_matched_overlap": 1.0,
                "minimum_level_gap": 0.1,
            },
        )
        addresses = [address for address, _payload in capture.messages]
        self.assertEqual(addresses.count("/qmw/v4/preview/begin"), 1)
        self.assertEqual(addresses.count("/qmw/v4/preview/spectrum"), 16)
        self.assertEqual(addresses.count("/qmw/v4/preview/pauli"), 255)
        self.assertEqual(addresses.count("/qmw/v4/preview/metrics"), 1)
        self.assertEqual(addresses.count("/qmw/v4/preview/end"), 1)

    def test_service_parses_max_bundle_atomically(self) -> None:
        service = HamiltonianOSCService.__new__(HamiltonianOSCService)
        service.config = HamiltonianLiveConfig()
        service._revision = 1
        revision, config = service._parse(
            (
                44,
                0.9,
                0.6,
                -0.1,
                2.5,
                "evolution",
                "periodic",
                "weave",
                128,
                "resample",
                99,
            )
        )
        self.assertEqual(revision, 44)
        self.assertEqual(config.coupling, 0.9)
        self.assertEqual(config.mode, "evolution")
        self.assertEqual(config.boundary, "periodic")
        self.assertEqual(config.sampling, "resample")


if __name__ == "__main__":
    unittest.main()
