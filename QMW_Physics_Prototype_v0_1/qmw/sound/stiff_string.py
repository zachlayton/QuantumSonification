"""Stateful, force-driven modal discretization of a simply supported stiff string.

mu*u_tt = T*u_xx - EI*u_xxxx - 2*mu*sigma0*u_t
          + 2*mu*sigma1*u_txx + f(x,t).
Boundaries: u=u_xx=0 at x=0,L. Displacement is in metres; forces in newtons.
Exact zero-order-hold time stepping of each retained linear mechanical mode.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
import numpy as np
from scipy.signal import lfilter


@dataclass(frozen=True)
class StringParameters:
    length_m: float = .86
    tension_n: float = 90.0
    linear_density_kg_m: float = .008
    bending_stiffness_nm2: float = .0025
    loss0_per_s: float = .35
    loss1_m2_s: float = .00015
    modes: int = 96

    def __post_init__(self):
        for name,value in asdict(self).items():
            if isinstance(value,bool) or not np.isfinite(value):raise ValueError(f"Invalid {name}")
        if min(self.length_m,self.tension_n,self.linear_density_kg_m)<=0:
            raise ValueError("Length, tension and mass per length must be positive")
        if min(self.bending_stiffness_nm2,self.loss0_per_s,self.loss1_m2_s)<0:
            raise ValueError("Stiffness and losses must be nonnegative")
        if not isinstance(self.modes,int) or not 1<=self.modes<=1024:
            raise ValueError("Mode count must be an integer in 1..1024")


@dataclass(frozen=True)
class ForceEvent:
    t: float
    impulse_ns: float
    position: float
    contact_s: float = .0015
    width_m: float = .006
    source: str = "manual"

    def __post_init__(self):
        if not np.isfinite([self.t,self.impulse_ns,self.position,self.contact_s,self.width_m]).all():
            raise ValueError("Force event contains nonfinite values")
        if self.t<0 or self.contact_s<=0 or self.width_m<0 or not 0<self.position<1:
            raise ValueError("Invalid event time, contact, position or width")


class StiffString:
    """Persistent displacement/velocity state; pickups do not alter the string.

    Only underdamped modes below 0.45*sample_rate are retained. High modes are
    explicitly truncated, not folded into audio. No oscillator phase resets,
    note envelopes, pitch quantization, hidden excitation or normalization.
    """
    def __init__(self, parameters: StringParameters | None = None, sample_rate: int = 48000):
        if isinstance(sample_rate,bool) or not isinstance(sample_rate,int) or sample_rate<8000:
            raise ValueError("Sample rate must be an integer >=8000")
        self.parameters=parameters or StringParameters();p=self.parameters
        self.sample_rate=sample_rate
        k=np.arange(1,p.modes+1)*np.pi/p.length_m
        omega2=(p.tension_n*k*k+p.bending_stiffness_nm2*k**4)/p.linear_density_kg_m
        sigma=p.loss0_per_s+p.loss1_m2_s*k*k
        keep=np.sqrt(omega2)<2*np.pi*.45*sample_rate
        if not np.any(keep):raise ValueError("No string modes fall within the audio bandwidth")
        self.k=k[keep];self.omega2=omega2[keep];self.sigma=sigma[keep]
        if np.any(self.sigma**2>=self.omega2):
            raise ValueError("This implementation requires underdamped retained modes; reduce losses")
        self.count=len(self.k);self.truncated_modes=p.modes-self.count
        self.modal_mass=p.linear_density_kg_m*p.length_m/2
        self.omega=np.sqrt(self.omega2)
        wd=np.sqrt(self.omega2-self.sigma**2);h=1/sample_rate
        r=np.exp(-self.sigma*h);c=np.cos(wd*h);s=np.sin(wd*h)/wd
        self.a11=r*(c+self.sigma*s);self.a12=r*s
        self.a21=-self.omega2*self.a12;self.a22=r*(c-self.sigma*s)
        self.det=r*r;self.trace=self.a11+self.a22
        self.bq=(1-self.a11)/(self.modal_mass*self.omega2)
        self.bq2=(self.det-self.a22)/(self.modal_mass*self.omega2)
        self.bv=self.a12/self.modal_mass
        self.q=np.zeros(self.count);self.v=np.zeros(self.count)
        self.samples_elapsed=0

    @property
    def frequency_hz(self):return self.omega/(2*np.pi)

    def spatial_weights(self, position: float, width_m: float = 0.0):
        p=self.parameters
        if not np.isfinite([position,width_m]).all() or not 0<=position<=1 or width_m<0:
            raise ValueError("Position must be in [0,1] and width nonnegative")
        if width_m>2*p.length_m*min(position,1-position)+1e-14:
            raise ValueError("Contact/pickup aperture extends past a string endpoint")
        # Average of sin(k*x) over a uniform contact/pickup aperture.
        return np.sin(self.k*(position*p.length_m))*np.sinc(self.k*width_m/(2*np.pi))

    def energy_j(self):
        return float(.5*self.modal_mass*np.sum(self.v**2+self.omega2*self.q**2))

    def static_pluck(self, displacement_m=.001,position=.23,width_m=.004):
        """Initialize a string at static equilibrium under a localized pull.

        The requested displacement is averaged over the contact aperture. Returns
        the required holding force (N). Call once to initialize, not per note.
        Subsequent process() calls preserve all existing motion.
        """
        if self.samples_elapsed or np.any(self.q) or np.any(self.v):
            raise ValueError("Static pluck initializes a fresh string only")
        if not np.isfinite(displacement_m):raise ValueError("Displacement must be finite")
        b=self.spatial_weights(position,width_m)
        compliance=np.sum(b*b/(self.modal_mass*self.omega2))
        if compliance<=0:raise ValueError("Cannot pluck at a fixed endpoint")
        hold=displacement_m/compliance
        self.q=hold*b/(self.modal_mass*self.omega2)
        return float(hold)

    def process(self, force_n, position=.23, contact_width_m=.006,
                pickups=(.18,.31),pickup_width_m=.008,output="velocity"):
        """Advance audio samples under scalar point/patch force or modal forces.

        A (samples,) input is total patch force N. A (modes,samples) input is
        already projected generalized force N per mode. Returns physical pickup
        displacement (m) or velocity (m/s), one column per pickup.
        """
        force=np.asarray(force_n,dtype=float)
        if force.ndim==1:
            weights=self.spatial_weights(position,contact_width_m)
            modal=None;n=len(force)
        elif force.ndim==2 and force.shape[0]==self.count:
            modal=force;n=force.shape[1]
        else:raise ValueError("Forces must have shape (samples,) or (retained_modes,samples)")
        if not np.isfinite(force).all():raise ValueError("Force must be finite")
        if output not in ("velocity","displacement"):raise ValueError("Unknown pickup output")
        pickup=np.array([self.spatial_weights(x,pickup_width_m) for x in pickups])
        result=np.zeros((n,len(pickups)))
        if not n:return result
        for i in range(self.count):
            f=modal[i] if modal is not None else force*weights[i]
            a=[1,-self.trace[i],self.det[i]]
            # Physical q/v -> exact IIR initial state at the start of each block.
            q,_=lfilter([self.bq[i],self.bq2[i]],a,f,
                zi=[self.a11[i]*self.q[i]+self.a12[i]*self.v[i],-self.det[i]*self.q[i]])
            v,_=lfilter([self.bv[i],-self.bv[i]],a,f,
                zi=[self.a21[i]*self.q[i]+self.a22[i]*self.v[i],-self.det[i]*self.v[i]])
            result+=(v if output=="velocity" else q)[:,None]*pickup[:,i]
            self.q[i]=q[-1];self.v[i]=v[-1]
        self.samples_elapsed+=n
        return result


def render_force_events(events, duration,parameters=None,sample_rate=48000,
                        pickups=(.18,.31),pickup_width_m=.008,block_size=2048):
    """Drive one persistent physical string; simultaneous contacts add forces."""
    if not np.isfinite(duration) or duration<=0:raise ValueError("Duration must be positive")
    if not isinstance(block_size,int) or block_size<=0:raise ValueError("Invalid block size")
    model=StiffString(parameters,sample_rate)
    total=int(np.ceil(duration*sample_rate));output=np.zeros((total,len(pickups)))
    prepared=[]
    for e in events:
        # Event validation belongs to ForceEvent. Integrate each sampled pulse to its impulse.
        count=max(2,int(round(e.contact_s*sample_rate)))
        phase=(np.arange(count)+.5)/count
        pulse=1-np.cos(2*np.pi*phase)
        pulse*=e.impulse_ns*sample_rate/pulse.sum()
        prepared.append((int(round(e.t*sample_rate)),pulse,model.spatial_weights(e.position,e.width_m)))
    for start in range(0,total,block_size):
        end=min(total,start+block_size);forces=np.zeros((model.count,end-start))
        for onset,pulse,weights in prepared:
            lo=max(start,onset);hi=min(end,onset+len(pulse))
            if hi>lo:forces[:,lo-start:hi-start]+=weights[:,None]*pulse[None,lo-onset:hi-onset]
        output[start:end]=model.process(forces,pickups=pickups,pickup_width_m=pickup_width_m)
    return output,model


def force_events_from_physics(events, region_count=16, impulse_gain=.5,
                              contact_s=.0015,width_m=.006):
    """Declared interface: scaled incoming flux -> N s impulse, region -> contact.

    No frequency is read or assigned. Each event acts on the same string.
    impulse_gain has units N s per scaled source unit. This is a sonification
    coupling, not physical energy transfer between quantum and acoustic systems.
    """
    from qmw.core import EventType
    if region_count<1 or not np.isfinite(impulse_gain) or impulse_gain<0:
        raise ValueError("Invalid force mapping")
    result=[]
    for e in events:
        if e.type!=EventType.ENERGY_ARRIVAL or e.region is None:continue
        if not 0<=e.region<region_count:raise ValueError("Region lies outside projection")
        if not np.isfinite(e.magnitude) or e.magnitude<0:raise ValueError("Invalid source magnitude")
        # Keep finite contacts away from the endpoints; this spatial mapping is explicit.
        position=.08+.84*(e.region+.5)/region_count
        result.append(ForceEvent(e.t,impulse_gain*e.magnitude,position,contact_s,width_m,
            f"{e.source_observable}; region={e.region}; raw_flux={e.magnitude:.9g}; gain={impulse_gain:g} N s/source-unit"))
    return result
