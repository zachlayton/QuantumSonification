"""Capability-aware adapters over existing QMW execution and data owners.

No evolution, remote submission, tomography, or sound mapping is implemented
here. Circuits/providers are injected at construction because an execution
request contains only immutable data. Replaying records never acquires new
experimental time or promotes an estimate to an authoritative simulator state.
"""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from contextlib import nullcontext
from dataclasses import replace
import hashlib
import io

import numpy as np

from .contracts import (
    BackendCapabilities, ClockStamp, ExecutionRequest, ExecutionResult, FeatureId,
    FeatureValue, Provenance, finite, freeze, plain,
)


DENSITY = FeatureId('quantum.state.rho', 'density_matrix', 'matrix')
POPULATIONS = FeatureId('quantum.state.populations', 'probabilities', 'vector')
COUNTS = FeatureId('quantum.measurement.counts', 'counts', 'record')
EXPECTATIONS = FeatureId('quantum.observables.expectations', 'expectation_values', 'record')
INTRINSIC_VARIANCES = FeatureId('quantum.observables.intrinsic_variances', 'observable_variances', 'record')
ESTIMATOR_VARIANCES = FeatureId('quantum.observables.estimator_variances', 'estimator_variances', 'record')


def require_request(capabilities, request, *, operation_features=None, allowed_payload=()):
    """Reject requirements before accessing an owner or invoking a provider."""
    if not isinstance(request, ExecutionRequest) or not isinstance(request.timestamp, ClockStamp):
        raise ValueError('typed execution request and timestamp required')
    if request.operation not in capabilities.operations:
        raise ValueError(f'unsupported operation {request.operation!r}')
    available = capabilities.available_features if operation_features is None else operation_features
    missing = request.required_features - frozenset(available)
    if missing:
        raise ValueError(f'unavailable required features: {sorted(missing)}')
    if set(request.payload) - set(allowed_payload):
        raise ValueError('unsupported execution payload fields')


def _positive_shots(value):
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise ValueError('shots must be a positive integer')
    return value


def _density(value, dimension, tolerance=1e-10):
    state = np.asarray(value, dtype=complex)
    if dimension < 1 or state.shape != (dimension, dimension):
        raise ValueError('density shape must match declared basis dimension')
    if not np.all(np.isfinite(state)):
        raise ValueError('density must be finite')
    if not np.allclose(state, state.conj().T, atol=tolerance, rtol=0):
        raise ValueError('density must be Hermitian')
    if not np.isclose(np.trace(state), 1, atol=tolerance, rtol=0):
        raise ValueError('density must have unit trace')
    if np.linalg.eigvalsh(state).min() < -tolerance:
        raise ValueError('density must be positive semidefinite')
    return state


def _counts(value, *, shots=None, dimension=0):
    if not isinstance(value, Mapping) or not value:
        raise ValueError('counts must be a nonempty mapping')
    result = {}
    widths = set()
    for label, count in value.items():
        if not isinstance(label, str) or not label or any(c not in '01' for c in label):
            raise ValueError('counts keys require explicitly ordered binary strings')
        if isinstance(count, bool) or not isinstance(count, (int, np.integer)) or count < 0:
            raise ValueError('counts require nonnegative integers, not probabilities or signed weights')
        result[label] = int(count)
        widths.add(len(label))
    if len(widths) != 1 or (dimension and 2 ** next(iter(widths)) != dimension):
        raise ValueError('counts width must match the declared basis')
    total = sum(result.values())
    _positive_shots(total)
    if shots is not None and _positive_shots(shots) != total:
        raise ValueError('shots disagree with total counts')
    return result, total


def _state_feature(feature):
    return (feature.id.path == DENSITY.path or feature.id.quantity in
            {'density_matrix', 'statevector', 'wavefunction'})


def _validate_state_access(capabilities, features):
    states = [f for f in features if f.availability == 'available' and _state_feature(f)]
    if not states:
        return
    if capabilities.state_access == 'none':
        raise ValueError('state access is unavailable; state features cannot be fabricated')
    for feature in states:
        if capabilities.state_access == 'estimated' and feature.provenance.evidence not in {
                'estimated', 'experimental_estimate', 'tomography_estimate'}:
            raise ValueError('state estimate requires separately declared estimation provenance')
        if feature.id.quantity == 'density_matrix':
            _density(feature.value, feature.provenance.basis.dimension)


