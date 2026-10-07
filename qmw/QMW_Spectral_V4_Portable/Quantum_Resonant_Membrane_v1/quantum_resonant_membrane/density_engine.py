"""Authoritative two-qubit density-matrix engine for the standalone instrument.

Unitary Hamiltonian evolution and explicit quantum channels own ``rho``.  No
geometry, membrane, OSC, or sound code writes back into this state.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
import math

import numpy as np


Array = np.ndarray
PREPARATION_MODES = ("localized", "coherent", "squeezed", "thermal", "vacuum")
PREPARATION_SEMANTICS = {
    "localized": "computational-basis localized state",
    "coherent": "two-qubit spin-coherent product state",
    "squeezed": "two-qubit pair-correlated squeezed analogue",
    "thermal": "Hamiltonian Gibbs state",
    "vacuum": "Hamiltonian ground state",
}
I2 = np.eye(2, dtype=np.complex128)
X = np.array([[0, 1], [1, 0]], dtype=np.complex128)
Y = np.array([[0, -1j], [1j, 0]], dtype=np.complex128)
Z = np.array([[1, 0], [0, -1]], dtype=np.complex128)
XI, YI, ZI = (np.kron(operator, I2) for operator in (X, Y, Z))
IX, IY, IZ = (np.kron(I2, operator) for operator in (X, Y, Z))
XX, YY, ZZ = (np.kron(operator, operator) for operator in (X, Y, Z))


@dataclass(frozen=True)
class DensityConfig:
    coupling: float = 0.72
    drive: float = 1.15
    dephasing_rate: float = 0.08
    damping_rate: float = 0.025
    depolarizing_rate: float = 0.005
    max_hamiltonian_phase_step: float = 0.15
    max_substeps: int = 256
    freeze: bool = False

    def validated(self) -> "DensityConfig":
        values = (
            self.coupling,
            self.drive,
            self.dephasing_rate,
            self.damping_rate,
            self.depolarizing_rate,
            self.max_hamiltonian_phase_step,
        )
        if not np.isfinite(values).all():
            raise ValueError("density configuration must be finite")
        if self.drive < 0.0:
            raise ValueError("drive must be nonnegative")
        if min(self.dephasing_rate, self.damping_rate, self.depolarizing_rate) < 0.0:
            raise ValueError("quantum-channel rates must be nonnegative")
        if self.max_hamiltonian_phase_step <= 0.0:
            raise ValueError("max_hamiltonian_phase_step must be positive")
        if int(self.max_substeps) != self.max_substeps or self.max_substeps < 1:
            raise ValueError("max_substeps must be a positive integer")
        return self


@dataclass(frozen=True)
class DensityFrame:
    time: float
    dt: float
    rho: Array
    hamiltonian: Array
    populations: Array
    coherence: Array
    coherence_l1: float
    purity: float
    entropy_bits: float
    hamiltonian_span: float
    substeps: int
    actual_substep: float
    config: DensityConfig
    preparation_mode: str
    preparation_semantics: str
    schema: str = "qmw.quantum_resonant_membrane.density.v1"


def _normalize_density(rho: Array) -> Array:
    matrix = 0.5 * (rho + rho.conj().T)
    values, vectors = np.linalg.eigh(matrix)
    values = np.maximum(values.real, 0.0)
    total = float(np.sum(values))
    if total <= 1.0e-15:
        raise ValueError("density matrix lost positive trace")
    return (vectors * (values / total)) @ vectors.conj().T


def _apply_local_channel(rho: Array, operators: tuple[Array, ...], qubit: int) -> Array:
    result = np.zeros_like(rho)
    for operator in operators:
        full = np.kron(operator, I2) if qubit == 0 else np.kron(I2, operator)
        result += full @ rho @ full.conj().T
    return result


def _dephase(rho: Array, rate: float, dt: float, qubit: int) -> Array:
    probability = 0.5 * (1.0 - math.exp(-rate * dt))
    return _apply_local_channel(
        rho,
        (math.sqrt(1.0 - probability) * I2, math.sqrt(probability) * Z),
        qubit,
    )


def _amplitude_damp(rho: Array, rate: float, dt: float, qubit: int) -> Array:
    gamma = 1.0 - math.exp(-rate * dt)
    operators = (
        np.array([[1, 0], [0, math.sqrt(1.0 - gamma)]], dtype=np.complex128),
        np.array([[0, math.sqrt(gamma)], [0, 0]], dtype=np.complex128),
    )
    return _apply_local_channel(rho, operators, qubit)


def _depolarize(rho: Array, rate: float, dt: float, qubit: int) -> Array:
    probability = 1.0 - math.exp(-rate * dt)
    operators = (
        math.sqrt(1.0 - probability) * I2,
        math.sqrt(probability / 3.0) * X,
        math.sqrt(probability / 3.0) * Y,
        math.sqrt(probability / 3.0) * Z,
    )
    return _apply_local_channel(rho, operators, qubit)


class DensityMatrixEngine:
    """Deterministic open-system density engine with explicit preparations.

    ``coherent`` and ``squeezed`` are finite two-qubit analogues, not claims
    that this engine is a continuous-variable Gaussian field simulator.
    """

    def __init__(self, config: DensityConfig | None = None) -> None:
        self.config = (config or DensityConfig()).validated()
        self.preparation_mode = "localized"
        self.localized_index = 0
        self.coherent_theta = 0.95
        self.coherent_phase = 0.55
        self.squeeze_magnitude = 0.62
        self.squeeze_phase = math.pi / 2.0
        self.temperature = 0.8
        self.time = 0.0
        self.reset()

    def reset(self) -> None:
        """Reapply the currently selected preparation at time zero."""
        self.prepare(self.preparation_mode)

    def prepare(self, mode: str) -> None:
        """Replace rho with a named, scientifically bounded preparation."""
        normalized_mode = str(mode).strip().lower()
        if normalized_mode not in PREPARATION_MODES:
            raise ValueError(
                f"unknown preparation {mode!r}; expected one of "
                + ", ".join(PREPARATION_MODES)
            )

        if normalized_mode == "localized":
            state = np.zeros(4, dtype=np.complex128)
            state[int(self.localized_index) % 4] = 1.0
            rho = np.outer(state, state.conj())
        elif normalized_mode == "coherent":
            # SU(2) spin-coherent product state: the finite two-qubit
            # counterpart used here for the older instrument's label.
            theta = float(np.clip(self.coherent_theta, 0.0, math.pi))
            phase = float(self.coherent_phase)
            qubit = np.array(
                [math.cos(theta / 2.0), np.exp(1j * phase) * math.sin(theta / 2.0)],
                dtype=np.complex128,
            )
            state = np.kron(qubit, qubit)
            rho = np.outer(state, state.conj())
        elif normalized_mode == "squeezed":
            # Pair-correlated |00> + exp(i*phase)|11> state. This preserves
            # the squeezing idea without pretending to provide a Gaussian CV
            # mode in a four-dimensional Hilbert space.
            magnitude = float(np.clip(self.squeeze_magnitude, 0.0, math.pi / 2.0))
            state = np.array(
                [
                    math.cos(magnitude),
                    0.0,
                    0.0,
                    np.exp(1j * self.squeeze_phase) * math.sin(magnitude),
                ],
                dtype=np.complex128,
            )
            rho = np.outer(state, state.conj())
        else:
            hamiltonian = self.hamiltonian(0.0)
            energies, vectors = np.linalg.eigh(hamiltonian)
            if normalized_mode == "vacuum":
                state = vectors[:, int(np.argmin(energies))]
                rho = np.outer(state, state.conj())
            else:
                temperature = max(float(self.temperature), 1.0e-6)
                weights = np.exp(-(energies - float(np.min(energies))) / temperature)
                weights /= np.sum(weights)
                rho = (vectors * weights) @ vectors.conj().T

        self.rho = _normalize_density(rho)
        self.preparation_mode = normalized_mode
        self.time = 0.0

    def set_config(self, **changes: object) -> None:
        self.config = replace(self.config, **changes).validated()

    def hamiltonian(self, time_value: float | None = None) -> Array:
        t = self.time if time_value is None else float(time_value)
        drive = self.config.drive
        local = (
            drive * (0.34 + 0.12 * math.sin(0.31 * t)) * XI
            + drive * (0.12 + 0.10 * math.cos(0.23 * t)) * YI
            + drive * 0.24 * ZI
            + drive * (0.21 + 0.11 * math.cos(0.29 * t)) * IX
            - drive * (0.14 + 0.08 * math.sin(0.37 * t)) * IY
            + drive * 0.29 * IZ
        )
        coupling = self.config.coupling
        return local + coupling * (ZZ + 0.31 * XX + 0.21 * YY)

    def step(self, dt: float) -> DensityFrame:
        dt = float(dt)
        if not math.isfinite(dt) or dt < 0.0:
            raise ValueError("dt must be finite and nonnegative")
        midpoint_hamiltonian = self.hamiltonian(self.time + 0.5 * dt)
        midpoint_energies = np.linalg.eigvalsh(midpoint_hamiltonian)
        hamiltonian_span = float(np.ptp(midpoint_energies.real))
        substeps = 0
        actual_substep = 0.0
        if not self.config.freeze and dt > 0.0:
            requested = max(
                1,
                int(
                    math.ceil(
                        hamiltonian_span
                        * dt
                        / self.config.max_hamiltonian_phase_step
                    )
                ),
            )
            if requested > self.config.max_substeps:
                raise RuntimeError(
                    "density evolution exceeded max_substeps; reduce dt or drive"
                )
            substeps = requested
            actual_substep = dt / substeps
            rho = self.rho
            for index in range(substeps):
                substep_time = self.time + (index + 0.5) * actual_substep
                hamiltonian = self.hamiltonian(substep_time)
                energies, vectors = np.linalg.eigh(hamiltonian)
                unitary = (
                    vectors * np.exp(-1j * energies * actual_substep)
                ) @ vectors.conj().T
                rho = unitary @ rho @ unitary.conj().T
                for qubit in (0, 1):
                    rho = _dephase(
                        rho, self.config.dephasing_rate, actual_substep, qubit
                    )
                    rho = _amplitude_damp(
                        rho, self.config.damping_rate, actual_substep, qubit
                    )
                    rho = _depolarize(
                        rho, self.config.depolarizing_rate, actual_substep, qubit
                    )
            self.rho = _normalize_density(rho)
        self.time += dt
        hamiltonian = self.hamiltonian(self.time)
        eigenvalues = np.maximum(np.linalg.eigvalsh(self.rho).real, 1.0e-15)
        coherence = np.abs(self.rho)
        np.fill_diagonal(coherence, 0.0)
        return DensityFrame(
            time=self.time,
            dt=dt,
            rho=self.rho.copy(),
            hamiltonian=hamiltonian.copy(),
            populations=np.real(np.diag(self.rho)).copy(),
            coherence=coherence,
            coherence_l1=float(np.sum(coherence)),
            purity=float(np.trace(self.rho @ self.rho).real),
            entropy_bits=float(-np.sum(eigenvalues * np.log2(eigenvalues))),
            hamiltonian_span=hamiltonian_span,
            substeps=substeps,
            actual_substep=actual_substep,
            config=self.config,
            preparation_mode=self.preparation_mode,
            preparation_semantics=PREPARATION_SEMANTICS[self.preparation_mode],
        )


__all__ = [
    "DensityConfig",
    "DensityFrame",
    "DensityMatrixEngine",
    "PREPARATION_MODES",
    "PREPARATION_SEMANTICS",
]
