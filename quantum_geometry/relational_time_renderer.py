"""Continuous modal rendering on accumulated state-derived relational time."""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np
from .modal_geometry_mixer import ModalMixtureFrames


@dataclass(frozen=True)
class RelationalTiming:
    frame_times_seconds: np.ndarray
    interval_seconds: np.ndarray
    trace_distances: np.ndarray


def relational_timing(states: np.ndarray, *, duration_seconds: float=32.0, inverse_power: float=.9, minimum_ratio: float=.55, maximum_ratio: float=1.8) -> RelationalTiming:
    states=np.asarray(states,dtype=np.complex128); fidelity=np.abs(np.sum(states[:-1].conj()*states[1:],axis=1))**2; distance=np.sqrt(np.maximum(0,1-fidelity))
    positive=distance[distance>1e-12]; reference=float(np.median(positive)) if len(positive) else 1.0
    raw=(reference/np.maximum(distance,1e-12))**inverse_power; raw=np.clip(raw,minimum_ratio,maximum_ratio); intervals=duration_seconds*raw/raw.sum(); frame_times=np.r_[0,np.cumsum(intervals)]
    return RelationalTiming(frame_times,intervals,distance)


def synthesize_continuous_modal(frames: ModalMixtureFrames, timing: RelationalTiming, *, route: str="complex", sample_rate: int=24000, onset_fade_seconds: float=.12, tail_fade_seconds: float=.12) -> np.ndarray:
    if route not in {"population","complex"}: raise ValueError("route must be population or complex")
    strengths=frames.population_strength if route=="population" else frames.complex_strength; frequencies=frames.population_frequency_hz if route=="population" else frames.complex_frequency_hz; phases=np.zeros_like(frames.complex_phase) if route=="population" else frames.complex_phase
    duration=float(timing.frame_times_seconds[-1]); n=max(2,int(round(duration*sample_rate))); sample_t=np.arange(n)/sample_rate; stereo=np.zeros((n,2),dtype=float)
    for k in range(len(frames.lineage_ids)):
        amp=np.interp(sample_t,timing.frame_times_seconds,strengths[:,k]); freq=np.interp(sample_t,timing.frame_times_seconds,frequencies[:,k]); phase_offset=np.interp(sample_t,timing.frame_times_seconds,np.unwrap(phases[:,k])); phase=np.cumsum(2*np.pi*freq/sample_rate)+phase_offset
        signal=amp*np.cos(phase); pan=.5+.42*np.sin(.754877666*(k+1)); stereo[:,0]+=signal*np.cos(.5*np.pi*pan); stereo[:,1]+=signal*np.sin(.5*np.pi*pan)
    onset=min(n,max(1,int(onset_fade_seconds*sample_rate))); tail=min(n,max(1,int(tail_fade_seconds*sample_rate))); stereo[:onset]*=(np.sin(.5*np.pi*np.linspace(0,1,onset))**2)[:,None]; stereo[-tail:]*=(np.cos(.5*np.pi*np.linspace(0,1,tail))**2)[:,None]
    return stereo.astype(np.float32)


def shared_normalize(*signals: np.ndarray, peak: float=.9) -> tuple[np.ndarray,...]:
    scale=max(max(float(np.max(np.abs(x))) for x in signals),1e-12)
    return tuple((peak*np.asarray(x)/scale).astype(np.float32) for x in signals)
