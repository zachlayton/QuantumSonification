#!/usr/bin/env python3
"""Hear fixed versus geometry-conditioned relational timing without GRW."""
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
import numpy as np
import soundfile as sf
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from quantum_geometry import conditional_history,dirichlet_energy
from quantum_geometry.geometry_conditioned_dynamics import GeometryConditionedConfig,geometry_conditioned_history
from quantum_geometry.modal_geometry_mixer import load_modal_world,mix_modal_lineages
from quantum_geometry.relational_time_renderer import relational_timing,shared_normalize,synthesize_continuous_modal


def trajectory_metrics(states,weights,L):
    participation=1/np.sum(weights*weights,axis=1); energy=np.array([dirichlet_energy(s,L) for s in states]); probability_energy=np.array([dirichlet_energy(np.sqrt(w),L) for w in weights]); speed=np.r_[0,np.sum(np.abs(np.diff(weights,axis=0)),axis=1)]
    return participation,energy,probability_energy,speed


def main():
    p=argparse.ArgumentParser(); p.add_argument("--benchmark-root",type=Path,default=ROOT/"outputs"/"quantum_geometry16_real_v1"); p.add_argument("--output",type=Path,default=ROOT/"outputs"/"quantum_geometry16_conditioned_audio_v1"); p.add_argument("--duration",type=float,default=32.0); p.add_argument("--sample-rate",type=int,default=24000); args=p.parse_args()
    manifest=json.loads((args.benchmark_root/"living_worlds.json").read_text()); worlds=tuple(load_modal_world(x,f"g{i:02d}") for i,x in enumerate(manifest["state_paths"])); z=np.load(args.benchmark_root/"real"/"benchmark_core.npz"); L=z["L_config"]; A=z["adjacency"]; psi=z["constraint_state"]
    potential=np.linspace(-.45,.45,16)+.08*np.sin(2*np.pi*np.arange(16)/16); base=.2*L+np.diag(potential)
    fixed=conditional_history(psi,base,steps=16,dt=.35); conditioned=geometry_conditioned_history(psi,base,A,potential,steps=16,dt=.35,config=GeometryConditionedConfig(substeps=16))
    ft=relational_timing(fixed.states,duration_seconds=args.duration); ct=relational_timing(conditioned.states,duration_seconds=args.duration); ff=mix_modal_lineages(fixed.states,worlds); cf=mix_modal_lineages(conditioned.states,worlds)
    signals=[synthesize_continuous_modal(ff,ft,route="population",sample_rate=args.sample_rate),synthesize_continuous_modal(ff,ft,route="complex",sample_rate=args.sample_rate),synthesize_continuous_modal(cf,ct,route="population",sample_rate=args.sample_rate),synthesize_continuous_modal(cf,ct,route="complex",sample_rate=args.sample_rate)]; signals=shared_normalize(*signals)
    args.output.mkdir(parents=True,exist_ok=True); names=("fixed_population","fixed_complex","conditioned_population","conditioned_complex"); paths={}
    for name,signal in zip(names,signals): paths[name]=args.output/f"{name}.wav"; sf.write(paths[name],signal,args.sample_rate,subtype="FLOAT")
    paths["complex_comparison_4ch"]=args.output/"fixed_vs_conditioned_complex_4ch.wav"; sf.write(paths["complex_comparison_4ch"],np.concatenate((signals[1],signals[3]),axis=1),args.sample_rate,subtype="FLOAT")
    fp,fe,fpe,fs=trajectory_metrics(fixed.states,fixed.weights,L); cp,ce,cpe,cs=trajectory_metrics(conditioned.states,conditioned.weights,L)
    npz=args.output/"conditioned_audio_trajectories.npz"; np.savez_compressed(npz,fixed_states=fixed.states,fixed_weights=fixed.weights,fixed_frame_times=ft.frame_times_seconds,fixed_intervals=ft.interval_seconds,fixed_trace_distances=ft.trace_distances,fixed_participation=fp,fixed_dirichlet_energy=fe,fixed_probability_dirichlet_energy=fpe,fixed_geometric_speed=fs,conditioned_states=conditioned.states,conditioned_weights=conditioned.weights,conditioned_frame_times=ct.frame_times_seconds,conditioned_intervals=ct.interval_seconds,conditioned_trace_distances=ct.trace_distances,conditioned_participation=cp,conditioned_dirichlet_energy=ce,conditioned_probability_dirichlet_energy=cpe,conditioned_geometric_speed=cs,fixed_population_lineage_weights=ff.population_strength,fixed_complex_lineage_weights=ff.complex_strength,conditioned_population_lineage_weights=cf.population_strength,conditioned_complex_lineage_weights=cf.complex_strength,lineage_ids=ff.lineage_ids)
    report={"schema":"qmw.quantum_geometry.conditioned_audio.v1","timing_rule":"interval proportional to inverse relational trace distance, accumulated and normalized to common duration","conditioned_substeps":16,"fixed_intervals_seconds":ft.interval_seconds.tolist(),"conditioned_intervals_seconds":ct.interval_seconds.tolist(),"fixed_trace_distances":ft.trace_distances.tolist(),"conditioned_trace_distances":ct.trace_distances.tolist(),"fixed_participation":fp.tolist(),"conditioned_participation":cp.tolist(),"fixed_dirichlet_energy":fe.tolist(),"conditioned_dirichlet_energy":ce.tolist(),"fixed_probability_dirichlet_energy":fpe.tolist(),"conditioned_probability_dirichlet_energy":cpe.tolist(),"fixed_geometric_speed":fs.tolist(),"conditioned_geometric_speed":cs.tolist(),"outputs":{**{k:str(v) for k,v in paths.items()},"trajectory_npz":str(npz)},"grw_enabled":False,"conductor_registered":False,"continuous_resonators":True}
    (args.output/"conditioned_audio_report.json").write_text(json.dumps(report,indent=2)+"\n"); print(json.dumps({"output":str(args.output),"fixed_interval_range":[float(ft.interval_seconds.min()),float(ft.interval_seconds.max())],"conditioned_interval_range":[float(ct.interval_seconds.min()),float(ct.interval_seconds.max())],"conditioned_trace_distance_range":[float(ct.trace_distances.min()),float(ct.trace_distances.max())],"conditioned_substeps":16,"files":report["outputs"]},indent=2))


if __name__=="__main__": main()
