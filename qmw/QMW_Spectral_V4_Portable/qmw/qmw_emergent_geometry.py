"""Read-only entanglement-to-relational-geometry observer for four-qubit QMW.

This module deliberately does *not* evolve ``rho``, modify a Hamiltonian,
alter a GPE field, or generate sound. Its graph and metric are an explicit
finite-dimensional model inspired by entanglement/geometry arguments, not a
claim of a bulk spacetime reconstruction.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Iterable, Mapping

import numpy as np


Array = np.ndarray
_EPS = 1.0e-12
_PAULI: Mapping[str, Array] = {
    "I": np.eye(2, dtype=np.complex128),
    "X": np.array([[0.0, 1.0], [1.0, 0.0]], dtype=np.complex128),
    "Y": np.array([[0.0, -1j], [1j, 0.0]], dtype=np.complex128),
    "Z": np.array([[1.0, 0.0], [0.0, -1.0]], dtype=np.complex128),
}


def _readonly(values: Array, *, dtype: object | None = None) -> Array:
    result = np.array(values, dtype=dtype, copy=True)
    result.setflags(write=False)
    return result


def _dimension_to_qubits(dimension: int) -> int:
    if dimension < 2 or dimension & (dimension - 1):
        raise ValueError("rho dimension must be a nontrivial power of two.")
    return int(math.log2(dimension))


def validate_density_matrix(rho: object, *, tolerance: float = 1.0e-9) -> Array:
    """Validate a density operator without mutating the caller's array."""

    if not math.isfinite(float(tolerance)) or tolerance <= 0.0:
        raise ValueError("tolerance must be finite and greater than zero.")
    matrix = np.asarray(rho, dtype=np.complex128)
    if matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1]:
        raise ValueError("rho must be square.")
    _dimension_to_qubits(matrix.shape[0])
    if not np.all(np.isfinite(matrix)):
        raise ValueError("rho must be finite.")
    if not np.allclose(matrix, matrix.conj().T, atol=tolerance, rtol=0.0):
        raise ValueError("rho must be Hermitian.")
    trace = complex(np.trace(matrix))
    if abs(trace.imag) > tolerance or not np.isclose(trace.real, 1.0, atol=tolerance, rtol=0.0):
        raise ValueError("rho must have unit trace.")
    hermitian = 0.5 * (matrix + matrix.conj().T)
    if float(np.min(np.linalg.eigvalsh(hermitian))) < -tolerance:
        raise ValueError("rho must be positive semidefinite.")
    return _readonly(hermitian, dtype=np.complex128)


def reduced_density_matrix(rho: object, keep_qubits: Iterable[int]) -> Array:
    """Return ``Tr_not_keep(rho)`` in QMW's most-significant-qubit ordering."""

    matrix = validate_density_matrix(rho)
    n_qubits = _dimension_to_qubits(matrix.shape[0])
    keep = tuple(sorted(set(int(qubit) for qubit in keep_qubits)))
    if not keep or any(qubit < 0 or qubit >= n_qubits for qubit in keep):
        raise ValueError("keep_qubits must be a nonempty valid set of qubit indices.")
    tensor = matrix.reshape((2,) * (2 * n_qubits))
    row_labels = list(range(n_qubits))
    column_labels = [n_qubits + qubit if qubit in keep else qubit for qubit in range(n_qubits)]
    output_labels = list(keep) + [n_qubits + qubit for qubit in keep]
    reduced = np.einsum(tensor, row_labels + column_labels, output_labels)
    return _readonly(reduced.reshape(2 ** len(keep), 2 ** len(keep)), dtype=np.complex128)


def von_neumann_entropy(rho: object, *, base: float = 2.0) -> float:
    """Return entropy in ``base`` units, clipping only sub-tolerance roundoff."""

    if not math.isfinite(float(base)) or base <= 0.0 or math.isclose(base, 1.0):
        raise ValueError("base must be finite, positive, and not one.")
    matrix = validate_density_matrix(rho)
    values = np.clip(np.linalg.eigvalsh(matrix).real, 0.0, 1.0)
    values = values[values > _EPS]
    return 0.0 if values.size == 0 else float(-np.sum(values * np.log(values)) / math.log(base))


