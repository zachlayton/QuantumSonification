"""Drives the algebraic surface's live sound design from a 4-qubit density
matrix, instead of (or on top of) manual sliders.

``density.density_matrix_engine_4q.DensityMatrixEngine`` is a self-driven
Hamiltonian that continuously evolves a 4-qubit density matrix under
state-dependent feedback -- it needs no external excitation to keep moving.
This module runs it on its own background thread and turns that motion into
two update streams, mirroring the two costs already in
``realtime_bridge_v1``: modulating sound design is cheap (no re-mesh), while
changing the mesh is not.

- fast (every tick, ``tick_hz``): reads the *already computed* modal packet
  and perturbs its per-mode amplitude and pan using live coherence phases
  (``numpy.angle`` of the density matrix's off-diagonal entries -- literal
  quantum phase shifting), then sends the modulated set straight to Sonic
  Pi. No mesh, eigensolve, or material-model recompute involved.
- slow (every ``slow_interval_seconds``): exponentially smooths global
  coherence and Bloch-vector statistics into wave speed, T60, and damping
  tilt, and hands them to a caller-supplied callback. The host GUI is
  expected to feed these into its own sliders so they drive the existing
  debounce/cache recompute path, rather than adding a second one here.

Purity and von Neumann entropy of the full system are deliberately not
used as slow-path sources: this engine's default state-conditioning keeps
the full 16-dimensional ``rho`` numerically pure (trace(rho^2) ~= 1)
regardless of its noise parameters, so those two quantities carry no
signal here. Coherence and per-qubit Bloch-vector spread do vary
continuously and are used instead.
"""

from __future__ import annotations

from dataclasses import dataclass
import threading
import time
from typing import Callable, TypedDict

import numpy as np

from density.density_matrix_engine_4q import (
    DIMENSION,
    DensityMatrixEngine,
    l1_coherence,
)
from surface_material_models_v1 import SurfaceModalPacket

from .realtime_bridge_v1 import SonicPiModeStreamer

ENGINE_PARAM_NAMES: tuple[str, ...] = (
    "dephase",
    "damping",
    "depolarize",
    "coupling",
    "drift",
    "feedback",
)


class SlowUpdate(TypedDict):
    wave_speed: float
    t60_seconds: float
    damping_frequency_tilt: float
    coherence: float
    bloch_spread: float
    mean_abs_z: float


@dataclass(frozen=True)
class QuantumConductorConfig:
    tick_hz: float = 20.0
    slow_interval_seconds: float = 0.4

    # 0 = mode weights untouched by phase; 1 = full phase-driven swing.
    modulation_depth: float = 0.5
    # 0 = static pseudo-random pan only; 1 = pan follows live phase_sin.
    pan_modulation: float = 0.6
    # Exponential-moving-average factor for the slow path, in [0, 1).
    # Higher = slower/smoother drift.
    smoothing: float = 0.9

    wave_speed_range: tuple[float, float] = (40.0, 260.0)
    t60_range: tuple[float, float] = (0.6, 6.0)
    damping_tilt_range: tuple[float, float] = (0.0, 0.9)

    # Density-engine parameters, forwarded via DensityMatrixEngine.set_param.
    dephase: float = 0.01
    damping: float = 0.004
    depolarize: float = 0.002
    coupling: float = 0.7
    drift: float = 0.15
    feedback: float = 0.35


