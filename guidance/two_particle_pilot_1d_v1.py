"""Two one-dimensional particles guided in joint (x1, x2) configuration space."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .pilot_wave_field_nd import (
    PilotWaveFieldND,
    TrajectoryBatch,
    normalize_wavefunction,
    split_step_fourier,
)


def entangled_gaussian_state(
    x1: np.ndarray,
    x2: np.ndarray,
    *,
    sigma_center: float = 1.8,
    sigma_relative: float = 0.8,
    phase_coupling: float = 0.65,
) -> np.ndarray:
    """Correlated amplitude with a joint phase S = coupling*x1*x2."""
    if sigma_center <= 0.0 or sigma_relative <= 0.0:
        raise ValueError("Gaussian widths must be positive")
    q1, q2 = np.meshgrid(x1, x2, indexing="ij")
    envelope = np.exp(
        -((q1 + q2) ** 2) / (8.0 * sigma_center**2)
        -((q1 - q2) ** 2) / (8.0 * sigma_relative**2)
    )
    return envelope * np.exp(1j * phase_coupling * q1 * q2)


def product_gaussian_state(
    x1: np.ndarray,
    x2: np.ndarray,
    *,
    centers: tuple[float, float] = (-1.0, 1.0),
    sigmas: tuple[float, float] = (0.9, 0.9),
    momenta: tuple[float, float] = (1.0, -1.0),
    hbar: float = 1.0,
) -> np.ndarray:
    q1, q2 = np.meshgrid(x1, x2, indexing="ij")
    first = np.exp(-((q1 - centers[0]) ** 2) / (4.0 * sigmas[0] ** 2))
    second = np.exp(-((q2 - centers[1]) ** 2) / (4.0 * sigmas[1] ** 2))
    phase = np.exp(
        1j
        * (
            momenta[0] * (q1 - centers[0])
            + momenta[1] * (q2 - centers[1])
        )
        / hbar
    )
    return first * second * phase


@dataclass(frozen=True)
class TwoParticleSnapshot:
    time: float
    norm: float
    expectation_x1: float
    expectation_x2: float
    covariance: float
    energy: float
    configurations: TrajectoryBatch | None
    coordinate_semantics: str = "two_particle_1d"


class TwoParticlePilot1D:
    """Joint wavefunction whose two axes are particles, not a physical plane."""

    coordinate_semantics = "two_particle_1d"

    def __init__(
        self,
        *,
        n_points: int = 128,
        x_min: float = -8.0,
        x_max: float = 8.0,
        psi: np.ndarray | None = None,
        masses: tuple[float, float] = (1.0, 1.0),
        hbar: float = 1.0,
        potential: float | np.ndarray = 0.0,
        node_density_floor: float = 1e-14,
    ) -> None:
        if n_points < 24 or x_max <= x_min:
            raise ValueError("invalid two-particle grid")
        self.x1 = np.linspace(x_min, x_max, n_points, endpoint=False)
        self.x2 = np.linspace(x_min, x_max, n_points, endpoint=False)
        self.axes = (self.x1, self.x2)
        self.masses = tuple(float(value) for value in masses)
        self.hbar = float(hbar)
        initial = (
            entangled_gaussian_state(self.x1, self.x2)
            if psi is None
            else np.asarray(psi, dtype=np.complex128)
        )
        if initial.shape != (n_points, n_points):
            raise ValueError("psi must have shape (n_points, n_points)")
        self.potential = np.asarray(potential, dtype=np.float64)
        if self.potential.ndim and self.potential.shape != initial.shape:
            raise ValueError("potential must be scalar or match psi")
        spacing = (
            float(self.x1[1] - self.x1[0]),
            float(self.x2[1] - self.x2[0]),
        )
        initial = normalize_wavefunction(initial, spacing)
        self.field = PilotWaveFieldND(
            self.axes,
            initial,
            mass=self.masses,
            hbar=self.hbar,
            boundary="periodic",
            node_density_floor=node_density_floor,
            coordinate_semantics=self.coordinate_semantics,
        )
        self.configurations: np.ndarray | None = None
        self.last_configurations: TrajectoryBatch | None = None

    @classmethod
    def entangled(cls, *, phase_coupling: float = 0.65, **kwargs) -> "TwoParticlePilot1D":
        n_points = int(kwargs.get("n_points", 128))
        x_min = float(kwargs.get("x_min", -8.0))
        x_max = float(kwargs.get("x_max", 8.0))
        axis = np.linspace(x_min, x_max, n_points, endpoint=False)
        psi = entangled_gaussian_state(
            axis, axis, phase_coupling=phase_coupling
        )
        return cls(psi=psi, **kwargs)

    @classmethod
    def separable(cls, **kwargs) -> "TwoParticlePilot1D":
        n_points = int(kwargs.get("n_points", 128))
        x_min = float(kwargs.get("x_min", -8.0))
        x_max = float(kwargs.get("x_max", 8.0))
        hbar = float(kwargs.get("hbar", 1.0))
        axis = np.linspace(x_min, x_max, n_points, endpoint=False)
        psi = product_gaussian_state(axis, axis, hbar=hbar)
        return cls(psi=psi, **kwargs)

    @property
    def time(self) -> float:
        return self.field.time

    def seed_configurations(self, size: int, *, seed: int | None = None) -> np.ndarray:
        self.configurations = self.field.sample_positions(size, seed=seed)
        return self.configurations.copy()

    def velocity_at(self, x1: float, x2: float) -> tuple[float, float]:
        velocity, _density, _valid = self.field.velocity_at(
            np.array([x1, x2], dtype=np.float64)
        )
        return float(velocity[0]), float(velocity[1])

    def nonlocal_response(
        self,
        *,
        fixed_x1: float,
        x2_values: np.ndarray,
    ) -> np.ndarray:
        values = np.asarray(x2_values, dtype=np.float64)
        points = np.column_stack((np.full(values.shape, fixed_x1), values))
        velocity, _density, _valid = self.field.velocity_at(points)
        return velocity[:, 0]

    def _propagate(self, dt: float) -> None:
        state = split_step_fourier(
            self.field.psi,
            self.axes,
            dt,
            potential=self.potential,
            mass=self.masses,
            hbar=self.hbar,
        )
        self.field.set_wavefunction(state, normalize=True)

    def step(self, dt: float, *, trajectory_method: str = "midpoint") -> TwoParticleSnapshot:
        if dt < 0.0:
            raise ValueError("dt must be non-negative")
        if dt > 0.0:
            self._propagate(0.5 * dt)
            active = None
            if self.configurations is not None:
                batch = self.field.advance_positions(
                    self.configurations, dt, method=trajectory_method
                )
                self.configurations = np.atleast_2d(batch.positions)
                active = np.atleast_1d(batch.active)
            self._propagate(0.5 * dt)
            self.field.time += dt
            if self.configurations is not None:
                velocities, densities, valid = self.field.velocity_at(
                    self.configurations
                )
                self.last_configurations = TrajectoryBatch(
                    self.configurations.copy(),
                    velocities,
                    densities,
                    valid,
                    np.ones(len(self.configurations), dtype=bool)
                    if active is None
                    else active,
                )
        return self.snapshot()

    def snapshot(self) -> TwoParticleSnapshot:
        q1, q2 = np.meshgrid(self.x1, self.x2, indexing="ij")
        density = self.field.density
        measure = self.field.cell_volume
        mean1 = float(np.sum(q1 * density) * measure)
        mean2 = float(np.sum(q2 * density) * measure)
        covariance = float(
            np.sum((q1 - mean1) * (q2 - mean2) * density) * measure
        )
        return TwoParticleSnapshot(
            time=self.time,
            norm=self.field.norm,
            expectation_x1=mean1,
            expectation_x2=mean2,
            covariance=covariance,
            energy=self.field.energy_expectation(self.potential),
            configurations=self.last_configurations,
        )

