#!/usr/bin/env python3
"""
procedural_chamber_mlx_v1.py

A self-contained MLX prototype for generating a hypothetical procedural
reverberation chamber and rendering a stereo impulse response from it.

The chamber pipeline is:

    Platonic mesh
      -> recursive triangular subdivision
      -> rounded polyhedral interpolation
      -> deterministic fractal deformation
      -> weighted surface graph Laplacian
      -> geometry-conditioned orthogonal FDN
      -> frequency-domain MLX solve
      -> stereo impulse response + OBJ + JSON

No NumPy dependency is required. Mesh topology bookkeeping and file I/O use
Python's standard library; dense numerical work uses mlx.core.

This is a structural / musical acoustics model rather than a boundary-element,
finite-difference, or geometrical ray-tracing solver. The exported mesh and
acoustic descriptors are designed to support later physically rigorous stages.
"""

from __future__ import annotations

import argparse
import json
import math
import random
import struct
import sys
import wave
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, Sequence

try:
    import mlx.core as mx
except ImportError as exc:  # pragma: no cover - exercised on systems without MLX
    raise SystemExit(
        "MLX is required. In your active environment run:  pip install -U mlx"
    ) from exc


VERSION = "1.0.0"
SPEED_OF_SOUND_M_S = 343.0


# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------


@dataclass(frozen=True)
class ChamberConfig:
    shape: str = "icosa"
    subdivisions: int = 2
    roundedness: float = 0.18
    radius_m: float = 7.5
    deformation: float = 0.34
    fractal_octaves: int = 5
    lacunarity: float = 2.03
    persistence: float = 0.52
    base_frequency: float = 1.15
    twist: float = 0.16
    porosity: float = 0.20
    anisotropy_x: float = 1.00
    anisotropy_y: float = 0.93
    anisotropy_z: float = 1.12
    seed: int = 271828


@dataclass(frozen=True)
class AcousticConfig:
    sample_rate: int = 48_000
    duration_s: float = 8.0
    rt60_s: float = 6.5
    hf_cutoff_hz: float = 9_500.0
    reflection: float = 0.78
    n_lines: int = 16
    n_early_reflections: int = 28
    early_mix: float = 0.34
    late_mix: float = 0.82
    direct_mix: float = 0.0
    chunk_bins: int = 1024
    output_ceiling: float = 0.95


@dataclass(frozen=True)
class RenderConfig:
    output_dir: str = "procedural_chamber_output"
    name: str = "procedural_chamber_mlx_v1"
    device: str = "auto"
    render_ir: bool = True


@dataclass
class Mesh:
    vertices: mx.array
    faces: list[tuple[int, int, int]]


@dataclass
class GeometryAnalysis:
    surface_area_m2: float
    volume_m3: float
    mean_radius_m: float
    radius_std_m: float
    roughness: float
    sphericity: float
    mean_edge_m: float
    min_edge_m: float
    max_edge_m: float
    vertex_count: int
    face_count: int
    edge_count: int


@dataclass
class SpectralAnalysis:
    eigenvalues: mx.array
    eigenvectors: mx.array
    selected_eigenvalues: mx.array


@dataclass
class AcousticModel:
    delay_samples: list[int]
    delay_ms: list[float]
    path_lengths_m: list[float]
    hf_cutoffs_hz: list[float]
    feedback_matrix: mx.array
    input_vector: mx.array
    output_vector_left: mx.array
    output_vector_right: mx.array
    early_delay_samples_left: list[int]
    early_delay_samples_right: list[int]
    early_gains_left: list[float]
    early_gains_right: list[float]
    source_position_m: list[float]
    listener_position_m: list[float]


# -----------------------------------------------------------------------------
# Utility helpers
# -----------------------------------------------------------------------------


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def next_power_of_two(n: int) -> int:
    if n <= 1:
        return 1
    return 1 << (n - 1).bit_length()


def normalize_python(v: Sequence[float]) -> tuple[float, float, float]:
    mag = math.sqrt(sum(float(x) * float(x) for x in v))
    if mag <= 1.0e-12:
        return (1.0, 0.0, 0.0)
    return tuple(float(x) / mag for x in v)  # type: ignore[return-value]


def normalize_mx(v: mx.array, axis: int | None = None, eps: float = 1.0e-8) -> mx.array:
    norm = mx.linalg.norm(v, axis=axis, keepdims=axis is not None)
    return v / mx.maximum(norm, eps)


def mx_float(value: mx.array) -> float:
    mx.eval(value)
    return float(value.item())


def mx_int(value: mx.array) -> int:
    mx.eval(value)
    return int(value.item())


def fibonacci_sphere(count: int) -> list[tuple[float, float, float]]:
    directions: list[tuple[float, float, float]] = []
    golden_angle = math.pi * (3.0 - math.sqrt(5.0))
    for i in range(count):
        y = 1.0 - (2.0 * (i + 0.5) / count)
        radius = math.sqrt(max(0.0, 1.0 - y * y))
        theta = golden_angle * i
        directions.append((math.cos(theta) * radius, y, math.sin(theta) * radius))
    return directions


def is_prime(n: int) -> bool:
    if n < 2:
        return False
    if n in (2, 3):
        return True
    if n % 2 == 0:
        return False
    limit = int(math.sqrt(n)) + 1
    for divisor in range(3, limit, 2):
        if n % divisor == 0:
            return False
    return True


def nearest_unique_prime(target: int, used: set[int], minimum: int = 127) -> int:
    target = max(minimum, int(target))
    if target % 2 == 0:
        target += 1
    radius = 0
    while True:
        candidates = (target + radius, target - radius) if radius else (target,)
        for candidate in candidates:
            if candidate >= minimum and candidate not in used and is_prime(candidate):
                used.add(candidate)
                return candidate
        radius += 2


