"""Supervisor-owned immutable contracts. Existing engine models remain intact."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
import hashlib
import json
import math
from types import MappingProxyType
from typing import Any, Mapping, Protocol

import numpy as np


def nonempty(value: str, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f'{name} must be a nonempty string')
    return value


def finite(value: float, name: str, *, minimum=None) -> float:
    if isinstance(value, (bool, np.bool_)):
        raise ValueError(f'{name} must be numeric')
    number = float(value)
    if not math.isfinite(number) or (minimum is not None and number < minimum):
        raise ValueError(f'{name} must be finite and >= {minimum}')
    return number


def frozen_array(value, dtype=None) -> np.ndarray:
    a = np.array(value, dtype=dtype, copy=True, order='C')
    if a.dtype.kind not in 'biufc' or not np.all(np.isfinite(a)):
        raise ValueError('arrays must be finite numeric/bool values')
    # Immutable bytes ownership prevents callers from re-enabling WRITEABLE.
    return np.frombuffer(a.tobytes(), dtype=a.dtype).reshape(a.shape)


def freeze(value):
    if isinstance(value, np.ndarray):
        return frozen_array(value)
    if isinstance(value, Mapping):
        if any(not isinstance(k, str) for k in value):
            raise ValueError('metadata keys must be strings')
        return MappingProxyType({k: freeze(v) for k, v in value.items()})
    if isinstance(value, (list, tuple)):
        return tuple(freeze(v) for v in value)
    if isinstance(value, (set, frozenset)):
        return frozenset(freeze(v) for v in value)
    if isinstance(value, np.generic):
        return freeze(value.item())
    if isinstance(value, (float, complex)) and not np.isfinite(value):
        raise ValueError('nonfinite metadata/value')
    if value is None or isinstance(value, (str, bool, int, float, complex)):
        return value
    raise ValueError(f'unsupported mutable/opaque metadata: {type(value).__name__}')


def plain(value):
    if hasattr(value, 'to_dict'):
        return value.to_dict()
    if isinstance(value, np.ndarray):
        return {'dtype':str(value.dtype),'shape':list(value.shape),'values':plain(value.tolist())}
    if isinstance(value, Mapping):
        return {k:plain(v) for k,v in value.items()}
    if isinstance(value, (list,tuple,set,frozenset)):
        return [plain(v) for v in value]
    if isinstance(value, complex):
        return {'real':value.real,'imag':value.imag}
    if isinstance(value, np.generic):
        return plain(value.item())
    return value


@dataclass(frozen=True)
class ClockStamp:
    value: float | None
    unit: str
    domain: str
    semantics: str
    origin: str

    def __post_init__(self):
        for name in ('unit','domain','semantics','origin'):
            nonempty(getattr(self,name),name)
        if self.value is not None:
            object.__setattr__(self,'value',finite(self.value,'clock value'))
        elif self.semantics != 'unavailable':
            raise ValueError('missing clock requires unavailable semantics')

    def to_dict(self):
        return dict(value=self.value,unit=self.unit,domain=self.domain,semantics=self.semantics,origin=self.origin)


@dataclass(frozen=True)
class BasisMetadata:
    basis_id: str
    dimension: int
    kind: str
    subsystem_order: str = 'q0_lsb'
    ordering: str = 'coordinate_index'
    gauge: str = 'declared_coordinates'
    details: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        for name in ('basis_id','kind','subsystem_order','ordering','gauge'):
            nonempty(getattr(self,name),name)
        if isinstance(self.dimension,bool) or not isinstance(self.dimension,int) or self.dimension < 0:
            raise ValueError('basis dimension must be a nonnegative integer; 0 means not applicable')
        object.__setattr__(self,'details',freeze(self.details))

    def to_dict(self):
        return {k:plain(getattr(self,k)) for k in self.__dataclass_fields__}


@dataclass(frozen=True)
class Provenance:
    record_id: str
    source_path: str
    operation: str
    version: str
    parameters: Mapping[str, Any]
    units: str
    normalization: str
    basis: BasisMetadata
    clock: ClockStamp
    backend: str
    evidence: str
    parents: tuple['Provenance', ...] = ()

    def __post_init__(self):
        for name in ('record_id','source_path','operation','version','units','normalization','backend','evidence'):
            nonempty(getattr(self,name),name)
        if not isinstance(self.basis,BasisMetadata) or not isinstance(self.clock,ClockStamp):
            raise ValueError('basis and clock must use shared metadata contracts')
        ps=tuple(self.parents)
        if not all(isinstance(p,Provenance) for p in ps):
            raise ValueError('all provenance parents must be Provenance nodes')
        object.__setattr__(self,'parents',ps)
        object.__setattr__(self,'parameters',freeze(self.parameters))

    def derive(self, record_id, operation, version='1', parameters=None, *, units=None,
               normalization=None, parents=None, basis=None, clock=None, source_path=None,
               backend=None, evidence='derived'):
        return Provenance(record_id,source_path or self.source_path,operation,version,parameters or {},
            units or self.units,normalization or self.normalization,basis or self.basis,clock or self.clock,
            backend or self.backend,evidence,(self,) if parents is None else tuple(parents))

    def to_dict(self):
        return {k:plain(getattr(self,k)) for k in self.__dataclass_fields__}

    @property
    def digest(self):
        return hashlib.sha256(json.dumps(self.to_dict(),sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()


@dataclass(frozen=True)
class FeatureId:
    path: str
    quantity: str
    kind: str = 'scalar'

    def __post_init__(self):
        for name in ('path','quantity','kind'):
            nonempty(getattr(self,name),name)
        if any(c.isspace() for c in self.path):
            raise ValueError('typed feature paths may not contain whitespace')
        if self.kind not in ('scalar','vector','matrix','tensor','record','events'):
            raise ValueError('unsupported feature kind')

    def to_dict(self):
        return dict(path=self.path,quantity=self.quantity,kind=self.kind)


@dataclass(frozen=True)
class FeatureValue:
    id: FeatureId
    value: Any
    provenance: Provenance
    availability: str = 'available'
    reason: str | None = None
    uncertainty: Mapping[str, Any] | None = None

    def __post_init__(self):
        if not isinstance(self.id,FeatureId) or not isinstance(self.provenance,Provenance):
            raise ValueError('typed ID and provenance required')
        if self.availability not in ('available','missing','unsupported','censored','not_applicable'):
            raise ValueError('invalid availability')
        if self.availability == 'available':
            if self.value is None:
                raise ValueError('available feature requires a value')
        else:
            nonempty(self.reason,'unavailability reason')
            if self.value is not None:
                raise ValueError('unavailable feature cannot pretend to have a measured value')
        object.__setattr__(self,'value',freeze(self.value))
        if self.uncertainty is not None:
            nonempty(self.uncertainty.get('kind'),'uncertainty kind')
            object.__setattr__(self,'uncertainty',freeze(self.uncertainty))

    @property
    def units(self):
        return self.provenance.units

    def require_available(self):
        if self.availability != 'available':
            raise ValueError(f'{self.id.path}: {self.availability}: {self.reason}')
        return self.value

    def to_dict(self):
        return {k:plain(getattr(self,k)) for k in self.__dataclass_fields__}


@dataclass(frozen=True)
class FeatureFrame:
    frame_id: str
    features: tuple[FeatureValue, ...]
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        nonempty(self.frame_id,'frame_id')
        fs=tuple(self.features)
        if not all(isinstance(f,FeatureValue) for f in fs) or len({f.id.path for f in fs})!=len(fs):
            raise ValueError('features must be typed with unique paths')
        object.__setattr__(self,'features',fs)
        object.__setattr__(self,'metadata',freeze(self.metadata))

    def get(self,path: str | FeatureId):
        name=path.path if isinstance(path,FeatureId) else path
        for f in self.features:
            if f.id.path==name:
                if isinstance(path,FeatureId) and path!=f.id:
                    raise ValueError('feature path has incompatible quantity/type')
                return f
        raise KeyError(name)

    def to_dict(self):
        return dict(frame_id=self.frame_id,features=[f.to_dict() for f in self.features],metadata=plain(self.metadata))


@dataclass(frozen=True)
class MappingSpec:
    mapping_id: str
    version: str
    operation: str
    input_ids: tuple[FeatureId,...]
    output_units: str
    normalization: str
    parameters: Mapping[str,Any] = field(default_factory=dict)

    def __post_init__(self):
        for name in ('mapping_id','version','operation','output_units','normalization'):
            nonempty(getattr(self,name),name)
        ids=tuple(self.input_ids)
        if not ids or not all(isinstance(i,FeatureId) for i in ids) or len(set(ids))!=len(ids):
            raise ValueError('mapping must declare distinct typed inputs')
        object.__setattr__(self,'input_ids',ids)
        object.__setattr__(self,'parameters',freeze(self.parameters))


class RoutingMode(str,Enum):
    ANALYSIS='ANALYSIS'
    INSTRUMENT='INSTRUMENT'
    COMPOSITE='COMPOSITE'


@dataclass(frozen=True)
class RouteSpec:
    destination: str
    primary_source: FeatureId
    mapping: MappingSpec
    active: bool = True

    def __post_init__(self):
        nonempty(self.destination,'destination')
        if self.primary_source not in self.mapping.input_ids:
            raise ValueError('primary source must be one of the declared inputs')
        if not isinstance(self.active,bool):
            raise ValueError('route active must be boolean')


@dataclass(frozen=True)
class RoutingPreset:
    preset_id: str
    routes: tuple[RouteSpec,...]

    def __post_init__(self):
        nonempty(self.preset_id,'preset_id')
        rs=tuple(self.routes)
        if not all(isinstance(r,RouteSpec) for r in rs):
            raise ValueError('routes must be RouteSpec')
        object.__setattr__(self,'routes',rs)


@dataclass(frozen=True)
class RoutedFrame:
    frame_id: str
    values: Mapping[str,FeatureValue]
    mode: RoutingMode
    preset_id: str

    def __post_init__(self):
        nonempty(self.frame_id,'frame_id'); nonempty(self.preset_id,'preset_id')
        if not all(isinstance(f,FeatureValue) for f in self.values.values()):
            raise ValueError('routed outputs must retain typed features')
        object.__setattr__(self,'values',MappingProxyType(dict(self.values)))
        object.__setattr__(self,'mode',RoutingMode(self.mode))


@dataclass(frozen=True)
class AnalysisBasis:
    metadata: BasisMetadata
    vectors: np.ndarray
    provenance: Provenance
    eigenvalues: np.ndarray | None = None

    def __post_init__(self):
        if not isinstance(self.metadata,BasisMetadata) or self.metadata.dimension<1:
            raise ValueError('analysis basis needs a positive dimension')
        if not isinstance(self.provenance,Provenance) or self.provenance.basis.to_dict()!=self.metadata.to_dict():
            raise ValueError('analysis basis must carry matching typed provenance')
        v=frozen_array(self.vectors,complex); n=self.metadata.dimension
        if v.shape!=(n,n) or not np.allclose(v.conj().T@v,np.eye(n),atol=1e-10,rtol=0):
            raise ValueError('AnalysisBasis requires square orthonormal columns; use modal projection for other banks')
        object.__setattr__(self,'vectors',v)
        fingerprint=self.provenance.parameters.get('vectors_sha256')
        if fingerprint is not None and fingerprint!=hashlib.sha256(np.asarray(v,dtype='<c16').tobytes()).hexdigest():
            raise ValueError('basis vectors do not match provenance fingerprint')
        if self.eigenvalues is not None:
            if np.iscomplexobj(self.eigenvalues):raise ValueError('basis eigenvalues must be real')
            e=frozen_array(self.eigenvalues,float)
            if e.shape!=(n,): raise ValueError('one eigenvalue per column')
            object.__setattr__(self,'eigenvalues',e)


@dataclass(frozen=True)
class BasisProjectionFrame:
    frame_id: str
    basis: AnalysisBasis
    rho: np.ndarray
    operators: Mapping[str,np.ndarray]
    populations: np.ndarray
    coherences: np.ndarray
    phases: np.ndarray
    phase_valid: np.ndarray
    diagnostics: Mapping[str,Any]
    provenance: Provenance

    def __post_init__(self):
        nonempty(self.frame_id,'frame_id')
        if not isinstance(self.basis,AnalysisBasis) or not isinstance(self.provenance,Provenance):
            raise ValueError('projection needs a valid basis and provenance')
        if self.provenance.basis.to_dict()!=self.basis.metadata.to_dict():
            raise ValueError('projection provenance basis mismatch')
        for name in ('rho','populations','coherences','phases','phase_valid'):
            object.__setattr__(self,name,frozen_array(getattr(self,name)))
        n=self.basis.metadata.dimension
        if self.rho.shape!=(n,n) or self.populations.shape!=(n,) or any(getattr(self,k).shape!=(n,n) for k in ('coherences','phases','phase_valid')):
            raise ValueError('projection shape mismatch')
        if not np.allclose(self.rho,self.rho.conj().T,atol=1e-9,rtol=0) or not np.isclose(np.trace(self.rho),1,atol=1e-9,rtol=0) or np.linalg.eigvalsh(self.rho).min() < -1e-9:
            raise ValueError('projection must remain a valid density matrix')
        if not np.allclose(self.populations,np.diag(self.rho).real,atol=1e-9,rtol=0) or not np.allclose(self.coherences,self.rho-np.diag(np.diag(self.rho)),atol=1e-9,rtol=0):
            raise ValueError('population/coherence diagnostics do not match rho')
        if any(np.shape(v)!=(n,n) for v in self.operators.values()):raise ValueError('operator shape mismatch')
        object.__setattr__(self,'operators',freeze(self.operators))
        object.__setattr__(self,'diagnostics',freeze(self.diagnostics))


@dataclass(frozen=True)
class BackendCapabilities:
    backend_id: str
    kind: str
    operations: frozenset[str]
    available_features: frozenset[str]
    state_access: str
    subsystem_order: str = 'q0_lsb'
    metadata: Mapping[str,Any] = field(default_factory=dict)

    def __post_init__(self):
        for name in ('backend_id','subsystem_order'): nonempty(getattr(self,name),name)
        if self.kind not in ('simulator','hardware','recorded','experimental'):
            raise ValueError('invalid backend kind')
        if self.state_access not in ('authoritative_simulated','estimated','recorded','none'):
            raise ValueError('invalid state access')
        if self.kind!='simulator' and self.state_access=='authoritative_simulated':
            raise ValueError('only simulator may own simulated state')
        if self.state_access=='recorded' and self.kind!='recorded':
            raise ValueError('recorded state access requires a recorded backend')
        for name in ('operations','available_features'):
            vals=frozenset(getattr(self,name))
            for x in vals: nonempty(x,name)
            object.__setattr__(self,name,vals)
        object.__setattr__(self,'metadata',freeze(self.metadata))


@dataclass(frozen=True)
class ExecutionRequest:
    request_id: str
    operation: str
    required_features: frozenset[str]
    timestamp: ClockStamp
    payload: Mapping[str,Any] = field(default_factory=dict)

    def __post_init__(self):
        nonempty(self.request_id,'request_id');nonempty(self.operation,'operation')
        object.__setattr__(self,'required_features',frozenset(self.required_features))
        object.__setattr__(self,'payload',freeze(self.payload))


@dataclass(frozen=True)
class ExecutionResult:
    result_id: str
    request_id: str
    capabilities: BackendCapabilities
    features: tuple[FeatureValue,...]
    provenance: Provenance
    shots: int | None = None
    calibration: Mapping[str,Any] | None = None
    metadata: Mapping[str,Any] = field(default_factory=dict)

    def __post_init__(self):
        nonempty(self.result_id,'result_id');nonempty(self.request_id,'request_id')
        fs=FeatureFrame(self.result_id,tuple(self.features)).features
        if not {f.id.path for f in fs}.issubset(self.capabilities.available_features):
            raise ValueError('result publishes undeclared features')
        object.__setattr__(self,'features',fs)
        if self.shots is not None and (isinstance(self.shots,bool) or not isinstance(self.shots,int) or self.shots<1):
            raise ValueError('shots must be a positive integer or unknown')
        if self.calibration is not None: object.__setattr__(self,'calibration',freeze(self.calibration))
        object.__setattr__(self,'metadata',freeze(self.metadata))


class QuantumBackend(Protocol):
    capabilities: BackendCapabilities
    def execute(self, request: ExecutionRequest) -> ExecutionResult: ...


@dataclass(frozen=True)
class RhythmEvent:
    event_id: str
    onset: ClockStamp
    interval_seconds: float | None
    source_feature: FeatureId
    provenance: Provenance
    active: bool = True

    def __post_init__(self):
        nonempty(self.event_id,'event_id')
        if self.onset.unit!='s' or self.onset.domain!='musical': raise ValueError('rhythm onset requires musical seconds')
        if self.interval_seconds is not None:
            finite(self.interval_seconds,'interval_seconds',minimum=0)


@dataclass(frozen=True)
class RhythmFrame:
    frame_id: str
    events: tuple[RhythmEvent,...]
    mapping_id: str
    provenance: Provenance

    def __post_init__(self):
        object.__setattr__(self,'events',tuple(self.events))


@dataclass(frozen=True)
class MeasurementRecord:
    event_id: str
    source_frame_id: str
    kind: str
    origin: str
    outcome: str | int
    probability: float | None
    basis: BasisMetadata
    clock: ClockStamp
    backend: str
    provenance: Provenance
    pre_state: np.ndarray | None = None
    post_state: np.ndarray | None = None
    shots: int | None = None
    metadata: Mapping[str,Any] = field(default_factory=dict)

    def __post_init__(self):
        for name in ('event_id','source_frame_id','kind','origin','backend'):nonempty(getattr(self,name),name)
        if self.origin not in ('simulated_sample','backend_observed','conditional_evaluation'):
            raise ValueError('explicit simulated, observed, or conditional measurement origin required')
        if self.probability is not None and not 0<=finite(self.probability,'probability')<=1:
            raise ValueError('probability outside [0,1]')
        if self.origin=='backend_observed' and (self.pre_state is not None or self.post_state is not None):
            raise ValueError('backend records cannot fabricate per-shot quantum states; tomography is a separate estimated feature')
        for name in ('pre_state','post_state'):
            if getattr(self,name) is not None:object.__setattr__(self,name,frozen_array(getattr(self,name),complex))
        if self.shots is not None and (isinstance(self.shots,bool) or not isinstance(self.shots,int) or self.shots<1):
            raise ValueError('shots must be positive or unknown')
        object.__setattr__(self,'metadata',freeze(self.metadata))
