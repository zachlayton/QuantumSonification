# bohmian_pilot.py
from __future__ import annotations

import numpy as np


class BohmianPilot1D:
    """
    A 1D phase-guided trajectory through a synthetic complex quantum field.

    Inputs:
        amplitudes : 16 spectral / population / eigenmode weights
        phases     : 16 phase values in radians

    Outputs:
        x, velocity, speed, curvature, phase, density, node_proximity
    """

    def __init__(
        self,
        n_modes: int = 16,
        grid_size: int = 512,
        mobility: float = 0.22,
        damping: float = 0.82,
        field_smoothing: float = 0.18,
        seed: int | None = None,
    ):
        self.n_modes = n_modes
        self.grid_size = grid_size
        self.mobility = mobility
        self.damping = damping
        self.field_smoothing = field_smoothing

        self.rng = np.random.default_rng(seed)

        # Position lives on a periodic circle: 0.0–1.0
        self.x = float(self.rng.random())
        self.velocity = 0.0

        self._last_amplitudes = np.ones(n_modes) / n_modes
        self._last_phases = np.zeros(n_modes)

        self.grid_x = np.linspace(0.0, 1.0, grid_size, endpoint=False)
        self.mode_numbers = np.arange(1, n_modes + 1, dtype=float)

    @staticmethod
    def _wrap01(value: float) -> float:
        return float(value % 1.0)

    @staticmethod
    def _circular_delta(target: float, source: float) -> float:
        """
        Signed shortest distance on a circle.
        Range approximately -0.5 to +0.5.
        """
        return ((target - source + 0.5) % 1.0) - 0.5

    def _prepare_amplitudes(self, amplitudes) -> np.ndarray:
        a = np.asarray(amplitudes, dtype=float).flatten()

        if len(a) < self.n_modes:
            a = np.pad(a, (0, self.n_modes - len(a)))
        else:
            a = a[: self.n_modes]

        a = np.nan_to_num(a, nan=0.0, posinf=0.0, neginf=0.0)
        a = np.maximum(a, 0.0)

        total = float(np.sum(a))
        if total < 1e-12:
            a = np.ones(self.n_modes) / self.n_modes
        else:
            a = a / total

        # Preserve continuity rather than radically rebuilding the field every frame.
        a = (
            self.field_smoothing * a
            + (1.0 - self.field_smoothing) * self._last_amplitudes
        )

        self._last_amplitudes = a.copy()
        return a

    def _prepare_phases(self, phases) -> np.ndarray:
        p = np.asarray(phases, dtype=float).flatten()

        if len(p) < self.n_modes:
            p = np.pad(p, (0, self.n_modes - len(p)))
        else:
            p = p[: self.n_modes]

        p = np.nan_to_num(p, nan=0.0, posinf=0.0, neginf=0.0)

        # Circular phase smoothing.
        old_complex = np.exp(1j * self._last_phases)
        new_complex = np.exp(1j * p)

        mixed = (
            (1.0 - self.field_smoothing) * old_complex
            + self.field_smoothing * new_complex
        )

        p = np.angle(mixed)
        self._last_phases = p.copy()
        return p

    def step(self, amplitudes, phases, dt: float = 0.02) -> dict:
        """
        Advance the pilot trajectory one step.

        dt should be the same approximate timing interval used by your engine.
        """
        dt = max(float(dt), 1e-5)

        amplitudes = self._prepare_amplitudes(amplitudes)
        phases = self._prepare_phases(phases)

        # psi(x) = sum a_k * exp(i * (2π kx + phase_k))
        theta = (
            2.0 * np.pi
            * self.grid_x[:, None]
            * self.mode_numbers[None, :]
            + phases[None, :]
        )

        exp_terms = np.exp(1j * theta)
        psi = exp_terms @ amplitudes

        # dψ/dx
        dpsi = exp_terms @ (
            amplitudes * (1j * 2.0 * np.pi * self.mode_numbers)
        )

        density = np.abs(psi) ** 2

        # Bohmian-style probability-current velocity:
        # v = Im(conj(psi) * dpsi/dx) / |psi|²
        raw_velocity = np.imag(np.conj(psi) * dpsi) / (density + 1e-8)

        # Avoid singular explosions near nodes.
        raw_velocity = np.tanh(raw_velocity * 0.06)

        # Find field values at current particle position.
        position_index = int(self.x * self.grid_size) % self.grid_size

        local_velocity = float(raw_velocity[position_index])
        local_density = float(density[position_index])
        local_phase = float(np.angle(psi[position_index]))

        # Normalize density relative to current field.
        density_max = float(np.max(density)) + 1e-12
        density_norm = np.clip(local_density / density_max, 0.0, 1.0)
        node_proximity = float(1.0 - density_norm)

        # Spatial curvature of the field velocity.
        dv_dx = np.gradient(raw_velocity, 1.0 / self.grid_size)
        local_curvature = float(dv_dx[position_index])

        # The trajectory has inertia, but remains field-governed.
        target_velocity = self.mobility * local_velocity

        self.velocity = (
            self.damping * self.velocity
            + (1.0 - self.damping) * target_velocity
        )

        self.x = self._wrap01(self.x + self.velocity * dt)

        return {
            "x": float(self.x),
            "velocity": float(self.velocity),
            "speed": float(abs(self.velocity)),
            "phase": local_phase,
            "density": float(density_norm),
            "node_proximity": node_proximity,
            "curvature": float(np.tanh(local_curvature * 0.03)),
            "field_velocity": local_velocity,
            "amplitudes": amplitudes.tolist(),
            "phases": phases.tolist(),
        }