def set_device(requested: str) -> str:
    requested = requested.lower()
    if requested not in {"auto", "cpu", "gpu"}:
        raise ValueError("device must be auto, cpu, or gpu")

    if requested == "cpu":
        mx.set_default_device(mx.cpu)
        return "cpu"

    if requested == "gpu":
        try:
            available = bool(mx.metal.is_available())
        except Exception:
            available = False
        if not available:
            raise RuntimeError("MLX Metal GPU is unavailable on this machine.")
        mx.set_default_device(mx.gpu)
        return "gpu"

    try:
        if mx.metal.is_available():
            mx.set_default_device(mx.gpu)
            return "gpu"
    except Exception:
        pass

    mx.set_default_device(mx.cpu)
    return "cpu"


# -----------------------------------------------------------------------------
# Platonic meshes and subdivision
# -----------------------------------------------------------------------------


def platonic_mesh(shape: str) -> tuple[list[tuple[float, float, float]], list[tuple[int, int, int]]]:
    shape = shape.lower()

    if shape == "tetra":
        vertices = [
            (1.0, 1.0, 1.0),
            (-1.0, -1.0, 1.0),
            (-1.0, 1.0, -1.0),
            (1.0, -1.0, -1.0),
        ]
        faces = [(0, 2, 1), (0, 1, 3), (0, 3, 2), (1, 2, 3)]
        return vertices, faces

    if shape == "cube":
        vertices = [
            (-1.0, -1.0, -1.0),
            (1.0, -1.0, -1.0),
            (1.0, 1.0, -1.0),
            (-1.0, 1.0, -1.0),
            (-1.0, -1.0, 1.0),
            (1.0, -1.0, 1.0),
            (1.0, 1.0, 1.0),
            (-1.0, 1.0, 1.0),
        ]
        faces = [
            (0, 2, 1), (0, 3, 2),
            (4, 5, 6), (4, 6, 7),
            (0, 1, 5), (0, 5, 4),
            (1, 2, 6), (1, 6, 5),
            (2, 3, 7), (2, 7, 6),
            (3, 0, 4), (3, 4, 7),
        ]
        return vertices, faces

    if shape == "octa":
        vertices = [
            (1.0, 0.0, 0.0),
            (-1.0, 0.0, 0.0),
            (0.0, 1.0, 0.0),
            (0.0, -1.0, 0.0),
            (0.0, 0.0, 1.0),
            (0.0, 0.0, -1.0),
        ]
        faces = [
            (0, 2, 4), (2, 1, 4), (1, 3, 4), (3, 0, 4),
            (2, 0, 5), (1, 2, 5), (3, 1, 5), (0, 3, 5),
        ]
        return vertices, faces

    if shape == "icosa":
        phi = (1.0 + math.sqrt(5.0)) / 2.0
        vertices = [
            (-1.0, phi, 0.0), (1.0, phi, 0.0),
            (-1.0, -phi, 0.0), (1.0, -phi, 0.0),
            (0.0, -1.0, phi), (0.0, 1.0, phi),
            (0.0, -1.0, -phi), (0.0, 1.0, -phi),
            (phi, 0.0, -1.0), (phi, 0.0, 1.0),
            (-phi, 0.0, -1.0), (-phi, 0.0, 1.0),
        ]
        faces = [
            (0, 11, 5), (0, 5, 1), (0, 1, 7), (0, 7, 10), (0, 10, 11),
            (1, 5, 9), (5, 11, 4), (11, 10, 2), (10, 7, 6), (7, 1, 8),
            (3, 9, 4), (3, 4, 2), (3, 2, 6), (3, 6, 8), (3, 8, 9),
            (4, 9, 5), (2, 4, 11), (6, 2, 10), (8, 6, 7), (9, 8, 1),
        ]
        return vertices, faces

    raise ValueError(f"Unsupported shape: {shape}. Choose tetra, cube, octa, or icosa.")


def subdivide_mesh(
    vertices: list[tuple[float, float, float]],
    faces: list[tuple[int, int, int]],
    levels: int,
) -> tuple[list[tuple[float, float, float]], list[tuple[int, int, int]]]:
    if levels < 0:
        raise ValueError("subdivisions must be >= 0")

    working_vertices = list(vertices)
    working_faces = list(faces)

    for _ in range(levels):
        midpoint_cache: dict[tuple[int, int], int] = {}
        next_faces: list[tuple[int, int, int]] = []

        def midpoint_index(a: int, b: int) -> int:
            edge = (a, b) if a < b else (b, a)
            cached = midpoint_cache.get(edge)
            if cached is not None:
                return cached
            va = working_vertices[a]
            vb = working_vertices[b]
            midpoint = (
                0.5 * (va[0] + vb[0]),
                0.5 * (va[1] + vb[1]),
                0.5 * (va[2] + vb[2]),
            )
            idx = len(working_vertices)
            working_vertices.append(midpoint)
            midpoint_cache[edge] = idx
            return idx

        for a, b, c in working_faces:
            ab = midpoint_index(a, b)
            bc = midpoint_index(b, c)
            ca = midpoint_index(c, a)
            next_faces.extend(
                [(a, ab, ca), (b, bc, ab), (c, ca, bc), (ab, bc, ca)]
            )

        working_faces = next_faces

    return working_vertices, working_faces


def unique_edges(faces: Iterable[tuple[int, int, int]]) -> list[tuple[int, int]]:
    edges: set[tuple[int, int]] = set()
    for a, b, c in faces:
        for u, v in ((a, b), (b, c), (c, a)):
            edges.add((u, v) if u < v else (v, u))
    return sorted(edges)


# -----------------------------------------------------------------------------
# MLX geometry construction and analysis
# -----------------------------------------------------------------------------


