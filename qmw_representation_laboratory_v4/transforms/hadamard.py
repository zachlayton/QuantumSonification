import numpy as np

from ..core import TransformContext, UnitaryOperator


class HadamardOperator(UnitaryOperator):
    name = "hadamard"
    description = "Tensor-product Hadamard representation over every qubit."

    def unitary(self, dimension: int, context: TransformContext = None) -> np.ndarray:
        if dimension <= 0 or dimension & (dimension - 1):
            raise ValueError(
                "hadamard requires a power-of-two Hilbert dimension"
            )
        single = np.array([[1, 1], [1, -1]], dtype=complex) / np.sqrt(2.0)
        result = np.array([[1.0]], dtype=complex)
        for _qubit in range(dimension.bit_length() - 1):
            result = np.kron(result, single)
        return result
