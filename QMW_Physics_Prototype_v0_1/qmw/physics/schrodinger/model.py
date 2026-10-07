"""Unitary, symmetric split-step Fourier evolution on a periodic spatial grid.

The controls are frozen for one step. Time-dependent driving is a sequence of
such steps; its work is accounted for by the runtime, separately from flow.
There is no per-step normalization and no dense spatial Hamiltonian.
"""
from __future__ import annotations

from collections import OrderedDict
from collections.abc import Mapping
from numbers import Real

import numpy as np

from qmw.core.domain import Domain
from qmw.core.frame import ControlState, ObservableData, StateData
from qmw.core.operators import wavenumbers
from qmw.core.spec import ModuleSpec, ParameterSpec, PortSpec


class SchrodingerModel:
    """A scaled 1-D Schrödinger model with real, smooth periodic potentials.

    ``packet_width`` is the initial density standard deviation and
    ``packet_momentum`` is canonical momentum, so its group velocity is p/m.
    Initialization periodizes the full complex Gaussian, allowing arbitrary
    resolved local momentum without introducing a discontinuity at the seam.

    ``potential_strength`` multiplies 1-cos(2πx/L). ``barrier_height`` is the
    central value of a sum of Gaussian images of width ``barrier_width``.
    All arrays use domain quadrature, dx sum(|psi|²).
    """

    model_id = "schrodinger_1d"
    supported_controls = frozenset({
        "potential_strength", "barrier_height", "barrier_width",
        "packet_width", "packet_center", "packet_momentum", "mass",
    })

    def __init__(self, domain: Domain | None = None, hbar: float = 1.0,
                 mass: float = 1.0):
        self.domain = domain if domain is not None else Domain.periodic()
        self.domain.require_periodic_space()
        self.hbar = self._positive(hbar, "hbar")
        self.mass = self._positive(mass, "mass")
        self.k = wavenumbers(self.domain)
        self.k.setflags(write=False)
        self._kinetic_phase_cache: OrderedDict[tuple[float, float], np.ndarray] = OrderedDict()
        self._potential_cache_key: tuple[float, float, float] | None = None
        self._potential_cache_value: np.ndarray | None = None
        dx, length = self.domain.spacing[0], self.domain.length
        self.defaults = {
            "potential_strength": 0.0,
            "barrier_height": 0.0,
            "barrier_width": max(2 * dx, min(1.0, length / 16)),
            "packet_width": max(2 * dx, min(2.0, length / 16)),
            "packet_center": -length / 4,
            "packet_momentum": min(1.0, 0.15 * self.hbar * np.pi / dx),
            "mass": self.mass,
        }

    @staticmethod
    def _number(value: object, name: str) -> float:
        if isinstance(value, (bool, np.bool_)) or not isinstance(value, Real):
            raise ValueError(f"{name} must be a finite real number")
        number = float(value)
        if not np.isfinite(number):
            raise ValueError(f"{name} must be a finite real number")
        return number

    @classmethod
    def _positive(cls, value: object, name: str) -> float:
        number = cls._number(value, name)
        if number <= 0:
            raise ValueError(f"{name} must be positive")
        return number

    def _controls(self, controls: ControlState | None) -> dict[str, float]:
        if controls is None:
            return dict(self.defaults)
        if not isinstance(controls, Mapping):
            raise ValueError("Controls must be a mapping of named real parameters")
        unknown = set(controls).difference(self.supported_controls)
        if unknown:
            raise ValueError(f"Unsupported Schrödinger controls: {sorted(unknown, key=str)}")
        result = dict(self.defaults)
        result.update({name: self._number(value, name) for name, value in controls.items()})
        if result["mass"] <= 0:
            raise ValueError("mass must be positive")
        dx, length = self.domain.spacing[0], self.domain.length
        for name in ("packet_width", "barrier_width"):
            if not 2 * dx <= result[name] <= length / 4:
                raise ValueError(f"{name} must lie between 2*dx and L/4")
        # The initial packet must be represented away from the Fourier cutoff.
        # Three inverse density widths give approximately six amplitude-spectrum
        # standard deviations; the 20% margin avoids populating the Nyquist mode.
        bandwidth = 3.0 / result["packet_width"]
        if abs(result["packet_momentum"] / self.hbar) + bandwidth >= 0.8 * np.pi / dx:
            raise ValueError("Initial packet momentum/width is unresolved on this grid")
        result["packet_center"] = ((result["packet_center"] + length / 2) % length
                                   - length / 2)
        return result

    def _potential_from(self, controls: Mapping[str, float]) -> np.ndarray:
        key = tuple(controls[name] for name in (
            "potential_strength", "barrier_height", "barrier_width"))
        if key == self._potential_cache_key:
            return self._potential_cache_value
        strength, height, width = key
        x, length = self.domain.coordinates, self.domain.length
        result = strength * (1.0 - np.cos(2 * np.pi * x / length))
        if height != 0:
            # Images make V and all its derivatives periodic. The omitted tails
            # are exponentially below floating-point precision for width <= L/4.
            images = int(np.ceil(8 * width / length)) + 1
            shape = np.zeros(self.domain.shape, dtype=float)
            central = 0.0
            for image in range(-images, images + 1):
                shape += np.exp(-0.5 * ((x - image * length) / width) ** 2)
                central += np.exp(-0.5 * (image * length / width) ** 2)
            result = result + height * shape / central
        if not np.isfinite(result).all():
            raise ValueError("Potential overflowed; reduce its controls")
        result.setflags(write=False)
        self._potential_cache_key, self._potential_cache_value = key, result
        return result

    def potential(self, controls: ControlState | None = None) -> np.ndarray:
        """Read-only, real periodic V(x); cached for unchanged potential controls."""
        return self._potential_from(self._controls(controls))

    def initialize(self, controls: ControlState | None = None) -> StateData:
        parameters = self._controls(controls)
        x, length = self.domain.coordinates, self.domain.length
        sigma = parameters["packet_width"]
        center = parameters["packet_center"]
        momentum = parameters["packet_momentum"]
        images = int(np.ceil(12 * sigma / length)) + 1
        psi = np.zeros(self.domain.shape, dtype=np.complex128)
        for image in range(-images, images + 1):
            displacement = x - center + image * length
            psi += (np.exp(-displacement**2 / (4 * sigma**2))
                    * np.exp(1j * momentum * displacement / self.hbar))
        norm = float(self.domain.integrate(np.abs(psi)**2))
        if not np.isfinite(norm) or norm <= 0:
            raise ValueError("Initial packet has no finite nonzero norm")
        # Normalization is an initializer operation, never an evolution repair.
        psi /= np.sqrt(norm)
        return StateData(psi=psi)

    def _state_psi(self, state: StateData) -> np.ndarray:
        if not isinstance(state, StateData):
            raise ValueError("Schrödinger state must be StateData")
        state.validate(self.domain)
        if state.psi is None:
            raise ValueError("Schrödinger evolution requires a psi state")
        return np.asarray(state.psi, dtype=np.complex128)

    def _phase(self, mass: float, dt: float) -> np.ndarray:
        key = (mass, dt)
        if key in self._kinetic_phase_cache:
            self._kinetic_phase_cache.move_to_end(key)
            return self._kinetic_phase_cache[key]
        argument = -0.5 * self.hbar / mass * self.k**2 * dt
        if not np.isfinite(argument).all():
            raise ValueError("Kinetic phase overflowed; reduce dt or adjust mass")
        phase = np.exp(1j * argument)
        phase.setflags(write=False)
        self._kinetic_phase_cache[key] = phase
        if len(self._kinetic_phase_cache) > 8:
            self._kinetic_phase_cache.popitem(last=False)
        return phase

    def step(self, state: StateData, controls: ControlState | None,
             dt: float) -> StateData:
        """Apply e^(-i V dt/2hbar) e^(-i T dt/hbar) e^(-i V dt/2hbar)."""
        delta = self._number(dt, "dt")
        if delta < 0:
            raise ValueError("dt must be nonnegative")
        parameters = self._controls(controls)
        psi = self._state_psi(state)
        if delta == 0:
            return StateData(psi=psi.copy())
        potential = self._potential_from(parameters)
        argument = -0.5 * potential / self.hbar * delta
        if not np.isfinite(argument).all():
            raise ValueError("Potential phase overflowed; reduce dt or V")
        potential_half = np.exp(1j * argument)
        transformed = np.fft.fft(potential_half * psi)
        transformed *= self._phase(parameters["mass"], delta)
        psi_next = potential_half * np.fft.ifft(transformed)
        if not np.isfinite(psi_next).all():
            raise ValueError("Nonfinite Schrödinger evolution")
        return StateData(psi=psi_next)

    def hamiltonian_apply(self, psi: np.ndarray,
                          controls: ControlState | None = None) -> np.ndarray:
        """Apply Hpsi via FFT without materializing an N×N operator."""
        parameters = self._controls(controls)
        values = np.asarray(psi, dtype=np.complex128)
        if values.shape != self.domain.shape or not np.isfinite(values).all():
            raise ValueError("psi must be a finite array matching the spatial domain")
        kinetic = (self.hbar**2 / (2 * parameters["mass"]) * self.k**2)
        result = (np.fft.ifft(kinetic * np.fft.fft(values))
                  + self._potential_from(parameters) * values)
        if not np.isfinite(result).all():
            raise ValueError("Hamiltonian application overflowed")
        return result

    def compute_observables(self, state: StateData,
                            controls: ControlState | None = None) -> ObservableData:
        """Delegate model-specific observables to the independent flow module."""
        from qmw.observables.schrodinger import schrodinger_observables
        parameters = self._controls(controls)
        self._state_psi(state)
        return schrodinger_observables(state, self.domain,
                                      self._potential_from(parameters),
                                      hbar=self.hbar, mass=parameters["mass"])

    def module_specs(self) -> tuple[ModuleSpec, ...]:
        dx, length = self.domain.spacing[0], self.domain.length
        defaults = self.defaults
        return (ModuleSpec(
            id="schrodinger_1d", title="Schrödinger Field Evolution",
            equation_latex=(r"i\hbar\partial_t\psi="
                            r"[-\hbar^2\partial_x^2/(2m)+V(x)]\psi"),
            equation_text="i hbar d_t psi = [-hbar²/(2m) d_x² + V(x)] psi",
            inputs=(PortSpec("psi", "complex wavefunction", "scaled amplitude", "space_1d"),
                    PortSpec("controls", "frozen Hamiltonian parameters", "scaled", "parameters")),
            outputs=(PortSpec("psi_next", "evolved wavefunction", "scaled amplitude", "space_1d"),),
            parameters=(
                ParameterSpec("mass", "Mass", defaults["mass"], 0.1, 10.0,
                              "scaled mass", "Inverse mass controls kinetic evolution; changes perform work."),
                ParameterSpec("potential_strength", "Periodic well strength", 0.0, -5.0, 5.0,
                              "scaled energy", "Coefficient of 1-cos(2πx/L)."),
                ParameterSpec("barrier_height", "Gaussian barrier height", 0.0, -5.0, 5.0,
                              "scaled energy", "Value at x=0 of a periodic Gaussian barrier."),
                ParameterSpec("barrier_width", "Barrier width", defaults["barrier_width"],
                              2*dx, length/4, "scaled length", "Standard deviation of each Gaussian image."),
                ParameterSpec("packet_width", "Initial packet width", defaults["packet_width"],
                              2*dx, length/4, "scaled length", "Density standard deviation; used on reset."),
                ParameterSpec("packet_center", "Initial packet center", defaults["packet_center"],
                              -length/2, length/2, "scaled length", "Periodic location; used on reset."),
                ParameterSpec("packet_momentum", "Initial packet momentum", defaults["packet_momentum"],
                              -min(8.0, 0.25*self.hbar*np.pi/dx),
                              min(8.0, 0.25*self.hbar*np.pi/dx), "scaled momentum",
                              "Canonical p; phase gradient=p/hbar, group velocity=p/m. Used on reset."),
            ),
            description="A normalized periodic Gaussian evolves with symmetric Fourier splitting; Hamiltonian controls are explicit.",
            destinations=("density_phase", "probability_current", "energy_density", "energy_flux"),
            assumptions=("One-dimensional uniform periodic spatial domain; scaled variables.",
                         "Real smooth potential, frozen during each step.",
                         "Second-order global timestep accuracy; no per-step renormalization.",
                         "Initialization controls apply when the state is reset."),
        ),)
