"""Four-bit maximal LFSR as a clock, unitary permutation, and rho operator.

The default primitive polynomial is x^4 + x + 1.  With state-vector components
[q0, q1, q2, q3], where q0 is the least-significant basis bit, the recurrence is

    s[k+4] = s[k+1] XOR s[k].

The resulting permutation has one 15-state nonzero orbit and fixes |0000>:

    P_A ~= X_15 direct-sum 1.

This is an explicitly programmed finite-state recurrence.  It must not be
reported as spontaneous time-translation symmetry breaking.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import gcd
from typing import Iterable, Sequence

import numpy as np

try:
    from .qmw_temporal_core16_v1 import (
        DIM,
        as_complex_matrix,
        evolve_unitary,
        qft_matrix,
        validate_density_matrix,
    )
except ImportError:  # pragma: no cover - permits direct script use
    from qmw_temporal_core16_v1 import (
        DIM,
        as_complex_matrix,
        evolve_unitary,
        qft_matrix,
        validate_density_matrix,
    )


def bits_from_int(state: int, *, width: int = 4) -> np.ndarray:
    integer = int(state)
    if not 0 <= integer < (1 << width):
        raise ValueError(f"state must be in [0, {(1 << width) - 1}]")
    return np.asarray([(integer >> bit) & 1 for bit in range(width)], dtype=np.uint8)


def int_from_bits(bits: Sequence[int]) -> int:
    result = 0
    for index, bit in enumerate(bits):
        result |= (int(bit) & 1) << index
    return result


def companion_matrix(
    *,
    degree: int = 4,
    feedback_exponents: Iterable[int] = (1, 0),
) -> np.ndarray:
    """Build the GF(2) recurrence matrix for x^n + sum_i x^i."""

    n = int(degree)
    if n <= 0:
        raise ValueError("degree must be positive")
    coefficients = np.zeros(n, dtype=np.uint8)
    for exponent in feedback_exponents:
        index = int(exponent)
        if not 0 <= index < n:
            raise ValueError(f"feedback exponent must be in [0, {n - 1}]")
        coefficients[index] ^= 1
    if not np.any(coefficients):
        raise ValueError("at least one feedback coefficient is required")

    matrix = np.zeros((n, n), dtype=np.uint8)
    for row in range(n - 1):
        matrix[row, row + 1] = 1
    matrix[n - 1, :] = coefficients
    return matrix


@dataclass(frozen=True)
class LFSRSnapshot:
    tick: int
    state: int
    bits_q0_first: tuple[int, ...]
    output_bit: int
    orbit_index: int | None
    phase_radians: float | None
    decimation: int


class LFSRClock4:
    """Primitive four-bit LFSR with exact Hilbert-space embedding."""

    width = 4
    hilbert_dim = DIM
    maximal_period = (1 << width) - 1
    protocol_kind = "programmed_maximal_lfsr"

    def __init__(
        self,
        *,
        seed: int = 1,
        feedback_exponents: Iterable[int] = (1, 0),
        output_qubit: int = 0,
        decimation: int = 1,
    ):
        self.matrix_gf2 = companion_matrix(
            degree=self.width,
            feedback_exponents=feedback_exponents,
        )
        self.feedback_exponents = tuple(int(x) for x in feedback_exponents)
        self.output_qubit = int(output_qubit)
        if not 0 <= self.output_qubit < self.width:
            raise ValueError("output_qubit must be in [0, 3]")
        self.decimation = int(decimation)
        if self.decimation <= 0:
            raise ValueError("decimation must be positive")
        self.seed = self._validate_seed(seed)
        self._state = self.seed
        self._tick = 0
        self._base_orbit = self._generate_base_orbit(self.seed)
        if len(self._base_orbit) != self.maximal_period:
            raise ValueError(
                "feedback polynomial is not primitive for this convention: "
                f"nonzero orbit length is {len(self._base_orbit)}, "
                f"expected {self.maximal_period}"
            )
        self._orbit_index = {state: index for index, state in enumerate(self._base_orbit)}
        self._permutation = self._build_permutation()

    @staticmethod
    def _validate_seed(seed: int) -> int:
        integer = int(seed)
        if not 0 < integer < DIM:
            raise ValueError("maximal LFSR seed must be a nonzero four-bit word")
        return integer

    def step_state_once(self, state: int) -> int:
        bits = bits_from_int(state, width=self.width)
        next_bits = (self.matrix_gf2 @ bits) % 2
        return int_from_bits(next_bits)

    def step_state(self, state: int, steps: int = 1) -> int:
        result = int(state)
        for _ in range(int(steps)):
            result = self.step_state_once(result)
        return result

    def _generate_base_orbit(self, seed: int) -> tuple[int, ...]:
        states: list[int] = []
        seen: set[int] = set()
        state = int(seed)
        while state not in seen:
            seen.add(state)
            states.append(state)
            state = self.step_state_once(state)
        if state != seed:
            raise ValueError("LFSR transition entered a different cycle")
        return tuple(states)

    def orbit(self, *, decimation: int | None = None) -> tuple[int, ...]:
        d = self.decimation if decimation is None else int(decimation)
        if d <= 0:
            raise ValueError("decimation must be positive")
        return tuple(
            self._base_orbit[(d * index) % self.maximal_period]
            for index in range(self.maximal_period // gcd(d, self.maximal_period))
        )

    @property
    def full_cycle_decimation(self) -> bool:
        return gcd(self.decimation, self.maximal_period) == 1

    @property
    def tick(self) -> int:
        return self._tick

    @property
    def state(self) -> int:
        return self._state

    def snapshot(self) -> LFSRSnapshot:
        bits = bits_from_int(self._state, width=self.width)
        orbit_index = self._orbit_index.get(self._state)
        phase = (
            2.0 * np.pi * orbit_index / self.maximal_period
            if orbit_index is not None
            else None
        )
        return LFSRSnapshot(
            tick=self._tick,
            state=self._state,
            bits_q0_first=tuple(int(bit) for bit in bits),
            output_bit=int(bits[self.output_qubit]),
            orbit_index=orbit_index,
            phase_radians=phase,
            decimation=self.decimation,
        )

    def advance(self, steps: int = 1) -> LFSRSnapshot:
        count = int(steps)
        if count < 0:
            raise ValueError("steps must be nonnegative")
        self._state = self.step_state(self._state, count * self.decimation)
        self._tick += count
        return self.snapshot()

    def reset(self, *, seed: int | None = None) -> LFSRSnapshot:
        if seed is not None:
            self.seed = self._validate_seed(seed)
            if seed not in self._orbit_index:
                raise ValueError("seed is not in the configured maximal orbit")
        self._state = self.seed
        self._tick = 0
        return self.snapshot()

    def _build_permutation(self) -> np.ndarray:
        permutation = np.zeros((DIM, DIM), dtype=np.complex128)
        for state in range(DIM):
            next_state = self.step_state_once(state)
            permutation[next_state, state] = 1.0
        return permutation

    def permutation_matrix(self, *, decimation: int | None = None) -> np.ndarray:
        d = self.decimation if decimation is None else int(decimation)
        if d <= 0:
            raise ValueError("decimation must be positive")
        return np.linalg.matrix_power(self._permutation, d)

    def apply_to_density(self, rho: np.ndarray, *, decimation: int | None = None) -> np.ndarray:
        matrix = as_complex_matrix(rho)
        permutation = self.permutation_matrix(decimation=decimation)
        result = evolve_unitary(matrix, permutation)
        validate_density_matrix(result, raise_on_error=True)
        return result

    def joint_clock_system_unitary(
        self,
        operator_zero: np.ndarray,
        operator_one: np.ndarray,
    ) -> np.ndarray:
        """Build the 8-qubit autonomous clock-system step.

        Joint basis indexing follows the established QMW history convention:

            joint_index = system_index + 16 * clock_index

        The operation is

            |x>_C |psi>_S -> |A x>_C V_{b(x)} |psi>_S.

        Repeating this one unitary internalizes the full LFSR control sequence.
        It remains a programmed finite-state drive, not an emergent time crystal.
        """

        v0 = as_complex_matrix(operator_zero)
        v1 = as_complex_matrix(operator_one)
        identity = np.eye(DIM, dtype=np.complex128)
        for name, operator in (("operator_zero", v0), ("operator_one", v1)):
            error = float(np.max(np.abs(operator.conj().T @ operator - identity)))
            if error > 1e-9:
                raise ValueError(f"{name} must be unitary; error={error}")

        joint_dim = DIM * DIM
        joint = np.zeros((joint_dim, joint_dim), dtype=np.complex128)
        for clock_state in range(DIM):
            bits = bits_from_int(clock_state, width=self.width)
            controlled = v1 if bits[self.output_qubit] else v0
            next_clock = self.step_state_once(clock_state)
            input_start = DIM * clock_state
            output_start = DIM * next_clock
            joint[
                output_start : output_start + DIM,
                input_start : input_start + DIM,
            ] = controlled
        return joint

    def coherence_orbits(self) -> tuple[tuple[tuple[int, int], ...], ...]:
        """Partition the 120 Hermitian coherence edges under one LFSR step."""

        remaining = {(left, right) for left in range(DIM) for right in range(left + 1, DIM)}
        orbits: list[tuple[tuple[int, int], ...]] = []
        while remaining:
            start = min(remaining)
            current = start
            orbit: list[tuple[int, int]] = []
            while current not in orbit:
                orbit.append(current)
                left = self.step_state_once(current[0])
                right = self.step_state_once(current[1])
                current = (min(left, right), max(left, right))
            for edge in orbit:
                remaining.discard(edge)
            orbits.append(tuple(orbit))
        return tuple(sorted(orbits, key=lambda item: (len(item), item[0])))

    def chronos_to_aion_matrix(self) -> np.ndarray:
        """15-point QFT for the ordered nonzero LFSR orbit."""

        return qft_matrix(self.maximal_period)

    def orbit_signal(self, rho: np.ndarray, coherence_orbit: int) -> np.ndarray:
        matrix = as_complex_matrix(rho)
        orbits = self.coherence_orbits()
        index = int(coherence_orbit)
        if not 0 <= index < len(orbits):
            raise ValueError(f"coherence_orbit must be in [0, {len(orbits) - 1}]")
        return np.asarray([matrix[left, right] for left, right in orbits[index]])

    def aion_spectrum(self, rho: np.ndarray, coherence_orbit: int) -> np.ndarray:
        signal = self.orbit_signal(rho, coherence_orbit)
        return np.fft.fft(signal) / signal.size

    def structural_report(self) -> dict[str, object]:
        permutation = self.permutation_matrix(decimation=1)
        coherence_orbits = self.coherence_orbits()
        terms = [f"x^{self.width}"]
        for exponent in sorted(self.feedback_exponents, reverse=True):
            terms.append("1" if exponent == 0 else ("x" if exponent == 1 else f"x^{exponent}"))
        return {
            "protocol_kind": self.protocol_kind,
            "primitive_polynomial": " + ".join(terms),
            "feedback_exponents": self.feedback_exponents,
            "period": self.maximal_period,
            "zero_fixed": self.step_state_once(0) == 0,
            "nonzero_states_visited": len(self._base_orbit),
            "unitarity_error": float(
                np.max(np.abs(permutation.conj().T @ permutation - np.eye(DIM)))
            ),
            "coherence_orbit_lengths": tuple(len(orbit) for orbit in coherence_orbits),
            "full_cycle_decimation": self.full_cycle_decimation,
        }
