"""Headless, deterministic GPE experiments used to validate field dynamics.

These experiments expose field and flow diagnostics only.  They make no GUI,
OSC, or acoustic claims; those layers may consume their results later.
"""

from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np

from ..qmw_gpe import GPEConfig, GPEEngine, GPEState
from ..qmw_probability_flow import FlowFrame2D
from .geometry_engine import GeometryPotentialEngine2D
from .field_frame import FieldFrame, observe_field_frame


Array = np.ndarray


@dataclass(frozen=True)
class CanonicalExperimentConfig:
    """Shared periodic grid and integration parameters for the four studies."""

    grid_size: int = 64
    spacing: float = 0.25
    dt: float = 0.002

    def __post_init__(self) -> None:
        if int(self.grid_size) != self.grid_size or self.grid_size < 16:
            raise ValueError("grid_size must be an integer >= 16.")
        if not all(math.isfinite(float(value)) and float(value) > 0.0 for value in (self.spacing, self.dt)):
            raise ValueError("spacing and dt must be finite and greater than zero.")


@dataclass(frozen=True)
class GPEExperimentResult:
    """Initial/final material fields and scalar diagnostics for one experiment."""

    name: str
    x: Array
    y: Array
    initial: GPEState
    final: GPEState
    diagnostics: dict[str, float]
    provenance: str = "headless_canonical_gpe_experiment"


@dataclass(frozen=True)
class PhaseCollisionSweep:
    """Final fields and 2-D regional flow for a controlled relative-phase sweep."""

    phases: Array
    results: tuple[GPEExperimentResult, ...]
    final_flows: tuple[FlowFrame2D, ...]
    provenance: str = "headless_two_packet_phase_collision_experiment"
    final_field_frames: tuple[FieldFrame, ...] = ()


def _grid(config: CanonicalExperimentConfig) -> tuple[Array, Array, Array, Array]:
    axis = (np.arange(config.grid_size) - config.grid_size / 2) * config.spacing
    return axis, axis.copy(), *np.meshgrid(axis, axis, indexing="ij")


def _normalise(psi: Array, spacing: float) -> Array:
    norm = float(np.sum(np.abs(psi) ** 2) * spacing**2)
    if norm <= 1.0e-12:
        raise ValueError("initial packet must have nonzero norm.")
    return psi / math.sqrt(norm)


def _evolve(
    psi: Array,
    potential: Array | float,
    interaction: float,
    duration: float,
    config: CanonicalExperimentConfig,
) -> tuple[GPEState, GPEState]:
    if not math.isfinite(duration) or duration <= 0.0:
        raise ValueError("duration must be finite and greater than zero.")
    engine = GPEEngine(
        psi.shape, spacing=config.spacing,
        config=GPEConfig(interaction_strength=interaction, max_substep=min(config.dt, 0.001)),
    )
    engine.set_potential(potential)
    initial = engine.set_wavefunction(_normalise(psi, config.spacing))
    steps = int(math.ceil(duration / config.dt))
    final = initial
    for _ in range(steps):
        final = engine.step(duration / steps)
    return initial, final


def _moments(density: Array, X: Array, Y: Array, spacing: float) -> tuple[float, float, float]:
    weight = density * spacing**2
    x_mean = float(np.sum(X * weight))
    y_mean = float(np.sum(Y * weight))
    radial_second_moment = float(np.sum((X**2 + Y**2) * weight))
    return x_mean, y_mean, radial_second_moment


def free_packet_experiment(
    *,
    config: CanonicalExperimentConfig | None = None,
    duration: float = 0.2,
) -> GPEExperimentResult:
    """Free Gaussian packet: verifies dispersive kinetic spreading at ``V=g=0``."""

    settings = config or CanonicalExperimentConfig()
    x, y, X, Y = _grid(settings)
    psi = np.exp(-((X + 2.0) ** 2 + Y**2) / (2.0 * 0.7**2)) * np.exp(0.5j * X)
    initial, final = _evolve(psi, 0.0, 0.0, duration, settings)
    initial_x, initial_y, initial_radius = _moments(initial.density, X, Y, settings.spacing)
    final_x, final_y, final_radius = _moments(final.density, X, Y, settings.spacing)
    initial_variance = initial_radius - initial_x**2 - initial_y**2
    final_variance = final_radius - final_x**2 - final_y**2
    return GPEExperimentResult(
        "free_packet", x, y, initial, final,
        {
            "initial_spatial_variance": initial_variance,
            "final_spatial_variance": final_variance,
            "initial_radial_second_moment": initial_radius,
            "final_radial_second_moment": final_radius,
        },
    )


