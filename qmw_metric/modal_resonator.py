"""Compact control-frame-driven bank of stable modal resonators."""

from __future__ import annotations

import numpy as np

from .config import ResonatorConfig
from .frames import CurvedModeFrame
from .grid import RealArray


class ModalResonator:
    """Audio-rate modal bank; it never receives the complete spatial field."""

    def __init__(self, config: ResonatorConfig = ResonatorConfig()):
        self.config = config
        self.frame: CurvedModeFrame | None = None
        self.positions = np.zeros(0, dtype=np.float64)
        self.velocities = np.zeros(0, dtype=np.float64)
        self.current_frequencies = np.zeros(0, dtype=np.float64)
        self.amplitude_correction = np.zeros(0, dtype=np.float64)
        self.velocity_correction = np.zeros(0, dtype=np.float64)
        self.amplitude_correction_samples = 0

    def update_mode_frame(self, frame: CurvedModeFrame) -> None:
        count = frame.frequencies.size
        previous = self.frame
        if self.positions.size != count:
            self.positions = np.zeros(count, dtype=np.float64)
            self.velocities = np.zeros(count, dtype=np.float64)
            self.current_frequencies = frame.frequencies.copy()
            self.amplitude_correction = np.zeros(count, dtype=np.float64)
            self.velocity_correction = np.zeros(count, dtype=np.float64)
            self.amplitude_correction_samples = 0
        elif previous is not None and frame.time > previous.time:
            # The antisymmetric moving-basis connection generates an
            # energy-preserving modal-coordinate rotation. A Cayley step is
            # orthogonal for a skew matrix and avoids Euler energy growth.
            dt = frame.time - previous.time
            connection = np.asarray(frame.intermodal_connection, dtype=np.float64)
            identity = np.eye(count)
            rotation = np.linalg.solve(
                identity + .5 * dt * connection,
                identity - .5 * dt * connection,
            )
            self.transition_state(rotation @ self.positions, rotation @ self.velocities)
        self.frame = frame

    def set_amplitudes(self, amplitudes: RealArray) -> None:
        value = np.asarray(amplitudes, dtype=np.float64)
        if value.shape != self.positions.shape:
            raise ValueError("amplitudes do not match resonator mode count")
        self.positions = value.copy()
        self.amplitude_correction = np.zeros_like(value)
        self.velocity_correction = np.zeros_like(value)
        self.amplitude_correction_samples = 0

    def transition_state(
        self,
        amplitudes: RealArray,
        velocities: RealArray,
        transition_seconds: float | None = None,
    ) -> None:
        target_positions = np.asarray(amplitudes, dtype=np.float64)
        target_velocities = np.asarray(velocities, dtype=np.float64)
        if target_positions.shape != self.positions.shape or target_velocities.shape != self.velocities.shape:
            raise ValueError("modal state does not match resonator mode count")
        seconds = self.config.retune_time_seconds if transition_seconds is None else float(transition_seconds)
        if not np.isfinite(seconds) or seconds < 0.0:
            raise ValueError("transition_seconds must be finite and nonnegative")
        samples = int(round(seconds * self.config.sample_rate))
        if samples <= 0:
            self.positions = target_positions.copy()
            self.velocities = target_velocities.copy()
            self.amplitude_correction = np.zeros_like(target_positions)
            self.velocity_correction = np.zeros_like(target_velocities)
            self.amplitude_correction_samples = 0
            return
        self.amplitude_correction = target_positions - self.positions
        self.velocity_correction = target_velocities - self.velocities
        self.amplitude_correction_samples = samples

    def transition_amplitudes(
        self, amplitudes: RealArray, transition_seconds: float | None = None
    ) -> None:
        """Apply a quench transfer continuously, avoiding an output discontinuity."""
        value = np.asarray(amplitudes, dtype=np.float64)
        if value.shape != self.positions.shape:
            raise ValueError("amplitudes do not match resonator mode count")
        self.transition_state(value, self.velocities, transition_seconds)

    def process_block(self, modal_excitation: RealArray, block_size: int) -> RealArray:
        if self.frame is None:
            raise RuntimeError("a mode frame must be installed before processing audio")
        if block_size <= 0:
            raise ValueError("block_size must be positive")
        excitation = np.asarray(modal_excitation, dtype=np.float64)
        count = self.frame.frequencies.size
        if excitation.shape == (count,):
            excitation = np.broadcast_to(excitation, (block_size, count))
        elif excitation.shape != (block_size, count):
            raise ValueError("excitation must have shape (modes,) or (block_size, modes)")
        output = np.empty(block_size, dtype=np.float64)
        dt = 1.0 / self.config.sample_rate
        if self.config.retune_time_seconds == 0.0:
            retune = 1.0
        else:
            retune = 1.0 - np.exp(-dt / self.config.retune_time_seconds)
        nyquist_limit = 0.45 * self.config.sample_rate
        for sample in range(block_size):
            if self.amplitude_correction_samples > 0:
                correction = self.amplitude_correction / self.amplitude_correction_samples
                self.positions += correction
                self.amplitude_correction -= correction
                velocity_correction = self.velocity_correction / self.amplitude_correction_samples
                self.velocities += velocity_correction
                self.velocity_correction -= velocity_correction
                self.amplitude_correction_samples -= 1
            self.current_frequencies += retune * (self.frame.frequencies - self.current_frequencies)
            omega = 2.0 * np.pi * np.minimum(self.current_frequencies, nyquist_limit)
            acceleration = (
                excitation[sample]
                - 2.0 * self.frame.damping * omega * self.velocities
                - omega**2 * self.positions
            )
            self.velocities += dt * acceleration
            self.positions += dt * self.velocities
            output[sample] = float(np.dot(self.frame.gains, self.positions)) / np.sqrt(count)
        return output