def construct_chamber_mesh(config: ChamberConfig) -> Mesh:
    if config.subdivisions > 3:
        raise ValueError(
            "v1 limits subdivisions to 3 because it uses a dense graph eigensolve."
        )
    if not 0.0 <= config.roundedness <= 1.0:
        raise ValueError("roundedness must be in [0, 1]")
    if config.fractal_octaves < 1:
        raise ValueError("fractal_octaves must be >= 1")
    if config.radius_m <= 0.0:
        raise ValueError("radius_m must be positive")

    base_vertices, base_faces = platonic_mesh(config.shape)
    subdivided_vertices, subdivided_faces = subdivide_mesh(
        base_vertices, base_faces, config.subdivisions
    )

    vertices = mx.array(subdivided_vertices, dtype=mx.float32)
    vertices = vertices - mx.mean(vertices, axis=0, keepdims=True)

    # Blend the subdivided polyhedron toward its circumsphere while retaining
    # the base solid's planar character at roundedness=0.
    radii = mx.linalg.norm(vertices, axis=1, keepdims=True)
    target_radius = mx.mean(mx.linalg.norm(mx.array(base_vertices, dtype=mx.float32), axis=1))
    spherical = vertices / mx.maximum(radii, 1.0e-8) * target_radius
    vertices = (1.0 - config.roundedness) * vertices + config.roundedness * spherical

    # Axis deformation gives the hypothetical chamber a non-isotropic body.
    axis_scale = mx.array(
        [config.anisotropy_x, config.anisotropy_y, config.anisotropy_z],
        dtype=mx.float32,
    )
    vertices = vertices * axis_scale

    # Deterministic fractal wave field. Python generates the reproducible field
    # parameters; all vertex-field evaluation is performed by MLX.
    rng = random.Random(config.seed)
    wave_vectors: list[tuple[float, float, float]] = []
    wave_phases: list[float] = []
    amplitudes: list[float] = []

    for octave in range(config.fractal_octaves):
        direction = normalize_python(
            (
                rng.uniform(-1.0, 1.0),
                rng.uniform(-1.0, 1.0),
                rng.uniform(-1.0, 1.0),
            )
        )
        frequency = config.base_frequency * (config.lacunarity ** octave)
        wave_vectors.append(tuple(frequency * x for x in direction))
        wave_phases.append(rng.uniform(-math.pi, math.pi))
        amplitudes.append(config.persistence ** octave)

    k = mx.array(wave_vectors, dtype=mx.float32)
    phase = mx.array(wave_phases, dtype=mx.float32)
    amplitude = mx.array(amplitudes, dtype=mx.float32)
    field = mx.sum(mx.sin(vertices @ k.T + phase[None, :]) * amplitude[None, :], axis=1)
    field = field / mx.maximum(mx.sum(mx.abs(amplitude)), 1.0e-8)

    # A secondary multiplicative field creates recessed pockets. It changes
    # boundary depth without claiming to create topological holes in v1.
    pocket_field = (
        mx.sin(vertices[:, 0] * 2.71 + 0.31)
        * mx.sin(vertices[:, 1] * 3.17 - 0.77)
        * mx.sin(vertices[:, 2] * 2.39 + 1.11)
    )
    pockets = 0.5 * (1.0 + mx.tanh(4.0 * (pocket_field - 0.18)))

    radial_scale = (
        1.0
        + config.deformation * field
        - 0.18 * config.porosity * pockets
    )
    radial_scale = mx.maximum(radial_scale, 0.30)
    vertices = vertices * radial_scale[:, None]

    # Twist about z, with a mild fractal phase term.
    twist_angle = config.twist * (
        vertices[:, 2] + 0.35 * mx.sin(1.7 * vertices[:, 1] + field)
    )
    cos_a = mx.cos(twist_angle)
    sin_a = mx.sin(twist_angle)
    x = vertices[:, 0] * cos_a - vertices[:, 1] * sin_a
    y = vertices[:, 0] * sin_a + vertices[:, 1] * cos_a
    vertices = mx.stack([x, y, vertices[:, 2]], axis=1)

    # Scale to physical units: radius_m is the maximum boundary radius.
    max_radius = mx.max(mx.linalg.norm(vertices, axis=1))
    vertices = vertices * (config.radius_m / mx.maximum(max_radius, 1.0e-8))
    mx.eval(vertices)

    if vertices.shape[0] < 17:
        raise ValueError(
            "The selected shape/subdivision has fewer than 17 vertices. "
            "Increase subdivisions so a 16-line spectral model can be formed."
        )

    return Mesh(vertices=vertices, faces=subdivided_faces)


def face_vertex_arrays(mesh: Mesh) -> tuple[mx.array, mx.array, mx.array]:
    faces = mx.array(mesh.faces, dtype=mx.int32)
    v0 = mx.take(mesh.vertices, faces[:, 0], axis=0)
    v1 = mx.take(mesh.vertices, faces[:, 1], axis=0)
    v2 = mx.take(mesh.vertices, faces[:, 2], axis=0)
    return v0, v1, v2


def cross_rows(a: mx.array, b: mx.array) -> mx.array:
    return mx.stack(
        [
            a[:, 1] * b[:, 2] - a[:, 2] * b[:, 1],
            a[:, 2] * b[:, 0] - a[:, 0] * b[:, 2],
            a[:, 0] * b[:, 1] - a[:, 1] * b[:, 0],
        ],
        axis=1,
    )


