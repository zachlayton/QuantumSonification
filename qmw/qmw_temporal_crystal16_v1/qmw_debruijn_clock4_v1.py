"""Order-four binary de Bruijn clock.

Unlike a linear four-bit maximal LFSR, this nonlinear/table-defined clock visits
all sixteen four-bit words, including 0000, in one cycle.  It is therefore the
exact full-cycle alternative when the 16 score columns must align one-to-one
with the 16 computational basis states.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

try:
    from .qmw_temporal_core16_v1 import DIM, as_complex_matrix, evolve_unitary
    from .qmw_lfsr_clock4_v1 import bits_from_int, int_from_bits
except ImportError:  # pragma: no cover
    from qmw_temporal_core16_v1 import DIM, as_complex_matrix, evolve_unitary
    from qmw_lfsr_clock4_v1 import bits_from_int, int_from_bits


def de_bruijn_binary(order: int) -> tuple[int, ...]:
    """Fredricksen-Kessler-Maiorana construction for B(2, order)."""

    n = int(order)
    if n <= 0:
        raise ValueError("order must be positive")
    alphabet = 2
    a = [0] * (alphabet * n)
    sequence: list[int] = []

    def db(t: int, period: int) -> None:
        if t > n:
            if n % period == 0:
                sequence.extend(a[1 : period + 1])
            return
        a[t] = a[t - period]
        db(t + 1, period)
        for value in range(a[t - period] + 1, alphabet):
            a[t] = value
            db(t + 1, t)

    db(1, 1)
    return tuple(sequence)


def de_bruijn_state_orbit(order: int = 4) -> tuple[int, ...]:
    sequence = de_bruijn_binary(order)
    states: list[int] = []
    for start in range(len(sequence)):
        window = [sequence[(start + offset) % len(sequence)] for offset in range(order)]
        states.append(int_from_bits(window))
    if len(set(states)) != 1 << order:
        raise RuntimeError("constructed sequence did not cover every binary word")
    return tuple(states)


@dataclass(frozen=True)
class DeBruijnSnapshot:
    tick: int
    index: int
    state: int
    bits_q0_first: tuple[int, ...]
    output_bit: int
    phase_radians: float


class DeBruijnClock4:
    width = 4
    period = DIM
    protocol_kind = "programmed_nonlinear_debruijn16"

    def __init__(self, *, start_index: int = 0, output_qubit: int = 0):
        self.orbit = de_bruijn_state_orbit(self.width)
        self.output_qubit = int(output_qubit)
        if not 0 <= self.output_qubit < self.width:
            raise ValueError("output_qubit must be in [0, 3]")
        self._index = int(start_index) % self.period
        self._tick = 0
        self._successor = {
            state: self.orbit[(index + 1) % self.period]
            for index, state in enumerate(self.orbit)
        }
        self._permutation = self._build_permutation()

    @property
    def state(self) -> int:
        return self.orbit[self._index]

    def snapshot(self) -> DeBruijnSnapshot:
        bits = bits_from_int(self.state, width=self.width)
        return DeBruijnSnapshot(
            tick=self._tick,
            index=self._index,
            state=self.state,
            bits_q0_first=tuple(int(bit) for bit in bits),
            output_bit=int(bits[self.output_qubit]),
            phase_radians=2.0 * np.pi * self._index / self.period,
        )

    def advance(self, steps: int = 1) -> DeBruijnSnapshot:
        count = int(steps)
        if count < 0:
            raise ValueError("steps must be nonnegative")
        self._tick += count
        self._index = (self._index + count) % self.period
        return self.snapshot()

    def successor(self, state: int) -> int:
        try:
            return self._successor[int(state)]
        except KeyError as exc:
            raise ValueError("state must be a four-bit word") from exc

    def _build_permutation(self) -> np.ndarray:
        permutation = np.zeros((DIM, DIM), dtype=np.complex128)
        for state in range(DIM):
            permutation[self.successor(state), state] = 1.0
        return permutation

    def permutation_matrix(self, steps: int = 1) -> np.ndarray:
        return np.linalg.matrix_power(self._permutation, int(steps))

    def apply_to_density(self, rho: np.ndarray, *, steps: int = 1) -> np.ndarray:
        matrix = as_complex_matrix(rho)
        return evolve_unitary(matrix, self.permutation_matrix(steps))

