from __future__ import annotations

from dataclasses import dataclass, field

from qmw.core.measurement_event import MeasurementEvent, MeasurementEventBus
from qmw.core.state_bus import StateBus
from qmw.core.state_frame import QuantumStateFrame


@dataclass
class QuantumDataBus:
    """Combined outlet for continuous state and discrete measurement streams.

    This intentionally mirrors the Estimator/Sampler split:
        - state_bus carries continuous quantum descriptors
        - measurement_bus carries BitArray/classical-register events

    OSC, Max, audio engines, and visualizers can subscribe to either side or
    treat this as the one public QMW data bus.
    """

    state_bus: StateBus = field(default_factory=StateBus)
    measurement_bus: MeasurementEventBus = field(default_factory=MeasurementEventBus)

    def publish_state(self, frame: QuantumStateFrame) -> None:
        self.state_bus.publish(frame)

    def publish_measurement(self, event: MeasurementEvent) -> None:
        self.measurement_bus.publish(event)

    @property
    def latest_state(self) -> QuantumStateFrame | None:
        return self.state_bus.latest

    @property
    def latest_measurement(self) -> MeasurementEvent | None:
        return self.measurement_bus.latest
