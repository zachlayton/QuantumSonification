#!/usr/bin/env python3
"""Turn QAC OpenQASM into 256-point local and IBM Quantum wavetables.

The bridge accepts the existing /qmw/qac/{begin,chunk,end,qasm} OSC protocol.
It publishes an immediate local-simulator table and can then replace it with a
table derived from either direct IBM SamplerV2 hardware counts or optional
Algorithmiq TEM expectation values. Counts determine harmonic magnitudes; they
do not recover quantum phase.
"""

from __future__ import annotations

import argparse
import math
import sys
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import unquote

import numpy as np
from pythonosc import dispatcher, osc_server
from pythonosc.udp_client import SimpleUDPClient
from density_hamiltonian_engine_v6 import density_hamiltonian_transitions

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from qac_quantumsonification_bridge_v1.qac_quantumsonification_bridge_v1 import (
    analyze,
    parse_qasm,
)

from quantum_sonification import write_wav


ACCOUNT_NAME = "quantum-sonification-workshop"
TABLE_SIZE = 256
PAULI15 = ("XI", "YI", "ZI", "IX", "IY", "IZ", "XX", "XY", "XZ", "YX", "YY", "YZ", "ZX", "ZY", "ZZ")
TEM_FUNCTION_NAME = "algorithmiq/tem"


def transformed_circuit(qasm: str, transform: str = "none"):
    """Load QAC QASM and append an optional QFT before any measurement.

    Measurements exported by QAC are removed first so the transform remains a
    genuine unitary stage. Measurement is added later by the selected mapping.
    """
    from qiskit import qasm2
    from qiskit.circuit.library import QFTGate

    circuit = qasm2.loads(qasm).remove_final_measurements(inplace=False)
    if transform == "none":
        return circuit
    if transform not in ("qft", "iqft"):
        raise ValueError(f"Unsupported circuit transform: {transform!r}")
    gate = QFTGate(circuit.num_qubits)
    if transform == "iqft":
        gate = gate.inverse()
    circuit.append(gate, circuit.qubits)
    return circuit


def local_qft_spectrum(
    qasm: str, transform: str = "qft"
) -> tuple[np.ndarray, np.ndarray, np.ndarray, int]:
    """Return probabilities, magnitudes, and phases of the transformed state."""
    from qiskit.quantum_info import Statevector

    circuit = transformed_circuit(qasm, transform)
    vector = np.asarray(Statevector.from_instruction(circuit).data, dtype=np.complex128)
    probabilities = np.abs(vector) ** 2
    magnitudes = np.abs(vector)
    phases = np.angle(vector)
    return probabilities, magnitudes, phases, circuit.num_qubits


def counts_to_wavetable(counts: dict[str, int], size: int = TABLE_SIZE) -> np.ndarray:
    """Map bitstring probabilities to successive harmonic magnitudes."""
    cleaned = {str(label).replace(" ", ""): int(value) for label, value in counts.items()}
    shots = sum(cleaned.values())
    if shots <= 0:
        raise ValueError("Sampler returned no counts")
    width = max(len(label) for label in cleaned)
    phase = 2.0 * np.pi * np.arange(size) / size
    table = np.zeros(size)
    for label, count in cleaned.items():
        index = int(label, 2)
        magnitude = math.sqrt(count / shots)
        table += magnitude * np.sin((index + 1) * phase)
    table -= np.mean(table)
    peak = float(np.max(np.abs(table)))
    if peak:
        table *= 0.95 / peak
    return table


def correlations_to_wavetable(correlations: dict[str, float], size: int = TABLE_SIZE) -> np.ndarray:
    """Map signed XX, YY, ZZ pair correlations to harmonics 1, 2, 3."""
    phase = 2.0 * np.pi * np.arange(size) / size
    table = np.zeros(size)
    for harmonic, axis in enumerate(("XX", "YY", "ZZ"), start=1):
        table += float(correlations[axis]) * np.sin(harmonic * phase)
    table -= np.mean(table)
    peak = float(np.max(np.abs(table)))
    if peak:
        table *= 0.95 / peak
    return table


def correlation_from_counts(counts: dict[str, int], qubit_a: int, qubit_b: int) -> float:
    """Return <axis_a axis_b> from same-axis measurement bitstrings."""
    total = sum(int(value) for value in counts.values())
    if total <= 0:
        raise ValueError("Sampler returned no counts")
    weighted = 0
    for label, count in counts.items():
        bits = str(label).replace(" ", "")
        bit_a = int(bits[-1 - qubit_a])
        bit_b = int(bits[-1 - qubit_b])
        weighted += int(count) * (1 if bit_a == bit_b else -1)
    return weighted / total


def expectation_from_counts(counts: dict[str, int], qubit: int) -> float:
    """Return a single-qubit Pauli expectation after its basis rotation."""
    total = sum(int(value) for value in counts.values())
    if total <= 0:
        raise ValueError("Sampler returned no counts")
    weighted = 0
    for label, count in counts.items():
        bits = str(label).replace(" ", "")
        weighted += int(count) * (1 if bits[-1 - qubit] == "0" else -1)
    return weighted / total


