"""Finite four-qubit Floquet time-crystal experiment and diagnostics.

This reference model repeats one identical Floquet unitary every drive period:

    U_F = U_interaction U_kick

with an imperfect global X rotation and an interacting disordered Ising
Hamiltonian.  It can exhibit finite-size period-doubled signatures, but four
qubits cannot establish a thermodynamic phase.  The module therefore reports
candidate signatures, perturbation sweeps, and quasienergy pairing without
claiming proof of genuine discrete time-crystalline order.

Programmed n-step score sequences do not enter U_F.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Any, Iterable, Sequence

import numpy as np

try:
    from .qmw_temporal_core16_v1 import (
        DIM,
        N_QUBITS,
        X,
        Z,
        as_complex_matrix,
        computational_basis_state,
        density_from_state,
        evolve_unitary,
        expectation,
        hermitian_unitary,
        operator_on_qubit,
        purity,
        trace_distance,
        two_qubit_product,
        validate_density_matrix,
    )
except ImportError:  # pragma: no cover
    from qmw_temporal_core16_v1 import (
        DIM,
        N_QUBITS,
        X,
        Z,
        as_complex_matrix,
        computational_basis_state,
        density_from_state,
        evolve_unitary,
        expectation,
        hermitian_unitary,
        operator_on_qubit,
        purity,
        trace_distance,
        two_qubit_product,
        validate_density_matrix,
    )


@dataclass(frozen=True)
class FloquetIsingConfig:
    """Configuration for a two-stage kicked four-spin Ising model."""

    kick_angle: float = np.pi
    pulse_error: float = 0.0
    interaction_time: float = 1.0
    interaction_strengths: tuple[float, ...] = (0.91, 1.07, 0.83)
    longitudinal_fields: tuple[float, ...] = (0.31, -0.27, 0.19, -0.11)
    transverse_fields: tuple[float, ...] = (0.0, 0.0, 0.0, 0.0)
    periodic_boundary: bool = False
    periodic_coupling: float = 0.97

    def __post_init__(self) -> None:
        expected_bonds = N_QUBITS if self.periodic_boundary else N_QUBITS - 1
        strengths = self.interaction_strengths
        if self.periodic_boundary and len(strengths) == N_QUBITS - 1:
            strengths = (*strengths, float(self.periodic_coupling))
            object.__setattr__(self, "interaction_strengths", strengths)
        if len(strengths) != expected_bonds:
            raise ValueError(
                f"interaction_strengths requires {expected_bonds} values "
                f"for this boundary condition"
            )
        if len(self.longitudinal_fields) != N_QUBITS:
            raise ValueError("longitudinal_fields requires four values")
        if len(self.transverse_fields) != N_QUBITS:
            raise ValueError("transverse_fields requires four values")

    @property
    def actual_kick_angle(self) -> float:
        return float(self.kick_angle * (1.0 + self.pulse_error))


@dataclass(frozen=True)
class SpectralOrderDiagnostics:
    target_frequency: float
    target_bin_frequency: float
    target_amplitude: float
    dominant_frequency: float
    dominant_amplitude: float
    locking_error: float
    peak_to_background: float
    complex_order_parameter: complex
    samples: int


@dataclass(frozen=True)
class FloquetTrajectory:
    ticks: np.ndarray
    density_matrices: np.ndarray = field(repr=False)
    magnetization_z: np.ndarray
    return_overlap: np.ndarray
    purity: np.ndarray
    protocol_kind: str = "floquet_repeated_single_period_map"


@dataclass(frozen=True)
class QuasienergyPairingDiagnostics:
    separation_radians: float
    mean_pairing_error: float
    maximum_pairing_error: float
    normalized_pairing_score: float
    eigenphases: np.ndarray = field(repr=False)


def analyze_temporal_order(
    signal: Sequence[complex],
    *,
    target_frequency: float,
    discard: int = 0,
    remove_mean: bool = True,
) -> SpectralOrderDiagnostics:
    """Analyze a complex stroboscopic signal in cycles per drive period."""

    values = np.asarray(signal, dtype=np.complex128).reshape(-1)
    values = values[int(discard) :]
    if values.size < 4:
        raise ValueError("at least four post-discard samples are required")
    if remove_mean:
        values = values - np.mean(values)

    spectrum = np.fft.fft(values) / values.size
    frequencies = np.mod(np.fft.fftfreq(values.size, d=1.0), 1.0)
    target = float(target_frequency) % 1.0

    circular_distance = np.abs(
        np.angle(np.exp(2j * np.pi * (frequencies - target)))
    ) / (2.0 * np.pi)
    target_index = int(np.argmin(circular_distance))

    # Ignore DC when selecting the dominant dynamical frequency.
    non_dc = np.where(np.abs(frequencies) > 1e-12)[0]
    dominant_index = int(non_dc[np.argmax(np.abs(spectrum[non_dc]))])

    excluded = {0, target_index}
    background = np.asarray(
        [abs(value) for index, value in enumerate(spectrum) if index not in excluded],
        dtype=float,
    )
    median_background = float(np.median(background)) if background.size else 0.0
    sample_index = np.arange(values.size)
    order_parameter = np.mean(
        values * np.exp(-2j * np.pi * target * sample_index)
    )
    # Evaluate the requested rational frequency directly; it need not coincide
    # with a finite-window FFT bin.
    target_amplitude = float(abs(order_parameter))
    peak_to_background = target_amplitude / max(median_background, 1e-15)
    return SpectralOrderDiagnostics(
        target_frequency=target,
        target_bin_frequency=float(frequencies[target_index]),
        target_amplitude=target_amplitude,
        dominant_frequency=float(frequencies[dominant_index]),
        dominant_amplitude=float(abs(spectrum[dominant_index])),
        locking_error=float(circular_distance[target_index]),
        peak_to_background=float(peak_to_background),
        complex_order_parameter=complex(order_parameter),
        samples=int(values.size),
    )


class FloquetTimeCrystal16:
    """Four-qubit repeated-map experiment with period-doubling diagnostics."""

    protocol_kind = "floquet_repeated_single_period_map"
    scientific_status = (
        "finite-size candidate signatures only; four qubits do not establish "
        "a thermodynamic time-crystalline phase"
    )

    def __init__(self, config: FloquetIsingConfig | None = None):
        self.config = config or FloquetIsingConfig()
        self._x_ops = tuple(operator_on_qubit(X, qubit) for qubit in range(N_QUBITS))
        self._z_ops = tuple(operator_on_qubit(Z, qubit) for qubit in range(N_QUBITS))
        self.magnetization_operator = sum(self._z_ops) / float(N_QUBITS)
        self.interaction_hamiltonian = self._build_interaction_hamiltonian()
        self.kick_hamiltonian = 0.5 * sum(self._x_ops)
        self.interaction_unitary = hermitian_unitary(
            self.interaction_hamiltonian,
            self.config.interaction_time,
        )
        self.kick_unitary = hermitian_unitary(
            self.kick_hamiltonian,
            self.config.actual_kick_angle,
        )
        # Rightmost U_kick acts first.
        self.floquet_unitary = self.interaction_unitary @ self.kick_unitary
        self._validate_unitary()

    def _build_interaction_hamiltonian(self) -> np.ndarray:
        hamiltonian = np.zeros((DIM, DIM), dtype=np.complex128)
        bonds = [(qubit, qubit + 1) for qubit in range(N_QUBITS - 1)]
        if self.config.periodic_boundary:
            bonds.append((N_QUBITS - 1, 0))
        for strength, (left, right) in zip(self.config.interaction_strengths, bonds):
            hamiltonian += float(strength) * two_qubit_product(Z, left, Z, right)
        for qubit, field_strength in enumerate(self.config.longitudinal_fields):
            hamiltonian += float(field_strength) * self._z_ops[qubit]
        for qubit, field_strength in enumerate(self.config.transverse_fields):
            hamiltonian += float(field_strength) * self._x_ops[qubit]
        return (hamiltonian + hamiltonian.conj().T) * 0.5

    def _validate_unitary(self) -> None:
        identity = np.eye(DIM, dtype=np.complex128)
        error = float(
            np.max(
                np.abs(
                    self.floquet_unitary.conj().T @ self.floquet_unitary - identity
                )
            )
        )
        if error > 1e-9:
            raise RuntimeError(f"Floquet unitary failed validation: error={error}")

    @staticmethod
    def product_density(index: int = 0) -> np.ndarray:
        return density_from_state(computational_basis_state(index))

    def step_density(self, rho: Any) -> np.ndarray:
        result = evolve_unitary(as_complex_matrix(rho), self.floquet_unitary)
        validate_density_matrix(result, raise_on_error=True)
        return result

    def run(
        self,
        periods: int,
        *,
        rho0: Any | None = None,
    ) -> FloquetTrajectory:
        count = int(periods)
        if count <= 0:
            raise ValueError("periods must be positive")
        initial = (
            self.product_density(0)
            if rho0 is None
            else as_complex_matrix(rho0)
        )
        validate_density_matrix(initial, raise_on_error=True)

        matrices = np.empty((count + 1, DIM, DIM), dtype=np.complex128)
        magnetization = np.empty(count + 1, dtype=float)
        overlap = np.empty(count + 1, dtype=float)
        purities = np.empty(count + 1, dtype=float)

        current = initial
        for tick in range(count + 1):
            matrices[tick] = current
            magnetization[tick] = float(
                np.real(expectation(current, self.magnetization_operator))
            )
            overlap[tick] = float(np.real(np.trace(initial @ current)))
            purities[tick] = purity(current)
            if tick < count:
                current = self.step_density(current)

        return FloquetTrajectory(
            ticks=np.arange(count + 1, dtype=int),
            density_matrices=matrices,
            magnetization_z=magnetization,
            return_overlap=overlap,
            purity=purities,
        )

    def subharmonic_diagnostics(
        self,
        trajectory: FloquetTrajectory,
        *,
        order: int = 2,
        winding: int = 1,
        discard: int = 0,
    ) -> SpectralOrderDiagnostics:
        n = int(order)
        q = int(winding)
        if n <= 0 or q <= 0:
            raise ValueError("order and winding must be positive")
        return analyze_temporal_order(
            # A run of N maps records both endpoints (N+1 states).  Analyze the
            # first N samples so an even-period run has an exact 1/2 FFT bin.
            trajectory.magnetization_z[:-1],
            target_frequency=q / n,
            discard=discard,
        )

    def quasienergy_pairing(
        self,
        *,
        separation_radians: float = np.pi,
    ) -> QuasienergyPairingDiagnostics:
        eigenvalues = np.linalg.eigvals(self.floquet_unitary)
        phases = np.mod(np.angle(eigenvalues), 2.0 * np.pi)
        separation = float(separation_radians) % (2.0 * np.pi)
        errors: list[float] = []
        for phase in phases:
            target = (phase + separation) % (2.0 * np.pi)
            distances = np.abs(
                np.angle(np.exp(1j * (phases - target)))
            )
            errors.append(float(np.min(distances)))
        mean_error = float(np.mean(errors))
        maximum_error = float(np.max(errors))
        normalization = max(min(separation, 2.0 * np.pi - separation), 1e-15)
        score = max(0.0, 1.0 - mean_error / normalization)
        return QuasienergyPairingDiagnostics(
            separation_radians=separation,
            mean_pairing_error=mean_error,
            maximum_pairing_error=maximum_error,
            normalized_pairing_score=score,
            eigenphases=np.sort(phases),
        )

    def rigidity_sweep(
        self,
        pulse_errors: Iterable[float],
        *,
        periods: int = 64,
        order: int = 2,
        winding: int = 1,
        discard: int = 0,
        rho0: Any | None = None,
    ) -> tuple[dict[str, float], ...]:
        results: list[dict[str, float]] = []
        for error in pulse_errors:
            model = FloquetTimeCrystal16(
                replace(self.config, pulse_error=float(error))
            )
            trajectory = model.run(periods, rho0=rho0)
            diagnostics = model.subharmonic_diagnostics(
                trajectory,
                order=order,
                winding=winding,
                discard=discard,
            )
            pairing = model.quasienergy_pairing(
                separation_radians=2.0 * np.pi * winding / order
            )
            results.append(
                {
                    "pulse_error": float(error),
                    "target_amplitude": diagnostics.target_amplitude,
                    "dominant_frequency": diagnostics.dominant_frequency,
                    "locking_error": diagnostics.locking_error,
                    "peak_to_background": diagnostics.peak_to_background,
                    "pairing_score": pairing.normalized_pairing_score,
                }
            )
        return tuple(results)

    def interaction_comparison(
        self,
        *,
        periods: int = 64,
        order: int = 2,
        rho0: Any | None = None,
    ) -> dict[str, SpectralOrderDiagnostics]:
        interacting = self.subharmonic_diagnostics(
            self.run(periods, rho0=rho0),
            order=order,
        )
        no_interaction = FloquetTimeCrystal16(
            replace(
                self.config,
                interaction_strengths=tuple(
                    0.0 for _ in self.config.interaction_strengths
                ),
            )
        )
        noninteracting = no_interaction.subharmonic_diagnostics(
            no_interaction.run(periods, rho0=rho0),
            order=order,
        )
        return {
            "interacting": interacting,
            "noninteracting": noninteracting,
        }

    def report(self, *, periods: int = 64, rho0: Any | None = None) -> dict[str, Any]:
        trajectory = self.run(periods, rho0=rho0)
        subharmonic = self.subharmonic_diagnostics(trajectory, order=2)
        pairing = self.quasienergy_pairing()
        return {
            "protocol_kind": self.protocol_kind,
            "scientific_status": self.scientific_status,
            "periods": int(periods),
            "kick_angle": self.config.actual_kick_angle,
            "pulse_error": self.config.pulse_error,
            "target_frequency": subharmonic.target_frequency,
            "target_amplitude": subharmonic.target_amplitude,
            "dominant_frequency": subharmonic.dominant_frequency,
            "peak_to_background": subharmonic.peak_to_background,
            "pi_pairing_score": pairing.normalized_pairing_score,
            "two_period_return_distance": trace_distance(
                trajectory.density_matrices[0],
                trajectory.density_matrices[2],
            )
            if periods >= 2
            else None,
        }
