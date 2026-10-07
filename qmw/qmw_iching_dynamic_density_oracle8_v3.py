#!/usr/bin/env python3
"""Persistent eight-qubit dynamic I Ching density-matrix oracle (V3).

Qubits q0..q5 are the six lines, bottom upward; q6 and q7 form the
shared change register. ``observe`` is non-destructive. ``consult`` performs
a projective hexagram measurement, collapses ``rho``, and returns traditional
6/7/8/9 line values together with primary (H0), moving (M), and relating (H1)
hexagrams.
"""

from __future__ import annotations

import argparse
import itertools
import json
import math
import time
from dataclasses import dataclass
from typing import Any, Mapping, Sequence

import numpy as np

from qmw_density_backend import DensityBackend, create_backend

N_QUBITS = 8
DIM = 2**N_QUBITS
LOWER_QUBITS = (0, 1, 2)
UPPER_QUBITS = (3, 4, 5)
HEXAGRAM_QUBITS = LOWER_QUBITS + UPPER_QUBITS
CHANGE_QUBITS = (6, 7)

I2 = np.eye(2, dtype=np.complex128)
X = np.array([[0, 1], [1, 0]], dtype=np.complex128)
Y = np.array([[0, -1j], [1j, 0]], dtype=np.complex128)
Z = np.array([[1, 0], [0, -1]], dtype=np.complex128)
SM = np.array([[0, 1], [0, 0]], dtype=np.complex128)
PAULIS = {"I": I2, "X": X, "Y": Y, "Z": Z}

TRIGRAMS = {
    (1, 1, 1): ("Qian", "Heaven"),
    (1, 1, 0): ("Dui", "Lake"),
    (1, 0, 1): ("Li", "Fire"),
    (1, 0, 0): ("Zhen", "Thunder"),
    (0, 1, 1): ("Xun", "Wind"),
    (0, 1, 0): ("Kan", "Water"),
    (0, 0, 1): ("Gen", "Mountain"),
    (0, 0, 0): ("Kun", "Earth"),
}


def bit(index: int, qubit: int) -> int:
    return (index >> qubit) & 1


def lines_from_index(index: int) -> list[int]:
    return [bit(index, q) for q in HEXAGRAM_QUBITS]


def index_from_lines(lines: Sequence[int]) -> int:
    if len(lines) != 6:
        raise ValueError("a hexagram must contain exactly six lines")
    return sum((int(value) & 1) << q for q, value in enumerate(lines))


def full_operator(local_ops: Mapping[int, np.ndarray]) -> np.ndarray:
    result = np.array([[1.0 + 0.0j]])
    for qubit in reversed(range(N_QUBITS)):
        result = np.kron(result, local_ops.get(qubit, I2))
    return result


def reduced_density_matrix(rho: np.ndarray, keep: Sequence[int]) -> np.ndarray:
    """Partial trace using a stable q7..q0 tensor convention."""
    keep = tuple(keep)
    traced = tuple(q for q in range(N_QUBITS) if q not in keep)
    d_keep, d_traced = 2 ** len(keep), 2 ** len(traced)
    result = np.zeros((d_keep, d_keep), dtype=np.complex128)
    for a in range(d_keep):
        for b in range(d_keep):
            total = 0.0j
            for environment in range(d_traced):
                ia = ib = 0
                for position, q in enumerate(keep):
                    ia |= bit(a, position) << q
                    ib |= bit(b, position) << q
                for position, q in enumerate(traced):
                    value = bit(environment, position) << q
                    ia |= value
                    ib |= value
                total += rho[ia, ib]
            result[a, b] = total
    return result


def entropy(rho: np.ndarray) -> float:
    hermitian = 0.5 * (rho + rho.conj().T)
    values = np.clip(np.linalg.eigvalsh(hermitian).real, 0.0, None)
    values = values[values > 1e-14]
    return float(-np.sum(values * np.log2(values))) if values.size else 0.0