def harmonic_trap_experiment(
    *,
    config: CanonicalExperimentConfig | None = None,
    omega: float = 0.35,
    duration: float = 0.5,
) -> GPEExperimentResult:
    """Displaced packet in ``V = 1/2 omega^2 r^2``: verifies stable geometry response."""

    settings = config or CanonicalExperimentConfig()
    x, y, X, Y = _grid(settings)
    geometry = GeometryPotentialEngine2D(x, y)
    potential = geometry.harmonic_bowl(omega).potential
    psi = np.exp(-((X + 2.0) ** 2 + Y**2) / (2.0 * 0.7**2))
    initial, final = _evolve(psi, potential, 0.0, duration, settings)
    x_initial, _, _ = _moments(initial.density, X, Y, settings.spacing)
    x_final, _, _ = _moments(final.density, X, Y, settings.spacing)
    return GPEExperimentResult(
        "harmonic_trap", x, y, initial, final,
        {"omega": float(omega), "initial_x_centroid": x_initial, "final_x_centroid": x_final},
    )


def repulsive_field_experiment(
    *,
    config: CanonicalExperimentConfig | None = None,
    interaction_strength: float = 5.0,
    duration: float = 0.2,
) -> tuple[GPEExperimentResult, GPEExperimentResult]:
    """Matched linear/repulsive packet pair for observing density-pressure spreading."""

    settings = config or CanonicalExperimentConfig()
    x, y, X, Y = _grid(settings)
    psi = np.exp(-(X**2 + Y**2) / (2.0 * 0.6**2))
    linear_initial, linear_final = _evolve(psi, 0.0, 0.0, duration, settings)
    repulsive_initial, repulsive_final = _evolve(psi, 0.0, interaction_strength, duration, settings)
    _, _, linear_radius = _moments(linear_final.density, X, Y, settings.spacing)
    _, _, repulsive_radius = _moments(repulsive_final.density, X, Y, settings.spacing)
    linear = GPEExperimentResult(
        "linear_packet_reference", x, y, linear_initial, linear_final,
        {"final_peak_density": float(np.max(linear_final.density)), "final_radial_second_moment": linear_radius},
    )
    repulsive = GPEExperimentResult(
        "repulsive_nonlinear_packet", x, y, repulsive_initial, repulsive_final,
        {"interaction_strength": float(interaction_strength), "final_peak_density": float(np.max(repulsive_final.density)), "final_radial_second_moment": repulsive_radius},
    )
    return linear, repulsive


def phase_collision_experiment(
    *,
    config: CanonicalExperimentConfig | None = None,
    phases: Array | None = None,
    duration: float = 1.0,
) -> PhaseCollisionSweep:
    """Evolve two packets while sweeping their literal relative field phase."""

    settings = config or CanonicalExperimentConfig()
    phase_values = np.asarray([0.0, 0.5 * np.pi, np.pi] if phases is None else phases, dtype=float)
    if phase_values.ndim != 1 or phase_values.size < 2 or not np.all(np.isfinite(phase_values)):
        raise ValueError("phases must be a finite one-dimensional array with at least two values.")
    x, y, X, Y = _grid(settings)
    first_packet = np.exp(-((X + 1.2) ** 2 + Y**2) / (2.0 * 0.5**2))
    second_packet = np.exp(-((X - 1.2) ** 2 + Y**2) / (2.0 * 0.5**2))
    regions = (X >= 0.0).astype(int)
    results: list[GPEExperimentResult] = []
    flows: list[FlowFrame2D] = []
    field_frames: list[FieldFrame] = []
    for phase in phase_values:
        initial, final = _evolve(first_packet + np.exp(1j * phase) * second_packet, 0.0, 0.0, duration, settings)
        field_frame = observe_field_frame(
            final.psi, time=duration, spacing=settings.spacing, coordinates=(x, y), regions=regions,
        )
        flow = field_frame.flow
        if not isinstance(flow, FlowFrame2D):  # A dimensionality guard, not a coercion.
            raise RuntimeError("two-dimensional phase collision produced an incompatible flow frame.")
        results.append(GPEExperimentResult(
            "two_packet_phase_collision", x, y, initial, final,
            {"relative_phase": float(phase), "final_peak_density": float(np.max(final.density)), "left_to_right_region_flux": float(flow.region_flux[1])},
        ))
        flows.append(flow)
        field_frames.append(field_frame)
    return PhaseCollisionSweep(phase_values, tuple(results), tuple(flows), final_field_frames=tuple(field_frames))


__all__ = [
    "CanonicalExperimentConfig", "GPEExperimentResult", "PhaseCollisionSweep",
    "free_packet_experiment", "harmonic_trap_experiment", "phase_collision_experiment",
    "repulsive_field_experiment",
]
