"""Bounded revision history for living eigenfield spectral controls.

The phase values in this module are complex eigenfield-mode phases.  They are
control-domain data and are not audio STFT phase-vocoder phases.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np


@dataclass(frozen=True)
class SpectralHistoryFrame:
    revision: int
    magnitudes: np.ndarray
    phases: np.ndarray
    frequencies_hz: np.ndarray
    decay_seconds: np.ndarray


def _fit_modes(values: np.ndarray, mode_count: int) -> np.ndarray:
    source = np.asarray(values, dtype=np.float64).reshape(-1)
    fitted = np.zeros(mode_count, dtype=np.float64)
    copied = min(mode_count, len(source))
    fitted[:copied] = source[:copied]
    return fitted


def _normalized_magnitudes(values: np.ndarray) -> np.ndarray:
    magnitudes = np.maximum(np.asarray(values, dtype=np.float64), 0.0)
    total = float(np.sum(magnitudes))
    if total <= 1e-12:
        return np.zeros_like(magnitudes)
    return magnitudes / total


def _wrapped_phase_delta(current: np.ndarray, previous: np.ndarray) -> np.ndarray:
    return np.angle(np.exp(1j * (current - previous)))


def build_spectral_history(
    frame: SpectralHistoryFrame,
    *,
    depth: int,
    previous_path: str | Path | None = None,
) -> dict[str, np.ndarray]:
    """Append one mode-aligned frame and return a bounded history payload."""

    depth = max(1, int(depth))
    magnitudes = np.asarray(frame.magnitudes, dtype=np.float64).reshape(-1)
    mode_count = len(magnitudes)
    phases = _fit_modes(frame.phases, mode_count)
    frequencies = _fit_modes(frame.frequencies_hz, mode_count)
    decay = _fit_modes(frame.decay_seconds, mode_count)

    previous_revisions = np.empty(0, dtype=np.int64)
    previous_magnitudes = np.empty((0, mode_count), dtype=np.float64)
    previous_phases = np.empty((0, mode_count), dtype=np.float64)
    previous_phase_deltas = np.empty((0, mode_count), dtype=np.float64)
    previous_frequencies = np.empty((0, mode_count), dtype=np.float64)
    previous_decay = np.empty((0, mode_count), dtype=np.float64)
    previous_transients = np.empty(0, dtype=np.float64)
    previous_phase_transients = np.empty(0, dtype=np.float64)

    path = None if previous_path is None else Path(previous_path)
    if path is not None and path.exists():
        with np.load(path, allow_pickle=False) as history:
            previous_revisions = np.asarray(history["revisions"], dtype=np.int64)
            previous_magnitudes = np.asarray(
                history["magnitudes"], dtype=np.float64
            )
            previous_phases = np.asarray(history["phases"], dtype=np.float64)
            previous_phase_deltas = np.asarray(
                history["phase_deltas"], dtype=np.float64
            )
            previous_frequencies = np.asarray(
                history["frequencies_hz"], dtype=np.float64
            )
            previous_decay = np.asarray(
                history["decay_seconds"], dtype=np.float64
            )
            previous_transients = np.asarray(
                history["magnitude_transients"], dtype=np.float64
            )
            previous_phase_transients = np.asarray(
                history["phase_transients"], dtype=np.float64
            )

        # A changed mode count starts a new history rather than silently
        # misaligning mode identities.
        if previous_magnitudes.ndim != 2 or previous_magnitudes.shape[1] != mode_count:
            previous_revisions = np.empty(0, dtype=np.int64)
            previous_magnitudes = np.empty((0, mode_count), dtype=np.float64)
            previous_phases = np.empty((0, mode_count), dtype=np.float64)
            previous_phase_deltas = np.empty((0, mode_count), dtype=np.float64)
            previous_frequencies = np.empty((0, mode_count), dtype=np.float64)
            previous_decay = np.empty((0, mode_count), dtype=np.float64)
            previous_transients = np.empty(0, dtype=np.float64)
            previous_phase_transients = np.empty(0, dtype=np.float64)

    if len(previous_magnitudes):
        phase_delta = _wrapped_phase_delta(phases, previous_phases[-1])
        magnitude_transient = 0.5 * float(
            np.sum(
                np.abs(
                    _normalized_magnitudes(magnitudes)
                    - _normalized_magnitudes(previous_magnitudes[-1])
                )
            )
        )
        phase_weights = _normalized_magnitudes(magnitudes)
        phase_transient = float(
            np.sum(phase_weights * np.abs(phase_delta)) / np.pi
        )
    else:
        phase_delta = np.zeros(mode_count, dtype=np.float64)
        magnitude_transient = 0.0
        phase_transient = 0.0

    keep = max(0, depth - 1)
    start = max(0, len(previous_revisions) - keep)
    revisions = np.concatenate(
        (previous_revisions[start:], np.asarray([frame.revision], dtype=np.int64))
    )
    magnitude_history = np.vstack((previous_magnitudes[start:], magnitudes))
    phase_history = np.vstack((previous_phases[start:], phases))
    phase_delta_history = np.vstack((previous_phase_deltas[start:], phase_delta))
    frequency_history = np.vstack((previous_frequencies[start:], frequencies))
    decay_history = np.vstack((previous_decay[start:], decay))
    magnitude_transients = np.concatenate(
        (previous_transients[start:], np.asarray([magnitude_transient]))
    )
    phase_transients = np.concatenate(
        (previous_phase_transients[start:], np.asarray([phase_transient]))
    )
    combined_transients = np.clip(
        0.75 * magnitude_transients + 0.25 * phase_transients,
        0.0,
        1.0,
    )
    return {
        "revisions": revisions,
        "magnitudes": magnitude_history,
        "phases": phase_history,
        "phase_deltas": phase_delta_history,
        "frequencies_hz": frequency_history,
        "decay_seconds": decay_history,
        "magnitude_transients": magnitude_transients,
        "phase_transients": phase_transients,
        "transients": combined_transients,
        "phase_domain": np.asarray("complex_eigenfield_mode"),
    }


def export_spectral_history(payload: dict[str, np.ndarray], path: str | Path) -> Path:
    output = Path(path)
    np.savez_compressed(output, **payload)
    return output