def sanitize_density_matrix(rho: np.ndarray, *, tolerance: float = 1e-10) -> np.ndarray:
    hermitian = 0.5 * (rho + rho.conj().T)
    values, vectors = np.linalg.eigh(hermitian)
    if float(values.min()) < -tolerance:
        values = np.clip(values, 0.0, None)
        hermitian = (vectors * values) @ vectors.conj().T
    trace = np.trace(hermitian).real
    if not np.isfinite(trace) or trace <= 0.0:
        raise ValueError("density matrix has non-positive trace")
    return hermitian / trace


@dataclass(frozen=True)
class PauliDescriptor:
    word: str
    label: str
    permutation: np.ndarray
    phase: np.ndarray


@dataclass
class DynamicFrame:
    time: float
    backend: str
    entropy_lower: float
    entropy_upper: float
    entropy_change: float
    entropy_hexagram: float
    mutual_information_lu: float
    d_entropy_lower: float
    d_entropy_upper: float
    d_entropy_change: float
    d_entropy_hexagram: float
    d_mutual_information_lu: float
    purity: float
    trace_error: float
    hermiticity_error: float
    minimum_eigenvalue: float
    hexagram_probabilities: list[float]
    dominant_hexagram_index: int
    dominant_hexagram_probability: float
    moving_probabilities: list[float]
    pauli81_values: dict[str, float]
    pauli81_labels: dict[str, str]
    dominant_pauli_word: str
    dominant_pauli_label: str
    dominant_pauli_expectation: float


@dataclass
class Consultation:
    time: float
    measurement_probability: float
    h0_index: int
    h0_lines: list[int]
    moving_probabilities: list[float]
    moving_lines: list[int]
    traditional_lines: list[int]
    h1_index: int
    h1_lines: list[int]
    lower_trigram: str
    upper_trigram: str

    @property
    def H0(self) -> list[int]:
        return self.h0_lines

    @property
    def M(self) -> list[int]:
        return self.moving_lines

    @property
    def H1(self) -> list[int]:
        return self.h1_lines


