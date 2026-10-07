"""Contracts for opt-in live adaptation, written before implementation."""
from dataclasses import replace
from pathlib import Path
import unittest
import numpy as np

from qmw.acoustics.note_timbre_live import (
    SourceSnapshot, LiveConfig, LatestSnapshotSlot, LiveProjector,
    PacketReceiver, LiveWorker, make_geometry, stereo_output, FRAME_ADDRESS,
)


def snapshot(revision=0, rho=None, session="session-a"):
    if rho is None:
        rho = np.diag([1.]+[0.]*15)
    return SourceSnapshot.capture(rho=rho,H=np.diag(np.arange(16)),
        source_revision=revision,source_time=revision*.02,dt=.02,
        session_id=session,source_id="native-fixture",operator_label="IIIX")


class SnapshotTests(unittest.TestCase):
    def test_copies_paired_arrays_and_declares_operator(self):
        rho=np.eye(16)/16; h=np.diag(np.arange(16))
        s=SourceSnapshot.capture(rho=rho,H=h,source_revision=8,source_time=.16,
            dt=.02,session_id="s",source_id="native",operator_label="IIIZ")
        rho[0,0]=5;h[0,0]=7
        self.assertEqual(s.rho[0,0],1/16)
        self.assertEqual(s.H[0,0],0)
        np.testing.assert_array_equal(np.diag(s.A),[1,-1]*8)
        self.assertEqual(s.context.frame_id,8)
        self.assertFalse(s.rho.flags.writeable)
        self.assertEqual(s.operator_revision,0)

    def test_incomplete_or_nonfinite_snapshot_rejected(self):
        for kw in [dict(rho=np.eye(2)),dict(H=np.ones((16,15))),dict(H=np.full((16,16),np.nan)),
                   dict(source_revision=-1),dict(source_time=np.inf),dict(operator_label="bogus")]:
            args=dict(rho=np.eye(16)/16,H=np.eye(16),source_revision=0,source_time=0.,dt=.02,
                      session_id="s",source_id="native",operator_label="IIIZ")
            with self.subTest(kw=kw),self.assertRaises(ValueError):
                SourceSnapshot.capture(**(args|kw))

    def test_latest_slot_bounded_and_ordered(self):
        slot=LatestSnapshotSlot()
        for rev in range(100):self.assertTrue(slot.submit(snapshot(rev)))
        self.assertEqual(slot.pending_count,1)
        self.assertEqual(slot.overwritten,99)
        self.assertFalse(slot.submit(snapshot(98)))
        self.assertEqual(slot.take().context.frame_id,99)
        self.assertIsNone(slot.take())
        self.assertFalse(slot.submit(snapshot(100,session="old-session")))


class ProjectionTests(unittest.TestCase):
    def test_actual_projectors_and_deterministic_max_one_event(self):
        s=snapshot();p=LiveProjector()
        a=p.process(s,now=10.)
        self.assertIsNotNone(a.note)
        self.assertEqual(a.note.source_state,0)
        self.assertEqual(a.note.target_state,1)
        self.assertEqual(a.note.strength,1.)
        self.assertEqual(a.body.context,a.note.context)
        self.assertEqual(a.operator_label,"IIIX")
        self.assertEqual(a.body.modal_probability_weights[0],1.)
        b=LiveProjector().process(s,now=10.)
        self.assertEqual(a.arguments(),b.arguments())

    def test_event_cap_has_no_catchup_burst(self):
        p=LiveProjector()
        emitted=[]
        for rev in range(100):
            a=p.process(snapshot(rev),now=rev*.01)
            if a.note is not None:emitted.append(rev)
        self.assertEqual(emitted,[0,50])
        self.assertIsNotNone(p.process(snapshot(100),now=100.).note)
        self.assertIsNone(p.process(snapshot(101),now=100.).note)

    def test_body_and_tuning_separation(self):
        s=snapshot()
        a=LiveProjector(LiveConfig(basis="identity")).process(s,now=0)
        b=LiveProjector(LiveConfig(basis="fourier")).process(s,now=0)
        self.assertEqual(a.note,b.note)
        np.testing.assert_array_equal(a.body.frequencies_hz,b.body.frequencies_hz)
        self.assertFalse(np.allclose(a.body.amplitude_gains,b.body.amplitude_gains))
        c=LiveProjector(LiveConfig(octave=1)).process(s,now=0)
        self.assertEqual(c.note.target_frequency_hz,a.note.target_frequency_hz*2)
        np.testing.assert_array_equal(a.body.amplitude_gains,c.body.amplitude_gains)
        np.testing.assert_array_equal(a.body.frequencies_hz,c.body.frequencies_hz)

    def test_hold_observer_does_not_freeze_authority(self):
        p=LiveProjector(LiveConfig(hold=True));first=snapshot()
        a=p.process(first,now=0)
        changed=snapshot(1,rho=np.eye(16)/16)
        b=p.process(changed,now=1)
        self.assertTrue(b.held)
        self.assertEqual(b.source_revision,0)
        self.assertEqual(b.observed_revision,1)
        np.testing.assert_array_equal(a.body.amplitude_gains,b.body.amplitude_gains)
        np.testing.assert_array_equal(changed.rho,np.eye(16)/16)
        p.configure(LiveConfig(revision=1,hold=False))
        c=p.process(snapshot(2,rho=np.eye(16)/16),now=2)
        self.assertFalse(c.held)
        self.assertEqual(c.source_revision,2)

    def test_controls_atomic_and_monotone(self):
        p=LiveProjector()
        self.assertTrue(p.configure(LiveConfig(revision=1,basis="fourier",excitation="pitched",octave=1)))
        self.assertFalse(p.configure(LiveConfig(revision=0)))
        a=p.process(snapshot(),now=0)
        self.assertEqual(a.config.revision,1)
        self.assertEqual(a.note.duration_seconds,.25)
        for kw in [dict(octave=4),dict(basis="physical_mesh"),dict(excitation="rho_phase"),dict(revision=-1)]:
            with self.assertRaises(ValueError):LiveConfig(**kw)

    def test_activity_not_physical_rate_and_no_diagnostic_audio_mapping(self):
        a=LiveProjector().process(snapshot(rho=np.eye(16)/16),now=0)
        self.assertIn("diagnostic",a.note.activity_name+str(a.provenance))
        np.testing.assert_allclose(a.body.amplitude_gains,.25)
        np.testing.assert_array_equal(a.body.frequencies_hz,make_geometry("identity").frequencies_hz)

    def test_invalid_density_fails_without_send_or_substitution(self):
        sent=[];worker=LiveWorker(sender=sent.append)
        worker.submit_snapshot(snapshot(rho=np.eye(16)))
        self.assertFalse(worker.pump_once(now=0))
        self.assertEqual(sent,[])
        self.assertIn("trace",worker.last_error)
        worker.submit_snapshot(snapshot(1))
        self.assertTrue(worker.pump_once(now=1))
        self.assertEqual(len(sent),1)


