#!/usr/bin/env python3
"""
density_matrix_modal_renderer_v2.py

Offline 4-qubit density-matrix modal renderer.

Concept
-------
The wavetable renderer treats a 4-qubit density matrix as a 16 x 16 grid,
which naturally gives 256 complex entries / 256 wavetable samples.

This renderer treats the density matrix more directly as an operator.
At each frame:

    rho(t) -> eigendecomposition -> 16 eigenvalues/eigenvectors -> 16 modes

The eigenvalues determine modal weight. The eigenvectors determine frequency,
phase, stereo position, and brightness. As rho evolves, the modal bank morphs.

This is intentionally independent from the live OSC / Max branch.
It renders directly to a 16-bit PCM WAV file.
"""

from __future__ import annotations

import argparse
import math
import wave
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

try:
    from excitation.hydrogen_orbital_v3 import HydrogenOrbitalSource
except ImportError:
    HydrogenOrbitalSource = None


ExcitationMode = Literal["continuous", "impulse_train", "probabilistic"]


@dataclass
class RenderConfig:
    sample_rate: int = 44_100
    duration_seconds: float = 12.0
    n_qubits: int = 4
    frames_per_second: float = 60.0
    output_path: Path = Path("density_matrix_modal_render_v2.wav")
    seed: int = 11

    excitation_source: str = "internal"
    hydrogen_n: int = 2
    hydrogen_l: int = 1
    hydrogen_m: int = 0
    hydrogen_gain: float = 1.0

    # Quantum evolution controls.
    hamiltonian_scale: float = 1.0
    drive_strength: float = 0.25
    decoherence: float = 0.01

    # Modal synthesis controls.
    base_frequency_hz: float = 55.0
    frequency_spread: float = 5.0
    min_decay_seconds: float = 0.08
    max_decay_seconds: float = 2.50
    modal_gain: float = 0.055
    brightness: float = 0.65
    stereo_width: float = 0.85
    normalize_output: bool = True
    output_ceiling: float = 0.70

    # Excitation controls.
    excitation_mode: ExcitationMode = "continuous"
    impulse_rate_hz: float = 8.0
    probability_threshold: float = 0.18


PAULI_I = np.array([[1, 0], [0, 1]], dtype=np.complex128)
PAULI_X = np.array([[0, 1], [1, 0]], dtype=np.complex128)
PAULI_Y = np.array([[0, -1j], [1j, 0]], dtype=np.complex128)
PAULI_Z = np.array([[1, 0], [0, -1]], dtype=np.complex128)


def kron_all(ops: list[np.ndarray]) -> np.ndarray:
    """Kronecker product of a list of single-qubit operators."""
    out = ops[0]
    for op in ops[1:]:
        out = np.kron(out, op)
    return out


def single_qubit_operator(op: np.ndarray, qubit: int, n_qubits: int) -> np.ndarray:
    """Embed a one-qubit operator into an n-qubit Hilbert space."""
    ops = [PAULI_I for _ in range(n_qubits)]
    ops[qubit] = op
    return kron_all(ops)


def two_qubit_operator(
    op_a: np.ndarray,
    qubit_a: int,
    op_b: np.ndarray,
    qubit_b: int,
    n_qubits: int,
) -> np.ndarray:
    """Embed a two-qubit tensor product operator into an n-qubit Hilbert space."""
    ops = [PAULI_I for _ in range(n_qubits)]
    ops[qubit_a] = op_a
    ops[qubit_b] = op_b
    return kron_all(ops)