class DynamicIChingDensityOracle:
    """Stateful density oracle with optional unitary and Lindblad evolution."""

    def __init__(
        self,
        *,
        backend: str = "numpy",
        seed: int | None = None,
        dephasing_rate: float = 0.0,
        damping_rate: float = 0.0,
        coupling: float = 0.16,
        field_strength: float = 0.23,
        allow_backend_fallback: bool = True,
    ) -> None:
        self.backend: DensityBackend = create_backend(
            backend, allow_fallback=allow_backend_fallback
        )
        self.rng = np.random.default_rng(seed)
        self.dephasing_rate = float(dephasing_rate)
        self.damping_rate = float(damping_rate)
        self.time = 0.0
        self._previous_metrics: tuple[float, dict[str, float]] | None = None
        self._osc_client: Any | None = None

        plus = np.ones(DIM, dtype=np.complex128) / math.sqrt(DIM)
        self.rho = self.backend.array(
            np.outer(plus, plus.conj()), dtype=self.backend.complex_dtype
        )
        self.hamiltonian_static = self._build_hamiltonian(coupling, field_strength)
        self.modulation_operator = full_operator({6: X}) + 0.7 * full_operator({7: Y})
        self._pauli_field = self._compile_pauli_field()
        self._moving_operators = [
            full_operator({line: Z, CHANGE_QUBITS[line % 2]: Z}) for line in range(6)
        ]
        self._collapse_operators = []
        if self.dephasing_rate > 0:
            self._collapse_operators.extend(
                math.sqrt(self.dephasing_rate) * full_operator({q: Z})
                for q in range(N_QUBITS)
            )
        if self.damping_rate > 0:
            self._collapse_operators.extend(
                math.sqrt(self.damping_rate) * full_operator({q: SM})
                for q in range(N_QUBITS)
            )

    @staticmethod
    def _build_hamiltonian(coupling: float, field_strength: float) -> np.ndarray:
        h = np.zeros((DIM, DIM), dtype=np.complex128)
        for q in range(N_QUBITS):
            h += field_strength * (1.0 + 0.08 * q) * full_operator({q: Z})
        for q in range(5):
            h += coupling * full_operator({q: X, q + 1: X})
        h += 0.8 * coupling * full_operator({2: Y, 3: Y})
        h += coupling * full_operator({0: X, 6: X})
        h += coupling * full_operator({5: X, 7: X})
        return h

    @staticmethod
    def _compile_pauli_field() -> list[PauliDescriptor]:
        structural_qubits = (0, 2, 3, 5)
        structural_names = ("lower_root", "lower_crown", "upper_root", "upper_crown")
        descriptors = []
        for letters in itertools.product("XYZ", repeat=4):
            word = "".join(letters)
            label = " | ".join(
                f"{name}:{letter}" for name, letter in zip(structural_names, letters)
            )
            permutation = np.arange(DIM, dtype=np.int64)
            phase = np.ones(DIM, dtype=np.complex128)
            for basis in range(DIM):
                target = basis
                coefficient = 1.0 + 0.0j
                for qubit, letter in zip(structural_qubits, letters):
                    value = bit(basis, qubit)
                    if letter == "X":
                        target ^= 1 << qubit
                    elif letter == "Y":
                        target ^= 1 << qubit
                        coefficient *= 1j if value == 0 else -1j
                    else:
                        coefficient *= 1.0 if value == 0 else -1.0
                permutation[basis] = target
                phase[basis] = coefficient
            descriptors.append(PauliDescriptor(word, label, permutation, phase))
        return descriptors

    def density_matrix(self) -> np.ndarray:
        return np.array(self.backend.to_numpy(self.rho), dtype=np.complex128, copy=True)

    def set_density_matrix(self, rho: np.ndarray) -> None:
        value = np.asarray(rho, dtype=np.complex128)
        if value.shape != (DIM, DIM):
            raise ValueError(f"rho must have shape {(DIM, DIM)}")
        value = sanitize_density_matrix(value)
        self.rho = self.backend.array(value, dtype=self.backend.complex_dtype)
        self._previous_metrics = None

    def set_statevector(self, state: np.ndarray) -> None:
        vector = np.asarray(state, dtype=np.complex128).reshape(-1)
        if vector.size != DIM:
            raise ValueError(f"state must contain {DIM} amplitudes")
        norm = np.linalg.norm(vector)
        if norm == 0:
            raise ValueError("statevector cannot be zero")
        vector /= norm
        self.set_density_matrix(np.outer(vector, vector.conj()))

    def hamiltonian(self, at_time: float | None = None) -> np.ndarray:
        t = self.time if at_time is None else at_time
        return self.hamiltonian_static + 0.11 * math.sin(0.71 * t) * self.modulation_operator

    def evolve(self, dt: float, *, steps: int = 1) -> None:
        if dt <= 0 or steps < 1:
            raise ValueError("dt and steps must be positive")
        sub_dt = dt / steps
        for _ in range(steps):
            h = self.hamiltonian(self.time + 0.5 * sub_dt)
            values, vectors = np.linalg.eigh(h)
            u_np = (vectors * np.exp(-1j * values * sub_dt)) @ vectors.conj().T
            u = self.backend.array(u_np, dtype=self.backend.complex_dtype)
            rho = self.backend.matmul(
                self.backend.matmul(u, self.rho), self.backend.conjugate_transpose(u)
            )
            self.backend.evaluate(rho)
            rho_np = np.asarray(self.backend.to_numpy(rho), dtype=np.complex128)
            if self._collapse_operators:
                drho = np.zeros_like(rho_np)
                for collapse in self._collapse_operators:
                    cd = collapse.conj().T
                    rate_op = cd @ collapse
                    drho += collapse @ rho_np @ cd
                    drho -= 0.5 * (rate_op @ rho_np + rho_np @ rate_op)
                rho_np += sub_dt * drho
            rho_np = sanitize_density_matrix(rho_np, tolerance=2e-6)
            self.rho = self.backend.array(rho_np, dtype=self.backend.complex_dtype)
            self.time += sub_dt

    @staticmethod
    def _hexagram_probabilities(rho: np.ndarray) -> np.ndarray:
        diagonal = np.clip(np.diag(rho).real, 0.0, None)
        result = np.zeros(64, dtype=float)
        for basis_index, probability in enumerate(diagonal):
            result[basis_index & 0x3F] += probability
        total = result.sum()
        return result / total if total else result

    def _moving_probabilities(self, rho: np.ndarray) -> np.ndarray:
        probabilities = []
        for operator in self._moving_operators:
            correlation = float(np.trace(rho @ operator).real)
            probabilities.append(np.clip(0.5 * (1.0 - correlation), 0.0, 1.0))
        return np.asarray(probabilities)

    def observe(self) -> DynamicFrame:
        rho = self.density_matrix()
        reduced_lower = reduced_density_matrix(rho, LOWER_QUBITS)
        reduced_upper = reduced_density_matrix(rho, UPPER_QUBITS)
        reduced_change = reduced_density_matrix(rho, CHANGE_QUBITS)
        reduced_hexagram = reduced_density_matrix(rho, HEXAGRAM_QUBITS)
        values = {
            "entropy_lower": entropy(reduced_lower),
            "entropy_upper": entropy(reduced_upper),
            "entropy_change": entropy(reduced_change),
            "entropy_hexagram": entropy(reduced_hexagram),
        }
        values["mutual_information_lu"] = (
            values["entropy_lower"] + values["entropy_upper"] - values["entropy_hexagram"]
        )
        derivatives = {name: 0.0 for name in values}
        if self._previous_metrics is not None:
            previous_time, previous = self._previous_metrics
            elapsed = self.time - previous_time
            if elapsed > 0:
                derivatives = {
                    name: (value - previous[name]) / elapsed for name, value in values.items()
                }
        self._previous_metrics = (self.time, values.copy())

        hexagrams = self._hexagram_probabilities(rho)
        moving = self._moving_probabilities(rho)
        basis_indices = np.arange(DIM)
        pauli_values = {
            descriptor.word: float(
                np.sum(rho[basis_indices, descriptor.permutation] * descriptor.phase).real
            )
            for descriptor in self._pauli_field
        }
        pauli_labels = {descriptor.word: descriptor.label for descriptor in self._pauli_field}
        dominant_word = max(pauli_values, key=lambda word: abs(pauli_values[word]))
        dominant_hexagram = int(np.argmax(hexagrams))
        eigenvalues = np.linalg.eigvalsh(0.5 * (rho + rho.conj().T))
        frame = DynamicFrame(
            time=self.time,
            backend=self.backend.name,
            **values,
            d_entropy_lower=derivatives["entropy_lower"],
            d_entropy_upper=derivatives["entropy_upper"],
            d_entropy_change=derivatives["entropy_change"],
            d_entropy_hexagram=derivatives["entropy_hexagram"],
            d_mutual_information_lu=derivatives["mutual_information_lu"],
            purity=float(np.trace(rho @ rho).real),
            trace_error=abs(float(np.trace(rho).real) - 1.0),
            hermiticity_error=float(np.linalg.norm(rho - rho.conj().T)),
            minimum_eigenvalue=float(eigenvalues.min()),
            hexagram_probabilities=hexagrams.tolist(),
            dominant_hexagram_index=dominant_hexagram,
            dominant_hexagram_probability=float(hexagrams[dominant_hexagram]),
            moving_probabilities=moving.tolist(),
            pauli81_values=pauli_values,
            pauli81_labels=pauli_labels,
            dominant_pauli_word=dominant_word,
            dominant_pauli_label=pauli_labels[dominant_word],
            dominant_pauli_expectation=pauli_values[dominant_word],
        )
        self._stream_frame(frame)
        return frame

    def consult(self) -> Consultation:
        rho = self.density_matrix()
        probabilities = self._hexagram_probabilities(rho)
        chosen = int(self.rng.choice(64, p=probabilities))
        mask = np.array([(basis & 0x3F) == chosen for basis in range(DIM)])
        collapsed = rho * np.outer(mask, mask)
        measurement_probability = float(np.trace(collapsed).real)
        collapsed /= measurement_probability
        self.rho = self.backend.array(collapsed, dtype=self.backend.complex_dtype)

        h0 = lines_from_index(chosen)
        moving_probabilities = self._moving_probabilities(collapsed)
        moving_lines = (self.rng.random(6) < moving_probabilities).astype(int).tolist()
        h1 = [line ^ moving for line, moving in zip(h0, moving_lines)]
        traditional = [
            9 if line and moving else 7 if line else 6 if moving else 8
            for line, moving in zip(h0, moving_lines)
        ]
        lower = TRIGRAMS[tuple(h0[:3])][0]
        upper = TRIGRAMS[tuple(h0[3:])][0]
        result = Consultation(
            time=self.time,
            measurement_probability=measurement_probability,
            h0_index=chosen,
            h0_lines=h0,
            moving_probabilities=moving_probabilities.tolist(),
            moving_lines=moving_lines,
            traditional_lines=traditional,
            h1_index=index_from_lines(h1),
            h1_lines=h1,
            lower_trigram=lower,
            upper_trigram=upper,
        )
        self._stream_consultation(result)
        return result

    def enable_osc(self, host: str = "127.0.0.1", port: int = 7403) -> None:
        try:
            from pythonosc.udp_client import SimpleUDPClient
        except ImportError as exc:
            raise RuntimeError("OSC requires the optional 'python-osc' package") from exc
        self._osc_client = SimpleUDPClient(host, port)

    def _stream_frame(self, frame: DynamicFrame) -> None:
        if self._osc_client is None:
            return
        c = self._osc_client
        c.send_message("/qmw/iching/v3/time", frame.time)
        c.send_message("/qmw/iching/v3/hexagram64", frame.hexagram_probabilities)
        c.send_message("/qmw/iching/v3/moving6", frame.moving_probabilities)
        c.send_message("/qmw/iching/v3/pauli81", list(frame.pauli81_values.values()))
        c.send_message(
            "/qmw/iching/v3/information",
            [frame.entropy_lower, frame.entropy_upper, frame.entropy_change,
             frame.entropy_hexagram, frame.mutual_information_lu, frame.purity],
        )

    def _stream_consultation(self, result: Consultation) -> None:
        if self._osc_client is not None:
            self._osc_client.send_message(
                "/qmw/iching/v3/consult",
                [result.h0_index, result.h1_index, *result.traditional_lines],
            )


