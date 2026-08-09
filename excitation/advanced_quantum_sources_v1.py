"""Two-electron, singular-shell, and relativistic quantum instruments."""

from __future__ import annotations

from dataclasses import replace
import math
from typing import Sequence

import numpy as np

from excitation.quantum_frames_v1 import DiracSpinorFieldFrame, RelativisticLevelFrame
from excitation.wavefunction_sources_v1 import (
    EPS,
    WavefunctionDescriptor,
    WavefunctionFrame,
    _frame_from_psi,
    _normalize,
)


Array = np.ndarray


class HeliumVariationalTwoElectronSource:
    """Screened-charge variational helium ground state in radial-pair form.

    The full spatial state is the symmetric product of two hydrogenic 1s
    orbitals with exponent zeta.  Angular variables are integrated out, so the
    emitted 2D field is the exact joint radial amplitude for this ansatz, not a
    six-dimensional pointwise wavefunction.  The antisymmetric electron state
    is completed by the spin singlet.
    """

    def __init__(
        self,
        *,
        n_points: int = 128,
        extent: float = 12.0,
        nuclear_charge: float = 2.0,
        effective_charge: float | None = None,
        hbar: float = 1.0,
    ) -> None:
        if n_points < 16 or extent <= 0.0 or nuclear_charge <= 0.0:
            raise ValueError("invalid helium radial grid or nuclear charge")
        self.nuclear_charge = float(nuclear_charge)
        self.effective_charge = float(
            nuclear_charge - 5.0 / 16.0 if effective_charge is None else effective_charge
        )
        if self.effective_charge <= 0.0:
            raise ValueError("effective charge must be positive")
        self.hbar = float(hbar)
        self.spacing = (extent / n_points, extent / n_points)
        radial = (np.arange(n_points, dtype=np.float64) + 0.5) * self.spacing[0]
        self.coordinates = (radial, radial)
        r1, r2 = np.meshgrid(radial, radial, indexing="ij")
        # sqrt of 4*zeta^3*r^2*exp(-2*zeta*r), the normalized 1s radial density.
        radial_amplitude_1 = 2.0 * self.effective_charge**1.5 * r1 * np.exp(-self.effective_charge * r1)
        radial_amplitude_2 = 2.0 * self.effective_charge**1.5 * r2 * np.exp(-self.effective_charge * r2)
        self.radial_amplitude = _normalize(
            radial_amplitude_1 * radial_amplitude_2,
            self.spacing[0] * self.spacing[1],
        )
        zeta = self.effective_charge
        self.kinetic_energy = zeta**2
        self.nuclear_attraction = -2.0 * self.nuclear_charge * zeta
        self.electron_repulsion = 5.0 * zeta / 8.0
        self.variational_energy = (
            self.kinetic_energy + self.nuclear_attraction + self.electron_repulsion
        )
        self.time = 0.0

    def reset(self) -> None:
        self.time = 0.0

    def frame(self, dt: float = 0.0) -> WavefunctionFrame:
        if dt < 0.0:
            raise ValueError("dt must be non-negative")
        self.time += dt
        psi = self.radial_amplitude * np.exp(
            -1j * self.variational_energy * self.time / self.hbar
        )
        probability = np.abs(psi) ** 2
        energy_density = self.variational_energy * probability
        zeros = np.zeros_like(probability)
        return _frame_from_psi(
            psi=psi,
            coordinates=self.coordinates,
            spacing=self.spacing,
            potential=zeros,
            time=self.time,
            source="helium_variational_two_electron",
            hbar=self.hbar,
            mass=1.0,
            current_override=(zeros, zeros),
            energy_density_override=energy_density,
            metadata={
                "nuclear_charge": self.nuclear_charge,
                "effective_charge": self.effective_charge,
                "kinetic_energy": self.kinetic_energy,
                "nuclear_attraction": self.nuclear_attraction,
                "electron_repulsion": self.electron_repulsion,
                "variational_energy": self.variational_energy,
                "spatial_exchange_symmetry": "symmetric",
                "spin_state": "singlet",
                "total_fermion_exchange_symmetry": "antisymmetric",
                "representation": "angle-integrated joint radial amplitude",
                "ansatz": "product of screened hydrogenic 1s orbitals",
            },
        )

    def descriptor(self, dt: float) -> WavefunctionDescriptor:
        return self.frame(dt).descriptor