def local_counts(
    qasm: str, shots: int, seed: int, transform: str = "none"
) -> tuple[dict[str, int], int]:
    if transform != "none":
        from qiskit.quantum_info import Statevector

        circuit = transformed_circuit(qasm, transform)
        state = Statevector.from_instruction(circuit)
        state.seed(seed)
        return dict(state.sample_counts(shots)), circuit.num_qubits
    circuit = parse_qasm(qasm, expected_qubits=None)
    frame = analyze(circuit, revision=0, shots=shots, seed=seed)
    return frame.counts, circuit.n_qubits


def local_correlations(
    qasm: str, qubit_a: int, qubit_b: int, transform: str = "none"
) -> tuple[dict[str, float], int]:
    """Calculate ideal pair correlations directly from the local statevector."""
    from qiskit.quantum_info import Pauli, Statevector

    circuit = transformed_circuit(qasm, transform)
    state = Statevector.from_instruction(circuit)
    values: dict[str, float] = {}
    for axis in "XYZ":
        label = ["I"] * circuit.num_qubits
        label[-1 - qubit_a] = axis
        label[-1 - qubit_b] = axis
        values[axis + axis] = float(np.real(state.expectation_value(Pauli("".join(label)))))
    return values, circuit.num_qubits


def local_pauli15(
    qasm: str, qubit_a: int, qubit_b: int, transform: str = "none"
) -> tuple[dict[str, float], int]:
    """Return the complete non-identity two-qubit Pauli expectation vector."""
    from qiskit.quantum_info import Pauli, Statevector

    circuit = transformed_circuit(qasm, transform)
    state = Statevector.from_instruction(circuit)
    values = {}
    for term in PAULI15:
        label = ["I"] * circuit.num_qubits
        label[-1 - qubit_a] = term[0]
        label[-1 - qubit_b] = term[1]
        values[term] = float(np.real(state.expectation_value(Pauli("".join(label)))))
    return values, circuit.num_qubits


def pauli15_surface(values: dict[str, float], size: int = TABLE_SIZE) -> np.ndarray:
    """Create four spectral views using distinct positive/negative harmonics.

    Each of the 15 Pauli expectations owns two partials: +v uses harmonic
    2*i+1 and -v uses harmonic 2*i+2.  This makes a sign change audible as a
    spectral change instead of the phase-only inversion produced by the old
    one-partial mapping.
    """
    phase = 2.0 * np.pi * np.arange(size) / size
    rows = np.zeros((4, size)) + 0.08 * np.sin(phase)
    for index, term in enumerate(PAULI15):
        value = float(values[term])
        base = 2 * index + (1 if value >= 0.0 else 2)
        # Four audibly different orchestrations of the *same* expectation
        # vector. The earlier q0/q1/correlation/full grouping produced
        # duplicate rows for Bell and other symmetric states, making a
        # correctly working Y inlet appear inert.
        harmonics = (base, base + 12, 2 * base, 61 - base)
        for row, harmonic in enumerate(harmonics):
            rows[row] += abs(value) * np.sin(harmonic * phase)
    # Only attenuate overloads. Do not peak-normalize every circuit, because
    # that would erase useful information about expectation-value magnitude.
    peak = float(np.max(np.abs(rows)))
    if peak > 0.95:
        rows *= 0.95 / peak
    return rows


def density_matrix_from_pauli15(values: dict[str, float]) -> np.ndarray:
    """Reconstruct and physically project a two-qubit density matrix."""
    matrices = {
        "I": np.eye(2, dtype=complex),
        "X": np.array([[0, 1], [1, 0]], dtype=complex),
        "Y": np.array([[0, -1j], [1j, 0]], dtype=complex),
        "Z": np.array([[1, 0], [0, -1]], dtype=complex),
    }
    rho = np.kron(matrices["I"], matrices["I"])
    for term in PAULI15:
        rho += float(values[term]) * np.kron(matrices[term[0]], matrices[term[1]])
    rho /= 4.0
    rho = (rho + rho.conj().T) / 2.0
    eigenvalues, eigenvectors = np.linalg.eigh(rho)
    eigenvalues = np.clip(eigenvalues.real, 0.0, None)
    if float(np.sum(eigenvalues)) <= 0.0:
        return np.eye(4, dtype=complex) / 4.0
    eigenvalues /= np.sum(eigenvalues)
    return (eigenvectors * eigenvalues) @ eigenvectors.conj().T


def two_qubit_concurrence(rho: np.ndarray) -> float:
    """Wootters concurrence for a physical two-qubit density matrix."""
    y = np.array([[0, -1j], [1j, 0]], dtype=complex)
    yy = np.kron(y, y)
    spin_flipped = yy @ rho.conj() @ yy
    eigenvalues = np.linalg.eigvals(rho @ spin_flipped)
    roots = np.sort(np.sqrt(np.clip(eigenvalues.real, 0.0, None)))[::-1]
    return float(np.clip(roots[0] - np.sum(roots[1:]), 0.0, 1.0))


