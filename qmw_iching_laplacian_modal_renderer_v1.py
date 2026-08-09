#!/usr/bin/env python3
"""Offline magnetic-Laplacian/Wilson renderer for an I Ching consultation.

The default audio is a node-resonator reading of the full graph-wave transport
from the primary hexagram.  Target-specific transport diagnostics are also
available through :func:`graph_wave_transfer_curve`.

The default instrument treats the 64 hexagrams as the complete Pascal aggregate
of the six-factor Wilson CPS ``1-3-5-7-11-13``.  Exact subset-product ratios set
the node carriers while a finite-width magnetic graph wave
``cos(sqrt(L) t) K |H0>`` supplies their evolving complex amplitudes, with
``K`` a normalized heat-kernel auditory probe centered on H0.  Linear and
logarithmic eigenmode carriers remain available as diagnostic alternatives.

In diagnostic modal mode, degenerate eigenspaces are represented as cluster
voices.  A cluster voice is built from the projector of the primary-node delta
into the whole eigenspace, so excitation weight and Yin/Yang pan do not depend
on the arbitrary basis returned by ``numpy.linalg.eigh`` inside a degenerate
subspace.
"""

from __future__ import annotations

import argparse
from fractions import Fraction
import math
import wave
from dataclasses import dataclass
from math import prod
from pathlib import Path

import numpy as np

from qmw_iching_density_laplacian_bridge_v1 import build_control_frame


@dataclass(frozen=True)
class RenderConfig:
    sample_rate: int = 44_100
    duration_seconds: float = 14.0
    output_path: Path = Path("qmw_iching_laplacian_modal_render_v1.wav")
    seed: int | None = None
    depth: int = 3
    base_frequency_hz: float = 90.0
    mode_count: int = 24
    degeneracy_tol: float = 1e-6
    ratio_clip: tuple[float, float] = (0.25, 256.0)
    maximum_frequency_hz: float = 20_000.0
    frequency_mapping: str = "wilson_cps"
    logarithmic_ratio_scale: float = 1.5
    wilson_generators: tuple[int, ...] = (1, 3, 5, 7, 11, 13)
    wilson_register_octaves: int = 3
    wilson_amplitude_exponent: float = 0.5
    wilson_probe_blur: float = 1.0
    graph_control_rate_hz: float = 200.0
    min_decay_seconds: float = 0.6
    max_decay_seconds: float = 6.0
    modal_gain: float = 0.09
    stereo_width: float = 0.85
    fade_seconds: float = 0.06
    normalize_output: bool = True
    output_ceiling: float = 0.72


def _validate_config(config: RenderConfig) -> None:
    if config.sample_rate <= 0 or config.duration_seconds <= 0:
        raise ValueError("sample rate and duration must be positive")
    if not 1 <= config.mode_count <= 64:
        raise ValueError("mode_count must be between 1 and 64")
    if config.degeneracy_tol < 0:
        raise ValueError("degeneracy_tol must be nonnegative")
    if not 0 < config.ratio_clip[0] <= config.ratio_clip[1]:
        raise ValueError("ratio_clip must contain positive ascending values")
    if config.maximum_frequency_hz <= 0:
        raise ValueError("maximum frequency must be positive")
    if config.frequency_mapping not in ("wilson_cps", "linear", "logarithmic"):
        raise ValueError(
            "frequency mapping must be 'wilson_cps', 'linear', or 'logarithmic'"
        )
    if config.logarithmic_ratio_scale <= 0:
        raise ValueError("logarithmic ratio scale must be positive")
    if (
        len(config.wilson_generators) < 1
        or any(int(value) <= 0 for value in config.wilson_generators)
        or len(set(map(int, config.wilson_generators))) != len(config.wilson_generators)
    ):
        raise ValueError("Wilson generators must be distinct positive integers")
    if config.wilson_register_octaves < 1:
        raise ValueError("Wilson register octaves must be positive")
    if not 0 < config.wilson_amplitude_exponent <= 1:
        raise ValueError("Wilson amplitude exponent must lie in (0, 1]")
    if config.wilson_probe_blur < 0:
        raise ValueError("Wilson probe blur must be nonnegative")
    if config.graph_control_rate_hz <= 0:
        raise ValueError("graph control rate must be positive")
    if config.fade_seconds < 0:
        raise ValueError("fade duration must be nonnegative")
    if not 0 < config.min_decay_seconds <= config.max_decay_seconds:
        raise ValueError("decay bounds must be positive and ascending")


