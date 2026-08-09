"""Three-dimensional spatial Bohm pilots for packets and complex orbitals."""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Sequence

import numpy as np

from .pilot_wave_field_nd import (
    PilotWaveFieldND,
    TrajectoryBatch,
    normalize_wavefunction,
    split_step_fourier,
)


HydrogenState = tuple[int, int, int, complex]


def _associated_legendre(l_value: int, m_value: int, x: np.ndarray) -> np.ndarray:
    m_abs = abs(m_value)
    if l_value < m_abs:
        raise ValueError("spherical harmonics require l >= |m|")
    p_mm = np.ones_like(x, dtype=np.float64)
    if m_abs:
        double_factorial = float(np.prod(np.arange(1, 2 * m_abs, 2)))
        p_mm = (
            (-1.0) ** m_abs
            * double_factorial
            * np.maximum(0.0, 1.0 - x**2) ** (m_abs / 2.0)
        )
    if l_value == m_abs:
        return p_mm
    p_m1m = x * (2 * m_abs + 1) * p_mm
    if l_value == m_abs + 1:
        return p_m1m
    previous_previous, previous = p_mm, p_m1m
    for ell in range(m_abs + 2, l_value + 1):
        current = (
            (2 * ell - 1) * x * previous
            - (ell + m_abs - 1) * previous_previous
        ) / (ell - m_abs)
        previous_previous, previous = previous, current
    return previous


def spherical_harmonic(
    l_value: int,
    m_value: int,
    theta: np.ndarray,
    phi: np.ndarray,
) -> np.ndarray:
    m_abs = abs(m_value)
    normalization = math.sqrt(
        (2 * l_value + 1)
        / (4.0 * math.pi)
        * math.factorial(l_value - m_abs)
        / math.factorial(l_value + m_abs)
    )
    positive = (
        normalization
        * _associated_legendre(l_value, m_abs, np.cos(theta))
        * np.exp(1j * m_abs * phi)
    )
    return ((-1) ** m_abs) * np.conj(positive) if m_value < 0 else positive


def _generalized_laguerre(order: int, alpha: int, x: np.ndarray) -> np.ndarray:
    if order == 0:
        return np.ones_like(x)
    if order == 1:
        return 1.0 + alpha - x
    previous_previous = np.ones_like(x)
    previous = 1.0 + alpha - x
    for index in range(2, order + 1):
        current = (
            (2 * index - 1 + alpha - x) * previous
            - (index - 1 + alpha) * previous_previous
        ) / index
        previous_previous, previous = previous, current
    return previous


def hydrogen_radial(
    n_value: int,
    l_value: int,
    radius: np.ndarray,
    bohr_radius: float = 1.0,
) -> np.ndarray:
    if n_value < 1 or l_value < 0 or l_value >= n_value:
        raise ValueError("hydrogen states require n >= 1 and 0 <= l < n")
    scaled = 2.0 * radius / (n_value * bohr_radius)
    normalization = (2.0 / (n_value * bohr_radius)) ** 1.5
    normalization *= math.sqrt(
        math.factorial(n_value - l_value - 1)
        / (2.0 * n_value * math.factorial(n_value + l_value))
    )
    return (
        normalization
        * np.exp(-0.5 * scaled)
        * scaled**l_value
        * _generalized_laguerre(
            n_value - l_value - 1, 2 * l_value + 1, scaled
        )
    )


def gaussian_wavepacket_3d(
    axes: tuple[np.ndarray, np.ndarray, np.ndarray],
    *,
    center: tuple[float, float, float] = (-3.0, 0.0, 0.0),
    sigma: float = 1.0,
    momentum: tuple[float, float, float] = (2.5, 0.0, 0.0),
    hbar: float = 1.0,
) -> np.ndarray:
    x, y, z = np.meshgrid(*axes, indexing="ij")
    radius_squared = (
        (x - center[0]) ** 2
        + (y - center[1]) ** 2
        + (z - center[2]) ** 2
    )
    phase = (
        momentum[0] * (x - center[0])
        + momentum[1] * (y - center[1])
        + momentum[2] * (z - center[2])
    ) / hbar
    return np.exp(-radius_squared / (4.0 * sigma**2) + 1j * phase)


