"""Versioned, renderer-neutral transport for :class:`MetricShaderFrame`.

The binary envelope uses only the standard library: a small JSON manifest plus
contiguous little-endian float32 array blocks, optionally compressed with zlib.
It is suitable for WebSocket binary messages while the JSON form remains an
inspectable compatibility path for Max, browsers, and offline fixtures.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
import struct
import zlib
from typing import Any, Mapping

import numpy as np

from .frames import MetricShaderFrame

CONTRACT = "qmw_metric.shader_frame.v1"
MAGIC = b"QMWF\x01\x00\x00\x00"
_HEADER = struct.Struct("<8sII")
ARRAY_FIELDS = (
    "density", "potential", "sigma", "lapse", "metric", "inverse_metric",
    "determinant", "grad_potential", "hessian", "curvature",
    "potential_laplacian", "probability_current", "phase_connection",
    "vorticity", "mode_shapes", "trajectory_positions",
)


class FrameContractError(ValueError):
    """A transport message does not satisfy the published frame contract."""


def _metadata(frame: MetricShaderFrame) -> dict[str, Any]:
    return {
        "contract": CONTRACT,
        "revision": frame.revision,
        "source_revision": frame.source_revision,
        "time": frame.time,
        "model_label": frame.model_label,
    }


def shader_frame_to_payload(frame: MetricShaderFrame) -> dict[str, Any]:
    """Return the documented JSON fallback payload."""
    payload = _metadata(frame)
    payload["arrays"] = {
        name: np.asarray(getattr(frame, name), dtype=np.float32).tolist()
        for name in ARRAY_FIELDS
    }
    return payload


def validate_payload(payload: Mapping[str, Any]) -> None:
    if payload.get("contract") != CONTRACT:
        raise FrameContractError("unsupported shader-frame contract")
    for name in ("revision", "source_revision"):
        value = payload.get(name)
        if not isinstance(value, int) or isinstance(value, bool) or value < 0:
            raise FrameContractError(f"{name} must be a nonnegative integer")
    if not np.isfinite(payload.get("time", np.nan)):
        raise FrameContractError("time must be finite")
    if not isinstance(payload.get("model_label"), str) or not payload["model_label"].strip():
        raise FrameContractError("model_label must be nonempty")
    arrays = payload.get("arrays")
    if not isinstance(arrays, Mapping) or tuple(arrays) != ARRAY_FIELDS:
        raise FrameContractError("array inventory/order does not match the contract")
    density = np.asarray(arrays["density"])
    if density.ndim != 2:
        raise FrameContractError("density must be two-dimensional")
    ny, nx = density.shape
    shapes = {
        "density": (ny, nx), "potential": (ny, nx), "sigma": (ny, nx),
        "lapse": (ny, nx), "metric": (2, 2, ny, nx),
        "inverse_metric": (2, 2, ny, nx), "determinant": (ny, nx),
        "grad_potential": (2, ny, nx), "hessian": (2, 2, ny, nx),
        "curvature": (ny, nx), "potential_laplacian": (ny, nx),
        "probability_current": (2, ny, nx), "phase_connection": (2, ny, nx),
        "vorticity": (ny, nx),
    }
    for name, expected in shapes.items():
        value = np.asarray(arrays[name])
        if value.shape != expected or not np.all(np.isfinite(value)):
            raise FrameContractError(f"{name} has invalid shape or values")
    modes = np.asarray(arrays["mode_shapes"])
    trajectory = np.asarray(arrays["trajectory_positions"])
    if trajectory.size == 0:
        trajectory = np.empty((0, 2), dtype=np.float32)
    if modes.ndim != 3 or modes.shape[1:] != (ny, nx):
        raise FrameContractError("mode_shapes has invalid shape")
    if trajectory.ndim != 2 or trajectory.shape[1:] != (2,):
        raise FrameContractError("trajectory_positions has invalid shape")


def encode_json_frame(frame: MetricShaderFrame) -> bytes:
    payload = shader_frame_to_payload(frame)
    return json.dumps(payload, separators=(",", ":"), allow_nan=False).encode("utf-8")


def encode_binary_frame(frame: MetricShaderFrame, *, compress: bool = True) -> bytes:
    """Encode a deterministic binary WebSocket message."""
    blocks: list[bytes] = []
    arrays: dict[str, dict[str, Any]] = {}
    offset = 0
    for name in ARRAY_FIELDS:
        value = np.ascontiguousarray(getattr(frame, name), dtype="<f4")
        block = value.tobytes(order="C")
        arrays[name] = {"shape": list(value.shape), "offset": offset, "nbytes": len(block)}
        blocks.append(block)
        offset += len(block)
    raw = b"".join(blocks)
    body = zlib.compress(raw, level=3) if compress else raw
    manifest = _metadata(frame) | {
        "encoding": "f32le+zlib" if compress else "f32le",
        "arrays": arrays,
        "raw_nbytes": len(raw),
    }
    header = json.dumps(manifest, separators=(",", ":")).encode("utf-8")
    return _HEADER.pack(MAGIC, len(header), len(body)) + header + body


def decode_binary_frame(message: bytes) -> dict[str, Any]:
    if len(message) < _HEADER.size:
        raise FrameContractError("binary frame is truncated")
    magic, header_size, body_size = _HEADER.unpack_from(message)
    if magic != MAGIC or len(message) != _HEADER.size + header_size + body_size:
        raise FrameContractError("binary frame envelope is invalid")
    start = _HEADER.size
    manifest = json.loads(message[start:start + header_size])
    body = message[start + header_size:]
    encoding = manifest.get("encoding")
    raw = zlib.decompress(body) if encoding == "f32le+zlib" else body
    if encoding not in ("f32le", "f32le+zlib") or len(raw) != manifest.get("raw_nbytes"):
        raise FrameContractError("binary payload encoding/length is invalid")
    descriptors = manifest.get("arrays", {})
    arrays: dict[str, np.ndarray] = {}
    if tuple(descriptors) != ARRAY_FIELDS:
        raise FrameContractError("binary array inventory/order is invalid")
    for name, spec in descriptors.items():
        offset, nbytes = int(spec["offset"]), int(spec["nbytes"])
        value = np.frombuffer(raw[offset:offset + nbytes], dtype="<f4").reshape(spec["shape"])
        arrays[name] = value.copy()
    payload = {key: manifest[key] for key in (
        "contract", "revision", "source_revision", "time", "model_label"
    )}
    payload["arrays"] = arrays
    validate_payload(payload)
    return payload


@dataclass
class RevisionGate:
    """Per-consumer stale/duplicate rejection, independent of transport."""

    last_revision: int = -1
    last_source_revision: int = -1

    def accept(self, payload: Mapping[str, Any]) -> bool:
        validate_payload(payload)
        revision = int(payload["revision"])
        source = int(payload["source_revision"])
        if revision <= self.last_revision or source < self.last_source_revision:
            return False
        self.last_revision = revision
        self.last_source_revision = source
        return True
