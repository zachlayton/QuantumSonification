#!/usr/bin/env python3
"""Render a finite-dimensional noncommutative geometry audio experiment.

This is an operator-order prototype, not a claim to implement the full
Kontsevich star product.  Two traceless linear generators deform one closed
base mesh.  Their exponentials are volume-preserving but noncommuting.

The four rendered slots are:

    A: apply A, then B
    B: apply B, then A
    C: exponential of the generator commutator [A, B]
    D: classical simultaneous flow exp(h(A + B))

Every variant retains identical topology and is normalized to the same outer
radius before entering the existing living spectral/IR pipeline.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
import argparse
import json
import time

import numpy as np
from scipy.linalg import expm
import soundfile as sf

from operators.algebraic_surface_pipeline_v1 import (
    AlgebraicSurfaceConfig,
    PipelineRenderConfig,
    marching_tetrahedra,
    run_living_pipeline,
    write_obj,
)
from operators.grasshopper_geometry_bridge_v1 import (
    GrasshopperMeshCandidate,
    MeshValidationPolicy,
)


@dataclass(frozen=True)
class OperatorOrderConfig:
    deformation: float = 0.85
    commutator_gain: float = 1.0
    radius_m: float = 0.25
    ir_energy_norm: float = 0.35
    ir_peak_ceiling: float = 0.25


def reserve_output_fork(
    requested_directory: Path,
) -> tuple[Path, dict[str, object]]:
    """Reserve a new output directory without modifying an earlier render."""
    requested = requested_directory.expanduser().resolve()
    requested.parent.mkdir(parents=True, exist_ok=True)
    if not requested.exists():
        requested.mkdir()
        return requested, {
            "fork_index": 1,
            "requested_directory": str(requested),
            "actual_directory": str(requested),
            "forked_from": None,
        }
    if requested.is_dir() and not any(requested.iterdir()):
        return requested, {
            "fork_index": 1,
            "requested_directory": str(requested),
            "actual_directory": str(requested),
            "forked_from": None,
        }
    if not requested.is_dir():
        raise NotADirectoryError(f"output path is not a directory: {requested}")

    fork_index = 2
    while True:
        candidate = requested.parent / (
            f"{requested.name}_fork_{fork_index:06d}"
        )
        try:
            candidate.mkdir()
        except FileExistsError:
            fork_index += 1
            continue
        return candidate, {
            "fork_index": fork_index,
            "requested_directory": str(requested),
            "actual_directory": str(candidate),
            "forked_from": str(requested),
        }


def deformation_generators() -> tuple[np.ndarray, np.ndarray]:
    """Return fixed traceless, noncommuting 3D deformation generators."""
    generator_a = np.asarray(
        [
            [0.20, 0.34, 0.00],
            [0.00, -0.12, 0.08],
            [0.00, 0.00, -0.08],
        ],
        dtype=np.float64,
    )
    generator_b = np.asarray(
        [
            [-0.10, 0.00, 0.12],
            [0.00, 0.16, 0.30],
            [0.06, 0.00, -0.06],
        ],
        dtype=np.float64,
    )
    if abs(float(np.trace(generator_a))) > 1.0e-12:
        raise AssertionError("generator A must be traceless")
    if abs(float(np.trace(generator_b))) > 1.0e-12:
        raise AssertionError("generator B must be traceless")
    return generator_a, generator_b


def experiment_operators(
    config: OperatorOrderConfig,
) -> dict[str, np.ndarray]:
    """Construct the ordered, commutator, and classical comparison maps."""
    h = float(config.deformation)
    generator_a, generator_b = deformation_generators()
    operator_a = expm(h * generator_a)
    operator_b = expm(h * generator_b)
    commutator = generator_a @ generator_b - generator_b @ generator_a
    return {
        # Column-vector convention: B @ A means A acts first, then B.
        "A_then_B": operator_b @ operator_a,
        "B_then_A": operator_a @ operator_b,
        "commutator": expm(
            float(config.commutator_gain) * (h**2) * commutator
        ),
        "classical": expm(h * (generator_a + generator_b)),
    }


def normalize_geometry(vertices: np.ndarray, radius_m: float) -> np.ndarray:
    result = np.asarray(vertices, dtype=np.float64).copy()
    result -= 0.5 * (np.min(result, axis=0) + np.max(result, axis=0))
    radius = float(np.max(np.linalg.norm(result, axis=1)))
    if radius <= 1.0e-15:
        raise ValueError("deformation collapsed the geometry")
    result *= float(radius_m) / radius
    return result


def apply_operator(
    vertices: np.ndarray,
    operator: np.ndarray,
    radius_m: float,
) -> np.ndarray:
    transformed = np.asarray(vertices, dtype=np.float64) @ operator.T
    return normalize_geometry(transformed, radius_m)


def save_candidate(
    slot_directory: Path,
    slot: str,
    label: str,
    revision: int,
    vertices: np.ndarray,
    faces: np.ndarray,
    operator: np.ndarray,
    config: OperatorOrderConfig,
) -> tuple[GrasshopperMeshCandidate, dict[str, str], dict[str, object]]:
    slot_directory.mkdir(parents=True, exist_ok=True)
    candidate = GrasshopperMeshCandidate(
        revision=revision,
        vertices=vertices,
        faces=faces,
        source="noncommutative_operator_order_v1",
        units="meters",
        metadata={
            "experiment": "finite_dimensional_operator_order",
            "slot": slot,
            "label": label,
            "operator_matrix": operator.tolist(),
            "deformation_parameter": config.deformation,
            "commutator_gain": config.commutator_gain,
            "mathematical_scope": (
                "noncommuting finite-dimensional deformation prototype; "
                "not full Kontsevich deformation quantization"
            ),
        },
    )
    diagnostics = candidate.validate(
        MeshValidationPolicy(
            require_connected=True,
            require_manifold=True,
            require_closed=True,
        )
    )
    stem = f"slot_{slot}_{label}"
    paths = {
        "candidate_json": str(
            candidate.save_json(slot_directory / f"{stem}_candidate.json")
        ),
        "obj_m": str(
            write_obj(
                slot_directory / f"{stem}.obj",
                vertices,
                faces,
                units="meters",
            )
        ),
        "obj_rhino_mm": str(
            write_obj(
                slot_directory / f"{stem}_rhino_mm.obj",
                vertices * 1000.0,
                faces,
                units="millimeters",
            )
        ),
    }
    return candidate, paths, diagnostics.to_dict()


def normalize_ir(
    source: str | Path,
    destination: str | Path,
    *,
    energy_norm: float,
    peak_ceiling: float,
) -> dict[str, float | str]:
    audio, sample_rate = sf.read(str(source), always_2d=True, dtype="float64")
    peak_before = float(np.max(np.abs(audio)))
    energy_before = float(np.sqrt(np.mean(np.sum(audio**2, axis=0))))
    if peak_before <= 1.0e-15 or energy_before <= 1.0e-15:
        raise ValueError(f"IR is silent: {source}")
    scale = min(
        float(energy_norm) / energy_before,
        float(peak_ceiling) / peak_before,
    )
    normalized = audio * scale
    sf.write(str(destination), normalized, sample_rate, subtype="FLOAT")
    return {
        "source": str(source),
        "path": str(destination),
        "scale": float(scale),
        "peak_before": peak_before,
        "peak_after": float(np.max(np.abs(normalized))),
        "energy_before": energy_before,
        "energy_after": float(
            np.sqrt(np.mean(np.sum(normalized**2, axis=0)))
        ),
    }


def run_experiment(
    output_directory: Path,
    operator_config: OperatorOrderConfig,
    surface_config: AlgebraicSurfaceConfig,
    render_config: PipelineRenderConfig,
    *,
    geometry_only: bool = False,
) -> dict[str, object]:
    output_directory, fork_metadata = reserve_output_fork(output_directory)
    base_vertices, faces = marching_tetrahedra(surface_config)
    operators = experiment_operators(operator_config)
    slot_labels = (
        ("A", "A_then_B"),
        ("B", "B_then_A"),
        ("C", "commutator"),
        ("D", "classical"),
    )

    manifest: dict[str, object] = {
        "experiment": "qmw.noncommutative_operator_order.v1",
        "scope": (
            "finite-dimensional noncommuting deformation prototype; "
            "not full Kontsevich deformation quantization"
        ),
        "fork": fork_metadata,
        "operator_config": asdict(operator_config),
        "surface_config": asdict(surface_config),
        "render_config": asdict(render_config),
        "operators": {
            name: matrix.tolist() for name, matrix in operators.items()
        },
        "operator_determinants": {
            name: float(np.linalg.det(matrix))
            for name, matrix in operators.items()
        },
        "commutator_frobenius_norm": float(
            np.linalg.norm(
                deformation_generators()[0] @ deformation_generators()[1]
                - deformation_generators()[1] @ deformation_generators()[0]
            )
        ),
        "slots": {},
    }

    slot_vertices: dict[str, np.ndarray] = {}
    for revision, (slot, label) in enumerate(slot_labels, start=1):
        started = time.monotonic()
        vertices = apply_operator(
            base_vertices, operators[label], operator_config.radius_m
        )
        slot_vertices[slot] = vertices
        slot_directory = output_directory / f"slot_{slot}_{label}"
        candidate, paths, diagnostics = save_candidate(
            slot_directory,
            slot,
            label,
            revision,
            vertices,
            faces,
            operators[label],
            operator_config,
        )
        slot_manifest: dict[str, object] = {
            "slot": slot,
            "label": label,
            "geometry_hash": candidate.geometry_hash,
            "vertex_count": int(len(vertices)),
            "face_count": int(len(faces)),
            "paths": paths,
            "diagnostics": diagnostics,
        }
        if not geometry_only:
            state = run_living_pipeline(
                candidate,
                slot_directory / "living",
                render_config,
            )
            raw_ir = Path(state.paths["ir_wav"])
            normalized_ir = slot_directory / f"slot_{slot}_{label}_normalized.wav"
            normalization = normalize_ir(
                raw_ir,
                normalized_ir,
                energy_norm=operator_config.ir_energy_norm,
                peak_ceiling=operator_config.ir_peak_ceiling,
            )
            slot_manifest["living_state"] = state.to_dict()
            slot_manifest["normalized_ir"] = normalization
        slot_manifest["elapsed_seconds"] = time.monotonic() - started
        manifest["slots"][slot] = slot_manifest

    difference = slot_vertices["A"] - slot_vertices["B"]
    manifest["ordered_geometry_difference"] = {
        "rms_m": float(np.sqrt(np.mean(difference**2))),
        "max_m": float(np.max(np.linalg.norm(difference, axis=1))),
    }
    manifest_path = output_directory / "noncommutative_operator_order_manifest.json"
    manifest["manifest_path"] = str(manifest_path)
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("noncommutative_geometry/operator_order_v1"),
    )
    parser.add_argument("--deformation", type=float, default=0.85)
    parser.add_argument("--commutator-gain", type=float, default=1.0)
    parser.add_argument("--resolution", type=int, default=28)
    parser.add_argument("--radius-m", type=float, default=0.25)
    parser.add_argument("--modes", type=int, default=20)
    parser.add_argument("--wave-speed", type=float, default=120.0)
    parser.add_argument("--t60", type=float, default=4.5)
    parser.add_argument("--ir-duration", type=float, default=8.0)
    parser.add_argument("--sample-rate", type=int, default=48000)
    parser.add_argument("--geometry-only", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    operator_config = OperatorOrderConfig(
        deformation=args.deformation,
        commutator_gain=args.commutator_gain,
        radius_m=args.radius_m,
    )
    surface_config = AlgebraicSurfaceConfig(
        surface="tanglecube",
        parameter=11.8,
        resolution=args.resolution,
        bound=3.0,
        radius_m=args.radius_m,
        revision=1,
    )
    render_config = PipelineRenderConfig(
        modes=args.modes,
        material_model="surface_laplacian",
        effective_wave_speed=args.wave_speed,
        t60_seconds=args.t60,
        ir_duration_seconds=args.ir_duration,
        sample_rate=args.sample_rate,
    )
    manifest = run_experiment(
        args.output.expanduser().resolve(),
        operator_config,
        surface_config,
        render_config,
        geometry_only=args.geometry_only,
    )
    print(json.dumps(manifest, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