class AtomicPacketTests(unittest.TestCase):
    def setUp(self):
        self.packet=LiveProjector().process(snapshot(),now=0)

    def test_one_complete_message_payload(self):
        args=self.packet.arguments()
        self.assertEqual(len(args),self.packet.argument_count)
        self.assertEqual(FRAME_ADDRESS,"/qmw/note_timbre/v1/frame")
        received=PacketReceiver().accept(args)
        self.assertEqual(received["source_revision"],0)
        self.assertEqual(len(received["frequencies_hz"]),16)
        np.testing.assert_array_equal(received["gains"],self.packet.body.amplitude_gains)

    def test_incomplete_nonfinite_or_invalid_packet_never_commits(self):
        args=self.packet.arguments()
        for bad in [args[:-1],args+[0],args[:5]+[np.nan]+args[6:]]:
            r=PacketReceiver()
            self.assertIsNone(r.accept(bad))
            self.assertIsNone(r.latest)

    def test_replay_order_restart_and_retired_sessions(self):
        receiver=PacketReceiver()
        a=self.packet.arguments()
        self.assertIsNotNone(receiver.accept(a))
        self.assertIsNone(receiver.accept(a))
        fresh=LiveProjector().process(snapshot(session="session-b"),now=0).arguments()
        self.assertIsNone(receiver.accept(fresh))  # explicit reconnect required
        receiver.reconnect()
        self.assertIsNotNone(receiver.accept(fresh))
        self.assertIsNone(receiver.accept(a))  # old session remains retired

    def test_config_revision_cannot_move_backward(self):
        p=LiveProjector(LiveConfig(revision=2));a=p.process(snapshot(),now=0)
        r=PacketReceiver();self.assertIsNotNone(r.accept(a.arguments()))
        bad=replace(p.process(snapshot(1),now=1),config=LiveConfig(revision=1))
        self.assertIsNone(r.accept(bad.arguments()))


class MixerAndSCTests(unittest.TestCase):
    def test_simple_lane_and_mute_own_all_existing_tails(self):
        old=np.ones((16,2));tails=np.ones((16,2))*.5
        for kw in [dict(armed=False),dict(sound_on=False),dict(plucks_on=False),
                   dict(master=0),dict(mix=0),dict(event_gain=0),dict(effective_voice_gains=(0,1,1,1,1,1,1,1))]:
            with self.subTest(kw=kw):
                out=stereo_output(old,tails,solo=True,**kw)
                np.testing.assert_array_equal(out,np.zeros_like(old))
        np.testing.assert_array_equal(stereo_output(old,tails,solo=True,effective_voice_gains=(0,)*8),old*0)

    def test_solo_is_exactly_restorable_without_touching_old_audio(self):
        old=np.arange(32).reshape(16,2)/32;original=old.copy();new=np.ones_like(old)*.1
        normal=stereo_output(old,new,solo=False)
        isolated=stereo_output(old,new,solo=True)
        np.testing.assert_allclose(normal-isolated,old)
        np.testing.assert_array_equal(old,original)
        np.testing.assert_array_equal(stereo_output(old,new,solo=False),normal)

    def test_synth_and_receiver_source_contract(self):
        root=Path(__file__).resolve().parents[1]
        sc=(root/'supercollider/qmw_note_timbre_live_v1.scd').read_text()
        for token in ["ReplaceOut.ar", "In.kr(voiceGainBus, 8)[0]", "~qrmSonify", "~qriPlucksEnabled",
                      "~qriMix", "~qrmMaster", "~qntArmed = false", "17930", "Ringz.ar",
                      "6.907755", "~qntReconnect", "~qntSolo", "~qntHold", "HOLD SNAPSHOT"]:
            self.assertIn(token,sc)
        self.assertIn("a[i].isKindOf(Symbol)",sc)
        self.assertIn("a[i] = a[i].asString",sc)
        self.assertIn("~qntRejectReason",sc)
        self.assertIn("originalAction !? { |action| action.value(view) }",sc)
        self.assertIn("~qntOpenPanel",sc)
        self.assertIn("Rect(18,336,204,34)",sc)
        self.assertNotIn('sendMsg("/qmw/4_4/dynamics/control',sc)


if __name__=='__main__':unittest.main()
