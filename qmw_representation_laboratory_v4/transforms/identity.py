import numpy as np

from ..core import TransformContext, UnitaryOperator


class IdentityOperator(UnitaryOperator):
    name = "identity"
    description = "Computational representation; the unchanged reference state."

    def unitary(self, dimension: int, context: TransformContext = None) -> np.ndarray:
        if dimension <= 0:
            raise ValueError("dimension must be positive")
        return np.eye(dimension, dtype=complex)