def make_hamiltonian(config: RenderConfig, rng: np.random.Generator) -> np.ndarray:
    """
    Build a compact 4-qubit Hamiltonian.

    It combines local Pauli fields, nearest-neighbor couplings, and a weak
    ring closure. Random coefficients are deterministic for a given seed.
    """
    n = config.n_qubits
    dim = 2**n
    h = np.zeros((dim, dim), dtype=np.complex128)

    for q in range(n):
        x = rng.uniform(-0.75, 0.75)
        y = rng.uniform(-0.75, 0.75)
        z = rng.uniform(-0.75, 0.75)
        h += x * single_qubit_operator(PAULI_X, q, n)
        h += y * single_qubit_operator(PAULI_Y, q, n)
        h += z * single_qubit_operator(PAULI_Z, q, n)

    for q in range(n - 1):
        xx = rng.uniform(-0.40, 0.40)
        yy = rng.uniform(-0.30, 0.30)
        zz = rng.uniform(-0.40, 0.40)
        h += xx * two_qubit_operator(PAULI_X, q, PAULI_X, q + 1, n)
        h += yy * two_qubit_operator(PAULI_Y, q, PAULI_Y, q + 1, n)
        h += zz * two_qubit_operator(PAULI_Z, q, PAULI_Z, q + 1, n)

    ring = rng.uniform(-0.25, 0.25)
    h += ring * two_qubit_operator(PAULI_X, n - 1, PAULI_X, 0, n)

    h *= config.hamiltonian_scale
    return 0.5 * (h + h.conj().T)


def initial_density_matrix(n_qubits: int) -> np.ndarray:
    """Start from |0000><0000| as a pure density matrix."""
    dim = 2**n_qubits
    psi = np.zeros(dim, dtype=np.complex128)
    psi[0] = 1.0
    return np.outer(psi, psi.conj())


def unitary_from_hamiltonian(h: np.ndarray, dt: float) -> np.ndarray:
    """Compute U = exp(-i H dt) using Hermitian eigendecomposition."""
    evals, evecs = np.linalg.eigh(h)
    phases = np.exp(-1j * evals * dt)
    return (evecs * phases) @ evecs.conj().T


def dephase_density_matrix(rho: np.ndarray, amount: float) -> np.ndarray:
    """
    Simple dephasing model.

    Diagonal populations are preserved while off-diagonal coherence is
    gradually reduced.
    """
    if amount <= 0.0:
        return rho

    amount = float(np.clip(amount, 0.0, 1.0))
    diag = np.diag(np.diag(rho))
    return (1.0 - amount) * rho + amount * diag


def renormalize_density_matrix(rho: np.ndarray) -> np.ndarray:
    """Restore Hermiticity and trace normalization."""
    rho = 0.5 * (rho + rho.conj().T)
    tr = np.trace(rho)
    if abs(tr) < 1e-12:
        raise ValueError("Density matrix trace collapsed to zero.")
    return rho / tr


def evolve_density_matrix(
    rho: np.ndarray,
    h: np.ndarray,
    t: float,
    dt: float,
    config: RenderConfig,
) -> np.ndarray:
    """Evolve rho by one modal-control frame."""
    slow_drive = math.sin(2.0 * math.pi * 0.053 * t)
    faster_drive = math.sin(2.0 * math.pi * 0.137 * t + 0.5)
    drive = 1.0 + config.drive_strength * (0.65 * slow_drive + 0.35 * faster_drive)

    u = unitary_from_hamiltonian(h * drive, dt)
    rho = u @ rho @ u.conj().T
    rho = dephase_density_matrix(rho, config.decoherence * dt)
    return renormalize_density_matrix(rho)


def density_metrics(rho: np.ndarray) -> dict[str, float]:
    """Return basic density-matrix metrics for synthesis diagnostics."""
    purity = float(np.real(np.trace(rho @ rho)))
    diag = np.real(np.diag(rho))
    diag = np.clip(diag, 1e-12, 1.0)
    entropy = float(-np.sum(diag * np.log2(diag)))
    coherence = float(np.sum(np.abs(rho - np.diag(np.diag(rho)))))
    return {
        "purity": purity,
        "entropy": entropy,
        "coherence": coherence,
    }


