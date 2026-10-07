from typing import Any

import numpy as np

from ..core import TransformContext, UnitaryOperator


class QFTOperator(UnitaryOperator):
    name = "qft"
    description = "Quantum Fourier representation over the complete Hilbert space."

    def __init__(self, *, inverse: bool = False) -> None:
        self.inverse = bool(inverse)
        if self.inverse:
            self.name = "inverse_qft"
            self.description = "Inverse quantum Fourier representation."

    def unitary(self, dimension: int, context: TransformContext = None) -> np.ndarray:
        if dimension <= 0 or dimension & (dimension - 1):
            raise ValueError("qft requires a power-of-two Hilbert dimension")
        indices = np.arange(dimension, dtype=float)
        sign = -1.0 if self.inverse else 1.0
        return np.exp(
            sign * 2j * np.pi * np.outer(indices, indices) / dimension
        ) / np.sqrt(dimension)

    def metadata(
        self, dimension: int, context: TransformContext = None
    ) -> dict[str, Any]:
        metadata = super().metadata(dimension, context)
        metadata["inverse"] = self.inverse
        return metadata