def pauli15_quantum_features(values: dict[str, float]) -> tuple[float, float, float, float]:
    """Return raw dimensionless features; make no musical-unit decisions.

    The result is (Z polarization, concurrence, correlation RMS, normalized
    Z-basis entropy). Concurrence remains valid for mixed pair states and for
    a reduced pair selected from a larger circuit.
    """
    polarization = 0.5 * (float(values["ZI"]) + float(values["IZ"]))
    entanglement = two_qubit_concurrence(density_matrix_from_pauli15(values))
    correlation_terms = ("XX", "XY", "XZ", "YX", "YY", "YZ", "ZX", "ZY", "ZZ")
    correlation_rms = float(np.sqrt(np.mean([float(values[t]) ** 2 for t in correlation_terms])))
    zi, iz, zz = (float(values[t]) for t in ("ZI", "IZ", "ZZ"))
    probabilities = np.asarray([
        (1 + zi + iz + zz) / 4,
        (1 + zi - iz - zz) / 4,
        (1 - zi + iz - zz) / 4,
        (1 - zi - iz + zz) / 4,
    ])
    probabilities = np.clip(probabilities, 0.0, 1.0)
    nonzero = probabilities[probabilities > 0.0]
    entropy = float(-np.sum(nonzero * np.log2(nonzero)) / 2.0)
    return polarization, entanglement, correlation_rms, entropy


def ibm_counts(
    qasm: str,
    shots: int,
    backend_name: str | None,
    account_name: str,
    transform: str = "none",
) -> tuple[dict[str, int], str, str]:
    """Run QAC state preparation plus the selected transform on IBM hardware."""
    from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
    from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2

    circuit = transformed_circuit(qasm, transform)
    circuit.measure_all()
    service = QiskitRuntimeService(name=account_name)
    backend = (
        service.backend(backend_name)
        if backend_name
        else service.least_busy(
            operational=True,
            simulator=False,
            min_num_qubits=circuit.num_qubits,
        )
    )
    pass_manager = generate_preset_pass_manager(backend=backend, optimization_level=1)
    isa_circuit = pass_manager.run(circuit)
    sampler = SamplerV2(mode=backend)
    job = sampler.run([isa_circuit], shots=shots)
    print(
        f"IBM job submitted: id={job.job_id()} backend={backend.name} "
        f"shots={shots}"
    )
    result = job.result()[0]
    # measure_all() appends a register named "meas" when QAC exported only an
    # unused creg. Otherwise preserve the circuit's original measurement creg.
    bit_array = result.data.meas
    return bit_array.get_counts(), backend.name, job.job_id()


def ibm_correlations(
    qasm: str,
    shots: int,
    backend_name: str | None,
    account_name: str,
    qubit_a: int,
    qubit_b: int,
    transform: str = "none",
) -> tuple[dict[str, float], str, str]:
    """Measure XX, YY, ZZ in one SamplerV2 job and return correlations."""
    from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
    from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2

    base = transformed_circuit(qasm, transform)
    circuits = []
    for axis in "XYZ":
        circuit = base.copy()
        if axis == "X":
            circuit.h([qubit_a, qubit_b])
        elif axis == "Y":
            circuit.sdg([qubit_a, qubit_b])
            circuit.h([qubit_a, qubit_b])
        circuit.measure_all()
        circuits.append(circuit)

    service = QiskitRuntimeService(name=account_name)
    backend = (
        service.backend(backend_name)
        if backend_name
        else service.least_busy(
            operational=True, simulator=False, min_num_qubits=base.num_qubits
        )
    )
    pass_manager = generate_preset_pass_manager(backend=backend, optimization_level=1)
    isa_circuits = pass_manager.run(circuits)
    sampler = SamplerV2(mode=backend)
    job = sampler.run(isa_circuits, shots=shots)
    print(
        f"IBM correlation job submitted: id={job.job_id()} backend={backend.name} "
        f"circuits=3 shots_per_basis={shots}"
    )
    results = job.result()
    values = {}
    for axis, result in zip("XYZ", results):
        counts = result.data.meas.get_counts()
        values[axis + axis] = correlation_from_counts(counts, qubit_a, qubit_b)
    return values, backend.name, job.job_id()


def ibm_pauli15(
    qasm: str,
    shots: int,
    backend_name: str | None,
    account_name: str,
    qubit_a: int,
    qubit_b: int,
    transform: str = "none",
) -> tuple[dict[str, float], str, str]:
    """Estimate all 15 two-qubit Pauli terms with nine basis circuits."""
    from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
    from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2

    base = transformed_circuit(qasm, transform)
    circuits = []
    bases = [(a, b) for a in "XYZ" for b in "XYZ"]

    def rotate(circuit, axis: str, qubit: int) -> None:
        if axis == "X":
            circuit.h(qubit)
        elif axis == "Y":
            circuit.sdg(qubit)
            circuit.h(qubit)

    for axis_a, axis_b in bases:
        circuit = base.copy()
        rotate(circuit, axis_a, qubit_a)
        rotate(circuit, axis_b, qubit_b)
        circuit.measure_all()
        circuits.append(circuit)

    service = QiskitRuntimeService(name=account_name)
    backend = (
        service.backend(backend_name)
        if backend_name
        else service.least_busy(
            operational=True, simulator=False, min_num_qubits=base.num_qubits
        )
    )
    pass_manager = generate_preset_pass_manager(backend=backend, optimization_level=1)
    isa_circuits = pass_manager.run(circuits)
    sampler = SamplerV2(mode=backend)
    job = sampler.run(isa_circuits, shots=shots)
    print(
        f"IBM Pauli-15 job submitted: id={job.job_id()} backend={backend.name} "
        f"circuits=9 shots_per_basis={shots}"
    )
    results = job.result()
    values: dict[str, float] = {}
    local_a = {axis: [] for axis in "XYZ"}
    local_b = {axis: [] for axis in "XYZ"}
    for (axis_a, axis_b), result in zip(bases, results):
        counts = result.data.meas.get_counts()
        values[axis_a + axis_b] = correlation_from_counts(counts, qubit_a, qubit_b)
        local_a[axis_a].append(expectation_from_counts(counts, qubit_a))
        local_b[axis_b].append(expectation_from_counts(counts, qubit_b))
    for axis in "XYZ":
        values[axis + "I"] = float(np.mean(local_a[axis]))
        values["I" + axis] = float(np.mean(local_b[axis]))
    return {term: values[term] for term in PAULI15}, backend.name, job.job_id()


