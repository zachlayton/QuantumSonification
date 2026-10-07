"""Configuration contracts for the effective metric observer."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal
import warnings

import numpy as np


@dataclass(frozen=True)
class PotentialConfig:
    coupling: float = 1.0
    screening_length: float = 0.25
    remove_mean: bool = True

    def __post_init__(self) -> None:
        if not np.isfinite(self.coupling) or self.coupling < 0.0:
            raise ValueError("coupling must be nonnegative")
        if not np.isfinite(self.screening_length) or self.screening_length <= 0.0:
            raise ValueError("screening_length must be positive")


@dataclass(frozen=True)
class MetricConfig:
    # Direct dimensionless maps: sigma = spatial_strength * Phi and
    # lapse = exp(lapse_strength * Phi), each bounded before exponentiation.
    spatial_strength: float = 12.0
    lapse_strength: float = 4.0
    sigma_limit: float = 1.5
    lapse_exponent_limit: float = 1.5

    def __post_init__(self) -> None:
        if not np.isfinite(self.spatial_strength) or not np.isfinite(self.lapse_strength):
            raise ValueError("metric strengths must be finite")
        if self.sigma_limit <= 0.0:
            raise ValueError("sigma_limit must be positive")
        if self.lapse_exponent_limit <= 0.0:
            raise ValueError("lapse_exponent_limit must be positive")


@dataclass(frozen=True)
class LorentzConfig:
    topography_mode: Literal["none", "explicit_force", "geodesic", "hybrid"] = "explicit_force"
    circulation_enabled: bool = False
    slope_gain: float = 1.0
    circulation_gain: float = 1.0
    geodesic_gain: float = 1.0
    allow_hybrid: bool = False

    def __post_init__(self) -> None:
        if self.topography_mode not in ("none", "explicit_force", "geodesic", "hybrid"):
            raise ValueError("unknown topography_mode")
        if self.topography_mode == "hybrid" and not self.allow_hybrid:
            raise ValueError(
                "hybrid topography can double-count Phi; set allow_hybrid=True "
                "only for an explicitly labeled exploratory mapping"
            )
        if self.topography_mode == "hybrid" and self.allow_hybrid:
            warnings.warn(
                "hybrid topography applies both -q*grad(Phi) and metric geodesic "
                "acceleration; this exploratory mode may double-count topography",
                RuntimeWarning,
                stacklevel=2,
            )
        gains = (self.slope_gain, self.circulation_gain, self.geodesic_gain)
        if not all(np.isfinite(value) for value in gains):
            raise ValueError("force gains must be finite")


@dataclass(frozen=True)
class ResonatorConfig:
    sample_rate: float = 48_000.0
    frequency_floor_hz: float = 30.0
    frequency_scale_hz: float = 80.0
    default_damping_ratio: float = 0.015
    retune_time_seconds: float = 0.02

    def __post_init__(self) -> None:
        if not np.isfinite(self.sample_rate) or self.sample_rate <= 0.0:
            raise ValueError("sample_rate must be positive")
        if (not np.isfinite(self.frequency_floor_hz)
                or not np.isfinite(self.frequency_scale_hz)
                or self.frequency_floor_hz < 0.0 or self.frequency_scale_hz <= 0.0):
            raise ValueError("frequency mapping must be nonnegative with positive scale")
        if self.default_damping_ratio < 0.0:
            raise ValueError("default_damping_ratio must be nonnegative")
        if self.retune_time_seconds < 0.0:
            raise ValueError("retune_time_seconds must be nonnegative")


@dataclass(frozen=True)
class QuantumMetricConfig:
    grid_size: tuple[int, int] = (32, 32)
    extent: tuple[float, float, float, float] = (-1.0, 1.0, -1.0, 1.0)
    quantum_dimension: int = 16
    mode_count: int = 24
    potential: PotentialConfig = field(default_factory=PotentialConfig)
    metric: MetricConfig = field(default_factory=MetricConfig)
    lorentz: LorentzConfig = field(default_factory=LorentzConfig)
    resonator: ResonatorConfig = field(default_factory=ResonatorConfig)
    metric_update_hz: float = 30.0
    mode_update_hz: float = 5.0

    def __post_init__(self) -> None:
        ny, nx = self.grid_size
        if ny < 4 or nx < 4:
            raise ValueError("grid_size entries must be at least four")
        if self.quantum_dimension <= 0 or self.mode_count <= 0:
            raise ValueError("quantum_dimension and mode_count must be positive")
        if self.mode_count >= ny * nx:
            raise ValueError("mode_count must be smaller than the grid point count")
        if self.metric_update_hz <= 0.0 or self.mode_update_hz <= 0.0:
            raise ValueError("update rates must be positive")
