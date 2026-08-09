"""Geometry and modal-continuity foundations for QuantumSonification."""

from .modal_subspace_tracker_v1 import (
    ModalSubspaceTracker,
    ModalTrackingConfig,
    TrackedModalCluster,
    TrackedModalFrame,
    generalized_eigen_residuals,
    mass_orthonormality_error,
)

__all__ = [
    "ModalSubspaceTracker",
    "ModalTrackingConfig",
    "TrackedModalCluster",
    "TrackedModalFrame",
    "generalized_eigen_residuals",
    "mass_orthonormality_error",
]
