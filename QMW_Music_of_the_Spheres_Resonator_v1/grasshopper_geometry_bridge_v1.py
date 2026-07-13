#!/usr/bin/env python3
"""Versioned mesh-candidate boundary between Grasshopper and living geometry."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from hashlib import sha256
from pathlib import Path
import argparse
import json
import threading
import time
from typing import Any, Mapping, Protocol

import numpy as np

from living_spectral_geometry_v1 import (
    LivingEventType,
    LivingOperatorEvent,
)


SCHEMA = "qmw.grasshopper_mesh_candidate"
SCHEMA_VERSION = 1

_UNIT_TO_METERS = {
    "m": 1.0,
    "meter": 1.0,
    "meters": 1.0,
    "mm": 0.001,
    "millimeter": 0.001,
    "millimeters": 0.001,
    "cm": 0.01,
    "centimeter": 0.01,
    "centimeters": 0.01,
    "in": 0.0254,
    "inch": 0.0254,
    "inches": 0.0254,
    "ft": 0.3048,
    "foot": 0.3048,
    "feet": 0.3048,
}


class LivingGeometryTarget(Protocol):
    def apply_event(
        self,
        event: LivingOperatorEvent,
        *,
        schedule: bool = True,
    ) -> int | None: ...


@dataclass(frozen=True)
class MeshValidationPolicy:
    require_connected: bool = True
    require_manifold: bool = True
    require_closed: bool = False
    reject_duplicate_faces: bool = True
    area_epsilon: float = 1.0e-15


@dataclass(frozen=True)
class MeshDiagnostics:
    vertex_count: int
    face_count: int
    edge_count: int
    boundary_edge_count: int
    nonmanifold_edge_count: int
    connected_components: int
    duplicate_face_count: int
    degenerate_face_count: int
    surface_area_m2: float
    bounding_box_min_m: tuple[float, float, float]
    bounding_box_max_m: tuple[float, float, float]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _as_vertices(values: Any) -> np.ndarray:
    vertices = np.asarray(values, dtype=np.float64)
    if vertices.ndim != 2 or vertices.shape[1] != 3 or len(vertices) < 3:
        raise ValueError("vertices must have shape (n>=3, 3)")
    if not np.all(np.isfinite(vertices)):
        raise ValueError("vertices must contain only finite values")
    return np.ascontiguousarray(vertices)


def _as_faces(values: Any) -> np.ndarray:
    raw = np.asarray(values)
    if raw.ndim != 2 or raw.shape[1] != 3 or len(raw) < 1:
        raise ValueError("faces must have shape (m>=1, 3)")
    if not np.issubdtype(raw.dtype, np.integer):
        numeric = np.asarray(raw, dtype=np.float64)
        if not np.all(np.isfinite(numeric)) or not np.all(numeric == np.rint(numeric)):
            raise ValueError("face indices must be integers")
    return np.ascontiguousarray(raw, dtype=np.int64)


def _edge_counts(faces: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    edges = np.concatenate(
        (faces[:, (0, 1)], faces[:, (1, 2)], faces[:, (2, 0)]), axis=0
    )
    edges.sort(axis=1)
    return np.unique(edges, axis=0, return_counts=True)


def _component_count(vertex_count: int, edges: np.ndarray) -> int:
    parent = np.arange(vertex_count, dtype=np.int64)

    def root(index: int) -> int:
        while parent[index] != index:
            parent[index] = parent[parent[index]]
            index = int(parent[index])
        return index

    for left, right in edges:
        a = root(int(left))
        b = root(int(right))
        if a != b:
            parent[b] = a
    return len({root(index) for index in range(vertex_count)})


def mesh_diagnostics(
    vertices_m: np.ndarray,
    faces: np.ndarray,
    *,
    area_epsilon: float = 1.0e-15,
) -> MeshDiagnostics:
    vertices_m = _as_vertices(vertices_m)
    faces = _as_faces(faces)
    if np.min(faces) < 0 or np.max(faces) >= len(vertices_m):
        raise ValueError("face index is outside the vertex array")

    triangles = vertices_m[faces]
    doubled_areas = np.linalg.norm(
        np.cross(triangles[:, 1] - triangles[:, 0], triangles[:, 2] - triangles[:, 0]),
        axis=1,
    )
    degenerate = int(np.count_nonzero(doubled_areas <= 2.0 * area_epsilon))
    canonical_faces = np.sort(faces, axis=1)
    duplicate_count = int(len(faces) - len(np.unique(canonical_faces, axis=0)))
    edges, counts = _edge_counts(faces)
    return MeshDiagnostics(
        vertex_count=int(len(vertices_m)),
        face_count=int(len(faces)),
        edge_count=int(len(edges)),
        boundary_edge_count=int(np.count_nonzero(counts == 1)),
        nonmanifold_edge_count=int(np.count_nonzero(counts > 2)),
        connected_components=_component_count(len(vertices_m), edges),
        duplicate_face_count=duplicate_count,
        degenerate_face_count=degenerate,
        surface_area_m2=float(0.5 * np.sum(doubled_areas)),
        bounding_box_min_m=tuple(float(value) for value in np.min(vertices_m, axis=0)),
        bounding_box_max_m=tuple(float(value) for value in np.max(vertices_m, axis=0)),
    )


def _validate_diagnostics(
    diagnostics: MeshDiagnostics,
    policy: MeshValidationPolicy,
) -> None:
    errors: list[str] = []
    if diagnostics.degenerate_face_count:
        errors.append(f"{diagnostics.degenerate_face_count} degenerate face(s)")
    if policy.reject_duplicate_faces and diagnostics.duplicate_face_count:
        errors.append(f"{diagnostics.duplicate_face_count} duplicate face(s)")
    if policy.require_manifold and diagnostics.nonmanifold_edge_count:
        errors.append(f"{diagnostics.nonmanifold_edge_count} non-manifold edge(s)")
    if policy.require_connected and diagnostics.connected_components != 1:
        errors.append(f"{diagnostics.connected_components} disconnected components")
    if policy.require_closed and diagnostics.boundary_edge_count:
        errors.append(f"{diagnostics.boundary_edge_count} boundary edge(s)")
    if errors:
        raise ValueError("invalid Grasshopper mesh candidate: " + ", ".join(errors))


@dataclass(frozen=True)
class GrasshopperMeshCandidate:
    revision: int
    vertices: np.ndarray
    faces: np.ndarray
    created_at: float = field(default_factory=time.time)
    source: str = "grasshopper"
    units: str = "meters"
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if int(self.revision) < 1:
            raise ValueError("candidate revision must be >= 1")
        unit = str(self.units).strip().lower()
        if unit not in _UNIT_TO_METERS:
            raise ValueError(f"unsupported geometry unit {self.units!r}")
        object.__setattr__(self, "revision", int(self.revision))
        object.__setattr__(self, "vertices", _as_vertices(self.vertices))
        object.__setattr__(self, "faces", _as_faces(self.faces))
        object.__setattr__(self, "units", unit)
        object.__setattr__(self, "metadata", dict(self.metadata))

    @property
    def vertices_m(self) -> np.ndarray:
        return self.vertices * _UNIT_TO_METERS[self.units]

    @property
    def geometry_hash(self) -> str:
        digest = sha256()
        digest.update(np.ascontiguousarray(self.vertices_m, dtype="<f8").tobytes())
        digest.update(np.ascontiguousarray(self.faces, dtype="<i8").tobytes())
        return digest.hexdigest()

    def validate(
        self,
        policy: MeshValidationPolicy = MeshValidationPolicy(),
    ) -> MeshDiagnostics:
        diagnostics = mesh_diagnostics(
            self.vertices_m,
            self.faces,
            area_epsilon=policy.area_epsilon,
        )
        _validate_diagnostics(diagnostics, policy)
        return diagnostics

    def to_payload(self) -> dict[str, Any]:
        return {
            "schema": SCHEMA,
            "schema_version": SCHEMA_VERSION,
            "revision": self.revision,
            "created_at": float(self.created_at),
            "source": self.source,
            "units": self.units,
            "vertices": self.vertices.tolist(),
            "faces": self.faces.tolist(),
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_payload(cls, payload: Mapping[str, Any]) -> "GrasshopperMeshCandidate":
        if payload.get("schema") != SCHEMA:
            raise ValueError(f"unsupported mesh candidate schema {payload.get('schema')!r}")
        if int(payload.get("schema_version", -1)) != SCHEMA_VERSION:
            raise ValueError(
                f"unsupported mesh candidate schema version {payload.get('schema_version')!r}"
            )
        return cls(
            revision=int(payload["revision"]),
            created_at=float(payload.get("created_at", time.time())),
            source=str(payload.get("source", "grasshopper")),
            units=str(payload.get("units", "meters")),
            vertices=payload["vertices"],
            faces=payload["faces"],
            metadata=dict(payload.get("metadata", {})),
        )

    @classmethod
    def load_json(cls, path: str | Path) -> "GrasshopperMeshCandidate":
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        if not isinstance(payload, Mapping):
            raise ValueError("mesh candidate JSON must contain an object")
        return cls.from_payload(payload)

    def save_json(self, path: str | Path) -> Path:
        destination = Path(path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        temporary = destination.with_name(f".{destination.name}.tmp")
        temporary.write_text(json.dumps(self.to_payload(), indent=2), encoding="utf-8")
        temporary.replace(destination)
        return destination

    def to_living_event(self) -> LivingOperatorEvent:
        return LivingOperatorEvent(
            LivingEventType.GEOMETRY,
            {
                "vertices": self.vertices_m,
                "faces": self.faces,
                "grasshopper_revision": self.revision,
                "geometry_hash": self.geometry_hash,
                "metadata": dict(self.metadata),
            },
            reason=f"Grasshopper mesh candidate {self.revision}",
        )


@dataclass(frozen=True)
class GeometryAcceptance:
    candidate_revision: int
    living_revision: int | None
    geometry_hash: str
    status: str
    diagnostics: MeshDiagnostics


class GrasshopperGeometryBridge:
    """Validate ordered Grasshopper snapshots before mutating living geometry."""

    def __init__(
        self,
        living_geometry: LivingGeometryTarget,
        policy: MeshValidationPolicy = MeshValidationPolicy(),
    ) -> None:
        self.living_geometry = living_geometry
        self.policy = policy
        self._last_candidate_revision = 0
        self._last_hash: str | None = None
        self._last_acceptance: GeometryAcceptance | None = None
        self._lock = threading.RLock()

    @property
    def last_acceptance(self) -> GeometryAcceptance | None:
        with self._lock:
            return self._last_acceptance

    def accept(
        self,
        candidate: GrasshopperMeshCandidate,
        *,
        schedule: bool = True,
    ) -> GeometryAcceptance:
        diagnostics = candidate.validate(self.policy)
        geometry_hash = candidate.geometry_hash
        with self._lock:
            if candidate.revision < self._last_candidate_revision:
                raise ValueError(
                    f"stale Grasshopper revision {candidate.revision}; "
                    f"last accepted revision is {self._last_candidate_revision}"
                )
            if candidate.revision == self._last_candidate_revision:
                if geometry_hash != self._last_hash:
                    raise ValueError(
                        f"Grasshopper revision {candidate.revision} changed content"
                    )
                assert self._last_acceptance is not None
                return self._last_acceptance
            if geometry_hash == self._last_hash:
                acceptance = GeometryAcceptance(
                    candidate.revision,
                    None,
                    geometry_hash,
                    "unchanged",
                    diagnostics,
                )
            else:
                living_revision = self.living_geometry.apply_event(
                    candidate.to_living_event(), schedule=schedule
                )
                acceptance = GeometryAcceptance(
                    candidate.revision,
                    living_revision,
                    geometry_hash,
                    "accepted",
                    diagnostics,
                )
            self._last_candidate_revision = candidate.revision
            self._last_hash = geometry_hash
            self._last_acceptance = acceptance
            return acceptance

    def accept_file(
        self,
        path: str | Path,
        *,
        schedule: bool = True,
    ) -> GeometryAcceptance:
        return self.accept(
            GrasshopperMeshCandidate.load_json(path), schedule=schedule
        )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate a Grasshopper mesh-candidate JSON file."
    )
    parser.add_argument("candidate", type=Path)
    parser.add_argument("--require-closed", action="store_true")
    args = parser.parse_args()
    candidate = GrasshopperMeshCandidate.load_json(args.candidate)
    diagnostics = candidate.validate(
        MeshValidationPolicy(require_closed=args.require_closed)
    )
    print(
        json.dumps(
            {
                "revision": candidate.revision,
                "geometry_hash": candidate.geometry_hash,
                "diagnostics": diagnostics.to_dict(),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
