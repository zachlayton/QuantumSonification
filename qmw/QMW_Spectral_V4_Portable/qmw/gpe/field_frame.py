"""Synchronized read-only GPE field frames.

``FieldFrame`` packages local flow, energy, and Fourier observations of one
already-evolved GPE mean field.  It neither evolves ``psi`` nor feeds a
sonification result back into the GPE or an authoritative density matrix.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Any, Sequence

import numpy as np

from ..gpe_observables import GPEObservables, observe_gpe_field
from ..qmw_probability_flow import (
    FlowFrame, FlowFrame2D, flow_from_observed_current_1d, flow_from_observed_current_2d,
    flow_from_wavefunction_1d, flow_from_wavefunction_2d,
)
from .basis_engine import FourierBasis, FourierModeFrame
from .geometry_mode_basis import GeometryModeBasis2D, GeometryModeFrame


Array = np.ndarray
Flow = FlowFrame | FlowFrame2D


def _coordinates(
    shape: tuple[int, ...], spacing: tuple[float, ...], values: Sequence[Any] | Any | None
) -> tuple[Array, ...]:
    if values is None:
        return tuple(np.arange(size, dtype=float) * step for size, step in zip(shape, spacing))
    if len(shape) == 1 and np.asarray(values).shape == (shape[0],):
        raw = (values,)
    else:
        raw = tuple(values)
    if len(raw) != len(shape):
        raise ValueError("coordinates must contain one axis per field dimension.")
    result = tuple(np.asarray(axis, dtype=float) for axis in raw)
    for axis, size, step in zip(result, shape, spacing):
        if axis.shape != (size,) or not np.all(np.isfinite(axis)) or not np.all(np.diff(axis) > 0.0):
            raise ValueError("coordinates must be finite, strictly increasing axes matching psi.")
        if not np.allclose(np.diff(axis), step, rtol=1.0e-9, atol=1.0e-12):
            raise ValueError("FieldFrame periodic coordinates must agree with spacing.")
    return tuple(np.array(axis, copy=True) for axis in result)


@dataclass(frozen=True)
class FieldFrame:
    """One synchronized set of physical observations of a GPE mean field."""

    time: float
    psi: Array
    density: Array
    phase: Array
    current: Array
    velocity: Array
    gradient_energy: Array
    potential_energy: Array
    interaction_energy: Array
    energy_density: Array
    norm: float
    total_energy: float
    mode_coeffs: Array
    mode_power: Array
    mode_phase: Array
    mode_phase_velocity: Array
    mode_wavenumbers: tuple[Array, ...]
    modal_probability: float
    parseval_error: float
    reconstruction_error: float
    region_population: Array
    region_flux: Array
    flow: Flow
    basis: FourierModeFrame
    observables: GPEObservables
    geometry_modes: GeometryModeFrame | None = None
    provenance: str = "synchronized_read_only_gpe_mean_field_frame"


def observe_field_frame(
    psi: Any,
    *,
    time: float,
    spacing: float | Sequence[float] = 1.0,
    coordinates: Sequence[Any] | Any | None = None,
    potential: Any = 0.0,
    interaction_strength: Any = 0.0,
    hbar: float = 1.0,
    mass: float = 1.0,
    gauge_link_phase: Sequence[Any] | None = None,
    regions: Array | Sequence[int] | None = None,
    geometry_mode_basis: GeometryModeBasis2D | None = None,
    previous: FieldFrame | None = None,
) -> FieldFrame:
    """Observe a single field atomically through flow, energy, and Fourier views."""

    field = np.asarray(psi, dtype=np.complex128)
    if field.ndim not in (1, 2) or any(size < 4 for size in field.shape) or not np.all(np.isfinite(field)):
        raise ValueError("psi must be a finite one- or two-dimensional field with every axis >= 4.")
    logical_time = float(time)
    if not math.isfinite(logical_time):
        raise ValueError("time must be finite.")
    steps = (float(spacing),) * field.ndim if np.isscalar(spacing) else tuple(float(value) for value in spacing)
    if len(steps) != field.ndim or any(not math.isfinite(step) or step <= 0.0 for step in steps):
        raise ValueError("spacing must contain one finite positive value per field dimension.")
    axes = _coordinates(field.shape, steps, coordinates)
    observations = observe_gpe_field(
        field, spacing=steps, potential=potential, interaction_strength=interaction_strength,
        hbar=hbar, mass=mass, gauge_link_phase=gauge_link_phase,
    )
    basis = FourierBasis(field.shape, spacing=steps)
    previous_basis = None if previous is None else previous.basis
    modes = basis.project(field, time=logical_time, previous=previous_basis)
    previous_geometry_modes = None if previous is None else previous.geometry_modes
    if geometry_mode_basis is not None and field.ndim != 2:
        raise ValueError("geometry_mode_basis is only defined for two-dimensional GPE fields.")
    geometry_modes = None if geometry_mode_basis is None else geometry_mode_basis.project(
        field, time=logical_time, previous=previous_geometry_modes,
    )
    if field.ndim == 1:
        previous_flow = None if previous is None else previous.flow
        if previous_flow is not None and not isinstance(previous_flow, FlowFrame):
            raise ValueError("previous FieldFrame has incompatible flow dimensionality.")
        flow = (
            flow_from_wavefunction_1d(
                field, axes[0], time=logical_time, hbar=hbar, mass=mass, regions=regions,
                previous=previous_flow, periodic=True,
            )
            if gauge_link_phase is None else flow_from_observed_current_1d(
                observations.density, observations.phase, observations.current[0], axes[0], time=logical_time,
                hbar=hbar, mass=mass, regions=regions, previous=previous_flow, periodic=True,
                current_on_positive_links=True,
            )
        )
    else:
        previous_flow = None if previous is None else previous.flow
        if previous_flow is not None and not isinstance(previous_flow, FlowFrame2D):
            raise ValueError("previous FieldFrame has incompatible flow dimensionality.")
        flow = (
            flow_from_wavefunction_2d(
                field, axes[0], axes[1], time=logical_time, hbar=hbar, mass=mass,
                regions=None if regions is None else np.asarray(regions, dtype=int), previous=previous_flow,
            )
            if gauge_link_phase is None else flow_from_observed_current_2d(
                observations.density, observations.phase, observations.current, axes[0], axes[1], time=logical_time,
                mass=mass, regions=None if regions is None else np.asarray(regions, dtype=int), previous=previous_flow,
                current_on_positive_links=True,
            )
        )
    return FieldFrame(
        time=logical_time, psi=np.array(field, copy=True), density=np.array(observations.density, copy=True),
        phase=np.array(observations.phase, copy=True), current=np.array(observations.current, copy=True),
        velocity=np.array(observations.velocity, copy=True),
        gradient_energy=np.array(observations.gradient_energy_density, copy=True),
        potential_energy=np.array(observations.potential_energy_density, copy=True),
        interaction_energy=np.array(observations.interaction_energy_density, copy=True),
        energy_density=np.array(observations.energy_density, copy=True), norm=observations.probability,
        total_energy=observations.total_energy, mode_coeffs=np.array(modes.coefficients, copy=True),
        mode_power=np.array(modes.power, copy=True), mode_phase=np.array(modes.phase, copy=True),
        mode_phase_velocity=np.array(modes.phase_velocity, copy=True),
        mode_wavenumbers=tuple(np.array(axis, copy=True) for axis in modes.wavenumbers),
        modal_probability=modes.modal_probability, parseval_error=modes.parseval_error,
        reconstruction_error=modes.reconstruction_error,
        region_population=np.array(flow.region_population, copy=True), region_flux=np.array(flow.region_flux, copy=True),
        flow=flow, basis=modes, observables=observations,
        geometry_modes=geometry_modes,
    )


__all__ = ["FieldFrame", "observe_field_frame"]
