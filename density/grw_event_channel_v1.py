"""Four-qubit discrete GRW-style spontaneous-localization instrument.

Version 1 uses local, one-qubit hits.  The channel owns its independent
Poisson clock and RNG, but it does not own the density matrix and has no OSC,
synthesis, pitch, or geometry dependencies.  A conductor passes the canonical
state in and installs the returned post-hit state.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, replace
import json
import math
from pathlib import Path
from typing import Callable, Dict, List, Optional, Sequence, Tuple

import numpy as np


I2 = np.eye(2, dtype=np.complex128)
X = np.array([[0.0, 1.0], [1.0, 0.0]], dtype=np.complex128)
Y = np.array([[0.0, -1j], [1j, 0.0]], dtype=np.complex128)
Z = np.array([[1.0, 0.0], [0.0, -1.0]], dtype=np.complex128)
H = np.array([[1.0, 1.0], [1.0, -1.0]], dtype=np.complex128) / math.sqrt(2.0)
S_DAGGER = np.diag([1.0, -1j]).astype(np.complex128)
PAULI = {"I": I2, "X": X, "Y": Y, "Z": Z}


def canonical_pauli_terms(n_qubits: int = 4) -> Tuple[str, ...]:
    """Return the project's canonical 34-term four-qubit Pauli ecology."""
    identity = "I" * n_qubits
    result = [identity]
    for qubit in range(n_qubits):
        position = n_qubits - 1 - qubit
        for axis in "XYZ":
            chars = list(identity)
            chars[position] = axis
            result.append("".join(chars))
    for a in range(n_qubits):
        for b in range(a + 1, n_qubits):
            for axis in "XYZ":
                chars = list(identity)
                chars[n_qubits - 1 - a] = axis
                chars[n_qubits - 1 - b] = axis
                result.append("".join(chars))
    result.extend(axis * n_qubits for axis in "XYZ")
    return tuple(dict.fromkeys(result))


PAULI_TERMS_4Q = canonical_pauli_terms(4)


@dataclass(frozen=True)
class GRWConfig:
    enabled: bool = False
    rate_hz: float = 1.0
    width: float = 1.25
    metric: str = "hamming"
    basis_source: str = "circuit"
    constituent_scale: float = 1.0
    seed: int = 23
    salience_floor: float = 0.002

    def __post_init__(self) -> None:
        if self.rate_hz < 0.0:
            raise ValueError("rate_hz must be non-negative")
        if self.width <= 0.0:
            raise ValueError("width must be positive")
        if self.metric.lower() != "hamming":
            raise ValueError("v1 supports only the hamming metric")
        if self.constituent_scale < 0.0:
            raise ValueError("constituent_scale must be non-negative")
        if self.salience_floor < 0.0:
            raise ValueError("salience_floor must be non-negative")

    @property
    def strength(self) -> float:
        """Unsharpness eta derived from the one-bit Hamming Gaussian width."""
        return float(np.tanh(1.0 / (4.0 * self.width * self.width)))


@dataclass(frozen=True)
class GRWEvent:
    event_id: int
    logical_time: float
    revision_before: int
    revision_after: int
    qubit: int
    outcome: int
    center: int
    bitstring: str
    basis: str
    probability: float
    rate_hz: float
    width: float
    strength: float
    trace_distance: float
    coherence_before: float
    coherence_after: float
    purity_before: float
    purity_after: float
    entropy_before: float
    entropy_after: float
    population_displacement: float
    local_bloch_delta: Tuple[Tuple[float, float, float], ...]
    pauli_deltas: Dict[str, float]
    mutual_information_deltas: Dict[str, float]
    concurrence_deltas: Dict[str, float]
    dominant_pauli_delta: str
    dominant_pauli_delta_value: float
    audible: bool
    rho_before: np.ndarray
    rho_after: np.ndarray
    delta_rho: np.ndarray

    @property
    def time_seconds(self) -> float:
        return self.logical_time

    @property
    def coherence_delta(self) -> float:
        return self.coherence_after - self.coherence_before

    @property
    def purity_delta(self) -> float:
        return self.purity_after - self.purity_before

    @property
    def entropy_delta(self) -> float:
        return self.entropy_after - self.entropy_before

    @property
    def dominant_pauli(self) -> str:
        return self.dominant_pauli_delta

    def to_record(self, include_matrices: bool = False) -> dict:
        """Return a JSON-safe ledger/state-packet representation."""
        record = asdict(self)
        for key in ("rho_before", "rho_after", "delta_rho"):
            matrix = record.pop(key)
            if include_matrices:
                record[key] = {
                    "real": np.asarray(matrix).real.tolist(),
                    "imag": np.asarray(matrix).imag.tolist(),
                }
        record["time_seconds"] = self.time_seconds
        record["coherence_delta"] = self.coherence_delta
        record["purity_delta"] = self.purity_delta
        record["entropy_delta"] = self.entropy_delta
        record["dominant_pauli"] = self.dominant_pauli
        return record


