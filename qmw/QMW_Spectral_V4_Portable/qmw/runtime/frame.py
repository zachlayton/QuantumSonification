"""Immutable envelope and causal metadata for one synchronized QMW tick.

This module does not evolve a density matrix and does not replace any native
frame contract.  It carries authoritative and derived frames together so a
runtime coordinator can order their adapters without inventing another state.
"""

from __future__ import annotations

from dataclasses import dataclass, field as dataclass_field, replace
from enum import Enum, IntEnum
import math
from types import MappingProxyType
from typing import Any, Mapping


class RuntimePhase(str, Enum):
    """The six causal phases of one QMW runtime tick."""

    CONTROL = "control"
    QUANTUM = "quantum"
    FLOW_GEOMETRY = "flow_geometry"
    FIELD_MEMORY = "field_memory"
    RECOVERY_SOUND = "recovery_sound"
    MEASUREMENT = "measurement"


class RuntimeStep(IntEnum):
    """The canonical 23-step QMW runtime order.

    Physical open-system channels belong to ``UPDATE_GENERATORS`` and affect
    the authoritative continuous evolution at ``INTEGRATE_RHO``.  The later
    ``APPLY_EXPERIMENTAL_CORRUPTION`` step is reserved for opt-in diagnostic
    or error-correction experiments; it is not physical decoherence.
    """

    RECEIVE_CONTROLS = 1
    UPDATE_GENERATORS = 2
    INTEGRATE_RHO = 3
    VALIDATE_RHO = 4
    COMPUTE_OBSERVABLES = 5
    PROJECT_SPATIAL_MODAL_BASIS = 6
    COMPUTE_CURRENT_FLUX = 7
    DETECT_EVENTS = 8
    UPDATE_GEOMETRY = 9
    UPDATE_GEOMETRY_EIGENMODES = 10
    UPDATE_QUANTUM_FIELD = 11
    APPLY_QUENCH = 12
    UPDATE_MEMORY_MATRIX = 13
    APPLY_EXPERIMENTAL_CORRUPTION = 14
    COMPUTE_SYNDROME = 15
    APPLY_RECOVERY = 16
    GENERATE_EXCITATIONS = 17
    RENDER_SOUND = 18
    SPATIALIZE = 19
    ACQUIRE_MEASUREMENT = 20
    UPDATE_TRANSFER_MEMORY_ESTIMATE = 21
    FEED_SELECTED_MEASUREMENTS = 22
    PUBLISH_FRAME = 23

    @property
    def phase(self) -> RuntimePhase:
        return _STEP_PHASE[self]


_STEP_PHASE = {
    RuntimeStep.RECEIVE_CONTROLS: RuntimePhase.CONTROL,
    RuntimeStep.UPDATE_GENERATORS: RuntimePhase.CONTROL,
    RuntimeStep.INTEGRATE_RHO: RuntimePhase.QUANTUM,
    RuntimeStep.VALIDATE_RHO: RuntimePhase.QUANTUM,
    RuntimeStep.COMPUTE_OBSERVABLES: RuntimePhase.QUANTUM,
    RuntimeStep.PROJECT_SPATIAL_MODAL_BASIS: RuntimePhase.FLOW_GEOMETRY,
    RuntimeStep.COMPUTE_CURRENT_FLUX: RuntimePhase.FLOW_GEOMETRY,
    RuntimeStep.DETECT_EVENTS: RuntimePhase.FLOW_GEOMETRY,
    RuntimeStep.UPDATE_GEOMETRY: RuntimePhase.FLOW_GEOMETRY,
    RuntimeStep.UPDATE_GEOMETRY_EIGENMODES: RuntimePhase.FLOW_GEOMETRY,
    RuntimeStep.UPDATE_QUANTUM_FIELD: RuntimePhase.FIELD_MEMORY,
    RuntimeStep.APPLY_QUENCH: RuntimePhase.FIELD_MEMORY,
    RuntimeStep.UPDATE_MEMORY_MATRIX: RuntimePhase.FIELD_MEMORY,
    RuntimeStep.APPLY_EXPERIMENTAL_CORRUPTION: RuntimePhase.RECOVERY_SOUND,
    RuntimeStep.COMPUTE_SYNDROME: RuntimePhase.RECOVERY_SOUND,
    RuntimeStep.APPLY_RECOVERY: RuntimePhase.RECOVERY_SOUND,
    RuntimeStep.GENERATE_EXCITATIONS: RuntimePhase.RECOVERY_SOUND,
    RuntimeStep.RENDER_SOUND: RuntimePhase.RECOVERY_SOUND,
    RuntimeStep.SPATIALIZE: RuntimePhase.RECOVERY_SOUND,
    RuntimeStep.ACQUIRE_MEASUREMENT: RuntimePhase.MEASUREMENT,
    RuntimeStep.UPDATE_TRANSFER_MEMORY_ESTIMATE: RuntimePhase.MEASUREMENT,
    RuntimeStep.FEED_SELECTED_MEASUREMENTS: RuntimePhase.MEASUREMENT,
    RuntimeStep.PUBLISH_FRAME: RuntimePhase.MEASUREMENT,
}

