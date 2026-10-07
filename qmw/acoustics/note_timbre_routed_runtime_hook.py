"""Opt-in v2 observer callback; the existing native runtime remains authoritative."""
from pathlib import Path
import json
import os
import sys
from threading import Thread
import uuid

import qmw
import qmw.core
import qmw.acoustics

SOURCE_ROOT=Path(__file__).resolve().parents[1]
# Only extend missing observer locations. Runtime packages stay first, including
# their state bus/authority. Never prepend a second runtime or replace modules.
for package,folder in [(qmw,SOURCE_ROOT),(qmw.core,SOURCE_ROOT/'core'),(qmw.acoustics,SOURCE_ROOT/'acoustics')]:
    if str(folder) not in package.__path__:package.__path__.append(str(folder))
for folder in (SOURCE_ROOT.parent,SOURCE_ROOT):
    if str(folder) not in sys.path:sys.path.append(str(folder))

from qmw.acoustics.note_timbre_runtime_hook import RuntimeAdapter as ExistingRuntimeAdapter
from qmw.acoustics.note_timbre_routed_live import (
    RoutedLiveWorker,RoutedLiveConfig,FRAME_ADDRESS,FRAME_PORT,CONTROL_ADDRESS,CONTROL_PORT,
)


class RoutedRuntimeAdapter(ExistingRuntimeAdapter):
    """Reuse snapshot capture, failure isolation and shutdown from the v1 hook."""
    def __init__(self,*,sender=None,start=True,session_id=None,log_path=None):
        self.session_id=session_id or uuid.uuid4().hex
        self.source_id='runtime.ClosedFourQubitSource'
        self.last_error=None;self._server=None;self._server_thread=None;self._client=None;self._log=None
        if log_path:
            path=Path(log_path);path.parent.mkdir(parents=True,exist_ok=True)
            self._log=path.open('a',encoding='utf-8')
        if sender is None:
            from pythonosc.udp_client import SimpleUDPClient
            self._client=SimpleUDPClient('127.0.0.1',FRAME_PORT)
            def send(packet):
                args=packet.arguments()
                self._client.send_message(FRAME_ADDRESS,args)
                if self._log:
                    entry={'schema':'qmw.note_timbre.record.v2','arguments':args,
                        'audit':packet.audit_entry(),'audit_digest':args[16],
                        'skipped_pending_snapshots':self.worker.slot.overwritten}
                    if packet.note is not None:
                        entry['source_matrices']={name:{'real':value.real.tolist(),'imag':value.imag.tolist()}
                            for name,value in [('H',packet.snapshot.H),('A',packet.snapshot.A),('rho',packet.snapshot.rho)]}
                    self._log.write(json.dumps(entry,allow_nan=False)+'\n');self._log.flush()
            sender=send
        self.worker=RoutedLiveWorker(sender=sender,error_handler=self._error)
        if start:
            from pythonosc.dispatcher import Dispatcher
            from pythonosc.osc_server import ThreadingOSCUDPServer
            dispatcher=Dispatcher();dispatcher.map(CONTROL_ADDRESS,self._control)
            try:
                self._server=ThreadingOSCUDPServer(('127.0.0.1',CONTROL_PORT),dispatcher)
                self._server.daemon_threads=True
                self._server_thread=Thread(target=self._server.serve_forever,name='qmw-routed-config',daemon=True)
                self._server_thread.start();self.worker.start()
            except Exception:
                self.close();raise
            print(f'QMW_ROUTED_LIVE_READY session={self.session_id} source={self.source_id} '
                  f'frame_udp={FRAME_PORT} config_udp={CONTROL_PORT} mode=ANALYSIS output=disarmed_SC',flush=True)

    def _control(self,address,*args):
        try:
            config=RoutedLiveConfig.from_control(args)
            if not self.worker.projector.configure(config):raise ValueError('stale or conflicting configuration revision')
        except Exception as error:self._error(f'QMW_ROUTED_CONFIG_REJECTED: {error}')


def open_adapter():
    return RoutedRuntimeAdapter(log_path=os.environ.get('QMW_NOTE_TIMBRE_LOG'))
