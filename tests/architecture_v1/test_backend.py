"""Execution adapters exercise existing code and reject unsupported observations."""
from types import SimpleNamespace
from dataclasses import replace

import numpy as np
import pytest
from qiskit import QuantumCircuit

from qmw.architecture_v1.contracts import (
    BackendCapabilities, BasisMetadata, ClockStamp, ExecutionRequest,
    FeatureValue, Provenance,
)
from qmw.architecture_v1.backend import (
    COUNTS, DENSITY, ESTIMATOR_VARIANCES, EXPECTATIONS, INTRINSIC_VARIANCES,
    POPULATIONS, BackendRecordBackend, DensitySnapshotBackend,
    ExistingExecutionProviderBackend, RecordedQuantumBackend,
)
from qmw_density_backend_numpy import NumPyDensityBackend
from qmw_qiskit_bridge_v1.qmw_qiskit_bridge_v1.operators import QMWOperator
from qmw_qiskit_bridge_v1.qmw_qiskit_bridge_v1.providers.statevector import StatevectorProvider


def origin(dimension=4, *, backend='fixture_numpy', evidence='simulator_fixture'):
    return Provenance(
        'source-0', 'quantum.state', 'prepare_fixture', '1', {}, 'dimensionless',
        'trace_one', BasisMetadata('computational', dimension, 'orthonormal'),
        ClockStamp(0.0, 's', 'simulation', 'elapsed', 'fixture_start'), backend, evidence,
    )


def request(operation, *paths, payload=None, name='request-1'):
    return ExecutionRequest(name, operation, frozenset(paths),
        ClockStamp(0.25, 's', 'simulation', 'elapsed', 'fixture_start'), payload or {})


def feature(result, feature_id):
    return next(item for item in result.features if item.id == feature_id)


def test_snapshot_reuses_numpy_array_backend_without_evolving_density():
    rho = np.diag([0.5, 0.0, 0.0, 0.5]).astype(complex)
    class Owner:
        logical_time = 1.5
        state_revision = 8
        def step(self, dt):
            raise AssertionError('snapshot must never evolve state')
    owner = Owner()
    owner.rho = rho
    arrays = NumPyDensityBackend()
    backend = DensitySnapshotBackend(owner, origin(), array_backend=arrays)
    result = backend.execute(request('snapshot', DENSITY.path, POPULATIONS.path))
    assert backend.array_backend is arrays
    np.testing.assert_array_equal(feature(result, DENSITY).value, rho)
    np.testing.assert_array_equal(feature(result, POPULATIONS).value, np.diag(rho).real)
    assert result.provenance.clock.value == 1.5
    assert result.provenance.parameters['state_revision'] == 8
    assert feature(result, POPULATIONS).provenance.parents[0] == feature(result, DENSITY).provenance
    assert result.capabilities.state_access == 'authoritative_simulated'
    rho[0, 0] = 0
    assert feature(result, DENSITY).value[0, 0] == 0.5
    with pytest.raises(ValueError):
        feature(result, DENSITY).value.setflags(write=True)


@pytest.mark.parametrize('rho', [np.eye(4), np.diag([1.1, -0.1, 0, 0]),
    np.array([[0.5, 1], [0, 0.5]]), np.full((4, 4), np.nan)])
def test_snapshot_rejects_invalid_density_instead_of_repairing_it(rho):
    backend = DensitySnapshotBackend(SimpleNamespace(rho=rho), origin())
    with pytest.raises(ValueError):
        backend.execute(request('snapshot', DENSITY.path))


def test_unsupported_snapshot_requirement_rejected_before_reading_owner():
    class Owner:
        @property
        def rho(self):
            raise AssertionError('must reject capability before reading state')
    backend = DensitySnapshotBackend(Owner(), origin())
    with pytest.raises(ValueError, match='required features'):
        backend.execute(request('snapshot', COUNTS.path))


def bell_provider():
    circuit = QuantumCircuit(2)
    circuit.h(0)
    circuit.cx(0, 1)
    # Existing QMWOperator owns Qiskit conversion and observable semantics.
    observable = QMWOperator.from_mapping('ZZ', {'ZZ': 1.0})
    return ExistingExecutionProviderBackend(StatevectorProvider(seed=17), circuit,
        origin(), observables=(observable,))


def test_real_existing_statevector_provider_expectations_and_intrinsic_variance():
    backend = bell_provider()
    result = backend.execute(request('expectations', EXPECTATIONS.path))
    assert feature(result, EXPECTATIONS).value['ZZ'] == pytest.approx(1.0)
    assert feature(result, INTRINSIC_VARIANCES).value['ZZ'] == pytest.approx(0.0, abs=1e-12)
    assert feature(result, EXPECTATIONS).uncertainty is None
    assert ESTIMATOR_VARIANCES.path not in result.capabilities.available_features
    assert result.shots is None
    assert result.metadata['provider_metadata']['provider'] == 'statevector'
    assert result.provenance.parameters['circuit_sha256']


