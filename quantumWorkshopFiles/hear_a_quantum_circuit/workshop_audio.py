"""Thin Qiskit-to-sound adapter for the Hear a Quantum Circuit workshop.

The live option reuses the OSC vocabulary from
examples/interactive_circuit_builder.py. The local fallback borrows the
repository's population-to-modal-synthesis idea, but renders a tiny WAV with
only Qiskit, NumPy, and Python's standard library.
"""

from __future__ import annotations

import argparse
import math
import shutil
import socket
import struct
import subprocess
import wave
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Pauli, Statevector, entropy, partial_trace


SAMPLE_RATE = 44_100
DEFAULT_OSC_HOST = "127.0.0.1"
OUTPUT_DIR = Path(__file__).resolve().parent / "outputs"
BLOCH_ANCHOR_HZ = (220.0, 440.0)


@dataclass(frozen=True)
class ListeningResult:
    """Facts a module may print or test after rendering."""

    state: Statevector
    probabilities: np.ndarray
    wav_path: Path
    played: bool


def statevector_for(circuit: QuantumCircuit) -> Statevector:
    """Simulate a circuit that contains gates but no measurements."""

    if circuit.num_clbits:
        circuit = circuit.remove_final_measurements(inplace=False)
    return Statevector.from_instruction(circuit)


def probabilities_for(state: Statevector) -> np.ndarray:
    probabilities = np.abs(np.asarray(state.data, dtype=np.complex128)) ** 2
    return probabilities / probabilities.sum()


def _pauli_label(n_qubits: int, terms: dict[int, str]) -> str:
    # Qiskit labels read q[n-1] ... q[0].
    label = ["I"] * n_qubits
    for qubit, axis in terms.items():
        label[n_qubits - 1 - qubit] = axis
    return "".join(label)


def bloch_vectors(state: Statevector) -> list[tuple[float, float, float]]:
    vectors: list[tuple[float, float, float]] = []
    for qubit in range(state.num_qubits):
        vector = tuple(
            float(
                np.real(
                    state.expectation_value(
                        Pauli(_pauli_label(state.num_qubits, {qubit: axis}))
                    )
                )
            )
            for axis in "XYZ"
        )
        vectors.append(vector)
    return vectors


def local_entropies(state: Statevector) -> list[float]:
    values: list[float] = []
    for qubit in range(state.num_qubits):
        traced_out = [q for q in range(state.num_qubits) if q != qubit]
        reduced = partial_trace(state, traced_out)
        values.append(float(entropy(reduced, base=2)))
    return values


def pair_correlations(
    state: Statevector, qubit_a: int, qubit_b: int
) -> tuple[float, float, float, float, float]:
    values = []
    for axes in ("XX", "XY", "YX", "YY", "ZZ"):
        operator = Pauli(
            _pauli_label(
                state.num_qubits,
                {qubit_a: axes[0], qubit_b: axes[1]},
            )
        )
        values.append(float(np.real(state.expectation_value(operator))))
    return tuple(values)