def analyze_geometry(mesh: Mesh) -> GeometryAnalysis:
    v0, v1, v2 = face_vertex_arrays(mesh)
    cross = cross_rows(v1 - v0, v2 - v0)
    face_areas = 0.5 * mx.linalg.norm(cross, axis=1)
    surface_area = mx.sum(face_areas)

    # Absolute signed tetrahedral volume relative to the origin.
    triple = mx.sum(v0 * cross_rows(v1, v2), axis=1)
    volume = mx.abs(mx.sum(triple) / 6.0)

    radii = mx.linalg.norm(mesh.vertices, axis=1)
    mean_radius = mx.mean(radii)
    radius_std = mx.std(radii)
    roughness = radius_std / mx.maximum(mean_radius, 1.0e-8)

    area_safe = mx.maximum(surface_area, 1.0e-8)
    sphericity = (
        (math.pi ** (1.0 / 3.0))
        * mx.power(6.0 * mx.maximum(volume, 1.0e-8), 2.0 / 3.0)
        / area_safe
    )

    edges = unique_edges(mesh.faces)
    edge_idx = mx.array(edges, dtype=mx.int32)
    edge_a = mx.take(mesh.vertices, edge_idx[:, 0], axis=0)
    edge_b = mx.take(mesh.vertices, edge_idx[:, 1], axis=0)
    edge_lengths = mx.linalg.norm(edge_b - edge_a, axis=1)

    values = [
        surface_area,
        volume,
        mean_radius,
        radius_std,
        roughness,
        sphericity,
        mx.mean(edge_lengths),
        mx.min(edge_lengths),
        mx.max(edge_lengths),
    ]
    mx.eval(*values)

    return GeometryAnalysis(
        surface_area_m2=float(surface_area.item()),
        volume_m3=float(volume.item()),
        mean_radius_m=float(mean_radius.item()),
        radius_std_m=float(radius_std.item()),
        roughness=float(roughness.item()),
        sphericity=float(sphericity.item()),
        mean_edge_m=float(mx.mean(edge_lengths).item()),
        min_edge_m=float(mx.min(edge_lengths).item()),
        max_edge_m=float(mx.max(edge_lengths).item()),
        vertex_count=int(mesh.vertices.shape[0]),
        face_count=len(mesh.faces),
        edge_count=len(edges),
    )


def build_weighted_normalized_laplacian(mesh: Mesh) -> mx.array:
    vertices_list = mesh.vertices.tolist()
    edges = unique_edges(mesh.faces)
    count = len(vertices_list)
    flat = [0.0] * (count * count)

    lengths: list[float] = []
    for a, b in edges:
        va = vertices_list[a]
        vb = vertices_list[b]
        length = math.sqrt(sum((float(vb[k]) - float(va[k])) ** 2 for k in range(3)))
        lengths.append(length)

    mean_length = sum(lengths) / max(1, len(lengths))
    for (a, b), length in zip(edges, lengths):
        # Gaussian proximity weight. Deformation therefore changes the graph
        # spectrum even when the mesh topology remains fixed.
        ratio = length / max(mean_length, 1.0e-8)
        weight = math.exp(-0.5 * ratio * ratio)
        flat[a * count + b] = weight
        flat[b * count + a] = weight

    adjacency = mx.reshape(mx.array(flat, dtype=mx.float32), (count, count))
    degree = mx.sum(adjacency, axis=1)
    inv_sqrt_degree = mx.rsqrt(mx.maximum(degree, 1.0e-8))
    normalized_adjacency = (
        inv_sqrt_degree[:, None]
        * adjacency
        * inv_sqrt_degree[None, :]
    )
    laplacian = mx.eye(count, dtype=mx.float32) - normalized_adjacency
    mx.eval(laplacian)
    return laplacian


def analyze_surface_spectrum(mesh: Mesh, n_lines: int) -> SpectralAnalysis:
    laplacian = build_weighted_normalized_laplacian(mesh)
    eigenvalues, eigenvectors = mx.linalg.eigh(laplacian)
    selected = eigenvalues[1 : n_lines + 1]
    mx.eval(eigenvalues, eigenvectors, selected)
    return SpectralAnalysis(
        eigenvalues=eigenvalues,
        eigenvectors=eigenvectors,
        selected_eigenvalues=selected,
    )


# -----------------------------------------------------------------------------
# Geometry-conditioned acoustic model
# -----------------------------------------------------------------------------


def select_directional_vertex(vertices: mx.array, direction: Sequence[float]) -> int:
    direction_mx = mx.array(normalize_python(direction), dtype=mx.float32)
    projection = vertices @ direction_mx
    return mx_int(mx.argmax(projection))


def stable_normalize_vector(vector: mx.array, bias: float = 0.0) -> mx.array:
    if bias:
        vector = vector + bias
    vector = vector - mx.mean(vector)
    norm = mx.linalg.norm(vector)
    fallback = mx.ones_like(vector) / math.sqrt(vector.shape[0])
    normalized = vector / mx.maximum(norm, 1.0e-8)
    return mx.where(norm > 1.0e-7, normalized, fallback)


def build_geometry_feedback_matrix(
    selected_eigenvalues: mx.array,
    roughness: float,
    sphericity: float,
    n_lines: int,
) -> mx.array:
    if n_lines & (n_lines - 1):
        raise ValueError("The v1 Hadamard FDN requires n_lines to be a power of two.")

    spectrum = selected_eigenvalues[:n_lines]
    spectrum_min = mx.min(spectrum)
    spectrum_max = mx.max(spectrum)
    p = (spectrum - spectrum_min) / mx.maximum(spectrum_max - spectrum_min, 1.0e-8)

    row = mx.arange(n_lines, dtype=mx.float32)[:, None] + 1.0
    col = mx.arange(n_lines, dtype=mx.float32)[None, :] + 1.0
    spectral_outer = p[:, None] * (1.0 + p[None, :])

    scatter = clamp(0.28 + 5.0 * roughness + 0.35 * (1.0 - sphericity), 0.25, 1.35)
    seed_matrix = (
        mx.eye(n_lines, dtype=mx.float32)
        + scatter * mx.sin(2.0 * math.pi * spectral_outer + 0.173 * row * col)
        + 0.37 * mx.cos((row + col) * (0.51 + p[:, None]))
    )

    q, r = mx.linalg.qr(seed_matrix)
    signs = mx.where(mx.diag(r) >= 0.0, 1.0, -1.0)
    q = q * signs[None, :]

    # MLX's native transform returns the orthonormal Hadamard action by default.
    hadamard = mx.hadamard_transform(mx.eye(n_lines, dtype=mx.float32))
    feedback = q @ hadamard @ q.T
    mx.eval(feedback)
    return feedback


