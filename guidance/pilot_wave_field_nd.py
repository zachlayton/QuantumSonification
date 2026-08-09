"""Dimension-independent spatial Bohm guidance on uniform Cartesian grids.

This is a physical field/trajectory layer, not a renderer.  It computes
probability current directly from the complex wavefunction and contains no
noise, damping, inertia, velocity clipping, or phase unwrapping.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from typing import Sequence

import numpy as np


Array = np.ndarray


def _as_tuple(value: float | Sequence[float], dimension: int) -> tuple[float, ...]:
    if np.isscalar(value):
        return tuple(float(value) for _ in range(dimension))
    result = tuple(float(item) for item in value)
    if len(result) != dimension:
        raise ValueError(f"expected {dimension} values, received {len(result)}")
    return result


def _validate_axes(axes: Sequence[Array], shape: tuple[int, ...]) -> tuple[tuple[Array, ...], tuple[float, ...]]:
    if len(axes) != len(shape):
        raise ValueError("one coordinate axis is required per psi dimension")
    clean_axes: list[Array] = []
    spacing: list[float] = []
    for dimension, (axis, size) in enumerate(zip(axes, shape)):
        coordinate = np.asarray(axis, dtype=np.float64)
        if coordinate.ndim != 1 or len(coordinate) != size:
            raise ValueError(f"axis {dimension} does not match psi shape")
        if size < 4:
            raise ValueError("each grid dimension requires at least four points")
        differences = np.diff(coordinate)
        if np.any(differences <= 0.0) or not np.allclose(
            differences, differences[0], rtol=1e-10, atol=1e-12
        ):
            raise ValueError("PilotWaveFieldND requires uniform increasing axes")
        clean_axes.append(coordinate.copy())
        spacing.append(float(differences[0]))
    return tuple(clean_axes), tuple(spacing)


def normalize_wavefunction(psi: Array, spacing: Sequence[float]) -> Array:
    state = np.asarray(psi, dtype=np.complex128)
    cell_volume = float(np.prod(tuple(spacing)))
    norm_squared = float(np.sum(np.abs(state) ** 2) * cell_volume)
    if norm_squared <= 1e-30:
        raise ValueError("wavefunction norm is zero")
    return state / np.sqrt(norm_squared)


def split_step_fourier(
    psi: Array,
    axes: Sequence[Array],
    dt: float,
    *,
    potential: float | Array = 0.0,
    mass: float | Sequence[float] = 1.0,
    hbar: float = 1.0,
) -> Array:
    """Advance one periodic Cartesian field with a Strang split step."""
    state = np.asarray(psi, dtype=np.complex128)
    if dt < 0.0:
        raise ValueError("dt must be non-negative")
    if dt == 0.0:
        return state.copy()
    if hbar <= 0.0:
        raise ValueError("hbar must be positive")
    clean_axes, spacing = _validate_axes(axes, state.shape)
    masses = _as_tuple(mass, state.ndim)
    if any(value <= 0.0 for value in masses):
        raise ValueError("masses must be positive")
    potential_array = np.asarray(potential, dtype=np.float64)
    if potential_array.ndim and potential_array.shape != state.shape:
        raise ValueError("potential must be scalar or match psi")

    half_potential = np.exp(-0.5j * potential_array * dt / hbar)
    working = half_potential * state
    spectrum = np.fft.fftn(working)
    kinetic_energy = np.zeros(state.shape, dtype=np.float64)
    for axis_index, (size, dx, axis_mass) in enumerate(
        zip(state.shape, spacing, masses)
    ):
        k = 2.0 * np.pi * np.fft.fftfreq(size, d=dx)
        reshape = [1] * state.ndim
        reshape[axis_index] = size
        kinetic_energy += (hbar**2 * k.reshape(reshape) ** 2) / (2.0 * axis_mass)
    working = np.fft.ifftn(
        spectrum * np.exp(-1j * kinetic_energy * dt / hbar)
    )
    return np.asarray(half_potential * working, dtype=np.complex128)


@dataclass(frozen=True)
class TrajectoryBatch:
    positions: Array
    velocities: Array
    densities: Array
    valid: Array
    active: Array


class PilotWaveFieldND:
    """Complex spatial field and exact current-over-density guidance law."""

    VALID_BOUNDARIES = {"periodic", "reflecting", "absorbing"}

    def __init__(
        self,
        axes: Sequence[Array],
        psi: Array,
        *,
        mass: float | Sequence[float] = 1.0,
        hbar: float = 1.0,
        boundary: str = "periodic",
        node_density_floor: float = 1e-14,
        normalize: bool = True,
        coordinate_semantics: str = "one_particle_physical_space",
    ) -> None:
        state = np.asarray(psi, dtype=np.complex128)
        if state.ndim < 1 or state.ndim > 3:
            raise ValueError("v1 supports one, two, or three grid dimensions")
        self.axes, self.spacing = _validate_axes(axes, state.shape)
        self.dimension = state.ndim
        self.shape = state.shape
        self.mass = _as_tuple(mass, self.dimension)
        if any(value <= 0.0 for value in self.mass):
            raise ValueError("masses must be positive")
        self.hbar = float(hbar)
        if self.hbar <= 0.0:
            raise ValueError("hbar must be positive")
        self.boundary = str(boundary).lower()
        if self.boundary not in self.VALID_BOUNDARIES:
            raise ValueError(f"boundary must be one of {sorted(self.VALID_BOUNDARIES)}")
        self.node_density_floor = float(node_density_floor)
        if self.node_density_floor <= 0.0:
            raise ValueError("node_density_floor must be positive")
        self.coordinate_semantics = str(coordinate_semantics)
        self.cell_volume = float(np.prod(self.spacing))
        self.time = 0.0
        self.set_wavefunction(state, normalize=normalize)

    @property
    def norm(self) -> float:
        return float(np.sum(self.density) * self.cell_volume)

    def set_wavefunction(self, psi: Array, *, normalize: bool = False) -> None:
        state = np.asarray(psi, dtype=np.complex128)
        if state.shape != self.shape:
            raise ValueError("new wavefunction must retain the grid shape")
        self.psi = (
            normalize_wavefunction(state, self.spacing) if normalize else state.copy()
        )
        self._recalculate()

    def _spectral_derivative(self, values: Array, axis: int) -> Array:
        k = 2.0 * np.pi * np.fft.fftfreq(
            self.shape[axis], d=self.spacing[axis]
        )
        # The even-grid Nyquist mode has no unique signed first derivative.
        # Setting it to zero preserves the real derivative of real fields and
        # prevents a spurious Bohm current in real stationary orbitals.
        if self.shape[axis] % 2 == 0:
            k[self.shape[axis] // 2] = 0.0
        reshape = [1] * self.dimension
        reshape[axis] = self.shape[axis]
        return np.fft.ifftn(
            1j * k.reshape(reshape) * np.fft.fftn(values)
        )

    def gradient(self, values: Array) -> tuple[Array, ...]:
        field = np.asarray(values)
        if field.shape != self.shape:
            raise ValueError("gradient field must match psi")
        if self.boundary == "periodic":
            return tuple(
                self._spectral_derivative(field, axis)
                for axis in range(self.dimension)
            )
        result = np.gradient(field, *self.spacing, edge_order=2)
        return (result,) if self.dimension == 1 else tuple(result)

    def laplacian(self, values: Array) -> Array:
        field = np.asarray(values)
        if field.shape != self.shape:
            raise ValueError("Laplacian field must match psi")
        if self.boundary == "periodic":
            spectrum = np.fft.fftn(field)
            k_squared = np.zeros(self.shape, dtype=np.float64)
            for axis, (size, dx) in enumerate(zip(self.shape, self.spacing)):
                k = 2.0 * np.pi * np.fft.fftfreq(size, d=dx)
                reshape = [1] * self.dimension
                reshape[axis] = size
                k_squared += k.reshape(reshape) ** 2
            return np.fft.ifftn(-k_squared * spectrum)
        result = np.zeros(self.shape, dtype=np.result_type(field, np.float64))
        for axis, first in enumerate(self.gradient(field)):
            result += self.gradient(first)[axis]
        return result

    def _recalculate(self) -> None:
        self.density = np.abs(self.psi) ** 2
        self.valid_mask = self.density > self.node_density_floor
        self.psi_gradient = self.gradient(self.psi)
        self.current = tuple(
            (self.hbar / axis_mass)
            * np.imag(np.conj(self.psi) * derivative)
            for axis_mass, derivative in zip(self.mass, self.psi_gradient)
        )
        self.velocity = tuple(
            np.divide(
                component,
                self.density,
                out=np.zeros_like(component, dtype=np.float64),
                where=self.valid_mask,
            )
            for component in self.current
        )
        amplitude = np.abs(self.psi)
        laplacian_amplitude = np.real(self.laplacian(amplitude))
        # A scalar mass is exact for one-particle isotropic space. For a
        # multi-coordinate configuration, sum each mass-weighted curvature.
        if len(set(self.mass)) == 1:
            quantum = -(
                self.hbar**2 / (2.0 * self.mass[0])
            ) * np.divide(
                laplacian_amplitude,
                amplitude,
                out=np.zeros_like(amplitude),
                where=self.valid_mask,
            )
        else:
            quantum = np.zeros(self.shape, dtype=np.float64)
            for axis, axis_mass in enumerate(self.mass):
                second = np.real(self.gradient(self.gradient(amplitude)[axis])[axis])
                quantum -= (self.hbar**2 / (2.0 * axis_mass)) * np.divide(
                    second,
                    amplitude,
                    out=np.zeros_like(amplitude),
                    where=self.valid_mask,
                )
        self.quantum_potential = quantum

    def divergence(self, components: Sequence[Array]) -> Array:
        if len(components) != self.dimension:
            raise ValueError("one component is required per dimension")
        result = np.zeros(self.shape, dtype=np.float64)
        for axis, component in enumerate(components):
            result += np.real(self.gradient(np.asarray(component))[axis])
        return result

    def continuity_residual(
        self,
        density_before: Array,
        density_after: Array,
        dt: float,
        *,
        currents: Sequence[Array] | None = None,
    ) -> Array:
        if dt <= 0.0:
            raise ValueError("dt must be positive")
        before = np.asarray(density_before, dtype=np.float64)
        after = np.asarray(density_after, dtype=np.float64)
        if before.shape != self.shape or after.shape != self.shape:
            raise ValueError("densities must match psi")
        return (after - before) / dt + self.divergence(
            self.current if currents is None else currents
        )

    def interpolate(self, values: Array, positions: Array) -> Array:
        field = np.asarray(values)
        if field.shape != self.shape:
            raise ValueError("interpolated field must match psi")
        points = np.asarray(positions, dtype=np.float64)
        single = points.ndim == 1
        points = np.atleast_2d(points)
        if points.shape[1] != self.dimension:
            raise ValueError("position dimension does not match field")

        lower_indices: list[Array] = []
        upper_indices: list[Array] = []
        fractions: list[Array] = []
        for axis_index, (axis, dx, size) in enumerate(
            zip(self.axes, self.spacing, self.shape)
        ):
            coordinate = (points[:, axis_index] - axis[0]) / dx
            if self.boundary == "periodic":
                base = np.floor(coordinate).astype(np.int64)
                fraction = coordinate - np.floor(coordinate)
                lower_indices.append(base % size)
                upper_indices.append((base + 1) % size)
            else:
                coordinate = np.clip(coordinate, 0.0, size - 1.0)
                base = np.minimum(np.floor(coordinate).astype(np.int64), size - 2)
                fraction = coordinate - base
                lower_indices.append(base)
                upper_indices.append(base + 1)
            fractions.append(fraction)

        result = np.zeros(len(points), dtype=field.dtype)
        for corner in product((0, 1), repeat=self.dimension):
            indices = []
            weight = np.ones(len(points), dtype=np.float64)
            for axis, upper in enumerate(corner):
                indices.append(
                    upper_indices[axis] if upper else lower_indices[axis]
                )
                weight *= fractions[axis] if upper else (1.0 - fractions[axis])
            result += weight * field[tuple(indices)]
        return result[0] if single else result

    def velocity_at(self, positions: Array) -> tuple[Array, Array, Array]:
        points = np.asarray(positions, dtype=np.float64)
        single = points.ndim == 1
        points = np.atleast_2d(points)
        density = np.asarray(self.interpolate(self.density, points), dtype=np.float64)
        valid = density > self.node_density_floor
        components = np.column_stack(
            [self.interpolate(component, points) for component in self.current]
        )
        velocities = np.divide(
            components,
            density[:, None],
            out=np.zeros_like(components, dtype=np.float64),
            where=valid[:, None],
        )
        if single:
            return velocities[0], density[0], valid[0]
        return velocities, density, valid

    def apply_boundary(self, positions: Array) -> tuple[Array, Array]:
        points = np.asarray(positions, dtype=np.float64).copy()
        single = points.ndim == 1
        points = np.atleast_2d(points)
        active = np.ones(len(points), dtype=bool)
        for axis_index, (axis, dx, size) in enumerate(
            zip(self.axes, self.spacing, self.shape)
        ):
            lower = float(axis[0])
            upper = float(axis[-1] + dx) if self.boundary == "periodic" else float(axis[-1])
            if self.boundary == "periodic":
                points[:, axis_index] = (
                    (points[:, axis_index] - lower) % (upper - lower)
                ) + lower
            elif self.boundary == "reflecting":
                span = upper - lower
                folded = (points[:, axis_index] - lower) % (2.0 * span)
                points[:, axis_index] = lower + np.where(
                    folded <= span, folded, 2.0 * span - folded
                )
            else:
                inside = (
                    (points[:, axis_index] >= lower)
                    & (points[:, axis_index] <= upper)
                )
                active &= inside
                points[:, axis_index] = np.clip(
                    points[:, axis_index], lower, upper
                )
        if single:
            return points[0], active[0]
        return points, active

    def advance_positions(
        self,
        positions: Array,
        dt: float,
        *,
        method: str = "midpoint",
    ) -> TrajectoryBatch:
        if dt < 0.0:
            raise ValueError("dt must be non-negative")
        points = np.asarray(positions, dtype=np.float64)
        single = points.ndim == 1
        points = np.atleast_2d(points)
        if points.shape[1] != self.dimension:
            raise ValueError("position dimension does not match field")
        if method not in {"midpoint", "rk4"}:
            raise ValueError("method must be midpoint or rk4")

        if method == "midpoint":
            k1, _, _ = self.velocity_at(points)
            middle, active_middle = self.apply_boundary(points + 0.5 * dt * k1)
            k2, _, _ = self.velocity_at(middle)
            advanced = points + dt * k2
            velocities = k2
            active = active_middle
        else:
            k1, _, _ = self.velocity_at(points)
            p2, a2 = self.apply_boundary(points + 0.5 * dt * k1)
            k2, _, _ = self.velocity_at(p2)
            p3, a3 = self.apply_boundary(points + 0.5 * dt * k2)
            k3, _, _ = self.velocity_at(p3)
            p4, a4 = self.apply_boundary(points + dt * k3)
            k4, _, _ = self.velocity_at(p4)
            velocities = (k1 + 2.0 * k2 + 2.0 * k3 + k4) / 6.0
            advanced = points + dt * velocities
            active = a2 & a3 & a4

        advanced, boundary_active = self.apply_boundary(advanced)
        active &= boundary_active
        final_velocity, density, valid = self.velocity_at(advanced)
        batch = TrajectoryBatch(
            positions=advanced,
            velocities=final_velocity,
            densities=density,
            valid=valid,
            active=active,
        )
        if not single:
            return batch
        return TrajectoryBatch(
            positions=batch.positions[0],
            velocities=batch.velocities[0],
            densities=batch.densities[0],
            valid=batch.valid[0],
            active=batch.active[0],
        )

    def sample_positions(
        self,
        size: int,
        *,
        seed: int | None = None,
        jitter: bool = True,
    ) -> Array:
        if size < 1:
            raise ValueError("size must be positive")
        probabilities = self.density.reshape(-1).astype(np.float64)
        probabilities /= max(float(np.sum(probabilities)), 1e-30)
        rng = np.random.default_rng(seed)
        flat = rng.choice(probabilities.size, size=size, p=probabilities)
        indices = np.column_stack(np.unravel_index(flat, self.shape))
        positions = np.column_stack(
            [axis[indices[:, dimension]] for dimension, axis in enumerate(self.axes)]
        ).astype(np.float64)
        if jitter:
            positions += rng.uniform(-0.5, 0.5, size=positions.shape) * np.asarray(
                self.spacing
            )
            positions, _ = self.apply_boundary(positions)
        return positions

    def energy_expectation(self, potential: float | Array = 0.0) -> float:
        potential_array = np.asarray(potential, dtype=np.float64)
        kinetic = np.zeros(self.shape, dtype=np.float64)
        for axis_mass, derivative in zip(self.mass, self.psi_gradient):
            kinetic += (self.hbar**2 / (2.0 * axis_mass)) * np.abs(derivative) ** 2
        return float(
            np.sum(kinetic + potential_array * self.density) * self.cell_volume
        )
