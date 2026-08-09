#!/usr/bin/env python3
"""Shared spectral-geometry interchange packet for QuantumSonification."""
from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
import json
import numpy as np


def _array(value: Any, dtype: Any, shape2: int | None = None) -> np.ndarray:
    arr = np.asarray(value, dtype=dtype)
    if shape2 is not None:
        if arr.size == 0:
            return np.empty((0, shape2), dtype=dtype)
        arr = arr.reshape((-1, shape2))
    return arr


def _jsonable(value: Any) -> Any:
    if isinstance(value, np.ndarray): return value.tolist()
    if isinstance(value, np.generic): return value.item()
    if isinstance(value, dict): return {str(k): _jsonable(v) for k,v in value.items()}
    if isinstance(value, (list,tuple)): return [_jsonable(v) for v in value]
    return value

@dataclass
class SpectralGeometryPacket:
    geometry_kind: str
    vertices: np.ndarray
    eigenvalues: np.ndarray
    eigenvectors: np.ndarray
    edges: np.ndarray = field(default_factory=lambda: np.empty((0,2), dtype=np.int64))
    faces: np.ndarray = field(default_factory=lambda: np.empty((0,3), dtype=np.int64))
    frequencies_hz: np.ndarray = field(default_factory=lambda: np.empty(0, dtype=np.float64))
    mode_weights: np.ndarray = field(default_factory=lambda: np.empty(0, dtype=np.float64))
    damping: np.ndarray = field(default_factory=lambda: np.empty(0, dtype=np.float64))
    vertex_labels: np.ndarray = field(default_factory=lambda: np.empty(0, dtype='U1'))
    edge_weights: np.ndarray = field(default_factory=lambda: np.empty(0, dtype=np.float64))
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.geometry_kind = str(self.geometry_kind)
        self.vertices = _array(self.vertices, np.float64, 3)
        self.edges = _array(self.edges, np.int64, 2)
        self.faces = _array(self.faces, np.int64, 3)
        self.eigenvalues = _array(self.eigenvalues, np.float64).reshape(-1)
        self.eigenvectors = _array(self.eigenvectors, np.float64)
        self.frequencies_hz = _array(self.frequencies_hz, np.float64).reshape(-1)
        self.mode_weights = _array(self.mode_weights, np.float64).reshape(-1)
        self.damping = _array(self.damping, np.float64).reshape(-1)
        self.vertex_labels = np.asarray(self.vertex_labels, dtype=str).reshape(-1)
        self.edge_weights = _array(self.edge_weights, np.float64).reshape(-1)
        self.validate()

    @property
    def n_vertices(self) -> int: return len(self.vertices)
    @property
    def n_modes(self) -> int: return len(self.eigenvalues)

    def validate(self) -> None:
        n, m = self.n_vertices, self.n_modes
        if self.eigenvectors.ndim != 2 or self.eigenvectors.shape != (n,m):
            raise ValueError(f'eigenvectors must have shape ({n}, {m}); got {self.eigenvectors.shape}')
        for name, arr in [('frequencies_hz',self.frequencies_hz),('mode_weights',self.mode_weights),('damping',self.damping)]:
            if len(arr) not in (0,m): raise ValueError(f'{name} must be empty or have {m} entries')
        if len(self.vertex_labels) not in (0,n): raise ValueError('vertex_labels length mismatch')
        if len(self.edge_weights) not in (0,len(self.edges)): raise ValueError('edge_weights length mismatch')
        if self.edges.size and (self.edges.min()<0 or self.edges.max()>=n): raise ValueError('edge index out of range')
        if self.faces.size and (self.faces.min()<0 or self.faces.max()>=n): raise ValueError('face index out of range')
        if np.any(self.eigenvalues < -1e-8): raise ValueError('eigenvalues must be nonnegative within tolerance')

    def save_npz(self, path: str|Path) -> Path:
        path=Path(path); path.parent.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(path, geometry_kind=np.asarray(self.geometry_kind), vertices=self.vertices,
            edges=self.edges, faces=self.faces, eigenvalues=self.eigenvalues, eigenvectors=self.eigenvectors,
            frequencies_hz=self.frequencies_hz, mode_weights=self.mode_weights, damping=self.damping,
            vertex_labels=self.vertex_labels, edge_weights=self.edge_weights,
            metadata_json=np.asarray(json.dumps(_jsonable(self.metadata), sort_keys=True)))
        return path

    @classmethod
    def load_npz(cls, path: str|Path) -> 'SpectralGeometryPacket':
        with np.load(path, allow_pickle=False) as z:
            files=set(z.files)
            meta=json.loads(str(z['metadata_json'].item())) if 'metadata_json' in files else {}
            return cls(geometry_kind=str(z['geometry_kind'].item()) if 'geometry_kind' in files else 'unknown',
                vertices=z['vertices'], edges=z['edges'] if 'edges' in files else [], faces=z['faces'] if 'faces' in files else [],
                eigenvalues=z['eigenvalues'], eigenvectors=z['eigenvectors'],
                frequencies_hz=z['frequencies_hz'] if 'frequencies_hz' in files else [],
                mode_weights=z['mode_weights'] if 'mode_weights' in files else [], damping=z['damping'] if 'damping' in files else [],
                vertex_labels=z['vertex_labels'] if 'vertex_labels' in files else [], edge_weights=z['edge_weights'] if 'edge_weights' in files else [], metadata=meta)

    def save_json(self, path: str|Path, include_eigenvectors: bool=False) -> Path:
        data={'geometry_kind':self.geometry_kind,'vertices':self.vertices.tolist(),'edges':self.edges.tolist(),'faces':self.faces.tolist(),
              'eigenvalues':self.eigenvalues.tolist(),'frequencies_hz':self.frequencies_hz.tolist(),'mode_weights':self.mode_weights.tolist(),
              'damping':self.damping.tolist(),'vertex_labels':self.vertex_labels.tolist(),'edge_weights':self.edge_weights.tolist(),
              'metadata':_jsonable(self.metadata)}
        if include_eigenvectors: data['eigenvectors']=self.eigenvectors.tolist()
        path=Path(path); path.write_text(json.dumps(data,indent=2)); return path
