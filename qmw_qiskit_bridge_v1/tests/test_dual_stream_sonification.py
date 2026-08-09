from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest
import wave

import numpy as np

from qmw_qiskit_bridge_v1.experiments import compare_floquet_routes
from qmw_qiskit_bridge_v1.sonification import render_dual_stream_sonification


class DualStreamSonificationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.comparison = compare_floquet_routes(periods=4)

    def test_exact_and_transformed_share_one_mapping(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            render = render_dual_stream_sonification(
                directory,
                transformed_route="qiskit_statevector_exact",
                comparison=self.comparison,
                sample_rate=8_000,
                seconds_per_period=0.08,
            )
            # Independent exact implementations differ only at roundoff scale.
            self.assertLess(np.max(np.abs(render.audio.difference)), 1e-10)
            # Panning differs, but each stereo stream collapses to the same mono signal.
            exact_mono = np.linalg.norm(render.audio.reference, axis=1)
            transformed_mono = np.linalg.norm(render.audio.transformed, axis=1)
            np.testing.assert_allclose(exact_mono, transformed_mono, atol=1e-10)

    def test_mix_is_exact_sum_under_one_shared_gain(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            render = render_dual_stream_sonification(
                directory,
                transformed_route="qiskit_trotter_order_2",
                comparison=self.comparison,
                sample_rate=8_000,
                seconds_per_period=0.08,
            )
            np.testing.assert_allclose(
                render.audio.difference,
                render.audio.difference_local_z
                + render.audio.difference_bond_zz
                + render.audio.difference_trace_distance,
                atol=1e-14,
            )
            np.testing.assert_allclose(
                render.audio.mix,
                render.audio.reference
                + render.audio.transformed
                + render.audio.difference,
                atol=1e-14,
            )
            self.assertLessEqual(float(np.max(np.abs(render.audio.mix))), 0.95 + 1e-12)

    def test_waves_metadata_and_source_data_are_complete(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            render = render_dual_stream_sonification(
                directory,
                transformed_route="aer_noisy",
                comparison=self.comparison,
                sample_rate=8_000,
                seconds_per_period=0.08,
            )
            for path in (
                render.reference_path,
                render.transformed_path,
                render.difference_path,
                render.difference_local_z_path,
                render.difference_bond_zz_path,
                render.difference_trace_distance_path,
                render.mix_path,
            ):
                with wave.open(str(path), "rb") as audio:
                    self.assertEqual(audio.getnchannels(), 2)
                    self.assertEqual(audio.getframerate(), 8_000)
                    self.assertEqual(audio.getnframes(), 4 * 640)
            metadata = json.loads(render.metadata_path.read_text(encoding="utf-8"))
            source = np.load(render.data_path)
            self.assertEqual(metadata["schema"], "qmw.dual_stream_sonification.v1")
            self.assertEqual(metadata["transformed_route"], "aer_noisy")
            self.assertEqual(
                set(metadata["streams"]["difference"]["components"]),
                {"local_z", "bond_zz", "trace_distance"},
            )
            self.assertEqual(source["exact_z"].shape, (5, 4))
            self.assertEqual(source["delta_zz_bonds"].shape, (5, 3))
            self.assertGreater(float(np.max(source["trace_distance"])), 0.0)


if __name__ == "__main__":
    unittest.main()
