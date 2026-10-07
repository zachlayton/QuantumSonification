"""Deterministic coordinator for the canonical QMW runtime phases.

The scheduler contains no quantum, geometric, acoustic, or recovery
mathematics.  Registered adapters transform the immutable umbrella frame in
the declared order.  A failed tick is never sent to the publisher.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass
from typing import Any

from .frame import CANONICAL_RUNTIME_STEPS, QMWFrame, RuntimeStep


FrameAdapter = Callable[[QMWFrame], QMWFrame]
FramePublisher = Callable[[QMWFrame], Any]


@dataclass(frozen=True)
class TickResult:
    """Frame plus an auditable record of eligible and skipped steps."""

    frame: QMWFrame
    visited_steps: tuple[RuntimeStep, ...]
    eligible_steps: tuple[RuntimeStep, ...]
    skipped_steps: tuple[RuntimeStep, ...]


class RuntimeStepError(RuntimeError):
    """A named runtime adapter failed before the frame could be published."""

    def __init__(self, step: RuntimeStep, frame: QMWFrame, cause: Exception) -> None:
        self.step = step
        self.frame = frame
        self.cause = cause
        super().__init__(f"QMW runtime step {step.value} ({step.name}) failed: {cause}")


class QMWRuntimeScheduler:
    """Order existing QMW adapters and publish exactly one completed frame.

    Adapters registered for the same step run in registration order.  Steps
    are always visited canonically regardless of registration order.  Dirty
    flags and triggers gate expensive or opt-in stages, and adapters retain
    responsibility for clearing a flag only after producing a valid payload.
    """

    def __init__(
        self,
        adapters: Mapping[RuntimeStep, Iterable[FrameAdapter]] | None = None,
        *,
        publisher: FramePublisher | None = None,
    ) -> None:
        self._adapters: dict[RuntimeStep, list[FrameAdapter]] = {
            step: [] for step in CANONICAL_RUNTIME_STEPS
        }
        if publisher is not None and not callable(publisher):
            raise TypeError("publisher must be callable")
        self._publisher = publisher
        if adapters is not None:
            for step, declared in adapters.items():
                for adapter in declared:
                    self.register(step, adapter)

    def register(self, step: RuntimeStep, adapter: FrameAdapter) -> FrameAdapter:
        """Register one frame adapter and return it for decorator-style use."""

        declared_step = step if isinstance(step, RuntimeStep) else RuntimeStep(step)
        if not callable(adapter):
            raise TypeError("adapter must be callable")
        self._adapters[declared_step].append(adapter)
        return adapter

    def adapters_for(self, step: RuntimeStep) -> tuple[FrameAdapter, ...]:
        declared_step = step if isinstance(step, RuntimeStep) else RuntimeStep(step)
        return tuple(self._adapters[declared_step])

    def run_tick(self, frame: QMWFrame) -> TickResult:
        """Run one already-timestamped frame through all eligible stages."""

        if not isinstance(frame, QMWFrame):
            raise TypeError("frame must be a QMWFrame")

        current = frame
        eligible: list[RuntimeStep] = []
        skipped: list[RuntimeStep] = []
        for step in CANONICAL_RUNTIME_STEPS:
            if not self._is_eligible(step, current):
                skipped.append(step)
                continue
            eligible.append(step)
            try:
                for adapter in self._adapters[step]:
                    updated = adapter(current)
                    if not isinstance(updated, QMWFrame):
                        raise TypeError("runtime adapters must return QMWFrame")
                    current = updated
                if step is RuntimeStep.PUBLISH_FRAME and self._publisher is not None:
                    self._publisher(current)
            except Exception as cause:
                raise RuntimeStepError(step, current, cause) from cause

        return TickResult(
            frame=current,
            visited_steps=CANONICAL_RUNTIME_STEPS,
            eligible_steps=tuple(eligible),
            skipped_steps=tuple(skipped),
        )

    @staticmethod
    def _is_eligible(step: RuntimeStep, frame: QMWFrame) -> bool:
        gates = {
            RuntimeStep.UPDATE_GEOMETRY: frame.dirty.geometry,
            RuntimeStep.UPDATE_GEOMETRY_EIGENMODES: frame.dirty.eigenbasis,
            RuntimeStep.APPLY_QUENCH: frame.triggers.quench,
            RuntimeStep.APPLY_EXPERIMENTAL_CORRUPTION: frame.triggers.experimental_corruption,
            RuntimeStep.APPLY_RECOVERY: frame.triggers.recovery,
            RuntimeStep.FEED_SELECTED_MEASUREMENTS: frame.triggers.feedback,
        }
        return gates.get(step, True)
