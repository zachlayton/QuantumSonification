"""Authoritative one-qubit density dynamics.

The closed step is exact. Optional T1 and pure-dephasing channels are exact
CPTP maps applied in a symmetric unitary/noise/unitary split. Measurement is
a separate method and never appears in the continuous derivative.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from threading import RLock

import numpy as np

from .frames import MeasurementEvent, OneQubitQuantumFrame, readonly


I2 = np.eye(2, dtype=np.complex128)
X = np.array(((0, 1), (1, 0)), dtype=np.complex128)
Y = np.array(((0, -1j), (1j, 0)), dtype=np.complex128)
Z = np.array(((1, 0), (0, -1)), dtype=np.complex128)
PAULI = (X, Y, Z)


def _positive_or_none(value: float | None, name: str) -> float | None:
    if value is None or float(value) == 0.0:
        return None
    result = float(value)
    if not math.isfinite(result) or result <= 0.0:
        raise ValueError(f"{name} must be positive, zero, or None")
    return result


def _validate_density(rho: object) -> np.ndarray:
    density = np.asarray(rho, dtype=np.complex128)
    if density.shape != (2, 2) or not np.all(np.isfinite(density)):
        raise ValueError("rho must be a finite 2x2 matrix")
    density = (density + density.conj().T) * 0.5
    if not np.isclose(np.trace(density), 1.0, atol=1e-10):
        raise ValueError("rho must have trace one")
    if np.min(np.linalg.eigvalsh(density)) < -1e-10:
        raise ValueError("rho must be positive semidefinite")
    return density


def density_from_bloch(x: float, y: float, z: float) -> np.ndarray:
    vector = np.asarray((x, y, z), dtype=float)
    if not np.all(np.isfinite(vector)) or np.linalg.norm(vector) > 1.0 + 1e-10:
        raise ValueError("Bloch coordinates must be finite and inside the unit ball")
    return readonly((I2 + x * X + y * Y + z * Z) * 0.5, dtype=np.complex128)


PREPARATIONS = {
    "0": density_from_bloch(0, 0, 1),
    "1": density_from_bloch(0, 0, -1),
    "+": density_from_bloch(1, 0, 0),
    "+i": density_from_bloch(0, 1, 0),
    "mixed": density_from_bloch(0, 0, 0),
}


@dataclass(frozen=True)
class OneQubitPhysicsControls:
    """Physical model parameters, in model radians and seconds."""

    omega_x: float = 1.60
    omega_y: float = 0.0
    omega_z: float = 0.70
    t1_seconds: float | None = None
    tphi_seconds: float | None = None

    def validated(self) -> "OneQubitPhysicsControls":
        omega = (self.omega_x, self.omega_y, self.omega_z)
        if not all(math.isfinite(float(value)) and abs(float(value)) <= 20.0 for value in omega):
            raise ValueError("Hamiltonian components must be finite and in [-20, 20] rad/s")
        object.__setattr__(self, "t1_seconds", _positive_or_none(self.t1_seconds, "T1"))
        object.__setattr__(self, "tphi_seconds", _positive_or_none(self.tphi_seconds, "Tphi"))
        return self

    @property
    def omega(self) -> np.ndarray:
        return np.asarray((self.omega_x, self.omega_y, self.omega_z), dtype=float)


def hamiltonian(controls: OneQubitPhysicsControls) -> np.ndarray:
    omega = controls.validated().omega
    return readonly(0.5 * sum(value * pauli for value, pauli in zip(omega, PAULI)), dtype=np.complex128)


def unitary(omega: np.ndarray, duration: float) -> np.ndarray:
    """Return exp(-i H dt) exactly for H = omega.sigma/2 and hbar=1."""

    dt = float(duration)
    if not math.isfinite(dt) or dt < 0.0:
        raise ValueError("duration must be finite and nonnegative")
    speed = float(np.linalg.norm(omega))
    if speed <= 1e-15 or dt == 0.0:
        return I2.copy()
    axis_operator = sum((omega[index] / speed) * PAULI[index] for index in range(3))
    angle = 0.5 * speed * dt
    return np.cos(angle) * I2 - 1j * np.sin(angle) * axis_operator


def evolve_unitary(rho: object, omega: np.ndarray, duration: float) -> np.ndarray:
    density = _validate_density(rho)
    propagator = unitary(np.asarray(omega, dtype=float), duration)
    return _validate_density(propagator @ density @ propagator.conj().T)


def apply_relaxation_and_dephasing(
    rho: object,
    duration: float,
    *,
    t1_seconds: float | None,
    tphi_seconds: float | None,
) -> np.ndarray:
    """Apply exact amplitude-damping and pure-dephasing channels for ``dt``."""

    density = _validate_density(rho)
    dt = float(duration)
    if not math.isfinite(dt) or dt < 0.0:
        raise ValueError("duration must be finite and nonnegative")
    t1 = _positive_or_none(t1_seconds, "T1")
    tphi = _positive_or_none(tphi_seconds, "Tphi")
    result = density.copy()
    if t1 is not None and dt > 0.0:
        survival = math.exp(-dt / t1)
        e0 = np.array(((1.0, 0.0), (0.0, math.sqrt(survival))), dtype=np.complex128)
        e1 = np.array(((0.0, math.sqrt(1.0 - survival)), (0.0, 0.0)), dtype=np.complex128)
        result = e0 @ result @ e0.conj().T + e1 @ result @ e1.conj().T
    if tphi is not None and dt > 0.0:
        factor = math.exp(-dt / tphi)
        result[0, 1] *= factor
        result[1, 0] *= factor
    return _validate_density(result)


class OneQubitEngine:
    """Thread-safe owner of one authoritative rho and Hamiltonian."""

    def __init__(
        self,
        controls: OneQubitPhysicsControls | None = None,
        *,
        preparation: str = "0",
        seed: int = 1729,
    ) -> None:
        if preparation not in PREPARATIONS:
            raise ValueError(f"unknown preparation: {preparation}")
        self._controls = (controls or OneQubitPhysicsControls()).validated()
        self._rho = np.array(PREPARATIONS[preparation], copy=True)
        self._time = 0.0
        self._revision = 0
        self._rng = np.random.default_rng(seed)
        self._lock = RLock()

    @property
    def controls(self) -> OneQubitPhysicsControls:
        with self._lock:
            return self._controls

    def snapshot(self) -> OneQubitQuantumFrame:
        with self._lock:
            return self._frame()

    def _frame(self) -> OneQubitQuantumFrame:
        return OneQubitQuantumFrame(
            revision=self._revision,
            time=self._time,
            rho=self._rho,
            hamiltonian=hamiltonian(self._controls),
            omega_rad_per_second=self._controls.omega,
            t1_seconds=self._controls.t1_seconds,
            tphi_seconds=self._controls.tphi_seconds,
        )

    def set_controls(self, controls: OneQubitPhysicsControls) -> OneQubitQuantumFrame:
        """Commit a sudden Hamiltonian/channel change while preserving rho."""

        with self._lock:
            self._controls = controls.validated()
            self._revision += 1
            return self._frame()

    def prepare(self, name: str) -> OneQubitQuantumFrame:
        with self._lock:
            if name not in PREPARATIONS:
                raise ValueError(f"unknown preparation: {name}")
            self._rho = np.array(PREPARATIONS[name], copy=True)
            self._time = 0.0
            self._revision += 1
            return self._frame()

    def step(self, duration: float) -> OneQubitQuantumFrame:
        """Advance with a second-order CPTP split; the closed step is exact."""

        dt = float(duration)
        if not math.isfinite(dt) or dt <= 0.0:
            raise ValueError("step duration must be finite and positive")
        with self._lock:
            omega = self._controls.omega
            if self._controls.t1_seconds is None and self._controls.tphi_seconds is None:
                self._rho = evolve_unitary(self._rho, omega, dt)
            else:
                half = evolve_unitary(self._rho, omega, 0.5 * dt)
                noisy = apply_relaxation_and_dephasing(
                    half,
                    dt,
                    t1_seconds=self._controls.t1_seconds,
                    tphi_seconds=self._controls.tphi_seconds,
                )
                self._rho = evolve_unitary(noisy, omega, 0.5 * dt)
            self._time += dt
            self._revision += 1
            return self._frame()

    def measure_z(self) -> tuple[MeasurementEvent, OneQubitQuantumFrame]:
        with self._lock:
            pre_revision = self._revision
            probabilities = np.clip(np.real(np.diag(self._rho)), 0.0, 1.0)
            probabilities /= probabilities.sum()
            outcome = int(self._rng.choice((0, 1), p=probabilities))
            probability = float(probabilities[outcome])
            self._rho = np.zeros((2, 2), dtype=np.complex128)
            self._rho[outcome, outcome] = 1.0
            self._revision += 1
            event = MeasurementEvent(
                pre_revision=pre_revision,
                post_revision=self._revision,
                time=self._time,
                basis="Z",
                outcome=outcome,
                probability=probability,
            )
            return event, self._frame()
