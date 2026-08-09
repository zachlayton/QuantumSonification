"""Measurement protocol contract and explicit sampling policies."""

from __future__ import annotations

import secrets
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from threading import Lock
from typing import Any


MAX_SEED = 2**32 - 1


class SamplingMode(str, Enum):
    FIXED = "fixed"
    RESAMPLE = "resample"
    SEQUENCE = "sequence"


@dataclass(frozen=True)
class SamplingResolution:
    mode: str
    requested_seed: int | None
    resolved_seed: int
    sequence_index: int | None = None


class SamplingPolicy:
    """Resolve reproducible or changing seeds for a measurement protocol."""

    def __init__(
        self,
        mode: SamplingMode | str = SamplingMode.FIXED,
        *,
        seed: int | None = 23,
    ) -> None:
        self.mode = SamplingMode(mode)
        if self.mode is not SamplingMode.RESAMPLE and seed is None:
            raise ValueError(f"{self.mode.value} sampling requires a seed")
        if seed is not None and not 0 <= int(seed) <= MAX_SEED:
            raise ValueError(f"seed must be between 0 and {MAX_SEED}")
        self.seed = None if seed is None else int(seed)
        self._index = 0
        self._lock = Lock()

    @classmethod
    def fixed(cls, seed: int = 23) -> "SamplingPolicy":
        return cls(SamplingMode.FIXED, seed=seed)

    @classmethod
    def resample(cls) -> "SamplingPolicy":
        return cls(SamplingMode.RESAMPLE, seed=None)

    @classmethod
    def sequence(cls, seed: int = 23) -> "SamplingPolicy":
        return cls(SamplingMode.SEQUENCE, seed=seed)

    def resolve(self, requested_seed: int | None = None) -> SamplingResolution:
        with self._lock:
            if self.mode is SamplingMode.RESAMPLE:
                resolved = secrets.randbelow(MAX_SEED + 1)
                return SamplingResolution(
                    self.mode.value,
                    requested_seed,
                    resolved,
                )
            base = self.seed if requested_seed is None else int(requested_seed)
            if not 0 <= base <= MAX_SEED:
                raise ValueError(f"seed must be between 0 and {MAX_SEED}")
            if self.mode is SamplingMode.FIXED:
                return SamplingResolution(
                    self.mode.value,
                    requested_seed,
                    base,
                )
            index = self._index
            self._index += 1
            return SamplingResolution(
                self.mode.value,
                requested_seed,
                (base + index) % (MAX_SEED + 1),
                index,
            )


@dataclass(frozen=True)
class MeasurementRecord:
    observable_estimates: dict[str, float]
    total_shots: int
    output: Any
    metadata: dict[str, Any]
    sampling: SamplingResolution


class MeasurementProtocol(ABC):
    name: str
    description: str
    kind = "measurement_protocol"

    def __init__(self, sampling: SamplingPolicy | None = None) -> None:
        self.sampling_policy = sampling or SamplingPolicy.fixed()

    def resolve_sampling(
        self,
        requested_seed: int | None,
    ) -> SamplingResolution:
        return self.sampling_policy.resolve(requested_seed)

    @abstractmethod
    def measure(
        self,
        rho: Any,
        *,
        preset: str,
        representation: str,
        shots: int,
        sampling: SamplingResolution,
        source: str,
    ) -> MeasurementRecord:
        """Sample and reconstruct one density representation."""

    def metadata(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "kind": self.kind,
        }
