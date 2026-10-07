"""Version 2 live adapter: existing source/engines, declared downstream routing.

No state evolution, audio-device ownership, hidden normalization or event backlog.
The v1 diagnostic field stays diagnostic; the appended amplitude is linear DSP gain.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
import hashlib
import json
from threading import Lock
import numpy as np

from qmw.core.state_frame import QuantumStateFrame
from qmw.core.transition import QuantumUnits, TransitionEngine
from qmw.acoustics.note_timbre import QuantumTimbreProjector, TransitionPitchProjector, RatioField
from qmw.acoustics.note_timbre_live import (
    LiveConfig, LivePacket, LiveWorker, PacketReceiver, SourceSnapshot,
    make_geometry, RATIOS, FRAME_PORT, CONTROL_PORT,
)
from qmw.architecture_v1.live import LiveRoutingConfig, route_live_event, analyze_live_snapshot
from qmw.architecture_v1.contracts import plain

FRAME_ADDRESS='/qmw/note_timbre/v2/frame'
CONTROL_ADDRESS='/qmw/note_timbre/v2/config'
AMPLITUDE_SOURCES=('matrix_element_magnitude','state_weighted_magnitude','diagnostic_activity')
RHYTHM_SOURCES=('energy_gap','absolute_order')
ANALYSIS_BASES=('computational','hamiltonian','qho','qft')


@dataclass(frozen=True)
class RoutedLiveConfig(LiveConfig):
    amplitude_source: int = 1
    rhythm_source: int = 1
    quantization: int = 0
    analysis_basis: int = 0

    def __post_init__(self):
        super().__post_init__()
        for name,size in [('amplitude_source',3),('rhythm_source',2),('quantization',2),('analysis_basis',4)]:
            value=getattr(self,name)
            if type(value) is not int or not 0<=value<size:raise ValueError(f'invalid {name}')

    def routing(self):
        return LiveRoutingConfig(amplitude_source=AMPLITUDE_SOURCES[self.amplitude_source],
            amplitude_reference=1.,rhythm_source=RHYTHM_SOURCES[self.rhythm_source],
            quantization=('continuous','lattice')[self.quantization],
            analysis_basis=ANALYSIS_BASES[self.analysis_basis],revision=self.revision,
            minimum_interval_seconds=.5,maximum_interval_seconds=8.)

    def declaration(self):
        return {'controls':asdict(self),'routing':self.routing().to_dict(),
            'mode':'ANALYSIS','transport_version':2,'duration_policy':'strike .001s; pitched .25s',
            'admission':'activity > 1e-6; strongest then source/target; at most one; no catchup',
            'configuration_change':'audible controls cancel pending deadline after minimum .5s; analysis view alone preserves deadline',
            'source_coordinates':'native q0-LSB; no bit reversal',
            'renderer_profile':{'id':'qmw.sc.ringz.stereo.v2.headroom1',
                'event_output_gain':0.125,'pitched_exciter_gain':0.02,
                'protective_limiter_peak':0.7,'stereo_distribution':'equal power',
                'scope':'fixed acoustic calibration; mixer and polyphony can still engage limiter'}}

    @property
    def digest(self):
        return hashlib.sha256(json.dumps(self.declaration(),sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()

    @classmethod
    def from_control(cls,args):
        if len(args)!=9 or any(type(v) is not int for v in args):raise ValueError('v2 config requires nine atomic integers')
        revision,body,excitation,octave,hold,amplitude,rhythm,quantization,analysis=args
        if body not in (0,1) or excitation not in (0,1) or hold not in (0,1):raise ValueError('invalid body/excitation/hold switch')
        return cls(revision,('identity','fourier')[body],('strike','pitched')[excitation],
            octave,bool(hold),amplitude,rhythm,quantization,analysis)


@dataclass(frozen=True)
class RoutedLivePacket(LivePacket):
    raw_activity: float = 0.
    scheduled_interval: float = 0.
    routing_audit: object = None
    argument_count: int = 108

    def audit_entry(self):
        source=self.snapshot
        result={'schema':'qmw.note_timbre.live.audit.v2','session_id':self.session_id,
            'sequence':self.sequence,'source_revision':self.source_revision,
            'observed_revision':self.observed_revision,'admitted':self.note is not None,
            'configuration':self.config.declaration(),'configuration_digest':self.config.digest,
            'routing':plain(self.routing_audit),'legacy_provenance':list(self.provenance),
            'source_H_sha256':hashlib.sha256(source.H.tobytes()).hexdigest(),
            'source_rho_sha256':hashlib.sha256(source.rho.tobytes()).hexdigest(),
            'source_A_sha256':hashlib.sha256(source.A.tobytes()).hexdigest()}
        return result

    def arguments(self):
        args=super().arguments();args[0]=2;args[21]=self.raw_activity if self.note else 0.
        args[16]=hashlib.sha256(json.dumps(self.audit_entry(),sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
        cfg=self.config
        return args+[float(self.note.strength) if self.note else 0.,self.scheduled_interval if self.note else 0.,
            cfg.amplitude_source,cfg.rhythm_source,cfg.quantization,cfg.analysis_basis,0,cfg.digest]


class RoutedLiveProjector:
    def __init__(self,config=None):
        self.config=config or RoutedLiveConfig();self._lock=Lock();self._held=None
        self._last_event=-np.inf;self._next_event=-np.inf;self._applied_audible_config=None;self._sequence=0
        self.units=QuantumUnits();self.transitions=TransitionEngine(units=self.units)
        self.timbres=QuantumTimbreProjector()

    def configure(self,config):
        if not isinstance(config,RoutedLiveConfig):raise TypeError('RoutedLiveConfig required')
        with self._lock:
            if config.revision<self.config.revision:return False
            if config.revision==self.config.revision:return config==self.config
            if not config.hold or not self.config.hold:self._held=None
            self.config=config
            return True

    def process(self,snapshot,*,now):
        if not np.isfinite(now) or now<0:raise ValueError('finite nonnegative musical monotonic time required')
        with self._lock:
            cfg=self.config
            if cfg.hold and self._held is None:self._held=snapshot
            source=self._held if cfg.hold else snapshot
        audible_config=(cfg.basis,cfg.excitation,cfg.octave,cfg.hold,cfg.amplitude_source,cfg.rhythm_source,cfg.quantization)
        if audible_config!=self._applied_audible_config:
            self._next_event=max(float(now),self._last_event+.5)
            self._applied_audible_config=audible_config
        transition=self.transitions.process(source.H,source.A,source.rho,source.context)
        pitch=TransitionPitchProjector(state_degrees=tuple(j%5+5*cfg.octave for j in range(16)),
            ratio_field=RatioField(RATIOS,reference_hz=220,name='live_explicit_five'),
            min_activity=1e-6,duration_seconds=.001 if cfg.excitation=='strike' else .25)
        notes=pitch.process(transition)
        geometry=make_geometry(cfg.basis)
        body=self.timbres.process(rho=source.rho,geometry_modes=geometry,context=source.context)
        mapped=None;raw=0.;interval=0.;audit=None
        state=QuantumStateFrame(source.context.time,source.context.dt,source.rho,source.H,source.context.source_id)
        if notes and now>=self._next_event:
            candidate=min(notes,key=lambda n:(-n.strength,n.source_state,n.target_state))
            routed=route_live_event(state=state,context=source.context,units=self.units,operator=source.A,
                transition=transition,note=candidate,pitch_projector=pitch,body=body,geometry=geometry,
                configuration=cfg.routing(),now=float(now))
            interval=routed.scheduled_interval_seconds;audit=routed.audit
            if now>=self._next_event:
                mapped=routed.prepared.excitation;raw=candidate.strength;self._last_event=float(now)
                self._next_event=float(now)+interval
        else:
            audit=analyze_live_snapshot(state=state,context=source.context,units=self.units,
                operator=source.A,configuration=cfg.routing())
        self._sequence+=1
        provenance=transition.provenance+body.provenance+(
            'qmw.architecture_v1.live.route_live_event; shared checked offline/live preparation',
            'source model time is provenance; musical playback begins on receipt; no physical waiting-time model',
            'latest snapshot only; minimum .5s; maximum one event; no catchup',
            'configuration:'+cfg.digest)
        return RoutedLivePacket(source.session_id,self._sequence,source.context.frame_id,snapshot.context.frame_id,
            cfg,cfg.hold,source.operator_label,source.operator_revision,mapped,body,float(now),provenance,source,
            raw_activity=raw,scheduled_interval=interval,routing_audit=audit)


class RoutedLiveWorker(LiveWorker):
    def __init__(self,*,sender,config=None,error_handler=print):
        super().__init__(sender=sender,error_handler=error_handler)
        self.projector=RoutedLiveProjector(config)


class RoutedPacketReceiver(PacketReceiver):
    """Validate every v2 extension before the existing atomic v1 watermark gate."""
    def accept(self,args):
        try:
            if len(args)!=108 or args[0]!=2:return None
            for i in range(100,107):
                if isinstance(args[i],bool) or not isinstance(args[i],(int,float,np.number)) or not np.isfinite(args[i]):return None
            if not 0<=args[100]<=1 or args[106]!=0:return None
            if args[35]:
                if not .5<=args[101]<=8.:return None
            elif args[100]!=0 or args[101]!=0:return None
            if any(int(args[i])!=args[i] for i in range(102,107)):return None
            cfg=RoutedLiveConfig.from_control([int(args[i]) for i in (7,11,9,10,8,102,103,104,105)])
            if args[107]!=cfg.digest:return None
            if not isinstance(args[16],str) or len(args[16])!=64 or any(c not in '0123456789abcdef' for c in args[16]):return None
            legacy=list(args[:100]);legacy[0]=1
            accepted=super().accept(legacy)
            if accepted is None:return None
            accepted.update(arguments=tuple(args),excitation_amplitude=float(args[100]),
                interval_seconds=float(args[101]),configuration_digest=args[107])
            return accepted
        except (ValueError,TypeError,IndexError,OverflowError):return None
