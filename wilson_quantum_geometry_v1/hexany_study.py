"""Offline sounding study of a Wilson Hexany as a four-qubit weight-two shell."""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import json
from pathlib import Path
import wave

import numpy as np

from .cps import CombinationProductSet
from .perception import harmonic_intersection, interval_tuneability


@dataclass(frozen=True)
class HexanyStudyConfig:
    duration_seconds: float = 36.0
    sample_rate: int = 48_000
    control_rate: int = 120
    fundamental_hz: float = 220.0
    seed: int = 23


@dataclass(frozen=True)
class HexanyStudyResult:
    states: np.ndarray
    measurement_frame: int
    measurement_tone: int
    section_frames: tuple[int, int]


def build_hamiltonian(cps: CombinationProductSet) -> np.ndarray:
    """Build an excitation-preserving walk weighted by perceptual proximity."""
    hamiltonian = np.zeros((cps.dimension, cps.dimension), dtype=np.float64)
    for edge in cps.perceptual_edges():
        interval = edge.interval_numerator / edge.interval_denominator
        intersection = harmonic_intersection(interval)
        strength = intersection / (1.0 + edge.harmonic_distance)
        hamiltonian[edge.source, edge.target] = strength
        hamiltonian[edge.target, edge.source] = strength
    eigenvalues = np.linalg.eigvalsh(hamiltonian)
    radius = float(np.max(np.abs(eigenvalues)))
    if radius > 0:
        hamiltonian /= radius
    return hamiltonian


def compose_states(config: HexanyStudyConfig) -> HexanyStudyResult:
    """Compose three operations: spread, complement, and measurement/coda."""
    cps = CombinationProductSet((1, 3, 5, 7), 2)
    hamiltonian = build_hamiltonian(cps)
    eigenvalues, eigenvectors = np.linalg.eigh(hamiltonian)
    total_frames = int(round(config.duration_seconds * config.control_rate)) + 1
    first_boundary = total_frames // 3
    second_boundary = 2 * total_frames // 3
    dt = 1.0 / config.control_rate
    rng = np.random.default_rng(config.seed)

    state = np.zeros(cps.dimension, dtype=np.complex128)
    state[0] = 1.0
    states = np.empty((total_frames, cps.dimension), dtype=np.complex128)
    measurement_tone = 0

    for frame in range(total_frames):
        if frame == first_boundary:
            complemented = np.zeros_like(state)
            for tone in cps.tones:
                complemented[tone.complement_index] = state[tone.index]
            state = complemented
        elif frame == second_boundary:
            probabilities = np.abs(state) ** 2
            measurement_tone = int(rng.choice(cps.dimension, p=probabilities))
            state = np.zeros_like(state)
            state[measurement_tone] = 1.0

        states[frame] = state
        if frame == total_frames - 1:
            continue
        if frame < first_boundary:
            rate = 1.15
        elif frame < second_boundary:
            rate = 0.78
        else:
            progress = (frame - second_boundary) / max(1, total_frames - second_boundary)
            rate = 0.48 * (1.0 - progress) + 0.08
        spectral = eigenvectors.conj().T @ state
        spectral *= np.exp(-1j * eigenvalues * rate * dt)
        state = eigenvectors @ spectral
        state /= np.linalg.norm(state)

    return HexanyStudyResult(
        states=states,
        measurement_frame=second_boundary,
        measurement_tone=measurement_tone,
        section_frames=(first_boundary, second_boundary),
    )