def modal_parameters_from_density(
    rho: np.ndarray,
    config: RenderConfig,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Convert density-matrix eigendata into modal synthesis parameters.

    Returns:
        frequencies: shape (16,)
        amplitudes:  shape (16,)
        decays:      shape (16,)
        phases:      shape (16,)
        pans:        shape (16,), -1 left to +1 right
    """
    eigenvalues, eigenvectors = np.linalg.eigh(rho)

    # Sort strongest modes first.
    order = np.argsort(eigenvalues)[::-1]
    eigenvalues = np.clip(eigenvalues[order].real, 0.0, 1.0)
    eigenvectors = eigenvectors[:, order]

    mode_count = len(eigenvalues)
    mode_index = np.arange(mode_count)

    # Frequency model:
    # Start from a harmonic ladder, then bend each mode according to the
    # eigenvector's phase centroid. This makes the modal bank breathe with rho.
    harmonic_ladder = mode_index + 1.0
    phase_centroid = np.angle(np.sum(eigenvectors, axis=0)) / math.pi
    magnitude_centroid = np.sum(np.abs(eigenvectors) * np.arange(1, mode_count + 1)[:, None], axis=0)
    magnitude_centroid /= np.sum(np.abs(eigenvectors), axis=0) + 1e-12

    frequency_bend = 2.0 ** (0.08 * phase_centroid)
    # Center the magnitude bend on the active Hilbert-space dimension. The
    # original 8.5 constant is correct for 16 modes, but shifted smaller modal
    # banks downward (an 8-mode bank is centered on 4.5).
    centroid_center = 0.5 * (mode_count + 1.0)
    inharmonicity = 1.0 + 0.015 * config.frequency_spread * (
        magnitude_centroid - centroid_center
    )
    frequencies = config.base_frequency_hz * harmonic_ladder * frequency_bend * inharmonicity
    frequencies = np.round(frequencies * 8.0) / 8.0
    frequencies = np.clip(frequencies, 20.0, config.sample_rate * 0.45)

    # Eigenvalues are modal weights. Keep the curve conservative: the first
    # pure-state eigenvalue can otherwise dominate and create a harsh drone.
    amplitudes = np.power(eigenvalues + 1e-9, 0.65)
    amplitudes *= config.modal_gain

    # Purity lengthens dominant resonances; entropy/coherence make modes shorter
    # and grainier. This creates a musically useful density-time relation.
    metrics = density_metrics(rho)
    purity = metrics["purity"]
    coherence = metrics["coherence"]
    decay_curve = np.power(eigenvalues + 1e-9, 0.25)
    decays = config.min_decay_seconds + decay_curve * (config.max_decay_seconds - config.min_decay_seconds)
    decays *= 0.65 + 0.70 * purity
    decays /= 1.0 + 0.035 * coherence
    decays = np.clip(decays, config.min_decay_seconds, config.max_decay_seconds)

    # Eigenvector phase supplies oscillator phase.
    phases = np.angle(eigenvectors[0, :])

    # Pan by comparing even/odd basis-state weight in each eigenvector.
    even_weight = np.sum(np.abs(eigenvectors[0::2, :]) ** 2, axis=0)
    odd_weight = np.sum(np.abs(eigenvectors[1::2, :]) ** 2, axis=0)
    pans = config.stereo_width * np.clip(odd_weight - even_weight, -1.0, 1.0)

    # Brightness tilts down upper modes unless brightness is high.
    tilt = 1.0 / np.power(harmonic_ladder, 1.0 - config.brightness)
    amplitudes *= tilt

    return frequencies, amplitudes, decays, phases, pans


def excitation_envelope(
    n_samples: int,
    sample_rate: int,
    t0: float,
    config: RenderConfig,
    source_descriptor=None,
    rng: np.random.Generator | None = None,
    modal_energy: float = 0.0,
) -> np.ndarray:
    """Create an excitation envelope for the current frame."""
    if source_descriptor is not None:
        probability = float(getattr(source_descriptor, "probability", 0.0))
        phase = float(getattr(source_descriptor, "phase", 0.0))
        curvature = float(getattr(source_descriptor, "curvature", 0.0))
        topology = float(getattr(source_descriptor, "topology", 0.0))

        env = np.zeros(n_samples, dtype=np.float64)
        center = int(np.clip(phase, 0.0, 0.999999) * n_samples)
        width = int(np.clip(2 + curvature * 32 + topology * 16, 2, max(2, n_samples // 3)))

        start = max(0, center - width // 2)
        stop = min(n_samples, center + width // 2)

        if stop > start:
            env[start:stop] += np.hanning(stop - start) * probability * config.hydrogen_gain

        return env

    if config.excitation_mode == "continuous":
        return np.ones(n_samples)

    times = t0 + np.arange(n_samples) / sample_rate

    if config.excitation_mode == "impulse_train":
        phase = (times * config.impulse_rate_hz) % 1.0
        impulse = phase < (config.impulse_rate_hz / sample_rate)
        env = np.zeros(n_samples)
        env[impulse] = 1.0
        return env

    if config.excitation_mode == "probabilistic":
        probability = np.clip(modal_energy * config.probability_threshold, 0.0001, 0.25)
        impulse = rng.random(n_samples) < probability / sample_rate
        env = np.zeros(n_samples)
        env[impulse] = 1.0
        return env

    raise ValueError(f"Unsupported excitation mode: {config.excitation_mode}")


def render_modal_frame(
    frequencies: np.ndarray,
    amplitudes: np.ndarray,
    decays: np.ndarray,
    phases: np.ndarray,
    pans: np.ndarray,
    modal_phases: np.ndarray,
    n_samples: int,
    sample_rate: int,
    t0: float,
    excitation: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """Render one modal-control frame as stereo audio."""
    local_t = np.arange(n_samples) / sample_rate
    frame = np.zeros((n_samples, 2), dtype=np.float64)

    new_modal_phases = modal_phases.copy()

    for mode_i, (freq, amp, decay, phase, pan) in enumerate(
        zip(frequencies, amplitudes, decays, phases, pans)
    ):
        envelope = np.exp(-local_t / decay)

        # Continuous mode should be a sustained oscillator, not a convolution
        # of a constant signal with a decay envelope. The earlier behavior
        # caused low-frequency buildup and DC-like glitches.
        if np.all(excitation >= 0.999):
            ring = np.ones_like(local_t)
        elif np.any(excitation > 0.0):
            ring = np.convolve(excitation, envelope, mode="full")[:n_samples]
        else:
            ring = envelope

        phase_inc = 2.0 * math.pi * freq / sample_rate
        phase_series = modal_phases[mode_i] + phase_inc * np.arange(n_samples)
        oscillator = np.sin(phase_series)
        new_modal_phases[mode_i] = (phase_series[-1] + phase_inc) % (2.0 * math.pi)
        signal = amp * ring * oscillator

        left_gain = math.sqrt(0.5 * (1.0 - pan))
        right_gain = math.sqrt(0.5 * (1.0 + pan))
        frame[:, 0] += left_gain * signal
        frame[:, 1] += right_gain * signal

    return frame, new_modal_phases


def render_audio(config: RenderConfig) -> np.ndarray:
    """Render the evolving density-matrix modal bank to stereo float audio."""
    rng = np.random.default_rng(config.seed)
    h = make_hamiltonian(config, rng)
    rho = initial_density_matrix(config.n_qubits)

    hydrogen_source = None
    if config.excitation_source == "hydrogen_orbital":
        if HydrogenOrbitalSource is None:
            raise ImportError("Could not import excitation.hydrogen_orbital_v3")
        hydrogen_source = HydrogenOrbitalSource(
            n=config.hydrogen_n,
            l=config.hydrogen_l,
            m=config.hydrogen_m,
            seed=config.seed,
        )

    total_samples = int(round(config.duration_seconds * config.sample_rate))
    frame_size = max(1, int(round(config.sample_rate / config.frames_per_second)))
    frame_dt = frame_size / config.sample_rate

    audio_chunks: list[np.ndarray] = []
    sample_index = 0
    t = 0.0

    previous_params = None

    modal_phases = np.zeros(2 ** config.n_qubits, dtype=np.float64)

    while sample_index < total_samples:
        this_frame_size = min(frame_size, total_samples - sample_index)

        rho = evolve_density_matrix(rho, h, t, frame_dt, config)
        params = modal_parameters_from_density(rho, config)

        # Smooth modal controls frame-to-frame to avoid zippering.
        if previous_params is not None:
            params = tuple(0.90 * old + 0.10 * new for new, old in zip(params, previous_params))
        previous_params = params

        frequencies, amplitudes, decays, phases, pans = params
        modal_energy = float(np.sum(amplitudes))

        source_descriptor = None
        if hydrogen_source is not None:
            hydrogen_source.step(frame_dt)
            source_descriptor = hydrogen_source.descriptor

        excitation = excitation_envelope(
            this_frame_size,
            config.sample_rate,
            t,
            config,
            source_descriptor=source_descriptor,
            rng=rng,
            modal_energy=modal_energy,
        )

        frame, modal_phases = render_modal_frame(
            frequencies,
            amplitudes,
            decays,
            phases,
            pans,
            modal_phases,
            this_frame_size,
            config.sample_rate,
            t,
            excitation,
        )
        audio_chunks.append(frame)

        sample_index += this_frame_size
        t += frame_dt

    audio = np.concatenate(audio_chunks, axis=0)

    # Remove static DC offset per channel before any normalization.
    audio = audio - np.mean(audio, axis=0, keepdims=True)

    # Simple one-pole DC blocker / very gentle high-pass filter.
    # y[n] = x[n] - x[n-1] + R y[n-1]
    r = 0.995
    filtered = np.zeros_like(audio)
    x_prev = np.zeros(2, dtype=np.float64)
    y_prev = np.zeros(2, dtype=np.float64)
    for i in range(len(audio)):
        x = audio[i]
        y = x - x_prev + r * y_prev
        filtered[i] = y
        x_prev = x
        y_prev = y
    audio = filtered

    # No nonlinear saturation here. tanh was useful as a safety device, but it
    # can create a constant fuzzy/glitchy layer under otherwise clean modes.

    # Safety fade.
    fade_len = min(int(0.015 * config.sample_rate), len(audio) // 2)
    if fade_len > 0:
        fade_in = np.linspace(0.0, 1.0, fade_len)
        fade_out = np.linspace(1.0, 0.0, fade_len)
        audio[:fade_len, :] *= fade_in[:, None]
        audio[-fade_len:, :] *= fade_out[:, None]

    if config.normalize_output:
        peak = np.max(np.abs(audio))
        if peak > 1e-12:
            audio = config.output_ceiling * audio / peak

    return np.clip(audio, -1.0, 1.0)


def float_to_int16(audio: np.ndarray) -> np.ndarray:
    """Convert floating-point audio in [-1, 1] to signed 16-bit PCM."""
    return (np.clip(audio, -1.0, 1.0) * 32767.0).astype(np.int16)


def write_wav(path: Path, audio: np.ndarray, sample_rate: int) -> None:
    """Write stereo int16 WAV."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    pcm = float_to_int16(audio)

    with wave.open(str(path), "wb") as wav_file:
        wav_file.setnchannels(2)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(pcm.tobytes())


def parse_args() -> RenderConfig:
    parser = argparse.ArgumentParser(
        description="Render evolving 4-qubit density matrices as a 16-mode resonator bank."
    )
    parser.add_argument("--output", type=Path, default=Path("density_matrix_modal_render_v2.wav"))
    parser.add_argument("--duration", type=float, default=12.0)
    parser.add_argument("--sample-rate", type=int, default=44_100)
    parser.add_argument("--fps", type=float, default=60.0)
    parser.add_argument("--seed", type=int, default=11)

    parser.add_argument("--hamiltonian-scale", type=float, default=1.0)
    parser.add_argument("--drive-strength", type=float, default=0.25)
    parser.add_argument("--decoherence", type=float, default=0.01)

    parser.add_argument("--base-frequency", type=float, default=55.0)
    parser.add_argument("--frequency-spread", type=float, default=5.0)
    parser.add_argument("--min-decay", type=float, default=0.08)
    parser.add_argument("--max-decay", type=float, default=2.50)
    parser.add_argument("--modal-gain", type=float, default=0.055)
    parser.add_argument("--brightness", type=float, default=0.65)
    parser.add_argument("--stereo-width", type=float, default=0.85)
    parser.add_argument("--no-normalize", action="store_true")
    parser.add_argument("--output-ceiling", type=float, default=0.70)

    parser.add_argument(
        "--excitation-mode",
        choices=["continuous", "impulse_train", "probabilistic"],
        default="continuous",
    )
    parser.add_argument("--impulse-rate", type=float, default=8.0)
    parser.add_argument("--probability-threshold", type=float, default=0.18)
    parser.add_argument(
        "--excitation-source",
        choices=["internal", "hydrogen_orbital"],
        default="internal",
    )
    parser.add_argument("--hydrogen-n", type=int, default=2)
    parser.add_argument("--hydrogen-l", type=int, default=1)
    parser.add_argument("--hydrogen-m", type=int, default=0)
    parser.add_argument("--hydrogen-gain", type=float, default=1.0)

    args = parser.parse_args()

    return RenderConfig(
        sample_rate=args.sample_rate,
        duration_seconds=args.duration,
        frames_per_second=args.fps,
        output_path=args.output,
        seed=args.seed,
        hamiltonian_scale=args.hamiltonian_scale,
        drive_strength=args.drive_strength,
        decoherence=args.decoherence,
        base_frequency_hz=args.base_frequency,
        frequency_spread=args.frequency_spread,
        min_decay_seconds=args.min_decay,
        max_decay_seconds=args.max_decay,
        modal_gain=args.modal_gain,
        brightness=args.brightness,
        stereo_width=args.stereo_width,
        normalize_output=not args.no_normalize,
        output_ceiling=args.output_ceiling,
        excitation_mode=args.excitation_mode,
        impulse_rate_hz=args.impulse_rate,
        probability_threshold=args.probability_threshold,
        excitation_source=args.excitation_source,
        hydrogen_n=args.hydrogen_n,
        hydrogen_l=args.hydrogen_l,
        hydrogen_m=args.hydrogen_m,
        hydrogen_gain=args.hydrogen_gain,
    )


def main() -> None:
    config = parse_args()
    audio = render_audio(config)
    peak = float(np.max(np.abs(audio)))
    rms = float(np.sqrt(np.mean(audio**2)))
    write_wav(config.output_path, audio, config.sample_rate)

    print("Density-matrix modal render complete")
    print(f"  output:          {config.output_path}")
    print(f"  sample rate:     {config.sample_rate} Hz")
    print(f"  duration:        {config.duration_seconds:.3f} seconds")
    print("  channels:        2")
    print(f"  modes:           {2 ** config.n_qubits}")
    print(f"  base frequency:  {config.base_frequency_hz:.3f} Hz")
    print(f"  excitation mode: {config.excitation_mode}")
    print(f"  excitation src:  {config.excitation_source}")
    if config.excitation_source == "hydrogen_orbital":
        print(
            f"  hydrogen:        n={config.hydrogen_n}, "
            f"l={config.hydrogen_l}, m={config.hydrogen_m}, "
            f"gain={config.hydrogen_gain:.3f}"
        )
    print(f"  decoherence:     {config.decoherence:.5f}")
    print(f"  peak:            {peak:.4f}")
    print(f"  rms:             {rms:.4f}")
    print(f"  output ceiling:  {config.output_ceiling:.3f}")


if __name__ == "__main__":
    main()
