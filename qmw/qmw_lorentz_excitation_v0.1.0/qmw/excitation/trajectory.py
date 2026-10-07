"""Trajectory state and velocity resolution for the excitation engine."""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
from numpy.typing import ArrayLike, NDArray


def as_vector3(value: ArrayLike, *, name: str) -> NDArray[np.float64]:
    """Validate a two- or three-component vector and return a 3D copy."""

    vector = np.asarray(value, dtype=float)
    if vector.shape not in {(2,), (3,)} or not np.all(np.isfinite(vector)):
        raise ValueError(f"{name} must contain two or three finite values")
    if vector.shape == (2,):
        vector = np.append(vector, 0.0)
    return vector.copy()


@dataclass(slots=True)
class TrajectoryTracker:
    """Resolve explicit velocity or estimate it from successive positions."""

    previous_position: NDArray[np.float64] | None = field(default=None, init=False)

    def resolve_velocity(
        self,
        position: ArrayLike,
        velocity: ArrayLike | None,
        dt: float,
    ) -> tuple[NDArray[np.float64], str]:
        point = as_vector3(position, name="position")
        if not np.isfinite(dt) or dt <= 0.0:
            raise ValueError("dt must be finite and greater than zero")

        if velocity is not None:
            resolved = as_vector3(velocity, name="velocity")
            source = "provided"
        elif self.previous_position is None:
            resolved = np.zeros(3, dtype=float)
            source = "initial_zero"
        else:
            resolved = (point - self.previous_position) / float(dt)
            source = "estimated"

        self.previous_position = point
        return resolved, source

    def reset(self) -> None:
        """Discard trajectory history."""

        self.previous_position = None

