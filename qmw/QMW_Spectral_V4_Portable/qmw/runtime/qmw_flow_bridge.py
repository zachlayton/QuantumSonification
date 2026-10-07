"""Checked bridge from authoritative ``QMW_flow`` frames to ``QMWFrame``.

The bridge coordinates native payloads; it does not create another quantum
state, flatten their provenance, or promote Hilbert-basis flow to spatial flow.
"""

from __future__ import annotations

import math
from typing import Any, Mapping

from qmw.flow import HilbertBasisFlowObservation
from qmw.quantum import QuantumFrame
from qmw.unified_instrument_v3 import RelationalGeometryFrame

from .frame import FrameRevisions, QMWFrame


def qmw_frame_from_authoritative_flow(
    quantum: QuantumFrame,
    geometry: RelationalGeometryFrame,
    *,
    controls: Any | None = None,
    dt: float = 0.0,
    field: Any | None = None,
    memory: Any | None = None,
    syndrome: Any | None = None,
    recovery: Any | None = None,
    excitation: Any | None = None,
    audio: Any | None = None,
    spatial: Any | None = None,
    measurement: Any | None = None,
    diagnostics: Mapping[str, Any] | None = None,
) -> QMWFrame:
    """Seal one synchronized packet around matching native source revisions.

    ``measurement`` remains an optional discrete result.  It never participates
    in the continuous derivative already sealed in ``quantum``.
    """

    if not isinstance(quantum, QuantumFrame):
        raise TypeError("quantum must be a sealed authoritative QuantumFrame")
    if not isinstance(geometry, RelationalGeometryFrame):
        raise TypeError("geometry must be a RelationalGeometryFrame")
    if geometry.quantum_revision != quantum.frame_index:
        raise ValueError("geometry must cite the supplied quantum revision")
    if not math.isclose(geometry.time, quantum.time, rel_tol=0.0, abs_tol=1.0e-12):
        raise ValueError("geometry and quantum frame times must match")

    flow = HilbertBasisFlowObservation(quantum)
    declared_diagnostics = {
        "quantum_provenance": quantum.provenance,
        "geometry_provenance": geometry.provenance,
        "flow_basis": flow.basis_label,
        "flow_is_spatial": flow.is_spatial,
        "measurement_is_continuous_derivative": False,
    }
    if diagnostics is not None:
        declared_diagnostics.update(diagnostics)

    return QMWFrame(
        time=quantum.time,
        controls=controls,
        quantum=quantum,
        observables=quantum.pauli,
        flow=flow,
        geometry=geometry,
        field=field,
        memory=memory,
        syndrome=syndrome,
        recovery=recovery,
        excitation=excitation,
        audio=audio,
        spatial=spatial,
        measurement=measurement,
        diagnostics=declared_diagnostics,
        dt=dt,
        tick=quantum.frame_index,
        revisions=FrameRevisions(
            quantum=quantum.frame_index,
            observables=quantum.frame_index,
            flow=quantum.frame_index,
            geometry=geometry.revision,
        ),
        provenance="qmw_flow_contract_bridge_v1",
    )


__all__ = ["qmw_frame_from_authoritative_flow"]
