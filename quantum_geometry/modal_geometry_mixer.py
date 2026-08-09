"""Phase-aware mixtures of tracked modal lineages across geometry worlds."""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence
import json
import numpy as np


@dataclass(frozen=True)
class ModalWorld:
    geometry_id: str
    lineage_ids: np.ndarray
    frequencies_hz: np.ndarray
    decay_seconds: np.ndarray
    amplitudes: np.ndarray
    topology_id: str = ""
    tracking_method: str = ""


@dataclass(frozen=True)
class ModalMixtureFrames:
    lineage_ids: np.ndarray
    population_strength: np.ndarray
    complex_strength: np.ndarray
    complex_phase: np.ndarray
    population_frequency_hz: np.ndarray
    complex_frequency_hz: np.ndarray
    decay_seconds: np.ndarray
    dominant_strength: np.ndarray
    dominant_phase: np.ndarray
    dominant_frequency_hz: np.ndarray


def load_modal_world(state_file: str | Path, geometry_id: str) -> ModalWorld:
    state_path=Path(state_file); data=json.loads(state_path.read_text()); bundle=Path(data["paths"]["bundle_npz"])
    if not bundle.is_absolute() and not bundle.exists(): bundle=state_path.parent/bundle
    with np.load(bundle) as z:
        ids=np.asarray(z["mode_stable_ids"],dtype=np.int64); frequencies=np.asarray(z["frequencies_hz"],dtype=float); decay=np.asarray(z["decay_times_seconds"],dtype=float)
        amplitudes=np.asarray(z["mode_amplitudes"],dtype=complex); material=np.asarray(z["mode_weights"],dtype=float)
    amplitudes=amplitudes*(material/max(float(np.max(np.abs(material))),1e-12))
    tracking=data.get("descriptors",{}).get("modal_tracking",{})
    if tracking.get("stable_mode_ids") != ids.tolist():
        raise ValueError(f"{geometry_id}: bundle lineage IDs disagree with state metadata")
    return ModalWorld(geometry_id,ids,frequencies,decay,amplitudes,str(tracking.get("topology_id","")),str(tracking.get("method","")))


def validate_lineage_compatibility(worlds: Sequence[ModalWorld]) -> dict:
    """Fail closed unless recorded Living Spectral Geometry lineage IDs are comparable."""
    worlds=tuple(worlds)
    if not worlds: raise ValueError("at least one modal world is required")
    topologies={w.topology_id for w in worlds}; methods={w.tracking_method for w in worlds}
    if "" in topologies or len(topologies)!=1: raise ValueError("modal worlds do not declare one shared topology")
    if methods!={"mass_weighted_invariant_subspace"}: raise ValueError("unsupported or missing Living modal tracking method")
    for w in worlds:
        n=len(w.lineage_ids)
        if len(set(map(int,w.lineage_ids)))!=n: raise ValueError(f"{w.geometry_id}: duplicate lineage IDs")
        if not all(len(x)==n for x in (w.frequencies_hz,w.decay_seconds,w.amplitudes)): raise ValueError(f"{w.geometry_id}: inconsistent modal array lengths")
        if np.any(w.frequencies_hz<=0) or np.any(w.decay_seconds<=0): raise ValueError(f"{w.geometry_id}: non-positive modal parameters")
    sets=[set(map(int,w.lineage_ids)) for w in worlds]
    overlaps=[len(a&b) for a,b in zip(sets,sets[1:])]
    if overlaps and min(overlaps)==0: raise ValueError("adjacent worlds have no recorded lineage continuity")
    return {"compatible":True,"world_count":len(worlds),"topology_id":next(iter(topologies)),"tracking_method":next(iter(methods)),"lineage_count":len(set.union(*sets)),"persistent_lineage_count":len(set.intersection(*sets)),"adjacent_overlap_counts":overlaps}


