import numpy as np
import pytest

from qmw.excitation import EffectiveFieldConfig, LorentzExcitationEngine
from qmw.fields import QuantumMatrixField


def test_linear_potential_with_zero_b_obeys_negative_gradient_force() -> None:
    y, x = np.mgrid[0:16, 0:16]
    potential = 20.0 + 1.5 * x - 0.25 * y
    field = QuantumMatrixField(potential.astype(np.complex128))
    charge = 2.0
    engine = LorentzExcitationEngine(
        charge=charge,
        field_config=EffectiveFieldConfig(
            constant_magnetic_field=np.zeros(3),
        ),
    )

    frame = engine.compute(
        matrix_field=field,
        position=np.array([7.25, 6.5, 0.0]),
        velocity=np.array([4.0, -2.0, 0.0]),
        dt=0.01,
    )

    expected_electric = np.array([-1.5, 0.25, 0.0])
    np.testing.assert_allclose(frame.electric_field, expected_electric, atol=1e-12)
    np.testing.assert_allclose(frame.force_vector, charge * expected_electric, atol=1e-12)
    assert frame.force_magnitude == pytest.approx(np.linalg.norm(charge * expected_electric))
    np.testing.assert_allclose(
        frame.force_direction,
        frame.force_vector / frame.force_magnitude,
        atol=1e-12,
    )


def test_constant_b_and_known_velocity_have_analytic_cross_product() -> None:
    field = QuantumMatrixField(np.ones((16, 16), dtype=np.complex128))
    velocity = np.array([2.0, -1.0, 0.0])
    magnetic = np.array([0.0, 0.0, 3.0])
    charge = 0.5
    engine = LorentzExcitationEngine(
        charge=charge,
        field_config=EffectiveFieldConfig(constant_magnetic_field=magnetic),
    )

    frame = engine.compute(
        matrix_field=field,
        position=[8.0, 8.0],
        velocity=velocity,
        dt=0.1,
    )

    expected_cross_product = np.array([-3.0, -6.0, 0.0])
    np.testing.assert_allclose(frame.electric_field, 0.0, atol=1e-12)
    np.testing.assert_allclose(frame.magnetic_field, magnetic, atol=1e-12)
    np.testing.assert_allclose(
        frame.force_vector, charge * expected_cross_product, atol=1e-12
    )


def test_velocity_can_be_estimated_and_force_derivative_tracks_magnitude() -> None:
    field = QuantumMatrixField(np.ones((16, 16), dtype=np.complex128))
    engine = LorentzExcitationEngine(
        field_config=EffectiveFieldConfig(
            constant_magnetic_field=np.array([0.0, 0.0, 2.0])
        )
    )

    initial = engine.compute(
        matrix_field=field,
        position=[1.0, 1.0],
        velocity=None,
        dt=0.5,
    )
    moved = engine.compute(
        matrix_field=field,
        position=[2.0, 1.0],
        velocity=None,
        dt=0.5,
    )

    np.testing.assert_allclose(initial.velocity, 0.0)
    assert initial.force_derivative == 0.0
    np.testing.assert_allclose(moved.velocity, [2.0, 0.0, 0.0])
    np.testing.assert_allclose(moved.force_vector, [0.0, -4.0, 0.0])
    assert moved.force_derivative == pytest.approx(8.0)
    assert moved.diagnostics["velocity_source"] == "estimated"


def test_frame_is_transport_friendly_and_reports_boundary_clipping() -> None:
    field = QuantumMatrixField(np.ones((16, 16), dtype=np.complex128))
    engine = LorentzExcitationEngine()

    frame = engine.compute(
        matrix_field=field,
        position=[-2.0, 20.0],
        velocity=[0.0, 0.0],
        dt=0.1,
    )
    payload = frame.to_dict()

    np.testing.assert_allclose(frame.excitation_position, [0.0, 15.0, 0.0])
    assert frame.diagnostics["position_clipped"] is True
    assert payload["frame_type"] == "qmw.lorentz_excitation"
    assert payload["schema_version"] == "1.0"
    assert payload["force_direction"] == [0.0, 0.0, 0.0]


def test_nonpositive_dt_is_rejected() -> None:
    field = QuantumMatrixField(np.ones((16, 16), dtype=np.complex128))
    engine = LorentzExcitationEngine()

    with pytest.raises(ValueError, match="greater than zero"):
        engine.compute(
            matrix_field=field,
            position=[1.0, 1.0],
            velocity=[0.0, 0.0],
            dt=0.0,
        )
