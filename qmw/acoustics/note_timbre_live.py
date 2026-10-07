"""Opt-in complete-source adapter. No authority, audio device, or evolution kernel.

The callback copies matching H/rho; a latest-only worker observes them. Wall time
controls musical admission only. Each OSC datagram is one entire note/body frame.
"""
from __future__ import annotations
from dataclasses import dataclass, replace
import hashlib
import json
from threading import Event, Lock, Thread
import time
from typing import Callable
import numpy as np

from qmw.core.transition import FrameContext, QuantumUnits, TransitionEngine, readonly
from qmw.acoustics.note_timbre import (
    GeometryModes, QuantumTimbreProjector, RatioField, TransitionPitchProjector,
    QuantumNoteEvent, ModalResonatorFrame,
)

FRAME_ADDRESS = "/qmw/note_timbre/v1/frame"
CONTROL_ADDRESS = "/qmw/note_timbre/v1/config"
FRAME_PORT, CONTROL_PORT = 17930, 17931
HEADER_COUNT, MODE_COUNT = 36, 16
RATIOS = (1., 9/8, 5/4, 4/3, 3/2)
BASIS_ID = "four_qubit_computational:q0-lsb"


@dataclass(frozen=True)
class SourceSnapshot:
    rho: np.ndarray
    H: np.ndarray
    A: np.ndarray
    context: FrameContext
    session_id: str
    operator_label: str
    operator_revision: int = 0

    @classmethod
    def capture(cls, *, rho, H, source_revision, source_time, dt, session_id,
                source_id, operator_label="IIIZ"):
        if not isinstance(session_id,str) or not session_id:
            raise ValueError("session_id required")
        if len(operator_label)!=4 or any(c not in "IXYZ" for c in operator_label):
            raise ValueError("operator_label must declare one four-qubit Pauli coupling")
        matrices=[]
        for name, raw in [("rho",rho),("H",H)]:
            value=readonly(raw,complex)
            if value.shape!=(16,16) or not np.isfinite(value).all():
                raise ValueError(f"{name} requires a complete finite 16x16 matrix")
            matrices.append(value)
        pauli={"I":np.eye(2),"X":np.array([[0,1],[1,0]]),
               "Y":np.array([[0,-1j],[1j,0]]),"Z":np.diag([1,-1])}
        a=np.ones((1,1))
        for c in operator_label:a=np.kron(a,pauli[c])
        context=FrameContext(source_id,source_revision,source_time,dt,BASIS_ID,
            provenance=("matched native H/rho snapshot",f"session:{session_id}",
                        f"declared diagnostic coupling:{operator_label};revision:0"))
        return cls(*matrices,readonly(a,complex),context,session_id,operator_label)


@dataclass(frozen=True)
class LiveConfig:
    revision: int = 0
    basis: str = "identity"
    excitation: str = "strike"
    octave: int = 0
    hold: bool = False

    def __post_init__(self):
        if type(self.revision) is not int or self.revision<0:
            raise ValueError("configuration revision must be a nonnegative integer")
        if self.basis not in ("identity","fourier") or self.excitation not in ("strike","pitched"):
            raise ValueError("unknown abstract basis or excitation policy")
        if type(self.octave) is not int or self.octave not in (0,1) or type(self.hold) is not bool:
            raise ValueError("octave must be 0/1 and hold boolean")


