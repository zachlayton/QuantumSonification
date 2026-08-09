"""Bounded acoustic feedback for the SPSA sonification loop."""

from __future__ import annotations

from dataclasses import dataclass, replace
import threading
import time
from typing import Any

from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import ThreadingOSCUDPServer


def _clip(value: float, low: float, high: float) -> float:
    return min(high, max(low, float(value)))


@dataclass(frozen=True)
class AudioFeedback:
    """One normalized analysis frame returned by the listening instrument."""

    energy: float = 0.0
    centroid: float = 0.5
    flux: float = 0.0
    stereo_balance: float = 0.0
    resonance: float = 0.5
    sequence: int = 0
    received_at: float = 0.0


@dataclass(frozen=True)
class FeedbackControls:
    epsilon: float
    batch_size: int
    learning_rate: float
    perturbation_polarity: float


class AudioFeedbackState:
    """Thread-safe latest-value store used by the OSC receive thread."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._frame = AudioFeedback()

    def update(
        self,
        energy: float,
        centroid: float,
        flux: float,
        stereo_balance: float,
        resonance: float,
    ) -> AudioFeedback:
        with self._lock:
            self._frame = AudioFeedback(
                energy=_clip(energy, 0.0, 1.0),
                centroid=_clip(centroid, 0.0, 1.0),
                flux=_clip(flux, 0.0, 1.0),
                stereo_balance=_clip(stereo_balance, -1.0, 1.0),
                resonance=_clip(resonance, 0.0, 1.0),
                sequence=self._frame.sequence + 1,
                received_at=time.monotonic(),
            )
            return self._frame

    def snapshot(self) -> AudioFeedback:
        with self._lock:
            return replace(self._frame)


def controls_from_feedback(
    frame: AudioFeedback,
    *,
    base_epsilon: float,
    base_batch_size: int,
    base_learning_rate: float,
    mix: float = 1.0,
    max_batch_size: int = 8,
) -> FeedbackControls:
    """Map normalized analysis to conservative, bounded next-step controls."""

    mix = _clip(mix, 0.0, 1.0)
    # Bright answers ask broader questions; dark answers ask finer ones.
    epsilon_factor = 2.0 ** ((frame.centroid - 0.5) * 1.5 * mix)
    epsilon = _clip(base_epsilon * epsilon_factor, base_epsilon * 0.5, base_epsilon * 2.0)

    # Sustained/resonant answers permit a stronger update; unstable ones slow it down.
    learning_factor = 1.0 + mix * (0.8 * frame.resonance - 0.4)
    learning_rate = _clip(
        base_learning_rate * learning_factor,
        base_learning_rate * 0.5,
        base_learning_rate * 1.5,
    )

    # High spectral motion requests more simultaneous questions before averaging.
    extra_probes = round(mix * frame.flux * 4.0)
    batch_size = min(max_batch_size, max(1, base_batch_size + extra_probes))

    # A strong stereo answer swaps the orientation of the following probe pair.
    polarity = (
        -1.0
        if mix > 0 and abs(frame.stereo_balance) > 0.12 and frame.stereo_balance > 0
        else 1.0
    )
    return FeedbackControls(
        epsilon=epsilon,
        batch_size=batch_size,
        learning_rate=learning_rate,
        perturbation_polarity=polarity,
    )


class AudioFeedbackReceiver:
    """Small localhost OSC server receiving analysis from SuperCollider."""

    def __init__(
        self,
        state: AudioFeedbackState,
        host: str = "127.0.0.1",
        port: int = 17421,
        root: str = "/qmw/spsa/feedback",
    ) -> None:
        self.state = state
        dispatcher = Dispatcher()
        dispatcher.map(root, self._handle_feedback)
        self.server = ThreadingOSCUDPServer((host, port), dispatcher)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)

    def _handle_feedback(self, _address: str, *values: Any) -> None:
        if len(values) < 5:
            return
        self.state.update(*(float(value) for value in values[:5]))

    def start(self) -> None:
        self.thread.start()

    def close(self) -> None:
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=1.0)