def mutual_information(rho: object, subsystem_a: Iterable[int], subsystem_b: Iterable[int]) -> float:
    """Return quantum mutual information ``S(A)+S(B)-S(AB)`` in bits."""

    a, b = tuple(sorted(set(subsystem_a))), tuple(sorted(set(subsystem_b)))
    if not a or not b or set(a).intersection(b):
        raise ValueError("subsystem_a and subsystem_b must be nonempty and disjoint.")
    value = (
        von_neumann_entropy(reduced_density_matrix(rho, a))
        + von_neumann_entropy(reduced_density_matrix(rho, b))
        - von_neumann_entropy(reduced_density_matrix(rho, tuple(sorted(a + b))))
    )
    if value < -1.0e-9:
        raise ValueError("mutual information became negative beyond numerical tolerance.")
    return float(max(value, 0.0))


def pauli_pair_expectation(rho: object, left: int, right: int, term: str) -> float:
    """Observe one two-site Pauli correlation, e.g. ``XX`` or ``ZZ``."""

    matrix = validate_density_matrix(rho)
    n_qubits = _dimension_to_qubits(matrix.shape[0])
    if left == right or not (0 <= left < n_qubits and 0 <= right < n_qubits):
        raise ValueError("left and right must be distinct valid qubit indices.")
    if len(term) != 2 or any(symbol not in _PAULI for symbol in term):
        raise ValueError("term must contain two Pauli labels from I, X, Y, Z.")
    factors = [_PAULI["I"] for _ in range(n_qubits)]
    factors[left], factors[right] = _PAULI[term[0]], _PAULI[term[1]]
    operator = factors[0]
    for factor in factors[1:]:
        operator = np.kron(operator, factor)
    value = complex(np.trace(matrix @ operator))
    if abs(value.imag) > 1.0e-9:
        raise ValueError("Pauli expectation was not real within tolerance.")
    return float(np.clip(value.real, -1.0, 1.0))


def two_qubit_concurrence(rho_pair: object) -> float:
    """Return Wootters concurrence for a two-qubit reduced density matrix."""

    matrix = validate_density_matrix(rho_pair)
    if matrix.shape != (4, 4):
        raise ValueError("two_qubit_concurrence requires a 4x4 reduced density matrix.")
    spin_flip = np.kron(_PAULI["Y"], _PAULI["Y"])
    product = matrix @ spin_flip @ matrix.conj() @ spin_flip
    roots = np.sqrt(np.maximum(np.linalg.eigvals(product).real, 0.0))
    roots.sort()
    return float(np.clip(roots[-1] - np.sum(roots[:-1]), 0.0, 1.0))


def bell_witness(correlations: Mapping[str, float]) -> tuple[str, float, float]:
    """Return best Bell-state fidelity and witness; a negative witness certifies entanglement."""

    try:
        xx, yy, zz = (float(correlations[term]) for term in ("XX", "YY", "ZZ"))
    except KeyError as error:
        raise ValueError("Bell witness requires XX, YY, and ZZ correlations.") from error
    fidelities = {
        "Phi+": (1.0 + xx - yy + zz) / 4.0,
        "Phi-": (1.0 - xx + yy + zz) / 4.0,
        "Psi+": (1.0 + xx + yy - zz) / 4.0,
        "Psi-": (1.0 - xx - yy - zz) / 4.0,
    }
    label = max(fidelities, key=fidelities.get)
    fidelity = float(np.clip(fidelities[label], 0.0, 1.0))
    return label, fidelity, 0.5 - fidelity


@dataclass(frozen=True)
class EntanglementGeometryConfig:
    """Numerical/modeling controls for the read-only relational graph."""

    pauli_terms: tuple[str, ...] = ("XX", "YY", "ZZ")
    distance_floor: float = 1.0e-6
    maximum_distance: float = 12.0
    pauli_envelope: float = 0.0
    normalized_laplacian: bool = False

    def __post_init__(self) -> None:
        valid = bool(self.pauli_terms) and all(len(term) == 2 and all(axis in _PAULI for axis in term) for term in self.pauli_terms)
        if not valid:
            raise ValueError("pauli_terms must contain nonempty two-axis Pauli terms.")
        if not math.isfinite(self.distance_floor) or not 0.0 < self.distance_floor <= 1.0:
            raise ValueError("distance_floor must lie in (0, 1].")
        if not math.isfinite(self.maximum_distance) or self.maximum_distance <= 0.0:
            raise ValueError("maximum_distance must be finite and positive.")
        if not math.isfinite(self.pauli_envelope) or not 0.0 <= self.pauli_envelope <= 1.0:
            raise ValueError("pauli_envelope must lie in [0, 1].")


