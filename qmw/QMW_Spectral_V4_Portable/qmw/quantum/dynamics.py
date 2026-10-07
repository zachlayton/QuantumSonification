"""Authoritative finite-dimensional density-matrix dynamics for QMW.

This module is deliberately upstream of projection, geometry, OSC, and sound.
``QuantumFrame`` is one synchronized observation of the evolving density
operator.  Pauli coordinates and Hilbert-basis current are independent,
read-only projections of the same ``(H, rho)`` pair; the latter is *not*
claimed to be a spatial current.

Measurement is intentionally absent here.  It is a discrete intervention on a
state, not a term in the continuous derivative represented by this kernel.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Iterable, Sequence

import numpy as np

from .hilbert_current import hermitian_matrix
from .pauli_basis import pauli_basis, pauli_matrix
from .pauli_decompose import PauliTerm, pauli_decomposition


Array = np.ndarray
_EPS = 1.0e-10


def _readonly(values: object, *, dtype: object = np.complex128) -> Array:
    result = np.array(values, dtype=dtype, copy=True)
    result.flags.writeable = False
    return result


def _density_matrix(values: object, *, tolerance: float = _EPS) -> Array:
    """Validate a finite, Hermitian, unit-trace positive semidefinite matrix."""

    density = hermitian_matrix("rho", values, tolerance=tolerance)
    trace = complex(np.trace(density))
    if abs(trace.imag) > tolerance or not np.isclose(trace.real, 1.0, atol=tolerance, rtol=0.0):
        raise ValueError("rho must have unit trace.")
    if float(np.min(np.linalg.eigvalsh(density))) < -tolerance:
        raise ValueError("rho must be positive semidefinite.")
    return density


def density_from_state(state: object, *, tolerance: float = _EPS) -> Array:
    """Return the normalized pure-state density operator ``|psi><psi|``."""

    vector = np.asarray(state, dtype=np.complex128)
    if vector.ndim != 1 or vector.size < 2 or not np.all(np.isfinite(vector)):
        raise ValueError("state must be a finite nontrivial vector.")
    norm = float(np.vdot(vector, vector).real)
    if not math.isfinite(norm) or norm <= tolerance:
        raise ValueError("state must have nonzero norm.")
    normalized = vector / math.sqrt(norm)
    return _density_matrix(np.outer(normalized, normalized.conj()), tolerance=tolerance)


@dataclass(frozen=True)
class LindbladChannel:
    """One physical GKSL channel ``rate * D[operator](rho)``.

    The channel is part of the continuous open-system generator.  It is not a
    sound-design noise source and it does not perform a measurement.
    """

    operator: Array
    rate: float = 1.0
    label: str = "lindblad"

    def __post_init__(self) -> None:
        operator = np.asarray(self.operator, dtype=np.complex128)
        if operator.ndim != 2 or operator.shape[0] != operator.shape[1] or operator.shape[0] < 2:
            raise ValueError("Lindblad operator must be a square matrix with dimension >= 2.")
        if not np.all(np.isfinite(operator)):
            raise ValueError("Lindblad operator must be finite.")
        if not math.isfinite(float(self.rate)) or self.rate < 0.0:
            raise ValueError("Lindblad rate must be finite and nonnegative.")
        if not str(self.label):
            raise ValueError("Lindblad label must be nonempty.")
        object.__setattr__(self, "operator", _readonly(operator))
        object.__setattr__(self, "rate", float(self.rate))
        object.__setattr__(self, "label", str(self.label))


def lindblad_dissipator(rho: object, channels: Iterable[LindbladChannel] = ()) -> Array:
    """Return the GKSL dissipative derivative for the declared channels."""

    density = _density_matrix(rho)
    derivative = np.zeros_like(density)
    for channel in tuple(channels):
        if not isinstance(channel, LindbladChannel):
            raise TypeError("channels must contain LindbladChannel values.")
        if channel.operator.shape != density.shape:
            raise ValueError("every Lindblad operator must match rho.")
        adjoint = channel.operator.conj().T
        number = adjoint @ channel.operator
        derivative += channel.rate * (
            channel.operator @ density @ adjoint
            - 0.5 * (number @ density + density @ number)
        )
    return _readonly((derivative + derivative.conj().T) * 0.5)


@dataclass(frozen=True)
class Hamiltonian:
    """A Hermitian finite-dimensional generator with an exact closed propagator."""

    matrix: Array
    hbar: float = 1.0
    label: str = "hamiltonian"

    def __post_init__(self) -> None:
        matrix = hermitian_matrix("hamiltonian", self.matrix)
        if matrix.shape[0] & (matrix.shape[0] - 1):
            raise ValueError("Hamiltonian dimension must be a power of two.")
        if not math.isfinite(float(self.hbar)) or self.hbar <= 0.0:
            raise ValueError("hbar must be finite and positive.")
        if not str(self.label):
            raise ValueError("Hamiltonian label must be nonempty.")
        object.__setattr__(self, "matrix", _readonly(matrix))
        object.__setattr__(self, "hbar", float(self.hbar))
        object.__setattr__(self, "label", str(self.label))

    @property
    def dimension(self) -> int:
        return int(self.matrix.shape[0])

    @property
    def qubits(self) -> int:
        return self.dimension.bit_length() - 1

    @property
    def pauli_terms(self) -> tuple[PauliTerm, ...]:
        return pauli_decomposition(self.matrix)

    def commutator(self, rho: object) -> Array:
        density = _density_matrix(rho)
        if density.shape != self.matrix.shape:
            raise ValueError("rho must match the Hamiltonian dimension.")
        return _readonly(self.matrix @ density - density @ self.matrix)

    def unitary_derivative(self, rho: object) -> Array:
        return _readonly((-1j / self.hbar) * self.commutator(rho))

    def propagator(self, duration: float) -> Array:
        elapsed = float(duration)
        if not math.isfinite(elapsed) or elapsed < 0.0:
            raise ValueError("duration must be finite and nonnegative.")
        eigenvalues, eigenvectors = np.linalg.eigh(self.matrix)
        result = (eigenvectors * np.exp(-1j * eigenvalues * elapsed / self.hbar)) @ eigenvectors.conj().T
        return _readonly(result)

    def evolve_unitary(self, rho: object, duration: float) -> Array:
        density = _density_matrix(rho)
        if density.shape != self.matrix.shape:
            raise ValueError("rho must match the Hamiltonian dimension.")
        unitary = self.propagator(duration)
        evolved = unitary @ density @ unitary.conj().T
        return _readonly(_density_matrix((evolved + evolved.conj().T) * 0.5))


def basis_current_inflow(rho: object, hamiltonian: Hamiltonian | object, *, hbar: float | None = None) -> Array:
    """Return ``J[i, j] = J_{i <- j}`` for unitary Hilbert-basis flow.

    ``J[i, j] = (2 / hbar) Im(H[i, j] rho[j, i])`` is antisymmetric and
    satisfies ``d rho[i, i] / dt = sum_j J[i, j]``.  It belongs to the
    declared computational basis, not to physical configuration space.
    """

    generator = hamiltonian if isinstance(hamiltonian, Hamiltonian) else Hamiltonian(hamiltonian)
    effective_hbar = generator.hbar if hbar is None else float(hbar)
    if not math.isfinite(effective_hbar) or effective_hbar <= 0.0:
        raise ValueError("hbar must be finite and positive.")
    density = _density_matrix(rho)
    if density.shape != generator.matrix.shape:
        raise ValueError("rho and hamiltonian must share a shape.")
    result = (2.0 / effective_hbar) * np.imag(generator.matrix * density.T)
    np.fill_diagonal(result, 0.0)
    return _readonly(result, dtype=float)


def pauli_coordinate_values(operator: object, *, qubits: int | None = None) -> tuple[tuple[str, ...], Array]:
    """Return all Pauli coordinates, including the identity coordinate."""

    matrix = np.asarray(operator, dtype=np.complex128)
    if matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1] or matrix.shape[0] < 2:
        raise ValueError("operator must be a nontrivial square matrix.")
    dimension = matrix.shape[0]
    inferred_qubits = dimension.bit_length() - 1
    if dimension != 2**inferred_qubits:
        raise ValueError("operator dimension must be a power of two.")
    if qubits is not None and int(qubits) != inferred_qubits:
        raise ValueError("qubits does not match the operator dimension.")
    labels_and_operators = pauli_basis(inferred_qubits, include_identity=True)
    values = np.empty(len(labels_and_operators), dtype=np.complex128)
    for index, (_, pauli) in enumerate(labels_and_operators):
        values[index] = np.trace(matrix @ pauli)
    if np.max(np.abs(values.imag), initial=0.0) > _EPS:
        raise ValueError("a Hermitian operator had unexpectedly complex Pauli coordinates.")
    return tuple(label for label, _ in labels_and_operators), _readonly(values.real, dtype=float)


def reconstruct_density_from_pauli(labels: Sequence[str], values: object) -> Array:
    """Reconstruct a density operator from its complete Pauli coordinates."""

    names = tuple(str(label) for label in labels)
    coordinates = np.asarray(values, dtype=float)
    if not names or coordinates.shape != (len(names),) or not np.all(np.isfinite(coordinates)):
        raise ValueError("labels and finite one-dimensional values must have the same nonzero length.")
    qubits = len(names[0])
    expected = tuple(label for label, _ in pauli_basis(qubits, include_identity=True))
    if names != expected:
        raise ValueError("labels must be the complete canonical Pauli basis including identity.")
    dimension = 2**qubits
    result = np.zeros((dimension, dimension), dtype=np.complex128)
    for label, value in zip(names, coordinates):
        result += value * pauli_matrix(label)
    return _readonly((result + result.conj().T) / (2.0 * dimension))


def conserved_pauli_labels(hamiltonian: Hamiltonian | object, *, tolerance: float = _EPS) -> tuple[str, ...]:
    """Return canonical Pauli observables commuting with the Hamiltonian."""

    generator = hamiltonian if isinstance(hamiltonian, Hamiltonian) else Hamiltonian(hamiltonian)
    if not math.isfinite(float(tolerance)) or tolerance <= 0.0:
        raise ValueError("tolerance must be finite and positive.")
    return tuple(
        label
        for label, pauli in pauli_basis(generator.qubits, include_identity=True)
        if np.linalg.norm(generator.matrix @ pauli - pauli @ generator.matrix, ord="fro") <= tolerance
    )


def energy_expectation(rho: object, hamiltonian: Hamiltonian | object) -> float:
    generator = hamiltonian if isinstance(hamiltonian, Hamiltonian) else Hamiltonian(hamiltonian)
    density = _density_matrix(rho)
    if density.shape != generator.matrix.shape:
        raise ValueError("rho and hamiltonian must share a shape.")
    value = complex(np.trace(density @ generator.matrix))
    if abs(value.imag) > _EPS:
        raise ValueError("Hamiltonian expectation was unexpectedly complex.")
    return float(value.real)


def energy_variance(rho: object, hamiltonian: Hamiltonian | object) -> float:
    generator = hamiltonian if isinstance(hamiltonian, Hamiltonian) else Hamiltonian(hamiltonian)
    density = _density_matrix(rho)
    average = energy_expectation(density, generator)
    second = complex(np.trace(density @ generator.matrix @ generator.matrix))
    if abs(second.imag) > _EPS:
        raise ValueError("Hamiltonian second moment was unexpectedly complex.")
    return float(max(0.0, second.real - average * average))


@dataclass(frozen=True)
class PauliCoordinates:
    """Complete operator-space coordinates and split continuous velocities."""

    labels: tuple[str, ...]
    values: Array
    unitary_velocity: Array
    dissipative_velocity: Array

    @property
    def velocity(self) -> Array:
        return _readonly(self.unitary_velocity + self.dissipative_velocity, dtype=float)

    def value(self, label: str) -> float:
        return float(self.values[self.labels.index(str(label).upper())])

    def derivative(self, label: str) -> float:
        return float(self.velocity[self.labels.index(str(label).upper())])

    def reconstruct(self) -> Array:
        return reconstruct_density_from_pauli(self.labels, self.values)


@dataclass(frozen=True)
class QuantumFrame:
    """One complete, immutable instant of authoritative density dynamics.

    The unitary current is defined only for ``rho_dot_unitary``.  A Lindblad
    contribution is retained as its own population-rate channel rather than
    being mislabeled as a Hamiltonian basis current.
    """

    time: float
    frame_index: int
    hamiltonian: Hamiltonian
    rho: Array
    commutator: Array
    rho_dot_unitary: Array
    rho_dot_dissipative: Array
    pauli: PauliCoordinates
    populations: Array
    population_rate_unitary: Array
    population_rate_dissipative: Array
    basis_current_inflow: Array
    channels: tuple[LindbladChannel, ...] = ()
    provenance: str = "authoritative_density_matrix_dynamics_v1"

    @property
    def rho_dot(self) -> Array:
        return _readonly(self.rho_dot_unitary + self.rho_dot_dissipative)

    @property
    def population_rate(self) -> Array:
        return _readonly(self.population_rate_unitary + self.population_rate_dissipative, dtype=float)

    @property
    def trace(self) -> float:
        return float(np.trace(self.rho).real)

    @property
    def purity(self) -> float:
        return float(np.trace(self.rho @ self.rho).real)

    @property
    def minimum_eigenvalue(self) -> float:
        return float(np.min(np.linalg.eigvalsh(self.rho)))

    @property
    def hermiticity_error(self) -> float:
        return float(np.max(np.abs(self.rho - self.rho.conj().T)))

    @property
    def commutator_norm(self) -> float:
        return float(np.linalg.norm(self.commutator, ord="fro"))

    @property
    def energy(self) -> float:
        return energy_expectation(self.rho, self.hamiltonian)

    @classmethod
    def observe(
        cls,
        *,
        time: float,
        frame_index: int,
        hamiltonian: Hamiltonian | object,
        rho: object,
        channels: Iterable[LindbladChannel] = (),
    ) -> "QuantumFrame":
        if not math.isfinite(float(time)):
            raise ValueError("time must be finite.")
        if int(frame_index) != frame_index or frame_index < 0:
            raise ValueError("frame_index must be a nonnegative integer.")
        generator = hamiltonian if isinstance(hamiltonian, Hamiltonian) else Hamiltonian(hamiltonian)
        density = _density_matrix(rho)
        if density.shape != generator.matrix.shape:
            raise ValueError("rho and hamiltonian must share a shape.")
        declared_channels = tuple(channels)
        unitary = generator.unitary_derivative(density)
        dissipative = lindblad_dissipator(density, declared_channels)
        labels, values = pauli_coordinate_values(density)
        derivative_labels, unitary_values = pauli_coordinate_values(unitary)
        dissipative_labels, dissipative_values = pauli_coordinate_values(dissipative)
        if labels != derivative_labels or labels != dissipative_labels:
            raise RuntimeError("Pauli coordinate bases did not agree.")
        population_unitary = np.real(np.diag(unitary))
        population_dissipative = np.real(np.diag(dissipative))
        return cls(
            time=float(time), frame_index=int(frame_index), hamiltonian=generator,
            rho=_readonly(density), commutator=generator.commutator(density),
            rho_dot_unitary=unitary, rho_dot_dissipative=dissipative,
            pauli=PauliCoordinates(labels, values, unitary_values, dissipative_values),
            populations=_readonly(np.real(np.diag(density)), dtype=float),
            population_rate_unitary=_readonly(population_unitary, dtype=float),
            population_rate_dissipative=_readonly(population_dissipative, dtype=float),
            basis_current_inflow=basis_current_inflow(density, generator),
            channels=declared_channels,
        )


def von_neumann_flow_i_hamiltonian(
    omega_1: float = 1.17,
    omega_2: float = 0.73,
    coupling: float = 0.61,
    *,
    hbar: float = 1.0,
) -> Hamiltonian:
    """Build the two-qubit reference Hamiltonian ``omega1 ZI + omega2 IZ + J XX``."""

    coefficients = (float(omega_1), float(omega_2), float(coupling))
    if not all(math.isfinite(value) for value in coefficients):
        raise ValueError("Von Neumann Flow I coefficients must be finite.")
    matrix = (
        coefficients[0] * pauli_matrix("ZI")
        + coefficients[1] * pauli_matrix("IZ")
        + coefficients[2] * pauli_matrix("XX")
    )
    return Hamiltonian(matrix, hbar=hbar, label="von_neumann_flow_i")


def von_neumann_flow_i_initial_state() -> Array:
    """Return ``|+>|0>`` in the displayed computational-bit ordering."""

    plus = np.array((1.0, 1.0), dtype=np.complex128) / math.sqrt(2.0)
    zero = np.array((1.0, 0.0), dtype=np.complex128)
    return _readonly(np.kron(plus, zero))


def von_neumann_flow_i_frame(
    time: float = 0.0,
    *,
    frame_index: int = 0,
    omega_1: float = 1.17,
    omega_2: float = 0.73,
    coupling: float = 0.61,
    hbar: float = 1.0,
) -> QuantumFrame:
    """Observe the exact closed reference state at ``time`` without adapters."""

    generator = von_neumann_flow_i_hamiltonian(omega_1, omega_2, coupling, hbar=hbar)
    initial_density = density_from_state(von_neumann_flow_i_initial_state())
    return QuantumFrame.observe(
        time=time,
        frame_index=frame_index,
        hamiltonian=generator,
        rho=generator.evolve_unitary(initial_density, float(time)),
    )


__all__ = [
    "Array", "Hamiltonian", "LindbladChannel", "PauliCoordinates", "QuantumFrame",
    "basis_current_inflow", "conserved_pauli_labels", "density_from_state",
    "energy_expectation", "energy_variance", "lindblad_dissipator",
    "pauli_coordinate_values", "reconstruct_density_from_pauli",
    "von_neumann_flow_i_frame", "von_neumann_flow_i_hamiltonian",
    "von_neumann_flow_i_initial_state",
]
