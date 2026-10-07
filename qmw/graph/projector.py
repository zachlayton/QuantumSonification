"""Read-only four-qubit graph observations for the Quantum Music Workstation.

``GraphProjector`` observes an authoritative density state and its Hamiltonian
in their shared computational basis.  It exposes three intentionally distinct
relations:

* the structural coupling graph from off-diagonal ``H``;
* the state-coherence graph from off-diagonal ``rho``; and
* directed Hilbert-basis current from both ``H`` and ``rho``.

It performs no evolution, measurement, graph walk, scheduling, or synthesis.
The graph spectrum belongs to the coupling topology; it is not QMW's
geometry-native 20-mode resonator spectrum, nor an energy eigenspectrum.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from types import MappingProxyType
from typing import Any, Mapping

import numpy as np


Array = np.ndarray
FOUR_QUBIT_DIMENSION = 16
_TOLERANCE = 1.0e-9


def _readonly(values: object, *, dtype: object) -> Array:
    """Copy one observer result so it cannot mutate the source frame."""

    result = np.array(values, dtype=dtype, copy=True)
    result.setflags(write=False)
    return result


def _square_matrix(name: str, values: object) -> Array:
    matrix = np.asarray(values, dtype=np.complex128)
    expected = (FOUR_QUBIT_DIMENSION, FOUR_QUBIT_DIMENSION)
    if matrix.shape != expected or not np.all(np.isfinite(matrix)):
        raise ValueError(f"{name} must be a finite exact 16x16 four-qubit matrix")
    return np.array(matrix, copy=True)


def _hamiltonian_matrix(hamiltonian: object) -> object:
    """Accept the matrix owned by QMW's immutable Hamiltonian value object."""

    return getattr(hamiltonian, "matrix", hamiltonian)


def _validate_quantum_pair(rho: object, hamiltonian: object) -> tuple[Array, Array]:
    """Return checked, private copies of one authoritative ``rho`` / ``H`` pair."""

    density = _square_matrix("rho", rho)
    generator = _square_matrix("hamiltonian", _hamiltonian_matrix(hamiltonian))
    density_error = float(np.max(np.abs(density - density.conj().T)))
    generator_error = float(np.max(np.abs(generator - generator.conj().T)))
    if density_error > _TOLERANCE:
        raise ValueError("rho must be Hermitian")
    if generator_error > _TOLERANCE:
        raise ValueError("hamiltonian must be Hermitian")
    trace = complex(np.trace(density))
    if abs(trace - 1.0) > _TOLERANCE:
        raise ValueError("rho must have unit trace")
    if float(np.min(np.linalg.eigvalsh((density + density.conj().T) * 0.5))) < -_TOLERANCE:
        raise ValueError("rho must be positive semidefinite")
    return density, generator


def _source_revision(frame: object) -> int:
    """Preserve a native revision when the source contract exposes one."""

    candidate = getattr(frame, "frame_index", None)
    if candidate is None:
        metadata = getattr(frame, "metadata", {})
        if isinstance(metadata, Mapping):
            candidate = metadata.get("revision", 0)
    if candidate is None:
        return 0
    if isinstance(candidate, bool) or int(candidate) != candidate or candidate < 0:
        raise ValueError("source revision must be a nonnegative integer")
    return int(candidate)


@dataclass(frozen=True)
class GraphEdge:
    """One graph relationship in the computational-basis state space.

    Coupling and coherence edges are undirected and stored with ``source <
    target``.  Current edges are directed: ``source -> target`` indicates
    positive instantaneous current into ``target``.
    """

    source: int
    target: int
    magnitude: float
    layer: str
    phase_radians: float | None = None
    signed_current: float | None = None


@dataclass(frozen=True)
class GraphProjectionFrame:
    """Immutable graph observation produced from exactly one QMW source frame."""

    revision: int
    source_revision: int
    time: float
    dt: float
    source_name: str | None
    node_labels: tuple[str, ...]
    populations: Array
    coupling_edges: tuple[GraphEdge, ...]
    coherence_edges: tuple[GraphEdge, ...]
    current_edges: tuple[GraphEdge, ...]
    coupling_adjacency: Array
    coupling_laplacian: Array
    coupling_eigenvalues: Array
    coupling_eigenvectors: Array
    population_graph_coefficients: Array
    basis_current_inflow: Array
    population_rate_unitary: Array
    diagnostics: Mapping[str, float | int | str]
    provenance: Mapping[str, str]

    @property
    def dimension(self) -> int:
        return len(self.node_labels)


