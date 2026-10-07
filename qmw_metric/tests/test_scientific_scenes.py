import numpy as np
import pytest

from qmw_metric.config import QuantumMetricConfig
from qmw_metric.scientific_scenes import build_controlled_scientific_scenes


@pytest.fixture(scope="module")
def scenes():
    return build_controlled_scientific_scenes(
        QuantumMetricConfig(grid_size=(16, 16), mode_count=6)
    )


def test_flat_and_one_well_change_only_potential_coupling(scenes):
    assert np.array_equal(scenes.flat.rho, scenes.one_well.rho)
    assert np.array_equal(scenes.flat.populations, scenes.one_well.populations)
    assert scenes.flat.potential_coupling == 0.0
    assert scenes.one_well.potential_coupling > 0.0
    assert np.allclose(scenes.flat.frame.field.potential, 0.0)
    assert np.allclose(scenes.flat.frame.field.sigma, 0.0)
    assert np.allclose(scenes.flat.frame.field.lapse, 1.0)
    assert np.allclose(
        scenes.flat.frame.field.metric[0, 0], 1.0
    )
    assert np.max(np.abs(scenes.one_well.frame.field.potential)) > 0.01


def test_dephasing_preserves_populations_and_removes_only_coherence(scenes):
    coherent = scenes.coherent
    decohered = scenes.decohered
    assert np.array_equal(coherent.populations, decohered.populations)
    assert np.array_equal(np.diag(coherent.rho), np.diag(decohered.rho))
    assert coherent.coherence_l1 > 0.0
    assert decohered.coherence_l1 == 0.0
    assert np.allclose(decohered.rho, np.diag(np.diag(coherent.rho)))
    assert coherent.purity == pytest.approx(1.0)
    assert decohered.purity < coherent.purity


def test_coherence_difference_is_spatially_conservative_but_nontrivial(scenes):
    diagnostics = scenes.diagnostics
    assert abs(diagnostics["interference_density_signed_integral"]) < 1e-12
    assert diagnostics["interference_density_l1"] > 0.05
    assert diagnostics["interference_potential_l2"] > 1e-4
    assert diagnostics["interference_frequency_rms_hz"] > 0.01


def test_scene_frames_preserve_provenance_and_are_read_only(scenes):
    expected_names = (
        "flat_geometry",
        "one_localized_well",
        "coherent_multi_well",
        "decohered_same_populations",
    )
    assert tuple(scene.name for scene in scenes.ordered()) == expected_names
    for revision, scene in enumerate(scenes.ordered(), start=1):
        assert scene.frame.source_revision == revision
        assert scene.frame.projection_basis == "localized_gaussians.controlled_scenes.v1"
        assert scene.frame.provenance == "qmw_metric.effective_metric.v1"
        assert scene.rho.flags.writeable is False
        assert scene.frame.field.density.flags.writeable is False
