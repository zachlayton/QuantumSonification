"""Local four-qubit tomography engine.

Labels are written in musical/logical order q0, q1, q2, q3.  Qiskit's
displayed measurement words use the reverse order q3 q2 q1 q0; the conversion
is kept internal so the OSC and JSON formats remain natural to read.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from itertools import product
from typing import Any, Iterable

import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit.library import QFTGate
from qiskit.quantum_info import Statevector


AXES = ("X", "Y", "Z")
SETTINGS = tuple("".join(chars) for chars in product(AXES, repeat=4))
PAULI_LABELS = tuple("".join(chars) for chars in product("IXYZ", repeat=4))
BASIS_LABELS = tuple(f"{index:04b}" for index in range(16))
PAULI_MATRICES = {
    "I": np.array([[1, 0], [0, 1]], dtype=complex),
    "X": np.array([[0, 1], [1, 0]], dtype=complex),
    "Y": np.array([[0, -1j], [1j, 0]], dtype=complex),
    "Z": np.array([[1, 0], [0, -1]], dtype=complex),
}


@dataclass(frozen=True)
class SettingResult:
    index: int
    axes: str
    counts: list[int]
    probabilities: list[float]


@dataclass(frozen=True)
class PauliResult:
    index: int
    label: str
    weight: int
    expectation: float
    compatible_settings: int


@dataclass(frozen=True)
class ShellResult:
    weight: int
    term_count: int
    rms: float
    mean_abs: float
    energy: float


@dataclass(frozen=True)
class TomographyResult:
    schema: str
    source: str
    preset: str
    transform: str
    shots_per_setting: int
    total_shots: int
    seed: int
    qubit_order: str
    settings: list[SettingResult]
    paulis: list[PauliResult]
    shells: list[ShellResult]
    metrics: dict[str, float]
    density_linear_real: list[list[float]]
    density_linear_imag: list[list[float]]
    density_physical_real: list[list[float]]
    density_physical_imag: list[list[float]]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def build_score_circuit(preset: str = "ghz") -> QuantumCircuit:
    """Return one of the compact four-qubit score presets."""
    name = preset.lower()
    circuit = QuantumCircuit(4, name=f"qmw_{name}")
    if name == "bell":
        circuit.h(0)
        circuit.cx(0, 1)
    elif name == "ghz":
        circuit.h(0)
        circuit.cx(0, 1)
        circuit.cx(1, 2)
        circuit.cx(2, 3)
    elif name == "weave":
        for qubit in range(4):
            circuit.h(qubit)
        circuit.cx(0, 1)
        circuit.cx(2, 3)
        circuit.cx(1, 2)
        circuit.t(0)
        circuit.s(3)
    else:
        raise ValueError(f"unknown preset {preset!r}; choose bell, ghz, or weave")
    return circuit


def _apply_transform(circuit: QuantumCircuit, transform: str) -> QuantumCircuit:
    name = transform.lower()
    transformed = circuit.copy()
    if name == "none":
        return transformed
    if name == "qft":
        transformed.append(QFTGate(4), range(4))
        return transformed
    if name == "iqft":
        transformed.append(QFTGate(4).inverse(), range(4))
        return transformed
    raise ValueError(f"unknown transform {transform!r}; choose none, qft, or iqft")


def _measurement_probabilities(state: Statevector, axes: str) -> np.ndarray:
    rotation = QuantumCircuit(4)
    for qubit, axis in enumerate(axes):
        if axis == "X":
            rotation.h(qubit)
        elif axis == "Y":
            rotation.sdg(qubit)
            rotation.h(qubit)
        elif axis != "Z":
            raise ValueError(f"invalid measurement axis {axis!r}")
    measured = state.evolve(rotation)
    probabilities = np.real_if_close(np.abs(measured.data) ** 2).astype(float)
    probabilities[probabilities < 0] = 0
    return probabilities / probabilities.sum()


def _bit_for_logical_qubit(basis_index: int, qubit: int) -> int:
    return (basis_index >> qubit) & 1


def _estimate_pauli(
    pauli: str, setting_results: Iterable[SettingResult], shots: int
) -> tuple[float, int]:
    active_qubits = [qubit for qubit, axis in enumerate(pauli) if axis != "I"]
    if not active_qubits:
        return 1.0, len(SETTINGS)
    estimates: list[float] = []
    for setting in setting_results:
        if any(
            pauli[qubit] != "I" and setting.axes[qubit] != pauli[qubit]
            for qubit in range(4)
        ):
            continue
        signed_sum = 0
        for basis_index, count in enumerate(setting.counts):
            parity = sum(
                _bit_for_logical_qubit(basis_index, qubit)
                for qubit in active_qubits
            )
            signed_sum += count if parity % 2 == 0 else -count
        estimates.append(signed_sum / shots)
    return float(np.mean(estimates)), len(estimates)


def _operator_for_label(label: str) -> np.ndarray:
    # Qiskit's statevector basis is q3 tensor q2 tensor q1 tensor q0.
    operator = PAULI_MATRICES[label[3]]
    for logical_qubit in (2, 1, 0):
        operator = np.kron(operator, PAULI_MATRICES[label[logical_qubit]])
    return operator


def _density_from_paulis(paulis: Iterable[PauliResult]) -> np.ndarray:
    density = np.zeros((16, 16), dtype=complex)
    for pauli in paulis:
        density += pauli.expectation * _operator_for_label(pauli.label)
    return density / 16.0


def _project_to_physical_density(density: np.ndarray) -> tuple[np.ndarray, float]:
    hermitian = (density + density.conj().T) / 2.0
    eigenvalues, eigenvectors = np.linalg.eigh(hermitian)
    minimum = float(np.min(eigenvalues))
    clipped = np.clip(eigenvalues, 0.0, None)
    if clipped.sum() <= 0:
        clipped[:] = 1.0 / len(clipped)
    else:
        clipped /= clipped.sum()
    physical = (eigenvectors * clipped) @ eigenvectors.conj().T
    return physical, minimum


def _matrix_parts(matrix: np.ndarray) -> tuple[list[list[float]], list[list[float]]]:
    return matrix.real.tolist(), matrix.imag.tolist()


def _assemble_tomography_result(
    *,
    setting_results: list[SettingResult],
    preset: str,
    transform: str,
    shots: int,
    seed: int,
    source: str,
) -> TomographyResult:
    """Reconstruct Pauli coefficients and density matrices from 81 settings."""
    pauli_results: list[PauliResult] = []
    for index, label in enumerate(PAULI_LABELS):
        expectation, compatible = _estimate_pauli(label, setting_results, shots)
        pauli_results.append(
            PauliResult(
                index=index,
                label=label,
                weight=sum(axis != "I" for axis in label),
                expectation=expectation,
                compatible_settings=compatible,
            )
        )

    shell_results: list[ShellResult] = []
    for weight in range(5):
        values = np.array(
            [p.expectation for p in pauli_results if p.weight == weight],
            dtype=float,
        )
        shell_results.append(
            ShellResult(
                weight=weight,
                term_count=len(values),
                rms=float(np.sqrt(np.mean(values**2))),
                mean_abs=float(np.mean(np.abs(values))),
                energy=float(np.sum(values**2)),
            )
        )

    density_linear = _density_from_paulis(pauli_results)
    density_physical, minimum_linear_eigenvalue = _project_to_physical_density(
        density_linear
    )
    physical_eigenvalues = np.linalg.eigvalsh(density_physical)
    nonzero = physical_eigenvalues[physical_eigenvalues > 1e-15]
    entropy = float(-np.sum(nonzero * np.log2(nonzero))) if len(nonzero) else 0.0
    ideal_state = Statevector.from_instruction(
        _apply_transform(build_score_circuit(preset), transform)
    )
    fidelity = float(
        np.real(np.vdot(ideal_state.data, density_physical @ ideal_state.data))
    )
    linear_real, linear_imag = _matrix_parts(density_linear)
    physical_real, physical_imag = _matrix_parts(density_physical)

    return TomographyResult(
        schema="qmw.full4q.tomography.v1",
        source=source,
        preset=preset.lower(),
        transform=transform.lower(),
        shots_per_setting=shots,
        total_shots=sum(sum(setting.counts) for setting in setting_results),
        seed=seed,
        qubit_order="labels:q0,q1,q2,q3; basis:q3q2q1q0",
        settings=setting_results,
        paulis=pauli_results,
        shells=shell_results,
        metrics={
            "trace_linear": float(np.real(np.trace(density_linear))),
            "purity_physical": float(
                np.real(np.trace(density_physical @ density_physical))
            ),
            "entropy_bits_physical": entropy,
            "minimum_linear_eigenvalue": minimum_linear_eigenvalue,
            "fidelity_to_local_ideal": fidelity,
        },
        density_linear_real=linear_real,
        density_linear_imag=linear_imag,
        density_physical_real=physical_real,
        density_physical_imag=physical_imag,
    )


def reconstruct_tomography(
    setting_counts: Iterable[Iterable[int]],
    *,
    preset: str = "ghz",
    transform: str = "none",
    shots: int = 256,
    seed: int = 0,
    source: str = "ibm_hardware",
) -> TomographyResult:
    """Reconstruct the Full4Q dataset from ordered XXXX…ZZZZ count rows."""
    if shots <= 0:
        raise ValueError("shots must be positive")
    rows = [list(map(int, row)) for row in setting_counts]
    if len(rows) != len(SETTINGS):
        raise ValueError(f"expected {len(SETTINGS)} settings, received {len(rows)}")

    setting_results: list[SettingResult] = []
    for index, (axes, counts) in enumerate(zip(SETTINGS, rows)):
        if len(counts) != len(BASIS_LABELS):
            raise ValueError(
                f"setting {axes} expected {len(BASIS_LABELS)} bins, "
                f"received {len(counts)}"
            )
        if any(value < 0 for value in counts):
            raise ValueError(f"setting {axes} contains a negative count")
        observed_shots = sum(counts)
        if observed_shots != shots:
            raise ValueError(
                f"setting {axes} contains {observed_shots} shots; expected {shots}"
            )
        setting_results.append(
            SettingResult(
                index=index,
                axes=axes,
                counts=counts,
                probabilities=[value / shots for value in counts],
            )
        )

    return _assemble_tomography_result(
        setting_results=setting_results,
        preset=preset,
        transform=transform,
        shots=shots,
        seed=seed,
        source=source,
    )


def tomography_result_from_dict(payload: dict[str, Any]) -> TomographyResult:
    """Restore a normalized tomography result from a saved JSON object."""
    return TomographyResult(
        schema=str(payload["schema"]),
        source=str(payload["source"]),
        preset=str(payload["preset"]),
        transform=str(payload["transform"]),
        shots_per_setting=int(payload["shots_per_setting"]),
        total_shots=int(payload["total_shots"]),
        seed=int(payload["seed"]),
        qubit_order=str(payload["qubit_order"]),
        settings=[
            SettingResult(
                index=int(item["index"]),
                axes=str(item["axes"]),
                counts=[int(value) for value in item["counts"]],
                probabilities=[float(value) for value in item["probabilities"]],
            )
            for item in payload["settings"]
        ],
        paulis=[
            PauliResult(
                index=int(item["index"]),
                label=str(item["label"]),
                weight=int(item["weight"]),
                expectation=float(item["expectation"]),
                compatible_settings=int(item["compatible_settings"]),
            )
            for item in payload["paulis"]
        ],
        shells=[
            ShellResult(
                weight=int(item["weight"]),
                term_count=int(item["term_count"]),
                rms=float(item["rms"]),
                mean_abs=float(item["mean_abs"]),
                energy=float(item["energy"]),
            )
            for item in payload["shells"]
        ],
        metrics={str(key): float(value) for key, value in payload["metrics"].items()},
        density_linear_real=[
            [float(value) for value in row]
            for row in payload["density_linear_real"]
        ],
        density_linear_imag=[
            [float(value) for value in row]
            for row in payload["density_linear_imag"]
        ],
        density_physical_real=[
            [float(value) for value in row]
            for row in payload["density_physical_real"]
        ],
        density_physical_imag=[
            [float(value) for value in row]
            for row in payload["density_physical_imag"]
        ],
    )


def simulate_tomography(
    *,
    preset: str = "ghz",
    transform: str = "none",
    shots: int = 256,
    seed: int = 23,
) -> TomographyResult:
    """Sample all 81 local X/Y/Z settings and reconstruct four-qubit data."""
    if shots <= 0:
        raise ValueError("shots must be positive")
    score = build_score_circuit(preset)
    transformed = _apply_transform(score, transform)
    state = Statevector.from_instruction(transformed)
    random = np.random.default_rng(seed)

    setting_results: list[SettingResult] = []
    for index, axes in enumerate(SETTINGS):
        probabilities = _measurement_probabilities(state, axes)
        counts = random.multinomial(shots, probabilities)
        setting_results.append(
            SettingResult(
                index=index,
                axes=axes,
                counts=[int(value) for value in counts],
                probabilities=[float(value) for value in probabilities],
            )
        )

    return _assemble_tomography_result(
        setting_results=setting_results,
        preset=preset,
        transform=transform,
        shots=shots,
        seed=seed,
        source="local_statevector_sampled",
    )
