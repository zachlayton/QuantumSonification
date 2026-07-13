

#!/usr/bin/env python3
"""
density_matrix_wavetable_renderer_v1.py

Offline 4-qubit density-matrix wavetable renderer.

Concept
-------
A 4-qubit density matrix has shape 16 x 16, giving 256 complex entries.
Each evolved density-matrix frame can therefore be interpreted as a
256-sample wavetable.

This file is intentionally independent from the live OSC / Max branch.
It renders directly to a 16-bit PCM WAV file.

Default mapping
---------------
    real(rho).flatten()  -> left / mono wavetable
    imag(rho).flatten()  -> optional right-channel wavetable

The physical constraints of rho are preserved during evolution:
    trace(rho) = 1
    rho is Hermitian
    rho is positive semidefinite

The audio mapping is representational, not a claim that the density matrix
is itself audio.
"""

from __future__ import annotations

import argparse
import math
import wave
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import numpy as np


MappingMode = Literal["real", "imag", "abs", "phase", "real_imag_stereo"]


@dataclass
class RenderConfig:
    sample_rate: int = 44_100
    duration_seconds: float = 8.0
    fundamental_hz: float = 172.265625  # 44100 / 256, one table per cycle
    n_qubits: int = 4
    wavetable_size: int = 256
    frames_per_second: float = 30.0
    mapping: MappingMode = "real_imag_stereo"
    output_path: Path = Path("density_matrix_wavetable_render_v1.wav")
    seed: int = 7
    hamiltonian_scale: float = 1.0
    drive_strength: float = 0.20
    decoherence: float = 0.015
    normalize_each_table: bool = True
    remove_dc: bool = True


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
    Build a small 4-qubit Hamiltonian.

    It combines:
        - local X/Y/Z fields on each qubit
        - nearest-neighbor XX and ZZ couplings
        - a weak ring coupling between qubit 3 and qubit 0

    The random coefficients are deterministic for a given seed.
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
        xx = rng.uniform(-0.35, 0.35)
        zz = rng.uniform(-0.35, 0.35)
        h += xx * two_qubit_operator(PAULI_X, q, PAULI_X, q + 1, n)
        h += zz * two_qubit_operator(PAULI_Z, q, PAULI_Z, q + 1, n)

    ring = rng.uniform(-0.20, 0.20)
    h += ring * two_qubit_operator(PAULI_X, n - 1, PAULI_X, 0, n)

    h *= config.hamiltonian_scale

    # Numerical hygiene: force Hermitian symmetry.
    return 0.5 * (h + h.conj().T)


def initial_density_matrix(n_qubits: int) -> np.ndarray:
    """
    Start from |0000><0000| as a pure density matrix.
    """
    dim = 2**n_qubits
    psi = np.zeros(dim, dtype=np.complex128)
    psi[0] = 1.0
    return np.outer(psi, psi.conj())


def unitary_from_hamiltonian(h: np.ndarray, dt: float) -> np.ndarray:
    """
    Compute U = exp(-i H dt) using Hermitian eigendecomposition.
    """
    evals, evecs = np.linalg.eigh(h)
    phases = np.exp(-1j * evals * dt)
    return (evecs * phases) @ evecs.conj().T


def dephase_density_matrix(rho: np.ndarray, amount: float) -> np.ndarray:
    """
    Simple representational dephasing model.

    Diagonal probability terms are preserved while off-diagonal coherence
    terms are gently reduced. This is not hardware noise; it is a controllable
    musical/physical model parameter.
    """
    if amount <= 0.0:
        return rho

    amount = float(np.clip(amount, 0.0, 1.0))
    diag = np.diag(np.diag(rho))
    return (1.0 - amount) * rho + amount * diag


def renormalize_density_matrix(rho: np.ndarray) -> np.ndarray:
    """
    Restore Hermiticity and trace normalization after numerical operations.
    """
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
    """
    Evolve rho by one frame.

    A slow sinusoidal drive slightly modulates the Hamiltonian, so the
    wavetable morphs rather than remaining static.
    """
    drive = 1.0 + config.drive_strength * math.sin(2.0 * math.pi * 0.071 * t)
    u = unitary_from_hamiltonian(h * drive, dt)
    rho = u @ rho @ u.conj().T
    rho = dephase_density_matrix(rho, config.decoherence * dt)
    return renormalize_density_matrix(rho)


def table_from_density_matrix(rho: np.ndarray, mode: MappingMode) -> np.ndarray:
    """
    Convert a density matrix into one or two wavetable channels.

    Returns:
        mono:   shape (256,)
        stereo: shape (256, 2)
    """
    if mode == "real":
        return rho.real.flatten()
    if mode == "imag":
        return rho.imag.flatten()
    if mode == "abs":
        return np.abs(rho).flatten()
    if mode == "phase":
        return np.angle(rho).flatten() / math.pi
    if mode == "real_imag_stereo":
        left = rho.real.flatten()
        right = rho.imag.flatten()
        return np.column_stack([left, right])

    raise ValueError(f"Unsupported mapping mode: {mode}")


def condition_table(table: np.ndarray, config: RenderConfig) -> np.ndarray:
    """
    Prepare wavetable values for audio use.

    This removes DC and scales into approximately [-1, 1].
    """
    out = np.asarray(table, dtype=np.float64)

    if config.remove_dc:
        out = out - np.mean(out, axis=0, keepdims=True)

    if config.normalize_each_table:
        peak = np.max(np.abs(out))
        if peak > 1e-12:
            out = out / peak

    return np.clip(out, -1.0, 1.0)