def coherence_phase_signals(rho: np.ndarray, count: int) -> tuple[np.ndarray, np.ndarray]:
    """sin/cos of the phases of `count` off-diagonal density-matrix entries.

    A 16-dimensional density matrix has 120 upper-triangular off-diagonal
    entries -- more than enough independent, continuously evolving phase
    signals to cover any realistic active-mode count. If more are
    requested than exist, the sequence repeats.
    """
    n = rho.shape[0]
    pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
    if count <= 0 or not pairs:
        return np.zeros(max(count, 0)), np.ones(max(count, 0))
    if count > len(pairs):
        pairs = (pairs * (count // len(pairs) + 1))[:count]
    else:
        pairs = pairs[:count]
    phases = np.array([np.angle(rho[i, j]) for i, j in pairs])
    return np.sin(phases), np.cos(phases)


def _lerp(bounds: tuple[float, float], unit: float) -> float:
    low, high = bounds
    return low + (high - low) * float(np.clip(unit, 0.0, 1.0))


class QuantumPhaseConductor:
    """Ticks a DensityMatrixEngine and streams its motion to Sonic Pi."""

    def __init__(
        self,
        streamer: SonicPiModeStreamer,
        get_packet: Callable[[], SurfaceModalPacket | None],
        on_slow_update: Callable[[SlowUpdate], None],
        config: QuantumConductorConfig = QuantumConductorConfig(),
    ) -> None:
        self.streamer = streamer
        self.get_packet = get_packet
        self.on_slow_update = on_slow_update
        self.config = config

        self.engine = DensityMatrixEngine(enable_circuit_bridge_control=False)
        for name in ENGINE_PARAM_NAMES:
            self.engine.set_param(name, getattr(config, name))

        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
        self._coherence_ema = 0.0
        self._bloch_spread_ema = 0.0
        self._mean_abs_z_ema = 0.0

    def start(self) -> None:
        if self._thread is not None:
            return
        self._stop.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        thread, self._thread = self._thread, None
        if thread is not None:
            thread.join(timeout=2.0)

    @property
    def is_running(self) -> bool:
        return self._thread is not None

    def _run(self) -> None:
        dt = 1.0 / max(self.config.tick_hz, 1.0)
        last_slow = 0.0
        while not self._stop.is_set():
            started = time.monotonic()
            rho = self.engine.step(dt)
            self._send_fast_update(rho)

            if started - last_slow >= self.config.slow_interval_seconds:
                self._send_slow_update(rho)
                last_slow = started

            elapsed = time.monotonic() - started
            self._stop.wait(max(0.0, dt - elapsed))

    def _send_fast_update(self, rho: np.ndarray) -> None:
        packet = self.get_packet()
        if packet is None:
            return
        count = len(packet.frequencies_hz)
        if count == 0:
            return

        phase_sin, phase_cos = coherence_phase_signals(rho, count)
        depth = float(np.clip(self.config.modulation_depth, 0.0, 1.0))
        shimmer = (1.0 - depth) + depth * (0.5 + 0.5 * phase_cos)
        amplitudes = np.asarray(packet.mode_weights, dtype=np.float64) * shimmer

        pan_blend = float(np.clip(self.config.pan_modulation, 0.0, 1.0))
        static_pan = self.streamer.default_pans(count)
        pans = np.clip((1.0 - pan_blend) * static_pan + pan_blend * phase_sin, -1.0, 1.0)

        self.streamer.send_modes(
            packet.frequencies_hz, packet.decay_times_seconds, amplitudes, pans
        )

    def _send_slow_update(self, rho: np.ndarray) -> None:
        coherence = l1_coherence(rho) / (DIMENSION - 1)
        bloch = self.engine.local_bloch_vectors(rho)
        magnitudes = np.linalg.norm(bloch, axis=1)
        bloch_spread = float(np.std(magnitudes))
        mean_abs_z = float(np.mean(np.abs(bloch[:, 2])))

        alpha = 1.0 - float(np.clip(self.config.smoothing, 0.0, 0.999))
        self._coherence_ema += alpha * (coherence - self._coherence_ema)
        self._bloch_spread_ema += alpha * (bloch_spread - self._bloch_spread_ema)
        self._mean_abs_z_ema += alpha * (mean_abs_z - self._mean_abs_z_ema)

        update: SlowUpdate = {
            "wave_speed": _lerp(self.config.wave_speed_range, self._coherence_ema),
            "t60_seconds": _lerp(
                self.config.t60_range, self._bloch_spread_ema / 0.3
            ),
            "damping_frequency_tilt": _lerp(
                self.config.damping_tilt_range, self._mean_abs_z_ema / 0.5
            ),
            "coherence": self._coherence_ema,
            "bloch_spread": self._bloch_spread_ema,
            "mean_abs_z": self._mean_abs_z_ema,
        }
        self.on_slow_update(update)
