"""Real route-to-wire acceptance; physics inputs and v1 semantics remain intact."""
from dataclasses import replace
import json
import unittest
from unittest.mock import patch
import numpy as np
from pythonosc.osc_message_builder import OscMessageBuilder
from pythonosc.osc_message import OscMessage
from qmw.acoustics.note_timbre_live import SourceSnapshot, PacketReceiver as V1Receiver
from qmw.acoustics.note_timbre_routed_live import (
    RoutedLiveConfig, RoutedLiveProjector, RoutedPacketReceiver, RoutedLiveWorker,
    FRAME_ADDRESS,
)


def snapshot(revision=0):
    v=np.arange(1,17,dtype=float);v/=np.linalg.norm(v)
    h=np.diag(np.arange(16,dtype=float))
    h[0,1]=h[1,0]=.3;h[2,5]=h[5,2]=.2
    return SourceSnapshot.capture(rho=np.outer(v,v),H=h,source_revision=revision,
        source_time=revision*.02,dt=.02,session_id='source-a',source_id='runtime.ClosedFourQubitSource')


class RoutedLiveTests(unittest.TestCase):
    def test_all_source_choices_roundtrip_real_osc(self):
        for amplitude in range(3):
            for rhythm in range(2):
                for quantization in range(2):
                    cfg=RoutedLiveConfig(amplitude_source=amplitude,rhythm_source=rhythm,quantization=quantization)
                    packet=RoutedLiveProjector(cfg).process(snapshot(),now=0.)
                    args=packet.arguments()
                    self.assertEqual(len(args),108)
                    self.assertEqual(args[0],2)
                    self.assertIsNotNone(packet.note)
                    self.assertGreater(args[21],0.)
                    self.assertTrue(0<=args[100]<=1)
                    self.assertTrue(.5<=args[101]<=8.)
                    self.assertEqual(args[102:105],[amplitude,rhythm,quantization])
                    self.assertIsNone(V1Receiver().accept(args))
                    builder=OscMessageBuilder(address=FRAME_ADDRESS)
                    for arg in args:builder.add_arg(arg)
                    wire=builder.build();self.assertLess(len(wire.dgram),4096)
                    decoded=OscMessage(wire.dgram)
                    self.assertIsNotNone(RoutedPacketReceiver().accept(decoded.params))
                    json.dumps(packet.audit_entry(),allow_nan=False)

    def test_analysis_view_does_not_change_source_or_sound(self):
        source=snapshot();h=source.H.copy();rho=source.rho.copy();packets=[]
        for basis in range(4):
            packets.append(RoutedLiveProjector(RoutedLiveConfig(analysis_basis=basis)).process(source,now=0.))
        for packet in packets:
            np.testing.assert_array_equal(packet.snapshot.H,h)
            np.testing.assert_array_equal(packet.snapshot.rho,rho)
            self.assertEqual(packet.note.target_frequency_hz,packets[0].note.target_frequency_hz)
            np.testing.assert_array_equal(packet.body.amplitude_gains,packets[0].body.amplitude_gains)

    def test_idempotent_config_and_no_catchup(self):
        projector=RoutedLiveProjector()
        cfg=RoutedLiveConfig(revision=1,hold=True)
        self.assertTrue(projector.configure(cfg))
        self.assertTrue(projector.configure(cfg))
        self.assertFalse(projector.configure(replace(cfg,octave=1)))
        first=projector.process(snapshot(),now=0.)
        self.assertIsNotNone(first.note)
        self.assertIsNone(projector.process(snapshot(1),now=.1).note)
        second=projector.process(snapshot(2),now=100.)
        self.assertIsNotNone(second.note)
        self.assertEqual(second.source_revision,0)
        self.assertEqual(second.observed_revision,2)
        self.assertIsNone(projector.process(snapshot(3),now=100.01).note)

    def test_rejection_is_atomic_and_config_digest_is_bound(self):
        args=RoutedLiveProjector().process(snapshot(),now=0.).arguments()
        for index,value in [(0,1),(100,-1),(100,float('nan')),(101,.1),(102,4),(103,2),(104,2),(105,4),(106,1),(107,'0'*64)]:
            receiver=RoutedPacketReceiver();bad=args.copy();bad[index]=value
            self.assertIsNone(receiver.accept(bad))
            self.assertEqual(receiver.sequence,-1)
            self.assertIsNotNone(receiver.accept(args))
            self.assertIsNone(receiver.accept(args))

    def test_published_deadline_survives_changing_candidate_interval(self):
        from qmw.acoustics import note_timbre_routed_live as live
        original=live.route_live_event
        count=0
        def changing_interval(**kwargs):
            nonlocal count
            result=original(**kwargs);count+=1
            return replace(result,scheduled_interval_seconds=8. if count==1 else .5)
        projector=RoutedLiveProjector()
        with patch.object(live,'route_live_event',side_effect=changing_interval):
            self.assertIsNotNone(projector.process(snapshot(),now=0.).note)
            self.assertIsNone(projector.process(snapshot(1),now=1.).note)
            self.assertIsNone(projector.process(snapshot(2),now=7.9).note)
            self.assertIsNotNone(projector.process(snapshot(3),now=8.).note)

    def test_analysis_only_configuration_preserves_pending_deadline(self):
        from qmw.acoustics import note_timbre_routed_live as live
        original=live.route_live_event
        def eight_seconds(**kwargs):return replace(original(**kwargs),scheduled_interval_seconds=8.)
        projector=RoutedLiveProjector()
        with patch.object(live,'route_live_event',side_effect=eight_seconds):
            self.assertIsNotNone(projector.process(snapshot(),now=0.).note)
            self.assertTrue(projector.configure(RoutedLiveConfig(revision=1,analysis_basis=3)))
            self.assertIsNone(projector.process(snapshot(1),now=1.).note)
            self.assertIsNotNone(projector.process(snapshot(2),now=8.).note)

    def test_no_transition_still_analyzes_selected_basis(self):
        for basis in range(4):
            source=SourceSnapshot.capture(rho=np.eye(16)/16,H=np.diag(np.arange(16)),source_revision=0,
                source_time=0.,dt=.02,session_id='silent',source_id='runtime.ClosedFourQubitSource')
            packet=RoutedLiveProjector(RoutedLiveConfig(analysis_basis=basis)).process(source,now=0.)
            self.assertIsNone(packet.note)
            self.assertIsNotNone(packet.routing_audit)
            self.assertEqual(packet.arguments()[100:102],[0.,0.])
            self.assertIsNotNone(RoutedPacketReceiver().accept(packet.arguments()))

    def test_worker_keeps_latest_frame_and_retired_session_rejected(self):
        sent=[];worker=RoutedLiveWorker(sender=sent.append)
        self.assertTrue(worker.submit_snapshot(snapshot(0)))
        self.assertTrue(worker.submit_snapshot(snapshot(1)))
        self.assertTrue(worker.pump_once(now=0.))
        self.assertEqual(sent[0].observed_revision,1)
        self.assertEqual(worker.slot.overwritten,1)
        receiver=RoutedPacketReceiver();self.assertIsNotNone(receiver.accept(sent[0].arguments()))
        receiver.reconnect();self.assertIsNone(receiver.accept(sent[0].arguments()))


if __name__=='__main__':unittest.main()
