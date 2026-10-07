"""Immutable contracts for the one-qubit instrument."""

from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np


Array = np.ndarray
MODE_COUNT = 9
MODE_LABELS = (
    "mixedness_monopole",
    "dipole_x",
    "dipole_y",
    "dipole_z",
    "quadrupole_xy",
    "quadrupole_yz",
    "quadrupole_zx",
    "quadrupole_x2_minus_y2",
    "quadrupole_3z2_minus_r2",
)


def readonly(values: object, *, dtype: object = float) -> Array:
    result = np.array(values, dtype=dtype, copy=True)
    result.flags.writeable = False
    return result


def _revision(value: int) -> int:
    if int(value) != value or value < 0:
        raise ValueError("revision must be a nonnegative integer")
    return int(value)


def _finite(value: float, name: str) -> float:
    result = float(value)
    if not math.isfinite(result):
        raise ValueError(f"{name} must be finite")
    return result


@dataclass(frozen=True)
class OneQubitQuantumFrame:
    """One authoritative state after a complete evolution/intervention step."""

    revision: int
    time: float
    rho: Array
    hamiltonian: Array
    omega_rad_per_second: Array
    t1_seconds: float | None
    tphi_seconds: float | None
    provenance: str = "authoritative_one_qubit_density_dynamics_v1"

    def __post_init__(self) -> None:
        object.__setattr__(self, "revision", _revision(self.revision))
        object.__setattr__(self, "time", _finite(self.time, "time"))
        rho = readonly(self.rho, dtype=np.complex128)
        hamiltonian = readonly(self.hamiltonian, dtype=np.complex128)
        omega = readonly(self.omega_rad_per_second, dtype=float)
        if rho.shape != (2, 2) or hamiltonian.shape != (2, 2) or omega.shape != (3,):
            raise ValueError("one-qubit frames require 2x2 rho/H and a three-vector omega")
        if not np.all(np.isfinite(rho)) or not np.all(np.isfinite(hamiltonian)) or not np.all(np.isfinite(omega)):
            raise ValueError("frame arrays must be finite")
        if not np.allclose(rho, rho.conj().T, atol=1e-10):
            raise ValueError("rho must be Hermitian")
        if not np.isclose(np.trace(rho), 1.0, atol=1e-10):
            raise ValueError("rho must have trace one")
        if np.min(np.linalg.eigvalsh(rho)) < -1e-10:
            raise ValueError("rho must be positive semidefinite")
        if not np.allclose(hamiltonian, hamiltonian.conj().T, atol=1e-10):
            raise ValueError("Hamiltonian must be Hermitian")
        for value, name in ((self.t1_seconds, "T1"), (self.tphi_seconds, "Tphi")):
            if value is not None and (not math.isfinite(float(value)) or float(value) <= 0.0):
                raise ValueError(f"{name} must be positive or disabled")
        if not self.provenance:
            raise ValueError("provenance must be nonempty")
        object.__setattr__(self, "rho", rho)
        object.__setattr__(self, "hamiltonian", hamiltonian)
        object.__setattr__(self, "omega_rad_per_second", omega)


@dataclass(frozen=True)
class MeasurementEvent:
    """A discrete Born-rule intervention, kept outside continuous evolution."""

    pre_revision: int
    post_revision: int
    time: float
    basis: str
    outcome: int
    probability: float
    provenance: str = "discrete_projective_measurement_intervention_v1"

    def __post_init__(self) -> None:
        object.__setattr__(self, "pre_revision", _revision(self.pre_revision))
        object.__setattr__(self, "post_revision", _revision(self.post_revision))
        object.__setattr__(self, "time", _finite(self.time, "time"))
        if self.post_revision <= self.pre_revision:
            raise ValueError("measurement must advance the state revision")
        if self.basis != "Z" or self.outcome not in (0, 1):
            raise ValueError("V1 supports Z measurement outcomes 0 and 1")
        if not 0.0 <= float(self.probability) <= 1.0:
            raise ValueError("probability must lie in [0, 1]")


