"""Synchronized 20-mode complex-field observer for QMW Unified Instrument V3."""

from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np

from .frames import (
    AcousticFieldFrame,
    MODE_COUNT,
    ModalResonanceFrame,
    RelationalSpectralControlFrame,
)


def _readonly(values: object, *, dtype: object) -> np.ndarray:
    result = np.array(values, dtype=dtype, copy=True)
    result.setflags(write=False)
    return result


def _revision(value: int, *, name: str) -> int:
    if int(value) != value or value < 0:
        raise ValueError(f"{name} must be a nonnegative integer.")
    return int(value)


def _time(value: float) -> float:
    result = float(value)
    if not math.isfinite(result):
        raise ValueError("time must be finite.")
    return result


def _mode_ids(values: tuple[str, ...]) -> tuple[str, ...]:
    if len(values) != MODE_COUNT or len(set(values)) != MODE_COUNT or any(not str(item) for item in values):
        raise ValueError("mode_ids must be 20 unique nonempty stable identifiers.")
    return tuple(str(item) for item in values)


@dataclass(frozen=True)
class PerformerEmphasisFrame:
    """One immutable creative snapshot of the performer's 20 modal gains.

    It is a control frame, not quantum evolution and not an audio channel map.
    """

    revision: int
    time: float
    mode_ids: tuple[str, ...]
    gain: np.ndarray
    provenance: str = "creative_performer_modal_emphasis_v3"

    def __post_init__(self) -> None:
        object.__setattr__(self, "revision", _revision(self.revision, name="revision"))
        object.__setattr__(self, "time", _time(self.time))
        object.__setattr__(self, "mode_ids", _mode_ids(self.mode_ids))
        gain = _readonly(self.gain, dtype=float)
        if gain.shape != (MODE_COUNT,) or not np.all(np.isfinite(gain)) or np.any(gain < 0.0):
            raise ValueError("gain must be a finite nonnegative 20-vector.")
        if not isinstance(self.provenance, str) or not self.provenance:
            raise ValueError("provenance must be a nonempty string.")
        object.__setattr__(self, "gain", gain)


@dataclass(frozen=True)
class FlowExcitationFrame:
    """One immutable read-only 20-mode complex flow-excitation descriptor.

    The upstream flow observer must create this descriptor.  This frame does
    not relabel a Hilbert-basis current as physical spatial flux.
    """

    revision: int
    time: float
    mode_ids: tuple[str, ...]
    modal_excitation: np.ndarray
    provenance: str = "derived_read_only_flow_excitation_descriptor_v3"

    def __post_init__(self) -> None:
        object.__setattr__(self, "revision", _revision(self.revision, name="revision"))
        object.__setattr__(self, "time", _time(self.time))
        object.__setattr__(self, "mode_ids", _mode_ids(self.mode_ids))
        excitation = _readonly(self.modal_excitation, dtype=np.complex128)
        if excitation.shape != (MODE_COUNT,) or not np.all(np.isfinite(excitation)):
            raise ValueError("modal_excitation must be a finite complex 20-vector.")
        if not isinstance(self.provenance, str) or not self.provenance:
            raise ValueError("provenance must be a nonempty string.")
        object.__setattr__(self, "modal_excitation", excitation)


@dataclass(frozen=True)
class AcousticFieldConfig:
    """Declared complex-field combination policy.

    With the V3 positive-phase convention, the field coefficient is
    ``a_n = g_n exp(i 2 pi f_n (t - t0)) + flow_mix * xi_n``.  Performer gain
    and flow excitation retain distinct provenance in the output frame.
    """

    flow_mix: float = 1.0
    phase_reference_time: float = 0.0
    field_basis_label: str = "v3_modal_field_over_declared_geometry_boundary_basis"

    def __post_init__(self) -> None:
        if not math.isfinite(float(self.flow_mix)) or self.flow_mix < 0.0:
            raise ValueError("flow_mix must be finite and nonnegative.")
        if not math.isfinite(float(self.phase_reference_time)):
            raise ValueError("phase_reference_time must be finite.")
        if not str(self.field_basis_label):
            raise ValueError("field_basis_label must be nonempty.")


def observe_acoustic_field(
    resonance: ModalResonanceFrame,
    performer: PerformerEmphasisFrame,
    flow: FlowExcitationFrame,
    *,
    config: AcousticFieldConfig | None = None,
    relational_control: RelationalSpectralControlFrame | None = None,
    revision: int | None = None,
) -> AcousticFieldFrame:
    """Combine synchronized resonant, performer, and flow snapshots read-only."""

    if not isinstance(resonance, ModalResonanceFrame):
        raise TypeError("resonance must be a ModalResonanceFrame.")
    if not isinstance(performer, PerformerEmphasisFrame):
        raise TypeError("performer must be a PerformerEmphasisFrame.")
    if not isinstance(flow, FlowExcitationFrame):
        raise TypeError("flow must be a FlowExcitationFrame.")
    if resonance.mode_ids != performer.mode_ids or resonance.mode_ids != flow.mode_ids:
        raise ValueError("resonance, performer, and flow must share the same stable mode ordering.")
    if not (math.isclose(resonance.time, performer.time, abs_tol=1.0e-12, rel_tol=0.0) and math.isclose(resonance.time, flow.time, abs_tol=1.0e-12, rel_tol=0.0)):
        raise ValueError("resonance, performer, and flow must have the same observation time.")
    cfg = config or AcousticFieldConfig()
    relational_gain = np.ones(MODE_COUNT, dtype=float)
    relational_revision = None
    relational_label = ""
    if relational_control is not None:
        if not isinstance(relational_control, RelationalSpectralControlFrame):
            raise TypeError("relational_control must be a RelationalSpectralControlFrame.")
        if relational_control.mode_ids != resonance.mode_ids:
            raise ValueError("relational control must use the resonance mode ordering.")
        if not math.isclose(relational_control.time, resonance.time, abs_tol=1.0e-12, rel_tol=0.0):
            raise ValueError("relational control and resonance must have the same observation time.")
        relational_gain = relational_control.excitation_gain
        relational_revision = relational_control.revision
        relational_label = " plus read-only relational Laplacian excitation shaping"
    phase = 2.0 * np.pi * resonance.frequency_hz * (resonance.time - float(cfg.phase_reference_time))
    carrier = performer.gain * np.exp(1j * phase)
    flow_contribution = float(cfg.flow_mix) * flow.modal_excitation
    coefficients = (carrier + flow_contribution) * relational_gain
    diagnostics = (
        "modal coefficients equal performer carrier plus declared read-only flow excitation" + relational_label,
        "the 20 coefficients describe one field and are not output channels",
    )
    return AcousticFieldFrame(
        revision=resonance.revision if revision is None else revision,
        time=resonance.time,
        resonance_revision=resonance.revision,
        mode_ids=resonance.mode_ids,
        modal_coefficients=coefficients,
        performer_gain=performer.gain,
        flow_excitation=flow_contribution * relational_gain,
        field_basis_label=str(cfg.field_basis_label),
        performer_revision=performer.revision,
        flow_revision=flow.revision,
        relational_control_revision=relational_revision,
        relational_excitation_gain=relational_gain if relational_revision is not None else None,
        combination_label="v3_performer_carrier_plus_read_only_flow_excitation" + relational_label,
        diagnostics=diagnostics,
    )


__all__ = [
    "AcousticFieldConfig", "FlowExcitationFrame", "PerformerEmphasisFrame",
    "observe_acoustic_field",
]