def render_audio(config: HexanyStudyConfig, result: HexanyStudyResult) -> np.ndarray:
    """Render state probability as energy and relative phase as spatial/timbral color."""
    cps = CombinationProductSet((1, 3, 5, 7), 2)
    sample_count = int(round(config.duration_seconds * config.sample_rate))
    sample_times = np.arange(sample_count, dtype=np.float64) / config.sample_rate
    control_times = np.arange(len(result.states), dtype=np.float64) / config.control_rate
    audio = np.zeros((sample_count, 2), dtype=np.float64)
    fixed_pan = np.array([-0.82, -0.46, -0.12, 0.12, 0.46, 0.82])

    for tone in cps.tones:
        control = result.states[:, tone.index]
        real = np.interp(sample_times, control_times, control.real)
        imag = np.interp(sample_times, control_times, control.imag)
        probability = real * real + imag * imag
        amplitude = np.sqrt(np.maximum(probability, 0.0))
        quantum_phase = np.arctan2(imag, real)
        frequency = config.fundamental_hz * tone.ratio
        oscillator_phase = 2.0 * np.pi * frequency * sample_times
        brightness = 0.16 + 0.24 * (0.5 + 0.5 * np.cos(quantum_phase))
        voice = amplitude * (
            np.sin(oscillator_phase)
            + brightness * np.sin(2.0 * oscillator_phase + quantum_phase)
            + 0.12 * np.sin(3.0 * oscillator_phase - quantum_phase)
        ) / 1.52
        pan = np.clip(fixed_pan[tone.index] + 0.12 * np.sin(quantum_phase), -0.95, 0.95)
        audio[:, 0] += voice * np.sqrt(0.5 * (1.0 - pan))
        audio[:, 1] += voice * np.sqrt(0.5 * (1.0 + pan))

    fade_samples = min(sample_count // 2, int(config.sample_rate * 1.5))
    envelope = np.ones(sample_count, dtype=np.float64)
    envelope[:fade_samples] = np.sin(np.linspace(0, np.pi / 2, fade_samples)) ** 2
    envelope[-fade_samples:] = np.cos(np.linspace(0, np.pi / 2, fade_samples)) ** 2
    audio *= envelope[:, None]
    peak = float(np.max(np.abs(audio)))
    if peak > 0:
        audio *= 0.88 / peak
    return audio


def write_wave(path: Path, audio: np.ndarray, sample_rate: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    pcm = np.round(np.clip(audio, -1.0, 1.0) * 32767.0).astype("<i2")
    with wave.open(str(path), "wb") as output:
        output.setnchannels(2)
        output.setsampwidth(2)
        output.setframerate(sample_rate)
        output.writeframes(pcm.tobytes())


def metadata(config: HexanyStudyConfig, result: HexanyStudyResult) -> dict[str, object]:
    cps = CombinationProductSet((1, 3, 5, 7), 2)
    tones = []
    for tone in cps.tones:
        report = interval_tuneability(tone.ratio, config.fundamental_hz)
        tones.append(
            {
                "index": tone.index,
                "factors": list(tone.factors),
                "bitmask": format(tone.bitmask, "04b"),
                "ratio": f"{tone.ratio_numerator}/{tone.ratio_denominator}",
                "frequency_hz": config.fundamental_hz * tone.ratio,
                "complement_index": tone.complement_index,
                "pitch_class_coordinates": [list(item) for item in tone.pitch_class_coordinates],
                "anchor_interval_tuneability": asdict(report),
            }
        )
    first, second = result.section_frames
    return {
        "title": "Hexany Quantum Walk Study v1",
        "cps": cps.name,
        "config": asdict(config),
        "sections": [
            {"name": "coherent_spread", "start_seconds": 0.0},
            {"name": "particle_hole_complement", "start_seconds": first / config.control_rate},
            {"name": "measurement_and_coda", "start_seconds": second / config.control_rate},
        ],
        "measurement_tone": result.measurement_tone,
        "measurement_factors": list(cps.tones[result.measurement_tone].factors),
        "tones": tones,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("output/wilson_quantum_geometry_v1/hexany_quantum_walk_study_v1.wav"),
    )
    parser.add_argument("--duration", type=float, default=36.0)
    parser.add_argument("--fundamental", type=float, default=220.0)
    parser.add_argument("--sample-rate", type=int, default=48_000)
    args = parser.parse_args()
    config = HexanyStudyConfig(
        duration_seconds=args.duration,
        fundamental_hz=args.fundamental,
        sample_rate=args.sample_rate,
    )
    result = compose_states(config)
    audio = render_audio(config, result)
    write_wave(args.output, audio, config.sample_rate)
    metadata_path = args.output.with_suffix(".json")
    metadata_path.write_text(json.dumps(metadata(config, result), indent=2, default=str) + "\n")
    print(args.output)
    print(metadata_path)
    print(f"measured tone {result.measurement_tone}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
