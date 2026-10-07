"""QMW Quantum Harmonic Oscillator Architecture v1."""

from .backends import (
    NumPyBosonicBackend,
    NumPyCoupledOscillatorBackend,
    OscillatorBackend,
)
from .coupled_model import (
    CoupledOscillatorModel,
    CoupledOscillatorOperators,
    CoupledOscillatorSpec,
)
from .coupled_observables import (
    coupled_frame_from_density,
    partial_traces,
    von_neumann_entropy,
)
from .coupled_schema import CoupledOscillatorFrame
from .coupled_states import product_coherent_state, product_fock_state, product_state
from .evolution import (
    LindbladEnvironment,
    evolve_density,
    evolve_lindblad,
    oscillator_collapse_operators,
    unitary,
)
from .model import OscillatorModel, OscillatorOperators, OscillatorSpec
from .observables import expectation, frame_from_density
from .operators import annihilation_operator, oscillator_operators
from .phase_space import wigner_grid
from .schema import OscillatorFrame, WignerGrid
from .states import (
    coherent_state,
    density_matrix,
    fock_state,
    squeezed_vacuum,
    thermal_state,
    vacuum_state,
)
from .validation import CrossBackendValidation, validate_reference_against_aer

__all__ = [
    "CrossBackendValidation",
    "CoupledOscillatorFrame",
    "CoupledOscillatorModel",
    "CoupledOscillatorOperators",
    "CoupledOscillatorSpec",
    "LindbladEnvironment",
    "NumPyBosonicBackend",
    "NumPyCoupledOscillatorBackend",
    "OscillatorBackend",
    "OscillatorFrame",
    "OscillatorModel",
    "OscillatorOperators",
    "OscillatorSpec",
    "WignerGrid",
    "annihilation_operator",
    "coherent_state",
    "coupled_frame_from_density",
    "density_matrix",
    "evolve_density",
    "evolve_lindblad",
    "expectation",
    "fock_state",
    "frame_from_density",
    "oscillator_operators",
    "oscillator_collapse_operators",
    "partial_traces",
    "product_coherent_state",
    "product_fock_state",
    "product_state",
    "squeezed_vacuum",
    "thermal_state",
    "unitary",
    "vacuum_state",
    "validate_reference_against_aer",
    "von_neumann_entropy",
    "wigner_grid",
]