@dataclass(frozen=True)
class GRWAdvanceResult:
    rho: np.ndarray
    events: Tuple[GRWEvent, ...]
    revision: int
    logical_time: float


def _normalize_density(rho: np.ndarray) -> np.ndarray:
    state = np.asarray(rho, dtype=np.complex128)
    if state.ndim != 2 or state.shape[0] != state.shape[1]:
        raise ValueError("rho must be a square density matrix")
    state = 0.5 * (state + state.conj().T)
    trace = float(np.trace(state).real)
    if trace <= 0.0:
        raise ValueError("rho must have positive trace")
    return state / trace


def _tensor(operators: Sequence[np.ndarray]) -> np.ndarray:
    result = np.array([[1.0]], dtype=np.complex128)
    for operator in operators:
        result = np.kron(result, operator)
    return result


def _local_operator(operator: np.ndarray, qubit: int) -> np.ndarray:
    if not 0 <= qubit < 4:
        raise ValueError("qubit must lie in [0, 3]")
    operators = [I2] * 4
    operators[qubit] = operator
    return _tensor(operators)


def _basis_change(basis: str) -> np.ndarray:
    """Return U satisfying U B U-dagger = Z."""
    label = basis.upper()
    if label == "Z":
        return I2
    if label == "X":
        return H
    if label == "Y":
        return H @ S_DAGGER
    raise ValueError("basis must be X, Y, or Z")


def width_to_strength(width: float) -> float:
    if width <= 0.0:
        raise ValueError("width must be positive")
    return float(np.tanh(1.0 / (4.0 * width * width)))


def strength_to_width(strength: float) -> float:
    """Inverse performance control mapping, with finite endpoint limits."""
    eta = float(strength)
    if not 0.0 <= eta <= 1.0:
        raise ValueError("strength must lie in [0, 1]")
    if eta <= 1e-12:
        return 1e6
    if eta >= 1.0 - 1e-12:
        return 1e-6
    return float(math.sqrt(1.0 / (4.0 * np.arctanh(eta))))


def single_qubit_kraus(strength: float, basis: str = "Z") -> Tuple[np.ndarray, np.ndarray]:
    """Return the two unsharp one-qubit localization operators."""
    eta = float(strength)
    if not 0.0 <= eta <= 1.0:
        raise ValueError("strength must lie in [0, 1]")
    root_plus = math.sqrt((1.0 + eta) / 2.0)
    root_minus = math.sqrt((1.0 - eta) / 2.0)
    diagonal = (
        np.diag([root_plus, root_minus]).astype(np.complex128),
        np.diag([root_minus, root_plus]).astype(np.complex128),
    )
    change = _basis_change(basis)
    return tuple(change.conj().T @ operator @ change for operator in diagonal)


def four_qubit_kraus(
    qubit: int,
    strength: float,
    basis: str = "Z",
) -> Tuple[np.ndarray, np.ndarray]:
    return tuple(_local_operator(operator, qubit) for operator in single_qubit_kraus(strength, basis))


