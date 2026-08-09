"""Mass-aware tracking of modal subspaces through changing geometry.

Individual eigenvectors are not stable objects at repeated or nearly repeated
eigenvalues: an eigensolver may return any orthonormal basis for the same
invariant subspace.  This tracker therefore gives persistent identities to
clusters, measures their principal angles, and uses an orthogonal/unitary
Procrustes alignment to provide a continuous gauge basis inside each matched
cluster.

``raw_eigenvectors`` remain the actual eigenvectors returned by the solver.
``aligned_basis`` is the continuity-preserving basis.  Inside a non-exactly
degenerate cluster, its columns may be mixtures of raw eigenvectors and must be
treated as a block basis rather than as independent scalar modes.

The update metric is the *new* mass matrix.  When meshes differ, callers must
provide a transfer matrix T with shape ``(new_vertices, old_vertices)``.

Dependencies
------------
numpy
scipy
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Sequence

import numpy as np
from scipy import sparse
from scipy.optimize import linear_sum_assignment


Array = np.ndarray
MassLike = Array | sparse.spmatrix | None


@dataclass(frozen=True)
class ModalTrackingConfig:
    relative_gap_tolerance: float = 2.0e-3
    absolute_gap_tolerance: float = 1.0e-8
    eigenvalue_floor: float = 1.0e-12
    subspace_score_weight: float = 0.90
    eigenvalue_similarity_scale: float = 0.25
    minimum_cluster_similarity: float = 0.20
    require_transfer_on_topology_change: bool = True
    orthonormality_tolerance: float = 2.0e-6

    def __post_init__(self) -> None:
        if self.relative_gap_tolerance < 0.0 or self.absolute_gap_tolerance < 0.0:
            raise ValueError("gap tolerances must be non-negative")
        if not 0.0 <= self.subspace_score_weight <= 1.0:
            raise ValueError("subspace_score_weight must lie in [0, 1]")
        if self.eigenvalue_similarity_scale <= 0.0:
            raise ValueError("eigenvalue_similarity_scale must be positive")
        if not 0.0 <= self.minimum_cluster_similarity <= 1.0:
            raise ValueError("minimum_cluster_similarity must lie in [0, 1]")


@dataclass(frozen=True)
class TrackedModalCluster:
    cluster_id: int
    basis_indices: tuple[int, ...]
    stable_mode_ids: tuple[int, ...]
    eigenvalue_min: float
    eigenvalue_max: float
    eigenvalue_centroid: float
    principal_angles_radians: Array
    overlap_confidence: float
    assignment_score: float
    matched_previous_cluster_id: int | None
    is_degenerate: bool

    @property
    def dimension(self) -> int:
        return len(self.basis_indices)


@dataclass
class TrackedModalFrame:
    eigenvalues: Array
    raw_eigenvectors: Array
    aligned_basis: Array
    mass: MassLike
    mode_stable_ids: tuple[int, ...]
    cluster_ids_by_mode: tuple[int, ...]
    clusters: tuple[TrackedModalCluster, ...]
    topology_id: str
    revision: int
    residuals: Array | None = None
    retired_mode_ids: tuple[int, ...] = ()
    retired_cluster_ids: tuple[int, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)

    def cluster(self, cluster_id: int) -> TrackedModalCluster:
        for cluster in self.clusters:
            if cluster.cluster_id == cluster_id:
                return cluster
        raise KeyError(cluster_id)


def _as_eigenpairs(
    eigenvalues: Array,
    eigenvectors: Array,
) -> tuple[Array, Array, Array]:
    values = np.asarray(eigenvalues, dtype=np.float64).reshape(-1)
    vectors = np.asarray(eigenvectors, dtype=np.complex128)
    if vectors.ndim != 2:
        raise ValueError("eigenvectors must have shape (vertices, modes)")
    if vectors.shape[1] != len(values):
        raise ValueError("eigenvalue/eigenvector count mismatch")
    if len(values) < 1:
        raise ValueError("at least one eigenpair is required")
    if not np.all(np.isfinite(values)) or not np.all(np.isfinite(vectors)):
        raise ValueError("eigenpairs must be finite")
    order = np.argsort(values, kind="stable")
    return values[order], vectors[:, order], order


def _validate_mass(mass: MassLike, dimension: int) -> MassLike:
    if mass is None:
        return None
    if sparse.issparse(mass):
        matrix = mass.tocsr().astype(np.complex128)
        if matrix.shape != (dimension, dimension):
            raise ValueError("sparse mass matrix has the wrong shape")
        hermitian_error = sparse.linalg.norm(matrix - matrix.getH())
        if hermitian_error > 1e-8:
            raise ValueError("mass matrix must be Hermitian")
        if matrix.data.size and not np.all(np.isfinite(matrix.data)):
            raise ValueError("mass matrix must contain only finite values")
        if dimension <= 2:
            smallest = float(np.min(np.linalg.eigvalsh(matrix.toarray())).real)
        else:
            smallest = float(
                sparse.linalg.eigsh(
                    matrix,
                    k=1,
                    which="SA",
                    return_eigenvectors=False,
                )[0].real
            )
        if smallest <= 0.0:
            raise ValueError("mass matrix must be positive definite")
        return matrix

    array = np.asarray(mass)
    if array.ndim == 1:
        diagonal = np.asarray(array, dtype=np.float64).reshape(-1)
        if len(diagonal) != dimension:
            raise ValueError("mass diagonal has the wrong length")
        if np.any(diagonal <= 0.0):
            raise ValueError("mass diagonal must be strictly positive")
        return diagonal
    matrix = np.asarray(array, dtype=np.complex128)
    if matrix.shape != (dimension, dimension):
        raise ValueError("mass matrix has the wrong shape")
    if np.max(np.abs(matrix - matrix.conj().T)) > 1e-8:
        raise ValueError("mass matrix must be Hermitian")
    if float(np.min(np.linalg.eigvalsh(matrix)).real) <= 0.0:
        raise ValueError("mass matrix must be positive definite")
    return matrix


def _mass_apply(mass: MassLike, vectors: Array) -> Array:
    if mass is None:
        return vectors
    if sparse.issparse(mass):
        return np.asarray(mass @ vectors)
    array = np.asarray(mass)
    if array.ndim == 1:
        if vectors.ndim == 1:
            return array * vectors
        return array[:, None] * vectors
    return array @ vectors


def _metric_overlap(left: Array, right: Array, mass: MassLike) -> Array:
    return left.conj().T @ _mass_apply(mass, right)


def _orthonormalize(vectors: Array, mass: MassLike) -> Array:
    """Return an M-orthonormal basis spanning the input columns."""

    gram = _metric_overlap(vectors, vectors, mass)
    gram = 0.5 * (gram + gram.conj().T)
    values, rotations = np.linalg.eigh(gram)
    threshold = max(1e-13, 1e-11 * float(np.max(np.abs(values))))
    if np.any(values <= threshold):
        raise ValueError("modal basis is rank deficient in the mass metric")
    inverse_sqrt = rotations @ np.diag(1.0 / np.sqrt(values)) @ rotations.conj().T
    return vectors @ inverse_sqrt


def _normalize_columns(vectors: Array, mass: MassLike) -> Array:
    result = np.asarray(vectors, dtype=np.complex128).copy()
    for index in range(result.shape[1]):
        norm_squared = complex(
            np.vdot(result[:, index], _mass_apply(mass, result[:, index]))
        )
        if abs(norm_squared.imag) > 1e-9 or norm_squared.real <= 1e-14:
            raise ValueError("modal vector has a non-positive mass norm")
        result[:, index] /= np.sqrt(norm_squared.real)
    return result


def _orthonormalize_by_groups(
    vectors: Array,
    mass: MassLike,
    groups: Sequence[Sequence[int]],
    *,
    require_global_orthogonal: bool = True,
) -> Array:
    """Orthonormalize only inside declared invariant subspaces.

    Mixing distinct eigenspaces merely to repair a slightly imperfect input
    Gram matrix would destroy their spectral meaning.  Cross-cluster overlap
    is therefore checked and reported as an input error instead.
    """

    result = np.asarray(vectors, dtype=np.complex128).copy()
    for group in groups:
        indices = np.asarray(group, dtype=np.int64)
        result[:, indices] = _orthonormalize(result[:, indices], mass)
    error = mass_orthonormality_error(result, mass)
    if require_global_orthogonal and error > 2.0e-6:
        raise ValueError(
            "modal vectors from distinct eigenvalue clusters are not "
            f"M-orthogonal; maximum Gram error={error:.3e}"
        )
    return result


def mass_orthonormality_error(vectors: Array, mass: MassLike = None) -> float:
    basis = np.asarray(vectors, dtype=np.complex128)
    gram = _metric_overlap(basis, basis, mass)
    return float(np.max(np.abs(gram - np.eye(basis.shape[1]))))


def generalized_eigen_residuals(
    operator: Array | sparse.spmatrix,
    mass: MassLike,
    eigenvalues: Array,
    eigenvectors: Array,
    *,
    epsilon: float = 1e-15,
) -> Array:
    """Return scale-independent residuals for ``K phi = lambda M phi``."""

    values = np.asarray(eigenvalues, dtype=np.float64).reshape(-1)
    vectors = np.asarray(eigenvectors, dtype=np.complex128)
    if vectors.shape[1] != len(values):
        raise ValueError("eigenvalue/eigenvector count mismatch")
    k_phi = np.asarray(operator @ vectors)
    m_phi = _mass_apply(mass, vectors)
    residual = k_phi - m_phi * values[None, :]
    numerator = np.linalg.norm(residual, axis=0)
    denominator = (
        np.linalg.norm(k_phi, axis=0)
        + np.abs(values) * np.linalg.norm(m_phi, axis=0)
    )
    return numerator / np.maximum(denominator, epsilon)


def _cluster_indices(values: Array, config: ModalTrackingConfig) -> list[tuple[int, ...]]:
    groups: list[list[int]] = [[0]]
    for index in range(1, len(values)):
        previous = float(values[index - 1])
        current = float(values[index])
        scale = max(abs(previous), abs(current), config.eigenvalue_floor)
        threshold = config.absolute_gap_tolerance + config.relative_gap_tolerance * scale
        if abs(current - previous) <= threshold:
            groups[-1].append(index)
        else:
            groups.append([index])
    return [tuple(group) for group in groups]


def _centroid(values: Array, indices: Sequence[int]) -> float:
    return float(np.mean(values[np.asarray(indices, dtype=np.int64)]))


def _subspace_comparison(
    old_basis: Array,
    new_basis: Array,
    mass: MassLike,
) -> tuple[float, Array, Array]:
    cross = _metric_overlap(old_basis, new_basis, mass)
    singular_values = np.linalg.svd(cross, compute_uv=False)
    singular_values = np.clip(np.real(singular_values), 0.0, 1.0)
    angles = np.arccos(singular_values)
    similarity = float(
        np.sum(singular_values**2) / max(old_basis.shape[1], new_basis.shape[1])
    )
    return similarity, angles, singular_values


def _phase_align(reference: Array, candidate: Array, mass: MassLike) -> Array:
    overlap = complex(np.vdot(reference, _mass_apply(mass, candidate)))
    if abs(overlap) <= 1e-14:
        return candidate
    return candidate * np.exp(-1j * np.angle(overlap))


class ModalSubspaceTracker:
    """Track stable modal and invariant-subspace identities across frames."""

    def __init__(
        self,
        config: ModalTrackingConfig = ModalTrackingConfig(),
    ) -> None:
        self.config = config
        self.previous: TrackedModalFrame | None = None
        self._next_mode_id = 0
        self._next_cluster_id = 0

    def _new_mode_id(self) -> int:
        value = self._next_mode_id
        self._next_mode_id += 1
        return value

    def _new_cluster_id(self) -> int:
        value = self._next_cluster_id
        self._next_cluster_id += 1
        return value

    @classmethod
    def resume(
        cls,
        frame: TrackedModalFrame,
        config: ModalTrackingConfig = ModalTrackingConfig(),
    ) -> "ModalSubspaceTracker":
        """Resume tracking from a previously published frame.

        Counter values are stored in frame metadata so retired identifiers are
        never reused after asynchronous or serialized computation boundaries.
        """

        tracker = cls(config)
        tracker.previous = frame
        active_modes = tuple(frame.mode_stable_ids) + tuple(frame.retired_mode_ids)
        active_clusters = tuple(
            cluster.cluster_id for cluster in frame.clusters
        ) + tuple(frame.retired_cluster_ids)
        tracker._next_mode_id = int(
            frame.metadata.get(
                "tracker_next_mode_id",
                0 if not active_modes else max(active_modes) + 1,
            )
        )
        tracker._next_cluster_id = int(
            frame.metadata.get(
                "tracker_next_cluster_id",
                0 if not active_clusters else max(active_clusters) + 1,
            )
        )
        return tracker

    def initialize(
        self,
        eigenvalues: Array,
        eigenvectors: Array,
        *,
        mass: MassLike = None,
        topology_id: str = "default",
        residuals: Array | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> TrackedModalFrame:
        values, vectors, order = _as_eigenpairs(eigenvalues, eigenvectors)
        metric = _validate_mass(mass, vectors.shape[0])
        groups = _cluster_indices(values, self.config)
        raw_vectors = _normalize_columns(vectors, metric)
        basis = _orthonormalize_by_groups(raw_vectors, metric, groups)
        error = mass_orthonormality_error(basis, metric)
        if error > self.config.orthonormality_tolerance:
            raise ValueError(f"could not M-orthonormalize modes; error={error:.3e}")

        mode_ids = [-1] * len(values)
        cluster_ids = [-1] * len(values)
        clusters: list[TrackedModalCluster] = []
        for indices in groups:
            stable_ids = tuple(self._new_mode_id() for _ in indices)
            cluster_id = self._new_cluster_id()
            for index, stable_id in zip(indices, stable_ids):
                mode_ids[index] = stable_id
                cluster_ids[index] = cluster_id
            cluster_values = values[np.asarray(indices)]
            clusters.append(
                TrackedModalCluster(
                    cluster_id=cluster_id,
                    basis_indices=indices,
                    stable_mode_ids=stable_ids,
                    eigenvalue_min=float(np.min(cluster_values)),
                    eigenvalue_max=float(np.max(cluster_values)),
                    eigenvalue_centroid=float(np.mean(cluster_values)),
                    principal_angles_radians=np.zeros(len(indices)),
                    overlap_confidence=1.0,
                    assignment_score=1.0,
                    matched_previous_cluster_id=None,
                    is_degenerate=len(indices) > 1,
                )
            )

        residual_array = None
        if residuals is not None:
            residual_array = np.asarray(residuals, dtype=np.float64).reshape(-1)
            if len(residual_array) != len(values):
                raise ValueError("residual count must match the mode count")
            residual_array = residual_array[order]

        frame = TrackedModalFrame(
            eigenvalues=values,
            raw_eigenvectors=raw_vectors,
            aligned_basis=basis.copy(),
            mass=metric,
            mode_stable_ids=tuple(mode_ids),
            cluster_ids_by_mode=tuple(cluster_ids),
            clusters=tuple(clusters),
            topology_id=str(topology_id),
            revision=0 if self.previous is None else self.previous.revision + 1,
            residuals=residual_array,
            metadata={
                **({} if metadata is None else dict(metadata)),
                "tracker_next_mode_id": self._next_mode_id,
                "tracker_next_cluster_id": self._next_cluster_id,
            },
        )
        self.previous = frame
        return frame

    def update(
        self,
        eigenvalues: Array,
        eigenvectors: Array,
        *,
        mass: MassLike = None,
        topology_id: str = "default",
        transfer_matrix: Array | sparse.spmatrix | None = None,
        residuals: Array | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> TrackedModalFrame:
        if self.previous is None:
            return self.initialize(
                eigenvalues,
                eigenvectors,
                mass=mass,
                topology_id=topology_id,
                residuals=residuals,
                metadata=metadata,
            )

        previous = self.previous
        values, vectors, order = _as_eigenpairs(eigenvalues, eigenvectors)
        metric = _validate_mass(mass, vectors.shape[0])
        new_groups = _cluster_indices(values, self.config)
        raw_vectors = _normalize_columns(vectors, metric)
        raw_basis = _orthonormalize_by_groups(raw_vectors, metric, new_groups)
        topology_changed = str(topology_id) != previous.topology_id

        if transfer_matrix is None:
            if previous.aligned_basis.shape[0] != raw_basis.shape[0]:
                raise ValueError("a transfer matrix is required when vertex counts change")
            if topology_changed and self.config.require_transfer_on_topology_change:
                raise ValueError("a transfer matrix is required when topology_id changes")
            old_in_new_space = previous.aligned_basis.copy()
        else:
            transfer = transfer_matrix
            if transfer.shape != (raw_basis.shape[0], previous.aligned_basis.shape[0]):
                raise ValueError(
                    "transfer matrix must have shape (new_vertices, old_vertices)"
                )
            old_in_new_space = np.asarray(transfer @ previous.aligned_basis)
        old_clusters = list(previous.clusters)
        old_in_new_space = _orthonormalize_by_groups(
            old_in_new_space,
            metric,
            [cluster.basis_indices for cluster in old_clusters],
            require_global_orthogonal=False,
        )
        score_matrix = np.zeros((len(old_clusters), len(new_groups)), dtype=np.float64)

        for old_position, old_cluster in enumerate(old_clusters):
            old_indices = np.asarray(old_cluster.basis_indices, dtype=np.int64)
            old_basis = old_in_new_space[:, old_indices]
            for new_position, new_indices_tuple in enumerate(new_groups):
                new_indices = np.asarray(new_indices_tuple, dtype=np.int64)
                new_basis = raw_basis[:, new_indices]
                subspace_similarity, angles, _ = _subspace_comparison(
                    old_basis, new_basis, metric
                )
                old_center = old_cluster.eigenvalue_centroid
                new_center = _centroid(values, new_indices)
                relative_difference = abs(new_center - old_center) / max(
                    abs(new_center), abs(old_center), self.config.eigenvalue_floor
                )
                eigenvalue_similarity = np.exp(
                    -relative_difference / self.config.eigenvalue_similarity_scale
                )
                weight = self.config.subspace_score_weight
                score_matrix[old_position, new_position] = (
                    weight * subspace_similarity
                    + (1.0 - weight) * eigenvalue_similarity
                )

        matched_new_to_old: dict[int, int] = {}
        if score_matrix.size:
            old_assignment, new_assignment = linear_sum_assignment(-score_matrix)
            for old_position, new_position in zip(old_assignment, new_assignment):
                if (
                    score_matrix[old_position, new_position]
                    >= self.config.minimum_cluster_similarity
                ):
                    matched_new_to_old[int(new_position)] = int(old_position)

        aligned = raw_basis.copy()
        mode_ids = [-1] * len(values)
        cluster_ids_by_mode = [-1] * len(values)
        clusters: list[TrackedModalCluster] = []
        used_old_cluster_positions: set[int] = set()

        for new_position, indices_tuple in enumerate(new_groups):
            indices = np.asarray(indices_tuple, dtype=np.int64)
            cluster_values = values[indices]
            old_position = matched_new_to_old.get(new_position)

            if old_position is None:
                cluster_id = self._new_cluster_id()
                stable_ids = tuple(self._new_mode_id() for _ in indices_tuple)
                angles = np.array([], dtype=np.float64)
                confidence = 0.0
                assignment_score = 0.0
                matched_previous_id = None
            else:
                used_old_cluster_positions.add(old_position)
                old_cluster = old_clusters[old_position]
                cluster_id = old_cluster.cluster_id
                old_indices = np.asarray(old_cluster.basis_indices, dtype=np.int64)
                old_basis = old_in_new_space[:, old_indices]
                new_basis = raw_basis[:, indices]
                cross = _metric_overlap(old_basis, new_basis, metric)
                left, singular_values, right_h = np.linalg.svd(cross, full_matrices=False)
                singular_values = np.clip(np.real(singular_values), 0.0, 1.0)
                angles = np.arccos(singular_values)
                confidence = float(np.mean(singular_values)) if len(singular_values) else 0.0
                assignment_score = float(score_matrix[old_position, new_position])
                matched_previous_id = old_cluster.cluster_id

                if len(old_indices) == len(indices):
                    rotation = right_h.conj().T @ left.conj().T
                    aligned[:, indices] = new_basis @ rotation
                    stable_ids = old_cluster.stable_mode_ids
                else:
                    pairwise = np.abs(cross)
                    old_members, new_members = linear_sum_assignment(-pairwise)
                    assigned: dict[int, int] = {}
                    for old_member, new_member in zip(old_members, new_members):
                        stable_id = old_cluster.stable_mode_ids[int(old_member)]
                        assigned[int(new_member)] = stable_id
                        aligned[:, indices[int(new_member)]] = _phase_align(
                            old_basis[:, int(old_member)],
                            new_basis[:, int(new_member)],
                            metric,
                        )
                    stable_ids = tuple(
                        assigned[member]
                        if member in assigned
                        else self._new_mode_id()
                        for member in range(len(indices))
                    )

            for index, stable_id in zip(indices_tuple, stable_ids):
                mode_ids[index] = stable_id
                cluster_ids_by_mode[index] = cluster_id

            clusters.append(
                TrackedModalCluster(
                    cluster_id=cluster_id,
                    basis_indices=indices_tuple,
                    stable_mode_ids=stable_ids,
                    eigenvalue_min=float(np.min(cluster_values)),
                    eigenvalue_max=float(np.max(cluster_values)),
                    eigenvalue_centroid=float(np.mean(cluster_values)),
                    principal_angles_radians=angles,
                    overlap_confidence=confidence,
                    assignment_score=assignment_score,
                    matched_previous_cluster_id=matched_previous_id,
                    is_degenerate=len(indices_tuple) > 1,
                )
            )

        active_mode_ids = set(mode_ids)
        active_cluster_ids = {cluster.cluster_id for cluster in clusters}
        previous_mode_ids = set(previous.mode_stable_ids)
        previous_cluster_ids = {cluster.cluster_id for cluster in previous.clusters}

        residual_array = None
        if residuals is not None:
            residual_array = np.asarray(residuals, dtype=np.float64).reshape(-1)
            if len(residual_array) != len(values):
                raise ValueError("residual count must match the mode count")
            residual_array = residual_array[order]

        error = mass_orthonormality_error(aligned, metric)
        if error > self.config.orthonormality_tolerance:
            raise ValueError(
                f"aligned modal basis lost M-orthonormality; error={error:.3e}"
            )

        frame = TrackedModalFrame(
            eigenvalues=values,
            raw_eigenvectors=raw_vectors,
            aligned_basis=aligned,
            mass=metric,
            mode_stable_ids=tuple(mode_ids),
            cluster_ids_by_mode=tuple(cluster_ids_by_mode),
            clusters=tuple(clusters),
            topology_id=str(topology_id),
            revision=previous.revision + 1,
            residuals=residual_array,
            retired_mode_ids=tuple(sorted(previous_mode_ids - active_mode_ids)),
            retired_cluster_ids=tuple(sorted(previous_cluster_ids - active_cluster_ids)),
            metadata={
                **({} if metadata is None else dict(metadata)),
                "topology_changed": topology_changed,
                "orthonormality_error": error,
                "tracker_next_mode_id": self._next_mode_id,
                "tracker_next_cluster_id": self._next_cluster_id,
            },
        )
        self.previous = frame
        return frame


__all__ = [
    "ModalSubspaceTracker",
    "ModalTrackingConfig",
    "TrackedModalCluster",
    "TrackedModalFrame",
    "generalized_eigen_residuals",
    "mass_orthonormality_error",
]
