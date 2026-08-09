import numpy as np
import pytest

from excitation.wavefunction_sources_v1 import (
    PotentialWavefunctionSource,
    WAVEFUNCTION_SOURCE_NAMES,
    create_wavefunction_source,
)
from hamiltonian.hamiltonian_state import HamiltonianState
from hamiltonian.mutator_quantum_sources_v2 import HamiltonianMutator


def test_installed_entry_point_supports_three_dimensions():
    source = PotentialWavefunctionSource(dimensions=3, grid_shape=12)
    frame = source.frame(0.02)
    assert frame.psi.shape == (12, 12, 12)
    assert frame.dimension == 3
    assert frame.norm == pytest.approx(1.0, abs=1e-12)


def test_all_named_wavefunction_sources_are_visible_to_mutator():
    available = set(HamiltonianMutator.available_sources())
    assert set(WAVEFUNCTION_SOURCE_NAMES) <= available
    assert {"audio", "hydrogen_spectrum", "hydrogen_orbital"} <= available


def test_three_dimensional_source_allocation_is_lazy():
    mutator = HamiltonianMutator(excitation_kind="audio")
    assert mutator._sources == {}
    mutator.set_excitation_kind("schrodinger_packet_3d")
    assert mutator._sources == {}
    frame = mutator.source_frame()
    assert frame.psi.shape == (32, 32, 32)
    assert tuple(mutator._sources) == ("schrodinger_packet_3d",)


def test_field_descriptor_projects_into_normalized_hamiltonian():
    mutator = HamiltonianMutator(excitation_kind="quantum_rotor")
    result = mutator.mutate_from_physics_source(
        HamiltonianState(x=1.0, y=0.0, z=0.0),
        0.05,
    )
    assert np.linalg.norm((result.x, result.y, result.z)) == pytest.approx(1.0)


def test_continuous_hydrogen_field_is_not_legacy_point_sampling():
    source = create_wavefunction_source(
        "hydrogen_orbital_field",
        grid_shape=12,
    )
    frame = source.frame()
    assert frame.psi.shape == (12, 12, 12)
    assert np.iscomplexobj(frame.psi)
    assert frame.norm == pytest.approx(1.0, abs=1e-12)
