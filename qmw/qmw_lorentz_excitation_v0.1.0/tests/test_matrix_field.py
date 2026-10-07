import numpy as np
import pytest

from qmw.fields import QuantumMatrixField


def test_matrix_field_requires_exactly_16_by_16_complex_values() -> None:
    with pytest.raises(ValueError, match="shape"):
        QuantumMatrixField(np.zeros((8, 8), dtype=np.complex128))
    with pytest.raises(TypeError, match="complex dtype"):
        QuantumMatrixField(np.zeros((16, 16), dtype=float))


def test_bilinear_sampling_and_coordinate_convention() -> None:
    y, x = np.mgrid[0:16, 0:16]
    field = QuantumMatrixField((x + 2.0 * y).astype(np.complex128))

    sampled = field.sample(field.magnitude, [3.25, 4.5])

    assert sampled == pytest.approx(3.25 + 2.0 * 4.5)


def test_sampling_clamps_out_of_bounds_and_reports_it() -> None:
    field = QuantumMatrixField(np.ones((16, 16), dtype=np.complex128))

    x_index, y_index, in_bounds = field.grid_indices([-3.0, 22.0])

    assert (x_index, y_index) == (0.0, 15.0)
    assert in_bounds is False
    np.testing.assert_allclose(field.clipped_position([-3.0, 22.0]), [0.0, 15.0, 0.0])

