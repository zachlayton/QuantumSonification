from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Dict

import numpy as np

from excitation.base import QuantumSource
from excitation.descriptor import QuantumDescriptor


@dataclass(frozen=True)
class SchrodingerPacketState:
    """Snapshot of the internal wavepacket state.

    The compact QuantumDescriptor drives the Hamiltonian, while this richer
    state can later drive visualization, Max multisliders, or Processing.
    """

    time: float
    expectation_x: float
    expectation_p: float
    uncertainty_x: float
    uncertainty_p: float
    peak_probability: float
    spread: float
    phase_curvature: float
    roughness: float


class SchrodingerPacketSource(QuantumSource):
    """1D free-particle Schrödinger wavepacket source.

    This source evolves a normalized complex wavefunction psi(x,t) on a
    periodic grid using a spectral kinetic propagator:

        psi_k(t + dt) = exp(-i k^2 dt / 2) psi_k(t)

    Units are dimensionless: hbar = 1 and mass = 1. The purpose is not to be
    a laboratory-precision simulator, but to provide a physically meaningful
    evolving quantum field for QMW.
    """

    def __init__(
        self,
        n_points: int = 256,
        x_min: float = -8.0,
        x_max: float = 8.0,
        initial_center: float = -3.0,
        initial_width: float = 0.85,
        initial_momentum: float = 3.0,
        interference: bool = False,
        sideband_weight: float = 0.55,
    ) -> None:
        if n_points < 16:
            raise ValueError("n_points must be at least 16.")
        if x_max <= x_min:
            raise ValueError("x_max must be greater than x_min.")
        if initial_width <= 0:
            raise ValueError("initial_width must be positive.")

        self.n_points = int(n_points)
        self.x_min = float(x_min)
        self.x_max = float(x_max)
        self.initial_center = float(initial_center)
        self.initial_width = float(initial_width)
        self.initial_momentum = float(initial_momentum)
        self.interference = bool(interference)
        self.sideband_weight = float(sideband_weight)

        self.x = np.linspace(self.x_min, self.x_max, self.n_points, endpoint=False)
        self.dx = float(self.x[1] - self.x[0])
        self.k = 2.0 * math.pi * np.fft.fftfreq(self.n_points, d=self.dx)
        self.length = self.x_max - self.x_min

        self.time = 0.0
        self.psi = self._initial_wavefunction()
        self._state = self._compute_state()
        self._descriptor = self._compute_descriptor()

    def _initial_wavefunction(self) -> np.ndarray:
        envelope = np.exp(
            -((self.x - self.initial_center) ** 2) / (2.0 * self.initial_width**2)
        )
        if self.interference:
            carrier = (
                1.0
                + self.sideband_weight * np.exp(1j * self.initial_momentum * self.x)
                + self.sideband_weight * np.exp(-1j * self.initial_momentum * self.x)
            )
        else:
            carrier = np.exp(1j * self.initial_momentum * self.x)
        psi = envelope * carrier
        return self._normalize(psi)

    def _normalize(self, psi: np.ndarray) -> np.ndarray:
        norm = math.sqrt(float(np.sum(np.abs(psi) ** 2) * self.dx))
        if norm <= 1e-15:
            raise ValueError("Wavefunction norm collapsed to zero.")
        return psi / norm

    def _probability(self) -> np.ndarray:
        return np.abs(self.psi) ** 2

    def _phase(self) -> np.ndarray:
        return np.unwrap(np.angle(self.psi))

    def _expectation_x(self, probability: np.ndarray) -> float:
        return float(np.sum(self.x * probability) * self.dx)

    def _expectation_p(self) -> float:
        psi_k = np.fft.fft(self.psi)
        spectral_probability = np.abs(psi_k) ** 2
        total = float(np.sum(spectral_probability))
        if total <= 1e-15:
            return 0.0
        return float(np.sum(self.k * spectral_probability) / total)

    def _uncertainty_x(self, probability: np.ndarray, mean_x: float) -> float:
        variance = float(np.sum(((self.x - mean_x) ** 2) * probability) * self.dx)
        return math.sqrt(max(0.0, variance))

    def _uncertainty_p(self, mean_p: float) -> float:
        psi_k = np.fft.fft(self.psi)
        spectral_probability = np.abs(psi_k) ** 2
        total = float(np.sum(spectral_probability))
        if total <= 1e-15:
            return 0.0
        variance = float(np.sum(((self.k - mean_p) ** 2) * spectral_probability) / total)
        return math.sqrt(max(0.0, variance))

    def _phase_curvature(self, phase: np.ndarray) -> float:
        gradient = np.gradient(phase, self.dx)
        curvature = np.gradient(gradient, self.dx)
        return float(np.mean(np.abs(curvature)))

    def _roughness(self, probability: np.ndarray) -> float:
        gradient = np.gradient(probability, self.dx)
        return float(np.mean(np.abs(gradient)))

    def _compute_state(self) -> SchrodingerPacketState:
        probability = self._probability()
        phase = self._phase()

        expectation_x = self._expectation_x(probability)
        expectation_p = self._expectation_p()
        uncertainty_x = self._uncertainty_x(probability, expectation_x)
        uncertainty_p = self._uncertainty_p(expectation_p)
        phase_curvature = self._phase_curvature(phase)
        roughness = self._roughness(probability)

        return SchrodingerPacketState(
            time=float(self.time),
            expectation_x=float(expectation_x),
            expectation_p=float(expectation_p),
            uncertainty_x=float(uncertainty_x),
            uncertainty_p=float(uncertainty_p),
            peak_probability=float(np.max(probability)),
            spread=float(uncertainty_x),
            phase_curvature=float(phase_curvature),
            roughness=float(roughness),
        )

    def _compute_descriptor(self) -> QuantumDescriptor:
        state = self._compute_state()
        phase = self._phase()

        energy = np.clip(abs(state.expectation_p) / 8.0, 0.0, 1.0)
        mean_phase = float(np.mean(phase))
        phase_normalized = (mean_phase / (2.0 * math.pi)) % 1.0
        probability_level = np.clip(state.peak_probability * self.initial_width, 0.0, 1.0)
        coherence = np.clip(1.0 / (1.0 + 0.12 * state.spread), 0.0, 1.0)
        entanglement = 0.0
        spin = 0.5
        topology = np.clip((state.roughness * 4.0) + (state.phase_curvature * 0.02), 0.0, 1.0)
        curvature = np.clip(state.phase_curvature / 20.0, 0.0, 1.0)

        return QuantumDescriptor(
            energy=float(energy),
            phase=float(phase_normalized),
            probability=float(probability_level),
            coherence=float(coherence),
            entanglement=float(entanglement),
            spin=float(spin),
            topology=float(topology),
            curvature=float(curvature),
        )

    def step(self, dt: float) -> None:
        """Advance the wavepacket by dt."""
        if dt < 0:
            raise ValueError("dt must be non-negative.")

        if dt > 0:
            psi_k = np.fft.fft(self.psi)
            propagator = np.exp(-0.5j * (self.k**2) * dt)
            self.psi = np.fft.ifft(psi_k * propagator)
            self.psi = self._normalize(self.psi)
            self.time += dt

        self._state = self._compute_state()
        self._descriptor = self._compute_descriptor()

    @property
    def descriptor(self) -> QuantumDescriptor:
        """Return the latest compact descriptor without advancing."""
        return self._descriptor

    @property
    def state(self) -> SchrodingerPacketState:
        """Return the latest rich physical state snapshot."""
        return self._state

    @property
    def wavefunction(self) -> np.ndarray:
        """Return a copy of the current complex wavefunction."""
        return self.psi.copy()

    @property
    def probability_distribution(self) -> np.ndarray:
        """Return |psi|^2 as a copy for visualization or OSC export."""
        return self._probability().copy()

    def state_dict(self) -> Dict[str, float]:
        """Return state values as a simple dictionary for logging or OSC."""
        return {
            "time": self.state.time,
            "expectation_x": self.state.expectation_x,
            "expectation_p": self.state.expectation_p,
            "uncertainty_x": self.state.uncertainty_x,
            "uncertainty_p": self.state.uncertainty_p,
            "peak_probability": self.state.peak_probability,
            "spread": self.state.spread,
            "phase_curvature": self.state.phase_curvature,
            "roughness": self.state.roughness,
        }
