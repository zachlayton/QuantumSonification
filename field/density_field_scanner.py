from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any

import numpy as np


@dataclass
class DensityFieldScannerConfig:
    particle_count: int = 16
    grid_size: int = 16
    attraction_gain: float = 1.65
    motion_gain: float = 2.25
    curl_gain: float = 1.10
    damping: float = 0.91
    max_speed: float = 1.50
    softening: float = 0.018
    seed: int = 23


@dataclass
class DensityFieldScanner:
    """Particle scanners guided by a 16x16 complex density-matrix field."""

    config: DensityFieldScannerConfig = field(default_factory=DensityFieldScannerConfig)

    def __post_init__(self) -> None:
        rng = np.random.default_rng(self.config.seed)
        count = int(self.config.particle_count)
        golden_ratio_conjugate = (math.sqrt(5.0) - 1.0) * 0.5
        positions = []
        for index in range(count):
            x = (index + 0.5) / count
            y = (0.5 + index * golden_ratio_conjugate) % 1.0
            positions.append((x, y))
        self.positions = np.asarray(positions, dtype=np.float64)
        self.positions += rng.uniform(-0.015, 0.015, size=self.positions.shape)
        self.positions %= 1.0
        self.velocities = np.zeros_like(self.positions)

        grid = int(self.config.grid_size)
        coords = (np.arange(grid, dtype=np.float64) + 0.5) / grid
        yy, xx = np.meshgrid(coords, coords, indexing="ij")
        self.cell_positions = np.column_stack([xx.reshape(-1), yy.reshape(-1)])

    @staticmethod
    def _wrap_delta(target: np.ndarray, source: np.ndarray) -> np.ndarray:
        return (target - source + 0.5) % 1.0 - 0.5

    @staticmethod
    def _normalize(values: np.ndarray) -> np.ndarray:
        peak = float(np.max(np.abs(values)))
        if peak <= 1e-12:
            return np.zeros_like(values, dtype=np.float64)
        return np.asarray(values, dtype=np.float64) / peak

    def _field_weights(
        self,
        rho: np.ndarray,
        delta_rho: np.ndarray,
    ) -> tuple[np.ndarray, np.ndarray]:
        magnitude = np.abs(rho).reshape(-1)
        motion = np.abs(delta_rho).reshape(-1)
        real_energy = np.abs(rho.real).reshape(-1)
        imag_curl = rho.imag.reshape(-1)
        delta_curl = delta_rho.imag.reshape(-1)

        attraction = (
            0.50 * self._normalize(magnitude)
            + 0.25 * self._normalize(real_energy)
            + 0.25 * self._normalize(motion)
        )
        curl = self._normalize(imag_curl + self.config.motion_gain * delta_curl)
        return attraction, curl

    def _sample_complex_field(self, rho: np.ndarray, x: float, y: float) -> complex:
        grid = self.config.grid_size
        fx = (x % 1.0) * grid - 0.5
        fy = (y % 1.0) * grid - 0.5
        x0 = int(math.floor(fx)) % grid
        y0 = int(math.floor(fy)) % grid
        x1 = (x0 + 1) % grid
        y1 = (y0 + 1) % grid
        tx = fx - math.floor(fx)
        ty = fy - math.floor(fy)

        v00 = rho[y0, x0]
        v10 = rho[y0, x1]
        v01 = rho[y1, x0]
        v11 = rho[y1, x1]
        return (
            (1.0 - tx) * (1.0 - ty) * v00
            + tx * (1.0 - ty) * v10
            + (1.0 - tx) * ty * v01
            + tx * ty * v11
        )

    def step(
        self,
        rho: np.ndarray,
        previous_rho: np.ndarray | None,
        dt: float,
    ) -> dict[str, Any]:
        rho = np.asarray(rho, dtype=np.complex128)
        if rho.shape != (self.config.grid_size, self.config.grid_size):
            raise ValueError(f"expected {self.config.grid_size}x{self.config.grid_size} rho")

        if previous_rho is None:
            delta_rho = np.zeros_like(rho)
        else:
            delta_rho = rho - np.asarray(previous_rho, dtype=np.complex128)

        attraction, curl = self._field_weights(rho, delta_rho)
        dt = max(float(dt), 1e-5)

        samples: list[complex] = []
        speeds: list[float] = []
        indices: list[int] = []
        saturation = 0.0

        for p in range(self.config.particle_count):
            pos = self.positions[p]
            delta = self._wrap_delta(self.cell_positions, pos)
            dist2 = np.sum(delta * delta, axis=1) + self.config.softening
            inv = 1.0 / dist2
            unit = delta / np.sqrt(dist2)[:, None]

            attract_force = np.sum(
                unit * (attraction * inv)[:, None],
                axis=0,
            )
            swirl_unit = np.column_stack([-unit[:, 1], unit[:, 0]])
            curl_force = np.sum(
                swirl_unit * (curl * inv)[:, None],
                axis=0,
            )

            force = (
                self.config.attraction_gain * attract_force
                + self.config.curl_gain * curl_force
            )
            force = np.tanh(force)

            self.velocities[p] = (
                self.config.damping * self.velocities[p]
                + (1.0 - self.config.damping) * force
            )

            speed = float(np.linalg.norm(self.velocities[p]))
            if speed > self.config.max_speed:
                saturation = max(
                    saturation,
                    float(np.clip(speed / self.config.max_speed, 0.0, 4.0) / 4.0),
                )
                self.velocities[p] *= self.config.max_speed / speed
                speed = self.config.max_speed

            self.positions[p] = (pos + self.velocities[p] * dt) % 1.0
            value = self._sample_complex_field(
                rho,
                float(self.positions[p, 0]),
                float(self.positions[p, 1]),
            )
            samples.append(value)
            speeds.append(float(np.linalg.norm(self.velocities[p])))
            col = int(np.floor(self.positions[p, 0] * self.config.grid_size)) % self.config.grid_size
            row = int(np.floor(self.positions[p, 1] * self.config.grid_size)) % self.config.grid_size
            indices.append(row * self.config.grid_size + col)

        sample_array = np.asarray(samples, dtype=np.complex128)
        speeds_array = np.asarray(speeds, dtype=np.float64)
        delta_abs = np.abs(delta_rho)
        coherence_mask = np.ones_like(delta_abs, dtype=bool)
        np.fill_diagonal(coherence_mask, False)

        return {
            "positions": self.positions.copy(),
            "velocities": self.velocities.copy(),
            "samples": sample_array,
            "sample_indices": indices,
            "magnitudes": np.abs(sample_array),
            "phases": np.angle(sample_array),
            "speeds": speeds_array,
            "delta_frobenius": float(np.linalg.norm(delta_rho)),
            "delta_max": float(np.max(delta_abs)),
            "delta_population": float(np.sum(np.abs(np.diag(delta_rho)))),
            "delta_coherence": float(np.sum(delta_abs[coherence_mask])),
            "mean_speed": float(np.mean(speeds_array)),
            "max_speed": float(np.max(speeds_array)),
            "speed_saturation": saturation,
            "speed_spread": float(np.std(speeds_array)),
            "magnitude_spread": float(np.std(np.abs(sample_array))),
            "phase_spread": float(np.std(np.angle(sample_array))),
        }
