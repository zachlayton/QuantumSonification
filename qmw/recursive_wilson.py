"""Bounded recursive four-qubit Wilson Hexany circuit engine."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
import math
from typing import Any

import numpy as np


HEXANY_MASKS = (0b0011, 0b0101, 0b0110, 0b1001, 0b1010, 0b1100)
WILSON_GENERATORS = (1, 3, 5, 7)


@dataclass(frozen=True)
class HexanyVoice:
    basis_index: int
    factors: tuple[int, int]
    complement_basis_index: int
    ratio_numerator: int
    ratio_denominator: int
    conditional_probability: float
    absolute_probability: float
    relative_phase: float

    @property
    def ratio(self) -> float:
        return self.ratio_numerator / self.ratio_denominator


@dataclass(frozen=True)
class HexanyFlow:
    source_basis_index: int
    destination_basis_index: int
    absolute_probability_flow: float
    conditional_probability_flow: float
    relative_phase: float


@dataclass(frozen=True)
class BasisFlow:
    source_basis_index: int
    destination_basis_index: int
    probability_flow: float
    relative_phase: float


@dataclass(frozen=True)
class RecursiveWilsonStep:
    generation: int
    qubits: tuple[int, ...]
    theta: float
    beta: float
    shell_probability: float
    voices: tuple[HexanyVoice, ...]
    flows: tuple[HexanyFlow, ...]
    basis_flows: tuple[BasisFlow, ...]
    motion: str = "XY"
    selected_basis: int = -1
    selected_grade: int = -1
    grade_probabilities: tuple[float, ...] = ()


def _octave_reduce(ratio: Fraction) -> Fraction:
    while ratio < 1:
        ratio *= 2
    while ratio >= 2:
        ratio /= 2
    return ratio


def hexany_voices(state: Any) -> tuple[float, tuple[HexanyVoice, ...]]:
    """Return shell leakage plus conditioned 2)4 1-3-5-7 CPS voices."""
    amplitudes = np.asarray(state.data, dtype=np.complex128)
    if amplitudes.shape != (16,):
        raise ValueError("Hexany rendering requires a four-qubit statevector")
    probabilities = np.abs(amplitudes) ** 2
    shell_probability = float(sum(probabilities[index] for index in HEXANY_MASKS))
    if shell_probability <= 1e-15:
        return 0.0, ()
    dominant = max(HEXANY_MASKS, key=lambda index: probabilities[index])
    reference_phase = float(np.angle(amplitudes[dominant]))
    voices = []
    for basis_index in HEXANY_MASKS:
        factors = tuple(
            WILSON_GENERATORS[qubit]
            for qubit in range(4)
            if (basis_index >> qubit) & 1
        )
        product = factors[0] * factors[1]
        ratio = _octave_reduce(Fraction(product, max(WILSON_GENERATORS)))
        phase = float(
            np.angle(np.exp(1j * (np.angle(amplitudes[basis_index]) - reference_phase)))
        )
        voices.append(
            HexanyVoice(
                basis_index=basis_index,
                factors=(factors[0], factors[1]),
                complement_basis_index=basis_index ^ 0b1111,
                ratio_numerator=ratio.numerator,
                ratio_denominator=ratio.denominator,
                conditional_probability=float(probabilities[basis_index] / shell_probability),
                absolute_probability=float(probabilities[basis_index]),
                relative_phase=phase,
            )
        )
    return shell_probability, tuple(voices)


def pascal_grade_probabilities(state: Any) -> tuple[float, ...]:
    """Probability mass in the five four-qubit Pascal grades 0 through 4."""
    amplitudes = np.asarray(state.data, dtype=np.complex128)
    if amplitudes.shape != (16,):
        raise ValueError("Pascal-grade analysis requires a four-qubit statevector")
    probabilities = np.abs(amplitudes) ** 2
    return tuple(
        float(sum(probabilities[basis] for basis in range(16) if basis.bit_count() == grade))
        for grade in range(5)
    )


def hexany_exchange_flows(
    before_state: Any,
    after_state: Any,
    qubits: tuple[int, int],
) -> tuple[HexanyFlow, ...]:
    """Measure directed probability transfer along the selected Hexany edges."""
    before = np.asarray(before_state.data, dtype=np.complex128)
    after = np.asarray(after_state.data, dtype=np.complex128)
    if before.shape != (16,) or after.shape != (16,):
        raise ValueError("Hexany flow analysis requires four-qubit statevectors")
    source_qubit, target_qubit = (int(qubits[0]), int(qubits[1]))
    exchange_mask = (1 << source_qubit) | (1 << target_qubit)
    after_probabilities = np.abs(after) ** 2
    before_probabilities = np.abs(before) ** 2
    shell_probability = float(sum(after_probabilities[index] for index in HEXANY_MASKS))
    denominator = max(shell_probability, 1e-15)
    flows = []
    for basis_index in HEXANY_MASKS:
        source_bit = (basis_index >> source_qubit) & 1
        target_bit = (basis_index >> target_qubit) & 1
        if source_bit != 1 or target_bit != 0:
            continue
        partner = basis_index ^ exchange_mask
        probability_delta = float(
            after_probabilities[partner] - before_probabilities[partner]
        )
        if abs(probability_delta) <= 1e-12:
            continue
        if probability_delta > 0:
            departure, arrival = basis_index, partner
        else:
            departure, arrival = partner, basis_index
        relative_phase = float(
            np.angle(after[arrival] * np.conj(after[departure]))
        )
        magnitude = abs(probability_delta)
        flows.append(
            HexanyFlow(
                source_basis_index=departure,
                destination_basis_index=arrival,
                absolute_probability_flow=magnitude,
                conditional_probability_flow=magnitude / denominator,
                relative_phase=relative_phase,
            )
        )
    return tuple(
        sorted(
            flows,
            key=lambda flow: flow.conditional_probability_flow,
            reverse=True,
        )
    )


def _basis_pair_flows(
    before_state: Any,
    after_state: Any,
    pairs: list[tuple[int, int]],
) -> tuple[BasisFlow, ...]:
    before = np.asarray(before_state.data, dtype=np.complex128)
    after = np.asarray(after_state.data, dtype=np.complex128)
    before_probabilities = np.abs(before) ** 2
    after_probabilities = np.abs(after) ** 2
    flows = []
    for first, second in pairs:
        delta_second = float(
            after_probabilities[second] - before_probabilities[second]
        )
        if abs(delta_second) <= 1e-12:
            continue
        if delta_second > 0:
            departure, arrival = first, second
        else:
            departure, arrival = second, first
        flows.append(
            BasisFlow(
                source_basis_index=departure,
                destination_basis_index=arrival,
                probability_flow=abs(delta_second),
                relative_phase=float(
                    np.angle(after[arrival] * np.conj(after[departure]))
                ),
            )
        )
    return tuple(
        sorted(flows, key=lambda flow: flow.probability_flow, reverse=True)
    )


def basis_exchange_flows(
    before_state: Any,
    after_state: Any,
    qubits: tuple[int, int],
) -> tuple[BasisFlow, ...]:
    """Probability currents on every rank for an excitation exchange."""
    first_qubit, second_qubit = (int(qubits[0]), int(qubits[1]))
    exchange_mask = (1 << first_qubit) | (1 << second_qubit)
    pairs = [
        (basis, basis ^ exchange_mask)
        for basis in range(16)
        if ((basis >> first_qubit) & 1) == 1
        and ((basis >> second_qubit) & 1) == 0
    ]
    return _basis_pair_flows(before_state, after_state, pairs)


def basis_gate_flows(
    before_state: Any,
    after_state: Any,
    name: str,
    qubits: tuple[int, ...],
) -> tuple[BasisFlow, ...]:
    """Directed probability flow induced by a programmer gate."""
    name = str(name).lower()
    if name in {"h", "x", "y"}:
        bit = 1 << int(qubits[0])
        pairs = [(basis, basis ^ bit) for basis in range(16) if not basis & bit]
    elif name == "cx":
        control, target = (int(qubits[0]), int(qubits[1]))
        target_bit = 1 << target
        pairs = [
            (basis, basis ^ target_bit)
            for basis in range(16)
            if ((basis >> control) & 1) == 1 and not basis & target_bit
        ]
    else:
        pairs = []
    return _basis_pair_flows(before_state, after_state, pairs)


class RecursiveWilsonEngine:
    """State-dependent, reproducible recursion on the Hexany Johnson graph."""

    def __init__(
        self,
        *,
        seed: int = 23,
        temperature: float = 0.65,
        max_depth: int = 32,
        probe_basis: int = 0b0101,
    ) -> None:
        self.seed = int(seed)
        self.temperature = float(temperature)
        self.max_depth = int(max_depth)
        self.probe_basis = int(probe_basis)
        self._validate_controls()
        self.rng = np.random.default_rng(self.seed)
        self.seed_circuit = None
        self.reset()

    def _validate_controls(self) -> None:
        if not 0.0 <= self.temperature <= 2.0:
            raise ValueError("temperature must be between 0 and 2")
        if not 1 <= self.max_depth <= 256:
            raise ValueError("max_depth must be between 1 and 256")
        if self.probe_basis not in HEXANY_MASKS:
            raise ValueError("probe_basis must be a weight-two four-qubit state")

    def configure(
        self,
        *,
        seed: int | None = None,
        temperature: float | None = None,
        max_depth: int | None = None,
    ) -> None:
        if temperature is not None:
            self.temperature = float(temperature)
        if max_depth is not None:
            self.max_depth = int(max_depth)
        if seed is not None:
            self.seed = int(seed)
            self.rng = np.random.default_rng(self.seed)
        self._validate_controls()

    def reset(
        self,
        seed_circuit: Any | None = None,
        *,
        prepare_probe: bool = True,
    ) -> None:
        from qiskit import QuantumCircuit
        from qiskit.quantum_info import Statevector

        self.generation = 0
        self.rng = np.random.default_rng(self.seed)
        self.logical_circuit = QuantumCircuit(4)
        if prepare_probe:
            for qubit in range(4):
                if (self.probe_basis >> qubit) & 1:
                    self.logical_circuit.x(qubit)
        if seed_circuit is not None:
            if int(seed_circuit.num_qubits) != 4:
                raise ValueError("seed circuit must contain four qubits")
            unitary_seed = seed_circuit.remove_final_measurements(inplace=False)
            self.seed_circuit = unitary_seed.copy()
            self.logical_circuit.compose(unitary_seed, inplace=True)
        elif self.seed_circuit is not None:
            self.logical_circuit.compose(self.seed_circuit, inplace=True)
        self.state = Statevector.from_instruction(self.logical_circuit)

    def clear_circuit(self) -> None:
        """Return to an actual empty |0000> circuit/state.

        This is deliberately distinct from ``reset()``, which retains the
        historical Wilson probe for autonomous recursion.
        """
        self.seed_circuit = None
        self.reset(prepare_probe=False)

    def load_qasm2(self, qasm_text: str) -> None:
        from qiskit import qasm2

        # A programmer circuit is defined relative to |0000>, not on top of
        # the autonomous weight-two Wilson probe. This makes Bell, GHZ, and an
        # empty circuit physically and sonically distinguishable.
        self.seed_circuit = None
        self.reset(qasm2.loads(str(qasm_text)), prepare_probe=False)

    def _select_exchange(self) -> tuple[int, int, float, float]:
        shell_probability, voices = hexany_voices(self.state)
        if not voices:
            vertex = int(self.rng.choice(HEXANY_MASKS))
        else:
            probabilities = np.asarray(
                [voice.conditional_probability for voice in voices], dtype=float
            )
            exploration = min(1.0, self.temperature / 2.0)
            exponent = 1.0 / max(0.08, self.temperature)
            weights = np.power(probabilities + 1e-9, exponent)
            weights /= weights.sum()
            weights = (1.0 - exploration) * weights + exploration / len(weights)
            vertex = int(self.rng.choice(HEXANY_MASKS, p=weights))
        occupied = [qubit for qubit in range(4) if (vertex >> qubit) & 1]
        empty = [qubit for qubit in range(4) if not ((vertex >> qubit) & 1)]
        source = int(self.rng.choice(occupied))
        target = int(self.rng.choice(empty))
        theta = float(
            np.clip(
                math.pi / 6 * (0.5 + self.temperature * self.rng.uniform(0.25, 1.5)),
                math.pi / 32,
                math.pi * 0.9,
            )
        )
        beta = float(self.rng.uniform(-math.pi, math.pi) * min(1.0, self.temperature))
        return source, target, theta, beta

    def _complete_cps_weights(self) -> np.ndarray:
        """Temperature-shaped weights over all sixteen Boolean/CPS vertices."""
        probabilities = np.abs(np.asarray(self.state.data, dtype=np.complex128)) ** 2
        exploration = min(1.0, self.temperature / 2.0)
        exponent = 1.0 / max(0.08, self.temperature)
        weights = np.power(probabilities + 1e-9, exponent)
        weights /= weights.sum()
        # At maximum temperature this becomes uniform per vertex; summing by
        # grade therefore yields the Pascal multiplicities 1:4:6:4:1.
        return (1.0 - exploration) * weights + exploration / len(weights)

    def _select_complete_cps_vertex(self) -> int:
        return int(self.rng.choice(16, p=self._complete_cps_weights()))

    def _exchange_angles(self) -> tuple[float, float]:
        theta = float(
            np.clip(
                math.pi / 6 * (0.5 + self.temperature * self.rng.uniform(0.25, 1.5)),
                math.pi / 32,
                math.pi * 0.9,
            )
        )
        beta = float(self.rng.uniform(-math.pi, math.pi) * min(1.0, self.temperature))
        return theta, beta

    def next(self) -> RecursiveWilsonStep:
        from qiskit.circuit.library import XXPlusYYGate

        if self.generation >= self.max_depth:
            raise RuntimeError(f"maximum recursion depth {self.max_depth} reached")
        source, target, theta, beta = self._select_exchange()
        gate = XXPlusYYGate(theta, beta)
        self.logical_circuit.append(gate, [source, target])
        before_state = self.state
        self.state = self.state.evolve(gate, qargs=[source, target])
        self.generation += 1
        shell_probability, voices = hexany_voices(self.state)
        flows = hexany_exchange_flows(
            before_state,
            self.state,
            (source, target),
        )
        basis_flows = basis_exchange_flows(
            before_state,
            self.state,
            (source, target),
        )
        return RecursiveWilsonStep(
            generation=self.generation,
            qubits=(source, target),
            theta=theta,
            beta=beta,
            shell_probability=shell_probability,
            voices=voices,
            flows=flows,
            basis_flows=basis_flows,
            grade_probabilities=pascal_grade_probabilities(self.state),
        )

    def next_complete_cps(self) -> RecursiveWilsonStep:
        """Advance using temperature over all Pascal grades of the 4-cube.

        Interior grades move tangentially with an excitation-preserving XY
        exchange.  The grade-zero and grade-four poles have no Johnson-graph
        neighbor, so they move transversely with a Hadamard step.
        """
        from qiskit.circuit.library import HGate, XXPlusYYGate

        if self.generation >= self.max_depth:
            raise RuntimeError(f"maximum recursion depth {self.max_depth} reached")
        vertex = self._select_complete_cps_vertex()
        grade = vertex.bit_count()
        before_state = self.state

        if grade in {0, 4}:
            qubit = int(self.rng.integers(0, 4))
            gate = HGate()
            self.logical_circuit.append(gate, [qubit])
            self.state = self.state.evolve(gate, qargs=[qubit])
            qubits: tuple[int, ...] = (qubit,)
            theta, beta = math.pi / 2, 0.0
            motion = "H"
            flows: tuple[HexanyFlow, ...] = ()
            basis_flows = basis_gate_flows(
                before_state,
                self.state,
                "h",
                (qubit,),
            )
        else:
            occupied = [qubit for qubit in range(4) if (vertex >> qubit) & 1]
            empty = [qubit for qubit in range(4) if not ((vertex >> qubit) & 1)]
            source = int(self.rng.choice(occupied))
            target = int(self.rng.choice(empty))
            theta, beta = self._exchange_angles()
            gate = XXPlusYYGate(theta, beta)
            self.logical_circuit.append(gate, [source, target])
            self.state = self.state.evolve(gate, qargs=[source, target])
            qubits = (source, target)
            motion = "XY"
            flows = hexany_exchange_flows(
                before_state,
                self.state,
                (source, target),
            )
            basis_flows = basis_exchange_flows(
                before_state,
                self.state,
                (source, target),
            )

        self.generation += 1
        shell_probability, voices = hexany_voices(self.state)
        return RecursiveWilsonStep(
            generation=self.generation,
            qubits=qubits,
            theta=theta,
            beta=beta,
            shell_probability=shell_probability,
            voices=voices,
            flows=flows,
            basis_flows=basis_flows,
            motion=motion,
            selected_basis=vertex,
            selected_grade=grade,
            grade_probabilities=pascal_grade_probabilities(self.state),
        )

    def apply_gate(self, name: str, qubits: tuple[int, ...]) -> tuple[BasisFlow, ...]:
        """Apply a programmer intervention to both circuit and live state."""
        from qiskit import QuantumCircuit

        name = str(name).strip().lower()
        arities = {"h": 1, "x": 1, "y": 1, "z": 1, "s": 1, "t": 1, "cx": 2}
        if name not in arities or len(qubits) != arities[name]:
            raise ValueError(f"unsupported intervention {name}{qubits}")
        logical_qubits = tuple(int(qubit) for qubit in qubits)
        if any(not 0 <= qubit < 4 for qubit in logical_qubits):
            raise ValueError(f"intervention qubit out of range: {logical_qubits}")
        if len(set(logical_qubits)) != len(logical_qubits):
            raise ValueError("intervention qubits must be distinct")
        fragment = QuantumCircuit(4)
        getattr(fragment, name)(*logical_qubits)
        instruction = fragment.data[0]
        before_state = self.state
        self.logical_circuit.append(instruction.operation, list(logical_qubits))
        self.state = self.state.evolve(instruction.operation, qargs=list(logical_qubits))
        return basis_gate_flows(
            before_state,
            self.state,
            name,
            logical_qubits,
        )

    def synthesis_result(self) -> Any:
        from qasm_circuit_bridge_v1 import ComposerCircuit
        from qmw.synthesis import SynthesisResult, normalize_to_qmw

        normalized = normalize_to_qmw(self.logical_circuit, optimization_level=0)
        return SynthesisResult(
            kind="recursive_wilson_hexany",
            source_circuit=self.logical_circuit.copy(),
            qiskit_circuit=normalized,
            composer_circuit=ComposerCircuit.from_qiskit_circuit(normalized),
            metadata={
                "generation": self.generation,
                "seed": self.seed,
                "temperature": self.temperature,
                "max_depth": self.max_depth,
                "probe_basis": self.probe_basis,
                "cps": "2)4 1-3-5-7 Hexany",
            },
        )
