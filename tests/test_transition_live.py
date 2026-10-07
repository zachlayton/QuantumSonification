from dataclasses import replace
import unittest
import numpy as np

from qmw.acoustics.note_timbre_live import SourceSnapshot
from qmw.acoustics.transition_live import (
    TransitionControls, TransitionProjector, TransitionWorker, observable_for,
    validate_arguments, ARGUMENT_COUNT, MATRIX_END, FRAME_ADDRESS, HARMONY_COUNT,
)


def snapshot(revision=0, rho=None):
    return SourceSnapshot.capture(rho=np.eye(16)/16 if rho is None else rho,
        H=np.diag(np.arange(16, dtype=float)), source_revision=revision,
        source_time=revision*.02, dt=.02, session_id="fixture", source_id="test")


class TransitionLiveTests(unittest.TestCase):
    def test_local_collective_and_pair_observables_are_hermitian_contractions(self):
        for scope in range(3):
            for qubit in range(4):
                for axis in range(3):
                    for blend in (0., .37, 1.):
                        a, label = observable_for(TransitionControls(scope=scope, qubit=qubit, axis=axis, blend=blend))
                        np.testing.assert_array_equal(a, a.conj().T)
                        self.assertLessEqual(max(abs(np.linalg.eigvalsh(a))), 1+1e-12)
                        self.assertFalse(a.flags.writeable)
                        self.assertTrue(label)
        a, label = observable_for(TransitionControls(axis=0, qubit=0))
        self.assertEqual(label, "IIIX")
        np.testing.assert_array_equal(a, np.kron(np.eye(8), [[0, 1], [1, 0]]))
        self.assertEqual(observable_for(TransitionControls(axis=2, scope=2, qubit=3))[1], "ZIIZ")

    def test_control_wire_roundtrip_and_invalid_settings(self):
        cfg = TransitionControls(revision=3, hold=True, blend=.4, octave=-1)
        self.assertEqual(TransitionControls.from_arguments(cfg.arguments()), cfg)
        for kwargs in ({"revision": -1}, {"axis": 3}, {"qubit": 4}, {"scope": 3}, {"blend": np.nan},
                       {"blend": 2}, {"rate_hz": 0}, {"rate_hz": 11}, {"duration": 0}, {"voices": 0},
                       {"base_hz": 20000}, {"hold": 1}, {"activity_threshold": -1}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                TransitionControls(**kwargs)
        for args in ([], [0]*17, [0]*19, [0]*7+[.5]+[0]*10):
            with self.assertRaises(ValueError):
                TransitionControls.from_arguments(args)

    def test_live_x_and_z_follow_selection_rules(self):
        x = TransitionProjector(TransitionControls(axis=0)).process(snapshot(), now=0)
        self.assertEqual(len(x.frame.transitions), 16)
        self.assertIsNotNone(x.note)
        z = TransitionProjector(TransitionControls(axis=2)).process(snapshot(), now=0)
        self.assertEqual(z.frame.transitions, ())
        self.assertIsNone(z.note)

    def test_hold_keeps_H_rho_and_allows_operator_changes_then_releases(self):
        projector = TransitionProjector(TransitionControls(axis=0, hold=True))
        first = projector.process(snapshot(), now=0)
        later = snapshot(1, np.diag([1.]+[0.]*15))
        self.assertTrue(projector.configure(TransitionControls(revision=1, axis=2, hold=True)))
        held = projector.process(later, now=1)
        self.assertEqual(held.source_digest, first.source_digest)
        self.assertEqual(held.snapshot.context.frame_id, 0)
        self.assertEqual(held.observed_revision, 1)
        self.assertEqual(held.snapshot.operator_label, "IIIZ")
        self.assertEqual(held.frame.transitions, ())
        self.assertFalse(any("revision:0" in p and "coupling" in p for p in held.frame.provenance))
        projector.configure(TransitionControls(revision=2, axis=0))
        released = projector.process(snapshot(2, later.rho), now=2)
        self.assertNotEqual(released.source_digest, first.source_digest)

    def test_strongest_cycle_selected_and_thresholds(self):
        cycle = TransitionProjector(TransitionControls(axis=0, selection=1))
        pairs = [(cycle.process(snapshot(i), now=float(i)).note.source_state) for i in range(3)]
        self.assertEqual(pairs, [0, 1, 2])
        selected = TransitionProjector(TransitionControls(axis=0, selection=2, source=6, target=7))
        packet = selected.process(snapshot(), now=0)
        self.assertEqual((packet.note.source_state, packet.note.target_state), (6, 7))
        selected.configure(replace(selected.config, revision=1, target=6))
        self.assertIsNone(selected.process(snapshot(1), now=1).note)
        for kwargs in ({"activity_threshold": .0625}, {"amplitude_threshold": 1}):
            packet = TransitionProjector(TransitionControls(axis=0, **kwargs)).process(snapshot(), now=0)
            self.assertEqual(packet.frame.transitions, ())

    def test_musical_clock_has_no_catchup_and_configuration_cannot_burst(self):
        p = TransitionProjector(TransitionControls(axis=0, rate_hz=2))
        self.assertIsNotNone(p.process(snapshot(), now=0).note)
        self.assertIsNone(p.process(snapshot(1), now=.1).note)
        p.configure(replace(p.config, revision=1, blend=.2))
        self.assertIsNone(p.process(snapshot(2), now=.2).note)
        self.assertIsNotNone(p.process(snapshot(3), now=.5).note)
        self.assertIsNotNone(p.process(snapshot(4), now=20).note)
        self.assertIsNone(p.process(snapshot(5), now=20.01).note)
        p.configure(replace(p.config, revision=2, rate_hz=.25))
        self.assertIsNone(p.process(snapshot(6), now=21).note)
        self.assertIsNotNone(p.process(snapshot(7), now=24).note)
        self.assertFalse(p.configure(p.config))
        with self.assertRaises(ValueError):
            p.process(snapshot(8), now=23)

    def test_pitch_body_and_duration_controls_preserve_source(self):
        raw = snapshot()
        p = TransitionProjector(TransitionControls(axis=0))
        a = p.process(raw, now=0)
        p.configure(replace(p.config, revision=1, base_hz=440, duration=.7))
        b = p.process(snapshot(1), now=1)
        self.assertAlmostEqual(b.note.target_frequency_hz/a.note.target_frequency_hz, 2)
        self.assertEqual(b.note.duration_seconds, .7)
        np.testing.assert_array_equal(a.body.amplitude_gains, b.body.amplitude_gains)
        np.testing.assert_array_equal(raw.rho, np.eye(16)/16)
        np.testing.assert_array_equal(raw.H, np.diag(np.arange(16)))
        p.configure(replace(p.config, revision=2, excitation=0))
        self.assertEqual(p.process(snapshot(2), now=2).note.duration_seconds, .001)

    def test_complete_packet_validation_and_matrix_orientation(self):
        packet = TransitionProjector(TransitionControls(axis=0)).process(snapshot(), now=0)
        args = packet.arguments()
        self.assertEqual(len(args), ARGUMENT_COUNT+HARMONY_COUNT)
        self.assertTrue(validate_arguments(args))
        matrix = np.asarray(args[88:MATRIX_END]).reshape(16, 16, 6)
        np.testing.assert_allclose(matrix[:, :, 0]+1j*matrix[:, :, 1], packet.frame.A_E)
        np.testing.assert_allclose(matrix[:, :, 2]+1j*matrix[:, :, 3], packet.frame.rho_E)
        np.testing.assert_allclose(matrix[:, :, 4], packet.frame.delta_E)
        np.testing.assert_allclose(matrix[:, :, 5], packet.frame.diagnostic_activity)
        for index, value in [(0, 4), (13, -1), (16, 0), (23, 0), (24, 0), (25, 2), (88, np.nan), (93, -1)]:
            bad = list(args)
            bad[index] = value
            with self.subTest(index=index), self.assertRaises(ValueError):
                validate_arguments(bad)
        with self.assertRaises(ValueError):
            validate_arguments(args[:-1])
        empty = TransitionProjector().process(snapshot(), now=0)
        self.assertTrue(validate_arguments(empty.arguments()))

    def test_follow_publishes_candidates_without_a_second_event_clock(self):
        p = TransitionProjector(TransitionControls(axis=0, timing=1, selection=1))
        a = p.process(snapshot(), now=0)
        b = p.process(snapshot(1), now=10)
        self.assertIsNone(a.note)
        self.assertIsNone(b.note)
        self.assertEqual(len(a.candidates), 16)
        self.assertEqual([(n.source_state,n.target_state) for n in a.candidates],
                         [(n.source_state,n.target_state) for n in b.candidates])
        self.assertEqual(len(a.arguments()), ARGUMENT_COUNT+HARMONY_COUNT+5*16)
        self.assertTrue(validate_arguments(a.arguments()))
        self.assertEqual(a.audit()["timing_source"], "rendered_qmw_event")
        self.assertEqual(a.source_digest, b.source_digest)

    def test_follow_candidates_obey_operator_selection_and_filters(self):
        raw = snapshot()
        def frame(**settings):
            return TransitionProjector(TransitionControls(timing=1, **settings)).process(raw, now=0)
        self.assertEqual(frame(axis=2).candidates, ())
        self.assertEqual(frame(axis=0, activity_threshold=1).candidates, ())
        strongest = frame(axis=0)
        self.assertEqual(len(strongest.candidates), 1)
        selected = frame(axis=0, selection=2, source=6, target=7)
        self.assertEqual((selected.candidates[0].source_state, selected.candidates[0].target_state), (6,7))
        p = TransitionProjector(TransitionControls(axis=0, timing=1))
        p.process(raw, now=0)
        p.configure(replace(p.config, revision=1, timing=0))
        pulse = p.process(snapshot(1), now=1)
        self.assertIsNotNone(pulse.note)
        self.assertEqual(pulse.candidates, ())

    def test_follow_wire_rejects_incomplete_invalid_or_mixed_onsets(self):
        packet = TransitionProjector(TransitionControls(axis=0,timing=1)).process(snapshot(),now=0)
        args = packet.arguments()
        self.assertTrue(validate_arguments(args))
        for i,value in [(MATRIX_END,2),(MATRIX_END+1,240),(ARGUMENT_COUNT,16),
                        (ARGUMENT_COUNT+3,.2),(10,0)]:
            bad=args.copy();bad[i]=value
            with self.subTest(i=i), self.assertRaises(ValueError):
                validate_arguments(bad)
        with self.assertRaises(ValueError):
            validate_arguments(args[:-1])
        from pythonosc.osc_message_builder import OscMessageBuilder
        from pythonosc.osc_message import OscMessage
        wire=OscMessageBuilder(address=FRAME_ADDRESS)
        for value in args: wire.add_arg(value)
        self.assertTrue(validate_arguments(OscMessage(wire.build().dgram).params))

    def test_dense_follow_frame_crosses_real_udp_socket_atomically(self):
        import socket
        from unittest.mock import patch
        from pythonosc.udp_client import SimpleUDPClient
        from pythonosc.osc_message import OscMessage
        from qmw.acoustics.transition_runtime_hook import RuntimeAdapter
        rng = np.random.default_rng(174)
        v, _ = np.linalg.qr(rng.normal(size=(16,16)) + 1j*rng.normal(size=(16,16)))
        raw = SourceSnapshot.capture(rho=np.eye(16)/16, H=(v*np.arange(16))@v.conj().T,
            source_revision=1, source_time=.02, dt=.02, session_id="dense", source_id="test")
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as receiver:
            receiver.bind(("127.0.0.1",0)); receiver.settimeout(2)
            with patch("pythonosc.udp_client.SimpleUDPClient",
                       side_effect=lambda host,port: SimpleUDPClient(host,receiver.getsockname()[1])):
                adapter=RuntimeAdapter(start=False)
            try:
                adapter.worker.projector.configure(TransitionControls(revision=1,axis=0,timing=1,selection=1,
                    amplitude_threshold=0,activity_threshold=0))
                adapter.worker.submit_snapshot(raw)
                self.assertTrue(adapter.worker.pump_once(now=0))
                wire,_=receiver.recvfrom(65536)
                self.assertGreater(len(wire),9216)
                decoded=OscMessage(wire)
                self.assertEqual(decoded.params[MATRIX_END+1],240)
                self.assertTrue(validate_arguments(decoded.params))
            finally:
                adapter.close()

    def test_actual_osc_encoding_preserves_the_atomic_frame(self):
        from pythonosc.osc_message_builder import OscMessageBuilder
        from pythonosc.osc_message import OscMessage
        packet = TransitionProjector(TransitionControls(axis=0)).process(snapshot(), now=0)
        builder = OscMessageBuilder(address=FRAME_ADDRESS)
        for arg in packet.arguments():
            builder.add_arg(arg)
        encoded = builder.build()
        self.assertLess(len(encoded.dgram), 16000)
        self.assertTrue(validate_arguments(OscMessage(encoded.dgram).params))

    def test_latest_only_worker_rejects_replay_and_saves_exact_audit(self):
        sent = []
        worker = TransitionWorker(sender=sent.append, config=TransitionControls(axis=0))
        self.assertTrue(worker.submit_snapshot(snapshot()))
        self.assertTrue(worker.submit_snapshot(snapshot(1)))
        self.assertFalse(worker.submit_snapshot(snapshot(1)))
        self.assertTrue(worker.pump_once(now=0))
        self.assertEqual(sent[0].observed_revision, 1)
        self.assertEqual(worker.slot.overwritten, 1)
        audit = sent[0].audit(full=True)
        self.assertEqual(audit["source_H_rho_sha256"], sent[0].source_digest)
        np.testing.assert_array_equal(audit["matrices"]["A"]["real"], sent[0].snapshot.A.real)
        self.assertEqual(len(audit["arguments"]), ARGUMENT_COUNT+HARMONY_COUNT)
        self.assertFalse(worker.pump_once(now=.1))
        worker.close()


if __name__ == "__main__":
    unittest.main()
