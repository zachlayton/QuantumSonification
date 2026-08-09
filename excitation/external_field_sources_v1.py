"""Wavefunction engines for uniform magnetic and electric external fields.

The implementations use atomic/natural units by default.  Landau states use
the Landau gauge A=(0, Bx, 0) and calculate gauge-covariant current.  Hydrogen
Zeeman and Stark sources evolve a finite hydrogenic basis under an explicit
Hermitian field Hamiltonian while retaining the continuous 3D wavefunction.
"""

from __future__ import annotations

import math
from typing import Literal, Sequence

import numpy as np

from excitation.wavefunction_sources_v1 import (
    EPS,
    WavefunctionDescriptor,
    WavefunctionFrame,
    _frame_from_psi,
    _hermite,
    _hydrogen_radial,
    _normalize,
    spherical_harmonic,
)


Array = np.ndarray


class LandauLevelSource:
    """Charged particle in a uniform perpendicular magnetic field.

    Basis entries are ``(level_n, momentum_index, coefficient)``.  The integer
    momentum index fixes k_y=2*pi*j/L_y and therefore the guiding center.  A
    superposition of different Landau levels produces cyclotron-time field
    motion without inventing an external event clock.
    """

    def __init__(
        self,
        *,
        grid_shape: int | Sequence[int] = 64,
        extent: float | Sequence[float] = (14.0, 14.0),
        magnetic_field: float = 1.0,
        charge: float = 1.0,
        mass: float = 1.0,
        hbar: float = 1.0,
        states: Sequence[tuple[int, int, complex]] | None = None,
    ) -> None:
        if np.isscalar(grid_shape):
            grid_shape = (int(grid_shape), int(grid_shape))
        if np.isscalar(extent):
            extent = (float(extent), float(extent))
        self.grid_shape = tuple(int(value) for value in grid_shape)
        self.extent = tuple(float(value) for value in extent)
        if len(self.grid_shape) != 2 or len(self.extent) != 2:
            raise ValueError("Landau levels require a two-dimensional grid")
        if min(self.grid_shape) < 8 or min(self.extent) <= 0.0:
            raise ValueError("invalid Landau grid")
        if mass <= 0.0 or hbar <= 0.0 or abs(charge * magnetic_field) <= EPS:
            raise ValueError("mass, hbar, and nonzero qB are required")
        self.magnetic_field = float(magnetic_field)
        self.charge = float(charge)
        self.mass = float(mass)
        self.hbar = float(hbar)
        self.cyclotron_angular_frequency = abs(charge * magnetic_field) / mass
        self.magnetic_length = math.sqrt(hbar / abs(charge * magnetic_field))
        self.coordinates = tuple(
            np.linspace(-length / 2.0, length / 2.0, count, endpoint=False)
            for length, count in zip(self.extent, self.grid_shape)
        )
        self.spacing = tuple(float(axis[1] - axis[0]) for axis in self.coordinates)
        self.x_grid, self.y_grid = np.meshgrid(*self.coordinates, indexing="ij")
        self.cell_area = float(np.prod(self.spacing))
        self.states = list(states or [(0, -1, 0.65), (1, 0, 1.0j), (2, 1, 0.45)])
        if any(level < 0 for level, _index, _coefficient in self.states):
            raise ValueError("Landau level indices must be non-negative")
        coefficient_norm = math.sqrt(sum(abs(value) ** 2 for _n, _j, value in self.states))
        if coefficient_norm <= EPS:
            raise ValueError("at least one Landau coefficient must be nonzero")
        self.states = [
            (level, index, complex(coefficient) / coefficient_norm)
            for level, index, coefficient in self.states
        ]
        self.basis: list[Array] = []
        self.guiding_centers: list[float] = []
        length_y = self.extent[1]
        signed_qb = self.charge * self.magnetic_field
        for level, momentum_index, _coefficient in self.states:
            k_y = 2.0 * math.pi * momentum_index / length_y
            center_x = self.hbar * k_y / signed_qb
            xi = (self.x_grid - center_x) / self.magnetic_length
            orbital = _hermite(level, xi) * np.exp(-0.5 * xi**2) * np.exp(1j * k_y * self.y_grid)
            self.basis.append(_normalize(orbital, self.cell_area))
            self.guiding_centers.append(float(center_x))
        self.time = 0.0

    def reset(self) -> None:
        self.time = 0.0

    def frame(self, dt: float = 0.0) -> WavefunctionFrame:
        if dt < 0.0:
            raise ValueError("dt must be non-negative")
        self.time += dt
        psi = np.zeros(self.grid_shape, dtype=np.complex128)
        level_populations: dict[int, float] = {}
        for (level, _index, coefficient), basis in zip(self.states, self.basis):
            energy = self.hbar * self.cyclotron_angular_frequency * (level + 0.5)
            psi += coefficient * basis * np.exp(-1j * energy * self.time / self.hbar)
            level_populations[level] = level_populations.get(level, 0.0) + abs(coefficient) ** 2
        psi = _normalize(psi, self.cell_area)

        derivative_x, derivative_y = np.gradient(psi, *self.spacing, edge_order=2)
        vector_potential_y = self.magnetic_field * self.x_grid
        mechanical_y = -1j * self.hbar * derivative_y - self.charge * vector_potential_y * psi
        current_x = (self.hbar / self.mass) * np.imag(np.conj(psi) * derivative_x)
        current_y = np.real(np.conj(psi) * mechanical_y) / self.mass
        energy_density = (
            np.abs(-1j * self.hbar * derivative_x) ** 2 + np.abs(mechanical_y) ** 2
        ) / (2.0 * self.mass)
        raw = _frame_from_psi(
            psi=psi,
            coordinates=self.coordinates,
            spacing=self.spacing,
            potential=np.zeros(self.grid_shape),
            time=self.time,
            source="landau_levels",
            hbar=self.hbar,
            mass=self.mass,
            current_override=(current_x, current_y),
            energy_density_override=energy_density,
            metadata={
                "magnetic_field": self.magnetic_field,
                "charge": self.charge,
                "cyclotron_angular_frequency": self.cyclotron_angular_frequency,
                "magnetic_length": self.magnetic_length,
                "levels": tuple(level for level, _index, _value in self.states),
                "level_populations": level_populations,
                "guiding_centers": tuple(self.guiding_centers),
                "gauge": "Landau A_y=B*x",
            },
        )
        return raw

    def descriptor(self, dt: float) -> WavefunctionDescriptor:
        return self.frame(dt).descriptor


