#!/usr/bin/env python3
"""Robustness sweep for geometry-conditioned relational dynamics."""
from __future__ import annotations
import argparse,csv,json,sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from quantum_geometry.geometry_conditioned_dynamics import GeometryConditionedConfig,geometry_conditioned_history


def summarize(history):
    distance=np.sqrt(np.maximum(0,1-history.step_fidelities)); speed=np.sum(np.abs(np.diff(history.weights,axis=0)),axis=1); participation=1/np.sum(history.weights**2,axis=1); dominant=np.argmax(history.weights,axis=1)
    compressed=[int(dominant[0])]
    for value in dominant[1:]:
        if int(value)!=compressed[-1]: compressed.append(int(value))
    return {"trace_distance_mean":float(distance.mean()),"trace_distance_std":float(distance.std()),"trace_distance_cv":float(distance.std()/max(distance.mean(),1e-12)),"trace_distance_min":float(distance.min()),"trace_distance_max":float(distance.max()),"maximum_geometric_speed":float(speed.max()),"final_participation":float(participation[-1]),"minimum_participation":float(participation.min()),"maximum_participation":float(participation.max()),"maximum_hamiltonian_change":float(np.max(history.hamiltonian_change_norms)),"maximum_norm_error":float(np.max(np.abs(np.linalg.norm(history.states,axis=1)-1))),"dominant_path":"-".join(map(str,compressed)),"mediated_15_14_13":compressed==[15,14,13]}


def write_csv(path,rows):
    with path.open("w",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)


def heatmaps(rows,output):
    import matplotlib; matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    population=sorted(set(r["population_strength"] for r in rows)); coherence=sorted(set(r["coherence_strength"] for r in rows)); dts=sorted(set(r["dt"] for r in rows))
    fig,axes=plt.subplots(len(dts),3,figsize=(12,3*len(dts)),constrained_layout=True)
    for row,dt in zip(axes,dts):
        subset=[r for r in rows if r["dt"]==dt]
        grids=[]
        for key in ("trace_distance_cv","final_participation","maximum_geometric_speed"):
            grids.append(np.array([[next(r[key] for r in subset if r["population_strength"]==p and r["coherence_strength"]==c) for c in coherence] for p in population]))
        for ax,grid,title in zip(row,grids,("Hilbert-step CV","Final participation","Max geometry speed")):
            im=ax.imshow(grid,origin="lower",aspect="auto",extent=[min(coherence),max(coherence),min(population),max(population)],cmap="viridis"); fig.colorbar(im,ax=ax); ax.set(title=f"{title}, dt={dt}",xlabel="coherence strength",ylabel="population strength")
    path=output/"conditioned_sweep_heatmaps.png"; fig.savefig(path,dpi=160); plt.close(fig); return path


def main():
    p=argparse.ArgumentParser(); p.add_argument("--benchmark",type=Path,default=ROOT/"outputs"/"quantum_geometry16_real_v1"/"real"); p.add_argument("--output",type=Path,default=ROOT/"outputs"/"quantum_geometry16_conditioned_sweep_v1"); args=p.parse_args()
    z=np.load(args.benchmark/"benchmark_core.npz"); L=z["L_config"]; A=z["adjacency"]; psi=z["constraint_state"]; potential=np.linspace(-.45,.45,16)+.08*np.sin(2*np.pi*np.arange(16)/16); base=.2*L+np.diag(potential)
    populations=(0,.3,.6,.9,1.2); coherences=(0,.25,.5,.7,1.0); dts=(.15,.25,.35,.5); horizon=5.25; rows=[]
    for dt in dts:
        steps=int(round(horizon/dt))+1
        for pop in populations:
            for coh in coherences:
                cfg=GeometryConditionedConfig(population_strength=pop,coherence_strength=coh,substeps=4); h=geometry_conditioned_history(psi,base,A,potential,steps=steps,dt=dt,config=cfg)
                rows.append({"population_strength":pop,"coherence_strength":coh,"dt":dt,"steps":steps,"actual_horizon":float((steps-1)*dt),**summarize(h)})
    convergence=[]
    reference=None
    for substeps in (1,2,4,8,16):
        cfg=GeometryConditionedConfig(substeps=substeps); h=geometry_conditioned_history(psi,base,A,potential,steps=16,dt=.35,config=cfg); summary=summarize(h)
        if substeps==16: reference=h.states[-1]
        convergence.append({"substeps":substeps,**summary,"final_state":h.states[-1]})
    for row in convergence:
        row["final_state_distance_to_substeps16"]=float(np.sqrt(max(0,1-abs(np.vdot(reference,row.pop("final_state")))**2)))
    nontrivial=[r for r in rows if r["population_strength"]>0 and r["coherence_strength"]>0]
    cvs=np.array([r["trace_distance_cv"] for r in nontrivial]); mediated=sum(r["mediated_15_14_13"] for r in nontrivial)
    report={"schema":"qmw.quantum_geometry.conditioned_sweep.v1","fixed_physical_horizon":horizon,"population_strengths":list(populations),"coherence_strengths":list(coherences),"timesteps":list(dts),"grid_count":len(rows),"nontrivial_summary":{"cv_min":float(cvs.min()),"cv_median":float(np.median(cvs)),"cv_max":float(cvs.max()),"fraction_cv_above_0_05":float(np.mean(cvs>.05)),"fraction_cv_above_0_10":float(np.mean(cvs>.10)),"mediated_path_fraction":mediated/len(nontrivial),"maximum_norm_error":max(r["maximum_norm_error"] for r in nontrivial)},"baseline_full":next(r for r in rows if r["population_strength"]==.9 and r["coherence_strength"]==.7 and r["dt"]==.35),"convergence":convergence,"grw_enabled":False,"conductor_registered":False,"audio_rendered":False}
    args.output.mkdir(parents=True,exist_ok=True); write_csv(args.output/"conditioned_sweep.csv",rows); (args.output/"conditioned_sweep.json").write_text(json.dumps({"report":report,"rows":rows},indent=2)+"\n"); heatmap=heatmaps(rows,args.output); report["heatmap"]=str(heatmap); (args.output/"conditioned_sweep_report.json").write_text(json.dumps(report,indent=2)+"\n"); print(json.dumps(report,indent=2))


if __name__=="__main__": main()
