"""Runtime steps 17-19 over existing Unified Instrument V3 observers.

This bridge is downstream-only. It never reads an acoustic descriptor back
into H or rho, and its default renderer produces a control-rate complex field,
not PCM samples or an audio-device stream.
"""

from __future__ import annotations

from dataclasses import dataclass, field as dataclass_field, replace
import math
from typing import Any, Protocol

import numpy as np

from qmw.unified_instrument_v3 import (
    AcousticFieldConfig,
    AcousticFieldFrame,
    FlowExcitationFrame,
    GeometryBoundaryConfig,
    GeometryBoundaryFrame,
    ModalResonanceConfig,
    ModalResonanceFrame,
    PerformerEmphasisFrame,
    RelationalGeometryFrame,
    RelationalSpectralConfig,
    RelationalSpectralControlFrame,
    StereoObservationFrame,
    TuningGeometryConfig,
    TuningGeometryFrame,
    observe_acoustic_field,
    observe_geometry_boundary,
    observe_mid_side_stereo,
    observe_modal_resonance,
    observe_relational_spectral_control,
    observe_tuning_geometry,
)
from qmw.unified_instrument_v3.frames import MODE_COUNT

from .frame import QMWFrame, RuntimeStep
from .scheduler import QMWRuntimeScheduler


