import csv
import json
from pathlib import Path
import tempfile
import unittest
import wave

import numpy as np

from density.quantum_temporal_monitor_v1 import (
    DetectorModel,
    DrivenQubitExperimentConfig,
    FixedResonator,
    GateOp,
    JumpChannel,
    MeasureOp,
    MonitorOp,
    QuantumPerformanceGraph,
    QuantumEvent,
    QuantumRhythmProjector,
    QuantumTrajectoryEngine,
    SIGMA_MINUS,
    SIGMA_X,
    advance_monitored_frame,
    bootstrap_factorial_cumulants,
    counts_per_window,
    detector_corrected_factorial_cumulants,
    export_driven_qubit_experiment,
    factorial_cumulants,
    full_counting_statistics,
    inter_event_intervals,
    poisson_count_diagnostics,
    run_driven_qubit_experiment,
)


GROUND = np.diag([1.0, 0.0]).astype(np.complex128)
EXCITED = np.diag([0.0, 1.0]).astype(np.complex128)
ZERO_H = np.zeros((2, 2), dtype=np.complex128)


class _JumpNowRng:
    def random(self):
        return 0.0

    def choice(self, _size, p):
        assert np.isclose(np.sum(p), 1.0)
        return 0


class ProcessContractTests(unittest.TestCase):
    def test_gate_measure_and_monitor_are_distinct_shared_process_objects(self):
        projectors = (
            np.diag([1.0, 0.0]).astype(np.complex128),
            np.diag([0.0, 1.0]).astype(np.complex128),
        )
        gate = GateOp("gate:h", 0.1, (0,), SIGMA_X)
        measure = MeasureOp("measure:z", 0.2, (0,), projectors)
        monitor = MonitorOp(
            "monitor:decay",
            0.3,
            1.0,
            (JumpChannel("decay", 0.1 * SIGMA_MINUS),),
        )
        graph = QuantumPerformanceGraph((gate, measure, monitor))
        self.assertIs(graph.operations[2], monitor)
        self.assertEqual([type(value).__name__ for value in graph.operations], ["GateOp", "MeasureOp", "MonitorOp"])
        self.assertFalse(gate.unitary.flags.writeable)
        self.assertFalse(measure.kraus_operators[0].flags.writeable)

    def test_invalid_unitary_instrument_and_monitor_span_fail_closed(self):
        with self.assertRaises(ValueError):
            GateOp("bad", 0.0, (0,), np.ones((2, 2)))
        with self.assertRaises(ValueError):
            MeasureOp("bad", 0.0, (0,), (np.eye(2) * 0.5,))
        with self.assertRaises(ValueError):
            MonitorOp("bad", 1.0, 1.0, (JumpChannel("decay", SIGMA_MINUS),))

    def test_duplicate_graph_identity_is_rejected(self):
        monitor = MonitorOp("shared", 0.0, 1.0, (JumpChannel("decay", SIGMA_MINUS),))
        with self.assertRaises(ValueError):
            QuantumPerformanceGraph((monitor, monitor))

    def test_simulated_event_cannot_claim_detector_evidence(self):
        with self.assertRaisesRegex(ValueError, "detector"):
            QuantumEvent(
                event_id="jump",
                time_s=0.1,
                source_id="monitor",
                channel="decay",
                rate_hz=1.0,
                probability=0.01,
                backaction_norm=1.0,
                rho_before=EXCITED,
                rho_after=GROUND,
                record_confidence=1.0,
            )


