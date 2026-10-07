"""Offline, reference-quality four-qubit XY transport for QMW.

The package is deliberately downstream-safe: it computes an inspectable
trajectory and can publish an explicitly musical granular-control projection,
but it never owns or mutates a live QMW density-matrix runtime.
"""

from .granular import GrainControlTrajectory, GrainMapping, project_grains
from .parity import XYParityReport, compare_trajectories, run_xy_qutip_parity
from .xy import FourQubitXYModel, QuantumTrajectory, run_xy_trajectory

__all__ = [
    "FourQubitXYModel",
    "GrainControlTrajectory",
    "GrainMapping",
    "QuantumTrajectory",
    "XYParityReport",
    "compare_trajectories",
    "project_grains",
    "run_xy_trajectory",
    "run_xy_qutip_parity",
]