def build_delay_lines(
    mesh: Mesh,
    spectral: SpectralAnalysis,
    geometry: GeometryAnalysis,
    acoustics: AcousticConfig,
) -> tuple[list[int], list[float], list[float], list[float]]:
    directions = mx.array(fibonacci_sphere(acoustics.n_lines), dtype=mx.float32)
    projection = mesh.vertices @ directions.T
    extents = mx.max(projection, axis=0) - mx.min(projection, axis=0)

    eigenvalues = spectral.selected_eigenvalues[: acoustics.n_lines]
    eig_min = mx.min(eigenvalues)
    eig_max = mx.max(eigenvalues)
    eig_norm = (eigenvalues - eig_min) / mx.maximum(eig_max - eig_min, 1.0e-8)

    line_index = mx.arange(acoustics.n_lines, dtype=mx.float32)
    path_lengths = (
        1.12 * extents
        + geometry.mean_radius_m * (0.24 + 0.36 * eig_norm)
        + geometry.mean_edge_m * (0.5 + 0.5 * mx.sin(1.73 * line_index + eig_norm))
    )
    path_lengths = mx.maximum(path_lengths, 0.75)
    raw_samples = path_lengths / SPEED_OF_SOUND_M_S * acoustics.sample_rate
    mx.eval(path_lengths, raw_samples, eig_norm)

    used: set[int] = set()
    delay_samples = [
        nearest_unique_prime(int(round(float(value))), used)
        for value in raw_samples.tolist()
    ]
    delay_ms = [1000.0 * sample / acoustics.sample_rate for sample in delay_samples]

    roughness_norm = clamp(geometry.roughness * 8.0, 0.0, 1.0)
    hf_cutoffs = (
        acoustics.hf_cutoff_hz
        * (0.64 + 0.36 * (1.0 - eig_norm))
        * (0.92 - 0.20 * roughness_norm)
    )
    hf_cutoffs = mx.clip(hf_cutoffs, 1_500.0, 0.46 * acoustics.sample_rate)
    mx.eval(hf_cutoffs)

    return (
        delay_samples,
        delay_ms,
        [float(v) for v in path_lengths.tolist()],
        [float(v) for v in hf_cutoffs.tolist()],
    )


def build_mode_vectors(
    mesh: Mesh,
    spectral: SpectralAnalysis,
    acoustics: AcousticConfig,
    source_direction: Sequence[float],
    listener_direction: Sequence[float],
) -> tuple[mx.array, mx.array, mx.array]:
    src_index = select_directional_vertex(mesh.vertices, source_direction)

    listener = normalize_python(listener_direction)
    left_direction = normalize_python((listener[0] - 0.14, listener[1] + 0.05, listener[2] + 0.03))
    right_direction = normalize_python((listener[0] + 0.14, listener[1] - 0.05, listener[2] - 0.03))
    left_index = select_directional_vertex(mesh.vertices, left_direction)
    right_index = select_directional_vertex(mesh.vertices, right_direction)

    mode_slice = slice(1, acoustics.n_lines + 1)
    input_vector = stable_normalize_vector(spectral.eigenvectors[src_index, mode_slice], bias=0.07)
    output_left = stable_normalize_vector(spectral.eigenvectors[left_index, mode_slice], bias=-0.04)
    output_right = stable_normalize_vector(spectral.eigenvectors[right_index, mode_slice], bias=0.04)
    mx.eval(input_vector, output_left, output_right)
    return input_vector, output_left, output_right


def choose_early_reflections(
    mesh: Mesh,
    source_position: mx.array,
    listener_position: mx.array,
    acoustics: AcousticConfig,
    ear_sign: float,
) -> tuple[list[int], list[float]]:
    ear_offset = mx.array([0.09 * ear_sign, 0.025, -0.015 * ear_sign], dtype=mx.float32)
    listener = listener_position + ear_offset
    source_to_wall = mx.linalg.norm(mesh.vertices - source_position[None, :], axis=1)
    wall_to_listener = mx.linalg.norm(mesh.vertices - listener[None, :], axis=1)
    path = source_to_wall + wall_to_listener
    sorted_path = mx.sort(path)
    mx.eval(sorted_path)

    path_list = [float(v) for v in sorted_path.tolist()]
    count = min(acoustics.n_early_reflections, len(path_list))
    if count <= 0:
        return [], []

    # Quantile sampling avoids selecting only a cluster of nearly identical
    # shortest paths on a highly tessellated surface.
    selected: list[float] = []
    for i in range(count):
        quantile = (i + 0.35) / count
        index = min(len(path_list) - 1, int(quantile * len(path_list)))
        selected.append(path_list[index])

    delays = [
        max(1, int(round(distance / SPEED_OF_SOUND_M_S * acoustics.sample_rate)))
        for distance in selected
    ]
    raw_gains = [
        acoustics.reflection * math.exp(-0.055 * i) / max(1.0, distance)
        for i, distance in enumerate(selected)
    ]
    norm = math.sqrt(sum(g * g for g in raw_gains)) or 1.0
    gains = [g / norm for g in raw_gains]
    return delays, gains