def hydrogenic_superposition_3d(
    axes: tuple[np.ndarray, np.ndarray, np.ndarray],
    states: Sequence[HydrogenState],
    *,
    time: float = 0.0,
    bohr_radius: float = 1.0,
    hbar: float = 1.0,
) -> np.ndarray:
    x, y, z = np.meshgrid(*axes, indexing="ij")
    radius = np.sqrt(x**2 + y**2 + z**2)
    safe_radius = np.maximum(radius, 1e-15)
    theta = np.arccos(np.clip(z / safe_radius, -1.0, 1.0))
    phi = np.arctan2(y, x)
    psi = np.zeros_like(radius, dtype=np.complex128)
    coefficient_norm = math.sqrt(sum(abs(state[3]) ** 2 for state in states))
    if coefficient_norm <= 0.0:
        raise ValueError("hydrogenic coefficient norm is zero")
    for n_value, l_value, m_value, coefficient in states:
        energy = -0.5 / n_value**2
        orbital = hydrogen_radial(
            n_value, l_value, radius, bohr_radius
        ) * spherical_harmonic(l_value, m_value, theta, phi)
        psi += (
            coefficient
            / coefficient_norm
            * orbital
            * np.exp(-1j * energy * time / hbar)
        )
    return psi


def spherical_harmonic_shell_3d(
    axes: tuple[np.ndarray, np.ndarray, np.ndarray],
    *,
    l_value: int = 2,
    m_value: int = 1,
    radius_center: float = 3.0,
    radial_width: float = 0.8,
) -> np.ndarray:
    x, y, z = np.meshgrid(*axes, indexing="ij")
    radius = np.sqrt(x**2 + y**2 + z**2)
    safe_radius = np.maximum(radius, 1e-15)
    theta = np.arccos(np.clip(z / safe_radius, -1.0, 1.0))
    phi = np.arctan2(y, x)
    radial = np.exp(-((radius - radius_center) ** 2) / (4.0 * radial_width**2))
    return radial * spherical_harmonic(l_value, m_value, theta, phi)


@dataclass(frozen=True)
class PilotSnapshot3D:
    time: float
    norm: float
    expectation_position: tuple[float, float, float]
    rms_radius: float
    energy: float
    valid_fraction: float
    trajectories: TrajectoryBatch | None
    state_family: str


