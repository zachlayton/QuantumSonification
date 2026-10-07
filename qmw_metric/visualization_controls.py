"""Read-only view controls for analysis and performance visualization."""

from __future__ import annotations

from dataclasses import dataclass, replace
from types import MappingProxyType
from typing import Literal, Mapping

import numpy as np

VisualizationMode = Literal["analysis", "performance"]

OVERLAY_IDS = (
    "density",
    "potential",
    "contours",
    "spatial_metric",
    "lapse",
    "curvature",
    "hessian_principal",
    "probability_current",
    "vorticity",
    "eigenmodes",
    "trajectory",
)


@dataclass(frozen=True)
class OverlayControl:
    """One independent display layer; it never changes the physics frame."""

    enabled: bool = False
    opacity: float = 1.0
    gain: float = 1.0

    def __post_init__(self) -> None:
        if not 0.0 <= self.opacity <= 1.0:
            raise ValueError("overlay opacity must be in [0, 1]")
        if not np.isfinite(self.gain) or self.gain < 0.0:
            raise ValueError("overlay gain must be finite and nonnegative")


@dataclass(frozen=True)
class VisualizationControls:
    """Immutable preset plus independently addressable overlay state."""

    mode: VisualizationMode
    overlays: Mapping[str, OverlayControl]
    selected_mode_index: int = 0
    contour_count: int = 12
    vector_stride: int = 4
    trajectory_length: int = 256
    height_scale: float = 0.72

    def __post_init__(self) -> None:
        if self.mode not in ("analysis", "performance"):
            raise ValueError("visualization mode must be analysis or performance")
        if tuple(self.overlays) != OVERLAY_IDS:
            raise ValueError("overlays must contain the canonical ordered inventory")
        if self.selected_mode_index < 0:
            raise ValueError("selected_mode_index must be nonnegative")
        if self.contour_count < 2 or self.vector_stride < 1 or self.trajectory_length < 1:
            raise ValueError("visualization sampling controls are out of range")
        if not np.isfinite(self.height_scale) or self.height_scale < 0.0:
            raise ValueError("height_scale must be finite and nonnegative")
        object.__setattr__(self, "overlays", MappingProxyType(dict(self.overlays)))

    def with_overlay(
        self,
        overlay_id: str,
        *,
        enabled: bool | None = None,
        opacity: float | None = None,
        gain: float | None = None,
    ) -> "VisualizationControls":
        if overlay_id not in self.overlays:
            raise KeyError(f"unknown visualization overlay {overlay_id!r}")
        prior = self.overlays[overlay_id]
        updated = replace(
            prior,
            enabled=prior.enabled if enabled is None else enabled,
            opacity=prior.opacity if opacity is None else opacity,
            gain=prior.gain if gain is None else gain,
        )
        overlays = dict(self.overlays)
        overlays[overlay_id] = updated
        return replace(self, overlays=overlays)


def _preset(mode: VisualizationMode, enabled: set[str]) -> VisualizationControls:
    overlays = {
        name: OverlayControl(enabled=name in enabled, opacity=0.78, gain=1.0)
        for name in OVERLAY_IDS
    }
    return VisualizationControls(mode=mode, overlays=overlays)


def analysis_visualization_controls() -> VisualizationControls:
    """Legible diagnostic preset; all layers remain independently available."""
    return _preset(
        "analysis",
        {"density", "potential", "contours", "spatial_metric", "trajectory"},
    )


def performance_visualization_controls() -> VisualizationControls:
    """Reduced visual preset with motion-bearing layers emphasized."""
    return replace(
        _preset(
            "performance",
            {"potential", "contours", "probability_current", "eigenmodes", "trajectory"},
        ),
        contour_count=8,
        vector_stride=6,
        height_scale=1.0,
    )
