"""Lorentz-force-inspired excitation physics for QMW."""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
from numpy.typing import ArrayLike, NDArray

from qmw.excitation.effective_fields import EffectiveFieldConfig, EffectiveFields
from qmw.excitation.trajectory import TrajectoryTracker, as_vector3
from qmw.fields import QuantumMatrixField
from qmw.frames import LorentzFrame


@dataclass(slots=True)
class LorentzExcitationEngine:
    """Evaluate ``q(E + v x B)`` over a matrix-derived effective field.

    This class owns only force dynamics and frame construction. Matrix feature
    extraction is delegated to :class:`EffectiveFields`; synthesis mappings
    intentionally do not appear in this module.
    """

    charge: float = 1.0
    field_config: EffectiveFieldConfig = field(default_factory=EffectiveFieldConfig)
    trajectory: TrajectoryTracker = field(default_factory=TrajectoryTracker)
    _previous_force: NDArray[np.float64] | None = field(default=None, init=False)

    def __post_init__(self) -> None:
        if not np.isfinite(self.charge):
            raise ValueError("charge must be finite")

    def compute(
        self,
        *,
        matrix_field: QuantumMatrixField,
        position: ArrayLike,
        velocity: ArrayLike | None,
        dt: float,
    ) -> LorentzFrame:
        """Compute one force frame at ``position``.

        ``velocity`` may be supplied directly. When it is ``None``, velocity is
        estimated from the current and previous positions; the first estimate
        is zero because no earlier sample exists.
        """

        if not isinstance(matrix_field, QuantumMatrixField):
            raise TypeError("matrix_field must be a QuantumMatrixField")
        point = as_vector3(position, name="position")
        resolved_velocity, velocity_source = self.trajectory.resolve_velocity(
            point, velocity, dt
        )
        effective_fields = EffectiveFields.from_matrix(matrix_field, self.field_config)
        electric, magnetic = effective_fields.sample(matrix_field, point)

        force = self.charge * (
            electric + np.cross(resolved_velocity, magnetic)
        )
        force_magnitude = float(np.linalg.norm(force))
        if self._previous_force is None:
            force_derivative = 0.0
        else:
            previous_magnitude = float(np.linalg.norm(self._previous_force))
            force_derivative = (force_magnitude - previous_magnitude) / float(dt)
        self._previous_force = force.copy()

        _, _, in_bounds = matrix_field.grid_indices(point, clip=True)
        excitation_position = matrix_field.clipped_position(point)
        diagnostics = {
            "charge": float(self.charge),
            "dt": float(dt),
            "in_bounds": in_bounds,
            "position_clipped": not in_bounds,
            "velocity_source": velocity_source,
            "potential_scale": float(self.field_config.potential_scale),
            "magnetic_scale": float(self.field_config.magnetic_scale),
            "magnetic_mode": (
                "constant_override"
                if self.field_config.constant_magnetic_field is not None
                else self.field_config.magnetic_mode
            ),
            "electric_norm": float(np.linalg.norm(electric)),
            "magnetic_norm": float(np.linalg.norm(magnetic)),
            "finite": bool(
                np.all(np.isfinite(electric))
                and np.all(np.isfinite(magnetic))
                and np.all(np.isfinite(force))
            ),
        }

        return LorentzFrame(
            position=point,
            velocity=resolved_velocity,
            electric_field=electric,
            magnetic_field=magnetic,
            force_vector=force,
            force_magnitude=force_magnitude,
            force_derivative=float(force_derivative),
            excitation_position=excitation_position,
            diagnostics=diagnostics,
        )

    def reset(self) -> None:
        """Reset derivative and trajectory history between independent runs."""

        self._previous_force = None
        self.trajectory.reset()

