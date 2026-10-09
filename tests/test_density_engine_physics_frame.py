import numpy as np

from density.density_matrix_engine_4q import (
    DIMENSION,
    X,
    Y,
    DensityMatrixEngine,
    pair_operator,
    state_to_density,
)
from qmw.core import QuantumDataBus, QuantumFrameAccumulator


def _bare_engine(rho, samples=4):
    engine = DensityMatrixEngine.__new__(DensityMatrixEngine)
    engine.rho = np.asarray(rho, dtype=np.complex128)
    engine.logical_time = 0.0
    engine.state_revision = 1
    engine.configuration_revision = 0
    engine.last_event_id = 0
    engine.last_event_type = "test"
    engine.source_descriptor = None
    engine.excitation_source_kind = "test"
    engine.data_bus = QuantumDataBus()
    engine.physics_frame_accumulator = QuantumFrameAccumulator(samples=samples)
    engine.data_bus.state_bus.subscribe(engine.physics_frame_accumulator)
    engine.latest_state_frame = None
    return engine


def _xy_01_hamiltonian():
    return 0.5 * (
        pair_operator(0, X, 1, X)
        + pair_operator(0, Y, 1, Y)
    )


def test_live_density_engine_populates_physics_frame_channels():
    psi = np.zeros(DIMENSION, dtype=np.complex128)
    psi[8] = 1.0 / np.sqrt(2.0)       # |1000>
    psi[4] = -1j / np.sqrt(2.0)       # |0100>
    engine = _bare_engine(state_to_density(psi), samples=4)
    hamiltonian = _xy_01_hamiltonian()

    for i in range(4):
        engine.logical_time = 0.1 * i
        frame = engine._publish_state_frame(hamiltonian, 0.1)

    assert frame.arrays["psi"].shape == (16,)
    assert frame.arrays["site_populations"].shape == (4,)
    assert frame.arrays["pauli_x"].shape == (4,)
    assert frame.arrays["pauli_y"].shape == (4,)
    assert frame.arrays["pauli_z"].shape == (4,)
    assert frame.arrays["edge_currents"].shape == (3,)
    assert frame.arrays["edge_currents"][0] > 0.0
    assert np.allclose(frame.arrays["edge_currents"][1:], 0.0, atol=1e-12)

    assert engine.physics_frame_ready
    trajectory = engine.physics_frame()

    assert trajectory.t.shape == (4,)
    assert trajectory.psi.shape == (4, 16)
    assert trajectory.rho.shape == (4, 16, 16)
    assert trajectory.observables["site_populations"].shape == (4, 4)
    assert trajectory.observables["pauli_x"].shape == (4, 4)
    assert trajectory.observables["pauli_y"].shape == (4, 4)
    assert trajectory.observables["pauli_z"].shape == (4, 4)
    assert trajectory.observables["edge_currents"].shape == (4, 3)
    assert trajectory.observables["energy"].shape == (4,)
    assert trajectory.observables["purity"].shape == (4,)
    assert trajectory.observables["commutator_activity"].shape == (4,)

    validation = trajectory.validate_quantum()
    assert validation["trace_error_max"] < 1e-12
    assert validation["state_norm_error_max"] < 1e-12
    assert validation["positive_semidefinite"]


def test_live_density_engine_does_not_invent_psi_for_mixed_state():
    rho = np.eye(DIMENSION, dtype=np.complex128) / DIMENSION
    engine = _bare_engine(rho, samples=1)

    frame = engine._publish_state_frame(
        np.zeros((DIMENSION, DIMENSION), dtype=np.complex128),
        0.1,
    )

    assert frame.metadata["psi_available"] is False
    assert "psi" not in frame.arrays

    trajectory = engine.physics_frame()
    assert trajectory.psi is None
    assert trajectory.rho.shape == (1, 16, 16)