class DeltaFunctionShellSource:
    """S-wave radial solver for V(r)=g*delta(r-a) on a finite box.

    The delta distribution is represented by one grid cell with integrated
    strength g.  Eigenstates therefore converge to the derivative-jump
    boundary condition as the radial grid is refined.
    """

    def __init__(
        self,
        *,
        n_points: int = 192,
        extent: float = 20.0,
        shell_radius: float = 3.0,
        shell_strength: float = -2.0,
        coefficients: Sequence[complex] | None = None,
        eigenstate_count: int = 3,
        hbar: float = 1.0,
        mass: float = 1.0,
    ) -> None:
        if n_points < 32 or extent <= 0.0 or not 0.0 < shell_radius < extent:
            raise ValueError("invalid radial delta-shell grid")
        if mass <= 0.0 or hbar <= 0.0 or eigenstate_count < 1:
            raise ValueError("invalid shell solver parameters")
        self.hbar = float(hbar)
        self.mass = float(mass)
        self.shell_radius = float(shell_radius)
        self.shell_strength = float(shell_strength)
        self.dr = extent / (n_points + 1)
        radial = self.dr * np.arange(1, n_points + 1, dtype=np.float64)
        self.coordinates = (radial,)
        self.spacing = (self.dr,)
        self.shell_index = int(np.argmin(np.abs(radial - shell_radius)))
        potential = np.zeros(n_points, dtype=np.float64)
        potential[self.shell_index] = self.shell_strength / self.dr
        self.potential = potential
        kinetic_scale = self.hbar**2 / (2.0 * self.mass * self.dr**2)
        hamiltonian = np.diag(np.full(n_points, 2.0 * kinetic_scale) + potential)
        off_diagonal = np.full(n_points - 1, -kinetic_scale)
        hamiltonian += np.diag(off_diagonal, 1) + np.diag(off_diagonal, -1)
        energies, vectors = np.linalg.eigh(hamiltonian)
        count = min(eigenstate_count, n_points)
        self.energies = energies[:count]
        self.eigenstates = vectors[:, :count].T / math.sqrt(self.dr)
        if coefficients is None:
            coefficients = (1.0, 0.35j) + (0.0,) * max(0, count - 2)
        coefficients_array = np.asarray(coefficients, dtype=np.complex128)
        if coefficients_array.size != count:
            raise ValueError("one coefficient is required per retained shell eigenstate")
        coefficient_norm = float(np.linalg.norm(coefficients_array))
        if coefficient_norm <= EPS:
            raise ValueError("shell coefficients must be nonzero")
        self.coefficients = coefficients_array / coefficient_norm
        self.time = 0.0

    def reset(self) -> None:
        self.time = 0.0

    def frame(self, dt: float = 0.0) -> WavefunctionFrame:
        if dt < 0.0:
            raise ValueError("dt must be non-negative")
        self.time += dt
        phases = np.exp(-1j * self.energies * self.time / self.hbar)
        psi = np.sum(
            (self.coefficients * phases)[:, None] * self.eigenstates,
            axis=0,
        )
        raw = _frame_from_psi(
            psi=psi,
            coordinates=self.coordinates,
            spacing=self.spacing,
            potential=self.potential,
            time=self.time,
            source="delta_function_shell",
            hbar=self.hbar,
            mass=self.mass,
            metadata={},
        )
        index = self.shell_index
        if 1 <= index < psi.size - 1:
            derivative_left = (psi[index] - psi[index - 1]) / self.dr
            derivative_right = (psi[index + 1] - psi[index]) / self.dr
            jump = derivative_right - derivative_left
            target = 2.0 * self.mass * self.shell_strength * psi[index] / self.hbar**2
            jump_residual = float(abs(jump - target) / max(abs(target), EPS))
        else:
            jump_residual = float("nan")
        exact_expectation = float(
            np.sum(np.abs(self.coefficients) ** 2 * self.energies)
        )
        return replace(
            raw,
            metadata={
                **raw.metadata,
                "shell_radius": self.shell_radius,
                "shell_strength": self.shell_strength,
                "shell_grid_radius": float(self.coordinates[0][self.shell_index]),
                "eigenenergies": tuple(float(value) for value in self.energies),
                "bound_state_count": int(np.sum(self.energies < 0.0)),
                "spectral_energy_expectation": exact_expectation,
                "derivative_jump_relative_residual": jump_residual,
                "representation": "s-wave reduced radial amplitude u(r)",
                "regularization": "single grid cell preserving integrated delta strength",
            },
        )

    def descriptor(self, dt: float) -> WavefunctionDescriptor:
        return self.frame(dt).descriptor


