"""Geometry-weight frames and auditable mixtures of artifact descriptors."""
from __future__ import annotations
from dataclasses import dataclass
import json
from pathlib import Path
import numpy as np
from .configuration_graph import GeometryState


@dataclass(frozen=True)
class GeometryFieldFrame:
    relational_time: float
    weights: np.ndarray
    dominant_geometry: str
    entropy_bits: float
    dirichlet_energy: float = 0.0
    probability_dirichlet_energy: float = 0.0


def dirichlet_energy(state: np.ndarray, laplacian: np.ndarray) -> float:
    state=np.asarray(state,dtype=np.complex128).reshape(-1); laplacian=np.asarray(laplacian,dtype=np.complex128)
    return float(np.vdot(state,laplacian@state).real)


def build_geometry_field(times, weights, states, *, amplitudes=None, laplacian=None) -> tuple[GeometryFieldFrame,...]:
    states=tuple(states); w=np.asarray(weights,dtype=float)
    if w.ndim != 2 or w.shape[1] != len(states): raise ValueError("one weight per geometry is required")
    out=[]
    for t,row in zip(times,w):
        row=np.maximum(row,0); row=row/row.sum(); nz=row[row>0]
        amp_energy=dirichlet_energy(amplitudes[len(out)],laplacian) if amplitudes is not None and laplacian is not None else 0.0
        probability_energy=dirichlet_energy(np.sqrt(row),laplacian) if laplacian is not None else 0.0
        out.append(GeometryFieldFrame(float(t),row,states[int(np.argmax(row))].id,float(-np.sum(nz*np.log2(nz))),amp_energy,probability_energy))
    return tuple(out)


def export_geometry_field(frames, states, output_prefix: str | Path) -> dict[str,Path]:
    prefix=Path(output_prefix); prefix.parent.mkdir(parents=True,exist_ok=True)
    npz=prefix.with_suffix(".npz"); js=prefix.with_suffix(".json")
    weights=np.stack([f.weights for f in frames]); times=np.array([f.relational_time for f in frames])
    np.savez_compressed(npz,times=times,geometry_weights=weights,geometry_ids=np.array([s.id for s in states]),dominant_indices=np.argmax(weights,axis=1),dirichlet_energy=np.array([f.dirichlet_energy for f in frames]),probability_dirichlet_energy=np.array([f.probability_dirichlet_energy for f in frames]))
    js.write_text(json.dumps({"schema":"qmw.quantum_geometry.field.v1","geometry_ids":[s.id for s in states],"frames":[{"relational_time":f.relational_time,"weights":f.weights.tolist(),"dominant_geometry":f.dominant_geometry,"entropy_bits":f.entropy_bits,"dirichlet_energy":f.dirichlet_energy,"probability_dirichlet_energy":f.probability_dirichlet_energy} for f in frames]},indent=2)+"\n")
    return {"npz":npz,"json":js}
