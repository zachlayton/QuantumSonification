"""Explicit external callback loaded only by QMW_NOTE_TIMBRE_HOOK.

Runtime qmw packages remain first. Extend only the two missing observer module
search paths to this checkout; no portable bundle, state engine or default bus
replacement. No thread/socket is opened by importing this module.
"""
from pathlib import Path
import hashlib
import json
import os
from threading import Thread
import uuid

import qmw.core
import qmw.acoustics

SOURCE_ROOT=Path(__file__).resolve().parents[1]
for package,subpath in [(qmw.core,"core"),(qmw.acoustics,"acoustics")]:
    fallback=str(SOURCE_ROOT/subpath)
    if fallback not in package.__path__:package.__path__.append(fallback)

from qmw.acoustics.note_timbre_live import (
    LiveWorker,LiveConfig,SourceSnapshot,FRAME_ADDRESS,FRAME_PORT,CONTROL_ADDRESS,CONTROL_PORT,
)


class RuntimeAdapter:
    def __init__(self,*,sender=None,start=True,session_id=None,log_path=None):
        self.session_id=session_id or uuid.uuid4().hex
        self.source_id="runtime.ClosedFourQubitSource"
        self.last_error=None;self._server=None;self._server_thread=None;self._client=None
        self._log=None
        if log_path:
            path=Path(log_path);path.parent.mkdir(parents=True,exist_ok=True)
            self._log=path.open("a",encoding="utf-8")
        if sender is None:
            from pythonosc.udp_client import SimpleUDPClient
            self._client=SimpleUDPClient("127.0.0.1",FRAME_PORT)
            def send(packet):
                args=packet.arguments()
                # One complete datagram; no begin/chunk partial-state synthesis.
                self._client.send_message(FRAME_ADDRESS,args)
                if self._log:
                    src=packet.snapshot
                    entry={"schema":"qmw.note_timbre.live.audit.v1","arguments":args,
                        "provenance":packet.provenance,"source_H_sha256":hashlib.sha256(src.H.tobytes()).hexdigest(),
                        "source_rho_sha256":hashlib.sha256(src.rho.tobytes()).hexdigest(),
                        "skipped_pending_snapshots":self.worker.slot.overwritten}
                    if packet.note is not None:
                        entry["source_matrices"]={key:{"real":matrix.real.tolist(),"imag":matrix.imag.tolist()}
                            for key,matrix in [("H",src.H),("A",src.A),("rho",src.rho)]}
                    self._log.write(json.dumps(entry,allow_nan=False)+"\n");self._log.flush()
            sender=send
        self.worker=LiveWorker(sender=sender,error_handler=self._error)
        if start:
            from pythonosc.dispatcher import Dispatcher
            from pythonosc.osc_server import ThreadingOSCUDPServer
            dispatcher=Dispatcher();dispatcher.map(CONTROL_ADDRESS,self._control)
            try:
                self._server=ThreadingOSCUDPServer(("127.0.0.1",CONTROL_PORT),dispatcher)
                self._server.daemon_threads=True
                self._server_thread=Thread(target=self._server.serve_forever,name="qmw-note-timbre-config",daemon=True)
                self._server_thread.start();self.worker.start()
            except Exception:
                self.close();raise
            print(f"QMW_NOTE_TIMBRE_READY session={self.session_id} source={self.source_id} "
                  f"frame_udp={FRAME_PORT} config_udp={CONTROL_PORT} output=disarmed_SC",flush=True)

    def _error(self,error):
        self.last_error=str(error)
        print(self.last_error,flush=True)
        if self._log:self._log.write(json.dumps({"error":self.last_error})+"\n");self._log.flush()

    def _control(self,address,*args):
        try:
            if len(args)!=5 or any(type(v) is not int for v in args):
                raise ValueError("config requires five atomic integers: revision,basis,excitation,octave,hold")
            rev,basis,excitation,octave,hold=args
            if basis not in (0,1) or excitation not in (0,1) or hold not in (0,1):
                raise ValueError("config switches must be 0 or 1")
            config=LiveConfig(rev,("identity","fourier")[basis],("strike","pitched")[excitation],octave,bool(hold))
            if not self.worker.projector.configure(config):raise ValueError("stale config revision")
        except Exception as error:self._error(f"QMW_NOTE_TIMBRE_CONFIG_REJECTED: {error}")

    def submit(self,*,rho,H,source_revision,source_time,dt):
        # Called on the source thread before any handoff. Read-only owning copies
        # freeze H/rho and the fixed A under this exact source revision/time.
        try:
            snapshot=SourceSnapshot.capture(rho=rho,H=H,source_revision=source_revision,
                source_time=source_time,dt=dt,session_id=self.session_id,source_id=self.source_id,operator_label="IIIZ")
            accepted=self.worker.submit_snapshot(snapshot)
            if not accepted:self._error("QMW_NOTE_TIMBRE_SOURCE_REJECTED: duplicate/backward/mismatched source snapshot")
            return accepted
        except Exception as error:
            self._error(f"QMW_NOTE_TIMBRE_SOURCE_REJECTED: {type(error).__name__}: {error}")
            return False

    def close(self):
        if hasattr(self,"worker"):self.worker.close()
        if self._server_thread:
            self._server.shutdown();self._server_thread.join(timeout=2.)
        if self._server:self._server.server_close()
        if self._client:self._client._sock.close()
        if self._log:self._log.close();self._log=None


def open_adapter():
    return RuntimeAdapter(log_path=os.environ.get("QMW_NOTE_TIMBRE_LOG"))
