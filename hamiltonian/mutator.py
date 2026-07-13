from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Literal, Optional

import numpy as np

from hamiltonian.hamiltonian_state import HamiltonianState


ExcitationKind = Literal[
    "audio",
    "hydrogen_spectrum",
    "hydrogen_orbital",
    "schrodinger_packet",
]


@dataclass(frozen=True)
class QuantumDescriptor:
    """Normalized quantum-physics descriptor used to excite the Hamiltonian.

    energy:      0..1 transition / kinetic / field energy
    phase:       0..1 phase angle mapped from 0..2π
    probability: 0..1 local probability density or spectral intensity
    structure:   0..1 nodal/interference/dispersion complexity
    """

    energy: float
    phase: float
    probability: float
    structure: float


class HydrogenSpectrumSource:
    """Discrete hydrogen transition source based on the Rydberg energy law."""

    TRANSITIONS = (
        (3, 2),
        (4, 2),
        (5, 2),
        (6, 2),
        (7, 2),
        (8, 2),
        (4, 3),
        (5, 3),
        (6, 3),
        (7, 3),
        (2, 1),
        (3, 1),
    )

    RYDBERG_EV = 13.605693122994

    def __init__(self) -> None:
        self.index = 0

    def descriptor(self, dt: float) -> QuantumDescriptor:
        n_hi, n_lo = self.TRANSITIONS[self.index % len(self.TRANSITIONS)]
        self.index += 1

        delta_e = self.RYDBERG_EV * ((1.0 / n_lo**2) - (1.0 / n_hi**2))
        normalized_energy = np.clip(delta_e / self.RYDBERG_EV, 0.0, 1.0)

        transition_ratio = n_hi / n_lo
        phase = transition_ratio % 1.0
        probability = np.clip(normalized_energy * (1.0 / n_lo), 0.0, 1.0)
        structure = np.clip(abs(n_hi - n_lo) / 7.0, 0.0, 1.0)

        return QuantumDescriptor(
            energy=float(normalized_energy),
            phase=float(phase),
            probability=float(probability),
            structure=float(structure),
        )


class HydrogenOrbitalSource:
    """Continuous hydrogen-orbital-like probability-field source.

    Uses simple analytic orbital proxies rather than a full scipy.special model,
    so the source remains lightweight and real-time friendly.
    """

    def __init__(self, orbital: str = "2p", seed: Optional[int] = None) -> None:
        self.orbital = orbital
        self.rng = np.random.default_rng(seed)
        self.time = 0.0

    def descriptor(self, dt: float) -> QuantumDescriptor:
        self.time += dt

        radius = 4.0 * self.rng.random() ** (1.0 / 3.0)
        theta = math.acos(2.0 * self.rng.random() - 1.0)
        phi = 2.0 * math.pi * self.rng.random() + 0.35 * self.time

        x = radius * math.sin(theta) * math.cos(phi)
        y = radius * math.sin(theta) * math.sin(phi)
        z = radius * math.cos(theta)

        r = max(1e-9, math.sqrt(x * x + y * y + z * z))

        if self.orbital == "1s":
            amplitude = math.exp(-r)
            angular = 1.0
            node_measure = 0.0
        elif self.orbital == "2s":
            amplitude = (2.0 - r) * math.exp(-0.5 * r)
            angular = 1.0
            node_measure = min(1.0, abs(r - 2.0) / 2.0)
        else:
            # 2p_z proxy: radial decay times cos(theta). The nodal plane is z=0.
            amplitude = r * math.exp(-0.5 * r) * (z / r)
            angular = abs(z / r)
            node_measure = min(1.0, abs(z) / 2.0)

        probability = np.clip(amplitude * amplitude, 0.0, 1.0)
        phase = (math.atan2(y, x) / (2.0 * math.pi)) % 1.0
        energy = np.clip(1.0 / (1.0 + r), 0.0, 1.0)
        structure = np.clip(1.0 - node_measure + 0.35 * angular, 0.0, 1.0)

        return QuantumDescriptor(
            energy=float(energy),
            phase=float(phase),
            probability=float(probability),
            structure=float(structure),
        )


class SchrodingerPacketSource:
    """Lightweight 1D free-particle Schrödinger wavepacket source."""

    def __init__(self, n_points: int = 128) -> None:
        self.n_points = n_points
        self.x = np.linspace(-8.0, 8.0, n_points, endpoint=False)
        self.dx = float(self.x[1] - self.x[0])
        self.k = 2.0 * math.pi * np.fft.fftfreq(n_points, d=self.dx)

        sigma = 0.9
        momentum = 3.0
        self.psi = np.exp(-(self.x + 3.0) ** 2 / (2.0 * sigma**2)) * np.exp(
            1j * momentum * self.x
        )
        self.psi = self.psi / np.sqrt(np.sum(np.abs(self.psi) ** 2))
        self.time = 0.0

    def descriptor(self, dt: float) -> QuantumDescriptor:
        self.time += dt

        psi_k = np.fft.fft(self.psi)
        propagator = np.exp(-0.5j * (self.k**2) * dt)
        self.psi = np.fft.ifft(psi_k * propagator)
        self.psi = self.psi / np.sqrt(np.sum(np.abs(self.psi) ** 2))

        probability = np.abs(self.psi) ** 2
        peak_density = float(np.max(probability))
        mean_x = float(np.sum(self.x * probability))
        spread = float(np.sqrt(np.sum(((self.x - mean_x) ** 2) * probability)))

        phase = np.unwrap(np.angle(self.psi))
        phase_gradient = np.gradient(phase, self.dx)
        mean_phase_velocity = float(np.mean(np.abs(phase_gradient)))
        roughness = float(np.mean(np.abs(np.gradient(probability, self.dx))))

        return QuantumDescriptor(
            energy=float(np.clip(mean_phase_velocity / 8.0, 0.0, 1.0)),
            phase=float((np.mean(phase) / (2.0 * math.pi)) % 1.0),
            probability=float(np.clip(peak_density * 8.0, 0.0, 1.0)),
            structure=float(np.clip((spread / 5.0) + (roughness * 3.0), 0.0, 1.0)),
        )


class HamiltonianMutator:
    def __init__(
        self,
        amount=0.1,
        excitation_kind: ExcitationKind = "audio",
    ):
        self.amount = amount
        self.excitation_kind = excitation_kind
        self.hydrogen_spectrum = HydrogenSpectrumSource()
        self.hydrogen_orbital = HydrogenOrbitalSource(orbital="2p")
        self.schrodinger_packet = SchrodingerPacketSource()

    def set_excitation_kind(self, excitation_kind: ExcitationKind) -> None:
        self.excitation_kind = excitation_kind

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

    def mutate_from_quantum_descriptor(
        self,
        hamiltonian,
        descriptor: QuantumDescriptor,
    ):
        """Mutate the Hamiltonian from a normalized quantum-physics descriptor."""
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
        """Mutate from the currently selected non-audio physics source."""
        if self.excitation_kind == "hydrogen_spectrum":
            descriptor = self.hydrogen_spectrum.descriptor(dt)
        elif self.excitation_kind == "hydrogen_orbital":
            descriptor = self.hydrogen_orbital.descriptor(dt)
        elif self.excitation_kind == "schrodinger_packet":
            descriptor = self.schrodinger_packet.descriptor(dt)
        else:
            raise ValueError(
                "mutate_from_physics_source requires a non-audio excitation_kind."
            )

        return self.mutate_from_quantum_descriptor(hamiltonian, descriptor)