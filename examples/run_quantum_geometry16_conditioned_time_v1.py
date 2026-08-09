#!/usr/bin/env python3
"""Compare fixed-generator and causal geometry-conditioned relational motion."""
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from quantum_geometry import conditional_history,dirichlet_energy
from quantum_geometry.geometry_conditioned_dynamics import GeometryConditionedConfig,geometry_conditioned_history


def metrics(states,weights,L):
    fidelity=np.abs(np.sum(states[:-1].conj()*states[1:],axis=1))**2; distance=np.sqrt(np.maximum(0,1-fidelity)); speed=np.sum(np.abs(np.diff(weights,axis=0)),axis=1); participation=1/np.sum(weights*weights,axis=1); energy=np.array([dirichlet_energy(s,L) for s in states])
    return {"step_fidelity":fidelity.tolist(),"relational_trace_distance":distance.tolist(),"trace_distance_mean":float(distance.mean()),"trace_distance_std":float(distance.std()),"trace_distance_cv":float(distance.std()/max(distance.mean(),1e-12)),"geometric_speed_l1":speed.tolist(),"participation":participation.tolist(),"dirichlet_energy":energy.tolist(),"dominant_indices":np.argmax(weights,axis=1).astype(int).tolist()}


def main():
    p=argparse.ArgumentParser(); p.add_argument("--benchmark",type=Path,default=ROOT/"outputs"/"quantum_geometry16_real_v1"/"real"); p.add_argument("--output",type=Path,default=ROOT/"outputs"/"quantum_geometry16_conditioned_time_v1"); args=p.parse_args()
    z=np.load(args.benchmark/"benchmark_core.npz"); L=z["L_config"]; A=z["adjacency"]; psi0=z["constraint_state"]
    potential=np.linspace(-.45,.45,16)+.08*np.sin(2*np.pi*np.arange(16)/16); base=.2*L+np.diag(potential); cfg=GeometryConditionedConfig()
    fixed=conditional_history(psi0,base,steps=16,dt=.35); conditioned=geometry_conditioned_history(psi0,base,A,potential,steps=16,dt=.35,config=cfg)
    fm=metrics(fixed.states,fixed.weights,L); cm=metrics(conditioned.states,conditioned.weights,L)
    args.output.mkdir(parents=True,exist_ok=True); np.savez_compressed(args.output/"conditioned_time_core.npz",fixed_states=fixed.states,fixed_weights=fixed.weights,conditioned_states=conditioned.states,conditioned_weights=conditioned.weights,effective_hamiltonians=conditioned.effective_hamiltonians,hamiltonian_change_norms=conditioned.hamiltonian_change_norms,L_config=L,adjacency=A)
    ablation_configs={"scaled_fixed":GeometryConditionedConfig(population_strength=0,coherence_strength=0),"population_only":GeometryConditionedConfig(population_strength=.9,coherence_strength=0),"coherence_only":GeometryConditionedConfig(population_strength=0,coherence_strength=.7),"full":cfg}
    ablations={}
    for name,ablation_cfg in ablation_configs.items():
        h=geometry_conditioned_history(psi0,base,A,potential,steps=16,dt=.35,config=ablation_cfg); m=metrics(h.states,h.weights,L)
        ablations[name]={"config":ablation_cfg.__dict__,"trace_distance_mean":m["trace_distance_mean"],"trace_distance_std":m["trace_distance_std"],"trace_distance_cv":m["trace_distance_cv"],"maximum_hamiltonian_change":float(np.max(h.hamiltonian_change_norms)),"maximum_geometric_speed":float(np.max(m["geometric_speed_l1"])),"final_participation":float(m["participation"][-1])}
    report={"schema":"qmw.quantum_geometry.conditioned_time.v1","interpretation":"causal nonlinear mean-field feedback; not yet a strict stationary Page-Wootters constraint","config":cfg.__dict__,"fixed":fm,"conditioned":cm,"ablations":ablations,"hilbert_step_nonuniformity_ratio":cm["trace_distance_cv"]/max(fm["trace_distance_cv"],1e-15),"hamiltonian_change_norms":conditioned.hamiltonian_change_norms.tolist(),"grw_enabled":False,"epistrophe_enabled":False,"conductor_registered":False,"audio_rendered":False}
    (args.output/"conditioned_time_report.json").write_text(json.dumps(report,indent=2)+"\n"); print(json.dumps({"output":str(args.output),"fixed_trace_distance_std":fm["trace_distance_std"],"conditioned_trace_distance_std":cm["trace_distance_std"],"conditioned_trace_distance_cv":cm["trace_distance_cv"],"fixed_dominant":fm["dominant_indices"],"conditioned_dominant":cm["dominant_indices"],"hamiltonian_change_range":[min(conditioned.hamiltonian_change_norms),max(conditioned.hamiltonian_change_norms)]},indent=2))


if __name__=="__main__": main()
