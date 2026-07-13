from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

from qmw.flucoma.quantum_descriptors import DescriptorVector


@dataclass(frozen=True)
class SearchResult:
    identifier: str
    distance: float
    index: int
    metadata: dict[str, Any]


class DescriptorCorpus:
    """Small in-process DataSet/KDTree/PCA analogue inspired by FluCoMa."""

    def __init__(self, max_items: int = 512, min_projection_items: int = 8) -> None:
        self.max_items = int(max_items)
        self.min_projection_items = int(min_projection_items)
        self.items: list[DescriptorVector] = []
        self._mean: np.ndarray | None = None
        self._scale: np.ndarray | None = None
        self._components: np.ndarray | None = None

    def add(self, descriptor: DescriptorVector) -> None:
        if self.items and descriptor.names != self.items[0].names:
            raise ValueError("All descriptors in a corpus must share the same names")
        self.items.append(descriptor)
        if len(self.items) > self.max_items:
            self.items = self.items[-self.max_items :]
        self._fit()

    def nearest(self, descriptor: DescriptorVector, *, exclude_self: bool = True) -> SearchResult | None:
        if not self.items:
            return None
        matrix = self.standardized_matrix()
        query = self.standardize(descriptor.values)
        distances = np.linalg.norm(matrix - query, axis=1)
        if exclude_self and self.items[-1].identifier == descriptor.identifier and len(distances) > 1:
            distances[-1] = np.inf
        index = int(np.argmin(distances))
        if not np.isfinite(distances[index]):
            return None
        item = self.items[index]
        return SearchResult(
            identifier=item.identifier,
            distance=float(distances[index]),
            index=index,
            metadata=dict(item.metadata),
        )

    def novelty(self, descriptor: DescriptorVector) -> float:
        result = self.nearest(descriptor, exclude_self=True)
        if result is None:
            return 0.0
        return float(np.clip(result.distance / 6.0, 0.0, 1.0))

    def projection(self, descriptor: DescriptorVector) -> tuple[float, float]:
        if self._components is None:
            return self._fallback_projection(descriptor.values)
        projected = self.standardize(descriptor.values) @ self._components.T
        return self._unit_pair(projected)

    def standardized_matrix(self) -> np.ndarray:
        if not self.items:
            return np.empty((0, 0), dtype=float)
        values = np.vstack([item.values for item in self.items])
        return self.standardize(values)

    def standardize(self, values: np.ndarray) -> np.ndarray:
        values = np.asarray(values, dtype=float)
        if self._mean is None or self._scale is None:
            return np.nan_to_num(values, nan=0.0)
        return np.nan_to_num((values - self._mean) / self._scale, nan=0.0)

    def _fit(self) -> None:
        values = np.vstack([item.values for item in self.items])
        self._mean = np.mean(values, axis=0)
        scale = np.std(values, axis=0)
        self._scale = np.where(scale > 1e-9, scale, 1.0)

        if len(self.items) < self.min_projection_items:
            self._components = None
            return

        standardized = self.standardize(values)
        _, _, vh = np.linalg.svd(standardized, full_matrices=False)
        if vh.shape[0] < 2:
            self._components = None
        else:
            self._components = vh[:2]

    @staticmethod
    def _unit_pair(values: np.ndarray) -> tuple[float, float]:
        x = float(0.5 + 0.18 * values[0])
        y = float(0.5 + 0.18 * values[1])
        return float(np.clip(x, 0.0, 1.0)), float(np.clip(y, 0.0, 1.0))

    @staticmethod
    def _fallback_projection(values: np.ndarray) -> tuple[float, float]:
        if values.size < 9:
            return 0.5, 0.5
        x = float(np.clip((values[6] + 1.0) * 0.5, 0.0, 1.0))
        y = float(np.clip((values[8] + 1.0) * 0.5, 0.0, 1.0))
        return x, y
