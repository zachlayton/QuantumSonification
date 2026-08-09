"""Dense H2 feature extraction and deterministic offline sonification."""

from __future__ import annotations

import json
import wave
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import numpy as np
from scipy.constants import physical_constants

from .h2_sweep import analyze_h2_point


@dataclass(frozen=True)
class DissociationConfig:
    distance_start: float = 0.3
    distance_stop: float = 3.0
    num_points: int = 61
    basis: str = "sto3g"
    num_eigenstates: int = 6
    duration_seconds: float = 36.0
    sample_rate: int = 48_000
    base_frequency_hz: float = 90.0

    def validate(self) -> None:
        if not 0 < self.distance_start < self.distance_stop:
            raise ValueError("require 0 < distance_start < distance_stop")
        if self.num_points < 3:
            raise ValueError("num_points must be at least 3")
        if self.duration_seconds <= 0 or self.sample_rate < 8_000:
            raise ValueError("invalid audio duration or sample rate")
        if self.base_frequency_hz <= 0:
            raise ValueError("base_frequency_hz must be positive")


def _natural_occupation_entropy(occupations: np.ndarray) -> float:
    probabilities = occupations / occupations.sum()
    active = probabilities[probabilities > 1e-15]
    return float(-np.sum(active * np.log2(active)))


def extract_features(point: dict[str, Any]) -> dict[str, Any]:
    energies = point["energies_hartree"]
    occupations = np.asarray(point["ground_state_rdm"]["natural_occupations"], dtype=float)
    exact_total = float(energies["total"][0])
    hartree_fock_total = float(energies["hartree_fock_total"])
    density_data = point["ground_state_fock_density"]["matrix"]
    density = np.asarray(density_data["real"], dtype=float) + 1j * np.asarray(
        density_data["imag"], dtype=float
    )
    # Reuse the established QMW 16x16 density -> 256-sample wavetable contract.
    from qmw_circuit_builder_controller import density_wavetable_channels

    wavetable = density_wavetable_channels(density)
    return {
        "distance_angstrom": float(point["distance_angstrom"]),
        "ground_energy_hartree": exact_total,
        "hartree_fock_energy_hartree": hartree_fock_total,
        "correlation_energy_hartree": exact_total - hartree_fock_total,
        "excitation_gaps_hartree": [float(x) for x in energies["excitation_gaps"]],
        "natural_occupations": occupations.tolist(),
        "natural_occupation_entropy_bits": _natural_occupation_entropy(occupations),
        "one_rdm_purity": float(np.sum(occupations**2)),
        "dipole_magnitude_atomic_units": float(point["dipole_atomic_units"]["total_magnitude"]),
        "qmw_wavetable_buffer": wavetable["buffer"],
        "qmw_wavetable_magnitude": wavetable["magnitude"],
        "qmw_wavetable_phase": wavetable["phase"],
        "qmw_wavetable_metrics": wavetable["bank"]["metrics"],
        "validation": point["validation"],
    }


def build_dense_dataset(config: DissociationConfig = DissociationConfig()) -> dict[str, Any]:
    config.validate()
    distances = np.linspace(config.distance_start, config.distance_stop, config.num_points)
    features = [
        extract_features(analyze_h2_point(float(distance), config.basis, config.num_eigenstates))
        for distance in distances
    ]
    energies = np.asarray([point["ground_energy_hartree"] for point in features])
    minimum = int(np.argmin(energies))
    first_gaps = np.asarray([point["excitation_gaps_hartree"][0] for point in features])
    reference_gap = float(np.median(first_gaps))
    return {
        "schema": "qmw.qiskit_nature.h2_dissociation_features.v1",
        "config": asdict(config),
        "points": features,
        "summary": {
            "sampled_minimum_distance_angstrom": features[minimum]["distance_angstrom"],
            "sampled_minimum_energy_hartree": features[minimum]["ground_energy_hartree"],
            "reference_gap_hartree": reference_gap,
            "maximum_dipole_magnitude_atomic_units": float(
                max(point["dipole_magnitude_atomic_units"] for point in features)
            ),
        },
        "feature_contract": {
            "correlation_energy_hartree": "exact total energy - Hartree-Fock total energy",
            "natural_occupation_entropy_bits": "Shannon entropy of natural occupations / particle number",
            "one_rdm_purity": "sum of squared natural occupations",
            "dipole_policy": "validation only for homonuclear H2; not mapped to sound",
        },
    }


def _interpolate_series(dataset: dict[str, Any], key: str, frames: int) -> np.ndarray:
    points = dataset["points"]
    source_x = np.linspace(0.0, 1.0, len(points))
    target_x = np.linspace(0.0, 1.0, frames)
    return np.interp(target_x, source_x, [float(point[key]) for point in points])