@dataclass(frozen=True)
class TEMExecutionResult:
    """Mitigated and reference expectation values returned by one TEM PUB."""

    values: dict[str, float]
    stds: dict[str, float]
    raw_values: dict[str, float]
    raw_stds: dict[str, float]
    backend: str
    job_id: str
    resource_usage: dict[str, object]


def pair_pauli_observables(
    num_qubits: int,
    qubit_a: int,
    qubit_b: int,
    terms: tuple[str, ...],
):
    """Build full-width Qiskit observables for a selected two-qubit pair."""
    from qiskit.quantum_info import SparsePauliOp

    if qubit_a == qubit_b:
        raise ValueError("TEM observables require two distinct qubits")
    if not 0 <= qubit_a < num_qubits or not 0 <= qubit_b < num_qubits:
        raise ValueError(
            f"TEM qubit pair q{qubit_a},q{qubit_b} is outside a {num_qubits}-qubit circuit"
        )
    observables = []
    for term in terms:
        if len(term) != 2 or any(axis not in "IXYZ" for axis in term):
            raise ValueError(f"Invalid two-qubit Pauli term: {term!r}")
        label = ["I"] * num_qubits
        label[-1 - qubit_a] = term[0]
        label[-1 - qubit_b] = term[1]
        observables.append(SparsePauliOp("".join(label)))
    return observables


def _tem_vector(name: str, value, terms: tuple[str, ...]) -> dict[str, float]:
    """Normalize a TEM result vector and retain the requested term ordering."""
    vector = np.asarray(value, dtype=float).reshape(-1)
    if vector.size != len(terms):
        raise RuntimeError(
            f"TEM {name} returned {vector.size} value(s) for {len(terms)} observable(s)"
        )
    return {term: float(item) for term, item in zip(terms, vector, strict=True)}


def tem_expectations(
    qasm: str,
    terms: tuple[str, ...],
    backend_name: str | None,
    qubit_a: int,
    qubit_b: int,
    transform: str = "none",
    precision: float = 0.1,
    account_name: str = ACCOUNT_NAME,
    instance_crn: str | None = None,
) -> TEMExecutionResult:
    """Run one lazy-loaded Algorithmiq TEM Estimator PUB.

    ``qiskit_ibm_catalog`` is imported only when this function is called, so
    local and direct Runtime modes do not require the optional package.
    """
    if precision <= 0.0:
        raise ValueError("TEM precision must be greater than zero")
    if not terms:
        raise ValueError("TEM requires at least one observable")

    try:
        from qiskit_ibm_catalog import QiskitFunctionsCatalog
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "TEM execution requires the optional qiskit-ibm-catalog package"
        ) from exc

    circuit = transformed_circuit(qasm, transform)
    observables = pair_pauli_observables(
        circuit.num_qubits, qubit_a, qubit_b, terms
    )
    if instance_crn is None:
        # Runtime can select a saved instance by account name, while the
        # Functions catalog requires the selected IBM Cloud instance's CRN.
        from qiskit_ibm_runtime import QiskitRuntimeService

        service = QiskitRuntimeService(name=account_name)
        instance_crn = service.active_instance()
    catalog = QiskitFunctionsCatalog(
        channel="ibm_quantum_platform", instance=instance_crn
    )
    tem = catalog.load(TEM_FUNCTION_NAME)
    run_args = {
        "pubs": [(circuit, observables)],
        "options": {"default_precision": float(precision)},
    }
    if backend_name:
        run_args["backend_name"] = backend_name
    job = tem.run(**run_args)
    job_id_value = getattr(job, "job_id", "")
    job_id = str(job_id_value() if callable(job_id_value) else job_id_value)
    backend = backend_name or "least-busy"
    print(
        f"TEM job submitted: id={job_id} backend={backend} "
        f"observables={len(terms)} precision={precision:g}"
    )

    primitive_result = job.result()
    if len(primitive_result) != 1:
        raise RuntimeError(
            f"TEM returned {len(primitive_result)} PUB results; expected exactly one"
        )
    pub_result = primitive_result[0]
    metadata = dict(getattr(pub_result, "metadata", {}) or {})
    data = getattr(pub_result, "data", None)
    if data is None:
        raise RuntimeError("TEM result is missing its data payload")
    if "evs_non_mitigated" not in metadata or "stds_non_mitigated" not in metadata:
        raise RuntimeError("TEM result is missing its unmitigated reference values")

    return TEMExecutionResult(
        values=_tem_vector("evs", getattr(data, "evs"), terms),
        stds=_tem_vector("stds", getattr(data, "stds"), terms),
        raw_values=_tem_vector(
            "evs_non_mitigated", metadata["evs_non_mitigated"], terms
        ),
        raw_stds=_tem_vector(
            "stds_non_mitigated", metadata["stds_non_mitigated"], terms
        ),
        backend=backend,
        job_id=job_id,
        resource_usage=dict(metadata.get("resource_usage", {}) or {}),
    )


