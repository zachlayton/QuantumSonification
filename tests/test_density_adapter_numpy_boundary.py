from __future__ import annotations

import inspect
import unittest

import numpy as np

from density.density_adapter import DensityAdapter


class DensityAdapterNumPyBoundaryTests(unittest.TestCase):
    def test_coherence_l1_uses_numpy_without_initializing_mlx(self) -> None:
        rho = np.array(
            [
                [0.5, 0.1 + 0.2j],
                [0.1 - 0.2j, 0.5],
            ],
            dtype=np.complex128,
        )

        observed = DensityAdapter(engine=object()).coherence_l1(rho)

        self.assertAlmostEqual(observed, 2.0 * abs(0.1 + 0.2j))
        self.assertNotIn("mlx.core", inspect.getsource(DensityAdapter.coherence_l1))


if __name__ == "__main__":
    unittest.main()
