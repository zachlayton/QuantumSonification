"""Registry spanning scalar fields and native non-scalar quantum engines."""

from __future__ import annotations

from typing import Any

from excitation.joint_particle_sources_v1 import IdenticalParticles1DSource
from excitation.spinor_sources_v1 import EPRBellPairSource, SpinHalfPrecessionSource
from excitation.wavefunction_sources_v1 import (
    WAVEFUNCTION_SOURCE_NAMES,
    create_wavefunction_source,
)


NATIVE_QUANTUM_INSTRUMENT_NAMES = (
    "spin_1_2_precession",
    "identical_particles_fermion_boson",
    "quantum_entanglement_epr",
    "epr_bell_pair",
    "dirac_hydrogen_fine_structure",
    "dirac_step_klein",
)

QUANTUM_INSTRUMENT_NAMES = tuple(
    dict.fromkeys((*WAVEFUNCTION_SOURCE_NAMES, *NATIVE_QUANTUM_INSTRUMENT_NAMES))
)


def create_quantum_instrument(name: str, **kwargs: Any):
    if name == "spin_1_2_precession":
        return SpinHalfPrecessionSource(**kwargs)
    if name == "identical_particles_fermion_boson":
        return IdenticalParticles1DSource(**kwargs)
    if name in ("quantum_entanglement_epr", "epr_bell_pair"):
        return EPRBellPairSource(**kwargs)
    if name in ("dirac_hydrogen_fine_structure", "dirac_step_klein"):
        from excitation.advanced_quantum_sources_v1 import (
            DiracHydrogenFineStructureSource,
            DiracStepKleinSource,
        )

        source_type = (
            DiracHydrogenFineStructureSource
            if name == "dirac_hydrogen_fine_structure"
            else DiracStepKleinSource
        )
        return source_type(**kwargs)
    return create_wavefunction_source(name, **kwargs)


__all__ = [
    "NATIVE_QUANTUM_INSTRUMENT_NAMES",
    "QUANTUM_INSTRUMENT_NAMES",
    "create_quantum_instrument",
]