class DensitySnapshotBackend:
    """Read an injected canonical owner using its existing array backend.

    The owner supplies ``rho`` and optionally ``logical_time``/``state_revision``.
    A supplied lock must also be used by the owner while publishing state.
    Without it, caller synchronization is required; revision changes observed
    during a snapshot are rejected. No Hamiltonian or state evolution is called.
    """
    def __init__(self, owner, provenance: Provenance, *, array_backend=None,
                 backend_id=None, lock=None):
        if not isinstance(provenance, Provenance):
            raise ValueError('source provenance required')
        if array_backend is None:
            from qmw_density_backend import create_backend
            array_backend = create_backend('numpy')
        self.owner = owner
        self.array_backend = array_backend
        self.source = provenance
        self.lock = lock
        self.capabilities = BackendCapabilities(
            backend_id or f'qmw_density_snapshot:{array_backend.name}', 'simulator',
            frozenset({'snapshot'}), frozenset({DENSITY.path, POPULATIONS.path}),
            'authoritative_simulated', provenance.basis.subsystem_order,
            {'array_backend': array_backend.name,
             'array_dtype': str(array_backend.complex_dtype),
             'requested_array_backend': getattr(array_backend, 'requested_name', array_backend.name),
             'fallback_reason': getattr(array_backend, 'fallback_reason', None),
             'evolution_owner': 'injected_existing_owner', 'snapshot_requires_owner_synchronization': True},
        )

    def execute(self, request: ExecutionRequest) -> ExecutionResult:
        require_request(self.capabilities, request)
        with self.lock if self.lock is not None else nullcontext():
            revision = getattr(self.owner, 'state_revision', None)
            logical_time = getattr(self.owner, 'logical_time', None)
            array = self.array_backend.array(self.owner.rho, dtype=self.array_backend.complex_dtype)
            self.array_backend.synchronize_frame((array,))
            snapshot = np.array(self.array_backend.to_numpy(array), copy=True)
            if getattr(self.owner, 'state_revision', None) != revision:
                raise RuntimeError('owner revision changed during snapshot; use owner synchronization')
        tolerance = 1e-6 if snapshot.dtype == np.complex64 else 1e-10
        state = _density(snapshot, self.source.basis.dimension, tolerance)
        stamp = self.source.clock
        if logical_time is not None:
            stamp = replace(stamp, value=finite(logical_time, 'logical_time'))
        result_id = f'{self.capabilities.backend_id}:{request.request_id}'
        p = self.source.derive(result_id, 'existing_density_owner_snapshot',
            parameters={'state_revision': revision, 'validation_tolerance': tolerance,
                        'array_backend': self.array_backend.name}, clock=stamp,
            backend=self.capabilities.backend_id, evidence='simulated_state_snapshot')
        density_p = p.derive(f'{result_id}:rho', 'copy_authoritative_density',
            source_path=DENSITY.path, units='dimensionless', normalization='trace_one',
            evidence='simulated_state_snapshot')
        density = FeatureValue(DENSITY, state, density_p)
        populations = FeatureValue(POPULATIONS, state.diagonal().real,
            density_p.derive(f'{result_id}:populations', 'real_density_diagonal',
                source_path=POPULATIONS.path, normalization='trace_one_no_renormalization'))
        return ExecutionResult(result_id, request.request_id, self.capabilities,
            (density, populations), p,
            metadata={'request_timestamp': plain(request.timestamp),
                      'state_revision': revision, 'array_backend': self.capabilities.metadata})


