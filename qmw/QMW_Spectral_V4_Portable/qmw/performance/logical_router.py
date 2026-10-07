"""Protected logical-to-physical sixteen-output routing contract.

This is deliberately not a hardware driver.  It maps a fully declared
perceptual excitation frame to named physical endpoints and leaves delivery,
calibration, mute/arm interlocks, and transducer control to a later body.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from types import MappingProxyType
from typing import Mapping

import numpy as np

from .envelope import Authority


OUTPUT_COUNT = 16


@dataclass(frozen=True)
class LogicalExcitationFrame:
    """A downstream perceptual frame, explicitly separate from native state."""

    source_id: str
    source_revision: int
    logical_time: float
    values: np.ndarray
    semantics: str
    authority: Authority = Authority.PERCEPTUAL_ADAPTER

    def __post_init__(self) -> None:
        values = np.asarray(self.values, dtype=float)
        if not self.source_id.strip() or not self.semantics.strip():
            raise ValueError("logical excitation source and semantics must be nonempty.")
        if int(self.source_revision) < 0 or not math.isfinite(float(self.logical_time)):
            raise ValueError("logical excitation revision and time must be valid.")
        if values.shape != (OUTPUT_COUNT,) or not np.all(np.isfinite(values)):
            raise ValueError("logical excitation requires sixteen finite values.")
        if self.authority is not Authority.PERCEPTUAL_ADAPTER:
            raise ValueError("logical routing accepts only perceptual-adapter excitation frames.")
        object.__setattr__(self, "source_revision", int(self.source_revision))
        object.__setattr__(self, "logical_time", float(self.logical_time))
        object.__setattr__(self, "values", np.array(values, copy=True))


@dataclass(frozen=True)
class PhysicalOutputContract:
    """Immutable endpoint declaration; labels are not device-control commands."""

    endpoints: tuple[str, ...]
    contract_id: str = "qmw.physical_output_contract.v1"

    def __post_init__(self) -> None:
        endpoints = tuple(str(endpoint) for endpoint in self.endpoints)
        if len(endpoints) != OUTPUT_COUNT or any(not endpoint.strip() for endpoint in endpoints):
            raise ValueError("physical output contract requires sixteen nonempty endpoints.")
        if len(set(endpoints)) != OUTPUT_COUNT:
            raise ValueError("physical output endpoints must be unique.")
        if not self.contract_id.strip():
            raise ValueError("physical output contract id must be nonempty.")
        object.__setattr__(self, "endpoints", endpoints)

    @classmethod
    def harmonic_voices(cls) -> "PhysicalOutputContract":
        return cls(tuple(f"H{index}" for index in range(1, OUTPUT_COUNT + 1)))


@dataclass(frozen=True)
class PhysicalOutputFrame:
    """Router result. ``delivery_enabled`` stays false until a hardware body exists."""

    source_id: str
    source_revision: int
    logical_time: float
    contract_id: str
    endpoint_values: Mapping[str, float]
    delivery_enabled: bool = False
    provenance: str = "protected_logical_to_physical_contract_only"

    def __post_init__(self) -> None:
        endpoint_values = {str(key): float(value) for key, value in self.endpoint_values.items()}
        if len(endpoint_values) != OUTPUT_COUNT or not all(math.isfinite(value) for value in endpoint_values.values()):
            raise ValueError("physical output frame requires sixteen finite endpoint values.")
        if self.delivery_enabled:
            raise ValueError("physical delivery is not implemented by the protected router.")
        object.__setattr__(self, "endpoint_values", MappingProxyType(endpoint_values))


class LogicalToPhysicalRouter16:
    """Fixed, validated 16x16 permutation/gain map with no hardware side effects."""

    def __init__(
        self, contract: PhysicalOutputContract, *, logical_to_endpoint: tuple[int, ...] | None = None,
        gains: tuple[float, ...] | None = None,
    ) -> None:
        if not isinstance(contract, PhysicalOutputContract):
            raise ValueError("router requires an explicit PhysicalOutputContract.")
        route = tuple(range(OUTPUT_COUNT)) if logical_to_endpoint is None else tuple(logical_to_endpoint)
        gain_values = (1.0,) * OUTPUT_COUNT if gains is None else tuple(float(value) for value in gains)
        if len(route) != OUTPUT_COUNT or set(route) != set(range(OUTPUT_COUNT)):
            raise ValueError("logical_to_endpoint must be a sixteen-output permutation.")
        if len(gain_values) != OUTPUT_COUNT or not all(math.isfinite(value) and value >= 0.0 for value in gain_values):
            raise ValueError("router gains must be sixteen finite nonnegative values.")
        self.contract = contract
        self.logical_to_endpoint = route
        self.gains = gain_values

    def route(self, excitation: LogicalExcitationFrame) -> PhysicalOutputFrame:
        if not isinstance(excitation, LogicalExcitationFrame):
            raise ValueError("router requires a LogicalExcitationFrame, not native state.")
        values = {
            self.contract.endpoints[endpoint]: float(excitation.values[lane] * self.gains[lane])
            for lane, endpoint in enumerate(self.logical_to_endpoint)
        }
        return PhysicalOutputFrame(
            source_id=excitation.source_id, source_revision=excitation.source_revision,
            logical_time=excitation.logical_time, contract_id=self.contract.contract_id,
            endpoint_values=values,
        )


__all__ = [
    "LogicalExcitationFrame", "LogicalToPhysicalRouter16", "OUTPUT_COUNT",
    "PhysicalOutputContract", "PhysicalOutputFrame",
]
