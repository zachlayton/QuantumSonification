"""One-particle Bohm experiments in physical two-dimensional space."""

from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np

from .pilot_wave_field_nd import (
    PilotWaveFieldND,
    TrajectoryBatch,
    normalize_wavefunction,
    split_step_fourier,
)


@dataclass(frozen=True)
class PilotSnapshot2D:
    time: float
    norm: float
    expectation_position: tuple[float, float]
    spread: tuple[float, float]
    energy: float
    valid_fraction: float
    trajectories: TrajectoryBatch | None


def _mesh(axes: tuple[np.ndarray, np.ndarray]) -> tuple[np.ndarray, np.ndarray]:
    return np.meshgrid(*axes, indexing="ij")


def gaussian_wavepacket_2d(
    axes: tuple[np.ndarray, np.ndarray],
    *,
    center: tuple[float, float] = (-3.0, 0.0),
    sigma: float | tuple[float, float] = 0.9,
    momentum: tuple[float, float] = (3.0, 0.0),
    hbar: float = 1.0,
) -> np.ndarray:
    x, y = _mesh(axes)
    widths = (float(sigma), float(sigma)) if np.isscalar(sigma) else tuple(sigma)
    if len(widths) != 2 or min(widths) <= 0.0:
        raise ValueError("sigma must contain two positive widths")
    envelope = np.exp(
        -((x - center[0]) ** 2) / (4.0 * widths[0] ** 2)
        -((y - center[1]) ** 2) / (4.0 * widths[1] ** 2)
    )
    phase = np.exp(
        1j
        * (
            momentum[0] * (x - center[0])
            + momentum[1] * (y - center[1])
        )
        / hbar
    )
    return np.asarray(envelope * phase, dtype=np.complex128)


def plane_wave_2d(
    axes: tuple[np.ndarray, np.ndarray],
    wavevector: tuple[float, float] = (1.0, 0.5),
) -> np.ndarray:
    x, y = _mesh(axes)
    return np.exp(1j * (wavevector[0] * x + wavevector[1] * y))


def vortex_state_2d(
    axes: tuple[np.ndarray, np.ndarray],
    *,
    center: tuple[float, float] = (0.0, 0.0),
    sigma: float = 2.0,
    charge: int = 1,
) -> np.ndarray:
    if sigma <= 0.0 or charge == 0:
        raise ValueError("vortex requires positive sigma and nonzero charge")
    x, y = _mesh(axes)
    complex_radius = (x - center[0]) + 1j * np.sign(charge) * (y - center[1])
    core = complex_radius ** abs(int(charge))
    return core * np.exp(
        -((x - center[0]) ** 2 + (y - center[1]) ** 2) / (4.0 * sigma**2)
    )


def harmonic_ground_state_2d(
    axes: tuple[np.ndarray, np.ndarray],
    *,
    mass: float = 1.0,
    omega: float = 1.0,
    hbar: float = 1.0,
) -> np.ndarray:
    x, y = _mesh(axes)
    return np.exp(-0.5 * mass * omega * (x**2 + y**2) / hbar).astype(
        np.complex128
    )


def double_slit_potential_2d(
    axes: tuple[np.ndarray, np.ndarray],
    *,
    barrier_x: float = 0.0,
    barrier_width: float = 0.20,
    slit_separation: float = 2.4,
    slit_width: float = 0.55,
    height: float = 180.0,
) -> np.ndarray:
    x, y = _mesh(axes)
    barrier = np.abs(x - barrier_x) <= 0.5 * barrier_width
    slit_a = np.abs(y - 0.5 * slit_separation) <= 0.5 * slit_width
    slit_b = np.abs(y + 0.5 * slit_separation) <= 0.5 * slit_width
    return np.where(barrier & ~(slit_a | slit_b), height, 0.0)


def emerging_double_slit_state_2d(
    axes: tuple[np.ndarray, np.ndarray],
    *,
    center_x: float = -2.0,
    sigma_x: float = 0.75,
    slit_separation: float = 2.4,
    slit_width: float = 0.42,
    momentum_x: float = 4.0,
    hbar: float = 1.0,
) -> np.ndarray:
    x, y = _mesh(axes)
    longitudinal = np.exp(-((x - center_x) ** 2) / (4.0 * sigma_x**2))
    slits = np.exp(-((y - slit_separation / 2.0) ** 2) / (4.0 * slit_width**2))
    slits += np.exp(-((y + slit_separation / 2.0) ** 2) / (4.0 * slit_width**2))
    return longitudinal * slits * np.exp(1j * momentum_x * x / hbar)


