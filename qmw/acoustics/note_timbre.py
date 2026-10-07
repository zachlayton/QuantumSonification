"""Independent note/body adapters and an executable offline synthesis junction.

There is no authoritative state, live audio, OSC transport, or random admission
here. The transition network selects notes; a separately declared modal basis
observes rho to describe a body. They first meet at OfflineModalResonator.process.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from types import MappingProxyType
from typing import Mapping

import numpy as np

from qmw.core.transition import (
    FrameContext, TransitionFrame, QuantumUnits, positive, nonempty, readonly, validated_spectrum,
)


@dataclass(frozen=True)
class RatioField:
    """Positive pitch-class ratios with a declared repeating period.

    Ratios are not required to be equal-tempered, sorted, octave-repeating, or
    rational numbers. Degree zero refers to ratios[0]; negative degrees use
    mathematical floor division. ScalaScale.pitch_classes and .period can be
    passed explicitly by a future file/provenance adapter without a new parser.
    """
    ratios: tuple[float, ...]
    period: float = 2.
    reference_hz: float = 220.
    name: str = "explicit_ratio_field"

    def __post_init__(self):
        ratios = tuple(positive(x, "ratio") for x in self.ratios)
        if not ratios:
            raise ValueError("ratio field must be nonempty")
        positive(self.period, "period")
        positive(self.reference_hz, "reference_hz")
        nonempty(self.name, "ratio field name")
        object.__setattr__(self, "ratios", ratios)
        object.__setattr__(self, "period", float(self.period))
        object.__setattr__(self, "reference_hz", float(self.reference_hz))

    def ratio(self, degree: int) -> float:
        if isinstance(degree, bool) or not isinstance(degree, (int, np.integer)):
            raise ValueError("degree must be an integer")
        octave, index = divmod(int(degree), len(self.ratios))
        try:
            ratio = self.ratios[index] * float(self.period)**octave
        except OverflowError as exc:
            raise ValueError("degree exceeds finite ratio range") from exc
        return positive(ratio, "projected ratio")

    def frequency_hz(self, degree: int) -> float:
        return positive(self.reference_hz*self.ratio(degree), "projected Hz")


@dataclass(frozen=True)
class QuantumNoteEvent:
    """A musical event, not a quantum jump. No timbre/body parameters.

    phase_rad retains the gauge-dependent matrix-element argument as metadata.
    strength is the selected diagnostic activity in its declared units; it is
    not a probability per second. Identity is deterministic within the supplied
    frame identity, representation/gauge and exact projector configuration.
    """
    event_id: str
    source_state: int
    target_state: int
    source_degree: int
    target_degree: int
    source_ratio: float
    target_ratio: float
    source_frequency_hz: float
    target_frequency_hz: float
    strength: float
    phase_rad: float | None
    delta_E: float
    omega: float
    units: QuantumUnits
    activity_name: str
    activity_units: str
    onset_seconds: float
    duration_seconds: float
    context: FrameContext
    provenance: tuple[str, ...]

    def __post_init__(self):
        for name in ("source_ratio", "target_ratio", "source_frequency_hz", "target_frequency_hz", "duration_seconds"):
            positive(getattr(self, name), name)
        positive(self.strength, "strength", zero=True)
        for name in ("delta_E", "omega", "onset_seconds"):
            if not np.isfinite(getattr(self, name)):
                raise ValueError(f"{name} must be finite")
        if self.phase_rad is not None and not np.isfinite(self.phase_rad):
            raise ValueError("phase_rad must be finite or None")
        object.__setattr__(self, "provenance", tuple(self.provenance))


class TransitionPitchProjector:
    """Pure deterministic endpoint mapping and event admission, downstream of H.

    Select non-diagonal, nonzero-gap edges with activity > min_activity in
    (source,target) order; retain the first max_events when bounded. Strength
    equals activity. No stochastic clock, physical rate interpretation, state
    tracking, or implicit energy-gap-to-Hz mapping. The default min_activity
    is an absolute 1e-12 in the model's activity units, a configurable musical
    admission floor to suppress numerical leakage, not a physical selection rule.
    All state degrees must be
    provided for each instantaneous energy basis; degeneracy caveats propagate.
    """
    def __init__(self, *, state_degrees: tuple[int, ...], ratio_field: RatioField,
                 min_activity: float = 1e-12, max_events: int | None = None,
                 delay_seconds: float = 0., duration_seconds: float = .02):
        self.state_degrees = tuple(state_degrees)
        for degree in self.state_degrees:
            ratio_field.ratio(degree)
        self.ratio_field = ratio_field
        self.min_activity = positive(min_activity, "min_activity", zero=True)
        if max_events is not None and (isinstance(max_events, bool) or not isinstance(max_events, int) or max_events < 1):
            raise ValueError("max_events must be a positive integer or None")
        self.max_events = max_events
        self.delay_seconds = positive(delay_seconds, "delay_seconds", zero=True)
        self.duration_seconds = positive(duration_seconds, "duration_seconds")

    def process(self, frame: TransitionFrame) -> tuple[QuantumNoteEvent, ...]:
        if len(self.state_degrees) != frame.spectrum.dimension:
            raise ValueError("one explicit scale degree per energy state is required")
        if frame.context.time_unit != "s":
            raise ValueError("pitch timing requires source seconds; supply an explicit timing adapter otherwise")
        policy = json.dumps({"name":self.ratio_field.name, "ratios":self.ratio_field.ratios,
            "period":self.ratio_field.period, "reference_hz":self.ratio_field.reference_hz,
            "degrees":tuple(int(d) for d in self.state_degrees), "min_activity":self.min_activity,
            "max_events":self.max_events, "delay_seconds":self.delay_seconds,
            "duration_seconds":self.duration_seconds}, sort_keys=True, separators=(",", ":"), allow_nan=False)
        notes = []
        for edge in frame.edges:
            activity = edge.activity[frame.activity_name]
            if edge.diagonal or edge.zero_gap or activity <= self.min_activity:
                continue
            source_degree, target_degree = [int(self.state_degrees[j]) for j in (edge.source, edge.target)]
            identity = json.dumps(["qmw.note.v1",frame.context.source_id,int(frame.context.frame_id),
                frame.context.basis_id, float(frame.context.time),float(frame.context.dt),
                frame.provenance, policy, edge.source, edge.target, activity,
                edge.phase_rad, edge.delta_E, edge.omega, frame.activity_name,frame.activity_units,
                frame.units.hbar,frame.units.energy_unit,frame.units.time_unit,frame.units.operator_unit],
                separators=(",", ":"), allow_nan=False)
            notes.append(QuantumNoteEvent(
                "qmw.note.v1:"+hashlib.sha256(identity.encode()).hexdigest(),
                edge.source, edge.target, source_degree, target_degree,
                self.ratio_field.ratio(source_degree), self.ratio_field.ratio(target_degree),
                self.ratio_field.frequency_hz(source_degree), self.ratio_field.frequency_hz(target_degree),
                activity, edge.phase_rad, edge.delta_E, edge.omega,frame.units,
                frame.activity_name,frame.activity_units,
                frame.context.time+self.delay_seconds, self.duration_seconds,frame.context,
                frame.provenance+("qmw.transition_pitch.v1", "pitch_policy:"+policy,
                    "admission:strict_threshold_source_target_order; timing:source_seconds_plus_delay",
                    frame.label_convention, frame.phase_convention)))
            if self.max_events is not None and len(notes) >= self.max_events:
                break
        return tuple(notes)


@dataclass(frozen=True)
class GeometryModes:
    """Independently supplied orthonormal Hilbert modes, columns phi_j.

    This is an abstract Hilbert-space geometry adapter, not a physical surface
    or a claim that qubit coordinates are vertices. Euclidean orthonormal
    incomplete bases are supported. A different space, dimension or metric is
    rejected: physical geometry needs a named embedding/inner-product adapter.
    space_id must name the same coordinates as the density snapshot context.
    The caller must supply independent modes; no rho-dependent default exists.
    """
    hilbert_vectors: np.ndarray
    space_id: str
    geometry_id: str
    mode_ids: tuple[str, ...]
    frequencies_hz: np.ndarray
    quality_factors: np.ndarray
    acoustic_phases_rad: np.ndarray
    complete: bool = True
    inner_product: str = "euclidean_hilbert"
    provenance: tuple[str, ...] = ()

    def __post_init__(self):
        for name in ("space_id", "geometry_id"):
            nonempty(getattr(self, name), name)
        if self.inner_product != "euclidean_hilbert":
            raise ValueError("unsupported inner product: requires named embedding/metric adapter")
        if not isinstance(self.complete, bool):
            raise ValueError("complete must be explicitly boolean")
        ids = tuple(self.mode_ids)
        if not ids or len(set(ids)) != len(ids):
            raise ValueError("mode IDs must be nonempty and unique")
        for mode_id in ids:
            nonempty(mode_id, "mode ID")
        object.__setattr__(self, "mode_ids", ids)
        phi = readonly(self.hilbert_vectors, complex)
        if phi.ndim != 2 or phi.shape[1] != len(ids) or not np.all(np.isfinite(phi)):
            raise ValueError("hilbert_vectors must be finite with one column per mode ID")
        object.__setattr__(self, "hilbert_vectors", phi)
        for name in ("frequencies_hz", "quality_factors", "acoustic_phases_rad"):
            raw = np.asarray(getattr(self, name))
            if np.iscomplexobj(raw):
                raise ValueError(f"{name} must be real")
            array = readonly(raw, float)
            if array.shape != (len(ids),) or not np.all(np.isfinite(array)):
                raise ValueError(f"{name} must be a finite per-mode vector")
            if name != "acoustic_phases_rad" and np.any(array <= 0):
                raise ValueError(f"{name} must be positive")
            object.__setattr__(self, name, array)
        object.__setattr__(self, "provenance", tuple(self.provenance))


@dataclass(frozen=True)
class ModalResonatorFrame:
    """Independent body with separate spectra, mode probabilities and gains.

    f in Hz; Q dimensionless; tau=Q/(pi*f) is amplitude e-folding time. Acoustic
    phases come only from GeometryModes, never density/energy eigenvector gauge.
    complete_basis=False means weights sum to captured_weight, not necessarily 1.
    """
    context: FrameContext
    geometry_id: str
    space_id: str
    mode_ids: tuple[str, ...]
    frequencies_hz: np.ndarray
    quality_factors: np.ndarray
    decay_seconds: np.ndarray
    acoustic_phases_rad: np.ndarray
    modal_probability_weights: np.ndarray
    amplitude_gains: np.ndarray
    density_eigenvalues: np.ndarray
    density_eigenvectors: np.ndarray
    geometry_hilbert_vectors: np.ndarray
    density_geometry_overlap: np.ndarray
    complete_basis: bool
    captured_weight: float
    purity: float
    entropy_nats: float
    diagnostics: Mapping[str, object]
    provenance: tuple[str, ...]

    def __post_init__(self):
        # Public frame construction/replacement also preserves snapshot ownership.
        for name in ("frequencies_hz", "quality_factors", "decay_seconds", "acoustic_phases_rad",
                     "modal_probability_weights", "amplitude_gains", "density_eigenvalues",
                     "density_eigenvectors", "geometry_hilbert_vectors", "density_geometry_overlap"):
            object.__setattr__(self, name, readonly(getattr(self, name)))
        object.__setattr__(self, "diagnostics", MappingProxyType(dict(self.diagnostics)))
        object.__setattr__(self, "provenance", tuple(self.provenance))
        object.__setattr__(self, "mode_ids", tuple(self.mode_ids))
        count = len(self.mode_ids)
        if not count or len(set(self.mode_ids)) != count:
            raise ValueError("body mode IDs must be nonempty and unique")
        for name in ("space_id", "geometry_id"):
            nonempty(getattr(self,name),name)
        if self.space_id != self.context.basis_id:
            raise ValueError("body space must match the source coordinate basis")
        for name in ("frequencies_hz", "quality_factors", "decay_seconds", "acoustic_phases_rad", "amplitude_gains"):
            a = getattr(self,name)
            if a.shape != (count,) or np.iscomplexobj(a) or not np.all(np.isfinite(a)):
                raise ValueError(f"{name} must be a real finite vector with one entry per body mode")
            if name != "acoustic_phases_rad" and np.any(a < 0 if name == "amplitude_gains" else a <= 0):
                raise ValueError(f"invalid body {name}")
        if not np.allclose(self.decay_seconds,self.quality_factors/(np.pi*self.frequencies_hz),rtol=1e-12,atol=0):
            raise ValueError("body decay must be Q/(pi*f)")


class QuantumTimbreProjector:
    def __init__(self, *, tolerance: float = 1e-10):
        self.tolerance = positive(tolerance, "tolerance")

    def process(self, *, rho, geometry_modes: GeometryModes, context: FrameContext) -> ModalResonatorFrame:
        density = np.array(rho, dtype=complex, copy=True)
        if density.ndim != 2 or density.shape[0] != density.shape[1] or not density.size:
            raise ValueError("rho must be a nonempty square density matrix")
        g = geometry_modes
        n = density.shape[0]
        phi = g.hilbert_vectors
        if g.space_id != context.basis_id or phi.shape[0] != n:
            raise ValueError("geometry and rho require one declared Hilbert space; embedding adapter not implemented")
        j = phi.shape[1]
        if j > n or g.complete != (j == n):
            raise ValueError("complete requires n orthonormal columns; incomplete requires fewer than n")
        gram_error = float(np.linalg.norm(phi.conj().T @ phi-np.eye(j)))
        if gram_error > self.tolerance*max(1.,np.sqrt(j)):
            raise ValueError("geometry Hilbert modes must be orthonormal in the declared inner product")
        # Reuse the canonical density decomposition with an inert zero auxiliary
        # H. It has no physical or sonic meaning; discard every energy output.
        spectrum, diagnostics = validated_spectrum(density, np.zeros_like(density), self.tolerance, 0.)
        lam, psi = spectrum.density_eigenvalues, spectrum.density_eigenvectors
        overlap = phi.conj().T @ psi
        weights = np.abs(overlap)**2 @ lam
        expected = np.diag(phi.conj().T @ density @ phi).real
        captured = float(weights.sum())
        if np.min(weights) < -self.tolerance or captured < -self.tolerance or captured > 1+4*self.tolerance:
            raise ValueError("modal projection outside density tolerance")
        diagnostics = {k:v for k,v in diagnostics.items() if not k.startswith("hamiltonian") and k != "energy_gap_tolerance"}
        diagnostics.update({"geometry_gram_residual_fro":gram_error,
            "modal_expectation_residual_max":float(np.max(np.abs(weights-expected))),
            "captured_weight":captured, "uncaptured_weight":1-captured,
            "normalization":"raw projected weight; no renormalization for complete or incomplete basis",
            "amplitude_policy":"sqrt(max(modal_probability_weights,0)); probability is not amplitude",
            "density_decomposition":"canonical observer with zero auxiliary H, energy outputs discarded",
            "geometry_inner_product":g.inner_product,
            "acoustic_phase_source":"independent GeometryModes.acoustic_phases_rad"})
        return ModalResonatorFrame(context,g.geometry_id,g.space_id,g.mode_ids,
            g.frequencies_hz,g.quality_factors,g.quality_factors/(np.pi*g.frequencies_hz),
            g.acoustic_phases_rad,weights,np.sqrt(np.maximum(weights,0)),lam,psi,phi,overlap,
            g.complete,captured,spectrum.purity,spectrum.entropy,diagnostics,
            context.provenance+g.provenance+("qmw.core.quantum_spectrum.analyze_quantum_spectrum:density_only",
                "qmw.quantum_timbre.v1",f"geometry:{g.geometry_id};space:{g.space_id}",
                "modal_weight:sum_lambda_abs_phi_dagger_psi_squared"))


@dataclass(frozen=True)
class OfflineRenderResult:
    excitation: QuantumNoteEvent
    timbre: ModalResonatorFrame
    excitation_signal: np.ndarray
    impulse_response: np.ndarray
    audio: np.ndarray
    sample_rate: int
    start_seconds: float
    diagnostics: Mapping[str, object]
    provenance: tuple[str, ...]


class OfflineModalResonator:
    """Executable finite stereo convolution, using the existing modal renderer.

    x = strength * Hann-windowed sine(target Hz), fixed acoustic phase zero.
    h = existing centered damped modal sine bank, independent of the note.
    y = x*h, truncated to the requested buffer. Body poles remain fixed: the
    note controls excitation pitch, not a promise of a single output fundamental.
    No gain normalization/limiter is hidden here. Buffers start at context.time;
    onset rounds to the nearest sample. No continuous-tail/live scheduling state.
    """
    def __init__(self, *, sample_rate: int = 24000, duration_seconds: float = .1):
        if isinstance(sample_rate, bool) or not isinstance(sample_rate, int) or sample_rate < 2:
            raise ValueError("sample_rate must be an integer >= 2")
        self.sample_rate = sample_rate
        self.duration_seconds = positive(duration_seconds, "duration_seconds")
        self.sample_count = round(self.duration_seconds*sample_rate)
        if self.sample_count < 2:
            raise ValueError("render requires at least two samples")

    def process(self, *, excitation: QuantumNoteEvent, timbre: ModalResonatorFrame) -> OfflineRenderResult:
        from density import density_matrix_modal_renderer_v2 as existing

        if excitation.context != timbre.context or excitation.context.time_unit != "s":
            raise ValueError("junction requires the same explicit frame context in seconds")
        sr, count = self.sample_rate, self.sample_count
        if excitation.target_frequency_hz >= sr/2 or np.any(timbre.frequencies_hz >= sr/2):
            raise ValueError("excitation and modal frequencies must lie below Nyquist")
        mode_count = len(timbre.mode_ids)
        for name in ("frequencies_hz", "quality_factors", "decay_seconds", "acoustic_phases_rad", "amplitude_gains"):
            a = getattr(timbre,name)
            if a.shape != (mode_count,) or not np.all(np.isfinite(a)) or np.iscomplexobj(a):
                raise ValueError(f"invalid render body {name}")
            if name != "acoustic_phases_rad" and np.any(a < 0 if name == "amplitude_gains" else a <= 0):
                raise ValueError(f"invalid render body {name}")
        if not np.allclose(timbre.decay_seconds,timbre.quality_factors/(np.pi*timbre.frequencies_hz),rtol=1e-12,atol=0):
            raise ValueError("decay must be Q/(pi*f)")
        onset = round((excitation.onset_seconds-excitation.context.time)*sr)
        burst_count = round(excitation.duration_seconds*sr)
        if onset < 0 or onset >= count or burst_count < 3 or onset+burst_count > count:
            raise ValueError("entire excitation burst must fit render window and contain at least three samples")
        signal = np.zeros(count)
        t = np.arange(burst_count)/sr
        signal[onset:onset+burst_count] = excitation.strength*np.hanning(burst_count)*np.sin(2*np.pi*excitation.target_frequency_hz*t)
        # A two-sample [1,0] impulse avoids both the legacy continuous-excitation
        # shortcut and its zero-excitation free-ring fallback. The separate
        # legacy `phases` parameter is unused; initial oscillator phase is here.
        ir, _ = existing.render_modal_frame(timbre.frequencies_hz,timbre.amplitude_gains,
            timbre.decay_seconds,np.zeros(mode_count),np.zeros(mode_count),
            timbre.acoustic_phases_rad,count,sr,0.,np.array([1.,0.]))
        fft_size = 1 << (2*count-2).bit_length()
        audio = np.fft.irfft(np.fft.rfft(signal, n=fft_size)[:,None] *
                            np.fft.rfft(ir,n=fft_size,axis=0), n=fft_size,axis=0)[:count]
        if not np.all(np.isfinite(audio)):
            raise ValueError("render overflow: adjust explicit excitation/body levels")
        diagnostics = MappingProxyType({"renderer":"density.density_matrix_modal_renderer_v2.render_modal_frame + FFT convolution",
            "sample_count":count, "peak_abs":float(np.max(np.abs(audio))),
            "onset_sample":onset,"onset_quantization_error_seconds":onset/sr-(excitation.onset_seconds-excitation.context.time),
            "excitation_duration_samples":burst_count,
            "excitation_phase":"fixed zero; matrix-element phase retained as metadata only",
            "tail_policy":"truncate convolution at buffer end; no automatic tail fade or normalization",
            "pitch_policy":"target Hz in excitation only; body poles unchanged"})
        return OfflineRenderResult(excitation,timbre,readonly(signal),readonly(ir),readonly(audio),sr,
            excitation.context.time,diagnostics,excitation.provenance+timbre.provenance+
            ("qmw.offline_modal_junction.v1",diagnostics["renderer"]))
