"""Shared QMW probability-current and transport primitives.

The module is deliberately upstream of sound design. Providers expose either a
one-dimensional complex wavefunction or a finite density-matrix graph as a
common :class:`FlowFrame`; consumers may render continuous occupation, inspect
transport, or turn accumulated boundary passage into their own event grammar.
No function mutates an authoritative state or labels an adapter event as a
measurement.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
import math
from typing import Mapping, Sequence

import numpy as np


Array = np.ndarray
EPS = 1.0e-12


def _vector(name: str, values: object, *, nonnegative: bool = False) -> Array:
    result = np.asarray(values, dtype=float)
    if result.ndim != 1 or result.size < 1 or not np.all(np.isfinite(result)):
        raise ValueError(f"{name} must be a finite one-dimensional array.")
    if nonnegative and np.any(result < 0.0):
        raise ValueError(f"{name} must be nonnegative.")
    return np.array(result, copy=True)


def _weights(coordinates: Array) -> Array:
    if coordinates.size < 3 or not np.all(np.diff(coordinates) > 0.0):
        raise ValueError("coordinates must be strictly increasing with length >= 3.")
    result = np.empty_like(coordinates)
    result[0] = 0.5 * (coordinates[1] - coordinates[0])
    result[-1] = 0.5 * (coordinates[-1] - coordinates[-2])
    result[1:-1] = 0.5 * (coordinates[2:] - coordinates[:-2])
    return result


def _regions(regions: Sequence[int] | Array | None, size: int, *, graph: bool) -> Array:
    if regions is None:
        return np.arange(size, dtype=int) if graph else np.zeros(size, dtype=int)
    result = np.asarray(regions, dtype=int)
    if result.shape != (size,) or np.any(result < 0):
        raise ValueError("regions must be a nonnegative integer label for every sample or node.")
    return np.array(result, copy=True)


@dataclass(frozen=True)
class BoundaryFlux:
    """Signed passage through one declared continuous or graph boundary.

    ``signed_flux`` is positive in the boundary's canonical orientation. The
    source/destination fields express the instantaneous physical direction.
    ``phase`` is a local relative phase for continuous interfaces or an edge
    coherence phase for density-matrix graphs; it may be absent.
    """

    boundary: str
    source_region: int
    destination_region: int
    direction: int
    signed_flux: float
    magnitude: float
    phase: float | None
    current_kind: str = "quantum_probability"


@dataclass(frozen=True)
class FlowEvent:
    """A threshold-marked passage event for downstream consumers."""

    time: float
    source_region: int
    destination_region: int
    boundary: str
    direction: int
    magnitude: float
    phase: float | None
    current_kind: str = "quantum_probability"


@dataclass(frozen=True)
class FlowFrame:
    """State, transport, regional, and optional event observables.

    ``representation`` is either ``continuous_1d`` or ``density_graph``.
    Continuous current is sampled on ``coordinates``. Graph current is ordered
    by ``edge_indices`` and uses positive current from the first node to the
    second. ``divergence`` is positive for net outward flow, so the continuity
    convention is ``density_rate + divergence = 0``.
    """

    time: float
    density: Array
    phase: Array | None
    phase_gradient: Array | None
    current: Array
    divergence: Array
    region_index: Array
    region_population: Array
    region_flux: Array
    boundary_fluxes: tuple[BoundaryFlux, ...]
    crossings: tuple[FlowEvent, ...]
    total_probability: float
    flow_energy: float
    circulation: float
    coherence_flow: float
    representation: str
    coordinates: Array | None = None
    edge_indices: Array | None = None
    continuity_residual: Array | None = None
    continuity_linf: float | None = None
    current_kind: str = "quantum_probability"


@dataclass(frozen=True)
class FlowFrame2D:
    """Two-dimensional continuous probability transport observations.

    ``current[0]`` and ``current[1]`` are respectively the x and y current
    components.  ``region_flux`` is net inward passage, so the compatible
    continuity convention is ``d(region_population)/dt = region_flux``.
    ``boundary_fluxes`` reports the declared, oriented periodic cell faces.
    """

    time: float
    density: Array
    phase: Array
    current: Array
    divergence: Array
    region_index: Array
    region_population: Array
    region_flux: Array
    boundary_fluxes: tuple[BoundaryFlux, ...]
    crossings: tuple[FlowEvent, ...]
    total_probability: float
    flow_energy: float
    coherence_flow: float
    coordinates: tuple[Array, Array]
    continuity_residual: Array | None = None
    continuity_linf: float | None = None
    representation: str = "continuous_2d"
    current_kind: str = "quantum_probability"


@dataclass(frozen=True)
class EffectiveTerrainFlowFrame:
    """Mesoscopic graph flow derived from terrain coordinates, never from rho evolution."""

    time: float
    q: Array
    qdot: Array
    edge_indices: Array
    current: Array
    divergence: Array
    region_index: Array
    region_coordinate: Array
    region_flux: Array
    boundary_fluxes: tuple[BoundaryFlux, ...]
    crossings: tuple[FlowEvent, ...]
    flow_energy: float
    coherence_flow: float
    representation: str = "effective_terrain_graph"
    current_kind: str = "effective_terrain"


@dataclass(frozen=True)
class FluxEventState:
    """Per-boundary accumulated passage retained between observations."""

    accumulated: Mapping[str, float] = field(default_factory=dict)

    def __post_init__(self) -> None:
        source = dict(self.accumulated)
        if any(not math.isfinite(float(value)) or float(value) < 0.0 for value in source.values()):
            raise ValueError("accumulated boundary passage must be finite and nonnegative.")
        object.__setattr__(self, "accumulated", source)


def _regional_observables(
    density: Array, divergence: Array, labels: Array, weights: Array
) -> tuple[Array, Array]:
    count = int(np.max(labels)) + 1
    population = np.zeros(count, dtype=float)
    flux = np.zeros(count, dtype=float)
    for region in range(count):
        mask = labels == region
        population[region] = float(np.sum(density[mask] * weights[mask]))
        # Net inward passage: minus the integral of outward divergence.
        flux[region] = -float(np.sum(divergence[mask] * weights[mask]))
    return population, flux


def _continuous_boundaries(
    labels: Array, current: Array, phase: Array | None, *, periodic: bool = False
) -> tuple[BoundaryFlux, ...]:
    boundaries: list[BoundaryFlux] = []
    limit = labels.size if periodic else labels.size - 1
    for index in range(limit):
        neighbour = (index + 1) % labels.size
        left, right = int(labels[index]), int(labels[neighbour])
        if left == right:
            continue
        signed = float(0.5 * (current[index] + current[neighbour]))
        direction = 1 if signed > EPS else (-1 if signed < -EPS else 0)
        source, destination = (left, right) if direction >= 0 else (right, left)
        relative_phase = (
            None if phase is None
            else float(np.angle(np.exp(1j * (phase[neighbour] - phase[index]))))
        )
        boundaries.append(BoundaryFlux(
            boundary=f"interface:{index}:{left}-{right}",
            source_region=source,
            destination_region=destination,
            direction=direction,
            signed_flux=signed,
            magnitude=abs(signed),
            phase=relative_phase,
        ))
    return tuple(boundaries)


def _continuity(previous: FlowFrame | None, time: float, density: Array, divergence: Array) -> tuple[Array | None, float | None]:
    if previous is None:
        return None, None
    dt = float(time) - float(previous.time)
    if dt <= 0.0 or previous.density.shape != density.shape:
        raise ValueError("previous flow frame must have the same density shape and an earlier time.")
    residual = ((density - previous.density) / dt) + divergence
    return residual, float(np.max(np.abs(residual)))


def flow_from_observed_current_1d(
    density: Array,
    phase: Array | None,
    current: Array,
    coordinates: Array,
    *,
    time: float,
    hbar: float = 1.0,
    mass: float = 1.0,
    regions: Sequence[int] | Array | None = None,
    previous: FlowFrame | None = None,
    periodic: bool = False,
    current_on_positive_links: bool = False,
) -> FlowFrame:
    """Package an authoritative observed 1D current as a shared flow frame.

    This provider is for sources that already calculate their own current,
    such as QMW's native ``WavefunctionFrame``. It keeps that current intact
    while adding divergence, regional observables, and diagnostics. ``phase``
    may be ``None`` for a mixed-state density-matrix projection, where no
    unique local phase exists; boundary records then retain ``phase=None``.
    """

    if not math.isfinite(hbar) or hbar <= 0.0 or not math.isfinite(mass) or mass <= 0.0:
        raise ValueError("hbar and mass must be finite and greater than zero.")
    x = _vector("coordinates", coordinates)
    weights = _weights(x)
    density = _vector("density", density, nonnegative=True)
    phase_values = None if phase is None else _vector("phase", phase)
    current = _vector("current", current)
    if any(field.shape != x.shape for field in (density, current)) or (
        phase_values is not None and phase_values.shape != x.shape
    ):
        raise ValueError("density, current, optional phase, and coordinates must share a shape.")
    phase_gradient = (
        None if phase_values is None else np.divide(
            mass * current,
            hbar * density,
            out=np.zeros_like(density, dtype=float),
            where=density > EPS,
        )
    )
    if periodic:
        spacing = float(x[1] - x[0])
        if not np.allclose(np.diff(x), spacing, rtol=1.0e-9, atol=1.0e-12):
            raise ValueError("periodic current observation requires uniform coordinates.")
        weights = np.full_like(x, spacing)
        divergence = (
            (current - np.roll(current, 1)) / spacing
            if current_on_positive_links
            else (np.roll(current, -1) - np.roll(current, 1)) / (2.0 * spacing)
        )
    else:
        divergence = np.gradient(current, x, edge_order=2)
    labels = _regions(regions, x.size, graph=False)
    population, flux = _regional_observables(density, divergence, labels, weights)
    residual, linf = _continuity(previous, time, density, divergence)
    return FlowFrame(
        time=float(time), density=density, phase=phase_values, phase_gradient=phase_gradient,
        current=current, divergence=divergence, region_index=labels,
        region_population=population, region_flux=flux,
        boundary_fluxes=_continuous_boundaries(labels, current, phase_values, periodic=periodic), crossings=(),
        total_probability=float(np.sum(density * weights)),
        flow_energy=float(0.5 * mass * np.sum((current * current / np.maximum(density, EPS)) * weights)),
        circulation=0.0,
        coherence_flow=float(np.sum(np.abs(current) * weights)),
        representation="continuous_1d", coordinates=x,
        continuity_residual=residual, continuity_linf=linf,
    )


def flow_from_wavefunction_1d(
    psi: Array,
    coordinates: Array,
    *,
    time: float,
    hbar: float = 1.0,
    mass: float = 1.0,
    regions: Sequence[int] | Array | None = None,
    previous: FlowFrame | None = None,
    periodic: bool = False,
) -> FlowFrame:
    """Observe a 1D complex wavefunction without normalizing or evolving it.

    The current is evaluated as ``(hbar / mass) Im(conj(psi) * dpsi/dx)``.
    The phase gradient is recovered from that current only where density is
    non-negligible, avoiding a false velocity at phase-singular nodes.
    """

    if not math.isfinite(hbar) or hbar <= 0.0 or not math.isfinite(mass) or mass <= 0.0:
        raise ValueError("hbar and mass must be finite and greater than zero.")
    x = _vector("coordinates", coordinates)
    _weights(x)
    field = np.asarray(psi, dtype=np.complex128)
    if field.shape != x.shape or not np.all(np.isfinite(field)):
        raise ValueError("psi must be finite and match coordinates.")
    density = np.abs(field) ** 2
    phase = np.angle(field)
    if periodic:
        spacing = float(x[1] - x[0])
        if not np.allclose(np.diff(x), spacing, rtol=1.0e-9, atol=1.0e-12):
            raise ValueError("periodic wavefunction observation requires uniform coordinates.")
        derivative = (np.roll(field, -1) - np.roll(field, 1)) / (2.0 * spacing)
    else:
        derivative = np.gradient(field, x, edge_order=2)
    current = (hbar / mass) * np.imag(np.conj(field) * derivative)
    return flow_from_observed_current_1d(
        density, phase, current, x, time=time, hbar=hbar, mass=mass,
        regions=regions, previous=previous, periodic=periodic,
    )


def flow_from_wavefunction_2d(
    psi: Array,
    x_coordinates: Array,
    y_coordinates: Array,
    *,
    time: float,
    hbar: float = 1.0,
    mass: float = 1.0,
    regions: Array | None = None,
    previous: FlowFrame2D | None = None,
) -> FlowFrame2D:
    """Analyze a periodic 2-D wavefunction as probability transport.

    This is a read-only companion to the GPE solver.  It calculates
    ``rho = |psi|^2``, ``j = (hbar/m) Im(conj(psi) grad(psi))``, regional
    occupation, oriented region-face fluxes, and the continuity diagnostic.
    It neither evolves the field nor labels a crossing as a measurement.
    """

    if not math.isfinite(hbar) or hbar <= 0.0 or not math.isfinite(mass) or mass <= 0.0:
        raise ValueError("hbar and mass must be finite and greater than zero.")
    x = _vector("x_coordinates", x_coordinates)
    y = _vector("y_coordinates", y_coordinates)
    if x.size < 4 or y.size < 4 or np.any(np.diff(x) <= 0.0) or np.any(np.diff(y) <= 0.0):
        raise ValueError("2-D coordinates must be strictly increasing with length >= 4.")
    dx, dy = float(x[1] - x[0]), float(y[1] - y[0])
    if not np.allclose(np.diff(x), dx, rtol=1.0e-9, atol=1.0e-12) or not np.allclose(np.diff(y), dy, rtol=1.0e-9, atol=1.0e-12):
        raise ValueError("periodic 2-D flow requires uniform coordinate axes.")
    field = np.asarray(psi, dtype=np.complex128)
    if field.shape != (x.size, y.size) or not np.all(np.isfinite(field)):
        raise ValueError("psi must be finite with shape (len(x_coordinates), len(y_coordinates)).")
    density = np.abs(field) ** 2
    phase = np.angle(field)
    derivative_x = (np.roll(field, -1, axis=0) - np.roll(field, 1, axis=0)) / (2.0 * dx)
    derivative_y = (np.roll(field, -1, axis=1) - np.roll(field, 1, axis=1)) / (2.0 * dy)
    current = (hbar / mass) * np.stack((
        np.imag(np.conj(field) * derivative_x),
        np.imag(np.conj(field) * derivative_y),
    ))
    return flow_from_observed_current_2d(
        density, phase, current, x, y, time=time, mass=mass, regions=regions, previous=previous,
    )


def flow_from_observed_current_2d(
    density: Array,
    phase: Array,
    current: Array,
    x_coordinates: Array,
    y_coordinates: Array,
    *,
    time: float,
    mass: float = 1.0,
    regions: Array | None = None,
    previous: FlowFrame2D | None = None,
    current_on_positive_links: bool = False,
) -> FlowFrame2D:
    """Build 2-D transport accounting from an already-observed current.

    This makes covariant GPE current available to the same regional and
    continuity observer without recalculating an ordinary phase gradient.
    """

    x, y = _vector("x_coordinates", x_coordinates), _vector("y_coordinates", y_coordinates)
    rho, phi, vector = np.asarray(density, dtype=float), np.asarray(phase, dtype=float), np.asarray(current, dtype=float)
    if rho.shape != (x.size, y.size) or phi.shape != rho.shape or vector.shape != (2, *rho.shape):
        raise ValueError("density, phase, and current must match the two-dimensional coordinate grid.")
    if not np.all(np.isfinite(rho)) or not np.all(np.isfinite(phi)) or not np.all(np.isfinite(vector)) or np.any(rho < 0.0):
        raise ValueError("density, phase, and current must be finite with nonnegative density.")
    if not math.isfinite(mass) or mass <= 0.0:
        raise ValueError("mass must be finite and greater than zero.")
    dx, dy = float(x[1] - x[0]), float(y[1] - y[0])
    if x.size < 4 or y.size < 4 or np.any(np.diff(x) <= 0.0) or np.any(np.diff(y) <= 0.0):
        raise ValueError("2-D coordinates must be strictly increasing with length >= 4.")
    if not np.allclose(np.diff(x), dx, rtol=1.0e-9, atol=1.0e-12) or not np.allclose(np.diff(y), dy, rtol=1.0e-9, atol=1.0e-12):
        raise ValueError("periodic 2-D flow requires uniform coordinate axes.")
    labels = np.zeros(rho.shape, dtype=int) if regions is None else np.asarray(regions, dtype=int)
    if labels.shape != rho.shape or np.any(labels < 0):
        raise ValueError("regions must be a nonnegative label for every field cell.")
    labels = np.array(labels, copy=True)
    # Face-integrated fluxes make regional accounting and divergence use the
    # same finite-volume convention.  The last-to-first periodic face is kept.
    face_x = (vector[0] if current_on_positive_links else 0.5 * (vector[0] + np.roll(vector[0], -1, axis=0))) * dy
    face_y = (vector[1] if current_on_positive_links else 0.5 * (vector[1] + np.roll(vector[1], -1, axis=1))) * dx
    cell_area = dx * dy
    divergence = (
        face_x - np.roll(face_x, 1, axis=0)
        + face_y - np.roll(face_y, 1, axis=1)
    ) / cell_area
    region_count = int(np.max(labels)) + 1
    region_population = np.zeros(region_count, dtype=float)
    region_flux = np.zeros(region_count, dtype=float)
    for region in range(region_count):
        mask = labels == region
        region_population[region] = float(np.sum(rho[mask]) * cell_area)
        region_flux[region] = -float(np.sum(divergence[mask]) * cell_area)
    boundaries: list[BoundaryFlux] = []
    for axis, face_flux in enumerate((face_x, face_y)):
        for index in np.ndindex(rho.shape):
            neighbour = list(index)
            neighbour[axis] = (neighbour[axis] + 1) % rho.shape[axis]
            neighbour_tuple = tuple(neighbour)
            first_region, second_region = int(labels[index]), int(labels[neighbour_tuple])
            if first_region == second_region:
                continue
            signed = float(face_flux[index])
            direction = 1 if signed > EPS else (-1 if signed < -EPS else 0)
            source, destination = (first_region, second_region) if direction >= 0 else (second_region, first_region)
            boundaries.append(BoundaryFlux(
                boundary=f"face:{'xy'[axis]}:{index[0]},{index[1]}",
                source_region=source, destination_region=destination, direction=direction,
                signed_flux=signed, magnitude=abs(signed),
                phase=float(np.angle(np.exp(1j * (phi[neighbour_tuple] - phi[index])))),
            ))
    residual: Array | None = None
    linf: float | None = None
    if previous is not None:
        if previous.density.shape != rho.shape or time <= previous.time:
            raise ValueError("previous flow frame must have the same density shape and an earlier time.")
        residual = ((rho - previous.density) / (float(time) - previous.time)) + divergence
        linf = float(np.max(np.abs(residual)))
    weights = cell_area
    flow_energy = 0.5 * mass * float(np.sum(np.sum(vector**2, axis=0) / np.maximum(rho, EPS)) * weights)
    return FlowFrame2D(
        time=float(time), density=rho, phase=phi, current=vector, divergence=divergence,
        region_index=labels, region_population=region_population, region_flux=region_flux,
        boundary_fluxes=tuple(boundaries), crossings=(), total_probability=float(np.sum(rho) * cell_area),
        flow_energy=flow_energy, coherence_flow=float(np.sum(np.linalg.norm(vector, axis=0)) * cell_area),
        coordinates=(x, y), continuity_residual=residual, continuity_linf=linf,
    )


def flow_from_density_matrix_graph(
    rho: Array,
    hamiltonian: Array,
    *,
    time: float,
    hbar: float = 1.0,
    regions: Sequence[int] | Array | None = None,
    previous: FlowFrame | None = None,
    edge_tolerance: float = 1.0e-12,
) -> FlowFrame:
    """Observe directed graph current from a density matrix and Hamiltonian.

    For each canonical edge ``i < j``, positive current is ``i -> j`` and is
    defined as ``-(2 / hbar) Im(H[i,j] * rho[j,i])``. With this convention,
    ``density_rate = -divergence`` under unitary evolution. A mixed density
    matrix has no unique node phase, so edge coherence phase is retained only
    on ``BoundaryFlux`` records.
    """

    if not math.isfinite(hbar) or hbar <= 0.0:
        raise ValueError("hbar must be finite and greater than zero.")
    matrix = np.asarray(rho, dtype=np.complex128)
    hamiltonian = np.asarray(hamiltonian, dtype=np.complex128)
    if matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1] or hamiltonian.shape != matrix.shape:
        raise ValueError("rho and hamiltonian must be square matrices with the same shape.")
    if not np.all(np.isfinite(matrix)) or not np.all(np.isfinite(hamiltonian)):
        raise ValueError("rho and hamiltonian must be finite.")
    if not np.allclose(matrix, matrix.conj().T, atol=1e-10) or not np.allclose(hamiltonian, hamiltonian.conj().T, atol=1e-10):
        raise ValueError("rho and hamiltonian must be Hermitian.")
    density = np.real(np.diag(matrix))
    if np.any(density < -1e-10):
        raise ValueError("rho must have nonnegative diagonal populations.")
    density = np.maximum(density, 0.0)
    size = density.size
    labels = _regions(regions, size, graph=True)
    divergence = np.zeros(size, dtype=float)
    edges: list[tuple[int, int]] = []
    currents: list[float] = []
    boundaries: list[BoundaryFlux] = []
    current_matrix = np.zeros((size, size), dtype=float)
    for left in range(size):
        for right in range(left + 1, size):
            coupling = hamiltonian[left, right]
            if abs(coupling) <= edge_tolerance:
                continue
            signed = float(-(2.0 / hbar) * np.imag(coupling * matrix[right, left]))
            edges.append((left, right))
            currents.append(signed)
            current_matrix[left, right] = signed
            current_matrix[right, left] = -signed
            divergence[left] += signed
            divergence[right] -= signed
            source_node, destination_node = (left, right) if signed >= 0.0 else (right, left)
            source_region, destination_region = int(labels[source_node]), int(labels[destination_node])
            if source_region != destination_region:
                boundaries.append(BoundaryFlux(
                    boundary=f"edge:{left}-{right}",
                    source_region=source_region,
                    destination_region=destination_region,
                    direction=1 if signed > EPS else (-1 if signed < -EPS else 0),
                    signed_flux=signed,
                    magnitude=abs(signed),
                    phase=float(np.angle(matrix[right, left])),
                ))
    weights = np.ones(size, dtype=float)
    population, flux = _regional_observables(density, divergence, labels, weights)
    residual, linf = _continuity(previous, time, density, divergence)
    circulation = 0.0
    for first in range(size):
        for second in range(first + 1, size):
            for third in range(second + 1, size):
                if all(abs(hamiltonian[a, b]) > edge_tolerance for a, b in ((first, second), (second, third), (first, third))):
                    circulation += abs(current_matrix[first, second] + current_matrix[second, third] + current_matrix[third, first])
    edge_array = np.asarray(edges, dtype=int).reshape((-1, 2)) if edges else np.empty((0, 2), dtype=int)
    current = np.asarray(currents, dtype=float)
    return FlowFrame(
        time=float(time), density=density, phase=None, phase_gradient=None,
        current=current, divergence=divergence, region_index=labels,
        region_population=population, region_flux=flux,
        boundary_fluxes=tuple(boundaries), crossings=(),
        total_probability=float(np.sum(density)),
        flow_energy=float(0.5 * np.sum(current * current)),
        circulation=float(circulation),
        coherence_flow=float(sum(abs(value) * abs(matrix[left, right]) for (left, right), value in zip(edges, currents))),
        representation="density_graph", edge_indices=edge_array,
        continuity_residual=residual, continuity_linf=linf,
    )


def flow_from_lagrangian_terrain(
    terrain: object,
    *,
    regions: Sequence[int] | Array | None = None,
    velocity_scale: float = 1.0,
    tension_scale: float = 0.25,
    edge_tolerance: float = 1.0e-12,
) -> EffectiveTerrainFlowFrame:
    """Interpret mesoscopic terrain motion as an explicitly effective current.

    For canonical edge ``i < j``, positive current is ``i -> j``.  Relative
    generalized velocity supplies the transport term and coupling tension
    supplies a bounded quasi-static contribution.  This current is never
    reported as quantum probability current.
    """

    for name, value in (
        ("velocity_scale", velocity_scale),
        ("tension_scale", tension_scale),
        ("edge_tolerance", edge_tolerance),
    ):
        if not math.isfinite(float(value)) or float(value) < 0.0:
            raise ValueError(f"{name} must be finite and nonnegative.")
    q = _vector("terrain.q", getattr(terrain, "q"))
    qdot = _vector("terrain.qdot", getattr(terrain, "qdot"))
    if q.shape != qdot.shape:
        raise ValueError("terrain q and qdot must share a shape.")
    size = q.size
    permeability = np.asarray(getattr(terrain, "permeability"), dtype=float)
    coupling = np.asarray(getattr(terrain, "coupling"), dtype=float)
    coherence = np.asarray(getattr(terrain, "coherence_magnitude"), dtype=float)
    phase = np.asarray(getattr(terrain, "coherence_phase"), dtype=float)
    for name, matrix in (
        ("permeability", permeability),
        ("coupling", coupling),
        ("coherence_magnitude", coherence),
        ("coherence_phase", phase),
    ):
        if matrix.shape != (size, size) or not np.all(np.isfinite(matrix)):
            raise ValueError(f"terrain {name} must be a finite square matrix matching q.")
    if not np.allclose(permeability, permeability.T, atol=1.0e-10):
        raise ValueError("terrain permeability must be symmetric.")

    labels = _regions(regions, size, graph=True)
    edges: list[tuple[int, int]] = []
    currents: list[float] = []
    divergence = np.zeros(size, dtype=float)
    boundaries: list[BoundaryFlux] = []
    for left in range(size):
        for right in range(left + 1, size):
            if permeability[left, right] <= edge_tolerance:
                continue
            signed = float(
                velocity_scale
                * permeability[left, right]
                * (qdot[left] - qdot[right])
                + tension_scale
                * coupling[left, right]
                * (q[left] - q[right])
            )
            edges.append((left, right))
            currents.append(signed)
            divergence[left] += signed
            divergence[right] -= signed
            source_node, destination_node = (
                (left, right) if signed >= 0.0 else (right, left)
            )
            source_region = int(labels[source_node])
            destination_region = int(labels[destination_node])
            if source_region != destination_region:
                boundaries.append(
                    BoundaryFlux(
                        boundary=f"terrain-edge:{left}-{right}",
                        source_region=source_region,
                        destination_region=destination_region,
                        direction=1 if signed > EPS else (-1 if signed < -EPS else 0),
                        signed_flux=signed,
                        magnitude=abs(signed),
                        phase=float(phase[right, left]),
                        current_kind="effective_terrain",
                    )
                )
    edge_indices = (
        np.asarray(edges, dtype=int).reshape((-1, 2))
        if edges
        else np.empty((0, 2), dtype=int)
    )
    current = np.asarray(currents, dtype=float)
    region_count = int(np.max(labels)) + 1
    region_coordinate = np.zeros(region_count, dtype=float)
    region_flux = np.zeros(region_count, dtype=float)
    for region in range(region_count):
        mask = labels == region
        region_coordinate[region] = float(np.sum(q[mask]))
        region_flux[region] = -float(np.sum(divergence[mask]))
    coherence_flow = float(
        sum(
            abs(value) * coherence[left, right]
            for (left, right), value in zip(edges, currents)
        )
    )
    return EffectiveTerrainFlowFrame(
        time=float(getattr(terrain, "time")),
        q=q,
        qdot=qdot,
        edge_indices=edge_indices,
        current=current,
        divergence=divergence,
        region_index=labels,
        region_coordinate=region_coordinate,
        region_flux=region_flux,
        boundary_fluxes=tuple(boundaries),
        crossings=(),
        flow_energy=0.5 * float(np.sum(current**2)),
        coherence_flow=coherence_flow,
    )


def emit_flux_events(
    frame: FlowFrame | FlowFrame2D | EffectiveTerrainFlowFrame,
    state: FluxEventState,
    *,
    dt: float,
    threshold: float,
) -> tuple[FlowFrame | FlowFrame2D | EffectiveTerrainFlowFrame, FluxEventState]:
    """Mark accumulated boundary passage without changing the underlying flow.

    The returned crossings are generic transport events for downstream OSC,
    score, or synthesis consumers. They are not quantum measurements. Each
    boundary retains its own remainder after an event, avoiding arbitrary reset
    timing during sustained flow.
    """

    if not math.isfinite(dt) or dt < 0.0:
        raise ValueError("dt must be finite and nonnegative.")
    if not math.isfinite(threshold) or threshold <= 0.0:
        raise ValueError("threshold must be finite and greater than zero.")
    accumulated = dict(state.accumulated)
    events: list[FlowEvent] = []
    for boundary in frame.boundary_fluxes:
        total = accumulated.get(boundary.boundary, 0.0) + (boundary.magnitude * dt)
        count = int(math.floor((total + EPS) / threshold))
        accumulated[boundary.boundary] = max(0.0, total - (count * threshold))
        for _ in range(count):
            events.append(FlowEvent(
                time=frame.time, source_region=boundary.source_region,
                destination_region=boundary.destination_region,
                boundary=boundary.boundary, direction=boundary.direction,
                magnitude=boundary.magnitude, phase=boundary.phase,
                current_kind=boundary.current_kind,
            ))
    return replace(frame, crossings=tuple(events)), FluxEventState(accumulated)


__all__ = [
    "BoundaryFlux", "EffectiveTerrainFlowFrame", "FlowEvent", "FlowFrame", "FlowFrame2D", "FluxEventState",
    "emit_flux_events", "flow_from_density_matrix_graph", "flow_from_observed_current_1d", "flow_from_observed_current_2d",
    "flow_from_lagrangian_terrain", "flow_from_wavefunction_1d", "flow_from_wavefunction_2d",
]
