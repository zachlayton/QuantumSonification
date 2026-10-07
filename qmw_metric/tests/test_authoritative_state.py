import numpy as np
import pytest

from qmw_metric.authoritative_state import (
    DensityMatrixEngineMetricAdapter,
    RevisionedDensityPairReceiver,
)
from density.density_state_injection import bit_reversal_permutation


class _Bridge:
    client = object()


class _Event:
    pass


class _Owner:
    def __init__(self):
        populations = np.arange(1, 17, dtype=float)
        self.rho = np.diag(populations / populations.sum()).astype(np.complex128)
        self.logical_time = 0.0
        self.state_revision = 0
        self.last_event_type = "reset"
        self.qmw_bridge = _Bridge()

    def hamiltonian(self):
        return np.diag(np.arange(16, dtype=float)).astype(np.complex128)

    def step(self, dt):
        self.logical_time += dt
        self.state_revision += 1
        self.last_event_type = "continuous_evolution"

    def perform_measurement(self, basis, mode, request_id):
        assert basis == "X" and mode == "collapse" and request_id == 1
        self.state_revision += 1
        self.last_event_type = "explicit_measurement"
        return _Event()


def test_adapter_observes_owner_without_transferring_authority():
    owner = _Owner()
    adapter = DensityMatrixEngineMetricAdapter(owner, silence_telemetry=True)
    before = owner.rho.copy()
    snapshot = adapter.snapshot()
    assert snapshot.source.endswith("DensityMatrixEngine")
    assert snapshot.basis_order == (
        "q0-LSB; rho and H bit-reversed from density-engine q0-MSB"
    )
    assert np.array_equal(owner.rho, before)
    permutation = bit_reversal_permutation(4)
    assert np.array_equal(snapshot.rho, before[np.ix_(permutation, permutation)])
    native_h = owner.hamiltonian()
    assert np.array_equal(
        snapshot.hamiltonian, native_h[np.ix_(permutation, permutation)]
    )
    assert snapshot.rho.flags.writeable is False
    with pytest.raises(ValueError):
        snapshot.rho[0, 0] = 0.0
    advanced = adapter.advance(.01)
    assert advanced.revision == 1
    assert advanced.time == pytest.approx(.01)
    assert owner.rho is not advanced.rho
    assert owner.qmw_bridge.client.send_message("ignored", 1) is None


def test_adapter_rejects_invalid_step_and_delegates_measurement():
    adapter = DensityMatrixEngineMetricAdapter(_Owner())
    with pytest.raises(ValueError, match="dt"):
        adapter.advance(0.0)
    snapshot, event = adapter.measure()
    assert isinstance(event, _Event)
    assert snapshot.event_type == "explicit_measurement"


def test_revisioned_osc_pair_commits_only_complete_new_physical_state():
    committed = []
    receiver = RevisionedDensityPairReceiver(on_commit=committed.append)
    rho = np.zeros((16, 16), dtype=np.complex128)
    rho[1, 1] = 0.7
    rho[8, 8] = 0.3
    real = (7, *rho.real.reshape(-1))
    imag = (7, *rho.imag.reshape(-1))
    receiver.receive_imag("/qmw/state/rho/imag", *imag)
    assert receiver.snapshot is None
    receiver.receive_real("/qmw/state/rho/real", *real)
    assert receiver.snapshot is committed[0]
    assert receiver.snapshot.revision == 7
    assert np.array_equal(receiver.snapshot.rho, rho)
    assert receiver.snapshot.basis_order.startswith("q0-LSB")
    receiver.receive_real("/qmw/state/rho/real", *real)
    receiver.receive_imag("/qmw/state/rho/imag", *imag)
    assert len(committed) == 1


def test_revisioned_osc_pair_rejects_malformed_or_unphysical_packets():
    receiver = RevisionedDensityPairReceiver()
    with pytest.raises(ValueError, match="256"):
        receiver.receive_real("/qmw/state/rho/real", 1, 0.0)
    bad = np.eye(16, dtype=np.complex128)
    receiver.receive_real("/qmw/state/rho/real", 2, *bad.real.reshape(-1))
    with pytest.raises(ValueError, match="unit trace"):
        receiver.receive_imag("/qmw/state/rho/imag", 2, *bad.imag.reshape(-1))
