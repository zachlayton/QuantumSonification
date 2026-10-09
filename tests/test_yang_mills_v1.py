from __future__ import annotations

from copy import deepcopy
from dataclasses import replace
import json
from pathlib import Path
import socket
import struct
import subprocess
import sys
import tempfile
import unittest
import numpy as np

from yang_mills_v1.engine import SU2Lattice, dagger, su2_exp
from yang_mills_v1.modal import ModalExcitationAdapter
from yang_mills_v1.osc import PREFIX, UDPClient, encode_bundle, frame_messages
from yang_mills_v1.build_max_host import build


class YangMillsTests(unittest.TestCase):
    def test_force_matches_independent_energy_finite_difference(self):
        model = SU2Lattice(3, seed=12)
        force = model.magnetic_force()
        epsilon = 1e-6
        for x, y, direction, color in ((0, 0, 0, 0), (1, 2, 1, 2), (2, 1, 0, 1)):
            original = model.links[x, y, direction].copy()
            vector = np.zeros(3)
            vector[color] = epsilon
            model.links[x, y, direction] = su2_exp(vector) @ original
            plus = model.snapshot().total_energy
            model.links[x, y, direction] = su2_exp(-vector) @ original
            minus = model.snapshot().total_energy
            model.links[x, y, direction] = original
            self.assertAlmostEqual(force[x, y, direction, color], -(plus - minus) / (2 * epsilon), places=8)

    def test_vacuum_and_pure_gauge_stay_stationary(self):
        model = SU2Lattice(3, amplitude=0)
        rotations = su2_exp(np.random.default_rng(4).normal(size=(3, 3, 3)))
        model.gauge_transform(rotations)
        frame = model.step(0.1, substeps=4)
        self.assertLess(frame.total_energy, 1e-13)
        self.assertLess(np.max(np.abs(model.electric)), 1e-14)

    def test_gauge_invariance_covariance_and_sound(self):
        a = SU2Lattice(4)
        a.step(0.2, substeps=20)
        b = deepcopy(a)
        rotations = su2_exp(np.random.default_rng(41).normal(size=(4, 4, 3)))
        b.gauge_transform(rotations)
        adapters = [ModalExcitationAdapter(), ModalExcitationAdapter()]
        for _ in range(3):
            sa, sb = a.snapshot(), b.snapshot()
            np.testing.assert_allclose(sa.site_energy, sb.site_energy, atol=2e-14)
            np.testing.assert_allclose(sa.wilson_trace, sb.wilson_trace, atol=2e-14)
            fa, fb = adapters[0].update(sa), adapters[1].update(sb)
            np.testing.assert_allclose(fa.magnitudes, fb.magnitudes, atol=2e-14)
            np.testing.assert_allclose(fa.speeds, fb.speeds, atol=1e-13)
            a.step(0.03, substeps=3)
            b.step(0.03, substeps=3)
        check = deepcopy(a)
        check.gauge_transform(rotations)
        np.testing.assert_allclose(check.links, b.links, atol=3e-14)
        np.testing.assert_allclose(check.electric, b.electric, atol=3e-14)

    def test_long_run_constraints_and_energy(self):
        model = SU2Lattice()
        peak_drift = 0
        for _ in range(500):
            frame = model.step(0.02, substeps=2)
            peak_drift = max(peak_drift, abs(frame.relative_energy_drift))
        self.assertLess(peak_drift, 5e-5)
        self.assertLess(frame.gauss_error, 1e-12)
        self.assertLess(frame.unitarity_error, 1e-12)
        self.assertLess(frame.determinant_error, 1e-12)
        self.assertGreater(np.sum(frame.electric_energy), 0.1)

    def test_second_order_convergence(self):
        trajectories = []
        for steps in (25, 50, 100, 400):
            model = SU2Lattice(3, seed=3)
            for _ in range(steps):
                model.step(1.0 / steps)
            trajectories.append(model)
        errors = [np.linalg.norm(m.links - trajectories[-1].links)
                  + np.linalg.norm(m.electric - trajectories[-1].electric)
                  for m in trajectories[:-1]]
        self.assertGreater(errors[0] / errors[1], 3.8)
        self.assertGreater(errors[1] / errors[2], 3.8)

    def test_covariant_laplacian_is_psd_and_has_invariant_spectrum(self):
        model = SU2Lattice(3)
        laplacian = model.covariant_laplacian()
        np.testing.assert_allclose(laplacian, dagger(laplacian), atol=1e-14)
        spectrum = np.linalg.eigvalsh(laplacian)
        self.assertGreaterEqual(spectrum.min(), -1e-12)
        rng = np.random.default_rng(32)
        field = rng.normal(size=(3, 3, 2)) + 1j * rng.normal(size=(3, 3, 2))
        difference_energy = 0.0
        for direction in range(2):
            transported = np.einsum("...ij,...j->...i", model.links[:, :, direction],
                                    np.roll(field, -1, axis=direction))
            difference_energy += np.sum(np.abs(field - transported) ** 2)
        self.assertAlmostEqual(np.vdot(field.ravel(), laplacian @ field.ravel()).real,
                               difference_energy, places=11)
        model.gauge_transform(su2_exp(rng.normal(size=(3, 3, 3))))
        np.testing.assert_allclose(spectrum, np.linalg.eigvalsh(model.covariant_laplacian()), atol=1e-13)

    def test_modal_mute_bounds_and_absolute_calibration(self):
        model = SU2Lattice()
        field = model.snapshot()
        muted = ModalExcitationAdapter(coupling=0).update(field)
        np.testing.assert_array_equal(muted.magnitudes, np.zeros(16))
        np.testing.assert_array_equal(muted.speeds, np.zeros(16))
        adapter = ModalExcitationAdapter(coupling=0.6, smoothing_seconds=0)
        first = adapter.update(field)
        weaker = replace(field, time=0.1, electric_energy=field.electric_energy / 2,
                         magnetic_energy=field.magnetic_energy / 2)
        second = adapter.update(weaker)
        self.assertTrue(np.all(second.magnitudes < first.magnitudes))
        self.assertTrue(np.all((second.speeds >= 0) & (second.speeds <= 0.6)))
        self.assertTrue(np.all((first.magnitudes >= 0) & (first.magnitudes <= 0.6)))
        with self.assertRaises(ValueError):
            adapter.update(weaker)

    def test_parameter_validation(self):
        for options in ({"size": 1}, {"size": 2.5}, {"beta": float("nan")}, {"amplitude": -1}):
            with self.assertRaises(ValueError):
                SU2Lattice(**options)
        for options in ({"coupling": 2}, {"energy_scale": 0}, {"smoothing_seconds": float("nan")}):
            with self.assertRaises(ValueError):
                ModalExcitationAdapter(**options)
        model = SU2Lattice()
        with self.assertRaises(ValueError):
            model.step(float("nan"))
        with self.assertRaises(ValueError):
            model.step(0.1, substeps=1.5)

    def test_real_udp_bundle_is_bounded_and_preserves_frame(self):
        frame = ModalExcitationAdapter().update(SU2Lattice().snapshot())
        messages = frame_messages(frame, 8)
        receiver = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        receiver.bind(("127.0.0.1", 0))
        receiver.settimeout(1)
        client = UDPClient(port=receiver.getsockname()[1])
        try:
            client.publish(frame, 8)
            payload, _ = receiver.recvfrom(2048)
        finally:
            client.close()
            receiver.close()
        self.assertEqual(payload, encode_bundle(messages))
        self.assertLess(len(payload), 1400)
        self.assertEqual(payload[:16], b"#bundle\0" + struct.pack(">Q", 1))
        decoded = []
        position = 16
        while position < len(payload):
            size = struct.unpack_from(">i", payload, position)[0]
            position += 4
            message = payload[position:position + size]
            position += size
            end = message.index(0)
            address = message[:end].decode()
            offset = (end + 4) // 4 * 4
            end = message.index(0, offset)
            tags = message[offset:end].decode()[1:]
            offset = (end + 4) // 4 * 4
            values = struct.unpack_from(">" + tags, message, offset)
            decoded.append((address, values))
        self.assertEqual(decoded[0][0], PREFIX + "/begin")
        self.assertEqual(decoded[-1], (PREFIX + "/end", (8,)))
        self.assertTrue(all(values[0] == 8 for _, values in decoded))
        np.testing.assert_allclose(decoded[1][1][1:], frame.magnitudes, rtol=1e-6)

    def test_max_host_routes_to_existing_modal_dsp_and_starts_muted(self):
        patch = build()["patcher"]
        boxes = {x["box"]["id"]: x["box"] for x in patch["boxes"]}
        links = {(tuple(x["patchline"]["source"]), tuple(x["patchline"]["destination"]))
                 for x in patch["lines"]}
        self.assertEqual(boxes["udp"]["text"], "udpreceive 7416")
        self.assertIn("modal_resonator16_mc_v4", boxes["gen"]["text"])
        self.assertIn((("adapter", 0), ("gen", 0)), links)
        self.assertIn((("watchdog", 0), ("adapter", 0)), links)
        self.assertEqual(boxes["masterinit"]["text"], "0.")
        self.assertEqual(boxes["dac"]["maxclass"], "ezdac~")
        path = Path(__file__).resolve().parents[1] / "QMW_Hilbert_Suite" / "QMW_Yang_Mills_Modal_Resonator_v1.maxpat"
        self.assertEqual(json.loads(path.read_text())["patcher"], patch)
        for source, target in links:
            self.assertIn(source[0], boxes)
            self.assertIn(target[0], boxes)

    def test_cli_streams_and_releases_excitation_and_preserves_manifests(self):
        root = Path(__file__).resolve().parents[1]
        receiver = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        receiver.bind(("127.0.0.1", 0))
        receiver.settimeout(1)
        with tempfile.TemporaryDirectory() as directory:
            manifest = Path(directory) / "run.json"
            command = [sys.executable, "-m", "yang_mills_v1", "--osc", "--steps", "8",
                       "--dt", "0.01", "--port", str(receiver.getsockname()[1]),
                       "--json", str(manifest)]
            try:
                result = subprocess.run(command, cwd=root, capture_output=True, text=True, timeout=5)
                self.assertEqual(result.returncode, 0, result.stderr)
                packets = []
                while True:
                    try:
                        packets.append(receiver.recvfrom(2048)[0])
                    except socket.timeout:
                        break
                self.assertGreaterEqual(len(packets), 3)
                # Final bundle explicitly releases all sixteen magnitudes.
                payload = packets[-1]
                marker = (PREFIX + "/magnitude").encode()
                offset = payload.index(marker)
                string_end = payload.index(0, offset)
                tags_start = offset + ((string_end - offset + 4) // 4) * 4
                tags_end = payload.index(0, tags_start)
                values_start = tags_start + ((tags_end - tags_start + 4) // 4) * 4
                values = struct.unpack_from(">i16f", payload, values_start)
                self.assertTrue(all(value == 0 for value in values[1:]))
                saved = manifest.read_bytes()
                self.assertEqual(json.loads(saved)["completed_steps"], 8)
                repeated = subprocess.run(command, cwd=root, capture_output=True, text=True, timeout=5)
                self.assertNotEqual(repeated.returncode, 0)
                self.assertEqual(manifest.read_bytes(), saved)
            finally:
                receiver.close()


if __name__ == "__main__":
    unittest.main()
