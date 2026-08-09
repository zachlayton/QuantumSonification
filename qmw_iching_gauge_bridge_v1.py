#!/usr/bin/env python3
"""Discrete U(1)-type gauge geometry on the 64 I Ching hexagrams.

The six line bits form the vertices of Q6.  Neighboring vertices differ by one
line.  Complex coherences of the reduced six-qubit density matrix provide edge
phases; moving-line probabilities modulate edge magnitudes.  Canonically
oriented elementary squares provide 240 gauge-invariant loop phases.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np

HEXAGRAM_DIMENSION = 64
FULL_DIMENSION = 256
LINE_COUNT = 6
PLAQUETTE_COUNT = 240


@dataclass(frozen=True)
class HypercubeEdge:
    source: int
    target: int
    line: int
    weight: float
    phase_radians: float


@dataclass(frozen=True)
class PlaquetteFlux:
    index: int
    base: int
    line_a: int
    line_b: int
    vertices: tuple[int, int, int, int]
    flux_radians: float
    strength: float


@dataclass(frozen=True)
class PairFluxDescriptor:
    line_a: int
    line_b: int
    count: int
    active_count: int
    mean_absolute_flux_radians: float
    circular_mean_phase_radians: float
    circular_variance: float
    chirality: float
    maximum_strength: float


@dataclass(frozen=True)
class GaugeDescriptors:
    plaquette_count: int
    active_plaquette_count: int
    mean_absolute_flux_radians: float
    circular_mean_phase_radians: float
    circular_variance: float
    chirality: float
    strongest_plaquette_index: int
    strongest_base: int
    strongest_line_a: int
    strongest_line_b: int
    strongest_vertices: tuple[int, int, int, int]
    strongest_flux_radians: float
    strongest_strength: float
    low_laplacian_eigenvalues: tuple[float, ...]
    laplacian_trace: float
    laplacian_minimum_eigenvalue: float
    laplacian_hermiticity_error: float


@dataclass(frozen=True)
class GaugeSnapshot:
    rho_hexagram: np.ndarray
    adjacency: np.ndarray
    laplacian: np.ndarray
    edges: tuple[HypercubeEdge, ...]
    plaquettes: tuple[PlaquetteFlux, ...]
    line_pairs: tuple[PairFluxDescriptor, ...]
    descriptors: GaugeDescriptors


def _validated_density(matrix: np.ndarray, dimension: int) -> np.ndarray:
    value = np.asarray(matrix, dtype=np.complex128)
    if value.shape != (dimension, dimension):
        raise ValueError(f"density matrix must have shape {(dimension, dimension)}")
    if not np.all(np.isfinite(value)):
        raise ValueError("density matrix contains non-finite values")
    if not np.allclose(value, value.conj().T, atol=1e-9, rtol=1e-9):
        raise ValueError("density matrix must be Hermitian")
    trace = np.trace(value)
    # MLX intentionally stores the persistent density matrix as complex64.
    # Accept its expected accumulation error, then normalize in complex128 so
    # every downstream gauge descriptor sees an exact unit-trace matrix.
    if abs(trace.imag) > 2e-6 or not np.isclose(trace.real, 1.0, atol=2e-6, rtol=2e-6):
        raise ValueError("density matrix trace must be one")
    hermitian = 0.5 * (value + value.conj().T)
    return hermitian / np.trace(hermitian).real


def hexagram_density_matrix(rho8: np.ndarray) -> np.ndarray:
    """Trace out q6,q7 from an LSB-ordered 8-qubit density matrix."""
    full = _validated_density(rho8, FULL_DIMENSION)
    reduced = np.zeros((HEXAGRAM_DIMENSION, HEXAGRAM_DIMENSION), dtype=np.complex128)
    basis = np.arange(HEXAGRAM_DIMENSION, dtype=np.int64)
    for change_state in range(4):
        indices = basis | (change_state << LINE_COUNT)
        reduced += full[np.ix_(indices, indices)]
    return 0.5 * (reduced + reduced.conj().T)


def build_hexagram_hypercube() -> tuple[tuple[int, int, int], ...]:
    """Return the 192 undirected Q6 edges as (source,target,line)."""
    edges = []
    for source in range(HEXAGRAM_DIMENSION):
        for line in range(LINE_COUNT):
            target = source ^ (1 << line)
            if source < target:
                edges.append((source, target, line + 1))
    return tuple(edges)


def build_magnetic_adjacency(
    rho_hexagram: np.ndarray,
    moving_probabilities: Iterable[float] = (1, 1, 1, 1, 1, 1),
    *,
    phase_threshold: float = 1e-12,
) -> tuple[np.ndarray, tuple[HypercubeEdge, ...]]:
    """Build a Hermitian adjacency from neighboring coherences of rho_H."""
    rho_h = _validated_density(rho_hexagram, HEXAGRAM_DIMENSION)
    probabilities = tuple(float(np.clip(value, 0.0, 1.0)) for value in moving_probabilities)
    if len(probabilities) != LINE_COUNT:
        raise ValueError("moving_probabilities must contain six values")
    adjacency = np.zeros_like(rho_h)
    records = []
    for source, target, line in build_hexagram_hypercube():
        coherence = complex(rho_h[source, target])
        magnitude = abs(coherence)
        weight = probabilities[line - 1] * magnitude
        phase = float(np.angle(coherence)) if magnitude > phase_threshold else 0.0
        value = weight * np.exp(1j * phase)
        adjacency[source, target] = value
        adjacency[target, source] = value.conjugate()
        records.append(HypercubeEdge(source, target, line, float(weight), phase))
    return adjacency, tuple(records)


def build_magnetic_laplacian(adjacency: np.ndarray) -> np.ndarray:
    """Return L=D-A with D_ii=sum_j |A_ij|, guaranteeing PSD in exact arithmetic."""
    value = np.asarray(adjacency, dtype=np.complex128)
    if value.shape != (HEXAGRAM_DIMENSION, HEXAGRAM_DIMENSION):
        raise ValueError("adjacency must have shape (64, 64)")
    if not np.allclose(value, value.conj().T, atol=1e-10, rtol=1e-10):
        raise ValueError("adjacency must be Hermitian")
    degree = np.sum(np.abs(value), axis=1)
    return np.diag(degree) - value


def square_cycle_fluxes(
    adjacency: np.ndarray,
    *,
    phase_threshold: float = 1e-15,
) -> tuple[PlaquetteFlux, ...]:
    """Enumerate all 15*16 canonical elementary plaquettes of Q6."""
    value = np.asarray(adjacency, dtype=np.complex128)
    if value.shape != (HEXAGRAM_DIMENSION, HEXAGRAM_DIMENSION):
        raise ValueError("adjacency must have shape (64, 64)")
    fluxes = []
    index = 0
    for line_a in range(LINE_COUNT):
        for line_b in range(line_a + 1, LINE_COUNT):
            for base in range(HEXAGRAM_DIMENSION):
                if base & (1 << line_a) or base & (1 << line_b):
                    continue
                a = base
                b = a ^ (1 << line_a)
                c = b ^ (1 << line_b)
                d = a ^ (1 << line_b)
                product = value[a, b] * value[b, c] * value[c, d] * value[d, a]
                magnitude = abs(product)
                fluxes.append(PlaquetteFlux(
                    index=index, base=base, line_a=line_a + 1, line_b=line_b + 1,
                    vertices=(a, b, c, d),
                    flux_radians=float(np.angle(product)) if magnitude > phase_threshold else 0.0,
                    strength=float(magnitude ** 0.25),
                ))
                index += 1
    if len(fluxes) != PLAQUETTE_COUNT:
        raise RuntimeError(f"expected 240 plaquettes; constructed {len(fluxes)}")
    return tuple(fluxes)


def _describe_flux_group(fluxes: tuple[PlaquetteFlux, ...],
                         phase_threshold: float) -> tuple[int, float, float, float, float, float]:
    phases = np.asarray([item.flux_radians for item in fluxes], dtype=np.float64)
    strengths = np.asarray([item.strength for item in fluxes], dtype=np.float64)
    active = strengths > phase_threshold
    active_count = int(np.count_nonzero(active))
    if active_count == 0:
        return 0, 0.0, 0.0, 1.0, 0.0, float(strengths.max(initial=0.0))
    phases = phases[active]
    weights = strengths[active]
    weight_sum = float(weights.sum())
    circular = np.sum(weights * np.exp(1j * phases)) / weight_sum
    mean_abs = float(np.sum(weights * np.abs(phases)) / weight_sum)
    mean_phase = float(np.angle(circular))
    variance = float(1.0 - abs(circular))
    chirality = float(np.sum(weights * np.sin(phases)) / weight_sum)
    return active_count, mean_abs, mean_phase, variance, chirality, float(strengths.max())


def gauge_descriptors(
    plaquettes: tuple[PlaquetteFlux, ...],
    laplacian: np.ndarray,
    *,
    low_mode_count: int = 8,
    phase_threshold: float = 1e-15,
) -> tuple[GaugeDescriptors, tuple[PairFluxDescriptor, ...]]:
    """Summarize 240 fluxes without treating angles as ordinary linear data."""
    if len(plaquettes) != PLAQUETTE_COUNT:
        raise ValueError("gauge descriptors require all 240 plaquettes")
    if not 1 <= low_mode_count <= HEXAGRAM_DIMENSION:
        raise ValueError("low_mode_count must be between 1 and 64")
    matrix = np.asarray(laplacian, dtype=np.complex128)
    if matrix.shape != (HEXAGRAM_DIMENSION, HEXAGRAM_DIMENSION):
        raise ValueError("laplacian must have shape (64, 64)")
    eigenvalues = np.linalg.eigvalsh(0.5 * (matrix + matrix.conj().T)).real
    active_count, mean_abs, mean_phase, variance, chirality, _maximum = (
        _describe_flux_group(plaquettes, phase_threshold)
    )
    # A strong but flat (zero-flux) square is not the most informative gauge
    # feature.  Rank the highlighted loop by phase-bearing salience so a
    # numerically dominant zero-phase plaquette cannot become a permanent cyan
    # marker in the presentation layer.
    strongest = max(
        plaquettes,
        key=lambda item: item.strength * abs(item.flux_radians),
    )
    pairs = []
    for line_a in range(1, LINE_COUNT + 1):
        for line_b in range(line_a + 1, LINE_COUNT + 1):
            group = tuple(
                item for item in plaquettes
                if item.line_a == line_a and item.line_b == line_b
            )
            count, pair_abs, pair_phase, pair_variance, pair_chirality, pair_maximum = (
                _describe_flux_group(group, phase_threshold)
            )
            pairs.append(PairFluxDescriptor(
                line_a, line_b, len(group), count, pair_abs, pair_phase,
                pair_variance, pair_chirality, pair_maximum,
            ))
    descriptors = GaugeDescriptors(
        plaquette_count=len(plaquettes), active_plaquette_count=active_count,
        mean_absolute_flux_radians=mean_abs,
        circular_mean_phase_radians=mean_phase,
        circular_variance=variance, chirality=chirality,
        strongest_plaquette_index=strongest.index,
        strongest_base=strongest.base,
        strongest_line_a=strongest.line_a,
        strongest_line_b=strongest.line_b,
        strongest_vertices=strongest.vertices,
        strongest_flux_radians=strongest.flux_radians,
        strongest_strength=strongest.strength,
        low_laplacian_eigenvalues=tuple(float(value) for value in eigenvalues[:low_mode_count]),
        laplacian_trace=float(np.trace(matrix).real),
        laplacian_minimum_eigenvalue=float(eigenvalues.min()),
        laplacian_hermiticity_error=float(np.linalg.norm(matrix - matrix.conj().T)),
    )
    return descriptors, tuple(pairs)


def build_gauge_snapshot(
    rho8: np.ndarray,
    moving_probabilities: Iterable[float],
    *,
    low_mode_count: int = 8,
) -> GaugeSnapshot:
    """Compute rho_H, A, L, 240 plaquettes, and bounded descriptors."""
    rho_h = hexagram_density_matrix(rho8)
    adjacency, edges = build_magnetic_adjacency(rho_h, moving_probabilities)
    laplacian = build_magnetic_laplacian(adjacency)
    plaquettes = square_cycle_fluxes(adjacency)
    descriptors, pairs = gauge_descriptors(
        plaquettes, laplacian, low_mode_count=low_mode_count
    )
    return GaugeSnapshot(rho_h, adjacency, laplacian, edges, plaquettes, pairs, descriptors)
