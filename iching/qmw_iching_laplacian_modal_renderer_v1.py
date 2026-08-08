#!/usr/bin/env python3
"""
qmw_iching_laplacian_modal_renderer_v1.py

Offline renderer that turns one I Ching consultation's magnetic Laplacian
(see qmw_iching_density_laplacian_bridge_v1.build_control_frame) into a modal
resonator bank, in the same spirit as density_matrix_modal_renderer_v2.py's
rho-eigendecomposition -> modal-bank approach.

Mechanism -- "primary-excited magnetic-Laplacian modal beating"
-----------------------------------------------------------------
This is NOT a reconstruction of graph-wave transport to the transformed
hexagram. It is a modal bank excited by plucking the primary hexagram's
node, with each mode individually decaying and beating. Real transport
requires the *coherent*, signed, cross-node sum

    u_x(t) = sum_k phi_k(x) * conj(phi_k(p)) * cos(sqrt(lambda_k) * t)

evaluated at a specific target node x -- that is what
`graph_wave_transfer_curve()` below computes, and it is the only place in
this file where a "how much reaches the transformed hexagram" claim is
actually justified. The audio engine renders each selected mode as its own
oscillator with a *signed* per-mode envelope (dropping the earlier abs()
that silently discarded the interference between modes), which is honest
about what it is: primary-weighted modal beating, shaped by a damped
(non-conservative, audio-practical) decay law -- not a lossless
reconstruction of the graph wave equation.

Concept
-------
    reading -> magnetic Laplacian on the 64-node hexagram hypercube
            -> eigendecomposition, grouped into numerically degenerate
               clusters so a degenerate eigenspace is never split across
               "selected" and "unselected" (individual eigenvectors within a
               degenerate subspace are basis-dependent; a subspace's total
               projection weight onto the primary node is not)
            -> "pluck" the primary hexagram's node -> per-mode excitation
               coeffs, gauge-invariant weight |phi_k(primary)|^2
            -> K loudest surviving modes -> modal resonator bank
            -> signed cos(sqrt(lambda) * t) envelope per mode (beating, not
               transport)

This is intentionally independent from the live OSC / Max branch, same as
density_matrix_modal_renderer_v2.py. Renders directly to a 16-bit PCM WAV.
"""
from __future__ import annotations

import argparse
import math
import wave
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from qmw_iching_density_laplacian_bridge_v1 import build_control_frame


@dataclass
class RenderConfig:
    sample_rate: int = 44_100
    duration_seconds: float = 14.0
    seed: int | None = None
    depth: int = 3
    output_path: Path = Path("iching_laplacian_render_v1.wav")

    base_frequency_hz: float = 90.0
    mode_count: int = 24
    degeneracy_tol: float = 1e-6  # relative to lambda_max
    ratio_clip: tuple[float, float] = (0.25, 48.0)
    min_decay_seconds: float = 0.6
    max_decay_seconds: float = 6.0
    modal_gain: float = 0.05
    stereo_width: float = 0.9
    output_ceiling: float = 0.70
    normalize_output: bool = True


def _degenerate_clusters(evals: np.ndarray, tol: float) -> list[list[int]]:
    """Group eigenvalue indices into numerically-degenerate clusters."""
    order = np.argsort(evals)
    clusters: list[list[int]] = [[int(order[0])]]
    for idx in order[1:]:
        if evals[idx] - evals[clusters[-1][-1]] < tol:
            clusters[-1].append(int(idx))
        else:
            clusters.append([int(idx)])
    return clusters


def graph_wave_transfer_curve(
    frame,
    laplacian: np.ndarray,
    t: np.ndarray,
) -> dict:
    """
    Rigorous primary -> transformed transport diagnostic. Uses the full
    64-mode coherent, signed sum -- this is the only quantity in this module
    that legitimately supports a "how much reaches the transformed hexagram"
    claim.

        u_x(t) = sum_k phi_k(x) * conj(phi_k(primary)) * cos(sqrt(lambda_k) t)
        P(t)   = |u_transformed(t)|^2

    Returns P(t), its max (excluding the trivial t=0 self-overlap when
    primary == transformed), the first-peak arrival time, and P(0) (survival
    amplitude at the origin node, which is 1 only when primary == transformed).
    """
    evals, evecs = np.linalg.eigh(laplacian)
    coeffs0 = np.conj(evecs[frame.primary, :])  # phi_k*(primary), all 64 modes
    cross = evecs[frame.transformed, :] * coeffs0  # phi_k(transformed) phi_k*(primary)

    sqrt_evals = np.sqrt(np.clip(evals, 0.0, None))
    u = np.array([np.sum(cross * np.cos(sqrt_evals * ti)) for ti in t])
    probability = np.abs(u) ** 2

    search_start = 1 if frame.primary == frame.transformed else 0
    peak_index = search_start + int(np.argmax(probability[search_start:]))

    return {
        "probability": probability,
        "p0": float(probability[0]),
        "max_transfer": float(probability[peak_index]),
        "first_peak_time": float(t[peak_index]),
        "primary_equals_transformed": bool(frame.primary == frame.transformed),
    }


