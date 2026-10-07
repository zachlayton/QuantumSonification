"""A single owner of physics state; explicit clocks and external-work ledgers."""
from __future__ import annotations
from collections import deque
import math
import threading
from uuid import uuid4
import numpy as np
from qmw.core import Domain, PhysicsFrame, PhysicsEvent, EventType
from qmw.core.serialization import jsonable
from qmw.conservation import ConservationMonitor
from qmw.projection import RegionProjector, ModalProjector
from qmw.events import FlowEventDetector
from qmw.sound import SonificationPolicy


SCHRODINGER_DEFAULTS = {
    "potential_strength":0.0,"barrier_height":0.0,"barrier_width":1.5,
    "packet_width":2.5,"packet_center":-16.0,"packet_momentum":0.6,"mass":0.5,
}
SCALAR_DEFAULTS = {
    "amplitude":0.6,"width":3.0,"rotation_frequency":0.95,
    "mass_squared":1.0,"attraction":1.0,"repulsion":1.0,"init":"rotating_gaussian",
}
LINDBLAD_DEFAULTS = {"init":"plus","seed":0,"damping_rate":0.05,"dephasing_rate":0.02,
    "h_x0":0.35,**{f"h_z{i}":-0.5 for i in range(4)}}
GLOBAL_DEFAULTS = {"dt":0.002,"threshold":0.003,"fundamental_hz":110.0,
    "gain":0.18,"decay_s":1.5,"flux_scale":0.05,"running":True}


