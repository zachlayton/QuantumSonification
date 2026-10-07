"""Authoritative finite-graph U(1) gauge dynamics for QMW quantum worlds.

The graph connection participates in the Hamiltonian through a Peierls link
factor.  Local gauge-frame changes transform ``rho``, the Hamiltonian, and any
physical projector together; they are representation changes and must not
alter current, measurement probabilities, or downstream sound data.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Callable, Mapping, Sequence

import numpy as np

from qmw.flow.gauge_transport import GaugeGraphConnection, GaugeFlowFrame, gauge_flow_from_density_matrix
from qmw.quantum.hilbert_current import hermitian_matrix


Array = np.ndarray
EPS = 1.0e-12


def graph_edges_from_hamiltonian(hamiltonian: object, *, tolerance: float = EPS) -> Array:
    """Return canonical ``i < j`` edges for nonzero Hamiltonian couplings."""

    generator = hermitian_matrix("hamiltonian", hamiltonian)
    if not math.isfinite(float(tolerance)) or tolerance <= 0.0:
        raise ValueError("tolerance must be finite and positive.")
    edges = [
        (left, right)
        for left in range(generator.shape[0])
        for right in range(left + 1, generator.shape[0])
        if abs(generator[left, right]) > tolerance
    ]
    if not edges:
        raise ValueError("hamiltonian must contain at least one off-diagonal coupling.")
    return np.asarray(edges, dtype=int)


def fundamental_cycle_basis(
    node_count: int, edge_indices: object,
) -> Mapping[str, tuple[int, ...]]:
    """Return a deterministic fundamental cycle basis for an undirected graph."""

    edges = np.asarray(edge_indices, dtype=int)
    if edges.ndim != 2 or edges.shape[1:] != (2,):
        raise ValueError("edge_indices must have shape (edge_count, 2).")
    parent = list(range(int(node_count)))

    def root(node: int) -> int:
        while parent[node] != node:
            parent[node] = parent[parent[node]]
            node = parent[node]
        return node

    tree: list[tuple[int, int]] = []
    chords: list[tuple[int, int]] = []
    for left, right in edges.tolist():
        left_root, right_root = root(left), root(right)
        if left_root != right_root:
            parent[right_root] = left_root
            tree.append((left, right))
        else:
            chords.append((left, right))

    adjacency: list[list[int]] = [[] for _ in range(int(node_count))]
    for left, right in tree:
        adjacency[left].append(right)
        adjacency[right].append(left)

    def tree_path(start: int, finish: int) -> tuple[int, ...]:
        queue = [start]
        previous = {start: -1}
        for node in queue:
            if node == finish:
                break
            for neighbor in sorted(adjacency[node]):
                if neighbor not in previous:
                    previous[neighbor] = node
                    queue.append(neighbor)
        if finish not in previous:
            raise ValueError("cycle basis requires chord endpoints in one tree component.")
        path = [finish]
        while path[-1] != start:
            path.append(previous[path[-1]])
        return tuple(reversed(path))

    return {
        f"cycle_{index:02d}": tree_path(left, right)
        for index, (left, right) in enumerate(chords)
    }


def gauge_unitary(local_phase: object) -> Array:
    phase = np.asarray(local_phase, dtype=float)
    if phase.ndim != 1 or not np.all(np.isfinite(phase)):
        raise ValueError("local_phase must be a finite vector.")
    return np.diag(np.exp(1j * phase))


def gauge_transform_operator(operator: object, local_phase: object) -> Array:
    matrix = np.asarray(operator, dtype=np.complex128)
    unitary = gauge_unitary(local_phase)
    if matrix.shape != unitary.shape or not np.all(np.isfinite(matrix)):
        raise ValueError("operator and local_phase must have the same dimension.")
    return unitary @ matrix @ unitary.conj().T


def peierls_hamiltonian(
    bare_hamiltonian: object,
    connection: GaugeGraphConnection,
    *,
    tolerance: float = EPS,
) -> Array:
    """Apply ``H_ij -> H_ij U_ij`` on the declared connection graph."""

    bare = hermitian_matrix("bare_hamiltonian", bare_hamiltonian)
    if bare.shape != (connection.node_count, connection.node_count):
        raise ValueError("bare Hamiltonian and connection dimensions must agree.")
    allowed = np.eye(connection.node_count, dtype=bool)
    source, destination = connection.edge_indices.T
    allowed[source, destination] = True
    allowed[destination, source] = True
    if np.any(np.abs(bare[~allowed]) > tolerance):
        raise ValueError("bare Hamiltonian has couplings outside the gauge graph.")
    gauged = np.diag(np.diag(bare)).astype(np.complex128)
    for (left, right), link in zip(connection.edge_indices, connection.link_variable):
        gauged[left, right] = bare[left, right] * link
        gauged[right, left] = np.conj(gauged[left, right])
    return hermitian_matrix("gauged_hamiltonian", gauged)


def transported_coherences(rho: object, connection: GaugeGraphConnection) -> Array:
    """Return invariant ``rho_ij U_ji`` for canonical connection edges."""

    density = hermitian_matrix("rho", rho)
    if density.shape != (connection.node_count, connection.node_count):
        raise ValueError("rho and connection dimensions must agree.")
    source, destination = connection.edge_indices.T
    return np.array(
        density[source, destination] * np.conj(connection.link_variable),
        copy=True,
    )


def connection_with_cycle_flux(
    connection: GaugeGraphConnection, cycle: Sequence[int], flux: float,
) -> GaugeGraphConnection:
    """Set a declared loop's oriented link phases to one physical holonomy.

    The phase is distributed uniformly along the selected cycle.  This is a
    physical connection change, not a local gauge-frame transformation.
    """

    value = float(flux)
    nodes = tuple(int(node) for node in cycle)
    if not math.isfinite(value) or not -math.pi <= value <= math.pi:
        raise ValueError("flux must be finite and lie in [-pi, pi].")
    if len(nodes) < 3:
        raise ValueError("cycle must contain at least three nodes.")
    result = GaugeGraphConnection(
        connection.node_count, connection.edge_indices,
        np.zeros_like(connection.link_phase), connection.coupling,
    )
    phase_per_link = value / len(nodes)
    for source, destination in zip(nodes, nodes[1:] + nodes[:1]):
        result = result.set_phase(source, destination, phase_per_link)
    return result


@dataclass(frozen=True)
class GaugeDynamicsFrame:
    time: float
    rho: Array
    hamiltonian: Array
    rho_dot: Array
    flow: GaugeFlowFrame
    transported_coherence: Array
    provenance: str = "authoritative_u1_graph_gauge_covariant_density_dynamics_v1"


class GaugeDynamicsEngine:
    """Evolve a density matrix under a graph-gauged Hamiltonian."""

    def __init__(
        self,
        bare_hamiltonian: object,
        connection: GaugeGraphConnection | None = None,
        *,
        hbar: float = 1.0,
        cycles: Mapping[str, Sequence[int]] | None = None,
    ) -> None:
        self.bare_hamiltonian = hermitian_matrix("bare_hamiltonian", bare_hamiltonian)
        if not math.isfinite(float(hbar)) or hbar <= 0.0:
            raise ValueError("hbar must be finite and positive.")
        self.hbar = float(hbar)
        if connection is None:
            edges = graph_edges_from_hamiltonian(self.bare_hamiltonian)
            connection = GaugeGraphConnection(
                self.bare_hamiltonian.shape[0], edges, np.zeros(edges.shape[0])
            )
        self.connection = connection
        self.hamiltonian = peierls_hamiltonian(self.bare_hamiltonian, connection)
        self.cycles = dict(cycles or fundamental_cycle_basis(
            connection.node_count, connection.edge_indices
        ))
        self._eigenvalues, self._eigenvectors = np.linalg.eigh(self.hamiltonian)
        self._previous_flow: GaugeFlowFrame | None = None

    def derivative(
        self,
        rho: object,
        *,
        open_system_derivative: Callable[[Array], object] | None = None,
    ) -> Array:
        density = hermitian_matrix("rho", rho)
        if density.shape != self.hamiltonian.shape:
            raise ValueError("rho must match the gauged Hamiltonian dimension.")
        result = (-1j / self.hbar) * (
            self.hamiltonian @ density - density @ self.hamiltonian
        )
        if open_system_derivative is not None:
            addition = np.asarray(open_system_derivative(np.array(density, copy=True)), dtype=np.complex128)
            if addition.shape != density.shape or not np.all(np.isfinite(addition)):
                raise ValueError("open-system derivative must be finite and match rho.")
            result = result + addition
        return np.array(result, copy=True)

    def advance_unitary(self, rho: object, dt: float) -> Array:
        density = hermitian_matrix("rho", rho)
        if density.shape != self.hamiltonian.shape:
            raise ValueError("rho must match the gauged Hamiltonian dimension.")
        duration = float(dt)
        if not math.isfinite(duration) or duration <= 0.0:
            raise ValueError("dt must be finite and positive.")
        propagator = (
            self._eigenvectors * np.exp(-1j * self._eigenvalues * duration / self.hbar)
        ) @ self._eigenvectors.conj().T
        evolved = propagator @ density @ propagator.conj().T
        return hermitian_matrix("evolved rho", (evolved + evolved.conj().T) * 0.5)

    def observe(self, rho: object, *, time: float) -> GaugeDynamicsFrame:
        density = hermitian_matrix("rho", rho)
        flow = gauge_flow_from_density_matrix(
            density,
            self.hamiltonian,
            self.connection,
            time=float(time),
            hbar=self.hbar,
            cycles=self.cycles,
            previous=self._previous_flow,
        )
        self._previous_flow = flow
        return GaugeDynamicsFrame(
            time=float(time),
            rho=np.array(density, copy=True),
            hamiltonian=np.array(self.hamiltonian, copy=True),
            rho_dot=self.derivative(density),
            flow=flow,
            transported_coherence=transported_coherences(density, self.connection),
        )

    def represented(self, local_phase: object) -> "GaugeDynamicsEngine":
        """Return the same physical engine in another local phase convention."""

        phase = np.asarray(local_phase, dtype=float)
        if phase.shape != (self.connection.node_count,):
            raise ValueError("local_phase must match the connection node count.")
        return GaugeDynamicsEngine(
            self.bare_hamiltonian,
            self.connection.transformed(phase),
            hbar=self.hbar,
            cycles=self.cycles,
        )


__all__ = [
    "GaugeDynamicsEngine", "GaugeDynamicsFrame", "fundamental_cycle_basis",
    "gauge_transform_operator", "gauge_unitary", "graph_edges_from_hamiltonian",
    "connection_with_cycle_flux", "peierls_hamiltonian", "transported_coherences",
]
