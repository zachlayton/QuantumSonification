#!/usr/bin/env python3
"""Measure standalone engine stage costs without OSC or sleeping."""

from __future__ import annotations

import argparse
from pathlib import Path
import statistics
import sys
import time

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from quantum_resonant_membrane.engine import QuantumResonantMembraneEngine


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--frames", type=int, default=600)
    parser.add_argument("--rate-hz", type=float, default=30.0)
    parser.add_argument("--compare-mlx", action="store_true")
    args = parser.parse_args()
    if args.frames < 1 or args.rate_hz <= 0:
        parser.error("frames and rate must be positive")
    engine = QuantumResonantMembraneEngine(modes=20)
    dt = 1.0 / args.rate_hz
    for _ in range(60):
        engine.step(dt)
    samples = {name: [] for name in ("density", "terrain", "flow", "membrane", "total")}
    for _ in range(args.frames):
        start = time.perf_counter_ns()
        density = engine.density_engine.step(dt)
        mark_density = time.perf_counter_ns()
        terrain = engine.terrain.step(density.rho, time=density.time, dt=dt)
        mark_terrain = time.perf_counter_ns()
        flow = engine.flow.observe(
            density.rho,
            density.hamiltonian,
            engine.geometry,
            time=density.time,
            dt=dt,
        )
        mark_flow = time.perf_counter_ns()
        engine.membrane.step(terrain, flow, dt=dt)
        end = time.perf_counter_ns()
        marks = (start, mark_density, mark_terrain, mark_flow, end)
        for name, left, right in zip(
            ("density", "terrain", "flow", "membrane"), marks, marks[1:]
        ):
            samples[name].append((right - left) / 1.0e6)
        samples["total"].append((end - start) / 1.0e6)
    budget = 1000.0 / args.rate_hz
    for name, values in samples.items():
        print(
            f"{name:9s} median={statistics.median(values):8.4f} ms "
            f"p95={sorted(values)[int(0.95 * (len(values) - 1))]:8.4f} ms"
        )
    total = statistics.mean(samples["total"])
    print(f"frame budget={budget:.4f} ms mean utilization={100.0 * total / budget:.2f}%")
    if args.compare_mlx:
        try:
            import mlx.core as mx
        except (ImportError, RuntimeError) as error:
            print(f"MLX comparison unavailable: {error}")
            return 0
        rng = np.random.default_rng(7)
        source = rng.normal(size=(20, 20))
        matrix = source.T @ source + np.eye(20)
        vector = rng.normal(size=20)
        repeats = 2000
        started = time.perf_counter()
        for _ in range(repeats):
            np.linalg.eigvalsh(matrix)
            np.linalg.solve(matrix, vector)
        numpy_ms = 1000.0 * (time.perf_counter() - started) / repeats
        try:
            mlx_matrix = mx.array(matrix)
            mlx_vector = mx.array(vector)
            mx.eval(mlx_matrix, mlx_vector)
            started = time.perf_counter()
            for _ in range(repeats):
                eigenvalues, _ = mx.linalg.eigh(mlx_matrix, stream=mx.cpu)
                solution = mx.linalg.solve(mlx_matrix, mlx_vector, stream=mx.cpu)
                mx.eval(eigenvalues, solution)
            mlx_ms = 1000.0 * (time.perf_counter() - started) / repeats
        except (RuntimeError, ValueError) as error:
            print(f"MLX 20x20 comparison unavailable: {error}")
            return 0
        print(f"20x20 eig+solve NumPy={numpy_ms:.4f} ms MLX={mlx_ms:.4f} ms")
        print(f"MLX/NumPy latency ratio={mlx_ms / numpy_ms:.2f}x")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