class TrajectoryTests(unittest.TestCase):
    def test_zero_rate_no_jump_preserves_the_ground_state(self):
        engine = QuantumTrajectoryEngine(seed=4)
        state, event = engine.step(
            rho=GROUND,
            hamiltonian=ZERO_H,
            channels=(JumpChannel("off", np.zeros((2, 2))),),
            time_s=0.0,
            dt_s=0.01,
            source_id="monitor",
        )
        np.testing.assert_allclose(state, GROUND)
        self.assertIsNone(event)

    def test_decay_jump_is_conditioned_normalized_and_auditable(self):
        engine = QuantumTrajectoryEngine(seed=4)
        engine.rng = _JumpNowRng()
        state, event = engine.step(
            rho=EXCITED,
            hamiltonian=ZERO_H,
            channels=(JumpChannel("decay", 2.0 * SIGMA_MINUS),),
            time_s=0.25,
            dt_s=0.01,
            source_id="monitor",
        )
        self.assertIsNotNone(event)
        np.testing.assert_allclose(state, GROUND)
        np.testing.assert_allclose(event.rho_before, EXCITED)
        np.testing.assert_allclose(event.rho_after, GROUND)
        self.assertEqual(event.origin, "simulated_quantum_trajectory")
        self.assertAlmostEqual(event.rate_hz, 4.0)
        self.assertAlmostEqual(event.probability, 0.04)
        self.assertGreater(event.backaction_norm, 1.0)
        self.assertIsNone(event.record_confidence)

    def test_unreliable_time_step_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "too large"):
            QuantumTrajectoryEngine(seed=1).step(
                rho=EXCITED,
                hamiltonian=ZERO_H,
                channels=(JumpChannel("decay", 2.0 * SIGMA_MINUS),),
                time_s=0.0,
                dt_s=0.02,
                source_id="monitor",
            )

    def test_backaction_precedes_observables_and_excitation(self):
        engine = QuantumTrajectoryEngine(seed=4)
        engine.rng = _JumpNowRng()
        monitor = MonitorOp(
            "monitor",
            0.0,
            1.0,
            (JumpChannel("decay", 2.0 * SIGMA_MINUS),),
        )
        observed = []

        def observe(rho):
            observed.append(np.array(rho, copy=True))
            return {"ground_population": float(rho[0, 0].real)}

        frame = advance_monitored_frame(
            engine=engine,
            rho=EXCITED,
            hamiltonian=ZERO_H,
            monitor=monitor,
            time_s=0.0,
            dt_s=0.01,
            revision=1,
            projector=QuantumRhythmProjector(),
            observable_function=observe,
        )
        np.testing.assert_allclose(observed[0], GROUND)
        np.testing.assert_allclose(frame.rho, GROUND)
        self.assertEqual(frame.observables["ground_population"], 1.0)
        self.assertEqual(frame.excitations[0].event_id, frame.quantum_event.event_id)
        self.assertEqual(
            frame.causal_order,
            ("quantum_measurement_and_backaction", "observables", "rhythm_projection", "sound"),
        )

    def test_seeded_driven_qubit_trajectory_is_reproducible_and_physical(self):
        config = DrivenQubitExperimentConfig(duration_s=2.0, counting_window_s=0.5, seed=42)
        first = run_driven_qubit_experiment(config)
        second = run_driven_qubit_experiment(config)
        self.assertEqual(
            [(event.time_s, event.channel) for event in first.events],
            [(event.time_s, event.channel) for event in second.events],
        )
        self.assertGreater(len(first.events), 0)
        self.assertTrue(all(0.0 < event.time_s <= config.duration_s for event in first.events))
        self.assertTrue(all(a.time_s < b.time_s for a, b in zip(first.events, first.events[1:])))
        self.assertAlmostEqual(float(np.trace(first.final_rho).real), 1.0, places=12)
        self.assertGreaterEqual(float(np.linalg.eigvalsh(first.final_rho).min()), -1e-9)
        self.assertFalse(first.final_rho.flags.writeable)


