"""Physics observations and modal projections for periodic GPE fields.

These are read-only calculations over a GPE field.  Modal functions are
supplied by a geometry/eigenmode provider; this module neither creates sound
events nor assumes that the supplied modes are acoustic modes.  Its historic
2-D flow names are compatibility aliases for the one canonical implementation
in :mod:`qmw.qmw_probability_flow`; no second flow calculation lives here.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Any, Sequence

import numpy as np

from .qmw_probability_flow import (
    BoundaryFlux as GPEBoundaryFlux2D,
    FlowFrame2D as GPEFlowFrame2D,
    flow_from_wavefunction_2d,
)
from .gauge_covariant import (
    covariant_forward_difference,
    covariant_gradient_energy_density,
    covariant_probability_current,
    gauge_link_phases,
)


Array = np.ndarray
EPS = 1.0e-12


def _spacing(values: float | Sequence[float], dimensions: int) -> tuple[float, ...]:
    result = (float(values),) * dimensions if np.isscalar(values) else tuple(float(value) for value in values)
    if len(result) != dimensions or any(not math.isfinite(value) or value <= 0.0 for value in result):
        raise ValueError("spacing must contain one finite positive value per field dimension.")
    return result


def periodic_laplacian(values: Any, *, spacing: float | Sequence[float] = 1.0) -> Array:
    """Second-order wrapped-grid Laplacian for a one- or two-dimensional field."""

    field = np.asarray(values, dtype=float)
    if field.ndim not in (1, 2) or any(size < 4 for size in field.shape) or not np.all(np.isfinite(field)):
        raise ValueError("values must be a finite one- or two-dimensional field with every axis >= 4.")
    steps = _spacing(spacing, field.ndim)
    result = np.zeros_like(field)
    for axis, step in enumerate(steps):
        result += (np.roll(field, -1, axis=axis) - 2.0 * field + np.roll(field, 1, axis=axis)) / step**2
    return result


@dataclass(frozen=True)
class GPEObservables:
    """Density, phase, vector current, and Hamiltonian-energy observations."""

    density: Array
    phase: Array
    current: Array
    velocity: Array
    gradient_energy_density: Array
    potential_energy_density: Array
    interaction_energy_density: Array
    energy_density: Array
    kinetic_energy: float
    external_potential_energy: float
    interaction_energy: float
    total_energy: float
    probability: float
    current_kind: str = "quantum_probability"
    gauge_coupled: bool = False


@dataclass(frozen=True)
class GPEModalProjection:
    """Complex projection of a field into caller-supplied geometric modes."""

    amplitudes: Array
    occupations: Array
    phases: Array
    mode_norms: Array
    provenance: str = "geometry_mode_projection_of_gpe_field"


def observe_gpe_field(
    psi: Any,
    *,
    spacing: float | Sequence[float] = 1.0,
    potential: Any = 0.0,
    interaction_strength: Any = 0.0,
    hbar: float = 1.0,
    mass: float = 1.0,
    gauge_link_phase: Sequence[Any] | None = None,
) -> GPEObservables:
    """Calculate periodic finite-difference current and energy observables.

    When ``gauge_link_phase`` is supplied, its positive-axis links represent
    ``(q / hbar) integral A . dl``.  The reported link current is the lattice
    form of ``rho (hbar grad S - q A) / m``; it is gauge covariant rather than
    a phase-gradient observer that happens to see a gauge field.
    """

    field = np.asarray(psi, dtype=np.complex128)
    if field.ndim not in (1, 2) or any(size < 4 for size in field.shape) or not np.all(np.isfinite(field)):
        raise ValueError("psi must be a finite one- or two-dimensional field with every axis >= 4.")
    steps = _spacing(spacing, field.ndim)
    if not all(math.isfinite(float(value)) and float(value) > 0.0 for value in (hbar, mass)):
        raise ValueError("hbar and mass must be finite and greater than zero.")
    interaction = np.asarray(interaction_strength, dtype=float)
    if interaction.ndim == 0:
        interaction = np.full(field.shape, float(interaction), dtype=float)
    if interaction.shape != field.shape or not np.all(np.isfinite(interaction)):
        raise ValueError("interaction_strength must be finite and scalar or match psi.")
    external = np.asarray(potential, dtype=float)
    if external.ndim == 0:
        external = np.full(field.shape, float(external), dtype=float)
    if external.shape != field.shape or not np.all(np.isfinite(external)):
        raise ValueError("potential must be finite and match psi.")
    gauge_links = None if gauge_link_phase is None else gauge_link_phases(gauge_link_phase, field.shape)
    active_connection = gauge_links is not None and any(np.any(link != 0.0) for link in gauge_links)
    if not active_connection:
        derivatives = [
            (np.roll(field, -1, axis=axis) - np.roll(field, 1, axis=axis)) / (2.0 * step)
            for axis, step in enumerate(steps)
        ]
    else:
        derivatives = list(covariant_forward_difference(field, gauge_links, steps))
    density = np.abs(field) ** 2
    if not active_connection:
        current = np.stack([(hbar / mass) * np.imag(np.conj(field) * derivative) for derivative in derivatives])
    else:
        current = np.stack(covariant_probability_current(field, gauge_links, steps, hbar=hbar, mass=mass))
    # The velocity is a derived hydrodynamic observation.  The epsilon keeps
    # nodes finite without inventing a velocity there or changing evolution.
    velocity = current / (density[None, ...] + EPS)
    cell_volume = float(np.prod(steps))
    gradient_energy_density = (
        (hbar**2 / (2.0 * mass)) * sum(np.abs(derivative) ** 2 for derivative in derivatives)
        if not active_connection
        else covariant_gradient_energy_density(field, gauge_links, steps, hbar=hbar, mass=mass)
    )
    potential_energy_density = external * density
    interaction_energy_density = 0.5 * interaction * density**2
    energy_density = gradient_energy_density + potential_energy_density + interaction_energy_density
    kinetic = cell_volume * float(np.sum(gradient_energy_density))
    external_energy = cell_volume * float(np.sum(potential_energy_density))
    interaction_energy = cell_volume * float(np.sum(interaction_energy_density))
    return GPEObservables(
        density=density, phase=np.angle(field), current=current, velocity=velocity,
        gradient_energy_density=gradient_energy_density,
        potential_energy_density=potential_energy_density,
        interaction_energy_density=interaction_energy_density,
        energy_density=energy_density,
        kinetic_energy=kinetic, external_potential_energy=external_energy,
        interaction_energy=interaction_energy,
        total_energy=kinetic + external_energy + interaction_energy,
        probability=cell_volume * float(np.sum(density)),
        current_kind="gauge_covariant_probability_link_current" if active_connection else "quantum_probability",
        gauge_coupled=active_connection,
    )


def project_gpe_modes(
    psi: Any,
    modes: Any,
    *,
    spacing: float | Sequence[float] = 1.0,
) -> GPEModalProjection:
    """Return ``a_n = integral(conj(phi_n) psi)`` for supplied spatial modes."""

    field = np.asarray(psi, dtype=np.complex128)
    basis = np.asarray(modes, dtype=np.complex128)
    if field.ndim not in (1, 2) or any(size < 1 for size in field.shape) or not np.all(np.isfinite(field)):
        raise ValueError("psi must be a finite one- or two-dimensional field.")
    if basis.ndim != field.ndim + 1 or basis.shape[1:] != field.shape or basis.shape[0] < 1 or not np.all(np.isfinite(basis)):
        raise ValueError("modes must be finite with shape (mode_count, *psi.shape).")
    cell_volume = float(np.prod(_spacing(spacing, field.ndim)))
    amplitudes = cell_volume * np.sum(np.conj(basis) * field[None, ...], axis=tuple(range(1, basis.ndim)))
    norms = cell_volume * np.sum(np.abs(basis) ** 2, axis=tuple(range(1, basis.ndim)))
    return GPEModalProjection(
        amplitudes=amplitudes, occupations=np.abs(amplitudes) ** 2,
        phases=np.angle(amplitudes), mode_norms=np.real(norms),
    )


__all__ = [
    "GPEBoundaryFlux2D", "GPEFlowFrame2D", "GPEModalProjection", "GPEObservables",
    "flow_from_wavefunction_2d", "observe_gpe_field", "periodic_laplacian", "project_gpe_modes",
]
