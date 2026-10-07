import numpy as np

from qmw_metric.config import ResonatorConfig
from qmw_metric.frames import CurvedModeFrame
from qmw_metric.modal_resonator import ModalResonator


def _frame(time: float, connection: np.ndarray) -> CurvedModeFrame:
    return CurvedModeFrame(
        time=time,
        eigenvalues=np.zeros(2),
        frequencies=np.zeros(2),
        modes=np.array(([[1.0, 0.0], [0.0, 0.0]], [[0.0, 1.0], [0.0, 0.0]])),
        damping=np.zeros(2),
        gains=np.zeros(2),
        basis_derivative_overlap=connection,
        metric_rate_overlap=np.zeros((2, 2)),
        intermodal_connection=connection,
    )


def test_intermodal_connection_rotates_state_smoothly_without_energy_growth():
    resonator = ModalResonator(
        ResonatorConfig(sample_rate=1_000.0, retune_time_seconds=.02)
    )
    zero = np.zeros((2, 2))
    resonator.update_mode_frame(_frame(0.0, zero))
    resonator.set_amplitudes(np.array((1.0, 0.0)))
    connection = np.array(((0.0, -2.0), (2.0, 0.0)))
    resonator.update_mode_frame(_frame(.2, connection))
    assert np.array_equal(resonator.positions, np.array((1.0, 0.0)))
    assert resonator.amplitude_correction_samples == 20
    target = resonator.positions + resonator.amplitude_correction
    assert np.isclose(np.linalg.norm(target), 1.0, atol=1e-12)
    resonator.process_block(np.zeros(2), 20)
    assert resonator.amplitude_correction_samples == 0
    assert np.allclose(resonator.positions, target, atol=1e-12)


def test_zero_transition_time_retains_immediate_state_install_contract():
    resonator = ModalResonator(
        ResonatorConfig(sample_rate=1_000.0, retune_time_seconds=.02)
    )
    resonator.update_mode_frame(_frame(0.0, np.zeros((2, 2))))
    resonator.transition_state(np.array((.2, .3)), np.array((.4, .5)), 0.0)
    assert np.array_equal(resonator.positions, np.array((.2, .3)))
    assert np.array_equal(resonator.velocities, np.array((.4, .5)))