def _validate_laplacian(laplacian: np.ndarray) -> np.ndarray:
    matrix = np.asarray(laplacian, dtype=np.complex128)
    if matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1]:
        raise ValueError("laplacian must be a square matrix")
    if not np.allclose(matrix, matrix.conj().T, atol=1e-9, rtol=1e-9):
        raise ValueError("laplacian must be Hermitian")
    return 0.5 * (matrix + matrix.conj().T)


def _degenerate_clusters(evals: np.ndarray, tol: float) -> list[list[int]]:
    """Group sorted eigenvalue indices whose adjacent gaps are below ``tol``."""
    values = np.asarray(evals, dtype=float)
    if values.ndim != 1 or len(values) == 0:
        raise ValueError("evals must be a nonempty one-dimensional array")
    order = np.argsort(values)
    clusters: list[list[int]] = [[int(order[0])]]
    for raw_index in order[1:]:
        index = int(raw_index)
        if values[index] - values[clusters[-1][-1]] <= tol:
            clusters[-1].append(index)
        else:
            clusters.append([index])
    return clusters


@dataclass(frozen=True)
class WilsonHexagramTone:
    """One exact CPS carrier assigned to one six-line hexagram node."""

    hexagram: int
    grade: int
    factors: tuple[int, ...]
    ratio_numerator: int
    ratio_denominator: int
    register: int
    frequency_hz: float
    pan: float

    @property
    def ratio(self) -> float:
        return self.ratio_numerator / self.ratio_denominator


def _period_fold(value: Fraction, period: int = 2) -> Fraction:
    if value <= 0 or period <= 1:
        raise ValueError("ratio must be positive and period greater than one")
    while value < 1:
        value *= period
    while value >= period:
        value /= period
    return value


def wilson_hexagram_tuning(
    config: RenderConfig,
    dimension: int = 64,
) -> tuple[WilsonHexagramTone, ...]:
    """Return the exact all-grades Wilson tuning field for the graph nodes.

    A node bit selects its corresponding generator.  Hamming weight therefore
    selects one shell of the six-factor Pascal aggregate, whose dimensions are
    ``1, 6, 15, 20, 15, 6, 1``.  Period folding changes only register; the
    subset-product identity remains exact and is retained as a fraction.
    """
    _validate_config(config)
    generators = tuple(map(int, config.wilson_generators))
    expected_dimension = 1 << len(generators)
    if dimension != expected_dimension:
        raise ValueError(
            f"Wilson field with {len(generators)} generators requires "
            f"{expected_dimension} nodes; got {dimension}"
        )
    reference = max(generators)
    line_count = len(generators)
    safe_ceiling = min(config.maximum_frequency_hz, config.sample_rate * 0.49)
    tones = []
    for node in range(dimension):
        factors = tuple(
            generators[line] for line in range(line_count) if node & (1 << line)
        )
        grade = len(factors)
        ratio = _period_fold(Fraction(prod(factors) if factors else 1, reference))
        register = (
            grade * (config.wilson_register_octaves - 1) + line_count // 2
        ) // line_count
        frequency = config.base_frequency_hz * float(ratio) * (2.0 ** register)
        frequency = float(np.clip(frequency, 20.0, safe_ceiling))

        # Lower-vs-upper trigram balance gives the stereo field a real I Ching
        # axis while leaving all-yin and all-yang centered.
        split = line_count // 2
        lower = sum((node >> line) & 1 for line in range(split)) / max(1, split)
        upper = sum((node >> line) & 1 for line in range(split, line_count)) / max(
            1, line_count - split
        )
        pan = float(np.clip(config.stereo_width * (upper - lower), -1.0, 1.0))
        tones.append(
            WilsonHexagramTone(
                hexagram=node,
                grade=grade,
                factors=factors,
                ratio_numerator=ratio.numerator,
                ratio_denominator=ratio.denominator,
                register=int(register),
                frequency_hz=frequency,
                pan=pan,
            )
        )
    return tuple(tones)