class ExistingExecutionProviderBackend:
    """Adapt actual local StatevectorProvider/AerProvider with no remote route.

    Intrinsic quantum variance from StatevectorProvider and estimator variance
    from AerProvider have different feature IDs. Neither existing provider
    returns a density matrix through its public result, so neither advertises it.
    """
    def __init__(self, provider, circuit, provenance: Provenance, *, observables=(), backend_id=None):
        from qiskit import QuantumCircuit, qpy
        from qmw_qiskit_bridge_v1.qmw_qiskit_bridge_v1.providers.statevector import StatevectorProvider
        from qmw_qiskit_bridge_v1.qmw_qiskit_bridge_v1.providers.aer import AerProvider
        if not isinstance(circuit, QuantumCircuit) or not isinstance(provenance, Provenance):
            raise ValueError('existing Qiskit circuit and source provenance required')
        if isinstance(provider, StatevectorProvider):
            self.provider_kind = 'statevector'
            self.variance_id = INTRINSIC_VARIANCES
        elif isinstance(provider, AerProvider):
            self.provider_kind = 'aer'
            self.variance_id = ESTIMATOR_VARIANCES
        else:
            raise ValueError('only existing local StatevectorProvider/AerProvider supported')
        if provenance.basis.subsystem_order != 'q0_lsb':
            raise ValueError('existing Qiskit providers require q0_lsb subsystem order')
        if provenance.basis.dimension != 2 ** circuit.num_qubits:
            raise ValueError('circuit width must match source basis')
        self.provider = provider
        self._circuit = circuit.copy()
        self.observables = tuple(observables)
        if len({op.name for op in self.observables}) != len(self.observables):
            raise ValueError('observable names must be unique')
        for observable in self.observables:
            if observable.n_qubits != circuit.num_qubits:
                raise ValueError('observable width must match circuit')
            matrix = observable.matrix()
            if not np.allclose(matrix, matrix.conj().T, atol=1e-12, rtol=0):
                raise ValueError('expectation observables must be Hermitian')
        buffer = io.BytesIO()
        qpy.dump(self._circuit, buffer)
        self.circuit_sha256 = hashlib.sha256(buffer.getvalue()).hexdigest()
        self.source = provenance
        available = {COUNTS.path}
        operations = {'samples'}
        if self.observables:
            available |= {EXPECTATIONS.path, self.variance_id.path}
            operations.add('expectations')
        self.capabilities = BackendCapabilities(
            backend_id or f'existing_qmw_{self.provider_kind}', 'simulator',
            frozenset(operations), frozenset(available), 'none',
            provenance.basis.subsystem_order,
            {'provider_class': f'{type(provider).__module__}.{type(provider).__name__}',
             'remote_execution': False, 'density_available_from_provider_result': False},
        )

    @property
    def circuit(self):
        """Inspection copy; caller edits cannot alter the fingerprinted circuit."""
        return self._circuit.copy()

    def execute(self, request: ExecutionRequest) -> ExecutionResult:
        paths = ({COUNTS.path} if request.operation == 'samples' else
                 {EXPECTATIONS.path, self.variance_id.path})
        require_request(self.capabilities, request, operation_features=paths,
            allowed_payload=('shots',) if request.operation == 'samples' else ())
        if request.timestamp.value is None or request.timestamp.unit != 's':
            raise ValueError('local provider request requires declared numeric time in seconds')
        time = finite(request.timestamp.value, 'provider time', minimum=0)
        # Capture provider configuration before execution, including an optional
        # existing Aer noise model. No simulator/noise implementation is copied.
        noise = getattr(self.provider, 'noise_model', None)
        noise_description = freeze(noise.to_dict()) if noise is not None else None
        shots = None
        if request.operation == 'samples':
            shots = _positive_shots(request.payload.get('shots', getattr(self.provider, 'shots', 1024)))
            frame = self.provider.run_samples(self._circuit.copy(), shots=shots, time=time)
        else:
            frame = self.provider.run_expectations(self._circuit.copy(), self.observables, time=time)
            if self.provider_kind == 'aer':
                shots = _positive_shots(self.provider.shots)
        result_id = f'{self.capabilities.backend_id}:{request.request_id}'
        p = self.source.derive(result_id, f'existing_provider_{request.operation}',
            parameters={'circuit_sha256': self.circuit_sha256, 'shots': shots,
                'observables': {op.name: tuple((term.label, term.coefficient) for term in op.terms)
                                for op in self.observables},
                'seed': getattr(self.provider, 'seed', None), 'noise_model': noise_description,
                'provider_circuit_policy': 'remove_final_measurements; samples_cover_all_qubits'},
            clock=request.timestamp, backend=self.capabilities.backend_id,
            evidence='local_simulator_execution')
        if request.operation == 'samples':
            counts, _ = _counts(frame.samples, shots=shots, dimension=self.source.basis.dimension)
            features = (FeatureValue(COUNTS, counts,
                p.derive(f'{result_id}:counts', 'retain_existing_provider_counts',
                    source_path=COUNTS.path, units='shots', normalization='integer_counts')) ,)
        else:
            names = {op.name for op in self.observables}
            if set(frame.expectations) != names or set(frame.variances) != names:
                raise ValueError('provider result lacks requested observable values or variances')
            values = {name: finite(v, f'expectation {name}') for name, v in frame.expectations.items()}
            variances = {name: finite(v, f'variance {name}') for name, v in frame.variances.items()}
            if min(variances.values(), default=0) < -1e-10:
                raise ValueError('provider returned a negative variance')
            # Retain tiny roundoff; do not turn intrinsic variance into an error bar.
            uncertainty = ({'kind': 'estimator_variance', 'values': variances,
                            'source': 'existing_AerProvider_datum_stds_squared'}
                           if self.provider_kind == 'aer' else None)
            features = (
                FeatureValue(EXPECTATIONS, values,
                    p.derive(f'{result_id}:expectations', 'retain_existing_provider_expectations',
                        source_path=EXPECTATIONS.path, normalization='raw_observable_expectation'),
                    uncertainty=uncertainty),
                FeatureValue(self.variance_id, variances,
                    p.derive(f'{result_id}:variances', f'retain_{self.variance_id.quantity}',
                        source_path=self.variance_id.path, units=f'({self.source.units})^2',
                        normalization='raw_variance')),
            )
        return ExecutionResult(result_id, request.request_id, self.capabilities,
            features, p, shots=shots, metadata={'provider_metadata': dict(frame.backend),
                'variance_semantics': self.variance_id.quantity,
                'shot_count_semantics': 'provider_declared' if shots is not None else 'not_applicable'})


