#!/usr/bin/env python3
"""Generate 16 real Living Spectral worlds and compare them with the synthetic control."""
from __future__ import annotations
import argparse, json, sys
from dataclasses import asdict, replace
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from geometry_acoustics_bridge_v2.geometry_acoustics_bridge_v2 import AcousticBridgeConfig
from operators.living_spectral_geometry_v1 import LivingSpectralConfig,LivingSpectralGeometry,height_field_to_mesh
from operators.spectral_geometry_v1 import SpectralGeometryConfig
from quantum_eigenfield_engine_v1 import QuantumEigenfieldConfig
from surface_material_models_v1 import SurfaceMaterialConfig
from quantum_geometry import ConfigurationGraph,GraphDensityBridge,GeometryState,build_constraint,build_geometry_field,conditional_history,export_geometry_field,generate_geometry16,solve_constraint
from quantum_geometry.adapters import export_artifact_sequence

FAMILY_WEIGHTS={"spectrum":0.30,"modal":0.25,"material":0.15,"geometry":0.15,"ir":0.15}


def surfaces(size=20):
    q=np.linspace(-1,1,size); x,y=np.meshgrid(q,q,indexing="xy"); r=np.sqrt(x*x+y*y); theta=np.arctan2(y,x)
    bases=[0.28*np.sin(np.pi*x)*np.cos(np.pi*y),0.35*np.exp(-2.2*r*r)*np.cos(3*theta),0.24*(x*x-y*y),0.18*(np.sin(2*np.pi*x)+np.sin(2*np.pi*y))]
    out=[]
    for family,z in enumerate(bases):
        for variant in range(4):
            ripple=(0.012+0.006*variant)*np.sin((variant+1)*np.pi*x)*np.sin((family+1)*np.pi*y)
            out.append((family,variant,z*(0.82+0.12*variant)+ripple))
    return out