_ZERO_GAINS = (0.0,) * MODE_COUNT
_ZERO_COMPLEX = (0.0j,) * MODE_COUNT
_RECEIVER_GAIN = 1.0 / math.sqrt(MODE_COUNT // 2)
_EVEN_RECEIVER = tuple(_RECEIVER_GAIN if i % 2 == 0 else 0.0 for i in range(MODE_COUNT))
_ODD_RECEIVER = tuple(_RECEIVER_GAIN if i % 2 == 1 else 0.0 for i in range(MODE_COUNT))


def _revision(value: int, *, name: str) -> int:
    if isinstance(value, bool) or int(value) != value or value < 0:
        raise ValueError(f"{name} must be a nonnegative integer")
    return int(value)


def _finite_time(value: float) -> float:
    result = float(value)
    if not math.isfinite(result):
        raise ValueError("time must be finite")
    return result


def _component_name(value: object, *, method: str, role: str) -> str:
    name = getattr(value, "name", None)
    if not isinstance(name, str) or not name:
        raise TypeError(f"{role} must expose a nonempty name")
    if not callable(getattr(value, method, None)):
        raise TypeError(f"{role} must implement {method}()")
    return name


@dataclass(frozen=True)
class SoundCapabilityUnavailable:
    """Explicit non-error result when a sound-stage capability is absent."""

    capability: str
    time: float
    source_revision: int
    reason: str
    provenance: str = "explicit_unavailable_downstream_sound_capability_v1"

    def __post_init__(self) -> None:
        if self.capability not in {"excitation", "audio", "spatial"}:
            raise ValueError("capability must be excitation, audio, or spatial")
        object.__setattr__(self, "time", _finite_time(self.time))
        object.__setattr__(
            self, "source_revision", _revision(self.source_revision, name="source_revision")
        )
        if not isinstance(self.reason, str) or not self.reason:
            raise ValueError("reason must be nonempty")
        if not isinstance(self.provenance, str) or not self.provenance:
            raise ValueError("provenance must be nonempty")


@dataclass(frozen=True)
class V3ModalExcitationFrame:
    """Synchronized V3 resonator inputs produced by a named provider."""

    revision: int
    time: float
    geometry: RelationalGeometryFrame
    boundary: GeometryBoundaryFrame
    tuning: TuningGeometryFrame
    resonance: ModalResonanceFrame
    relational_control: RelationalSpectralControlFrame
    performer: PerformerEmphasisFrame
    flow: FlowExcitationFrame
    provider_name: str
    provenance: str = "synchronized_v3_modal_excitation_inputs_v1"

    def __post_init__(self) -> None:
        revision = _revision(self.revision, name="revision")
        time = _finite_time(self.time)
        typed = (
            (self.geometry, RelationalGeometryFrame, "geometry"),
            (self.boundary, GeometryBoundaryFrame, "boundary"),
            (self.tuning, TuningGeometryFrame, "tuning"),
            (self.resonance, ModalResonanceFrame, "resonance"),
            (self.relational_control, RelationalSpectralControlFrame, "relational_control"),
            (self.performer, PerformerEmphasisFrame, "performer"),
            (self.flow, FlowExcitationFrame, "flow"),
        )
        for value, expected, name in typed:
            if not isinstance(value, expected):
                raise TypeError(f"{name} must be a {expected.__name__}")
            if not math.isclose(value.time, time, rel_tol=0.0, abs_tol=1.0e-12):
                raise ValueError("all excitation inputs must share one time")
        if revision != self.geometry.revision:
            raise ValueError("excitation revision must match geometry revision")
        if self.boundary.geometry_revision != revision:
            raise ValueError("boundary must source the declared geometry")
        if self.tuning.geometry_revision != revision:
            raise ValueError("tuning must source the declared geometry")
        if self.relational_control.geometry_revision != revision:
            raise ValueError("relational control must source the declared geometry")
        if self.resonance.tuning_revision != self.tuning.revision:
            raise ValueError("resonance must source the declared tuning")
        mode_ids = self.resonance.mode_ids
        if any(
            item.mode_ids != mode_ids
            for item in (
                self.boundary, self.tuning, self.relational_control, self.performer, self.flow
            )
        ):
            raise ValueError("all excitation inputs must share stable mode ordering")
        if not isinstance(self.provider_name, str) or not self.provider_name:
            raise ValueError("provider_name must be nonempty")
        if not isinstance(self.provenance, str) or not self.provenance:
            raise ValueError("provenance must be nonempty")
        object.__setattr__(self, "revision", revision)
        object.__setattr__(self, "time", time)


class ModalExcitationProvider(Protocol):
    """Named seam for creative and flow excitation sources."""

    name: str

    def provide(
        self, frame: QMWFrame, resonance: ModalResonanceFrame
    ) -> tuple[PerformerEmphasisFrame, FlowExcitationFrame]: ...


class SoundDescriptorRenderer(Protocol):
    """Named renderer seam; implementations declare their output level."""

    name: str
    output_level: str
    produces_audio_buffer: bool

    def render(self, frame: QMWFrame, excitation: V3ModalExcitationFrame) -> Any: ...


class SpatialDescriptorObserver(Protocol):
    """Named spatial observer seam over one renderer payload."""

    name: str
    output_level: str

    def observe(
        self, frame: QMWFrame, audio: Any, excitation: V3ModalExcitationFrame
    ) -> Any: ...


@dataclass(frozen=True)
class FixedModalExcitationProvider:
    """Explicit fixed creative input, defaulting to safe silence."""

    performer_gain: object = _ZERO_GAINS
    modal_excitation: object = _ZERO_COMPLEX
    name: str = "fixed_modal_excitation_provider_v1"

    def __post_init__(self) -> None:
        gain = np.asarray(self.performer_gain, dtype=float)
        flow = np.asarray(self.modal_excitation, dtype=np.complex128)
        if gain.shape != (MODE_COUNT,) or not np.all(np.isfinite(gain)) or np.any(gain < 0.0):
            raise ValueError("performer_gain must be a finite nonnegative 20-vector")
        if flow.shape != (MODE_COUNT,) or not np.all(np.isfinite(flow)):
            raise ValueError("modal_excitation must be a finite complex 20-vector")
        if not isinstance(self.name, str) or not self.name:
            raise ValueError("name must be nonempty")
        object.__setattr__(self, "performer_gain", tuple(float(value) for value in gain))
        object.__setattr__(self, "modal_excitation", tuple(complex(value) for value in flow))

    @classmethod
    def unity_carrier(cls) -> "FixedModalExcitationProvider":
        """Return an opt-in all-mode unit carrier with no flow component."""

        return cls(performer_gain=(1.0,) * MODE_COUNT)

    def provide(
        self, frame: QMWFrame, resonance: ModalResonanceFrame
    ) -> tuple[PerformerEmphasisFrame, FlowExcitationFrame]:
        return (
            PerformerEmphasisFrame(
                revision=resonance.revision,
                time=frame.time,
                mode_ids=resonance.mode_ids,
                gain=self.performer_gain,
                provenance="explicit_fixed_creative_modal_emphasis_v1",
            ),
            FlowExcitationFrame(
                revision=resonance.revision,
                time=frame.time,
                mode_ids=resonance.mode_ids,
                modal_excitation=self.modal_excitation,
                provenance="explicit_fixed_nonquantum_modal_excitation_v1",
            ),
        )


@dataclass(frozen=True)
class V3AcousticDescriptorRenderer:
    """Render V3 inputs to the existing complex acoustic-field contract."""

    config: AcousticFieldConfig = dataclass_field(default_factory=AcousticFieldConfig)
    name: str = "v3_acoustic_complex_field_descriptor_renderer_v1"
    output_level: str = "control_rate_complex_modal_descriptor"
    produces_audio_buffer: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.config, AcousticFieldConfig):
            raise TypeError("config must be an AcousticFieldConfig")

    def render(
        self, frame: QMWFrame, excitation: V3ModalExcitationFrame
    ) -> AcousticFieldFrame:
        return observe_acoustic_field(
            excitation.resonance,
            excitation.performer,
            excitation.flow,
            config=self.config,
            relational_control=excitation.relational_control,
            revision=excitation.revision,
        )


