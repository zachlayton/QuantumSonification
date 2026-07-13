#!/usr/bin/env python3
"""Cotangent Laplace–Beltrami spectrum for triangular surface meshes."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import argparse
import json
from typing import Any

import numpy as np
from scipy import sparse
from scipy.sparse import linalg as spla


@dataclass(frozen=True)
class SpectralGeometryConfig:
    n_modes: int = 48
    effective_wave_speed: float = 120.0
    frequency_scale: float = 1.0
    min_frequency_hz: float = 0.0
    max_frequency_hz: float = float("inf")
    regularization: float = 1e-9


@dataclass
class SpectralGeometryResult:
    vertices: np.ndarray
    faces: np.ndarray
    eigenvalues: np.ndarray
    eigenvectors: np.ndarray
    frequencies_hz: np.ndarray
    mode_weights: np.ndarray
    localization_ipr: np.ndarray
    source_listener_weights: np.ndarray | None
    source_vertex: int | None
    listener_vertex: int | None
    spectral_gap: float
    mean_spacing: float
    spacing_variance: float
    spectral_entropy: float

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "vertex_count": int(len(self.vertices)),
            "face_count": int(len(self.faces)),
            "mode_count": int(len(self.eigenvalues)),
            "eigenvalues": self.eigenvalues.tolist(),
            "frequencies_hz": self.frequencies_hz.tolist(),
            "mode_weights": self.mode_weights.tolist(),
            "localization_ipr": self.localization_ipr.tolist(),
            "source_listener_weights": (
                None
                if self.source_listener_weights is None
                else self.source_listener_weights.tolist()
            ),
            "source_vertex": self.source_vertex,
            "listener_vertex": self.listener_vertex,
            "spectral_gap": self.spectral_gap,
            "mean_eigenvalue_spacing": self.mean_spacing,
            "eigenvalue_spacing_variance": self.spacing_variance,
            "spectral_entropy": self.spectral_entropy,
        }


def load_obj(path: str | Path) -> tuple[np.ndarray, np.ndarray]:
    """Load OBJ vertices and triangulate polygon faces using a fan."""
    vertices: list[list[float]] = []
    faces: list[list[int]] = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        fields = line.strip().split()
        if not fields or fields[0].startswith("#"):
            continue
        if fields[0] == "v" and len(fields) >= 4:
            vertices.append([float(fields[1]), float(fields[2]), float(fields[3])])
        elif fields[0] == "f" and len(fields) >= 4:
            polygon: list[int] = []
            for token in fields[1:]:
                raw = int(token.split("/")[0])
                polygon.append(raw - 1 if raw > 0 else len(vertices) + raw)
            for index in range(1, len(polygon) - 1):
                faces.append([polygon[0], polygon[index], polygon[index + 1]])
    vertex_array = np.asarray(vertices, dtype=np.float64)
    face_array = np.asarray(faces, dtype=np.int64)
    if vertex_array.ndim != 2 or vertex_array.shape[1:] != (3,):
        raise ValueError(f"OBJ {path} contains no valid 3D vertices")
    if face_array.ndim != 2 or face_array.shape[1:] != (3,):
        raise ValueError(f"OBJ {path} contains no valid triangular faces")
    return vertex_array, face_array


def _validate_mesh(
    vertices: np.ndarray, faces: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    vertices = np.asarray(vertices, dtype=np.float64)
    faces = np.asarray(faces, dtype=np.int64)
    if vertices.ndim != 2 or vertices.shape[1] != 3 or len(vertices) < 3:
        raise ValueError("vertices must have shape (n>=3, 3)")
    if faces.ndim != 2 or faces.shape[1] != 3 or len(faces) < 1:
        raise ValueError("faces must have shape (m>=1, 3)")
    if np.min(faces) < 0 or np.max(faces) >= len(vertices):
        raise ValueError("face indices are outside the vertex array")
    if not np.all(np.isfinite(vertices)):
        raise ValueError("vertices must be finite")
    return vertices, faces


def cotangent_operators(
    vertices: np.ndarray, faces: np.ndarray
) -> tuple[sparse.csr_matrix, sparse.csr_matrix]:
    """Return a positive-semidefinite cotangent Laplacian and lumped mass."""
    vertices, faces = _validate_mesh(vertices, faces)
    edge_weights: dict[tuple[int, int], float] = {}
    areas = np.zeros(len(vertices), dtype=np.float64)

    for i, j, k in faces:
        vi, vj, vk = vertices[i], vertices[j], vertices[k]
        normal = np.cross(vj - vi, vk - vi)
        twice_area = float(np.linalg.norm(normal))
        if twice_area <= 1e-15:
            continue
        areas[[i, j, k]] += (0.5 * twice_area) / 3.0
        cot_i = float(np.dot(vj - vi, vk - vi) / twice_area)
        cot_j = float(np.dot(vi - vj, vk - vj) / twice_area)
        cot_k = float(np.dot(vi - vk, vj - vk) / twice_area)
        for a, b, cotangent in (
            (j, k, cot_i),
            (i, k, cot_j),
            (i, j, cot_k),
        ):
            key = (min(int(a), int(b)), max(int(a), int(b)))
            edge_weights[key] = edge_weights.get(key, 0.0) + 0.5 * cotangent

    if not edge_weights or not np.any(areas > 0.0):
        raise ValueError("mesh has no nondegenerate connected triangles")
    rows: list[int] = []
    cols: list[int] = []
    data: list[float] = []
    diagonal = np.zeros(len(vertices), dtype=np.float64)
    for (i, j), weight in edge_weights.items():
        diagonal[i] += weight
        diagonal[j] += weight
        rows.extend((i, j))
        cols.extend((j, i))
        data.extend((-weight, -weight))
    rows.extend(range(len(vertices)))
    cols.extend(range(len(vertices)))
    data.extend(diagonal.tolist())
    laplacian = sparse.coo_matrix(
        (data, (rows, cols)), shape=(len(vertices), len(vertices))
    ).tocsr()
    positive_areas = areas[areas > 1e-15]
    area_floor = max(float(np.median(positive_areas)) * 1e-9, 1e-15)
    mass = sparse.diags(np.maximum(areas, area_floor), format="csr")
    return laplacian, mass


class MeshSpectralGeometry:
    def __init__(
        self,
        vertices: np.ndarray,
        faces: np.ndarray,
        config: SpectralGeometryConfig = SpectralGeometryConfig(),
    ) -> None:
        self.vertices, self.faces = _validate_mesh(vertices, faces)
        self.config = config
        self.result: SpectralGeometryResult | None = None

    def _eigenpairs(self) -> tuple[np.ndarray, np.ndarray]:
        laplacian, mass = cotangent_operators(self.vertices, self.faces)
        n = len(self.vertices)
        wanted = max(1, min(int(self.config.n_modes), n - 1))
        solve_count = min(n - 1, wanted + 1)
        regularized = laplacian + self.config.regularization * mass
        if n <= 64 or solve_count >= n - 1:
            inverse_sqrt = 1.0 / np.sqrt(mass.diagonal())
            normalized = (
                inverse_sqrt[:, None]
                * regularized.toarray()
                * inverse_sqrt[None, :]
            )
            values, normalized_vectors = np.linalg.eigh(normalized)
            vectors = inverse_sqrt[:, None] * normalized_vectors
        else:
            values, vectors = spla.eigsh(
                regularized,
                k=solve_count,
                M=mass,
                sigma=0.0,
                which="LM",
            )
        order = np.argsort(np.real(values))
        values = np.maximum(np.real(values[order]), 0.0)
        vectors = np.real(vectors[:, order])
        keep = values > max(self.config.regularization * 10.0, 1e-10)
        return values[keep][:wanted], vectors[:, keep][:, :wanted]

    def solve(
        self,
        source_position: np.ndarray | list[float] | None = None,
        listener_position: np.ndarray | list[float] | None = None,
    ) -> SpectralGeometryResult:
        eigenvalues, eigenvectors = self._eigenpairs()
        if len(eigenvalues) == 0:
            raise ValueError("spectral solve produced no nonconstant modes")
        frequencies = (
            self.config.effective_wave_speed
            * self.config.frequency_scale
            * np.sqrt(eigenvalues)
            / (2.0 * np.pi)
        )
        audible = (
            (frequencies >= self.config.min_frequency_hz)
            & (frequencies <= self.config.max_frequency_hz)
        )
        eigenvalues = eigenvalues[audible]
        eigenvectors = eigenvectors[:, audible]
        frequencies = frequencies[audible]
        if len(eigenvalues) == 0:
            raise ValueError("no modes remain inside the configured frequency range")

        norms = np.sqrt(np.sum(eigenvectors**2, axis=0))
        normalized_vectors = eigenvectors / np.maximum(norms, 1e-15)
        localization = np.sum(normalized_vectors**4, axis=0)
        mode_weights = 1.0 / np.sqrt(1.0 + np.arange(len(eigenvalues)))
        mode_weights /= max(float(np.max(mode_weights)), 1e-15)

        source_vertex = None
        listener_vertex = None
        coupling = None
        if source_position is not None and listener_position is not None:
            source = np.asarray(source_position, dtype=np.float64).reshape(3)
            listener = np.asarray(listener_position, dtype=np.float64).reshape(3)
            source_vertex = int(np.argmin(np.linalg.norm(self.vertices - source, axis=1)))
            listener_vertex = int(
                np.argmin(np.linalg.norm(self.vertices - listener, axis=1))
            )
            coupling = eigenvectors[source_vertex] * eigenvectors[listener_vertex]

        spacing = np.diff(eigenvalues)
        probabilities = eigenvalues / max(float(np.sum(eigenvalues)), 1e-15)
        entropy = float(
            -np.sum(probabilities * np.log2(np.maximum(probabilities, 1e-15)))
        )
        self.result = SpectralGeometryResult(
            vertices=self.vertices,
            faces=self.faces,
            eigenvalues=eigenvalues,
            eigenvectors=eigenvectors,
            frequencies_hz=frequencies,
            mode_weights=mode_weights,
            localization_ipr=localization,
            source_listener_weights=coupling,
            source_vertex=source_vertex,
            listener_vertex=listener_vertex,
            spectral_gap=float(eigenvalues[0]),
            mean_spacing=float(np.mean(spacing)) if len(spacing) else 0.0,
            spacing_variance=float(np.var(spacing)) if len(spacing) else 0.0,
            spectral_entropy=entropy,
        )
        return self.result

    def export_npz(self, path: str | Path) -> Path:
        if self.result is None:
            raise RuntimeError("solve() must be called before export_npz()")
        output = Path(path)
        output.parent.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(
            output,
            geometry_kind=np.array("triangular_surface"),
            vertices=self.result.vertices,
            edges=np.empty((0, 2), dtype=np.int64),
            faces=self.result.faces,
            eigenvalues=self.result.eigenvalues,
            eigenvectors=self.result.eigenvectors,
            frequencies_hz=self.result.frequencies_hz,
            mode_weights=self.result.mode_weights,
            damping=np.empty(0, dtype=np.float64),
            vertex_labels=np.empty(0, dtype="U1"),
            edge_weights=np.empty(0, dtype=np.float64),
            metadata_json=np.asarray(
                json.dumps(
                    {
                        "solver": "spectral_geometry_v1",
                        "operator": "cotangent_laplace_beltrami",
                    },
                    sort_keys=True,
                )
            ),
            localization_ipr=self.result.localization_ipr,
            source_listener_weights=(
                np.array([], dtype=np.float64)
                if self.result.source_listener_weights is None
                else self.result.source_listener_weights
            ),
        )
        return output


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mesh", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--json", type=Path)
    parser.add_argument("--modes", type=int, default=48)
    parser.add_argument("--wave-speed", type=float, default=120.0)
    args = parser.parse_args()
    vertices, faces = load_obj(args.mesh)
    solver = MeshSpectralGeometry(
        vertices,
        faces,
        SpectralGeometryConfig(
            n_modes=args.modes,
            effective_wave_speed=args.wave_speed,
        ),
    )
    result = solver.solve()
    solver.export_npz(args.output)
    if args.json is not None:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(
            json.dumps(result.to_json_dict(), indent=2), encoding="utf-8"
        )
    print(f"Solved {len(result.eigenvalues)} modes → {args.output}")


if __name__ == "__main__":
    main()
