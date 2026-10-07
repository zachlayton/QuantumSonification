"""AtomicOrbitalFrame V4: fixed-manifold hydrogenic Pauli-spinor physics."""

from .evolution import evolve_state
from .model import AtomicManifoldModel, AtomicManifoldSpec
from .observables import observe_state
from .schema import AtomicOrbitalFrame
from .sonification import AtomicSonificationFrame, atomic_sonification_frame
from .spatial import hydrogen_radial, probability_density, spin_density, spinor_wavefunction
from .states import AtomicState, basis_state, pauli_spinor, product_state
from .temporal import AtomicClockReading, AtomicStateClock

__all__ = [
    "AtomicClockReading",
    "AtomicManifoldModel",
    "AtomicManifoldSpec",
    "AtomicOrbitalFrame",
    "AtomicSonificationFrame",
    "AtomicState",
    "AtomicStateClock",
    "atomic_sonification_frame",
    "basis_state",
    "evolve_state",
    "hydrogen_radial",
    "observe_state",
    "pauli_spinor",
    "probability_density",
    "product_state",
    "spin_density",
    "spinor_wavefunction",
]
