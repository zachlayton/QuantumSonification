"""Reversible complex fields and explicitly routed stationary audio projection."""
from dataclasses import replace

import numpy as np
import pytest

from qmw.architecture_v1.audio_projection import AudioProjection256
from qmw.architecture_v1.contracts import (
    BasisMetadata, ClockStamp, FeatureFrame, FeatureId, FeatureValue, MappingSpec,
    Provenance, RouteSpec, RoutingPreset,
)
from qmw.architecture_v1.router import SonificationRouter
from qmw.fields.quantum_matrix_field import QuantumMatrixField
from qmw.manifolds.quantum_matrix_manifold import QuantumMatrixManifold
from qmw.transforms.manifold_spectral_transform import ManifoldSpectralTransform, qft_matrix


def matrix_feature(matrix, *, units="matrix_unit"):
    p = Provenance("matrix:1", "manifold.matrix", "declared_complex_slice", "1", {"eta": 0.37},
                   units, "none", BasisMetadata("manifold:eta:.37", 16, "basis_path"),
                   ClockStamp(0.1, "s", "simulation", "elapsed", "matrix-run"), "numpy", "fixture")
    return FeatureValue(FeatureId("manifold.matrix", "complex_matrix", "matrix"), matrix, p)


def route(table):
    spec = MappingSpec("explicit-table", "1", "identity", (table.id,), "1", "none")
    router = SonificationRouter(RoutingPreset("table", (RouteSpec("audio.wavetable", table.id, spec),)))
    return router.route(FeatureFrame("audio:route", (table,))).values["audio.wavetable"]


def prepared(table):
    projector = AudioProjection256()
    view = projector.project(matrix_feature(np.asarray(table).reshape(16, 16)),
                             mode="real_bipolar").get("audio_projection.raw")
    normalized = projector.normalize(view).get("audio_projection.table")
    return projector, route(normalized)


def test_reversible_complex_flattening_preserves_every_cell_and_primary_source():
    rng = np.random.default_rng(41)
    source = matrix_feature(rng.normal(size=(16, 16))+1j*rng.normal(size=(16, 16)))
    before = source.value.copy()
    projector = AudioProjection256()
    frame = projector.project(source)
    assert frame.get(source.id) is source
    flat = frame.get("audio_projection.buffer256")
    assert flat.value.dtype.kind == "c" and flat.value.shape == (256,)
    for m in range(16):
        for n in range(16):
            assert flat.value[16*m+n] == source.value[m, n]
    recovered = projector.unflatten(flat)
    np.testing.assert_array_equal(recovered.value, source.value)
    np.testing.assert_array_equal(recovered.value, QuantumMatrixField.unflatten(flat.value))
    np.testing.assert_array_equal(before, source.value)
    assert recovered.provenance.parents == (flat.provenance,)
    assert flat.provenance.parameters["flattening"] == "k=16*m+n; C row-major"
    with pytest.raises(ValueError):
        flat.value.setflags(write=True)


@pytest.mark.parametrize("mode", ["magnitude", "real_bipolar", "phase_cos"])
def test_real_view_modes_are_declared_and_phase_zero_has_no_fabricated_signal(mode):
    matrix = np.zeros((16, 16), complex)
    matrix[0, :4] = [1, 1j, -1, -1j]
    source = matrix_feature(matrix)
    frame = AudioProjection256().project(source, mode=mode)
    view = frame.get("audio_projection.raw")
    expected = {"magnitude": [1, 1, 1, 1], "real_bipolar": [1, 0, -1, 0],
                "phase_cos": [1, 0, -1, 0]}[mode]
    np.testing.assert_allclose(view.value[:4], expected, atol=1e-15)
    assert np.count_nonzero(view.value[4:]) == 0
    assert view.provenance.parameters["mode"] == mode
    if mode == "phase_cos":
        assert view.units == "1"
        mask = frame.get("audio_projection.phase_valid")
        np.testing.assert_array_equal(mask.value[:5], [True, True, True, True, False])
    else:
        assert view.units == source.units


