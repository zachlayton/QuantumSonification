"""Fourier-space complex scalar PDE with charge-preserving velocity Verlet."""
from __future__ import annotations
import numpy as np
from ...core.domain import Domain
from ...core.frame import StateData
from ...core.operators import laplacian, wavenumbers
from ...core.spec import ModuleSpec, PortSpec, ParameterSpec
from .potentials import PolynomialPotential
from .qball import checked_qball_profile


class ScalarFieldModel:
    model_id = "complex-scalar-field-1d"

    def __init__(self, domain: Domain | None = None,
                 potential: PolynomialPotential | None = None):
        self.domain = domain or Domain.periodic()
        self.domain.require_periodic_space()
        self.potential = potential or PolynomialPotential()
        self.initialization_metadata: dict = {}

    def selected_potential(self, controls=None) -> PolynomialPotential:
        controls = controls or {}
        return PolynomialPotential(
            mass_squared=float(controls.get("mass_squared", self.potential.mass_squared)),
            attraction=float(controls.get("attraction", self.potential.attraction)),
            repulsion=float(controls.get("repulsion", self.potential.repulsion)),
        )

    def initialize(self, controls=None) -> StateData:
        controls = controls or {}
        omega = float(controls.get("rotation_frequency", .95))
        if not np.isfinite(omega):
            raise ValueError("Scalar rotation frequency must be finite")
        initial = str(controls.get("init", "rotating_gaussian"))
        potential = self.selected_potential(controls)
        if initial == "qball":
            field, self.initialization_metadata = checked_qball_profile(
                self.domain, potential, omega,
            )
        elif initial == "rotating_gaussian":
            amplitude = float(controls.get("amplitude", .6))
            width = float(controls.get("width", min(3.0, self.domain.length/8)))
            if not np.isfinite([amplitude, width]).all() or amplitude < 0 or width <= 0:
                raise ValueError("Scalar amplitude must be finite and nonnegative; width must be positive")
            if width < 2*self.domain.spacing[0] or width > self.domain.length/4:
                raise ValueError("Scalar Gaussian width must be resolved (>=2dx) and <=L/4")
            center = float(controls.get("center", 0.0))
            if not np.isfinite(center):
                raise ValueError("Scalar center must be finite")
            center = (center+self.domain.length/2) % self.domain.length-self.domain.length/2
            distance = self.domain.coordinates-center
            # Summing smooth periodic images avoids the derivative cusp caused
            # by a Gaussian of the shortest wrapped distance, especially when wide.
            count = max(2, int(np.ceil(12*width/self.domain.length))+1)
            field = np.zeros(self.domain.shape, dtype=complex)
            for image in range(-count, count+1):
                field += amplitude*np.exp(-.5*((distance+image*self.domain.length)/width)**2)
            self.initialization_metadata = {
                "dimension": 1, "initializer": "rotating-gaussian-scalar-demo",
                "description": "Rotating initial data; not a stationary Q-ball solution.",
            }
        else:
            raise ValueError(f"Unsupported scalar initializer: {initial}")
        return StateData(phi=field, pi=1j*omega*field)

    def acceleration(self, phi: np.ndarray, controls=None) -> np.ndarray:
        return laplacian(phi, self.domain) + self.selected_potential(controls).force(phi)

    def stable_dt_bound(self, state: StateData, controls=None) -> float:
        potential = self.selected_potential(controls)
        maximum_frequency = np.sqrt(np.max(wavenumbers(self.domain)**2) + potential.curvature_bound(state.phi))
        return float(2/maximum_frequency) if maximum_frequency else float("inf")

    def step(self, state: StateData, controls=None, dt: float = .001) -> StateData:
        state.validate(self.domain)
        if state.phi is None or state.pi is None:
            raise ValueError("Scalar field requires phi and pi")
        if isinstance(dt, (bool, np.bool_)) or not np.isfinite(dt) or dt < 0:
            raise ValueError("dt must be finite and nonnegative")
        if dt == 0:
            return StateData(phi=state.phi.copy(), pi=state.pi.copy())
        bound = self.stable_dt_bound(state, controls)
        if dt >= bound:
            raise ValueError(f"Scalar Verlet dt={dt:g} must be < {bound:g} for the resolved spatial frequencies")
        half_pi = state.pi + .5*dt*self.acceleration(state.phi, controls)
        phi = state.phi + dt*half_pi
        candidate = StateData(phi=phi, pi=half_pi)
        if dt >= self.stable_dt_bound(candidate, controls):
            raise ValueError("Scalar field grew beyond this timestep's stability bound; reduce dt")
        pi = half_pi + .5*dt*self.acceleration(phi, controls)
        result = StateData(phi=phi, pi=pi)
        result.validate(self.domain)
        return result

    def compute_observables(self, state: StateData, controls=None):
        from ...observables.scalar import scalar_observables
        state.validate(self.domain)
        return scalar_observables(state, self.domain, self.selected_potential(controls))

    def module_specs(self) -> tuple[ModuleSpec, ...]:
        potential = self.potential
        return (ModuleSpec(
            "scalar_field", "Complex scalar field",
            r"\dot\Phi=\Pi,\quad\dot\Pi=\partial_x^2\Phi-2U'(|\Phi|^2)\Phi",
            "phi_dot = pi; pi_dot = d_x² phi - 2 U'(|phi|²) phi",
            inputs=(PortSpec("phi", "complex scalar field", "scaled field", "space_1d"),
                    PortSpec("pi", "field velocity", "scaled field/time", "space_1d")),
            outputs=(PortSpec("phi", "evolved field", "scaled field", "space_1d"),
                     PortSpec("pi", "evolved velocity", "scaled field/time", "space_1d")),
            parameters=(
                ParameterSpec("mass_squared", "Mass squared", potential.mass_squared, 0, 4,
                              "1 / scaled time²", "m² in U(s)=m²s/2-a s²/4+b s³/6"),
                ParameterSpec("attraction", "Quartic attraction", potential.attraction, 0, 4,
                              "scaled", "a; positive attraction requires sextic stabilization"),
                ParameterSpec("repulsion", "Sextic repulsion", potential.repulsion, 0, 4,
                              "scaled", "b; stabilizes the attractive quartic term"),
            ),
            description="L=|pi|²/2-|d_x phi|²/2-U. Fourier derivatives and velocity Verlet.",
            destinations=("energy and charge", "region projection", "conservation diagnostics"),
            assumptions=("One spatial dimension; c=1 in scaled variables.",
                         "U(1) charge preserved to roundoff for frozen radial controls.",
                         "Verlet energy has bounded O(dt²) error; dt is checked against spatial frequencies.",
                         "Default Gaussian is a scalar demo; optional qball initializer checks the 1-D profile residual."),
        ),)
