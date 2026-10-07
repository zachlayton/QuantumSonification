"""Portable offline report: all scientific aggregates originate in Python."""

import json
from pathlib import Path

from .backend import ColliderBackend


def render_report(backend: ColliderBackend, path: str | Path) -> Path:
    template = Path(__file__).with_name("viewer.html").read_text(encoding="utf-8")
    payload = json.dumps(backend.summary(), allow_nan=False, sort_keys=True)
    # A provenance string must never terminate an HTML script element.
    payload = payload.replace("&", "\\u0026").replace("<", "\\u003c").replace(">", "\\u003e")
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(template.replace("__COLLIDER_DATA__", payload), encoding="utf-8")
    return path