def modal_parameters_from_laplacian(
    frame,
    laplacian: np.ndarray,
    config: RenderConfig,
):
    """
    Convert the magnetic Laplacian's eigendata into modal synthesis
    parameters for a primary-excited beating bank (see module docstring --
    this is NOT the transport reconstruction; see graph_wave_transfer_curve
    for that).

    Returns:
        frequencies: (K,) Hz
        decays:      (K,) seconds
        pans:        (K,) -1..1, Yin/Yang balance
        coeffs0:     (K,) complex, conj(phi_k(primary)) -- signed excitation
        sqrt_evals:  (K,) angular rate used to propagate coeffs0 over time
        retained_weight: fraction of total primary-node excitation weight
                         kept by the K selected modes (report this -- a small
                         mode_count can silently discard most of the reading)
    """
    evals, evecs = np.linalg.eigh(laplacian)

    # Gauge-invariant per-mode weight at the primary node: |phi_k(primary)|^2
    # is unchanged under phi_k -> e^{i theta} phi_k, unlike a bare phase.
    coeffs0_full = np.conj(evecs[frame.primary, :])
    weight_full = np.abs(coeffs0_full) ** 2

    # Select whole degenerate clusters by total weight, never a partial
    # cluster -- individual eigenvectors within a degenerate eigenspace are
    # an arbitrary basis choice of eigh's; the subspace's total projection
    # onto the primary node is not.
    tol = config.degeneracy_tol * max(evals.max(), 1e-12)
    clusters = _degenerate_clusters(evals, tol)
    cluster_weight = [sum(weight_full[i] for i in c) for c in clusters]
    cluster_order = np.argsort(cluster_weight)[::-1]

    selected: list[int] = []
    for ci in cluster_order:
        if len(selected) >= config.mode_count:
            break
        selected.extend(clusters[ci])
    selected = np.array(sorted(selected))

    retained_weight = float(weight_full[selected].sum() / max(weight_full.sum(), 1e-12))

    evals_k = evals[selected]
    evecs_k = evecs[:, selected]
    coeffs0 = coeffs0_full[selected]  # signed/complex, NOT abs()'d

    sqrt_evals = np.sqrt(np.clip(evals_k, 0.0, None))

    # Frequency: sqrt(eigenvalue) is the correct discrete-wave-equation modal
    # rate. Normalize into ratios against the smallest nonzero rate among the
    # selected modes (same move quantum_population_osc_v9_resonator.py makes
    # with Hamiltonian eigenvalue gaps) so every reading yields an audible
    # partial series regardless of the Laplacian's very small,
    # reading-dependent absolute energy scale.
    nonzero = sqrt_evals[sqrt_evals > 1e-9]
    reference_rate = float(nonzero.min()) if len(nonzero) else 1.0
    ratios = sqrt_evals / reference_rate
    ratios = np.clip(ratios, config.ratio_clip[0], config.ratio_clip[1])
    frequencies = config.base_frequency_hz * ratios
    frequencies = np.clip(frequencies, 20.0, config.sample_rate * 0.45)

    # Decay: a damped, non-conservative modification for audio practicality
    # -- higher-frequency modes ring shorter, as in ordinary physical
    # resonators. This does not preserve the graph-wave equation's dynamics;
    # it is a deliberate audio-engineering choice layered on top of it.
    decay_curve = 1.0 / (1.0 + ratios)
    decays = config.min_decay_seconds + decay_curve * (
        config.max_decay_seconds - config.min_decay_seconds
    )

    # Pan by Yin/Yang balance: how much of this mode's weight sits on
    # hexagrams with more Yang (1) lines vs more Yin (0) lines. |evecs_k|^2
    # is a per-node probability, gauge-invariant.
    popcount = np.array([bin(v).count("1") for v in range(64)], dtype=np.float64)
    mode_prob = np.abs(evecs_k) ** 2  # shape (64, K), each column sums to 1
    yang_weight = (mode_prob * (popcount / 6.0)[:, None]).sum(axis=0)
    pans = config.stereo_width * np.clip(2.0 * yang_weight - 1.0, -1.0, 1.0)

    return frequencies, decays, pans, coeffs0, sqrt_evals, retained_weight


