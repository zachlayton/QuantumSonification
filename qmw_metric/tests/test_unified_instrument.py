import numpy as np
import pytest

from qmw_metric.config import QuantumMetricConfig
from qmw_metric.unified_instrument import (
    UNIFIED_METRIC_OSC_SCHEMA,
    UnifiedMetricFrame,
    UnifiedMetricObserver,
    UnifiedMetricOSCPublisher,
)


class _Client:
    def __init__(self):
        self.sent = []

    def send_message(self, address, payload):
        self.sent.append((address, payload))


def test_observer_builds_twenty_mode_downstream_frame_without_mutating_rho():
    observer = UnifiedMetricObserver(
        QuantumMetricConfig(grid_size=(16, 16), mode_count=20)
    )
    rho = np.eye(16, dtype=np.complex128) / 16.0
    before = rho.copy()
    frame = observer.observe(rho, time=0.02, source_revision=4, dt=0.02)
    assert np.array_equal(rho, before)
    assert frame.geometry_ratios.shape == (20,)
    assert frame.decay_seconds.shape == (20,)
    assert frame.excitation_profile.shape == (20,)
    assert frame.intermodal_connection.shape == (20, 20)
    assert np.all(frame.geometry_ratios > 0.0)
    assert np.all(frame.decay_seconds > 0.0)
    assert frame.source_revision == 4


def test_unified_frame_rejects_nonunit_profile_and_non_skew_connection():
    common = dict(
        revision=1,
        source_revision=1,
        time=0.0,
        geometry_ratios=np.ones(20),
        decay_seconds=np.ones(20),
        excitation_profile=np.ones(20),
        intermodal_connection=np.zeros((20, 20)),
        trajectory_pan=0.0,
        topography_mode="explicit_force",
    )
    with pytest.raises(ValueError, match="unit L2"):
        UnifiedMetricFrame(**common)
    common["excitation_profile"] = np.zeros(20)
    common["intermodal_connection"] = np.triu(np.ones((20, 20)), 1)
    with pytest.raises(ValueError, match="antisymmetric"):
        UnifiedMetricFrame(**common)


def test_atomic_osc_contract_and_monotonic_publication():
    observer = UnifiedMetricObserver(
        QuantumMetricConfig(grid_size=(16, 16), mode_count=20)
    )
    frame = observer.observe(
        np.eye(16, dtype=np.complex128) / 16.0,
        time=0.02,
        source_revision=2,
        dt=0.02,
    )
    client = _Client()
    publisher = UnifiedMetricOSCPublisher(client)
    assert publisher.publish(frame) == frame.revision
    assert publisher.publish(frame) is None
    addresses = [address for address, _payload in client.sent]
    assert addresses[0].endswith("/frame/begin")
    assert addresses[-1].endswith("/frame/end")
    assert client.sent[0][1][3] == UNIFIED_METRIC_OSC_SCHEMA
    assert len(client.sent[1][1]) == 21
    assert len(client.sent[4][1]) == 401
