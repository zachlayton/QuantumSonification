"""Reusable probability-flow primitives for the Quantum Material Workstation.

The flow layer preserves physical dynamics before they are reduced to musical
control signals.  It currently supports:

* one-dimensional complex wavefunctions,
* smooth, time-dependent region projections, and
* finite-dimensional Hamiltonian/density-matrix graphs.

No hard threshold or crossing trigger is embedded here.  A later ``qmw_skin``
module can supply evolving membership fields, permeability, phase response,
and event statistics while consuming the frames defined in this module.

Natural units (hbar = mass = 1) are the defaults, but both constants remain
explicit throughout the API.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Any, Optional

import numpy as np


Array = np.ndarray
EPS = 1.0e-12


def _trapezoid(values: Array, coordinates: Array) -> np.generic:
    trapezoid = getattr(np, "trapezoid", None)
    if trapezoid is not None:
        return trapezoid(values, x=coordinates)
    return np.trapz(values, x=coordinates)


def _validate_positive(name: str, value: float) -> float:
    value = float(value)
    if not math.isfinite(value) or value <= 0.0:
        raise ValueError(f"{name} must be finite and greater than zero.")
    return value


def _validate_time(time: float) -> float:
    time = float(time)
    if not math.isfinite(time):
        raise ValueError("time must be finite.")
    return time


def _validate_coordinates_1d(coordinates: Any) -> Array:
    result = np.asarray(coordinates, dtype=float)
    if result.ndim != 1:
        raise ValueError("coordinates must be a one-dimensional array.")
    if result.size < 3:
        raise ValueError("coordinates must contain at least three samples.")
    if not np.all(np.isfinite(result)):
        raise ValueError("coordinates must contain only finite values.")
    if not np.all(np.diff(result) > 0.0):
        raise ValueError("coordinates must be strictly increasing.")
    return np.array(result, dtype=float, copy=True)


def _validate_real_field_1d(name: str, values: Any, coordinates: Array) -> Array:
    result = np.asarray(values, dtype=float)
    if result.shape != coordinates.shape:
        raise ValueError(
            f"{name} must have shape {coordinates.shape}, received {result.shape}."
        )
    if not np.all(np.isfinite(result)):
        raise ValueError(f"{name} must contain only finite values.")
    return np.array(result, dtype=float, copy=True)


def _validate_complex_field_1d(name: str, values: Any, coordinates: Array) -> Array:
    result = np.asarray(values, dtype=np.complex128)
    if result.shape != coordinates.shape:
        raise ValueError(
            f"{name} must have shape {coordinates.shape}, received {result.shape}."
        )
    if not np.all(np.isfinite(result.real)) or not np.all(np.isfinite(result.imag)):
        raise ValueError(f"{name} must contain only finite values.")
    return np.array(result, dtype=np.complex128, copy=True)


def integrate_1d(values: Any, coordinates: Any) -> complex | float:
    """Integrate a sampled one-dimensional field on a nonuniform grid."""

    x = _validate_coordinates_1d(coordinates)
    field = np.asarray(values)
    if field.shape != x.shape:
        raise ValueError(
            f"values must have shape {x.shape}, received {field.shape}."
        )
    if not np.all(np.isfinite(field.real)) or not np.all(np.isfinite(field.imag)):
        raise ValueError("values must contain only finite values.")
    result = _trapezoid(field, x)
    result = np.real_if_close(result)
    if np.iscomplexobj(result):
        return complex(result)
    return float(result)


def normalize_wavefunction_1d(psi: Any, coordinates: Any) -> Array:
    """Return a copy of ``psi`` normalized with respect to ``coordinates``."""

    x = _validate_coordinates_1d(coordinates)
    state = _validate_complex_field_1d("psi", psi, x)
    norm_squared = float(np.real(_trapezoid(np.abs(state) ** 2, x)))
    if not math.isfinite(norm_squared) or norm_squared <= EPS:
        raise ValueError("psi must have nonzero finite norm.")
    return state / math.sqrt(norm_squared)


@dataclass(frozen=True)
class ContinuityDiagnostics1D:
    """Finite-difference diagnostics for ``partial_t rho + partial_x j = 0``."""

    dt: Optional[float] = None
    local_l2: Optional[float] = None
    local_linf: Optional[float] = None
    global_residual: Optional[float] = None


@dataclass(frozen=True)
class FlowFrame1D:
    """One complete one-dimensional probability-flow state."""

    time: float
    coordinates: Array
    psi: Array
    density: Array
    phase: Array
    phase_gradient: Array
    current: Array
    velocity: Array
    divergence: Array
    total_probability: float
    current_l1: float
    mean_velocity: float
    transport_energy: float
    current_model: str
    continuity_residual: Optional[Array]
    continuity: ContinuityDiagnostics1D


def build_flow_frame_1d(
    *,
    psi: Any,
    coordinates: Any,
    time: float = 0.0,
    hbar: float = 1.0,
    mass: float = 1.0,
    density_floor: float = EPS,
    normalize: bool = False,
    current_override: Optional[Any] = None,
    previous: Optional[FlowFrame1D] = None,
) -> FlowFrame1D:
    """Calculate density, phase geometry, current, velocity, and continuity.

    ``current_override`` allows gauge-coupled or otherwise specialized
    wavefunction providers to supply their physical current.  The canonical
    phase gradient is still calculated from ``psi``.
    """

    x = _validate_coordinates_1d(coordinates)
    state = _validate_complex_field_1d("psi", psi, x)
    logical_time = _validate_time(time)
    hbar = _validate_positive("hbar", hbar)
    mass = _validate_positive("mass", mass)
    density_floor = _validate_positive("density_floor", density_floor)

    if normalize:
        state = normalize_wavefunction_1d(state, x)

    density = np.abs(state) ** 2
    total_probability = float(np.real(_trapezoid(density, x)))
    if not math.isfinite(total_probability) or total_probability <= density_floor:
        raise ValueError("psi must have nonzero finite probability.")

    derivative = np.gradient(state, x, edge_order=2)
    canonical_phase_flow = np.imag(np.conj(state) * derivative)
    phase_gradient = np.divide(
        canonical_phase_flow,
        density,
        out=np.zeros_like(density),
        where=density > density_floor,
    )

    if current_override is None:
        current = (hbar / mass) * canonical_phase_flow
        current_model = "canonical"
    else:
        current = _validate_real_field_1d("current_override", current_override, x)
        current_model = "override"

    velocity = np.divide(
        current,
        density,
        out=np.zeros_like(current),
        where=density > density_floor,
    )
    divergence = np.gradient(current, x, edge_order=2)
    phase = np.unwrap(np.angle(state))

    current_l1 = float(np.real(_trapezoid(np.abs(current), x)))
    mean_velocity = float(np.real(_trapezoid(current, x))) / total_probability
    transport_energy_density = np.divide(
        0.5 * mass * current**2,
        density,
        out=np.zeros_like(density),
        where=density > density_floor,
    )
    transport_energy = float(
        np.real(_trapezoid(transport_energy_density, x))
    )

    continuity_residual: Optional[Array] = None
    continuity = ContinuityDiagnostics1D()
    if previous is not None:
        if previous.coordinates.shape != x.shape or not np.allclose(
            previous.coordinates, x, rtol=0.0, atol=1.0e-12
        ):
            raise ValueError(
                "previous frame must use the same coordinate grid; call reset() "
                "before changing grids."
            )
        dt = logical_time - previous.time
        if dt <= 0.0:
            raise ValueError("time must increase relative to the previous frame.")

        density_rate = (density - previous.density) / dt
        midpoint_current = 0.5 * (current + previous.current)
        midpoint_divergence = np.gradient(midpoint_current, x, edge_order=2)
        continuity_residual = density_rate + midpoint_divergence
        local_l2 = math.sqrt(
            max(float(np.real(_trapezoid(continuity_residual**2, x))), 0.0)
        )
        local_linf = float(np.max(np.abs(continuity_residual)))
        total_probability_rate = (
            total_probability - previous.total_probability
        ) / dt
        global_residual = float(
            total_probability_rate
            + midpoint_current[-1]
            - midpoint_current[0]
        )
        continuity = ContinuityDiagnostics1D(
            dt=dt,
            local_l2=local_l2,
            local_linf=local_linf,
            global_residual=global_residual,
        )

    return FlowFrame1D(
        time=logical_time,
        coordinates=x,
        psi=state,
        density=np.array(density, dtype=float, copy=True),
        phase=np.array(phase, dtype=float, copy=True),
        phase_gradient=np.array(phase_gradient, dtype=float, copy=True),
        current=np.array(current, dtype=float, copy=True),
        velocity=np.array(velocity, dtype=float, copy=True),
        divergence=np.array(divergence, dtype=float, copy=True),
        total_probability=total_probability,
        current_l1=current_l1,
        mean_velocity=mean_velocity,
        transport_energy=transport_energy,
        current_model=current_model,
        continuity_residual=(
            None
            if continuity_residual is None
            else np.array(continuity_residual, dtype=float, copy=True)
        ),
        continuity=continuity,
    )


class ProbabilityFlow1D:
    """Stateful wrapper that attaches continuity diagnostics across frames."""

    def __init__(
        self,
        *,
        hbar: float = 1.0,
        mass: float = 1.0,
        density_floor: float = EPS,
        normalize: bool = False,
    ) -> None:
        self.hbar = _validate_positive("hbar", hbar)
        self.mass = _validate_positive("mass", mass)
        self.density_floor = _validate_positive("density_floor", density_floor)
        self.normalize = bool(normalize)
        self._previous: Optional[FlowFrame1D] = None

    @property
    def previous(self) -> Optional[FlowFrame1D]:
        return self._previous

    def reset(self) -> None:
        self._previous = None

    def compute(
        self,
        *,
        psi: Any,
        coordinates: Any,
        time: float = 0.0,
        current_override: Optional[Any] = None,
    ) -> FlowFrame1D:
        frame = build_flow_frame_1d(
            psi=psi,
            coordinates=coordinates,
            time=time,
            hbar=self.hbar,
            mass=self.mass,
            density_floor=self.density_floor,
            normalize=self.normalize,
            current_override=current_override,
            previous=self._previous,
        )
        self._previous = frame
        return frame

    def from_wavefunction_frame(self, frame: Any) -> FlowFrame1D:
        """Adapt the existing QMW ``WavefunctionFrame`` structural contract."""

        dimension = int(getattr(frame, "dimension", 0))
        if dimension != 1:
            raise ValueError(
                "ProbabilityFlow1D requires a one-dimensional WavefunctionFrame."
            )

        coordinates = getattr(frame, "coordinates")
        if len(coordinates) != 1:
            raise ValueError("WavefunctionFrame must expose exactly one coordinate axis.")

        currents = getattr(frame, "probability_current", None)
        current_override = None
        if currents is not None:
            if len(currents) != 1:
                raise ValueError(
                    "WavefunctionFrame probability_current must have one component."
                )
            current_override = currents[0]

        return self.compute(
            psi=getattr(frame, "psi"),
            coordinates=coordinates[0],
            time=float(getattr(frame, "time")),
            current_override=current_override,
        )


@dataclass(frozen=True)
class SmoothRegionProjection1D:
    """Occupation and flux projected through a smooth region membership field."""

    population: float
    interface_flux: float
    domain_boundary_flux: float
    transport_rate: float
    membership_motion_rate: float
    total_population_rate: float


def project_smooth_region_1d(
    frame: FlowFrame1D,
    membership: Any,
    *,
    membership_rate: Optional[Any] = None,
    membership_tolerance: float = 1.0e-9,
) -> SmoothRegionProjection1D:
    """Project a flow frame into an evolving soft region.

    ``membership`` is a sampled field in [0, 1].  Its spatial gradient is the
    distributed interface or skin.  For a static field ``s(x)``,

        d/dt integral(s rho dx)
            = integral(j partial_x s dx) - [s j]_left^right.

    ``membership_rate`` adds ``integral(rho partial_t s dx)`` when the region
    itself moves or deforms.  This prepares dynamic skins without imposing a
    Boolean crossing test.
    """

    x = frame.coordinates
    membership_tolerance = _validate_positive(
        "membership_tolerance", membership_tolerance
    )
    region = _validate_real_field_1d("membership", membership, x)
    if (
        float(np.min(region)) < -membership_tolerance
        or float(np.max(region)) > 1.0 + membership_tolerance
    ):
        raise ValueError("membership values must lie in the interval [0, 1].")
    region = np.clip(region, 0.0, 1.0)

    population = float(np.real(_trapezoid(frame.density * region, x)))
    region_gradient = np.gradient(region, x, edge_order=2)
    interface_flux = float(
        np.real(_trapezoid(frame.current * region_gradient, x))
    )
    domain_boundary_flux = float(
        (region[0] * frame.current[0]) - (region[-1] * frame.current[-1])
    )
    transport_rate = interface_flux + domain_boundary_flux

    membership_motion_rate = 0.0
    if membership_rate is not None:
        region_rate = _validate_real_field_1d(
            "membership_rate", membership_rate, x
        )
        membership_motion_rate = float(
            np.real(_trapezoid(frame.density * region_rate, x))
        )

    return SmoothRegionProjection1D(
        population=population,
        interface_flux=interface_flux,
        domain_boundary_flux=domain_boundary_flux,
        transport_rate=transport_rate,
        membership_motion_rate=membership_motion_rate,
        total_population_rate=transport_rate + membership_motion_rate,
    )


def _validate_hermitian_matrix(name: str, values: Any, tolerance: float) -> Array:
    result = np.asarray(values, dtype=np.complex128)
    if result.ndim != 2 or result.shape[0] != result.shape[1]:
        raise ValueError(f"{name} must be a square matrix.")
    if not np.all(np.isfinite(result.real)) or not np.all(np.isfinite(result.imag)):
        raise ValueError(f"{name} must contain only finite values.")
    if not np.allclose(
        result, np.conj(result.T), rtol=tolerance, atol=tolerance
    ):
        raise ValueError(f"{name} must be Hermitian within tolerance.")
    return np.array(result, dtype=np.complex128, copy=True)


def graph_probability_current(
    hamiltonian: Any,
    density_matrix: Any,
    *,
    hbar: float = 1.0,
    hermitian_tolerance: float = 1.0e-9,
) -> Array:
    """Return directed current between basis states.

    ``current[i, j]`` is the probability current from basis state ``j`` into
    basis state ``i``:

        J[i <- j] = (2 / hbar) Im(H[i, j] rho[j, i]).

    For Hermitian ``H`` and ``rho`` the matrix is antisymmetric and
    ``current.sum(axis=1)`` equals the von Neumann population derivative.
    """

    hbar = _validate_positive("hbar", hbar)
    hermitian_tolerance = _validate_positive(
        "hermitian_tolerance", hermitian_tolerance
    )
    hamiltonian_array = _validate_hermitian_matrix(
        "hamiltonian", hamiltonian, hermitian_tolerance
    )
    density_array = _validate_hermitian_matrix(
        "density_matrix", density_matrix, hermitian_tolerance
    )
    if hamiltonian_array.shape != density_array.shape:
        raise ValueError("hamiltonian and density_matrix must have the same shape.")

    current = (2.0 / hbar) * np.imag(hamiltonian_array * density_array.T)
    current = 0.5 * (current - current.T)
    np.fill_diagonal(current, 0.0)
    return np.asarray(current, dtype=float)


@dataclass(frozen=True)
class GraphContinuityDiagnostics:
    dt: Optional[float] = None
    local_l2: Optional[float] = None
    local_linf: Optional[float] = None
    global_residual: Optional[float] = None


@dataclass(frozen=True)
class GraphFlowFrame:
    """Probability transport on a finite Hamiltonian graph."""

    time: float
    density_matrix: Array
    hamiltonian: Array
    populations: Array
    coherence_magnitude: Array
    coherence_phase: Array
    edge_current: Array
    net_inflow: Array
    total_probability: float
    conservation_error: float
    continuity_residual: Optional[Array]
    continuity: GraphContinuityDiagnostics


def build_graph_flow_frame(
    *,
    density_matrix: Any,
    hamiltonian: Any,
    time: float = 0.0,
    hbar: float = 1.0,
    hermitian_tolerance: float = 1.0e-9,
    previous: Optional[GraphFlowFrame] = None,
) -> GraphFlowFrame:
    """Build the density-matrix/graph counterpart of ``FlowFrame1D``."""

    logical_time = _validate_time(time)
    hbar = _validate_positive("hbar", hbar)
    hermitian_tolerance = _validate_positive(
        "hermitian_tolerance", hermitian_tolerance
    )
    hamiltonian_array = _validate_hermitian_matrix(
        "hamiltonian", hamiltonian, hermitian_tolerance
    )
    density_array = _validate_hermitian_matrix(
        "density_matrix", density_matrix, hermitian_tolerance
    )
    if hamiltonian_array.shape != density_array.shape:
        raise ValueError("hamiltonian and density_matrix must have the same shape.")

    edge_current = graph_probability_current(
        hamiltonian_array,
        density_array,
        hbar=hbar,
        hermitian_tolerance=hermitian_tolerance,
    )
    populations = np.real(np.diag(density_array))
    net_inflow = np.sum(edge_current, axis=1)
    total_probability = float(np.real(np.trace(density_array)))
    conservation_error = abs(float(np.sum(net_inflow)))

    continuity_residual: Optional[Array] = None
    continuity = GraphContinuityDiagnostics()
    if previous is not None:
        if previous.populations.shape != populations.shape:
            raise ValueError(
                "previous graph frame must have the same dimension; call reset() "
                "before changing graph size."
            )
        dt = logical_time - previous.time
        if dt <= 0.0:
            raise ValueError("time must increase relative to the previous frame.")

        observed_population_rate = (populations - previous.populations) / dt
        midpoint_inflow = 0.5 * (net_inflow + previous.net_inflow)
        continuity_residual = observed_population_rate - midpoint_inflow
        continuity = GraphContinuityDiagnostics(
            dt=dt,
            local_l2=float(np.linalg.norm(continuity_residual)),
            local_linf=float(np.max(np.abs(continuity_residual))),
            global_residual=abs(float(np.sum(observed_population_rate))),
        )

    return GraphFlowFrame(
        time=logical_time,
        density_matrix=density_array,
        hamiltonian=hamiltonian_array,
        populations=np.array(populations, dtype=float, copy=True),
        coherence_magnitude=np.array(np.abs(density_array), dtype=float, copy=True),
        coherence_phase=np.array(np.angle(density_array), dtype=float, copy=True),
        edge_current=np.array(edge_current, dtype=float, copy=True),
        net_inflow=np.array(net_inflow, dtype=float, copy=True),
        total_probability=total_probability,
        conservation_error=conservation_error,
        continuity_residual=(
            None
            if continuity_residual is None
            else np.array(continuity_residual, dtype=float, copy=True)
        ),
        continuity=continuity,
    )


class GraphProbabilityFlow:
    """Stateful density-matrix flow engine with continuity diagnostics."""

    def __init__(
        self,
        *,
        hbar: float = 1.0,
        hermitian_tolerance: float = 1.0e-9,
    ) -> None:
        self.hbar = _validate_positive("hbar", hbar)
        self.hermitian_tolerance = _validate_positive(
            "hermitian_tolerance", hermitian_tolerance
        )
        self._previous: Optional[GraphFlowFrame] = None

    @property
    def previous(self) -> Optional[GraphFlowFrame]:
        return self._previous

    def reset(self) -> None:
        self._previous = None

    def compute(
        self,
        *,
        density_matrix: Any,
        hamiltonian: Any,
        time: float = 0.0,
    ) -> GraphFlowFrame:
        frame = build_graph_flow_frame(
            density_matrix=density_matrix,
            hamiltonian=hamiltonian,
            time=time,
            hbar=self.hbar,
            hermitian_tolerance=self.hermitian_tolerance,
            previous=self._previous,
        )
        self._previous = frame
        return frame


__all__ = [
    "ContinuityDiagnostics1D",
    "FlowFrame1D",
    "GraphContinuityDiagnostics",
    "GraphFlowFrame",
    "GraphProbabilityFlow",
    "ProbabilityFlow1D",
    "SmoothRegionProjection1D",
    "build_flow_frame_1d",
    "build_graph_flow_frame",
    "graph_probability_current",
    "integrate_1d",
    "normalize_wavefunction_1d",
    "project_smooth_region_1d",
]
