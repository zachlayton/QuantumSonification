from __future__ import annotations

from collections import Counter
from collections.abc import Callable
from dataclasses import dataclass, field
import math
from typing import Any, Iterable, Sequence

import numpy as np


@dataclass(frozen=True)
class BitArray:
    """Small immutable bit container for measurement-event processing."""

    bits: tuple[int, ...]

    @classmethod
    def from_bits(cls, bits: Iterable[int | bool]) -> "BitArray":
        return cls(tuple(1 if int(bit) else 0 for bit in bits))

    @classmethod
    def from_int(cls, value: int, width: int) -> "BitArray":
        if value < 0:
            raise ValueError("BitArray value must be non-negative.")
        return cls(tuple((value >> shift) & 1 for shift in range(width - 1, -1, -1)))

    @classmethod
    def from_string(cls, text: str) -> "BitArray":
        stripped = text.strip().replace(" ", "")
        if any(char not in {"0", "1"} for char in stripped):
            raise ValueError(f"Invalid bit string: {text!r}")
        return cls(tuple(int(char) for char in stripped))

    def __len__(self) -> int:
        return len(self.bits)

    def __iter__(self):
        return iter(self.bits)

    def __getitem__(self, index: int) -> int:
        return self.bits[index]

    def to_int(self) -> int:
        value = 0
        for bit in self.bits:
            value = (value << 1) | bit
        return value

    def to_string(self) -> str:
        return "".join(str(bit) for bit in self.bits)

    def population_count(self) -> int:
        return sum(self.bits)

    def parity(self) -> int:
        return self.population_count() % 2

    def hamming_distance(self, other: "BitArray") -> int:
        self._check_width(other)
        return sum(a != b for a, b in zip(self.bits, other.bits))

    def bit_flips(self, other: "BitArray") -> tuple[int, ...]:
        self._check_width(other)
        return tuple(index for index, (a, b) in enumerate(zip(self.bits, other.bits)) if a != b)

    def gray_code(self) -> "BitArray":
        value = self.to_int()
        return BitArray.from_int(value ^ (value >> 1), len(self))

    def bitwise_not(self) -> "BitArray":
        return BitArray(tuple(0 if bit else 1 for bit in self.bits))

    def bitwise_and(self, other: "BitArray") -> "BitArray":
        self._check_width(other)
        return BitArray(tuple(a & b for a, b in zip(self.bits, other.bits)))

    def bitwise_or(self, other: "BitArray") -> "BitArray":
        self._check_width(other)
        return BitArray(tuple(a | b for a, b in zip(self.bits, other.bits)))

    def bitwise_xor(self, other: "BitArray") -> "BitArray":
        self._check_width(other)
        return BitArray(tuple(a ^ b for a, b in zip(self.bits, other.bits)))

    def binary_mask(self, mask: "BitArray") -> "BitArray":
        return self.bitwise_and(mask)

    def cellular_automata_step(self, rule: int = 30, wrap: bool = True) -> "BitArray":
        if not (0 <= rule <= 255):
            raise ValueError("Elementary cellular automaton rule must be 0..255.")

        next_bits: list[int] = []
        width = len(self.bits)
        for index, bit in enumerate(self.bits):
            if wrap:
                left = self.bits[(index - 1) % width]
                right = self.bits[(index + 1) % width]
            else:
                left = self.bits[index - 1] if index > 0 else 0
                right = self.bits[index + 1] if index < width - 1 else 0

            neighborhood = (left << 2) | (bit << 1) | right
            next_bits.append((rule >> neighborhood) & 1)

        return BitArray(tuple(next_bits))

    def _check_width(self, other: "BitArray") -> None:
        if len(self) != len(other):
            raise ValueError(f"BitArray widths differ: {len(self)} != {len(other)}")

    @staticmethod
    def concatenate_bits(registers: Sequence["ShotBitArray"]) -> "ShotBitArray":
        return ShotBitArray.concatenate_bits(registers)