@dataclass(frozen=True)
class MidSideStereoDescriptorObserver:
    """Portable normalized alternating-mode M/S receiver observation."""

    even_receiver: object = _EVEN_RECEIVER
    odd_receiver: object = _ODD_RECEIVER
    name: str = "v3_normalized_alternating_mode_mid_side_observer_v1"
    output_level: str = "control_rate_complex_stereo_descriptor"

    def __post_init__(self) -> None:
        even = np.asarray(self.even_receiver, dtype=np.complex128)
        odd = np.asarray(self.odd_receiver, dtype=np.complex128)
        if any(v.shape != (MODE_COUNT,) or not np.all(np.isfinite(v)) for v in (even, odd)):
            raise ValueError("M/S receivers must be finite complex 20-vectors")
        if not isinstance(self.name, str) or not self.name:
            raise ValueError("name must be nonempty")
        object.__setattr__(self, "even_receiver", tuple(complex(v) for v in even))
        object.__setattr__(self, "odd_receiver", tuple(complex(v) for v in odd))

    def observe(
        self, frame: QMWFrame, audio: Any, excitation: V3ModalExcitationFrame
    ) -> StereoObservationFrame:
        if not isinstance(audio, AcousticFieldFrame):
            raise TypeError("the V3 M/S observer requires an AcousticFieldFrame")
        return observe_mid_side_stereo(
            audio,
            even_receiver=self.even_receiver,
            odd_receiver=self.odd_receiver,
            revision=audio.revision,
            receiver_label=self.name,
        )


@dataclass(frozen=True)
class SoundSpatialRuntimeConfig:
    """Declared V3 geometry-to-resonator policies for steps 17-19."""

    boundary: GeometryBoundaryConfig = dataclass_field(default_factory=GeometryBoundaryConfig)
    tuning: TuningGeometryConfig = dataclass_field(default_factory=TuningGeometryConfig)
    resonance: ModalResonanceConfig = dataclass_field(default_factory=ModalResonanceConfig)
    relational: RelationalSpectralConfig = dataclass_field(default_factory=RelationalSpectralConfig)
    acoustic: AcousticFieldConfig = dataclass_field(default_factory=AcousticFieldConfig)

    def __post_init__(self) -> None:
        expected = (
            (self.boundary, GeometryBoundaryConfig, "boundary"),
            (self.tuning, TuningGeometryConfig, "tuning"),
            (self.resonance, ModalResonanceConfig, "resonance"),
            (self.relational, RelationalSpectralConfig, "relational"),
            (self.acoustic, AcousticFieldConfig, "acoustic"),
        )
        for value, kind, name in expected:
            if not isinstance(value, kind):
                raise TypeError(f"{name} must be a {kind.__name__}")


