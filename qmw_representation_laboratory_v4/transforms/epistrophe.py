"""Explicit adapter for a user-defined reversible return operator."""

from __future__ import annotations

from typing import Any

import numpy as np

from ..core import (
    TransformContext,
    UnitaryOperator,
    square_matrix,
    validate_unitary,
)


class EpistropheBasis(UnitaryOperator):
    """A mathematically honest slot for a future Epistrophē construction.

    V4 does not invent that construction. It accepts an explicitly supplied
    unitary return map, records its definition label, and applies it repeatedly.
    """

    name = "epistrophe"
    description = "User-defined reversible return/recurrence representation."

    def __init__(
        self,
        return_unitary: Any,
        *,
        returns: int = 1,
        definition: str = "user_supplied_unitary",
    ) -> None:
        matrix = square_matrix(return_unitary, name="Epistrophe return unitary")
        validate_unitary(matrix, matrix.shape[0])
        if int(returns) != returns or returns < 0:
            raise ValueError("returns must be a non-negative integer")
        self._return_unitary = np.array(matrix, copy=True)
        self.returns = int(returns)
        self.definition = str(definition)

    def unitary(self, dimension: int, context: TransformContext = None) -> np.ndarray:
        if self._return_unitary.shape != (dimension, dimension):
            raise ValueError("Epistrophe and density dimensions do not match")
        return np.linalg.matrix_power(self._return_unitary, self.returns)

    def metadata(
        self, dimension: int, context: TransformContext = None
    ) -> dict[str, Any]:
        metadata = super().metadata(dimension, context)
        metadata.update(returns=self.returns, definition=self.definition)
        return metadata