@dataclass(frozen=True)
class RelationalEdge:
    """A two-qubit relation; distance/permeability are declared model proxies."""

    left: int
    right: int
    mutual_information_bits: float
    two_qubit_concurrence: float
    bell_target: str
    bell_fidelity: float
    bell_witness: float
    witness_certifies_entanglement: bool
    information_strength: float
    pauli_correlations: tuple[tuple[str, float], ...]
    adjacency_weight: float
    metric_length: float
    boundary_permeability: float


@dataclass(frozen=True)
class EmergentGeometryFrame:
    """One immutable observation: quantum invariants plus modeled graph geometry."""

    revision: int
    time: float
    reduced_density_matrices: Mapping[tuple[int, ...], Array]
    node_entropy_bits: Array
    edges: tuple[RelationalEdge, ...]
    adjacency: Array
    laplacian: Array
    eigenvalues: Array
    eigenvectors: Array
    provenance: str = "read_only_entanglement_relational_graph_v1"


def observe_emergent_geometry(
    rho: object,
    *,
    revision: int,
    time: float,
    config: EntanglementGeometryConfig | None = None,
) -> EmergentGeometryFrame:
    """Observe a finite relational graph from a four-qubit density matrix.

    Mutual information and pair-entanglement diagnostics are quantum
    information observables. Turning them into a distance, permeability, or
    Laplacian mode is an explicit finite-model choice.
    """

    if int(revision) != revision or revision < 0:
        raise ValueError("revision must be a nonnegative integer.")
    if not math.isfinite(float(time)):
        raise ValueError("time must be finite.")
    cfg = config or EntanglementGeometryConfig()
    matrix = validate_density_matrix(rho)
    n_qubits = _dimension_to_qubits(matrix.shape[0])
    if n_qubits != 4:
        raise ValueError("v1 is deliberately bounded to the QMW four-qubit density contract.")

    reduced: dict[tuple[int, ...], Array] = {}
    node_entropy = np.empty(n_qubits, dtype=float)
    for node in range(n_qubits):
        key = (node,)
        reduced[key] = reduced_density_matrix(matrix, key)
        node_entropy[node] = von_neumann_entropy(reduced[key])

    adjacency = np.zeros((n_qubits, n_qubits), dtype=float)
    edges: list[RelationalEdge] = []
    for left in range(n_qubits):
        for right in range(left + 1, n_qubits):
            pair_key = (left, right)
            reduced[pair_key] = reduced_density_matrix(matrix, pair_key)
            information = mutual_information(matrix, (left,), (right,))
            information_strength = float(np.clip(information / 2.0, 0.0, 1.0))
            terms = tuple(dict.fromkeys((*cfg.pauli_terms, "XX", "YY", "ZZ")))
            correlations = tuple((term, pauli_pair_expectation(matrix, left, right, term)) for term in terms)
            correlation_map = dict(correlations)
            target, fidelity, witness = bell_witness(correlation_map)
            concurrence = two_qubit_concurrence(reduced[pair_key])
            correlation_norm = float(np.mean([abs(value) for _, value in correlations]))
            adjacency_weight = information_strength * ((1.0 - cfg.pauli_envelope) + cfg.pauli_envelope * correlation_norm)
            adjacency_weight = float(np.clip(adjacency_weight, 0.0, 1.0))
            metric_length = min(cfg.maximum_distance, -math.log(max(adjacency_weight, cfg.distance_floor)))
            adjacency[left, right] = adjacency[right, left] = adjacency_weight
            edges.append(RelationalEdge(
                left=left, right=right, mutual_information_bits=information,
                two_qubit_concurrence=concurrence, bell_target=target,
                bell_fidelity=fidelity, bell_witness=witness,
                witness_certifies_entanglement=bool(witness < -1.0e-9),
                information_strength=information_strength, pauli_correlations=correlations,
                adjacency_weight=adjacency_weight, metric_length=float(metric_length),
                boundary_permeability=adjacency_weight,
            ))
    degree = np.sum(adjacency, axis=1)
    if cfg.normalized_laplacian:
        inverse = np.zeros_like(degree)
        active = degree > _EPS
        inverse[active] = 1.0 / np.sqrt(degree[active])
        laplacian = np.eye(n_qubits) - inverse[:, None] * adjacency * inverse[None, :]
        laplacian[~active, :] = 0.0
        laplacian[:, ~active] = 0.0
    else:
        laplacian = np.diag(degree) - adjacency
    eigenvalues, eigenvectors = np.linalg.eigh(laplacian)
    return EmergentGeometryFrame(
        revision=int(revision), time=float(time), reduced_density_matrices=dict(reduced),
        node_entropy_bits=_readonly(node_entropy), edges=tuple(edges),
        adjacency=_readonly(adjacency), laplacian=_readonly(laplacian),
        eigenvalues=_readonly(np.maximum(eigenvalues, 0.0)), eigenvectors=_readonly(eigenvectors),
    )