@pytest.mark.parametrize("mode", ["row_bank", "column_bank"])
@pytest.mark.parametrize("encoding", ["magnitude", "real_bipolar", "phase_cos"])
def test_row_column_banks_keep_explicit_axis_and_encoding(mode, encoding):
    matrix = np.arange(256).reshape(16, 16)*np.exp(0.2j)
    frame = AudioProjection256().project(matrix_feature(matrix), mode=mode, encoding=encoding)
    view = frame.get("audio_projection.raw")
    expected = np.abs(matrix) if encoding == "magnitude" else matrix.real if encoding == "real_bipolar" else np.where(np.abs(matrix)>0, np.cos(np.angle(matrix)), 0)
    if mode == "column_bank":
        expected = expected.T
    assert view.value.shape == (16, 16)
    np.testing.assert_allclose(view.value, expected)
    assert view.provenance.parameters["bank_axis"] == ("row_m" if mode == "row_bank" else "column_n")
    np.testing.assert_array_equal(frame.get("audio_projection.buffer256").value, matrix.reshape(256))


def test_fft2_reuses_existing_transform_and_is_not_implicitly_a_wavetable():
    rng = np.random.default_rng(19)
    matrix = rng.normal(size=(16, 16))+1j*rng.normal(size=(16, 16))
    projector = AudioProjection256()
    spectrum = projector.project(matrix_feature(matrix), mode="fft2").get("audio_projection.raw")
    np.testing.assert_allclose(spectrum.value, ManifoldSpectralTransform.fft2(matrix))
    assert spectrum.value.dtype.kind == "c"
    with pytest.raises(ValueError, match="real audio view"):
        projector.normalize(spectrum)
    view = projector.project(matrix_feature(matrix), mode="fft2", encoding="magnitude").get("audio_projection.raw")
    np.testing.assert_allclose(view.value, np.abs(spectrum.value).reshape(256))
    assert view.provenance.parents[0].operation == "ManifoldSpectralTransform.fft2"


def test_explicit_normalization_dc_and_gain_are_separate_from_raw_views():
    projector = AudioProjection256()
    raw = np.linspace(2, 6, 256).reshape(16, 16)
    source = matrix_feature(raw)
    view = projector.project(source, mode="real_bipolar").get("audio_projection.raw")
    frame = projector.normalize(view, remove_dc=True)
    table = frame.get("audio_projection.table")
    assert frame.get(view.id) is view
    assert table.units == "1" and np.max(np.abs(table.value)) == pytest.approx(1)
    assert np.mean(table.value) == pytest.approx(0, abs=1e-14)
    assert table.provenance.parameters["dc_removed"] == pytest.approx(4)
    assert table.provenance.parameters["normalization_denominator"] == pytest.approx(2)
    assert table.provenance.parameters["audio_gain_applied"] is False
    np.testing.assert_array_equal(view.value, raw.reshape(256))


def test_global_bank_peak_preserves_relative_table_amplitudes_and_per_table_is_opt_in():
    raw = np.zeros((16, 16)); raw[0, 1] = 2; raw[1, 1] = 4
    projector = AudioProjection256()
    view = projector.project(matrix_feature(raw), mode="row_bank", encoding="real_bipolar").get("audio_projection.raw")
    global_table = projector.normalize(view).get("audio_projection.table")
    separate = projector.normalize(view, peak_scope="per_table").get("audio_projection.table")
    assert global_table.value[0, 1] == 0.5 and global_table.value[1, 1] == 1
    assert separate.value[0, 1] == separate.value[1, 1] == 1
    assert not np.any(separate.value[2:])


def test_zero_is_exact_silence_and_small_nonzero_fields_are_not_thresholded_away():
    projector, table = prepared(np.zeros(256))
    audio = projector.play(table, fundamental_hz=100, sample_rate=48000, sample_count=64)
    assert np.count_nonzero(audio.get("audio_projection.samples").value) == 0
    assert table.value.max() == 0
    tiny = np.zeros(256); tiny[1] = 1e-200
    _, table = prepared(tiny)
    assert table.value[1] == 1


def test_periodic_fourier_interpolation_wraps_positive_and_negative_cycles():
    k = np.arange(256)
    projector, table = prepared(np.cos(2*np.pi*k/256))
    phases = np.array([0.125, 1.125, -0.875, 10.125])
    frame = projector.sample_periodic(table, phases, fundamental_hz=100, sample_rate=48000)
    np.testing.assert_allclose(frame.get("audio_projection.samples").value, np.sqrt(0.5), atol=1e-13)


