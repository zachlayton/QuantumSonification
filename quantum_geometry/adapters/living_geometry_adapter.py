"""Bridge conditional geometry weights to existing Living Spectral/IR artifacts."""
from __future__ import annotations
from pathlib import Path
from typing import Sequence
import json
import numpy as np
from ..configuration_graph import GeometryState


def load_living_geometry_states(paths: Sequence[str | Path]) -> tuple[GeometryState,...]:
    return tuple(GeometryState.from_living_state(p,state_id=f"g{i:02d}") for i,p in enumerate(paths))


def artifact_frame(weights: np.ndarray, states: Sequence[GeometryState]) -> dict:
    weights=np.asarray(weights,dtype=float); weights=np.maximum(weights,0); weights/=weights.sum()
    dominant=int(np.argmax(weights))
    return {"schema":"qmw.quantum_geometry.living_mix.v1","weights":weights.tolist(),"geometry_ids":[s.id for s in states],"dominant_index":dominant,"dominant_geometry":states[dominant].id,"dominant_ir_path":states[dominant].ir_path,"living_state_paths":[s.living_state_path for s in states]}


def export_artifact_sequence(frames, states: Sequence[GeometryState], path: str | Path) -> Path:
    path=Path(path); path.parent.mkdir(parents=True,exist_ok=True)
    payload={"schema":"qmw.quantum_geometry.living_sequence.v1","note":"Weights are explicit; downstream audio may select the dominant IR or crossfade compatible IRs.","frames":[{"relational_time":f.relational_time,**artifact_frame(f.weights,states)} for f in frames]}
    path.write_text(json.dumps(payload,indent=2)+"\n"); return path
