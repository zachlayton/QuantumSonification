"""Extract effective physical-model fields from a complex QMW matrix."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import numpy as np
from numpy.typing import ArrayLike, NDArray

from qmw.fields import QuantumMatrixField


MagneticMode = Literal["circulation", "phase"]


def _vector3(value: ArrayLike, *, name: str) -> NDArray[np.float64]:
    vector = np.asarray(value, dtype=float)
    if vector.shape != (3,) or not np.all(np.isfinite(vector)):
        raise ValueError(f"{name} must contain exactly three finite values")
    return vector.copy()


def _wrap_phase(angle: NDArray[np.float64]) -> NDArray[np.float64]:
    return (angle + np.pi) % (2.0 * np.pi) - np.pi


@dataclass(frozen=True, slots=True)
class EffectiveFieldConfig:
    """Controls matrix-to-field extraction without defining musical mappings."""

    potential_scale: float = 1.0
    magnetic_scale: float = 1.0
    magnetic_mode: MagneticMode = "circulation"
    constant_magnetic_field: NDArray[np.float64] | None = None

    def __post_init__(self) -> None:
        if not np.isfinite(self.potential_scale):
            raise ValueError("potential_scale must be finite")
        if not np.isfinite(self.magnetic_scale):
            raise ValueError("magnetic_scale must be finite")
        if self.magnetic_mode not in {"circulation", "phase"}:
            raise ValueError("magnetic_mode must be 'circulation' or 'phase'")
        if self.constant_magnetic_field is not None:
            object.__setattr__(
                self,
                "constant_magnetic_field",
                _vector3(self.constant_magnetic_field, name="constant_magnetic_field"),
            )


@dataclass(frozen=True, slots=True)
class EffectiveFields:
    """Potential plus electric and magnetic-like grids derived from one matrix."""

    potential: NDArray[np.float64]
    electric: NDArray[np.float64]
    magnetic: NDArray[np.float64]

    @classmethod
    def from_matrix(
        cls,
        matrix_field: QuantumMatrixField,
        config: EffectiveFieldConfig | None = None,
    ) -> "EffectiveFields":
        config = config or EffectiveFieldConfig()
        potential = config.potential_scale * matrix_field.magnitude
        dx, dy = matrix_field.spacing
        d_v_dy, d_v_dx = np.gradient(potential, dy, dx, edge_order=2)
        electric = np.stack((-d_v_dx, -d_v_dy, np.zeros_like(potential)), axis=-1)

        if config.constant_magnetic_field is not None:
            magnetic = np.broadcast_to(
                config.constant_magnetic_field, potential.shape + (3,)
            ).copy()
        elif config.magnetic_mode == "phase":
            magnetic = cls._phase_field(matrix_field.phase, config.magnetic_scale)
        else:
            magnetic = cls._circulation_field(
                matrix_field.phase, config.magnetic_scale
            )
        return cls(potential=potential, electric=electric, magnetic=magnetic)

    @staticmethod
    def _phase_field(
        phase: NDArray[np.float64], scale: float
    ) -> NDArray[np.float64]:
        """Interpret local wrapped phase directly as perpendicular field."""

        zeros = np.zeros_like(phase)
        return np.stack((zeros, zeros, scale * phase / np.pi), axis=-1)

    @staticmethod
    def _circulation_field(
        phase: NDArray[np.float64], scale: float
    ) -> NDArray[np.float64]:
        """Convert wrapped plaquette phase winding into a z-directed field.

        Each plaquette accumulates the wrapped phase increments around its
        counter-clockwise boundary. The resulting winding number is averaged
        onto the four adjacent matrix nodes. Smooth phase ramps therefore
        produce zero field, while phase vortices produce localized circulation.
        """

        p00 = phase[:-1, :-1]
        p10 = phase[:-1, 1:]
        p11 = phase[1:, 1:]
        p01 = phase[1:, :-1]
        circulation = (
            _wrap_phase(p10 - p00)
            + _wrap_phase(p11 - p10)
            + _wrap_phase(p01 - p11)
            + _wrap_phase(p00 - p01)
        ) / (2.0 * np.pi)

        node_sum = np.zeros_like(phase)
        node_count = np.zeros_like(phase)
        node_sum[:-1, :-1] += circulation
        node_sum[:-1, 1:] += circulation
        node_sum[1:, 1:] += circulation
        node_sum[1:, :-1] += circulation
        node_count[:-1, :-1] += 1.0
        node_count[:-1, 1:] += 1.0
        node_count[1:, 1:] += 1.0
        node_count[1:, :-1] += 1.0
        b_z = scale * np.divide(
            node_sum, node_count, out=np.zeros_like(node_sum), where=node_count > 0
        )
        zeros = np.zeros_like(phase)
        return np.stack((zeros, zeros, b_z), axis=-1)

    def sample(
        self, matrix_field: QuantumMatrixField, position: ArrayLike
    ) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
        """Sample ``(electric, magnetic)`` at one physical position."""

        electric = matrix_field.sample(self.electric, position)
        magnetic = matrix_field.sample(self.magnetic, position)
        return np.asarray(electric, dtype=float), np.asarray(magnetic, dtype=float)

