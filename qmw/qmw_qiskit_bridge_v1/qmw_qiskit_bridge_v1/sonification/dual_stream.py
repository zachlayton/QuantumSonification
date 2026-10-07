"""Auditable dual-stream sonification of QMW execution comparisons."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import re
import wave
from typing import Any, Mapping

import numpy as np

from ..experiments.floquet_comparison import (
    FloquetComparison,
    RouteTrajectory,
    _trace_distance,
    compare_floquet_routes,
)


SCHEMA = "qmw.dual_stream_sonification.v1"
REFERENCE_ROUTE = "qmw_dense_exact"
DEFAULT_CARRIERS_HZ = (110.0, 137.5, 165.0, 220.0)
DEFAULT_BOND_CARRIERS_HZ = (247.5, 297.0, 371.25)


@dataclass(frozen=True)
class RenderedAudio:
    reference: np.ndarray
    transformed: np.ndarray
    difference: np.ndarray
    difference_local_z: np.ndarray
    difference_bond_zz: np.ndarray
    difference_trace_distance: np.ndarray
    mix: np.ndarray
    sample_rate: int
    global_gain: float


@dataclass(frozen=True)
class DualStreamRender:
    output_directory: Path
    reference_path: Path
    transformed_path: Path
    difference_path: Path
    difference_local_z_path: Path
    difference_bond_zz_path: Path
    difference_trace_distance_path: Path
    mix_path: Path
    metadata_path: Path
    data_path: Path
    metadata: Mapping[str, Any]
    audio: RenderedAudio = None  # type: ignore[assignment]


def _single_pauli(symbol: str, qubit: int) -> np.ndarray:
    table = {
        "I": np.eye(2, dtype=np.complex128),
        "Z": np.asarray([[1, 0], [0, -1]], dtype=np.complex128),
    }
    letters = ["I"] * 4
    letters[3 - qubit] = symbol
    result = np.asarray([[1.0 + 0.0j]])
    for letter in letters:
        result = np.kron(result, table[letter])
    return result


def _observables(route: RouteTrajectory) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    z_operators = [_single_pauli("Z", qubit) for qubit in range(4)]
    bond_operators = [
        z_operators[left] @ z_operators[right]
        for left, right in ((0, 1), (1, 2), (2, 3))
    ]
    local_z = np.asarray(
        [
            [float(np.real(np.trace(rho @ operator))) for operator in z_operators]
            for rho in route.density_matrices
        ]
    )
    bond_zz = np.asarray(
        [
            [float(np.real(np.trace(rho @ operator))) for operator in bond_operators]
            for rho in route.density_matrices
        ]
    )
    purity = np.real(
        np.einsum(
            "tij,tji->t",
            route.density_matrices,
            route.density_matrices,
        )
    )
    return local_z, bond_zz, purity


def _interpolate(values: np.ndarray, positions: np.ndarray) -> np.ndarray:
    ticks = np.arange(values.shape[0], dtype=float)
    if values.ndim == 1:
        return np.interp(positions, ticks, values)
    return np.column_stack(
        [np.interp(positions, ticks, values[:, index]) for index in range(values.shape[1])]
    )


def _equal_power_pan(mono: np.ndarray, pan: float) -> np.ndarray:
    position = float(np.clip(pan, -1.0, 1.0))
    angle = (position + 1.0) * np.pi / 4.0
    return np.column_stack((mono * np.cos(angle), mono * np.sin(angle)))


def _voice_stream(
    local_z: np.ndarray,
    *,
    positions: np.ndarray,
    sample_rate: int,
    carriers_hz: tuple[float, ...],
    pan: float,
) -> np.ndarray:
    interpolated = _interpolate(local_z, positions)
    seconds = np.arange(len(positions), dtype=float) / sample_rate
    mono = np.zeros(len(positions), dtype=float)
    for qubit, frequency in enumerate(carriers_hz):
        # <Z_q> = p(0)-p(1), hence p(0)=(1+<Z_q>)/2.
        population_zero = np.clip((1.0 + interpolated[:, qubit]) * 0.5, 0.0, 1.0)
        amplitude = 0.035 + 0.115 * np.sqrt(population_zero)
        phase = 2.0 * np.pi * frequency * seconds + qubit * np.pi / 7.0
        mono += amplitude * np.sin(phase)
    return _equal_power_pan(mono, pan)


def _difference_streams(
    delta_z: np.ndarray,
    delta_bonds: np.ndarray,
    trace_distance: np.ndarray,
    *,
    positions: np.ndarray,
    sample_rate: int,
    carriers_hz: tuple[float, ...],
    bond_carriers_hz: tuple[float, ...],
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    dz = _interpolate(delta_z, positions)
    db = _interpolate(delta_bonds, positions)
    distance = np.clip(_interpolate(trace_distance, positions), 0.0, 1.0)
    seconds = np.arange(len(positions), dtype=float) / sample_rate
    local_mono = np.zeros(len(positions), dtype=float)
    bond_mono = np.zeros(len(positions), dtype=float)

    # Signed errors retain polarity as a phase inversion; identical routes cancel.
    for qubit, frequency in enumerate(carriers_hz):
        local_mono += 0.18 * dz[:, qubit] * np.sin(
            2.0 * np.pi * (2.0 * frequency) * seconds + qubit * np.pi / 7.0
        )
    for bond, frequency in enumerate(bond_carriers_hz):
        bond_mono += 0.12 * db[:, bond] * np.sin(
            2.0 * np.pi * frequency * seconds + bond * np.pi / 5.0
        )

    # Full-state trace distance controls a deterministic symmetric beating pair.
    # This exposes discrepancies invisible to the selected Z and ZZ observables.
    detune_hz = 28.0 * distance
    phase_low = 2.0 * np.pi * np.cumsum(330.0 - detune_hz) / sample_rate
    phase_high = 2.0 * np.pi * np.cumsum(330.0 + detune_hz) / sample_rate
    trace_mono = 0.11 * distance * (np.sin(phase_low) + np.sin(phase_high))
    local = _equal_power_pan(local_mono, 0.0)
    bonds = _equal_power_pan(bond_mono, 0.0)
    trace = _equal_power_pan(trace_mono, 0.0)
    return local, bonds, trace, local + bonds + trace


def _fade(audio: np.ndarray, sample_rate: int, seconds: float = 0.02) -> np.ndarray:
    result = np.array(audio, copy=True)
    count = min(int(seconds * sample_rate), len(result) // 2)
    if count:
        ramp = np.sin(np.linspace(0.0, np.pi / 2.0, count)) ** 2
        result[:count] *= ramp[:, None]
        result[-count:] *= ramp[::-1, None]
    return result


def _write_wave(path: Path, audio: np.ndarray, sample_rate: int) -> None:
    samples = np.asarray(
        np.round(np.clip(audio, -1.0, 1.0) * 32767.0),
        dtype="<i2",
    )
    with wave.open(str(path), "wb") as output:
        output.setnchannels(2)
        output.setsampwidth(2)
        output.setframerate(sample_rate)
        output.writeframes(samples.tobytes())


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")


def render_dual_stream_sonification(
    output_directory: str | Path,
    *,
    transformed_route: str = "qiskit_trotter_order_2",
    periods: int = 16,
    comparison: FloquetComparison | None = None,
    sample_rate: int = 24_000,
    seconds_per_period: float = 0.4,
    carriers_hz: tuple[float, ...] = DEFAULT_CARRIERS_HZ,
    bond_carriers_hz: tuple[float, ...] = DEFAULT_BOND_CARRIERS_HZ,
) -> DualStreamRender:
    if sample_rate < 8_000:
        raise ValueError("sample_rate must be at least 8000")
    if seconds_per_period <= 0:
        raise ValueError("seconds_per_period must be positive")
    if len(carriers_hz) != 4 or len(bond_carriers_hz) != 3:
        raise ValueError("four local and three bond carriers are required")
    comparison = comparison or compare_floquet_routes(periods=periods)
    try:
        reference = comparison.routes[REFERENCE_ROUTE]
        transformed = comparison.routes[transformed_route]
    except KeyError as exc:
        raise ValueError(
            f"unknown route {exc.args[0]!r}; available routes: "
            f"{', '.join(comparison.routes)}"
        ) from exc
    if len(reference.frames) != len(transformed.frames):
        raise ValueError("reference and transformed routes must share the same ticks")

    exact_z, exact_bonds, exact_purity = _observables(reference)
    transformed_z, transformed_bonds, transformed_purity = _observables(transformed)
    delta_z = transformed_z - exact_z
    delta_bonds = transformed_bonds - exact_bonds
    distances = np.asarray(
        [
            _trace_distance(left, right)
            for left, right in zip(
                transformed.density_matrices, reference.density_matrices
            )
        ]
    )

    period_count = len(reference.frames) - 1
    sample_count = int(round(period_count * seconds_per_period * sample_rate))
    positions = np.arange(sample_count, dtype=float) / (
        sample_rate * seconds_per_period
    )
    reference_audio = _voice_stream(
        exact_z,
        positions=positions,
        sample_rate=sample_rate,
        carriers_hz=carriers_hz,
        pan=-0.65,
    )
    transformed_audio = _voice_stream(
        transformed_z,
        positions=positions,
        sample_rate=sample_rate,
        carriers_hz=carriers_hz,
        pan=0.65,
    )
    (
        difference_local_z,
        difference_bond_zz,
        difference_trace_distance,
        difference_audio,
    ) = _difference_streams(
        delta_z,
        delta_bonds,
        distances,
        positions=positions,
        sample_rate=sample_rate,
        carriers_hz=carriers_hz,
        bond_carriers_hz=bond_carriers_hz,
    )
    reference_audio = _fade(reference_audio, sample_rate)
    transformed_audio = _fade(transformed_audio, sample_rate)
    difference_local_z = _fade(difference_local_z, sample_rate)
    difference_bond_zz = _fade(difference_bond_zz, sample_rate)
    difference_trace_distance = _fade(difference_trace_distance, sample_rate)
    difference_audio = (
        difference_local_z
        + difference_bond_zz
        + difference_trace_distance
    )
    mix = reference_audio + transformed_audio + difference_audio
    peak = float(np.max(np.abs(mix))) if mix.size else 0.0
    global_gain = min(1.0, 0.95 / peak) if peak else 1.0
    reference_audio *= global_gain
    transformed_audio *= global_gain
    difference_audio *= global_gain
    difference_local_z *= global_gain
    difference_bond_zz *= global_gain
    difference_trace_distance *= global_gain
    mix *= global_gain
    audio = RenderedAudio(
        reference_audio,
        transformed_audio,
        difference_audio,
        difference_local_z,
        difference_bond_zz,
        difference_trace_distance,
        mix,
        sample_rate,
        global_gain,
    )

    output = Path(output_directory)
    output.mkdir(parents=True, exist_ok=True)
    slug = _slug(transformed_route)
    reference_path = output / f"{slug}_exact_reference.wav"
    transformed_path = output / f"{slug}_transformed.wav"
    difference_path = output / f"{slug}_difference.wav"
    difference_local_z_path = output / f"{slug}_difference_local_z.wav"
    difference_bond_zz_path = output / f"{slug}_difference_bond_zz.wav"
    difference_trace_distance_path = output / f"{slug}_difference_trace_distance.wav"
    mix_path = output / f"{slug}_dual_stream_mix.wav"
    metadata_path = output / f"{slug}_mapping.json"
    data_path = output / f"{slug}_source_data.npz"
    for path, signal in (
        (reference_path, reference_audio),
        (transformed_path, transformed_audio),
        (difference_path, difference_audio),
        (difference_local_z_path, difference_local_z),
        (difference_bond_zz_path, difference_bond_zz),
        (difference_trace_distance_path, difference_trace_distance),
        (mix_path, mix),
    ):
        _write_wave(path, signal, sample_rate)

    metadata: dict[str, Any] = {
        "schema": SCHEMA,
        "reference_route": REFERENCE_ROUTE,
        "transformed_route": transformed_route,
        "periods": period_count,
        "sample_rate": sample_rate,
        "seconds_per_period": seconds_per_period,
        "duration_seconds": sample_count / sample_rate,
        "basis_order": "|q3 q2 q1 q0>",
        "streams": {
            "reference": {
                "pan": -0.65,
                "mapping": "four fixed carriers; amplitude from sqrt((1+<Z_q>)/2)",
            },
            "transformed": {
                "pan": 0.65,
                "mapping": "identical to reference; transformed density matrices only",
            },
            "difference": {
                "pan": 0.0,
                "mapping": (
                    "signed delta<Z_q> and delta<Z_q Z_(q+1)> as phase-polar voices; "
                    "trace distance as deterministic symmetric beating"
                ),
                "components": {
                    "local_z": "signed delta<Z_q> voices",
                    "bond_zz": "signed neighboring delta<Z_q Z_(q+1)> voices",
                    "trace_distance": "symmetric beating controlled by full-state trace distance",
                },
            },
        },
        "carriers_hz": list(carriers_hz),
        "bond_carriers_hz": list(bond_carriers_hz),
        "global_gain": global_gain,
        "normalization": "one shared safety gain applied to every stem and mix",
        "interpolation": "linear between physical Floquet ticks; carrier phases continuous",
        "metrics": {
            "maximum_trace_distance": float(np.max(distances)),
            "final_trace_distance": float(distances[-1]),
            "maximum_absolute_delta_z": float(np.max(np.abs(delta_z))),
            "maximum_absolute_delta_zz": float(np.max(np.abs(delta_bonds))),
            "final_reference_purity": float(exact_purity[-1]),
            "final_transformed_purity": float(transformed_purity[-1]),
        },
        "files": {
            "reference": reference_path.name,
            "transformed": transformed_path.name,
            "difference": difference_path.name,
            "difference_local_z": difference_local_z_path.name,
            "difference_bond_zz": difference_bond_zz_path.name,
            "difference_trace_distance": difference_trace_distance_path.name,
            "mix": mix_path.name,
            "source_data": data_path.name,
        },
    }
    metadata_path.write_text(
        json.dumps(metadata, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    np.savez_compressed(
        data_path,
        ticks=np.arange(len(reference.frames), dtype=int),
        exact_z=exact_z,
        transformed_z=transformed_z,
        delta_z=delta_z,
        exact_zz_bonds=exact_bonds,
        transformed_zz_bonds=transformed_bonds,
        delta_zz_bonds=delta_bonds,
        trace_distance=distances,
        exact_purity=exact_purity,
        transformed_purity=transformed_purity,
    )
    return DualStreamRender(
        output,
        reference_path,
        transformed_path,
        difference_path,
        difference_local_z_path,
        difference_bond_zz_path,
        difference_trace_distance_path,
        mix_path,
        metadata_path,
        data_path,
        metadata,
        audio,
    )