def test_real_existing_statevector_samples_preserve_shots_and_reject_rho():
    backend = bell_provider()
    with pytest.raises(ValueError, match='required features'):
        backend.execute(request('samples', DENSITY.path, payload={'shots': 128}))
    result = backend.execute(request('samples', COUNTS.path, payload={'shots': 128}))
    counts = feature(result, COUNTS).value
    assert set(counts).issubset({'00', '11'})
    assert sum(counts.values()) == result.shots == 128
    assert result.capabilities.state_access == 'none'
    assert len(result.features) == 1


@pytest.mark.parametrize('shots', [True, 0, -1, 1.5, '100'])
def test_invalid_shots_rejected_before_existing_provider(shots):
    backend = bell_provider()
    with pytest.raises(ValueError, match='shots'):
        backend.execute(request('samples', COUNTS.path, payload={'shots': shots}))


def test_request_operation_feature_and_payload_are_checked_before_execution():
    backend = bell_provider()
    with pytest.raises(ValueError, match='required features'):
        backend.execute(request('samples', EXPECTATIONS.path))
    with pytest.raises(ValueError, match='operation'):
        backend.execute(request('remote_submit'))
    with pytest.raises(ValueError, match='payload'):
        backend.execute(request('samples', payload={'unexpected': 1}))


def hardware_record():
    return BackendRecordBackend.from_counts(
        {'00': 25, '11': 75}, origin(backend='offline_ibm_fixture', evidence='offline_fixture'),
        backend_id='offline_ibm_fixture', kind='hardware', shots=100,
        calibration={'calibration_id': 'fixture-cal-1', 'time': None},
        metadata={'job_id': 'fixture-no-job-executed'},
    )


def test_hardware_record_has_no_inferred_rho_and_retains_calibration():
    backend = hardware_record()
    with pytest.raises(ValueError, match='required features'):
        backend.execute(request('record', DENSITY.path))
    result = backend.execute(request('record', COUNTS.path))
    assert result.shots == 100
    assert result.capabilities.kind == 'hardware'
    assert result.capabilities.state_access == 'none'
    assert result.calibration['time'] is None
    assert result.calibration['calibration_id'] == 'fixture-cal-1'
    assert result.provenance.clock.value == 0.0  # ingestion does not invent acquisition time
    assert result.metadata['job_id'] == 'fixture-no-job-executed'
    assert len(result.features) == 1


@pytest.mark.parametrize('counts,shots', [({'00': -1, '11': 2}, 1),
    ({'00': 1.5}, 1), ({'00': True}, 1), ({'bad': 10}, 10),
    ({'00': 10}, 11), ({}, 1), ({'0': 1, '11': 1}, 2)])
def test_counts_admission_rejects_invalid_records(counts, shots):
    with pytest.raises(ValueError):
        BackendRecordBackend.from_counts(counts, origin(), backend_id='fixture', shots=shots)


def test_hardware_density_requires_separate_declared_estimate():
    p = origin()
    density = FeatureValue(DENSITY, np.eye(4) / 4, p)
    capabilities = BackendCapabilities('record', 'hardware', frozenset({'record'}),
        frozenset({DENSITY.path}), 'none')
    with pytest.raises(ValueError, match='state access'):
        BackendRecordBackend(capabilities, (density,), p)
    estimated = BackendCapabilities('record', 'hardware', frozenset({'record'}),
        frozenset({DENSITY.path}), 'estimated')
    with pytest.raises(ValueError, match='estimate'):
        BackendRecordBackend(estimated, (density,), p)
    estimated_p = p.derive('tomography-1', 'declared_tomography', evidence='tomography_estimate')
    backend = BackendRecordBackend(estimated, (FeatureValue(DENSITY, np.eye(4)/4,
        estimated_p, uncertainty={'kind': 'unavailable', 'reason': 'fixture'}),), estimated_p)
    assert backend.execute(request('record', DENSITY.path)).capabilities.state_access == 'estimated'


def test_recorded_replay_preserves_source_time_and_provenance_and_does_not_advance_on_failure():
    original = hardware_record().execute(request('record', COUNTS.path))
    replay = RecordedQuantumBackend((original,))
    with pytest.raises(ValueError, match='required features'):
        replay.execute(request('replay', DENSITY.path))
    result = replay.execute(request('replay', COUNTS.path, name='replay-1'))
    assert result.capabilities.kind == 'recorded'
    assert result.request_id == 'replay-1'
    assert result.shots == original.shots
    assert result.calibration == original.calibration
    assert result.features[0].provenance.parents[0] == original.features[0].provenance
    assert result.features[0].provenance.clock == original.features[0].provenance.clock
    assert result.provenance.parents[0] == original.provenance
    with pytest.raises(StopIteration):
        replay.execute(request('replay', COUNTS.path, name='replay-2'))