@dataclass(frozen=True)
class ShotBitArray:
    """Shot-wise bit container for Qiskit-like measurement data processing."""

    shots: tuple[BitArray, ...]
    name: str = "meas"

    @classmethod
    def from_bitstrings(
        cls,
        bitstrings: Iterable[str],
        *,
        name: str = "meas",
    ) -> "ShotBitArray":
        return cls(
            tuple(BitArray.from_string(bitstring) for bitstring in bitstrings),
            name=name,
        )

    @classmethod
    def from_bits(
        cls,
        shots: Iterable[Iterable[int | bool]],
        *,
        name: str = "meas",
    ) -> "ShotBitArray":
        return cls(
            tuple(BitArray.from_bits(bits) for bits in shots),
            name=name,
        )

    def __len__(self) -> int:
        return len(self.shots)

    def __iter__(self):
        return iter(self.shots)

    def __getitem__(self, index: Any) -> "ShotBitArray | BitArray":
        if isinstance(index, (int, np.integer)):
            return self.shots[int(index)]

        indices = self._normalize_indices(index)
        return ShotBitArray(tuple(self.shots[i] for i in indices), name=self.name)

    @property
    def width(self) -> int:
        return len(self.shots[0]) if self.shots else 0

    @property
    def shape(self) -> tuple[int, int]:
        return (len(self.shots), self.width)

    @property
    def array(self) -> np.ndarray:
        """Return a Qiskit-like shot array of binary byte strings."""
        return np.array(
            [[f"0b{shot.to_string()}"] for shot in self.shots],
            dtype=object,
        )

    @property
    def bitstrings(self) -> list[str]:
        return [shot.to_string() for shot in self.shots]

    def slice_bits(self, bit_indices: Sequence[int]) -> "ShotBitArray":
        indices = [int(index) for index in bit_indices]
        for index in indices:
            if index < 0 or index >= self.width:
                raise IndexError(f"Bit index {index} out of range for width {self.width}.")

        return ShotBitArray(
            tuple(BitArray.from_bits(shot[index] for index in indices) for shot in self.shots),
            name=self.name,
        )

    def slice_shots(self, shot_indices: Sequence[int]) -> "ShotBitArray":
        indices = [int(index) for index in shot_indices]
        for index in indices:
            if index < 0 or index >= len(self.shots):
                raise IndexError(f"Shot index {index} out of range for {len(self.shots)} shots.")

        return ShotBitArray(tuple(self.shots[index] for index in indices), name=self.name)

    def expectation_values(self, observables: Sequence[Any]) -> list[float]:
        return [
            self.expectation_value(observable)
            for observable in observables
        ]

    def expectation_value(self, observable: Any) -> float:
        label = diagonal_observable_label(observable)
        if len(label) != self.width:
            raise ValueError(
                f"Observable width {len(label)} does not match register width {self.width}."
            )

        if any(char not in {"I", "Z"} for char in label):
            raise ValueError(
                "ShotBitArray expectations support diagonal I/Z observables only."
            )

        if not self.shots:
            return 0.0

        total = 0.0
        for shot in self.shots:
            eigenvalue = 1.0
            for bit, pauli in zip(shot, label):
                if pauli == "Z" and bit:
                    eigenvalue *= -1.0
            total += eigenvalue

        return total / len(self.shots)

    def counts(self) -> dict[str, int]:
        return dict(Counter(self.bitstrings))

    @staticmethod
    def concatenate_bits(registers: Sequence["ShotBitArray"]) -> "ShotBitArray":
        if not registers:
            return ShotBitArray(())

        shot_count = len(registers[0])
        if any(len(register) != shot_count for register in registers):
            raise ValueError("All registers must have the same number of shots.")

        name = "_".join(register.name for register in registers)
        merged = []
        for shot_index in range(shot_count):
            bits: list[int] = []
            for register in registers:
                bits.extend(register.shots[shot_index].bits)
            merged.append(BitArray.from_bits(bits))

        return ShotBitArray(tuple(merged), name=name)

    def _normalize_indices(self, index: Any) -> list[int]:
        if isinstance(index, slice):
            return list(range(len(self.shots)))[index]

        if isinstance(index, np.ndarray):
            if index.dtype == bool:
                if index.shape[0] != len(self.shots):
                    raise IndexError("Boolean shot mask length does not match shot count.")
                return [i for i, keep in enumerate(index.tolist()) if keep]
            return [int(i) for i in index.tolist()]

        if isinstance(index, Sequence) and not isinstance(index, (str, bytes)):
            if all(isinstance(item, (bool, np.bool_)) for item in index):
                if len(index) != len(self.shots):
                    raise IndexError("Boolean shot mask length does not match shot count.")
                return [i for i, keep in enumerate(index) if keep]
            return [int(i) for i in index]

        raise TypeError(f"Unsupported ShotBitArray index: {index!r}")


def diagonal_observable_label(observable: Any) -> str:
    """Extract an I/Z Pauli label from a string or Qiskit-like object."""
    if isinstance(observable, str):
        text = observable
    elif hasattr(observable, "paulis") and len(observable.paulis) == 1:
        text = str(observable.paulis[0])
    elif hasattr(observable, "to_list"):
        items = observable.to_list()
        if len(items) != 1:
            raise ValueError("Only single-term diagonal observables are supported.")
        text = str(items[0][0])
    else:
        text = str(observable)

    text = text.strip()
    if "SparsePauliOp" in text:
        for token in ("'", '"'):
            parts = text.split(token)
            for part in parts:
                if part and all(char in {"I", "X", "Y", "Z"} for char in part):
                    return part

    text = text.replace(" ", "")
    if text.startswith("0b"):
        raise ValueError("Observable must be a Pauli label, not a bit string.")

    return text


