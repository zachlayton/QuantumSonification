"""Offline first-listen experiment for the GRW sonification adapter."""

from __future__ import annotations

from pathlib import Path
import wave

import numpy as np

from density.cnmat_resonator_model import density_matrix_to_cnmat_resonators
from density.grw_event_channel_v1 import GRWConfig, GRWEventChannel, ghz_density
from density.grw_sonification_adapter_v1 import (
    GRWSonificationFrame,
    frame_from_grw_event,
)


I2 = np.eye(2, dtype=np.complex128)
X = np.array([[0.0, 1.0], [1.0, 0.0]], dtype=np.complex128)
Z = np.array([[1.0, 0.0], [0.0, -1.0]], dtype=np.complex128)


def _local(operator: np.ndarray, qubit: int) -> np.ndarray:
    factors = [I2] * 4
    factors[qubit] = operator
    result = np.array([[1.0]], dtype=np.complex128)
    for factor in factors:
        result = np.kron(result, factor)
    return result


def ghz_demo_hamiltonian() -> np.ndarray:
    """Stable four-branch transverse-field/nearest-neighbor resonant body."""
    operator = np.zeros((16, 16), dtype=np.complex128)
    for qubit in range(4):
        operator += (0.19 + 0.055 * qubit) * _local(Z, qubit)
        operator += (0.31 - 0.035 * qubit) * _local(X, qubit)
    for qubit in range(3):
        operator += 0.23 * (_local(Z, qubit) @ _local(Z, qubit + 1))
    return 0.5 * (operator + operator.conj().T)


def make_ghz_event(*, qubit: int = 2, outcome: int = 0, strength: float = 0.94):
    """Create a deterministic, non-projective GHZ localization event."""
    channel = GRWEventChannel(GRWConfig(seed=23))
    return channel.apply_hit(
        ghz_density(),
        revision_before=0,
        basis="Z",
        qubit=qubit,
        outcome=outcome,
        strength=strength,
    )


def _render_modal_bank(
    frame,
    duration_seconds: float,
    sample_rate: int,
    *,
    amplitude: float,
    grain_rate_hz: float,
    bandwidth_hz: float,
    orientation: tuple[float, float, float],
    branch: int,
    decaying: bool,
    mode_count: int = 48,
) -> np.ndarray:
    sample_count = int(round(duration_seconds * sample_rate))
    t = np.arange(sample_count, dtype=np.float64) / sample_rate
    output = np.zeros(sample_count, dtype=np.float64)
    strongest = np.argsort(frame.gains)[-min(mode_count, frame.resonance_count):]
    weights = frame.gains[strongest].astype(np.float64)
    weight_sum = float(np.sum(np.abs(weights)))
    if weight_sum <= 1.0e-15 or amplitude <= 0.0:
        return np.zeros((sample_count, 2), dtype=np.float64)
    weights /= weight_sum

    x, y, z = orientation
    orientation_phase = y * (np.pi / 2.0) + min(0.0, z) * np.pi
    modulation_index = min(7.5, bandwidth_hz / max(2.0 * grain_rate_hz, 1.0))
    grain_phase = 2.0 * np.pi * grain_rate_hz * t
    grain_envelope = 0.28 + 0.72 * np.square(0.5 + 0.5 * np.cos(grain_phase))

    for weight, index in zip(weights, strongest):
        frequency = float(frame.frequencies_hz[index])
        phase = float(frame.phases_radians[index]) + orientation_phase
        phase_motion = modulation_index * np.sin(grain_phase + 0.37 * index)
        envelope = np.exp(-t / float(frame.decays_seconds[index])) if decaying else 1.0
        axis_shape = np.cos(2.0 * np.pi * frequency * t + phase + phase_motion)
        if abs(x) > 0.5:
            axis_shape += 0.22 * np.cos(4.0 * np.pi * frequency * t + phase)
        output += weight * envelope * axis_shape

    attack = np.minimum(1.0, t / 0.008)
    output *= amplitude * attack * grain_envelope
    pan = float(np.linspace(-0.78, 0.78, 4)[int(branch)])
    left = np.cos((pan + 1.0) * np.pi / 4.0)
    right = np.sin((pan + 1.0) * np.pi / 4.0)
    return np.column_stack((left * output, right * output))


def render_ghz_experiment(
    output_path: str | Path,
    *,
    sample_rate: int = 48_000,
    pre_event_seconds: float = 1.25,
    post_event_seconds: float = 5.0,
    qubit: int = 2,
    outcome: int = 0,
    strength: float = 0.94,
) -> tuple[Path, GRWSonificationFrame]:
    """Render pre-hit GHZ ambience, the hit, and the post-hit resonant body."""
    if sample_rate < 8_000:
        raise ValueError("sample_rate must be at least 8000 Hz")
    if pre_event_seconds < 0.0 or post_event_seconds <= 0.0:
        raise ValueError("durations must be non-negative, with positive post duration")

    event = make_ghz_event(qubit=qubit, outcome=outcome, strength=strength)
    hamiltonian = ghz_demo_hamiltonian()
    maximum_frequency_hz = min(8_000.0, 0.45 * sample_rate)
    sonic = frame_from_grw_event(event)

    pre_frame = density_matrix_to_cnmat_resonators(
        event.rho_before,
        hamiltonian,
        minimum_frequency_hz=30.0,
        maximum_frequency_hz=maximum_frequency_hz,
        total_gain=0.42,
    )
    post_frame = density_matrix_to_cnmat_resonators(
        event.rho_after,
        hamiltonian,
        minimum_frequency_hz=30.0,
        maximum_frequency_hz=maximum_frequency_hz,
        total_gain=0.42,
    )
    before = _render_modal_bank(
        pre_frame,
        pre_event_seconds,
        sample_rate,
        amplitude=0.075,
        grain_rate_hz=4.0,
        bandwidth_hz=18.0,
        orientation=(0.0, 0.0, 1.0),
        branch=qubit,
        decaying=False,
    )
    after = _render_modal_bank(
        post_frame,
        post_event_seconds,
        sample_rate,
        amplitude=sonic.excitation_amplitude,
        grain_rate_hz=4.0 + 48.0 * sonic.grain_structure,
        bandwidth_hz=18.0 + 1_582.0 * sonic.bandwidth,
        orientation=sonic.orientation,
        branch=sonic.branch,
        decaying=True,
    )
    audio = np.vstack((before, after))
    peak = float(np.max(np.abs(audio))) if audio.size else 0.0
    if peak > 0.98:
        audio *= 0.98 / peak
    pcm = np.round(np.clip(audio, -1.0, 1.0) * 32767.0).astype("<i2")

    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(destination), "wb") as wav_file:
        wav_file.setnchannels(2)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(pcm.tobytes())
    return destination, sonic