def test_recorded_exact_simulator_density_is_recorded_not_estimated():
    source = DensitySnapshotBackend(SimpleNamespace(rho=np.eye(4)/4), origin())
    original = source.execute(request('snapshot', DENSITY.path))
    replay = RecordedQuantumBackend((original,))
    result = replay.execute(request('replay', DENSITY.path))
    assert result.capabilities.state_access == 'recorded'
    assert result.metadata['original_state_access'] == 'authoritative_simulated'
    assert result.provenance.parents[0] == original.provenance
    np.testing.assert_array_equal(feature(result, DENSITY).value, feature(original, DENSITY).value)
    # A second replay retains the original exact-simulator evidence too.
    twice = RecordedQuantumBackend((result,)).execute(request('replay', DENSITY.path))
    assert twice.metadata['original_state_access'] == 'authoritative_simulated'
    with pytest.raises(ValueError, match='original state access'):
        RecordedQuantumBackend((replace(result, metadata={}),))


def test_recorded_access_is_not_valid_on_live_backend_contracts():
    for kind in ('simulator', 'hardware', 'experimental'):
        with pytest.raises(ValueError):
            BackendCapabilities('invalid', kind, frozenset({'snapshot'}),
                frozenset({DENSITY.path}), 'recorded')


def test_missing_feature_in_one_replay_frame_is_rejected_without_consumption():
    original = hardware_record().execute(request('record', COUNTS.path))
    unavailable = replace(original.features[0], value=None, availability='missing', reason='not acquired')
    missing = replace(original, features=(unavailable,))
    replay = RecordedQuantumBackend((missing, original))
    with pytest.raises(ValueError, match='required features'):
        replay.execute(request('replay', COUNTS.path))
    assert replay.index == 0
    first = replay.execute(request('replay'))
    assert first.features[0].availability == 'missing'
    assert replay.index == 1


def test_array_fallback_and_precision_remain_explicit():
    arrays = NumPyDensityBackend()
    arrays.requested_name = 'mlx'
    arrays.fallback_reason = 'test fixture: optional MLX unavailable'
    backend = DensitySnapshotBackend(SimpleNamespace(rho=np.eye(4)/4), origin(), array_backend=arrays)
    assert backend.capabilities.metadata['array_backend'] == 'numpy'
    assert backend.capabilities.metadata['requested_array_backend'] == 'mlx'
    assert backend.capabilities.metadata['fallback_reason']


def test_concurrent_revision_change_during_snapshot_is_rejected():
    class Owner:
        state_revision = 0
        @property
        def rho(self):
            self.state_revision += 1
            return np.eye(4)/4
    with pytest.raises(RuntimeError, match='revision changed'):
        DensitySnapshotBackend(Owner(), origin()).execute(request('snapshot', DENSITY.path))


def test_aer_estimator_variance_adapter_contract_with_explicit_offline_frame():
    # Aer is optional and absent in this environment. This test validates the
    # existing provider's public result contract, not an Aer execution claim.
    from qmw_qiskit_bridge_v1.qmw_qiskit_bridge_v1.models import QuantumMaterialFrame
    from qmw_qiskit_bridge_v1.qmw_qiskit_bridge_v1.providers.aer import AerProvider
    class OfflineAerContractFixture(AerProvider):
        def __init__(self):
            self.shots = 200
            self.seed = 1
            self.noise_model = None
        def run_expectations(self, circuit, observables, *, time=0):
            return QuantumMaterialFrame(time, expectations={'ZZ': .8}, variances={'ZZ': .002},
                backend={'provider': 'offline_Aer_contract_fixture', 'shots': 200})
    circuit = QuantumCircuit(2)
    observable = QMWOperator.from_mapping('ZZ', {'ZZ': 1.0})
    adapter = ExistingExecutionProviderBackend(OfflineAerContractFixture(), circuit,
        origin(), observables=(observable,))
    result = adapter.execute(request('expectations', EXPECTATIONS.path, ESTIMATOR_VARIANCES.path))
    assert feature(result, EXPECTATIONS).uncertainty['kind'] == 'estimator_variance'
    assert feature(result, EXPECTATIONS).uncertainty['values']['ZZ'] == .002
    assert feature(result, ESTIMATOR_VARIANCES).value['ZZ'] == .002
    assert INTRINSIC_VARIANCES.path not in adapter.capabilities.available_features
