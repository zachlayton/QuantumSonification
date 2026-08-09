from __future__ import annotations

from pathlib import Path
import subprocess
import unittest

import numpy as np

from qmw_qiskit_bridge_v1.experiments import compare_floquet_routes
from qmw_qiskit_bridge_v1.realtime import QMWComparisonOSCPublisher, frame_messages
from qmw_qiskit_bridge_v1.realtime.osc_instrument import comparison_frame
from qmw_qiskit_bridge_v1.sonification.dual_stream import _observables


class CaptureClient:
    def __init__(self) -> None:
        self.messages = []

    def send_message(self, address, value) -> None:
        self.messages.append((address, list(value)))


class RealtimeOSCTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.comparison = compare_floquet_routes(periods=4)

    def test_frame_transaction_is_atomic_and_revisioned(self) -> None:
        frame = comparison_frame(self.comparison, "aer_noisy", tick=2, revision=31)
        messages = frame_messages(frame)
        self.assertEqual(messages[0][0], "/qmw/qiskit_compare/frame/begin")
        self.assertEqual(messages[-1], ("/qmw/qiskit_compare/frame/end", [31]))
        self.assertTrue(all(values[0] == 31 for _, values in messages))
        self.assertEqual(len(messages), 9)

    def test_live_values_match_comparison_density_matrices(self) -> None:
        frame = comparison_frame(self.comparison, "aer_noisy", tick=3, revision=1)
        exact_z, exact_zz, _ = _observables(
            self.comparison.routes["qmw_dense_exact"]
        )
        transformed_z, transformed_zz, _ = _observables(
            self.comparison.routes["aer_noisy"]
        )
        np.testing.assert_allclose(frame.exact_z, exact_z[3])
        np.testing.assert_allclose(frame.transformed_z, transformed_z[3])
        np.testing.assert_allclose(frame.delta_z, transformed_z[3] - exact_z[3])
        np.testing.assert_allclose(frame.delta_zz, transformed_zz[3] - exact_zz[3])

    def test_publisher_advances_and_loops_without_partial_frames(self) -> None:
        client = CaptureClient()
        publisher = QMWComparisonOSCPublisher(
            client,
            periods=4,
            transformed_route="qiskit_trotter_order_2",
            comparison=self.comparison,
        )
        first = publisher.publish_current()
        publisher.advance()
        second = publisher.publish_current()
        self.assertEqual((first.tick, second.tick), (0, 1))
        self.assertEqual((first.revision, second.revision), (1, 2))
        self.assertEqual(len(client.messages), 18)
        for start in (0, 9):
            self.assertTrue(client.messages[start][0].endswith("/begin"))
            self.assertTrue(client.messages[start + 8][0].endswith("/end"))

    def test_noise_change_is_staged_until_reset(self) -> None:
        client = CaptureClient()
        publisher = QMWComparisonOSCPublisher(
            client,
            periods=4,
            comparison=self.comparison,
        )
        original = publisher.comparison
        publisher.stage_noise_scale(0.5)
        self.assertIs(publisher.comparison, original)
        # Avoid rebuilding in this unit test; verify the staged contract directly.
        self.assertEqual(publisher._pending_noise_scale, 0.5)

    def test_supercollider_listener_stages_and_commits_matching_revision(self) -> None:
        path = Path(__file__).resolve().parents[1] / "supercollider" / "qmw_qiskit_compare_instrument_v1.scd"
        text = path.read_text(encoding="utf-8")
        self.assertIn("/qmw/qiskit_compare/frame/begin", text)
        self.assertIn("/qmw/qiskit_compare/frame/end", text)
        self.assertIn("msg[1].asInteger == ~qmwCompareStageRevision", text)
        self.assertIn("~qmwCompareSynth.setn(\\deltaZZ", text)

    def test_realtime_example_imports_from_outside_component_directory(self) -> None:
        component = Path(__file__).resolve().parents[1]
        example = component / "examples" / "run_realtime_comparison.py"
        result = subprocess.run(
            [
                "/Users/zlayton/miniconda3/envs/music/bin/python",
                "-c",
                (
                    "import runpy; "
                    f"runpy.run_path({str(example)!r}, run_name='qmw_import_test')"
                ),
            ],
            cwd="/private/tmp",
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
