"""Canonical Phase Collision I: one GPE field, three synchronized observers.

Every phase run evolves only the prepared GPE mean field.  Each stored
``FieldFrame`` simultaneously records local density/current, local energy,
complex Fourier modes, and geometry-defined boundary flux.  The companion
musical-domain controls are downstream observations for an eventual renderer,
not an audio claim or a feedback path.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Callable, Sequence

import numpy as np

from ..mappings.gpe_musical_domains import GPEMusicalDomains, map_gpe_musical_domains
from ..qmw_gpe import GPEConfig, GPEEngine
from .field_frame import FieldFrame
from .geometry_engine import GeometryPotential2D
from .geometry_mode_basis import GeometryModeBasis2D


Array = np.ndarray


@dataclass(frozen=True)
class PhaseCollisionIConfig:
    """Physical preparation and recording parameters for the phase sweep."""

    grid_size: int = 64
    spacing: float = 0.2
    dt: float = 0.004
    duration: float = 0.8
    interaction_strength: float = 0.5
    separation: float = 2.4
    width: float = 0.5
    incident_wavenumber: float = 1.25
    phases: tuple[float, ...] = (0.0, 0.25 * np.pi, 0.5 * np.pi, np.pi)
    potential: GeometryPotential2D | None = None
    geometry_mode_basis: GeometryModeBasis2D | None = None

    def __post_init__(self) -> None:
        if int(self.grid_size) != self.grid_size or self.grid_size < 16:
            raise ValueError("grid_size must be an integer >= 16.")
        for name in ("spacing", "dt", "duration", "separation", "width"):
            value = float(getattr(self, name))
            if not math.isfinite(value) or value <= 0.0:
                raise ValueError(f"{name} must be finite and greater than zero.")
        if not math.isfinite(float(self.interaction_strength)) or not math.isfinite(float(self.incident_wavenumber)):
            raise ValueError("interaction_strength and incident_wavenumber must be finite.")
        phase_values = tuple(float(value) for value in self.phases)
        if len(phase_values) < 2 or not all(math.isfinite(value) for value in phase_values):
            raise ValueError("phases must contain at least two finite relative phases.")
        object.__setattr__(self, "phases", phase_values)
        axis = (np.arange(int(self.grid_size)) - int(self.grid_size) / 2) * float(self.spacing)
        if self.potential is not None:
            values = np.asarray(self.potential.potential, dtype=float)
            if values.shape != (int(self.grid_size), int(self.grid_size)) or not np.all(np.isfinite(values)):
                raise ValueError("potential must be finite and match the Phase Collision I grid.")
            if not np.allclose(self.potential.x, axis) or not np.allclose(self.potential.y, axis):
                raise ValueError("geometry potential axes must match the Phase Collision I periodic grid.")
        if self.geometry_mode_basis is not None:
            if self.geometry_mode_basis.shape != (int(self.grid_size), int(self.grid_size)):
                raise ValueError("geometry_mode_basis must match the Phase Collision I grid.")
            if not np.allclose(self.geometry_mode_basis.x, axis) or not np.allclose(self.geometry_mode_basis.y, axis):
                raise ValueError("geometry_mode_basis axes must match the Phase Collision I periodic grid.")


@dataclass(frozen=True)
class PhaseCollisionITrace:
    """One literal relative-phase realization and its synchronized record."""

    phase: float
    frames: tuple[FieldFrame, ...]
    musical_domains: tuple[GPEMusicalDomains, ...]
    provenance: str = "phase_collision_i_synchronized_gpe_record"


@dataclass(frozen=True)
class PhaseCollisionISweep:
    """Comparable Phase Collision I traces with every physical parameter shared."""

    config: PhaseCollisionIConfig
    x: Array
    y: Array
    regions: Array
    traces: tuple[PhaseCollisionITrace, ...]
    provenance: str = "canonical_qmw_gpe_phase_collision_i"


def _initial_field(config: PhaseCollisionIConfig, X: Array, Y: Array, phase: float) -> Array:
    offset = 0.5 * config.separation
    # psi_A and psi_B have equal/opposite incident momentum; their supplied
    # relative phase is the only swept preparation parameter.
    first = np.exp(-((X + offset) ** 2 + Y**2) / (2.0 * config.width**2)) * np.exp(1j * config.incident_wavenumber * X)
    second = np.exp(-((X - offset) ** 2 + Y**2) / (2.0 * config.width**2)) * np.exp(-1j * config.incident_wavenumber * X)
    field = first + np.exp(1j * phase) * second
    norm = float(np.sum(np.abs(field) ** 2) * config.spacing**2)
    if norm <= 1.0e-12:
        raise ValueError("phase-collision preparation produced a zero field.")
    return field / math.sqrt(norm)


FrameObserver = Callable[[float, FieldFrame, GPEMusicalDomains], None]


def phase_collision_i(
    config: PhaseCollisionIConfig | None = None,
    *,
    on_frame: FrameObserver | None = None,
) -> PhaseCollisionISweep:
    """Run the canonical phase sweep and record each physical frame atomically."""

    settings = config or PhaseCollisionIConfig()
    axis = (np.arange(settings.grid_size) - settings.grid_size / 2) * settings.spacing
    x, y = axis, axis.copy()
    X, Y = np.meshgrid(x, y, indexing="ij")
    regions = (X >= 0.0).astype(int)
    potential = np.zeros((settings.grid_size, settings.grid_size), dtype=float) if settings.potential is None else settings.potential.potential
    steps = int(math.ceil(settings.duration / settings.dt))
    step_duration = settings.duration / steps
    traces: list[PhaseCollisionITrace] = []
    for phase in settings.phases:
        engine = GPEEngine(
            (settings.grid_size, settings.grid_size), spacing=settings.spacing,
            config=GPEConfig(interaction_strength=settings.interaction_strength, max_substep=min(step_duration, 0.001)),
        )
        engine.set_wavefunction(_initial_field(settings, X, Y, phase))
        engine.set_potential(potential)
        frames: list[FieldFrame] = [engine.field_frame(
            coordinates=(x, y), regions=regions, geometry_mode_basis=settings.geometry_mode_basis,
        )]
        domains: list[GPEMusicalDomains] = [map_gpe_musical_domains(frames[-1])]
        if on_frame is not None:
            on_frame(float(phase), frames[-1], domains[-1])
        for _ in range(steps):
            engine.step(step_duration)
            frame = engine.field_frame(
                coordinates=(x, y), regions=regions, geometry_mode_basis=settings.geometry_mode_basis,
                previous=frames[-1],
            )
            frames.append(frame)
            domains.append(map_gpe_musical_domains(frame))
            if on_frame is not None:
                on_frame(float(phase), frame, domains[-1])
        traces.append(PhaseCollisionITrace(float(phase), tuple(frames), tuple(domains)))
    return PhaseCollisionISweep(
        config=settings, x=np.array(x, copy=True), y=np.array(y, copy=True),
        regions=np.array(regions, copy=True), traces=tuple(traces),
    )


__all__ = ["FrameObserver", "PhaseCollisionIConfig", "PhaseCollisionITrace", "PhaseCollisionISweep", "phase_collision_i"]