class HydrogenExternalFieldSource:
    """Hydrogen basis evolved under orbital Zeeman or electric Stark coupling."""

    def __init__(
        self,
        *,
        effect: Literal["zeeman", "stark"],
        grid_shape: int | Sequence[int] = 32,
        extent: float | Sequence[float] = 20.0,
        field_strength: float = 0.08,
        states: Sequence[tuple[int, int, int]] | None = None,
        initial_coefficients: Sequence[complex] | None = None,
        bohr_radius: float = 1.0,
        hbar: float = 1.0,
    ) -> None:
        if effect not in ("zeeman", "stark"):
            raise ValueError("effect must be zeeman or stark")
        if np.isscalar(grid_shape):
            grid_shape = (int(grid_shape),) * 3
        if np.isscalar(extent):
            extent = (float(extent),) * 3
        self.grid_shape = tuple(int(value) for value in grid_shape)
        self.extent = tuple(float(value) for value in extent)
        if len(self.grid_shape) != 3 or len(self.extent) != 3:
            raise ValueError("hydrogen external-field sources require a 3D grid")
        if min(self.grid_shape) < 8 or min(self.extent) <= 0.0:
            raise ValueError("invalid hydrogen grid")
        self.effect = effect
        self.field_strength = float(field_strength)
        self.bohr_radius = float(bohr_radius)
        self.hbar = float(hbar)
        self.coordinates = tuple(
            np.linspace(-length / 2.0, length / 2.0, count, endpoint=False)
            for length, count in zip(self.extent, self.grid_shape)
        )
        self.spacing = tuple(float(axis[1] - axis[0]) for axis in self.coordinates)
        self.cell_volume = float(np.prod(self.spacing))
        x, y, z = np.meshgrid(*self.coordinates, indexing="ij")
        self.x_grid, self.y_grid, self.z_grid = x, y, z
        radius = np.sqrt(x**2 + y**2 + z**2)
        safe_radius = np.maximum(radius, EPS)
        theta = np.arccos(np.clip(z / safe_radius, -1.0, 1.0))
        phi = np.arctan2(y, x)
        if states is None:
            states = (
                ((2, 1, -1), (2, 1, 1))
                if effect == "zeeman"
                else ((2, 0, 0), (2, 1, 0))
            )
        self.states = tuple(states)
        self.basis = []
        for principal, orbital, magnetic in self.states:
            field = _hydrogen_radial(principal, orbital, radius, self.bohr_radius)
            field = field * spherical_harmonic(orbital, magnetic, theta, phi)
            self.basis.append(_normalize(field, self.cell_volume))

        basis_count = len(self.states)
        if initial_coefficients is None:
            initial_coefficients = (
                (1.0,) * basis_count
                if effect == "zeeman"
                else (1.0,) + (0.0,) * (basis_count - 1)
            )
        coefficients = np.asarray(initial_coefficients, dtype=np.complex128)
        if coefficients.shape != (basis_count,):
            raise ValueError("one initial coefficient is required per basis state")
        coefficient_norm = float(np.linalg.norm(coefficients))
        if coefficient_norm <= EPS:
            raise ValueError("initial coefficients must be nonzero")
        self.initial_coefficients = coefficients / coefficient_norm

        hamiltonian = np.diag(
            [-0.5 / (principal**2) for principal, _orbital, _magnetic in self.states]
        ).astype(np.complex128)
        if effect == "zeeman":
            # Normal orbital Zeeman term in atomic units: (B/2) L_z.
            for index, (_principal, _orbital, magnetic) in enumerate(self.states):
                hamiltonian[index, index] += 0.5 * self.field_strength * magnetic
        else:
            for row, bra in enumerate(self.basis):
                for column, ket in enumerate(self.basis):
                    dipole = np.sum(np.conj(bra) * self.z_grid * ket) * self.cell_volume
                    hamiltonian[row, column] += self.field_strength * dipole
        self.hamiltonian = 0.5 * (hamiltonian + hamiltonian.conj().T)
        self.energies, self.eigenvectors = np.linalg.eigh(self.hamiltonian)
        self.initial_in_eigenbasis = self.eigenvectors.conj().T @ self.initial_coefficients
        softening = 0.5 * min(self.spacing)
        self.coulomb_potential = -1.0 / np.sqrt(radius**2 + softening**2)
        self.time = 0.0

    def reset(self) -> None:
        self.time = 0.0

    def frame(self, dt: float = 0.0) -> WavefunctionFrame:
        if dt < 0.0:
            raise ValueError("dt must be non-negative")
        self.time += dt
        phases = np.exp(-1j * self.energies * self.time / self.hbar)
        coefficients = self.eigenvectors @ (self.initial_in_eigenbasis * phases)
        psi = sum(coefficient * basis for coefficient, basis in zip(coefficients, self.basis))
        psi = _normalize(np.asarray(psi), self.cell_volume)
        probability = np.abs(psi) ** 2
        dipole_z = float(np.sum(self.z_grid * probability) * self.cell_volume)
        angular_momentum_z = float(
            sum(abs(coefficient) ** 2 * state[2] for coefficient, state in zip(coefficients, self.states))
        )
        return _frame_from_psi(
            psi=psi,
            coordinates=self.coordinates,
            spacing=self.spacing,
            potential=self.coulomb_potential + (
                self.field_strength * self.z_grid if self.effect == "stark" else 0.0
            ),
            time=self.time,
            source=f"hydrogen_{self.effect}",
            hbar=self.hbar,
            mass=1.0,
            metadata={
                "effect": self.effect,
                "field_strength": self.field_strength,
                "basis_states": self.states,
                "field_energies": tuple(float(value) for value in self.energies),
                "splitting": float(np.ptp(self.energies)),
                "dipole_z": dipole_z,
                "angular_momentum_z": angular_momentum_z,
                "basis_populations": tuple(float(abs(value) ** 2) for value in coefficients),
                "approximation": "truncated hydrogen basis; orbital normal Zeeman" if self.effect == "zeeman" else "truncated hydrogen basis; linear Stark coupling",
            },
        )

    def descriptor(self, dt: float) -> WavefunctionDescriptor:
        return self.frame(dt).descriptor


class HydrogenZeemanSource(HydrogenExternalFieldSource):
    def __init__(self, **kwargs) -> None:
        super().__init__(effect="zeeman", **kwargs)


class HydrogenStarkSource(HydrogenExternalFieldSource):
    def __init__(self, **kwargs) -> None:
        super().__init__(effect="stark", **kwargs)


__all__ = [
    "HydrogenExternalFieldSource",
    "HydrogenStarkSource",
    "HydrogenZeemanSource",
    "LandauLevelSource",
]
