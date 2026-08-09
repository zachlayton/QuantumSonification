"""Finite-dimensional spinor instruments: Larmor precession and EPR pairs."""

from __future__ import annotations

import math
from typing import Mapping, Sequence

import numpy as np

from excitation.quantum_frames_v1 import EntangledQubitFrame, SpinorFrame


Array = np.ndarray
I2 = np.eye(2, dtype=np.complex128)
PAULI = (
    np.array([[0.0, 1.0], [1.0, 0.0]], dtype=np.complex128),
    np.array([[0.0, -1.0j], [1.0j, 0.0]], dtype=np.complex128),
    np.array([[1.0, 0.0], [0.0, -1.0]], dtype=np.complex128),
)


def _vector3(values: Sequence[float]) -> tuple[float, float, float]:
    result = tuple(float(value) for value in values)
    if len(result) != 3:
        raise ValueError("expected three vector components")
    return result  # type: ignore[return-value]


def _normalize(state: Array) -> Array:
    vector = np.asarray(state, dtype=np.complex128).reshape(-1)
    norm = float(np.linalg.norm(vector))
    if norm <= 1e-15:
        raise ValueError("quantum state must have nonzero norm")
    return vector / norm


def _spin_unitary(omega: Sequence[float], dt: float) -> Array:
    vector = np.asarray(omega, dtype=np.float64)
    magnitude = float(np.linalg.norm(vector))
    if magnitude <= 1e-15 or dt == 0.0:
        return I2.copy()
    generator = sum(component * matrix for component, matrix in zip(vector / magnitude, PAULI))
    angle = 0.5 * magnitude * dt
    return math.cos(angle) * I2 - 1j * math.sin(angle) * generator


def _bloch(density: Array) -> tuple[float, float, float]:
    return tuple(float(np.trace(density @ matrix).real) for matrix in PAULI)  # type: ignore[return-value]


def _conditional_bloch(
    local: Sequence[float],
    measured_local: Sequence[float],
    correlations: Array,
    *,
    measured_party: str,
) -> tuple[float, float, float]:
    """Bloch vector conditioned on a +1 measurement along the other party's X axis."""
    axis_x = np.array((1.0, 0.0, 0.0), dtype=np.float64)
    transfer = correlations @ axis_x if measured_party == "b" else correlations.T @ axis_x
    denominator = 1.0 + float(np.dot(measured_local, axis_x))
    result = (np.asarray(local, dtype=np.float64) + transfer) / max(denominator, 1e-15)
    return tuple(float(value) for value in result)  # type: ignore[return-value]


class SpinHalfPrecessionSource:
    """Exact Pauli-spinor evolution in a static magnetic field."""

    def __init__(
        self,
        *,
        magnetic_field: Sequence[float] = (0.0, 0.0, 1.0),
        gyromagnetic_ratio: float = 2.0 * math.pi,
        initial_spinor: Sequence[complex] = (1.0, 1.0),
        hbar: float = 1.0,
    ) -> None:
        self.magnetic_field = _vector3(magnetic_field)
        self.gyromagnetic_ratio = float(gyromagnetic_ratio)
        self.hbar = float(hbar)
        self._initial_spinor = _normalize(np.asarray(initial_spinor, dtype=np.complex128))
        if self._initial_spinor.size != 2:
            raise ValueError("spin-1/2 requires two complex amplitudes")
        self.spinor = self._initial_spinor.copy()
        self.time = 0.0

    @property
    def larmor_vector(self) -> tuple[float, float, float]:
        return tuple(self.gyromagnetic_ratio * value for value in self.magnetic_field)  # type: ignore[return-value]

    def reset(self) -> None:
        self.spinor = self._initial_spinor.copy()
        self.time = 0.0

    def frame(self, dt: float = 0.0) -> SpinorFrame:
        if dt < 0.0:
            raise ValueError("dt must be non-negative")
        self.spinor = _spin_unitary(self.larmor_vector, dt) @ self.spinor
        self.spinor = _normalize(self.spinor)
        self.time += dt
        density = np.outer(self.spinor, self.spinor.conj())
        bloch = _bloch(density)
        omega = self.larmor_vector
        hamiltonian = 0.5 * self.hbar * sum(value * matrix for value, matrix in zip(omega, PAULI))
        energy = float(np.vdot(self.spinor, hamiltonian @ self.spinor).real)
        relative_phase = float(np.angle(self.spinor[1]) - np.angle(self.spinor[0]))
        relative_phase = float((relative_phase + math.pi) % (2.0 * math.pi) - math.pi)
        return SpinorFrame(
            spinor=self.spinor.copy(),
            density_matrix=density,
            probabilities_z=(float(abs(self.spinor[0]) ** 2), float(abs(self.spinor[1]) ** 2)),
            bloch_vector=bloch,
            magnetic_field=self.magnetic_field,
            larmor_vector=omega,
            larmor_angular_frequency=float(np.linalg.norm(omega)),
            energy_expectation=energy,
            relative_phase=relative_phase,
            time=self.time,
            norm=float(np.vdot(self.spinor, self.spinor).real),
            source="spin_1_2_precession",
            metadata={"gyromagnetic_ratio": self.gyromagnetic_ratio, "hbar": self.hbar},
        )