def test_stationary_bandlimit_keeps_only_harmonics_strictly_below_audio_nyquist():
    phase = np.arange(256)/256
    raw = np.cos(2*np.pi*phase)+0.5*np.cos(2*np.pi*3*phase)+0.25*np.cos(2*np.pi*4*phase)
    projector, table = prepared(raw)
    frame = projector.play(table, fundamental_hz=1000, sample_rate=8000, sample_count=128)
    t = np.arange(128)/8000
    expected = (np.cos(2*np.pi*1000*t)+0.5*np.cos(2*np.pi*3000*t))/1.75
    np.testing.assert_allclose(frame.get("audio_projection.samples").value, expected, atol=1e-12)
    harmonics = frame.get("audio_projection.harmonics").value
    assert 3 in harmonics and -3 in harmonics and 4 not in harmonics and -4 not in harmonics
    fft = np.fft.rfft(frame.get("audio_projection.samples").value)
    assert abs(fft[64]) < 1e-10


def test_table_nyquist_bin_is_explicitly_excluded_even_at_low_fundamental():
    projector, table = prepared((-1.)**np.arange(256))
    frame = projector.play(table, fundamental_hz=1, sample_rate=48000, sample_count=32)
    assert not np.any(frame.get("audio_projection.samples").value)
    assert 128 not in abs(frame.get("audio_projection.harmonics").value)
    assert frame.metadata["table_nyquist_policy"] == "excluded"
    assert frame.metadata["excluded_table_nyquist_coefficient"] == pytest.approx(1)


def test_bank_playback_keeps_16_independent_tables_and_seven_harmonic_limit():
    x = np.arange(16)/16
    raw = np.zeros((16, 16)); raw[0] = np.sin(2*np.pi*x); raw[1] = np.cos(2*np.pi*x)
    projector = AudioProjection256()
    view = projector.project(matrix_feature(raw), mode="row_bank", encoding="real_bipolar").get("audio_projection.raw")
    table = route(projector.normalize(view).get("audio_projection.table"))
    frame = projector.play(table, fundamental_hz=100, sample_rate=48000, sample_count=128)
    samples = frame.get("audio_projection.samples").value
    assert samples.shape == (16, 128)
    t = np.arange(128)/48000
    np.testing.assert_allclose(samples[0], np.sin(2*np.pi*100*t), atol=1e-13)
    np.testing.assert_allclose(samples[1], np.cos(2*np.pi*100*t), atol=1e-13)
    assert np.max(abs(frame.get("audio_projection.harmonics").value)) == 7
    assert not np.any(samples[2:])


def test_playback_requires_router_admission_and_complete_projection_chain():
    projector = AudioProjection256()
    f = projector.project(matrix_feature(np.ones((16, 16))), mode="magnitude").get("audio_projection.raw")
    table = projector.normalize(f).get("audio_projection.table")
    with pytest.raises(ValueError, match="SonificationRouter"):
        projector.play(table, fundamental_hz=100, sample_rate=48000, sample_count=2)
    routed = route(table)
    out = projector.play(routed, fundamental_hz=100, sample_rate=48000, sample_count=2)
    samples = out.get("audio_projection.samples")
    assert samples.provenance.clock.domain == "audio"
    assert samples.provenance.parameters["fundamental_hz"] == 100
    coefficient_p = samples.provenance.parents[0]
    assert coefficient_p.parents[0] is routed.provenance
    assert routed.provenance.parents[0] is table.provenance
    assert out.metadata["antialias_scope"] == "stationary waveform and constant frequency; no abrupt modulation guarantee"


def test_actual_manifold_slice_retains_effective_basis_and_reversible_source():
    rho = np.ones((16, 16), complex)/16
    manifold = QuantumMatrixManifold(rho, np.eye(16), qft_matrix(16))
    f = matrix_feature(manifold.matrix_at(0.37), units="1")
    before = f.value.copy()
    projector = AudioProjection256()
    frame = projector.project(f, mode="real_bipolar")
    restored = projector.unflatten(frame.get("audio_projection.buffer256"))
    np.testing.assert_array_equal(restored.value, before)
    assert frame.get("audio_projection.raw").provenance.basis.basis_id == "manifold:eta:.37"
    np.testing.assert_array_equal(f.value, before)