class BackendRecordBackend:
    """Admit completed hardware/experimental records; never submit a job.

    Counts, observables and separately reconstructed state estimates are kept as
    distinct typed features. Missing estimates and calibration times remain
    missing. A supplied density estimate requires explicit estimation evidence.
    """
    def __init__(self, capabilities: BackendCapabilities, features: Sequence[FeatureValue],
                 provenance: Provenance, *, shots=None, calibration=None, metadata=None):
        if capabilities.kind not in {'hardware', 'experimental'}:
            raise ValueError('record ingestion requires hardware or experimental capabilities')
        if capabilities.operations != frozenset({'record'}):
            raise ValueError('completed record backend supports only record operation')
        self.capabilities = capabilities
        self.features = tuple(features)
        self.source = provenance
        self.shots = None if shots is None else _positive_shots(shots)
        self.calibration = None if calibration is None else freeze(calibration)
        self.metadata = freeze(metadata or {})
        _validate_state_access(capabilities, self.features)
        for feature in self.features:
            if feature.id == COUNTS and feature.availability == 'available':
                _, count_shots = _counts(feature.value, shots=self.shots,
                    dimension=feature.provenance.basis.dimension)
                self.shots = count_shots
        # Existing shared contract supplies duplicate-path/declaration validation.
        ExecutionResult('admission', 'admission', capabilities, self.features,
            provenance, shots=self.shots, calibration=self.calibration, metadata=self.metadata)

    @classmethod
    def from_counts(cls, counts, provenance: Provenance, *, backend_id,
                    kind='hardware', shots=None, calibration=None, metadata=None):
        counts, total = _counts(counts, shots=shots, dimension=provenance.basis.dimension)
        capabilities = BackendCapabilities(backend_id, kind, frozenset({'record'}),
            frozenset({COUNTS.path}), 'none', provenance.basis.subsystem_order,
            {'remote_execution': False, 'source': 'supplied_completed_record'})
        p = provenance.derive(f'{provenance.record_id}:counts', 'admit_completed_counts',
            parameters={'total_recorded_shots': total}, source_path=COUNTS.path,
            units='shots', normalization='integer_counts', backend=backend_id,
            evidence=provenance.evidence)
        return cls(capabilities, (FeatureValue(COUNTS, counts, p),), provenance,
            shots=total, calibration=calibration, metadata=metadata)

    def execute(self, request: ExecutionRequest) -> ExecutionResult:
        available = {f.id.path for f in self.features if f.availability == 'available'}
        require_request(self.capabilities, request, operation_features=available)
        result_id = f'{self.capabilities.backend_id}:{request.request_id}'
        p = self.source.derive(result_id, 'admit_backend_record',
            parameters={'request_timestamp': plain(request.timestamp)},
            backend=self.capabilities.backend_id, evidence=self.source.evidence)
        features = tuple(replace(f, provenance=f.provenance.derive(
            f'{result_id}:{f.id.path}', 'retain_completed_feature',
            parents=(f.provenance, p), evidence=f.provenance.evidence)) for f in self.features)
        return ExecutionResult(result_id, request.request_id, self.capabilities,
            features, p, shots=self.shots, calibration=self.calibration, metadata=self.metadata)