class SchrodingerPilot2D:
    coordinate_semantics = "one_particle_physical_xy"

    def __init__(
        self,
        *,
        grid_shape: int | tuple[int, int] = 128,
        extent: float | tuple[float, float] = 16.0,
        psi: np.ndarray | None = None,
        potential: float | np.ndarray = 0.0,
        mass: float = 1.0,
        hbar: float = 1.0,
        boundary: str = "periodic",
        node_density_floor: float = 1e-14,
    ) -> None:
        shape = (
            (int(grid_shape), int(grid_shape))
            if np.isscalar(grid_shape)
            else tuple(int(value) for value in grid_shape)
        )
        lengths = (
            (float(extent), float(extent))
            if np.isscalar(extent)
            else tuple(float(value) for value in extent)
        )
        if len(shape) != 2 or len(lengths) != 2 or min(shape) < 24 or min(lengths) <= 0.0:
            raise ValueError("invalid two-dimensional grid")
        self.axes = tuple(
            np.linspace(-length / 2.0, length / 2.0, count, endpoint=False)
            for length, count in zip(lengths, shape)
        )
        self.mass = float(mass)
        self.hbar = float(hbar)
        initial = (
            gaussian_wavepacket_2d(self.axes, hbar=self.hbar)
            if psi is None
            else np.asarray(psi, dtype=np.complex128)
        )
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
            boundary=boundary,
            node_density_floor=node_density_floor,
            coordinate_semantics=self.coordinate_semantics,
        )
        self.trajectory_positions: np.ndarray | None = None
        self.last_trajectories: TrajectoryBatch | None = None

    @classmethod
    def plane_wave(cls, *, wavevector=(1.0, 0.5), **kwargs) -> "SchrodingerPilot2D":
        shape = kwargs.get("grid_shape", 128)
        extent = kwargs.get("extent", 16.0)
        shape_tuple = (shape, shape) if np.isscalar(shape) else tuple(shape)
        extent_tuple = (extent, extent) if np.isscalar(extent) else tuple(extent)
        axes = tuple(
            np.linspace(-length / 2.0, length / 2.0, int(count), endpoint=False)
            for length, count in zip(extent_tuple, shape_tuple)
        )
        return cls(psi=plane_wave_2d(axes, wavevector), **kwargs)

    @classmethod
    def gaussian(cls, *, center=(-3.0, 0.0), sigma=0.9, momentum=(3.0, 0.0), **kwargs) -> "SchrodingerPilot2D":
        shape = kwargs.get("grid_shape", 128)
        extent = kwargs.get("extent", 16.0)
        hbar = float(kwargs.get("hbar", 1.0))
        shape_tuple = (shape, shape) if np.isscalar(shape) else tuple(shape)
        extent_tuple = (extent, extent) if np.isscalar(extent) else tuple(extent)
        axes = tuple(
            np.linspace(-length / 2.0, length / 2.0, int(count), endpoint=False)
            for length, count in zip(extent_tuple, shape_tuple)
        )
        psi = gaussian_wavepacket_2d(
            axes, center=center, sigma=sigma, momentum=momentum, hbar=hbar
        )
        return cls(psi=psi, **kwargs)

    @classmethod
    def vortex(cls, *, sigma=2.0, charge=1, **kwargs) -> "SchrodingerPilot2D":
        shape = kwargs.get("grid_shape", 128)
        extent = kwargs.get("extent", 16.0)
        shape_tuple = (shape, shape) if np.isscalar(shape) else tuple(shape)
        extent_tuple = (extent, extent) if np.isscalar(extent) else tuple(extent)
        axes = tuple(
            np.linspace(-length / 2.0, length / 2.0, int(count), endpoint=False)
            for length, count in zip(extent_tuple, shape_tuple)
        )
        return cls(psi=vortex_state_2d(axes, sigma=sigma, charge=charge), **kwargs)

    @classmethod
    def harmonic_ground(cls, *, omega=1.0, **kwargs) -> "SchrodingerPilot2D":
        shape = kwargs.get("grid_shape", 128)
        extent = kwargs.get("extent", 16.0)
        mass = float(kwargs.get("mass", 1.0))
        hbar = float(kwargs.get("hbar", 1.0))
        shape_tuple = (shape, shape) if np.isscalar(shape) else tuple(shape)
        extent_tuple = (extent, extent) if np.isscalar(extent) else tuple(extent)
        axes = tuple(
            np.linspace(-length / 2.0, length / 2.0, int(count), endpoint=False)
            for length, count in zip(extent_tuple, shape_tuple)
        )
        x, y = _mesh(axes)
        potential = 0.5 * mass * omega**2 * (x**2 + y**2)
        psi = harmonic_ground_state_2d(
            axes, mass=mass, omega=omega, hbar=hbar
        )
        return cls(psi=psi, potential=potential, **kwargs)

    @classmethod
    def double_slit(
        cls,
        *,
        emerging: bool = True,
        slit_separation: float = 2.4,
        slit_width: float = 0.55,
        **kwargs,
    ) -> "SchrodingerPilot2D":
        shape = kwargs.get("grid_shape", (192, 128))
        extent = kwargs.get("extent", (20.0, 14.0))
        hbar = float(kwargs.get("hbar", 1.0))
        shape_tuple = (shape, shape) if np.isscalar(shape) else tuple(shape)
        extent_tuple = (extent, extent) if np.isscalar(extent) else tuple(extent)
        axes = tuple(
            np.linspace(-length / 2.0, length / 2.0, int(count), endpoint=False)
            for length, count in zip(extent_tuple, shape_tuple)
        )
        if emerging:
            psi = emerging_double_slit_state_2d(
                axes,
                slit_separation=slit_separation,
                slit_width=slit_width,
                hbar=hbar,
            )
            potential = 0.0
        else:
            psi = gaussian_wavepacket_2d(
                axes,
                center=(-4.0, 0.0),
                sigma=(1.0, 1.5),
                momentum=(4.0, 0.0),
                hbar=hbar,
            )
            potential = double_slit_potential_2d(
                axes,
                slit_separation=slit_separation,
                slit_width=slit_width,
            )
        return cls(psi=psi, potential=potential, grid_shape=shape, extent=extent, **{
            key: value for key, value in kwargs.items() if key not in {"grid_shape", "extent"}
        })

    @property
    def time(self) -> float:
        return self.field.time

    def seed_trajectories(self, size: int, *, seed: int | None = None) -> np.ndarray:
        self.trajectory_positions = self.field.sample_positions(size, seed=seed)
        return self.trajectory_positions.copy()

    def _propagate(self, dt: float) -> None:
        state = split_step_fourier(
            self.field.psi,
            self.axes,
            dt,
            potential=self.potential,
            mass=self.mass,
            hbar=self.hbar,
        )
        self.field.set_wavefunction(state, normalize=True)

    def step(self, dt: float, *, trajectory_method: str = "midpoint") -> PilotSnapshot2D:
        if dt < 0.0:
            raise ValueError("dt must be non-negative")
        if dt > 0.0:
            self._propagate(0.5 * dt)
            active = None
            if self.trajectory_positions is not None:
                batch = self.field.advance_positions(
                    self.trajectory_positions, dt, method=trajectory_method
                )
                self.trajectory_positions = np.atleast_2d(batch.positions)
                active = np.atleast_1d(batch.active)
            self._propagate(0.5 * dt)
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

    def phase_winding(
        self,
        radius: float,
        *,
        center: tuple[float, float] = (0.0, 0.0),
        samples: int = 512,
    ) -> float:
        angles = np.linspace(0.0, 2.0 * np.pi, samples + 1)
        points = np.column_stack(
            (
                center[0] + radius * np.cos(angles),
                center[1] + radius * np.sin(angles),
            )
        )
        phase = np.unwrap(np.angle(self.field.interpolate(self.field.psi, points)))
        return float(phase[-1] - phase[0])

    def circulation(
        self,
        radius: float,
        *,
        center: tuple[float, float] = (0.0, 0.0),
        samples: int = 1024,
    ) -> float:
        angles = np.linspace(0.0, 2.0 * np.pi, samples, endpoint=False)
        points = np.column_stack(
            (
                center[0] + radius * np.cos(angles),
                center[1] + radius * np.sin(angles),
            )
        )
        velocity, _, valid = self.field.velocity_at(points)
        tangents = np.column_stack((-np.sin(angles), np.cos(angles)))
        integrand = np.sum(velocity * tangents, axis=1)
        integrand = np.where(valid, integrand, 0.0)
        return float(np.sum(integrand) * radius * (2.0 * np.pi / samples))

    def snapshot(self) -> PilotSnapshot2D:
        x, y = _mesh(self.axes)
        density = self.field.density
        measure = self.field.cell_volume
        means = (
            float(np.sum(x * density) * measure),
            float(np.sum(y * density) * measure),
        )
        spreads = (
            float(np.sqrt(np.sum((x - means[0]) ** 2 * density) * measure)),
            float(np.sqrt(np.sum((y - means[1]) ** 2 * density) * measure)),
        )
        return PilotSnapshot2D(
            time=self.time,
            norm=self.field.norm,
            expectation_position=means,
            spread=spreads,
            energy=self.field.energy_expectation(self.potential),
            valid_fraction=float(np.mean(self.field.valid_mask)),
            trajectories=self.last_trajectories,
        )

