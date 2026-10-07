"""Bounded, read-only density-to-dynamic-geometry sidecar for QMW performance.

This is deliberately a control-rate observer.  It never evolves ``rho`` and
never transmits a triangle mesh to an audio process.
"""
from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Any

import numpy as np

from qmw.qmw_emergent_geometry import observe_emergent_geometry, validate_density_matrix

SCHEMA = "qmw.dynamic_geometry.osc.v1"
OSC_ROOT = "/qmw/performance/v1/dynamic_geometry"


@dataclass(frozen=True)
class DynamicGeometryFrame:
    """Atomic compact controls derived from one authoritative four-qubit rho."""

    revision: int
    time: float
    mode_activity: np.ndarray  # 16 modeled body activations
    node_entropy: np.ndarray  # 4 measured single-site entropies
    neck_permeability: np.ndarray  # symmetric 4 x 4 modeled MI connections
    provenance: str = "read_only_density_dynamic_geometry_v1"


class DynamicGeometryObserver:
    """Rate gate plus deterministic observer; callers may safely drop stale work."""

    def __init__(self, *, maximum_hz: float = 20.0) -> None:
        if not math.isfinite(maximum_hz) or not 0.1 <= maximum_hz <= 120.0:
            raise ValueError("maximum_hz must be finite and lie in [0.1, 120].")
        self.minimum_interval = 1.0 / float(maximum_hz)
        self._last_time: float | None = None

    def observe_if_due(self, rho: object, *, revision: int, time: float) -> DynamicGeometryFrame | None:
        if self._last_time is not None and time - self._last_time < self.minimum_interval:
            return None
        frame = self.observe(rho, revision=revision, time=time)
        self._last_time = float(time)
        return frame

    @staticmethod
    def observe(rho: object, *, revision: int, time: float) -> DynamicGeometryFrame:
        matrix = validate_density_matrix(rho)
        if matrix.shape != (16, 16):
            raise ValueError("dynamic geometry v1 requires the canonical four-qubit 16x16 rho.")
        relational = observe_emergent_geometry(matrix, revision=revision, time=time)
        populations = np.clip(np.real(np.diag(matrix)), 0.0, 1.0)
        # Coherence magnitude is measured; the conversion to body activity is
        # explicitly a perceptual/material choice, not quantum evolution.
        coherence = (np.sum(np.abs(matrix), axis=1) - populations) / 15.0
        modes = np.clip(0.15 * np.sqrt(populations) + 0.85 * coherence, 0.0, 1.0)
        return DynamicGeometryFrame(int(revision), float(time), np.array(modes, copy=True),
            np.array(relational.node_entropy_bits, copy=True), np.array(relational.adjacency, copy=True))


class DynamicGeometryOSCPublisher:
    """Publish compact atomic controls; no receiver or audio effect is implied."""

    def __init__(self, client: Any) -> None:
        if not hasattr(client, "send_message"):
            raise ValueError("OSC client must expose send_message().")
        self.client = client

    def publish(self, frame: DynamicGeometryFrame) -> int:
        self.client.send_message(f"{OSC_ROOT}/begin", [frame.revision, frame.time, SCHEMA, 16, 4, 6])
        for index, value in enumerate(frame.mode_activity):
            self.client.send_message(f"{OSC_ROOT}/mode", [frame.revision, index, float(value)])
        for index, value in enumerate(frame.node_entropy):
            self.client.send_message(f"{OSC_ROOT}/node", [frame.revision, index, float(value)])
        for left in range(4):
            for right in range(left + 1, 4):
                self.client.send_message(f"{OSC_ROOT}/neck", [frame.revision, left, right, float(frame.neck_permeability[left, right])])
        self.client.send_message(f"{OSC_ROOT}/end", [frame.revision])
        return frame.revision


__all__ = ["DynamicGeometryFrame", "DynamicGeometryObserver", "DynamicGeometryOSCPublisher", "OSC_ROOT", "SCHEMA"]
