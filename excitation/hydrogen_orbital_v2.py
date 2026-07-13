from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Dict, Literal, Optional

import numpy as np

from excitation.base import QuantumSource
from excitation.descriptor import QuantumDescriptor


OrbitalName = Literal["1s", "2s", "2p", "3d"]
OrbitalQuantumNumbers = tuple[int, int, int]


ORBITAL_QUANTUM_NUMBERS: dict[str, OrbitalQuantumNumbers] = {
    "1s": (1, 0, 0),
    "2s": (2, 0, 0),
    "2p": (2, 1, 0),
    "3d": (3, 2, 0),
}


def _orbital_from_quantum_numbers(
    n: Optional[int],
    l: Optional[int],
    m: Optional[int],
) -> OrbitalName:
    if n is None:
        raise ValueError("n is required when selecting an orbital by quantum numbers.")

    shell_defaults = {
        1: "1s",
        2: "2p",
        3: "3d",
    }
    if l is None:
        orbital = shell_defaults.get(n)
        if orbital is None:
            raise ValueError(f"Unsupported principal quantum number n={n}.")
        return orbital  # type: ignore[return-value]

    if m is None:
        m = 0

    if n < 1:
        raise ValueError("n must be at least 1.")
    if l < 0 or l >= n:
        raise ValueError("l must satisfy 0 <= l < n.")
    if abs(m) > l:
        raise ValueError("m must satisfy -l <= m <= l.")
    if m != 0:
        raise ValueError("Only m=0 z-oriented real orbital proxies are supported.")

    quantum_lookup = {values: key for key, values in ORBITAL_QUANTUM_NUMBERS.items()}
    orbital = quantum_lookup.get((n, l, m))
    if orbital is None:
        supported = ", ".join(
            f"{name}: n={qn[0]}, l={qn[1]}, m={qn[2]}"
            for name, qn in ORBITAL_QUANTUM_NUMBERS.items()
        )
        raise ValueError(
            f"Unsupported orbital quantum numbers n={n}, l={l}, m={m}. "
            f"Supported proxies are {supported}."
        )

    return orbital  # type: ignore[return-value]


@dataclass(frozen=True)
class HydrogenOrbitalState:
    orbital: str
    time: float
    r: float
    theta: float
    phi: float
    x: float
    y: float
    z: float
    amplitude: float
    probability: float
    phase: float
    radial_node: float
    angular_node: float
    topology: float
    curvature: float