def test_actual_four_qubit_demo_manifold_reaches_router_and_fourier_audio():
    from qmw.architecture_v1.integration import build_four_qubit_demo

    demo = build_four_qubit_demo()
    source = demo["manifold"]
    before = source.value.copy()
    projector = AudioProjection256()
    view = projector.project(source, mode="real_bipolar")
    table = projector.normalize(view.get("audio_projection.raw"), remove_dc=True).get("audio_projection.table")
    audio = projector.play(route(table), fundamental_hz=110, sample_rate=24000, sample_count=512)
    samples = audio.get("audio_projection.samples").value
    assert samples.shape == (512,) and np.all(np.isfinite(samples))
    assert np.max(np.abs(samples)) > 0
    np.testing.assert_array_equal(projector.unflatten(view.get("audio_projection.buffer256")).value, before)
    np.testing.assert_array_equal(source.value, before)
    assert source.provenance.basis.basis_id == "manifold:eta:.37"
    assert demo["report"]["authority_unchanged"]


def test_signed_frequency_reverses_phase_traversal_without_changing_magnitude_filter():
    x = np.arange(256)/256
    projector, table = prepared(np.sin(2*np.pi*x))
    positive = projector.play(table, fundamental_hz=100, sample_rate=48000, sample_count=64)
    negative = projector.play(table, fundamental_hz=-100, sample_rate=48000, sample_count=64)
    np.testing.assert_allclose(positive.get("audio_projection.samples").value,
                               -negative.get("audio_projection.samples").value, atol=1e-13)
    np.testing.assert_array_equal(positive.get("audio_projection.harmonics").value,
                                  negative.get("audio_projection.harmonics").value)


def test_phase_threshold_and_input_uncertainty_are_auditable():
    matrix = np.zeros((16, 16), complex); matrix[0, :2] = [1e-6, 1]
    source = replace(matrix_feature(matrix), uncertainty={"kind": "covariance_reference", "uri": "cov:matrix"})
    frame = AudioProjection256(phase_epsilon=1e-4).project(source, mode="phase_cos")
    np.testing.assert_array_equal(frame.get("audio_projection.phase_valid").value[:2], [False, True])
    np.testing.assert_array_equal(frame.get("audio_projection.raw").value[:2], [0, 1])
    p = frame.get("audio_projection.raw").provenance
    assert p.parameters["phase_epsilon"] == 1e-4
    assert p.parents[0].parameters["source_uncertainty"]["uri"] == "cov:matrix"


@pytest.mark.parametrize("bad", [np.zeros((15, 15)), np.zeros((16, 15)), np.zeros(256)])
def test_only_explicit_16_by_16_matrix_sources_are_accepted(bad):
    with pytest.raises(ValueError, match="16x16"):
        AudioProjection256().project(matrix_feature(bad))


def test_missing_source_and_incompatible_buffer_are_rejected():
    f = matrix_feature(np.zeros((16, 16)))
    with pytest.raises(ValueError, match="not measured"):
        AudioProjection256().project(replace(f, value=None, availability="missing", reason="not measured"))
    with pytest.raises(ValueError, match="buffer"):
        AudioProjection256().unflatten(f)


@pytest.mark.parametrize("kwargs", [{"mode": "automatic"}, {"mode": "row_bank"},
    {"mode": "magnitude", "encoding": "phase_cos"}, {"mode": "fft2", "encoding": "automatic"}])
def test_encoding_choices_must_be_explicit_and_consistent(kwargs):
    with pytest.raises(ValueError):
        AudioProjection256().project(matrix_feature(np.zeros((16, 16))), **kwargs)


@pytest.mark.parametrize("kwargs", [{"fundamental_hz": 0}, {"fundamental_hz": 24000},
    {"sample_rate": 0}, {"sample_count": 0}, {"sample_count": True}, {"initial_phase": float("nan")}])
def test_invalid_playback_parameters_reject(kwargs):
    projector, table = prepared(np.zeros(256))
    config = dict(fundamental_hz=100, sample_rate=48000, sample_count=16, initial_phase=0)
    config.update(kwargs)
    with pytest.raises(ValueError):
        projector.play(table, **config)
