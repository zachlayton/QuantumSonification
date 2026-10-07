"""Gauge-covariant transport observers for QMW flow providers.

The connections in this module are *observer data*: attaching one to a
``FieldFrame`` does not change a GPE solver, a density-matrix evolution, or a
resonator's fixed modal frequencies.  They let downstream geometry and audio
adapters inspect gauge-invariant relative phase, transport, and holonomy.

For an oriented link ``i -> j`` we use ``U_ij = exp(-i A_ij)`` and
``delta_ij = arg(psi_j) - arg(psi_i) - A_ij``.  Under the local convention
``psi_i -> exp(i chi_i) psi_i``, the link phase transforms as
``A_ij -> A_ij + chi_j - chi_i``.  Consequently ``delta_ij``, link currents,
and closed-loop holonomies are invariant.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Literal, Mapping, Sequence

import numpy as np


Array = np.ndarray
EPS = 1.0e-12


def _wrapped(values: object) -> Array:
    value = np.asarray(values, dtype=float)
    if not np.all(np.isfinite(value)):
        raise ValueError("gauge phases must be finite.")
    return np.angle(np.exp(1j * value))


def _complex_field(psi: object, shape: tuple[int, ...]) -> Array:
    field = np.asarray(psi, dtype=np.complex128)
    if field.shape != shape or not np.all(np.isfinite(field)):
        raise ValueError(f"psi must be finite with shape {shape}.")
    return field


def _local_phase(values: object, shape: tuple[int, ...]) -> Array:
    phase = np.asarray(values, dtype=float)
    if phase.shape != shape or not np.all(np.isfinite(phase)):
        raise ValueError(f"local_phase must be finite with shape {shape}.")
    return phase


def _positive(name: str, value: float) -> float:
    result = float(value)
    if not math.isfinite(result) or result <= 0.0:
        raise ValueError(f"{name} must be finite and greater than zero.")
    return result


@dataclass(frozen=True)
class GaugeFieldFrame:
    """Read-only covariant transport sampled from a periodic field.

    ``link_phase[axis]`` is the connection integral from each grid sample to
    its positive neighbour. ``covariant_phase_difference`` and
    ``link_current`` have the same per-axis layout.  For 1-D,
    ``holonomy`` is the loop integral; for 2-D, it is the plaquette flux.
    """

    dimension: int
    link_phase: tuple[Array, ...]
    covariant_phase_difference: tuple[Array, ...]
    link_current: tuple[Array, ...]
    holonomy: Array
    current_rms: float
    current_max_abs: float
    provenance: str = "read_only_u1_gauge_covariant_transport"


@dataclass(frozen=True)
class GaugeField1D:
    """Periodic sampling of a continuous U(1) connection in one dimension.

    ``link_phase[i]`` approximates the line integral of ``A dx`` from sample
    ``i`` to ``i + 1`` (with the final link wrapping to zero).
    """

    link_phase: Array

    def __post_init__(self) -> None:
        phase = _wrapped(self.link_phase)
        if phase.ndim != 1 or phase.size < 4:
            raise ValueError("GaugeField1D requires at least four link phases.")
        object.__setattr__(self, "link_phase", np.array(phase, copy=True))

    @property
    def shape(self) -> tuple[int, ...]:
        return self.link_phase.shape

    def transformed(self, local_phase: object) -> "GaugeField1D":
        chi = _local_phase(local_phase, self.shape)
        return GaugeField1D(self.link_phase + np.roll(chi, -1) - chi)

    def observe(self, psi: object, *, spacing: float, hbar: float = 1.0, mass: float = 1.0) -> GaugeFieldFrame:
        dx, hbar, mass = _positive("spacing", spacing), _positive("hbar", hbar), _positive("mass", mass)
        field = _complex_field(psi, self.shape)
        transported_next = np.exp(-1j * self.link_phase) * np.roll(field, -1)
        relative = np.angle(np.exp(1j * (np.angle(np.roll(field, -1)) - np.angle(field) - self.link_phase)))
        current = (hbar / (mass * dx)) * np.imag(np.conj(field) * transported_next)
        holonomy = np.asarray([float(np.angle(np.exp(1j * np.sum(self.link_phase))))])
        return GaugeFieldFrame(
            dimension=1, link_phase=(np.array(self.link_phase, copy=True),),
            covariant_phase_difference=(relative,), link_current=(current,), holonomy=holonomy,
            current_rms=float(np.sqrt(np.mean(current**2))), current_max_abs=float(np.max(np.abs(current))),
        )


@dataclass(frozen=True)
class GaugeField2D:
    """Periodic sampling of a continuous U(1) connection on a 2-D field.

    ``x_link_phase`` and ``y_link_phase`` are positive-axis link integrals.
    The reported holonomy is the oriented plaquette flux
    ``A_x + A_y(x+) - A_x(y+) - A_y``.
    """

    x_link_phase: Array
    y_link_phase: Array

    def __post_init__(self) -> None:
        x_phase, y_phase = _wrapped(self.x_link_phase), _wrapped(self.y_link_phase)
        if x_phase.ndim != 2 or x_phase.shape != y_phase.shape or min(x_phase.shape) < 4:
            raise ValueError("GaugeField2D link phases must be matching arrays with axes >= 4.")
        object.__setattr__(self, "x_link_phase", np.array(x_phase, copy=True))
        object.__setattr__(self, "y_link_phase", np.array(y_phase, copy=True))

    @property
    def shape(self) -> tuple[int, int]:
        return self.x_link_phase.shape

    def transformed(self, local_phase: object) -> "GaugeField2D":
        chi = _local_phase(local_phase, self.shape)
        return GaugeField2D(
            self.x_link_phase + np.roll(chi, -1, axis=0) - chi,
            self.y_link_phase + np.roll(chi, -1, axis=1) - chi,
        )

    def observe(self, psi: object, *, spacing: Sequence[float], hbar: float = 1.0, mass: float = 1.0) -> GaugeFieldFrame:
        if len(spacing) != 2:
            raise ValueError("2-D gauge observation requires two spacings.")
        dx, dy = (_positive("spacing", spacing[0]), _positive("spacing", spacing[1]))
        hbar, mass = _positive("hbar", hbar), _positive("mass", mass)
        field = _complex_field(psi, self.shape)
        x_next, y_next = np.roll(field, -1, axis=0), np.roll(field, -1, axis=1)
        x_transport = np.exp(-1j * self.x_link_phase) * x_next
        y_transport = np.exp(-1j * self.y_link_phase) * y_next
        x_relative = np.angle(np.exp(1j * (np.angle(x_next) - np.angle(field) - self.x_link_phase)))
        y_relative = np.angle(np.exp(1j * (np.angle(y_next) - np.angle(field) - self.y_link_phase)))
        x_current = (hbar / (mass * dx)) * np.imag(np.conj(field) * x_transport)
        y_current = (hbar / (mass * dy)) * np.imag(np.conj(field) * y_transport)
        holonomy = np.angle(np.exp(1j * (
            self.x_link_phase + np.roll(self.y_link_phase, -1, axis=0)
            - np.roll(self.x_link_phase, -1, axis=1) - self.y_link_phase
        )))
        combined = np.stack((x_current, y_current))
        return GaugeFieldFrame(
            dimension=2,
            link_phase=(np.array(self.x_link_phase, copy=True), np.array(self.y_link_phase, copy=True)),
            covariant_phase_difference=(x_relative, y_relative), link_current=(x_current, y_current),
            holonomy=holonomy, current_rms=float(np.sqrt(np.mean(combined**2))),
            current_max_abs=float(np.max(np.abs(combined))),
        )


@dataclass(frozen=True)
class GaugeGraphConnection:
    """Oriented U(1) links on a finite graph, stored in canonical ``i < j`` order.

    This immutable descriptor does not mutate a density matrix by itself.
    Observer routes may inspect it read-only; ``GaugeDynamicsEngine`` may
    explicitly consume it as part of an authoritative gauged Hamiltonian.
    Methods which sound imperative (``set_phase`` and ``transform``) return a
    new connection, preserving the object as a stable frame descriptor.
    """

    node_count: int
    edge_indices: Array
    link_phase: Array
    coupling: float | Sequence[float] | Array = 1.0

    def __post_init__(self) -> None:
        if int(self.node_count) != self.node_count or self.node_count < 2:
            raise ValueError("node_count must be an integer of at least two.")
        edges = np.asarray(self.edge_indices, dtype=int)
        phase = _wrapped(self.link_phase)
        if edges.ndim != 2 or edges.shape[1:] != (2,) or edges.shape[0] != phase.size:
            raise ValueError("edge_indices must have shape (edge_count, 2) matching link_phase.")
        if np.any(edges < 0) or np.any(edges >= self.node_count) or np.any(edges[:, 0] >= edges[:, 1]):
            raise ValueError("graph edges must use canonical distinct node pairs i < j.")
        if len({tuple(edge) for edge in edges.tolist()}) != len(edges):
            raise ValueError("graph edges must be unique.")
        coupling = np.broadcast_to(np.asarray(self.coupling, dtype=float), phase.shape)
        if not np.all(np.isfinite(coupling)) or np.any(coupling < 0.0):
            raise ValueError("coupling must be finite and nonnegative per graph edge.")
        object.__setattr__(self, "node_count", int(self.node_count))
        object.__setattr__(self, "edge_indices", np.array(edges, copy=True))
        object.__setattr__(self, "link_phase", np.array(phase, copy=True))
        object.__setattr__(self, "coupling", np.array(coupling, dtype=float, copy=True))

    @property
    def connection_phases(self) -> Array:
        """Connection phase ``A`` for each canonical edge, as a copy."""
        return np.array(self.link_phase, copy=True)

    @property
    def link_variable(self) -> Array:
        """Parallel-transport link variables ``U = exp(-i A)``."""
        return np.exp(-1j * self.link_phase)

    @property
    def phase_matrix(self) -> Array:
        """Antisymmetric ``A[j, k]`` matrix, zero away from declared edges."""
        result = np.zeros((self.node_count, self.node_count), dtype=float)
        source, destination = self.edge_indices.T
        result[source, destination] = self.link_phase
        result[destination, source] = -self.link_phase
        return result

    def transformed(self, local_phase: object) -> "GaugeGraphConnection":
        chi = _local_phase(local_phase, (self.node_count,))
        source, destination = self.edge_indices[:, 0], self.edge_indices[:, 1]
        return GaugeGraphConnection(
            self.node_count,
            self.edge_indices,
            self.link_phase + chi[destination] - chi[source],
            self.coupling,
        )

    def transform(self, local_phase: object) -> "GaugeGraphConnection":
        """Return this connection in the locally transformed phase convention."""
        return self.transformed(local_phase)

    def set_phase(self, source: int, destination: int, value: float) -> "GaugeGraphConnection":
        """Return a replacement with the oriented edge phase set to ``value``."""
        if not math.isfinite(float(value)):
            raise ValueError("connection phase must be finite.")
        index, orientation = self._edge_index(int(source), int(destination))
        phase = np.array(self.link_phase, copy=True)
        phase[index] = orientation * float(value)
        return GaugeGraphConnection(self.node_count, self.edge_indices, phase, self.coupling)

    def covariant_phase(self, local_phase: object) -> Array:
        """Return ``phi_k - phi_j - A_jk`` on each canonical edge ``j < k``."""
        phase = _local_phase(local_phase, (self.node_count,))
        source, destination = self.edge_indices.T
        return np.angle(np.exp(1j * (phase[destination] - phase[source] - self.link_phase)))

    def _edge_index(self, source: int, destination: int) -> tuple[int, int]:
        for index, (left, right) in enumerate(self.edge_indices):
            if (left, right) == (source, destination):
                return index, 1
            if (left, right) == (destination, source):
                return index, -1
        raise ValueError(f"cycle references absent edge {source}->{destination}.")

    def holonomy(self, cycle: Sequence[int]) -> float:
        nodes = tuple(int(node) for node in cycle)
        if len(nodes) < 3 or any(node < 0 or node >= self.node_count for node in nodes):
            raise ValueError("a cycle needs at least three valid nodes.")
        total = 0.0
        for source, destination in zip(nodes, nodes[1:] + nodes[:1]):
            index, orientation = self._edge_index(source, destination)
            total += orientation * self.link_phase[index]
        return float(np.angle(np.exp(1j * total)))

    def hamiltonian(self, coupling: float | Sequence[float] | Array | None = None) -> Array:
        values = self.coupling if coupling is None else np.broadcast_to(np.asarray(coupling, dtype=float), self.link_phase.shape)
        if not np.all(np.isfinite(values)) or np.any(values < 0.0):
            raise ValueError("coupling must be finite and nonnegative per graph edge.")
        hamiltonian = np.zeros((self.node_count, self.node_count), dtype=np.complex128)
        for (source, destination), phase, weight in zip(self.edge_indices, self.link_phase, values):
            hamiltonian[source, destination] = -weight * np.exp(-1j * phase)
            hamiltonian[destination, source] = np.conj(hamiltonian[source, destination])
        return hamiltonian

    def wavefunction_link_current(self, psi: object, *, coupling: float | Sequence[float] | Array | None = None, hbar: float = 1.0) -> Array:
        hbar = _positive("hbar", hbar)
        field = _complex_field(psi, (self.node_count,))
        values = self.coupling if coupling is None else np.broadcast_to(np.asarray(coupling, dtype=float), self.link_phase.shape)
        if not np.all(np.isfinite(values)) or np.any(values < 0.0):
            raise ValueError("coupling must be finite and nonnegative per graph edge.")
        source, destination = self.edge_indices[:, 0], self.edge_indices[:, 1]
        transported = np.exp(-1j * self.link_phase) * field[destination]
        return (2.0 * values / hbar) * np.imag(np.conj(field[source]) * transported)


@dataclass(frozen=True)
class GaugeFlowFrame:
    """One gauge-invariant transport observation on a finite resonant graph.

    ``edge_currents[n]`` is positive from ``edge_indices[n, 0]`` to
    ``edge_indices[n, 1]``.  ``node_inflow`` and ``node_outflow`` are signed
    net quantities, so ``node_inflow == -node_outflow``.  ``node_phases`` and
    ``covariant_phase_edges`` are deliberately ``None`` for a general mixed
    density matrix: neither is determined by ``rho`` alone.
    """

    time: float
    current_source: Literal["wavefunction_graph", "density_matrix_graph"]
    populations: Array
    node_phases: Array | None
    connection_phases: Array
    edge_indices: Array
    covariant_phase_edges: Array | None
    edge_currents: Array
    node_inflow: Array
    node_outflow: Array
    incoming_strength: Array
    outgoing_strength: Array
    population_rate: Array
    continuity_residual: Array
    holonomies: Mapping[str, float]
    current_derivative: Array | None = None
    density_matrix: Array | None = None
    hamiltonian: Array | None = None
    flow_frame: object | None = None
    provenance: str = "read_only_u1_gauge_covariant_graph_transport"

    @property
    def link_current(self) -> Array:
        """Compatibility spelling for edge currents in canonical-edge order."""
        return self.edge_currents

    @property
    def density_flow(self) -> object | None:
        """Optional legacy density-graph observer retained by the convenience wrapper."""
        return self.flow_frame


# The earlier public spelling remains valid while the unified frame becomes
# the canonical graph-gauge observation contract.
GaugeGraphTransportFrame = GaugeFlowFrame
# Short public spelling for the connection layer described by the instrument
# architecture.  The graph-specific name remains for source compatibility.
GaugeConnection = GaugeGraphConnection


def _edge_current_matrix(connection: GaugeGraphConnection, edge_currents: Array) -> Array:
    result = np.zeros((connection.node_count, connection.node_count), dtype=float)
    source, destination = connection.edge_indices.T
    result[source, destination] = edge_currents
    result[destination, source] = -edge_currents
    return result


def _holonomies(connection: GaugeGraphConnection, cycles: Mapping[str, Sequence[int]] | None) -> Mapping[str, float]:
    return {} if cycles is None else {str(name): connection.holonomy(cycle) for name, cycle in cycles.items()}


def _frame(
    *,
    time: float,
    current_source: Literal["wavefunction_graph", "density_matrix_graph"],
    connection: GaugeGraphConnection,
    edge_currents: Array,
    populations: Array,
    population_rate: Array,
    node_phases: Array | None,
    cycles: Mapping[str, Sequence[int]] | None,
    previous: GaugeFlowFrame | None,
    density_matrix: Array | None = None,
    hamiltonian: Array | None = None,
    flow_frame: object | None = None,
) -> GaugeFlowFrame:
    edge_currents = np.asarray(edge_currents, dtype=float)
    matrix = _edge_current_matrix(connection, edge_currents)
    node_inflow = np.sum(matrix, axis=0)
    node_outflow = np.sum(matrix, axis=1)
    if not np.allclose(node_inflow, -node_outflow, rtol=0.0, atol=1.0e-12):
        raise RuntimeError("gauge graph current must be antisymmetric.")
    current_derivative: Array | None = None
    if previous is not None:
        if not np.array_equal(previous.edge_indices, connection.edge_indices):
            raise ValueError("previous gauge frame must use the same graph edges.")
        dt = float(time) - previous.time
        if dt <= 0.0:
            raise ValueError("time must increase relative to the previous gauge frame.")
        current_derivative = (edge_currents - previous.edge_currents) / dt
    covariant = None if node_phases is None else connection.covariant_phase(node_phases)
    return GaugeFlowFrame(
        time=float(time), current_source=current_source,
        populations=np.array(populations, dtype=float, copy=True),
        node_phases=None if node_phases is None else np.array(node_phases, dtype=float, copy=True),
        connection_phases=connection.connection_phases,
        edge_indices=np.array(connection.edge_indices, dtype=int, copy=True),
        covariant_phase_edges=None if covariant is None else np.array(covariant, dtype=float, copy=True),
        edge_currents=np.array(edge_currents, dtype=float, copy=True),
        node_inflow=np.array(node_inflow, dtype=float, copy=True),
        node_outflow=np.array(node_outflow, dtype=float, copy=True),
        incoming_strength=np.sum(np.maximum(matrix, 0.0), axis=0),
        outgoing_strength=np.sum(np.maximum(matrix, 0.0), axis=1),
        population_rate=np.array(population_rate, dtype=float, copy=True),
        continuity_residual=np.array(population_rate - node_inflow, dtype=float, copy=True),
        holonomies=_holonomies(connection, cycles),
        current_derivative=None if current_derivative is None else np.array(current_derivative, dtype=float, copy=True),
        density_matrix=None if density_matrix is None else np.array(density_matrix, dtype=np.complex128, copy=True),
        hamiltonian=None if hamiltonian is None else np.array(hamiltonian, dtype=np.complex128, copy=True),
        flow_frame=flow_frame,
    )


def gauge_flow_from_wavefunction(
    psi: object,
    connection: GaugeGraphConnection,
    *,
    time: float = 0.0,
    hbar: float = 1.0,
    cycles: Mapping[str, Sequence[int]] | None = None,
    previous: GaugeFlowFrame | None = None,
) -> GaugeFlowFrame:
    """Observe ``psi + A -> J`` without evolving the supplied wavefunction."""
    if not math.isfinite(float(time)):
        raise ValueError("time must be finite.")
    field = _complex_field(psi, (connection.node_count,))
    hamiltonian = connection.hamiltonian()
    density = np.outer(field, field.conj())
    from qmw.quantum.hilbert_current import von_neumann_population_rate

    return _frame(
        time=float(time), current_source="wavefunction_graph", connection=connection,
        edge_currents=connection.wavefunction_link_current(field, hbar=hbar),
        populations=np.abs(field) ** 2,
        population_rate=von_neumann_population_rate(density, hamiltonian, hbar=hbar),
        node_phases=np.angle(field), cycles=cycles, previous=previous,
        density_matrix=density, hamiltonian=hamiltonian,
    )


def gauge_flow_from_density_matrix(
    rho: object,
    hamiltonian: object,
    connection: GaugeGraphConnection,
    *,
    time: float = 0.0,
    hbar: float = 1.0,
    cycles: Mapping[str, Sequence[int]] | None = None,
    previous: GaugeFlowFrame | None = None,
    flow_frame: object | None = None,
) -> GaugeFlowFrame:
    """Observe ``rho + H -> J`` on the declared connection topology.

    The connection supplies topology and holonomies.  The Hamiltonian remains
    the authoritative generator of density-matrix current and must not carry
    any nonzero coupling outside that topology.
    """
    if not math.isfinite(float(time)):
        raise ValueError("time must be finite.")
    from qmw.quantum.hilbert_current import current_matrix, hermitian_matrix, von_neumann_population_rate

    density = hermitian_matrix("rho", rho)
    generator = hermitian_matrix("hamiltonian", hamiltonian)
    if density.shape != (connection.node_count, connection.node_count) or generator.shape != density.shape:
        raise ValueError("rho, hamiltonian, and connection must share a graph dimension.")
    allowed = np.zeros_like(generator, dtype=bool)
    source, destination = connection.edge_indices.T
    allowed[source, destination] = True
    allowed[destination, source] = True
    diagonal = np.eye(connection.node_count, dtype=bool)
    if np.any(np.abs(generator[~(allowed | diagonal)]) > EPS):
        raise ValueError("hamiltonian has couplings outside the declared GaugeGraphConnection.")
    directed = current_matrix(density, generator, hbar=hbar)
    edge_currents = directed[source, destination]
    return _frame(
        time=float(time), current_source="density_matrix_graph", connection=connection,
        edge_currents=edge_currents, populations=np.real(np.diag(density)),
        population_rate=von_neumann_population_rate(density, generator, hbar=hbar),
        node_phases=None, cycles=cycles, previous=previous,
        density_matrix=density, hamiltonian=generator, flow_frame=flow_frame,
    )


def gauge_density_matrix_transport(
    rho: object,
    connection: GaugeGraphConnection,
    *,
    time: float,
    coupling: float | Sequence[float] | Array | None = None,
    hbar: float = 1.0,
    cycles: Mapping[str, Sequence[int]] | None = None,
    regions: Sequence[int] | Array | None = None,
    previous: object | None = None,
):
    """Convenience density route using the connection's hopping Hamiltonian.

    ``GaugeFlowFrame`` is the canonical return value.  The contained optional
    ``density_flow`` remains available for existing regional graph observers.
    """
    from qmw.qmw_probability_flow import flow_from_density_matrix_graph

    configured = connection if coupling is None else GaugeGraphConnection(
        connection.node_count, connection.edge_indices, connection.link_phase, coupling,
    )
    hamiltonian = configured.hamiltonian()
    prior = None if previous is None else previous.density_flow
    flow = flow_from_density_matrix_graph(
        rho, hamiltonian, time=time, hbar=hbar, regions=regions, previous=prior,
    )
    return gauge_flow_from_density_matrix(
        rho,
        hamiltonian,
        configured,
        time=time,
        hbar=hbar,
        cycles=cycles,
        previous=previous,
        flow_frame=flow,
    )


def triangle_gauge_connection(
    flux: float = 0.0,
    *,
    coupling: float | Sequence[float] | Array = 1.0,
) -> GaugeGraphConnection:
    """Build the smallest closed resonant topology with declared loop flux.

    The flux is evenly distributed over the three canonical links, so the
    triangle holonomy is ``flux`` modulo ``2 pi``.
    """
    if not math.isfinite(float(flux)):
        raise ValueError("flux must be finite.")
    return GaugeGraphConnection(
        3,
        np.array(((0, 1), (0, 2), (1, 2))),
        np.array((float(flux) / 3.0, -float(flux) / 3.0, float(flux) / 3.0)),
        coupling,
    )


def observe_triangle_gauge_flow(
    psi: object,
    *,
    flux: float = 0.0,
    coupling: float | Sequence[float] | Array = 1.0,
    time: float = 0.0,
    hbar: float = 1.0,
    previous: GaugeFlowFrame | None = None,
) -> GaugeFlowFrame:
    """Observe a three-resonator circulation study; it does not render sound."""
    return gauge_flow_from_wavefunction(
        psi,
        triangle_gauge_connection(flux, coupling=coupling),
        time=time,
        hbar=hbar,
        cycles={"triangle": (0, 1, 2)},
        previous=previous,
    )


def observe_gauge_field(
    psi: object,
    connection: GaugeField1D | GaugeField2D,
    *,
    spacing: float | Sequence[float],
    hbar: float = 1.0,
    mass: float = 1.0,
) -> GaugeFieldFrame:
    """Observe a matching field connection without changing its evolution."""
    if isinstance(connection, GaugeField1D):
        if not np.isscalar(spacing):
            raise ValueError("GaugeField1D requires scalar spacing.")
        return connection.observe(psi, spacing=float(spacing), hbar=hbar, mass=mass)
    if isinstance(connection, GaugeField2D):
        if np.isscalar(spacing):
            raise ValueError("GaugeField2D requires two spacings.")
        return connection.observe(psi, spacing=spacing, hbar=hbar, mass=mass)
    raise TypeError("connection must be GaugeField1D or GaugeField2D.")


__all__ = [
    "GaugeConnection", "GaugeField1D", "GaugeField2D", "GaugeFieldFrame", "GaugeGraphConnection",
    "GaugeFlowFrame", "GaugeGraphTransportFrame", "gauge_density_matrix_transport",
    "gauge_flow_from_density_matrix", "gauge_flow_from_wavefunction",
    "observe_gauge_field", "observe_triangle_gauge_flow", "triangle_gauge_connection",
]
