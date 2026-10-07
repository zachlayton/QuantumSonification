"""Validated projectors and projector banks."""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Mapping, Sequence

import numpy as np


Array = np.ndarray


def _finite_square(name: str, values: object) -> Array:
    matrix = np.asarray(values, dtype=np.complex128)
    if matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1] or not np.all(np.isfinite(matrix)):
        raise ValueError(f"{name} must be a finite square matrix.")
    return np.array(matrix, copy=True)


@dataclass(frozen=True)
class ProjectorSpec:
    name: str
    matrix: Array
    family: str = "custom"
    rank: int | None = None
    metadata: Mapping[str, object] = field(default_factory=dict)
    tolerance: float = field(default=1.0e-9, repr=False, compare=False)

    def __post_init__(self) -> None:
        if not self.name or not self.family:
            raise ValueError("projector name and family must be nonempty.")
        matrix = _finite_square("projector", self.matrix)
        if self.tolerance <= 0.0:
            raise ValueError("tolerance must be positive.")
        if not np.allclose(matrix, matrix.conj().T, rtol=0.0, atol=self.tolerance):
            raise ValueError(f"projector {self.name!r} must be Hermitian.")
        if not np.allclose(matrix @ matrix, matrix, rtol=0.0, atol=self.tolerance):
            raise ValueError(f"projector {self.name!r} must be idempotent.")
        measured_rank = int(np.count_nonzero(np.linalg.eigvalsh(matrix) > 0.5))
        if self.rank is not None and int(self.rank) != measured_rank:
            raise ValueError(f"projector {self.name!r} rank does not match its matrix.")
        matrix.setflags(write=False)
        object.__setattr__(self, "matrix", matrix)
        object.__setattr__(self, "rank", measured_rank)
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))

    @property
    def dimension(self) -> int:
        return int(self.matrix.shape[0])


@dataclass(frozen=True)
class ProjectorBank:
    identifier: str
    projectors: Sequence[ProjectorSpec]
    complete: bool = False
    orthogonal: bool = False
    tolerance: float = field(default=1.0e-9, repr=False, compare=False)

    def __post_init__(self) -> None:
        projectors = tuple(self.projectors)
        if not self.identifier or not projectors:
            raise ValueError("a projector bank needs an identifier and at least one projector.")
        dimension = projectors[0].dimension
        if any(item.dimension != dimension for item in projectors):
            raise ValueError("all projectors in a bank must share a dimension.")
        if len({item.name for item in projectors}) != len(projectors):
            raise ValueError("projector names must be unique within a bank.")
        if self.complete and not self.orthogonal:
            raise ValueError("a complete PVM must also be declared orthogonal.")
        if self.orthogonal:
            for left, first in enumerate(projectors):
                for second in projectors[left + 1:]:
                    if not np.allclose(first.matrix @ second.matrix, 0.0, rtol=0.0, atol=self.tolerance):
                        raise ValueError("declared projector bank is not orthogonal.")
        if self.complete:
            total = np.sum([item.matrix for item in projectors], axis=0)
            if not np.allclose(total, np.eye(dimension), rtol=0.0, atol=self.tolerance):
                raise ValueError("declared complete projector bank does not resolve identity.")
        object.__setattr__(self, "projectors", projectors)

    @property
    def dimension(self) -> int:
        return self.projectors[0].dimension

    @property
    def names(self) -> tuple[str, ...]:
        return tuple(item.name for item in self.projectors)


__all__ = ["ProjectorBank", "ProjectorSpec"]