def make_geometry(basis: str) -> GeometryModes:
    if basis not in ("identity","fourier"):
        raise ValueError("unsupported physical/abstract basis")
    phi=np.eye(16) if basis=="identity" else np.exp(2j*np.pi*np.outer(np.arange(16),np.arange(16))/16)/4
    # Independently fixed supportive poles, never recomputed from a current note.
    f=np.array([220*RATIOS[j%5]*2**(j//5) for j in range(16)])
    return GeometryModes(phi,BASIS_ID,"fixed_abstract_"+basis,
        tuple(f"mode-{j+1}" for j in range(16)), f,np.pi*f*.18,np.zeros(16),
        provenance=("independent fixed abstract Hilbert basis:"+basis,
                    "fixed supportive ratio poles; amplitude tau=.18s; acoustic phase=0; no physical embedding"))


class LatestSnapshotSlot:
    """Single owning session; atomically replace pending work, never queue a burst."""
    def __init__(self):
        self._lock=Lock();self._pending=None;self._session=None
        self._revision=-1;self._time=-np.inf;self.overwritten=0

    @property
    def pending_count(self):
        with self._lock:return int(self._pending is not None)

    def submit(self,snapshot):
        with self._lock:
            if self._session is not None and snapshot.session_id!=self._session:return False
            if snapshot.context.frame_id<=self._revision or snapshot.context.time<self._time:return False
            self._session=snapshot.session_id
            self._revision=snapshot.context.frame_id;self._time=snapshot.context.time
            self.overwritten+=int(self._pending is not None)
            self._pending=snapshot
            return True

    def take(self):
        with self._lock:
            pending=self._pending;self._pending=None
            return pending


@dataclass(frozen=True)
class LivePacket:
    session_id: str
    sequence: int
    source_revision: int
    observed_revision: int
    config: LiveConfig
    held: bool
    operator_label: str
    operator_revision: int
    note: QuantumNoteEvent | None
    body: ModalResonatorFrame
    emitted_at: float
    provenance: tuple[str,...]
    snapshot: SourceSnapshot
    argument_count: int = HEADER_COUNT + 4*MODE_COUNT

    def arguments(self):
        note=self.note;ctx=self.body.context
        digest=hashlib.sha256(json.dumps(self.provenance,separators=(",",":")).encode()).hexdigest()
        result=[1,self.session_id,self.sequence,self.source_revision,self.observed_revision,
            ctx.time,ctx.dt,self.config.revision,int(self.held),int(self.config.excitation=="pitched"),
            self.config.octave,int(self.config.basis=="fourier"),self.operator_label,self.operator_revision,
            ctx.source_id,ctx.basis_id,digest,note.event_id if note else "-",
            note.source_state if note else -1,note.target_state if note else -1,
            note.target_frequency_hz if note else 0.,note.strength if note else 0.,
            note.duration_seconds if note else 0.,note.delta_E if note else 0.,note.omega if note else 0.,
            (note.phase_rad or 0.) if note else 0.,int(note is not None and note.phase_rad is not None),
            self.body.purity,self.body.entropy_nats,self.body.captured_weight,1.,"model_energy",16,
            "dimensionless",self.emitted_at,int(note is not None)]
        for row in zip(self.body.frequencies_hz,self.body.amplitude_gains,self.body.decay_seconds,self.body.acoustic_phases_rad):
            result.extend(float(v) for v in row)
        return result


class LiveProjector:
    def __init__(self,config=None):
        self.config=config or LiveConfig();self._lock=Lock();self._held=None
        self._next_event=-np.inf;self._sequence=0
        self.transitions=TransitionEngine(units=QuantumUnits())
        self.timbres=QuantumTimbreProjector()

    def configure(self,config):
        with self._lock:
            if config.revision<=self.config.revision:return False
            if not config.hold or not self.config.hold:self._held=None
            self.config=config
            return True

    def process(self,snapshot,*,now):
        if not np.isfinite(now):raise ValueError("wall-clock input must be finite")
        with self._lock:
            cfg=self.config
            if cfg.hold and self._held is None:self._held=snapshot
            source=self._held if cfg.hold else snapshot
        transition=self.transitions.process(source.H,source.A,source.rho,source.context)
        duration=.001 if cfg.excitation=="strike" else .25
        notes=TransitionPitchProjector(state_degrees=tuple(j%5+5*cfg.octave for j in range(16)),
            ratio_field=RatioField(RATIOS,reference_hz=220,name="live_explicit_five"),
            min_activity=1e-6,duration_seconds=duration).process(transition)
        note=None
        if notes and now>=self._next_event:
            note=min(notes,key=lambda n:(-n.strength,n.source_state,n.target_state))
            self._next_event=now+.5
        body=self.timbres.process(rho=source.rho,geometry_modes=make_geometry(cfg.basis),context=source.context)
        self._sequence+=1
        provenance=transition.provenance+body.provenance+(
            "live musical admission:activity>1e-6;max_activity_then_source_target;max1event;wall_interval>=.5s;no_catchup",
            f"config_revision:{cfg.revision};excitation:{cfg.excitation};octave:{cfg.octave};held_observer:{cfg.hold}",
            "source model seconds are provenance; playback begins on receipt; no stochastic physical rate")
        return LivePacket(source.session_id,self._sequence,source.context.frame_id,snapshot.context.frame_id,
            cfg,cfg.hold,source.operator_label,source.operator_revision,note,body,float(now),provenance,source)


class PacketReceiver:
    """Python specification mirrored by the SC commit gate, no partial assembly."""
    def __init__(self):
        self.session=None;self.retired=set();self.sequence=-1;self.config_revision=-1
        self.observed_revision=-1;self.source_revision=-1;self.latest=None

    def reconnect(self):
        if self.session is not None:self.retired.add(self.session)
        self.session=None;self.sequence=-1;self.config_revision=-1
        self.observed_revision=-1;self.source_revision=-1;self.latest=None

    def accept(self,args):
        try:
            if len(args)!=HEADER_COUNT+4*MODE_COUNT or args[0]!=1 or args[32]!=16:return None
            string_indices={1,12,14,15,16,17,31,33}
            if any(not isinstance(args[i],str) or not args[i] for i in string_indices):return None
            if any(not isinstance(v,(int,float,np.number)) or not np.isfinite(v)
                   for i,v in enumerate(args) if i not in string_indices):return None
            for i in (2,3,4,7,13):
                if int(args[i])!=args[i] or args[i]<0:return None
            if any(args[i] not in (0,1) for i in (8,9,10,11,26,35)):return None
            if args[6]<0 or args[30]!=1 or args[31]!="model_energy" or args[33]!="dimensionless":return None
            if args[15]!=BASIS_ID or len(args[12])!=4 or any(c not in "IXYZ" for c in args[12]):return None
            if len(args[16])!=64 or args[1] in self.retired:return None
            if self.session is not None and args[1]!=self.session:return None
            if args[2]<=self.sequence or args[7]<self.config_revision or args[4]<=self.observed_revision:return None
            if args[3]>args[4] or (not args[8] and args[3]<self.source_revision):return None
            if args[35]:
                if any(int(args[i])!=args[i] or not 0<=args[i]<16 for i in (18,19)):return None
                if args[18]==args[19] or args[17]=="-" or not 0<args[20]<18000 or not 0<args[21]<=1+1e-6:return None
                if not np.isclose(args[22],(.25 if args[9] else .001),atol=1e-7,rtol=0):return None
            elif args[17]!="-" or args[21]!=0 or args[18]!=-1 or args[19]!=-1:return None
            modes=np.asarray(args[HEADER_COUNT:],float).reshape(16,4)
            if np.any(modes[:,0]<=0) or np.any(modes[:,0]>=18000) or np.any(modes[:,1]<0) or np.any(modes[:,1]>1+1e-6):return None
            if np.any(modes[:,2]<=0) or np.any(modes[:,2]>2) or np.any(modes[:,3]!=0):return None
            self.session=args[1];self.sequence=args[2];self.config_revision=args[7]
            self.observed_revision=args[4];self.source_revision=args[3]
            self.latest={"session_id":args[1],"sequence":args[2],"source_revision":args[3],
                "frequencies_hz":modes[:,0].copy(),"gains":modes[:,1].copy(),"arguments":tuple(args)}
            return self.latest
        except (TypeError,ValueError,IndexError,OverflowError):return None


class LiveWorker:
    def __init__(self,*,sender:Callable,config=None,error_handler=print):
        self.sender=sender;self.projector=LiveProjector(config);self.slot=LatestSnapshotSlot()
        self.last_error=None;self.errors=0;self._error_handler=error_handler
        self._stop=Event();self._thread=None

    def submit_snapshot(self,snapshot):return self.slot.submit(snapshot)

    def pump_once(self,*,now):
        snapshot=self.slot.take()
        if snapshot is None:return False
        try:
            packet=self.projector.process(snapshot,now=now)
            self.sender(packet);self.last_error=None
            return True
        except Exception as error:
            self.last_error=f"QMW_NOTE_TIMBRE_ERROR: {type(error).__name__}: {error}"
            self.errors+=1;self._error_handler(self.last_error)
            return False

    def start(self):
        if self._thread is not None:raise RuntimeError("worker already started")
        def run():
            while not self._stop.is_set():
                self.pump_once(now=time.monotonic())
                self._stop.wait(.1)  # <=10 analyses/s, latest-only overload behavior
        self._thread=Thread(target=run,name="qmw-note-timbre-observer",daemon=True)
        self._thread.start()
        return self

    def close(self):
        self._stop.set()
        if self._thread is not None:self._thread.join(timeout=2.)


def stereo_output(existing,private,*,solo=False,armed=True,sound_on=True,plucks_on=True,
                  master=1.,mix=1.,event_gain=1.,effective_voice_gains=(1.,)*8):
    """Offline oracle for SC's final stereo gate/solo, including resonant tails.

    No source gains/state are changed. Disarm+solo is silence; normal restores
    the exact old mix. The actual effective SIMPLE bus already includes its mute.
    """
    gains=np.asarray(effective_voice_gains,float)
    if gains.shape!=(8,) or not np.isfinite(gains).all():raise ValueError("eight effective voice gains required")
    scalars=np.array([master,mix,event_gain],float)
    if not np.isfinite(scalars).all():raise ValueError("finite owning mixer values required")
    gate=float(bool(armed and sound_on and plucks_on))*np.prod(np.maximum(scalars,0))*max(gains[0],0)
    return np.asarray(private)*gate+(0 if solo else np.asarray(existing))
