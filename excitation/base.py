from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from excitation.descriptor import QuantumDescriptor


class QuantumSource(ABC):
    """Shared interface for all QMW quantum source models.

    Contract:
        source.step(dt) advances the internal physical model.
        source.descriptor returns the compact normalized descriptor.
        source.state returns the richer model-specific state snapshot.
    """

    @abstractmethod
    def step(self, dt: float) -> None:
        """Advance the source model by dt seconds or normalized time units."""
        raise NotImplementedError

    @property
    @abstractmethod
    def descriptor(self) -> QuantumDescriptor:
        """Return the latest compact descriptor without advancing the model."""
        raise NotImplementedError

    @property
    @abstractmethod
    def state(self) -> Any:
        """Return the latest model-specific state snapshot."""
        raise NotImplementedError