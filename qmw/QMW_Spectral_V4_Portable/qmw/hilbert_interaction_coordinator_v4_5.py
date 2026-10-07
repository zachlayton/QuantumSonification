"""Authoritative in-process coordinator for a Hilbert-driven interaction view.

The public Hilbert OSC transport is deliberately bounded and never contains a
full density matrix.  This coordinator therefore owns the only permitted join:
one authoritative four-qubit density evolution and one GPE evolution are
advanced on a shared logical clock, then joined locally through
``HilbertTransportInteractionAdapterV44``.  It emits only downstream
observations: a bounded interaction frame and, optionally, a bounded
``FieldFrame`` observer transaction.  Neither observer can feed back into the
Hilbert or GPE source.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Callable, Protocol

import numpy as np

from .gpe.field_frame import FieldFrame
from .hilbert_transport_interaction_v4_4 import (
    FieldFrameTransportEnvelopeV44,
    HilbertTransportInteractionAdapterV44,
    HilbertTransportInteractionFrameV44,
    HilbertTransportSourceFrameV44,
)


Array = np.ndarray


class HilbertDensitySourceV45(Protocol):
    """Coordinator-owned source of the authoritative four-qubit density."""

    def advance(self, dt: float) -> Array: ...


class GPEFieldFrameSourceV45(Protocol):
    """Coordinator-owned source of an already-observed GPE FieldFrame."""

    def advance(self, time: float, dt: float) -> FieldFrame: ...


FieldFrameObserverV45 = Callable[[FieldFrameTransportEnvelopeV44], None]
HilbertObserverV45 = Callable[[HilbertTransportSourceFrameV44], None]


@dataclass(frozen=True)
class HilbertInteractionTransactionV45:
    """One accepted same-time, same-revision coordinator commit."""

    revision: int
    time: float
    hilbert: HilbertTransportSourceFrameV44
    field: FieldFrameTransportEnvelopeV44
    interaction: HilbertTransportInteractionFrameV44
    provenance: str = "in_process_authoritative_hilbert_gpe_to_interaction_commit_v4_5"


class HilbertInteractionCoordinatorV45:
    """Advance aligned sources and publish no interaction on a rejected join.

    A shared revision here identifies a synchronized observation transaction;
    it does *not* claim that the Hilbert density and GPE mean field are the
    same physical state space.  They remain independent sources joined only by
    the explicitly read-only interaction adapter.
    """

    def __init__(
        self,
        hilbert_source: HilbertDensitySourceV45,
        field_source: GPEFieldFrameSourceV45,
        adapter: HilbertTransportInteractionAdapterV44,
        *,
        start_time: float = 0.0,
        time_tolerance: float = 1.0e-8,
        hilbert_observer: HilbertObserverV45 | None = None,
        field_observer: FieldFrameObserverV45 | None = None,
    ) -> None:
        if not hasattr(hilbert_source, "advance") or not hasattr(field_source, "advance"):
            raise ValueError("coordinator sources must expose advance().")
        if not isinstance(adapter, HilbertTransportInteractionAdapterV44):
            raise ValueError("coordinator requires a HilbertTransportInteractionAdapterV44.")
        if not math.isfinite(float(start_time)):
            raise ValueError("start_time must be finite.")
        if not math.isfinite(float(time_tolerance)) or time_tolerance < 0.0:
            raise ValueError("time_tolerance must be finite and nonnegative.")
        self.hilbert_source = hilbert_source
        self.field_source = field_source
        self.adapter = adapter
        self.time = float(start_time)
        self.revision = 0
        self.time_tolerance = float(time_tolerance)
        self.hilbert_observer = hilbert_observer
        self.field_observer = field_observer
        self.last_transaction: HilbertInteractionTransactionV45 | None = None

    def step(self, dt: float) -> HilbertInteractionTransactionV45:
        """Advance both authorities once and commit their aligned observation."""

        duration = float(dt)
        if not math.isfinite(duration) or duration <= 0.0:
            raise ValueError("dt must be finite and positive.")
        logical_time = self.time + duration
        revision = self.revision
        rho = self.hilbert_source.advance(duration)
        field_frame = self.field_source.advance(logical_time, duration)
        if not isinstance(field_frame, FieldFrame):
            raise ValueError("GPE field source must return a FieldFrame.")
        if abs(float(field_frame.time) - logical_time) > self.time_tolerance:
            raise ValueError("coordinator GPE FieldFrame time must equal its logical Hilbert time.")

        hilbert = HilbertTransportSourceFrameV44(revision, logical_time, rho)
        field = FieldFrameTransportEnvelopeV44(revision, field_frame)
        # ``update`` performs a second defensive revision/time check before it
        # steps or publishes the downstream interaction adapter.
        interaction = self.adapter.update(hilbert, field, dt=duration)
        transaction = HilbertInteractionTransactionV45(
            revision=revision, time=logical_time, hilbert=hilbert,
            field=field, interaction=interaction,
        )
        if self.hilbert_observer is not None:
            self.hilbert_observer(hilbert)
        if self.field_observer is not None:
            self.field_observer(field)
        self.time = logical_time
        self.revision += 1
        self.last_transaction = transaction
        return transaction


__all__ = [
    "FieldFrameObserverV45", "GPEFieldFrameSourceV45", "HilbertDensitySourceV45",
    "HilbertInteractionCoordinatorV45", "HilbertInteractionTransactionV45",
    "HilbertObserverV45",
]