def _fade_envelope(length: int, sample_rate: int) -> np.ndarray:
    envelope = np.ones(length, dtype=np.float64)
    fade = min(int(0.02 * sample_rate), max(1, length // 3))
    envelope[:fade] = np.linspace(0.0, 1.0, fade)
    envelope[-fade:] = np.linspace(1.0, 0.0, fade)
    return envelope


def _mode(
    frequency: float,
    amplitude: float,
    duration: float,
    phase: float,
    sample_rate: int,
) -> np.ndarray:
    count = max(1, int(duration * sample_rate))
    time = np.arange(count, dtype=np.float64) / sample_rate
    decay = np.exp(-2.2 * time / max(duration, 0.01))
    tone = np.sin(2.0 * math.pi * frequency * time + phase)
    tone += 0.22 * np.sin(4.0 * math.pi * frequency * time + 0.5 * phase)
    return amplitude * tone * decay * _fade_envelope(count, sample_rate)


def _frequency_for(index: int) -> float:
    # A compact minor-pentatonic ladder keeps up to 16 basis states distinct.
    semitones = (0, 3, 5, 7, 10)
    octave, degree = divmod(index, len(semitones))
    midi = 55 + 12 * octave + semitones[degree]
    return 440.0 * (2.0 ** ((midi - 69) / 12.0))


def render_probabilities(
    probabilities: Sequence[float],
    output_path: Path,
    *,
    phases: Sequence[float] | None = None,
    arpeggiate: bool = True,
    sample_rate: int = SAMPLE_RATE,
) -> Path:
    """Render active basis states, optionally auditioning them before the chord."""

    probs = np.asarray(probabilities, dtype=np.float64)
    probs = np.clip(probs, 0.0, None)
    if probs.sum() <= 0:
        raise ValueError("At least one probability must be positive.")
    probs /= probs.sum()

    phase_values = np.zeros(len(probs)) if phases is None else np.asarray(phases)
    active = [index for index, value in enumerate(probs) if value > 1e-7]

    note_seconds = 0.30
    gap_seconds = 0.045
    chord_seconds = 0.85
    gap = np.zeros(int(gap_seconds * sample_rate))
    pieces: list[np.ndarray] = []

    if arpeggiate:
        for index in active:
            amplitude = 0.16 + 0.68 * math.sqrt(float(probs[index]))
            pieces.append(
                _mode(
                    _frequency_for(index),
                    amplitude,
                    note_seconds,
                    float(phase_values[index]),
                    sample_rate,
                )
            )
            pieces.append(gap)

    chord = np.zeros(int(chord_seconds * sample_rate), dtype=np.float64)
    for index in active:
        amplitude = 0.10 + 0.44 * math.sqrt(float(probs[index]))
        chord += _mode(
            _frequency_for(index),
            amplitude,
            chord_seconds,
            float(phase_values[index]),
            sample_rate,
        )
    pieces.append(chord)

    audio = np.concatenate(pieces)
    peak = float(np.max(np.abs(audio)))
    if peak > 1e-12:
        audio *= 0.82 / peak

    pcm = (np.clip(audio, -1.0, 1.0) * 32767.0).astype("<i2")
    output_path = Path(output_path).expanduser().resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(output_path), "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(pcm.tobytes())
    return output_path


def one_qubit_relative_phase(state: Statevector) -> float | None:
    """Return phase(beta)-phase(alpha), or None when a basis voice is absent."""

    amplitudes = np.asarray(state.data, dtype=np.complex128)
    if len(amplitudes) != 2:
        raise ValueError("The Bloch-sphere renderer expects one qubit.")
    if abs(amplitudes[0]) < 1e-8 or abs(amplitudes[1]) < 1e-8:
        return None
    phase = float(np.angle(amplitudes[1]) - np.angle(amplitudes[0]))
    return (phase + math.pi) % (2.0 * math.pi) - math.pi


def module2_phase_frequency(
    state: Statevector,
) -> tuple[float | None, float | None, float]:
    """Map exact relative phase continuously around the 220–440 Hz octave."""

    amplitudes = np.asarray(state.data, dtype=np.complex128)
    phase = one_qubit_relative_phase(state)
    if phase is None:
        return None, None, 0.0
    turn = (phase % (2.0 * math.pi)) / (2.0 * math.pi)
    frequency = BLOCH_ANCHOR_HZ[0] * (2.0 ** turn)
    coherence = float(2.0 * abs(amplitudes[0] * amplitudes[1]))
    return frequency, phase, coherence


def module2_polar_frequency(state: Statevector) -> tuple[float, float]:
    """Map the actual Bloch polar angle continuously to 220–440 Hz."""

    z = float(np.clip(bloch_vectors(state)[0][2], -1.0, 1.0))
    polar_angle = math.acos(z)
    frequency = BLOCH_ANCHOR_HZ[0] * (2.0 ** (polar_angle / math.pi))
    return frequency, polar_angle


def _cue_tone(
    frequency: float,
    duration: float,
    sample_rate: int,
    *,
    bright: bool,
) -> np.ndarray:
    """Make a steady-level angle cue; brightness distinguishes phi from theta."""

    count = max(1, int(duration * sample_rate))
    time = np.arange(count, dtype=np.float64) / sample_rate
    tone = np.sin(2.0 * math.pi * frequency * time)
    if bright:
        tone += 0.28 * np.sin(6.0 * math.pi * frequency * time)
        tone += 0.12 * np.sin(10.0 * math.pi * frequency * time)
        tone /= 1.40
    return 0.62 * tone * _fade_envelope(count, sample_rate)


def _event_separator(count: int, sample_rate: int) -> np.ndarray:
    """Return count short deterministic noise clicks as a non-musical label."""

    click_count = max(1, int(0.012 * sample_rate))
    click_gap = np.zeros(int(0.065 * sample_rate), dtype=np.float64)
    tail = np.zeros(int(0.12 * sample_rate), dtype=np.float64)
    rng = np.random.default_rng(20_260_725)
    click = rng.uniform(-1.0, 1.0, click_count)
    click *= np.exp(-7.0 * np.linspace(0.0, 1.0, click_count))
    click *= 0.28
    pieces: list[np.ndarray] = []
    for index in range(count):
        pieces.append(click)
        if index + 1 < count:
            pieces.append(click_gap)
    pieces.append(tail)
    return np.concatenate(pieces)


def render_bloch_state(
    state: Statevector,
    output_path: Path,
    *,
    sample_rate: int = SAMPLE_RATE,
) -> tuple[Path, float, float, float | None, float | None, float]:
    """Render Module 2 with continuous polar and azimuth pitch cues.

    |0> is 220 Hz and |1> is 440 Hz. Their amplitudes are the Z-basis
    probabilities. A steady polar cue maps the actual Bloch theta to that exact
    octave, so theta is not represented only by amplitude. A brighter steady
    cue maps physical relative phase/azimuth to the octave. It is absent only at
    a pole, where azimuth is undefined. Global phase is never encoded.
    """

    probabilities = probabilities_for(state)
    if len(probabilities) != 2:
        raise ValueError("The Bloch-sphere renderer expects one qubit.")
    polar_frequency, polar_angle = module2_polar_frequency(state)
    phase_frequency, relative_phase, coherence = module2_phase_frequency(state)
    gap = np.zeros(int(0.055 * sample_rate), dtype=np.float64)
    pieces: list[np.ndarray] = []

    # One click: probability-weighted basis anchors, heard low then high.
    pieces.append(_event_separator(1, sample_rate))
    for frequency, probability in zip(BLOCH_ANCHOR_HZ, probabilities):
        if probability > 1e-7:
            pieces.append(
                _mode(
                    frequency,
                    0.78 * float(probability),
                    0.42,
                    0.0,
                    sample_rate,
                )
            )
            pieces.append(gap)

    # A stable-level pitch makes the actual polar angle directly audible:
    # 220 * 2^(theta / π), for canonical theta in [0, π].
    pieces.append(_event_separator(2, sample_rate))
    pieces.append(_cue_tone(polar_frequency, 0.72, sample_rate, bright=False))
    pieces.append(gap)

    # Azimuth/relative phase is another exact continuous turn around the same
    # octave. A brighter timbre distinguishes it from the preceding polar cue.
    pieces.append(_event_separator(3, sample_rate))
    if phase_frequency is not None:
        pieces.append(_cue_tone(phase_frequency, 0.72, sample_rate, bright=True))
    else:
        # Preserve the event order at a pole: three clicks, then an empty phi
        # slot, because azimuth is undefined there.
        pieces.append(np.zeros(int(0.72 * sample_rate), dtype=np.float64))
    pieces.append(gap)

    # Four clicks: the final probability chord. It intentionally excludes phi,
    # so changing only azimuth cannot change these anchor notes or their levels.
    pieces.append(_event_separator(4, sample_rate))
    chord_seconds = 1.20
    chord = np.zeros(int(chord_seconds * sample_rate), dtype=np.float64)
    for frequency, probability in zip(BLOCH_ANCHOR_HZ, probabilities):
        balance = float(probability)
        if balance <= 1e-7:
            continue
        chord += _mode(
            frequency,
            0.62 * balance,
            chord_seconds,
            0.0,
            sample_rate,
        )
    chord_peak = float(np.max(np.abs(chord)))
    if chord_peak > 1e-12:
        chord *= 0.72 / chord_peak
    pieces.append(chord)

    audio = np.concatenate(pieces)
    peak = float(np.max(np.abs(audio)))
    if peak > 0.95:
        audio *= 0.95 / peak
    pcm = (np.clip(audio, -1.0, 1.0) * 32767.0).astype("<i2")
    output_path = Path(output_path).expanduser().resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(output_path), "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(pcm.tobytes())
    return (
        output_path,
        polar_frequency,
        polar_angle,
        phase_frequency,
        relative_phase,
        coherence,
    )


def play_wav(path: Path) -> bool:
    """Play with an OS command when one is available."""

    candidates = (
        ("afplay", [str(path)]),
        ("aplay", [str(path)]),
        ("paplay", [str(path)]),
    )
    for command, arguments in candidates:
        executable = shutil.which(command)
        if executable is None:
            continue
        try:
            subprocess.run(
                [executable, *arguments],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            return True
        except (OSError, subprocess.CalledProcessError):
            continue
    return False


def _osc_string(value: str) -> bytes:
    encoded = value.encode("utf-8") + b"\0"
    return encoded + b"\0" * ((4 - len(encoded) % 4) % 4)


def _osc_message(address: str, values: Iterable[int | float | str]) -> bytes:
    values = list(values)
    tags = ","
    payload = b""
    for value in values:
        if isinstance(value, (int, np.integer)):
            tags += "i"
            payload += struct.pack(">i", int(value))
        elif isinstance(value, (float, np.floating)):
            tags += "f"
            payload += struct.pack(">f", float(value))
        else:
            tags += "s"
            payload += _osc_string(str(value))
    return _osc_string(address) + _osc_string(tags) + payload


def publish_qmw(
    state: Statevector,
    *,
    host: str = DEFAULT_OSC_HOST,
    port: int,
) -> None:
    """Send the OSC state vocabulary already understood by the QMW synth."""

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def send(address: str, values: Iterable[int | float | str]) -> None:
        sock.sendto(_osc_message(address, values), (host, int(port)))

    send("/qmw/circuit/probabilities", probabilities_for(state))
    for qubit, (vector, value) in enumerate(
        zip(bloch_vectors(state), local_entropies(state))
    ):
        send(f"/qmw/circuit/q{qubit}/bloch", vector)
        send(f"/qmw/circuit/q{qubit}/entropy", [value])
    for qubit_a in range(state.num_qubits):
        for qubit_b in range(qubit_a + 1, state.num_qubits):
            send(
                f"/qmw/circuit/correlation/{qubit_a}_{qubit_b}",
                pair_correlations(state, qubit_a, qubit_b),
            )
    sock.close()


def print_probabilities(probabilities: Sequence[float]) -> None:
    width = max(1, int(math.ceil(math.log2(len(probabilities)))))
    for index, probability in enumerate(probabilities):
        if probability > 1e-7:
            print(f"  |{index:0{width}b}>  {probability:6.1%}")


def add_listening_arguments(
    parser: argparse.ArgumentParser, default_filename: str
) -> argparse.ArgumentParser:
    parser.add_argument(
        "--output",
        type=Path,
        default=OUTPUT_DIR / default_filename,
        help="WAV path (default: outputs/<module>.wav)",
    )
    parser.add_argument(
        "--no-play",
        action="store_true",
        help="Write the WAV without trying to play it.",
    )
    parser.add_argument(
        "--osc-port",
        type=int,
        help="Also send the existing QMW /qmw/circuit OSC messages.",
    )
    return parser


def listen(
    circuit: QuantumCircuit,
    *,
    label: str,
    output_path: Path,
    play: bool = True,
    osc_port: int | None = None,
    arpeggiate: bool = True,
) -> ListeningResult:
    state = statevector_for(circuit)
    probabilities = probabilities_for(state)
    phases = np.angle(np.asarray(state.data, dtype=np.complex128))
    wav_path = render_probabilities(
        probabilities,
        output_path,
        phases=phases,
        arpeggiate=arpeggiate,
    )

    print(f"\n{label}")
    print(circuit.draw(output="text"))
    print("Probabilities:")
    print_probabilities(probabilities)
    if arpeggiate:
        print("\nListen: each possible basis state is a pitch; louder means more likely.")
    elif np.count_nonzero(probabilities > 1e-7) == 1:
        print("\nListen: the one certain joint outcome sounds as a single tone.")
    else:
        print(
            "\nListen: the possible joint outcomes sound together in one chord; "
            "louder means more likely."
        )

    played = play and play_wav(wav_path)
    if played:
        print(f"Played: {wav_path}")
    else:
        print(f"WAV ready: {wav_path}")
        if play:
            print("Automatic playback was unavailable; open the WAV in any player.")

    if osc_port is not None:
        publish_qmw(state, port=osc_port)
        print(f"Sent the existing QMW circuit messages to UDP port {osc_port}.")

    return ListeningResult(state, probabilities, wav_path, played)