def material_changes(index):
    model=("surface_laplacian","tensioned_membrane","elastic_shell","bioelectric_surface")[index%4]
    return dict(model=model,effective_wave_speed=90+12*index,surface_tension=.65+.18*(index%4),surface_density=.8+.12*(index//4),bending_stiffness=.015*(index%4),damping_base=1.15+.13*index,damping_frequency_tilt=.15+.08*(index%4),conductivity_base=.7+.14*(index//4),leakage_base=.008+.004*(index%4))


def generate_living_worlds(root: Path) -> list[Path]:
    root.mkdir(parents=True,exist_ok=True); worlds=surfaces(); _,_,h0=worlds[0]; vertices,faces=height_field_to_mesh(h0,2.0/(h0.shape[0]-1))
    config=LivingSpectralConfig(spectral=SpectralGeometryConfig(n_modes=16),material=SurfaceMaterialConfig(n_modes=16),quantum=QuantumEigenfieldConfig(n_geometric_modes=16),acoustic=AcousticBridgeConfig(sample_rate=16000,duration_seconds=2.0,minimum_duration_seconds=.5))
    paths=[]
    with LivingSpectralGeometry(vertices,faces,root,config=config) as living:
        for index,(family,variant,height) in enumerate(worlds):
            vertices,faces=height_field_to_mesh(height,2.0/(height.shape[0]-1))
            living.update_geometry(vertices,faces,schedule=False,reason=f"real world g{index:02d} geometry family {family} variant {variant}")
            living.update_material(schedule=False,reason=f"real world g{index:02d} material",**material_changes(index))
            state=living.recompute_now(f"quantum geometry real world g{index:02d}")
            paths.append(Path(state.paths["directory"])/"state.json")
    return paths


def benchmark(states, graph, output: Path, label: str):
    potential=np.linspace(-.45,.45,16)+.08*np.sin(2*np.pi*np.arange(16)/16); matter=np.diag(.05*np.cos(2*np.pi*np.arange(16)/8))
    raw=build_constraint(graph.laplacian,alpha=.32,geometry_potential=potential,matter_hamiltonian=matter)
    eig=np.linalg.eigvalsh(raw); offset=float(eig[np.argmin(np.abs(eig))]); constraint=raw-offset*np.eye(16)
    solution=solve_constraint(constraint); rho=GraphDensityBridge.from_state(solution.state)
    history=conditional_history(solution.state,.2*graph.laplacian+np.diag(potential),steps=16,dt=.35)
    frames=build_geometry_field(history.times,history.weights,states,amplitudes=history.states,laplacian=graph.laplacian)
    output.mkdir(parents=True,exist_ok=True); field=export_geometry_field(frames,states,output/"geometry_field")
    export_artifact_sequence(frames,states,output/"living_ir_sequence.json")
    le=np.linalg.eigvalsh(graph.laplacian); participation=1/np.sum(history.weights**2,axis=1); speed=np.r_[0,np.sum(np.abs(np.diff(history.weights,axis=0)),axis=1)]
    dominant=np.argmax(history.weights,axis=1); changes=np.flatnonzero(np.r_[True,dominant[1:]!=dominant[:-1]])
    runs=[]
    for n,start in enumerate(changes):
        end=changes[n+1] if n+1<len(changes) else len(dominant); runs.append({"world":states[int(dominant[start])].id,"start":int(start),"length":int(end-start)})
    report={"schema":"qmw.quantum_geometry.benchmark.v2","label":label,"laplacian_spectrum":le.tolist(),"spectral_gap":float(le[1]),"near_zero_count":int(np.sum(le<max(1e-10,.1*le[1]))),"constraint_residual_norm":solution.residual_norm,"backend":solution.backend,"dominant_sequence":[states[int(i)].id for i in dominant],"dominant_runs":runs,"participation":participation.tolist(),"probability_speed_l1":speed.tolist(),"slow_steps":np.argsort(speed[1:])[:4].astype(int).tolist(),"dirichlet_energy":[f.dirichlet_energy for f in frames],"probability_dirichlet_energy":[f.probability_dirichlet_energy for f in frames],"family_weights":dict(graph.family_weights),"field_json":str(field["json"])}
    np.savez_compressed(output/"benchmark_core.npz",distances=graph.distances,adjacency=graph.adjacency,L_config=graph.laplacian,constraint=constraint,constraint_state=solution.state,rho=rho,conditional_states=history.states,geometry_weights=history.weights,dirichlet_energy=np.array(report["dirichlet_energy"]),probability_dirichlet_energy=np.array(report["probability_dirichlet_energy"]),**{f"distance2_{k}":v for k,v in graph.family_distance_squared.items()})
    (output/"benchmark_report.json").write_text(json.dumps(report,indent=2)+"\n"); return report


def main():
    p=argparse.ArgumentParser(); p.add_argument("--output",type=Path,default=ROOT/"outputs"/"quantum_geometry16_real_v1"); p.add_argument("--reuse",action="store_true"); args=p.parse_args()
    manifest=args.output/"living_worlds.json"
    if args.reuse and manifest.exists(): paths=[Path(x) for x in json.loads(manifest.read_text())["state_paths"]]
    else:
        paths=generate_living_worlds(args.output/"living_worlds"); args.output.mkdir(parents=True,exist_ok=True); manifest.write_text(json.dumps({"schema":"qmw.quantum_geometry.real_worlds.v1","state_paths":[str(x) for x in paths]},indent=2)+"\n")
    real_states=tuple(GeometryState.from_living_state(x,state_id=f"g{i:02d}") for i,x in enumerate(paths))
    real_graph=ConfigurationGraph.build_interpretable(real_states,family_weights=FAMILY_WEIGHTS,neighbors=4)
    control_states=generate_geometry16(); control_graph=ConfigurationGraph.build(control_states,neighbors=4)
    real=benchmark(real_states,real_graph,args.output/"real","real_living_spectral_geometry")
    control=benchmark(control_states,control_graph,args.output/"control","synthetic_control")
    comparison={"schema":"qmw.quantum_geometry.real_vs_control.v1","real":real,"control":control,"registration":"withheld","grw_enabled":False,"acoustic_rendering_enabled":False}
    (args.output/"comparison_report.json").write_text(json.dumps(comparison,indent=2)+"\n"); print(json.dumps({"output":str(args.output),"real_spectral_gap":real["spectral_gap"],"control_spectral_gap":control["spectral_gap"],"real_residual":real["constraint_residual_norm"],"real_dominant_runs":real["dominant_runs"],"real_participation_range":[min(real["participation"]),max(real["participation"])],"real_dirichlet_range":[min(real["dirichlet_energy"]),max(real["dirichlet_energy"])]},indent=2))


if __name__=="__main__": main()