class RecordedQuantumBackend:
    """Deterministic replay of immutable quantum results with original evidence.

    This accepts validated results, not pickle files or visual-state fixtures.
    Replayed state access is ``recorded`` and always carries the original state
    access and backend. No new evolution, measurements or acquisition times are
    inferred. A rejected request does not consume the next record.
    """
    def __init__(self, records: Sequence[ExecutionResult], *, backend_id='qmw_recorded_quantum'):
        self.records = tuple(records)
        if not self.records or not all(isinstance(r, ExecutionResult) for r in self.records):
            raise ValueError('nonempty sequence of validated ExecutionResult records required')
        orders = {r.capabilities.subsystem_order for r in self.records}
        if len(orders) != 1:
            raise ValueError('replay records require one explicit subsystem ordering')
        for record in self.records:
            _validate_state_access(record.capabilities, record.features)
            if record.capabilities.state_access == 'recorded' and 'original_state_access' not in record.metadata:
                raise ValueError('recorded state requires original state access metadata')
        self.index = 0
        has_state = any(_state_feature(f) and f.availability == 'available'
                        for record in self.records for f in record.features)
        self.capabilities = BackendCapabilities(backend_id, 'recorded', frozenset({'replay'}),
            frozenset(f.id.path for r in self.records for f in r.features),
            'recorded' if has_state else 'none', next(iter(orders)),
            {'original_state_access': tuple(r.capabilities.state_access for r in self.records),
             'original_backends': tuple(r.capabilities.backend_id for r in self.records),
             'acquisition': 'none_replay_only'})

    def execute(self, request: ExecutionRequest) -> ExecutionResult:
        require_request(self.capabilities, request)
        if self.index >= len(self.records):
            raise StopIteration('recorded quantum results exhausted')
        original = self.records[self.index]
        available = {f.id.path for f in original.features if f.availability == 'available'}
        require_request(self.capabilities, request, operation_features=available)
        result_id = f'{self.capabilities.backend_id}:{request.request_id}:{self.index}'
        p = original.provenance.derive(result_id, 'replay_recorded_quantum_result',
            parameters={'original_result_id': original.result_id, 'record_index': self.index,
                        'replay_request_timestamp': plain(request.timestamp)},
            backend=self.capabilities.backend_id, evidence='recorded_replay')
        features = tuple(replace(f, provenance=f.provenance.derive(
            f'{result_id}:{f.id.path}', 'replay_recorded_feature',
            parents=(f.provenance, p), evidence='recorded_replay')) for f in original.features)
        original_access = original.metadata.get('original_state_access', original.capabilities.state_access)
        metadata = {'original_result_id': original.result_id,
            'original_state_access': original_access,
            'original_backend_id': original.capabilities.backend_id,
            'original_metadata': original.metadata}
        result = ExecutionResult(result_id, request.request_id, self.capabilities, features, p,
            shots=original.shots, calibration=original.calibration, metadata=metadata)
        self.index += 1
        return result


__all__ = ['DENSITY', 'POPULATIONS', 'COUNTS', 'EXPECTATIONS', 'INTRINSIC_VARIANCES',
    'ESTIMATOR_VARIANCES', 'DensitySnapshotBackend', 'ExistingExecutionProviderBackend',
    'BackendRecordBackend', 'RecordedQuantumBackend', 'require_request']