def wilson_node_parameters_from_laplacian(
    frame,
    laplacian: np.ndarray,
    config: RenderConfig,
) -> tuple[
    tuple[WilsonHexagramTone, ...], np.ndarray, np.ndarray, np.ndarray, np.ndarray, float
]:
    """Select active Wilson nodes and return their full graph-wave envelopes.

    Selection uses mean node activity over the requested render, computed from
    the full spectrum and the H0-centered auditory probe.  It therefore does
    not depend on an arbitrary basis in
    a degenerate eigenspace.  ``retained_activity`` is the selected share of
    total mean squared graph-wave displacement.
    """
    _validate_config(config)
    if config.frequency_mapping != "wilson_cps":
        raise ValueError("Wilson node parameters require frequency_mapping='wilson_cps'")
    matrix = _validate_laplacian(laplacian)
    dimension = matrix.shape[0]
    primary = int(frame.primary)
    if not 0 <= primary < dimension:
        raise ValueError("primary node falls outside the Laplacian")
    tuning = wilson_hexagram_tuning(config, dimension)

    evals, evecs = np.linalg.eigh(matrix)
    sqrt_evals = np.sqrt(np.clip(evals.real, 0.0, None))
    control_count = max(
        2, int(math.ceil(config.duration_seconds * config.graph_control_rate_hz)) + 1
    )
    control_times = np.linspace(0.0, config.duration_seconds, control_count)
    # A literal delta displacement makes exactly one node carrier nonzero at
    # onset, which collapses the auditory image to one pitch.  The sonification
    # probe is therefore a normalized heat-kernel localization around H0.  It
    # remains centered on H0, uses only L, and is identical for C and I.
    maximum_eigenvalue = float(np.max(evals)) if len(evals) else 0.0
    if maximum_eigenvalue > 1e-15 and config.wilson_probe_blur > 0:
        probe_filter = np.exp(
            -config.wilson_probe_blur * evals / maximum_eigenvalue
        )
    else:
        probe_filter = np.ones_like(evals)
    spectral_probe = probe_filter * np.conj(evecs[primary, :])
    probe_norm = float(np.linalg.norm(spectral_probe))
    if probe_norm > 1e-15:
        spectral_probe /= probe_norm
    spectral_excitation = spectral_probe[:, None]
    wave = evecs @ (
        spectral_excitation * np.cos(np.outer(sqrt_evals, control_times))
    )
    activity = np.mean(np.abs(wave) ** 2, axis=1)
    selected_nodes = np.argsort(-activity, kind="stable")[: config.mode_count]
    selected_nodes = np.asarray(sorted(map(int, selected_nodes)), dtype=np.int64)
    selected_tones = tuple(tuning[node] for node in selected_nodes)
    selected_wave = wave[selected_nodes, :]

    total_activity = float(np.sum(activity))
    retained = (
        float(np.sum(activity[selected_nodes]) / total_activity)
        if total_activity > 1e-15
        else 1.0
    )

    # Node voices must remain alive long enough for graph transport to reach
    # them.  Modal-rate damping (often below 1.2 s here) silences destination
    # nodes before the physically computed 5-11 s transfer peaks.  The Wilson
    # bank therefore uses one common slow damping constant; all internal motion
    # still comes from the unmodified graph wave.
    decays = np.full(len(selected_nodes), config.max_decay_seconds, dtype=float)
    frequencies = np.asarray([tone.frequency_hz for tone in selected_tones], dtype=float)
    pans = np.asarray([tone.pan for tone in selected_tones], dtype=float)
    return selected_tones, frequencies, decays, pans, selected_wave, retained