def render_audio(config: RenderConfig):
    frame, rho_density, rho_lu, adjacency, laplacian, field = build_control_frame(
        seed=config.seed, depth=config.depth
    )

    frequencies, decays, pans, coeffs0, sqrt_evals, retained_weight = (
        modal_parameters_from_laplacian(frame, laplacian, config)
    )

    n_total = int(config.duration_seconds * config.sample_rate)
    audio = np.zeros((n_total, 2), dtype=np.float64)
    t = np.arange(n_total) / config.sample_rate

    for mode_i in range(len(frequencies)):
        # Signed envelope: Re(conj(phi_k(primary)) * cos(sqrt(lambda_k) t)).
        # Keeping the sign (not abs()) means modes can beat destructively
        # against each other when mixed, which is what lets this be honestly
        # called "modal beating" rather than an arbitrary set of independent
        # decaying tones -- the interference is real, it just isn't targeted
        # at the transformed node the way a true coherent u_x(t) sum would be.
        signed_envelope = np.real(coeffs0[mode_i] * np.cos(sqrt_evals[mode_i] * t))

        ring = np.exp(-t / decays[mode_i])
        envelope = signed_envelope * ring
        peak = np.max(np.abs(envelope))
        if peak > 1e-12:
            envelope = envelope / peak

        # No separate hand-picked oscillator phase: the signed envelope
        # already carries the physically meaningful sign information, so the
        # carrier itself starts at a fixed, arbitrary (and irrelevant) phase.
        oscillator = np.sin(2.0 * math.pi * frequencies[mode_i] * t)
        signal = config.modal_gain * envelope * oscillator

        left_gain = math.sqrt(0.5 * (1.0 - pans[mode_i]))
        right_gain = math.sqrt(0.5 * (1.0 + pans[mode_i]))
        audio[:, 0] += left_gain * signal
        audio[:, 1] += right_gain * signal

    if config.normalize_output:
        peak = np.max(np.abs(audio))
        if peak > 1e-9:
            audio *= config.output_ceiling / peak

    return audio, frame, frequencies, decays, pans, retained_weight


def float_to_int16(audio: np.ndarray) -> np.ndarray:
    return np.clip(audio * 32767.0, -32768, 32767).astype(np.int16)


def write_wav(path: Path, audio: np.ndarray, sample_rate: int) -> None:
    pcm = float_to_int16(audio)
    with wave.open(str(path), "w") as handle:
        handle.setnchannels(2)
        handle.setsampwidth(2)
        handle.setframerate(sample_rate)
        handle.writeframes(pcm.tobytes())


def parse_args() -> RenderConfig:
    parser = argparse.ArgumentParser(description="I Ching magnetic-Laplacian modal renderer")
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--depth", type=int, default=3)
    parser.add_argument("--duration", type=float, default=14.0)
    parser.add_argument("--modes", type=int, default=24)
    parser.add_argument("--base-frequency", type=float, default=90.0)
    parser.add_argument("--output", default="iching_laplacian_render_v1.wav")
    args = parser.parse_args()
    return RenderConfig(
        seed=args.seed,
        depth=args.depth,
        duration_seconds=args.duration,
        mode_count=args.modes,
        base_frequency_hz=args.base_frequency,
        output_path=Path(args.output),
    )


def main() -> None:
    config = parse_args()
    audio, frame, frequencies, decays, pans, retained_weight = render_audio(config)
    write_wav(config.output_path, audio, config.sample_rate)

    _, _, _, _, laplacian, _ = build_control_frame(
        seed=frame.seed, depth=config.depth, revision=frame.revision
    )
    t_diag = np.linspace(0.0, 200.0, 4000)
    transfer = graph_wave_transfer_curve(frame, laplacian, t_diag)

    moving = bin(frame.moving_mask).count("1")
    print(f"seed={frame.seed} primary={frame.primary:06b} transformed={frame.transformed:06b} "
          f"moving_lines={moving}")
    print(f"purity={frame.density_purity:.4f} I(L:U)={frame.mutual_information_bits:.4f} bits")
    print(f"frequency range: {frequencies.min():.1f}-{frequencies.max():.1f} Hz "
          f"decay range: {decays.min():.2f}-{decays.max():.2f} s")
    print(f"retained modal weight: {retained_weight:.4f} "
          f"({'WARNING: below 0.8, mode_count may be too small' if retained_weight < 0.8 else 'ok'})")
    print(f"[honest transport diagnostic, full 64-mode coherent sum]")
    print(f"  P_transformed(0)={transfer['p0']:.4f}  "
          f"max transfer={transfer['max_transfer']:.4f} at t={transfer['first_peak_time']:.2f}"
          + (" (primary == transformed: this is return/survival probability, not transport)"
             if transfer["primary_equals_transformed"] else ""))
    print(f"wrote {config.output_path}")


if __name__ == "__main__":
    main()
