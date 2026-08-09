"""Physically grounded one-particle Bohm pilot in one spatial dimension."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import numpy as np

from .pilot_wave_field_nd import (
    PilotWaveFieldND,
    TrajectoryBatch,
    normalize_wavefunction,
    split_step_fourier,
)


@dataclass(frozen=True)
class PilotSnapshot1D:
    time: float
    norm: float
    expectation_x: float
    expectation_p: float
    uncertainty_x: float
    energy: float
    trajectories: TrajectoryBatch | None


def gaussian_wavepacket_1d(
    x: np.ndarray,
    *,
    center: float = -3.0,
    sigma: float = 0.8,
    momentum: float = 3.0,
    hbar: float = 1.0,
) -> np.ndarray:
    if sigma <= 0.0:
        raise ValueError("sigma must be positive")
    envelope = np.exp(-((x - center) ** 2) / (4.0 * sigma**2))
    carrier = np.exp(1j * momentum * (x - center) / hbar)
    return np.asarray(envelope * carrier, dtype=np.complex128)


def harmonic_ground_state_1d(
    x: np.ndarray,
    *,
    mass: float = 1.0,
    omega: float = 1.0,
    hbar: float = 1.0,
) -> np.ndarray:
    if mass <= 0.0 or omega <= 0.0 or hbar <= 0.0:
        raise ValueError("mass, omega, and hbar must be positive")
    return np.exp(-0.5 * mass * omega * x**2 / hbar).astype(np.complex128)


class SchrodingerPilot1D:
    """Split-step wavefunction evolution synchronized with Bohm trajectories."""

    coordinate_semantics = "one_particle_1d"

    def __init__(
        self,
        *,
        n_points: int = 512,
        x_min: float = -12.0,
        x_max: float = 12.0,
        psi: np.ndarray | None = None,
        potential: float | np.ndarray | Callable[[np.ndarray], np.ndarray] = 0.0,
        mass: float = 1.0,
        hbar: float = 1.0,
        boundary: str = "periodic",
        node_density_floor: float = 1e-14,
    ) -> None:
        if n_points < 32 or x_max <= x_min:
            raise ValueError("invalid one-dimensional grid")
        self.x = np.linspace(x_min, x_max, int(n_points), endpoint=False)
        self.dx = float(self.x[1] - self.x[0])
        self.mass = float(mass)
        self.hbar = float(hbar)
        if callable(potential):
            potential_value = potential(self.x)
        else:
            potential_value = potential
        self.potential = np.asarray(potential_value, dtype=np.float64)
        if self.potential.ndim and self.potential.shape != self.x.shape:
            raise ValueError("potential must be scalar or match x")
        initial = (
            gaussian_wavepacket_1d(self.x, hbar=self.hbar)
            if psi is None
            else np.asarray(psi, dtype=np.complex128)
        )
        if initial.shape != self.x.shape:
            raise ValueError("psi must match the one-dimensional grid")
        initial = normalize_wavefunction(initial, (self.dx,))
        self.field = PilotWaveFieldND(
            (self.x,),
            initial,
            mass=self.mass,
            hbar=self.hbar,
            boundary=boundary,
            node_density_floor=node_density_floor,
            normalize=False,
            coordinate_semantics=self.coordinate_semantics,
        )
        self.trajectory_positions: np.ndarray | None = None
        self.last_trajectories: TrajectoryBatch | None = None

    @classmethod
    def free_gaussian(cls, **kwargs) -> "SchrodingerPilot1D":
        n_points = int(kwargs.pop("n_points", 512))
        x_min = float(kwargs.pop("x_min", -12.0))
        x_max = float(kwargs.pop("x_max", 12.0))
        center = float(kwargs.pop("center", -3.0))
        sigma = float(kwargs.pop("sigma", 0.8))
        momentum = float(kwargs.pop("momentum", 3.0))
        hbar = float(kwargs.get("hbar", 1.0))
        x = np.linspace(x_min, x_max, n_points, endpoint=False)
        psi = gaussian_wavepacket_1d(
            x,
            center=center,
            sigma=sigma,
            momentum=momentum,
            hbar=hbar,
        )
        return cls(
            n_points=n_points,
            x_min=x_min,
            x_max=x_max,
            psi=psi,
            potential=0.0,
            **kwargs,
        )

    @classmethod
    def harmonic_ground(
        cls,
        *,
        omega: float = 1.0,
        **kwargs,
    ) -> "SchrodingerPilot1D":
        n_points = int(kwargs.pop("n_points", 512))
        x_min = float(kwargs.pop("x_min", -8.0))
        x_max = float(kwargs.pop("x_max", 8.0))
        mass = float(kwargs.get("mass", 1.0))
        hbar = float(kwargs.get("hbar", 1.0))
        x = np.linspace(x_min, x_max, n_points, endpoint=False)
        psi = harmonic_ground_state_1d(
            x, mass=mass, omega=omega, hbar=hbar
        )
        potential = 0.5 * mass * omega**2 * x**2
        return cls(
            n_points=n_points,
            x_min=x_min,
            x_max=x_max,
            psi=psi,
            potential=potential,
            **kwargs,
        )

    @property
    def time(self) -> float:
        return self.field.time

    @property
    def psi(self) -> np.ndarray:
        return self.field.psi.copy()

    def seed_trajectories(
        self,
        size: int,
        *,
        seed: int | None = None,
        jitter: bool = True,
    ) -> np.ndarray:
        self.trajectory_positions = self.field.sample_positions(
            size, seed=seed, jitter=jitter
        )
        return self.trajectory_positions.copy()

    def _propagate(self, dt: float) -> None:
        evolved = split_step_fourier(
            self.field.psi,
            (self.x,),
            dt,
            potential=self.potential,
            mass=self.mass,
            hbar=self.hbar,
        )
        self.field.set_wavefunction(evolved, normalize=True)

    def step(self, dt: float, *, trajectory_method: str = "midpoint") -> PilotSnapshot1D:
        if dt < 0.0:
            raise ValueError("dt must be non-negative")
        if dt > 0.0:
            self._propagate(0.5 * dt)
            if self.trajectory_positions is not None:
                batch = self.field.advance_positions(
                    self.trajectory_positions,
                    dt,
                    method=trajectory_method,
                )
                self.trajectory_positions = np.atleast_2d(batch.positions)
            self._propagate(0.5 * dt)
            self.field.time += dt

        if self.trajectory_positions is not None:
            velocities, densities, valid = self.field.velocity_at(
                self.trajectory_positions
            )
            self.last_trajectories = TrajectoryBatch(
                positions=self.trajectory_positions.copy(),
                velocities=velocities,
                densities=densities,
                valid=valid,
                active=np.ones(len(self.trajectory_positions), dtype=bool),
            )
        return self.snapshot()

    def snapshot(self) -> PilotSnapshot1D:
        density = self.field.density
        mean_x = float(np.sum(self.x * density) * self.dx)
        variance = float(np.sum((self.x - mean_x) ** 2 * density) * self.dx)
        spectrum = np.fft.fft(self.field.psi)
        k = 2.0 * np.pi * np.fft.fftfreq(len(self.x), d=self.dx)
        weights = np.abs(spectrum) ** 2
        expectation_p = float(
            self.hbar * np.sum(k * weights) / max(float(np.sum(weights)), 1e-30)
        )
        return PilotSnapshot1D(
            time=self.time,
            norm=self.field.norm,
            expectation_x=mean_x,
            expectation_p=expectation_p,
            uncertainty_x=float(np.sqrt(max(variance, 0.0))),
            energy=self.field.energy_expectation(self.potential),
            trajectories=self.last_trajectories,
        )

