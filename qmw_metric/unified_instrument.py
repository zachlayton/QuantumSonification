"""Read-only Quantum Metric Field adapter for the 20-mode Unified Instrument."""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any

import numpy as np
from numpy.typing import NDArray

from .config import PotentialConfig, QuantumMetricConfig
from .engine import QuantumMetricEngine

RealArray = NDArray[np.float64]
ComplexArray = NDArray[np.complex128]

UNIFIED_MODE_COUNT = 20
UNIFIED_METRIC_OSC_ROOT = "/qmw/metric/unified"
UNIFIED_METRIC_OSC_SCHEMA = "qmw.metric.unified.v1"
UNIFIED_METRIC_OSC_PORT = 17890


def _readonly(value: RealArray, shape: tuple[int, ...]) -> RealArray:
    result = np.asarray(value, dtype=np.float64).copy()
    if result.shape != shape or not np.all(np.isfinite(result)):
        raise ValueError(f"expected finite array with shape {shape}")
    result.setflags(write=False)
    return result


@dataclass(frozen=True)
class UnifiedMetricFrame:
    """One complete downstream deformation/excitation frame.

    The frame cannot create events or modify rho. ``geometry_ratios`` deform
    the instrument body; ``excitation_profile`` shapes only events admitted by
    the existing Unified Instrument authority.
    """

    revision: int
    source_revision: int
    time: float
    geometry_ratios: RealArray
    decay_seconds: RealArray
    excitation_profile: RealArray
    intermodal_connection: RealArray
    trajectory_pan: float
    topography_mode: str

    def __post_init__(self) -> None:
        if self.revision < 0 or self.source_revision < 0 or not np.isfinite(self.time):
            raise ValueError("unified metric frame revision/time are invalid")
        if not self.topography_mode.strip():
            raise ValueError("topography_mode must be nonempty")
        for name in ("geometry_ratios", "decay_seconds", "excitation_profile"):
            object.__setattr__(self, name, _readonly(getattr(self, name), (UNIFIED_MODE_COUNT,)))
        object.__setattr__(
            self,
            "intermodal_connection",
            _readonly(self.intermodal_connection, (UNIFIED_MODE_COUNT, UNIFIED_MODE_COUNT)),
        )
        if np.min(self.geometry_ratios) <= 0.0 or np.min(self.decay_seconds) <= 0.0:
            raise ValueError("geometry ratios and decay times must be positive")
        if np.min(self.excitation_profile) < 0.0:
            raise ValueError("excitation profile must be nonnegative")
        norm = float(np.linalg.norm(self.excitation_profile))
        if norm > 1e-12 and not np.isclose(norm, 1.0, atol=1e-9):
            raise ValueError("nonzero excitation profile must have unit L2 norm")
        if not np.allclose(
            self.intermodal_connection,
            -self.intermodal_connection.T,
            atol=1e-9,
        ):
            raise ValueError("intermodal connection must be antisymmetric")
        if not -1.0 <= self.trajectory_pan <= 1.0:
            raise ValueError("trajectory_pan must lie in [-1, 1]")


