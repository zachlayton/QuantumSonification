#!/usr/bin/env python3
"""Render population, phase-aware, and winner-only versions of the real benchmark."""
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from quantum_geometry.modal_geometry_mixer import export_modal_mixture,load_modal_world,mix_modal_lineages,synthesize_modal_comparison,validate_lineage_compatibility


def main():
    p=argparse.ArgumentParser(); p.add_argument("--benchmark",type=Path,default=ROOT/"outputs"/"quantum_geometry16_real_v1"); p.add_argument("--output",type=Path,default=ROOT/"outputs"/"quantum_geometry16_modal_mix_v1"); p.add_argument("--duration",type=float,default=32.0); p.add_argument("--sample-rate",type=int,default=24000); p.add_argument("--reconstruct-ir",action="store_true",help="also export the compatible time-varying modal reconstruction (off by default)"); args=p.parse_args()
    manifest=json.loads((args.benchmark/"living_worlds.json").read_text()); state_paths=[Path(x) for x in manifest["state_paths"]]
    worlds=tuple(load_modal_world(x,f"g{i:02d}") for i,x in enumerate(state_paths)); compatibility=validate_lineage_compatibility(worlds); core=np.load(args.benchmark/"real"/"benchmark_core.npz"); states=core["conditional_states"]
    frames=mix_modal_lineages(states,worlds); audio,diagnostics=synthesize_modal_comparison(frames,duration_seconds=args.duration,sample_rate=args.sample_rate)
    energy=np.asarray(core["dirichlet_energy"]); probability_energy=np.asarray(core["probability_dirichlet_energy"]); weights=np.asarray(core["geometry_weights"]); participation=1/np.sum(weights*weights,axis=1); geometric_speed=np.r_[0,np.sum(np.abs(np.diff(weights,axis=0)),axis=1)]
    fidelity=np.r_[1,np.abs(np.sum(states[:-1].conj()*states[1:],axis=1))**2]; relational_distance=np.sqrt(np.maximum(0,1-fidelity))
    divergence=np.asarray(diagnostics["population_complex_rms_divergence"]); pop=frames.population_strength; coh=frames.complex_strength
    pop_shape=pop/np.maximum(np.linalg.norm(pop,axis=1,keepdims=True),1e-12); coh_shape=coh/np.maximum(np.linalg.norm(coh,axis=1,keepdims=True),1e-12)
    shape_divergence=np.linalg.norm(pop_shape-coh_shape,axis=1); gain_ratio=np.linalg.norm(coh,axis=1)/np.maximum(np.linalg.norm(pop,axis=1),1e-12)
    cancellation=1-np.sum(coh,axis=1)/np.maximum(np.sum(np.sqrt(np.maximum(pop,0)),axis=1),1e-12)
    diagnostics.update({"grw_enabled":False,"conductor_registered":False,"ir_reconstruction_enabled":args.reconstruct_ir,"modal_compatibility":compatibility,"lineage_count":int(len(frames.lineage_ids)),"participation":participation.tolist(),"amplitude_dirichlet_energy":energy.tolist(),"probability_dirichlet_energy":probability_energy.tolist(),"geometry_weights":weights.tolist(),"geometric_speed_l1":geometric_speed.tolist(),"relational_trace_distance":relational_distance.tolist(),"dirichlet_difference":(energy-probability_energy).tolist(),"modal_shape_divergence":shape_divergence.tolist(),"complex_population_gain_ratio":gain_ratio.tolist(),"coherent_cancellation_index":cancellation.tolist(),"divergence_correlation_with_amplitude_dirichlet":float(np.corrcoef(divergence,energy)[0,1]),"shape_divergence_correlation_with_amplitude_dirichlet":float(np.corrcoef(shape_divergence,energy)[0,1]),"cancellation_correlation_with_amplitude_dirichlet":float(np.corrcoef(cancellation,energy)[0,1])})
    paths=export_modal_mixture(frames,audio,diagnostics,args.output,reconstruct_ir=args.reconstruct_ir,ir_compatible=compatibility["compatible"])
    np.savez_compressed(args.output/"trajectory_timeseries.npz",participation=participation,amplitude_dirichlet_energy=energy,probability_dirichlet_energy=probability_energy,geometry_weights=weights,lineage_ids=frames.lineage_ids,population_lineage_weights=frames.population_strength,complex_lineage_weights=frames.complex_strength,complex_lineage_phases=frames.complex_phase,dominant_lineage_weights=frames.dominant_strength)
    report={"schema":"qmw.quantum_geometry.modal_mix.report.v1","source_benchmark":str(args.benchmark/"real"),"render_paths":{"population":str(paths["population_modal"]),"complex_amplitude":str(paths["complex_amplitude_modal"]),"dominant_world":str(paths["dominant_world_modal"])},"lineage_compatibility":compatibility,"ir_reconstruction":"enabled" if args.reconstruct_ir else "disabled_by_default","population_complex_audio_rms":float(np.sqrt(np.mean((audio[1]-audio[0])**2))),"participation_range":[float(participation.min()),float(participation.max())],"amplitude_dirichlet_range":[float(energy.min()),float(energy.max())],"probability_dirichlet_range":[float(probability_energy.min()),float(probability_energy.max())],"grw_enabled":False,"conductor_registered":False}
    (args.output/"comparison_report.json").write_text(json.dumps(report,indent=2)+"\n")
    (args.output/"COMPARISON.md").write_text("# Quantum Geometry 16 modal comparison\n\nAll three renders use the same validated real-geometry Page-Wootters trajectory. Population uses `p_i`; complex amplitude sums `c_i a_ik` within recorded Living modal lineages; dominant uses the maximum-population world.\n\n- Modal lineage compatibility: passed (%d lineages; %d persistent across all worlds)\n- Population/complex audio RMS difference: %.6f\n- Participation range: %.3f–%.3f worlds\n- IR reconstruction: %s\n- GRW: disabled\n- Conductor registration: disabled\n"%(compatibility["lineage_count"],compatibility["persistent_lineage_count"],report["population_complex_audio_rms"],participation.min(),participation.max(),report["ir_reconstruction"]))
    print(json.dumps(report,indent=2))


if __name__=="__main__": main()