class SoundSpatialRuntimeAdapter:
    """Attach downstream V3 excitation, acoustic, and stereo observations."""

    def __init__(
        self,
        *,
        excitation_provider: ModalExcitationProvider | None = None,
        renderer: SoundDescriptorRenderer | None = None,
        spatializer: SpatialDescriptorObserver | None = None,
        config: SoundSpatialRuntimeConfig | None = None,
    ) -> None:
        self.config = config or SoundSpatialRuntimeConfig()
        self.excitation_provider = excitation_provider
        self.renderer = (
            renderer
            if renderer is not None
            else V3AcousticDescriptorRenderer(self.config.acoustic)
        )
        self.spatializer = (
            spatializer
            if spatializer is not None
            else MidSideStereoDescriptorObserver()
        )
        if excitation_provider is not None:
            _component_name(excitation_provider, method="provide", role="excitation_provider")
        _component_name(self.renderer, method="render", role="renderer")
        _component_name(self.spatializer, method="observe", role="spatializer")

    @staticmethod
    def _unavailable(
        frame: QMWFrame, capability: str, reason: str
    ) -> SoundCapabilityUnavailable:
        source_revision = (
            frame.geometry.revision
            if isinstance(frame.geometry, RelationalGeometryFrame)
            else frame.revisions.geometry
        )
        return SoundCapabilityUnavailable(
            capability=capability,
            time=frame.time,
            source_revision=source_revision,
            reason=reason,
        )

    def generate_excitations(self, frame: QMWFrame) -> QMWFrame:
        geometry = frame.geometry
        reason: str | None = None
        if self.excitation_provider is None:
            reason = "no named modal excitation provider is configured"
        elif not isinstance(geometry, RelationalGeometryFrame):
            reason = "V3 excitation requires a RelationalGeometryFrame"
        elif not geometry.embedding_valid:
            reason = "V3 excitation requires a valid relational geometry embedding"

        diagnostics = dict(frame.diagnostics)
        if reason is not None:
            unavailable = self._unavailable(frame, "excitation", reason)
            diagnostics.update(
                {
                    "excitation_available": False,
                    "excitation_unavailable_reason": reason,
                    "sound_is_downstream_observer": True,
                }
            )
            return frame.with_updates(excitation=unavailable, diagnostics=diagnostics)

        assert isinstance(geometry, RelationalGeometryFrame)
        if not math.isclose(geometry.time, frame.time, rel_tol=0.0, abs_tol=1.0e-12):
            raise ValueError("QMWFrame and relational geometry times must match")
        boundary = observe_geometry_boundary(geometry, config=self.config.boundary)
        tuning = observe_tuning_geometry(geometry, config=self.config.tuning)
        relational = observe_relational_spectral_control(geometry, config=self.config.relational)
        resonance = observe_modal_resonance(
            tuning, config=self.config.resonance, relational_control=relational
        )
        provided = self.excitation_provider.provide(frame, resonance)
        if not isinstance(provided, tuple) or len(provided) != 2:
            raise TypeError(
                "excitation provider must return (PerformerEmphasisFrame, FlowExcitationFrame)"
            )
        performer, flow = provided
        excitation = V3ModalExcitationFrame(
            revision=geometry.revision,
            time=frame.time,
            geometry=geometry,
            boundary=boundary,
            tuning=tuning,
            resonance=resonance,
            relational_control=relational,
            performer=performer,
            flow=flow,
            provider_name=self.excitation_provider.name,
        )
        diagnostics.update(
            {
                "excitation_available": True,
                "excitation_provider": excitation.provider_name,
                "excitation_mode_count": MODE_COUNT,
                "excitation_is_quantum_evolution": False,
                "sound_is_downstream_observer": True,
            }
        )
        return frame.with_updates(excitation=excitation, diagnostics=diagnostics)

    def render_sound(self, frame: QMWFrame) -> QMWFrame:
        diagnostics = dict(frame.diagnostics)
        if isinstance(frame.excitation, SoundCapabilityUnavailable):
            reason = f"upstream excitation unavailable: {frame.excitation.reason}"
            unavailable = self._unavailable(frame, "audio", reason)
            diagnostics.update(
                {
                    "audio_available": False,
                    "audio_unavailable_reason": reason,
                    "audio_contains_pcm_samples": False,
                }
            )
            return frame.with_updates(
                audio=unavailable,
                revisions=replace(frame.revisions, audio=unavailable.source_revision),
                diagnostics=diagnostics,
            )
        if not isinstance(frame.excitation, V3ModalExcitationFrame):
            raise TypeError("step 18 requires V3ModalExcitationFrame from step 17")
        audio = self.renderer.render(frame, frame.excitation)
        if audio is None:
            raise TypeError("renderer must return a payload")
        if not math.isclose(
            float(getattr(audio, "time", frame.time)),
            frame.time,
            rel_tol=0.0,
            abs_tol=1.0e-12,
        ):
            raise ValueError("renderer payload time must match QMWFrame time")
        audio_revision = _revision(
            getattr(audio, "revision", frame.excitation.revision), name="audio revision"
        )
        diagnostics.update(
            {
                "audio_available": True,
                "audio_renderer": self.renderer.name,
                "audio_output_level": getattr(self.renderer, "output_level", "unspecified"),
                "audio_contains_pcm_samples": bool(
                    getattr(self.renderer, "produces_audio_buffer", False)
                ),
                "audio_is_quantum_evolution": False,
            }
        )
        return frame.with_updates(
            audio=audio,
            revisions=replace(frame.revisions, audio=audio_revision),
            diagnostics=diagnostics,
        )

    def spatialize(self, frame: QMWFrame) -> QMWFrame:
        diagnostics = dict(frame.diagnostics)
        if isinstance(frame.audio, SoundCapabilityUnavailable):
            reason = f"upstream audio unavailable: {frame.audio.reason}"
            unavailable = self._unavailable(frame, "spatial", reason)
            diagnostics.update(
                {"spatial_available": False, "spatial_unavailable_reason": reason}
            )
            return frame.with_updates(spatial=unavailable, diagnostics=diagnostics)
        if not isinstance(frame.excitation, V3ModalExcitationFrame):
            raise TypeError("step 19 requires V3ModalExcitationFrame from step 17")
        spatial = self.spatializer.observe(frame, frame.audio, frame.excitation)
        if spatial is None:
            raise TypeError("spatializer must return a payload")
        if not math.isclose(
            float(getattr(spatial, "time", frame.time)),
            frame.time,
            rel_tol=0.0,
            abs_tol=1.0e-12,
        ):
            raise ValueError("spatial payload time must match QMWFrame time")
        diagnostics.update(
            {
                "spatial_available": True,
                "spatializer": self.spatializer.name,
                "spatial_output_level": getattr(self.spatializer, "output_level", "unspecified"),
                "spatial_is_quantum_evolution": False,
                "spatial_delivery_enabled": False,
            }
        )
        return frame.with_updates(spatial=spatial, diagnostics=diagnostics)