class DiracHydrogenFineStructureSource:
    """Exact point-Coulomb Dirac energy multiplet with evolving amplitudes."""

    def __init__(
        self,
        *,
        nuclear_charge: int = 1,
        fine_structure_constant: float = 1.0 / 137.035999084,
        mass: float = 1.0,
        hbar: float = 1.0,
        states: Sequence[tuple[int, int, float, complex]] | None = None,
        time_scale: float = 1.0,
    ) -> None:
        if nuclear_charge < 1 or fine_structure_constant <= 0.0 or mass <= 0.0:
            raise ValueError("invalid Dirac hydrogen constants")
        self.nuclear_charge = int(nuclear_charge)
        self.alpha = float(fine_structure_constant)
        self.mass = float(mass)
        self.hbar = float(hbar)
        self.c = 1.0 / self.alpha
        self.rest_energy = self.mass * self.c**2
        self.time_scale = float(time_scale)
        if self.time_scale <= 0.0:
            raise ValueError("time_scale must be positive")
        self.states = list(states or [(2, 1, 0.5, 1.0), (2, -2, 1.5, 1.0j)])
        coefficients = np.asarray([state[3] for state in self.states], dtype=np.complex128)
        coefficient_norm = float(np.linalg.norm(coefficients))
        if coefficient_norm <= EPS:
            raise ValueError("at least one relativistic level coefficient is required")
        self.initial_amplitudes = coefficients / coefficient_norm
        self.quantum_numbers = tuple((n, kappa, float(m_j)) for n, kappa, m_j, _ in self.states)
        total_energies = []
        za = self.nuclear_charge * self.alpha
        for principal, kappa, _m_j, _coefficient in self.states:
            if principal < abs(kappa) or za >= abs(kappa):
                raise ValueError("invalid or supercritical Dirac-Coulomb quantum numbers")
            gamma = math.sqrt(kappa**2 - za**2)
            denominator = principal - abs(kappa) + gamma
            total = self.rest_energy / math.sqrt(1.0 + (za / denominator) ** 2)
            total_energies.append(total)
        self.total_energies = np.asarray(total_energies, dtype=np.float64)
        self.binding_energies = self.total_energies - self.rest_energy
        self.time = 0.0

    def reset(self) -> None:
        self.time = 0.0

    def frame(self, dt: float = 0.0) -> RelativisticLevelFrame:
        if dt < 0.0:
            raise ValueError("dt must be non-negative")
        self.time += dt * self.time_scale
        # Remove the huge common rest-energy phase; all observable relative
        # phases are exactly preserved by using binding energies here.
        amplitudes = self.initial_amplitudes * np.exp(
            -1j * self.binding_energies * self.time / self.hbar
        )
        probabilities = np.abs(amplitudes) ** 2
        return RelativisticLevelFrame(
            amplitudes=amplitudes,
            probabilities=probabilities,
            quantum_numbers=self.quantum_numbers,
            total_energies=self.total_energies.copy(),
            binding_energies=self.binding_energies.copy(),
            energy_expectation=float(np.sum(probabilities * self.binding_energies)),
            fine_structure_splitting=float(np.ptp(self.binding_energies)),
            time=self.time,
            norm=float(np.sum(probabilities)),
            source="dirac_hydrogen_fine_structure",
            metadata={
                "nuclear_charge": self.nuclear_charge,
                "fine_structure_constant": self.alpha,
                "rest_energy": self.rest_energy,
                "time_scale": self.time_scale,
                "representation": "finite exact Dirac-Coulomb energy multiplet",
                "omissions": "finite nuclear size, recoil, Lamb shift, radiative QED",
            },
        )