def outcome_probabilities(rho: np.ndarray, kraus_ops: Sequence[np.ndarray]) -> np.ndarray:
    state = _normalize_density(rho)
    if state.shape != (16, 16):
        raise ValueError("GRW v1 requires a 16x16 four-qubit density matrix")
    probabilities = np.array(
        [np.trace(k @ state @ k.conj().T).real for k in kraus_ops],
        dtype=float,
    )
    probabilities = np.maximum(probabilities, 0.0)
    return probabilities / np.sum(probabilities)


def apply_outcome(rho: np.ndarray, kraus: np.ndarray) -> Tuple[np.ndarray, float]:
    state = _normalize_density(rho)
    if state.shape != (16, 16):
        raise ValueError("GRW v1 requires a 16x16 four-qubit density matrix")
    unnormalized = kraus @ state @ kraus.conj().T
    probability = float(np.trace(unnormalized).real)
    if probability <= 0.0:
        raise ValueError("selected outcome has zero probability")
    return _normalize_density(unnormalized / probability), probability


def l1_coherence(rho: np.ndarray) -> float:
    state = _normalize_density(rho)
    return float(np.sum(np.abs(state - np.diag(np.diag(state)))))


def purity(rho: np.ndarray) -> float:
    state = _normalize_density(rho)
    return float(np.trace(state @ state).real)


def entropy(rho: np.ndarray) -> float:
    values = np.linalg.eigvalsh(_normalize_density(rho)).real
    values = values[values > 1e-14]
    return float(-np.sum(values * np.log2(values))) if values.size else 0.0


def trace_distance(rho_a: np.ndarray, rho_b: np.ndarray) -> float:
    singular_values = np.linalg.svd(_normalize_density(rho_a) - _normalize_density(rho_b), compute_uv=False)
    return float(0.5 * np.sum(singular_values))


def _partial_trace(rho: np.ndarray, keep: Sequence[int]) -> np.ndarray:
    keep = tuple(sorted(keep))
    tensor = _normalize_density(rho).reshape((2,) * 8)
    input_labels = list(range(4)) + [q + 4 if q in keep else q for q in range(4)]
    output_labels = list(keep) + [q + 4 for q in keep]
    return np.einsum(tensor, input_labels, output_labels).reshape(2 ** len(keep), -1)


def _bloch_vectors(rho: np.ndarray) -> np.ndarray:
    return np.array(
        [[np.trace(_partial_trace(rho, [q]) @ PAULI[axis]).real for axis in "XYZ"] for q in range(4)],
        dtype=float,
    )


def _mutual_information(rho: np.ndarray) -> Dict[str, float]:
    result: Dict[str, float] = {}
    for a in range(4):
        for b in range(a + 1, 4):
            result[f"{a}{b}"] = max(
                0.0,
                entropy(_partial_trace(rho, [a]))
                + entropy(_partial_trace(rho, [b]))
                - entropy(_partial_trace(rho, [a, b])),
            )
    return result


def _concurrence_two_qubit(rho: np.ndarray) -> float:
    state = np.asarray(rho, dtype=np.complex128)
    yy = np.kron(Y, Y)
    spin_flip = yy @ state.conj() @ yy
    eigenvalues = np.linalg.eigvals(state @ spin_flip)
    roots = np.sort(np.sqrt(np.maximum(eigenvalues.real, 0.0)))[::-1]
    return float(max(0.0, roots[0] - np.sum(roots[1:])))


def _concurrences(rho: np.ndarray) -> Dict[str, float]:
    return {
        f"{a}{b}": _concurrence_two_qubit(_partial_trace(rho, [a, b]))
        for a in range(4)
        for b in range(a + 1, 4)
    }


_PAULI_OPERATORS = {
    term: _tensor([PAULI[label] for label in term])
    for term in PAULI_TERMS_4Q
}


def pauli_expectations(rho: np.ndarray) -> Dict[str, float]:
    state = _normalize_density(rho)
    return {
        term: float(np.trace(state @ operator).real)
        for term, operator in _PAULI_OPERATORS.items()
    }