CANONICAL_RUNTIME_STEPS = tuple(RuntimeStep)


def steps_for_phase(phase: RuntimePhase) -> tuple[RuntimeStep, ...]:
    """Return the canonical contiguous steps belonging to ``phase``."""

    declared = phase if isinstance(phase, RuntimePhase) else RuntimePhase(phase)
    return tuple(step for step in CANONICAL_RUNTIME_STEPS if step.phase is declared)


@dataclass(frozen=True)
class DirtyFlags:
    """Expensive derived layers that require refresh before publication.

    Invalidation follows the causal chain.  Geometry invalidation also marks
    its eigenbasis, field, and memory dependants dirty; an eigenbasis change
    invalidates the field and memory.  Adapters explicitly clear their own
    flag only after producing a valid replacement frame.
    """

    geometry: bool = False
    eigenbasis: bool = False
    field: bool = False
    memory: bool = False

    def __post_init__(self) -> None:
        for name in ("geometry", "eigenbasis", "field", "memory"):
            if not isinstance(getattr(self, name), bool):
                raise TypeError(f"{name} dirty flag must be boolean")

    def invalidate_geometry(self) -> "DirtyFlags":
        return DirtyFlags(geometry=True, eigenbasis=True, field=True, memory=True)

    def invalidate_eigenbasis(self) -> "DirtyFlags":
        return replace(self, eigenbasis=True, field=True, memory=True)

    def invalidate_field(self) -> "DirtyFlags":
        return replace(self, field=True)

    def invalidate_memory(self) -> "DirtyFlags":
        return replace(self, memory=True)

    def clear(self, *names: str) -> "DirtyFlags":
        changes: dict[str, bool] = {}
        for name in names:
            if name not in {"geometry", "eigenbasis", "field", "memory"}:
                raise ValueError(f"unknown dirty flag: {name}")
            changes[name] = False
        return replace(self, **changes)


@dataclass(frozen=True)
class RuntimeTriggers:
    """Explicit opt-in gates for conditional runtime operations."""

    quench: bool = False
    experimental_corruption: bool = False
    recovery: bool = False
    feedback: bool = False

    def __post_init__(self) -> None:
        for name in ("quench", "experimental_corruption", "recovery", "feedback"):
            if not isinstance(getattr(self, name), bool):
                raise TypeError(f"{name} runtime trigger must be boolean")

    def cleared(self, *names: str) -> "RuntimeTriggers":
        changes: dict[str, bool] = {}
        for name in names:
            if name not in {"quench", "experimental_corruption", "recovery", "feedback"}:
                raise ValueError(f"unknown runtime trigger: {name}")
            changes[name] = False
        return replace(self, **changes)


_REVISION_NAMES = (
    "quantum",
    "observables",
    "projection",
    "flow",
    "geometry",
    "eigenbasis",
    "field",
    "memory",
    "syndrome",
    "audio",
    "measurement",
)


