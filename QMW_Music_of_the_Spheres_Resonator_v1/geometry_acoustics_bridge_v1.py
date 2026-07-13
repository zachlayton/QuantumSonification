#!/usr/bin/env python3
"""Geometry Acoustics Bridge v1.

Converts a triangular mesh into:
1. spectral-geometry descriptors,
2. a modal impulse response,
3. a descriptor JSON / spectrum NPZ package.

This is an offline/slow-rate bridge intended for periodic IR regeneration.
Real-time convolution should crossfade between previously generated IR files.

Dependencies:
    numpy
    scipy
    soundfile

Local dependency:
    spectral_geometry_v1.py
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
import json
from typing import Any

import numpy as np
import soundfile as sf
from scipy.signal import butter, sosfilt

from spectral_geometry_v1 import (
    MeshSpectralGeometry,
    SpectralGeometryConfig,
    SpectralGeometryResult,
    load_obj,
)


@dataclass(frozen=True)
class AcousticBridgeConfig:
    sample_rate: int = 48000
    duration_seconds: float = 6.0
    n_modes: int = 48
    effective_wave_speed: float = 120.0
    frequency_scale: float = 1.0
    base_decay_seconds: float = 2.5
    decay_frequency_tilt: float = 0.45
    localization_decay_gain: float = 1.2
    early_reflection_gain: float = 0.20
    modal_gain: float = 0.82
    stereo_width: float = 0.55
    output_peak: float = 0.80
    highpass_hz: float = 18.0
    seed: int = 23


class GeometryAcousticsBridge:
    def __init__(
        self,
        vertices: np.ndarray,
        faces: np.ndarray,
        config: AcousticBridgeConfig = AcousticBridgeConfig(),
    ) -> None:
        self.vertices = np.asarray(vertices, dtype=np.float64)
        self.faces = np.asarray(faces, dtype=np.int64)
        self.config = config
        self.spectral_solver: MeshSpectralGeometry | None = None
        self.spectrum: SpectralGeometryResult | None = None
        self.ir: np.ndarray | None = None

    def analyze(
        self,
        source_position: np.ndarray | list[float],
        listener_position: np.ndarray | list[float],
    ) -> SpectralGeometryResult:
        spectral_config = SpectralGeometryConfig(
            n_modes=self.config.n_modes,
            effective_wave_speed=self.config.effective_wave_speed,
            frequency_scale=self.config.frequency_scale,
            min_frequency_hz=max(20.0, self.config.highpass_hz),
            max_frequency_hz=0.45 * self.config.sample_rate,
        )
        self.spectral_solver = MeshSpectralGeometry(
            self.vertices,
            self.faces,
            spectral_config,
        )
        self.spectrum = self.spectral_solver.solve(
            source_position=source_position,
            listener_position=listener_position,
        )
        return self.spectrum

    def _mode_decays(self) -> np.ndarray:
        assert self.spectrum is not None
        f = self.spectrum.frequencies_hz
        if not len(f):
            return np.array([], dtype=np.float64)

        f_norm = f / max(float(np.median(f)), 1.0)
        localization = self.spectrum.localization_ipr
        localization = localization / max(float(np.median(localization)), 1e-12)

        decay = self.config.base_decay_seconds / (
            np.maximum(f_norm, 1e-6) ** self.config.decay_frequency_tilt
        )
        decay *= 1.0 / (
            1.0 + self.config.localization_decay_gain * np.maximum(localization - 1.0, 0.0)
        )
        return np.clip(decay, 0.05, self.config.duration_seconds * 1.5)

    def _mode_amplitudes(self) -> np.ndarray:
        assert self.spectrum is not None

        coupling = self.spectrum.source_listener_weights
        if coupling is None:
            coupling = np.ones_like(self.spectrum.frequencies_hz)

        amplitudes = np.asarray(coupling, dtype=np.float64)
        max_abs = max(float(np.max(np.abs(amplitudes))), 1e-12)
        amplitudes = amplitudes / max_abs

        # Suppress very high modes gently while retaining geometrically irregular
        # spacing and source/listener sign.
        mode_index = np.arange(len(amplitudes), dtype=np.float64)
        amplitudes *= 1.0 / np.sqrt(1.0 + mode_index)
        return amplitudes

    def synthesize_modal_ir(self) -> np.ndarray:
        if self.spectrum is None:
            raise RuntimeError("analyze() must be called before IR synthesis")

        cfg = self.config
        rng = np.random.default_rng(cfg.seed)
        n_samples = max(2, int(round(cfg.duration_seconds * cfg.sample_rate)))
        t = np.arange(n_samples, dtype=np.float64) / cfg.sample_rate

        frequencies = self.spectrum.frequencies_hz
        amplitudes = self._mode_amplitudes()
        decays = self._mode_decays()

        left = np.zeros(n_samples, dtype=np.float64)
        right = np.zeros(n_samples, dtype=np.float64)

        phases = rng.uniform(-np.pi, np.pi, len(frequencies))
        pans = rng.uniform(-1.0, 1.0, len(frequencies)) * cfg.stereo_width

        for index, (frequency, amplitude, decay, phase, pan) in enumerate(
            zip(frequencies, amplitudes, decays, phases, pans)
        ):
            envelope = np.exp(-t / decay)
            signal = amplitude * envelope * np.sin(
                2.0 * np.pi * frequency * t + phase
            )

            left_gain = np.sqrt(0.5 * (1.0 - pan))
            right_gain = np.sqrt(0.5 * (1.0 + pan))
            left += left_gain * signal
            right += right_gain * signal

        modal = np.column_stack([left, right])

        # Sparse early reflections derived from mesh scale and source/listener
        # separation. They provide temporal articulation before the modal tail.
        early = np.zeros_like(modal)
        bounds = np.ptp(self.vertices, axis=0)
        characteristic_size = max(float(np.linalg.norm(bounds)), 1e-6)
        reflection_count = max(8, min(64, len(self.faces) // 100))
        speed = max(cfg.effective_wave_speed, 1e-6)

        for reflection_index in range(reflection_count):
            path_scale = 0.35 + 2.8 * (reflection_index + 1) / reflection_count
            delay_seconds = characteristic_size * path_scale / speed
            delay_seconds *= rng.uniform(0.85, 1.15)
            sample_index = int(round(delay_seconds * cfg.sample_rate))
            if 1 <= sample_index < n_samples:
                gain = (
                    cfg.early_reflection_gain
                    * rng.choice([-1.0, 1.0])
                    / (1.0 + 0.18 * reflection_index)
                )
                pan = rng.uniform(-cfg.stereo_width, cfg.stereo_width)
                early[sample_index, 0] += gain * np.sqrt(0.5 * (1.0 - pan))
                early[sample_index, 1] += gain * np.sqrt(0.5 * (1.0 + pan))

        ir = cfg.modal_gain * modal + early

        # Gentle DC/very-low-frequency removal.
        if 0.0 < cfg.highpass_hz < 0.45 * cfg.sample_rate:
            sos = butter(
                2,
                cfg.highpass_hz,
                btype="highpass",
                fs=cfg.sample_rate,
                output="sos",
            )
            ir = sosfilt(sos, ir, axis=0)

        # Fade the end to guarantee clean truncation.
        fade_samples = min(int(0.05 * cfg.sample_rate), n_samples // 4)
        if fade_samples > 1:
            fade = np.linspace(1.0, 0.0, fade_samples)
            ir[-fade_samples:, :] *= fade[:, None]

        peak = max(float(np.max(np.abs(ir))), 1e-12)
        ir *= cfg.output_peak / peak
        self.ir = ir.astype(np.float32)
        return self.ir

    def acoustic_descriptors(self) -> dict[str, Any]:
        if self.spectrum is None:
            raise RuntimeError("analyze() must be called first")

        frequencies = self.spectrum.frequencies_hz
        decays = self._mode_decays()
        amplitudes = np.abs(self._mode_amplitudes())
        weights = amplitudes / max(float(np.sum(amplitudes)), 1e-12)

        centroid = float(np.sum(weights * frequencies)) if len(frequencies) else 0.0
        bandwidth = (
            float(np.sqrt(np.sum(weights * (frequencies - centroid) ** 2)))
            if len(frequencies)
            else 0.0
        )

        return {
            "sample_rate": self.config.sample_rate,
            "duration_seconds": self.config.duration_seconds,
            "mode_count": int(len(frequencies)),
            "frequency_min_hz": float(frequencies[0]) if len(frequencies) else 0.0,
            "frequency_max_hz": float(frequencies[-1]) if len(frequencies) else 0.0,
            "spectral_centroid_hz": centroid,
            "spectral_bandwidth_hz": bandwidth,
            "mean_decay_seconds": float(np.mean(decays)) if len(decays) else 0.0,
            "spectral_gap": self.spectrum.spectral_gap,
            "mean_eigenvalue_spacing": self.spectrum.mean_spacing,
            "eigenvalue_spacing_variance": self.spectrum.spacing_variance,
            "spectral_entropy": self.spectrum.spectral_entropy,
            "mean_localization_ipr": (
                float(np.mean(self.spectrum.localization_ipr))
                if len(self.spectrum.localization_ipr)
                else 0.0
            ),
            "source_vertex": self.spectrum.source_vertex,
            "listener_vertex": self.spectrum.listener_vertex,
        }

    def export(
        self,
        output_prefix: str | Path,
    ) -> dict[str, Path]:
        if self.spectrum is None or self.spectral_solver is None:
            raise RuntimeError("analyze() must be called before export()")
        if self.ir is None:
            self.synthesize_modal_ir()
        assert self.ir is not None

        prefix = Path(output_prefix)
        prefix.parent.mkdir(parents=True, exist_ok=True)

        wav_path = prefix.with_suffix(".wav")
        json_path = prefix.with_suffix(".json")
        npz_path = prefix.with_suffix(".npz")

        sf.write(wav_path, self.ir, self.config.sample_rate, subtype="FLOAT")
        self.spectral_solver.export_npz(npz_path)

        payload = {
            "bridge_config": asdict(self.config),
            "mesh": {
                "vertex_count": int(len(self.vertices)),
                "face_count": int(len(self.faces)),
            },
            "spectral_geometry": self.spectrum.to_json_dict(),
            "acoustics": self.acoustic_descriptors(),
        }
        json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

        return {
            "wav": wav_path,
            "json": json_path,
            "npz": npz_path,
        }


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mesh", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--source", type=float, nargs=3, required=True)
    parser.add_argument("--listener", type=float, nargs=3, required=True)
    parser.add_argument("--sample-rate", type=int, default=48000)
    parser.add_argument("--duration", type=float, default=6.0)
    parser.add_argument("--modes", type=int, default=48)
    parser.add_argument("--wave-speed", type=float, default=120.0)
    parser.add_argument("--frequency-scale", type=float, default=1.0)
    parser.add_argument("--decay", type=float, default=2.5)
    parser.add_argument("--seed", type=int, default=23)
    args = parser.parse_args()

    vertices, faces = load_obj(args.mesh)
    bridge = GeometryAcousticsBridge(
        vertices,
        faces,
        AcousticBridgeConfig(
            sample_rate=args.sample_rate,
            duration_seconds=args.duration,
            n_modes=args.modes,
            effective_wave_speed=args.wave_speed,
            frequency_scale=args.frequency_scale,
            base_decay_seconds=args.decay,
            seed=args.seed,
        ),
    )
    spectrum = bridge.analyze(args.source, args.listener)
    bridge.synthesize_modal_ir()
    paths = bridge.export(args.output)

    print("Geometry acoustics bridge complete")
    print(f"  mesh:             {args.mesh}")
    print(f"  modes:            {len(spectrum.eigenvalues)}")
    print(f"  spectral gap:     {spectrum.spectral_gap:.8f}")
    print(f"  spectral entropy: {spectrum.spectral_entropy:.6f}")
    print(f"  IR:               {paths['wav']}")
    print(f"  descriptors:      {paths['json']}")
    print(f"  spectrum:         {paths['npz']}")


if __name__ == "__main__":
    main()
