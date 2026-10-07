"""Quantum-field propagator impulse responses for downstream convolution."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
import math
from pathlib import Path
from typing import Any

import numpy as np
from scipy.signal import fftconvolve, resample_poly
import soundfile as sf

from .model import ScalarFieldModel
from .schema import ScalarFieldFrame


@dataclass(frozen=True)
class QuantumFieldIRSpec:
    sample_rate: int = 48_000
    duration_seconds: float = 2.5
    root_hz: float = 72.0
    decay_seconds: float = 1.2
    source_site: int = 4
    correlation_depth: float = 0.35
    geometry_ir_path: str | None = None
    geometry_mix: float = 0.55

    def __post_init__(self) -> None:
        if int(self.sample_rate) != self.sample_rate or self.sample_rate < 8_000:
            raise ValueError("sample_rate must be an integer of at least 8000")
        positive = (self.duration_seconds, self.root_hz, self.decay_seconds)
        if not np.isfinite(positive).all() or min(positive) <= 0.0:
            raise ValueError("duration, root frequency, and decay must be positive")
        if not 0.0 <= self.correlation_depth <= 1.0:
            raise ValueError("correlation_depth must lie in [0, 1]")
        if not 0.0 <= self.geometry_mix <= 1.0:
            raise ValueError("geometry_mix must lie in [0, 1]")


@dataclass(frozen=True)
class QuantumFieldIRArtifact:
    audio: np.ndarray
    metadata: dict[str, Any]


def _equal_power_site_readout(sites: int) -> tuple[np.ndarray, np.ndarray]:
    pan = np.linspace(-1.0, 1.0, sites)
    left = np.cos(0.25 * math.pi * (pan + 1.0))
    right = np.sin(0.25 * math.pi * (pan + 1.0))
    return left, right


def _normalize_for_convolution(
    audio: np.ndarray, *, transfer_ceiling: float = 0.8
) -> tuple[np.ndarray, dict[str, float]]:
    """Bound maximum filter gain rather than individual IR sample peaks."""

    value = np.asarray(audio, dtype=float)
    if value.ndim != 2 or value.shape[1] != 2 or not np.isfinite(value).all():
        raise ValueError("convolution IR must be finite stereo audio")
    if not 0.0 < transfer_ceiling <= 1.0:
        raise ValueError("transfer_ceiling must lie in (0, 1]")
    # Extra zero padding samples the response densely enough to catch narrow
    # resonant peaks between the native DFT bins.
    fft_size = 1 << max(1, (2 * len(value) - 1).bit_length())
    response = np.fft.rfft(value, n=fft_size, axis=0)
    maximum_transfer = float(np.max(np.abs(response)))
    scale = (
        transfer_ceiling / maximum_transfer
        if maximum_transfer > 1e-15
        else 1.0
    )
    normalized = value * scale
    verified = np.fft.rfft(normalized, n=fft_size, axis=0)
    return normalized, {
        "pre_normalization_max_transfer": maximum_transfer,
        "transfer_ceiling": transfer_ceiling,
        "normalization_scale": scale,
        "verified_max_transfer": float(np.max(np.abs(verified))),
        "fft_size": float(fft_size),
    }


def render_quantum_field_ir(
    model: ScalarFieldModel,
    frame: ScalarFieldFrame,
    spec: QuantumFieldIRSpec | None = None,
) -> QuantumFieldIRArtifact:
    """Render a stereo audio mapping of the retarded lattice propagator.

    The undamped field kernel is ``theta(t) sin(sqrt(K)t)/sqrt(K)``. Audible
    frequency scaling and exponential damping are explicit sonification steps.
    """

    spec = spec or QuantumFieldIRSpec(source_site=model.spec.sites // 2)
    if frame.sites != model.spec.sites:
        raise ValueError("frame and field model site counts differ")
    if not 0 <= spec.source_site < model.spec.sites:
        raise ValueError("source_site lies outside the lattice")
    sample_count = max(2, int(round(spec.duration_seconds * spec.sample_rate)))
    time = np.arange(sample_count, dtype=float) / spec.sample_rate
    audible_hz = spec.root_hz * model.frequencies / model.frequencies[0]
    source_projection = model.mode_vectors[spec.source_site, :]
    modal_kernel = (
        np.sin(math.tau * audible_hz[:, None] * time[None, :])
        * (source_projection / model.frequencies)[:, None]
    )
    site_response = model.mode_vectors @ modal_kernel

    correlation = np.abs(frame.covariance_phi[:, spec.source_site])
    correlation /= max(float(np.max(correlation)), 1e-15)
    site_weight = (1.0 - spec.correlation_depth) + spec.correlation_depth * correlation
    left_readout, right_readout = _equal_power_site_readout(model.spec.sites)
    quantum_ir = np.column_stack(
        [
            (left_readout * site_weight) @ site_response,
            (right_readout * site_weight) @ site_response,
        ]
    )
    quantum_ir *= np.exp(-time / spec.decay_seconds)[:, None]
    tail_fade = min(sample_count, max(16, int(0.05 * spec.sample_rate)))
    quantum_ir[-tail_fade:] *= np.linspace(1.0, 0.0, tail_fade)[:, None]
    peak = float(np.max(np.abs(quantum_ir)))
    if peak > 0.0:
        quantum_ir *= 0.9 / peak

    geometry_metadata: dict[str, Any] = {"enabled": False}
    audio = quantum_ir
    if spec.geometry_ir_path is not None and spec.geometry_mix > 0.0:
        geometry_path = Path(spec.geometry_ir_path).expanduser().resolve()
        geometry_audio, geometry_rate = sf.read(geometry_path, always_2d=True)
        geometry_audio = np.asarray(geometry_audio[:, :2], dtype=float)
        if geometry_rate != spec.sample_rate:
            divisor = math.gcd(int(geometry_rate), int(spec.sample_rate))
            geometry_audio = resample_poly(
                geometry_audio,
                spec.sample_rate // divisor,
                int(geometry_rate) // divisor,
                axis=0,
            )
        convolved = np.column_stack(
            [
                fftconvolve(
                    quantum_ir[:, channel], geometry_audio[:, channel]
                )
                for channel in range(2)
            ]
        )
        maximum_samples = int(
            round((spec.duration_seconds + 2.5) * spec.sample_rate)
        )
        convolved = convolved[:maximum_samples]
        geometry_direct = np.pad(
            quantum_ir,
            ((0, max(0, len(convolved) - len(quantum_ir))), (0, 0)),
        )[: len(convolved)]
        audio = (
            (1.0 - spec.geometry_mix) * geometry_direct
            + spec.geometry_mix * convolved
        )
        geometry_metadata = {
            "enabled": True,
            "path": str(geometry_path),
            "source_sample_rate": int(geometry_rate),
            "mix": spec.geometry_mix,
            "interpretation": "procedural geometric acoustic realization",
        }
    audio, convolution_normalization = _normalize_for_convolution(audio)
    audio = np.asarray(audio, dtype=np.float32)
    metadata: dict[str, Any] = {
        "schema": "qmw.scalar_field_ir.v3",
        "quantum_kernel": "retarded_free_lattice_propagator",
        "kernel_equation": "theta(t) sin(sqrt(K)t) / sqrt(K)",
        "field_spec": asdict(model.spec),
        "ir_spec": asdict(spec),
        "audible_mode_frequencies_hz": audible_hz.tolist(),
        "source_site": spec.source_site,
        "correlation_site_weights": site_weight.tolist(),
        "geometry": geometry_metadata,
        "convolution_normalization": convolution_normalization,
        "sonification_boundary": {
            "frequency_scaling": True,
            "exponential_damping": True,
            "stereo_site_readout": True,
            "physical_room_ir_claim": False,
        },
    }
    return QuantumFieldIRArtifact(audio=audio, metadata=metadata)


def write_quantum_field_ir(
    artifact: QuantumFieldIRArtifact,
    wav_path: str | Path,
    *,
    sample_rate: int,
) -> tuple[Path, Path]:
    wav = Path(wav_path).expanduser().resolve()
    wav.parent.mkdir(parents=True, exist_ok=True)
    sf.write(wav, artifact.audio, int(sample_rate), subtype="FLOAT")
    digest = hashlib.sha256(wav.read_bytes()).hexdigest()
    metadata = dict(artifact.metadata)
    metadata["wav_path"] = str(wav)
    metadata["wav_sha256"] = digest
    metadata["sample_rate"] = int(sample_rate)
    metadata["frames"] = int(len(artifact.audio))
    json_path = wav.with_suffix(".json")
    json_path.write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n")
    return wav, json_path


__all__ = [
    "QuantumFieldIRArtifact",
    "QuantumFieldIRSpec",
    "render_quantum_field_ir",
    "write_quantum_field_ir",
]