def interpolate_table(table: np.ndarray, phase: np.ndarray) -> np.ndarray:
    """
    Linear wavetable lookup.

    phase is in [0, 1). Supports mono or stereo tables.
    """
    size = table.shape[0]
    position = phase * size
    i0 = np.floor(position).astype(np.int64) % size
    i1 = (i0 + 1) % size
    frac = position - i0

    if table.ndim == 1:
        return (1.0 - frac) * table[i0] + frac * table[i1]

    frac = frac[:, None]
    return (1.0 - frac) * table[i0, :] + frac * table[i1, :]


def render_audio(config: RenderConfig) -> np.ndarray:
    """
    Render the evolving density-matrix wavetable oscillator to float audio.
    """
    rng = np.random.default_rng(config.seed)
    h = make_hamiltonian(config, rng)
    rho = initial_density_matrix(config.n_qubits)

    total_samples = int(round(config.duration_seconds * config.sample_rate))
    frame_size = max(1, int(round(config.sample_rate / config.frames_per_second)))
    frame_dt = frame_size / config.sample_rate

    audio_chunks: list[np.ndarray] = []
    oscillator_phase = 0.0
    sample_index = 0
    t = 0.0

    while sample_index < total_samples:
        this_frame_size = min(frame_size, total_samples - sample_index)

        rho = evolve_density_matrix(rho, h, t, frame_dt, config)
        table = table_from_density_matrix(rho, config.mapping)
        table = condition_table(table, config)

        phase_increment = config.fundamental_hz / config.sample_rate
        phases = (oscillator_phase + phase_increment * np.arange(this_frame_size)) % 1.0
        chunk = interpolate_table(table, phases)
        audio_chunks.append(chunk)

        oscillator_phase = float((phases[-1] + phase_increment) % 1.0)
        sample_index += this_frame_size
        t += frame_dt

    audio = np.concatenate(audio_chunks, axis=0)

    # Very small safety fade to avoid edge clicks.
    fade_len = min(int(0.010 * config.sample_rate), len(audio) // 2)
    if fade_len > 0:
        fade_in = np.linspace(0.0, 1.0, fade_len)
        fade_out = np.linspace(1.0, 0.0, fade_len)
        if audio.ndim == 1:
            audio[:fade_len] *= fade_in
            audio[-fade_len:] *= fade_out
        else:
            audio[:fade_len, :] *= fade_in[:, None]
            audio[-fade_len:, :] *= fade_out[:, None]

    return np.clip(audio, -1.0, 1.0)


def float_to_int16(audio: np.ndarray) -> np.ndarray:
    """Convert floating-point audio in [-1, 1] to signed 16-bit PCM."""
    return (np.clip(audio, -1.0, 1.0) * 32767.0).astype(np.int16)


def write_wav(path: Path, audio: np.ndarray, sample_rate: int) -> None:
    """Write mono or stereo int16 WAV."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    pcm = float_to_int16(audio)
    channels = 1 if pcm.ndim == 1 else pcm.shape[1]

    with wave.open(str(path), "wb") as wav_file:
        wav_file.setnchannels(channels)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(pcm.tobytes())


def parse_args() -> RenderConfig:
    parser = argparse.ArgumentParser(
        description="Render evolving 4-qubit density matrices as 256-point wavetables."
    )
    parser.add_argument("--output", type=Path, default=Path("density_matrix_wavetable_render_v1.wav"))
    parser.add_argument("--duration", type=float, default=8.0)
    parser.add_argument("--sample-rate", type=int, default=44_100)
    parser.add_argument("--fundamental", type=float, default=172.265625)
    parser.add_argument("--fps", type=float, default=30.0)
    parser.add_argument(
        "--mapping",
        choices=["real", "imag", "abs", "phase", "real_imag_stereo"],
        default="real_imag_stereo",
    )
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--hamiltonian-scale", type=float, default=1.0)
    parser.add_argument("--drive-strength", type=float, default=0.20)
    parser.add_argument("--decoherence", type=float, default=0.015)
    parser.add_argument("--no-normalize", action="store_true")
    parser.add_argument("--keep-dc", action="store_true")

    args = parser.parse_args()

    return RenderConfig(
        sample_rate=args.sample_rate,
        duration_seconds=args.duration,
        fundamental_hz=args.fundamental,
        frames_per_second=args.fps,
        mapping=args.mapping,
        output_path=args.output,
        seed=args.seed,
        hamiltonian_scale=args.hamiltonian_scale,
        drive_strength=args.drive_strength,
        decoherence=args.decoherence,
        normalize_each_table=not args.no_normalize,
        remove_dc=not args.keep_dc,
    )


def main() -> None:
    config = parse_args()
    audio = render_audio(config)
    write_wav(config.output_path, audio, config.sample_rate)

    channels = 1 if audio.ndim == 1 else audio.shape[1]
    print("Density-matrix wavetable render complete")
    print(f"  output:      {config.output_path}")
    print(f"  sample rate: {config.sample_rate} Hz")
    print(f"  duration:    {config.duration_seconds:.3f} seconds")
    print(f"  channels:    {channels}")
    print(f"  mapping:     {config.mapping}")
    print(f"  fundamental: {config.fundamental_hz:.6f} Hz")
    print(f"  table size:  {config.wavetable_size} samples")


if __name__ == "__main__":
    main()