def _demo(args: argparse.Namespace) -> None:
    oracle = DynamicIChingDensityOracle(
        backend=args.backend,
        seed=args.seed,
        dephasing_rate=args.dephasing,
        damping_rate=args.damping,
    )
    if args.osc:
        oracle.enable_osc(args.osc_host, args.osc_port)
    started = time.perf_counter()
    frame = oracle.observe()
    for _ in range(args.steps):
        oracle.evolve(args.dt)
        frame = oracle.observe()
    elapsed = time.perf_counter() - started
    consultation = oracle.consult()
    print(json.dumps({
        "backend": oracle.backend.name,
        "requested_backend": args.backend,
        "steps": args.steps,
        "elapsed_seconds": elapsed,
        "frames_per_second": (args.steps + 1) / elapsed,
        "trace_error": frame.trace_error,
        "minimum_eigenvalue": frame.minimum_eigenvalue,
        "purity": frame.purity,
        "H0": consultation.H0,
        "M": consultation.M,
        "traditional_lines": consultation.traditional_lines,
        "H1": consultation.H1,
        "dominant_pauli": frame.dominant_pauli_word,
    }, indent=2))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--backend", choices=("numpy", "mlx"), default="numpy")
    parser.add_argument("--steps", type=int, default=3)
    parser.add_argument("--dt", type=float, default=0.01)
    parser.add_argument("--seed", type=int, default=8)
    parser.add_argument("--dephasing", type=float, default=0.0)
    parser.add_argument("--damping", type=float, default=0.0)
    parser.add_argument("--osc", action="store_true")
    parser.add_argument("--osc-host", default="127.0.0.1")
    parser.add_argument("--osc-port", type=int, default=7403)
    return parser


if __name__ == "__main__":
    _demo(build_parser().parse_args())
