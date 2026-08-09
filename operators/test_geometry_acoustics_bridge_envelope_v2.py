from __future__ import annotations

from pathlib import Path
import tempfile

import numpy as np

from geometry_acoustics_bridge_v2 import (
    AcousticBridgeConfig,
    GeometryAcousticsBridgeV2,
)
if __package__:
    from .operator_ecology_controller_v1 import OperatorEcologyPolicy
else:  # Direct-test compatibility.
    from operator_ecology_controller_v1 import OperatorEcologyPolicy
from surface_material_models_v1 import (
    DEFAULT_T60_SECONDS,
    SurfaceMaterialConfig,
    damping_rate_from_t60,
    t60_from_damping_rate,
)


def modal_packet(decays=(0.1, 0.2)):
    return {
        "model": "test_surface",
        "eigenvalues": np.array([1.0, 2.0]),
        "frequencies_hz": np.array([200.0, 317.0]),
        "decay_times_seconds": np.asarray(decays, dtype=np.float64),
        "damping_rates": 1.0 / np.asarray(decays, dtype=np.float64),
        "mode_weights": np.array([1.0, 0.7]),
    }


def test_coherent_modal_ir_has_onset_and_tail() -> None:
    bridge = GeometryAcousticsBridgeV2(
        modal_packet(),
        AcousticBridgeConfig(
            sample_rate=8000,
            duration_seconds=1.0,
            highpass_hz=0.0,
            phase_mode="coherent",
            direct_gain=0.1,
            tail_fade_seconds=0.02,
            seed=9,
        ),
    )
    ir = bridge.synthesize_modal_ir()
    assert ir.shape == (8000, 2)
    assert np.all(np.isfinite(ir))
    assert int(np.argmax(np.max(np.abs(ir), axis=1))) == 0
    early_rms = float(np.sqrt(np.mean(ir[:800] ** 2)))
    late_rms = float(np.sqrt(np.mean(ir[-800:] ** 2)))
    assert late_rms < 0.03 * early_rms
    np.testing.assert_allclose(ir[-1], 0.0, atol=1e-8)


def test_time_constant_reports_true_t60() -> None:
    bridge = GeometryAcousticsBridgeV2(
        modal_packet((3.0, 4.0)),
        AcousticBridgeConfig(duration_seconds=1.0),
    )
    np.testing.assert_allclose(
        bridge.packet.t60_seconds,
        np.log(1000.0) * np.array([3.0, 4.0]),
    )
    descriptors = bridge.acoustic_descriptors()
    assert descriptors["decay_time_definition"] == "amplitude_time_constant"
    assert np.isclose(descriptors["t60_max_seconds"], np.log(1000.0) * 4.0)
    assert descriptors["slowest_tail_level_db_at_end"] > -3.0


def test_energy_aware_tail_trimming() -> None:
    bridge = GeometryAcousticsBridgeV2(
        modal_packet((0.12, 0.18)),
        AcousticBridgeConfig(
            sample_rate=8000,
            duration_seconds=4.0,
            highpass_hz=0.0,
            auto_trim=True,
            trim_threshold_db=-60.0,
            trim_window_seconds=0.02,
            trim_hold_seconds=0.05,
            minimum_duration_seconds=0.25,
        ),
    )
    ir = bridge.synthesize_modal_ir()
    assert 2000 <= len(ir) < 32000
    np.testing.assert_allclose(ir[-1], 0.0, atol=1e-8)
    descriptors = bridge.acoustic_descriptors()
    assert descriptors["trimmed"] is True
    assert descriptors["duration_seconds"] < 4.0
    assert descriptors["maximum_duration_seconds"] == 4.0


def test_export_autonames_instead_of_overwriting() -> None:
    bridge = GeometryAcousticsBridgeV2(
        modal_packet(),
        AcousticBridgeConfig(
            sample_rate=8000,
            duration_seconds=0.02,
            minimum_duration_seconds=1.0,
            preserve_existing_files=True,
        ),
    )
    with tempfile.TemporaryDirectory() as directory:
        prefix = Path(directory) / "ir_test_surface_r000001"
        first = bridge.export(prefix)
        second = bridge.export(prefix)
        assert first["wav"].name == "ir_test_surface_r000001.wav"
        assert second["wav"].name == "ir_test_surface_r000001_v002.wav"
        assert first["wav"].exists()
        assert second["wav"].exists()


def test_material_defaults_center_t60_without_clamping_headroom() -> None:
    config = SurfaceMaterialConfig()
    assert np.isclose(
        t60_from_damping_rate(config.damping_base), DEFAULT_T60_SECONDS
    )
    requested = np.array([0.2, 1.0, 4.0, 10.0, 30.0, 60.0])
    np.testing.assert_allclose(
        t60_from_damping_rate(damping_rate_from_t60(requested)), requested
    )
    policy = OperatorEcologyPolicy()
    assert np.isclose(t60_from_damping_rate(policy.damping_min), 10.0)
    assert np.isclose(t60_from_damping_rate(policy.damping_max), 1.0)


def main() -> None:
    test_coherent_modal_ir_has_onset_and_tail()
    test_time_constant_reports_true_t60()
    test_energy_aware_tail_trimming()
    test_export_autonames_instead_of_overwriting()
    test_material_defaults_center_t60_without_clamping_headroom()
    print("all geometry acoustics bridge envelope v2 tests passed")


if __name__ == "__main__":
    main()
