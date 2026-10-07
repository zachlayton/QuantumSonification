"""Named immutable frames crossing observer boundaries."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

RealArray = NDArray[np.float64]


def _readonly(value: RealArray, shape: tuple[int, ...] | None = None) -> RealArray:
    array = np.asarray(value, dtype=np.float64).copy()
    if shape is not None and array.shape != shape:
        raise ValueError(f"expected shape {shape}, got {array.shape}")
    if not np.all(np.isfinite(array)):
        raise ValueError("frame arrays must be finite")
    array.setflags(write=False)
    return array


@dataclass(frozen=True)
class MetricFieldFrame:
    time: float
    density: RealArray
    potential: RealArray
    sigma: RealArray
    lapse: RealArray
    metric: RealArray
    inverse_metric: RealArray
    determinant: RealArray
    sqrt_g: RealArray
    inverse_metric_factor: RealArray
    grad_potential: RealArray
    grad_sigma: RealArray
    potential_laplacian: RealArray
    hessian: RealArray
    christoffel: RealArray
    curvature: RealArray
    current: RealArray
    flow_velocity: RealArray
    vorticity: RealArray

    def __post_init__(self) -> None:
        if not np.isfinite(self.time):
            raise ValueError("frame time must be finite")
        shape = np.asarray(self.density).shape
        if len(shape) != 2:
            raise ValueError("density must be two-dimensional")
        for name in ("density", "potential", "sigma", "lapse", "determinant",
                     "sqrt_g", "inverse_metric_factor", "potential_laplacian",
                     "curvature", "vorticity"):
            object.__setattr__(self, name, _readonly(getattr(self, name), shape))
        for name in ("grad_potential", "grad_sigma", "current", "flow_velocity"):
            object.__setattr__(self, name, _readonly(getattr(self, name), (2, *shape)))
        for name, tensor_shape in (
            ("metric", (2, 2, *shape)),
            ("inverse_metric", (2, 2, *shape)),
            ("hessian", (2, 2, *shape)),
            ("christoffel", (2, 2, 2, *shape)),
        ):
            object.__setattr__(self, name, _readonly(getattr(self, name), tensor_shape))
        if (np.min(self.density) < 0.0 or np.min(self.sqrt_g) <= 0.0
                or np.min(self.lapse) <= 0.0 or np.min(self.determinant) <= 0.0):
            raise ValueError("density must be nonnegative and metric/lapse positive")
        if not np.allclose(self.metric, np.swapaxes(self.metric, 0, 1), atol=1e-9):
            raise ValueError("metric must be symmetric")
        point_metrics = np.moveaxis(self.metric, (0, 1), (-2, -1))
        if np.min(np.linalg.eigvalsh(point_metrics)) <= 0.0:
            raise ValueError("metric must be positive definite")
        identity = np.einsum("ijyx,jkyx->ikyx", self.metric, self.inverse_metric)
        expected = np.zeros_like(identity)
        expected[0, 0] = expected[1, 1] = 1.0
        if not np.allclose(identity, expected, atol=1e-9):
            raise ValueError("metric and inverse_metric are inconsistent")
        if not np.allclose(self.determinant, self.sqrt_g**2, atol=1e-9):
            raise ValueError("determinant and sqrt_g are inconsistent")
        if not np.allclose(self.determinant, np.linalg.det(point_metrics), atol=1e-9):
            raise ValueError("determinant does not match metric tensor")


@dataclass(frozen=True)
class CurvedModeFrame:
    time: float
    eigenvalues: RealArray
    frequencies: RealArray
    modes: RealArray
    damping: RealArray
    gains: RealArray
    basis_derivative_overlap: RealArray
    metric_rate_overlap: RealArray
    intermodal_connection: RealArray

    def __post_init__(self) -> None:
        if not np.isfinite(self.time):
            raise ValueError("mode time must be finite")
        count = np.asarray(self.eigenvalues).size
        object.__setattr__(self, "eigenvalues", _readonly(self.eigenvalues, (count,)))
        object.__setattr__(self, "frequencies", _readonly(self.frequencies, (count,)))
        object.__setattr__(self, "damping", _readonly(self.damping, (count,)))
        object.__setattr__(self, "gains", _readonly(self.gains, (count,)))
        for name in (
            "basis_derivative_overlap", "metric_rate_overlap", "intermodal_connection"
        ):
            object.__setattr__(self, name, _readonly(getattr(self, name), (count, count)))
        if not np.allclose(self.metric_rate_overlap, self.metric_rate_overlap.T, atol=1e-9):
            raise ValueError("metric_rate_overlap must be symmetric")
        if not np.allclose(
            self.intermodal_connection, -self.intermodal_connection.T, atol=1e-9
        ):
            raise ValueError("intermodal_connection must be antisymmetric")
        modes = np.asarray(self.modes)
        if modes.ndim != 3 or modes.shape[0] != count:
            raise ValueError("modes must have shape (mode_count, ny, nx)")
        object.__setattr__(self, "modes", _readonly(modes))
        if np.min(self.eigenvalues) < 0.0 or np.min(self.frequencies) < 0.0:
            raise ValueError("eigenvalues and frequencies must be nonnegative")

    @property
    def intermodal_coupling(self) -> RealArray:
        """Backward-compatible alias for the metric-compatible connection."""
        return self.intermodal_connection


@dataclass(frozen=True)
class TrajectoryFrame:
    time: float
    position: RealArray
    velocity: RealArray
    force: RealArray
    kinetic_energy: float
    potential_energy: float
    work_rate: float

    def __post_init__(self) -> None:
        if not np.isfinite(self.time):
            raise ValueError("trajectory time must be finite")
        for name in ("position", "velocity", "force"):
            object.__setattr__(self, name, _readonly(getattr(self, name), (2,)))
        energies = (self.kinetic_energy, self.potential_energy, self.work_rate)
        if not all(np.isfinite(value) for value in energies):
            raise ValueError("trajectory energies and work rate must be finite")


@dataclass(frozen=True)
class MetricShaderFrame:
    """Complete render payload sampled from the same numerical coordinates."""

    revision: int
    source_revision: int
    time: float
    density: RealArray
    potential: RealArray
    sigma: RealArray
    lapse: RealArray
    metric: RealArray
    inverse_metric: RealArray
    determinant: RealArray
    grad_potential: RealArray
    hessian: RealArray
    curvature: RealArray
    potential_laplacian: RealArray
    probability_current: RealArray
    phase_connection: RealArray
    vorticity: RealArray
    mode_shapes: RealArray
    trajectory_positions: RealArray
    model_label: str

    def __post_init__(self) -> None:
        if self.revision < 0 or self.source_revision < 0 or not np.isfinite(self.time):
            raise ValueError("shader revisions/time are invalid")
        if not self.model_label.strip():
            raise ValueError("model_label must be nonempty")
        shape = np.asarray(self.density).shape
        if len(shape) != 2:
            raise ValueError("shader density must be two-dimensional")
        for name in (
            "density", "potential", "sigma", "lapse", "curvature",
            "determinant", "potential_laplacian", "vorticity",
        ):
            object.__setattr__(self, name, _readonly(getattr(self, name), shape))
        for name in ("grad_potential", "probability_current", "phase_connection"):
            object.__setattr__(self, name, _readonly(getattr(self, name), (2, *shape)))
        for name in ("metric", "inverse_metric", "hessian"):
            object.__setattr__(self, name, _readonly(getattr(self, name), (2, 2, *shape)))
        modes = np.asarray(self.mode_shapes)
        if modes.ndim != 3 or modes.shape[1:] != shape:
            raise ValueError("mode_shapes must have shape (count, ny, nx)")
        object.__setattr__(self, "mode_shapes", _readonly(modes))
        trajectory = np.asarray(self.trajectory_positions)
        if trajectory.ndim != 2 or trajectory.shape[1] != 2:
            raise ValueError("trajectory_positions must have shape (count, 2)")
        object.__setattr__(self, "trajectory_positions", _readonly(trajectory))


@dataclass(frozen=True)
class QMWMetricFrame:
    """Revision-locked aggregate shared by analysis, sound, and rendering."""

    revision: int
    source_revision: int
    time: float
    field: MetricFieldFrame
    modes: CurvedModeFrame
    trajectory: TrajectoryFrame | None
    shader: MetricShaderFrame
    projection_basis: str
    potential_model: str
    metric_model: str
    topography_mode: str
    provenance: str = "qmw_metric.effective_metric.v1"

    def __post_init__(self) -> None:
        if self.revision < 0 or self.source_revision < 0:
            raise ValueError("revisions must be nonnegative")
        for name in (
            "projection_basis", "potential_model", "metric_model",
            "topography_mode", "provenance",
        ):
            if not getattr(self, name).strip():
                raise ValueError(f"{name} must be nonempty")
        if self.shader.revision != self.revision:
            raise ValueError("shader revision is not synchronized")
        if self.shader.source_revision != self.source_revision:
            raise ValueError("shader source revision is not synchronized")
        if not np.isclose(self.shader.time, self.time):
            raise ValueError("shader time is not synchronized")
        if self.field.time > self.time or self.modes.time > self.time:
            raise ValueError("field or mode frame comes from the future")
        if self.trajectory is not None and not np.isclose(self.trajectory.time, self.time):
            raise ValueError("trajectory time is not synchronized")