class PhysicsEngine:
    def __init__(self, model="schrodinger", n=2048, length=64.0, controls=None):
        self.lock = threading.RLock()
        self.n,self.length=n,length
        self.sequence=-1
        self.run_id=uuid4().hex
        self.event_history=deque(maxlen=100)
        self.force_history=deque(maxlen=100)
        self.controls={**GLOBAL_DEFAULTS}
        self.model_kind=model
        self._reset_unlocked(model)
        if controls:
            self.set_controls(controls)
            # Constructor overrides define initial conditions, rather than a quench
            # of the default initial state. Interactive controls remain reset-required.
            self.reset()

    def _new_model(self, kind):
        if kind=="schrodinger":
            from qmw.physics.schrodinger import SchrodingerModel
            model=SchrodingerModel(Domain.periodic(self.n,self.length))
            defaults=dict(SCHRODINGER_DEFAULTS)
            if self.n<64:
                defaults.update({key:model.defaults[key] for key in ("packet_width","barrier_width","packet_momentum")})
            return model,defaults
        if kind=="scalar":
            from qmw.physics.scalar_field import ScalarFieldModel
            defaults={**SCALAR_DEFAULTS,"width":max(2*self.length/self.n,min(3.0,self.length/8))}
            return ScalarFieldModel(domain=Domain.periodic(self.n,self.length)),defaults
        if kind=="lindblad":
            from qmw.physics.lindblad import LindbladModel
            return LindbladModel(),LINDBLAD_DEFAULTS
        raise ValueError("Model must be schrodinger, scalar or lindblad")

    def _physics_controls(self, values=None, kind=None, model=None):
        source=self.controls if values is None else values
        kind=self.model_kind if kind is None else kind
        model=self.model if model is None else model
        if kind=="schrodinger":names=model.supported_controls
        elif kind=="scalar":names=set(SCALAR_DEFAULTS)
        else:
            names=set(LINDBLAD_DEFAULTS)
            names.update(f"h_{axis}{i}" for axis in "xyz" for i in range(4))
            names.update(f"j_{axis}{i}{j}" for axis in ("xx","yy","zz") for i in range(4) for j in range(i+1,4))
        return {k:v for k,v in source.items() if k in names}

    def _make_policy(self, controls=None):
        c=self.controls if controls is None else controls
        return SonificationPolicy(fundamental_hz=c["fundamental_hz"],decay_s=c["decay_s"],
            gain=c["gain"],flux_scale=c["flux_scale"])

    def _reset_unlocked(self, kind=None):
        requested=kind or self.model_kind
        old_kind=getattr(self,"model_kind",None)
        old_controls=self._physics_controls() if hasattr(self,"model") else {}
        model,defaults=self._new_model(requested)
        global_controls={k:self.controls.get(k,v) for k,v in GLOBAL_DEFAULTS.items()}
        candidate_controls={**global_controls,**defaults,"model":requested}
        if old_kind==requested:candidate_controls.update(old_controls)
        if requested=="schrodinger" and self.length != 64:
            candidate_controls["packet_center"]=-self.length/4
            for key in ("packet_width","barrier_width"):
                candidate_controls[key]=max(2*self.length/self.n,min(candidate_controls[key],self.length/8))
        pc=self._physics_controls(candidate_controls,requested,model)
        candidate_state=model.initialize(pc)
        candidate_state.validate(model.domain)
        self._validate_timestep(model,candidate_state,pc,candidate_controls["dt"])
        self.model_kind=requested;self.model=model
        self.controls=candidate_controls;self.state=candidate_state
        self.t=0.0;self.cumulative_work=0.0;self.cumulative_environment_energy=0.0
        self.monitor=ConservationMonitor(self.model.domain)
        count=min(16,self.model.domain.size)
        self.region_projector=RegionProjector(self.model.domain,count)
        self.modal_projector=ModalProjector(self.model.domain,count)
        self.detector=FlowEventDetector(self.controls["threshold"],mode_threshold=.1 if requested=="lindblad" else None)
        self.policy=self._make_policy()
        self.event_history.clear()
        self.force_history.clear()
        self.sequence+=1
        self.frame=self._build_frame(0.0)
        self.sound=self.policy.map(self.frame)
        # Establish the baseline without producing reset-time plucks.
        self.detector.update(None,self.frame)

    def reset(self, model=None):
        with self.lock:self._reset_unlocked(model)

    @staticmethod
    def _validate_timestep(model,state,physics_controls,dt):
        if hasattr(model,"stable_dt_bound"):
            bound=model.stable_dt_bound(state,physics_controls)
            if dt>=bound:raise ValueError(f"Timestep {dt:g} must be below scalar stability bound {bound:.6g}")

    def _build_frame(self, dt):
        obs=self.model.compute_observables(self.state,self._physics_controls())
        conservation,diagnostics=self.monitor.evaluate(self.state,obs,self.cumulative_work,self.cumulative_environment_energy)
        frame=PhysicsFrame(self.sequence,self.t,dt,self.model.model_id,self.model.domain,self.state,
            obs,conservation=conservation,diagnostics=diagnostics)
        frame.regions=self.region_projector.project(frame)
        frame.modes=self.modal_projector.project(frame)
        if hasattr(self.model,"initialization_metadata"):
            description=self.model.initialization_metadata.get("description")
            if description:diagnostics.notes.append(description)
        if self.model_kind=="lindblad":
            diagnostics.notes.append("Environment ledger integrates Tr(H D(rho)) with trapezoidal time quadrature; its O(dt²) integration error remains visible in energy drift.")
        if frame.modes.coefficients is not None and self.state.psi is not None and frame.modes.captured_norm < .9:
            diagnostics.notes.append(f"Only {frame.modes.captured_norm:.3g} of the wavefunction norm is captured by the displayed {len(frame.modes.populations)} modes; the full field is still evolved.")
        frame.validate()
        return frame

    def step(self, count=1):
        if isinstance(count,bool) or not isinstance(count,int) or not 1<=count<=100000:
            raise ValueError("Step count must be an integer in 1..100000")
        with self.lock:
            events=[]
            for _ in range(count):
                previous=self.frame;old_state=self.state
                pc=self._physics_controls();dt=float(self.controls["dt"])
                self.state=self.model.step(old_state,pc,dt)
                if self.model_kind=="lindblad":
                    h=self.model.hamiltonian(pc)
                    new_power=float(np.trace(h@self.model.dissipator(self.state.rho,pc)).real)
                    self.cumulative_environment_energy+=.5*dt*(previous.observables.source_power+new_power)
                self.t+=dt;self.sequence+=1
                self.frame=self._build_frame(dt)
                self.frame.events=self.detector.update(previous,self.frame)
                current_sound=self.policy.map(self.frame)
                for event in current_sound.events:
                    event.event_id=f"{self.run_id}:{event.event_id}"
                events.extend(current_sound.events)
                self.event_history.extend(current_sound.events)
                from qmw.sound.stiff_string import force_events_from_physics
                for index, force in enumerate(force_events_from_physics(self.frame.events)):
                    self.force_history.append({**jsonable(force), "event_id":f"{self.run_id}:string:{self.model_kind}:{self.sequence}:{index}"})
                self.sound=current_sound
            # Batched publication preserves every event encountered, not only the last step's.
            self.sound.events=events
            return self.frame,self.sound

    def set_controls(self, updates):
        if not isinstance(updates,dict):raise ValueError("Controls must be a JSON object")
        with self.lock:
            requested=updates.get("model",self.model_kind)
            if requested!=self.model_kind:
                if set(updates)!={"model"}:raise ValueError("Select a model separately from changing parameters")
                # Build and initialize first so a bad selector cannot alter current state.
                self._reset_unlocked(requested)
                return
            allowed=set(self.controls)|set(self._physics_controls())
            if self.model_kind=="lindblad":
                allowed.update(f"h_{a}{i}" for a in "xyz" for i in range(4))
                allowed.update(f"j_{a}{i}{j}" for a in ("xx","yy","zz") for i in range(4) for j in range(i+1,4))
            unknown=set(updates)-allowed
            if unknown:raise ValueError(f"Unknown controls: {sorted(unknown)}")
            candidate={**self.controls,**updates}
            if not isinstance(candidate["running"],bool):raise ValueError("running must be true or false")
            for key,value in updates.items():
                if key not in ("model","init","running"):
                    if isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(value):
                        raise ValueError(f"{key} must be a finite number")
            if not .00001<=candidate["dt"]<=.02:raise ValueError("dt must be in [0.00001,0.02] simulation time")
            new_policy=self._make_policy(candidate)
            new_detector=FlowEventDetector(candidate["threshold"],mode_threshold=.1 if self.model_kind=="lindblad" else None)
            pc=self._physics_controls(candidate)
            # Validate initializer controls without changing the authoritative state.
            old_metadata=getattr(self.model,"initialization_metadata",None)
            try:initial_candidate=self.model.initialize(pc)
            finally:
                if old_metadata is not None:self.model.initialization_metadata=old_metadata
            self._validate_timestep(self.model,self.state,pc,candidate["dt"])
            self._validate_timestep(self.model,initial_candidate,pc,candidate["dt"])
            before=self.frame.observables.total_energy
            after_obs=self.model.compute_observables(self.state,pc)
            after=after_obs.total_energy
            work=0.0 if before is None or after is None else after-before
            threshold_changed=candidate["threshold"]!=self.controls["threshold"]
            self.controls=candidate;self.policy=new_policy
            self.cumulative_work+=work
            self.sequence+=1
            self.frame=self._build_frame(0.0)
            if abs(work)>1e-15:
                self.frame.events=[PhysicsEvent(EventType.QUENCH,self.t,abs(work),"conservation.cumulative_work",
                    frame_sequence=self.sequence,detail=f"Control change added signed external work {work:.6g}.")]
            if threshold_changed:
                self.detector=new_detector;self.detector.update(None,self.frame)
            self.sound=self.policy.map(self.frame)

    def snapshot(self, include_state=False):
        with self.lock:
            physics=jsonable(self.frame)
            if not include_state:physics.pop("state",None)
            return {"run_id":self.run_id,"physics":physics,"sound":jsonable(self.sound),"controls":dict(self.controls),
                "running":self.controls["running"],"event_history":jsonable(list(self.event_history)),
                "force_history":list(self.force_history),
                "visualization":{"field_magnitude":jsonable(np.abs(self.state.phi)**2) if self.state.phi is not None else None},
                "initialization":jsonable(getattr(self.model,"initialization_metadata",{}))}
