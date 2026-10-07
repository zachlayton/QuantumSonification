"""Exact four-qubit XY-chain transport trajectory.

This module is an offline/reference backend.  Its ``QuantumTrajectory`` is a
time-indexed collection of observations, whereas the integrated QMW
``QuantumFrame`` is a sealed observation at one instant.  ``iter_observations``
is the intentionally narrow bridge between the two representations.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Iterator, Mapping

import numpy as np


Array = np.ndarray
_EPSILON = 1.0e-12


def _readonly(values: object, *, dtype: object | None = None) -> Array:
    array = np.array(values, dtype=dtype, copy=True)
    array.flags.writeable = False
    return array


def _pauli(name: str) -> Array:
    matrices = {
        "I": np.array(((1.0, 0.0), (0.0, 1.0)), dtype=np.complex128),
        "X": np.array(((0.0, 1.0), (1.0, 0.0)), dtype=np.complex128),
        "Y": np.array(((0.0, -1.0j), (1.0j, 0.0)), dtype=np.complex128),
        "Z": np.array(((1.0, 0.0), (0.0, -1.0)), dtype=np.complex128),
    }
    return matrices[name]


def _tensor(operators: tuple[Array, ...]) -> Array:
    result = operators[0]
    for operator in operators[1:]:
        result = np.kron(result, operator)
    return result


def _embedded(name: str, site: int, *, qubits: int = 4) -> Array:
    if not 0 <= site < qubits:
        raise ValueError("site is outside the qubit chain.")
    return _tensor(tuple(_pauli(name) if index == site else _pauli("I") for index in range(qubits)))


def _number_operator(site: int) -> Array:
    return (_embedded("I", site) - _embedded("Z", site)) * 0.5


@dataclass(frozen=True)
class FourQubitXYModel:
    """Nearest-neighbour XY transport with displayed bit order ``q0 q1 q2 q3``.

    The initial ket ``|1000>`` therefore means an excitation at the leftmost,
    ``q0`` site.  ``hbar`` is set to one by default, so time is in inverse
    units of the supplied coupling strengths.
    """

    couplings: tuple[float, float, float] = (1.0, 0.82, 1.13)
    hbar: float = 1.0
    label: str = "four_qubit_xy_transport_v1"

    def __post_init__(self) -> None:
        values = tuple(float(value) for value in self.couplings)
        if len(values) != 3 or not all(np.isfinite(values)):
            raise ValueError("couplings must contain three finite values.")
        if not np.isfinite(float(self.hbar)) or self.hbar <= 0.0:
            raise ValueError("hbar must be finite and positive.")
        if not self.label:
            raise ValueError("label must be nonempty.")
        object.__setattr__(self, "couplings", values)
        object.__setattr__(self, "hbar", float(self.hbar))

    @property
    def qubits(self) -> int:
        return 4

    @property
    def dimension(self) -> int:
        return 2**self.qubits

    @property
    def site_number_operators(self) -> tuple[Array, ...]:
        return tuple(_readonly(_number_operator(site)) for site in range(self.qubits))

    @property
    def bond_hamiltonians(self) -> tuple[Array, ...]:
        terms: list[Array] = []
        for left, coupling in enumerate(self.couplings):
            right = left + 1
            term = coupling * 0.5 * (
                _embedded("X", left) @ _embedded("X", right)
                + _embedded("Y", left) @ _embedded("Y", right)
            )
            terms.append(_readonly(term))
        return tuple(terms)

    @property
    def hamiltonian(self) -> Array:
        return _readonly(sum(self.bond_hamiltonians, start=np.zeros((self.dimension, self.dimension), dtype=np.complex128)))

    @property
    def initial_state(self) -> Array:
        state = np.zeros(self.dimension, dtype=np.complex128)
        # q0 is the most-significant displayed bit: |1000> has index eight.
        state[1 << (self.qubits - 1)] = 1.0
        return _readonly(state)


@dataclass(frozen=True)
class QuantumTrajectory:
    """A validated sequence of density-matrix observations from one model.

    This class carries no claim that its 2048 values are audio samples.  The
    arrays are a numerical record of the declared quantum evolution and stay
    separate from musical mappings held in :mod:`granular`.
    """

    time: Array
    state: Array | None
    rho: Array
    site_populations: Array
    edge_current_left_to_right: Array
    hamiltonian: Array
    model: FourQubitXYModel
    metadata: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        time = np.asarray(self.time, dtype=float)
        state = None if self.state is None else np.asarray(self.state, dtype=np.complex128)
        rho = np.asarray(self.rho, dtype=np.complex128)
        populations = np.asarray(self.site_populations, dtype=float)
        currents = np.asarray(self.edge_current_left_to_right, dtype=float)
        dimension = self.model.dimension
        if time.ndim != 1 or time.size < 2 or not np.all(np.isfinite(time)):
            raise ValueError("time must be a finite one-dimensional sequence with at least two points.")
        if np.any(np.diff(time) <= 0.0):
            raise ValueError("time must increase strictly.")
        if state is not None and state.shape != (time.size, dimension):
            raise ValueError("state must have shape (samples, 16).")
        if rho.shape != (time.size, dimension, dimension):
            raise ValueError("rho must have shape (samples, 16, 16).")
        if populations.shape != (time.size, self.model.qubits):
            raise ValueError("site_populations must have shape (samples, 4).")
        if currents.shape != (time.size, self.model.qubits - 1):
            raise ValueError("edge currents must have shape (samples, 3).")
        hamiltonian = np.asarray(self.hamiltonian, dtype=np.complex128)
        if hamiltonian.shape != (dimension, dimension):
            raise ValueError("hamiltonian must have shape (16, 16).")
        object.__setattr__(self, "time", _readonly(time, dtype=float))
        object.__setattr__(self, "state", None if state is None else _readonly(state))
        object.__setattr__(self, "rho", _readonly(rho))
        object.__setattr__(self, "site_populations", _readonly(populations, dtype=float))
        object.__setattr__(self, "edge_current_left_to_right", _readonly(currents, dtype=float))
        object.__setattr__(self, "hamiltonian", _readonly(hamiltonian))
        object.__setattr__(self, "metadata", dict(self.metadata))

    @property
    def samples(self) -> int:
        return int(self.time.size)

    @property
    def duration(self) -> float:
        return float(self.time[-1] - self.time[0])

    @property
    def energy(self) -> Array:
        return np.real(np.einsum("tij,ji->t", self.rho, self.hamiltonian))

    @property
    def excitation_total(self) -> Array:
        return self.site_populations.sum(axis=1)

    @property
    def population_center(self) -> Array:
        # One conserved excitation makes this a site-coordinate expectation.
        return self.site_populations @ np.arange(self.model.qubits, dtype=float)

    @property
    def population_entropy(self) -> Array:
        safe = np.clip(self.site_populations, _EPSILON, 1.0)
        return -np.sum(safe * np.log2(safe), axis=1)

    def validate(self, *, tolerance: float = 1.0e-9) -> dict[str, float | bool]:
        identity = np.eye(self.model.dimension)
        trace = np.trace(self.rho, axis1=1, axis2=2)
        hermitian = self.rho - self.rho.swapaxes(1, 2).conj()
        eigenvalues = np.linalg.eigvalsh(self.rho)
        rho_dot = (-1.0j / self.model.hbar) * (self.hamiltonian @ self.rho - self.rho @ self.hamiltonian)
        population_rate = np.stack(
            [np.real(np.einsum("tij,ji->t", rho_dot, operator)) for operator in self.model.site_number_operators],
            axis=1,
        )
        expected_rate = np.empty_like(population_rate)
        expected_rate[:, 0] = -self.edge_current_left_to_right[:, 0]
        expected_rate[:, 1:-1] = self.edge_current_left_to_right[:, :-1] - self.edge_current_left_to_right[:, 1:]
        expected_rate[:, -1] = self.edge_current_left_to_right[:, -1]
        result: dict[str, float | bool] = {
            "trace_error_max": float(np.max(np.abs(trace - 1.0))),
            "hermiticity_error_max": float(np.max(np.abs(hermitian))),
            "minimum_density_eigenvalue": float(np.min(eigenvalues)),
            "positive_semidefinite": bool(float(np.min(eigenvalues)) >= -tolerance),
            "excitation_error_max": float(np.max(np.abs(self.excitation_total - 1.0))),
            "energy_drift_max": float(np.ptp(self.energy)),
            "site_continuity_error_max": float(np.max(np.abs(population_rate - expected_rate))),
            "hamiltonian_identity_error": float(np.max(np.abs(self.hamiltonian - self.hamiltonian.conj().T))),
            "identity_dimension": bool(identity.shape == self.hamiltonian.shape),
        }
        if self.state is not None:
            norm = np.sum(np.abs(self.state) ** 2, axis=1)
            result["state_norm_error_max"] = float(np.max(np.abs(norm - 1.0)))
        return result

    def iter_observations(self) -> Iterator[tuple[float, int, Array, Array]]:
        """Yield ``time, index, H, rho`` for a sealed-frame observer.

        A live owner can call its existing ``QuantumFrame.observe`` or
        equivalent from this iterator.  This iterator never pushes state back
        upstream and never treats the trajectory as a new authority.
        """
        for index, time in enumerate(self.time):
            yield float(time), index, self.hamiltonian, self.rho[index]

    def observe_with(self, observer: Callable[..., object]) -> tuple[object, ...]:
        """Adapt samples through a caller-supplied sealed-frame constructor."""
        if not callable(observer):
            raise TypeError("observer must be callable.")
        return tuple(
            observer(time=time, frame_index=index, hamiltonian=hamiltonian, rho=rho)
            for time, index, hamiltonian, rho in self.iter_observations()
        )


def run_xy_trajectory(
    *,
    samples: int = 2048,
    duration: float = 24.0,
    model: FourQubitXYModel | None = None,
) -> QuantumTrajectory:
    """Propagate ``|1000>`` through an exact, closed four-qubit XY chain."""
    if int(samples) != samples or int(samples) < 2:
        raise ValueError("samples must be an integer greater than one.")
    if not np.isfinite(float(duration)) or duration <= 0.0:
        raise ValueError("duration must be finite and positive.")
    selected = model if model is not None else FourQubitXYModel()
    if not isinstance(selected, FourQubitXYModel):
        raise TypeError("model must be a FourQubitXYModel or None.")
    time = np.linspace(0.0, float(duration), int(samples), dtype=float)
    hamiltonian = selected.hamiltonian
    eigenvalues, eigenvectors = np.linalg.eigh(hamiltonian)
    coefficients = eigenvectors.conj().T @ selected.initial_state
    phases = np.exp(-1.0j * np.outer(time, eigenvalues) / selected.hbar)
    state = np.einsum("ij,tj->ti", eigenvectors, phases * coefficients[None, :])
    rho = np.einsum("ti,tj->tij", state, state.conj())
    populations = np.stack(
        [np.real(np.einsum("tij,ji->t", rho, operator)) for operator in selected.site_number_operators],
        axis=1,
    )
    currents: list[Array] = []
    for left, (bond, number_left) in enumerate(zip(selected.bond_hamiltonians, selected.site_number_operators)):
        derivative = (-1.0j / selected.hbar) * (bond @ rho - rho @ bond)
        # Positive means excitation leaves ``left`` and enters ``left + 1``.
        currents.append(-np.real(np.einsum("tij,ji->t", derivative, number_left)))
    return QuantumTrajectory(
        time=time,
        state=state,
        rho=rho,
        site_populations=populations,
        edge_current_left_to_right=np.stack(currents, axis=1),
        hamiltonian=hamiltonian,
        model=selected,
        metadata={
            "backend": "numpy_exact_eigendecomposition",
            "initial_state": "|1000>",
            "basis_order": "q0 q1 q2 q3, q0 most-significant bit",
            "current_convention": "positive current leaves site i for i+1",
            "scientific_role": "offline reference trajectory",
        },
    )
