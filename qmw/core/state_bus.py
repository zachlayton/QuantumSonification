from __future__ import annotations

from collections.abc import Callable

from qmw.core.state_frame import QuantumStateFrame


FrameSubscriber = Callable[[QuantumStateFrame], None]


class StateBus:
    """Small synchronous publisher for QMW state frames."""

    def __init__(self) -> None:
        self._subscribers: list[FrameSubscriber] = []
        self.latest: QuantumStateFrame | None = None

    def subscribe(self, callback: FrameSubscriber) -> FrameSubscriber:
        self._subscribers.append(callback)
        return callback

    def unsubscribe(self, callback: FrameSubscriber) -> None:
        self._subscribers = [
            subscriber
            for subscriber in self._subscribers
            if subscriber is not callback
        ]

    def publish(self, frame: QuantumStateFrame) -> None:
        self.latest = frame
        for subscriber in tuple(self._subscribers):
            subscriber(frame)

