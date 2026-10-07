#!/usr/bin/env python3
"""Emergent Geometry Engine v1.

Autonomous morphogenesis prototype for QuantumSonification.

The engine evolves a two-field Gray-Scott reaction-diffusion system in MLX,
interprets the resulting field as a deformable surface, calculates compact
morphology descriptors, and optionally exports:

- a NumPy-compatible .npz state archive
- a JSON descriptor file
- a Wavefront .obj mesh
- grayscale PNG previews of the morphogen and height fields

The initial version intentionally excludes OSC, audio feedback, and quantum
control so the autonomous morphogenetic behavior can be verified first.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from dataclasses import asdict, dataclass, replace
from pathlib import Path
from typing import Any

try:
    import mlx.core as mx
except ImportError as exc:  # pragma: no cover - environment dependent
    raise SystemExit(
        "MLX is required. Activate your Apple-silicon environment and run: pip install mlx"
    ) from exc

try:
    import numpy as np
except ImportError as exc:  # pragma: no cover
    raise SystemExit("NumPy is required: pip install numpy") from exc


@dataclass(frozen=True)
class MorphogenParameters:
    diffusion_u: float = 0.16
    diffusion_v: float = 0.08
    feed: float = 0.060
    kill: float = 0.062
    dt: float = 1.0


@dataclass(frozen=True)
class GeometryParameters:
    spatial_scale: float = 1.0
    growth_gain: float = 2.5
    edge_gain: float = 0.35
    smoothing: float = 0.08


PRESETS: dict[str, MorphogenParameters] = {
    # Stable, readable starting families rather than an exhaustive catalog.
    "labyrinth": MorphogenParameters(feed=0.0367, kill=0.0649),
    "cellular": MorphogenParameters(feed=0.0545, kill=0.0620),
    "coral_growth": MorphogenParameters(feed=0.0250, kill=0.0600),
}


def _scalar(value: mx.array) -> float:
    """Materialize an MLX scalar as a Python float."""
    return float(value.item())


def _to_numpy(value: mx.array) -> np.ndarray:
    """Materialize an MLX array as float32 NumPy data."""
    return np.asarray(value, dtype=np.float32)


def laplacian(field: mx.array) -> mx.array:
    """Periodic 9-point Laplacian suitable for reaction-diffusion fields."""
    axial = (
        mx.roll(field, 1, axis=0)
        + mx.roll(field, -1, axis=0)
        + mx.roll(field, 1, axis=1)
        + mx.roll(field, -1, axis=1)
    )
    diagonal = (
        mx.roll(mx.roll(field, 1, axis=0), 1, axis=1)
        + mx.roll(mx.roll(field, 1, axis=0), -1, axis=1)
        + mx.roll(mx.roll(field, -1, axis=0), 1, axis=1)
        + mx.roll(mx.roll(field, -1, axis=0), -1, axis=1)
    )
    return -field + 0.20 * axial + 0.05 * diagonal


class MorphogenField:
    def __init__(
        self,
        size: int,
        parameters: MorphogenParameters,
        seed: int = 23,
        seed_count: int = 14,
        seed_radius: int = 4,
    ) -> None:
        if size < 32:
            raise ValueError("size must be at least 32")
        if seed_count < 1:
            raise ValueError("seed_count must be positive")
        if seed_radius < 1:
            raise ValueError("seed_radius must be positive")

        self.size = int(size)
        self.parameters = parameters
        self.seed_value = int(seed)
        self.seed_count = int(seed_count)
        self.seed_radius = int(seed_radius)
        self.u: mx.array
        self.v: mx.array
        self.reset()

    def reset(self) -> None:
        rng = np.random.default_rng(self.seed_value)
        u = np.ones((self.size, self.size), dtype=np.float32)
        v = np.zeros((self.size, self.size), dtype=np.float32)

        margin = max(self.seed_radius + 2, self.size // 12)
        for _ in range(self.seed_count):
            cy = int(rng.integers(margin, self.size - margin))
            cx = int(rng.integers(margin, self.size - margin))
            radius = int(rng.integers(max(2, self.seed_radius // 2), self.seed_radius + 1))
            yy, xx = np.ogrid[: self.size, : self.size]
            mask = (xx - cx) ** 2 + (yy - cy) ** 2 <= radius**2
            u[mask] = rng.uniform(0.35, 0.55)
            v[mask] = rng.uniform(0.65, 0.95)

        # A small perturbation breaks perfect symmetry without dominating growth.
        u += rng.normal(0.0, 0.006, u.shape).astype(np.float32)
        v += rng.normal(0.0, 0.006, v.shape).astype(np.float32)
        self.u = mx.array(np.clip(u, 0.0, 1.0))
        self.v = mx.array(np.clip(v, 0.0, 1.0))
        mx.eval(self.u, self.v)

    def step(self, iterations: int = 1) -> None:
        p = self.parameters
        for _ in range(iterations):
            lu = laplacian(self.u)
            lv = laplacian(self.v)
            reaction = self.u * self.v * self.v

            du = p.diffusion_u * lu - reaction + p.feed * (1.0 - self.u)
            dv = p.diffusion_v * lv + reaction - (p.feed + p.kill) * self.v

            self.u = mx.clip(self.u + p.dt * du, 0.0, 1.0)
            self.v = mx.clip(self.v + p.dt * dv, 0.0, 1.0)
        mx.eval(self.u, self.v)


class EmergentSurface:
    def __init__(self, size: int, parameters: GeometryParameters) -> None:
        self.size = int(size)
        self.parameters = parameters
        self.height = mx.zeros((size, size), dtype=mx.float32)
        self.previous_height = self.height

    def update_from_fields(self, u: mx.array, v: mx.array) -> None:
        p = self.parameters
        raw = p.growth_gain * (v - 0.42 * (1.0 - u)) + p.edge_gain * laplacian(v)
        # Low-pass persistence keeps the surface developmental rather than jittery.
        next_height = (1.0 - p.smoothing) * raw + p.smoothing * self.height
        self.previous_height = self.height
        self.height = next_height
        mx.eval(self.height)

    def descriptors(self, v: mx.array) -> dict[str, float | int]:
        h = self.height
        dx = 0.5 * (mx.roll(h, -1, axis=1) - mx.roll(h, 1, axis=1))
        dy = 0.5 * (mx.roll(h, -1, axis=0) - mx.roll(h, 1, axis=0))
        curvature = laplacian(h)
        velocity = h - self.previous_height

        area_density = mx.sqrt(1.0 + dx * dx + dy * dy)
        grad_energy_x = mx.mean(dx * dx)
        grad_energy_y = mx.mean(dy * dy)
        anisotropy = mx.abs(grad_energy_x - grad_energy_y) / (
            grad_energy_x + grad_energy_y + 1e-8
        )

        # Binary occupancy entropy provides a robust first pattern-complexity metric.
        occupancy = mx.mean((v > mx.mean(v)).astype(mx.float32))
        occ = mx.clip(occupancy, 1e-6, 1.0 - 1e-6)
        binary_entropy = -(occ * mx.log2(occ) + (1.0 - occ) * mx.log2(1.0 - occ))

        return {
            "surface_area": _scalar(mx.sum(area_density))
            * (self.parameters.spatial_scale**2),
            "mean_height": _scalar(mx.mean(h)),
            "height_variance": _scalar(mx.var(h)),
            "mean_abs_curvature": _scalar(mx.mean(mx.abs(curvature))),
            "curvature_variance": _scalar(mx.var(curvature)),
            "pattern_entropy": _scalar(binary_entropy),
            "anisotropy": _scalar(anisotropy),
            "growth_velocity": _scalar(mx.mean(mx.abs(velocity))),
            "morphogen_u_mean": 0.0,  # filled by engine
            "morphogen_v_mean": _scalar(mx.mean(v)),
            "morphogen_v_max": _scalar(mx.max(v)),
        }

    def export_obj(self, path: Path) -> None:
        height = _to_numpy(self.height)
        n = self.size
        scale = self.parameters.spatial_scale
        half = 0.5 * (n - 1)

        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as handle:
            handle.write("# Emergent Geometry Engine v1\n")
            handle.write(f"# grid {n} x {n}\n")
            for y in range(n):
                py = (y - half) * scale
                for x in range(n):
                    px = (x - half) * scale
                    handle.write(f"v {px:.7f} {py:.7f} {height[y, x]:.7f}\n")

            for y in range(n - 1):
                for x in range(n - 1):
                    a = y * n + x + 1
                    b = a + 1
                    c = a + n
                    d = c + 1
                    handle.write(f"f {a} {b} {d}\n")
                    handle.write(f"f {a} {d} {c}\n")


class EmergentGeometryEngine:
    def __init__(
        self,
        size: int,
        morphogen: MorphogenParameters,
        geometry: GeometryParameters,
        seed: int,
        seed_count: int,
        seed_radius: int,
        developmental_field: Any | None = None,
    ) -> None:
        self.field = (
            MorphogenField(
                size=size,
                parameters=morphogen,
                seed=seed,
                seed_count=seed_count,
                seed_radius=seed_radius,
            )
            if developmental_field is None
            else developmental_field
        )
        if int(self.field.size) != int(size):
            raise ValueError(
                "developmental field and emergent surface sizes must match"
            )
        self.surface = EmergentSurface(size=size, parameters=geometry)
        self.step_count = 0
        primary, secondary = self._geometry_fields()
        self.surface.update_from_fields(primary, secondary)

    def _geometry_fields(self) -> tuple[mx.array, mx.array]:
        if hasattr(self.field, "geometry_fields"):
            primary, secondary = self.field.geometry_fields()
            return primary, secondary
        return self.field.u, self.field.v

    def step(self, iterations: int = 1) -> None:
        self.field.step(iterations)
        primary, secondary = self._geometry_fields()
        self.surface.update_from_fields(primary, secondary)
        self.step_count += iterations

    def descriptors(self) -> dict[str, Any]:
        primary, secondary = self._geometry_fields()
        data = self.surface.descriptors(secondary)
        data["morphogen_u_mean"] = _scalar(mx.mean(primary))
        data["developmental_model"] = getattr(
            self.field, "model_name", "gray_scott"
        )
        data["step"] = self.step_count
        data["size"] = self.field.size
        return data

    def save_state(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        primary, secondary = self._geometry_fields()
        np.savez_compressed(
            path,
            u=_to_numpy(primary),
            v=_to_numpy(secondary),
            primary_field=_to_numpy(primary),
            secondary_field=_to_numpy(secondary),
            developmental_model=np.asarray(
                getattr(self.field, "model_name", "gray_scott")
            ),
            height=_to_numpy(self.surface.height),
            step=np.asarray(self.step_count, dtype=np.int64),
        )

    def save_descriptors(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "engine": "emergent_geometry_engine_v1",
            "morphogen_parameters": (
                self.field.parameter_dict()
                if hasattr(self.field, "parameter_dict")
                else asdict(self.field.parameters)
            ),
            "geometry_parameters": asdict(self.surface.parameters),
            "descriptors": self.descriptors(),
        }
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def save_pngs(self, output_prefix: Path) -> None:
        try:
            from PIL import Image
        except ImportError:
            print("PNG export skipped: install Pillow with `pip install pillow`.", file=sys.stderr)
            return

        output_prefix.parent.mkdir(parents=True, exist_ok=True)
        for suffix, data in (
            ("v", _to_numpy(self._geometry_fields()[1])),
            ("height", _to_numpy(self.surface.height)),
        ):
            lo = float(np.min(data))
            hi = float(np.max(data))
            normalized = (data - lo) / max(hi - lo, 1e-8)
            image = Image.fromarray(np.uint8(np.clip(normalized, 0.0, 1.0) * 255), mode="L")
            image.save(output_prefix.with_name(f"{output_prefix.name}_{suffix}.png"))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--preset", choices=sorted(PRESETS), default="labyrinth")
    parser.add_argument("--size", type=int, default=192)
    parser.add_argument("--steps", type=int, default=12000)
    parser.add_argument("--chunk", type=int, default=100)
    parser.add_argument("--seed", type=int, default=23)
    parser.add_argument("--seed-count", type=int, default=14)
    parser.add_argument("--seed-radius", type=int, default=4)
    parser.add_argument("--feed", type=float)
    parser.add_argument("--kill", type=float)
    parser.add_argument("--diffusion-u", type=float)
    parser.add_argument("--diffusion-v", type=float)
    parser.add_argument("--dt", type=float)
    parser.add_argument("--growth-gain", type=float, default=2.5)
    parser.add_argument("--edge-gain", type=float, default=0.35)
    parser.add_argument("--smoothing", type=float, default=0.08)
    parser.add_argument("--spatial-scale", type=float, default=1.0)
    parser.add_argument("--report-every", type=int, default=1000)
    parser.add_argument("--export-state", type=Path)
    parser.add_argument("--export-descriptors", type=Path)
    parser.add_argument("--export-obj", type=Path)
    parser.add_argument("--export-png-prefix", type=Path)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    if args.steps < 0 or args.chunk < 1:
        raise SystemExit("--steps must be nonnegative and --chunk must be positive")

    morphogen = PRESETS[args.preset]
    overrides = {
        "feed": args.feed,
        "kill": args.kill,
        "diffusion_u": args.diffusion_u,
        "diffusion_v": args.diffusion_v,
        "dt": args.dt,
    }
    morphogen = replace(
        morphogen, **{key: value for key, value in overrides.items() if value is not None}
    )
    geometry = GeometryParameters(
        spatial_scale=args.spatial_scale,
        growth_gain=args.growth_gain,
        edge_gain=args.edge_gain,
        smoothing=args.smoothing,
    )

    engine = EmergentGeometryEngine(
        size=args.size,
        morphogen=morphogen,
        geometry=geometry,
        seed=args.seed,
        seed_count=args.seed_count,
        seed_radius=args.seed_radius,
    )

    print("Emergent Geometry Engine v1")
    print(f"  preset: {args.preset}")
    print(f"  field:  {args.size} x {args.size}")
    print(f"  steps:  {args.steps}")
    print(
        "  Gray-Scott: "
        f"Du={morphogen.diffusion_u:.5f} Dv={morphogen.diffusion_v:.5f} "
        f"F={morphogen.feed:.5f} k={morphogen.kill:.5f} dt={morphogen.dt:.3f}"
    )

    remaining = args.steps
    next_report = args.report_every if args.report_every > 0 else math.inf
    while remaining > 0:
        batch = min(args.chunk, remaining)
        engine.step(batch)
        remaining -= batch
        if engine.step_count >= next_report or remaining == 0:
            d = engine.descriptors()
            print(
                f"  step {engine.step_count:6d} | "
                f"v_mean={d['morphogen_v_mean']:.5f} "
                f"entropy={d['pattern_entropy']:.4f} "
                f"curvature={d['mean_abs_curvature']:.6f} "
                f"growth={d['growth_velocity']:.7f}"
            )
            while next_report <= engine.step_count:
                next_report += args.report_every

    descriptors = engine.descriptors()
    print("\nFinal descriptors")
    print(json.dumps(descriptors, indent=2))

    if args.export_state:
        engine.save_state(args.export_state)
        print(f"state:       {args.export_state}")
    if args.export_descriptors:
        engine.save_descriptors(args.export_descriptors)
        print(f"descriptors: {args.export_descriptors}")
    if args.export_obj:
        engine.surface.export_obj(args.export_obj)
        print(f"mesh:        {args.export_obj}")
    if args.export_png_prefix:
        engine.save_pngs(args.export_png_prefix)
        print(f"images:      {args.export_png_prefix}_v.png / _height.png")


if __name__ == "__main__":
    main()