@dataclass(frozen=True)
class OneQubitObservationFrame:
    """Read-only physical observables derived from one authoritative frame."""

    revision: int
    time: float
    quantum_revision: int
    bloch_xyz: Array
    radius: float
    population_0: float
    population_1: float
    coherence_l1: float
    purity: float
    entropy_nats: float
    energy_gap_over_hbar_rad_per_second: float
    omega_rad_per_second: Array
    t1_seconds: float | None
    tphi_seconds: float | None
    provenance: str = "derived_one_qubit_observables_v1"

    def __post_init__(self) -> None:
        object.__setattr__(self, "revision", _revision(self.revision))
        object.__setattr__(self, "quantum_revision", _revision(self.quantum_revision))
        object.__setattr__(self, "time", _finite(self.time, "time"))
        bloch = readonly(self.bloch_xyz, dtype=float)
        omega = readonly(self.omega_rad_per_second, dtype=float)
        if bloch.shape != (3,) or omega.shape != (3,) or not np.all(np.isfinite(bloch)) or not np.all(np.isfinite(omega)):
            raise ValueError("Bloch and Hamiltonian coordinates must be finite three-vectors")
        if np.linalg.norm(bloch) > 1.0 + 1e-9:
            raise ValueError("Bloch vector lies outside the physical ball")
        scalars = (
            self.radius, self.population_0, self.population_1, self.coherence_l1,
            self.purity, self.entropy_nats,
            self.energy_gap_over_hbar_rad_per_second,
        )
        if not all(math.isfinite(float(value)) for value in scalars):
            raise ValueError("observables must be finite")
        for value, name in ((self.t1_seconds, "T1"), (self.tphi_seconds, "Tphi")):
            if value is not None and (not math.isfinite(float(value)) or float(value) <= 0.0):
                raise ValueError(f"{name} must be positive or disabled")
        object.__setattr__(self, "bloch_xyz", bloch)
        object.__setattr__(self, "omega_rad_per_second", omega)


@dataclass(frozen=True)
class SoundAdapterControls:
    """Perceptual/acoustic controls; none are quantum evolution parameters."""

    base_frequency_hz: float = 82.4069
    probe_rate_hz: float = 3.0
    probe_brightness: float = 0.55
    body_detail: float = 0.45
    base_decay_seconds: float = 0.85
    decay_tilt: float = 0.32
    master: float = 0.28
    sound_locked: bool = True

    def validated(self) -> "SoundAdapterControls":
        values = (
            self.base_frequency_hz, self.probe_rate_hz, self.probe_brightness,
            self.body_detail, self.base_decay_seconds, self.decay_tilt, self.master,
        )
        if not all(math.isfinite(float(value)) for value in values):
            raise ValueError("sound controls must be finite")
        if not 30.0 <= self.base_frequency_hz <= 440.0:
            raise ValueError("base frequency must lie in [30, 440] Hz")
        if not 0.25 <= self.probe_rate_hz <= 16.0:
            raise ValueError("probe rate must lie in [0.25, 16] Hz")
        if not 0.0 <= self.probe_brightness <= 1.0 or not 0.0 <= self.body_detail <= 1.0:
            raise ValueError("brightness and detail must lie in [0, 1]")
        if not 0.04 <= self.base_decay_seconds <= 5.0:
            raise ValueError("body decay must lie in [0.04, 5] seconds")
        if not -1.0 <= self.decay_tilt <= 1.0 or not 0.0 <= self.master <= 1.0:
            raise ValueError("decay tilt/master out of range")
        return self


@dataclass(frozen=True)
class ResonantBodyFrame:
    """Immutable, explicitly acoustic rendering targets for one modal body."""

    revision: int
    time: float
    observation_revision: int
    mode_labels: tuple[str, ...]
    frequencies_hz: Array
    decay_seconds: Array
    signed_weights: Array
    controls: SoundAdapterControls
    mapping_label: str = "mixedness_monopole_plus_bloch_dipole_quadrupole_v1"
    provenance: str = "perceptual_resonant_body_adapter_v1"

    def __post_init__(self) -> None:
        object.__setattr__(self, "revision", _revision(self.revision))
        object.__setattr__(self, "observation_revision", _revision(self.observation_revision))
        object.__setattr__(self, "time", _finite(self.time, "time"))
        if tuple(self.mode_labels) != MODE_LABELS:
            raise ValueError("mode labels must use the stable V1 ordering")
        frequencies = readonly(self.frequencies_hz, dtype=float)
        decays = readonly(self.decay_seconds, dtype=float)
        weights = readonly(self.signed_weights, dtype=float)
        if any(value.shape != (MODE_COUNT,) for value in (frequencies, decays, weights)):
            raise ValueError("body arrays must contain nine modes")
        if not all(np.all(np.isfinite(value)) for value in (frequencies, decays, weights)):
            raise ValueError("body arrays must be finite")
        if np.any(frequencies <= 0.0) or np.any(decays <= 0.0):
            raise ValueError("modal frequencies and decay times must be positive")
        if not np.isclose(np.dot(weights, weights), 1.0, atol=1e-9):
            raise ValueError("signed modal weights must have unit squared norm")
        object.__setattr__(self, "frequencies_hz", frequencies)
        object.__setattr__(self, "decay_seconds", decays)
        object.__setattr__(self, "signed_weights", weights)
        object.__setattr__(self, "controls", self.controls.validated())
