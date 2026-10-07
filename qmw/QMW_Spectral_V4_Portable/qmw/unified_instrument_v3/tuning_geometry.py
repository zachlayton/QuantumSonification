"""Explicit geometry-spectrum lifting operator for V3's 20 modal identities."""

from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np

from .frames import DEFAULT_MODE_IDS, MODE_COUNT, RelationalGeometryFrame, TuningGeometryFrame


_GRAPH_MODE_COUNT = 4
_SUBMODES_PER_GRAPH_MODE = MODE_COUNT // _GRAPH_MODE_COUNT


@dataclass(frozen=True)
class TuningGeometryConfig:
    """Declared finite lift from four graph eigenvalues to twenty mode ratios.

    Each graph eigenvalue owns five stable V3 mode IDs.  The graph factor is
    bounded in ``[1, 1 + eigenvalue_spread]`` after normalization by the
    current graph spectral span; a fixed log-spaced subcell supplies five
    intra-band relations.  This is a named modal expansion policy, not an
    assertion that the four-node graph has twenty eigenvectors.
    """

    reference_hz: float = 220.0
    eigenvalue_spread: float = 1.0
    submode_octave_span: float = 0.8
    spectral_floor: float = 1.0e-10
    mode_ids: tuple[str, ...] = DEFAULT_MODE_IDS
    equilibrium_label: str | None = None
    equilibrium_ratios: tuple[float, ...] | None = None
    equilibrium_blend: float = 0.0

    def __post_init__(self) -> None:
        values = (float(self.reference_hz), float(self.eigenvalue_spread), float(self.submode_octave_span), float(self.spectral_floor), float(self.equilibrium_blend))
        if not all(math.isfinite(value) for value in values):
            raise ValueError("tuning configuration values must be finite.")
        if values[0] <= 0.0 or values[1] < 0.0 or values[2] < 0.0 or values[3] <= 0.0 or not 0.0 <= values[4] <= 1.0:
            raise ValueError("reference_hz/floor must be positive; spreads nonnegative; blend in [0, 1].")
        if len(self.mode_ids) != MODE_COUNT or len(set(self.mode_ids)) != MODE_COUNT or any(not str(item) for item in self.mode_ids):
            raise ValueError("mode_ids must contain 20 unique nonempty stable identifiers.")
        if self.equilibrium_label is None:
            if self.equilibrium_ratios is not None or values[4] != 0.0:
                raise ValueError("equilibrium label, ratios, and blend must be declared together.")
        else:
            ratios = np.asarray(self.equilibrium_ratios, dtype=float)
            if ratios.shape != (MODE_COUNT,) or not np.all(np.isfinite(ratios)) or np.any(ratios <= 0.0):
                raise ValueError("equilibrium_ratios must be a positive finite 20-vector.")


def lift_geometry_spectrum(geometry: RelationalGeometryFrame, config: TuningGeometryConfig) -> np.ndarray:
    """Return ordered 20 geometry ratios before an optional equilibrium blend."""

    if not isinstance(geometry, RelationalGeometryFrame):
        raise TypeError("geometry must be a RelationalGeometryFrame.")
    if not geometry.embedding_valid:
        raise ValueError("TuningGeometryFrame requires valid relational geometry.")
    eigenvalues = np.asarray(geometry.eigenvalues, dtype=float)
    if eigenvalues.shape != (_GRAPH_MODE_COUNT,) or not np.all(np.isfinite(eigenvalues)) or np.any(eigenvalues < -config.spectral_floor):
        raise ValueError("geometry must provide four nonnegative finite graph eigenvalues.")
    shifted = np.maximum(eigenvalues - eigenvalues[0], 0.0)
    span = max(float(shifted[-1]), float(config.spectral_floor))
    graph_factors = 1.0 + (float(config.eigenvalue_spread) * (shifted / span))
    subcell = np.exp2((float(config.submode_octave_span) * np.arange(_SUBMODES_PER_GRAPH_MODE)) / _SUBMODES_PER_GRAPH_MODE)
    ratios = (graph_factors[:, None] * subcell[None, :]).reshape(MODE_COUNT)
    ratios /= ratios[0]
    ratios.flags.writeable = False
    return ratios


def observe_tuning_geometry(
    geometry: RelationalGeometryFrame,
    *,
    config: TuningGeometryConfig | None = None,
    revision: int | None = None,
) -> TuningGeometryFrame:
    """Observe one immutable V3 tuning frame from verified graph eigenvalues."""

    cfg = config or TuningGeometryConfig()
    geometry_ratios = lift_geometry_spectrum(geometry, cfg)
    equilibrium = None if cfg.equilibrium_ratios is None else np.asarray(cfg.equilibrium_ratios, dtype=float)
    ratios = geometry_ratios if equilibrium is None else np.exp(
        ((1.0 - float(cfg.equilibrium_blend)) * np.log(geometry_ratios))
        + (float(cfg.equilibrium_blend) * np.log(equilibrium))
    )
    diagnostics = (
        "four graph eigenvalues lifted through five fixed submodes each; this is a declared 4x5 modal expansion",
        "geometry spectrum is dimensionless until this named downstream frequency conversion",
    )
    return TuningGeometryFrame(
        revision=geometry.revision if revision is None else revision,
        time=geometry.time,
        geometry_revision=geometry.revision,
        mode_ids=tuple(cfg.mode_ids),
        ratios=ratios,
        frequency_hz=float(cfg.reference_hz) * ratios,
        reference_hz=float(cfg.reference_hz),
        geometry_eigenvalues=geometry.eigenvalues,
        geometry_ratios=geometry_ratios,
        equilibrium_label=cfg.equilibrium_label,
        equilibrium_blend=float(cfg.equilibrium_blend),
        equilibrium_ratios=equilibrium,
        spectrum_lift_label="v3_bounded_graph_eigenvalue_4x5_log_subcell_lift",
        diagnostics=diagnostics,
    )


__all__ = ["TuningGeometryConfig", "lift_geometry_spectrum", "observe_tuning_geometry"]
