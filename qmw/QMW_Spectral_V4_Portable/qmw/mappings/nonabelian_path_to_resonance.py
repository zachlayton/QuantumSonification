"""Declared odd/even harmonic excitation from ordered Pauli commutators.

The source is a read-only ``K=-i[A,B]`` observation.  Pauli coefficient
magnitude supplies excitation amount; reversing an ordered pair reverses the
coefficient sign and therefore swaps the declared odd/even harmonic balance.
No resonator frequency, quantum state, or future operator is changed here.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from types import MappingProxyType
from typing import Mapping

import numpy as np

from qmw.performance.logical_router import LogicalExcitationFrame
from qmw.quantum.nonabelian_path import NonAbelianCommutatorFrame
from qmw.quantum.pauli_basis import normalize_pauli_label


_FAMILY_SIZE = 8
_LANE_COUNT = 16


def _positive(name: str, value: float) -> float:
    result = float(value)
    if not math.isfinite(result) or result <= 0.0:
        raise ValueError(f"{name} must be finite and positive.")
    return result


def _nonnegative(name: str, value: float) -> float:
    result = float(value)
    if not math.isfinite(result) or result < 0.0:
        raise ValueError(f"{name} must be finite and nonnegative.")
    return result


@dataclass(frozen=True)
class PauliOddEvenRoutingConfig:
    """Explicit label-to-harmonic-family profiles; each profile sums to one."""

    profile_by_pauli_label: Mapping[str, tuple[float, ...]]
    sustain_gain: float = 1.0
    order_softness: float = 1.0
    transient_gain: float = 1.0
    identifier: str = "qmw.nonabelian.odd_even_harmonic_routes.v1"

    def __post_init__(self) -> None:
        if not self.identifier.strip():
            raise ValueError("odd/even routing identifier must be nonempty.")
        profiles: dict[str, tuple[float, ...]] = {}
        for raw_label, raw_profile in dict(self.profile_by_pauli_label).items():
            label = normalize_pauli_label(raw_label)
            profile = tuple(float(value) for value in raw_profile)
            if len(profile) != _FAMILY_SIZE or not all(math.isfinite(value) and value >= 0.0 for value in profile):
                raise ValueError("each Pauli odd/even profile needs eight finite nonnegative weights.")
            if not math.isclose(sum(profile), 1.0, rel_tol=0.0, abs_tol=1.0e-9):
                raise ValueError("each Pauli odd/even profile must sum to one.")
            profiles[label] = profile
        object.__setattr__(self, "profile_by_pauli_label", MappingProxyType(profiles))
        object.__setattr__(self, "sustain_gain", _nonnegative("sustain_gain", self.sustain_gain))
        object.__setattr__(self, "order_softness", _positive("order_softness", self.order_softness))
        object.__setattr__(self, "transient_gain", _nonnegative("transient_gain", self.transient_gain))
        object.__setattr__(self, "identifier", self.identifier.strip())


@dataclass(frozen=True)
class NonAbelianResonantExcitationFrame:
    """Downstream odd/even excitation plus a separate transient descriptor."""

    source_revision: int
    logical_time: float
    sequence_index: int
    routing_id: str
    sustained_excitation: np.ndarray
    transient_excitation: np.ndarray
    odd_family_energy: float
    even_family_energy: float
    transient_derivative_available: bool
    logical_excitation: LogicalExcitationFrame
    frequency_policy: str = "fixed_resonator_frequencies_unchanged"
    provenance: str = "downstream_read_only_nonabelian_commutator_to_odd_even_excitation"

    def __post_init__(self) -> None:
        sustain = np.asarray(self.sustained_excitation, dtype=float)
        transient = np.asarray(self.transient_excitation, dtype=float)
        if sustain.shape != (_LANE_COUNT,) or transient.shape != (_LANE_COUNT,):
            raise ValueError("non-Abelian resonant excitation requires sixteen lanes.")
        if not np.all(np.isfinite(sustain)) or not np.all(np.isfinite(transient)):
            raise ValueError("non-Abelian resonant excitation values must be finite.")
        if np.min(sustain) < 0.0 or np.min(transient) < 0.0:
            raise ValueError("non-Abelian excitation values must be nonnegative.")
        if not isinstance(self.logical_excitation, LogicalExcitationFrame):
            raise ValueError("non-Abelian resonant frame requires a LogicalExcitationFrame.")
        if self.logical_excitation.source_revision != int(self.source_revision) or not math.isclose(self.logical_excitation.logical_time, float(self.logical_time), abs_tol=1.0e-9):
            raise ValueError("logical excitation must retain commutator revision and time.")
        object.__setattr__(self, "sustained_excitation", np.array(sustain, copy=True))
        object.__setattr__(self, "transient_excitation", np.array(transient, copy=True))


def nonabelian_path_to_resonant_excitation(
    frame: NonAbelianCommutatorFrame,
    routing: PauliOddEvenRoutingConfig,
    *, previous: NonAbelianResonantExcitationFrame | None = None,
) -> NonAbelianResonantExcitationFrame:
    """Map a commutator frame into odd/even harmonic lanes.

    For each generated Pauli coefficient ``c``:

    ``m = sustain_gain * abs(c)``
    ``s = tanh(c / order_softness)``
    ``odd = m * (1 + s) / 2`` and ``even = m * (1 - s) / 2``.

    Lanes 0,2,...,14 are H1,H3,...,H15; lanes 1,3,...,15 are
    H2,H4,...,H16.  A reversal changes ``c`` to ``-c`` and swaps those family
    amounts while preserving the explicitly declared within-family profile.
    """

    if not isinstance(frame, NonAbelianCommutatorFrame):
        raise TypeError("frame must be a NonAbelianCommutatorFrame.")
    if not isinstance(routing, PauliOddEvenRoutingConfig):
        raise TypeError("routing must be a PauliOddEvenRoutingConfig.")
    sustain = np.zeros(_LANE_COUNT, dtype=float)
    for term in frame.generated_terms:
        try:
            profile = np.asarray(routing.profile_by_pauli_label[term.label], dtype=float)
        except KeyError as error:
            raise KeyError(f"no odd/even harmonic route is declared for generated Pauli term {term.label!r}.") from error
        coefficient = float(term.coefficient)
        amount = routing.sustain_gain * abs(coefficient)
        order_balance = math.tanh(coefficient / routing.order_softness)
        sustain[0::2] += amount * (1.0 + order_balance) * 0.5 * profile
        sustain[1::2] += amount * (1.0 - order_balance) * 0.5 * profile

    transient = np.zeros(_LANE_COUNT, dtype=float)
    derivative_available = False
    if previous is not None:
        if not isinstance(previous, NonAbelianResonantExcitationFrame):
            raise TypeError("previous must be a NonAbelianResonantExcitationFrame.")
        if previous.routing_id != routing.identifier:
            raise ValueError("previous non-Abelian excitation must use the same routing configuration.")
        interval = float(frame.logical_time) - previous.logical_time
        if interval < 0.0:
            raise ValueError("previous non-Abelian excitation cannot come from the future.")
        if interval > 0.0:
            transient = routing.transient_gain * np.abs(sustain - previous.sustained_excitation) / interval
            derivative_available = True

    logical = LogicalExcitationFrame(
        source_id="qmw.nonabelian.pauli_path", source_revision=frame.source_revision,
        logical_time=frame.logical_time, values=sustain,
        semantics="ordered Pauli commutator odd/even harmonic sustained excitation",
    )
    return NonAbelianResonantExcitationFrame(
        source_revision=frame.source_revision, logical_time=frame.logical_time,
        sequence_index=frame.sequence_index, routing_id=routing.identifier,
        sustained_excitation=sustain, transient_excitation=transient,
        odd_family_energy=float(np.sum(sustain[0::2])),
        even_family_energy=float(np.sum(sustain[1::2])),
        transient_derivative_available=derivative_available,
        logical_excitation=logical,
    )


__all__ = [
    "NonAbelianResonantExcitationFrame", "PauliOddEvenRoutingConfig",
    "nonabelian_path_to_resonant_excitation",
]