class RhythmAndStatisticsTests(unittest.TestCase):
    def test_uniform_time_dilation_preserves_ratios_and_constant_amplitude(self):
        result = run_driven_qubit_experiment(
            DrivenQubitExperimentConfig(duration_s=2.0, counting_window_s=0.5, seed=42)
        )
        original = [QuantumRhythmProjector(1.0).project(event) for event in result.events]
        slow = [QuantumRhythmProjector(100.0).project(event) for event in result.events]
        np.testing.assert_allclose(
            [value.onset_s for value in slow],
            np.asarray([value.onset_s for value in original]) * 100.0,
        )
        self.assertEqual({value.amplitude for value in original + slow}, {1.0})
        np.testing.assert_allclose(
            inter_event_intervals(result.events),
            np.diff([event.time_s for event in result.events]),
        )

    def test_count_distribution_and_first_four_factorial_cumulants(self):
        counts = np.array([0, 1, 0, 1], dtype=np.int64)
        expected = np.array([0.5, -0.25, 0.25, -0.375])
        np.testing.assert_allclose(factorial_cumulants(counts, 4), expected)

        result = run_driven_qubit_experiment(
            DrivenQubitExperimentConfig(duration_s=1.0, counting_window_s=0.25, seed=42)
        )
        statistics = full_counting_statistics(
            result.events, window_s=0.25, duration_s=1.0, maximum_order=4
        )
        self.assertAlmostEqual(float(statistics.probabilities.sum()), 1.0)
        self.assertEqual(len(statistics.factorial_cumulants), 4)
        self.assertEqual(int(statistics.counts.sum()), len(result.events))
        with self.assertRaises(ValueError):
            statistics.counts.setflags(write=True)

    def test_count_windows_reject_partial_or_out_of_span_data(self):
        result = run_driven_qubit_experiment(
            DrivenQubitExperimentConfig(duration_s=1.0, counting_window_s=0.25, seed=42)
        )
        with self.assertRaises(ValueError):
            counts_per_window(result.events, window_s=0.3, duration_s=1.0)
        with self.assertRaises(ValueError):
            counts_per_window(result.events, window_s=0.25, duration_s=0.5)

    def test_bootstrap_intervals_are_seeded_and_poisson_comparison_is_bounded(self):
        counts = np.array([0, 1, 2, 1, 0, 3, 1, 2], dtype=np.int64)
        first = bootstrap_factorial_cumulants(counts, 4, resamples=250, seed=91)
        second = bootstrap_factorial_cumulants(counts, 4, resamples=250, seed=91)
        np.testing.assert_array_equal(first, second)
        self.assertEqual(first.shape, (4, 2))
        self.assertTrue(np.all(first[:, 0] <= first[:, 1]))
        diagnostics = poisson_count_diagnostics(counts)
        self.assertEqual(diagnostics["window_count"], len(counts))
        self.assertGreaterEqual(diagnostics["poisson_total_variation_distance"], 0.0)
        self.assertLessEqual(diagnostics["poisson_total_variation_distance"], 1.0)
        self.assertIn("descriptive_only", diagnostics["inference"])

    def test_declared_detector_model_corrects_factorial_cumulants_analytically(self):
        model = DetectorModel(efficiency=0.5, false_event_rate_hz=2.0)
        corrected = detector_corrected_factorial_cumulants(
            [2.0, 3.0, 4.0], window_s=0.25, model=model
        )
        np.testing.assert_allclose(corrected, [3.0, 12.0, 32.0])
        with self.assertRaises(ValueError):
            DetectorModel(efficiency=0.0)

    def test_full_statistics_export_uncertainty_and_detector_assumptions(self):
        result = run_driven_qubit_experiment(
            DrivenQubitExperimentConfig(duration_s=1.0, counting_window_s=0.25, seed=42)
        )
        record = result.statistics.to_record()
        self.assertEqual(len(record["factorial_cumulant_ci95"]), 4)
        self.assertEqual(record["bootstrap"]["resamples"], 2000)
        self.assertEqual(record["detector_model"]["efficiency"], 1.0)
        np.testing.assert_allclose(
            record["detector_corrected_factorial_cumulants"],
            record["factorial_cumulants"],
        )
        self.assertIn("does not establish", record["poisson_diagnostics"]["claim_boundary"])


class ExportTests(unittest.TestCase):
    def test_export_contains_data_statistics_synchronized_svg_and_audio(self):
        result = run_driven_qubit_experiment(
            DrivenQubitExperimentConfig(duration_s=1.0, counting_window_s=0.25, seed=42)
        )
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary)
            manifest_path = export_driven_qubit_experiment(
                result,
                output,
                resonator=FixedResonator(frequency_hz=220.0, decay_s=0.05, sample_rate_hz=2_000),
            )
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(manifest["event_count"], len(result.events))
            self.assertEqual(manifest["scientific_scope"]["rhythm_origin"], "emergent simulated jump timestamps")
            self.assertIsNone(manifest["projection"]["meter"])
            self.assertIsNone(manifest["projection"]["quantization"])
            self.assertEqual(len(manifest["counting_statistics"]["factorial_cumulants"]), 4)
            self.assertEqual(len(manifest["counting_statistics"]["factorial_cumulant_ci95"]), 4)
            self.assertIn("resolution of the measurement problem", manifest["scientific_scope"]["not_claimed"])

            svg = (output / "circuit_zx_temporal_timeline.svg").read_text(encoding="utf-8")
            self.assertGreaterEqual(svg.count(result.config.monitor_id), 2)
            self.assertIn("jump times emergent and unquantized", svg)
            self.assertNotIn("beat grid</text>", svg)

            with (output / "resonator_excitations_100x.csv").open(newline="", encoding="utf-8") as stream:
                rows = list(csv.DictReader(stream))
            self.assertEqual(len(rows), len(result.events))
            for event, row in zip(result.events, rows):
                self.assertAlmostEqual(float(row["onset_s"]), event.time_s * 100.0)
                self.assertEqual(float(row["amplitude"]), 1.0)

            frame_counts = []
            for scale in ("1x", "10x", "100x"):
                with wave.open(str(output / f"fixed_resonator_{scale}.wav"), "rb") as stream:
                    self.assertEqual(stream.getnchannels(), 1)
                    self.assertEqual(stream.getframerate(), 2_000)
                    frame_counts.append(stream.getnframes())
            self.assertLess(frame_counts[0], frame_counts[1])
            self.assertLess(frame_counts[1], frame_counts[2])
            self.assertEqual(set(manifest["files"]), {path.name for path in output.iterdir()} - {"manifest.json"})


if __name__ == "__main__":
    unittest.main(verbosity=2)
