#!/usr/bin/env python3
"""Turn modal density matrices into Laplacian deformations of an icosphere.

Four density states isolate the formal distinctions under study:

* ``pure``: a single occupied Laplacian mode;
* ``coherent``: a pure complex superposition of four modes;
* ``dephased``: the same populations with off-diagonal terms removed;
* ``maximally_mixed``: identity on the selected modal subspace.

The optional ``coherence_only`` form is a derived control. It subtracts the
dephased displacement from the coherent displacement and rescales the signed
difference, making geometry caused only by off-diagonal terms visible.

Outputs include meter and Rhino-millimeter OBJ meshes, candidate JSON payloads
for the existing QMW Grasshopper/living-geometry bridge, per-vertex fields,
and a compressed numerical archive.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from scipy import sparse
from scipy.sparse.linalg import eigsh, spsolve


@dataclass(frozen=True)
class Mesh:
    vertices: np.ndarray
    faces: np.ndarray


def _unit(values: np.ndarray) -> np.ndarray:
    return values / np.linalg.norm(values, axis=-1, keepdims=True)


def make_icosphere(subdivisions: int = 3) -> Mesh:
    """Create a closed unit icosphere with shared indexed vertices."""
    if subdivisions < 0:
        raise ValueError("subdivisions must be nonnegative")
    phi = (1.0 + np.sqrt(5.0)) / 2.0
    vertices = _unit(
        np.asarray(
            [
                (-1, phi, 0), (1, phi, 0), (-1, -phi, 0), (1, -phi, 0),
                (0, -1, phi), (0, 1, phi), (0, -1, -phi), (0, 1, -phi),
                (phi, 0, -1), (phi, 0, 1), (-phi, 0, -1), (-phi, 0, 1),
            ],
            dtype=np.float64,
        )
    )
    faces = [
        (0, 11, 5), (0, 5, 1), (0, 1, 7), (0, 7, 10), (0, 10, 11),
        (1, 5, 9), (5, 11, 4), (11, 10, 2), (10, 7, 6), (7, 1, 8),
        (3, 9, 4), (3, 4, 2), (3, 2, 6), (3, 6, 8), (3, 8, 9),
        (4, 9, 5), (2, 4, 11), (6, 2, 10), (8, 6, 7), (9, 8, 1),
    ]
    verts = [row.copy() for row in vertices]
    for _ in range(subdivisions):
        cache: dict[tuple[int, int], int] = {}

        def midpoint(a: int, b: int) -> int:
            key = (a, b) if a < b else (b, a)
            if key not in cache:
                point = np.asarray(verts[a]) + np.asarray(verts[b])
                point /= np.linalg.norm(point)
                cache[key] = len(verts)
                verts.append(point)
            return cache[key]

        refined: list[tuple[int, int, int]] = []
        for a, b, c in faces:
            ab, bc, ca = midpoint(a, b), midpoint(b, c), midpoint(c, a)
            refined.extend(((a, ab, ca), (b, bc, ab), (c, ca, bc), (ab, bc, ca)))
        faces = refined
    return Mesh(np.asarray(verts), np.asarray(faces, dtype=np.int64))


def cotangent_operators(mesh: Mesh) -> tuple[sparse.csr_matrix, sparse.csr_matrix, np.ndarray]:
    """Return the positive cotangent Laplacian, lumped mass, and vertex areas."""
    n = len(mesh.vertices)
    weights: dict[tuple[int, int], float] = {}
    areas = np.zeros(n, dtype=np.float64)
    for i, j, k in mesh.faces:
        vi, vj, vk = mesh.vertices[i], mesh.vertices[j], mesh.vertices[k]
        twice_area = float(np.linalg.norm(np.cross(vj - vi, vk - vi)))
        if twice_area <= 1e-15:
            continue
        areas[[i, j, k]] += (0.5 * twice_area) / 3.0
        cotangents = (
            ((j, k), np.dot(vj - vi, vk - vi) / twice_area),
            ((i, k), np.dot(vi - vj, vk - vj) / twice_area),
            ((i, j), np.dot(vi - vk, vj - vk) / twice_area),
        )
        for edge, cotangent in cotangents:
            key = tuple(sorted(edge))
            weights[key] = weights.get(key, 0.0) + 0.5 * float(cotangent)

    rows: list[int] = []
    columns: list[int] = []
    data: list[float] = []
    diagonal = np.zeros(n, dtype=np.float64)
    for (i, j), weight in weights.items():
        rows.extend((i, j))
        columns.extend((j, i))
        data.extend((-weight, -weight))
        diagonal[[i, j]] += weight
    rows.extend(range(n))
    columns.extend(range(n))
    data.extend(diagonal.tolist())
    laplacian = sparse.coo_matrix((data, (rows, columns)), shape=(n, n)).tocsr()
    mass = sparse.diags(areas, format="csr")
    return laplacian, mass, areas


def laplacian_modes(
    laplacian: sparse.csr_matrix,
    mass: sparse.csr_matrix,
    count: int,
) -> tuple[np.ndarray, np.ndarray]:
    if count < 7 or count >= laplacian.shape[0]:
        raise ValueError("mode count must be at least 7 and below vertex count")
    values, vectors = eigsh(
        laplacian,
        k=count,
        M=mass,
        sigma=1e-9,
        which="LM",
        v0=np.linspace(1.0, 2.0, laplacian.shape[0]),
    )
    order = np.argsort(values)
    values = np.maximum(np.real(values[order]), 0.0)
    vectors = np.real(vectors[:, order])
    # Sparse eigensolvers may flip eigenvector signs between runs. Canonicalize
    # each sign so exported geometry is deterministic.
    for column in range(vectors.shape[1]):
        pivot = int(np.argmax(np.abs(vectors[:, column])))
        if vectors[pivot, column] < 0:
            vectors[:, column] *= -1
    return values, vectors


def density_states(mode_count: int) -> dict[str, np.ndarray]:
    """Construct four Hermitian positive trace-one matrices."""
    if mode_count < 7:
        raise ValueError("at least seven modes are required")
    pure = np.zeros((mode_count, mode_count), dtype=np.complex128)
    if mode_count >= 25:
        # Reach into the l=4 shell. Complete shells contain 1+3+5+7+9=25
        # spherical modes; these indices sample each nonconstant shell.
        pure_index = 20
        active = np.asarray([2, 5, 10, 14, 18, 24])
        amplitude = np.asarray([0.36, 0.42, 0.48, 0.39, 0.44, 0.31])
        phase = np.asarray([0.0, 0.37, 0.71, 1.08, 1.43, 1.81]) * np.pi
    else:
        pure_index = 4
        active = np.asarray([1, 2, 4, 6])
        amplitude = np.asarray([0.55, 0.45, 0.50, 0.35])
        phase = np.asarray([0.0, np.pi / 3, 0.73 * np.pi, 1.31 * np.pi])
    pure[pure_index, pure_index] = 1.0

    coefficients = np.zeros(mode_count, dtype=np.complex128)
    coefficients[active] = amplitude * np.exp(1j * phase)
    coefficients /= np.linalg.norm(coefficients)
    coherent = np.outer(coefficients, coefficients.conjugate())
    return {
        "pure": pure,
        "coherent": coherent,
        "dephased": np.diag(np.diag(coherent)),
        "maximally_mixed": np.eye(mode_count, dtype=np.complex128) / mode_count,
    }


def probability_field(density: np.ndarray, modes: np.ndarray, areas: np.ndarray) -> np.ndarray:
    """Evaluate K_rho(x,x) and normalize it in the mesh area measure."""
    field = np.einsum("vm,mn,vn->v", modes, density, modes.conjugate()).real
    field = np.maximum(field, 0.0)
    integral = float(np.dot(areas, field))
    if integral <= 0:
        raise ValueError("empty spatial probability field")
    return field / integral


def density_metrics(density: np.ndarray) -> dict[str, float]:
    spectrum = np.linalg.eigvalsh(density).real
    spectrum = spectrum[spectrum > 1e-14]
    off_diagonal = density - np.diag(np.diag(density))
    return {
        "purity": float(np.trace(density @ density).real),
        "l1_coherence": float(np.sum(np.abs(off_diagonal))),
        "von_neumann_entropy": float(-np.sum(spectrum * np.log(spectrum))),
    }


def deform(
    mesh: Mesh,
    laplacian: sparse.csr_matrix,
    mass: sparse.csr_matrix,
    areas: np.ndarray,
    fields: dict[str, np.ndarray],
    screening: float,
    max_displacement: float,
) -> tuple[dict[str, Mesh], dict[str, np.ndarray]]:
    if screening <= 0 or max_displacement < 0:
        raise ValueError("screening must be positive and displacement nonnegative")
    total_area = float(areas.sum())
    operator = laplacian + screening * mass
    raw: dict[str, np.ndarray] = {}
    for name, field in fields.items():
        mean = float(np.dot(areas, field) / total_area)
        solution = np.asarray(spsolve(operator, mass @ (field - mean)))
        solution -= np.dot(areas, solution) / total_area
        raw[name] = solution
    largest = max(float(np.max(np.abs(values))) for values in raw.values())
    scale = max_displacement / largest if largest > 1e-14 else 0.0
    normals = _unit(mesh.vertices)
    displacements = {name: scale * values for name, values in raw.items()}
    meshes = {
        name: Mesh(mesh.vertices + values[:, None] * normals, mesh.faces.copy())
        for name, values in displacements.items()
    }
    return meshes, displacements


def reserve_output_fork(requested: Path) -> tuple[Path, dict[str, object]]:
    requested = requested.expanduser().resolve()
    requested.parent.mkdir(parents=True, exist_ok=True)
    if not requested.exists():
        requested.mkdir()
        return requested, {"fork_index": 1, "forked_from": None}
    if requested.is_dir() and not any(requested.iterdir()):
        return requested, {"fork_index": 1, "forked_from": None}
    if not requested.is_dir():
        raise NotADirectoryError(requested)
    index = 2
    while True:
        candidate = requested.parent / f"{requested.name}_fork_{index:06d}"
        try:
            candidate.mkdir()
            return candidate, {"fork_index": index, "forked_from": str(requested)}
        except FileExistsError:
            index += 1


def _write_obj(path: Path, mesh: Mesh) -> None:
    with path.open("w", encoding="utf-8") as handle:
        handle.write("# QMW Timaean density geometry v1\n")
        for x, y, z in mesh.vertices:
            handle.write(f"v {x:.10f} {y:.10f} {z:.10f}\n")
        for a, b, c in mesh.faces + 1:
            handle.write(f"f {a} {b} {c}\n")


def _geometry_hash(mesh: Mesh) -> str:
    digest = hashlib.sha256()
    digest.update(np.ascontiguousarray(mesh.vertices, dtype="<f8").tobytes())
    digest.update(np.ascontiguousarray(mesh.faces, dtype="<i8").tobytes())
    return digest.hexdigest()


def _write_candidate(
    path: Path,
    mesh: Mesh,
    state: str,
    revision: int,
    density: np.ndarray,
    metrics: dict[str, float],
) -> None:
    matrix_label = "coherence_operator" if state == "coherence_only" else "density_matrix"
    payload = {
        "schema": "qmw.grasshopper_mesh_candidate",
        "schema_version": 1,
        "revision": revision,
        "created_at": time.time(),
        "source": "timaean_density_geometry_v1",
        "units": "meters",
        "vertices": mesh.vertices.tolist(),
        "faces": mesh.faces.tolist(),
        "metadata": {
            "experiment": (
                "qmw.timaean_density_geometry.l4_coherence_v2"
                if state == "coherence_only"
                else "qmw.timaean_density_geometry.v1"
            ),
            "state": state,
            f"{matrix_label}_real": density.real.tolist(),
            f"{matrix_label}_imag": density.imag.tolist(),
            **metrics,
        },
    }
    path.write_text(json.dumps(payload, separators=(",", ":")) + "\n", encoding="utf-8")


def run(
    output: Path,
    *,
    subdivisions: int = 3,
    mode_count: int = 9,
    screening: float = 0.35,
    max_displacement: float = 0.28,
    radius_m: float = 0.25,
    preserve_existing: bool = True,
    include_coherence_only: bool = False,
) -> dict[str, object]:
    if radius_m <= 0:
        raise ValueError("radius_m must be positive")
    if preserve_existing:
        output, fork = reserve_output_fork(output)
    else:
        output.mkdir(parents=True, exist_ok=True)
        fork = {"fork_index": 1, "forked_from": None}

    base = make_icosphere(subdivisions)
    laplacian, mass, areas = cotangent_operators(base)
    eigenvalues, modes = laplacian_modes(laplacian, mass, mode_count)
    states = density_states(mode_count)
    fields = {
        name: probability_field(density, modes, areas)
        for name, density in states.items()
    }
    deformed, displacement = deform(
        base,
        laplacian,
        mass,
        areas,
        fields,
        screening,
        max_displacement,
    )

    coherence_operator: np.ndarray | None = None
    coherence_field: np.ndarray | None = None
    if include_coherence_only:
        coherence_operator = states["coherent"] - states["dephased"]
        coherence_field = fields["coherent"] - fields["dephased"]
        difference = displacement["coherent"] - displacement["dephased"]
        largest_difference = float(np.max(np.abs(difference)))
        if largest_difference <= 1e-14:
            raise ValueError("coherent and dephased states produced no geometric difference")
        coherence_displacement = difference * (max_displacement / largest_difference)
        displacement["coherence_only"] = coherence_displacement
        deformed["coherence_only"] = Mesh(
            base.vertices + coherence_displacement[:, None] * _unit(base.vertices),
            base.faces.copy(),
        )

    base_m = Mesh(base.vertices * radius_m, base.faces)
    _write_obj(output / "base_icosphere.obj", base_m)
    _write_obj(output / "base_icosphere_rhino_mm.obj", Mesh(base_m.vertices * 1000, base.faces))
    metrics = {name: density_metrics(density) for name, density in states.items()}
    state_manifest: dict[str, object] = {}
    for revision, name in enumerate(states, start=1):
        mesh_m = Mesh(deformed[name].vertices * radius_m, base.faces)
        _write_obj(output / f"{name}.obj", mesh_m)
        _write_obj(output / f"{name}_rhino_mm.obj", Mesh(mesh_m.vertices * 1000, base.faces))
        _write_candidate(
            output / f"{name}_candidate.json",
            mesh_m,
            name,
            revision,
            states[name],
            metrics[name],
        )
        np.savetxt(
            output / f"{name}_vertex_data.csv",
            np.column_stack((fields[name], displacement[name])),
            delimiter=",",
            header="probability,displacement",
            comments="",
        )
        state_manifest[name] = {
            **metrics[name],
            "geometry_hash": _geometry_hash(mesh_m),
        }

    if include_coherence_only and coherence_operator is not None and coherence_field is not None:
        name = "coherence_only"
        mesh_m = Mesh(deformed[name].vertices * radius_m, base.faces)
        operator_metrics = {
            "operator_trace": float(np.trace(coherence_operator).real),
            "operator_frobenius_norm": float(np.linalg.norm(coherence_operator)),
            "max_abs_displacement": float(np.max(np.abs(displacement[name]))),
        }
        _write_obj(output / f"{name}.obj", mesh_m)
        _write_obj(output / f"{name}_rhino_mm.obj", Mesh(mesh_m.vertices * 1000, base.faces))
        _write_candidate(
            output / f"{name}_candidate.json",
            mesh_m,
            name,
            len(states) + 1,
            coherence_operator,
            operator_metrics,
        )
        np.savetxt(
            output / f"{name}_vertex_data.csv",
            np.column_stack((coherence_field, displacement[name])),
            delimiter=",",
            header="coherent_minus_dephased_probability,displacement",
            comments="",
        )
        state_manifest[name] = {
            "derived": True,
            "source": "coherent_minus_dephased",
            **operator_metrics,
            "geometry_hash": _geometry_hash(mesh_m),
        }

    np.savez_compressed(
        output / "timaean_lab_data.npz",
        vertices=base.vertices,
        faces=base.faces,
        eigenvalues=eigenvalues,
        modes=modes,
        **{f"rho_{name}": value for name, value in states.items()},
        **{f"p_{name}": value for name, value in fields.items()},
        **{f"u_{name}": value for name, value in displacement.items()},
        **(
            {
                "rho_coherence_only": coherence_operator,
                "p_coherence_only": coherence_field,
            }
            if include_coherence_only
            else {}
        ),
    )
    manifest: dict[str, object] = {
        "experiment": (
            "qmw.timaean_density_geometry.l4_coherence_v2"
            if include_coherence_only and mode_count >= 25
            else "qmw.timaean_density_geometry.v1"
        ),
        "output_directory": str(output),
        "fork": fork,
        "mesh": {
            "subdivisions": subdivisions,
            "vertices": int(len(base.vertices)),
            "faces": int(len(base.faces)),
            "surface_area": float(areas.sum()),
            "radius_m": radius_m,
        },
        "mode_count": mode_count,
        "eigenvalues": eigenvalues.tolist(),
        "deformation": {
            "screening": screening,
            "common_max_displacement": max_displacement,
            "coherence_only_normalized_separately": include_coherence_only,
        },
        "states": state_manifest,
    }
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("timaean_lab/output"))
    parser.add_argument("--subdivisions", type=int, default=3)
    parser.add_argument("--modes", type=int, default=9)
    parser.add_argument("--screening", type=float, default=0.35)
    parser.add_argument("--displacement", type=float, default=0.28)
    parser.add_argument("--radius-m", type=float, default=0.25)
    parser.add_argument(
        "--coherence-only",
        action="store_true",
        help="export an exaggerated coherent-minus-dephased differential form",
    )
    args = parser.parse_args()
    result = run(
        args.output,
        subdivisions=args.subdivisions,
        mode_count=args.modes,
        screening=args.screening,
        max_displacement=args.displacement,
        radius_m=args.radius_m,
        include_coherence_only=args.coherence_only,
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
