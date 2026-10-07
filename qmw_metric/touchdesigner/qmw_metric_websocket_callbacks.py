"""TouchDesigner WebSocket DAT callbacks for the JSON fallback contract.

Install this file as the callbacks DAT and connect to
``ws://127.0.0.1:8767/qmw/metric/v1?format=json``. The component stores only
validated incoming arrays; Script TOP/CHOP operators decide how to display them.
"""

from __future__ import annotations

import json

CONTRACT = "qmw_metric.shader_frame.v1"
ARRAYS = (
    "density", "potential", "sigma", "lapse", "metric", "inverse_metric",
    "determinant", "grad_potential", "hessian", "curvature",
    "potential_laplacian", "probability_current", "phase_connection",
    "vorticity", "mode_shapes", "trajectory_positions",
)


def _accept(owner, payload):
    if payload.get("contract") != CONTRACT or tuple(payload.get("arrays", {})) != ARRAYS:
        owner.store("qmw_status", "rejected contract")
        return False
    revision, source = payload.get("revision"), payload.get("source_revision")
    last = owner.fetch("qmw_revision", -1)
    last_source = owner.fetch("qmw_source_revision", -1)
    if not isinstance(revision, int) or not isinstance(source, int) or revision <= last or source < last_source:
        owner.store("qmw_status", "stale frame rejected")
        return False
    owner.store("qmw_revision", revision)
    owner.store("qmw_source_revision", source)
    owner.store("qmw_frame", payload)
    owner.store("qmw_status", "live")
    return True


def onReceiveText(dat, rowIndex, message):
    payload = json.loads(message)
    if payload.get("type") != "hello":
        _accept(dat.parent(), payload)
    return


def onConnect(dat):
    dat.parent().store("qmw_status", "connected")
    return


def onDisconnect(dat):
    dat.parent().store("qmw_status", "disconnected")
    return


def onReceiveBinary(dat, contents):
    # Use ?format=json. Binary QMWF decoding remains canonical in Python/browser.
    dat.parent().store("qmw_status", "binary disabled; request format=json")
    return