def observe_statevector_relational_geometry(
    statevector: object,
    *,
    revision: int,
    time: float,
    config: EntanglementGeometryConfig | None = None,
) -> EmergentGeometryFrame:
    """Observe an arbitrary-qubit pure circuit state without materializing ``rho``.

    This is an additive circuit/statevector capability for larger experiments;
    ``observe_emergent_geometry`` remains the authoritative four-qubit density
    observer.  The returned entropies, mutual information, and Pauli values are
    exact for the supplied normalized statevector (subject to floating point
    precision).  The graph/metric fields retain their declared model status.
    """

    if int(revision) != revision or revision < 0:
        raise ValueError("revision must be a nonnegative integer.")
    if not math.isfinite(float(time)):
        raise ValueError("time must be finite.")
    vector = np.asarray(statevector, dtype=np.complex128).reshape(-1)
    n_qubits = _dimension_to_qubits(vector.size)
    if not np.all(np.isfinite(vector)) or not np.isclose(np.vdot(vector, vector).real, 1.0, atol=1.0e-9, rtol=0.0):
        raise ValueError("statevector must be finite and normalized.")
    cfg = config or EntanglementGeometryConfig()

    def reduce(keep: tuple[int, ...]) -> Array:
        retained = tuple(sorted(keep))
        rest = tuple(index for index in range(n_qubits) if index not in retained)
        tensor = vector.reshape((2,) * n_qubits)
        ordered = np.transpose(tensor, retained + rest).reshape(2 ** len(retained), -1)
        return _readonly(ordered @ ordered.conj().T, dtype=np.complex128)

    reduced: dict[tuple[int, ...], Array] = {}
    node_entropy = np.empty(n_qubits, dtype=float)
    for node in range(n_qubits):
        reduced[(node,)] = reduce((node,))
        node_entropy[node] = von_neumann_entropy(reduced[(node,)])
    adjacency = np.zeros((n_qubits, n_qubits), dtype=float)
    edges: list[RelationalEdge] = []
    terms = tuple(dict.fromkeys((*cfg.pauli_terms, "XX", "YY", "ZZ")))
    for left in range(n_qubits):
        for right in range(left + 1, n_qubits):
            pair_key = (left, right)
            pair = reduced[pair_key] = reduce(pair_key)
            information = max(0.0, node_entropy[left] + node_entropy[right] - von_neumann_entropy(pair))
            information_strength = float(np.clip(information / 2.0, 0.0, 1.0))
            correlations = tuple((term, float(np.real(np.trace(pair @ np.kron(_PAULI[term[0]], _PAULI[term[1]]))))) for term in terms)
            target, fidelity, witness = bell_witness(dict(correlations))
            concurrence = two_qubit_concurrence(pair)
            correlation_norm = float(np.mean([abs(value) for _, value in correlations]))
            weight = float(np.clip(information_strength * ((1.0 - cfg.pauli_envelope) + cfg.pauli_envelope * correlation_norm), 0.0, 1.0))
            adjacency[left, right] = adjacency[right, left] = weight
            edges.append(RelationalEdge(left, right, information, concurrence, target, fidelity, witness,
                bool(witness < -1.0e-9), information_strength, correlations, weight,
                float(min(cfg.maximum_distance, -math.log(max(weight, cfg.distance_floor)))), weight))
    degree = np.sum(adjacency, axis=1)
    if cfg.normalized_laplacian:
        inverse = np.zeros_like(degree)
        active = degree > _EPS
        inverse[active] = 1.0 / np.sqrt(degree[active])
        laplacian = np.eye(n_qubits) - inverse[:, None] * adjacency * inverse[None, :]
        laplacian[~active, :] = laplacian[:, ~active] = 0.0
    else:
        laplacian = np.diag(degree) - adjacency
    eigenvalues, eigenvectors = np.linalg.eigh(laplacian)
    return EmergentGeometryFrame(int(revision), float(time), dict(reduced), _readonly(node_entropy), tuple(edges),
        _readonly(adjacency), _readonly(laplacian), _readonly(np.maximum(eigenvalues, 0.0)), _readonly(eigenvectors),
        provenance="read_only_pure_state_relational_graph_v1")