class GraphProjector:
    """Project a native four-qubit QMW state into read-only graph diagnostics.

    ``edge_threshold`` is a visualization/observation threshold in the source
    matrix's native units.  It only determines which graph edges are retained;
    it does not modify ``rho``, ``H``, their dynamics, or the QMW event path.
    """

    def __init__(self, *, hbar: float | None = None, edge_threshold: float = 1.0e-12) -> None:
        if hbar is not None and (not math.isfinite(float(hbar)) or hbar <= 0.0):
            raise ValueError("hbar must be finite and positive when supplied")
        if not math.isfinite(float(edge_threshold)) or edge_threshold < 0.0:
            raise ValueError("edge_threshold must be finite and nonnegative")
        self.hbar = None if hbar is None else float(hbar)
        self.edge_threshold = float(edge_threshold)
        self._next_revision = 0

    def project(self, frame: object) -> GraphProjectionFrame:
        """Observe a frame carrying the authoritative ``rho`` and ``hamiltonian``.

        The installed V3 runtime exposes a sealed ``QuantumFrame`` and is
        required whenever that native contract is available.  The root
        checkout retains a legacy ``QuantumStateFrame`` seam only to keep the
        observer independently testable while V3 source is elsewhere.
        """

        try:  # The current root checkout may not contain the V3 implementation.
            from qmw.quantum.dynamics import QuantumFrame
        except ImportError:  # pragma: no cover - depends on checkout layout.
            QuantumFrame = None  # type: ignore[assignment,misc]
        if QuantumFrame is not None and not isinstance(frame, QuantumFrame):
            raise TypeError("GraphProjector requires a sealed native QuantumFrame")
        if not hasattr(frame, "rho") or not hasattr(frame, "hamiltonian"):
            raise TypeError("frame must expose authoritative rho and hamiltonian")
        if getattr(frame, "hamiltonian") is None:
            raise ValueError("GraphProjector requires an authoritative Hamiltonian")
        source_hamiltonian = frame.hamiltonian
        density, generator = _validate_quantum_pair(frame.rho, source_hamiltonian)
        source_hbar = getattr(source_hamiltonian, "hbar", None)
        if source_hbar is not None and (
            not math.isfinite(float(source_hbar)) or float(source_hbar) <= 0.0
        ):
            raise ValueError("source Hamiltonian hbar must be finite and positive")
        effective_hbar = float(source_hbar) if self.hbar is None and source_hbar is not None else (
            1.0 if self.hbar is None else self.hbar
        )
        if source_hbar is not None and self.hbar is not None and not math.isclose(
            self.hbar, float(source_hbar), rel_tol=0.0, abs_tol=_TOLERANCE
        ):
            raise ValueError("projector hbar must match the authoritative Hamiltonian hbar")

        time = float(getattr(frame, "time", getattr(frame, "t", 0.0)))
        dt = float(getattr(frame, "dt", 0.0))
        if not math.isfinite(time) or not math.isfinite(dt) or dt < 0.0:
            raise ValueError("frame time must be finite and dt must be finite and nonnegative")
        revision = self._next_revision
        self._next_revision += 1

        populations = np.real(np.diag(density))
        adjacency = np.zeros((FOUR_QUBIT_DIMENSION, FOUR_QUBIT_DIMENSION), dtype=float)
        coupling_edges: list[GraphEdge] = []
        coherence_edges: list[GraphEdge] = []
        for source in range(FOUR_QUBIT_DIMENSION):
            for target in range(source + 1, FOUR_QUBIT_DIMENSION):
                coupling = generator[source, target]
                coupling_magnitude = float(abs(coupling))
                if coupling_magnitude > self.edge_threshold:
                    adjacency[source, target] = adjacency[target, source] = coupling_magnitude
                    coupling_edges.append(
                        GraphEdge(
                            source=source,
                            target=target,
                            magnitude=coupling_magnitude,
                            layer="hamiltonian_coupling",
                            phase_radians=float(np.angle(coupling)),
                        )
                    )
                coherence = density[source, target]
                coherence_magnitude = float(abs(coherence))
                if coherence_magnitude > self.edge_threshold:
                    coherence_edges.append(
                        GraphEdge(
                            source=source,
                            target=target,
                            magnitude=coherence_magnitude,
                            layer="density_coherence",
                            phase_radians=float(np.angle(coherence)),
                        )
                    )

        # QMW convention: J[destination, source] is current into destination
        # from source.  Its row sum is the unitary population derivative.
        current = (2.0 / effective_hbar) * np.imag(generator * density.T)
        current = 0.5 * (current - current.T)
        np.fill_diagonal(current, 0.0)
        current_edges: list[GraphEdge] = []
        for low in range(FOUR_QUBIT_DIMENSION):
            for high in range(low + 1, FOUR_QUBIT_DIMENSION):
                inflow_low_from_high = float(current[low, high])
                if abs(inflow_low_from_high) <= self.edge_threshold:
                    continue
                source, target = (high, low) if inflow_low_from_high > 0.0 else (low, high)
                current_edges.append(
                    GraphEdge(
                        source=source,
                        target=target,
                        magnitude=abs(inflow_low_from_high),
                        layer="hilbert_basis_probability_current",
                        signed_current=inflow_low_from_high,
                    )
                )

        laplacian = np.diag(np.sum(adjacency, axis=1)) - adjacency
        eigenvalues, eigenvectors = np.linalg.eigh(laplacian)
        coefficients = eigenvectors.T @ populations
        unitary_rate = np.real(np.diag((-1j / effective_hbar) * (generator @ density - density @ generator)))
        continuity_error = float(np.max(np.abs(np.sum(current, axis=1) - unitary_rate)))
        labels = tuple(f"|{index:04b}>" for index in range(FOUR_QUBIT_DIMENSION))
        diagnostics = MappingProxyType(
            {
                "dimension": FOUR_QUBIT_DIMENSION,
                "qubits": 4,
                "coupling_edge_count": len(coupling_edges),
                "coherence_edge_count": len(coherence_edges),
                "current_edge_count": len(current_edges),
                "edge_threshold": self.edge_threshold,
                "hbar": effective_hbar,
                "current_antisymmetry_error": float(np.max(np.abs(current + current.T))),
                "continuity_error": continuity_error,
                "coupling_laplacian_zero_modes": int(np.count_nonzero(np.abs(eigenvalues) <= _TOLERANCE)),
                "coupling_laplacian_orthogonality_error": float(
                    np.max(np.abs(eigenvectors.T @ eigenvectors - np.eye(FOUR_QUBIT_DIMENSION)))
                ),
                "current_convention": "J[destination,source]=(2/hbar) Im(H[destination,source] rho[source,destination])",
                "spectrum_convention": "coupling graph Laplacian; not energy spectrum or 20-mode resonator spectrum",
            }
        )
        provenance = MappingProxyType(
            {
                "projection": "qmw.graph_projector.v1",
                "authority": "read_only_rho_and_hamiltonian",
                "basis": "computational_basis",
                "event_policy": "no_event_generation_or_scheduling",
            }
        )
        return GraphProjectionFrame(
            revision=revision,
            source_revision=_source_revision(frame),
            time=time,
            dt=dt,
            source_name=getattr(frame, "source_name", None),
            node_labels=labels,
            populations=_readonly(populations, dtype=float),
            coupling_edges=tuple(coupling_edges),
            coherence_edges=tuple(coherence_edges),
            current_edges=tuple(current_edges),
            coupling_adjacency=_readonly(adjacency, dtype=float),
            coupling_laplacian=_readonly(laplacian, dtype=float),
            coupling_eigenvalues=_readonly(eigenvalues, dtype=float),
            coupling_eigenvectors=_readonly(eigenvectors, dtype=float),
            population_graph_coefficients=_readonly(coefficients, dtype=float),
            basis_current_inflow=_readonly(current, dtype=float),
            population_rate_unitary=_readonly(unitary_rate, dtype=float),
            diagnostics=diagnostics,
            provenance=provenance,
        )


__all__ = [
    "FOUR_QUBIT_DIMENSION",
    "GraphEdge",
    "GraphProjectionFrame",
    "GraphProjector",
]
