"""Opt-in runtime hook using the existing paired-snapshot coordinator callback."""
from pathlib import Path
import json
import os
import socket
from threading import Thread
import uuid

import qmw.core
import qmw.acoustics

SOURCE_ROOT = Path(__file__).resolve().parents[1]
for package, subpath in [(qmw.core, "core"), (qmw.acoustics, "acoustics")]:
    fallback = str(SOURCE_ROOT/subpath)
    if fallback not in package.__path__:
        package.__path__.append(fallback)

from qmw.acoustics.note_timbre_live import SourceSnapshot
from qmw.acoustics.transition_live import (
    TransitionWorker, TransitionControls, FRAME_ADDRESS, FRAME_PORT, CONTROL_ADDRESS, CONTROL_PORT,
)


class RuntimeAdapter:
    def __init__(self, *, sender=None, start=True, session_id=None, output_directory=None):
        self.session_id = session_id or uuid.uuid4().hex
        self.last_error = None
        self._server = self._server_thread = self._client = self._log = None
        self.latest = None
        self._saved = 0
        self.output = Path(output_directory) if output_directory else None
        if self.output:
            self.output.mkdir(parents=True, exist_ok=True)
            self._log = (self.output/("transitions-"+self.session_id+".jsonl")).open("a", encoding="utf-8")
        if sender is None:
            from pythonosc.udp_client import SimpleUDPClient
            self._client = SimpleUDPClient("127.0.0.1", FRAME_PORT)
            # Full 16-state cycle frames exceed Darwin's 9216-byte default.
            # Size this owned socket only; no global network configuration.
            self._client._sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 65536)
            sender = lambda packet: self._client.send_message(FRAME_ADDRESS, packet.arguments())
        def send(packet):
            self.latest = packet
            sender(packet)
            if self._log:
                self._log.write(json.dumps(packet.audit(), allow_nan=False)+"\n")
                self._log.flush()
        self.worker = TransitionWorker(sender=send, error_handler=self._error)
        if start:
            from pythonosc.dispatcher import Dispatcher
            from pythonosc.osc_server import ThreadingOSCUDPServer
            dispatcher = Dispatcher()
            dispatcher.map(CONTROL_ADDRESS, self._control)
            dispatcher.map("/qmw/transitions/v1/save", self._save)
            try:
                self._server = ThreadingOSCUDPServer(("127.0.0.1", CONTROL_PORT), dispatcher)
                self._server.daemon_threads = True
                self._server_thread = Thread(target=self._server.serve_forever, daemon=True)
                self._server_thread.start()
                self.worker.start()
            except Exception:
                self.close()
                raise
            print(f"QMW_TRANSITIONS_READY session={self.session_id} frame={FRAME_PORT} controls={CONTROL_PORT}", flush=True)

    def _error(self, error):
        self.last_error = str(error)
        print("QMW_TRANSITIONS_ERROR: "+self.last_error, flush=True)

    def _control(self, address, *args):
        try:
            controls = TransitionControls.from_arguments(args)
            if not self.worker.projector.configure(controls):
                raise ValueError("stale configuration revision")
        except Exception as error:
            self._error(error)

    def _save(self, address, *args):
        try:
            packet = self.latest
            if args or packet is None or self.output is None:
                raise ValueError("save requires a current frame and configured output directory")
            # The complete packet is immutable; save it without holding source locks.
            destination = self.output/(f"snapshot-{packet.snapshot.session_id}-{packet.sequence}.json")
            destination.write_text(json.dumps(packet.audit(full=True), indent=2, allow_nan=False)+"\n")
            if self._client:
                self._client.send_message("/qmw/transitions/v1/saved", str(destination))
            print(f"QMW_TRANSITIONS_SAVED {destination}", flush=True)
        except Exception as error:
            self._error(error)

    def submit(self, *, rho, H, source_revision, source_time, dt):
        try:
            snapshot = SourceSnapshot.capture(rho=rho, H=H, source_revision=source_revision,
                source_time=source_time, dt=dt, session_id=self.session_id,
                source_id="runtime.ClosedFourQubitSource")
            accepted = self.worker.submit_snapshot(snapshot)
            if not accepted:
                raise ValueError("duplicate/backward/mismatched source snapshot")
            return True
        except Exception as error:
            self._error(error)
            return False

    def close(self):
        if hasattr(self, "worker"):
            self.worker.close()
        if self._server_thread:
            self._server.shutdown()
            self._server_thread.join(timeout=2)
        if self._server:
            self._server.server_close()
        if self._client:
            self._client._sock.close()
        if self._log:
            self._log.close()
            self._log = None


def open_adapter():
    return RuntimeAdapter(output_directory=os.environ.get("QMW_TRANSITION_OUTPUT"))