QMW_EMERGENT_GEOMETRY_OSC_ROOT = "/qmw/emergent_geometry"
QMW_EMERGENT_GEOMETRY_OSC_SCHEMA = "qmw.emergent_geometry.osc.v1"
QMW_EMERGENT_GEOMETRY_OSC_PORT = 17874


class EmergentGeometryOSCPublisher:
    """Publish a bounded atomic observer frame; no receiver is implied."""

    def __init__(self, client: object) -> None:
        if not hasattr(client, "send_message"):
            raise ValueError("OSC client must expose send_message().")
        self.client = client

    def publish(self, frame: EmergentGeometryFrame) -> int:
        count = frame.node_entropy_bits.size
        self.client.send_message(f"{QMW_EMERGENT_GEOMETRY_OSC_ROOT}/frame/begin", [
            frame.revision, frame.time, QMW_EMERGENT_GEOMETRY_OSC_SCHEMA,
            int(count), len(frame.edges), int(frame.eigenvalues.size),
        ])
        for node, entropy in enumerate(frame.node_entropy_bits):
            self.client.send_message(f"{QMW_EMERGENT_GEOMETRY_OSC_ROOT}/node", [frame.revision, node, float(entropy)])
        for index, edge in enumerate(frame.edges):
            self.client.send_message(f"{QMW_EMERGENT_GEOMETRY_OSC_ROOT}/edge", [
                frame.revision, index, edge.left, edge.right, edge.mutual_information_bits,
                edge.two_qubit_concurrence, edge.bell_target, edge.bell_fidelity,
                edge.bell_witness, int(edge.witness_certifies_entanglement),
                edge.adjacency_weight, edge.metric_length, edge.boundary_permeability,
            ])
            for term, value in edge.pauli_correlations:
                self.client.send_message(f"{QMW_EMERGENT_GEOMETRY_OSC_ROOT}/correlation", [frame.revision, index, term, value])
        for mode, eigenvalue in enumerate(frame.eigenvalues):
            self.client.send_message(f"{QMW_EMERGENT_GEOMETRY_OSC_ROOT}/mode", [frame.revision, mode, float(eigenvalue)])
        self.client.send_message(f"{QMW_EMERGENT_GEOMETRY_OSC_ROOT}/frame/end", [frame.revision])
        return frame.revision


__all__ = [
    "EmergentGeometryFrame", "EmergentGeometryOSCPublisher", "EntanglementGeometryConfig",
    "QMW_EMERGENT_GEOMETRY_OSC_PORT", "QMW_EMERGENT_GEOMETRY_OSC_ROOT",
    "QMW_EMERGENT_GEOMETRY_OSC_SCHEMA", "RelationalEdge", "bell_witness",
    "mutual_information", "observe_emergent_geometry", "observe_statevector_relational_geometry", "pauli_pair_expectation",
    "reduced_density_matrix", "two_qubit_concurrence", "validate_density_matrix",
    "von_neumann_entropy",
]
