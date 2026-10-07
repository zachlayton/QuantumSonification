"""Explicit bridge from a material phonon frame to the existing modal body.

The mechanics layer reports angular frequencies in its own source time unit.
This adapter requires a declared conversion to acoustic hertz and declared
quality factors. It identifies lattice coordinates with a named Hilbert-space
coordinate basis only when the caller explicitly gives the same ``space_id``
used by the quantum frame context.
"""

from __future__ import annotations

from typing import Sequence

import numpy as np

from qmw.acoustics.note_timbre import (
    GeometryModes,
    ModalResonatorFrame,
    QuantumTimbreProjector,
)
from qmw.core.phonon import PhononFrame
from qmw.core.transition import FrameContext


class PhononModalAdapter:
    """Adapt phonon normal modes into ``GeometryModes`` and a resonator body.

    ``angular_frequency_to_hz`` is an explicit scale with units
    acoustic-Hz/source-angular-frequency-unit. For a source already measured
    in rad/s, use ``1 / (2*pi)`` for literal frequency; larger values are an
    authored sonification transposition. Free translation modes are excluded
    by default because the existing resonator contract requires positive Hz.
    """

    def __init__(
        self,
        *,
        angular_frequency_to_hz: float,
        quality_factors: object,
        exclude_zero_modes: bool = True,
        zero_tolerance: float = 1.0e-10,
        projector_tolerance: float = 1.0e-10,
    ) -> None:
        scale = float(angular_frequency_to_hz)
        if not np.isfinite(scale) or scale <= 0.0:
            raise ValueError("angular_frequency_to_hz must be finite and positive")
        if not isinstance(exclude_zero_modes, bool):
            raise ValueError("exclude_zero_modes must be boolean")
        zero = float(zero_tolerance)
        if not np.isfinite(zero) or zero < 0.0:
            raise ValueError("zero_tolerance must be finite and nonnegative")
        projector = float(projector_tolerance)
        if not np.isfinite(projector) or projector <= 0.0:
            raise ValueError("projector_tolerance must be finite and positive")
        raw_q = np.asarray(quality_factors)
        if np.iscomplexobj(raw_q):
            raise ValueError("quality_factors must be real")
        q = np.array(raw_q, dtype=np.float64, copy=True)
        if q.ndim > 1 or not np.all(np.isfinite(q)) or np.any(q <= 0.0):
            raise ValueError("quality_factors must be a positive scalar or vector")
        self.angular_frequency_to_hz = scale
        self.quality_factors = q
        self.exclude_zero_modes = exclude_zero_modes
        self.zero_tolerance = zero
        self.projector_tolerance = projector

    def _selected_indices(self, frame: PhononFrame) -> np.ndarray:
        if not isinstance(frame, PhononFrame):
            raise TypeError("adapter requires an actual PhononFrame")
        if self.exclude_zero_modes:
            selected = np.flatnonzero(frame.frequencies > self.zero_tolerance)
        else:
            selected = np.arange(len(frame.frequencies))
        if not len(selected):
            raise ValueError("no positive phonon modes are available for the acoustic body")
        if np.any(frame.frequencies[selected] <= 0.0):
            raise ValueError(
                "the modal resonator requires positive Hz; exclude zero modes or add physical pinning"
            )
        return selected

    def _quality_values(self, frame: PhononFrame, selected: np.ndarray) -> np.ndarray:
        if self.quality_factors.ndim == 0:
            return np.full(len(selected), float(self.quality_factors))
        values = self.quality_factors.reshape(-1)
        if values.shape == (len(frame.frequencies),):
            return values[selected]
        if values.shape == (len(selected),):
            return values.copy()
        raise ValueError(
            "quality_factors must be scalar, one value per phonon mode, or one per selected mode"
        )

    def geometry_modes(
        self,
        frame: PhononFrame,
        *,
        space_id: str,
        geometry_id: str,
        mode_ids: Sequence[str] | None = None,
        acoustic_phases_rad: object | None = None,
        provenance: Sequence[str] = (),
    ) -> GeometryModes:
        """Create the existing independent geometry contract from a frame."""

        selected = self._selected_indices(frame)
        if mode_ids is None:
            ids = tuple(f"phonon-mode-{index}" for index in selected)
        else:
            ids = tuple(mode_ids)
            if len(ids) != len(selected):
                raise ValueError("mode_ids must contain one ID per selected phonon mode")
        phases = (
            frame.modal_phases[selected]
            if acoustic_phases_rad is None
            else np.asarray(acoustic_phases_rad)
        )
        if phases.shape != (len(selected),):
            raise ValueError("acoustic_phases_rad must contain one value per selected phonon mode")
        return GeometryModes(
            hilbert_vectors=frame.mode_shapes[:, selected].astype(np.complex128),
            space_id=space_id,
            geometry_id=geometry_id,
            mode_ids=ids,
            frequencies_hz=self.angular_frequency_to_hz * frame.frequencies[selected],
            quality_factors=self._quality_values(frame, selected),
            acoustic_phases_rad=phases,
            complete=len(selected) == len(frame.frequencies),
            inner_product="euclidean_hilbert",
            provenance=frame.provenance
            + tuple(provenance)
            + (
                "qmw.phonon_modal_adapter.v1",
                f"angular_frequency_to_hz:{self.angular_frequency_to_hz:.17g}",
                "coordinate_identification:phonon_sites_to_declared_hilbert_space",
            ),
        )

    def project(
        self,
        frame: PhononFrame,
        *,
        rho: object,
        context: FrameContext,
        geometry_id: str,
        space_id: str | None = None,
        mode_ids: Sequence[str] | None = None,
        acoustic_phases_rad: object | None = None,
        provenance: Sequence[str] = (),
    ) -> ModalResonatorFrame:
        """Reach ``ModalResonatorFrame`` through ``QuantumTimbreProjector``."""

        declared_space = context.basis_id if space_id is None else space_id
        if declared_space != context.basis_id:
            raise ValueError(
                "phonon geometry space must equal the quantum frame context basis; "
                "a different embedding requires its own named adapter"
            )
        geometry = self.geometry_modes(
            frame,
            space_id=declared_space,
            geometry_id=geometry_id,
            mode_ids=mode_ids,
            acoustic_phases_rad=acoustic_phases_rad,
            provenance=provenance,
        )
        return QuantumTimbreProjector(tolerance=self.projector_tolerance).process(
            rho=rho,
            geometry_modes=geometry,
            context=context,
        )


__all__ = ["PhononModalAdapter"]