@dataclass(frozen=True)
class FrameRevisions:
    """Monotonic source revisions carried without equating unlike frames."""

    quantum: int = 0
    observables: int = 0
    projection: int = 0
    flow: int = 0
    geometry: int = 0
    eigenbasis: int = 0
    field: int = 0
    memory: int = 0
    syndrome: int = 0
    audio: int = 0
    measurement: int = 0

    def __post_init__(self) -> None:
        for name in _REVISION_NAMES:
            value = getattr(self, name)
            if isinstance(value, bool) or int(value) != value or value < 0:
                raise ValueError(f"{name} revision must be a nonnegative integer")
            object.__setattr__(self, name, int(value))

    def bumped(self, *names: str) -> "FrameRevisions":
        changes: dict[str, int] = {}
        for name in names:
            if name not in _REVISION_NAMES:
                raise ValueError(f"unknown revision: {name}")
            changes[name] = getattr(self, name) + 1
        return replace(self, **changes)


@dataclass(frozen=True)
class QMWFrame:
    """One synchronized QMW runtime envelope.

    Payloads remain owned and validated by their native modules.  For example,
    ``quantum`` may be the sealed authoritative density-dynamics frame while
    ``geometry`` and ``field`` are read-only observers.  Freezing this envelope
    prevents rewiring a published tick; it does not relabel downstream sound or
    sensor data as quantum evolution.
    """

    time: float
    controls: Any | None = None
    quantum: Any | None = None
    observables: Any | None = None
    flow: Any | None = None
    geometry: Any | None = None
    field: Any | None = None
    memory: Any | None = None
    syndrome: Any | None = None
    recovery: Any | None = None
    excitation: Any | None = None
    audio: Any | None = None
    spatial: Any | None = None
    measurement: Any | None = None
    diagnostics: Mapping[str, Any] = dataclass_field(default_factory=dict)
    dt: float = 0.0
    tick: int = 0
    projection: Any | None = None
    events: tuple[Any, ...] = ()
    eigenmodes: Any | None = None
    revisions: FrameRevisions = dataclass_field(default_factory=FrameRevisions)
    dirty: DirtyFlags = dataclass_field(default_factory=DirtyFlags)
    triggers: RuntimeTriggers = dataclass_field(default_factory=RuntimeTriggers)
    provenance: str = "qmw_synchronized_runtime_frame_v1"

    def __post_init__(self) -> None:
        time = float(self.time)
        dt = float(self.dt)
        if not math.isfinite(time):
            raise ValueError("time must be finite")
        if not math.isfinite(dt) or dt < 0.0:
            raise ValueError("dt must be finite and nonnegative")
        if isinstance(self.tick, bool) or int(self.tick) != self.tick or self.tick < 0:
            raise ValueError("tick must be a nonnegative integer")
        if not isinstance(self.revisions, FrameRevisions):
            raise TypeError("revisions must be a FrameRevisions value")
        if not isinstance(self.dirty, DirtyFlags):
            raise TypeError("dirty must be a DirtyFlags value")
        if not isinstance(self.triggers, RuntimeTriggers):
            raise TypeError("triggers must be a RuntimeTriggers value")
        if not isinstance(self.provenance, str) or not self.provenance:
            raise ValueError("provenance must be a nonempty string")
        if not isinstance(self.diagnostics, Mapping):
            raise TypeError("diagnostics must be a mapping")
        for name in ("quantum", "observables", "flow", "geometry"):
            if getattr(self, name) is None:
                raise ValueError(f"{name} must be present in every QMWFrame")
        object.__setattr__(self, "time", time)
        object.__setattr__(self, "dt", dt)
        object.__setattr__(self, "tick", int(self.tick))
        object.__setattr__(self, "events", tuple(self.events))
        object.__setattr__(self, "diagnostics", MappingProxyType(dict(self.diagnostics)))

    @property
    def t(self) -> float:
        """Compatibility spelling for consumers that use ``frame.t``."""

        return self.time

    def with_updates(self, **changes: Any) -> "QMWFrame":
        """Return a newly validated envelope with named payload changes."""

        return replace(self, **changes)
