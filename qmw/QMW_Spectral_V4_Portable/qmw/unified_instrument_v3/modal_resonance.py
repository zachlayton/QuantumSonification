"""Read-only resonant-body observer for the V3 geometry-derived tuning frame."""

from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np

from .frames import (
    MODE_COUNT,
    QUBIT_COUNT,
    ModalResonanceFrame,
    RelationalSpectralControlFrame,
    TuningGeometryFrame,
)


_SUBMODES_PER_GRAPH_MODE = MODE_COUNT // QUBIT_COUNT


@dataclass(frozen=True)
class ModalResonanceConfig:
    """Declared resonant-body policy downstream of the geometry tuning.

    ``quality_tilt`` applies a bounded linear tilt across the ordered modal
    spectrum.  The decay convention is explicitly amplitude e-folding time,
    ``tau = Q / (pi * f)``.  It is a resonator-model descriptor, not a change
    to quantum evolution or a feedback route.
    """

    base_quality_factor: float = 900.0
    quality_tilt: float = 0.35
    phase_convention: str = "positive_complex_modal_rotation_exp_plus_i_phi"

    def __post_init__(self) -> None:
        if not math.isfinite(float(self.base_quality_factor)) or self.base_quality_factor <= 0.0:
            raise ValueError("base_quality_factor must be finite and positive.")
        if not math.isfinite(float(self.quality_tilt)) or not -0.95 <= self.quality_tilt <= 0.95:
            raise ValueError("quality_tilt must lie in [-0.95, 0.95].")
        if not str(self.phase_convention):
            raise ValueError("phase_convention must be nonempty.")


def modal_shape_membership() -> np.ndarray:
    """Return the declared 4x5 graph-mode/submode membership descriptor."""

    membership = np.zeros((MODE_COUNT, QUBIT_COUNT), dtype=float)
    membership[np.arange(MODE_COUNT), np.arange(MODE_COUNT) // _SUBMODES_PER_GRAPH_MODE] = 1.0
    membership.flags.writeable = False
    return membership


def observe_modal_resonance(
    tuning: TuningGeometryFrame,
    *,
    config: ModalResonanceConfig | None = None,
    relational_control: RelationalSpectralControlFrame | None = None,
    revision: int | None = None,
) -> ModalResonanceFrame:
    """Observe resonator descriptors using the tuning frame's exact Hz array."""

    if not isinstance(tuning, TuningGeometryFrame):
        raise TypeError("tuning must be a TuningGeometryFrame.")
    cfg = config or ModalResonanceConfig()
    frequency = np.asarray(tuning.frequency_hz, dtype=float)
    if frequency.shape != (MODE_COUNT,) or not np.all(np.isfinite(frequency)) or np.any(frequency <= 0.0):
        raise ValueError("tuning must provide a positive finite 20-mode frequency array.")
    logarithmic_position = np.linspace(-1.0, 1.0, MODE_COUNT)
    quality = float(cfg.base_quality_factor) * (1.0 + (float(cfg.quality_tilt) * logarithmic_position))
    relational_diagnostics: tuple[str, ...] = ()
    if relational_control is not None:
        if not isinstance(relational_control, RelationalSpectralControlFrame):
            raise TypeError("relational_control must be a RelationalSpectralControlFrame.")
        if relational_control.mode_ids != tuning.mode_ids:
            raise ValueError("relational control must use the tuning mode ordering.")
        if not math.isclose(relational_control.time, tuning.time, abs_tol=1.0e-12, rel_tol=0.0):
            raise ValueError("relational control and tuning must have the same observation time.")
        if relational_control.geometry_revision != tuning.geometry_revision:
            raise ValueError("relational control must derive from the tuning geometry revision.")
        quality = quality * relational_control.decay_scale
        relational_diagnostics = (
            "quality and amplitude e-folding decay are shaped by the read-only relational Laplacian control",
        )
    decay = quality / (np.pi * frequency)
    diagnostics = (
        "quality factor and amplitude e-folding decay are resonant-body descriptors downstream of tuning",
        "IR peak frequencies are exactly the ModalResonanceFrame frequency_hz array",
    ) + relational_diagnostics
    return ModalResonanceFrame(
        revision=tuning.revision if revision is None else revision,
        time=tuning.time,
        tuning_revision=tuning.revision,
        mode_ids=tuning.mode_ids,
        frequency_hz=frequency,
        quality_factor=quality,
        decay_seconds=decay,
        phase_convention=str(cfg.phase_convention),
        ir_peak_hz=frequency,
        mode_shape_weights=modal_shape_membership(),
        mode_shape_label="v3_graph_eigenmode_membership_4x5_subcell_descriptor",
        diagnostics=diagnostics,
    )


__all__ = ["ModalResonanceConfig", "modal_shape_membership", "observe_modal_resonance"]