def graph_wave_transfer_curve(frame, laplacian: np.ndarray, t: np.ndarray) -> dict:
    """Return rigorous full-spectrum primary-to-transformed wave transport.

    For zero initial velocity and a delta displacement at primary node ``p``::

        u_x(t) = sum_k phi_k(x) conj(phi_k(p)) cos(sqrt(lambda_k) t)

    The returned probability is ``abs(u_transformed(t))**2``.  ``first_peak``
    is the first local maximum after the initial sample; ``max_transfer`` is
    independently the largest sampled value in the diagnostic window.
    """
    matrix = _validate_laplacian(laplacian)
    times = np.asarray(t, dtype=np.float64)
    if times.ndim != 1 or len(times) < 2 or np.any(np.diff(times) <= 0):
        raise ValueError("t must be a strictly increasing one-dimensional array")
    dimension = matrix.shape[0]
    primary, transformed = int(frame.primary), int(frame.transformed)
    if not (0 <= primary < dimension and 0 <= transformed < dimension):
        raise ValueError("frame nodes fall outside the Laplacian")

    evals, evecs = np.linalg.eigh(matrix)
    sqrt_evals = np.sqrt(np.clip(evals.real, 0.0, None))
    cross = evecs[transformed, :] * np.conj(evecs[primary, :])
    amplitude = cross @ np.cos(np.outer(sqrt_evals, times))
    probability = np.abs(amplitude) ** 2

    search_start = 1 if primary == transformed else 0
    max_index = search_start + int(np.argmax(probability[search_start:]))
    local = np.flatnonzero(
        (probability[1:-1] >= probability[:-2])
        & (probability[1:-1] > probability[2:])
    ) + 1
    local = local[local >= max(1, search_start)]
    first_index = int(local[0]) if len(local) else max_index

    return {
        "time": times,
        "amplitude": amplitude,
        "probability": probability,
        "p0": float(probability[0]),
        "first_peak_time": float(times[first_index]),
        "first_peak_transfer": float(probability[first_index]),
        "max_transfer": float(probability[max_index]),
        "max_transfer_time": float(times[max_index]),
        "primary_equals_transformed": primary == transformed,
    }


def modal_parameters_from_laplacian(
    frame,
    laplacian: np.ndarray,
    config: RenderConfig,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, float]:
    """Derive basis-invariant, primary-excited cluster voices.

    ``mode_count`` is an eigen-dimension budget.  Selection proceeds by total
    primary-node projector weight and never splits a degenerate cluster.  One
    audible voice represents each selected cluster.

    Returns ``frequencies, decays, pans, coefficients, sqrt_eigenvalues,
    retained_weight``.  Coefficients are nonnegative cluster-projection norms;
    the sign in each voice comes from ``cos(sqrt(lambda) * t)``.
    """
    _validate_config(config)
    if config.frequency_mapping == "wilson_cps":
        raise ValueError(
            "modal parameters are diagnostic only; choose linear or logarithmic, "
            "or use wilson_node_parameters_from_laplacian"
        )
    matrix = _validate_laplacian(laplacian)
    dimension = matrix.shape[0]
    primary = int(frame.primary)
    if not 0 <= primary < dimension:
        raise ValueError("primary node falls outside the Laplacian")

    evals, evecs = np.linalg.eigh(matrix)
    evals = np.clip(evals.real, 0.0, None)
    tolerance = config.degeneracy_tol * max(float(evals.max()), 1e-12)
    clusters = _degenerate_clusters(evals, tolerance)
    delta = np.zeros(dimension, dtype=np.complex128)
    delta[primary] = 1.0

    records = []
    popcount = np.array([int(index).bit_count() for index in range(dimension)], dtype=float)
    line_count = max(1, int(round(math.log2(dimension))))
    yin_yang_axis = 2.0 * popcount / line_count - 1.0

    for cluster in clusters:
        vectors = evecs[:, cluster]
        projected = vectors @ (vectors.conj().T @ delta)
        weight = float(np.vdot(projected, projected).real)
        if weight > 1e-15:
            distribution = np.abs(projected) ** 2 / weight
            pan = config.stereo_width * float(np.dot(distribution, yin_yang_axis))
        else:
            pan = 0.0
        records.append({
            "indices": cluster,
            "eigenvalue": float(np.mean(evals[cluster])),
            "weight": max(0.0, weight),
            "coefficient": math.sqrt(max(0.0, weight)),
            "pan": float(np.clip(pan, -1.0, 1.0)),
        })

    selected = []
    dimensions_used = 0
    for record in sorted(records, key=lambda item: item["weight"], reverse=True):
        if dimensions_used >= config.mode_count:
            break
        selected.append(record)
        dimensions_used += len(record["indices"])
    selected.sort(key=lambda item: item["eigenvalue"])

    eigenvalues = np.array([item["eigenvalue"] for item in selected])
    sqrt_evals = np.sqrt(np.clip(eigenvalues, 0.0, None))
    coefficients = np.array([item["coefficient"] for item in selected])
    pans = np.array([item["pan"] for item in selected])
    retained_weight = float(sum(item["weight"] for item in selected))

    # ``tolerance`` is expressed in eigenvalue units.  Comparing it directly
    # with sqrt(lambda) incorrectly promotes numerical near-zero modes into the
    # frequency reference, forcing all physical modes into ``ratio_clip``'s
    # upper ceiling.  Classify zero modes before taking the square root.
    resolved = eigenvalues > max(1e-12, tolerance)
    nonzero = sqrt_evals[resolved]
    reference = float(nonzero.min()) if len(nonzero) else 1.0
    physical_ratios = sqrt_evals / reference
    if config.frequency_mapping == "logarithmic":
        mapped = 1.0 + config.logarithmic_ratio_scale * np.log2(
            np.maximum(physical_ratios, 1.0)
        )
    else:
        mapped = physical_ratios
    audible_ratios = np.where(resolved, mapped, 1.0)
    audible_ratios = np.clip(audible_ratios, *config.ratio_clip)
    frequencies = config.base_frequency_hz * audible_ratios
    safe_ceiling = min(config.maximum_frequency_hz, config.sample_rate * 0.49)
    frequencies = np.clip(frequencies, 20.0, safe_ceiling)

    decay_curve = 1.0 / (1.0 + physical_ratios)
    decays = config.min_decay_seconds + decay_curve * (
        config.max_decay_seconds - config.min_decay_seconds
    )
    return frequencies, decays, pans, coefficients, sqrt_evals, retained_weight


