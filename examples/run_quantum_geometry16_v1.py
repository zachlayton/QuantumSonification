#!/usr/bin/env python3
"""Run the standalone 4-qubit / 16-whole-geometry validation path."""
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from quantum_geometry import ConfigurationGraph,GraphDensityBridge,build_constraint,build_geometry_field,conditional_history,export_geometry_field,generate_geometry16,solve_constraint
from quantum_geometry.adapters.living_geometry_adapter import export_artifact_sequence,load_living_geometry_states


def main():
    p=argparse.ArgumentParser(); p.add_argument("--living-state",action="append",default=[],help="Repeat exactly 16 times to use existing Living Spectral state.json artifacts")
    p.add_argument("--output",type=Path,default=ROOT/"outputs"/"quantum_geometry16_v1"); p.add_argument("--steps",type=int,default=16); args=p.parse_args()
    if args.living_state and len(args.living_state)!=16: p.error("--living-state must be omitted or supplied exactly 16 times")
    states=load_living_geometry_states(args.living_state) if args.living_state else generate_geometry16()
    graph=ConfigurationGraph.build(states,neighbors=4); graph_rho=GraphDensityBridge.encode(graph.laplacian)
    potential=np.linspace(-.45,.45,16)+.08*np.sin(2*np.pi*np.arange(16)/16); matter=np.diag(.05*np.cos(2*np.pi*np.arange(16)/8))
    raw=build_constraint(graph.laplacian,alpha=.32,geometry_potential=potential,matter_hamiltonian=matter)
    eig=np.linalg.eigvalsh(raw); offset=float(eig[np.argmin(np.abs(eig))]); constraint=raw-offset*np.eye(16)
    solution=solve_constraint(constraint); rho=GraphDensityBridge.from_state(solution.state)
    generator=.2*graph.laplacian+np.diag(potential); history=conditional_history(solution.state,generator,steps=args.steps,dt=.35)
    frames=build_geometry_field(history.times,history.weights,states); args.output.mkdir(parents=True,exist_ok=True)
    field_paths=export_geometry_field(frames,states,args.output/"geometry_field")
    living_path=export_artifact_sequence(frames,states,args.output/"living_ir_sequence.json")
    np.savez_compressed(args.output/"quantum_geometry16_core.npz",distances=graph.distances,adjacency=graph.adjacency,L_config=graph.laplacian,constraint=constraint,constraint_state=solution.state,rho=rho,graph_rho=graph_rho,conditional_states=history.states,geometry_weights=history.weights)
    report={"schema":"qmw.quantum_geometry.validation.v1","dimension":16,"qubits":4,"geometry_source":"living" if args.living_state else "generated","backend":solution.backend,"constraint_eigenvalue":solution.eigenvalue,"constraint_residual_norm":solution.residual_norm,"constraint_expectation":solution.expectation,"clock_steps":args.steps,"weights_shape":list(history.weights.shape),"collapse_enabled":False,"outputs":{"core_npz":str(args.output/"quantum_geometry16_core.npz"),"field_npz":str(field_paths["npz"]),"field_json":str(field_paths["json"]),"living_sequence_json":str(living_path)}}
    (args.output/"validation_report.json").write_text(json.dumps(report,indent=2)+"\n"); print(json.dumps(report,indent=2))


if __name__=="__main__": main()
