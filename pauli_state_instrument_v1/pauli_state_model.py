"""State-address, spinor, and fermionic antisymmetry model.

This module supplies the non-audio laws of the first Pauli State Instrument.
It distinguishes a strong-field uncoupled address (n, l, m_l, m_s) from a
weak-field coupled address (n, l, j, m_j), enforces one electron per complete
uncoupled address, and exposes the spinorial and Slater-overlap quantities used
by the Max prototype.
"""

from __future__ import annotations

from dataclasses import dataclass
import cmath
import math
import random


_TOLERANCE = 1.0e-12


@dataclass(frozen=True, order=True)
class ElectronAddress:
    """A complete one-electron address in the uncoupled basis.

    ``spin_twice`` stores 2*m_s exactly and must therefore be -1 or +1.
    """

    n: int
    l: int
    m_l: int
    spin_twice: int

    def __post_init__(self) -> None:
        if self.n < 1:
            raise ValueError("n must be positive")
        if not 0 <= self.l < self.n:
            raise ValueError("l must satisfy 0 <= l < n")
        if not -self.l <= self.m_l <= self.l:
            raise ValueError("m_l must satisfy -l <= m_l <= l")
        if self.spin_twice not in (-1, 1):
            raise ValueError("spin_twice must be -1 or +1")

    @property
    def m_s(self) -> float:
        return self.spin_twice / 2.0

    @property
    def m_j_twice(self) -> int:
        return 2 * self.m_l + self.spin_twice

    @property
    def label(self) -> str:
        arrow = "up" if self.spin_twice > 0 else "down"
        return f"({self.n},{self.l},{self.m_l},{arrow})"


@dataclass(frozen=True, order=True)
class CoupledAddress:
    """One-electron address in an LS-coupled spin-orbit basis."""

    n: int
    l: int
    j_twice: int
    m_j_twice: int

    def __post_init__(self) -> None:
        if self.n < 1 or not 0 <= self.l < self.n:
            raise ValueError("invalid n,l values")
        allowed_j = {2 * self.l + 1}
        if self.l > 0:
            allowed_j.add(2 * self.l - 1)
        if self.j_twice not in allowed_j:
            raise ValueError("j must equal l +/- 1/2")
        if abs(self.m_j_twice) > self.j_twice:
            raise ValueError("|m_j| cannot exceed j")
        if (self.j_twice - self.m_j_twice) % 2:
            raise ValueError("m_j must advance in integer steps")

    @property
    def j(self) -> float:
        return self.j_twice / 2.0

    @property
    def m_j(self) -> float:
        return self.m_j_twice / 2.0


def coupled_components(state: CoupledAddress) -> tuple[tuple[ElectronAddress, float], ...]:
    """Expand |n,l,j,m_j> in the |n,l,m_l,m_s> basis.

    The returned real amplitudes follow a fixed Condon-Shortley convention.
    Zero-coefficient or out-of-range components are omitted.
    """

    l_value = state.l
    m_value = state.m_j
    denominator = 2.0 * l_value + 1.0
    candidates: list[tuple[int, int, float]]
    if state.j_twice == 2 * l_value + 1:
        candidates = [
            (round(m_value - 0.5), 1, math.sqrt((l_value + m_value + 0.5) / denominator)),
            (round(m_value + 0.5), -1, math.sqrt((l_value - m_value + 0.5) / denominator)),
        ]
    else:
        candidates = [
            (round(m_value - 0.5), 1, -math.sqrt((l_value - m_value + 0.5) / denominator)),
            (round(m_value + 0.5), -1, math.sqrt((l_value + m_value + 0.5) / denominator)),
        ]

    result = []
    for m_l, spin_twice, amplitude in candidates:
        if abs(amplitude) <= _TOLERANCE or not -l_value <= m_l <= l_value:
            continue
        result.append((ElectronAddress(state.n, l_value, m_l, spin_twice), amplitude))
    return tuple(result)


@dataclass(frozen=True)
class OccupancyResult:
    accepted: bool
    address: ElectronAddress
    reason: str