def render_audio(
    config: RenderConfig,
) -> tuple[np.ndarray, object, np.ndarray, np.ndarray, np.ndarray, float]:
    """Cast and render one damped primary-excited modal-beating bank."""
    _validate_config(config)
    frame, _rho, _rho_lu, _adjacency, laplacian, _field = build_control_frame(
        seed=config.seed, depth=config.depth
    )
    audio, frequencies, decays, pans, retained = render_audio_from_frame(
        frame, laplacian, config
    )
    return audio, frame, frequencies, decays, pans, retained


def render_audio_from_frame(
    frame,
    laplacian: np.ndarray,
    config: RenderConfig,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, float]:
    """Render an already-frozen consultation without casting a second reading."""
    _validate_config(config)
    if config.frequency_mapping == "wilson_cps":
        return _render_wilson_audio_from_frame(frame, laplacian, config)

    frequencies, decays, pans, coefficients, sqrt_evals, retained = (
        modal_parameters_from_laplacian(frame, laplacian, config)
    )

    n_total = int(round(config.duration_seconds * config.sample_rate))
    t = np.arange(n_total, dtype=np.float64) / config.sample_rate
    audio = np.zeros((n_total, 2), dtype=np.float64)

    for frequency, decay, pan, coefficient, graph_rate in zip(
        frequencies, decays, pans, coefficients, sqrt_evals
    ):
        signed_envelope = coefficient * np.cos(graph_rate * t)
        damped_envelope = signed_envelope * np.exp(-t / decay)
        carrier = np.sin(2.0 * math.pi * frequency * t)
        signal = config.modal_gain * damped_envelope * carrier
        left_gain = math.sqrt(0.5 * (1.0 - pan))
        right_gain = math.sqrt(0.5 * (1.0 + pan))
        audio[:, 0] += left_gain * signal
        audio[:, 1] += right_gain * signal

    audio -= np.mean(audio, axis=0, keepdims=True)
    _apply_fade(audio, config)
    if config.normalize_output:
        peak = float(np.max(np.abs(audio)))
        if peak > 1e-12:
            audio *= config.output_ceiling / peak
    return np.clip(audio, -1.0, 1.0), frequencies, decays, pans, retained


