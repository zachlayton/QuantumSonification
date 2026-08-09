import unittest
import threading
import sys
import types
from types import SimpleNamespace
from unittest.mock import patch

import numpy as np

from qac_ibm_wavetable_bridge import (
    ACCOUNT_NAME,
    PAULI15,
    TEMExecutionResult,
    TEM_FUNCTION_NAME,
    build_parser,
    correlation_from_counts,
    expectation_from_counts,
    correlations_to_wavetable,
    counts_to_wavetable,
    local_correlations,
    local_counts,
    local_pauli15,
    local_qft_spectrum,
    pauli15_surface,
    pauli15_quantum_features,
    pair_pauli_observables,
    tem_expectations,
    density_matrix_from_pauli15,
    two_qubit_concurrence,
    transformed_circuit,
    WavetableBridge,
)


BELL_QASM = """OPENQASM 2.0;
include "qelib1.inc";
qreg q[2];
creg c[2];
h q[0];
cx q[0],q[1];
measure q[0] -> c[0];
measure q[1] -> c[1];
"""


class QACIBMWavetableTest(unittest.TestCase):
    def test_default_mode_is_local_and_256_shots(self):
        args = build_parser().parse_args([])
        self.assertEqual(args.mode, "local")
        self.assertEqual(args.shots, 256)
        self.assertFalse(args.confirm_ibm)
        self.assertEqual(args.ibm_max_jobs, 1)
        self.assertEqual(args.transform, "none")
        self.assertEqual(args.ibm_executor, "runtime")
        self.assertEqual(args.tem_precision, 0.1)
        self.assertIsNone(args.ibm_instance)

    def test_tem_pair_observables_follow_qiskit_qubit_order(self):
        observables = pair_pauli_observables(3, 0, 2, ("XI", "YZ"))
        self.assertEqual(observables[0].to_list(), [("IIX", (1 + 0j))])
        self.assertEqual(observables[1].to_list(), [("ZIY", (1 + 0j))])

    def test_tem_adapter_lazy_loads_catalog_and_maps_reference_values(self):
        captured = {}

        class FakeJob:
            job_id = "tem-job-123"

            def result(self):
                return [
                    SimpleNamespace(
                        data=SimpleNamespace(
                            evs=np.array([0.92, -0.88, 0.95]),
                            stds=np.array([0.02, 0.03, 0.01]),
                        ),
                        metadata={
                            "evs_non_mitigated": np.array([0.70, -0.61, 0.75]),
                            "stds_non_mitigated": np.array([0.04, 0.05, 0.03]),
                            "resource_usage": {"qpu_seconds": 1.5},
                        },
                    )
                ]

        class FakeFunction:
            def run(self, **kwargs):
                captured["run"] = kwargs
                return FakeJob()

        class FakeCatalog:
            def __init__(self, **kwargs):
                captured["catalog"] = kwargs

            def load(self, name):
                captured["function_name"] = name
                return FakeFunction()

        fake_module = types.ModuleType("qiskit_ibm_catalog")
        fake_module.QiskitFunctionsCatalog = FakeCatalog
        with patch.dict(sys.modules, {"qiskit_ibm_catalog": fake_module}):
            result = tem_expectations(
                BELL_QASM,
                ("XX", "YY", "ZZ"),
                "ibm_test",
                0,
                1,
                precision=0.08,
                instance_crn="crn:test",
            )

        self.assertEqual(
            captured["catalog"],
            {"channel": "ibm_quantum_platform", "instance": "crn:test"},
        )
        self.assertEqual(captured["function_name"], TEM_FUNCTION_NAME)
        self.assertEqual(captured["run"]["backend_name"], "ibm_test")
        self.assertEqual(
            captured["run"]["options"], {"default_precision": 0.08}
        )
        circuit, observables = captured["run"]["pubs"][0]
        self.assertNotIn("measure", circuit.count_ops())
        self.assertEqual(
            [observable.to_list()[0][0] for observable in observables],
            ["XX", "YY", "ZZ"],
        )
        self.assertEqual(
            result.values, {"XX": 0.92, "YY": -0.88, "ZZ": 0.95}
        )
        self.assertEqual(
            result.raw_values, {"XX": 0.70, "YY": -0.61, "ZZ": 0.75}
        )
        self.assertEqual(result.job_id, "tem-job-123")
        self.assertEqual(result.resource_usage, {"qpu_seconds": 1.5})

    def test_run_ibm_routes_tem_values_through_existing_correlation_publisher(self):
        bridge = object.__new__(WavetableBridge)
        bridge.args = SimpleNamespace(
            ibm_executor="tem",
            mapping="correlations",
            backend="ibm_test",
            qubit_a=0,
            qubit_b=1,
            tem_precision=0.1,
            account=ACCOUNT_NAME,
            ibm_instance=None,
        )
        bridge.lock = threading.RLock()
        bridge.ibm_in_flight_revision = 17
        sent = []
        published = []
        bridge.send = lambda address, value: sent.append((address, value))
        bridge.error = lambda message: self.fail(message)
        bridge.publish_correlations = lambda *args: published.append(args)
        fake_result = TEMExecutionResult(
            values={"XX": 0.9, "YY": -0.8, "ZZ": 0.95},
            stds={"XX": 0.02, "YY": 0.03, "ZZ": 0.01},
            raw_values={"XX": 0.7, "YY": -0.6, "ZZ": 0.75},
            raw_stds={"XX": 0.04, "YY": 0.05, "ZZ": 0.03},
            backend="ibm_test",
            job_id="tem-job-123",
            resource_usage={},
        )
        with patch(
            "qac_ibm_wavetable_bridge.tem_expectations", return_value=fake_result
        ) as mocked_tem:
            bridge.run_ibm(17, BELL_QASM, "none")

        mocked_tem.assert_called_once_with(
            BELL_QASM,
            ("XX", "YY", "ZZ"),
            "ibm_test",
            0,
            1,
            "none",
            0.1,
            ACCOUNT_NAME,
            None,
        )
        self.assertEqual(
            published[0],
            (
                17,
                "ibm",
                fake_result.values,
                2,
                "ibm_test",
                "tem-job-123",
            ),
        )
        self.assertTrue(any(address == "/qmw/tem/result" for address, _ in sent))
        self.assertIsNone(bridge.ibm_in_flight_revision)

    def test_qft_of_basis_state_has_uniform_frequency_bins(self):
        qasm = BELL_QASM.replace("h q[0];\ncx q[0],q[1];", "x q[0];")
        counts, qubits = local_counts(qasm, shots=4096, seed=7, transform="qft")
        self.assertEqual(qubits, 2)
        self.assertEqual(set(counts), {"00", "01", "10", "11"})
        for count in counts.values():
            self.assertLess(abs(count / 4096 - 0.25), 0.04)

    def test_inverse_qft_maps_uniform_state_to_zero_bin(self):
        qasm = BELL_QASM.replace("h q[0];\ncx q[0],q[1];", "h q[0];\nh q[1];")
        counts, _ = local_counts(qasm, shots=256, seed=7, transform="iqft")
        self.assertEqual(counts, {"00": 256})

    def test_qft_and_inverse_qft_round_trip(self):
        from qiskit.quantum_info import Statevector, state_fidelity

        source = transformed_circuit(BELL_QASM)
        forward = transformed_circuit(BELL_QASM, "qft")
        round_trip = forward.copy()
        round_trip.append(forward.data[-1].operation.inverse(), round_trip.qubits)
        self.assertAlmostEqual(
            state_fidelity(Statevector(source), Statevector(round_trip)), 1.0
        )

    def test_live_transform_selector_updates_subsequent_jobs(self):
        bridge = object.__new__(WavetableBridge)
        bridge.lock = threading.RLock()
        bridge.transform = "none"
        bridge.ibm_in_flight_revision = None
        sent = []
        bridge.send = lambda address, value: sent.append((address, value))
        bridge.set_transform("/qmw/wavetable/transform", "QFT")
        self.assertEqual(bridge.transform, "qft")
        self.assertEqual(sent[-1], ("/qmw/wavetable/status", ["transform", "qft"]))

    def test_v5_qft_spectrum_exposes_all_complex_bins(self):
        probabilities, magnitudes, phases, qubits = local_qft_spectrum(BELL_QASM, "qft")
        self.assertEqual(qubits, 2)
        self.assertEqual(probabilities.shape, (4,))
        self.assertEqual(magnitudes.shape, (4,))
        self.assertEqual(phases.shape, (4,))
        self.assertAlmostEqual(float(np.sum(probabilities)), 1.0)
        np.testing.assert_allclose(magnitudes ** 2, probabilities)

    def test_counts_make_exact_normalized_table(self):
        table = counts_to_wavetable({"00": 512, "11": 512})
        self.assertEqual(len(table), 256)
        self.assertAlmostEqual(float(np.max(np.abs(table))), 0.95)
        self.assertAlmostEqual(float(np.mean(table)), 0.0, places=12)

    def test_local_bell_qasm_has_only_correlated_results(self):
        counts, qubits = local_counts(BELL_QASM, shots=1024, seed=7)
        self.assertEqual(qubits, 2)
        self.assertEqual(set(counts), {"00", "11"})
        self.assertEqual(sum(counts.values()), 1024)

    def test_bell_has_expected_xyz_correlation_signature(self):
        values, qubits = local_correlations(BELL_QASM, 0, 1)
        self.assertEqual(qubits, 2)
        self.assertAlmostEqual(values["XX"], 1.0)
        self.assertAlmostEqual(values["YY"], -1.0)
        self.assertAlmostEqual(values["ZZ"], 1.0)
        table = correlations_to_wavetable(values)
        self.assertEqual(len(table), 256)
        self.assertAlmostEqual(float(np.max(np.abs(table))), 0.95)

    def test_correlation_from_counts_uses_qiskit_bit_order(self):
        self.assertAlmostEqual(correlation_from_counts({"00": 5, "11": 5}, 0, 1), 1.0)
        self.assertAlmostEqual(correlation_from_counts({"01": 5, "10": 5}, 0, 1), -1.0)

    def test_single_expectation_from_counts_uses_qiskit_bit_order(self):
        counts = {"00": 6, "01": 2, "10": 1, "11": 1}
        self.assertAlmostEqual(expectation_from_counts(counts, 0), 0.4)
        self.assertAlmostEqual(expectation_from_counts(counts, 1), 0.6)

    def test_pauli15_bell_surface_has_four_rows(self):
        values, _ = local_pauli15(BELL_QASM, 0, 1)
        self.assertAlmostEqual(values["XX"], 1.0)
        self.assertAlmostEqual(values["YY"], -1.0)
        self.assertAlmostEqual(values["ZZ"], 1.0)
        self.assertTrue(all(abs(values[t]) < 1e-12 for t in ("XI", "YI", "ZI", "IX", "IY", "IZ")))
        surface = pauli15_surface(values)
        self.assertEqual(surface.shape, (4, 256))
        for first in range(4):
            for second in range(first + 1, 4):
                self.assertFalse(np.allclose(surface[first], surface[second]))

    def test_pauli15_sign_uses_different_harmonic(self):
        positive = {term: 0.0 for term in PAULI15}
        negative = dict(positive)
        positive["XI"] = 0.5
        negative["XI"] = -0.5
        positive_fft = np.abs(np.fft.rfft(pauli15_surface(positive)[0]))
        negative_fft = np.abs(np.fft.rfft(pauli15_surface(negative)[0]))
        self.assertGreater(positive_fft[1], positive_fft[2])
        self.assertGreater(negative_fft[2], negative_fft[1])

    def test_bell_entanglement_drives_fast_surface_scan(self):
        values, _ = local_pauli15(BELL_QASM, 0, 1)
        polarization, entanglement, correlation, entropy = pauli15_quantum_features(values)
        self.assertAlmostEqual(polarization, 0.0)
        self.assertAlmostEqual(entanglement, 1.0)
        self.assertAlmostEqual(correlation, np.sqrt(1.0 / 3.0))
        self.assertAlmostEqual(entropy, 0.5)

    def test_product_state_drives_slow_surface_scan(self):
        values = {term: 0.0 for term in PAULI15}
        values["ZI"] = values["IZ"] = values["ZZ"] = 1.0
        polarization, entanglement, correlation, entropy = pauli15_quantum_features(values)
        self.assertAlmostEqual(polarization, 1.0)
        self.assertAlmostEqual(entanglement, 0.0)
        self.assertAlmostEqual(correlation, 1.0 / 3.0)
        self.assertAlmostEqual(entropy, 0.0)

    def test_classical_yz_correlation_is_not_entanglement(self):
        values = {term: 0.0 for term in PAULI15}
        values["YZ"] = -1.0
        rho = density_matrix_from_pauli15(values)
        self.assertAlmostEqual(float(np.trace(rho).real), 1.0)
        self.assertAlmostEqual(two_qubit_concurrence(rho), 0.0)


if __name__ == "__main__":
    unittest.main()