class PauliStateLedger:
    """A deterministic ledger with maximum occupation one per full address."""

    def __init__(self) -> None:
        self._occupied: set[ElectronAddress] = set()
        self.rejected_attempts = 0

    @property
    def occupied(self) -> tuple[ElectronAddress, ...]:
        return tuple(sorted(self._occupied))

    def occupy(self, address: ElectronAddress) -> OccupancyResult:
        if address in self._occupied:
            self.rejected_attempts += 1
            return OccupancyResult(False, address, "excluded: complete state already occupied")
        self._occupied.add(address)
        return OccupancyResult(True, address, "occupied")

    def release(self, address: ElectronAddress) -> bool:
        if address not in self._occupied:
            return False
        self._occupied.remove(address)
        return True

    def clear(self) -> None:
        self._occupied.clear()

    def fill_subshell(self, n: int, l: int) -> tuple[OccupancyResult, ...]:
        results = []
        for m_l in range(-l, l + 1):
            for spin_twice in (-1, 1):
                results.append(self.occupy(ElectronAddress(n, l, m_l, spin_twice)))
        return tuple(results)

    def subshell_capacity(self, l: int) -> int:
        return 2 * (2 * l + 1)

    def subshell_closed(self, n: int, l: int) -> bool:
        count = sum(address.n == n and address.l == l for address in self._occupied)
        return count == self.subshell_capacity(l)


@dataclass(frozen=True)
class Spinor:
    """Normalized two-component Pauli spinor."""

    alpha: complex = 1.0 + 0.0j
    beta: complex = 0.0 + 0.0j

    def __post_init__(self) -> None:
        norm = math.sqrt(abs(self.alpha) ** 2 + abs(self.beta) ** 2)
        if norm <= _TOLERANCE:
            raise ValueError("spinor cannot be the zero vector")
        object.__setattr__(self, "alpha", self.alpha / norm)
        object.__setattr__(self, "beta", self.beta / norm)

    def inner(self, other: "Spinor") -> complex:
        return self.alpha.conjugate() * other.alpha + self.beta.conjugate() * other.beta

    def rotate_y(self, angle_radians: float) -> "Spinor":
        half = angle_radians / 2.0
        cosine = math.cos(half)
        sine = math.sin(half)
        return Spinor(
            cosine * self.alpha - sine * self.beta,
            sine * self.alpha + cosine * self.beta,
        )

    def measurement_probabilities(self, theta: float, phi: float) -> tuple[float, float]:
        plus = Spinor(math.cos(theta / 2.0), cmath.exp(1.0j * phi) * math.sin(theta / 2.0))
        probability_plus = min(1.0, max(0.0, abs(plus.inner(self)) ** 2))
        return probability_plus, 1.0 - probability_plus

    def measure(self, theta: float, phi: float, rng: random.Random | None = None) -> tuple[int, "Spinor"]:
        source = rng or random.Random()
        plus_probability, _ = self.measurement_probabilities(theta, phi)
        if source.random() < plus_probability:
            return 1, Spinor(math.cos(theta / 2.0), cmath.exp(1.0j * phi) * math.sin(theta / 2.0))
        return -1, Spinor(-cmath.exp(-1.0j * phi) * math.sin(theta / 2.0), math.cos(theta / 2.0))

    def coherent_reference_intensity(self, reference: "Spinor") -> float:
        """Interference intensity of equally weighted state and reference paths."""

        summed_alpha = self.alpha + reference.alpha
        summed_beta = self.beta + reference.beta
        return (abs(summed_alpha) ** 2 + abs(summed_beta) ** 2) / 4.0


def antisymmetric_norm(first: Spinor, second: Spinor, orbital_overlap: complex = 1.0 + 0.0j) -> float:
    """Return the norm of a normalized two-fermion Slater wedge.

    For normalized one-particle states this is ``sqrt(1-|<a|b>|^2)``.
    ``orbital_overlap`` allows spatial distinguishability to reduce the total
    overlap independently of spin.
    """

    total_overlap = orbital_overlap * first.inner(second)
    return math.sqrt(max(0.0, 1.0 - min(1.0, abs(total_overlap) ** 2)))


def strong_field_audio_frequency(
    address: ElectronAddress,
    *,
    base_hz: float,
    orbital_spacing_hz: float,
    field_t: float,
    zeeman_hz_per_t: float,
) -> float:
    """Perceptual strong-field mapping proportional to m_l + 2*m_s."""

    magnetic_factor = address.m_l + 2.0 * address.m_s
    return base_hz + orbital_spacing_hz * address.m_l + field_t * zeeman_hz_per_t * magnetic_factor


def two_p_addresses() -> tuple[ElectronAddress, ...]:
    return tuple(
        ElectronAddress(2, 1, m_l, spin_twice)
        for m_l in (-1, 0, 1)
        for spin_twice in (-1, 1)
    )