class EPRBellPairSource:
    """Two entangled qubits under independent exact local spin precession."""

    BELL_STATES: Mapping[str, tuple[complex, complex, complex, complex]] = {
        "phi_plus": (1.0, 0.0, 0.0, 1.0),
        "phi_minus": (1.0, 0.0, 0.0, -1.0),
        "psi_plus": (0.0, 1.0, 1.0, 0.0),
        "singlet": (0.0, 1.0, -1.0, 0.0),
    }

    def __init__(
        self,
        *,
        bell_state: str = "singlet",
        omega_a: Sequence[float] = (0.0, 0.0, 2.0 * math.pi),
        omega_b: Sequence[float] = (0.0, 0.0, -2.0 * math.pi),
    ) -> None:
        if bell_state not in self.BELL_STATES:
            raise ValueError(f"unknown Bell state {bell_state!r}")
        self.bell_state = bell_state
        self.omega_a = _vector3(omega_a)
        self.omega_b = _vector3(omega_b)
        self._initial_state = _normalize(np.asarray(self.BELL_STATES[bell_state]))
        self.state = self._initial_state.copy()
        self.time = 0.0

    def reset(self) -> None:
        self.state = self._initial_state.copy()
        self.time = 0.0

    def frame(self, dt: float = 0.0) -> EntangledQubitFrame:
        if dt < 0.0:
            raise ValueError("dt must be non-negative")
        unitary = np.kron(_spin_unitary(self.omega_a, dt), _spin_unitary(self.omega_b, dt))
        self.state = _normalize(unitary @ self.state)
        self.time += dt
        density = np.outer(self.state, self.state.conj())
        tensor = density.reshape(2, 2, 2, 2)
        reduced_a = np.trace(tensor, axis1=1, axis2=3)
        reduced_b = np.trace(tensor, axis1=0, axis2=2)
        correlations = np.array(
            [
                [float(np.trace(density @ np.kron(a, b)).real) for b in PAULI]
                for a in PAULI
            ],
            dtype=np.float64,
        )
        singular_values = np.linalg.eigvalsh(correlations.T @ correlations)
        chsh = 2.0 * math.sqrt(max(0.0, float(singular_values[-1] + singular_values[-2])))
        a, b, c, d = self.state
        concurrence = float(np.clip(2.0 * abs(a * d - b * c), 0.0, 1.0))
        bloch_a = _bloch(reduced_a)
        bloch_b = _bloch(reduced_b)
        return EntangledQubitFrame(
            state=self.state.copy(),
            density_matrix=density,
            reduced_a=reduced_a,
            reduced_b=reduced_b,
            bloch_a=bloch_a,
            bloch_b=bloch_b,
            conditional_a_given_b_x_plus=_conditional_bloch(
                bloch_a, bloch_b, correlations, measured_party="b"
            ),
            conditional_b_given_a_x_plus=_conditional_bloch(
                bloch_b, bloch_a, correlations, measured_party="a"
            ),
            correlation_tensor=correlations,
            concurrence=concurrence,
            chsh_maximum=chsh,
            time=self.time,
            norm=float(np.vdot(self.state, self.state).real),
            source="quantum_entanglement_epr",
            metadata={
                "bell_state": self.bell_state,
                "omega_a": self.omega_a,
                "omega_b": self.omega_b,
            },
        )


__all__ = ["EPRBellPairSource", "SpinHalfPrecessionSource"]