def parallel_transport_gauge(states: np.ndarray) -> np.ndarray:
    """Remove unobservable global phase while preserving relative geometry phases."""
    states=np.asarray(states,dtype=np.complex128).copy()
    anchor=int(np.argmax(np.abs(states[0]))); states[0]*=np.exp(-1j*np.angle(states[0,anchor]))
    for t in range(1,len(states)):
        overlap=np.vdot(states[t-1],states[t])
        if abs(overlap)>1e-14: states[t]*=np.exp(-1j*np.angle(overlap))
    return states


def _fold_audible(frequency: float, low: float=45.0, high: float=6000.0) -> float:
    f=max(float(frequency),1e-9)
    while f<low: f*=2.0
    while f>high: f*=0.5
    return f


def mix_modal_lineages(conditional_states: np.ndarray, worlds: Sequence[ModalWorld]) -> ModalMixtureFrames:
    worlds=tuple(worlds); validate_lineage_compatibility(worlds)
    raw=np.asarray(conditional_states,dtype=np.complex128)
    norms=np.sum(np.abs(raw)**2,axis=1)
    if np.any(~np.isfinite(norms)) or np.any(norms<=1e-14): raise ValueError("conditional states must have finite nonzero norm")
    c=parallel_transport_gauge(raw/np.sqrt(norms)[:,None])
    if c.shape[1]!=len(worlds): raise ValueError("one conditional amplitude per geometry world is required")
    ids=np.asarray(sorted(set().union(*(set(w.lineage_ids.tolist()) for w in worlds))),dtype=np.int64); index={int(k):j for j,k in enumerate(ids)}
    shape=(len(c),len(ids)); pop=np.zeros(shape); coh=np.zeros(shape); phase=np.zeros(shape); popf=np.zeros(shape); cohf=np.zeros(shape); decay=np.ones(shape)
    dom=np.zeros(shape); domphase=np.zeros(shape); domf=np.zeros(shape)
    for t,ct in enumerate(c):
        p=np.abs(ct)**2; dominant=int(np.argmax(p))
        for col,lineage in enumerate(ids):
            entries=[]
            for i,w in enumerate(worlds):
                hits=np.flatnonzero(w.lineage_ids==lineage)
                if len(hits):
                    j=int(hits[0]); entries.append((i,w.amplitudes[j],w.frequencies_hz[j],w.decay_seconds[j]))
            if not entries: continue
            pi=np.asarray([p[i] for i,_,_,_ in entries]); ci=np.asarray([ct[i] for i,_,_,_ in entries]); a=np.asarray([a for _,a,_,_ in entries]); f=np.asarray([f for *_,f,_ in entries]); d=np.asarray([d for *_,d in entries])
            pw=pi*np.abs(a); cw=np.abs(ci*a); z=np.sum(ci*a)
            pop[t,col]=np.sum(pw); coh[t,col]=abs(z); phase[t,col]=np.angle(z)
            popf[t,col]=_fold_audible(np.sum(pw*f)/max(np.sum(pw),1e-12)); cohf[t,col]=_fold_audible(np.sum(cw*f)/max(np.sum(cw),1e-12)); decay[t,col]=np.sum(cw*d)/max(np.sum(cw),1e-12)
            for i,a0,f0,_ in entries:
                if i==dominant: dom[t,col]=abs(a0); domphase[t,col]=np.angle(a0); domf[t,col]=_fold_audible(f0)
    return ModalMixtureFrames(ids,pop,coh,phase,popf,cohf,decay,dom,domphase,domf)


