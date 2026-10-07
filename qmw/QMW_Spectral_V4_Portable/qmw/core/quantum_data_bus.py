from __future__ import annotations

from dataclasses import dataclass, field

from qmw.core.measurement_event import MeasurementEvent, MeasurementEventBus
from qmw.core.state_bus import StateBus
from qmw.core.state_frame import QuantumStateFrame
from qmw.core.quantum_spectrum import (
    QMWSpectralObserver,
    QMWSpectralTextLogger,
    QMWSpectralTrace,
)


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
    spectral_observer: QMWSpectralObserver = field(default_factory=QMWSpectralObserver)
    spectral_trace: QMWSpectralTrace = field(default_factory=QMWSpectralTrace)
    spectral_text_logger: QMWSpectralTextLogger | None = None

    def publish_state(self, frame: QuantumStateFrame) -> None:
        spectrum = self.spectral_observer.observe(frame)
        if spectrum is not None:
            record = self.spectral_trace.append(frame, spectrum)
            if self.spectral_text_logger is not None:
                self.spectral_text_logger.append(record)
        self.state_bus.publish(frame)

    def enable_spectral_text_log(
        self, path: str, *, overwrite: bool = True
    ) -> QMWSpectralTextLogger:
        """Start an explicit per-frame text log; disabled unless a caller opts in."""

        self.spectral_text_logger = QMWSpectralTextLogger(path, overwrite=overwrite)
        return self.spectral_text_logger

    def publish_measurement(self, event: MeasurementEvent) -> None:
        self.measurement_bus.publish(event)

    @property
    def latest_state(self) -> QuantumStateFrame | None:
        return self.state_bus.latest

    @property
    def latest_measurement(self) -> MeasurementEvent | None:
        return self.measurement_bus.latest
