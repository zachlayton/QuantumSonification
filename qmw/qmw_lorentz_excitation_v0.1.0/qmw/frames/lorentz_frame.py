"""Output frame for one Lorentz excitation-engine evaluation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
from numpy.typing import NDArray


@dataclass(frozen=True, slots=True)
class LorentzFrame:
    """Standardized, synthesis-independent QMW excitation frame.

    ``force_derivative`` is the signed time derivative of force magnitude. The
    full vector and its unit direction remain available separately.
    """

    position: NDArray[np.float64]
    velocity: NDArray[np.float64]
    electric_field: NDArray[np.float64]
    magnetic_field: NDArray[np.float64]
    force_vector: NDArray[np.float64]
    force_magnitude: float
    force_derivative: float
    excitation_position: NDArray[np.float64]
    diagnostics: dict[str, Any]

    frame_type: str = "qmw.lorentz_excitation"
    schema_version: str = "1.0"

    @property
    def force_direction(self) -> NDArray[np.float64]:
        """Unit direction of force, or the zero vector at zero magnitude."""

        if self.force_magnitude == 0.0:
            return np.zeros(3, dtype=float)
        return self.force_vector / self.force_magnitude

    def to_dict(self) -> dict[str, Any]:
        """Return a transport-friendly representation of the QMW frame."""

        return {
            "frame_type": self.frame_type,
            "schema_version": self.schema_version,
            "position": self.position.tolist(),
            "velocity": self.velocity.tolist(),
            "electric_field": self.electric_field.tolist(),
            "magnetic_field": self.magnetic_field.tolist(),
            "force_vector": self.force_vector.tolist(),
            "force_magnitude": self.force_magnitude,
            "force_direction": self.force_direction.tolist(),
            "force_derivative": self.force_derivative,
            "excitation_position": self.excitation_position.tolist(),
            "diagnostics": dict(self.diagnostics),
        }
