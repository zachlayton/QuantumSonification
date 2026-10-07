"""Declared musical mappings. None of these choices changes physical state."""
from __future__ import annotations

import numpy as np
from qmw.core.frame import EventType, PhysicsFrame, SoundControlFrame, SoundEvent


class SonificationPolicy:
    """Map regional flux events to integer-harmonic plucks.

    ``gain`` is an audio amplitude ceiling. ``flux_scale`` is a musical reference
    for source magnitudes in scaled simulation units; it is not a physical gain.
    An optional ``mode_sqrt`` pitch mapping interprets positive modal eigenvalues
    through a declared square-root ratio, with an explicit fundamental in Hz.
    """

    def __init__(self, fundamental_hz=110.0, decay_s=1.5, gain=0.18,
                 flux_scale=1.0, pitch_mapping="harmonic"):
        values = np.array([fundamental_hz, decay_s, gain, flux_scale], float)
        if not np.isfinite(values).all() or fundamental_hz <= 0 or decay_s <= 0 or flux_scale <= 0:
            raise ValueError("Fundamental, decay and source reference must be finite and positive")
        if not 0 <= gain <= 0.95:
            raise ValueError("Audio gain must lie in [0, 0.95]")
        if pitch_mapping not in {"harmonic", "mode_sqrt"}:
            raise ValueError("Unknown pitch mapping")
        self.fundamental_hz = float(fundamental_hz)
        self.decay_s = float(decay_s)
        self.gain = float(gain)
        self.flux_scale = float(flux_scale)
        self.pitch_mapping = pitch_mapping

    def map(self, physics: PhysicsFrame) -> SoundControlFrame:
        if physics.regions is not None:
            count = len(physics.regions.centers)
        elif physics.modes is not None:
            count = len(physics.modes.populations)
        else:
            count = 16
        if count < 1:
            raise ValueError("Sound requires at least one voice")
        ratios = np.arange(1, count + 1, dtype=float)
        pitch_description = "integer harmonic ratio"
        if self.pitch_mapping == "mode_sqrt":
            if physics.modes is None or len(physics.modes.eigenvalues) < count:
                raise ValueError("Square-root pitch mapping requires one eigenvalue per voice")
            if physics.modes.operator_semantics in {"basis_index_not_energy", "density_matrix_eigenvalues"}:
                raise ValueError("Bookkeeping indices and density-matrix eigenvalues are not geometric acoustic modes")
            eigenvalues = np.asarray(physics.modes.eigenvalues[:count], float)
            positive = eigenvalues[eigenvalues > 1e-12]
            if not len(positive):
                raise ValueError("Square-root pitch mapping requires positive eigenvalues")
            ratios = np.sqrt(np.maximum(eigenvalues, 0) / positive.min())
            ratios[eigenvalues <= 1e-12] = 1.0
            pitch_description = "declared sqrt(eigenvalue/reference) ratio; zero modes use f₀"
        frequencies = self.fundamental_hz * ratios

        energy = None
        if physics.regions is not None and physics.regions.energy is not None:
            energy = np.maximum(physics.regions.energy, 0)
        elif physics.modes is not None:
            energy = np.maximum(physics.modes.populations[:count], 0)
        amplitudes = np.zeros(count)
        if energy is not None and np.sum(energy) > 0:
            amplitudes = self.gain * np.sqrt(energy / np.sum(energy))
        phases = np.zeros(count)
        if physics.modes is not None and physics.modes.coefficients is not None:
            coefficients = physics.modes.coefficients
            phases[:min(count, len(coefficients))] = np.angle(coefficients[:count])

        sound_events = []
        for event_index, event in enumerate(physics.events):
            if event.type not in {EventType.ENERGY_ARRIVAL, EventType.MODE_CROSSING}:
                continue
            if not np.isfinite(event.magnitude) or event.magnitude <= 0:
                continue
            voice = event.region if event.region is not None else event.mode
            if voice is None or not 0 <= voice < count:
                continue
            source_fraction = min(event.magnitude / self.flux_scale, 1.0)
            amplitude = self.gain * np.sqrt(source_fraction)
            pan = 0.0 if count == 1 else 1.7 * voice / (count - 1) - 0.85
            detail = event.detail.strip() or "The detector emitted a physical source event."
            explanation = (
                f"{detail} Source {event.source_observable}={event.magnitude:.6g} "
                f"in scaled simulation units. Voice {voice + 1}: "
                f"f₀={self.fundamental_hz:g} Hz × {ratios[voice]:.6g} ({pitch_description}) "
                f"→ {frequencies[voice]:.6g} Hz. Audio amplitude "
                f"{self.gain:g} × sqrt(min(source/{self.flux_scale:g}, 1)) "
                f"= {amplitude:.6g}; decay={self.decay_s:g} s; pan={pan:.3g}."
            )
            event_id = f"{physics.model_id}:{physics.sequence}:{event_index}:{event.type.value}"
            sound_events.append(SoundEvent(event_id, float(event.t), float(frequencies[voice]),
                                           float(amplitude), self.decay_s, float(pan),
                                           event.region, event.mode, event.source_observable,
                                           explanation))
        return SoundControlFrame(physics.sequence, physics.t, frequencies,
                                 amplitudes, np.full(count, self.decay_s), phases,
                                 sound_events, f"{self.pitch_mapping}-plucks")