def register_sound_spatial(
    scheduler: QMWRuntimeScheduler,
    *,
    excitation_provider: ModalExcitationProvider | None = None,
    renderer: SoundDescriptorRenderer | None = None,
    spatializer: SpatialDescriptorObserver | None = None,
    config: SoundSpatialRuntimeConfig | None = None,
) -> SoundSpatialRuntimeAdapter:
    """Register downstream sound observers at canonical steps 17-19."""

    if not isinstance(scheduler, QMWRuntimeScheduler):
        raise TypeError("scheduler must be a QMWRuntimeScheduler")
    adapter = SoundSpatialRuntimeAdapter(
        excitation_provider=excitation_provider,
        renderer=renderer,
        spatializer=spatializer,
        config=config,
    )
    scheduler.register(RuntimeStep.GENERATE_EXCITATIONS, adapter.generate_excitations)
    scheduler.register(RuntimeStep.RENDER_SOUND, adapter.render_sound)
    scheduler.register(RuntimeStep.SPATIALIZE, adapter.spatialize)
    return adapter


__all__ = [
    "FixedModalExcitationProvider",
    "MidSideStereoDescriptorObserver",
    "ModalExcitationProvider",
    "SoundCapabilityUnavailable",
    "SoundDescriptorRenderer",
    "SoundSpatialRuntimeAdapter",
    "SoundSpatialRuntimeConfig",
    "SpatialDescriptorObserver",
    "V3AcousticDescriptorRenderer",
    "V3ModalExcitationFrame",
    "register_sound_spatial",
]