def _render_wilson_audio_from_frame(
    frame,
    laplacian: np.ndarray,
    config: RenderConfig,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, float]:
    """Render exact Wilson carriers under complex graph-wave envelopes."""
    tones, frequencies, decays, pans, control_wave, retained = (
        wilson_node_parameters_from_laplacian(frame, laplacian, config)
    )
    auditory_wave = _compress_complex_activity(
        control_wave, config.wilson_amplitude_exponent
    )
    n_total = int(round(config.duration_seconds * config.sample_rate))
    t = np.arange(n_total, dtype=np.float64) / config.sample_rate
    control_times = np.linspace(0.0, config.duration_seconds, auditory_wave.shape[1])
    audio = np.zeros((n_total, 2), dtype=np.float64)

    for tone, frequency, decay, pan, node_wave in zip(
        tones, frequencies, decays, pans, auditory_wave
    ):
        wave_real = np.interp(t, control_times, node_wave.real)
        wave_imag = np.interp(t, control_times, node_wave.imag)
        carrier_phase = 2.0 * math.pi * frequency * t
        # Im(u_h(t) exp(i 2 pi f_h t)) turns the magnetic graph phase into
        # oscillator phase without reinterpreting it as pitch deviation.
        signal = config.modal_gain * np.exp(-t / decay) * (
            wave_real * np.sin(carrier_phase) + wave_imag * np.cos(carrier_phase)
        )
        left_gain = math.sqrt(0.5 * (1.0 - pan))
        right_gain = math.sqrt(0.5 * (1.0 + pan))
        audio[:, 0] += left_gain * signal
        audio[:, 1] += right_gain * signal

    audio -= np.mean(audio, axis=0, keepdims=True)
    _apply_fade(audio, config)
    if config.normalize_output:
        peak = float(np.max(np.abs(audio)))
        if peak > 1e-12:
            audio *= config.output_ceiling / peak
    return np.clip(audio, -1.0, 1.0), frequencies, decays, pans, retained


def _compress_complex_activity(wave: np.ndarray, exponent: float) -> np.ndarray:
    """Compress node magnitudes while preserving phase and per-frame L2 energy."""
    values = np.asarray(wave, dtype=np.complex128)
    magnitudes = np.abs(values)
    compressed_magnitudes = np.where(
        magnitudes > 1e-12, magnitudes ** float(exponent), 0.0
    )
    phases = np.divide(
        values,
        magnitudes,
        out=np.zeros_like(values),
        where=magnitudes > 1e-12,
    )
    raw_norm = np.sqrt(np.sum(magnitudes ** 2, axis=0, keepdims=True))
    compressed_norm = np.sqrt(
        np.sum(compressed_magnitudes ** 2, axis=0, keepdims=True)
    )
    scale = np.divide(
        raw_norm,
        compressed_norm,
        out=np.zeros_like(raw_norm),
        where=compressed_norm > 1e-15,
    )
    return phases * compressed_magnitudes * scale


def _apply_fade(audio: np.ndarray, config: RenderConfig) -> None:
    """Apply a click-safe equal-power attack and release in place."""
    fade_length = min(int(config.fade_seconds * config.sample_rate), len(audio) // 2)
    if not fade_length:
        return
    fade = np.sin(np.linspace(0.0, math.pi / 2.0, fade_length)) ** 2
    audio[:fade_length] *= fade[:, None]
    audio[-fade_length:] *= fade[::-1, None]


def float_to_int16(audio: np.ndarray) -> np.ndarray:
    return (np.clip(audio, -1.0, 1.0) * 32767.0).astype(np.int16)


def write_wav(path: Path, audio: np.ndarray, sample_rate: int) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(destination), "wb") as wav_file:
        wav_file.setnchannels(2)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(float_to_int16(audio).tobytes())