class SchrodingerPilot3D:
    coordinate_semantics = "one_particle_physical_xyz"

    def __init__(
        self,
        *,
        grid_shape: int | tuple[int, int, int] = 40,
        extent: float | tuple[float, float, float] = 20.0,
        psi: np.ndarray | None = None,
        potential: float | np.ndarray = 0.0,
        mass: float = 1.0,
        hbar: float = 1.0,
        node_density_floor: float = 1e-14,
        analytic_hydrogen_states: Sequence[HydrogenState] | None = None,
        bohr_radius: float = 1.0,
        state_family: str = "free_gaussian",
    ) -> None:
        shape = (
            (int(grid_shape),) * 3
            if np.isscalar(grid_shape)
            else tuple(int(value) for value in grid_shape)
        )
        lengths = (
            (float(extent),) * 3
            if np.isscalar(extent)
            else tuple(float(value) for value in extent)
        )
        if len(shape) != 3 or len(lengths) != 3 or min(shape) < 16:
            raise ValueError("invalid three-dimensional grid")
        self.axes = tuple(
            np.linspace(-length / 2.0, length / 2.0, count, endpoint=False)
            for length, count in zip(lengths, shape)
        )
        self.mass = float(mass)
        self.hbar = float(hbar)
        self.bohr_radius = float(bohr_radius)
        self.analytic_hydrogen_states = (
            tuple(analytic_hydrogen_states)
            if analytic_hydrogen_states is not None
            else None
        )
        self.state_family = str(state_family)
        if psi is None:
            if self.analytic_hydrogen_states is not None:
                initial = hydrogenic_superposition_3d(
                    self.axes,
                    self.analytic_hydrogen_states,
                    bohr_radius=self.bohr_radius,
                    hbar=self.hbar,
                )
            else:
                initial = gaussian_wavepacket_3d(self.axes, hbar=self.hbar)
        else:
            initial = np.asarray(psi, dtype=np.complex128)
        if initial.shape != shape:
            raise ValueError("psi must match grid_shape")
        self.potential = np.asarray(potential, dtype=np.float64)
        if self.potential.ndim and self.potential.shape != shape:
            raise ValueError("potential must be scalar or match grid_shape")
        spacing = tuple(float(axis[1] - axis[0]) for axis in self.axes)
        initial = normalize_wavefunction(initial, spacing)
        self.field = PilotWaveFieldND(
            self.axes,
            initial,
            mass=self.mass,
            hbar=self.hbar,
            boundary="periodic",
            node_density_floor=node_density_floor,
            coordinate_semantics=self.coordinate_semantics,
        )
        self.trajectory_positions: np.ndarray | None = None
        self.last_trajectories: TrajectoryBatch | None = None

    @classmethod
    def gaussian(cls, **kwargs) -> "SchrodingerPilot3D":
        shape = kwargs.get("grid_shape", 40)
        extent = kwargs.get("extent", 20.0)
        center = kwargs.pop("center", (-3.0, 0.0, 0.0))
        sigma = kwargs.pop("sigma", 1.0)
        momentum = kwargs.pop("momentum", (2.5, 0.0, 0.0))
        hbar = float(kwargs.get("hbar", 1.0))
        shape_tuple = (shape,) * 3 if np.isscalar(shape) else tuple(shape)
        extent_tuple = (extent,) * 3 if np.isscalar(extent) else tuple(extent)
        axes = tuple(
            np.linspace(-length / 2.0, length / 2.0, int(count), endpoint=False)
            for length, count in zip(extent_tuple, shape_tuple)
        )
        psi = gaussian_wavepacket_3d(
            axes, center=center, sigma=sigma, momentum=momentum, hbar=hbar
        )
        return cls(psi=psi, state_family="free_gaussian", **kwargs)

    @classmethod
    def hydrogenic(
        cls,
        *,
        states: Sequence[HydrogenState] = ((2, 1, 1, 1.0 + 0.0j),),
        bohr_radius: float = 1.0,
        **kwargs,
    ) -> "SchrodingerPilot3D":
        shape = kwargs.get("grid_shape", 40)
        extent = kwargs.get("extent", 20.0)
        shape_tuple = (shape,) * 3 if np.isscalar(shape) else tuple(shape)
        extent_tuple = (extent,) * 3 if np.isscalar(extent) else tuple(extent)
        axes = tuple(
            np.linspace(-length / 2.0, length / 2.0, int(count), endpoint=False)
            for length, count in zip(extent_tuple, shape_tuple)
        )
        x, y, z = np.meshgrid(*axes, indexing="ij")
        radius = np.sqrt(x**2 + y**2 + z**2)
        dx = min(float(axis[1] - axis[0]) for axis in axes)
        potential = -1.0 / np.sqrt(radius**2 + (0.5 * dx) ** 2)
        return cls(
            analytic_hydrogen_states=states,
            bohr_radius=bohr_radius,
            potential=potential,
            state_family="hydrogenic",
            **kwargs,
        )

    @classmethod
    def spherical_harmonic_shell(
        cls,
        *,
        l_value: int = 2,
        m_value: int = 1,
        **kwargs,
    ) -> "SchrodingerPilot3D":
        shape = kwargs.get("grid_shape", 40)
        extent = kwargs.get("extent", 20.0)
        shape_tuple = (shape,) * 3 if np.isscalar(shape) else tuple(shape)
        extent_tuple = (extent,) * 3 if np.isscalar(extent) else tuple(extent)
        axes = tuple(
            np.linspace(-length / 2.0, length / 2.0, int(count), endpoint=False)
            for length, count in zip(extent_tuple, shape_tuple)
        )
        psi = spherical_harmonic_shell_3d(
            axes, l_value=l_value, m_value=m_value
        )
        return cls(psi=psi, state_family="spherical_harmonic_shell", **kwargs)

    @property
    def time(self) -> float:
        return self.field.time

    def seed_trajectories(self, size: int, *, seed: int | None = None) -> np.ndarray:
        self.trajectory_positions = self.field.sample_positions(size, seed=seed)
        return self.trajectory_positions.copy()

    def _set_analytic_time(self, time: float) -> None:
        if self.analytic_hydrogen_states is None:
            raise RuntimeError("no analytic hydrogen state is configured")
        state = hydrogenic_superposition_3d(
            self.axes,
            self.analytic_hydrogen_states,
            time=time,
            bohr_radius=self.bohr_radius,
            hbar=self.hbar,
        )
        self.field.set_wavefunction(state, normalize=True)

    def _propagate_numerical(self, dt: float) -> None:
        state = split_step_fourier(
            self.field.psi,
            self.axes,
            dt,
            potential=self.potential,
            mass=self.mass,
            hbar=self.hbar,
        )
        self.field.set_wavefunction(state, normalize=True)

    def step(self, dt: float, *, trajectory_method: str = "midpoint") -> PilotSnapshot3D:
        if dt < 0.0:
            raise ValueError("dt must be non-negative")
        if dt > 0.0:
            if self.analytic_hydrogen_states is not None:
                self._set_analytic_time(self.time + 0.5 * dt)
            else:
                self._propagate_numerical(0.5 * dt)
            active = None
            if self.trajectory_positions is not None:
                batch = self.field.advance_positions(
                    self.trajectory_positions, dt, method=trajectory_method
                )
                self.trajectory_positions = np.atleast_2d(batch.positions)
                active = np.atleast_1d(batch.active)
            if self.analytic_hydrogen_states is not None:
                self._set_analytic_time(self.time + dt)
            else:
                self._propagate_numerical(0.5 * dt)
            self.field.time += dt
            if self.trajectory_positions is not None:
                velocities, densities, valid = self.field.velocity_at(
                    self.trajectory_positions
                )
                self.last_trajectories = TrajectoryBatch(
                    self.trajectory_positions.copy(),
                    velocities,
                    densities,
                    valid,
                    np.ones(len(self.trajectory_positions), dtype=bool)
                    if active is None
                    else active,
                )
        return self.snapshot()

    def spherical_velocity_components(self, positions: np.ndarray) -> np.ndarray:
        points = np.atleast_2d(np.asarray(positions, dtype=np.float64))
        velocity, _density, _valid = self.field.velocity_at(points)
        radius = np.linalg.norm(points, axis=1)
        cylindrical = np.linalg.norm(points[:, :2], axis=1)
        safe_radius = np.maximum(radius, 1e-15)
        safe_cylindrical = np.maximum(cylindrical, 1e-15)
        e_r = points / safe_radius[:, None]
        e_phi = np.column_stack(
            (-points[:, 1] / safe_cylindrical, points[:, 0] / safe_cylindrical, np.zeros(len(points)))
        )
        e_theta = np.cross(e_phi, e_r)
        return np.column_stack(
            (
                np.sum(velocity * e_r, axis=1),
                np.sum(velocity * e_theta, axis=1),
                np.sum(velocity * e_phi, axis=1),
            )
        )

    def snapshot(self) -> PilotSnapshot3D:
        x, y, z = np.meshgrid(*self.axes, indexing="ij")
        density = self.field.density
        measure = self.field.cell_volume
        means = tuple(
            float(np.sum(coordinate * density) * measure)
            for coordinate in (x, y, z)
        )
        radius_squared = x**2 + y**2 + z**2
        return PilotSnapshot3D(
            time=self.time,
            norm=self.field.norm,
            expectation_position=means,
            rms_radius=float(np.sqrt(np.sum(radius_squared * density) * measure)),
            energy=self.field.energy_expectation(self.potential),
            valid_fraction=float(np.mean(self.field.valid_mask)),
            trajectories=self.last_trajectories,
            state_family=self.state_family,
        )

