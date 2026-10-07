"""Provider-driven runtime steps 20-22 for physical measurement feedback.

Acquisition remains outside the scientific engines: a host injects a provider
that either returns one explicitly sourced sample or no sample.  Transfer
responses pass an admission audit before they reach ``MemoryMatrixEngine``.
Selected scalar channels may be mapped to a generator-control batch, but that
batch is queued for a later tick and never mutates the current quantum frame.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass, field, replace
import math
from threading import RLock
from types import MappingProxyType
from typing import Literal, Protocol

from qmw.quantum import QuantumFrame
from qmw_memory_matrix import MemoryDensityProjection, MemoryMatrixEngine, TransferMatrix

from .frame import QMWFrame, RuntimeStep
from .quantum_engine_adapter import QuantumGeneratorControlBatch
from .scheduler import QMWRuntimeScheduler


MeasurementOrigin = Literal["physical_sensor", "test_fixture"]
_ORIGINS = frozenset(("physical_sensor", "test_fixture"))
_EPS = 1.0e-12


def _nonnegative_integer(value: object, *, name: str) -> int:
    if isinstance(value, bool):
        raise ValueError(f"{name} must be a nonnegative integer")
    try:
        result = int(value)
    except (TypeError, ValueError, OverflowError) as cause:
        raise ValueError(f"{name} must be a nonnegative integer") from cause
    if result != value or result < 0:
        raise ValueError(f"{name} must be a nonnegative integer")
    return result


def _finite(value: object, *, name: str) -> float:
    result = float(value)
    if not math.isfinite(result):
        raise ValueError(f"{name} must be finite")
    return result


def _label(value: object, *, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a nonempty string")
    return value


def _origins(values: object, *, name: str) -> tuple[MeasurementOrigin, ...]:
    declared = tuple(values)  # type: ignore[arg-type]
    if not declared or len(set(declared)) != len(declared):
        raise ValueError(f"{name} must contain unique declared origins")
    if any(value not in _ORIGINS for value in declared):
        raise ValueError(f"{name} contains an unknown measurement origin")
    return declared  # type: ignore[return-value]


@dataclass(frozen=True)
class MeasurementRequest:
    """Read-only acquisition request for one synchronized runtime tick."""

    tick: int
    time: float
    dt: float
    quantum_revision: int
    audio_revision: int
    measurement_revision: int
    provenance: str = "qmw_measurement_acquisition_request_v1"

    def __post_init__(self) -> None:
        object.__setattr__(self, "tick", _nonnegative_integer(self.tick, name="tick"))
        object.__setattr__(self, "time", _finite(self.time, name="time"))
        dt = _finite(self.dt, name="dt")
        if dt < 0.0:
            raise ValueError("dt must be nonnegative")
        object.__setattr__(self, "dt", dt)
        for name in ("quantum_revision", "audio_revision", "measurement_revision"):
            object.__setattr__(self, name, _nonnegative_integer(getattr(self, name), name=name))
        object.__setattr__(self, "provenance", _label(self.provenance, name="provenance"))


@dataclass(frozen=True)
class TransferMeasurementQuality:
    """Acquisition facts required before a transfer response can be admitted."""

    calibrated: bool
    timing_synchronized: bool
    calibration_id: str
    captured_samples: int
    snr_db: float
    clipped_fraction: float = 0.0

    def __post_init__(self) -> None:
        if not isinstance(self.calibrated, bool) or not isinstance(self.timing_synchronized, bool):
            raise TypeError("calibrated and timing_synchronized must be booleans")
        object.__setattr__(self, "calibration_id", _label(self.calibration_id, name="calibration_id"))
        object.__setattr__(
            self,
            "captured_samples",
            _nonnegative_integer(self.captured_samples, name="captured_samples"),
        )
        if self.captured_samples < 2:
            raise ValueError("captured_samples must be at least two")
        object.__setattr__(self, "snr_db", _finite(self.snr_db, name="snr_db"))
        clipped = _finite(self.clipped_fraction, name="clipped_fraction")
        if not 0.0 <= clipped <= 1.0:
            raise ValueError("clipped_fraction must lie in [0, 1]")
        object.__setattr__(self, "clipped_fraction", clipped)


@dataclass(frozen=True)
class AcquiredMeasurement:
    """One provider-sourced sample; origin remains explicit in every fixture."""

    revision: int
    acquired_time: float
    provider_id: str
    measurement_id: str
    origin: MeasurementOrigin
    channels: Mapping[str, float] = field(default_factory=dict)
    transfer: TransferMatrix | None = None
    transfer_quality: TransferMeasurementQuality | None = None
    provenance: str = "provider_acquired_measurement_v1"

    def __post_init__(self) -> None:
        object.__setattr__(self, "revision", _nonnegative_integer(self.revision, name="revision"))
        object.__setattr__(self, "acquired_time", _finite(self.acquired_time, name="acquired_time"))
        object.__setattr__(self, "provider_id", _label(self.provider_id, name="provider_id"))
        object.__setattr__(self, "measurement_id", _label(self.measurement_id, name="measurement_id"))
        if self.origin not in _ORIGINS:
            raise ValueError("origin must be physical_sensor or test_fixture")
        if not isinstance(self.channels, Mapping):
            raise TypeError("channels must be a mapping")
        channels: dict[str, float] = {}
        for raw_name, raw_value in self.channels.items():
            name = _label(raw_name, name="measurement channel")
            if name in channels:
                raise ValueError("measurement channel names must be unique")
            channels[name] = _finite(raw_value, name=f"channel {name}")
        object.__setattr__(self, "channels", MappingProxyType(channels))
        if self.transfer is not None and not isinstance(self.transfer, TransferMatrix):
            raise TypeError("transfer must be a TransferMatrix")
        if self.transfer is None and self.transfer_quality is not None:
            raise ValueError("transfer_quality requires a transfer response")
        if self.transfer is not None and not isinstance(self.transfer_quality, TransferMeasurementQuality):
            raise ValueError("a transfer response requires TransferMeasurementQuality")
        object.__setattr__(self, "provenance", _label(self.provenance, name="provenance"))


class MeasurementProvider(Protocol):
    """Injected hardware/service boundary; returning ``None`` means no sample."""

    def acquire(self, request: MeasurementRequest) -> AcquiredMeasurement | None:
        ...


@dataclass(frozen=True)
class TransferMeasurementValidation:
    """Audit result controlling the sole path into adaptive transfer memory."""

    accepted: bool
    reasons: tuple[str, ...]
    measurement_revision: int | None
    transfer_revision: int | None
    provenance: str = "qmw_transfer_measurement_validation_v1"

    def __post_init__(self) -> None:
        if not isinstance(self.accepted, bool):
            raise TypeError("accepted must be boolean")
        reasons = tuple(str(reason) for reason in self.reasons)
        if (self.accepted and reasons) or (not self.accepted and not reasons):
            raise ValueError("accepted validation has no reasons; rejected validation has reasons")
        object.__setattr__(self, "reasons", reasons)
        for name in ("measurement_revision", "transfer_revision"):
            value = getattr(self, name)
            if value is not None:
                object.__setattr__(self, name, _nonnegative_integer(value, name=name))
        object.__setattr__(self, "provenance", _label(self.provenance, name="provenance"))


@dataclass(frozen=True)
class TransferMemoryEstimateUpdate:
    """Records an estimate transition that becomes observable next tick."""

    admitted: bool
    prior_update_count: int
    resulting_update_count: int
    resulting_transfer_revision: int | None
    effective_tick: int
    reasons: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.admitted, bool):
            raise TypeError("admitted must be boolean")
        for name in ("prior_update_count", "resulting_update_count", "effective_tick"):
            object.__setattr__(self, name, _nonnegative_integer(getattr(self, name), name=name))
        if self.resulting_transfer_revision is not None:
            object.__setattr__(
                self,
                "resulting_transfer_revision",
                _nonnegative_integer(self.resulting_transfer_revision, name="resulting_transfer_revision"),
            )
        object.__setattr__(self, "reasons", tuple(str(reason) for reason in self.reasons))
        if self.admitted:
            if self.resulting_update_count != self.prior_update_count + 1:
                raise ValueError("an admitted transfer update must advance update_count exactly once")
            if self.resulting_transfer_revision is None or self.reasons:
                raise ValueError("an admitted transfer update requires a revision and no rejection reasons")
        elif (
            self.resulting_update_count != self.prior_update_count
            or self.resulting_transfer_revision is not None
            or not self.reasons
        ):
            raise ValueError("a rejected transfer update must preserve state and declare reasons")


@dataclass(frozen=True)
class SelectedMeasurement:
    """Only the explicitly named scalar channels exposed to a feedback mapper."""

    source_tick: int
    source_measurement_revision: int
    provider_id: str
    measurement_id: str
    channels: Mapping[str, float]

    def __post_init__(self) -> None:
        object.__setattr__(self, "source_tick", _nonnegative_integer(self.source_tick, name="source_tick"))
        object.__setattr__(
            self,
            "source_measurement_revision",
            _nonnegative_integer(self.source_measurement_revision, name="source_measurement_revision"),
        )
        object.__setattr__(self, "provider_id", _label(self.provider_id, name="provider_id"))
        object.__setattr__(self, "measurement_id", _label(self.measurement_id, name="measurement_id"))
        selected = {str(name): _finite(value, name=f"selected channel {name}") for name, value in self.channels.items()}
        if not selected:
            raise ValueError("selected feedback channels must be nonempty")
        object.__setattr__(self, "channels", MappingProxyType(selected))


@dataclass(frozen=True)
class QueuedMeasurementFeedback:
    """A delayed generator batch with its measurement provenance."""

    source_tick: int
    eligible_tick: int
    selection: SelectedMeasurement
    batch: QuantumGeneratorControlBatch
    provenance: str = "selected_measurement_to_next_tick_generator_controls_v1"

    def __post_init__(self) -> None:
        source = _nonnegative_integer(self.source_tick, name="source_tick")
        eligible = _nonnegative_integer(self.eligible_tick, name="eligible_tick")
        if eligible <= source:
            raise ValueError("feedback eligible_tick must be later than source_tick")
        if not isinstance(self.selection, SelectedMeasurement):
            raise TypeError("selection must be SelectedMeasurement")
        if not isinstance(self.batch, QuantumGeneratorControlBatch):
            raise TypeError("batch must be QuantumGeneratorControlBatch")
        object.__setattr__(self, "source_tick", source)
        object.__setattr__(self, "eligible_tick", eligible)
        object.__setattr__(self, "provenance", _label(self.provenance, name="provenance"))


class MeasurementFeedbackQueue:
    """Thread-safe delayed handoff; the host injects ready batches at step 1."""

    def __init__(self) -> None:
        self._lock = RLock()
        self._pending: list[QueuedMeasurementFeedback] = []
        self._last_batch_revision = -1

    @property
    def pending(self) -> tuple[QueuedMeasurementFeedback, ...]:
        with self._lock:
            return tuple(self._pending)

    def enqueue(self, item: QueuedMeasurementFeedback) -> None:
        if not isinstance(item, QueuedMeasurementFeedback):
            raise TypeError("item must be QueuedMeasurementFeedback")
        with self._lock:
            if item.batch.revision <= self._last_batch_revision:
                raise ValueError("feedback batch revisions must increase monotonically")
            self._pending.append(item)
            self._pending.sort(key=lambda value: (value.eligible_tick, value.batch.revision))
            self._last_batch_revision = item.batch.revision

    def pop_ready(self, tick: int) -> tuple[QueuedMeasurementFeedback, ...]:
        declared_tick = _nonnegative_integer(tick, name="tick")
        with self._lock:
            ready = tuple(item for item in self._pending if item.eligible_tick <= declared_tick)
            if ready:
                ready_ids = {id(item) for item in ready}
                self._pending = [item for item in self._pending if id(item) not in ready_ids]
            return ready


@dataclass(frozen=True)
class MeasurementRuntimeFrame:
    """Composite step-20/21/22 result carried by ``QMWFrame.measurement``."""

    revision: int
    request: MeasurementRequest
    sample: AcquiredMeasurement | None
    acquisition_valid: bool
    acquisition_reasons: tuple[str, ...] = ()
    transfer_validation: TransferMeasurementValidation | None = None
    transfer_update: TransferMemoryEstimateUpdate | None = None
    queued_feedback: QueuedMeasurementFeedback | None = None
    feedback_reasons: tuple[str, ...] = ()
    provenance: str = "qmw_measurement_feedback_runtime_frame_v1"

    def __post_init__(self) -> None:
        object.__setattr__(self, "revision", _nonnegative_integer(self.revision, name="revision"))
        if not isinstance(self.request, MeasurementRequest):
            raise TypeError("request must be MeasurementRequest")
        if self.sample is not None and not isinstance(self.sample, AcquiredMeasurement):
            raise TypeError("sample must be AcquiredMeasurement or None")
        if not isinstance(self.acquisition_valid, bool):
            raise TypeError("acquisition_valid must be boolean")
        reasons = tuple(str(reason) for reason in self.acquisition_reasons)
        if self.sample is None and self.acquisition_valid:
            raise ValueError("a missing sample cannot be acquisition_valid")
        if self.acquisition_valid and reasons:
            raise ValueError("a valid acquisition cannot carry rejection reasons")
        if self.sample is not None and not self.acquisition_valid and not reasons:
            raise ValueError("an invalid acquisition requires rejection reasons")
        object.__setattr__(self, "acquisition_reasons", reasons)
        object.__setattr__(self, "feedback_reasons", tuple(str(reason) for reason in self.feedback_reasons))
        object.__setattr__(self, "provenance", _label(self.provenance, name="provenance"))


FeedbackMapper = Callable[[SelectedMeasurement, QMWFrame], QuantumGeneratorControlBatch | None]
MemoryDensityProjector = Callable[[QuantumFrame], MemoryDensityProjection]


@dataclass(frozen=True)
class MeasurementFeedbackConfig:
    """Admission thresholds plus a separate explicit feedback permission."""

    max_sample_age_seconds: float = 0.25
    min_transfer_snr_db: float = 20.0
    max_transfer_clipped_fraction: float = 0.0
    admitted_transfer_origins: tuple[MeasurementOrigin, ...] = ("physical_sensor",)
    admitted_feedback_origins: tuple[MeasurementOrigin, ...] = ("physical_sensor",)
    feedback_enabled: bool = False
    selected_feedback_channels: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        age = _finite(self.max_sample_age_seconds, name="max_sample_age_seconds")
        if age < 0.0:
            raise ValueError("max_sample_age_seconds must be nonnegative")
        object.__setattr__(self, "max_sample_age_seconds", age)
        object.__setattr__(self, "min_transfer_snr_db", _finite(self.min_transfer_snr_db, name="min_transfer_snr_db"))
        clipped = _finite(self.max_transfer_clipped_fraction, name="max_transfer_clipped_fraction")
        if not 0.0 <= clipped <= 1.0:
            raise ValueError("max_transfer_clipped_fraction must lie in [0, 1]")
        object.__setattr__(self, "max_transfer_clipped_fraction", clipped)
        object.__setattr__(
            self,
            "admitted_transfer_origins",
            _origins(self.admitted_transfer_origins, name="admitted_transfer_origins"),
        )
        object.__setattr__(
            self,
            "admitted_feedback_origins",
            _origins(self.admitted_feedback_origins, name="admitted_feedback_origins"),
        )
        if not isinstance(self.feedback_enabled, bool):
            raise TypeError("feedback_enabled must be boolean")
        selected = tuple(_label(name, name="selected feedback channel") for name in self.selected_feedback_channels)
        if len(set(selected)) != len(selected):
            raise ValueError("selected_feedback_channels must be unique")
        object.__setattr__(self, "selected_feedback_channels", selected)


class MeasurementFeedbackRuntimeAdapter:
    """Acquire, validate/admit transfer data, and queue selected feedback."""

    def __init__(
        self,
        provider: MeasurementProvider,
        memory_engine: MemoryMatrixEngine,
        *,
        config: MeasurementFeedbackConfig | None = None,
        density_projector: MemoryDensityProjector | None = None,
        feedback_mapper: FeedbackMapper | None = None,
        feedback_queue: MeasurementFeedbackQueue | None = None,
    ) -> None:
        if not callable(getattr(provider, "acquire", None)):
            raise TypeError("provider must define callable acquire(request)")
        if not isinstance(memory_engine, MemoryMatrixEngine):
            raise TypeError("memory_engine must be a MemoryMatrixEngine")
        if density_projector is not None and not callable(density_projector):
            raise TypeError("density_projector must be callable")
        if feedback_mapper is not None and not callable(feedback_mapper):
            raise TypeError("feedback_mapper must be callable")
        if feedback_queue is not None and not isinstance(feedback_queue, MeasurementFeedbackQueue):
            raise TypeError("feedback_queue must be MeasurementFeedbackQueue")
        self.provider = provider
        self.memory_engine = memory_engine
        self.config = MeasurementFeedbackConfig() if config is None else config
        if not isinstance(self.config, MeasurementFeedbackConfig):
            raise TypeError("config must be MeasurementFeedbackConfig")
        self.density_projector = density_projector
        self.feedback_mapper = feedback_mapper
        self.feedback_queue = MeasurementFeedbackQueue() if feedback_queue is None else feedback_queue
        self._lock = RLock()
        self._last_provider_revisions: dict[str, int] = {}
        self._last_measurement_ids: set[tuple[str, str]] = set()
        self._last_runtime_measurement_revision = -1

    def _projection(self, quantum: QuantumFrame) -> MemoryDensityProjection:
        if self.density_projector is None:
            if quantum.rho.shape != (self.memory_engine.nodes, self.memory_engine.nodes):
                raise ValueError(
                    "quantum rho does not match memory nodes; provide an explicit named density_projector"
                )
            projection = MemoryDensityProjection(
                rho=quantum.rho,
                basis_label=self.memory_engine.basis_label,
                quantum_revision=quantum.frame_index,
                provenance="direct_authoritative_density_in_declared_memory_basis_v1",
            )
        else:
            projection = self.density_projector(quantum)
        if not isinstance(projection, MemoryDensityProjection):
            raise TypeError("density_projector must return MemoryDensityProjection")
        if projection.quantum_revision != quantum.frame_index:
            raise ValueError("memory density projection must cite the current quantum revision")
        return projection

    def _acquisition_reasons(self, sample: AcquiredMeasurement, frame: QMWFrame) -> tuple[str, ...]:
        reasons: list[str] = []
        age = frame.time - sample.acquired_time
        if age < -_EPS:
            reasons.append("acquired_in_future")
        elif age > self.config.max_sample_age_seconds + _EPS:
            reasons.append("sample_too_old")
        last_revision = self._last_provider_revisions.get(sample.provider_id)
        if last_revision is not None and sample.revision <= last_revision:
            reasons.append("provider_revision_not_monotonic")
        if (sample.provider_id, sample.measurement_id) in self._last_measurement_ids:
            reasons.append("measurement_id_replayed")
        return tuple(reasons)

    def acquire_measurement(self, frame: QMWFrame) -> QMWFrame:
        request = MeasurementRequest(
            tick=frame.tick,
            time=frame.time,
            dt=frame.dt,
            quantum_revision=frame.revisions.quantum,
            audio_revision=frame.revisions.audio,
            measurement_revision=frame.revisions.measurement,
        )
        sample = self.provider.acquire(request)
        if sample is not None and not isinstance(sample, AcquiredMeasurement):
            raise TypeError("measurement provider must return AcquiredMeasurement or None")
        with self._lock:
            reasons = () if sample is None else self._acquisition_reasons(sample, frame)
            valid = sample is not None and not reasons
            if valid and sample is not None:
                self._last_provider_revisions[sample.provider_id] = sample.revision
                self._last_measurement_ids.add((sample.provider_id, sample.measurement_id))
            revision = max(
                frame.revisions.measurement,
                self._last_runtime_measurement_revision,
            ) + 1
            self._last_runtime_measurement_revision = revision
            measurement = MeasurementRuntimeFrame(
                revision=revision,
                request=request,
                sample=sample,
                acquisition_valid=valid,
                acquisition_reasons=("no_sample",) if sample is None else reasons,
            )
        diagnostics = dict(frame.diagnostics)
        diagnostics.update(
            {
                "measurement_provider_called": True,
                "measurement_sample_available": sample is not None,
                "measurement_acquisition_valid": valid,
                "measurement_origin": None if sample is None else sample.origin,
            }
        )
        return frame.with_updates(
            measurement=measurement,
            revisions=replace(frame.revisions, measurement=revision),
            diagnostics=diagnostics,
        )

    def _transfer_validation(self, measurement: MeasurementRuntimeFrame) -> TransferMeasurementValidation:
        sample = measurement.sample
        reasons: list[str] = []
        if sample is None:
            reasons.append("no_sample")
        elif not measurement.acquisition_valid:
            reasons.extend(measurement.acquisition_reasons)
        elif sample.transfer is None:
            reasons.append("no_transfer_response")
        else:
            quality = sample.transfer_quality
            assert quality is not None
            if sample.origin not in self.config.admitted_transfer_origins:
                reasons.append("origin_not_admitted_for_transfer")
            if not quality.calibrated:
                reasons.append("not_calibrated")
            if not quality.timing_synchronized:
                reasons.append("timing_not_synchronized")
            if quality.captured_samples != sample.transfer.samples:
                reasons.append("captured_sample_count_mismatch")
            if quality.snr_db < self.config.min_transfer_snr_db:
                reasons.append("snr_below_threshold")
            if quality.clipped_fraction > self.config.max_transfer_clipped_fraction + _EPS:
                reasons.append("clipping_above_threshold")
            if not self.memory_engine.adaptive_memory.transfer.compatible_with(sample.transfer):
                reasons.append("transfer_incompatible_with_memory")
        transfer_revision = None if sample is None or sample.transfer is None else sample.transfer.revision
        return TransferMeasurementValidation(
            accepted=not reasons,
            reasons=tuple(reasons),
            measurement_revision=None if sample is None else sample.revision,
            transfer_revision=transfer_revision,
        )

    def update_transfer_memory_estimate(self, frame: QMWFrame) -> QMWFrame:
        if not isinstance(frame.measurement, MeasurementRuntimeFrame):
            raise TypeError("step 21 requires MeasurementRuntimeFrame from step 20")
        validation = self._transfer_validation(frame.measurement)
        before = self.memory_engine.adaptive_memory.update_count
        resulting_revision: int | None = None
        if validation.accepted:
            if frame.dt <= 0.0:
                validation = replace(
                    validation,
                    accepted=False,
                    reasons=("positive_tick_dt_required_for_transfer_update",),
                )
            else:
                sample = frame.measurement.sample
                assert sample is not None and sample.transfer is not None
                if not isinstance(frame.quantum, QuantumFrame):
                    raise TypeError("QMWFrame.quantum must be an authoritative QuantumFrame")
                updated = self.memory_engine.update_from_measured_response(
                    sample.transfer,
                    dt=frame.dt,
                    projection=self._projection(frame.quantum),
                )
                resulting_revision = updated.transfer.revision
        after = self.memory_engine.adaptive_memory.update_count
        update = TransferMemoryEstimateUpdate(
            admitted=validation.accepted,
            prior_update_count=before,
            resulting_update_count=after,
            resulting_transfer_revision=resulting_revision,
            effective_tick=frame.tick + 1,
            reasons=validation.reasons,
        )
        measurement = replace(
            frame.measurement,
            transfer_validation=validation,
            transfer_update=update,
        )
        diagnostics = dict(frame.diagnostics)
        diagnostics.update(
            {
                "transfer_measurement_admitted": validation.accepted,
                "transfer_measurement_reasons": validation.reasons,
                "transfer_memory_update_effective_tick": frame.tick + 1,
                "transfer_memory_current_frame_rewritten": False,
            }
        )
        return frame.with_updates(measurement=measurement, diagnostics=diagnostics)

    def feed_selected_measurements(self, frame: QMWFrame) -> QMWFrame:
        if not isinstance(frame.measurement, MeasurementRuntimeFrame):
            raise TypeError("step 22 requires MeasurementRuntimeFrame from step 20")
        sample = frame.measurement.sample
        reasons: list[str] = []
        if not self.config.feedback_enabled:
            reasons.append("feedback_disabled")
        if self.feedback_mapper is None:
            reasons.append("feedback_mapper_not_configured")
        if not self.config.selected_feedback_channels:
            reasons.append("no_feedback_channels_selected")
        if sample is None:
            reasons.append("no_sample")
        elif not frame.measurement.acquisition_valid:
            reasons.extend(frame.measurement.acquisition_reasons)
        elif sample.origin not in self.config.admitted_feedback_origins:
            reasons.append("origin_not_admitted_for_feedback")
        if sample is not None:
            missing = tuple(name for name in self.config.selected_feedback_channels if name not in sample.channels)
            if missing:
                reasons.append("selected_feedback_channel_missing:" + ",".join(missing))

        queued: QueuedMeasurementFeedback | None = None
        if not reasons:
            assert sample is not None and self.feedback_mapper is not None
            selection = SelectedMeasurement(
                source_tick=frame.tick,
                source_measurement_revision=sample.revision,
                provider_id=sample.provider_id,
                measurement_id=sample.measurement_id,
                channels={name: sample.channels[name] for name in self.config.selected_feedback_channels},
            )
            batch = self.feedback_mapper(selection, frame)
            if batch is None:
                reasons.append("feedback_mapper_declined")
            elif not isinstance(batch, QuantumGeneratorControlBatch):
                raise TypeError("feedback_mapper must return QuantumGeneratorControlBatch or None")
            elif not batch.controls:
                reasons.append("feedback_mapper_produced_empty_batch")
            elif any(control.time < frame.time - _EPS for control in batch.controls):
                raise ValueError("feedback controls may not target time before their source measurement")
            else:
                queued = QueuedMeasurementFeedback(
                    source_tick=frame.tick,
                    eligible_tick=frame.tick + 1,
                    selection=selection,
                    batch=batch,
                )
                self.feedback_queue.enqueue(queued)

        measurement = replace(
            frame.measurement,
            queued_feedback=queued,
            feedback_reasons=tuple(reasons),
        )
        diagnostics = dict(frame.diagnostics)
        diagnostics.update(
            {
                "measurement_feedback_queued": queued is not None,
                "measurement_feedback_reasons": tuple(reasons),
                "measurement_feedback_current_quantum_mutated": False,
                "measurement_feedback_eligible_tick": None if queued is None else queued.eligible_tick,
            }
        )
        return frame.with_updates(
            measurement=measurement,
            triggers=frame.triggers.cleared("feedback"),
            diagnostics=diagnostics,
        )


def register_measurement_feedback(
    scheduler: QMWRuntimeScheduler,
    provider: MeasurementProvider,
    memory_engine: MemoryMatrixEngine,
    *,
    config: MeasurementFeedbackConfig | None = None,
    density_projector: MemoryDensityProjector | None = None,
    feedback_mapper: FeedbackMapper | None = None,
    feedback_queue: MeasurementFeedbackQueue | None = None,
) -> MeasurementFeedbackRuntimeAdapter:
    """Register the provider boundary, estimator admission, and delayed queue."""

    if not isinstance(scheduler, QMWRuntimeScheduler):
        raise TypeError("scheduler must be a QMWRuntimeScheduler")
    adapter = MeasurementFeedbackRuntimeAdapter(
        provider,
        memory_engine,
        config=config,
        density_projector=density_projector,
        feedback_mapper=feedback_mapper,
        feedback_queue=feedback_queue,
    )
    scheduler.register(RuntimeStep.ACQUIRE_MEASUREMENT, adapter.acquire_measurement)
    scheduler.register(
        RuntimeStep.UPDATE_TRANSFER_MEMORY_ESTIMATE,
        adapter.update_transfer_memory_estimate,
    )
    scheduler.register(RuntimeStep.FEED_SELECTED_MEASUREMENTS, adapter.feed_selected_measurements)
    return adapter


__all__ = [
    "AcquiredMeasurement",
    "FeedbackMapper",
    "MeasurementFeedbackConfig",
    "MeasurementFeedbackQueue",
    "MeasurementFeedbackRuntimeAdapter",
    "MeasurementOrigin",
    "MeasurementProvider",
    "MeasurementRequest",
    "MeasurementRuntimeFrame",
    "QueuedMeasurementFeedback",
    "SelectedMeasurement",
    "TransferMeasurementQuality",
    "TransferMeasurementValidation",
    "TransferMemoryEstimateUpdate",
    "register_measurement_feedback",
]
