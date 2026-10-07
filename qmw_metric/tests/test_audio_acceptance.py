import numpy as np

from qmw_metric.audio_acceptance import _analyse, _comparison_metrics


def test_comparison_metrics_distinguish_spectral_relationship():
    sample_rate = 8_000
    time = np.arange(sample_rate, dtype=float) / sample_rate
    a = np.sin(2.0 * np.pi * 220.0 * time)
    b = np.sin(2.0 * np.pi * 440.0 * time)
    distinct = _comparison_metrics(a, b, sample_rate)
    identical = _comparison_metrics(a, a.copy(), sample_rate)
    assert distinct["objectively_distinct"]
    assert distinct["spectral_distance_db_rms"] > 2.0
    assert not identical["objectively_distinct"]
    assert identical["level_matched_waveform_distance"] == 0.0


def test_click_evidence_checks_mode_boundaries_not_only_global_peak():
    signal = np.sin(np.linspace(0.0, 20.0, 2_000)) * .1
    evidence = _analyse(
        signal,
        sample_rate=2_000,
        mode_boundaries=[400, 800, 1_200],
        trajectory=np.array(((0.0, 0.0), (1.0, 0.0))),
    )
    assert evidence.mode_updates == 3
    assert evidence.mode_tracking_click_free
    assert evidence.trajectory_distance == 1.0
