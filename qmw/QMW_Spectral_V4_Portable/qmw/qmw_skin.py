"""Evolving one-dimensional encounter fields for QMW probability flow.

This module deliberately *observes* a flow frame rather than changing the
quantum state that produced it.  A skin is a finite-width relational field:
it describes where an encounter can occur, its phase sensitivity, and a
classical response suitable for a later sound or control adapter.  It is not a
measurement postulate, a collapse mechanism, or a DSP model.

``qmw_flow`` remains the authoritative source of density and current.  This
module accepts any frame-like object exposing ``coordinates``, ``density``,
``phase``, ``current``, and ``time``; it therefore remains usable while the
flow core lives in its existing engine package.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Any, Optional, Protocol

import numpy as np


Array = np.ndarray
EPS = 1.0e-12


class FlowFrame1DLike(Protocol):
    """Minimal read-only flow contract consumed by a skin."""

    time: float
    coordinates: Array
    density: Array
    phase: Array
    current: Array


def _coordinates(values: Any) -> Array:
    x = np.asarray(values, dtype=float)
    if x.ndim != 1 or x.size < 3 or not np.all(np.isfinite(x)):
        raise ValueError("coordinates must be a finite one-dimensional field of length >= 3.")
    if not np.all(np.diff(x) > 0.0):
        raise ValueError("coordinates must be strictly increasing.")
    return np.array(x, copy=True)


def _field(name: str, values: Any, x: Array, *, lower: float | None = None,
           upper: float | None = None) -> Array:
    result = np.asarray(values, dtype=float)
    if result.shape != x.shape or not np.all(np.isfinite(result)):
        raise ValueError(f"{name} must be finite and have shape {x.shape}.")
    if lower is not None and np.any(result < lower):
        raise ValueError(f"{name} must be at least {lower}.")
    if upper is not None and np.any(result > upper):
        raise ValueError(f"{name} must be at most {upper}.")
    return np.array(result, copy=True)


def _positive(name: str, value: float) -> float:
    value = float(value)
    if not math.isfinite(value) or value <= 0.0:
        raise ValueError(f"{name} must be finite and greater than zero.")
    return value


def _integrate(values: Array, x: Array) -> float:
    trapezoid = getattr(np, "trapezoid", None)
    if trapezoid is None:
        # NumPy < 2 exposed ``trapz``; access it lazily because NumPy 2.4
        # removed that compatibility name.
        trapezoid = getattr(np, "trapz", None)
    if trapezoid is None:
        raise RuntimeError("NumPy must provide trapezoid or trapz integration.")
    return float(trapezoid(values, x=x))


@dataclass(frozen=True)
class SkinField1D:
    """Static material fields of a finite-width skin.

    ``membership`` is a smooth field from exterior (0) to interior (1).
    ``presence`` identifies the material extent of the skin itself.  The two
    are separate so a broad, partially permeable skin need not be confused
    with a Boolean boundary.
    """

    coordinates: Array
    membership: Array
    presence: Array
    permeability: Array
    phase: Optional[Array] = None

    def __post_init__(self) -> None:
        x = _coordinates(self.coordinates)
        membership = _field("membership", self.membership, x, lower=0.0, upper=1.0)
        presence = _field("presence", self.presence, x, lower=0.0)
        permeability = _field("permeability", self.permeability, x, lower=0.0, upper=1.0)
        phase = None if self.phase is None else _field("phase", self.phase, x)
        object.__setattr__(self, "coordinates", x)
        object.__setattr__(self, "membership", membership)
        object.__setattr__(self, "presence", presence)
        object.__setattr__(self, "permeability", permeability)
        object.__setattr__(self, "phase", phase)

    @classmethod
    def gaussian(cls, coordinates: Any, *, center: float, width: float,
                 permeability: float = 1.0, phase: float | None = None) -> "SkinField1D":
        """Create a normalized-shape, finite-width skin centered at ``center``."""

        x = _coordinates(coordinates)
        width = _positive("width", width)
        permeability = float(permeability)
        if not math.isfinite(permeability) or not 0.0 <= permeability <= 1.0:
            raise ValueError("permeability must be between zero and one.")
        presence = np.exp(-0.5 * ((x - float(center)) / width) ** 2)
        membership = 0.5 * (1.0 + np.tanh((x - float(center)) / width))
        phase_field = None if phase is None else np.full_like(x, float(phase))
        return cls(x, membership, presence, np.full_like(x, permeability), phase_field)


@dataclass(frozen=True)
class SkinMechanics1D:
    """Classical displacement state of the skin; never fed back implicitly."""

    displacement: float = 0.0
    velocity: float = 0.0


@dataclass(frozen=True)
class SkinEncounter1D:
    """An observational encounter between a flow frame and a skin field."""

    time: float
    co_presence: float
    directional_flux: float
    incident_flux: float
    transmitted_flux: float
    reflected_flux: float
    absorbed_flux: float
    phase_alignment: float
    hazard_rate: float
    force: float
    relative_phase: Optional[Array]


def evaluate_skin_encounter(flow: FlowFrame1DLike, skin: SkinField1D,
                            *, sensitivity: float = 1.0) -> SkinEncounter1D:
    """Evaluate an encounter without modifying either flow or skin.

    ``hazard_rate`` is an explicitly phenomenological event-intensity adapter:
    it is useful for a later stochastic scheduler, but it is not asserted to
    be a quantum measurement probability.  The quantum quantities reported
    here are density/current-derived observables.
    """

    sensitivity = _positive("sensitivity", sensitivity)
    x = _coordinates(flow.coordinates)
    if not np.array_equal(x, skin.coordinates):
        raise ValueError("flow and skin coordinates must be identical.")
    density = _field("flow.density", flow.density, x, lower=0.0)
    current = _field("flow.current", flow.current, x)
    flow_phase = _field("flow.phase", flow.phase, x)

    co_presence = _integrate(density * skin.presence, x)
    membership_gradient = np.gradient(skin.membership, x, edge_order=2)
    directional_flux = _integrate(current * membership_gradient, x)
    incident_flux = _integrate(np.abs(current) * skin.presence, x)

    relative_phase: Optional[Array] = None
    if skin.phase is None:
        phase_alignment = 1.0
        phase_weight = np.ones_like(x)
    else:
        relative_phase = np.angle(np.exp(1j * (flow_phase - skin.phase)))
        phase_weight = 0.5 * (1.0 + np.cos(relative_phase))
        material_weight = skin.presence * np.abs(current)
        total_weight = _integrate(material_weight, x)
        phase_alignment = 1.0 if total_weight <= EPS else _integrate(material_weight * phase_weight, x) / total_weight

    transmitted_flux = _integrate(np.abs(current) * skin.presence * skin.permeability, x)
    residual_flux = max(0.0, incident_flux - transmitted_flux)
    # The skin has no quantum absorption dynamics yet; residual contact is
    # reported as reflection rather than silently destroying probability.
    reflected_flux = residual_flux
    absorbed_flux = 0.0
    hazard_rate = sensitivity * _integrate(np.abs(current) * skin.presence * phase_weight, x)
    force = directional_flux
    return SkinEncounter1D(float(flow.time), co_presence, directional_flux, incident_flux,
                           transmitted_flux, reflected_flux, absorbed_flux, phase_alignment,
                           hazard_rate, force, relative_phase)


def advance_skin_mechanics(state: SkinMechanics1D, encounter: SkinEncounter1D, *, dt: float,
                           mass: float = 1.0, damping: float = 0.0,
                           stiffness: float = 1.0) -> SkinMechanics1D:
    """Advance a damped classical skin response driven by encounter force."""

    dt = _positive("dt", dt)
    mass = _positive("mass", mass)
    damping = float(damping)
    stiffness = float(stiffness)
    if not math.isfinite(damping) or damping < 0.0 or not math.isfinite(stiffness) or stiffness < 0.0:
        raise ValueError("damping and stiffness must be finite and nonnegative.")
    acceleration = (encounter.force - damping * state.velocity - stiffness * state.displacement) / mass
    velocity = state.velocity + dt * acceleration
    return SkinMechanics1D(state.displacement + dt * velocity, velocity)


__all__ = [
    "FlowFrame1DLike", "SkinEncounter1D", "SkinField1D", "SkinMechanics1D",
    "advance_skin_mechanics", "evaluate_skin_encounter",
]
