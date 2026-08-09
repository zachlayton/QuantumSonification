"""QuantumSonification wavefunction sources v1.

The module exposes a common complex-field contract for analytic and numerical
wavefunctions.  NumPy is the only dependency.  Natural units are used by
default (hbar = mass = 1), while every solver keeps those quantities explicit.

The canonical interface is::

    source = create_wavefunction_source("schrodinger_packet_3d")
    frame = source.frame(dt=0.01)
    descriptor = frame.descriptor

``descriptor(dt)`` is retained for compatibility with the original
``mutator_quantum_sources_v1.py`` architecture.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import math
from typing import Any, Mapping, Optional, Protocol, Sequence

import numpy as np


Array = np.ndarray
EPS = 1.0e-12


@dataclass(frozen=True)
class WavefunctionDescriptor:
    """Normalized control projection derived from a complete wavefunction.

    The first four fields match the original ``QuantumDescriptor`` contract.
    The additional fields preserve relational and dynamical information that
    would otherwise be lost when a complex field is reduced to four numbers.
    """

    energy: float
    phase: float
    probability: float
    structure: float
    coherence: float = 0.0
    current: float = 0.0
    position: tuple[float, ...] = ()
    spread: tuple[float, ...] = ()
    momentum: tuple[float, ...] = ()


@dataclass(frozen=True)
class WavefunctionFrame:
    """One normalized complex-field state and its physical observables."""

    psi: Array
    probability: Array
    phase: Array
    probability_current: tuple[Array, ...]
    energy_density: Array
    coordinates: tuple[Array, ...]
    time: float
    norm: float
    dimension: int
    source: str
    descriptor: WavefunctionDescriptor
    metadata: Mapping[str, Any] = field(default_factory=dict)


class WavefunctionSource(Protocol):
    """Structural interface shared by every source in this module."""

    def frame(self, dt: float = 0.0) -> WavefunctionFrame: ...

    def descriptor(self, dt: float) -> WavefunctionDescriptor: ...

    def reset(self) -> None: ...


def _as_tuple(value: Any, dimensions: int, cast: type = float) -> tuple[Any, ...]:
    if np.isscalar(value):
        return tuple(cast(value) for _ in range(dimensions))
    result = tuple(cast(item) for item in value)
    if len(result) != dimensions:
        raise ValueError(f"Expected {dimensions} values, received {len(result)}.")
    return result


def _normalize(psi: Array, measure: float | Array) -> Array:
    norm = math.sqrt(max(float(np.sum(np.abs(psi) ** 2 * measure).real), EPS))
    return np.asarray(psi, dtype=np.complex128) / norm


def _hermite(order: int, x: Array) -> Array:
    if order < 0:
        raise ValueError("Hermite order must be non-negative.")
    if order == 0:
        return np.ones_like(x)
    if order == 1:
        return 2.0 * x
    h_nm2 = np.ones_like(x)
    h_nm1 = 2.0 * x
    for n in range(2, order + 1):
        h_n = (2.0 * x * h_nm1) - (2.0 * (n - 1) * h_nm2)
        h_nm2, h_nm1 = h_nm1, h_n
    return h_nm1


def _integration_measure(spacing: tuple[float, ...], weights: Optional[Array]) -> float | Array:
    if weights is not None:
        return weights
    return float(np.prod(spacing))


def _frame_from_psi(
    *,
    psi: Array,
    coordinates: tuple[Array, ...],
    spacing: tuple[float, ...],
    potential: Array,
    time: float,
    source: str,
    hbar: float = 1.0,
    mass: float = 1.0,
    integration_weights: Optional[Array] = None,
    current_override: Optional[tuple[Array, ...]] = None,
    energy_density_override: Optional[Array] = None,
    metadata: Optional[Mapping[str, Any]] = None,
) -> WavefunctionFrame:
    """Normalize a field and calculate a stable cross-model descriptor."""

    dimension = psi.ndim
    if dimension != len(coordinates) or dimension != len(spacing):
        raise ValueError("psi dimensionality, coordinates, and spacing must agree.")

    measure = _integration_measure(spacing, integration_weights)
    psi = _normalize(psi, measure)
    probability = np.abs(psi) ** 2
    phase = np.angle(psi)

    gradients_raw = np.gradient(psi, *spacing, edge_order=2)
    gradients = (gradients_raw,) if dimension == 1 else tuple(gradients_raw)
    if current_override is None:
        currents = tuple((hbar / mass) * np.imag(np.conj(psi) * grad) for grad in gradients)
    else:
        currents = current_override

    if energy_density_override is None:
        kinetic_density = (hbar**2 / (2.0 * mass)) * sum(
            np.abs(grad) ** 2 for grad in gradients
        )
        energy_density = np.real(kinetic_density + (potential * probability))
    else:
        energy_density = np.real(energy_density_override)

    norm = math.sqrt(max(float(np.sum(probability * measure).real), EPS))
    expectation_energy = float(np.sum(energy_density * measure).real)

    position: list[float] = []
    spread: list[float] = []
    momentum: list[float] = []
    for axis, coordinate in enumerate(coordinates):
        shape = [1] * dimension
        shape[axis] = coordinate.size
        coordinate_field = coordinate.reshape(shape)
        mean = float(np.sum(coordinate_field * probability * measure).real)
        variance = float(
            np.sum(((coordinate_field - mean) ** 2) * probability * measure).real
        )
        position.append(mean)
        spread.append(math.sqrt(max(variance, 0.0)))
        momentum.append(float(mass * np.sum(currents[axis] * measure).real))

    neighbor_coherences: list[complex] = []
    for axis in range(dimension):
        shifted = np.roll(psi, -1, axis=axis)
        neighbor_coherences.append(complex(np.sum(np.conj(psi) * shifted * measure)))
    coherence_complex = sum(neighbor_coherences) / max(len(neighbor_coherences), 1)
    coherence = float(np.clip(abs(coherence_complex), 0.0, 1.0))
    relative_phase = float((np.angle(coherence_complex) / (2.0 * math.pi)) % 1.0)

    mass_distribution = np.asarray(probability * measure, dtype=float).ravel()
    mass_distribution /= max(float(np.sum(mass_distribution)), EPS)
    entropy = -float(np.sum(mass_distribution * np.log(mass_distribution + EPS)))
    entropy_normalized = entropy / max(math.log(mass_distribution.size), EPS)
    localization = float(np.clip(1.0 - entropy_normalized, 0.0, 1.0))

    prob_grad_raw = np.gradient(probability, *spacing, edge_order=2)
    prob_gradients = (prob_grad_raw,) if dimension == 1 else tuple(prob_grad_raw)
    grad_magnitude = np.sqrt(sum(component**2 for component in prob_gradients))
    mean_probability = float(np.mean(probability))
    roughness_ratio = (
        float(np.mean(grad_magnitude)) * float(np.mean(spacing))
        / max(mean_probability, EPS)
    )
    roughness = roughness_ratio / (1.0 + roughness_ratio)
    structure = float(np.clip((0.65 * roughness) + (0.35 * (1.0 - coherence)), 0.0, 1.0))

    current_density = np.sqrt(sum(component**2 for component in currents))
    current_strength = float(np.sum(current_density * measure).real)
    current_normalized = current_strength / (1.0 + current_strength)
    energy_scale = float((metadata or {}).get("energy_scale", 1.0))
    energy_normalized = abs(expectation_energy) / (
        abs(expectation_energy) + max(energy_scale, EPS)
    )

    descriptor = WavefunctionDescriptor(
        energy=float(np.clip(energy_normalized, 0.0, 1.0)),
        phase=relative_phase,
        probability=localization,
        structure=structure,
        coherence=coherence,
        current=float(np.clip(current_normalized, 0.0, 1.0)),
        position=tuple(position),
        spread=tuple(spread),
        momentum=tuple(momentum),
    )
    frame_metadata = dict(metadata or {})
    frame_metadata.update(
        expectation_energy=expectation_energy,
        current_strength=current_strength,
        entropy=entropy_normalized,
    )

    return WavefunctionFrame(
        psi=psi,
        probability=probability,
        phase=phase,
        probability_current=currents,
        energy_density=energy_density,
        coordinates=coordinates,
        time=float(time),
        norm=norm,
        dimension=dimension,
        source=source,
        descriptor=descriptor,
        metadata=frame_metadata,
    )


class PotentialWavefunctionSource:
    """Split-step Fourier Schrödinger solver for 1D, 2D, or 3D fields.

    The solver uses periodic numerical boundaries.  Localized packets and the
    supplied confining potentials keep the active field away from those edges.
    Grid presets of 128 (1D), 64x64 (2D), and 32x32x32 (3D) are suitable for
    interactive control-rate work on a typical CPU.
    """

    POTENTIALS = (
        "free",
        "harmonic",
        "double_well",
        "barrier",
        "periodic_lattice",
        "coulomb",
        "driven",
    )

    def __init__(
        self,
        *,
        dimensions: int = 1,
        grid_shape: int | Sequence[int] | None = None,
        extent: float | Sequence[float] = 16.0,
        potential: str = "free",
        initial_state: str = "gaussian",
        center: float | Sequence[float] = 0.0,
        momentum: float | Sequence[float] = 0.0,
        sigma: float | Sequence[float] = 0.9,
        hbar: float = 1.0,
        mass: float = 1.0,
        omega: float | Sequence[float] = 1.0,
        mode: int | Sequence[int] = 0,
        squeeze: float = 0.75,
        potential_parameters: Optional[Mapping[str, Any]] = None,
        source_name: Optional[str] = None,
    ) -> None:
        if dimensions not in (1, 2, 3):
            raise ValueError("dimensions must be 1, 2, or 3.")
        if potential not in self.POTENTIALS:
            raise ValueError(f"Unknown potential {potential!r}; choose from {self.POTENTIALS}.")
        if grid_shape is None:
            grid_shape = {1: 128, 2: 64, 3: 32}[dimensions]

        self.dimensions = dimensions
        self.grid_shape = _as_tuple(grid_shape, dimensions, int)
        self.extent = _as_tuple(extent, dimensions, float)
        self.center = _as_tuple(center, dimensions, float)
        self.initial_momentum = _as_tuple(momentum, dimensions, float)
        self.sigma = _as_tuple(sigma, dimensions, float)
        self.omega = _as_tuple(omega, dimensions, float)
        self.mode = _as_tuple(mode, dimensions, int)
        self.hbar = float(hbar)
        self.mass = float(mass)
        self.potential_name = potential
        self.initial_state = initial_state
        self.squeeze = float(squeeze)
        self.potential_parameters = dict(potential_parameters or {})
        self.source_name = source_name or f"{potential}_{dimensions}d"

        self.coordinates = tuple(
            np.linspace(-length / 2.0, length / 2.0, count, endpoint=False)
            for length, count in zip(self.extent, self.grid_shape)
        )
        self.spacing = tuple(float(axis[1] - axis[0]) for axis in self.coordinates)
        self.mesh = tuple(np.meshgrid(*self.coordinates, indexing="ij", sparse=True))
        k_axes = tuple(
            2.0 * math.pi * np.fft.fftfreq(count, d=step)
            for count, step in zip(self.grid_shape, self.spacing)
        )
        k_mesh = tuple(np.meshgrid(*k_axes, indexing="ij", sparse=True))
        self.kinetic_energy = (self.hbar**2 / (2.0 * self.mass)) * sum(
            component**2 for component in k_mesh
        )
        self.cell_volume = float(np.prod(self.spacing))
        self.time = 0.0
        self.psi = self._make_initial_state()
        self._initial_psi = self.psi.copy()

    def _make_initial_state(self) -> Array:
        if self.initial_state in ("gaussian", "coherent", "squeezed"):
            widths = list(self.sigma)
            if self.initial_state in ("coherent", "squeezed"):
                widths = [
                    math.sqrt(self.hbar / (2.0 * self.mass * max(w, EPS)))
                    for w in self.omega
                ]
            if self.initial_state == "squeezed":
                widths = [width * math.exp(-self.squeeze) for width in widths]
            exponent = sum(
                ((axis - center) ** 2) / (4.0 * max(width, EPS) ** 2)
                for axis, center, width in zip(self.mesh, self.center, widths)
            )
            phase = sum(
                momentum * axis / self.hbar
                for momentum, axis in zip(self.initial_momentum, self.mesh)
            )
            psi = np.exp(-exponent) * np.exp(1j * phase)
        elif self.initial_state == "harmonic_eigen":
            psi = np.ones(self.grid_shape, dtype=np.complex128)
            for axis, omega, n in zip(self.mesh, self.omega, self.mode):
                scaled = np.sqrt(self.mass * omega / self.hbar) * axis
                psi *= _hermite(n, scaled) * np.exp(-0.5 * scaled**2)
        else:
            raise ValueError(
                "initial_state must be gaussian, coherent, squeezed, or harmonic_eigen."
            )
        return _normalize(np.asarray(psi, dtype=np.complex128), self.cell_volume)

    def _potential(self, time: float) -> Array:
        params = self.potential_parameters
        r2 = sum(axis**2 for axis in self.mesh)
        if self.potential_name == "free":
            value: Array | float = 0.0
        elif self.potential_name == "harmonic":
            value = sum(
                0.5 * self.mass * (omega**2) * axis**2
                for omega, axis in zip(self.omega, self.mesh)
            )
        elif self.potential_name == "double_well":
            axis_index = int(params.get("axis", 0))
            separation = float(params.get("separation", 2.0))
            height = float(params.get("height", 0.35))
            coordinate = self.mesh[axis_index]
            value = height * (((coordinate / separation) ** 2) - 1.0) ** 2
            for index, axis in enumerate(self.mesh):
                if index != axis_index:
                    value = value + (0.5 * self.mass * self.omega[index] ** 2 * axis**2)
        elif self.potential_name == "barrier":
            height = float(params.get("height", 4.0))
            width = float(params.get("width", 0.55))
            value = height * np.exp(-r2 / (2.0 * width**2))
        elif self.potential_name == "periodic_lattice":
            depth = float(params.get("depth", 1.5))
            period = float(params.get("period", 2.0))
            value = depth * sum(np.sin(math.pi * axis / period) ** 2 for axis in self.mesh)
        elif self.potential_name == "coulomb":
            strength = float(params.get("strength", 1.0))
            softening = float(params.get("softening", 0.35))
            value = -strength / np.sqrt(r2 + softening**2)
        elif self.potential_name == "driven":
            rate = float(params.get("drive_rate", 0.5))
            amplitude = float(params.get("drive_amplitude", 0.25))
            direction = _as_tuple(params.get("drive_direction", (1.0,) + (0.0,) * (self.dimensions - 1)), self.dimensions, float)
            harmonic = sum(
                0.5 * self.mass * (omega**2) * axis**2
                for omega, axis in zip(self.omega, self.mesh)
            )
            drive = sum(component * axis for component, axis in zip(direction, self.mesh))
            value = harmonic + (amplitude * math.cos(rate * time) * drive)
        else:  # guarded in __init__
            raise RuntimeError("Unreachable potential branch.")
        return np.broadcast_to(np.asarray(value, dtype=float), self.grid_shape)

    def reset(self) -> None:
        self.time = 0.0
        self.psi = self._initial_psi.copy()

    def frame(self, dt: float = 0.0) -> WavefunctionFrame:
        if dt < 0.0:
            raise ValueError("dt must be non-negative.")
        if dt > 0.0:
            mid_time = self.time + (0.5 * dt)
            potential = self._potential(mid_time)
            half_potential = np.exp(-0.5j * potential * dt / self.hbar)
            self.psi = half_potential * self.psi
            psi_k = np.fft.fftn(self.psi)
            kinetic_phase = np.exp(-1j * self.kinetic_energy * dt / self.hbar)
            self.psi = np.fft.ifftn(psi_k * kinetic_phase)
            self.psi = half_potential * self.psi
            self.psi = _normalize(self.psi, self.cell_volume)
            self.time += dt
        potential_now = self._potential(self.time)
        return _frame_from_psi(
            psi=self.psi,
            coordinates=self.coordinates,
            spacing=self.spacing,
            potential=potential_now,
            time=self.time,
            source=self.source_name,
            hbar=self.hbar,
            mass=self.mass,
            metadata={
                "potential": self.potential_name,
                "grid_shape": self.grid_shape,
                "extent": self.extent,
                "initial_state": self.initial_state,
            },
        )

    def descriptor(self, dt: float) -> WavefunctionDescriptor:
        return self.frame(dt).descriptor


class SchrodingerPacketSource1D(PotentialWavefunctionSource):
    def __init__(self, **kwargs: Any) -> None:
        defaults = dict(
            dimensions=1,
            potential="free",
            center=-3.0,
            momentum=3.0,
            sigma=0.9,
            source_name="schrodinger_packet",
        )
        defaults.update(kwargs)
        super().__init__(**defaults)


class SchrodingerPacketSource3D(PotentialWavefunctionSource):
    def __init__(self, **kwargs: Any) -> None:
        defaults = dict(
            dimensions=3,
            grid_shape=32,
            potential="free",
            center=(-3.0, 0.0, 0.0),
            momentum=(3.0, 1.0, 0.5),
            sigma=(0.9, 1.1, 1.3),
            source_name="schrodinger_packet_3d",
        )
        defaults.update(kwargs)
        super().__init__(**defaults)


class HarmonicOscillatorSource(PotentialWavefunctionSource):
    def __init__(self, state: str = "harmonic_eigen", dimensions: int = 1, **kwargs: Any) -> None:
        defaults = dict(
            dimensions=dimensions,
            potential="harmonic",
            initial_state=state,
            source_name=f"harmonic_{state}_{dimensions}d",
        )
        defaults.update(kwargs)
        super().__init__(**defaults)


class ParticleInBoxSource:
    """Exact 1D infinite-well eigenstate superposition."""

    def __init__(
        self,
        *,
        n_points: int = 256,
        length: float = 10.0,
        coefficients: Optional[Mapping[int, complex]] = None,
        hbar: float = 1.0,
        mass: float = 1.0,
    ) -> None:
        self.coordinates = (np.linspace(0.0, length, n_points),)
        self.spacing = (float(self.coordinates[0][1] - self.coordinates[0][0]),)
        self.length = float(length)
        self.hbar = float(hbar)
        self.mass = float(mass)
        self.coefficients = dict(coefficients or {1: 1.0, 2: 1.0j})
        norm = math.sqrt(sum(abs(value) ** 2 for value in self.coefficients.values()))
        self.coefficients = {key: value / norm for key, value in self.coefficients.items()}
        self.time = 0.0

    def reset(self) -> None:
        self.time = 0.0

    def frame(self, dt: float = 0.0) -> WavefunctionFrame:
        self.time += dt
        x = self.coordinates[0]
        psi = np.zeros_like(x, dtype=np.complex128)
        for n, coefficient in self.coefficients.items():
            energy = (self.hbar**2 * math.pi**2 * n**2) / (2.0 * self.mass * self.length**2)
            basis = math.sqrt(2.0 / self.length) * np.sin(n * math.pi * x / self.length)
            psi += coefficient * basis * np.exp(-1j * energy * self.time / self.hbar)
        return _frame_from_psi(
            psi=psi,
            coordinates=self.coordinates,
            spacing=self.spacing,
            potential=np.zeros_like(x),
            time=self.time,
            source="particle_in_box",
            hbar=self.hbar,
            mass=self.mass,
            metadata={"modes": tuple(sorted(self.coefficients)), "length": self.length},
        )

    def descriptor(self, dt: float) -> WavefunctionDescriptor:
        return self.frame(dt).descriptor


class QuantumRotorSource:
    """Exact wavefunction on a circle with integer angular-momentum modes."""

    def __init__(
        self,
        *,
        n_points: int = 256,
        coefficients: Optional[Mapping[int, complex]] = None,
        hbar: float = 1.0,
        moment_of_inertia: float = 1.0,
    ) -> None:
        self.coordinates = (np.linspace(0.0, 2.0 * math.pi, n_points, endpoint=False),)
        self.spacing = (2.0 * math.pi / n_points,)
        self.coefficients = dict(coefficients or {-2: 0.5, 1: 1.0, 3: 0.5j})
        norm = math.sqrt(sum(abs(value) ** 2 for value in self.coefficients.values()))
        self.coefficients = {key: value / norm for key, value in self.coefficients.items()}
        self.hbar = float(hbar)
        self.moment_of_inertia = float(moment_of_inertia)
        self.time = 0.0

    def reset(self) -> None:
        self.time = 0.0

    def frame(self, dt: float = 0.0) -> WavefunctionFrame:
        self.time += dt
        phi = self.coordinates[0]
        psi = np.zeros_like(phi, dtype=np.complex128)
        for angular_momentum, coefficient in self.coefficients.items():
            energy = self.hbar**2 * angular_momentum**2 / (2.0 * self.moment_of_inertia)
            basis = np.exp(1j * angular_momentum * phi) / math.sqrt(2.0 * math.pi)
            psi += coefficient * basis * np.exp(-1j * energy * self.time / self.hbar)
        effective_mass = self.moment_of_inertia
        return _frame_from_psi(
            psi=psi,
            coordinates=self.coordinates,
            spacing=self.spacing,
            potential=np.zeros_like(phi),
            time=self.time,
            source="quantum_rotor",
            hbar=self.hbar,
            mass=effective_mass,
            metadata={"angular_momenta": tuple(sorted(self.coefficients))},
        )

    def descriptor(self, dt: float) -> WavefunctionDescriptor:
        return self.frame(dt).descriptor


def _associated_legendre(l_value: int, m_value: int, x: Array) -> Array:
    m_abs = abs(m_value)
    if l_value < m_abs:
        raise ValueError("Spherical harmonic requires l >= |m|.")
    p_mm = np.ones_like(x, dtype=float)
    if m_abs > 0:
        double_factorial = 1.0
        for factor in range(1, 2 * m_abs, 2):
            double_factorial *= factor
        p_mm = ((-1.0) ** m_abs) * double_factorial * np.maximum(0.0, 1.0 - x**2) ** (m_abs / 2.0)
    if l_value == m_abs:
        return p_mm
    p_m1m = x * (2 * m_abs + 1) * p_mm
    if l_value == m_abs + 1:
        return p_m1m
    p_lm2, p_lm1 = p_mm, p_m1m
    for ell in range(m_abs + 2, l_value + 1):
        p_lm = (
            ((2 * ell - 1) * x * p_lm1) - ((ell + m_abs - 1) * p_lm2)
        ) / (ell - m_abs)
        p_lm2, p_lm1 = p_lm1, p_lm
    return p_lm1


def spherical_harmonic(l_value: int, m_value: int, theta: Array, phi: Array) -> Array:
    """NumPy-only normalized complex spherical harmonic Y_l^m."""

    m_abs = abs(m_value)
    normalization = math.sqrt(
        ((2 * l_value + 1) / (4.0 * math.pi))
        * (math.factorial(l_value - m_abs) / math.factorial(l_value + m_abs))
    )
    positive = normalization * _associated_legendre(l_value, m_abs, np.cos(theta)) * np.exp(1j * m_abs * phi)
    if m_value < 0:
        return ((-1) ** m_abs) * np.conj(positive)
    return positive


class SphericalHarmonicSource:
    """Time-evolving superposition on S^2 using rotor energies l(l+1)/2I."""

    def __init__(
        self,
        *,
        n_theta: int = 64,
        n_phi: int = 128,
        states: Optional[Sequence[tuple[int, int, complex]]] = None,
        hbar: float = 1.0,
        moment_of_inertia: float = 1.0,
    ) -> None:
        d_theta = math.pi / n_theta
        self.theta = (np.arange(n_theta) + 0.5) * d_theta
        self.phi = np.linspace(0.0, 2.0 * math.pi, n_phi, endpoint=False)
        self.coordinates = (self.theta, self.phi)
        self.spacing = (d_theta, 2.0 * math.pi / n_phi)
        theta_grid, phi_grid = np.meshgrid(self.theta, self.phi, indexing="ij")
        self.theta_grid = theta_grid
        self.phi_grid = phi_grid
        self.weights = np.sin(theta_grid) * self.spacing[0] * self.spacing[1]
        self.states = list(states or [(1, -1, 0.5), (2, 0, 1.0), (3, 2, 0.5j)])
        coefficient_norm = math.sqrt(sum(abs(state[2]) ** 2 for state in self.states))
        self.states = [(ell, m, coefficient / coefficient_norm) for ell, m, coefficient in self.states]
        self.hbar = float(hbar)
        self.moment_of_inertia = float(moment_of_inertia)
        self.basis = [
            spherical_harmonic(ell, m, theta_grid, phi_grid)
            for ell, m, _ in self.states
        ]
        self.time = 0.0

    def reset(self) -> None:
        self.time = 0.0

    def frame(self, dt: float = 0.0) -> WavefunctionFrame:
        self.time += dt
        psi = np.zeros_like(self.theta_grid, dtype=np.complex128)
        for (ell, _m, coefficient), basis in zip(self.states, self.basis):
            energy = self.hbar**2 * ell * (ell + 1) / (2.0 * self.moment_of_inertia)
            psi += coefficient * basis * np.exp(-1j * energy * self.time / self.hbar)
        psi = _normalize(psi, self.weights)
        d_theta, d_phi = np.gradient(psi, *self.spacing, edge_order=2)
        sin_theta = np.maximum(np.sin(self.theta_grid), 1.0e-6)
        current_theta = (self.hbar / self.moment_of_inertia) * np.imag(np.conj(psi) * d_theta)
        current_phi = (self.hbar / self.moment_of_inertia) * np.imag(np.conj(psi) * d_phi) / sin_theta
        energy_density = (self.hbar**2 / (2.0 * self.moment_of_inertia)) * (
            np.abs(d_theta) ** 2 + (np.abs(d_phi) ** 2 / sin_theta**2)
        )
        return _frame_from_psi(
            psi=psi,
            coordinates=self.coordinates,
            spacing=self.spacing,
            potential=np.zeros_like(psi.real),
            time=self.time,
            source="spherical_harmonic",
            hbar=self.hbar,
            mass=self.moment_of_inertia,
            integration_weights=self.weights,
            current_override=(current_theta, current_phi),
            energy_density_override=energy_density,
            metadata={"states": tuple((ell, m) for ell, m, _ in self.states)},
        )

    def descriptor(self, dt: float) -> WavefunctionDescriptor:
        return self.frame(dt).descriptor


def _generalized_laguerre(order: int, alpha: int, x: Array) -> Array:
    if order == 0:
        return np.ones_like(x)
    if order == 1:
        return 1.0 + alpha - x
    l_nm2 = np.ones_like(x)
    l_nm1 = 1.0 + alpha - x
    for n in range(2, order + 1):
        l_n = (
            ((2 * n - 1 + alpha - x) * l_nm1) - ((n - 1 + alpha) * l_nm2)
        ) / n
        l_nm2, l_nm1 = l_nm1, l_n
    return l_nm1


def _hydrogen_radial(n_value: int, l_value: int, radius: Array, bohr_radius: float) -> Array:
    if n_value < 1 or l_value < 0 or l_value >= n_value:
        raise ValueError("Hydrogen states require n >= 1 and 0 <= l < n.")
    rho = 2.0 * radius / (n_value * bohr_radius)
    normalization = (2.0 / (n_value * bohr_radius)) ** 1.5
    normalization *= math.sqrt(
        math.factorial(n_value - l_value - 1)
        / (2.0 * n_value * math.factorial(n_value + l_value))
    )
    laguerre = _generalized_laguerre(n_value - l_value - 1, 2 * l_value + 1, rho)
    return normalization * np.exp(-0.5 * rho) * rho**l_value * laguerre


class HydrogenSuperpositionSource3D:
    """Continuous 3D hydrogen wavefunction, including orbital superpositions.

    States are ``(n, l, m, complex_coefficient)`` tuples.  Atomic-unit energy
    evolution is used by default, while the spatial grid is explicitly exposed.
    """

    def __init__(
        self,
        *,
        grid_shape: int | Sequence[int] = 32,
        extent: float | Sequence[float] = 20.0,
        states: Optional[Sequence[tuple[int, int, int, complex]]] = None,
        bohr_radius: float = 1.0,
        hbar: float = 1.0,
    ) -> None:
        self.grid_shape = _as_tuple(grid_shape, 3, int)
        self.extent = _as_tuple(extent, 3, float)
        self.coordinates = tuple(
            np.linspace(-length / 2.0, length / 2.0, count, endpoint=False)
            for length, count in zip(self.extent, self.grid_shape)
        )
        self.spacing = tuple(float(axis[1] - axis[0]) for axis in self.coordinates)
        x, y, z = np.meshgrid(*self.coordinates, indexing="ij")
        radius = np.sqrt(x**2 + y**2 + z**2)
        safe_radius = np.maximum(radius, EPS)
        theta = np.arccos(np.clip(z / safe_radius, -1.0, 1.0))
        phi = np.arctan2(y, x)
        self.radius = radius
        self.bohr_radius = float(bohr_radius)
        self.hbar = float(hbar)
        self.states = list(states or [(1, 0, 0, 1.0), (2, 1, 0, 1.0j)])
        coefficient_norm = math.sqrt(sum(abs(state[3]) ** 2 for state in self.states))
        self.states = [
            (n, ell, m, coefficient / coefficient_norm)
            for n, ell, m, coefficient in self.states
        ]
        cell_volume = float(np.prod(self.spacing))
        self.basis: list[Array] = []
        for n, ell, m, _ in self.states:
            orbital = _hydrogen_radial(n, ell, radius, self.bohr_radius) * spherical_harmonic(ell, m, theta, phi)
            self.basis.append(_normalize(orbital, cell_volume))
        softening = 0.5 * min(self.spacing)
        self.potential = -1.0 / np.sqrt(radius**2 + softening**2)
        self.time = 0.0

    def reset(self) -> None:
        self.time = 0.0

    def frame(self, dt: float = 0.0) -> WavefunctionFrame:
        self.time += dt
        psi = np.zeros(self.grid_shape, dtype=np.complex128)
        for (n, _ell, _m, coefficient), basis in zip(self.states, self.basis):
            energy = -0.5 / (n**2)
            psi += coefficient * basis * np.exp(-1j * energy * self.time / self.hbar)
        return _frame_from_psi(
            psi=psi,
            coordinates=self.coordinates,
            spacing=self.spacing,
            potential=self.potential,
            time=self.time,
            source="hydrogen_superposition_3d",
            hbar=self.hbar,
            mass=1.0,
            metadata={
                "states": tuple((n, ell, m) for n, ell, m, _ in self.states),
                "bohr_radius": self.bohr_radius,
            },
        )

    def descriptor(self, dt: float) -> WavefunctionDescriptor:
        return self.frame(dt).descriptor


WAVEFUNCTION_SOURCE_NAMES = (
    "schrodinger_packet",
    "schrodinger_packet_3d",
    "free_packet_1d",
    "free_packet_3d",
    "harmonic_oscillator",
    "harmonic_oscillator_3d",
    "coherent_state",
    "squeezed_state",
    "particle_in_box",
    "quantum_rotor",
    "double_well",
    "barrier_scattering",
    "periodic_lattice",
    "hydrogen_orbital_field",
    "hydrogen_superposition_3d",
    "spherical_harmonic",
)


def _merged(defaults: Mapping[str, Any], overrides: Mapping[str, Any]) -> dict[str, Any]:
    result = dict(defaults)
    result.update(overrides)
    return result


def create_wavefunction_source(name: str, **kwargs: Any) -> WavefunctionSource:
    """Create a named source without allocating every 3D model in advance."""

    if name in ("schrodinger_packet", "free_packet_1d"):
        return SchrodingerPacketSource1D(**kwargs)
    if name in ("schrodinger_packet_3d", "free_packet_3d"):
        return SchrodingerPacketSource3D(**kwargs)
    if name == "harmonic_oscillator":
        return HarmonicOscillatorSource(**_merged({"state": "harmonic_eigen", "mode": 2}, kwargs))
    if name == "harmonic_oscillator_3d":
        return HarmonicOscillatorSource(**_merged({"state": "harmonic_eigen", "dimensions": 3, "grid_shape": 32, "mode": (1, 2, 3)}, kwargs))
    if name == "coherent_state":
        return HarmonicOscillatorSource(**_merged({"state": "coherent", "center": 2.0, "momentum": 1.0}, kwargs))
    if name == "squeezed_state":
        return HarmonicOscillatorSource(**_merged({"state": "squeezed", "center": 1.5, "momentum": 0.5}, kwargs))
    if name == "particle_in_box":
        return ParticleInBoxSource(**kwargs)
    if name == "quantum_rotor":
        return QuantumRotorSource(**kwargs)
    if name == "double_well":
        return PotentialWavefunctionSource(**_merged({"potential": "double_well", "center": -2.0, "sigma": 0.65, "source_name": "double_well"}, kwargs))
    if name == "barrier_scattering":
        return PotentialWavefunctionSource(**_merged({"potential": "barrier", "center": -4.0, "momentum": 4.0, "sigma": 0.7, "source_name": "barrier_scattering"}, kwargs))
    if name == "periodic_lattice":
        return PotentialWavefunctionSource(**_merged({"potential": "periodic_lattice", "center": -3.0, "momentum": 2.0, "source_name": "periodic_lattice"}, kwargs))
    if name == "hydrogen_orbital_field":
        return HydrogenSuperpositionSource3D(**_merged({"states": [(2, 1, 0, 1.0)]}, kwargs))
    if name == "hydrogen_superposition_3d":
        return HydrogenSuperpositionSource3D(**kwargs)
    if name == "spherical_harmonic":
        return SphericalHarmonicSource(**kwargs)
    raise ValueError(f"Unknown wavefunction source {name!r}; choose from {WAVEFUNCTION_SOURCE_NAMES}.")


__all__ = [
    "WavefunctionDescriptor",
    "WavefunctionFrame",
    "WavefunctionSource",
    "PotentialWavefunctionSource",
    "SchrodingerPacketSource1D",
    "SchrodingerPacketSource3D",
    "HarmonicOscillatorSource",
    "ParticleInBoxSource",
    "QuantumRotorSource",
    "SphericalHarmonicSource",
    "HydrogenSuperpositionSource3D",
    "WAVEFUNCTION_SOURCE_NAMES",
    "create_wavefunction_source",
    "spherical_harmonic",
]
