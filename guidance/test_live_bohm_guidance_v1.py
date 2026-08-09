import unittest
from types import SimpleNamespace

import numpy as np

from guidance.four_qubit_configuration_guidance_v1 import (
    ConfigurationEnsemble,
    evolve_ensemble,
    unitary_step,
)
from guidance.live_bohm_guidance_v1 import (
    BohmEventFamily,
    BohmGuidanceConfig,
    LiveBohmGuidance,
    unitary_generator,
)
from qmw_circuit_bridge import H, cnot_unitary, single_qubit_unitary
from qmw_circuit_bridge import PilotWaveGraph
from density.density_matrix_engine_4q import (
    CircuitEnabledPopulationMixin,
    GuidanceVector,
)


def basis_density(index: int, dimension: int = 16) -> np.ndarray:
    ket = np.zeros(dimension, dtype=np.complex128)
    ket[index] = 1.0
    return np.outer(ket, ket.conj())


class LiveBohmGuidanceTests(unittest.TestCase):
    def test_generators_reproduce_supported_gate_density_actions(self):
        rng = np.random.default_rng(12)
        ket = rng.normal(size=16) + 1j * rng.normal(size=16)
        ket /= np.linalg.norm(ket)
        rho = np.outer(ket, ket.conj())
        gates = (
            single_qubit_unitary(H, 0, 4),
            cnot_unitary(0, 2, 4),
            cnot_unitary(1, 3, 4) @ single_qubit_unitary(H, 1, 4),
        )
        duration = 0.17
        for gate in gates:
            generator = unitary_generator(gate, duration)
            reconstructed = unitary_step(generator, duration)
            expected = gate @ rho @ gate.conj().T
            actual = reconstructed @ rho @ reconstructed.conj().T
            np.testing.assert_allclose(actual, expected, atol=2e-12)

    def test_unfolded_hadamard_obeys_equivariance(self):
        rho = basis_density(0)
        gate = single_qubit_unitary(H, 0, 4)
        duration = 0.2
        generator = unitary_generator(gate, duration)
        ensemble = ConfigurationEnsemble.from_rho(rho, 24_000, seed=71)
        after = evolve_ensemble(
            rho,
            generator,
            ensemble,
            duration=duration,
            microsteps=160,
        )
        np.testing.assert_allclose(
            ensemble.distribution(16),
            np.real(np.diag(after)),
            atol=0.012,
        )

    def test_discontinuous_families_are_distinct_and_grw_retains_configuration(self):
        guidance = LiveBohmGuidance(BohmGuidanceConfig(seed=4))
        rho = basis_density(3)
        guidance.reset(rho)
        before = guidance.configuration
        grw = guidance.record_discontinuity(
            BohmEventFamily.SPONTANEOUS_LOCALIZATION,
            basis_density(12),
            logical_time=1.0,
        )
        self.assertEqual(grw.configuration_after, before)
        measurement = guidance.record_discontinuity(
            BohmEventFamily.EXPLICIT_MEASUREMENT,
            basis_density(12),
            logical_time=1.1,
            ensure_supported=True,
        )
        self.assertEqual(measurement.configuration_after, 12)
        self.assertEqual(
            [event.family for event in guidance.event_history[-2:]],
            [
                BohmEventFamily.SPONTANEOUS_LOCALIZATION,
                BohmEventFamily.EXPLICIT_MEASUREMENT,
            ],
        )
        self.assertEqual(measurement.beable_basis, "computational_z")

    def test_legacy_pilot_uses_source_column_and_zero_current_does_not_move(self):
        hamiltonian = np.array([[0.0, 1.0], [1.0, 0.0]], dtype=complex)
        psi = np.array([1.0, 1j]) / np.sqrt(2.0)
        rho = np.outer(psi, psi.conj())
        pilot = PilotWaveGraph(2, seed=7)
        pilot.node = 1
        pilot._initialized = True
        frame = pilot.update(rho, hamiltonian, 10.0)
        self.assertEqual(frame.node, 1)
        self.assertEqual(frame.next_node, 0)  # positive J[0, 1]: 1 -> 0

        stationary = PilotWaveGraph(2, seed=8)
        stationary.node = 1
        stationary._initialized = True
        frame = stationary.update(rho, np.zeros((2, 2)), 10.0)
        self.assertEqual(frame.node, 1)
        self.assertEqual(frame.next_node, 1)

    def test_population_projection_no_longer_injects_controlled_noise(self):
        guidance = GuidanceVector(
            node=0,
            target_node=8,
            momentum=0.7,
            phase_force=0.2,
            diffusion=1.0,
        )
        first = SimpleNamespace(position=np.zeros(4), velocity=np.zeros(4))
        second = SimpleNamespace(position=np.zeros(4), velocity=np.zeros(4))
        dummy = SimpleNamespace()
        CircuitEnabledPopulationMixin.guide_member(dummy, first, guidance, 0.0)
        CircuitEnabledPopulationMixin.guide_member(dummy, second, guidance, 100.0)
        np.testing.assert_allclose(first.position, second.position)
        np.testing.assert_allclose(first.velocity, second.velocity)


if __name__ == "__main__":
    unittest.main()
