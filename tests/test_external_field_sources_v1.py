import math
import unittest

import numpy as np

from excitation.external_field_sources_v1 import (
    HydrogenStarkSource,
    HydrogenZeemanSource,
    LandauLevelSource,
)
from excitation.wavefunction_sources_v1 import (
    WAVEFUNCTION_SOURCE_NAMES,
    create_wavefunction_source,
)


class ExternalFieldSourceTests(unittest.TestCase):
    def test_landau_levels_are_normalized_and_move_at_cyclotron_beats(self):
        source = LandauLevelSource(grid_shape=32, magnetic_field=1.25)
        initial = source.frame()
        evolved = source.frame(0.17)
        self.assertAlmostEqual(evolved.norm, 1.0, places=10)
        self.assertAlmostEqual(
            evolved.metadata["cyclotron_angular_frequency"], 1.25, places=12
        )
        self.assertAlmostEqual(
            evolved.metadata["magnetic_length"], 1.0 / math.sqrt(1.25), places=12
        )
        self.assertGreater(np.max(np.abs(evolved.probability - initial.probability)), 1e-4)
        self.assertEqual(len(evolved.probability_current), 2)
        self.assertEqual(evolved.metadata["gauge"], "Landau A_y=B*x")

    def test_hydrogen_zeeman_has_normal_orbital_splitting(self):
        field = 0.12
        source = HydrogenZeemanSource(grid_shape=16, extent=16.0, field_strength=field)
        initial = source.frame()
        evolved = source.frame(0.3)
        self.assertAlmostEqual(evolved.norm, 1.0, places=10)
        self.assertAlmostEqual(evolved.metadata["splitting"], field, places=12)
        self.assertGreater(np.max(np.abs(evolved.probability - initial.probability)), 1e-5)
        self.assertEqual(evolved.metadata["effect"], "zeeman")

    def test_hydrogen_stark_couples_opposite_parity_states(self):
        source = HydrogenStarkSource(grid_shape=16, extent=16.0, field_strength=0.08)
        initial = source.frame()
        evolved = source.frame(0.5)
        self.assertAlmostEqual(evolved.norm, 1.0, places=10)
        self.assertGreater(evolved.metadata["splitting"], 0.0)
        self.assertGreater(evolved.metadata["basis_populations"][1], 1e-3)
        self.assertGreater(np.max(np.abs(evolved.probability - initial.probability)), 1e-5)
        self.assertEqual(evolved.metadata["effect"], "stark")

    def test_registry_exposes_external_field_family(self):
        for name in ("landau_levels", "hydrogen_zeeman", "hydrogen_stark"):
            self.assertIn(name, WAVEFUNCTION_SOURCE_NAMES)
        self.assertEqual(
            create_wavefunction_source("landau_levels", grid_shape=16).frame().source,
            "landau_levels",
        )


if __name__ == "__main__":
    unittest.main()