def build_acoustic_model(
    mesh: Mesh,
    geometry: GeometryAnalysis,
    spectral: SpectralAnalysis,
    acoustics: AcousticConfig,
) -> AcousticModel:
    if acoustics.n_lines != 16:
        raise ValueError("v1 is intentionally fixed at 16 feedback delay lines.")
    if acoustics.rt60_s <= 0.0:
        raise ValueError("rt60_s must be positive")
    if acoustics.duration_s <= 0.0:
        raise ValueError("duration_s must be positive")

    feedback = build_geometry_feedback_matrix(
        spectral.selected_eigenvalues,
        geometry.roughness,
        geometry.sphericity,
        acoustics.n_lines,
    )
    delay_samples, delay_ms, path_lengths, hf_cutoffs = build_delay_lines(
        mesh, spectral, geometry, acoustics
    )

    source_direction = (0.62, -0.31, 0.72)
    listener_direction = (-0.48, 0.78, 0.39)
    input_vector, output_left, output_right = build_mode_vectors(
        mesh, spectral, acoustics, source_direction, listener_direction
    )

    radius = geometry.mean_radius_m
    source_position = mx.array([0.16 * radius, -0.11 * radius, 0.07 * radius], dtype=mx.float32)
    listener_position = mx.array([-0.19 * radius, 0.13 * radius, -0.04 * radius], dtype=mx.float32)

    early_l, gains_l = choose_early_reflections(
        mesh, source_position, listener_position, acoustics, ear_sign=-1.0
    )
    early_r, gains_r = choose_early_reflections(
        mesh, source_position, listener_position, acoustics, ear_sign=1.0
    )

    mx.eval(source_position, listener_position)
    return AcousticModel(
        delay_samples=delay_samples,
        delay_ms=delay_ms,
        path_lengths_m=path_lengths,
        hf_cutoffs_hz=hf_cutoffs,
        feedback_matrix=feedback,
        input_vector=input_vector,
        output_vector_left=output_left,
        output_vector_right=output_right,
        early_delay_samples_left=early_l,
        early_delay_samples_right=early_r,
        early_gains_left=gains_l,
        early_gains_right=gains_r,
        source_position_m=[float(v) for v in source_position.tolist()],
        listener_position_m=[float(v) for v in listener_position.tolist()],
    )


# -----------------------------------------------------------------------------
# Frequency-domain FDN rendering in MLX
# -----------------------------------------------------------------------------


def early_transfer(
    omega: mx.array,
    delays: Sequence[int],
    gains: Sequence[float],
) -> mx.array:
    if not delays:
        return mx.zeros_like(omega, dtype=mx.complex64)
    delay_array = mx.array(delays, dtype=mx.float32)
    gain_array = mx.array(gains, dtype=mx.float32)
    phase = mx.exp(-1j * omega[:, None] * delay_array[None, :])
    return mx.sum(phase * gain_array[None, :], axis=1)


def solve_complex_system_via_real(system: mx.array, rhs: mx.array) -> mx.array:
    """Solve batched complex systems using MLX's real-valued linalg.solve.

    For (A + iB)(x + iy) = c + id, solve the equivalent real block system:

        [ A  -B ] [x] = [c]
        [ B   A ] [y]   [d]

    This keeps the frequency-domain FDN in MLX while remaining compatible with
    MLX releases/devices whose direct complex solve is unavailable.
    """
    n = system.shape[-1]
    real = mx.real(system)
    imag = mx.imag(system)
    top = mx.concatenate([real, -imag], axis=2)
    bottom = mx.concatenate([imag, real], axis=2)
    block = mx.concatenate([top, bottom], axis=1)
    rhs_block = mx.concatenate([mx.real(rhs), mx.imag(rhs)], axis=1)
    solution = mx.linalg.solve(block, rhs_block[:, :, None])[:, :, 0]
    return solution[:, :n] + 1j * solution[:, n:]


def render_stereo_ir_mlx(
    model: AcousticModel,
    acoustics: AcousticConfig,
) -> tuple[mx.array, dict[str, float | int]]:
    sample_count = max(1, int(round(acoustics.duration_s * acoustics.sample_rate)))
    fft_size = next_power_of_two(sample_count)
    bin_count = fft_size // 2 + 1
    n_lines = acoustics.n_lines

    feedback = model.feedback_matrix.astype(mx.complex64)
    input_vector = model.input_vector.astype(mx.complex64)
    output_l = model.output_vector_left.astype(mx.complex64)
    output_r = model.output_vector_right.astype(mx.complex64)
    identity = mx.eye(n_lines, dtype=mx.complex64)

    delay_samples = mx.array(model.delay_samples, dtype=mx.float32)
    delay_seconds = delay_samples / float(acoustics.sample_rate)
    line_gain = mx.power(10.0, -3.0 * delay_seconds / acoustics.rt60_s)

    hf_cutoffs = mx.array(model.hf_cutoffs_hz, dtype=mx.float32)
    poles = mx.exp(-2.0 * math.pi * hf_cutoffs / acoustics.sample_rate)

    spectrum_left_chunks: list[mx.array] = []
    spectrum_right_chunks: list[mx.array] = []

    for start in range(0, bin_count, acoustics.chunk_bins):
        stop = min(bin_count, start + acoustics.chunk_bins)
        omega = (
            2.0
            * math.pi
            * mx.arange(start, stop, dtype=mx.float32)
            / float(fft_size)
        )

        z_minus_1 = mx.exp(-1j * omega[:, None])
        lowpass = (1.0 - poles[None, :]) / (
            1.0 - poles[None, :] * z_minus_1
        )
        delay_phase = mx.exp(-1j * omega[:, None] * delay_samples[None, :])
        diagonal_delay = delay_phase * line_gain[None, :] * lowpass

        # y = (I - D A)^(-1) D b
        system = identity[None, :, :] - diagonal_delay[:, :, None] * feedback[None, :, :]
        rhs = diagonal_delay * input_vector[None, :]
        state = solve_complex_system_via_real(system, rhs)

        late_l = mx.sum(state * output_l[None, :], axis=1)
        late_r = mx.sum(state * output_r[None, :], axis=1)
        early_l = early_transfer(
            omega, model.early_delay_samples_left, model.early_gains_left
        )
        early_r = early_transfer(
            omega, model.early_delay_samples_right, model.early_gains_right
        )

        direct = mx.ones_like(late_l) * acoustics.direct_mix
        transfer_l = (
            acoustics.late_mix * late_l
            + acoustics.early_mix * early_l
            + direct
        )
        transfer_r = (
            acoustics.late_mix * late_r
            + acoustics.early_mix * early_r
            + direct
        )

        mx.eval(transfer_l, transfer_r)
        spectrum_left_chunks.append(transfer_l)
        spectrum_right_chunks.append(transfer_r)

    spectrum_left = mx.concatenate(spectrum_left_chunks, axis=0)
    spectrum_right = mx.concatenate(spectrum_right_chunks, axis=0)
    ir_left = mx.fft.irfft(spectrum_left, n=fft_size)[:sample_count]
    ir_right = mx.fft.irfft(spectrum_right, n=fft_size)[:sample_count]
    stereo = mx.stack([ir_left, ir_right], axis=1)

    # Remove tiny numerical DC, then taper the final 8% to suppress circular
    # wrap when the requested duration is shorter than the effective decay.
    stereo = stereo - mx.mean(stereo, axis=0, keepdims=True)
    fade_start = int(0.92 * sample_count)
    index = mx.arange(sample_count, dtype=mx.float32)
    fade_t = mx.clip(
        (index - fade_start) / max(1.0, float(sample_count - fade_start - 1)),
        0.0,
        1.0,
    )
    fade = 0.5 * (1.0 + mx.cos(math.pi * fade_t))
    fade = mx.where(index < fade_start, 1.0, fade)
    stereo = stereo * fade[:, None]

    peak = mx.max(mx.abs(stereo))
    scale = acoustics.output_ceiling / mx.maximum(peak, 1.0e-9)
    stereo = stereo * scale
    rms = mx.sqrt(mx.mean(stereo * stereo))
    mx.eval(stereo, peak, rms)

    stats: dict[str, float | int] = {
        "sample_count": sample_count,
        "fft_size": fft_size,
        "frequency_bins": bin_count,
        "pre_normalization_peak": float(peak.item()),
        "post_normalization_peak": float(mx.max(mx.abs(stereo)).item()),
        "rms": float(rms.item()),
    }
    return stereo, stats