class DiracStepKleinSource:
    """Two-component 1D Dirac packet scattering from an electrostatic step."""

    def __init__(
        self,
        *,
        n_points: int = 512,
        extent: float = 80.0,
        mass: float = 1.0,
        speed_of_light: float = 1.0,
        hbar: float = 1.0,
        step_height: float = 6.5,
        packet_center: float = -20.0,
        packet_width: float = 2.5,
        momentum: float = 4.0,
    ) -> None:
        if n_points < 64 or extent <= 0.0 or mass <= 0.0 or speed_of_light <= 0.0:
            raise ValueError("invalid Dirac grid or constants")
        if packet_width <= 0.0:
            raise ValueError("packet_width must be positive")
        self.mass = float(mass)
        self.c = float(speed_of_light)
        self.hbar = float(hbar)
        self.step_height = float(step_height)
        self.coordinates = np.linspace(-extent / 2.0, extent / 2.0, n_points, endpoint=False)
        self.dx = float(self.coordinates[1] - self.coordinates[0])
        self.potential = np.where(self.coordinates >= 0.0, self.step_height, 0.0)
        self.wave_numbers = 2.0 * math.pi * np.fft.fftfreq(n_points, d=self.dx)
        incoming_energy = math.sqrt((self.c * momentum) ** 2 + (self.mass * self.c**2) ** 2)
        upper = math.sqrt((incoming_energy + self.mass * self.c**2) / (2.0 * incoming_energy))
        lower = math.copysign(
            math.sqrt((incoming_energy - self.mass * self.c**2) / (2.0 * incoming_energy)),
            momentum,
        )
        envelope = np.exp(-((self.coordinates - packet_center) ** 2) / (4.0 * packet_width**2))
        carrier = np.exp(1j * momentum * self.coordinates / self.hbar)
        self.spinor = np.vstack((upper * envelope * carrier, lower * envelope * carrier))
        self.spinor = self._normalize_spinor(self.spinor)
        self.initial_spinor = self.spinor.copy()
        self.incoming_energy = incoming_energy
        self.time = 0.0

    def _normalize_spinor(self, spinor: Array) -> Array:
        density = np.sum(np.abs(spinor) ** 2, axis=0)
        norm = math.sqrt(max(float(np.sum(density) * self.dx), EPS))
        return spinor / norm

    def reset(self) -> None:
        self.spinor = self.initial_spinor.copy()
        self.time = 0.0

    def _kinetic_step(self, dt: float) -> None:
        momentum = self.hbar * self.wave_numbers
        d_x = self.c * momentum
        d_z = np.full_like(d_x, self.mass * self.c**2)
        energy = np.sqrt(d_x**2 + d_z**2)
        angle = energy * dt / self.hbar
        cosine = np.cos(angle)
        sine_over_energy = np.sin(angle) / np.maximum(energy, EPS)
        upper_k = np.fft.fft(self.spinor[0])
        lower_k = np.fft.fft(self.spinor[1])
        h_upper = d_z * upper_k + d_x * lower_k
        h_lower = d_x * upper_k - d_z * lower_k
        self.spinor[0] = np.fft.ifft(cosine * upper_k - 1j * sine_over_energy * h_upper)
        self.spinor[1] = np.fft.ifft(cosine * lower_k - 1j * sine_over_energy * h_lower)

    def frame(self, dt: float = 0.0) -> DiracSpinorFieldFrame:
        if dt < 0.0:
            raise ValueError("dt must be non-negative")
        if dt > 0.0:
            half_potential = np.exp(-0.5j * self.potential * dt / self.hbar)
            self.spinor *= half_potential
            self._kinetic_step(dt)
            self.spinor *= half_potential
            self.spinor = self._normalize_spinor(self.spinor)
            self.time += dt
        density = np.sum(np.abs(self.spinor) ** 2, axis=0)
        current = 2.0 * self.c * np.real(np.conj(self.spinor[0]) * self.spinor[1])
        left = float(np.sum(density[self.coordinates < 0.0]) * self.dx)
        right = float(np.sum(density[self.coordinates >= 0.0]) * self.dx)
        upper_k = np.fft.fft(self.spinor[0])
        lower_k = np.fft.fft(self.spinor[1])
        derivative_upper = np.fft.ifft(1j * self.wave_numbers * upper_k)
        derivative_lower = np.fft.ifft(1j * self.wave_numbers * lower_k)
        kinetic_density = np.real(
            np.conj(self.spinor[0]) * (-1j * self.hbar * self.c * derivative_lower)
            + np.conj(self.spinor[1]) * (-1j * self.hbar * self.c * derivative_upper)
        )
        mass_density = self.mass * self.c**2 * (
            np.abs(self.spinor[0]) ** 2 - np.abs(self.spinor[1]) ** 2
        )
        energy = float(
            np.sum(kinetic_density + mass_density + self.potential * density) * self.dx
        )
        return DiracSpinorFieldFrame(
            spinor=self.spinor.copy(),
            probability=density,
            probability_current=current,
            coordinates=self.coordinates.copy(),
            potential=self.potential.copy(),
            energy_expectation=energy,
            left_probability=left,
            right_probability=right,
            time=self.time,
            norm=float(np.sum(density) * self.dx),
            source="dirac_step_klein",
            metadata={
                "mass": self.mass,
                "speed_of_light": self.c,
                "step_height": self.step_height,
                "incoming_positive_energy": self.incoming_energy,
                "klein_zone": self.step_height > self.incoming_energy + self.mass * self.c**2,
                "representation": "1D two-component Dirac spinor; split-operator propagation",
                "probability_partition": "left/right spatial mass, not asymptotic coefficients before separation",
            },
        )


__all__ = [
    "DeltaFunctionShellSource",
    "DiracHydrogenFineStructureSource",
    "DiracStepKleinSource",
    "HeliumVariationalTwoElectronSource",
]
