"""Jones coherency matrix and its exact qubit/Pauli correspondence."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .jones import JonesState
from .stokes import StokesParameters


@dataclass(frozen=True, slots=True)
class PolarizationDensityMatrix:
    """Trace-one coherency matrix in the ordered ``(|x>, |y>)`` basis.

    Because Poincare axes are ordered ``(S1,S2,S3)`` while standard qubit
    axes are ``(sigma_x,sigma_y,sigma_z)``, the exact relation is

    ``(<sigma_x>, <sigma_y>, <sigma_z>) = (S2, -S3, S1) / S0``.

    This coordinate permutation is intentional; an axis-for-axis
    ``(S1,S2,S3)`` Pauli assignment would not equal ``|J><J|``.
    """

    matrix: np.ndarray
    pauli_expectations: tuple[float, float, float]
    purity: float

    @classmethod
    def from_jones(cls, jones: JonesState) -> "PolarizationDensityMatrix":
        vector = jones.vector(normalized=True)
        matrix = np.outer(vector, vector.conjugate())
        matrix.setflags(write=False)
        stokes = StokesParameters.from_jones(jones)
        expectations = (
            stokes.s2 / stokes.s0,
            -stokes.s3 / stokes.s0,
            stokes.s1 / stokes.s0,
        )
        purity = float(np.trace(matrix @ matrix).real)
        return cls(matrix, expectations, purity)


__all__ = ["PolarizationDensityMatrix"]
