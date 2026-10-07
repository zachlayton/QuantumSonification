"""Runtime steps 6-10 for explicit Hilbert flow and relational geometry.

The native four-qubit path has no canonical spatial wavefunction.  Step 6
therefore publishes the computational-basis projection that is actually
defined by the authoritative density matrix and labels it non-spatial.  A
future spatial projector can replace this adapter without changing the
downstream frame slots or pretending that Hilbert indices are positions.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
import math

import numpy as np

from qmw.flow import (
    CurrentEvent,
    HilbertBasisFlowObservation,
    events_from_hilbert_edges,
)
from qmw.quantum.dynamics import QuantumFrame
from qmw.quantum.hilbert_current import sparse_current_edges
from qmw.unified_instrument_v3.frames import RelationalGeometryFrame
from qmw.unified_instrument_v3.relational_geometry import (
    RelationalGeometryConfig,
    observe_relational_geometry,
)

from .frame import QMWFrame, RuntimeStep
from .scheduler import QMWRuntimeScheduler


def _readonly(values: object, *, dtype: object = float) -> np.ndarray:
    result = np.array(values, dtype=dtype, copy=True)
    result.setflags(write=False)
    return result


@dataclass(frozen=True)
class HilbertBasisProjectionFrame:
    """Declared computational-basis population projection of one rho.

    This is a finite Hilbert-graph observation, not a configuration-space or
    physical-space projection.  Mixed states are supported without inventing
    a wavefunction phase.
    """

    source: QuantumFrame
    revision: int
    time: float
    quantum_revision: int
    basis_ids: tuple[str, ...]
    populations: np.ndarray
    basis_label: str = "displayed_computational_basis"
    is_spatial: bool = False
    provenance: str = "explicit_hilbert_basis_population_projection_v1"

    def __post_init__(self) -> None:
        if not isinstance(self.source, QuantumFrame):
            raise TypeError("source must be a sealed QuantumFrame")
        if isinstance(self.revision, bool) or int(self.revision) != self.revision or self.revision < 0:
            raise ValueError("revision must be a nonnegative integer")
        if isinstance(self.quantum_revision, bool) or int(self.quantum_revision) != self.quantum_revision or self.quantum_revision < 0:
            raise ValueError("quantum_revision must be a nonnegative integer")
        time = float(self.time)
        if not math.isfinite(time):
            raise ValueError("time must be finite")
        identifiers = tuple(str(value) for value in self.basis_ids)
        populations = _readonly(self.populations)
        if populations.ndim != 1 or populations.size == 0:
            raise ValueError("populations must be a nonempty vector")
        if len(identifiers) != populations.size or len(set(identifiers)) != len(identifiers) or any(not value for value in identifiers):
            raise ValueError("basis_ids must uniquely identify every population")
        if not np.all(np.isfinite(populations)) or np.any(populations < -1.0e-12):
            raise ValueError("populations must be finite and nonnegative")
        if not np.isclose(np.sum(populations), 1.0, atol=1.0e-10, rtol=1.0e-10):
            raise ValueError("populations must sum to one")
        if self.is_spatial:
            raise ValueError("the computational-basis projection is not spatial")
        if not self.basis_label or not self.provenance:
            raise ValueError("basis_label and provenance must be nonempty")
        if int(self.revision) != self.source.frame_index or int(self.quantum_revision) != self.source.frame_index:
            raise ValueError("projection revisions must match the source QuantumFrame")
        if not math.isclose(time, self.source.time, rel_tol=0.0, abs_tol=1.0e-12):
            raise ValueError("projection time must match the source QuantumFrame")
        if not np.allclose(populations, self.source.populations, atol=1.0e-12, rtol=0.0):
            raise ValueError("projection populations must come from the source QuantumFrame")
        object.__setattr__(self, "revision", int(self.revision))
        object.__setattr__(self, "quantum_revision", int(self.quantum_revision))
        object.__setattr__(self, "time", time)
        object.__setattr__(self, "basis_ids", identifiers)
        object.__setattr__(self, "populations", populations)


@dataclass(frozen=True)
class GeometryEigenmodeFrame:
    """Audited Laplacian eigenmodes of one relational-geometry revision."""

    source: RelationalGeometryFrame
    revision: int
    time: float
    geometry_revision: int
    node_ids: tuple[str, ...]
    eigenvalues: np.ndarray
    eigenvectors: np.ndarray
    zero_mode_count: int
    spectral_gap: float
    degenerate_groups: tuple[tuple[int, ...], ...]
    basis_stable: bool
    domain: str = "derived_relational_graph"
    provenance: str = "canonical_sign_relational_laplacian_eigenmodes_v1"

    def __post_init__(self) -> None:
        if not isinstance(self.source, RelationalGeometryFrame):
            raise TypeError("source must be a RelationalGeometryFrame")
        for name in ("revision", "geometry_revision", "zero_mode_count"):
            value = getattr(self, name)
            if isinstance(value, bool) or int(value) != value or value < 0:
                raise ValueError(f"{name} must be a nonnegative integer")
            object.__setattr__(self, name, int(value))
        time = float(self.time)
        gap = float(self.spectral_gap)
        values = _readonly(self.eigenvalues)
        vectors = _readonly(self.eigenvectors)
        identifiers = tuple(str(value) for value in self.node_ids)
        count = len(identifiers)
        if not math.isfinite(time) or not math.isfinite(gap) or gap < 0.0:
            raise ValueError("time and spectral_gap must be finite and spectral_gap nonnegative")
        if count == 0 or len(set(identifiers)) != count or any(not value for value in identifiers):
            raise ValueError("node_ids must be nonempty and unique")
        if values.shape != (count,) or vectors.shape != (count, count):
            raise ValueError("eigenvalues and eigenvectors must match node_ids")
        if not np.all(np.isfinite(values)) or not np.all(np.isfinite(vectors)):
            raise ValueError("eigenmodes must be finite")
        if np.any(values < -1.0e-10) or np.any(np.diff(values) < -1.0e-10):
            raise ValueError("eigenvalues must be ordered and nonnegative")
        groups = tuple(tuple(int(index) for index in group) for group in self.degenerate_groups)
        flattened = tuple(index for group in groups for index in group)
        if flattened != tuple(range(count)) or any(not group for group in groups):
            raise ValueError("degenerate_groups must partition the ordered modes")
        if self.zero_mode_count > count:
            raise ValueError("zero_mode_count cannot exceed the mode count")
        expected_stability = all(len(group) == 1 for group in groups)
        if bool(self.basis_stable) != expected_stability:
            raise ValueError("basis_stable must report whether every eigenspace is simple")
        if not self.domain or not self.provenance:
            raise ValueError("domain and provenance must be nonempty")
        if self.revision != self.source.revision or self.geometry_revision != self.source.revision:
            raise ValueError("eigenmode revisions must match the source geometry")
        if not math.isclose(time, self.source.time, rel_tol=0.0, abs_tol=1.0e-12):
            raise ValueError("eigenmode time must match the source geometry")
        if identifiers != self.source.node_ids or not np.allclose(values, self.source.eigenvalues, atol=1.0e-12, rtol=0.0):
            raise ValueError("eigenmode nodes and values must match the source geometry")
        if not np.allclose(self.source.laplacian @ vectors, vectors * values, atol=1.0e-8, rtol=1.0e-8):
            raise ValueError("eigenvectors must solve the source geometry Laplacian")
        object.__setattr__(self, "time", time)
        object.__setattr__(self, "spectral_gap", gap)
        object.__setattr__(self, "node_ids", identifiers)
        object.__setattr__(self, "eigenvalues", values)
        object.__setattr__(self, "eigenvectors", vectors)
        object.__setattr__(self, "degenerate_groups", groups)
        object.__setattr__(self, "basis_stable", bool(self.basis_stable))


@dataclass(frozen=True)
class FlowGeometryRuntimeConfig:
    """Numerical and event-volume policy for runtime steps 6-10."""

    current_event_threshold: float = 1.0e-9
    maximum_current_events: int = 64
    eigenvalue_tolerance: float = 1.0e-9
    relational_geometry: RelationalGeometryConfig = RelationalGeometryConfig()

    def __post_init__(self) -> None:
        threshold = float(self.current_event_threshold)
        tolerance = float(self.eigenvalue_tolerance)
        if not math.isfinite(threshold) or threshold <= 0.0:
            raise ValueError("current_event_threshold must be finite and positive")
        if isinstance(self.maximum_current_events, bool) or int(self.maximum_current_events) != self.maximum_current_events or self.maximum_current_events <= 0:
            raise ValueError("maximum_current_events must be a positive integer")
        if not math.isfinite(tolerance) or tolerance <= 0.0:
            raise ValueError("eigenvalue_tolerance must be finite and positive")
        if not isinstance(self.relational_geometry, RelationalGeometryConfig):
            raise TypeError("relational_geometry must be a RelationalGeometryConfig")
        object.__setattr__(self, "current_event_threshold", threshold)
        object.__setattr__(self, "maximum_current_events", int(self.maximum_current_events))
        object.__setattr__(self, "eigenvalue_tolerance", tolerance)


def _basis_ids(dimension: int) -> tuple[str, ...]:
    qubits = int(round(math.log2(dimension)))
    if 2 ** qubits != dimension:
        raise ValueError("computational-basis projection requires a power-of-two dimension")
    return tuple(format(index, f"0{qubits}b") for index in range(dimension))


def _degenerate_groups(values: np.ndarray, tolerance: float) -> tuple[tuple[int, ...], ...]:
    groups: list[tuple[int, ...]] = []
    start = 0
    for index in range(1, values.size):
        scale = max(1.0, abs(float(values[index])), abs(float(values[index - 1])))
        if abs(float(values[index] - values[index - 1])) > tolerance * scale:
            groups.append(tuple(range(start, index)))
            start = index
    groups.append(tuple(range(start, values.size)))
    return tuple(groups)


def _canonical_signs(vectors: np.ndarray) -> np.ndarray:
    result = np.array(vectors, dtype=float, copy=True)
    for column in range(result.shape[1]):
        pivot = int(np.argmax(np.abs(result[:, column])))
        if result[pivot, column] < 0.0:
            result[:, column] *= -1.0
    return result


class FlowGeometryRuntimeAdapter:
    """Attach explicit projection, flow, events, geometry, and eigenmodes."""

    def __init__(self, *, config: FlowGeometryRuntimeConfig | None = None) -> None:
        self.config = config or FlowGeometryRuntimeConfig()

    @staticmethod
    def _quantum(frame: QMWFrame) -> QuantumFrame:
        if not isinstance(frame.quantum, QuantumFrame):
            raise TypeError("QMWFrame.quantum must be a sealed QuantumFrame")
        if not math.isclose(frame.quantum.time, frame.time, rel_tol=0.0, abs_tol=1.0e-12):
            raise ValueError("QMWFrame and QuantumFrame times must match")
        return frame.quantum

    def project_basis(self, frame: QMWFrame) -> QMWFrame:
        quantum = self._quantum(frame)
        projection = HilbertBasisProjectionFrame(
            source=quantum,
            revision=quantum.frame_index,
            time=quantum.time,
            quantum_revision=quantum.frame_index,
            basis_ids=_basis_ids(quantum.rho.shape[0]),
            populations=quantum.populations,
        )
        dirty = frame.dirty
        geometry_quantum_revision = getattr(frame.geometry, "quantum_revision", None)
        if geometry_quantum_revision != quantum.frame_index:
            dirty = dirty.invalidate_geometry()
        elif getattr(frame.eigenmodes, "geometry_revision", None) != getattr(frame.geometry, "revision", None):
            dirty = dirty.invalidate_eigenbasis()
        diagnostics = dict(frame.diagnostics)
        diagnostics.update(
            {
                "projection_domain": "hilbert_graph",
                "projection_is_spatial": False,
                "projection_basis": projection.basis_label,
            }
        )
        return frame.with_updates(
            projection=projection,
            revisions=replace(frame.revisions, projection=quantum.frame_index),
            dirty=dirty,
            diagnostics=diagnostics,
        )

    def compute_flow(self, frame: QMWFrame) -> QMWFrame:
        quantum = self._quantum(frame)
        flow = HilbertBasisFlowObservation(quantum)
        diagnostics = dict(frame.diagnostics)
        diagnostics.update(
            {
                "flow_domain": "hilbert_graph",
                "flow_is_spatial": False,
                "flow_current_convention": "inflow_indexed_i_receives_from_j",
            }
        )
        return frame.with_updates(
            flow=flow,
            revisions=replace(frame.revisions, flow=quantum.frame_index),
            diagnostics=diagnostics,
        )

    def detect_events(self, frame: QMWFrame) -> QMWFrame:
        if not isinstance(frame.flow, HilbertBasisFlowObservation):
            raise TypeError("step 8 requires a HilbertBasisFlowObservation from step 7")
        # QuantumFrame stores I[i,j] as inflow i <- j.  sparse_current_edges
        # expects positive J[source,destination], hence the explicit transpose.
        edges = sparse_current_edges(
            frame.flow.current_inflow.T,
            threshold=self.config.current_event_threshold,
        )
        ranked = sorted(edges, key=lambda edge: (-edge.magnitude, edge.source, edge.destination))
        bounded = tuple(ranked[: self.config.maximum_current_events])
        events: tuple[CurrentEvent, ...] = events_from_hilbert_edges(bounded)
        diagnostics = dict(frame.diagnostics)
        diagnostics.update(
            {
                "hilbert_current_events_detected": len(edges),
                "hilbert_current_events_published": len(events),
                "hilbert_current_event_threshold": self.config.current_event_threshold,
            }
        )
        return frame.with_updates(
            events=frame.events + events,
            diagnostics=diagnostics,
        )

    def update_geometry(self, frame: QMWFrame) -> QMWFrame:
        quantum = self._quantum(frame)
        geometry = observe_relational_geometry(
            quantum,
            config=self.config.relational_geometry,
        )
        diagnostics = dict(frame.diagnostics)
        diagnostics.update(
            {
                "geometry_model": geometry.provenance,
                "geometry_embedding_valid": geometry.embedding_valid,
            }
        )
        return frame.with_updates(
            geometry=geometry,
            revisions=replace(frame.revisions, geometry=geometry.revision),
            dirty=frame.dirty.clear("geometry"),
            diagnostics=diagnostics,
        )

    def update_eigenmodes(self, frame: QMWFrame) -> QMWFrame:
        if not isinstance(frame.geometry, RelationalGeometryFrame):
            raise TypeError("step 10 requires a RelationalGeometryFrame from step 9")
        geometry = frame.geometry
        values = np.asarray(geometry.eigenvalues, dtype=float)
        vectors = _canonical_signs(geometry.eigenvectors)
        if not np.allclose(
            geometry.laplacian @ vectors,
            vectors * values,
            atol=1.0e-8,
            rtol=1.0e-8,
        ):
            raise ValueError("geometry eigenpairs do not solve the declared Laplacian")
        tolerance = self.config.eigenvalue_tolerance
        zero_modes = int(np.count_nonzero(values <= tolerance))
        positive = values[values > tolerance]
        gap = 0.0 if positive.size == 0 else float(positive[0])
        groups = _degenerate_groups(values, tolerance)
        eigenmodes = GeometryEigenmodeFrame(
            source=geometry,
            revision=geometry.revision,
            time=geometry.time,
            geometry_revision=geometry.revision,
            node_ids=geometry.node_ids,
            eigenvalues=values,
            eigenvectors=vectors,
            zero_mode_count=zero_modes,
            spectral_gap=gap,
            degenerate_groups=groups,
            basis_stable=all(len(group) == 1 for group in groups),
        )
        diagnostics = dict(frame.diagnostics)
        diagnostics.update(
            {
                "geometry_zero_modes": zero_modes,
                "geometry_spectral_gap": gap,
                "geometry_eigenbasis_stable": eigenmodes.basis_stable,
            }
        )
        return frame.with_updates(
            eigenmodes=eigenmodes,
            revisions=replace(frame.revisions, eigenbasis=geometry.revision),
            dirty=frame.dirty.clear("eigenbasis"),
            diagnostics=diagnostics,
        )


def register_flow_geometry(
    scheduler: QMWRuntimeScheduler,
    *,
    config: FlowGeometryRuntimeConfig | None = None,
) -> FlowGeometryRuntimeAdapter:
    """Register the authoritative native four-qubit path at steps 6-10."""

    if not isinstance(scheduler, QMWRuntimeScheduler):
        raise TypeError("scheduler must be a QMWRuntimeScheduler")
    adapter = FlowGeometryRuntimeAdapter(config=config)
    scheduler.register(RuntimeStep.PROJECT_SPATIAL_MODAL_BASIS, adapter.project_basis)
    scheduler.register(RuntimeStep.COMPUTE_CURRENT_FLUX, adapter.compute_flow)
    scheduler.register(RuntimeStep.DETECT_EVENTS, adapter.detect_events)
    scheduler.register(RuntimeStep.UPDATE_GEOMETRY, adapter.update_geometry)
    scheduler.register(RuntimeStep.UPDATE_GEOMETRY_EIGENMODES, adapter.update_eigenmodes)
    return adapter


__all__ = [
    "FlowGeometryRuntimeAdapter",
    "FlowGeometryRuntimeConfig",
    "GeometryEigenmodeFrame",
    "HilbertBasisProjectionFrame",
    "register_flow_geometry",
]
