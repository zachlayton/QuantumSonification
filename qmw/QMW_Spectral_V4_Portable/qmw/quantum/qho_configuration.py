"""Read-only configuration-space observation for a declared QHO Fock state.

This module is the explicit bridge from a *canonical truncated harmonic-
oscillator Fock basis* to one-dimensional configuration space.  It does not
reinterpret an arbitrary qubit register as position.  A ``QuantumFrame`` is
accepted only when its generator is the declared QHO Hamiltonian (up to an
irrelevant scalar energy offset) and its source basis is explicitly declared.

For ``rho`` in the Fock basis and real oscillator eigenfunctions ``phi_n(x)``,
the observer evaluates

``n(x) = <x|rho|x>``

and

``j(x) = (hbar / mass) Im [d_x rho(x, x')]_{x'=x}``.

The configuration current is distinct from computational-basis current.  It
is only meaningful through this declared position representation.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Sequence

import numpy as np

from qmw.qho.model import OscillatorSpec
from qmw.qmw_probability_flow import FlowFrame, FluxEventState, emit_flux_events, flow_from_observed_current_1d

from .dynamics import Array, Hamiltonian, QuantumFrame, _density_matrix, _readonly


_EPS = 1.0e-10
QHO_FOCK_BASIS = "truncated_qho_fock_basis"


def _coordinates(values: object) -> Array:
    coordinates = np.asarray(values, dtype=float)
    if (
        coordinates.ndim != 1
        or coordinates.size < 5
        or not np.all(np.isfinite(coordinates))
        or np.any(np.diff(coordinates) <= 0.0)
    ):
        raise ValueError("QHO coordinates must be a finite, strictly increasing grid of length >= 5.")
    return _readonly(coordinates, dtype=float)


def _trapezoid_weights(coordinates: Array) -> Array:
    weights = np.empty_like(coordinates)
    weights[0] = 0.5 * (coordinates[1] - coordinates[0])
    weights[-1] = 0.5 * (coordinates[-1] - coordinates[-2])
    weights[1:-1] = 0.5 * (coordinates[2:] - coordinates[:-2])
    return _readonly(weights, dtype=float)


def _basis_values_and_derivatives(spec: OscillatorSpec, coordinates: Array, mass: float) -> tuple[Array, Array]:
    """Evaluate normalized Hermite functions and their analytic derivatives."""

    length = math.sqrt(spec.hbar / (mass * spec.omega))
    y = coordinates / length
    # One extra mode is needed for d(phi_{dimension - 1})/dx.
    functions = np.empty((coordinates.size, spec.dimension + 1), dtype=float)
    functions[:, 0] = np.exp(-0.5 * y * y) / (math.pi ** 0.25 * math.sqrt(length))
    functions[:, 1] = math.sqrt(2.0) * y * functions[:, 0]
    for level in range(1, spec.dimension):
        functions[:, level + 1] = (
            math.sqrt(2.0 / (level + 1)) * y * functions[:, level]
            - math.sqrt(level / (level + 1)) * functions[:, level - 1]
        )
    basis = functions[:, :spec.dimension]
    derivatives = np.empty_like(basis)
    for level in range(spec.dimension):
        lower = 0.0 if level == 0 else math.sqrt(level / 2.0) * functions[:, level - 1]
        upper = math.sqrt((level + 1) / 2.0) * functions[:, level + 1]
        derivatives[:, level] = (lower - upper) / length
    return _readonly(basis, dtype=float), _readonly(derivatives, dtype=float)


@dataclass(frozen=True)
class QHOConfigurationFrame:
    """One immutable configuration-space observation derived from QHO ``rho``.

    ``density_rate_unitary`` and ``density_rate_dissipative`` are projections
    of the authoritative split derivative.  Therefore
    ``continuity_residual = density_rate_unitary + density_rate_dissipative
    + d(j)/dx`` reports genuine non-unitary source/sink contributions rather
    than silently calling them current.
    """

    time: float
    source_frame_index: int | None
    basis_provenance: str
    coordinates: Array
    density: Array
    current: Array
    density_rate_unitary: Array
    density_rate_dissipative: Array
    continuity_residual: Array
    continuity_linf: float
    projected_probability: float
    basis_orthonormality_error: float
    flow: FlowFrame
    event_state: FluxEventState | None = None
    provenance: str = "read_only_qho_fock_configuration_projection"

    @property
    def n(self) -> Array:
        """Configuration density ``n(x)`` (read-only copy)."""

        return _readonly(self.density, dtype=float)

    @property
    def j(self) -> Array:
        """Configuration probability current ``j(x)`` (read-only copy)."""

        return _readonly(self.current, dtype=float)

    @property
    def regional_flux(self) -> Array:
        """Net inward flux for each declared configuration-space region."""

        return _readonly(self.flow.region_flux, dtype=float)

    @property
    def events(self) -> tuple[object, ...]:
        """Thresholded flow markers; these are never measurements."""

        return tuple(self.flow.crossings)


@dataclass(frozen=True)
class QHOConfigurationProjector:
    """Analytic position projector for one declared truncated QHO basis.

    The finite grid is accepted only after its quadrature resolves the chosen
    Fock basis.  This makes the configuration map auditable: finite-window
    truncation or under-sampling cannot be mistaken for a normalized spatial
    representation.
    """

    spec: OscillatorSpec
    coordinates: Array
    mass: float = 1.0
    orthonormality_tolerance: float = 2.0e-6

    def __post_init__(self) -> None:
        if not isinstance(self.spec, OscillatorSpec):
            raise TypeError("spec must be an OscillatorSpec.")
        if not math.isfinite(float(self.mass)) or self.mass <= 0.0:
            raise ValueError("mass must be finite and positive.")
        if not math.isfinite(float(self.orthonormality_tolerance)) or self.orthonormality_tolerance <= 0.0:
            raise ValueError("orthonormality_tolerance must be finite and positive.")
        coordinates = _coordinates(self.coordinates)
        weights = _trapezoid_weights(coordinates)
        basis, derivatives = _basis_values_and_derivatives(self.spec, coordinates, float(self.mass))
        overlap = basis.T @ (weights[:, None] * basis)
        error = float(np.max(np.abs(overlap - np.eye(self.spec.dimension))))
        if error > float(self.orthonormality_tolerance):
            raise ValueError(
                "coordinate grid does not resolve the declared QHO Fock basis "
                f"(orthonormality error {error:.3e})."
            )
        object.__setattr__(self, "coordinates", coordinates)
        object.__setattr__(self, "mass", float(self.mass))
        object.__setattr__(self, "orthonormality_tolerance", float(self.orthonormality_tolerance))
        object.__setattr__(self, "_weights", weights)
        object.__setattr__(self, "_basis", basis)
        object.__setattr__(self, "_derivatives", derivatives)
        object.__setattr__(self, "_basis_orthonormality_error", error)

    @classmethod
    def recommended(
        cls,
        spec: OscillatorSpec,
        *,
        mass: float = 1.0,
        points: int = 4097,
        extent: float | None = None,
        orthonormality_tolerance: float = 2.0e-6,
    ) -> "QHOConfigurationProjector":
        """Build a symmetric grid covering the outer Fock turning region.

        ``extent`` is in physical position units.  The default includes four
        oscillator lengths beyond the highest retained classical turning point.
        """

        if int(points) != points or int(points) < 5:
            raise ValueError("points must be an integer >= 5.")
        if not math.isfinite(float(mass)) or mass <= 0.0:
            raise ValueError("mass must be finite and positive.")
        length = math.sqrt(spec.hbar / (float(mass) * spec.omega))
        resolved_extent = (
            (math.sqrt(2.0 * spec.dimension - 1.0) + 4.0) * length
            if extent is None else float(extent)
        )
        if not math.isfinite(resolved_extent) or resolved_extent <= 0.0:
            raise ValueError("extent must be finite and positive.")
        return cls(
            spec=spec,
            coordinates=np.linspace(-resolved_extent, resolved_extent, int(points)),
            mass=float(mass),
            orthonormality_tolerance=orthonormality_tolerance,
        )

    @property
    def basis_orthonormality_error(self) -> float:
        return self._basis_orthonormality_error

    @property
    def basis_values(self) -> Array:
        return _readonly(self._basis, dtype=float)

    @property
    def basis_derivatives(self) -> Array:
        return _readonly(self._derivatives, dtype=float)

    def _validate_density(self, rho: object) -> Array:
        density = _density_matrix(rho)
        if density.shape != (self.spec.dimension, self.spec.dimension):
            raise ValueError("rho dimension must match the declared QHO Fock cutoff.")
        return density

    def _canonical_matrix(self) -> Array:
        energies = self.spec.hbar * self.spec.omega * (
            np.arange(self.spec.dimension, dtype=float) + 0.5
        )
        return _readonly(np.diag(energies))

    def _require_compatible_generator(self, hamiltonian: Hamiltonian) -> None:
        if hamiltonian.dimension != self.spec.dimension:
            raise ValueError("QuantumFrame dimension must match the declared QHO Fock cutoff.")
        if not math.isclose(hamiltonian.hbar, self.spec.hbar, rel_tol=0.0, abs_tol=_EPS):
            raise ValueError("QuantumFrame hbar must match the QHO projector spec.")
        canonical = self._canonical_matrix()
        difference = hamiltonian.matrix - canonical
        offset = np.trace(difference) / self.spec.dimension
        residual = difference - offset * np.eye(self.spec.dimension)
        if np.linalg.norm(residual, ord="fro") > _EPS * max(1.0, np.linalg.norm(canonical, ord="fro")):
            raise ValueError(
                "QuantumFrame Hamiltonian is not the declared canonical QHO generator; "
                "an explicit configuration projector cannot reinterpret this basis."
            )

    def _project_density_rate(self, derivative: Array) -> Array:
        values = np.einsum("xm,mn,xn->x", self._basis, derivative, self._basis, optimize=True)
        if float(np.max(np.abs(values.imag), initial=0.0)) > 5.0e-9:
            raise ValueError("a Hermitian density derivative produced a complex configuration density rate.")
        return _readonly(values.real, dtype=float)

    def _observe(
        self,
        rho: object,
        *,
        time: float,
        unitary_derivative: Array,
        dissipative_derivative: Array,
        source_frame_index: int | None,
        basis_provenance: str,
        regions: Sequence[int] | Array | None,
        previous: QHOConfigurationFrame | None,
        event_threshold: float | None,
    ) -> QHOConfigurationFrame:
        logical_time = float(time)
        if not math.isfinite(logical_time):
            raise ValueError("time must be finite.")
        state = self._validate_density(rho)
        unitary_rate = self._project_density_rate(unitary_derivative)
        dissipative_rate = self._project_density_rate(dissipative_derivative)
        density_values = np.einsum("xm,mn,xn->x", self._basis, state, self._basis, optimize=True)
        if float(np.max(np.abs(density_values.imag), initial=0.0)) > 5.0e-9:
            raise ValueError("a Hermitian density matrix produced complex configuration density.")
        density = np.maximum(density_values.real, 0.0)
        derivative_kernel = np.einsum("xm,mn,xn->x", self._derivatives, state, self._basis, optimize=True)
        current = (self.spec.hbar / self.mass) * derivative_kernel.imag
        if not np.all(np.isfinite(current)):
            raise ValueError("configuration current must be finite.")
        if previous is not None:
            if not np.array_equal(previous.coordinates, self.coordinates):
                raise ValueError("previous configuration frame must use the same projector grid.")
            if logical_time <= previous.time:
                raise ValueError("previous configuration frame must be strictly earlier.")
        previous_flow = None if previous is None else previous.flow
        flow = flow_from_observed_current_1d(
            density, None, current, self.coordinates, time=logical_time,
            hbar=self.spec.hbar, mass=self.mass, regions=regions, previous=previous_flow,
        )
        divergence = np.gradient(current, self.coordinates, edge_order=2)
        residual = _readonly(unitary_rate + dissipative_rate + divergence, dtype=float)
        event_state: FluxEventState | None = None
        if event_threshold is not None:
            threshold = float(event_threshold)
            if not math.isfinite(threshold) or threshold <= 0.0:
                raise ValueError("event_threshold must be finite and positive.")
            prior_state = FluxEventState() if previous is None or previous.event_state is None else previous.event_state
            if previous is None:
                event_state = prior_state
            else:
                flow, event_state = emit_flux_events(
                    flow, prior_state, dt=logical_time - previous.time, threshold=threshold,
                )
        return QHOConfigurationFrame(
            time=logical_time, source_frame_index=source_frame_index,
            basis_provenance=basis_provenance, coordinates=_readonly(self.coordinates, dtype=float),
            density=_readonly(density, dtype=float), current=_readonly(current, dtype=float),
            density_rate_unitary=unitary_rate, density_rate_dissipative=dissipative_rate,
            continuity_residual=residual, continuity_linf=float(np.max(np.abs(residual))),
            projected_probability=float(np.sum(density * self._weights)),
            basis_orthonormality_error=self._basis_orthonormality_error,
            flow=flow, event_state=event_state,
        )

    def observe_density(
        self,
        rho: object,
        *,
        time: float,
        regions: Sequence[int] | Array | None = None,
        previous: QHOConfigurationFrame | None = None,
        event_threshold: float | None = None,
    ) -> QHOConfigurationFrame:
        """Project a declared QHO density matrix under its canonical generator."""

        state = self._validate_density(rho)
        zero = np.zeros_like(state)
        canonical = self._canonical_matrix()
        return self._observe(
            state, time=time,
            unitary_derivative=(-1j / self.spec.hbar) * (canonical @ state - state @ canonical),
            dissipative_derivative=zero, source_frame_index=None,
            basis_provenance=QHO_FOCK_BASIS, regions=regions, previous=previous,
            event_threshold=event_threshold,
        )

    def observe_quantum_frame(
        self,
        frame: QuantumFrame,
        *,
        basis_provenance: str,
        regions: Sequence[int] | Array | None = None,
        previous: QHOConfigurationFrame | None = None,
        event_threshold: float | None = None,
    ) -> QHOConfigurationFrame:
        """Project one sealed QHO ``QuantumFrame`` into configuration space.

        ``basis_provenance`` is deliberately required: a dimensional match is
        not sufficient evidence that a register index is a Fock occupation.
        """

        if not isinstance(frame, QuantumFrame):
            raise TypeError("observe_quantum_frame requires a sealed QuantumFrame.")
        if basis_provenance != QHO_FOCK_BASIS:
            raise ValueError(
                f"basis_provenance must explicitly equal {QHO_FOCK_BASIS!r}."
            )
        self._require_compatible_generator(frame.hamiltonian)
        return self._observe(
            frame.rho, time=frame.time, unitary_derivative=frame.rho_dot_unitary,
            dissipative_derivative=frame.rho_dot_dissipative,
            source_frame_index=frame.frame_index, basis_provenance=basis_provenance,
            regions=regions, previous=previous, event_threshold=event_threshold,
        )


__all__ = [
    "QHO_FOCK_BASIS", "QHOConfigurationFrame", "QHOConfigurationProjector",
]
