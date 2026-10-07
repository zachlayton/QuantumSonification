#!/usr/bin/env python3
"""Shared-reference Wilson graph-wave A/B sonification for I Ching comparisons.

Both routes use the exact Wilson CPS magnetic graph-wave renderer used by a
normal ``C`` consultation.  The frozen ideal consultation supplies one common
complex reference Laplacian and one common six-factor tuning field.  LOCAL
excites it at the local H0; Aer/IBM excites the same instrument at its measured
H0.  This is a controlled readout comparison, not a claim that four
measurement circuits reconstruct hardware phases.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import threading
from dataclasses import asdict, dataclass, replace
from pathlib import Path
from typing import Any

import numpy as np

from qmw_iching_density_laplacian_bridge_v1 import build_control_frame
from qmw_iching_laplacian_modal_renderer_v1 import (
    RenderConfig,
    render_audio_from_frame,
    write_wav,
)


@dataclass(frozen=True)
class ComparisonSonificationConfig:
    sample_rate: int = 44_100
    route_seconds: float = 7.0
    gap_seconds: float = 0.45
    coda_seconds: float = 1.6
    base_frequency_hz: float = 90.0
    mode_count: int = 24
    output_ceiling: float = 0.72


def _validate(config: ComparisonSonificationConfig) -> None:
    if config.sample_rate <= 0:
        raise ValueError("sample rate must be positive")
    if config.route_seconds <= 0 or config.gap_seconds < 0 or config.coda_seconds <= 0:
        raise ValueError("segment durations must be positive and gap nonnegative")
    if config.base_frequency_hz <= 0:
        raise ValueError("base frequency must be positive")
    if not 1 <= config.mode_count <= 64:
        raise ValueError("mode count must be between 1 and 64")
    if not 0 < config.output_ceiling <= 1:
        raise ValueError("output ceiling must be in (0, 1]")


def comparison_audio_markers(config: ComparisonSonificationConfig) -> dict[str, float]:
    """Return the exact local/external/coda boundaries."""
    _validate(config)
    external = config.route_seconds + config.gap_seconds
    coda = external + config.route_seconds + config.gap_seconds
    return {
        "local_start_seconds": 0.0,
        "external_start_seconds": external,
        "coda_start_seconds": coda,
        "duration_seconds": coda + config.coda_seconds,
    }


def modal_render_config(config: ComparisonSonificationConfig) -> RenderConfig:
    """Translate comparison timing into the unchanged C-renderer contract."""
    _validate(config)
    return RenderConfig(
        sample_rate=config.sample_rate,
        duration_seconds=config.route_seconds,
        base_frequency_hz=config.base_frequency_hz,
        mode_count=config.mode_count,
        output_ceiling=config.output_ceiling,
    )


def build_shared_reference(comparison: Any):
    """Build the frozen C frame/L and the external H0 excitation frame."""
    frame, _rho, _rho_lu, _adjacency, laplacian, _field = build_control_frame(
        seed=int(comparison.seed), depth=int(comparison.depth)
    )
    expected = (
        int(comparison.local.primary), int(comparison.local.moving_mask),
        int(comparison.local.transformed),
    )
    actual = (int(frame.primary), int(frame.moving_mask), int(frame.transformed))
    if actual != expected:
        raise ValueError(f"local comparison route {expected} does not match frozen C frame {actual}")
    external_frame = replace(
        frame,
        primary=int(comparison.external.primary),
        moving_mask=int(comparison.external.moving_mask),
        transformed=int(comparison.external.transformed),
        change_register=int(comparison.external.change_register),
    )
    return frame, external_frame, laplacian


def render_modal_routes(comparison: Any,
                        config: ComparisonSonificationConfig | None = None):
    """Render both H0 excitations through one unchanged C modal instrument."""
    config = config or ComparisonSonificationConfig()
    frame, external_frame, laplacian = build_shared_reference(comparison)
    render_config = modal_render_config(config)
    local_audio, local_frequencies, local_decays, local_pans, local_retained = (
        render_audio_from_frame(frame, laplacian, render_config)
    )
    external_audio, external_frequencies, external_decays, external_pans, external_retained = (
        render_audio_from_frame(external_frame, laplacian, render_config)
    )
    diagnostics = {
        "reference": "frozen local magnetic Laplacian and Wilson tuning field",
        "local": {
            "primary": int(frame.primary), "retained_weight": float(local_retained),
            "frequencies_hz": local_frequencies.tolist(),
            "decays_seconds": local_decays.tolist(), "pans": local_pans.tolist(),
        },
        "external": {
            "primary": int(external_frame.primary), "retained_weight": float(external_retained),
            "frequencies_hz": external_frequencies.tolist(),
            "decays_seconds": external_decays.tolist(), "pans": external_pans.tolist(),
        },
    }
    return local_audio, external_audio, diagnostics


def _envelope(sample_count: int, sample_rate: int, attack: float, release: float) -> np.ndarray:
    result = np.ones(sample_count, dtype=np.float64)
    attack_count = min(sample_count, max(1, int(attack * sample_rate)))
    release_count = min(sample_count, max(1, int(release * sample_rate)))
    result[:attack_count] *= np.sin(np.linspace(0, np.pi / 2, attack_count)) ** 2
    result[-release_count:] *= np.sin(np.linspace(np.pi / 2, 0, release_count)) ** 2
    return result


def render_comparison_audio(comparison: Any,
                            config: ComparisonSonificationConfig | None = None) -> np.ndarray:
    """Render C(local), C(external), then a compact metric-difference coda."""
    config = config or ComparisonSonificationConfig()
    markers = comparison_audio_markers(config)
    total = int(round(markers["duration_seconds"] * config.sample_rate))
    route_count = int(round(config.route_seconds * config.sample_rate))
    external_start = int(round(markers["external_start_seconds"] * config.sample_rate))
    coda_start = int(round(markers["coda_start_seconds"] * config.sample_rate))
    audio = np.zeros((total, 2), dtype=np.float64)
    local_audio, external_audio, _diagnostics = render_modal_routes(comparison, config)
    audio[:route_count] = local_audio
    audio[external_start:external_start+route_count] = external_audio

    coda_count = total - coda_start
    t = np.arange(coda_count, dtype=np.float64) / config.sample_rate
    disagreement = float(np.clip(
        comparison.primary_tvd + 2.0 * comparison.moving_probability_mae
        + (1.0 - comparison.primary_hellinger_fidelity), 0.0, 1.0
    ))
    base = config.base_frequency_hz * 1.5
    detune_ratio = 2 ** ((80.0 * disagreement) / 1200.0)
    coda = np.column_stack((
        np.sin(2 * np.pi * base * t),
        np.sin(2 * np.pi * base * detune_ratio * t),
    )) * 0.13
    coda *= _envelope(coda_count, config.sample_rate, 0.05, 0.42)[:, None]
    audio[coda_start:] = coda
    return np.clip(audio, -1.0, 1.0)


def sonification_manifest(comparison: Any,
                          config: ComparisonSonificationConfig) -> dict[str, Any]:
    _local, _external, diagnostics = render_modal_routes(comparison, config)
    return {
        "schema": "qmw.iching.comparison-sonification.v2-shared-modal",
        "source": comparison.source,
        "backend": comparison.backend,
        "job_id": comparison.job_id,
        "seed": int(comparison.seed),
        "markers": comparison_audio_markers(config),
        "mapping": {
            "form": "C(local H0), C(external H0), disagreement coda",
            "instrument": "shared 24-node Wilson CPS magnetic graph-wave renderer",
            "carrier_frequency_mapping": (
                "exact period-folded subset products of 1-3-5-7-11-13; "
                "Pascal shells occupy three octave registers"
            ),
            "graph_rate_mapping": (
                "full cos(sqrt(L)t)|H0> complex node wave; not converted to pitch"
            ),
            "controlled_geometry": (
                "one frozen local reference Laplacian and Wilson tuning field "
                "for both routes"
            ),
            "route_difference": "H0 excitation node measured by each route",
            "moving_and_h1": "reported as comparison data; not audible in the C renderer",
            "hardware_phase_claim": "none; four measurement circuits do not reconstruct phases",
        },
        "modal_diagnostics": diagnostics,
        "config": asdict(config),
    }


class ComparisonAudioPlayer:
    """Archive and play the newest shared-modal comparison."""

    def __init__(self, config: ComparisonSonificationConfig, volume: float = 1.0):
        executable = shutil.which("afplay")
        if executable is None:
            raise RuntimeError("comparison playback requires /usr/bin/afplay")
        self.config = config
        self.volume = float(max(0.0, volume))
        self.executable = executable
        self._lock = threading.Lock()
        self._process: subprocess.Popen | None = None

    def play(self, comparison: Any, output_path: Path) -> None:
        audio = render_comparison_audio(comparison, self.config)
        path = Path(output_path)
        write_wav(path, audio, self.config.sample_rate)
        path.with_suffix(".json").write_text(
            json.dumps(sonification_manifest(comparison, self.config), indent=2) + "\n",
            encoding="utf-8",
        )
        with self._lock:
            self._stop_locked()
            self._process = subprocess.Popen(
                [self.executable, "--volume", str(self.volume), str(path)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

    def _stop_locked(self) -> None:
        if self._process is None or self._process.poll() is not None:
            return
        self._process.terminate()
        try:
            self._process.wait(timeout=1.0)
        except subprocess.TimeoutExpired:
            self._process.kill()
            self._process.wait(timeout=1.0)

    def close(self) -> None:
        with self._lock:
            self._stop_locked()
