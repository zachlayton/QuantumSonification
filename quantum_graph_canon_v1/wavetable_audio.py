"""Direct density-matrix wavetable synthesis for Quantum Graph Canon v1.

This module deliberately does not pass through MIDI.  Each computational-basis
row of a 16 x 16 four-qubit density matrix drives one continuously running
oscillator.  The row's 16 complex entries become the first 16 harmonics of a
256-sample wavetable, preserving both magnitude and phase information.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import math
from pathlib import Path
from typing import Any, Sequence
import wave

import numpy as np


@dataclass(frozen=True)
class DensityWavetableRenderConfig:
    """Controls for the fixed 16-voice, 256-point density synthesizer."""

    sample_rate: int = 48_000
    duration_seconds: float = 16.0
    control_rate_hz: float = 60.0
    wavetable_size: int = 256
    voice_count: int = 16
    base_frequency_hz: float = 55.0
    tuning_semitones: tuple[float, ...] = (
        0.0,
        2.0,
        4.0,
        7.0,
        9.0,
        12.0,
        14.0,
        16.0,
        19.0,
        21.0,
        24.0,
        26.0,
        28.0,
        31.0,
        33.0,
        36.0,
    )
    harmonic_tilt: float = 0.65
    amplitude_gamma: float = 0.65
    maximum_pitch_bend_semitones: float = 0.5
    stereo_width: float = 0.9
    fade_seconds: float = 0.03
    output_ceiling: float = 0.85

    def __post_init__(self) -> None:
        for name, value in (
            ("sample_rate", self.sample_rate),
            ("wavetable_size", self.wavetable_size),
            ("voice_count", self.voice_count),
        ):
            if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
                raise ValueError(f"{name} must be a positive integer")
        if self.wavetable_size != 256:
            raise ValueError("wavetable_size must be exactly 256")
        if self.voice_count != 16:
            raise ValueError("voice_count must be exactly 16")
        if len(self.tuning_semitones) != self.voice_count:
            raise ValueError("tuning_semitones must contain one value per voice")
        finite_positive = (
            ("duration_seconds", self.duration_seconds),
            ("control_rate_hz", self.control_rate_hz),
            ("base_frequency_hz", self.base_frequency_hz),
        )
        for name, value in finite_positive:
            if not math.isfinite(value) or value <= 0.0:
                raise ValueError(f"{name} must be finite and positive")
        if not all(math.isfinite(value) for value in self.tuning_semitones):
            raise ValueError("tuning_semitones must all be finite")
        if not math.isfinite(self.harmonic_tilt) or self.harmonic_tilt < 0.0:
            raise ValueError("harmonic_tilt must be finite and nonnegative")
        if not math.isfinite(self.amplitude_gamma) or self.amplitude_gamma <= 0.0:
            raise ValueError("amplitude_gamma must be finite and positive")
        if (
            not math.isfinite(self.maximum_pitch_bend_semitones)
            or self.maximum_pitch_bend_semitones < 0.0
        ):
            raise ValueError(
                "maximum_pitch_bend_semitones must be finite and nonnegative"
            )
        if not math.isfinite(self.stereo_width) or not 0.0 <= self.stereo_width <= 1.0:
            raise ValueError("stereo_width must lie in [0, 1]")
        if not math.isfinite(self.fade_seconds) or self.fade_seconds < 0.0:
            raise ValueError("fade_seconds must be finite and nonnegative")
        if (
            not math.isfinite(self.output_ceiling)
            or not 0.0 < self.output_ceiling <= 1.0
        ):
            raise ValueError("output_ceiling must lie in (0, 1]")


@dataclass(frozen=True)
class DensityWavetableRenderResult:
    """Rendered floating-point stereo audio and reproducibility diagnostics."""

    audio: np.ndarray
    sample_rate: int
    snapshot_count: int
    peak_before_normalization: float
    peak_after_normalization: float
    rms_after_normalization: float
    normalization_gain: float


@dataclass(frozen=True)
class ArticulatedDensityWavetableConfig(DensityWavetableRenderConfig):
    """Controls for the event-based density wavetable composition."""

    duration_seconds: float = 24.0
    maximum_pitch_bend_semitones: float = 1.75
    tempo_bpm: float = 92.0
    subdivisions_per_beat: int = 4
    event_probability_floor: float = 0.025
    event_probability_scale: float = 0.62
    population_compression: float = 0.32
    minimum_gate_steps: float = 0.28
    maximum_gate_steps: float = 1.05
    coherence_subdivision_scale: float = 0.68
    section_hold_fraction: float = 0.72

    def __post_init__(self) -> None:
        super().__post_init__()
        if not math.isfinite(self.tempo_bpm) or self.tempo_bpm <= 0.0:
            raise ValueError("tempo_bpm must be finite and positive")
        if (
            isinstance(self.subdivisions_per_beat, bool)
            or not isinstance(self.subdivisions_per_beat, int)
            or self.subdivisions_per_beat <= 0
        ):
            raise ValueError("subdivisions_per_beat must be a positive integer")
        for name, value in (
            ("event_probability_floor", self.event_probability_floor),
            ("event_probability_scale", self.event_probability_scale),
            ("coherence_subdivision_scale", self.coherence_subdivision_scale),
            ("section_hold_fraction", self.section_hold_fraction),
        ):
            if not math.isfinite(value) or not 0.0 <= value <= 1.0:
                raise ValueError(f"{name} must lie in [0, 1]")
        if (
            not math.isfinite(self.population_compression)
            or self.population_compression <= 0.0
        ):
            raise ValueError("population_compression must be finite and positive")
        if (
            not math.isfinite(self.minimum_gate_steps)
            or self.minimum_gate_steps <= 0.0
        ):
            raise ValueError("minimum_gate_steps must be finite and positive")
        if (
            not math.isfinite(self.maximum_gate_steps)
            or self.maximum_gate_steps < self.minimum_gate_steps
        ):
            raise ValueError(
                "maximum_gate_steps must be finite and at least minimum_gate_steps"
            )


@dataclass(frozen=True)
class ArticulatedDensityWavetableRenderResult(DensityWavetableRenderResult):
    """An event render plus articulation diagnostics."""

    event_count: int
    subdivision_event_count: int
    events_by_voice: tuple[int, ...]
    events_by_section: tuple[int, ...]
    voice_offsets: tuple[int, ...]


def voice_wavetables_from_density(
    density: np.ndarray,
    config: DensityWavetableRenderConfig | None = None,
) -> np.ndarray:
    """Map all 256 complex density entries to 16 phase-aware wavetables.

    Density row ``i`` drives voice ``i``.  Column ``j`` maps to harmonic
    ``((j - i) mod 16) + 1``, which places the real diagonal population on the
    fundamental while retaining every off-diagonal coherence as a complex
    harmonic coefficient.
    """
    selected = config or DensityWavetableRenderConfig()
    rho = _validated_density(density, selected.voice_count)
    coefficients = np.empty((selected.voice_count, selected.voice_count), complex)
    for voice in range(selected.voice_count):
        for column in range(selected.voice_count):
            harmonic_index = (column - voice) % selected.voice_count
            coefficients[voice, harmonic_index] = rho[voice, column]

    harmonics = np.arange(1, selected.voice_count + 1, dtype=float)
    phases = math.tau * np.arange(selected.wavetable_size) / selected.wavetable_size
    basis = np.exp(1j * np.outer(harmonics, phases))
    tilted = coefficients / harmonics[np.newaxis, :] ** selected.harmonic_tilt
    tables = np.real(tilted @ basis)
    tables -= np.mean(tables, axis=1, keepdims=True)
    peaks = np.max(np.abs(tables), axis=1)
    active = peaks > 1e-15
    tables[active] /= peaks[active, np.newaxis]
    tables[~active] = 0.0
    return np.asarray(tables, dtype=np.float64)


def density_voice_parameters(
    density: np.ndarray,
    config: DensityWavetableRenderConfig | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    """Return density-derived relative amplitudes and frequencies for 16 voices."""
    selected = config or DensityWavetableRenderConfig()
    rho = _validated_density(density, selected.voice_count)
    row_energy = np.linalg.norm(rho, axis=1)
    amplitudes = np.power(row_energy, selected.amplitude_gamma)
    amplitude_norm = float(np.linalg.norm(amplitudes))
    if amplitude_norm > 1e-15:
        amplitudes /= amplitude_norm

    off_diagonal = rho.copy()
    np.fill_diagonal(off_diagonal, 0.0)
    coherence_scale = np.sum(np.abs(off_diagonal), axis=1)
    signed_phase = np.divide(
        np.imag(np.sum(off_diagonal, axis=1)),
        coherence_scale,
        out=np.zeros(selected.voice_count, dtype=float),
        where=coherence_scale > 1e-15,
    )
    bends = selected.maximum_pitch_bend_semitones * np.clip(
        signed_phase,
        -1.0,
        1.0,
    )
    semitones = np.asarray(selected.tuning_semitones, dtype=float) + bends
    frequencies = selected.base_frequency_hz * np.power(2.0, semitones / 12.0)
    return amplitudes, frequencies


def render_density_wavetable_bank(
    density_snapshots: Sequence[np.ndarray],
    config: DensityWavetableRenderConfig | None = None,
) -> DensityWavetableRenderResult:
    """Synthesize stereo audio directly from evolving density matrices."""
    selected = config or DensityWavetableRenderConfig()
    snapshots = tuple(
        _validated_density(snapshot, selected.voice_count)
        for snapshot in density_snapshots
    )
    if not snapshots:
        raise ValueError("density_snapshots must contain at least one matrix")

    sample_count = int(round(selected.duration_seconds * selected.sample_rate))
    if sample_count < 2:
        raise ValueError("duration and sample rate must produce at least two samples")
    block_size = max(1, int(round(selected.sample_rate / selected.control_rate_hz)))
    audio = np.zeros((sample_count, 2), dtype=np.float64)
    phases = np.zeros(selected.voice_count, dtype=np.float64)

    pan_positions = np.linspace(
        -selected.stereo_width,
        selected.stereo_width,
        selected.voice_count,
    )
    pan_angles = (pan_positions + 1.0) * math.pi / 4.0
    pan_left = np.cos(pan_angles)
    pan_right = np.sin(pan_angles)

    for block_start in range(0, sample_count, block_size):
        block_end = min(sample_count, block_start + block_size)
        frame_count = block_end - block_start
        start_unit = block_start / (sample_count - 1)
        end_unit = (block_end - 1) / (sample_count - 1)
        density_start = _interpolate_snapshots(snapshots, start_unit)
        density_end = _interpolate_snapshots(snapshots, end_unit)
        tables_start = voice_wavetables_from_density(density_start, selected)
        tables_end = voice_wavetables_from_density(density_end, selected)
        amplitudes_start, frequencies_start = density_voice_parameters(
            density_start,
            selected,
        )
        amplitudes_end, frequencies_end = density_voice_parameters(
            density_end,
            selected,
        )
        blend = np.linspace(0.0, 1.0, frame_count, endpoint=True)

        for voice in range(selected.voice_count):
            frequencies = (
                frequencies_start[voice]
                + (frequencies_end[voice] - frequencies_start[voice]) * blend
            )
            cycle_offsets = np.empty(frame_count, dtype=float)
            cycle_offsets[0] = 0.0
            if frame_count > 1:
                cycle_offsets[1:] = np.cumsum(frequencies[:-1]) / selected.sample_rate
            voice_phases = np.mod(phases[voice] + cycle_offsets, 1.0)
            phases[voice] = float(
                np.mod(phases[voice] + np.sum(frequencies) / selected.sample_rate, 1.0)
            )
            start_wave = _lookup_wavetable(tables_start[voice], voice_phases)
            end_wave = _lookup_wavetable(tables_end[voice], voice_phases)
            waveform = start_wave + (end_wave - start_wave) * blend
            amplitudes = (
                amplitudes_start[voice]
                + (amplitudes_end[voice] - amplitudes_start[voice]) * blend
            )
            signal = waveform * amplitudes
            audio[block_start:block_end, 0] += signal * pan_left[voice]
            audio[block_start:block_end, 1] += signal * pan_right[voice]

    audio -= np.mean(audio, axis=0, keepdims=True)
    fade_samples = min(
        int(round(selected.fade_seconds * selected.sample_rate)),
        sample_count // 2,
    )
    if fade_samples > 0:
        fade = np.linspace(0.0, 1.0, fade_samples, endpoint=True)
        audio[:fade_samples] *= fade[:, np.newaxis]
        audio[-fade_samples:] *= fade[::-1, np.newaxis]

    peak_before = float(np.max(np.abs(audio)))
    if peak_before <= 1e-15:
        raise ValueError("density snapshots produced silent audio")
    normalization_gain = selected.output_ceiling / peak_before
    audio *= normalization_gain
    np.clip(audio, -selected.output_ceiling, selected.output_ceiling, out=audio)
    peak_after = float(np.max(np.abs(audio)))
    rms_after = float(np.sqrt(np.mean(np.square(audio))))
    return DensityWavetableRenderResult(
        audio=audio,
        sample_rate=selected.sample_rate,
        snapshot_count=len(snapshots),
        peak_before_normalization=peak_before,
        peak_after_normalization=peak_after,
        rms_after_normalization=rms_after,
        normalization_gain=normalization_gain,
    )


def graph_qnn_voice_offsets(
    graph_edges: Sequence[tuple[int, int]],
    selected_mask: int,
) -> tuple[int, ...]:
    """Derive 16 canon offsets from quotient-graph distance to a QNN mask."""
    import networkx as nx

    if isinstance(selected_mask, bool) or not isinstance(selected_mask, int):
        raise ValueError("selected_mask must be an integer")
    if not 0 <= selected_mask < 16:
        raise ValueError("selected_mask must lie in [0, 15]")
    graph = nx.Graph()
    graph.add_nodes_from(range(4))
    graph.add_edges_from((int(start), int(end)) for start, end in graph_edges)
    if not nx.is_connected(graph):
        raise ValueError("graph_edges must connect qubits 0 through 3")
    selected_nodes = [qubit for qubit in range(4) if (selected_mask >> qubit) & 1]
    if not selected_nodes:
        selected_nodes = [max(graph.nodes, key=lambda node: (graph.degree(node), -node))]
    path_lengths = dict(nx.all_pairs_shortest_path_length(graph))

    offsets = []
    for voice in range(16):
        active_nodes = [qubit for qubit in range(4) if (voice >> qubit) & 1]
        graph_distance = sum(
            min(path_lengths[node][selected] for selected in selected_nodes)
            for node in active_nodes
        )
        hamming_distance = (voice ^ selected_mask).bit_count()
        offsets.append((hamming_distance + 2 * graph_distance) % 8)
    return tuple(offsets)


def render_articulated_density_wavetable_bank(
    density_snapshots: Sequence[np.ndarray],
    config: ArticulatedDensityWavetableConfig | None = None,
    *,
    voice_offsets: Sequence[int] | None = None,
    qnn_probabilities: Sequence[float] | None = None,
) -> ArticulatedDensityWavetableRenderResult:
    """Render density matrices as discrete, coherence-driven musical events."""
    selected = config or ArticulatedDensityWavetableConfig()
    snapshots = tuple(
        _validated_density(snapshot, selected.voice_count)
        for snapshot in density_snapshots
    )
    if not snapshots:
        raise ValueError("density_snapshots must contain at least one matrix")

    offsets = _validated_voice_offsets(voice_offsets, selected.voice_count)
    qnn_drive = _validated_qnn_drive(qnn_probabilities, selected.voice_count)
    sample_count = int(round(selected.duration_seconds * selected.sample_rate))
    if sample_count < 2:
        raise ValueError("duration and sample rate must produce at least two samples")
    step_seconds = 60.0 / selected.tempo_bpm / selected.subdivisions_per_beat
    step_samples = step_seconds * selected.sample_rate
    step_count = int(math.ceil(sample_count / step_samples))
    audio = np.zeros((sample_count, 2), dtype=np.float64)

    pan_positions = np.linspace(
        -selected.stereo_width,
        selected.stereo_width,
        selected.voice_count,
    )
    pan_angles = (pan_positions + 1.0) * math.pi / 4.0
    pan_left = np.cos(pan_angles)
    pan_right = np.sin(pan_angles)
    events_by_voice = np.zeros(selected.voice_count, dtype=int)
    events_by_section = np.zeros(len(snapshots), dtype=int)
    event_count = 0
    subdivision_event_count = 0

    for step in range(step_count):
        event_start = int(round(step * step_samples))
        if event_start >= sample_count:
            break
        unit_time = event_start / (sample_count - 1)
        density, section = _sectioned_density(
            snapshots,
            unit_time,
            selected.section_hold_fraction,
        )
        tables = voice_wavetables_from_density(density, selected)
        _, frequencies = density_voice_parameters(density, selected)
        row_energy = np.linalg.norm(density, axis=1)
        population = np.clip(np.real(np.diag(density)), 0.0, None)
        off_diagonal = density.copy()
        np.fill_diagonal(off_diagonal, 0.0)
        coherence = np.sum(np.abs(off_diagonal), axis=1)

        energy_drive = np.power(
            row_energy / max(float(np.max(row_energy)), 1e-15),
            selected.population_compression,
        )
        population_drive = np.power(
            population / max(float(np.max(population)), 1e-15),
            selected.population_compression,
        )
        density_drive = 0.72 * energy_drive + 0.28 * population_drive
        coherence_drive = coherence / max(float(np.max(coherence)), 1e-15)
        section_activity = 0.36 + 0.64 * section / max(len(snapshots) - 1, 1)

        for voice in range(selected.voice_count):
            if step < offsets[voice]:
                continue
            rhythmic_phase = (step - offsets[voice]) % 16
            period = 3 + voice % 5
            structural_accent = rhythmic_phase in {0, 6, 10} or (
                step - offsets[voice]
            ) % period == 0
            event_probability = (
                selected.event_probability_floor
                + selected.event_probability_scale
                * section_activity
                * density_drive[voice]
                * (0.48 + 0.52 * qnn_drive[voice])
                + (0.15 * density_drive[voice] if structural_accent else 0.0)
            )
            event_probability = float(np.clip(event_probability, 0.0, 0.94))
            if _deterministic_unit(step, voice, section) >= event_probability:
                continue

            gate_steps = selected.minimum_gate_steps + (
                selected.maximum_gate_steps - selected.minimum_gate_steps
            ) * (0.20 + 0.80 * coherence_drive[voice])
            duration_samples = max(3, int(round(gate_steps * step_samples)))
            amplitude = (
                density_drive[voice]
                * (0.50 + 0.50 * qnn_drive[voice])
                * (1.18 if structural_accent else 0.88)
            )
            coherence_sum = np.sum(off_diagonal[voice])
            initial_phase = float(np.angle(coherence_sum) / math.tau) % 1.0
            _add_articulated_event(
                audio,
                event_start,
                duration_samples,
                tables[voice],
                float(frequencies[voice]),
                float(amplitude),
                initial_phase,
                float(coherence_drive[voice]),
                float(pan_left[voice]),
                float(pan_right[voice]),
                selected.sample_rate,
            )
            event_count += 1
            events_by_voice[voice] += 1
            events_by_section[section] += 1

            subdivision_probability = (
                selected.coherence_subdivision_scale
                * section_activity
                * coherence_drive[voice]
            )
            if (
                _deterministic_unit(step, voice, section + 37)
                < subdivision_probability
            ):
                subdivision_start = event_start + int(round(step_samples / 2.0))
                if subdivision_start < sample_count:
                    _add_articulated_event(
                        audio,
                        subdivision_start,
                        max(3, int(round(duration_samples * 0.58))),
                        tables[voice],
                        float(frequencies[voice]),
                        float(amplitude * 0.55),
                        (initial_phase + 0.5 * coherence_drive[voice]) % 1.0,
                        float(coherence_drive[voice]),
                        float(pan_left[voice]),
                        float(pan_right[voice]),
                        selected.sample_rate,
                    )
                    event_count += 1
                    subdivision_event_count += 1
                    events_by_voice[voice] += 1
                    events_by_section[section] += 1

    audio -= np.mean(audio, axis=0, keepdims=True)
    fade_samples = min(
        int(round(selected.fade_seconds * selected.sample_rate)),
        sample_count // 2,
    )
    if fade_samples > 0:
        fade = np.linspace(0.0, 1.0, fade_samples, endpoint=True)
        audio[:fade_samples] *= fade[:, np.newaxis]
        audio[-fade_samples:] *= fade[::-1, np.newaxis]

    peak_before = float(np.max(np.abs(audio)))
    if peak_before <= 1e-15:
        raise ValueError("density snapshots produced silent articulated audio")
    normalization_gain = selected.output_ceiling / peak_before
    audio *= normalization_gain
    np.clip(audio, -selected.output_ceiling, selected.output_ceiling, out=audio)
    return ArticulatedDensityWavetableRenderResult(
        audio=audio,
        sample_rate=selected.sample_rate,
        snapshot_count=len(snapshots),
        peak_before_normalization=peak_before,
        peak_after_normalization=float(np.max(np.abs(audio))),
        rms_after_normalization=float(np.sqrt(np.mean(np.square(audio)))),
        normalization_gain=normalization_gain,
        event_count=event_count,
        subdivision_event_count=subdivision_event_count,
        events_by_voice=tuple(int(value) for value in events_by_voice),
        events_by_section=tuple(int(value) for value in events_by_section),
        voice_offsets=offsets,
    )


def write_density_wavetable_wav(
    path: str | Path,
    result: DensityWavetableRenderResult,
) -> Path:
    """Write a render result as stereo 16-bit PCM WAV."""
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    audio = np.asarray(result.audio, dtype=float)
    if audio.ndim != 2 or audio.shape[1] != 2:
        raise ValueError("result audio must have shape (sample_count, 2)")
    if not np.all(np.isfinite(audio)):
        raise ValueError("result audio must contain only finite samples")
    pcm = np.round(np.clip(audio, -1.0, 1.0) * 32767.0).astype("<i2")
    with wave.open(str(output), "wb") as wav_file:
        wav_file.setnchannels(2)
        wav_file.setsampwidth(2)
        wav_file.setframerate(result.sample_rate)
        wav_file.writeframes(pcm.tobytes())
    return output


def density_wavetable_manifest(
    result: DensityWavetableRenderResult,
    config: DensityWavetableRenderConfig,
    density_snapshots: Sequence[np.ndarray],
) -> dict[str, Any]:
    """Describe the direct audio mapping and numerical render diagnostics."""
    snapshots = tuple(
        _validated_density(snapshot, config.voice_count)
        for snapshot in density_snapshots
    )
    return {
        "synthesis_path": "density_matrix_to_wavetable_bank_to_pcm_wav",
        "direct_synthesis": True,
        "midi_source": False,
        "voice_semantics": "one oscillator per four-qubit computational-basis row",
        "wavetable_mapping": (
            "rho[i,j] -> complex harmonic ((j-i) mod 16)+1 of voice i; "
            "rho[i,i] -> fundamental"
        ),
        "temporal_mapping": "piecewise-linear interpolation across density snapshots",
        "config": asdict(config),
        "render": {
            "channel_count": 2,
            "sample_count": int(result.audio.shape[0]),
            "snapshot_count": result.snapshot_count,
            "duration_seconds": result.audio.shape[0] / result.sample_rate,
            "peak_before_normalization": result.peak_before_normalization,
            "peak_after_normalization": result.peak_after_normalization,
            "rms_after_normalization": result.rms_after_normalization,
            "normalization_gain": result.normalization_gain,
            "clipped_sample_count": int(
                np.count_nonzero(np.abs(result.audio) > config.output_ceiling + 1e-12)
            ),
        },
        "density_snapshots": [
            {
                "index": index,
                "trace_real": float(np.real(np.trace(snapshot))),
                "purity": float(np.real(np.trace(snapshot @ snapshot))),
                "minimum_population": float(np.min(np.real(np.diag(snapshot)))),
                "maximum_population": float(np.max(np.real(np.diag(snapshot)))),
                "minimum_row_energy": float(np.min(np.linalg.norm(snapshot, axis=1))),
                "maximum_row_energy": float(np.max(np.linalg.norm(snapshot, axis=1))),
            }
            for index, snapshot in enumerate(snapshots)
        ],
    }


def articulated_density_wavetable_manifest(
    result: ArticulatedDensityWavetableRenderResult,
    config: ArticulatedDensityWavetableConfig,
    density_snapshots: Sequence[np.ndarray],
    qnn_probabilities: Sequence[float] | None = None,
) -> dict[str, Any]:
    """Describe the event-based density synthesis and articulation counts."""
    manifest = density_wavetable_manifest(
        result,
        config,
        density_snapshots,
    )
    manifest.update(
        synthesis_path=(
            "density_matrix_to_population_coherence_events_to_"
            "wavetable_bank_to_pcm_wav"
        ),
        temporal_mapping=(
            "four held density sections with crossfades; diagonal population and "
            "row energy trigger envelopes; coherence generates subdivisions"
        ),
        articulation={
            "event_source": "density population, row energy, and coherence",
            "rhythmic_offsets_source": (
                "NetworkX quotient shortest-path distance to QNN selected mask"
            ),
            "qnn_probabilities_condition_event_likelihood": (
                qnn_probabilities is not None
            ),
            "voice_offsets_in_subdivision_steps": list(result.voice_offsets),
            "events_by_voice": list(result.events_by_voice),
            "events_by_section": list(result.events_by_section),
        },
    )
    manifest["render"].update(
        event_count=result.event_count,
        primary_event_count=(
            result.event_count - result.subdivision_event_count
        ),
        coherence_subdivision_event_count=result.subdivision_event_count,
    )
    return manifest


def _validated_density(density: np.ndarray, dimension: int) -> np.ndarray:
    rho = np.asarray(density, dtype=np.complex128)
    if rho.shape != (dimension, dimension):
        raise ValueError(f"density matrix must have shape ({dimension}, {dimension})")
    if not np.all(np.isfinite(rho)):
        raise ValueError("density matrix must contain only finite values")
    if not np.allclose(rho, rho.conj().T, atol=1e-9):
        raise ValueError("density matrix must be Hermitian")
    trace = np.trace(rho)
    if abs(float(np.imag(trace))) > 1e-9 or float(np.real(trace)) <= 0.0:
        raise ValueError("density matrix must have a positive real trace")
    return rho / float(np.real(trace))


def _validated_voice_offsets(
    voice_offsets: Sequence[int] | None,
    voice_count: int,
) -> tuple[int, ...]:
    if voice_offsets is None:
        return tuple(0 for _ in range(voice_count))
    offsets = tuple(voice_offsets)
    if len(offsets) != voice_count:
        raise ValueError("voice_offsets must contain one offset per voice")
    if any(
        isinstance(value, bool) or not isinstance(value, (int, np.integer)) or value < 0
        for value in offsets
    ):
        raise ValueError("voice_offsets must contain nonnegative integers")
    return tuple(int(value) for value in offsets)


def _validated_qnn_drive(
    qnn_probabilities: Sequence[float] | None,
    voice_count: int,
) -> np.ndarray:
    if qnn_probabilities is None:
        return np.ones(voice_count, dtype=float)
    values = np.asarray(qnn_probabilities, dtype=float)
    if values.shape != (voice_count,):
        raise ValueError("qnn_probabilities must contain one value per voice")
    if not np.all(np.isfinite(values)) or np.any(values < 0.0):
        raise ValueError("qnn_probabilities must be finite and nonnegative")
    maximum = float(np.max(values))
    if maximum <= 0.0:
        raise ValueError("qnn_probabilities must contain positive mass")
    return np.power(values / maximum, 0.22)


def _sectioned_density(
    snapshots: tuple[np.ndarray, ...],
    unit_time: float,
    hold_fraction: float,
) -> tuple[np.ndarray, int]:
    if len(snapshots) == 1:
        return snapshots[0], 0
    position = float(np.clip(unit_time, 0.0, 1.0)) * len(snapshots)
    section = min(int(math.floor(position)), len(snapshots) - 1)
    if section == len(snapshots) - 1:
        return snapshots[section], section
    local_position = position - section
    if local_position <= hold_fraction:
        return snapshots[section], section
    blend = (local_position - hold_fraction) / (1.0 - hold_fraction)
    smooth_blend = blend * blend * (3.0 - 2.0 * blend)
    density = (
        (1.0 - smooth_blend) * snapshots[section]
        + smooth_blend * snapshots[section + 1]
    )
    return density, section


def _deterministic_unit(step: int, voice: int, salt: int) -> float:
    value = (
        ((step + 1) * 0x9E3779B1)
        ^ ((voice + 1) * 0x85EBCA77)
        ^ ((salt + 1) * 0xC2B2AE3D)
    ) & 0xFFFFFFFF
    value ^= value >> 16
    value = (value * 0x7FEB352D) & 0xFFFFFFFF
    value ^= value >> 15
    value = (value * 0x846CA68B) & 0xFFFFFFFF
    value ^= value >> 16
    return value / 2**32


def _add_articulated_event(
    audio: np.ndarray,
    start_sample: int,
    duration_samples: int,
    table: np.ndarray,
    frequency: float,
    amplitude: float,
    initial_phase: float,
    coherence_drive: float,
    pan_left: float,
    pan_right: float,
    sample_rate: int,
) -> None:
    end_sample = min(len(audio), start_sample + duration_samples)
    frame_count = end_sample - start_sample
    if frame_count < 3:
        return
    time = np.arange(frame_count, dtype=float) / sample_rate
    vibrato_rate = 3.0 + 3.0 * coherence_drive
    vibrato_depth = 0.001 + 0.006 * coherence_drive
    phase_modulation = (
        vibrato_depth
        * frequency
        / vibrato_rate
        * (1.0 - np.cos(math.tau * vibrato_rate * time))
        / math.tau
    )
    phases = np.mod(initial_phase + frequency * time + phase_modulation, 1.0)
    waveform = _lookup_wavetable(table, phases)

    attack_samples = max(2, min(frame_count - 1, int(round(frame_count * 0.08))))
    envelope = np.empty(frame_count, dtype=float)
    envelope[:attack_samples] = np.sin(
        np.linspace(0.0, math.pi / 2.0, attack_samples, endpoint=False)
    ) ** 1.5
    release_position = np.linspace(
        0.0,
        1.0,
        frame_count - attack_samples,
        endpoint=True,
    )
    envelope[attack_samples:] = np.exp(-3.8 * release_position) * (
        1.0 - release_position
    )
    signal = waveform * envelope * amplitude
    audio[start_sample:end_sample, 0] += signal * pan_left
    audio[start_sample:end_sample, 1] += signal * pan_right


def _interpolate_snapshots(
    snapshots: tuple[np.ndarray, ...],
    unit_time: float,
) -> np.ndarray:
    if len(snapshots) == 1:
        return snapshots[0]
    position = float(np.clip(unit_time, 0.0, 1.0)) * (len(snapshots) - 1)
    start = min(int(math.floor(position)), len(snapshots) - 1)
    end = min(start + 1, len(snapshots) - 1)
    blend = position - start
    return (1.0 - blend) * snapshots[start] + blend * snapshots[end]


def _lookup_wavetable(table: np.ndarray, phases: np.ndarray) -> np.ndarray:
    positions = phases * len(table)
    lower = np.floor(positions).astype(int) % len(table)
    upper = (lower + 1) % len(table)
    fractions = positions - np.floor(positions)
    return table[lower] + (table[upper] - table[lower]) * fractions
