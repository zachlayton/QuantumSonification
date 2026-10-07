"""Read-only performer-facing comparison of raw and covariant graph phase."""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Mapping, Sequence

import numpy as np

from qmw.flow.gauge_transport import GaugeConnection


def _wrap(value: np.ndarray | float) -> np.ndarray | float:
    return np.angle(np.exp(1j * value))


@dataclass(frozen=True)
class GaugePhaseEdgeView:
    """One legible edge row: raw phase, connection, and covariant phase."""

    source: int
    destination: int
    raw_phase_difference: float
    connection_phase: float
    covariant_phase_difference: float
    current: float


@dataclass(frozen=True)
class GaugePerformerPhaseView:
    """A UI-neutral frame which never controls its wavefunction or connection."""

    time: float
    node_raw_phase: tuple[float, ...]
    edges: tuple[GaugePhaseEdgeView, ...]
    face_holonomies: Mapping[str, float]
    raw_phase_label: str = "raw local phase (gauge-dependent)"
    covariant_phase_label: str = "phase difference minus connection (gauge-invariant)"
    provenance: str = "read_only_performer_raw_vs_covariant_gauge_phase_view"


def observe_gauge_performer_phase_view(
    psi: object,
    connection: GaugeConnection,
    *,
    time: float,
    cycles: Mapping[str, Sequence[int]] | None = None,
    hbar: float = 1.0,
) -> GaugePerformerPhaseView:
    """Expose raw and covariant phase without conflating their meanings."""

    logical_time = float(time)
    if not math.isfinite(logical_time) or not math.isfinite(float(hbar)) or float(hbar) <= 0.0:
        raise ValueError("time must be finite and hbar must be finite and positive.")
    field = np.asarray(psi, dtype=np.complex128)
    if field.shape != (connection.node_count,) or not np.all(np.isfinite(field)):
        raise ValueError("psi must be finite and match the connection node count.")
    raw = np.angle(field)
    currents = connection.wavefunction_link_current(field, hbar=float(hbar))
    rows = tuple(
        GaugePhaseEdgeView(
            source=int(source), destination=int(destination),
            raw_phase_difference=float(_wrap(raw[destination] - raw[source])),
            connection_phase=float(phase),
            covariant_phase_difference=float(_wrap(raw[destination] - raw[source] - phase)),
            current=float(current),
        )
        for (source, destination), phase, current in zip(connection.edge_indices, connection.connection_phases, currents)
    )
    holonomies = {} if cycles is None else {
        str(name): connection.holonomy(tuple(int(node) for node in cycle)) for name, cycle in cycles.items()
    }
    return GaugePerformerPhaseView(
        time=logical_time,
        node_raw_phase=tuple(float(value) for value in raw),
        edges=rows,
        face_holonomies=holonomies,
    )


def render_gauge_performer_phase_view(view: GaugePerformerPhaseView) -> str:
    """Render a compact terminal panel suitable for an inspector sidecar."""

    lines = [
        "QMW GAUGE PHASE — READ-ONLY PERFORMER VIEW",
        f"t={view.time:.5f}",
        "RAW NODE PHASE: " + "  ".join(f"{index}:{phase:+.3f}" for index, phase in enumerate(view.node_raw_phase)),
        "EDGE      RAW Δφ       A        COVARIANT Δφ      J",
    ]
    lines.extend(
        f"{edge.source}->{edge.destination}   {edge.raw_phase_difference:+.4f}   {edge.connection_phase:+.4f}"
        f"     {edge.covariant_phase_difference:+.4f}    {edge.current:+.5f}"
        for edge in view.edges
    )
    if view.face_holonomies:
        lines.append("FACE HOLONOMY: " + "  ".join(f"{name}={value:+.4f}" for name, value in view.face_holonomies.items()))
    lines.append("Raw phase changes with gauge choice; covariant phase and holonomy do not.")
    return "\n".join(lines)


__all__ = [
    "GaugePerformerPhaseView", "GaugePhaseEdgeView", "observe_gauge_performer_phase_view",
    "render_gauge_performer_phase_view",
]