class HydrogenOrbitalSource(QuantumSource):
    """Hydrogen-orbital probability-field source.

    Lightweight analytic orbital proxies:
        1s  smooth spherical ground state
        2s  radial node
        2p  nodal plane
        3d  multi-lobed angular structure
    """

    def __init__(
        self,
        orbital: Optional[OrbitalName] = None,
        n: Optional[int] = None,
        l: Optional[int] = None,
        m: Optional[int] = None,
        seed: Optional[int] = None,
        radius_scale: float = 6.0,
        phase_rate: float = 0.35,
    ) -> None:
        if n is not None or l is not None or m is not None:
            quantum_orbital = _orbital_from_quantum_numbers(n, l, m)
            if orbital is not None and orbital != quantum_orbital:
                raise ValueError(
                    f"orbital={orbital!r} conflicts with quantum numbers "
                    f"n={n}, l={l}, m={m} ({quantum_orbital!r})."
                )
            orbital = quantum_orbital
        if orbital is None:
            orbital = "2p"

        self.orbital = orbital
        self.n, self.l, self.m = ORBITAL_QUANTUM_NUMBERS[orbital]
        self.rng = np.random.default_rng(seed)
        self.radius_scale = float(radius_scale)
        self.phase_rate = float(phase_rate)
        self.time = 0.0

        self._state = self._sample_state()
        self._descriptor = self._compute_descriptor(self._state)

    def _sample_point(self) -> tuple[float, float, float, float, float, float]:
        r = self.radius_scale * self.rng.random() ** (1.0 / 3.0)
        theta = math.acos(2.0 * self.rng.random() - 1.0)
        phi = 2.0 * math.pi * self.rng.random() + self.phase_rate * self.time

        x = r * math.sin(theta) * math.cos(phi)
        y = r * math.sin(theta) * math.sin(phi)
        z = r * math.cos(theta)
        return r, theta, phi, x, y, z

    def _orbital_amplitude(
        self,
        r: float,
        theta: float,
        z: float,
    ) -> tuple[float, float, float, float]:
        cos_theta = math.cos(theta)

        if self.orbital == "1s":
            amplitude = math.exp(-r)
            radial_node = 0.0
            angular_node = 0.0
            angular_complexity = 0.0

        elif self.orbital == "2s":
            amplitude = (2.0 - r) * math.exp(-0.5 * r)
            radial_node = 1.0 - min(1.0, abs(r - 2.0) / 2.0)
            angular_node = 0.0
            angular_complexity = 0.15

        elif self.orbital == "2p":
            amplitude = r * math.exp(-0.5 * r) * cos_theta
            radial_node = 0.0
            angular_node = 1.0 - min(1.0, abs(z) / 2.0)
            angular_complexity = abs(cos_theta)

        elif self.orbital == "3d":
            # 3d_z^2-like proxy: radial shell times (3cos²θ - 1).
            angular = 3.0 * cos_theta**2 - 1.0
            amplitude = (r**2) * math.exp(-r / 3.0) * angular
            radial_node = 0.0
            angular_node = 1.0 - min(1.0, abs(angular) / 1.5)
            angular_complexity = min(1.0, abs(angular))

        else:
            raise ValueError(f"Unsupported orbital: {self.orbital}")

        return amplitude, radial_node, angular_node, angular_complexity

    def _sample_state(self) -> HydrogenOrbitalState:
        r, theta, phi, x, y, z = self._sample_point()
        amplitude, radial_node, angular_node, angular_complexity = (
            self._orbital_amplitude(r, theta, z)
        )

        probability = float(np.clip(amplitude * amplitude, 0.0, 1.0))
        phase = (math.atan2(y, x) / (2.0 * math.pi)) % 1.0

        topology = float(
            np.clip(
                0.45 * radial_node
                + 0.45 * angular_node
                + 0.10 * angular_complexity,
                0.0,
                1.0,
            )
        )

        curvature = float(
            np.clip(
                abs(angular_complexity - radial_node)
                + 0.25 * angular_node,
                0.0,
                1.0,
            )
        )

        return HydrogenOrbitalState(
            orbital=self.orbital,
            time=float(self.time),
            r=float(r),
            theta=float(theta),
            phi=float(phi % (2.0 * math.pi)),
            x=float(x),
            y=float(y),
            z=float(z),
            amplitude=float(amplitude),
            probability=probability,
            phase=float(phase),
            radial_node=float(radial_node),
            angular_node=float(angular_node),
            topology=topology,
            curvature=curvature,
        )

    def _compute_descriptor(self, state: HydrogenOrbitalState) -> QuantumDescriptor:
        # Hydrogen-like energy scale: larger n = lower bound-state energy.
        n_lookup = {"1s": 1, "2s": 2, "2p": 2, "3d": 3}
        n = n_lookup[self.orbital]
        energy = np.clip(1.0 / (n * n), 0.0, 1.0)

        # Coherence stays high for a stationary orbital proxy.
        coherence = 1.0

        # Single-electron orbital source: no internal entanglement yet.
        entanglement = 0.0

        # Neutral spin until we add explicit spinors / Zeeman splitting.
        spin = 0.5

        return QuantumDescriptor(
            energy=float(energy),
            phase=float(state.phase),
            probability=float(state.probability),
            coherence=float(coherence),
            entanglement=float(entanglement),
            spin=float(spin),
            topology=float(state.topology),
            curvature=float(state.curvature),
        )
    
    def step(self, dt: float) -> QuantumDescriptor:
        """Advance the orbital source by dt.

        QuantumSource expects a step() method. For this source,
        step() and descriptor() return the same compact descriptor.
        """
        return self.descriptor(dt)

    def descriptor(self, dt: float) -> QuantumDescriptor:
        if dt < 0:
            raise ValueError("dt must be non-negative.")

        self.time += dt
        self._state = self._sample_state()
        self._descriptor = self._compute_descriptor(self._state)
        return self._descriptor

    @property
    def state(self) -> HydrogenOrbitalState:
        return self._state

    def state_dict(self) -> Dict[str, float | str]:
        return {
            "orbital": self.state.orbital,
            "time": self.state.time,
            "r": self.state.r,
            "theta": self.state.theta,
            "phi": self.state.phi,
            "x": self.state.x,
            "y": self.state.y,
            "z": self.state.z,
            "amplitude": self.state.amplitude,
            "probability": self.state.probability,
            "phase": self.state.phase,
            "radial_node": self.state.radial_node,
            "angular_node": self.state.angular_node,
            "topology": self.state.topology,
            "curvature": self.state.curvature,
        }
