"""Phase-coherent audible projection of an electromagnetic Jones state.

No pitch is derived from polarization.  A fixed audible carrier replaces the
inaccessible EM carrier while the Jones amplitudes and relative phase are
preserved exactly in two coherent output channels.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from pathlib import Path
from threading import RLock
import wave

import numpy as np

from qmw.electromagnetic.jones import JonesState


@dataclass(frozen=True, slots=True)
class PhaseCoherentPolarizationSonifier:
    sample_rate: int = 48_000
    carrier_frequency_hz: float = 220.0
    gain: float = 0.2

    def __post_init__(self) -> None:
        if self.sample_rate < 8_000:
            raise ValueError("sample_rate must be at least 8000 Hz")
        if not 0.0 < self.carrier_frequency_hz < self.sample_rate / 2.0:
            raise ValueError("carrier_frequency_hz must lie below Nyquist")
        if not math.isfinite(self.gain) or not 0.0 <= self.gain <= 1.0:
            raise ValueError("gain must lie in [0, 1]")

    def render(
        self,
        jones: JonesState,
        duration_seconds: float,
        *,
        start_sample: int = 0,
    ) -> np.ndarray:
        """Render ``Re[J exp(-i Omega t)]`` as x/y stereo channels."""

        count = int(round(float(duration_seconds) * self.sample_rate))
        if count < 0 or start_sample < 0:
            raise ValueError("duration and start_sample cannot be negative")
        samples = np.arange(start_sample, start_sample + count, dtype=np.float64)
        phase = math.tau * self.carrier_frequency_hz * samples / self.sample_rate
        rotation = np.exp(-1j * phase)
        audio = np.column_stack(
            (
                np.real(jones.ex * rotation),
                np.real(jones.ey * rotation),
            )
        )
        return np.asarray(self.gain * audio, dtype=np.float64)

    @staticmethod
    def rotation_direction(jones: JonesState, *, tolerance: float = 1.0e-12) -> str:
        orientation = jones.amplitude_x * jones.amplitude_y * math.sin(
            jones.relative_phase
        )
        if abs(orientation) <= tolerance:
            return "none"
        return (
            "counterclockwise_along_plus_z"
            if orientation > 0.0
            else "clockwise_along_plus_z"
        )

    def write_wav(
        self,
        path: str | Path,
        jones: JonesState,
        duration_seconds: float,
    ) -> Path:
        audio = np.clip(self.render(jones, duration_seconds), -1.0, 1.0)
        pcm = np.asarray(np.round(audio * 32767.0), dtype="<i2")
        destination = Path(path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        with wave.open(str(destination), "wb") as output:
            output.setnchannels(2)
            output.setsampwidth(2)
            output.setframerate(self.sample_rate)
            output.writeframes(pcm.tobytes())
        return destination


class PhaseCoherentAudioStream:
    """Optional sounddevice stream with a continuous carrier sample clock."""

    def __init__(
        self,
        sonifier: PhaseCoherentPolarizationSonifier,
        jones: JonesState,
        *,
        blocksize: int = 512,
    ) -> None:
        self.sonifier = sonifier
        self._jones = jones
        self._sample_index = 0
        self._blocksize = int(blocksize)
        self._lock = RLock()
        self._stream = None

    def set_jones(self, jones: JonesState) -> None:
        with self._lock:
            self._jones = jones

    def render_block(self, frame_count: int) -> np.ndarray:
        with self._lock:
            block = self.sonifier.render(
                self._jones,
                frame_count / self.sonifier.sample_rate,
                start_sample=self._sample_index,
            )
            self._sample_index += frame_count
        return np.asarray(block, dtype=np.float32)

    def start(self) -> None:
        try:
            import sounddevice as sd
        except ImportError as error:
            raise RuntimeError(
                "real-time playback requires the optional 'sounddevice' package; "
                "use --render-wav for dependency-free output"
            ) from error

        def callback(outdata, frames, _time_info, status):
            if status:
                # The callback must not raise merely because PortAudio reports a
                # recoverable underflow; the host can inspect its own status.
                pass
            outdata[:] = self.render_block(frames)

        self._stream = sd.OutputStream(
            samplerate=self.sonifier.sample_rate,
            channels=2,
            dtype="float32",
            blocksize=self._blocksize,
            callback=callback,
        )
        self._stream.start()

    def stop(self) -> None:
        if self._stream is not None:
            self._stream.stop()
            self._stream.close()
            self._stream = None


__all__ = ["PhaseCoherentAudioStream", "PhaseCoherentPolarizationSonifier"]
