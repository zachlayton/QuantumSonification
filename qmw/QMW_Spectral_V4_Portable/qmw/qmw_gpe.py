"""Dimensionless periodic Gross--Pitaevskii field engine.

``GPEEngine`` has one responsibility: evolve a complex field under a supplied
potential and scalar interaction strength.  It contains no regions, event
thresholds, OSC, GUI, or acoustic mappings.  For one-dimensional QMW flow
analysis and density-matrix initialization adapters, see the compatible
specialization :class:`qmw.gpe_engine.GrossPitaevskii1D`.

The default configuration is the dimensionless equation
``i dpsi/dt = (-1/2 laplacian + V + g |psi|^2) psi``.  The implementation is
N-dimensional for one- and two-dimensional periodic grids; bounded membrane
solvers remain a later finite-difference/finite-element concern.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Any, Sequence

import numpy as np

from .gpe_engine import (
    DensityMatrixGPEProjection,
    GPEConfig,
    GPEFieldFrame,
    GrossPitaevskii1D,
    project_density_matrix_to_gpe_1d,
)
from .gpe_observables import observe_gpe_field
from .gauge_covariant import covariant_kinetic_step, gauge_link_phases


Array = np.ndarray
EPS = 1.0e-12


def _shape(values: Sequence[int]) -> tuple[int, ...]:
    shape = tuple(int(value) for value in values)
    if len(shape) not in (1, 2) or any(value < 4 for value in shape):
        raise ValueError("grid_shape must be a one- or two-dimensional shape with every axis >= 4.")
    return shape


def _spacing(values: float | Sequence[float], dimensions: int) -> tuple[float, ...]:
    raw = (float(values),) * dimensions if np.isscalar(values) else tuple(float(value) for value in values)
    if len(raw) != dimensions or any(not math.isfinite(value) or value <= 0.0 for value in raw):
        raise ValueError("spacing must contain one finite positive value per grid axis.")
    return raw


@dataclass(frozen=True)
class GPEState:
    """A downstream observation of the material field, not a sound packet."""

    psi: Array
    density: Array
    phase: Array
    potential: Array
    nonlinear_potential: Array
    effective_potential: Array
    gradient_energy_density: Array
    potential_energy_density: Array
    interaction_energy_density: Array
    energy_density: Array
    time: float
    probability: float
    kinetic_energy: float
    external_potential_energy: float
    interaction_energy: float
    total_energy: float
    interaction_strength: float
    interaction_field: Array
    boundary_condition: str = "periodic"
    provenance: str = "dimensionless_gross_pitaevskii_material_field"
    probability_current: Array | None = None
    gauge_link_phase: tuple[Array, ...] | None = None
    current_kind: str = "quantum_probability"
    evolution_enabled: bool = True


class GPEEngine:
    """Small split-step Fourier solver for periodic 1-D or 2-D fields."""

    def __init__(
        self,
        grid_shape: Sequence[int],
        *,
        spacing: float | Sequence[float] = 1.0,
        config: GPEConfig | None = None,
        time: float = 0.0,
    ) -> None:
        self.grid_shape = _shape(grid_shape)
        self.spacing = _spacing(spacing, len(self.grid_shape))
        self.config = config or GPEConfig()
        self._cell_volume = float(np.prod(self.spacing))
        self._psi: Array | None = None
        self._potential = np.zeros(self.grid_shape, dtype=float)
        self._interaction = np.full(self.grid_shape, self.config.interaction_strength, dtype=float)
        self._gauge_link_phase: tuple[Array, ...] | None = None
        self._evolution_enabled = True
        self._time = float(time)
        if not math.isfinite(self._time):
            raise ValueError("time must be finite.")
        wavenumbers = [2.0 * np.pi * np.fft.fftfreq(size, d=step) for size, step in zip(self.grid_shape, self.spacing)]
        grids = np.meshgrid(*wavenumbers, indexing="ij")
        self._k_squared = sum(grid * grid for grid in grids)

    @property
    def time(self) -> float:
        return self._time

    @property
    def evolution_enabled(self) -> bool:
        """Whether this engine is permitted to advance its own GPE field."""

        return self._evolution_enabled

    def set_evolution_enabled(self, enabled: bool) -> GPEState:
        """Enable or disable GPE timesteps without changing any source state.

        Disabled means ``step(dt)`` returns the existing material-field
        observation at its existing simulation time.  It is deliberately not a
        projection, reset, or mutation of an upstream Hilbert source.
        """

        if not isinstance(enabled, (bool, np.bool_)):
            raise TypeError("enabled must be a boolean.")
        self._evolution_enabled = bool(enabled)
        return self.state() if self._psi is not None else self._uninitialized_state()

    def set_wavefunction(self, psi: Any) -> GPEState:
        """Set the initial field; the caller deliberately controls its norm."""

        field = np.asarray(psi, dtype=np.complex128)
        if field.shape != self.grid_shape or not np.all(np.isfinite(field)):
            raise ValueError("psi must be finite and match grid_shape.")
        if float(np.sum(np.abs(field) ** 2) * self._cell_volume) <= EPS:
            raise ValueError("psi must have nonzero probability norm.")
        self._psi = np.array(field, copy=True)
        return self.state()

    def set_potential(self, potential: Any) -> GPEState:
        """Set real geometry-derived ``V`` without evolving the field."""

        values = np.asarray(potential, dtype=float)
        if values.ndim == 0:
            values = np.full(self.grid_shape, float(values), dtype=float)
        if values.shape != self.grid_shape or not np.all(np.isfinite(values)):
            raise ValueError("potential must be finite and match grid_shape.")
        self._potential = np.array(values, copy=True)
        return self.state() if self._psi is not None else self._uninitialized_state()

    def set_interaction(self, interaction_strength: Any) -> GPEState:
        """Set scalar ``g(t)`` or a declared spatial field ``g(r, t)``.

        This is an engine control operation.  Whether a time-varying value
        represents a physical interaction protocol or an experimental mapping
        is intentionally decided by the caller.
        """

        values = np.asarray(interaction_strength, dtype=float)
        if values.ndim == 0:
            value = float(values)
            if not math.isfinite(value):
                raise ValueError("interaction_strength must be finite.")
            self._interaction = np.full(self.grid_shape, value, dtype=float)
            self.config = GPEConfig(
                hbar=self.config.hbar, mass=self.config.mass,
                interaction_strength=value, max_substep=self.config.max_substep,
            )
        else:
            if values.shape != self.grid_shape or not np.all(np.isfinite(values)):
                raise ValueError("interaction field must be finite and match grid_shape.")
            self._interaction = np.array(values, copy=True)
        return self.state() if self._psi is not None else self._uninitialized_state()

    @property
    def gauge_link_phase(self) -> tuple[Array, ...] | None:
        """Read-only positive-axis gauge links, or ``None`` for the FFT path."""

        return None if self._gauge_link_phase is None else tuple(np.array(link, copy=True) for link in self._gauge_link_phase)

    def set_gauge_link_phase(self, gauge_link_phase: Sequence[Any] | None) -> GPEState:
        """Set the dimensionless periodic gauge connection used by evolution.

        Each axis field is ``(q / hbar) integral A . dl`` on a positive grid
        link.  Passing ``None`` removes the connection and restores the
        original split-step Fourier kinetic operator exactly.
        """

        self._gauge_link_phase = (
            None if gauge_link_phase is None else gauge_link_phases(gauge_link_phase, self.grid_shape)
        )
        return self.state() if self._psi is not None else self._uninitialized_state()

    def set_gauge_field(self, gauge_field: Any | None) -> GPEState:
        """Adapt an existing continuous-field gauge observer to this grid.

        ``GaugeField1D`` provides ``link_phase``; ``GaugeField2D`` provides
        ``x_link_phase`` and ``y_link_phase``.  The engine reads those values
        into its own immutable-by-copy kinetic connection and never writes to
        the observer.
        """

        if gauge_field is None:
            return self.set_gauge_link_phase(None)
        if len(self.grid_shape) == 1 and hasattr(gauge_field, "link_phase"):
            return self.set_gauge_link_phase((gauge_field.link_phase,))
        if len(self.grid_shape) == 2 and hasattr(gauge_field, "x_link_phase") and hasattr(gauge_field, "y_link_phase"):
            return self.set_gauge_link_phase((gauge_field.x_link_phase, gauge_field.y_link_phase))
        raise TypeError("gauge_field must provide link phases compatible with this GPE grid dimension.")

    def step(self, dt: float) -> GPEState:
        """Return the evolved field after a bounded Strang split-step update."""

        if self._psi is None:
            raise RuntimeError("set_wavefunction must be called before step.")
        duration = float(dt)
        if not math.isfinite(duration) or duration < 0.0:
            raise ValueError("dt must be finite and nonnegative.")
        if duration == 0.0 or not self._evolution_enabled:
            return self.state()
        count = max(1, int(math.ceil(duration / self.config.max_substep)))
        substep = duration / count
        use_fft_kinetic = self._gauge_link_phase is None or all(np.all(link == 0.0) for link in self._gauge_link_phase)
        kinetic = (
            np.exp(-0.5j * self.config.hbar * self._k_squared * substep / self.config.mass)
            if use_fft_kinetic else None
        )
        for _ in range(count):
            nonlinear = self._interaction * np.abs(self._psi) ** 2
            self._psi *= np.exp(-0.5j * (self._potential + nonlinear) * substep / self.config.hbar)
            self._psi = (
                np.fft.ifftn(np.fft.fftn(self._psi) * kinetic)
                if use_fft_kinetic
                else covariant_kinetic_step(
                    self._psi, self._gauge_link_phase, self.spacing, substep,
                    hbar=self.config.hbar, mass=self.config.mass,
                )
            )
            nonlinear = self._interaction * np.abs(self._psi) ** 2
            self._psi *= np.exp(-0.5j * (self._potential + nonlinear) * substep / self.config.hbar)
        self._time += duration
        return self.state()

    def state(self) -> GPEState:
        if self._psi is None:
            raise RuntimeError("set_wavefunction must be called before requesting state.")
        density = np.abs(self._psi) ** 2
        nonlinear = self._interaction * density
        observations = observe_gpe_field(
            self._psi, spacing=self.spacing, potential=self._potential,
            interaction_strength=self._interaction, hbar=self.config.hbar,
            mass=self.config.mass, gauge_link_phase=self._gauge_link_phase,
        )
        return GPEState(
            psi=np.array(self._psi, copy=True), density=density, phase=np.angle(self._psi),
            potential=np.array(self._potential, copy=True), nonlinear_potential=nonlinear,
            effective_potential=self._potential + nonlinear, time=self._time,
            gradient_energy_density=np.array(observations.gradient_energy_density, copy=True),
            potential_energy_density=np.array(observations.potential_energy_density, copy=True),
            interaction_energy_density=np.array(observations.interaction_energy_density, copy=True),
            energy_density=np.array(observations.energy_density, copy=True),
            probability=observations.probability,
            kinetic_energy=observations.kinetic_energy,
            external_potential_energy=observations.external_potential_energy,
            interaction_energy=observations.interaction_energy,
            total_energy=observations.total_energy,
            interaction_strength=float(np.mean(self._interaction)),
            interaction_field=np.array(self._interaction, copy=True),
            probability_current=np.array(observations.current, copy=True),
            gauge_link_phase=self.gauge_link_phase,
            current_kind=observations.current_kind,
            evolution_enabled=self._evolution_enabled,
        )

    def field_frame(
        self,
        *,
        coordinates: Sequence[Any] | Any | None = None,
        regions: Array | Sequence[int] | None = None,
        geometry_mode_basis: Any = None,
        previous: Any = None,
    ) -> Any:
        """Return synchronized flow, energy, and Fourier observations.

        This is deliberately a read-only convenience seam around the one
        evolving GPE mean field.  It does not make the density matrix, flow,
        modal analysis, or a sound adapter part of the solver timestep.
        """

        if self._psi is None:
            raise RuntimeError("set_wavefunction must be called before requesting a field frame.")
        from .gpe.field_frame import observe_field_frame

        return observe_field_frame(
            self._psi, time=self._time, spacing=self.spacing, coordinates=coordinates,
            potential=self._potential, interaction_strength=self._interaction,
            hbar=self.config.hbar, mass=self.config.mass, regions=regions,
            geometry_mode_basis=geometry_mode_basis, previous=previous,
            gauge_link_phase=(
                None if self._gauge_link_phase is None or all(np.all(link == 0.0) for link in self._gauge_link_phase)
                else self._gauge_link_phase
            ),
        )

    def _uninitialized_state(self) -> GPEState:
        """Internal state returned after configuring potential or g before psi exists."""

        zero = np.zeros(self.grid_shape, dtype=float)
        return GPEState(
            psi=np.zeros(self.grid_shape, dtype=np.complex128), density=zero,
            phase=zero, potential=np.array(self._potential, copy=True),
            nonlinear_potential=zero, effective_potential=np.array(self._potential, copy=True),
            gradient_energy_density=zero, potential_energy_density=zero,
            interaction_energy_density=zero, energy_density=zero,
            time=self._time, probability=0.0, kinetic_energy=0.0,
            external_potential_energy=0.0, interaction_energy=0.0, total_energy=0.0,
            interaction_strength=float(np.mean(self._interaction)),
            interaction_field=np.array(self._interaction, copy=True),
            probability_current=np.zeros((len(self.grid_shape), *self.grid_shape), dtype=float),
            gauge_link_phase=self.gauge_link_phase,
            evolution_enabled=self._evolution_enabled,
        )


__all__ = [
    "DensityMatrixGPEProjection", "GPEConfig", "GPEEngine", "GPEFieldFrame", "GPEState",
    "GrossPitaevskii1D", "project_density_matrix_to_gpe_1d",
]