class GRWEventChannel:
    """Seeded local-hit instrument with a state-independent Poisson clock."""

    def __init__(self, config: GRWConfig = GRWConfig()):
        self.config = config
        self.rng = np.random.default_rng(config.seed)
        self.logical_time = 0.0
        self.event_count = 0
        self.event_history: List[GRWEvent] = []
        self.next_event_time = math.inf
        self._schedule_from_now()

    @property
    def total_rate_hz(self) -> float:
        # rate_hz is the per-constituent rate; four equal constituents amplify it.
        return 4.0 * self.config.rate_hz * self.config.constituent_scale

    @property
    def next_event_ms(self) -> float:
        if not np.isfinite(self.next_event_time):
            return math.inf
        return max(0.0, (self.next_event_time - self.logical_time) * 1000.0)

    def _schedule_from_now(self) -> None:
        if not self.config.enabled or self.total_rate_hz <= 0.0:
            self.next_event_time = math.inf
            return
        self.next_event_time = self.logical_time + float(self.rng.exponential(1.0 / self.total_rate_hz))

    def reconfigure(self, **changes: object) -> None:
        """Replace immutable config and reschedule from the current time."""
        old_seed = self.config.seed
        self.config = replace(self.config, **changes)
        if self.config.seed != old_seed:
            self.rng = np.random.default_rng(self.config.seed)
        self._schedule_from_now()

    def pause(self) -> None:
        self.reconfigure(enabled=False)

    def resume(self) -> None:
        self.reconfigure(enabled=True)

    def sample_waiting_time(self, size: Optional[int] = None) -> np.ndarray | float:
        if self.total_rate_hz <= 0.0:
            return math.inf if size is None else np.full(size, math.inf)
        return self.rng.exponential(1.0 / self.total_rate_hz, size=size)

    def apply_hit(
        self,
        rho: np.ndarray,
        *,
        revision_before: int,
        basis: str = "Z",
        qubit: Optional[int] = None,
        outcome: Optional[int] = None,
        strength: Optional[float] = None,
    ) -> GRWEvent:
        state_before = _normalize_density(rho)
        if state_before.shape != (16, 16):
            raise ValueError("GRW v1 requires a 16x16 four-qubit density matrix")
        selected_qubit = int(self.rng.integers(0, 4)) if qubit is None else int(qubit)
        eta = self.config.strength if strength is None else float(strength)
        operators = four_qubit_kraus(selected_qubit, eta, basis)
        probabilities = outcome_probabilities(state_before, operators)
        selected_outcome = (
            int(self.rng.choice(2, p=probabilities))
            if outcome is None
            else int(outcome)
        )
        if selected_outcome not in (0, 1):
            raise ValueError("outcome must be 0 or 1")
        state_after, probability = apply_outcome(state_before, operators[selected_outcome])
        delta = state_after - state_before

        before_pauli = pauli_expectations(state_before)
        after_pauli = pauli_expectations(state_after)
        pauli_delta = {term: after_pauli[term] - value for term, value in before_pauli.items()}
        nonidentity = {term: value for term, value in pauli_delta.items() if set(term) != {"I"}}
        dominant = max(nonidentity, key=lambda term: abs(nonidentity[term]))
        before_mi = _mutual_information(state_before)
        after_mi = _mutual_information(state_after)
        before_concurrence = _concurrences(state_before)
        after_concurrence = _concurrences(state_after)
        salience = trace_distance(state_before, state_after)
        center = int(np.argmax(np.real(np.diag(state_after))))

        self.event_count += 1
        event = GRWEvent(
            event_id=self.event_count,
            logical_time=self.logical_time,
            revision_before=int(revision_before),
            revision_after=int(revision_before) + 1,
            qubit=selected_qubit,
            outcome=selected_outcome,
            center=center,
            bitstring=format(center, "04b"),
            basis=basis.upper(),
            probability=probability,
            rate_hz=self.config.rate_hz,
            width=self.config.width,
            strength=eta,
            trace_distance=salience,
            coherence_before=l1_coherence(state_before),
            coherence_after=l1_coherence(state_after),
            purity_before=purity(state_before),
            purity_after=purity(state_after),
            entropy_before=entropy(state_before),
            entropy_after=entropy(state_after),
            population_displacement=float(0.5 * np.sum(np.abs(np.diag(delta).real))),
            local_bloch_delta=tuple(map(tuple, _bloch_vectors(state_after) - _bloch_vectors(state_before))),
            pauli_deltas=pauli_delta,
            mutual_information_deltas={key: after_mi[key] - value for key, value in before_mi.items()},
            concurrence_deltas={key: after_concurrence[key] - value for key, value in before_concurrence.items()},
            dominant_pauli_delta=dominant,
            dominant_pauli_delta_value=pauli_delta[dominant],
            audible=salience >= self.config.salience_floor,
            rho_before=state_before.copy(),
            rho_after=state_after.copy(),
            delta_rho=delta.copy(),
        )
        self.event_history.append(event)
        return event

    def advance(
        self,
        rho: np.ndarray,
        dt: float,
        *,
        revision: int,
        basis: str = "Z",
        evolve: Optional[Callable[[np.ndarray, float], np.ndarray]] = None,
        on_event: Optional[Callable[[GRWEvent], None]] = None,
    ) -> GRWAdvanceResult:
        """Advance exactly to each due event, hit, then evolve the remainder."""
        if dt < 0.0:
            raise ValueError("dt must be non-negative")
        state = _normalize_density(rho)
        if state.shape != (16, 16):
            raise ValueError("GRW v1 requires a 16x16 four-qubit density matrix")
        end_time = self.logical_time + dt
        events: List[GRWEvent] = []
        evolve_state = evolve or (lambda current, _duration: current)

        while self.config.enabled and self.next_event_time <= end_time:
            segment = max(0.0, self.next_event_time - self.logical_time)
            if segment > 0.0:
                state = _normalize_density(evolve_state(state, segment))
                revision += 1
            self.logical_time = self.next_event_time
            event = self.apply_hit(state, revision_before=revision, basis=basis)
            state = event.rho_after
            revision = event.revision_after
            events.append(event)
            if on_event is not None:
                on_event(event)
            self._schedule_from_now()

        remainder = max(0.0, end_time - self.logical_time)
        if remainder > 0.0:
            state = _normalize_density(evolve_state(state, remainder))
            revision += 1
        self.logical_time = end_time
        return GRWAdvanceResult(state, tuple(events), revision, self.logical_time)

    def export_event_ledger(self, path: str | Path, include_matrices: bool = False) -> None:
        """Write the reproducible in-memory history as an append-compatible JSONL file."""
        destination = Path(path)
        with destination.open("w", encoding="utf-8") as handle:
            for event in self.event_history:
                record = event.to_record(include_matrices=include_matrices)
                record["rng_seed"] = self.config.seed
                handle.write(json.dumps(record, sort_keys=True) + "\n")


