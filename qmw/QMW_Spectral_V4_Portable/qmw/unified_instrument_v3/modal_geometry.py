"""Unified Instrument facade for the canonical 20-mode modal geometry engine.

The implementation lives in :mod:`engine.qmw_modal_frame` so the same
auditable frame can later feed the density-derived ``rho -> W`` observer,
WebGL/Processing viewer, and SuperCollider adapter without competing maths.
"""

from __future__ import annotations

from typing import Iterable

import numpy as np

from engine.qmw_graph_geometry import canonical_dodecahedral_graph
from engine.qmw_modal_frame import ModalGeometryConfig, ModalGeometryFrame, StaticModalGeometryEngine
from wilson_quantum_geometry_v1.scala import ScalaScale


def canonical_dodecahedral_topology() -> tuple[np.ndarray, tuple[tuple[int, int], ...]]:
    """Compatibility view of the shared 20 sites and the 30 unit-weight edges."""

    coordinates, adjacency, _, _ = canonical_dodecahedral_graph()
    edges = tuple(map(tuple, np.argwhere(np.triu(adjacency, 1) > 0.0)))
    return coordinates, edges


def build_static_modal_geometry(
    scala_ratios: Iterable[float],
    *,
    scala_label: str,
    config: ModalGeometryConfig | None = None,
    frame_id: int = 0,
    time: float = 0.0,
) -> ModalGeometryFrame:
    """Build the reference frame from a supplied explicit 20-ratio scale.

    New callers should prefer :class:`StaticModalGeometryEngine` with an
    actual Scala file.  This compatibility entry point retains the previous
    explicit-ratio interface while using the corrected reference-relative
    geometry factor (therefore exactly no rest detuning).
    """

    supplied = tuple(float(value) for value in scala_ratios)
    ratios = tuple(value / supplied[0] for value in supplied) if supplied else ()
    if len(ratios) != 20 or any(not np.isfinite(value) or value <= 0.0 for value in ratios):
        raise ValueError("scala_ratios must be a finite positive 20-vector")
    # A one-period 20-degree scale keeps the supplied values exact at rest.
    scale = ScalaScale(scala_label, ratios[1:] + (ratios[-1] * 2.0,), tuple(str(value) for value in ratios[1:]) + (str(ratios[-1] * 2.0),))
    engine = StaticModalGeometryEngine(scale, config=config or ModalGeometryConfig())
    frame = engine.frame(time=time)
    if frame_id == 0:
        return frame
    # Frame ID is transport metadata only; rebuild with the requested legacy ID.
    return ModalGeometryFrame(**{**frame.__dict__, "frame_id": int(frame_id)})


__all__ = ["ModalGeometryConfig", "ModalGeometryFrame", "StaticModalGeometryEngine", "build_static_modal_geometry", "canonical_dodecahedral_topology"]
