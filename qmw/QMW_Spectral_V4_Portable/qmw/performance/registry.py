"""Capability and source registration for QMW Unified Quantum Instrument v1."""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Iterable, Mapping

from .envelope import StateKind


@dataclass(frozen=True)
class SourceDescriptor:
    source_id: str
    label: str
    state_kinds: frozenset[StateKind]
    capabilities: frozenset[str]
    logical_audio_lanes: int
    legacy_contracts: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.source_id.strip() or not self.label.strip():
            raise ValueError("source identity and label must be nonempty")
        if not self.state_kinds:
            raise ValueError("a source must declare at least one state kind")
        if int(self.logical_audio_lanes) < 1:
            raise ValueError("logical_audio_lanes must be positive")
        object.__setattr__(self, "state_kinds", frozenset(self.state_kinds))
        object.__setattr__(self, "capabilities", frozenset(self.capabilities))
        object.__setattr__(self, "logical_audio_lanes", int(self.logical_audio_lanes))
        object.__setattr__(self, "legacy_contracts", tuple(self.legacy_contracts))


class SourceRegistry:
    """Small deterministic registry; registration never starts a source."""

    def __init__(self, descriptors: Iterable[SourceDescriptor] = ()) -> None:
        self._descriptors: dict[str, SourceDescriptor] = {}
        for descriptor in descriptors:
            self.register(descriptor)

    def register(self, descriptor: SourceDescriptor) -> None:
        if descriptor.source_id in self._descriptors:
            raise ValueError(f"source already registered: {descriptor.source_id}")
        self._descriptors[descriptor.source_id] = descriptor

    def get(self, source_id: str) -> SourceDescriptor:
        try:
            return self._descriptors[source_id]
        except KeyError as exc:
            raise KeyError(f"unknown performance source: {source_id}") from exc

    def compatible(self, state_kind: StateKind) -> tuple[SourceDescriptor, ...]:
        return tuple(
            descriptor
            for descriptor in self._descriptors.values()
            if state_kind in descriptor.state_kinds
        )

    @property
    def descriptors(self) -> Mapping[str, SourceDescriptor]:
        return MappingProxyType(dict(self._descriptors))


__all__ = ["SourceDescriptor", "SourceRegistry"]