class Transfer:
    def __init__(self, revision: int, total: int):
        self.revision = revision
        self.total = total
        self.chunks: dict[int, str] = {}

    def add(self, index: int, total: int, text: str) -> None:
        if total != self.total or not 0 <= index < self.total:
            raise ValueError("Invalid QASM chunk metadata")
        self.chunks[index] = text

    def assemble(self) -> str:
        missing = [index for index in range(self.total) if index not in self.chunks]
        if missing:
            raise ValueError(f"Incomplete QASM transfer; missing {missing}")
        return unquote("".join(self.chunks[index] for index in range(self.total)))


class WavetableBridge:
    def __init__(self, args: argparse.Namespace):
        self.args = args
        self.client = SimpleUDPClient(args.out_host, args.out_port)
        self.transfer: Transfer | None = None
        self.latest_revision = -1
        self.ibm_in_flight_revision: int | None = None
        self.ibm_jobs_started = 0
        self.transform = args.transform
        self.lock = threading.RLock()
        routes = dispatcher.Dispatcher()
        routes.map("/qmw/qac/begin", self.begin)
        routes.map("/qmw/qac/chunk", self.chunk)
        routes.map("/qmw/qac/end", self.end)
        routes.map("/qmw/qac/qasm", self.qasm)
        routes.map("/qmw/wavetable/ping", self.ping)
        routes.map("/qmw/wavetable/reset", self.reset)
        routes.map("/qmw/wavetable/transform", self.set_transform)
        self.server = osc_server.ThreadingOSCUDPServer((args.in_host, args.in_port), routes)

    def send(self, address: str, value) -> None:
        self.client.send_message(address, value)

    def error(self, message: str) -> None:
        print(f"[wavetable bridge error] {message}")
        self.send("/qmw/wavetable/error", message)

    def send_points(self, revision: int, table: np.ndarray) -> None:
        """Send the stable V3 revision + 256 point OSC payload."""
        points = np.asarray(table, dtype=float).reshape(-1)
        if points.size != TABLE_SIZE:
            raise ValueError(f"Expected {TABLE_SIZE} wavetable points, got {points.size}")
        self.send("/qmw/wavetable/points", [revision, *points.tolist()])

    def publish_qft_spectrum(
        self,
        revision: int,
        source: str,
        transform: str,
        probabilities: np.ndarray,
        magnitudes: np.ndarray,
        phases: np.ndarray | None = None,
    ) -> None:
        """Publish dimensionless transformed-state bins for V5 synthesis."""
        prefix = [revision, source, transform]
        self.send("/qmw/qft/bins", [*prefix, *np.asarray(probabilities, dtype=float).tolist()])
        self.send(
            "/qmw/qft/amplitudes",
            [*prefix, *np.asarray(magnitudes, dtype=float).tolist()],
        )
        if phases is not None:
            self.send(
                "/qmw/qft/phases",
                [*prefix, *np.asarray(phases, dtype=float).tolist()],
            )

        # Compatibility frame for Max: this travels over the correlations
        # route already proven by the V3/V4 patch, avoiding dependence on
        # newly-added OSC address outlets in an open Max patcher.
        probability_values = np.asarray(probabilities, dtype=float).reshape(-1).tolist()
        magnitude_values = np.asarray(magnitudes, dtype=float).reshape(-1).tolist()
        phase_values = (
            np.asarray(phases, dtype=float).reshape(-1).tolist()
            if phases is not None
            else [0.0] * len(probability_values)
        )
        self.send(
            "/qmw/wavetable/correlations",
            [
                revision,
                "qft_frame",
                source,
                transform,
                *probability_values,
                *magnitude_values,
                *phase_values,
            ],
        )

    def set_transform(self, _address: str, value: str) -> None:
        """Select the unitary transform applied to subsequent submissions."""
        transform = str(value).strip().lower()
        if transform not in ("none", "qft", "iqft"):
            self.error(f"Unsupported circuit transform: {value!r}")
            return
        with self.lock:
            if self.ibm_in_flight_revision is not None:
                self.error("Cannot change transform while an IBM job is in flight")
                return
            self.transform = transform
        self.send("/qmw/wavetable/status", ["transform", transform])
        print(f"circuit transform selected: {transform}")

    def begin(self, _address: str, revision: int, total: int) -> None:
        try:
            with self.lock:
                if int(revision) <= self.latest_revision:
                    raise ValueError(f"Stale revision {revision}")
                self.transfer = Transfer(int(revision), int(total))
            self.send("/qmw/wavetable/status", ["receiving", int(revision), int(total)])
        except Exception as exc:
            self.error(str(exc))

    def chunk(self, _address: str, revision: int, index: int, total: int, text: str) -> None:
        try:
            with self.lock:
                if self.transfer is None or self.transfer.revision != int(revision):
                    raise ValueError(f"No transfer for revision {revision}")
                self.transfer.add(int(index), int(total), str(text))
        except Exception as exc:
            self.error(str(exc))

    def end(self, _address: str, revision: int) -> None:
        try:
            with self.lock:
                if self.transfer is None or self.transfer.revision != int(revision):
                    raise ValueError(f"No transfer for revision {revision}")
                qasm = self.transfer.assemble()
                self.transfer = None
            self.submit(int(revision), qasm)
        except Exception as exc:
            self.error(str(exc))

    def qasm(self, _address: str, *args) -> None:
        try:
            if not args:
                raise ValueError("QASM message is empty")
            if isinstance(args[0], int) and len(args) > 1:
                revision, text = int(args[0]), " ".join(map(str, args[1:]))
            else:
                revision, text = int(time.time()), " ".join(map(str, args))
            self.submit(revision, unquote(text))
        except Exception as exc:
            self.error(str(exc))

    def submit(self, revision: int, qasm: str) -> None:
        launch_ibm = self.args.mode in ("ibm", "both")
        ibm_skip_reason = None
        with self.lock:
            if revision <= self.latest_revision:
                raise ValueError(f"Stale revision {revision}")
            if launch_ibm:
                if self.ibm_in_flight_revision is not None:
                    if self.args.mode == "ibm":
                        raise ValueError(
                            f"IBM job for revision {self.ibm_in_flight_revision} is still in flight; "
                            "send ignored to protect quota"
                        )
                    launch_ibm = False
                    ibm_skip_reason = f"job_{self.ibm_in_flight_revision}_in_flight"
                elif self.ibm_jobs_started >= self.args.ibm_max_jobs:
                    if self.args.mode == "ibm":
                        raise ValueError(
                            f"IBM session job limit ({self.args.ibm_max_jobs}) reached; "
                            "restart the bridge for another deliberate submission"
                        )
                    launch_ibm = False
                    ibm_skip_reason = "session_job_limit"
                else:
                    self.ibm_in_flight_revision = revision
                    self.ibm_jobs_started += 1
            self.latest_revision = revision
            transform = self.transform
        if ibm_skip_reason:
            self.send("/qmw/wavetable/status", ["local_only", revision, ibm_skip_reason])
        try:
            if self.args.mode in ("local", "both"):
                if self.args.publish_qft_spectrum:
                    probabilities, magnitudes, phases, _ = local_qft_spectrum(qasm, transform)
                    self.publish_qft_spectrum(
                        revision, "local", transform,
                        probabilities, magnitudes, phases,
                    )
                if self.args.mapping == "pauli15":
                    values, qubits = local_pauli15(
                        qasm, self.args.qubit_a, self.args.qubit_b, transform
                    )
                    self.publish_pauli15(
                        revision, "local", values, qubits, "local-statevector", "none"
                    )
                elif self.args.mapping == "correlations":
                    values, qubits = local_correlations(
                        qasm, self.args.qubit_a, self.args.qubit_b, transform
                    )
                    self.publish_correlations(
                        revision, "local", values, qubits, "local-statevector", "none"
                    )
                else:
                    counts, qubits = local_counts(
                        qasm, self.args.shots, self.args.seed, transform
                    )
                    self.publish(revision, "local", counts, qubits, "local-simulator", "none")
        except Exception:
            with self.lock:
                if launch_ibm and self.ibm_in_flight_revision == revision:
                    self.ibm_in_flight_revision = None
                    self.ibm_jobs_started -= 1
            raise
        if launch_ibm:
            thread = threading.Thread(
                target=self.run_ibm, args=(revision, qasm, transform), daemon=True
            )
            thread.start()

    def run_ibm(self, revision: int, qasm: str, transform: str) -> None:
        try:
            self.send("/qmw/wavetable/status", ["ibm_queued", revision])
            if self.args.ibm_executor == "tem":
                if self.args.mapping == "counts":
                    raise ValueError(
                        "TEM executor supports correlations and pauli15 mappings, not counts"
                    )
                terms = PAULI15 if self.args.mapping == "pauli15" else ("XX", "YY", "ZZ")
                tem_result = tem_expectations(
                    qasm,
                    terms,
                    self.args.backend,
                    self.args.qubit_a,
                    self.args.qubit_b,
                    transform,
                    self.args.tem_precision,
                    self.args.account,
                    self.args.ibm_instance,
                )
                telemetry = [revision, self.args.mapping, tem_result.backend, tem_result.job_id]
                for term in terms:
                    telemetry.extend(
                        [
                            term,
                            tem_result.values[term],
                            tem_result.stds[term],
                            tem_result.raw_values[term],
                            tem_result.raw_stds[term],
                        ]
                    )
                self.send("/qmw/tem/result", telemetry)
                if self.args.mapping == "pauli15":
                    self.publish_pauli15(
                        revision,
                        "ibm",
                        tem_result.values,
                        max(self.args.qubit_a, self.args.qubit_b) + 1,
                        tem_result.backend,
                        tem_result.job_id,
                    )
                else:
                    self.publish_correlations(
                        revision,
                        "ibm",
                        tem_result.values,
                        max(self.args.qubit_a, self.args.qubit_b) + 1,
                        tem_result.backend,
                        tem_result.job_id,
                    )
                comparison = " ".join(
                    f"{term}={tem_result.raw_values[term]:+.3f}->{tem_result.values[term]:+.3f}"
                    for term in terms
                )
                print(f"TEM raw-to-mitigated revision={revision}: {comparison}")
                return
            if self.args.mapping == "pauli15":
                values, backend, job_id = ibm_pauli15(
                    qasm,
                    self.args.shots,
                    self.args.backend,
                    self.args.account,
                    self.args.qubit_a,
                    self.args.qubit_b,
                    transform,
                )
                self.publish_pauli15(
                    revision, "ibm", values,
                    max(self.args.qubit_a, self.args.qubit_b) + 1,
                    backend, job_id,
                )
            elif self.args.mapping == "correlations":
                values, backend, job_id = ibm_correlations(
                    qasm,
                    self.args.shots,
                    self.args.backend,
                    self.args.account,
                    self.args.qubit_a,
                    self.args.qubit_b,
                    transform,
                )
                self.publish_correlations(
                    revision, "ibm", values, max(self.args.qubit_a, self.args.qubit_b) + 1,
                    backend, job_id,
                )
            else:
                counts, backend, job_id = ibm_counts(
                    qasm, self.args.shots, self.args.backend, self.args.account,
                    transform,
                )
                width = max(len(label.replace(" ", "")) for label in counts)
                if self.args.publish_qft_spectrum:
                    ordered = np.zeros(1 << width, dtype=float)
                    shots = float(sum(counts.values()))
                    for label, count in counts.items():
                        ordered[int(label.replace(" ", ""), 2)] = float(count) / shots
                    self.publish_qft_spectrum(
                        revision, "ibm", transform, ordered, np.sqrt(ordered)
                    )
                self.publish(revision, "ibm", counts, width, backend, job_id)
        except Exception as exc:
            self.error(f"IBM job {revision}: {exc}")
        finally:
            with self.lock:
                if self.ibm_in_flight_revision == revision:
                    self.ibm_in_flight_revision = None

    def publish(
        self,
        revision: int,
        source: str,
        counts: dict[str, int],
        qubits: int,
        backend: str,
        job_id: str,
    ) -> None:
        table = counts_to_wavetable(counts)
        output = self.args.output_dir / f"wavetable_{revision}_{source}.wav"
        write_wav(output, table)
        flat_counts = []
        for label, count in sorted(counts.items()):
            flat_counts.extend([label, int(count)])
        self.send("/qmw/wavetable/begin", [revision, source, TABLE_SIZE, qubits, self.args.shots])
        self.send_points(revision, table)
        self.send("/qmw/wavetable/counts", [revision, *flat_counts])
        self.send("/qmw/wavetable/end", [revision, source, backend, job_id])
        print(f"published revision={revision} source={source} backend={backend} wav={output}")

    def publish_correlations(
        self,
        revision: int,
        source: str,
        correlations: dict[str, float],
        qubits: int,
        backend: str,
        job_id: str,
    ) -> None:
        table = correlations_to_wavetable(correlations)
        output = self.args.output_dir / f"wavetable_{revision}_{source}_correlations.wav"
        write_wav(output, table)
        values = [float(correlations[axis]) for axis in ("XX", "YY", "ZZ")]
        self.send("/qmw/wavetable/begin", [revision, source, TABLE_SIZE, qubits, self.args.shots])
        self.send_points(revision, table)
        self.send("/qmw/wavetable/correlations", [revision, *values])
        self.send("/qmw/wavetable/end", [revision, source, backend, job_id])
        print(
            f"published correlation revision={revision} source={source} backend={backend} "
            f"XX={values[0]:+.3f} YY={values[1]:+.3f} ZZ={values[2]:+.3f} wav={output}"
        )

    def publish_pauli15(
        self,
        revision: int,
        source: str,
        values: dict[str, float],
        qubits: int,
        backend: str,
        job_id: str,
    ) -> None:
        rows = pauli15_surface(values)
        output = self.args.output_dir / f"wavetable_{revision}_{source}_pauli15.wav"
        surface_output = self.args.output_dir / f"pauli_surface_{revision}_{source}_4x256.wav"
        polarization, entanglement, correlation_rms, entropy = pauli15_quantum_features(values)
        coefficients = [float(values[t]) for t in PAULI15]
        # V3 compact protocol: state descriptors, never rendered waveforms.
        self.send(
            "/qmw/quantum/state",
            [revision, source, *coefficients, polarization, entanglement, correlation_rms, entropy],
        )
        density_lines = density_hamiltonian_transitions(values)
        self.send(
            "/qmw/workshop/density_lines",
            [revision, source, *[item for line in density_lines for item in line]],
        )
        if not self.args.compact_state:
            write_wav(output, rows[3])
            write_wav(surface_output, rows.reshape(-1))
            self.send("/qmw/wavetable/begin", [revision, source, TABLE_SIZE, qubits, self.args.shots])
            self.send_points(revision, rows[3])
            self.send("/qmw/wavetable/pauli15", [revision, *coefficients])
            self.send("/qmw/wavetable/surface_file", [revision, str(surface_output.resolve())])
            self.send("/qmw/wavetable/end", [revision, source, backend, job_id])
        self.send(
            "/qmw/quantum/features",
            [revision, polarization, entanglement, correlation_rms, entropy],
        )
        active = " ".join(f"{term}={values[term]:+.2f}" for term in PAULI15 if abs(values[term]) > 1e-6)
        print(
            f"published Pauli-15 revision={revision} source={source} backend={backend} "
            f"active=[{active}] "
            f"polarization={polarization:+.3f} entanglement={entanglement:.3f} "
            f"correlation_rms={correlation_rms:.3f} entropy={entropy:.3f} "
            f"transport={'compact-state' if self.args.compact_state else 'waveform+state'}"
        )

    def ping(self, _address: str, *_args) -> None:
        self.send(
            "/qmw/wavetable/status",
            ["ready", self.args.mode, self.transform, self.latest_revision],
        )

    def reset(self, _address: str, *_args) -> None:
        """Forget transfer/revision state without touching credentials or files."""
        with self.lock:
            self.transfer = None
            self.latest_revision = -1
        self.send("/qmw/wavetable/status", ["reset", self.args.mode, -1])
        print("wavetable bridge revision state reset")

    def serve(self) -> None:
        print(f"QAC QASM in: udp://{self.args.in_host}:{self.args.in_port}")
        print(f"Wavetable out: udp://{self.args.out_host}:{self.args.out_port}")
        print(f"Mode: {self.args.mode}; shots: {self.args.shots}; backend: {self.args.backend or 'least_busy'}")
        print(
            f"IBM executor: {self.args.ibm_executor}"
            + (
                f"; TEM precision: {self.args.tem_precision:g}"
                if self.args.ibm_executor == "tem"
                else ""
            )
        )
        print(f"Circuit transform: {self.transform}")
        print(
            f"Mapping: {self.args.mapping}; correlation pair: "
            f"q{self.args.qubit_a},q{self.args.qubit_b}"
        )
        self.server.serve_forever()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("local", "ibm", "both"), default="local")
    parser.add_argument(
        "--confirm-ibm",
        action="store_true",
        help="required acknowledgement before ibm or both mode can submit hardware jobs",
    )
    parser.add_argument("--in-host", default="127.0.0.1")
    parser.add_argument("--in-port", type=int, default=7411)
    parser.add_argument("--out-host", default="127.0.0.1")
    parser.add_argument("--out-port", type=int, default=7412)
    parser.add_argument("--shots", type=int, default=256)
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--backend", help="IBM backend name; default selects least busy")
    parser.add_argument(
        "--ibm-executor",
        choices=("runtime", "tem"),
        default="runtime",
        help="direct Qiskit Runtime Sampler or Algorithmiq TEM function",
    )
    parser.add_argument(
        "--tem-precision",
        type=float,
        default=0.1,
        help="target TEM expectation precision (default: 0.1)",
    )
    parser.add_argument(
        "--ibm-max-jobs", type=int, default=1,
        help="maximum IBM submissions during this bridge process (default: 1)",
    )
    parser.add_argument("--account", default=ACCOUNT_NAME)
    parser.add_argument(
        "--ibm-instance",
        help="IBM Cloud instance CRN for Functions; default resolves the active saved instance",
    )
    parser.add_argument("--mapping", choices=("counts", "correlations", "pauli15"), default="counts")
    parser.add_argument(
        "--transform", choices=("none", "qft", "iqft"), default="none",
        help="append QFT or inverse QFT after QAC state preparation and before measurement",
    )
    parser.add_argument(
        "--compact-state", action="store_true",
        help="publish Pauli descriptors without WAV files or 256-point OSC arrays (V3)",
    )
    parser.add_argument(
        "--publish-qft-spectrum", action="store_true",
        help="publish full transformed-state bins, amplitudes, and local phases for V5",
    )
    parser.add_argument("--qubit-a", type=int, default=0)
    parser.add_argument("--qubit-b", type=int, default=1)
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).parent / "generated_audio")
    parser.add_argument("--qasm", type=Path, help="render one QASM locally and exit")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    if args.mode in ("ibm", "both") and not args.confirm_ibm:
        raise SystemExit(
            "IBM mode requires --confirm-ibm. Use --mode local for quota-free rehearsal."
        )
    if args.tem_precision <= 0.0:
        raise SystemExit("--tem-precision must be greater than zero")
    if (
        args.mode in ("ibm", "both")
        and args.ibm_executor == "tem"
        and args.mapping == "counts"
    ):
        raise SystemExit(
            "TEM executor supports --mapping correlations or pauli15, not counts"
        )
    if args.qasm:
        text = args.qasm.read_text(encoding="utf-8")
        output = args.output_dir / (
            f"wavetable_{args.qasm.stem}_local_{args.mapping}_{args.transform}.wav"
        )
        if args.mapping == "pauli15":
            values, qubits = local_pauli15(text, args.qubit_a, args.qubit_b, args.transform)
            rows = pauli15_surface(values)
            write_wav(output, rows[3])
            print(f"qubits={qubits} pauli15={values}")
        elif args.mapping == "correlations":
            values, qubits = local_correlations(text, args.qubit_a, args.qubit_b, args.transform)
            write_wav(output, correlations_to_wavetable(values))
            print(f"qubits={qubits} correlations={values}")
        else:
            counts, qubits = local_counts(text, args.shots, args.seed, args.transform)
            write_wav(output, counts_to_wavetable(counts))
            print(f"qubits={qubits} counts={counts}")
        return
    if args.ibm_max_jobs < 1:
        raise SystemExit("--ibm-max-jobs must be at least 1")
    try:
        WavetableBridge(args).serve()
    except KeyboardInterrupt:
        print("\nbridge stopped")


if __name__ == "__main__":
    main()