def _interpolate_vector(dataset: dict[str, Any], key: str, frames: int, count: int) -> np.ndarray:
    points = dataset["points"]
    source_x = np.linspace(0.0, 1.0, len(points))
    target_x = np.linspace(0.0, 1.0, frames)
    values = np.asarray([point[key][:count] for point in points], dtype=float)
    return np.column_stack(
        [np.interp(target_x, source_x, values[:, index]) for index in range(count)]
    )


def _oscillator(frequency: np.ndarray, amplitude: np.ndarray, sample_rate: int) -> np.ndarray:
    phase = np.cumsum(2.0 * np.pi * frequency / sample_rate)
    return amplitude * np.sin(phase)


def _fade(audio: np.ndarray, sample_rate: int, seconds: float = 0.08) -> np.ndarray:
    frames = min(int(sample_rate * seconds), len(audio) // 2)
    if frames:
        ramp = np.linspace(0.0, 1.0, frames)
        audio[:frames] *= ramp[:, None]
        audio[-frames:] *= ramp[::-1, None]
    return audio


def render_audio(dataset: dict[str, Any], route: str) -> np.ndarray:
    config = dataset["config"]
    sample_rate = int(config["sample_rate"])
    frames = int(round(float(config["duration_seconds"]) * sample_rate))
    base = float(config["base_frequency_hz"])
    reference_gap = float(dataset["summary"]["reference_gap_hartree"])
    gaps = _interpolate_vector(dataset, "excitation_gaps_hartree", frames, 3)
    ratios = 1.0 + gaps / reference_gap
    stereo = np.zeros((frames, 2), dtype=float)

    if route == "raw":
        frequency_ratios = ratios
        amplitudes = np.asarray([0.20, 0.13, 0.09])
    elif route == "shaped":
        # Smooth dynamic-range compression only: no rounding, scale, or tuning grid.
        frequency_ratios = ratios**0.58
        entropy = _interpolate_series(dataset, "natural_occupation_entropy_bits", frames)
        entropy /= max(float(np.max(entropy)), 1e-12)
        amplitudes = np.asarray([0.22, 0.15, 0.10])
    else:
        raise ValueError("route must be 'raw' or 'shaped'")

    pans = (-0.65, 0.0, 0.65)
    for voice, pan in enumerate(pans):
        amplitude = np.full(frames, amplitudes[voice])
        if route == "shaped":
            amplitude *= 0.72 + entropy * (0.20 if voice else 0.08)
        signal = _oscillator(base * frequency_ratios[:, voice], amplitude, sample_rate)
        left = np.sqrt((1.0 - pan) / 2.0)
        right = np.sqrt((1.0 + pan) / 2.0)
        stereo[:, 0] += left * signal
        stereo[:, 1] += right * signal

    if route == "shaped":
        correlation = -_interpolate_series(dataset, "correlation_energy_hartree", frames)
        correlation /= max(float(np.max(correlation)), 1e-12)
        upper = _oscillator(base * frequency_ratios[:, 0] * (1.5 + 0.5 * correlation), 0.035 * correlation, sample_rate)
        stereo[:, 0] += upper * 0.6
        stereo[:, 1] += upper * 0.8

    peak = float(np.max(np.abs(stereo)))
    if peak > 0:
        stereo *= 0.92 / peak
    return _fade(stereo, sample_rate)


def relational_mapping_descriptor(dataset: dict[str, Any]) -> dict[str, Any]:
    """Describe the stable-voice mapping used by the accepted-design candidate."""
    config = dataset["config"]
    base = float(config["base_frequency_hz"])
    carriers = base * np.geomspace(1.0, 4.6, 4)
    return {
        "schema": "qmw.qiskit_nature.h2_relational_mapping.v2",
        "carrier_frequencies_hz": carriers.tolist(),
        "carrier_policy": "four fixed logarithmically spaced auditory display anchors",
        "pitch_policy": "molecular gaps never alter carrier pitch",
        "controls": {
            "natural_occupations": "amplitudes of four persistent natural-orbital voices",
            "excitation_gaps": "continuous amplitude-beating rates only",
            "correlation_energy": "cross-modulation depth between persistent voices",
            "natural_occupation_entropy": "activation of fixed sqrt(2) inharmonic color voices",
            "cumulative_state_change": "timing of non-grid molecular-change articulations",
            "dipole": "diagnostic only; not sonified for homonuclear H2",
        },
        "tuning_policy": "continuous and unrounded; no tuning grid or scale quantization",
    }


def _state_change_events(dataset: dict[str, Any], frames: int, count: int = 18) -> np.ndarray:
    """Place events uniformly in cumulative feature-space distance, not clock time."""
    points = dataset["points"]
    correlation = np.asarray([p["correlation_energy_hartree"] for p in points], dtype=float)
    entropy = np.asarray([p["natural_occupation_entropy_bits"] for p in points], dtype=float)
    gap = np.asarray([p["excitation_gaps_hartree"][0] for p in points], dtype=float)

    def normalized(values: np.ndarray) -> np.ndarray:
        span = float(np.ptp(values))
        return (values - values[0]) / span if span > 0 else np.zeros_like(values)

    coordinates = np.column_stack((normalized(correlation), normalized(entropy), normalized(np.log1p(gap))))
    increments = np.linalg.norm(np.diff(coordinates, axis=0), axis=1)
    cumulative = np.concatenate(([0.0], np.cumsum(increments)))
    if cumulative[-1] <= 0:
        return np.empty(0, dtype=int)
    targets = np.linspace(cumulative[-1] / (count + 1), cumulative[-1] * count / (count + 1), count)
    positions = np.interp(targets, cumulative, np.linspace(0, frames - 1, len(points)))
    return np.asarray(np.round(positions), dtype=int)


def render_relational_audio(dataset: dict[str, Any]) -> tuple[np.ndarray, dict[str, Any]]:
    """Render stable voices whose internal relations change with the molecule."""
    config = dataset["config"]
    sample_rate = int(config["sample_rate"])
    frames = int(round(float(config["duration_seconds"]) * sample_rate))
    mapping = relational_mapping_descriptor(dataset)
    carriers = np.asarray(mapping["carrier_frequencies_hz"], dtype=float)
    occupations = _interpolate_vector(dataset, "natural_occupations", frames, 4)
    entropy = _interpolate_series(dataset, "natural_occupation_entropy_bits", frames)
    correlation = -_interpolate_series(dataset, "correlation_energy_hartree", frames)
    gaps = _interpolate_vector(dataset, "excitation_gaps_hartree", frames, 3)
    reference_gap = float(dataset["summary"]["reference_gap_hartree"])

    entropy_norm = (entropy - entropy.min()) / max(float(np.ptp(entropy)), 1e-12)
    correlation_norm = correlation / max(float(correlation.max()), 1e-12)
    occupation_amplitude = np.sqrt(np.clip(occupations / 2.0, 0.0, 1.0))
    stereo = np.zeros((frames, 2), dtype=float)
    pans = np.asarray((-0.78, -0.24, 0.24, 0.78))
    phases = np.zeros(4, dtype=float)
    modulator = np.zeros(frames, dtype=float)

    for voice, carrier in enumerate(carriers):
        gap = gaps[:, min(voice, gaps.shape[1] - 1)]
        beat_rate = 0.12 + 5.5 * gap / (gap + reference_gap)
        beat_phase = np.cumsum(2.0 * np.pi * beat_rate / sample_rate)
        beating = 0.68 + 0.32 * np.sin(beat_phase + voice * 0.71)
        coupled_frequency = carrier * (
            1.0 + 0.006 * correlation_norm * np.sin(np.cumsum(2.0 * np.pi * 0.19 * (voice + 1) / sample_rate))
        )
        phase = phases[voice] + np.cumsum(2.0 * np.pi * coupled_frequency / sample_rate)
        signal = 0.20 * occupation_amplitude[:, voice] * beating * np.sin(phase)
        color = (
            0.055
            * entropy_norm
            * occupation_amplitude[:, voice]
            * np.sin(np.sqrt(2.0) * phase + 0.37 * voice)
        )
        signal += color
        modulator += signal
        left = np.sqrt((1.0 - pans[voice]) / 2.0)
        right = np.sqrt((1.0 + pans[voice]) / 2.0)
        stereo[:, 0] += left * signal
        stereo[:, 1] += right * signal

    # Articulations occur at equal increments of molecular feature-space distance.
    events = _state_change_events(dataset, frames)
    event_length = max(1, int(0.18 * sample_rate))
    local_time = np.arange(event_length) / sample_rate
    for event_index, center in enumerate(events):
        start = min(max(0, int(center)), frames - 1)
        stop = min(frames, start + event_length)
        length = stop - start
        voice = int(np.argmax(occupations[start]))
        envelope = np.exp(-local_time[:length] * 22.0)
        articulation = 0.07 * envelope * np.sin(2.0 * np.pi * carriers[voice] * local_time[:length])
        pan = pans[voice]
        stereo[start:stop, 0] += articulation * np.sqrt((1.0 - pan) / 2.0)
        stereo[start:stop, 1] += articulation * np.sqrt((1.0 + pan) / 2.0)

    peak = float(np.max(np.abs(stereo)))
    if peak > 0:
        stereo *= 0.92 / peak
    mapping["state_change_event_count"] = int(len(events))
    mapping["state_change_event_frames"] = events.tolist()
    return _fade(stereo, sample_rate), mapping


def export_relational_study(dataset: dict[str, Any], output_directory: Path) -> dict[str, Path]:
    output_directory.mkdir(parents=True, exist_ok=True)
    wav_path = output_directory / "h2_dissociation_relational_v2.wav"
    mapping_path = output_directory / "h2_dissociation_relational_mapping_v2.json"
    audio, mapping = render_relational_audio(dataset)
    write_wav(wav_path, audio, int(dataset["config"]["sample_rate"]))
    mapping_path.write_text(json.dumps(mapping, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {"relational_wav": wav_path, "mapping": mapping_path}


def uniform_downshift_mapping(
    dataset: dict[str, Any], sample_rate: int = 96_000, nyquist_fraction: float = 0.90
) -> dict[str, Any]:
    """Return the single-factor map from all computed excitation gaps to audio."""
    if sample_rate < 8_000:
        raise ValueError("sample_rate must be at least 8000")
    if not 0 < nyquist_fraction < 1:
        raise ValueError("nyquist_fraction must lie strictly between 0 and 1")
    gaps = np.asarray([point["excitation_gaps_hartree"] for point in dataset["points"]], dtype=float)
    positive = gaps[gaps > 0]
    if positive.size == 0:
        raise ValueError("dataset has no positive excitation gaps")
    hartree_hz = float(physical_constants["hartree-hertz relationship"][0])
    maximum_audio_hz = nyquist_fraction * sample_rate / 2.0
    maximum_physical_hz = float(positive.max() * hartree_hz)
    division_factor = maximum_physical_hz / maximum_audio_hz
    audio_hz = gaps * hartree_hz / division_factor
    return {
        "schema": "qmw.qiskit_nature.h2_uniform_spectrum.v3",
        "source": "all nonzero excitation gaps in the computed two-electron STO-3G sector",
        "num_excitation_branches": int(gaps.shape[1]),
        "hartree_hertz_relationship": hartree_hz,
        "sample_rate": int(sample_rate),
        "nyquist_hz": sample_rate / 2.0,
        "nyquist_fraction": float(nyquist_fraction),
        "global_division_factor": division_factor,
        "physical_frequency_range_hz": [float(positive.min() * hartree_hz), maximum_physical_hz],
        "audio_frequency_range_hz": [float(audio_hz[audio_hz > 0].min()), float(audio_hz.max())],
        "formula": "f_audio = (DeltaE_hartree * hartree_hertz_relationship) / global_division_factor",
        "ratio_policy": "one constant division preserves all simultaneous frequency ratios and degeneracies",
        "boundary_policy": "no folding, clipping, tuning quantization, or forced lower audible bound",
        "branch_policy": "branches are energy-sorted at each geometry; the instantaneous spectrum is authoritative",
    }


def render_uniform_downshift_audio(
    dataset: dict[str, Any], sample_rate: int = 96_000, nyquist_fraction: float = 0.90
) -> tuple[np.ndarray, dict[str, Any]]:
    mapping = uniform_downshift_mapping(dataset, sample_rate, nyquist_fraction)
    duration = float(dataset["config"]["duration_seconds"])
    frames = int(round(duration * sample_rate))
    branch_count = int(mapping["num_excitation_branches"])
    gaps = _interpolate_vector(dataset, "excitation_gaps_hartree", frames, branch_count)
    frequencies = (
        gaps * float(mapping["hartree_hertz_relationship"]) / float(mapping["global_division_factor"])
    )
    stereo = np.zeros((frames, 2), dtype=float)
    pans = np.linspace(-0.85, 0.85, branch_count)
    amplitude = 0.16 / np.sqrt(max(branch_count, 1))
    for branch in range(branch_count):
        signal = _oscillator(frequencies[:, branch], np.full(frames, amplitude), sample_rate)
        left = np.sqrt((1.0 - pans[branch]) / 2.0)
        right = np.sqrt((1.0 + pans[branch]) / 2.0)
        stereo[:, 0] += left * signal
        stereo[:, 1] += right * signal
    peak = float(np.max(np.abs(stereo)))
    if peak > 0:
        stereo *= 0.92 / peak
    return _fade(stereo, sample_rate), mapping


def export_uniform_downshift_study(
    dataset: dict[str, Any], output_directory: Path, sample_rate: int = 96_000
) -> dict[str, Path]:
    output_directory.mkdir(parents=True, exist_ok=True)
    wav_path = output_directory / "h2_complete_spectrum_uniform_downshift_v3.wav"
    mapping_path = output_directory / "h2_complete_spectrum_uniform_downshift_v3.json"
    audio, mapping = render_uniform_downshift_audio(dataset, sample_rate=sample_rate)
    write_wav(wav_path, audio, sample_rate)
    mapping_path.write_text(json.dumps(mapping, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {"spectrum_wav": wav_path, "mapping": mapping_path}


def _octave_register(frequency: float, lower_hz: float, upper_hz: float) -> tuple[float, int]:
    """Move a positive frequency by exact powers of two into a display register."""
    if frequency <= 0 or lower_hz <= 0 or upper_hz <= lower_hz:
        raise ValueError("invalid frequency or register")
    registered = float(frequency)
    shift = 0
    while registered < lower_hz:
        registered *= 2.0
        shift += 1
    while registered > upper_hz:
        registered /= 2.0
        shift -= 1
    return registered, shift


def chamber_mapping_descriptor(
    dataset: dict[str, Any], lower_hz: float = 82.5, upper_hz: float = 2640.0
) -> dict[str, Any]:
    """Create three H2-derived spectral chords for the composed chamber route."""
    points = dataset["points"]
    targets = {
        "compressed": 0.45,
        "equilibrium": float(dataset["summary"]["sampled_minimum_distance_angstrom"]),
        "dissociated": 2.5,
    }
    references = {
        name: min(points, key=lambda point: abs(point["distance_angstrom"] - target))
        for name, target in targets.items()
    }
    equilibrium_gap = float(references["equilibrium"]["excitation_gaps_hartree"][0])
    reference_audio_hz = 220.0
    chords: dict[str, Any] = {}
    for name, point in references.items():
        gaps = np.asarray(point["excitation_gaps_hartree"], dtype=float)
        uniformly_transposed = reference_audio_hz * gaps / equilibrium_gap
        registered = [_octave_register(float(value), lower_hz, upper_hz) for value in uniformly_transposed]
        chords[name] = {
            "distance_angstrom": float(point["distance_angstrom"]),
            "excitation_gaps_hartree": gaps.tolist(),
            "uniformly_transposed_hz": uniformly_transposed.tolist(),
            "registered_hz": [value for value, _ in registered],
            "octave_shifts": [shift for _, shift in registered],
            "natural_occupations": point["natural_occupations"],
            "natural_occupation_entropy_bits": point["natural_occupation_entropy_bits"],
        }
    return {
        "schema": "qmw.qiskit_nature.h2_spectral_chamber.v4",
        "reference": {
            "equilibrium_first_gap_hartree": equilibrium_gap,
            "equilibrium_first_gap_audio_hz": reference_audio_hz,
        },
        "register_hz": [lower_hz, upper_hz],
        "chords": chords,
        "frequency_policy": (
            "all intervals originate in H2 gaps; one reference transposition is followed only by "
            "exact power-of-two register shifts"
        ),
        "form_policy": (
            "three recurring spectral gestures articulate compressed, equilibrium, and dissociated "
            "reference states; primary onset timing follows cumulative molecular feature-space distance"
        ),
        "baseline_policy": "v3 remains the unfurled full-spectrum scientific reference",
    }


def _add_resonant_chord(
    stereo: np.ndarray,
    start: int,
    frequencies: np.ndarray,
    weights: np.ndarray,
    duration_seconds: float,
    decay_seconds: float,
    sample_rate: int,
    gesture_index: int,
) -> None:
    length = min(int(duration_seconds * sample_rate), len(stereo) - start)
    if length <= 0:
        return
    time = np.arange(length, dtype=float) / sample_rate
    envelope = (1.0 - np.exp(-time * 90.0)) * np.exp(-time / max(decay_seconds, 1e-6))
    branch_count = len(frequencies)
    pans = np.linspace(-0.82, 0.82, branch_count)
    gesture_masks = (
        np.asarray([1.0, 0.72, 0.48, 0.18, 0.12]),
        np.asarray([0.28, 0.32, 0.36, 0.88, 0.72]),
        np.asarray([0.72, 0.72, 0.72, 0.66, 0.62]),
    )
    mask = gesture_masks[gesture_index % len(gesture_masks)]
    for branch, frequency in enumerate(frequencies):
        amplitude = 0.11 * float(weights[branch]) * float(mask[branch])
        phase = 0.41 * branch + 0.19 * gesture_index
        signal = amplitude * envelope * np.sin(2.0 * np.pi * frequency * time + phase)
        # A very quiet fixed-ratio color partial makes each excitation resonant rather than a bare sine.
        signal += 0.018 * amplitude * envelope * np.sin(
            2.0 * np.pi * np.sqrt(2.0) * frequency * time + phase
        )
        left = np.sqrt((1.0 - pans[branch]) / 2.0)
        right = np.sqrt((1.0 + pans[branch]) / 2.0)
        stereo[start : start + length, 0] += left * signal
        stereo[start : start + length, 1] += right * signal


def render_spectral_chamber_audio(
    dataset: dict[str, Any], sample_rate: int = 48_000, duration_seconds: float = 48.0
) -> tuple[np.ndarray, dict[str, Any]]:
    """Compose recurring resonant gestures from three molecular reference spectra."""
    mapping = chamber_mapping_descriptor(dataset)
    frames = int(round(sample_rate * duration_seconds))
    stereo = np.zeros((frames, 2), dtype=float)
    state_events = _state_change_events(dataset, frames, count=21)
    chord_names = ("compressed", "equilibrium", "dissociated")
    reference_distances = np.asarray(
        [mapping["chords"][name]["distance_angstrom"] for name in chord_names], dtype=float
    )
    source_distances = np.asarray([point["distance_angstrom"] for point in dataset["points"]])
    event_records: list[dict[str, Any]] = []

    # Add a clear opening and final recollection around the state-derived events.
    event_frames = np.unique(np.concatenate(([int(0.6 * sample_rate)], state_events, [int(45.0 * sample_rate)])))
    for event_index, event_frame in enumerate(event_frames):
        progress = event_frame / max(frames - 1, 1)
        distance = float(np.interp(progress, np.linspace(0.0, 1.0, len(source_distances)), source_distances))
        chord_index = int(np.argmin(np.abs(reference_distances - distance)))
        chord_name = chord_names[chord_index]
        chord = mapping["chords"][chord_name]
        frequencies = np.asarray(chord["registered_hz"], dtype=float)
        occupations = np.asarray(chord["natural_occupations"], dtype=float)
        entropy = float(chord["natural_occupation_entropy_bits"])
        # Five excitation weights inherit the four natural occupations plus their mean correlation voice.
        weights = np.concatenate((np.sqrt(np.clip(occupations / 2.0, 0.0, 1.0)), [np.sqrt(np.mean(occupations) / 2.0)]))
        weights /= max(float(weights.max()), 1e-12)
        decay = 0.8 + 2.6 * (entropy - 1.0)

        gap_shape = np.asarray(chord["excitation_gaps_hartree"], dtype=float)
        gap_shape /= max(float(gap_shape.max()), 1e-12)
        offsets_seconds = (0.0, 0.16 + 0.34 * gap_shape[0], 0.48 + 0.52 * gap_shape[3])
        for gesture_index, offset in enumerate(offsets_seconds):
            start = event_frame + int(offset * sample_rate)
            _add_resonant_chord(
                stereo,
                start,
                frequencies,
                weights,
                duration_seconds=4.2,
                decay_seconds=decay,
                sample_rate=sample_rate,
                gesture_index=gesture_index,
            )
        event_records.append(
            {
                "frame": int(event_frame),
                "time_seconds": float(event_frame / sample_rate),
                "trajectory_distance_angstrom": distance,
                "reference_chord": chord_name,
                "gesture_offsets_seconds": list(offsets_seconds),
            }
        )

    peak = float(np.max(np.abs(stereo)))
    if peak > 0:
        stereo *= 0.92 / peak
    mapping["sample_rate"] = int(sample_rate)
    mapping["duration_seconds"] = float(duration_seconds)
    mapping["events"] = event_records
    mapping["state_derived_event_count"] = int(len(state_events))
    mapping["formal_boundary_event_count"] = 2
    return _fade(stereo, sample_rate), mapping


def export_spectral_chamber_study(
    dataset: dict[str, Any], output_directory: Path, sample_rate: int = 48_000
) -> dict[str, Path]:
    output_directory.mkdir(parents=True, exist_ok=True)
    wav_path = output_directory / "h2_spectral_chamber_v4.wav"
    mapping_path = output_directory / "h2_spectral_chamber_mapping_v4.json"
    audio, mapping = render_spectral_chamber_audio(dataset, sample_rate=sample_rate)
    write_wav(wav_path, audio, sample_rate)
    mapping_path.write_text(json.dumps(mapping, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {"chamber_wav": wav_path, "mapping": mapping_path}


def qmw_wavetable_wilson_mapping(dataset: dict[str, Any], sample_rate: int = 48_000) -> dict[str, Any]:
    """Describe H2 density wavetables played through existing Wilson CPS material."""
    from qmw_iching_laplacian_modal_renderer_v1 import RenderConfig, wilson_hexagram_tuning

    config = RenderConfig(sample_rate=sample_rate, base_frequency_hz=55.0)
    tuning = wilson_hexagram_tuning(config)
    grade_one_nodes = (1, 2, 4, 8, 16, 32)
    tones = [tuning[node] for node in grade_one_nodes]
    return {
        "schema": "qmw.qiskit_nature.h2_density_wavetable_wilson_material.v5",
        "wavetable_source": {
            "physical_source": "exact H2 ground-state 16x16 Fock-space density matrix",
            "existing_transform": "qmw_circuit_builder_controller.density_wavetable_channels",
            "table_size": 256,
            "table_count": len(dataset["points"]),
            "morph_axis": "bond distance in angstrom",
        },
        "wilson_material": {
            "status": "compositional tuning material; not an oracle consultation or molecular claim",
            "source": "existing qmw_iching_laplacian_modal_renderer_v1.wilson_hexagram_tuning",
            "generators": list(config.wilson_generators),
            "shell": "canonical grade-one shell",
            "tones": [
                {
                    "node": tone.hexagram,
                    "factor": list(tone.factors),
                    "ratio": [tone.ratio_numerator, tone.ratio_denominator],
                    "frequency_hz": tone.frequency_hz,
                    "pan": tone.pan,
                }
                for tone in tones
            ],
        },
        "instrument_contract": {
            "pitch": "existing exact Wilson CPS material",
            "timbre": "existing QMW density-wavetable transform of the H2 state",
            "morphing": "continuous interpolation along the molecular bond trajectory",
            "timing": "recurring six-voice gestures placed by cumulative molecular state change",
            "ontology": "molecular physics and I Ching/Wilson material remain explicitly distinct",
        },
    }


def _morphed_wavetable_signal(
    tables: np.ndarray, frequency_hz: float, frames: int, sample_rate: int, phase_offset: float
) -> np.ndarray:
    trajectory = np.linspace(0.0, len(tables) - 1, frames)
    table_low = np.floor(trajectory).astype(int)
    table_high = np.minimum(table_low + 1, len(tables) - 1)
    table_mix = trajectory - table_low
    phase = (phase_offset + np.arange(frames, dtype=float) * frequency_hz / sample_rate) % 1.0
    sample_position = phase * tables.shape[1]
    sample_low = np.floor(sample_position).astype(int) % tables.shape[1]
    sample_high = (sample_low + 1) % tables.shape[1]
    sample_mix = sample_position - np.floor(sample_position)
    low_table_value = (
        tables[table_low, sample_low] * (1.0 - sample_mix)
        + tables[table_low, sample_high] * sample_mix
    )
    high_table_value = (
        tables[table_high, sample_low] * (1.0 - sample_mix)
        + tables[table_high, sample_high] * sample_mix
    )
    return low_table_value * (1.0 - table_mix) + high_table_value * table_mix


def render_qmw_wavetable_wilson_audio(
    dataset: dict[str, Any], sample_rate: int = 48_000, duration_seconds: float = 48.0
) -> tuple[np.ndarray, dict[str, Any]]:
    mapping = qmw_wavetable_wilson_mapping(dataset, sample_rate)
    tables = np.asarray([point["qmw_wavetable_buffer"] for point in dataset["points"]], dtype=float)
    if tables.ndim != 2 or tables.shape[1] != 256:
        raise ValueError("QMW molecular wavetable bank must have shape (points, 256)")
    frames = int(round(sample_rate * duration_seconds))
    tones = mapping["wilson_material"]["tones"]
    voice_count = len(tones)
    gates = np.full((frames, voice_count), 0.025, dtype=float)
    events = _state_change_events(dataset, frames, count=24)
    gesture_offsets = (0.0, 0.19, 0.47)
    event_length = int(1.8 * sample_rate)
    local_time = np.arange(event_length, dtype=float) / sample_rate
    envelope = (1.0 - np.exp(-local_time * 55.0)) * np.exp(-local_time / 0.72)
    event_records: list[dict[str, Any]] = []
    for event_index, event in enumerate(events):
        active = tuple((event_index + offset) % voice_count for offset in (0, 2, 5))
        for gesture_index, offset_seconds in enumerate(gesture_offsets):
            start = int(event + offset_seconds * sample_rate)
            stop = min(frames, start + event_length)
            if stop <= start:
                continue
            voice = active[gesture_index]
            gates[start:stop, voice] += 0.82 * envelope[: stop - start]
        event_records.append(
            {
                "frame": int(event),
                "time_seconds": float(event / sample_rate),
                "active_grade_one_nodes": [int(tones[index]["node"]) for index in active],
            }
        )

    stereo = np.zeros((frames, 2), dtype=float)
    for voice, tone in enumerate(tones):
        signal = _morphed_wavetable_signal(
            tables,
            float(tone["frequency_hz"]),
            frames,
            sample_rate,
            phase_offset=voice / voice_count,
        )
        signal *= gates[:, voice]
        pan = float(tone["pan"])
        stereo[:, 0] += signal * np.sqrt((1.0 - pan) / 2.0)
        stereo[:, 1] += signal * np.sqrt((1.0 + pan) / 2.0)
    peak = float(np.max(np.abs(stereo)))
    if peak > 0:
        stereo *= 0.92 / peak
    mapping["sample_rate"] = int(sample_rate)
    mapping["duration_seconds"] = float(duration_seconds)
    mapping["state_change_event_count"] = int(len(events))
    mapping["events"] = event_records
    mapping["osc_compatibility"] = {
        "table_address": "/qmw/circuit/wavetable/buffer",
        "size_address": "/qmw/circuit/wavetable/size",
        "existing_max_table_size": 256,
    }
    return _fade(stereo, sample_rate), mapping


def export_qmw_wavetable_wilson_study(
    dataset: dict[str, Any], output_directory: Path, sample_rate: int = 48_000
) -> dict[str, Path]:
    output_directory.mkdir(parents=True, exist_ok=True)
    wav_path = output_directory / "h2_qmw_density_wavetable_wilson_v5.wav"
    mapping_path = output_directory / "h2_qmw_density_wavetable_wilson_v5.json"
    bank_path = output_directory / "h2_qmw_density_wavetable_bank_v5.npz"
    audio, mapping = render_qmw_wavetable_wilson_audio(dataset, sample_rate=sample_rate)
    write_wav(wav_path, audio, sample_rate)
    mapping_path.write_text(json.dumps(mapping, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    np.savez_compressed(
        bank_path,
        distance_angstrom=np.asarray([point["distance_angstrom"] for point in dataset["points"]]),
        wavetable=np.asarray([point["qmw_wavetable_buffer"] for point in dataset["points"]]),
    )
    return {"preview_wav": wav_path, "mapping": mapping_path, "wavetable_bank": bank_path}


def write_wav(path: Path, audio: np.ndarray, sample_rate: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    pcm = np.asarray(np.clip(audio, -1.0, 1.0) * 32767.0, dtype="<i2")
    with wave.open(str(path), "wb") as handle:
        handle.setnchannels(2)
        handle.setsampwidth(2)
        handle.setframerate(sample_rate)
        handle.writeframes(pcm.tobytes())


def export_study(dataset: dict[str, Any], output_directory: Path) -> dict[str, Path]:
    output_directory.mkdir(parents=True, exist_ok=True)
    descriptor_path = output_directory / "h2_dissociation_features.json"
    arrays_path = output_directory / "h2_dissociation_data.npz"
    raw_wav = output_directory / "h2_dissociation_raw.wav"
    shaped_wav = output_directory / "h2_dissociation_shaped.wav"
    descriptor_path.write_text(json.dumps(dataset, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    points = dataset["points"]
    np.savez_compressed(
        arrays_path,
        distance_angstrom=np.asarray([p["distance_angstrom"] for p in points]),
        ground_energy_hartree=np.asarray([p["ground_energy_hartree"] for p in points]),
        hartree_fock_energy_hartree=np.asarray([p["hartree_fock_energy_hartree"] for p in points]),
        correlation_energy_hartree=np.asarray([p["correlation_energy_hartree"] for p in points]),
        excitation_gaps_hartree=np.asarray([p["excitation_gaps_hartree"] for p in points]),
        natural_occupations=np.asarray([p["natural_occupations"] for p in points]),
        natural_occupation_entropy_bits=np.asarray([p["natural_occupation_entropy_bits"] for p in points]),
        one_rdm_purity=np.asarray([p["one_rdm_purity"] for p in points]),
    )
    sample_rate = int(dataset["config"]["sample_rate"])
    write_wav(raw_wav, render_audio(dataset, "raw"), sample_rate)
    write_wav(shaped_wav, render_audio(dataset, "shaped"), sample_rate)
    return {"descriptor": descriptor_path, "data": arrays_path, "raw_wav": raw_wav, "shaped_wav": shaped_wav}