@dataclass
class MeasurementEvent:
    """One discrete measurement event emitted beside the continuous state bus."""

    t: float
    step: int
    bit_array: BitArray
    register_name: str = "c"
    osc_route: str | None = None
    persistence: str = "single_shot"
    shot_index: int | None = None
    circuit_name: str | None = None
    basis_label: str | None = None
    active_qubit: int | None = None
    probabilities: dict[str, float] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def bitstring(self) -> str:
        return self.bit_array.to_string()

    @property
    def value(self) -> int:
        return self.bit_array.to_int()

    @property
    def population_count(self) -> int:
        return self.bit_array.population_count()

    @property
    def gray_code(self) -> BitArray:
        return self.bit_array.gray_code()

    @property
    def parity(self) -> int:
        return self.bit_array.parity()

    def osc_payload(self) -> list[Any]:
        return [
            self.register_name,
            "" if self.osc_route is None else self.osc_route,
            self.persistence,
            self.bitstring,
            self.value,
            self.population_count,
            self.gray_code.to_string(),
            self.parity,
            -1 if self.active_qubit is None else self.active_qubit,
            "" if self.basis_label is None else self.basis_label,
            self.step,
        ]


@dataclass
class ClassicalRegister:
    """Named classical measurement register, analogous to Qiskit result data."""

    name: str
    bit_array: BitArray
    role: str = "measurement"
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def bitstring(self) -> str:
        return self.bit_array.to_string()

    @property
    def value(self) -> int:
        return self.bit_array.to_int()

    @property
    def population_count(self) -> int:
        return self.bit_array.population_count()

    @property
    def parity(self) -> int:
        return self.bit_array.parity()

    @property
    def gray_code(self) -> BitArray:
        return self.bit_array.gray_code()

    def xor(self, other: "ClassicalRegister") -> BitArray:
        return self.bit_array.bitwise_xor(other.bit_array)

    def hamming_distance(self, other: "ClassicalRegister") -> int:
        return self.bit_array.hamming_distance(other.bit_array)


@dataclass
class MeasurementStats:
    shots: int
    counts: dict[str, int]
    register_counts: dict[str, dict[str, int]] = field(default_factory=dict)

    @classmethod
    def from_events(cls, events: Iterable[MeasurementEvent]) -> "MeasurementStats":
        event_list = list(events)
        counter = Counter(event.bitstring for event in event_list)
        register_counts: dict[str, dict[str, int]] = {}
        for event in event_list:
            register_counts.setdefault(event.register_name, {})
            register_counts[event.register_name][event.bitstring] = (
                register_counts[event.register_name].get(event.bitstring, 0) + 1
            )
        return cls(
            shots=sum(counter.values()),
            counts=dict(counter),
            register_counts=register_counts,
        )

    def probability(self, bitstring: str) -> float:
        if self.shots <= 0:
            return 0.0
        return self.counts.get(bitstring, 0) / self.shots

    def register_probability(self, register_name: str, bitstring: str) -> float:
        register = self.register_counts.get(register_name, {})
        shots = sum(register.values())
        if shots <= 0:
            return 0.0
        return register.get(bitstring, 0) / shots

    def shannon_entropy(self, register_name: str | None = None) -> float:
        counts = (
            self.register_counts.get(register_name, {})
            if register_name is not None
            else self.counts
        )
        shots = sum(counts.values())
        if shots <= 0:
            return 0.0

        entropy = 0.0
        for count in counts.values():
            probability = count / shots
            if probability > 0.0:
                entropy -= probability * math.log2(probability)
        return entropy


@dataclass
class MeasurementHistoryAnalysis:
    register_name: str
    shots: int
    entropy: float
    population_counts: list[int]
    parity_sequence: list[int]
    hamming_steps: list[int]
    bit_flip_counts: dict[int, int]
    bit_means: list[float]
    bit_correlations: dict[tuple[int, int], float]
    run_lengths: list[int]
    transition_counts: dict[str, int]
    temporal_mean_hamming: float
    temporal_activity: float


MeasurementSubscriber = Callable[[MeasurementEvent], None]


