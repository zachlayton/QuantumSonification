"""Configuration-space graph whose vertices are complete candidate geometries."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping, Sequence
import json
import numpy as np


@dataclass(frozen=True)
class GeometryState:
    id: str
    descriptor: np.ndarray
    mesh_path: str | None = None
    spectral_eigenvalues: np.ndarray = field(default_factory=lambda: np.empty(0))
    modal_frequencies: np.ndarray = field(default_factory=lambda: np.empty(0))
    ir_path: str | None = None
    living_state_path: str | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)
    descriptor_families: Mapping[str, np.ndarray] = field(default_factory=dict)

    def __post_init__(self) -> None:
        d = np.asarray(self.descriptor, dtype=np.float64).reshape(-1)
        if not len(d) or not np.all(np.isfinite(d)):
            raise ValueError("descriptor must be a non-empty finite vector")
        object.__setattr__(self, "descriptor", d)
        object.__setattr__(self, "spectral_eigenvalues", np.asarray(self.spectral_eigenvalues, dtype=np.float64).reshape(-1))
        object.__setattr__(self, "modal_frequencies", np.asarray(self.modal_frequencies, dtype=np.float64).reshape(-1))
        object.__setattr__(self, "descriptor_families", {str(k): np.asarray(v, dtype=np.float64).reshape(-1) for k, v in self.descriptor_families.items()})

    @classmethod
    def from_living_state(cls, state_file: str | Path, *, state_id: str | None = None) -> "GeometryState":
        path = Path(state_file).resolve()
        data = json.loads(path.read_text())
        paths = data.get("paths", {})
        def resolve_artifact(value: str) -> Path:
            candidate=Path(value)
            if candidate.is_absolute(): return candidate
            if candidate.exists(): return candidate.resolve()
            return (path.parent/candidate).resolve()
        spectral_path = resolve_artifact(paths["spectral_npz"])
        with np.load(spectral_path) as z:
            eig = np.asarray(z["eigenvalues"], dtype=np.float64)
            freq = np.asarray(z["frequencies_hz"], dtype=np.float64)
            vertices = np.asarray(z["vertices"], dtype=np.float64)
            faces = np.asarray(z["faces"], dtype=np.int64)
        material_path = resolve_artifact(paths["material_json"])
        ir_json_path = resolve_artifact(paths["ir_json"])
        material = json.loads(material_path.read_text())
        ir = json.loads(ir_json_path.read_text())
        packet = material.get("packet", {}); config = material.get("config", {})
        decays = np.asarray(packet.get("decay_times_seconds", []), dtype=float)
        k = 12
        positive = np.maximum(eig[:k], 1e-12)
        spectrum = np.pad(np.log(positive), (0, max(0, k-len(positive))), constant_values=np.log(1e-12))
        logf = np.log(np.maximum(freq, 1e-12))
        modal = np.asarray([np.mean(logf), np.std(logf), np.min(logf), np.max(logf), np.mean(decays) if len(decays) else 0.0, np.std(decays) if len(decays) else 0.0])
        tri = vertices[faces]
        area = 0.5*np.linalg.norm(np.cross(tri[:,1]-tri[:,0], tri[:,2]-tri[:,0]), axis=1).sum()
        extent = np.ptp(vertices, axis=0); centered = vertices-np.mean(vertices,axis=0)
        geometry = np.r_[np.log1p(len(vertices)),np.log1p(len(faces)),np.log(np.maximum(extent,1e-12)),np.log(max(area,1e-12)),np.sqrt(np.mean(centered*centered,axis=0))]
        material_family = np.asarray([float(config.get(k,0.0)) for k in ("effective_wave_speed","surface_tension","surface_density","bending_stiffness","damping_base","damping_frequency_tilt","conductivity_base","leakage_base")])
        acoustics = ir.get("acoustics", {})
        ir_family = np.asarray([float(acoustics.get(k,0.0)) for k in ("frequency_min_hz","frequency_max_hz","t60_min_seconds","t60_max_seconds","direct_gain","duration_seconds","slowest_tail_level_db_at_end")])
        families={"spectrum":spectrum,"modal":modal,"material":material_family,"geometry":geometry,"ir":ir_family}
        descriptor=np.concatenate(tuple(families.values()))
        ir_path=str(resolve_artifact(paths["ir_wav"])) if paths.get("ir_wav") else None
        return cls(state_id or f"g_{path.parent.name}", descriptor, spectral_eigenvalues=eig, modal_frequencies=freq, ir_path=ir_path, living_state_path=str(path), metadata={"source": "living_spectral_geometry_v1", "material_model": data.get("material_model")}, descriptor_families=families)


@dataclass(frozen=True)
class ConfigurationGraph:
    states: tuple[GeometryState, ...]
    distances: np.ndarray
    adjacency: np.ndarray
    laplacian: np.ndarray
    family_distance_squared: Mapping[str, np.ndarray] = field(default_factory=dict)
    family_weights: Mapping[str, float] = field(default_factory=dict)

    @classmethod
    def build(cls, states: Sequence[GeometryState], *, neighbors: int = 4, sigma: float | None = None) -> "ConfigurationGraph":
        states = tuple(states)
        if len(states) < 2 or len({s.id for s in states}) != len(states):
            raise ValueError("need at least two uniquely identified geometry states")
        width = max(len(s.descriptor) for s in states)
        x = np.stack([np.pad(s.descriptor, (0, width-len(s.descriptor))) for s in states])
        std = np.std(x, axis=0); std[std < 1e-12] = 1.0
        x = (x - np.mean(x, axis=0)) / std
        distances = np.linalg.norm(x[:, None, :] - x[None, :, :], axis=-1)
        nonzero = distances[distances > 0]
        sigma = float(sigma or (np.median(nonzero) if len(nonzero) else 1.0))
        weights = np.exp(-(distances ** 2) / (2.0 * sigma ** 2)); np.fill_diagonal(weights, 0.0)
        adjacency = np.zeros_like(weights)
        k = min(max(1, int(neighbors)), len(states)-1)
        for i in range(len(states)):
            js = np.argsort(distances[i])[1:k+1]
            adjacency[i, js] = weights[i, js]
        adjacency = np.maximum(adjacency, adjacency.T)
        laplacian = np.diag(np.sum(adjacency, axis=1)) - adjacency
        return cls(states, distances, adjacency, laplacian)

    @classmethod
    def build_interpretable(cls, states: Sequence[GeometryState], *, family_weights: Mapping[str,float] | None = None, neighbors: int = 4, sigma: float | None = None) -> "ConfigurationGraph":
        """Build a graph from independently robust-scaled descriptor families."""
        states=tuple(states)
        if len(states)<2 or len({s.id for s in states})!=len(states): raise ValueError("need uniquely identified geometry states")
        names=("spectrum","modal","material","geometry","ir")
        if any(set(s.descriptor_families)!=set(names) for s in states): raise ValueError(f"every state must expose descriptor families {names}")
        weights={n:1.0 for n in names}; weights.update(family_weights or {})
        if any(weights[n]<0 for n in names) or sum(weights.values())<=0: raise ValueError("family weights must be nonnegative and nontrivial")
        total=sum(weights.values()); weights={n:weights[n]/total for n in names}
        family_d2={}; combined=np.zeros((len(states),len(states)))
        for name in names:
            width=max(len(s.descriptor_families[name]) for s in states)
            x=np.stack([np.pad(s.descriptor_families[name],(0,width-len(s.descriptor_families[name]))) for s in states])
            median=np.median(x,axis=0); q25,q75=np.percentile(x,[25,75],axis=0); scale=q75-q25
            fallback=np.std(x,axis=0); scale=np.where(scale>1e-12,scale,np.where(fallback>1e-12,fallback,1.0))
            x=(x-median)/scale
            d2=np.mean((x[:,None,:]-x[None,:,:])**2,axis=-1)
            family_d2[name]=d2; combined += weights[name]*d2
        distances=np.sqrt(np.maximum(combined,0)); nonzero=distances[distances>0]
        sigma=float(sigma or (np.median(nonzero) if len(nonzero) else 1.0))
        kernel=np.exp(-combined/(2*sigma*sigma)); np.fill_diagonal(kernel,0)
        adjacency=np.zeros_like(kernel); k=min(max(1,int(neighbors)),len(states)-1)
        for i in range(len(states)):
            js=np.argsort(distances[i])[1:k+1]; adjacency[i,js]=kernel[i,js]
        adjacency=np.maximum(adjacency,adjacency.T); laplacian=np.diag(adjacency.sum(axis=1))-adjacency
        return cls(states,distances,adjacency,laplacian,family_d2,weights)


def generate_geometry16(seed: int = 1604) -> tuple[GeometryState, ...]:
    """Deterministic synthetic whole-geometry descriptors for standalone validation."""
    rng = np.random.default_rng(seed)
    states = []
    for i in range(16):
        bits = np.array([(i >> b) & 1 for b in range(4)], dtype=float)
        spectrum = np.cumsum(0.5 + 0.18*bits.mean() + rng.uniform(0.02, 0.16, 12))
        descriptor = np.r_[bits, spectrum/spectrum[-1], np.sin((i+1)*np.arange(1,5)*np.pi/17)]
        states.append(GeometryState(f"g{i:02d}", descriptor, spectral_eigenvalues=spectrum, modal_frequencies=55*np.sqrt(spectrum), metadata={"generated": True, "basis_index": i}))
    return tuple(states)