def ghz_density(phase: complex = 1j) -> np.ndarray:
    psi = np.zeros(16, dtype=np.complex128)
    psi[0] = 1.0
    psi[15] = phase
    psi /= np.linalg.norm(psi)
    return np.outer(psi, psi.conj())


def _demo() -> None:
    base = ghz_density()
    scenarios = (
        ("no_hit", None),
        ("weak", 0.15),
        ("strong", 0.85),
        ("projective", 1.0),
    )
    print("scenario outcome coherence_before coherence_after purity_after entropy_after trace_distance dominant_pauli")
    for index, (name, strength) in enumerate(scenarios):
        if strength is None:
            print(f"{name:10s} - {l1_coherence(base):.6f} {l1_coherence(base):.6f} {purity(base):.6f} {entropy(base):.6f} 0.000000 -")
            continue
        channel = GRWEventChannel(GRWConfig(seed=23 + index))
        event = channel.apply_hit(
            base,
            revision_before=0,
            basis="Z",
            qubit=0,
            outcome=0,
            strength=strength,
        )
        print(
            f"{name:10s} {event.outcome} {event.coherence_before:.6f} "
            f"{event.coherence_after:.6f} {event.purity_after:.6f} "
            f"{event.entropy_after:.6f} {event.trace_distance:.6f} "
            f"{event.dominant_pauli_delta}"
        )


if __name__ == "__main__":
    _demo()
