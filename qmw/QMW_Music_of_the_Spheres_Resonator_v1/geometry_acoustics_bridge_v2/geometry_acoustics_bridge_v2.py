#!/usr/bin/env python3
"""Render a modal impulse response without re-deriving material acoustics."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
import argparse
import json
from typing import Any, Mapping

import numpy as np
import soundfile as sf


@dataclass(frozen=True)
class AcousticBridgeConfig:
    sample_rate: int = 48000
    duration_seconds: float = 6.0
    highpass_hz: float = 12.0
    peak_level: float = 0.8
    stereo_width: float = 0.85
    phase_mode: str = "coherent"
    direct_gain: float = 0.08
    tail_fade_seconds: float = 0.02
    auto_trim: bool = True
    trim_threshold_db: float = -60.0
    trim_window_seconds: float = 0.02
    trim_hold_seconds: float = 0.10
    minimum_duration_seconds: float = 1.0
    preserve_existing_files: bool = True
    seed: int = 23


@dataclass(frozen=True)
class ModalAcousticPacket:
    model: str
    eigenvalues: np.ndarray
    eigenvectors: np.ndarray | None
    frequencies_hz: np.ndarray
    angular_frequencies: np.ndarray
    decay_times_seconds: np.ndarray
    t60_seconds: np.ndarray
    damping_rates: np.ndarray
    mode_weights: np.ndarray
    quantum_gains: np.ndarray
    metadata: dict[str, Any]


def _scalar_text(value: Any, default: str = "unknown") -> str:
    if value is None:
        return default
    array = np.asarray(value)
    return str(array.item() if array.ndim == 0 else array.reshape(-1)[0])


def _mapping(source: str | Path | Mapping[str, Any] | Any) -> dict[str, Any]:
    if isinstance(source, (str, Path)):
        with np.load(source, allow_pickle=False) as packet:
            result = {name: packet[name] for name in packet.files}
        metadata_key = (
            "material_metadata_json"
            if "material_metadata_json" in result
            else "metadata_json" if "metadata_json" in result else None
        )
        if metadata_key is not None:
            result["metadata"] = json.loads(
                str(np.asarray(result[metadata_key]).item())
            )
        return result
    if isinstance(source, Mapping):
        return dict(source)
    names = (
        "model",
        "material_model",
        "eigenvalues",
        "eigenvectors",
        "geometric_eigenvalues",
        "geometric_eigenvectors",
        "frequencies_hz",
        "angular_frequencies",
        "decay_times_seconds",
        "damping_rates",
        "mode_weights",
        "mode_probabilities",
        "mode_amplitudes",
        "metadata",
    )
    return {name: getattr(source, name) for name in names if hasattr(source, name)}


def normalize_modal_packet(
    source: str | Path | Mapping[str, Any] | Any,
) -> ModalAcousticPacket:
    raw = _mapping(source)
    missing = [
        name
        for name in ("frequencies_hz", "decay_times_seconds", "mode_weights")
        if name not in raw
    ]
    if missing:
        raise ValueError(
            "A SurfaceModalPacket is required; missing preserved material fields: "
            + ", ".join(missing)
        )

    frequencies = np.asarray(raw["frequencies_hz"], dtype=np.float64).reshape(-1)
    decay = np.asarray(raw["decay_times_seconds"], dtype=np.float64).reshape(-1)
    weights = np.asarray(raw["mode_weights"], dtype=np.float64).reshape(-1)
    required_lengths = {
        "frequencies_hz": len(frequencies),
        "decay_times_seconds": len(decay),
        "mode_weights": len(weights),
    }
    if len(set(required_lengths.values())) != 1:
        raise ValueError(f"modal field length mismatch: {required_lengths}")
    count = len(frequencies)
    if count == 0:
        raise ValueError("The modal packet contains no modes")
    if not np.all(np.isfinite(frequencies)) or np.any(frequencies < 0.0):
        raise ValueError("frequencies_hz must be finite and nonnegative")
    if not np.all(np.isfinite(decay)) or np.any(decay <= 0.0):
        raise ValueError("decay_times_seconds must be finite and positive")
    if not np.all(np.isfinite(weights)):
        raise ValueError("mode_weights must be finite")
    eigenvalues = np.asarray(
        raw.get("eigenvalues", raw.get("geometric_eigenvalues", np.arange(len(frequencies)))),
        dtype=np.float64,
    ).reshape(-1)
    if len(eigenvalues) < count:
        raise ValueError(
            f"eigenvalues has {len(eigenvalues)} values; expected at least {count}"
        )

    vectors_value = raw.get("eigenvectors", raw.get("geometric_eigenvectors"))
    vectors = None if vectors_value is None else np.asarray(vectors_value, dtype=np.float64)
    if vectors is not None:
        if vectors.ndim != 2 or vectors.shape[1] < count:
            raise ValueError(
                "eigenvectors must have shape (vertices, modes) with at least "
                f"{count} mode columns"
            )
        vectors = vectors[:, :count]
    def optional_or_default(name: str, default: np.ndarray) -> np.ndarray:
        value = np.asarray(raw.get(name, []), dtype=np.float64).reshape(-1)
        if len(value) == 0:
            return np.asarray(default, dtype=np.float64)[:count]
        if len(value) < count:
            raise ValueError(
                f"modal field {name!r} has {len(value)} values; "
                f"expected at least {count}"
            )
        return value[:count]

    angular = optional_or_default(
        "angular_frequencies", 2.0 * np.pi * frequencies
    )
    damping = optional_or_default(
        "damping_rates", 1.0 / np.maximum(decay, 1e-9)
    )

    if "mode_amplitudes" in raw:
        gains = np.abs(np.asarray(raw["mode_amplitudes"]).reshape(-1)).astype(
            np.float64
        )
    elif "mode_probabilities" in raw:
        gains = np.sqrt(np.maximum(np.asarray(raw["mode_probabilities"], dtype=np.float64).reshape(-1), 0.0))
    else:
        gains = np.ones(count, dtype=np.float64)
    if len(gains) < count:
        gains = np.pad(gains, (0, count - len(gains)), constant_values=1.0)
    gains = gains[:count]
    gains /= max(float(np.max(gains)), 1e-12)

    return ModalAcousticPacket(
        model=_scalar_text(raw.get("model", raw.get("material_model"))),
        eigenvalues=eigenvalues[:count],
        eigenvectors=vectors,
        frequencies_hz=frequencies[:count],
        angular_frequencies=angular,
        decay_times_seconds=decay[:count],
        t60_seconds=decay[:count] * np.log(1000.0),
        damping_rates=damping,
        mode_weights=weights[:count],
        quantum_gains=gains,
        metadata=dict(raw.get("metadata", {})),
    )


class GeometryAcousticsBridgeV2:
    """Consume material frequencies and decays as authoritative values."""

    def __init__(
        self,
        modal_packet: str | Path | Mapping[str, Any] | Any,
        config: AcousticBridgeConfig = AcousticBridgeConfig(),
    ) -> None:
        self.packet = normalize_modal_packet(modal_packet)
        self.config = config
        self._last_render_info: dict[str, Any] = {
            "actual_duration_seconds": float(config.duration_seconds),
            "trimmed": False,
        }

    def _stereo_pan(self) -> tuple[np.ndarray, np.ndarray]:
        rng = np.random.default_rng(self.config.seed)
        pan = rng.uniform(-1.0, 1.0, len(self.packet.frequencies_hz))
        pan *= np.clip(self.config.stereo_width, 0.0, 1.0)
        return np.sqrt(0.5 * (1.0 - pan)), np.sqrt(0.5 * (1.0 + pan))

    def _trim_silent_tail(
        self,
        ir: np.ndarray,
        sample_rate: int,
    ) -> np.ndarray:
        configured_duration = len(ir) / sample_rate
        self._last_render_info = {
            "actual_duration_seconds": configured_duration,
            "trimmed": False,
        }
        if not self.config.auto_trim:
            return ir
        minimum_samples = max(
            1,
            int(round(sample_rate * max(0.0, self.config.minimum_duration_seconds))),
        )
        if len(ir) <= minimum_samples:
            return ir

        window_samples = max(
            1,
            int(round(sample_rate * max(1.0e-4, self.config.trim_window_seconds))),
        )
        block_count = len(ir) // window_samples
        if block_count < 2:
            return ir
        blocked = ir[: block_count * window_samples].reshape(
            block_count, window_samples, ir.shape[1]
        )
        rms = np.sqrt(np.mean(np.square(blocked, dtype=np.float64), axis=(1, 2)))
        reference = float(np.max(rms))
        if reference <= 1.0e-15:
            trim_sample = minimum_samples
        else:
            threshold = reference * 10.0 ** (float(self.config.trim_threshold_db) / 20.0)
            active = np.flatnonzero(rms >= threshold)
            if len(active) == 0:
                trim_sample = minimum_samples
            else:
                last_active_end = (int(active[-1]) + 1) * window_samples
                hold_samples = int(
                    round(sample_rate * max(0.0, self.config.trim_hold_seconds))
                )
                trim_sample = max(minimum_samples, last_active_end + hold_samples)
        trim_sample = min(len(ir), trim_sample)
        if trim_sample >= len(ir):
            return ir
        self._last_render_info = {
            "actual_duration_seconds": trim_sample / sample_rate,
            "trimmed": True,
        }
        return ir[:trim_sample].copy()

    def synthesize_modal_ir(self) -> np.ndarray:
        sample_rate = max(1, int(self.config.sample_rate))
        length = max(1, int(round(sample_rate * self.config.duration_seconds)))
        time = np.arange(length, dtype=np.float64) / sample_rate
        ir = np.zeros((length, 2), dtype=np.float64)
        left_gain, right_gain = self._stereo_pan()
        rng = np.random.default_rng(self.config.seed + 1)

        phase_mode = str(self.config.phase_mode).strip().lower()
        if phase_mode not in {"coherent", "random"}:
            raise ValueError("phase_mode must be 'coherent' or 'random'")
        direct_gain = max(0.0, float(self.config.direct_gain))

        amplitudes = self.packet.mode_weights * self.packet.quantum_gains
        for index, frequency in enumerate(self.packet.frequencies_hz):
            if not np.isfinite(frequency) or frequency <= 0.0 or frequency >= 0.5 * sample_rate:
                continue
            tau = max(float(self.packet.decay_times_seconds[index]), 1e-4)
            phase = (
                0.0
                if phase_mode == "coherent"
                else rng.uniform(0.0, 2.0 * np.pi)
            )
            mode = amplitudes[index] * np.exp(-time / tau) * np.cos(
                2.0 * np.pi * frequency * time + phase
            )
            ir[:, 0] += left_gain[index] * mode
            ir[:, 1] += right_gain[index] * mode

        if direct_gain > 0.0:
            direct_amplitude = direct_gain * max(
                float(np.sum(np.abs(amplitudes))), 1e-12
            )
            ir[0, :] += direct_amplitude * np.sqrt(0.5)

        highpass = max(0.0, float(self.config.highpass_hz))
        if highpass > 0.0:
            coefficient = np.exp(-2.0 * np.pi * highpass / sample_rate)
            for channel in range(2):
                previous_input = 0.0
                previous_output = 0.0
                for index in range(length):
                    current = ir[index, channel]
                    previous_output = coefficient * (previous_output + current - previous_input)
                    previous_input = current
                    ir[index, channel] = previous_output

        peak = float(np.max(np.abs(ir)))
        if peak > 1e-12:
            ir *= np.clip(self.config.peak_level, 0.0, 1.0) / peak

        ir = self._trim_silent_tail(ir, sample_rate)

        fade_samples = min(
            len(ir),
            max(
                0,
                int(round(sample_rate * float(self.config.tail_fade_seconds))),
            ),
        )
        if fade_samples > 1:
            ir[-fade_samples:, :] *= np.linspace(
                1.0, 0.0, fade_samples, dtype=np.float64
            )[:, None]

        return ir.astype(np.float32)

    def acoustic_descriptors(self) -> dict[str, Any]:
        audible = self.packet.frequencies_hz[
            (self.packet.frequencies_hz > 0.0)
            & (self.packet.frequencies_hz < 0.5 * self.config.sample_rate)
        ]
        actual_duration = float(
            self._last_render_info.get(
                "actual_duration_seconds", self.config.duration_seconds
            )
        )
        return {
            "material_model": self.packet.model,
            "mode_count": int(len(self.packet.frequencies_hz)),
            "audible_mode_count": int(len(audible)),
            "frequency_min_hz": None if len(audible) == 0 else float(np.min(audible)),
            "frequency_max_hz": None if len(audible) == 0 else float(np.max(audible)),
            "decay_time_definition": "amplitude_time_constant",
            "t60_min_seconds": float(np.min(self.packet.t60_seconds)),
            "t60_max_seconds": float(np.max(self.packet.t60_seconds)),
            "slowest_tail_level_db_at_end": float(
                -20.0
                / np.log(10.0)
                * actual_duration
                / max(float(np.max(self.packet.decay_times_seconds)), 1e-12)
            ),
            "phase_mode": str(self.config.phase_mode),
            "direct_gain": float(self.config.direct_gain),
            "tail_fade_seconds": float(self.config.tail_fade_seconds),
            "duration_seconds": actual_duration,
            "maximum_duration_seconds": float(self.config.duration_seconds),
            "auto_trim": bool(self.config.auto_trim),
            "trimmed": bool(self._last_render_info.get("trimmed", False)),
            "trim_threshold_db": float(self.config.trim_threshold_db),
            "trim_window_seconds": float(self.config.trim_window_seconds),
            "trim_hold_seconds": float(self.config.trim_hold_seconds),
            "minimum_duration_seconds": float(self.config.minimum_duration_seconds),
            "sample_rate": int(self.config.sample_rate),
        }

    @staticmethod
    def _output_set_exists(prefix: Path) -> bool:
        return any(prefix.with_suffix(suffix).exists() for suffix in (".wav", ".npz", ".json"))

    def _available_output_prefix(self, requested: Path) -> Path:
        if not self.config.preserve_existing_files or not self._output_set_exists(requested):
            return requested
        version = 2
        while True:
            candidate = requested.with_name(f"{requested.name}_v{version:03d}")
            if not self._output_set_exists(candidate):
                return candidate
            version += 1

    def export(self, output_prefix: str | Path) -> dict[str, Path]:
        prefix = self._available_output_prefix(Path(output_prefix))
        prefix.parent.mkdir(parents=True, exist_ok=True)
        wav_path = prefix.with_suffix(".wav")
        npz_path = prefix.with_suffix(".npz")
        json_path = prefix.with_suffix(".json")
        ir = self.synthesize_modal_ir()
        sf.write(wav_path, ir, self.config.sample_rate, subtype="FLOAT")
        np.savez_compressed(
            npz_path,
            impulse_response=ir,
            sample_rate=np.array(self.config.sample_rate),
            material_model=np.array(self.packet.model),
            eigenvalues=self.packet.eigenvalues,
            eigenvectors=(
                np.empty((0, 0), dtype=np.float64)
                if self.packet.eigenvectors is None
                else self.packet.eigenvectors
            ),
            frequencies_hz=self.packet.frequencies_hz,
            angular_frequencies=self.packet.angular_frequencies,
            decay_times_seconds=self.packet.decay_times_seconds,
            t60_seconds=self.packet.t60_seconds,
            damping_rates=self.packet.damping_rates,
            mode_weights=self.packet.mode_weights,
            quantum_gains=self.packet.quantum_gains,
            metadata_json=np.asarray(
                json.dumps(self.packet.metadata, sort_keys=True)
            ),
        )
        json_path.write_text(
            json.dumps(
                {
                    "bridge": "geometry_acoustics_bridge_v2",
                    "config": asdict(self.config),
                    "acoustics": self.acoustic_descriptors(),
                },
                indent=2,
            ),
            encoding="utf-8",
        )
        return {"wav": wav_path, "npz": npz_path, "json": json_path}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("packet", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--sample-rate", type=int, default=48000)
    parser.add_argument("--duration", type=float, default=6.0)
    parser.add_argument("--no-auto-trim", action="store_true")
    parser.add_argument("--trim-threshold-db", type=float, default=-60.0)
    args = parser.parse_args()
    bridge = GeometryAcousticsBridgeV2(
        args.packet,
        AcousticBridgeConfig(
            sample_rate=args.sample_rate,
            duration_seconds=args.duration,
            auto_trim=not args.no_auto_trim,
            trim_threshold_db=args.trim_threshold_db,
        ),
    )
    paths = bridge.export(args.output)
    print(f"Rendered {paths['wav']} from {bridge.packet.model}")


if __name__ == "__main__":
    main()