# -----------------------------------------------------------------------------
# Exporters
# -----------------------------------------------------------------------------


def write_obj(path: Path, mesh: Mesh) -> None:
    vertices = mesh.vertices.tolist()
    with path.open("w", encoding="utf-8") as handle:
        handle.write(f"# procedural_chamber_mlx_v1 {VERSION}\n")
        for x, y, z in vertices:
            handle.write(f"v {float(x):.9f} {float(y):.9f} {float(z):.9f}\n")
        for a, b, c in mesh.faces:
            handle.write(f"f {a + 1} {b + 1} {c + 1}\n")


def float_to_pcm24(value: float) -> bytes:
    clipped = clamp(value, -1.0, 1.0)
    integer = int(round(clipped * 8_388_607.0))
    if integer < 0:
        integer += 1 << 24
    return struct.pack(
        "<BBB",
        integer & 0xFF,
        (integer >> 8) & 0xFF,
        (integer >> 16) & 0xFF,
    )


def write_stereo_wav_24(path: Path, stereo: mx.array, sample_rate: int) -> None:
    samples = stereo.tolist()
    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(2)
        wav.setsampwidth(3)
        wav.setframerate(sample_rate)
        block = bytearray()
        for left, right in samples:
            block.extend(float_to_pcm24(float(left)))
            block.extend(float_to_pcm24(float(right)))
        wav.writeframes(bytes(block))


def rounded_list(values: Sequence[float], digits: int = 9) -> list[float]:
    return [round(float(value), digits) for value in values]


def write_descriptor_json(
    path: Path,
    chamber: ChamberConfig,
    acoustics: AcousticConfig,
    render: RenderConfig,
    device_used: str,
    geometry: GeometryAnalysis,
    spectral: SpectralAnalysis,
    model: AcousticModel,
    render_stats: dict[str, float | int] | None,
    obj_filename: str,
    wav_filename: str | None,
) -> None:
    selected_eigenvalues = [float(v) for v in spectral.selected_eigenvalues.tolist()]
    feedback = [[float(x) for x in row] for row in model.feedback_matrix.tolist()]

    payload = {
        "format": "procedural_chamber_mlx_descriptor",
        "version": VERSION,
        "backend": "mlx",
        "device": device_used,
        "files": {
            "mesh_obj": obj_filename,
            "stereo_ir_wav": wav_filename,
        },
        "chamber_config": asdict(chamber),
        "acoustic_config": asdict(acoustics),
        "render_config": asdict(render),
        "geometry": asdict(geometry),
        "surface_graph": {
            "laplacian_type": "weighted_normalized_surface_graph",
            "selected_nonzero_eigenvalues": rounded_list(selected_eigenvalues),
            "interpretation": (
                "Surface-graph modes condition the synthetic reverb. They are not "
                "claimed to be exact volumetric cavity eigenmodes."
            ),
        },
        "fdn": {
            "line_count": acoustics.n_lines,
            "delay_samples": model.delay_samples,
            "delay_ms": rounded_list(model.delay_ms, 6),
            "path_lengths_m": rounded_list(model.path_lengths_m, 6),
            "hf_cutoffs_hz": rounded_list(model.hf_cutoffs_hz, 3),
            "feedback_matrix": feedback,
            "input_vector": rounded_list(model.input_vector.tolist()),
            "output_vector_left": rounded_list(model.output_vector_left.tolist()),
            "output_vector_right": rounded_list(model.output_vector_right.tolist()),
            "rt60_s": acoustics.rt60_s,
        },
        "early_reflections": {
            "left_delay_samples": model.early_delay_samples_left,
            "right_delay_samples": model.early_delay_samples_right,
            "left_gains": rounded_list(model.early_gains_left),
            "right_gains": rounded_list(model.early_gains_right),
        },
        "source_listener": {
            "source_position_m": rounded_list(model.source_position_m),
            "listener_position_m": rounded_list(model.listener_position_m),
        },
        "render_stats": render_stats,
    }

    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=False)
        handle.write("\n")


