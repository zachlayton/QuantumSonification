"""Explicit runtime controls for the authoritative density-matrix engine.

Controls are scheduled at absolute simulation times.  They are not derivative
terms: Hamiltonian and channel controls select the generator for subsequent
piecewise-constant evolution, while gate and projective controls are discrete
state interventions.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from types import MappingProxyType
from typing import Mapping, Protocol

import numpy as np

from qmw.measurement.projector import ProjectorBank

from .dynamics import Array, Hamiltonian, LindbladChannel, _density_matrix, _readonly


def _time(value: float) -> float:
    result = float(value)
    if not math.isfinite(result):
        raise ValueError("control time must be finite.")
    return result


@dataclass(frozen=True)
class ControlTransition:
    """Candidate state/generator after one discrete scheduled control."""

    rho: Array
    hamiltonian: Hamiltonian
    channels: tuple[LindbladChannel, ...]
    measurement_probability: float | None = None


class RuntimeControl(Protocol):
    """A deterministic intervention at one absolute simulation time."""

    time: float
    label: str
    kind: str

    def apply(
        self,
        rho: Array,
        hamiltonian: Hamiltonian,
        channels: tuple[LindbladChannel, ...],
    ) -> ControlTransition:
        """Return a candidate transition without mutating engine-owned state."""


@dataclass(frozen=True)
class HamiltonianControl:
    """Select a new fixed Hamiltonian for evolution after ``time``."""

    time: float
    hamiltonian: Hamiltonian | object
    label: str = "hamiltonian_update"
    kind: str = "hamiltonian"

    def __post_init__(self) -> None:
        object.__setattr__(self, "time", _time(self.time))
        object.__setattr__(
            self, "hamiltonian",
            self.hamiltonian if isinstance(self.hamiltonian, Hamiltonian) else Hamiltonian(self.hamiltonian),
        )
        if not str(self.label):
            raise ValueError("control label must be nonempty.")

    def apply(self, rho: Array, hamiltonian: Hamiltonian, channels: tuple[LindbladChannel, ...]) -> ControlTransition:
        if self.hamiltonian.dimension != hamiltonian.dimension:
            raise ValueError("Hamiltonian control dimension must match the engine.")
        return ControlTransition(_readonly(rho), self.hamiltonian, channels)


@dataclass(frozen=True)
class ChannelRateControl:
    """Update declared GKSL channel rates without changing their operators."""

    time: float
    rates: Mapping[str, float]
    label: str = "channel_rate_update"
    kind: str = "channel_rates"

    def __post_init__(self) -> None:
        object.__setattr__(self, "time", _time(self.time))
        normalized = {str(name): float(rate) for name, rate in dict(self.rates).items()}
        if not normalized or any(not name for name in normalized):
            raise ValueError("channel rate controls require nonempty channel labels.")
        if any(not math.isfinite(rate) or rate < 0.0 for rate in normalized.values()):
            raise ValueError("channel rates must be finite and nonnegative.")
        if not str(self.label):
            raise ValueError("control label must be nonempty.")
        object.__setattr__(self, "rates", MappingProxyType(normalized))

    def apply(self, rho: Array, hamiltonian: Hamiltonian, channels: tuple[LindbladChannel, ...]) -> ControlTransition:
        existing = {channel.label for channel in channels}
        unknown = set(self.rates).difference(existing)
        if unknown:
            raise ValueError(f"channel rate control names unknown channels: {sorted(unknown)!r}.")
        updated = tuple(
            LindbladChannel(channel.operator, self.rates.get(channel.label, channel.rate), channel.label)
            for channel in channels
        )
        return ControlTransition(_readonly(rho), hamiltonian, updated)


@dataclass(frozen=True)
class UnitaryGateControl:
    """Apply one explicit instantaneous gate ``rho -> U rho U†`` at ``time``."""

    time: float
    unitary: Array
    label: str = "unitary_gate"
    kind: str = "unitary_gate"

    def __post_init__(self) -> None:
        object.__setattr__(self, "time", _time(self.time))
        unitary = np.asarray(self.unitary, dtype=np.complex128)
        if unitary.ndim != 2 or unitary.shape[0] != unitary.shape[1] or not np.all(np.isfinite(unitary)):
            raise ValueError("gate must be a finite square matrix.")
        if not np.allclose(unitary.conj().T @ unitary, np.eye(unitary.shape[0]), atol=1.0e-10, rtol=0.0):
            raise ValueError("gate must be unitary.")
        if not str(self.label):
            raise ValueError("control label must be nonempty.")
        object.__setattr__(self, "unitary", _readonly(unitary))

    def apply(self, rho: Array, hamiltonian: Hamiltonian, channels: tuple[LindbladChannel, ...]) -> ControlTransition:
        if self.unitary.shape != hamiltonian.matrix.shape:
            raise ValueError("gate dimension must match the engine.")
        evolved = self.unitary @ rho @ self.unitary.conj().T
        return ControlTransition(_readonly(_density_matrix(evolved)), hamiltonian, channels)


@dataclass(frozen=True)
class ProjectiveMeasurementControl:
    """Apply one explicit conditioned outcome from a complete projective PVM.

    The selected outcome is supplied by the caller, making the control
    deterministic and auditable.  Sampling policy belongs outside the engine.
    """

    time: float
    bank: ProjectorBank
    outcome: int | str
    label: str = "projective_measurement"
    kind: str = "projective_measurement"

    def __post_init__(self) -> None:
        object.__setattr__(self, "time", _time(self.time))
        if not isinstance(self.bank, ProjectorBank) or not self.bank.complete or not self.bank.orthogonal:
            raise ValueError("measurement requires a complete orthogonal ProjectorBank.")
        index = self._outcome_index()
        if not 0 <= index < len(self.bank.projectors):
            raise ValueError("measurement outcome is outside the projector bank.")
        if not str(self.label):
            raise ValueError("control label must be nonempty.")

    def _outcome_index(self) -> int:
        if isinstance(self.outcome, str):
            try:
                return self.bank.names.index(self.outcome)
            except ValueError as error:
                raise ValueError("measurement outcome name is not in the projector bank.") from error
        if int(self.outcome) != self.outcome:
            raise ValueError("measurement outcome must be an integer index or projector name.")
        return int(self.outcome)

    @property
    def outcome_index(self) -> int:
        return self._outcome_index()

    def apply(self, rho: Array, hamiltonian: Hamiltonian, channels: tuple[LindbladChannel, ...]) -> ControlTransition:
        if self.bank.dimension != hamiltonian.dimension:
            raise ValueError("measurement projector bank must match the engine dimension.")
        projector = self.bank.projectors[self.outcome_index].matrix
        probability = complex(np.trace(projector @ rho))
        if abs(probability.imag) > 1.0e-10:
            raise ValueError("measurement probability was unexpectedly complex.")
        value = float(probability.real)
        if value <= 1.0e-12:
            raise ValueError("cannot condition a measurement on a zero-probability outcome.")
        collapsed = projector @ rho @ projector / value
        return ControlTransition(
            _readonly(_density_matrix(collapsed)), hamiltonian, channels,
            measurement_probability=value,
        )


__all__ = [
    "ChannelRateControl", "ControlTransition", "HamiltonianControl",
    "ProjectiveMeasurementControl", "RuntimeControl", "UnitaryGateControl",
]