class MeasurementEventBus:
    """Synchronous publisher for discrete measurement events."""

    def __init__(self) -> None:
        self._subscribers: list[MeasurementSubscriber] = []
        self.events: list[MeasurementEvent] = []
        self.latest: MeasurementEvent | None = None

    def subscribe(self, callback: MeasurementSubscriber) -> MeasurementSubscriber:
        self._subscribers.append(callback)
        return callback

    def unsubscribe(self, callback: MeasurementSubscriber) -> None:
        self._subscribers = [
            subscriber
            for subscriber in self._subscribers
            if subscriber is not callback
        ]

    def publish(self, event: MeasurementEvent) -> None:
        self.latest = event
        self.events.append(event)
        for subscriber in tuple(self._subscribers):
            subscriber(event)

    def stats(self) -> MeasurementStats:
        return MeasurementStats.from_events(self.events)

    def events_for_register(self, register_name: str) -> list[MeasurementEvent]:
        return [
            event
            for event in self.events
            if event.register_name == register_name
        ]

    def analyze_register(self, register_name: str) -> MeasurementHistoryAnalysis:
        return analyze_measurement_history(
            self.events_for_register(register_name),
            register_name=register_name,
        )

    def clear(self) -> None:
        self.events.clear()
        self.latest = None


def analyze_measurement_history(
    events: Iterable[MeasurementEvent],
    *,
    register_name: str = "c",
) -> MeasurementHistoryAnalysis:
    event_list = list(events)
    stats = MeasurementStats.from_events(event_list)

    if not event_list:
        return MeasurementHistoryAnalysis(
            register_name=register_name,
            shots=0,
            entropy=0.0,
            population_counts=[],
            parity_sequence=[],
            hamming_steps=[],
            bit_flip_counts={},
            bit_means=[],
            bit_correlations={},
            run_lengths=[],
            transition_counts={},
            temporal_mean_hamming=0.0,
            temporal_activity=0.0,
        )

    bit_arrays = [event.bit_array for event in event_list]
    width = len(bit_arrays[0])
    if any(len(bits) != width for bits in bit_arrays):
        raise ValueError("All events in one register must have the same bit width.")

    population_counts = [bits.population_count() for bits in bit_arrays]
    parity_sequence = [bits.parity() for bits in bit_arrays]
    hamming_steps = [
        previous.hamming_distance(current)
        for previous, current in zip(bit_arrays, bit_arrays[1:])
    ]
    bit_flip_counts: dict[int, int] = {index: 0 for index in range(width)}
    for previous, current in zip(bit_arrays, bit_arrays[1:]):
        for index in previous.bit_flips(current):
            bit_flip_counts[index] += 1

    bit_means = [
        sum(bits[index] for bits in bit_arrays) / len(bit_arrays)
        for index in range(width)
    ]
    bit_correlations = {
        (a, b): bit_correlation(bit_arrays, a, b)
        for a in range(width)
        for b in range(a + 1, width)
    }
    run_lengths = bitstring_run_lengths([bits.to_string() for bits in bit_arrays])
    transition_counts = Counter(
        f"{previous.to_string()}->{current.to_string()}"
        for previous, current in zip(bit_arrays, bit_arrays[1:])
    )
    temporal_mean_hamming = (
        sum(hamming_steps) / len(hamming_steps)
        if hamming_steps
        else 0.0
    )
    temporal_activity = (
        temporal_mean_hamming / width
        if width > 0
        else 0.0
    )

    return MeasurementHistoryAnalysis(
        register_name=register_name,
        shots=len(event_list),
        entropy=stats.shannon_entropy(register_name),
        population_counts=population_counts,
        parity_sequence=parity_sequence,
        hamming_steps=hamming_steps,
        bit_flip_counts=bit_flip_counts,
        bit_means=bit_means,
        bit_correlations=bit_correlations,
        run_lengths=run_lengths,
        transition_counts=dict(transition_counts),
        temporal_mean_hamming=temporal_mean_hamming,
        temporal_activity=temporal_activity,
    )


def bit_correlation(
    bit_arrays: list[BitArray],
    bit_a: int,
    bit_b: int,
) -> float:
    values_a = [1.0 if bits[bit_a] else -1.0 for bits in bit_arrays]
    values_b = [1.0 if bits[bit_b] else -1.0 for bits in bit_arrays]
    mean_a = sum(values_a) / len(values_a)
    mean_b = sum(values_b) / len(values_b)
    return sum(
        (a - mean_a) * (b - mean_b)
        for a, b in zip(values_a, values_b)
    ) / len(values_a)


def bitstring_run_lengths(bitstrings: list[str]) -> list[int]:
    if not bitstrings:
        return []

    runs: list[int] = []
    current = bitstrings[0]
    length = 1
    for bitstring in bitstrings[1:]:
        if bitstring == current:
            length += 1
        else:
            runs.append(length)
            current = bitstring
            length = 1
    runs.append(length)
    return runs
