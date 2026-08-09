"""Shared four-qubit temporal primitives for the Quantum Material Workstation.

The canonical live state is always a 16 x 16 density matrix.  Clock registers,
history records, and temporal analyses are separate objects.  NumPy is used as
the reference backend so the module can validate MLX and Qiskit integrations
without making either package a runtime requirement.

QMW bit ordering is preserved:

    integer basis index = q0 + 2*q1 + 4*q2 + 8*q3
    ket display order   = |q3 q2 q1 q0>

Python wall time is deliberately absent from the dynamics.  A caller supplies
a logical tick and fixed simulation interval.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from typing import Any, Deque, Iterable, Mapping, Sequence

import numpy as np

N_QUBITS = 4
DIM = 1 << N_QUBITS

I2 = np.eye(2, dtype=np.complex128)
X = np.array([[0, 1], [1, 0]], dtype=np.complex128)
Y = np.array([[0, -1j], [1j, 0]], dtype=np.complex128)
Z = np.array([[1, 0], [0, -1]], dtype=np.complex128)


def as_complex_matrix(value: Any, *, dim: int = DIM) -> np.ndarray:
    """Convert NumPy/MLX-like input to a copied square complex matrix."""

    array = np.asarray(value, dtype=np.complex128)
    if array.shape != (dim, dim):
        raise ValueError(f"expected shape {(dim, dim)}, received {array.shape}")
    return np.array(array, copy=True)


def as_statevector(value: Any, *, dim: int = DIM) -> np.ndarray:
    """Return a normalized complex statevector."""

    state = np.asarray(value, dtype=np.complex128).reshape(-1)
    if state.shape != (dim,):
        raise ValueError(f"expected {dim} amplitudes, received {state.shape}")
    norm = float(np.linalg.norm(state))
    if norm <= 0.0:
        raise ValueError("statevector norm must be positive")
    return np.array(state / norm, copy=True)


def computational_basis_state(index: int, *, dim: int = DIM) -> np.ndarray:
    if not 0 <= int(index) < dim:
        raise ValueError(f"basis index must be in [0, {dim - 1}]")
    state = np.zeros(dim, dtype=np.complex128)
    state[int(index)] = 1.0
    return state


def density_from_state(state: Any) -> np.ndarray:
    psi = as_statevector(state)
    return np.outer(psi, psi.conj())


def maximally_mixed(*, dim: int = DIM) -> np.ndarray:
    return np.eye(dim, dtype=np.complex128) / float(dim)


def operator_on_qubit(operator: Any, qubit: int) -> np.ndarray:
    """Embed a single-qubit operator with q0 as the least-significant bit."""

    if not 0 <= int(qubit) < N_QUBITS:
        raise ValueError(f"qubit must be in [0, {N_QUBITS - 1}]")
    local = np.asarray(operator, dtype=np.complex128)
    if local.shape != (2, 2):
        raise ValueError("single-qubit operator must have shape (2, 2)")

    # Kronecker factors are written in display order |q3 q2 q1 q0>.
    result = np.array([[1.0 + 0.0j]])
    for q in reversed(range(N_QUBITS)):
        result = np.kron(result, local if q == qubit else I2)
    return result


def pauli_string(letters: str) -> np.ndarray:
    """Build a Pauli string written in display order q3 q2 q1 q0."""

    cleaned = letters.replace(" ", "").upper()
    if len(cleaned) != N_QUBITS:
        raise ValueError(f"Pauli string must contain {N_QUBITS} letters")
    table = {"I": I2, "X": X, "Y": Y, "Z": Z}
    result = np.array([[1.0 + 0.0j]])
    for letter in cleaned:
        try:
            result = np.kron(result, table[letter])
        except KeyError as exc:
            raise ValueError(f"unsupported Pauli letter {letter!r}") from exc
    return result


def two_qubit_product(
    first_operator: Any,
    first_qubit: int,
    second_operator: Any,
    second_qubit: int,
) -> np.ndarray:
    if first_qubit == second_qubit:
        raise ValueError("two-qubit product requires distinct qubits")
    return operator_on_qubit(first_operator, first_qubit) @ operator_on_qubit(
        second_operator, second_qubit
    )


def hermitian_unitary(hamiltonian: Any, duration: float = 1.0) -> np.ndarray:
    """Compute exp(-i H duration) using a Hermitian eigendecomposition."""

    matrix = as_complex_matrix(hamiltonian)
    if not np.allclose(matrix, matrix.conj().T, atol=1e-10):
        raise ValueError("Hamiltonian must be Hermitian")
    eigenvalues, eigenvectors = np.linalg.eigh(matrix)
    phases = np.exp(-1j * float(duration) * eigenvalues)
    return (eigenvectors * phases) @ eigenvectors.conj().T


def evolve_unitary(rho: Any, unitary: Any) -> np.ndarray:
    matrix = as_complex_matrix(rho)
    u = as_complex_matrix(unitary)
    return u @ matrix @ u.conj().T


def expectation(rho: Any, operator: Any) -> complex:
    matrix = as_complex_matrix(rho)
    observable = as_complex_matrix(operator)
    return complex(np.trace(matrix @ observable))


def purity(rho: Any) -> float:
    matrix = as_complex_matrix(rho)
    return float(np.real(np.trace(matrix @ matrix)))


def l1_coherence(rho: Any) -> float:
    matrix = as_complex_matrix(rho)
    return float(np.sum(np.abs(matrix)) - np.sum(np.abs(np.diag(matrix))))


def von_neumann_entropy(rho: Any, *, epsilon: float = 1e-15) -> float:
    matrix = as_complex_matrix(rho)
    eigenvalues = np.linalg.eigvalsh((matrix + matrix.conj().T) * 0.5)
    probabilities = np.clip(np.real(eigenvalues), 0.0, 1.0)
    nonzero = probabilities[probabilities > epsilon]
    return float(-np.sum(nonzero * np.log2(nonzero)))


def trace_distance(rho_a: Any, rho_b: Any) -> float:
    """Trace distance 1/2 ||rho_a-rho_b||_1 for Hermitian inputs."""

    delta = as_complex_matrix(rho_a) - as_complex_matrix(rho_b)
    delta = (delta + delta.conj().T) * 0.5
    return float(0.5 * np.sum(np.abs(np.linalg.eigvalsh(delta))))


@dataclass(frozen=True)
class DensityValidation:
    valid: bool
    shape_ok: bool
    hermiticity_error: float
    trace_error: float
    minimum_eigenvalue: float
    maximum_eigenvalue: float
    positivity_tolerance: float


def validate_density_matrix(
    rho: Any,
    *,
    dim: int = DIM,
    atol: float = 1e-9,
    positivity_tolerance: float = 1e-9,
    raise_on_error: bool = False,
) -> DensityValidation:
    array = np.asarray(rho, dtype=np.complex128)
    shape_ok = array.shape == (dim, dim)
    if not shape_ok:
        report = DensityValidation(
            valid=False,
            shape_ok=False,
            hermiticity_error=float("inf"),
            trace_error=float("inf"),
            minimum_eigenvalue=float("-inf"),
            maximum_eigenvalue=float("inf"),
            positivity_tolerance=positivity_tolerance,
        )
    else:
        hermiticity_error = float(np.max(np.abs(array - array.conj().T)))
        trace_error = float(abs(np.trace(array) - 1.0))
        hermitian = (array + array.conj().T) * 0.5
        eigenvalues = np.linalg.eigvalsh(hermitian)
        minimum = float(np.min(np.real(eigenvalues)))
        maximum = float(np.max(np.real(eigenvalues)))
        valid = (
            hermiticity_error <= atol
            and trace_error <= atol
            and minimum >= -positivity_tolerance
        )
        report = DensityValidation(
            valid=valid,
            shape_ok=True,
            hermiticity_error=hermiticity_error,
            trace_error=trace_error,
            minimum_eigenvalue=minimum,
            maximum_eigenvalue=maximum,
            positivity_tolerance=positivity_tolerance,
        )

    if raise_on_error and not report.valid:
        raise ValueError(f"invalid density matrix: {report}")
    return report


@dataclass(frozen=True)
class BasisClockSnapshot:
    tick: int
    index: int
    page: int
    cycle: int
    phase_radians: float


class BasisClock16:
    """Logical 16-position clock; independent of Python wall time."""

    size = DIM

    def __init__(self, tick: int = 0):
        self._tick = int(tick)

    @property
    def tick(self) -> int:
        return self._tick

    def snapshot(self) -> BasisClockSnapshot:
        tick = self._tick
        return BasisClockSnapshot(
            tick=tick,
            index=tick % self.size,
            page=tick // self.size,
            cycle=(tick // self.size),
            phase_radians=2.0 * np.pi * (tick % self.size) / self.size,
        )

    def advance(self, steps: int = 1) -> BasisClockSnapshot:
        self._tick += int(steps)
        return self.snapshot()

    def reset(self, tick: int = 0) -> BasisClockSnapshot:
        self._tick = int(tick)
        return self.snapshot()


@dataclass(frozen=True)
class ClockFrame:
    tick: int
    simulation_time: float
    revision: int
    rho: np.ndarray = field(repr=False)
    protocol: str = "observer"
    clock: Mapping[str, Any] = field(default_factory=dict)
    events: tuple[Mapping[str, Any], ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        matrix = as_complex_matrix(self.rho)
        matrix.setflags(write=False)
        object.__setattr__(self, "rho", matrix)


class RevisionedDensityState:
    """Single-writer state store for the canonical 16 x 16 rho."""

    def __init__(self, rho: Any, *, revision: int = 0):
        matrix = as_complex_matrix(rho)
        validate_density_matrix(matrix, raise_on_error=True)
        self._rho = matrix
        self._revision = int(revision)

    @property
    def revision(self) -> int:
        return self._revision

    def read(self) -> np.ndarray:
        return np.array(self._rho, copy=True)

    def commit(self, rho: Any, *, expected_revision: int | None = None) -> int:
        if expected_revision is not None and expected_revision != self._revision:
            raise RuntimeError(
                f"stale state revision {expected_revision}; "
                f"current revision is {self._revision}"
            )
        matrix = as_complex_matrix(rho)
        validate_density_matrix(matrix, raise_on_error=True)
        self._rho = matrix
        self._revision += 1
        return self._revision


class HistoryBank:
    """Bounded classical history of density snapshots.

    This record supports trajectory and temporal-spectrum analysis.  It does not
    claim to contain the cross-time coherences of a Page-Wootters history state.
    """

    def __init__(self, capacity: int = 240):
        if int(capacity) <= 0:
            raise ValueError("history capacity must be positive")
        self.capacity = int(capacity)
        self._frames: Deque[ClockFrame] = deque(maxlen=self.capacity)

    def __len__(self) -> int:
        return len(self._frames)

    def append(self, frame: ClockFrame) -> None:
        self._frames.append(frame)

    def frames(self) -> tuple[ClockFrame, ...]:
        return tuple(self._frames)

    def latest(self) -> ClockFrame:
        if not self._frames:
            raise IndexError("history is empty")
        return self._frames[-1]

    def observable_series(self, operator: Any) -> np.ndarray:
        observable = as_complex_matrix(operator)
        return np.asarray(
            [expectation(frame.rho, observable) for frame in self._frames],
            dtype=np.complex128,
        )

    def temporal_spectrum(
        self,
        operator: Any,
        *,
        remove_mean: bool = False,
    ) -> tuple[np.ndarray, np.ndarray]:
        values = self.observable_series(operator)
        if values.size == 0:
            return np.array([], dtype=float), np.array([], dtype=np.complex128)
        if remove_mean:
            values = values - np.mean(values)
        spectrum = np.fft.fft(values) / values.size
        frequencies = np.fft.fftfreq(values.size, d=1.0)
        return frequencies, spectrum


def qft_matrix(size: int) -> np.ndarray:
    if int(size) <= 0:
        raise ValueError("QFT size must be positive")
    n = int(size)
    rows = np.arange(n)[:, None]
    columns = np.arange(n)[None, :]
    return np.exp(2j * np.pi * rows * columns / n) / np.sqrt(n)


def least_common_multiple(values: Iterable[int]) -> int:
    result = 1
    for value in values:
        integer = abs(int(value))
        if integer == 0:
            raise ValueError("LCM arguments must be nonzero")
        result = int(np.lcm(result, integer))
    return result


def flatten_complex_matrix(rho: Any) -> tuple[list[float], list[float]]:
    matrix = as_complex_matrix(rho)
    return (
        np.real(matrix).reshape(-1).astype(float).tolist(),
        np.imag(matrix).reshape(-1).astype(float).tolist(),
    )


def metadata_copy(mapping: Mapping[str, Any] | None) -> dict[str, Any]:
    return dict(mapping or {})

