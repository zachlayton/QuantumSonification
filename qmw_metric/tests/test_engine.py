import numpy as np
import pytest

from qmw_metric.config import QuantumMetricConfig, ResonatorConfig
from qmw_metric.engine import QuantumMetricEngine


def test_complete_vertical_slice_is_finite_and_shader_uses_same_coordinates():
    config = QuantumMetricConfig(
        grid_size=(12, 12),
        mode_count=5,
        resonator=ResonatorConfig(frequency_scale_hz=20.0),
    )
    engine = QuantumMetricEngine(config)
    state = np.zeros(16, dtype=np.complex128)
    state[5] = 1.0
    field = engine.update_quantum_frame(np.outer(state, state.conj()), 0.0)
    trajectory = engine.process_control_step(1.0 / 500.0)
    audio = engine.process_audio_block(128)
    assert np.all(np.isfinite(audio))
    assert engine.mode_frame is not None
    assert engine.modal_excitation.shape == (5,)
    assert np.isclose(
        float(engine.shader.sample("potential", trajectory.position)),
        float(engine.grid.sample(field.potential, trajectory.position)),
        atol=1e-8,
    )
    assert engine.system_frame is not None
    assert engine.system_frame.revision == engine.shader.frame.revision
    assert engine.system_frame.shader.mode_shapes.shape == engine.mode_frame.modes.shape
    assert engine.system_frame.shader.trajectory_positions.shape == (1, 2)
    assert engine.system_frame.field.density.flags.writeable is False
    assert engine.system_frame.projection_basis == "localized_gaussians.v1"
    assert engine.system_frame.potential_model == "screened_poisson.periodic_fft.v1"
    assert engine.system_frame.metric_model == "conformal_2d_plus_lapse.v1"
    assert engine.system_frame.topography_mode == "explicit_force"


def test_measurement_quench_is_an_explicit_separate_operation():
    config = QuantumMetricConfig(grid_size=(12, 12), mode_count=4)
    engine = QuantumMetricEngine(config)
    rho_a = np.diag([1.0] + [0.0] * 15).astype(np.complex128)
    rho_b = np.diag([0.0, 1.0] + [0.0] * 14).astype(np.complex128)
    engine.update_quantum_frame(rho_a, 0.0)
    engine.resonator.set_amplitudes(np.array((1.0, 0.0, 0.0, 0.0)))
    positions_before = engine.resonator.positions.copy()
    engine.apply_measurement_quench(rho_b, 0.1)
    assert engine.field_frame.time == 0.1
    assert np.all(np.isfinite(engine.resonator.positions))
    assert np.array_equal(engine.resonator.positions, positions_before)
    assert engine.resonator.amplitude_correction_samples > 0
    remaining = engine.resonator.amplitude_correction_samples
    engine.resonator.process_block(np.zeros(4), 64)
    assert engine.resonator.amplitude_correction_samples == remaining - 64


def test_source_and_system_revisions_are_monotonic_and_synchronized():
    engine = QuantumMetricEngine(QuantumMetricConfig(grid_size=(12, 12), mode_count=4))
    rho = np.eye(16, dtype=np.complex128) / 16.0
    engine.update_quantum_frame(rho, 0.0, source_revision=7)
    first_revision = engine.system_frame.revision
    engine.process_control_step(0.002)
    assert engine.system_frame.revision == first_revision + 1
    assert engine.system_frame.source_revision == 7
    assert engine.system_frame.shader.source_revision == 7
    assert engine.system_frame.trajectory.time == engine.system_frame.time
    with pytest.raises(ValueError, match="source_revision"):
        engine.update_quantum_frame(rho, 0.01, source_revision=6)
    with pytest.raises(ValueError, match="time"):
        engine.update_quantum_frame(rho, -0.01, source_revision=8)


def test_custom_projection_basis_requires_provenance_identifier():
    config = QuantumMetricConfig(grid_size=(12, 12), mode_count=4)
    basis = np.ones((16, 12, 12), dtype=np.complex128)
    with pytest.raises(ValueError, match="basis_id"):
        QuantumMetricEngine(config, basis=basis)
    engine = QuantumMetricEngine(config, basis=basis, basis_id="test.constant_basis.v1")
    assert engine.basis_id == "test.constant_basis.v1"
