"""Randomized-basis, non-grid sonification of clock Schmidt modes.

Each nonzero Schmidt mode is treated as an independently measured temporal
voice.  Every event chooses a local Pauli measurement basis on the six clock
qubits, samples an outcome from that mode, and accumulates a new interval from
the sampled amplitude's probability and phase change.  The classical choice
of measurement basis and the sonification map are explicit transducers; the
outcome distribution is derived from the simulated quantum clock mode.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Mapping
import json

import numpy as np

from .diagnostics import analyze_history
from .granular_sonification import _grain_window, _normalize, _place_grain
from .history_state import DiscreteHistoryState


PAULI_BASES = ("X", "Y", "Z")


@dataclass(frozen=True)
class RandomizedClockConfig:
    sample_rate: int = 48_000
    duration_seconds: float = 12.0
    base_interval_ms: float = 82.0
    minimum_interval_ms: float = 22.0
    maximum_interval_ms: float = 240.0
    phase_interval_octaves: float = 0.78
    surprise_interval_octaves: float = 0.38
    mode_rate_exponent: float = 0.22
    grain_seconds: float = 0.014
    base_frequency: float = 760.0
    max_modes: int = 16
    eigenvalue_tolerance: float = 1e-10
    seed: int = 64021


@dataclass(frozen=True)
class RandomizedClockRender:
    coherent_measurement_rhythm: np.ndarray
    phase_erased_control: np.ndarray
    mode_stems: np.ndarray
    report: Mapping[str, object]


def _single_qubit_basis_state(basis: str, outcome: int) -> np.ndarray:
    bit = int(outcome)
    if basis == "Z":
        return np.asarray([1.0, 0.0] if bit == 0 else [0.0, 1.0], complex)
    if basis == "X":
        return np.asarray([1.0, 1.0 if bit == 0 else -1.0], complex) / np.sqrt(2.0)
    if basis == "Y":
        return np.asarray([1.0, 1j if bit == 0 else -1j], complex) / np.sqrt(2.0)
    raise ValueError(f"unsupported basis {basis!r}")


def _measurement_matrix(bases: tuple[str, ...]) -> np.ndarray:
    """Return columns containing all product-basis measurement kets."""

    dimension = 1 << len(bases)
    matrix = np.empty((dimension, dimension), dtype=np.complex128)
    for outcome in range(dimension):
        state = np.asarray([1.0 + 0.0j])
        for qubit in range(len(bases) - 1, -1, -1):
            state = np.kron(
                state,
                _single_qubit_basis_state(
                    bases[qubit],
                    (outcome >> qubit) & 1,
                ),
            )
        matrix[:, outcome] = state
    return matrix


def _click_grain(
    voice: int,
    *,
    samples: int,
    sample_rate: int,
    base_frequency: float,
) -> np.ndarray:
    time = np.arange(int(samples), dtype=float) / float(sample_rate)
    frequency = float(base_frequency) * 2.0 ** ((voice % 8) / 12.0)
    decay = np.exp(-(190.0 + 8.0 * voice) * time)
    attack = np.minimum(1.0, 3200.0 * time)
    carrier = np.sin(2.0 * np.pi * frequency * time)
    edge = 0.34 * np.sin(2.0 * np.pi * 2.17 * frequency * time + 0.3)
    return attack * decay * (carrier + edge) * _grain_window(time.size)


def _alternating_pan(voice: int, count: int) -> float:
    side = -1.0 if voice % 2 == 0 else 1.0
    pair = voice // 2
    pairs = max(1, (count + 1) // 2)
    radius = 0.22 + 0.70 * (pair + 1) / pairs
    return float(side * radius)


def render_randomized_clock(
    history: DiscreteHistoryState,
    config: RandomizedClockConfig | None = None,
) -> RandomizedClockRender:
    """Render independent stochastic measurement streams for Schmidt modes."""

    settings = config or RandomizedClockConfig()
    if history.clock_qubits != 6:
        raise ValueError("randomized clock reference requires six clock qubits")
    if settings.sample_rate <= 0 or settings.duration_seconds <= 0.0:
        raise ValueError("sample rate and duration must be positive")
    if not (
        0.0 < settings.minimum_interval_ms
        <= settings.base_interval_ms
        <= settings.maximum_interval_ms
    ):
        raise ValueError("clock interval bounds are inconsistent")
    if settings.grain_seconds <= 0.0:
        raise ValueError("grain duration must be positive")

    diagnostics = analyze_history(history)
    eigenvalues = diagnostics.clock_schmidt_eigenvalues
    active = np.flatnonzero(eigenvalues > settings.eigenvalue_tolerance)
    active = active[: min(settings.max_modes, history.system_dimension)]
    if active.size == 0:
        raise RuntimeError("history has no active Schmidt modes")
    weights = eigenvalues[active]
    modes = diagnostics.clock_schmidt_modes[active]
    maximum_weight = float(weights[0])

    total_samples = int(round(settings.sample_rate * settings.duration_seconds))
    coherent = np.zeros((total_samples, 2), dtype=float)
    control = np.zeros_like(coherent)
    stems = np.zeros((active.size, total_samples, 2), dtype=float)
    grain_samples = int(round(settings.sample_rate * settings.grain_seconds))
    grains = [
        _click_grain(
            voice,
            samples=grain_samples,
            sample_rate=settings.sample_rate,
            base_frequency=settings.base_frequency,
        )
        for voice in range(active.size)
    ]

    basis_cache: dict[tuple[str, ...], np.ndarray] = {}
    interval_statistics: list[dict[str, float]] = []
    event_counts: list[int] = []
    basis_counts = {basis: 0 for basis in PAULI_BASES}
    outcome_histogram = np.zeros(history.clock_states, dtype=int)

    for voice, (weight, mode, grain) in enumerate(zip(weights, modes, grains)):
        rng = np.random.default_rng(settings.seed + 7919 * voice)
        nominal_interval_ms = settings.base_interval_ms * (
            maximum_weight / float(weight)
        ) ** settings.mode_rate_exponent
        onset = float(rng.uniform(0.0, nominal_interval_ms)) / 1000.0
        control_onset = onset
        previous_phase = 0.0
        coherent_intervals: list[float] = []
        events = 0
        pan = _alternating_pan(voice, active.size)

        while onset < settings.duration_seconds:
            bases = tuple(
                PAULI_BASES[int(value)]
                for value in rng.integers(0, len(PAULI_BASES), 6)
            )
            for basis in bases:
                basis_counts[basis] += 1
            measurement = basis_cache.get(bases)
            if measurement is None:
                measurement = _measurement_matrix(bases)
                basis_cache[bases] = measurement
            amplitudes = measurement.conj().T @ mode
            probabilities = np.abs(amplitudes) ** 2
            probabilities /= probabilities.sum()
            outcome = int(rng.choice(history.clock_states, p=probabilities))
            outcome_histogram[outcome] += 1
            amplitude = amplitudes[outcome]
            probability = max(float(probabilities[outcome]), 1e-15)
            phase = float(np.angle(amplitude))
            phase_change = float(np.angle(np.exp(1j * (phase - previous_phase))))
            previous_phase = phase
            surprise_per_qubit = -np.log2(probability) / history.clock_qubits
            phase_octaves = (
                settings.phase_interval_octaves * phase_change / np.pi
            )
            surprise_octaves = settings.surprise_interval_octaves * (
                surprise_per_qubit - 1.0
            )
            coherent_interval_ms = float(np.clip(
                nominal_interval_ms * 2.0 ** (phase_octaves + surprise_octaves),
                settings.minimum_interval_ms,
                settings.maximum_interval_ms,
            ))
            control_interval_ms = float(np.clip(
                nominal_interval_ms * 2.0 ** surprise_octaves,
                settings.minimum_interval_ms,
                settings.maximum_interval_ms,
            ))
            relative_probability = min(1.0, np.sqrt(
                probability * history.clock_states
            ))
            level = (
                0.14
                * np.sqrt(float(weight) / maximum_weight)
                * (0.55 + 0.45 * relative_probability)
            )
            timbral_grain = grain * (
                0.82 + 0.18 * ((outcome.bit_count() + 1) / 7.0)
            )
            _place_grain(
                coherent,
                timbral_grain,
                onset,
                sample_rate=settings.sample_rate,
                amplitude=level,
                pan=pan,
            )
            _place_grain(
                stems[voice],
                timbral_grain,
                onset,
                sample_rate=settings.sample_rate,
                amplitude=level,
                pan=pan,
            )

            # The control shares the exact measurement records.  Only the
            # phase term is removed from its independently accumulated clock.
            _place_grain(
                control,
                timbral_grain,
                control_onset,
                sample_rate=settings.sample_rate,
                amplitude=level,
                pan=pan,
            )
            coherent_intervals.append(coherent_interval_ms)
            onset += coherent_interval_ms / 1000.0
            control_onset += control_interval_ms / 1000.0
            events += 1

        values = np.asarray(coherent_intervals, dtype=float)
        event_counts.append(events)
        interval_statistics.append({
            "mean_ms": float(np.mean(values)),
            "standard_deviation_ms": float(np.std(values)),
            "coefficient_of_variation": float(np.std(values) / np.mean(values)),
            "minimum_ms": float(np.min(values)),
            "maximum_ms": float(np.max(values)),
        })

    coherent = _normalize(coherent, 0.92)
    control = _normalize(control, 0.92)
    for voice in range(active.size):
        stems[voice] = _normalize(stems[voice], 0.78)

    report: dict[str, object] = {
        "protocol_kind": "qmw.randomized_basis_entangled_clock.v1",
        "scientific_status": (
            "local Pauli basis choices and the audio mapping are classical; "
            "outcomes, probabilities, and phases come from exact clock "
            "Schmidt modes; streams are a stochastic unraveling, not a claim "
            "that the density matrix contains hidden classical trajectories"
        ),
        "config": asdict(settings),
        "clock_states": history.clock_states,
        "system_dimension": history.system_dimension,
        "effective_schmidt_rank": diagnostics.effective_schmidt_rank,
        "rendered_mode_count": int(active.size),
        "schmidt_participation_number": (
            diagnostics.schmidt_participation_number
        ),
        "linear_entropy_E2": diagnostics.system_time_linear_entropy,
        "schmidt_von_neumann_entropy_bits": (
            diagnostics.schmidt_von_neumann_entropy_bits
        ),
        "active_eigenvalues": [float(value) for value in weights],
        "event_counts": event_counts,
        "interval_statistics": interval_statistics,
        "measurement_basis_uses": basis_counts,
        "measurement_outcome_histogram": outcome_histogram.tolist(),
        "mapping": {
            "voice": "one independent stream per clock Schmidt mode",
            "measurement": "new random local X/Y/Z clock basis per event",
            "outcome": "Born sample from the selected Schmidt mode",
            "interval": "recursively accumulated from phase change and outcome surprisal",
            "level": "Schmidt weight and sampled probability",
            "pan": "even/odd voice ranks displaced to opposite stereo sides",
            "control": "identical measurement records with phase removed from interval accumulation",
        },
    }
    return RandomizedClockRender(
        coherent_measurement_rhythm=coherent,
        phase_erased_control=control,
        mode_stems=stems,
        report=report,
    )


def write_randomized_clock(
    render: RandomizedClockRender,
    output_directory: str | Path,
    *,
    sample_rate: int,
) -> dict[str, Path]:
    import soundfile as sf

    directory = Path(output_directory)
    directory.mkdir(parents=True, exist_ok=True)
    paths: dict[str, Path] = {}
    for name, signal in {
        "randomized_clock_coherent": render.coherent_measurement_rhythm,
        "randomized_clock_phase_erased": render.phase_erased_control,
    }.items():
        path = directory / f"{name}.wav"
        sf.write(path, signal.astype(np.float32), int(sample_rate), subtype="FLOAT")
        paths[name] = path
    for voice, stem in enumerate(render.mode_stems):
        path = directory / f"randomized_clock_mode_{voice + 1:02d}.wav"
        sf.write(path, stem.astype(np.float32), int(sample_rate), subtype="FLOAT")
        paths[f"mode_{voice + 1:02d}"] = path
    report_path = directory / "randomized_clock_report.json"
    report_path.write_text(json.dumps(render.report, indent=2) + "\n")
    paths["report"] = report_path
    return paths