def synthesize_modal_comparison(frames: ModalMixtureFrames, *, duration_seconds: float=32.0, sample_rate: int=24000, onset_fade_seconds: float=0.04, tail_fade_seconds: float=0.06) -> tuple[np.ndarray,dict]:
    n=max(2,int(duration_seconds*sample_rate)); sample_t=np.arange(n)/sample_rate; frame_t=np.linspace(0,duration_seconds,len(frames.population_strength))
    outputs=[]
    specs=((frames.population_strength,frames.population_frequency_hz,np.zeros_like(frames.complex_phase)),(frames.complex_strength,frames.complex_frequency_hz,frames.complex_phase),(frames.dominant_strength,frames.dominant_frequency_hz,frames.dominant_phase))
    for strengths,frequencies,phases in specs:
        stereo=np.zeros((n,2),dtype=float)
        for k in range(len(frames.lineage_ids)):
            amp=np.interp(sample_t,frame_t,strengths[:,k]); freq=np.interp(sample_t,frame_t,frequencies[:,k]); ph=np.interp(sample_t,frame_t,np.unwrap(phases[:,k]))
            # A lineage is one continuous resonator voice.  The earlier renderer
            # restarted a decay envelope at every frame, producing audible steps.
            oscillator=np.cos(np.cumsum(2*np.pi*freq/sample_rate)+ph); signal=amp*oscillator
            pan=.5+.42*np.sin(.754877666*(k+1)); stereo[:,0]+=signal*np.cos(.5*np.pi*pan); stereo[:,1]+=signal*np.sin(.5*np.pi*pan)
        outputs.append(stereo)
    audio=np.stack(outputs,axis=0)
    onset_samples=min(n,max(1,int(onset_fade_seconds*sample_rate))); tail_samples=min(n,max(1,int(tail_fade_seconds*sample_rate)))
    onset=np.sin(.5*np.pi*np.linspace(0,1,onset_samples))**2; tail=np.cos(.5*np.pi*np.linspace(0,1,tail_samples))**2
    audio[:,:onset_samples,:]*=onset[None,:,None]; audio[:,-tail_samples:,:]*=tail[None,:,None]
    peak=max(float(np.max(np.abs(audio))),1e-12); audio=.9*audio/peak
    frame_edges=np.linspace(0,n,len(frame_t)+1,dtype=int); divergence=[]
    for a,b in zip(frame_edges[:-1],frame_edges[1:]): divergence.append(float(np.sqrt(np.mean((audio[1,a:b]-audio[0,a:b])**2))))
    return audio.astype(np.float32),{"sample_rate":sample_rate,"duration_seconds":duration_seconds,"onset_fade_seconds":onset_fade_seconds,"tail_fade_seconds":tail_fade_seconds,"voice_envelopes":"continuous_no_frame_retrigger","shared_normalization_peak":peak,"population_complex_rms_divergence":divergence}


def export_modal_mixture(frames: ModalMixtureFrames, audio: np.ndarray, diagnostics: dict, output: str | Path, *, reconstruct_ir: bool = False, ir_compatible: bool = False) -> dict[str,Path]:
    import soundfile as sf
    output=Path(output); output.mkdir(parents=True,exist_ok=True); names=("population_modal","complex_amplitude_modal","dominant_world_modal")
    paths={}
    for i,name in enumerate(names): paths[name]=output/f"{name}.wav"; sf.write(paths[name],audio[i],diagnostics["sample_rate"],subtype="FLOAT")
    paths["comparison_6ch"]=output/"comparison_population_complex_dominant_6ch.wav"; sf.write(paths["comparison_6ch"],np.concatenate(tuple(audio),axis=1),diagnostics["sample_rate"],subtype="FLOAT")
    if reconstruct_ir and not ir_compatible:
        raise ValueError("time-varying IR reconstruction requested without passing modal compatibility checks")
    if reconstruct_ir:
        paths["time_varying_modal_ir"]=output/"time_varying_modal_ir_complex.wav"; sf.write(paths["time_varying_modal_ir"],audio[1],diagnostics["sample_rate"],subtype="FLOAT")
    paths["modal_frames"]=output/"modal_lineage_frames.npz"; np.savez_compressed(paths["modal_frames"],**{name:getattr(frames,name) for name in frames.__dataclass_fields__})
    paths["diagnostics"]=output/"modal_mix_diagnostics.json"; paths["diagnostics"].write_text(json.dumps({"schema":"qmw.quantum_geometry.modal_mix.v1",**diagnostics,"outputs":{k:str(v) for k,v in paths.items() if k!="diagnostics"}},indent=2)+"\n")
    return paths