def parse_args() -> RenderConfig:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=RenderConfig.output_path)
    parser.add_argument("--duration", type=float, default=RenderConfig.duration_seconds)
    parser.add_argument("--sample-rate", type=int, default=RenderConfig.sample_rate)
    parser.add_argument("--seed", type=int)
    parser.add_argument("--depth", type=int, default=RenderConfig.depth)
    parser.add_argument("--base-frequency", type=float, default=RenderConfig.base_frequency_hz)
    parser.add_argument("--maximum-frequency", type=float, default=RenderConfig.maximum_frequency_hz)
    parser.add_argument(
        "--frequency-mapping", choices=("wilson_cps", "linear", "logarithmic"),
        default=RenderConfig.frequency_mapping,
    )
    parser.add_argument(
        "--logarithmic-ratio-scale", type=float,
        default=RenderConfig.logarithmic_ratio_scale,
    )
    parser.add_argument(
        "--wilson-generators", type=int, nargs="+",
        default=RenderConfig.wilson_generators,
    )
    parser.add_argument(
        "--wilson-register-octaves", type=int,
        default=RenderConfig.wilson_register_octaves,
    )
    parser.add_argument(
        "--wilson-amplitude-exponent", type=float,
        default=RenderConfig.wilson_amplitude_exponent,
    )
    parser.add_argument(
        "--wilson-probe-blur", type=float,
        default=RenderConfig.wilson_probe_blur,
    )
    parser.add_argument(
        "--graph-control-rate", type=float,
        default=RenderConfig.graph_control_rate_hz,
    )
    parser.add_argument("--modes", type=int, default=RenderConfig.mode_count)
    parser.add_argument("--degeneracy-tol", type=float, default=RenderConfig.degeneracy_tol)
    parser.add_argument("--min-decay", type=float, default=RenderConfig.min_decay_seconds)
    parser.add_argument("--max-decay", type=float, default=RenderConfig.max_decay_seconds)
    parser.add_argument("--modal-gain", type=float, default=RenderConfig.modal_gain)
    parser.add_argument("--stereo-width", type=float, default=RenderConfig.stereo_width)
    parser.add_argument("--fade", type=float, default=RenderConfig.fade_seconds)
    parser.add_argument("--output-ceiling", type=float, default=RenderConfig.output_ceiling)
    parser.add_argument("--no-normalize", action="store_true")
    args = parser.parse_args()
    return RenderConfig(
        sample_rate=args.sample_rate,
        duration_seconds=args.duration,
        output_path=args.output,
        seed=args.seed,
        depth=args.depth,
        base_frequency_hz=args.base_frequency,
        maximum_frequency_hz=args.maximum_frequency,
        frequency_mapping=args.frequency_mapping,
        logarithmic_ratio_scale=args.logarithmic_ratio_scale,
        wilson_generators=tuple(args.wilson_generators),
        wilson_register_octaves=args.wilson_register_octaves,
        wilson_amplitude_exponent=args.wilson_amplitude_exponent,
        wilson_probe_blur=args.wilson_probe_blur,
        graph_control_rate_hz=args.graph_control_rate,
        mode_count=args.modes,
        degeneracy_tol=args.degeneracy_tol,
        min_decay_seconds=args.min_decay,
        max_decay_seconds=args.max_decay,
        modal_gain=args.modal_gain,
        stereo_width=args.stereo_width,
        fade_seconds=args.fade,
        normalize_output=not args.no_normalize,
        output_ceiling=args.output_ceiling,
    )


def main() -> None:
    config = parse_args()
    audio, frame, frequencies, decays, pans, retained = render_audio(config)
    write_wav(config.output_path, audio, config.sample_rate)
    _, _, _, _, laplacian, _ = build_control_frame(
        seed=frame.seed, depth=config.depth, revision=frame.revision
    )
    diagnostic_time = np.linspace(0.0, 200.0, 4000)
    transfer = graph_wave_transfer_curve(frame, laplacian, diagnostic_time)
    moving_count = int(frame.moving_mask).bit_count()
    print("QMW I Ching magnetic-Laplacian/Wilson render complete")
    print(f"  output: {config.output_path}")
    print(f"  seed={frame.seed} H0={frame.primary:06b} M={frame.moving_mask:06b} "
          f"H1={frame.transformed:06b} moving_lines={moving_count}")
    voice_label = "Wilson hexagram nodes" if config.frequency_mapping == "wilson_cps" else "clusters"
    print(f"  {voice_label}={len(frequencies)} frequency={frequencies.min():.1f}-"
          f"{frequencies.max():.1f} Hz decay={decays.min():.2f}-{decays.max():.2f} s")
    warning = "WARNING: increase --modes" if retained < 0.8 else "ok"
    retained_label = (
        "graph-wave node activity"
        if config.frequency_mapping == "wilson_cps"
        else "primary excitation weight"
    )
    print(f"  retained {retained_label}={retained:.4f} ({warning})")
    label = "return/survival" if transfer["primary_equals_transformed"] else "transport"
    print(f"  full-spectrum {label}: P(0)={transfer['p0']:.4f} "
          f"first peak={transfer['first_peak_transfer']:.4f} at "
          f"t={transfer['first_peak_time']:.2f}; max={transfer['max_transfer']:.4f} "
          f"at t={transfer['max_transfer_time']:.2f}")


if __name__ == "__main__":
    main()
