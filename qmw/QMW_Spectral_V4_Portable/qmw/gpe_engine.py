"""One-dimensional Gross--Pitaevskii material-field layer for QMW.

This module evolves a complex order parameter ``psi`` under

``i hbar dpsi/dt = (-hbar^2/(2m) d2/dx2 + V(x) + g |psi|^2) psi``.

It is deliberately distinct from both the authoritative density-matrix and
the effective Lagrangian terrain.  A density matrix can be *projected* into a
spatial initial condition, but that projection is explicitly non-unique (and
does not turn a mixed density matrix into a pure state).  Geometry enters as
an externally supplied real potential.  The evolved field can then be
observed through :mod:`qmw.qmw_probability_flow`; no sound or event adapter
feeds back into this physical evolution.

The numerical integrator is a norm-preserving Strang split-step Fourier method
on a uniform periodic one-dimensional grid.  It is an intentionally bounded
first material-field primitive, not a claim of arbitrary-manifold GPE support.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
import math
from typing import Any, Callable, Sequence

import numpy as np

from .qmw_probability_flow import FlowFrame, flow_from_wavefunction_1d
from .gpe_observables import observe_gpe_field, periodic_laplacian


Array = np.ndarray
PotentialSource = float | Sequence[float] | Array | Callable[[Array], Any]
EPS = 1.0e-12


def _finite_positive(name: str, value: float, *, allow_zero: bool = False) -> float:
    value = float(value)
    if not math.isfinite(value) or (value < 0.0 if allow_zero else value <= 0.0):
        relation = "nonnegative" if allow_zero else "greater than zero"
        raise ValueError(f"{name} must be finite and {relation}.")
    return value


def _coordinates(values: Any) -> tuple[Array, float]:
    x = np.asarray(values, dtype=float)
    if x.ndim != 1 or x.size < 4 or not np.all(np.isfinite(x)):
        raise ValueError("coordinates must be a finite one-dimensional array with length >= 4.")
    differences = np.diff(x)
    if np.any(differences <= 0.0):
        raise ValueError("coordinates must be strictly increasing.")
    spacing = float(differences[0])
    if not np.allclose(differences, spacing, rtol=1.0e-9, atol=1.0e-12):
        raise ValueError("the split-step GPE engine requires a uniform coordinate grid.")
    return np.array(x, copy=True), spacing


def _integral(values: Array, coordinates: Array) -> float:
    trapezoid = getattr(np, "trapezoid", None)
    if trapezoid is not None:
        return float(trapezoid(values, coordinates))
    return float(np.trapz(values, coordinates))


def _potential(source: PotentialSource, coordinates: Array) -> Array:
    values = source(coordinates) if callable(source) else source
    array = np.asarray(values, dtype=float)
    if array.ndim == 0:
        array = np.full(coordinates.shape, float(array), dtype=float)
    if array.shape != coordinates.shape or not np.all(np.isfinite(array)):
        raise ValueError("geometry potential must be finite and match coordinates.")
    return np.array(array, copy=True)


def _density_matrix(values: Any, tolerance: float = 1.0e-9) -> Array:
    rho = np.asarray(values, dtype=np.complex128)
    if rho.ndim != 2 or rho.shape[0] != rho.shape[1] or rho.shape[0] == 0:
        raise ValueError("rho must be a nonempty square density matrix.")
    if not np.all(np.isfinite(rho)):
        raise ValueError("rho must be finite.")
    if not np.allclose(rho, rho.conj().T, atol=tolerance, rtol=tolerance):
        raise ValueError("rho must be Hermitian within tolerance.")
    trace = complex(np.trace(rho))
    if abs(trace.imag) > tolerance or abs(trace.real - 1.0) > tolerance:
        raise ValueError("rho must have unit trace within tolerance.")
    if float(np.min(np.linalg.eigvalsh(rho))) < -tolerance:
        raise ValueError("rho must be positive semidefinite within tolerance.")
    return np.array(rho, copy=True)


@dataclass(frozen=True)
class GPEConfig:
    """Physical and numerical parameters for a periodic 1-D GPE field."""

    hbar: float = 1.0
    mass: float = 1.0
    interaction_strength: float = 0.0
    max_substep: float = 1.0 / 960.0

    def __post_init__(self) -> None:
        _finite_positive("hbar", self.hbar)
        _finite_positive("mass", self.mass)
        _finite_positive("max_substep", self.max_substep)
        if not math.isfinite(float(self.interaction_strength)):
            raise ValueError("interaction_strength must be finite.")


@dataclass(frozen=True)
class DensityMatrixGPEProjection:
    """A declared, non-authoritative density-matrix-to-field initialization.

    ``psi`` is a single coherent order parameter constructed from localized
    packet modes.  Its use for a mixed ``rho`` is a visualization/initializing
    choice, not a preservation of all mixed-state information.
    """

    psi: Array
    packet_modes: Array
    populations: Array
    relative_phases: Array
    interaction_strength: float
    purity: float
    provenance: str = "density_matrix_to_gpe_initialization_adapter"


@dataclass(frozen=True)
class GPEFieldFrame:
    """A material-field observation produced by :class:`GrossPitaevskii1D`."""

    time: float
    psi: Array
    density: Array
    phase: Array
    current: Array
    external_potential: Array
    interaction_potential: Array
    effective_potential: Array
    quantum_pressure: Array
    gradient_energy_density: Array
    potential_energy_density: Array
    interaction_energy_density: Array
    energy_density: Array
    total_probability: float
    kinetic_energy: float
    external_potential_energy: float
    interaction_energy: float
    total_energy: float
    hbar: float
    mass: float
    interaction_strength: float
    boundary_condition: str = "periodic"
    provenance: str = "gross_pitaevskii_1d_material_field"


def project_density_matrix_to_gpe_1d(
    rho: Any,
    coordinates: Any,
    *,
    packet_centers: Sequence[float] | Array | None = None,
    packet_width: float | None = None,
    base_interaction_strength: float = 0.0,
    coherence_interaction_scale: float = 0.0,
) -> DensityMatrixGPEProjection:
    """Construct a documented spatial packet projection of a density matrix.

    Populations set packet amplitudes.  Relative phases are read from the
    first coherence column where available; absent coherence gives zero phase.
    The off-diagonal coherence magnitude may add to ``g`` only through the
    explicit ``coherence_interaction_scale`` argument.  Neither operation
    mutates ``rho`` or provides feedback to it.
    """

    matrix = _density_matrix(rho)
    x, dx = _coordinates(coordinates)
    if not math.isfinite(float(base_interaction_strength)) or not math.isfinite(float(coherence_interaction_scale)):
        raise ValueError("interaction parameters must be finite.")
    count = matrix.shape[0]
    extent = float(x[-1] - x[0])
    if packet_centers is None:
        centers = np.linspace(x[0] + extent / (2.0 * count), x[-1] - extent / (2.0 * count), count)
    else:
        centers = np.asarray(packet_centers, dtype=float)
        if centers.shape != (count,) or not np.all(np.isfinite(centers)):
            raise ValueError("packet_centers must be one finite value per density-matrix basis state.")
    width = extent / max(4.0 * count, 4.0) if packet_width is None else _finite_positive("packet_width", packet_width)
    modes = np.exp(-0.5 * ((x[None, :] - centers[:, None]) / width) ** 2).astype(np.complex128)
    for index in range(count):
        modes[index] /= math.sqrt(float(np.sum(np.abs(modes[index]) ** 2) * dx))
    populations = np.maximum(np.real(np.diag(matrix)), 0.0)
    phases = np.zeros(count, dtype=float)
    if count > 1:
        phases[1:] = np.angle(matrix[1:, 0])
    psi = np.sum(np.sqrt(populations)[:, None] * np.exp(1j * phases)[:, None] * modes, axis=0)
    norm = float(np.sum(np.abs(psi) ** 2) * dx)
    if norm <= EPS:
        raise ValueError("density-matrix projection produced a zero field.")
    psi /= math.sqrt(norm)
    off_diagonal = np.abs(matrix.copy())
    np.fill_diagonal(off_diagonal, 0.0)
    coherence = float(np.sum(off_diagonal) / max(count * (count - 1), 1))
    interaction = float(base_interaction_strength + coherence_interaction_scale * coherence)
    return DensityMatrixGPEProjection(
        psi=np.array(psi, copy=True), packet_modes=np.array(modes, copy=True),
        populations=np.array(populations, copy=True), relative_phases=phases,
        interaction_strength=interaction, purity=float(np.real(np.trace(matrix @ matrix))),
    )


class GrossPitaevskii1D:
    """Stateful, periodic one-dimensional nonlinear quantum material field."""

    def __init__(
        self,
        coordinates: Any,
        psi: Any,
        geometry_potential: PotentialSource = 0.0,
        *,
        config: GPEConfig | None = None,
        time: float = 0.0,
        projection: DensityMatrixGPEProjection | None = None,
    ) -> None:
        self.config = config or GPEConfig()
        self.coordinates, self._dx = _coordinates(coordinates)
        field = np.asarray(psi, dtype=np.complex128)
        if field.shape != self.coordinates.shape or not np.all(np.isfinite(field)):
            raise ValueError("psi must be finite and match coordinates.")
        if _integral(np.abs(field) ** 2, self.coordinates) <= EPS:
            raise ValueError("psi must have nonzero probability norm.")
        self._psi = np.array(field, copy=True)
        self._external_potential = _potential(geometry_potential, self.coordinates)
        self._time = float(time)
        if not math.isfinite(self._time):
            raise ValueError("time must be finite.")
        self.projection = projection
        self._wavenumber = 2.0 * np.pi * np.fft.fftfreq(self.coordinates.size, d=self._dx)

    @classmethod
    def from_density_matrix(
        cls,
        rho: Any,
        coordinates: Any,
        geometry_potential: PotentialSource = 0.0,
        *,
        config: GPEConfig | None = None,
        packet_centers: Sequence[float] | Array | None = None,
        packet_width: float | None = None,
        coherence_interaction_scale: float = 0.0,
        time: float = 0.0,
    ) -> "GrossPitaevskii1D":
        """Create a field from the explicit density-matrix initialization adapter."""

        initial_config = config or GPEConfig()
        projection = project_density_matrix_to_gpe_1d(
            rho, coordinates, packet_centers=packet_centers, packet_width=packet_width,
            base_interaction_strength=initial_config.interaction_strength,
            coherence_interaction_scale=coherence_interaction_scale,
        )
        return cls(
            coordinates, projection.psi, geometry_potential,
            config=replace(initial_config, interaction_strength=projection.interaction_strength),
            time=time, projection=projection,
        )

    @property
    def time(self) -> float:
        return self._time

    def set_geometry_potential(self, geometry_potential: PotentialSource) -> None:
        """Replace the supplied external geometry potential without changing ``psi``."""

        self._external_potential = _potential(geometry_potential, self.coordinates)

    def advance(self, dt: float) -> GPEFieldFrame:
        """Evolve by ``dt`` using bounded Strang substeps and return the new frame."""

        duration = _finite_positive("dt", dt, allow_zero=True)
        if duration == 0.0:
            return self.frame()
        substeps = max(1, int(math.ceil(duration / self.config.max_substep)))
        step = duration / substeps
        kinetic_phase = np.exp(-0.5j * self.config.hbar * self._wavenumber**2 * step / self.config.mass)
        for _ in range(substeps):
            density = np.abs(self._psi) ** 2
            self._psi *= np.exp(-0.5j * (self._external_potential + self.config.interaction_strength * density) * step / self.config.hbar)
            self._psi = np.fft.ifft(np.fft.fft(self._psi) * kinetic_phase)
            density = np.abs(self._psi) ** 2
            self._psi *= np.exp(-0.5j * (self._external_potential + self.config.interaction_strength * density) * step / self.config.hbar)
        self._time += duration
        return self.frame()

    def frame(self) -> GPEFieldFrame:
        """Observe the current nonlinear material field without evolving it."""

        psi = np.array(self._psi, copy=True)
        density = np.abs(psi) ** 2
        phase = np.angle(psi)
        observations = observe_gpe_field(
            psi, spacing=self._dx, potential=self._external_potential,
            interaction_strength=self.config.interaction_strength, hbar=self.config.hbar,
            mass=self.config.mass,
        )
        current = observations.current[0]
        root_density = np.sqrt(density)
        curvature = periodic_laplacian(root_density, spacing=self._dx)
        quantum_pressure = np.divide(
            -(self.config.hbar**2 / (2.0 * self.config.mass)) * curvature,
            root_density, out=np.zeros_like(root_density), where=root_density > EPS,
        )
        interaction_potential = self.config.interaction_strength * density
        kinetic = observations.kinetic_energy
        external = observations.external_potential_energy
        interaction = observations.interaction_energy
        return GPEFieldFrame(
            time=self._time, psi=psi, density=density, phase=phase, current=current,
            external_potential=np.array(self._external_potential, copy=True),
            interaction_potential=interaction_potential,
            effective_potential=self._external_potential + interaction_potential,
            quantum_pressure=quantum_pressure,
            gradient_energy_density=np.array(observations.gradient_energy_density, copy=True),
            potential_energy_density=np.array(observations.potential_energy_density, copy=True),
            interaction_energy_density=np.array(observations.interaction_energy_density, copy=True),
            energy_density=np.array(observations.energy_density, copy=True),
            total_probability=observations.probability, kinetic_energy=kinetic,
            external_potential_energy=external, interaction_energy=interaction,
            total_energy=kinetic + external + interaction, hbar=self.config.hbar,
            mass=self.config.mass, interaction_strength=self.config.interaction_strength,
        )

    def flow_frame(
        self,
        *,
        regions: Sequence[int] | Array | None = None,
        previous: FlowFrame | None = None,
    ) -> FlowFrame:
        """Export the field through QMW's shared quantum probability-current contract."""

        return flow_from_wavefunction_1d(
            self._psi, self.coordinates, time=self._time, hbar=self.config.hbar,
            mass=self.config.mass, regions=regions, previous=previous, periodic=True,
        )

    def field_frame(self, *, regions: Sequence[int] | Array | None = None, previous: Any = None) -> Any:
        """Return the synchronized GPE--Field Architecture v1 observation."""

        from .gpe.field_frame import observe_field_frame

        return observe_field_frame(
            self._psi, time=self._time, spacing=self._dx, coordinates=self.coordinates,
            potential=self._external_potential, interaction_strength=self.config.interaction_strength,
            hbar=self.config.hbar, mass=self.config.mass, regions=regions, previous=previous,
        )


__all__ = [
    "DensityMatrixGPEProjection", "GPEConfig", "GPEFieldFrame", "GrossPitaevskii1D",
    "project_density_matrix_to_gpe_1d",
]