class UnifiedMetricObserver:
    """Map successive authoritative rho frames into one 20-mode control frame."""

    def __init__(self, config: QuantumMetricConfig | None = None):
        selected = config or QuantumMetricConfig(
            grid_size=(24, 24), mode_count=UNIFIED_MODE_COUNT
        )
        if selected.mode_count != UNIFIED_MODE_COUNT:
            raise ValueError("Unified Instrument requires exactly 20 QMF modes")
        self.config = selected
        self.engine = QuantumMetricEngine(selected)
        flat_config = replace(
            selected,
            potential=replace(selected.potential, coupling=0.0),
        )
        flat = QuantumMetricEngine(flat_config)
        reference_rho = np.eye(selected.quantum_dimension, dtype=np.complex128)
        reference_rho /= selected.quantum_dimension
        flat.update_quantum_frame(reference_rho, 0.0, force_modes=True, source_revision=0)
        self.flat_frequencies = flat.mode_frame.frequencies.copy()

    def observe(
        self,
        rho: ComplexArray,
        *,
        time: float,
        source_revision: int,
        dt: float,
    ) -> UnifiedMetricFrame:
        if not np.isfinite(dt) or dt <= 0.0:
            raise ValueError("dt must be positive")
        self.engine.update_quantum_frame(
            rho,
            time=float(time),
            source_revision=int(source_revision),
        )
        trajectory = self.engine.process_control_step(float(dt))
        modes = self.engine.mode_frame
        excitation = np.abs(self.engine.modal_excitation)
        norm = float(np.linalg.norm(excitation))
        profile = excitation / norm if norm > 1e-12 else np.zeros_like(excitation)
        quality = 1.0 / np.maximum(2.0 * modes.damping, 1e-12)
        decay = quality / np.maximum(np.pi * modes.frequencies, 1e-12)
        xmin, xmax, _ymin, _ymax = self.engine.grid.extent
        pan = 2.0 * (trajectory.position[0] - xmin) / (xmax - xmin) - 1.0
        system = self.engine.system_frame
        return UnifiedMetricFrame(
            revision=system.revision,
            source_revision=int(source_revision),
            time=float(time),
            geometry_ratios=modes.frequencies / self.flat_frequencies,
            decay_seconds=decay,
            excitation_profile=profile,
            intermodal_connection=modes.intermodal_connection,
            trajectory_pan=float(np.clip(pan, -1.0, 1.0)),
            topography_mode=self.config.lorentz.topography_mode,
        )


class UnifiedMetricOSCPublisher:
    """Publish an atomic, monotonic QMF transaction to SuperCollider."""

    def __init__(self, client: Any):
        if not hasattr(client, "send_message"):
            raise TypeError("client must provide send_message")
        self.client = client
        self._last_revision = -1

    @classmethod
    def from_udp(
        cls, host: str = "127.0.0.1", port: int = UNIFIED_METRIC_OSC_PORT
    ) -> "UnifiedMetricOSCPublisher":
        from pythonosc.udp_client import SimpleUDPClient

        return cls(SimpleUDPClient(host, int(port)))

    def messages(self, frame: UnifiedMetricFrame) -> list[tuple[str, list[Any]]]:
        root = UNIFIED_METRIC_OSC_ROOT
        frame_id = frame.revision
        return [
            (f"{root}/frame/begin", [
                frame_id,
                frame.source_revision,
                frame.time,
                UNIFIED_METRIC_OSC_SCHEMA,
                UNIFIED_MODE_COUNT,
                frame.topography_mode,
            ]),
            (f"{root}/geometry_ratios", [frame_id, *frame.geometry_ratios.tolist()]),
            (f"{root}/decay_seconds", [frame_id, *frame.decay_seconds.tolist()]),
            (f"{root}/excitation", [frame_id, *frame.excitation_profile.tolist()]),
            (f"{root}/connection", [frame_id, *frame.intermodal_connection.reshape(-1).tolist()]),
            (f"{root}/trajectory_pan", [frame_id, frame.trajectory_pan]),
            (f"{root}/frame/end", [frame_id]),
        ]

    def publish(self, frame: UnifiedMetricFrame) -> int | None:
        if frame.revision <= self._last_revision:
            return None
        for address, payload in self.messages(frame):
            self.client.send_message(address, payload)
        self._last_revision = frame.revision
        return frame.revision


__all__ = [
    "UNIFIED_METRIC_OSC_PORT",
    "UNIFIED_METRIC_OSC_ROOT",
    "UNIFIED_METRIC_OSC_SCHEMA",
    "UNIFIED_MODE_COUNT",
    "UnifiedMetricFrame",
    "UnifiedMetricObserver",
    "UnifiedMetricOSCPublisher",
]
