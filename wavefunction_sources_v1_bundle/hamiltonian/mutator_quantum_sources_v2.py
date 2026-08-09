"""Backward-compatible QuantumSonification mutator with lazy wavefunction sources.

This is a new v2 file: it does not overwrite ``mutator_quantum_sources_v1.py``.
The original names ``audio``, ``hydrogen_spectrum``, ``hydrogen_orbital``, and
``schrodinger_packet`` remain valid.  New continuous-field sources are created
only when selected, so a 3D grid does not consume memory unless it is used.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Any, Mapping, Optional

import numpy as np

from hamiltonian.hamiltonian_state import HamiltonianState

try:
    from excitation.wavefunction_sources_v1 import (
        WAVEFUNCTION_SOURCE_NAMES,
        WavefunctionFrame,
        create_wavefunction_source,
    )
except ImportError:  # Allows direct testing beside wavefunction_sources_v1.py.
    from wavefunction_sources_v1 import (  # type: ignore
        WAVEFUNCTION_SOURCE_NAMES,
        WavefunctionFrame,
        create_wavefunction_source,
    )


SOURCE_NAMES = (
    "audio",
    "hydrogen_spectrum",
    "hydrogen_orbital",
    *WAVEFUNCTION_SOURCE_NAMES,
)


@dataclass(frozen=True)
class QuantumDescriptor:
    """Original normalized four-field contract retained for legacy sources."""

    energy: float
    phase: float
    probability: float
    structure: float


class HydrogenSpectrumSource:
    """Original discrete Rydberg transition event source.

    This remains available for compatibility but is intentionally kept outside
    the wavefunction registry because it does not emit a complex field psi.
    """

    TRANSITIONS = (
        (3, 2), (4, 2), (5, 2), (6, 2), (7, 2), (8, 2),
        (4, 3), (5, 3), (6, 3), (7, 3),
        (2, 1), (3, 1),
    )
    RYDBERG_EV = 13.605693122994

    def __init__(self) -> None:
        self.index = 0

    def reset(self) -> None:
        self.index = 0

    def descriptor(self, dt: float) -> QuantumDescriptor:
        del dt
        n_hi, n_lo = self.TRANSITIONS[self.index % len(self.TRANSITIONS)]
        self.index += 1
        delta_e = self.RYDBERG_EV * ((1.0 / n_lo**2) - (1.0 / n_hi**2))
        normalized_energy = np.clip(delta_e / self.RYDBERG_EV, 0.0, 1.0)
        return QuantumDescriptor(
            energy=float(normalized_energy),
            phase=float((n_hi / n_lo) % 1.0),
            probability=float(np.clip(normalized_energy / n_lo, 0.0, 1.0)),
            structure=float(np.clip(abs(n_hi - n_lo) / 7.0, 0.0, 1.0)),
        )


class LegacyHydrogenOrbitalSource:
    """The original stochastic 1s/2s/2p descriptor source, unchanged."""

    def __init__(self, orbital: str = "2p", seed: Optional[int] = None) -> None:
        self.orbital = orbital
        self.seed = seed
        self.rng = np.random.default_rng(seed)
        self.time = 0.0

    def reset(self) -> None:
        self.rng = np.random.default_rng(self.seed)
        self.time = 0.0

    def descriptor(self, dt: float) -> QuantumDescriptor:
        self.time += dt
        radius = 4.0 * self.rng.random() ** (1.0 / 3.0)
        theta = math.acos(2.0 * self.rng.random() - 1.0)
        phi = 2.0 * math.pi * self.rng.random() + 0.35 * self.time
        x = radius * math.sin(theta) * math.cos(phi)
        y = radius * math.sin(theta) * math.sin(phi)
        z = radius * math.cos(theta)
        r = max(1.0e-9, math.sqrt(x * x + y * y + z * z))

        if self.orbital == "1s":
            amplitude, angular, node_measure = math.exp(-r), 1.0, 0.0
        elif self.orbital == "2s":
            amplitude = (2.0 - r) * math.exp(-0.5 * r)
            angular = 1.0
            node_measure = min(1.0, abs(r - 2.0) / 2.0)
        else:
            amplitude = r * math.exp(-0.5 * r) * (z / r)
            angular = abs(z / r)
            node_measure = min(1.0, abs(z) / 2.0)

        return QuantumDescriptor(
            energy=float(np.clip(1.0 / (1.0 + r), 0.0, 1.0)),
            phase=float((math.atan2(y, x) / (2.0 * math.pi)) % 1.0),
            probability=float(np.clip(amplitude * amplitude, 0.0, 1.0)),
            structure=float(np.clip(1.0 - node_measure + 0.35 * angular, 0.0, 1.0)),
        )


class HamiltonianMutator:
    """Drop-in v2 mutator with configurable, lazily allocated source models."""

    def __init__(
        self,
        amount: float = 0.1,
        excitation_kind: str = "audio",
        source_parameters: Optional[Mapping[str, Any]] = None,
    ) -> None:
        self.amount = float(amount)
        self._sources: dict[str, Any] = {}
        self._source_parameters: dict[str, dict[str, Any]] = {}
        self.set_excitation_kind(excitation_kind)
        if source_parameters:
            self.configure_source(excitation_kind, **dict(source_parameters))

    @staticmethod
    def available_sources() -> tuple[str, ...]:
        return SOURCE_NAMES

    def set_excitation_kind(self, excitation_kind: str) -> None:
        if excitation_kind not in SOURCE_NAMES:
            raise ValueError(
                f"Unknown excitation kind {excitation_kind!r}; choose from {SOURCE_NAMES}."
            )
        self.excitation_kind = excitation_kind

    def configure_source(self, source_name: str, **parameters: Any) -> None:
        """Store parameters and rebuild only the named source."""

        if source_name not in SOURCE_NAMES or source_name == "audio":
            raise ValueError(f"Cannot configure unknown/non-physics source {source_name!r}.")
        self._source_parameters[source_name] = dict(parameters)
        self._sources.pop(source_name, None)

    def _create_source(self, source_name: str) -> Any:
        parameters = self._source_parameters.get(source_name, {})
        if source_name == "hydrogen_spectrum":
            return HydrogenSpectrumSource()
        if source_name == "hydrogen_orbital":
            return LegacyHydrogenOrbitalSource(**parameters)
        return create_wavefunction_source(source_name, **parameters)

    def get_source(self, source_name: Optional[str] = None) -> Any:
        name = source_name or self.excitation_kind
        if name == "audio":
            raise ValueError("audio is a descriptor input, not a physics source object.")
        if name not in self._sources:
            self._sources[name] = self._create_source(name)
        return self._sources[name]

    def reset_source(self, source_name: Optional[str] = None) -> None:
        source = self.get_source(source_name)
        source.reset()

    def source_descriptor(self, dt: float):
        if self.excitation_kind == "audio":
            raise ValueError("source_descriptor requires a non-audio excitation kind.")
        return self.get_source().descriptor(dt)

    def source_frame(self, dt: float = 0.0) -> WavefunctionFrame:
        """Return the complete field for true wavefunction sources."""

        source = self.get_source()
        if not hasattr(source, "frame"):
            raise TypeError(
                f"{self.excitation_kind!r} is a descriptor/event source and has no psi frame. "
                "Use 'hydrogen_orbital_field' for a continuous orbital wavefunction."
            )
        return source.frame(dt)

    def mutate_from_audio(self, hamiltonian, audio_descriptor):
        new_h = HamiltonianState(
            x=hamiltonian.x,
            y=hamiltonian.y,
            z=hamiltonian.z,
        )
        brightness = min(1.0, audio_descriptor.brightness / 8000.0)
        density = min(1.0, audio_descriptor.onset_density / 8.0)
        instability = 1.0 - audio_descriptor.groove_stability
        new_h.x += self.amount * brightness
        new_h.y += self.amount * density
        new_h.z += self.amount * instability
        return new_h.normalize()

    def mutate_from_quantum_descriptor(self, hamiltonian, descriptor):
        """Accept either the legacy descriptor or the extended field descriptor."""

        new_h = HamiltonianState(
            x=hamiltonian.x,
            y=hamiltonian.y,
            z=hamiltonian.z,
        )
        phase_centered = (2.0 * descriptor.phase) - 1.0
        structure_centered = (2.0 * descriptor.structure) - 1.0
        new_h.x += self.amount * (descriptor.energy + 0.35 * structure_centered)
        new_h.y += self.amount * phase_centered
        new_h.z += self.amount * (descriptor.probability - 0.25 * structure_centered)
        return new_h.normalize()

    def mutate_from_physics_source(self, hamiltonian, dt: float):
        descriptor = self.source_descriptor(dt)
        return self.mutate_from_quantum_descriptor(hamiltonian, descriptor)


__all__ = [
    "SOURCE_NAMES",
    "QuantumDescriptor",
    "HydrogenSpectrumSource",
    "LegacyHydrogenOrbitalSource",
    "HamiltonianMutator",
]
