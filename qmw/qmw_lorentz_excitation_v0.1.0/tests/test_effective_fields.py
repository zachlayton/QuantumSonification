import numpy as np

from qmw.excitation import EffectiveFieldConfig, EffectiveFields
from qmw.fields import QuantumMatrixField


def test_linear_magnitude_produces_known_negative_gradient() -> None:
    y, x = np.mgrid[0:16, 0:16]
    potential = 10.0 + 3.0 * x + 2.0 * y
    matrix_field = QuantumMatrixField(potential.astype(np.complex128))

    fields = EffectiveFields.from_matrix(
        matrix_field,
        EffectiveFieldConfig(magnetic_scale=0.0),
    )

    np.testing.assert_allclose(fields.potential, potential)
    np.testing.assert_allclose(fields.electric[..., 0], -3.0, atol=1e-12)
    np.testing.assert_allclose(fields.electric[..., 1], -2.0, atol=1e-12)
    np.testing.assert_allclose(fields.electric[..., 2], 0.0, atol=1e-12)


def test_constant_magnetic_override_is_spatially_uniform() -> None:
    matrix_field = QuantumMatrixField(np.ones((16, 16), dtype=np.complex128))
    expected = np.array([0.25, -0.5, 3.0])

    fields = EffectiveFields.from_matrix(
        matrix_field,
        EffectiveFieldConfig(constant_magnetic_field=expected),
    )

    np.testing.assert_allclose(fields.magnetic, np.broadcast_to(expected, (16, 16, 3)))


def test_smooth_phase_ramp_has_zero_wrapped_circulation() -> None:
    y, x = np.mgrid[0:16, 0:16]
    matrix_field = QuantumMatrixField(np.exp(1j * (0.1 * x + 0.2 * y)))

    fields = EffectiveFields.from_matrix(matrix_field)

    np.testing.assert_allclose(fields.magnetic, 0.0, atol=1e-12)


def test_phase_vortex_produces_localized_magnetic_like_circulation() -> None:
    y, x = np.mgrid[0:16, 0:16]
    phase = np.arctan2(y - 7.5, x - 7.5)
    matrix_field = QuantumMatrixField(np.exp(1j * phase))

    fields = EffectiveFields.from_matrix(matrix_field)
    b_z = fields.magnetic[..., 2]

    np.testing.assert_allclose(np.max(b_z), 0.25, atol=1e-12)
    np.testing.assert_allclose(np.sum(b_z), 1.0, atol=1e-12)