# -----------------------------------------------------------------------------
# CLI
# -----------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Generate a fractally deformed Platonic chamber and a geometry-conditioned "
            "16-line stereo FDN impulse response using MLX."
        )
    )

    parser.add_argument("--shape", choices=["tetra", "cube", "octa", "icosa"], default="icosa")
    parser.add_argument("--subdivisions", type=int, default=2)
    parser.add_argument("--roundedness", type=float, default=0.18)
    parser.add_argument("--radius-m", type=float, default=7.5)
    parser.add_argument("--deformation", type=float, default=0.34)
    parser.add_argument("--fractal-octaves", type=int, default=5)
    parser.add_argument("--lacunarity", type=float, default=2.03)
    parser.add_argument("--persistence", type=float, default=0.52)
    parser.add_argument("--base-frequency", type=float, default=1.15)
    parser.add_argument("--twist", type=float, default=0.16)
    parser.add_argument("--porosity", type=float, default=0.20)
    parser.add_argument("--anisotropy-x", type=float, default=1.00)
    parser.add_argument("--anisotropy-y", type=float, default=0.93)
    parser.add_argument("--anisotropy-z", type=float, default=1.12)
    parser.add_argument("--seed", type=int, default=271828)

    parser.add_argument("--sample-rate", type=int, default=48_000)
    parser.add_argument("--duration", type=float, default=8.0)
    parser.add_argument("--rt60", type=float, default=6.5)
    parser.add_argument("--hf-cutoff", type=float, default=9_500.0)
    parser.add_argument("--reflection", type=float, default=0.78)
    parser.add_argument("--early-reflections", type=int, default=28)
    parser.add_argument("--early-mix", type=float, default=0.34)
    parser.add_argument("--late-mix", type=float, default=0.82)
    parser.add_argument("--direct-mix", type=float, default=0.0)
    parser.add_argument("--chunk-bins", type=int, default=1024)
    parser.add_argument("--ceiling", type=float, default=0.95)

    parser.add_argument("--output-dir", default="procedural_chamber_output")
    parser.add_argument("--name", default="procedural_chamber_mlx_v1")
    parser.add_argument("--device", choices=["auto", "cpu", "gpu"], default="auto")
    parser.add_argument(
        "--geometry-only",
        action="store_true",
        help="Export OBJ and JSON without rendering the impulse response.",
    )
    return parser


def configs_from_args(args: argparse.Namespace) -> tuple[ChamberConfig, AcousticConfig, RenderConfig]:
    chamber = ChamberConfig(
        shape=args.shape,
        subdivisions=args.subdivisions,
        roundedness=args.roundedness,
        radius_m=args.radius_m,
        deformation=args.deformation,
        fractal_octaves=args.fractal_octaves,
        lacunarity=args.lacunarity,
        persistence=args.persistence,
        base_frequency=args.base_frequency,
        twist=args.twist,
        porosity=args.porosity,
        anisotropy_x=args.anisotropy_x,
        anisotropy_y=args.anisotropy_y,
        anisotropy_z=args.anisotropy_z,
        seed=args.seed,
    )
    acoustics = AcousticConfig(
        sample_rate=args.sample_rate,
        duration_s=args.duration,
        rt60_s=args.rt60,
        hf_cutoff_hz=args.hf_cutoff,
        reflection=args.reflection,
        n_lines=16,
        n_early_reflections=args.early_reflections,
        early_mix=args.early_mix,
        late_mix=args.late_mix,
        direct_mix=args.direct_mix,
        chunk_bins=args.chunk_bins,
        output_ceiling=args.ceiling,
    )
    render = RenderConfig(
        output_dir=args.output_dir,
        name=args.name,
        device=args.device,
        render_ir=not args.geometry_only,
    )
    return chamber, acoustics, render


def run(chamber: ChamberConfig, acoustics: AcousticConfig, render: RenderConfig) -> dict[str, Path]:
    device_used = set_device(render.device)
    output_dir = Path(render.output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Procedural Chamber MLX v{VERSION}")
    print(f"  MLX device:       {device_used}")
    print(f"  shape:            {chamber.shape}")
    print(f"  subdivisions:     {chamber.subdivisions}")

    mesh = construct_chamber_mesh(chamber)
    geometry = analyze_geometry(mesh)
    print(f"  mesh:             {geometry.vertex_count} vertices / {geometry.face_count} faces")
    print(f"  chamber volume:   {geometry.volume_m3:.3f} m^3")
    print(f"  surface area:     {geometry.surface_area_m2:.3f} m^2")
    print(f"  roughness:        {geometry.roughness:.5f}")

    spectral = analyze_surface_spectrum(mesh, acoustics.n_lines)
    model = build_acoustic_model(mesh, geometry, spectral, acoustics)

    obj_path = output_dir / f"{render.name}.obj"
    json_path = output_dir / f"{render.name}.json"
    wav_path = output_dir / f"{render.name}_stereo_ir.wav"
    write_obj(obj_path, mesh)

    render_stats: dict[str, float | int] | None = None
    actual_wav_path: Path | None = None
    if render.render_ir:
        print(
            f"  rendering IR:     {acoustics.duration_s:.3f} s @ "
            f"{acoustics.sample_rate} Hz"
        )
        stereo, render_stats = render_stereo_ir_mlx(model, acoustics)
        write_stereo_wav_24(wav_path, stereo, acoustics.sample_rate)
        actual_wav_path = wav_path
        print(f"  IR peak:          {render_stats['post_normalization_peak']:.6f}")
        print(f"  IR RMS:           {render_stats['rms']:.6f}")

    write_descriptor_json(
        json_path,
        chamber,
        acoustics,
        render,
        device_used,
        geometry,
        spectral,
        model,
        render_stats,
        obj_path.name,
        actual_wav_path.name if actual_wav_path else None,
    )

    print(f"  OBJ:              {obj_path}")
    print(f"  JSON:             {json_path}")
    if actual_wav_path:
        print(f"  WAV:              {actual_wav_path}")

    result = {"obj": obj_path, "json": json_path}
    if actual_wav_path:
        result["wav"] = actual_wav_path
    return result


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        chamber, acoustics, render = configs_from_args(args)
        run(chamber, acoustics, render)
    except (ValueError, RuntimeError) as exc:
        parser.error(str(exc))
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
