"""Projective measurement contracts for finite-dimensional QMW worlds."""

from .basis_motion import ProjectorBasisMotion
from .engine import MeasurementFrame, ProjectiveMeasurementEngine
from .gauge_projective import GaugeProjectiveEngine, GaugeProjectiveFrame
from .projector import ProjectorBank, ProjectorSpec
from .projector_bank import (
    computational_projector_bank,
    geometry_projector_bank,
    hypercube_geometry_projector_bank,
    pauli_eigenbasis_projector_bank,
    pauli_projector_bank,
    transform_projector_bank,
)

__all__ = [
    "GaugeProjectiveEngine", "GaugeProjectiveFrame", "MeasurementFrame",
    "ProjectiveMeasurementEngine", "ProjectorBank",
    "ProjectorBasisMotion", "ProjectorSpec", "computational_projector_bank",
    "geometry_projector_bank", "hypercube_geometry_projector_bank",
    "pauli_eigenbasis_projector_bank", "pauli_projector_bank",
    "transform_projector_bank",
]
